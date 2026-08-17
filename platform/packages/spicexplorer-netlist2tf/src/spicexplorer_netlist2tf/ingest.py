"""Stage 1 — ingestion: a parsed netlist (``NetlistView``) → the typed internal IR (``Circuit2TF``).

This is the single ingestion seam. It starts at a :class:`~spicexplorer_core.spice_engine.NetlistView`
(core owns all SPICE text parsing) and maps the string-level accessors into netlist2tf's **own**
typed IR — it never re-parses SPICE and never imports the circuitgraph peer (the device-typing logic
here is re-implemented, not borrowed; only *parsing* lives in core — ``doc/plan_netlist2tf.md`` §1/OD-5).

Front-ends, all producing the same IR:

* :func:`ingest_netlist` — from an already-built ``NetlistView`` (at whatever hierarchy level it sits).
* :func:`from_file` / :func:`from_string` — convenience wrappers that build the ``NetlistView`` first.

Everything is **sympified once** here (plan §4): geometry/value param strings → sympy ``Expr`` (numeric
→ ``Float``; symbolic reference → ``Symbol``), with all netlist-derived symbol names lower-cased (SPICE
is case-insensitive, so this is collision-free and makes device-card refs match global ``.param`` names).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import sympy as sp
from spicexplorer_core.eng import parse_value
from spicexplorer_core.spice_engine import NetlistView

from .model.ir import (
    Circuit2TF,
    Device,
    DeviceKind,
    Net,
    NetRole,
    PinRole,
    PortPair,
    Terminal,
)

logger = logging.getLogger(__name__)

__all__ = ["ingest_netlist", "from_file", "from_string"]

# Name-based supply classification (re-implemented from circuitgraph's _classify_supply *logic*,
# not imported — the peer wall). Normalization drops separators + the global-net "!" and lower-cases.
_GROUND_NAMES = {"0", "gnd", "vgnd"}
_NEG_RAIL_NAMES = {"vss", "vee", "vssa", "vssio"}
_POS_RAIL_NAMES = {"vdd", "vcc", "vpwr", "vdda", "vddio", "vcca"}

# Reference-designator prefixes (refs come back upper-cased from spicelib). X-wrapped primitives
# (XM/XR/XC/XL) are treated as the primitive they wrap; a bare X… is an opaque subckt instance.
_MOS_PREFIXES = ("M", "XM")
_RES_PREFIXES = ("R", "XR")
_CAP_PREFIXES = ("C", "XC")
_IND_PREFIXES = ("L", "XL")

# MOSFET / BJT pin orders (spicelib's node order for an M/Q card).
_MOS_PINS = (PinRole.DRAIN, PinRole.GATE, PinRole.SOURCE, PinRole.BULK)
_MOS_PINS_NO_BULK = (PinRole.DRAIN, PinRole.GATE, PinRole.SOURCE)
_TWO_TERMINAL = (PinRole.PLUS, PinRole.MINUS)


# ------------------------------------------------------------------------
# Value sympification
# ------------------------------------------------------------------------
def _lower_symbols(expr: sp.Expr) -> sp.Expr:
    """Lower-case every symbol name in ``expr`` (SPICE is case-insensitive → canonical form)."""
    subs = {s: sp.Symbol(str(s).lower()) for s in expr.free_symbols if str(s) != str(s).lower()}
    return expr.xreplace(subs) if subs else expr


# SPICE engineering scale factors (case-insensitive; 'meg' = 1e6, 'm' = milli — SPICE-correct).
# Used as a fallback for tokens core's parse_value misses (e.g. an upper-case 'P', or 'meg').
_ENG_SCALE = {"t": 1e12, "g": 1e9, "k": 1e3, "m": 1e-3, "u": 1e-6, "µ": 1e-6,
              "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18}
_ENG_RE = re.compile(r"^([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)([a-zµ]*)$", re.IGNORECASE)


def _try_eng(s: str) -> float | None:
    """SPICE-correct, case-insensitive engineering parse; ``None`` if ``s`` is not numeric."""
    m = _ENG_RE.match(s)
    if not m:
        return None
    mant, suf = m.group(1), m.group(2).lower()
    if not suf:
        return float(mant)
    if suf.startswith("meg"):
        return float(mant) * 1e6
    factor = _ENG_SCALE.get(suf[0])  # trailing unit letters after the scale are ignored (SPICE)
    return float(mant) * factor if factor is not None else None


def _as_number(num: float) -> sp.Expr:
    return sp.Integer(int(num)) if num == int(num) else sp.Float(num)


def sympify_value(raw: object) -> sp.Expr:
    """Parse one SPICE value token into a sympy ``Expr``.

    Numeric (with optional engineering suffix, e.g. ``"50f"``, ``"0.18u"``, ``"0P"``, ``1.5``) → a
    sympy ``Float``/``Integer``. A symbolic reference or expression (``"CL"``, ``"{2*W}"``,
    ``"x_dut_nfet_input_w"``) → the corresponding symbolic ``Expr`` with lower-cased symbol names.
    """
    if isinstance(raw, bool):  # guard: bool is an int subclass
        return sp.Integer(int(raw))
    if isinstance(raw, (int, float)):
        return _as_number(float(raw))
    s = str(raw).strip()
    if not s:
        raise ValueError("empty value token")
    s = s.strip("{}").strip()  # SPICE brace-expressions
    # Engineering numeric first: core's parse_value (platform-consistent), then a SPICE-correct
    # case-insensitive fallback for tokens it misses ('0P', 'meg').
    try:
        return _as_number(float(parse_value(s)))
    except (ValueError, TypeError):
        eng = _try_eng(s)
        if eng is not None:
            return _as_number(eng)
    # Symbolic reference / expression.
    expr = sp.sympify(s, rational=True)  # type: ignore[call-overload]
    return _lower_symbols(expr)


# ------------------------------------------------------------------------
# Net role classification
# ------------------------------------------------------------------------
def _normalize_net(name: str) -> str:
    return name.strip().lower().replace("_", "").replace("!", "")


def classify_net_role(name: str) -> NetRole:
    """Map a net name to its small-signal :class:`NetRole` (name-based, plan §4 / OD-5).

    ``GROUND`` for the reference node; ``SUPPLY_DC`` for a named positive/negative rail (both are
    AC grounds); ``SIGNAL`` otherwise. Source-driven role inference (a net shorted to ground by a
    pure-DC source) is layered on in the MNA stage where the DC short physically lives.
    """
    norm = _normalize_net(name)
    if norm in _GROUND_NAMES:
        return NetRole.GROUND
    if norm in _NEG_RAIL_NAMES or norm in _POS_RAIL_NAMES:
        return NetRole.SUPPLY_DC
    return NetRole.SIGNAL


# ------------------------------------------------------------------------
# Device dispatch
# ------------------------------------------------------------------------
def _mos_kind(model: str | None) -> DeviceKind:
    if model:
        lo = model.lower()
        if "nmos" in lo or re.search(r"\bnfet\b", lo):
            return DeviceKind.NMOS
        if "pmos" in lo or re.search(r"\bpfet\b", lo):
            return DeviceKind.PMOS
    return DeviceKind.MOS


def _geometry_params(view: NetlistView, ref: str) -> dict[str, sp.Expr]:
    """Sympify a device's ``k=v`` parameters, dropping spicelib's duplicate ``'Value'`` key."""
    out: dict[str, sp.Expr] = {}
    for k, v in view.get_component_parameters(ref).items():
        if k == "Value":
            continue
        try:
            out[k.lower()] = sympify_value(v)
        except (ValueError, TypeError, sp.SympifyError):
            logger.warning("ref %s: could not sympify param %s=%r; keeping symbolic", ref, k, v)
            out[k.lower()] = sp.Symbol(f"{ref.lower()}_{k.lower()}")
    return out


def _source_params(view: NetlistView, ref: str) -> dict[str, sp.Expr]:
    """Best-effort parse of an independent-source value spec (``'dc VCM ac 1'``, ``'IBIAS'``, ``'0'``).

    Records ``dc``/``ac`` magnitudes when recognizable plus the raw ``spec`` string. For the
    small-signal TF a V-source is a branch short and an I-source is open; the spec only matters for
    bias/excitation (handled later), so verbatim preservation here is enough.
    """
    spec = str(view.get_component_value(ref)).strip()
    out: dict[str, sp.Expr] = {}
    toks = spec.split()
    i = 0
    saw_kw = False
    while i < len(toks):
        kw = toks[i].lower()
        if kw in ("dc", "ac") and i + 1 < len(toks):
            saw_kw = True
            try:
                out[kw] = sympify_value(toks[i + 1])
            except (ValueError, TypeError, sp.SympifyError):
                pass
            i += 2
            continue
        i += 1
    # A bare leading token (no dc/ac keyword) is the DC value, e.g. 'IBIAS' or '0'.
    if not saw_kw and toks:
        try:
            out["dc"] = sympify_value(toks[0])
        except (ValueError, TypeError, sp.SympifyError):
            pass
    return out


def _terminals(roles: tuple[PinRole, ...], nets: list[str]) -> tuple[Terminal, ...]:
    return tuple(Terminal(role, net) for role, net in zip(roles, nets))


def build_device(view: NetlistView, ref: str) -> Device:
    """Type one reference designator into a :class:`Device` (dispatch by prefix)."""
    ref_u = ref.upper()
    nets = view.get_component_nodes(ref)

    if ref_u.startswith(_MOS_PREFIXES):
        model = view.get_component_value(ref)
        if len(nets) == 4:
            roles = _MOS_PINS
        elif len(nets) == 3:
            roles = _MOS_PINS_NO_BULK
        else:
            return _opaque_device(view, ref, nets)
        return Device(
            ref=ref,
            kind=_mos_kind(model),
            terminals=_terminals(roles, nets),
            model=model,
            params=_geometry_params(view, ref),
        )

    if ref_u.startswith(_RES_PREFIXES) and len(nets) == 2:
        return _two_terminal(view, ref, nets, DeviceKind.RESISTOR)
    if ref_u.startswith(_CAP_PREFIXES) and len(nets) == 2:
        return _two_terminal(view, ref, nets, DeviceKind.CAPACITOR)
    if ref_u.startswith(_IND_PREFIXES) and len(nets) == 2:
        return _two_terminal(view, ref, nets, DeviceKind.INDUCTOR)

    if ref_u.startswith("V") and len(nets) == 2:
        return Device(ref, DeviceKind.VSOURCE, _terminals(_TWO_TERMINAL, nets),
                      model=None, params=_source_params(view, ref))
    if ref_u.startswith("I") and len(nets) == 2:
        return Device(ref, DeviceKind.ISOURCE, _terminals(_TWO_TERMINAL, nets),
                      model=None, params=_source_params(view, ref))

    return _opaque_device(view, ref, nets)


def _two_terminal(view: NetlistView, ref: str, nets: list[str], kind: DeviceKind) -> Device:
    """An R/C/L: the element value is its ``get_component_value`` token, kept under ``params['value']``."""
    params = _geometry_params(view, ref)
    try:
        params["value"] = sympify_value(view.get_component_value(ref))
    except (ValueError, TypeError, sp.SympifyError):
        params["value"] = sp.Symbol(f"{ref.lower()}_value")
    return Device(ref, kind, _terminals(_TWO_TERMINAL, nets), model=None, params=params)


def _opaque_device(view: NetlistView, ref: str, nets: list[str]) -> Device:
    """A subckt instance or an unhandled element: positional PORT terminals, model = referenced name."""
    kind = DeviceKind.SUBCKT if ref.upper().startswith("X") else DeviceKind.UNKNOWN
    roles = tuple(PinRole.PORT for _ in nets)
    model = view.get_component_value(ref) if kind is DeviceKind.SUBCKT else None
    logger.debug("ref %s typed as %s (%d ports)", ref, kind.value, len(nets))
    return Device(ref, kind, _terminals(roles, nets), model=model,
                  params=_geometry_params(view, ref))


# ------------------------------------------------------------------------
# Subckt flatten (plan §4: flatten via get_subcircuit, rename with a `_<inst>` postfix)
# ------------------------------------------------------------------------
_FLATTEN_MAX_DEPTH = 8


def _rename_for_instance(dev: Device, suffix: str, net_map: dict[str, str]) -> Device:
    """Re-home a definition-level device into the parent level: formal-port nets map to the
    instance's actual nets, AC-ground nets (global by convention) keep their names, and every
    other (internal) net/ref gets the per-instance postfix so instances never collide."""

    def map_net(n: str) -> str:
        if n in net_map:
            return net_map[n]
        if classify_net_role(n) is not NetRole.SIGNAL:
            return n  # ground/supply names are global AC grounds either way — never localize
        return f"{n}{suffix}"

    return Device(
        ref=f"{dev.ref}{suffix.upper()}",
        kind=dev.kind,
        terminals=tuple(Terminal(t.role, map_net(t.net)) for t in dev.terminals),
        model=dev.model,
        params=dev.params,
        op=dev.op,
        match_group=dev.match_group,
    )


def _flatten_subckt(
    view: NetlistView, dev: Device, *, keep_opaque: set[str], depth: int
) -> tuple[Device, ...] | None:
    """Expand an opaque subckt-instance ``Device`` into its definition's (renamed) devices.

    Returns ``None`` when the definition or its formal ports can't be resolved (the caller keeps
    the instance opaque, matching the pre-flatten behavior). Nested instances flatten recursively
    (innermost first), so each emitted device carries the full ``_<inner>_<outer>`` postfix chain.
    """
    try:
        sub = view.get_subcircuit(dev.ref)
    except Exception as exc:  # noqa: BLE001 — unresolvable definition is an expected fallback
        logger.debug("flatten: no definition for %s (%s): %s", dev.ref, dev.model, exc)
        return None
    formals = view.get_subcircuit_ports(dev.ref)
    actuals = [t.net for t in dev.terminals]
    if not formals or len(formals) != len(actuals):
        logger.warning(
            "flatten: %s (%s) port mismatch (formal %s vs %d actual nets); kept opaque",
            dev.ref, dev.model, formals, len(actuals),
        )
        return None

    suffix = f"_{dev.ref.lower()}"
    net_map = dict(zip(formals, actuals))
    out: list[Device] = []
    for ref in sub.get_components():
        d = build_device(sub, ref)
        expanded: tuple[Device, ...] | None = None
        if d.kind is DeviceKind.SUBCKT and (d.model or "").lower() not in keep_opaque:
            if depth <= 1:
                logger.warning("flatten: max depth reached at %s%s; kept opaque", d.ref, suffix)
            else:
                expanded = _flatten_subckt(sub, d, keep_opaque=keep_opaque, depth=depth - 1)
        for e in expanded if expanded is not None else (d,):
            out.append(_rename_for_instance(e, suffix, net_map))
    return tuple(out)


# ------------------------------------------------------------------------
# Top-level ingestion
# ------------------------------------------------------------------------
def _global_params(view: NetlistView) -> dict[str, sp.Expr]:
    out: dict[str, sp.Expr] = {}
    try:
        raw = view.get_parameters()
    except Exception as exc:  # noqa: BLE001 — older core / step-in views may not expose globals
        logger.debug("global .param read unavailable: %s", exc)
        return out
    for name, val in raw.items():
        try:
            out[name.lower()] = sympify_value(val)
        except (ValueError, TypeError, sp.SympifyError):
            logger.debug("global param %s=%r not sympifiable; skipped", name, val)
    return out


def ingest_netlist(
    view: NetlistView,
    *,
    name: str = "circuit",
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    flatten: bool = True,
    keep_opaque: tuple[str, ...] = (),
) -> Circuit2TF:
    """Map a :class:`NetlistView` (at its current hierarchy level) into the typed IR.

    ``ports`` optionally names analysis ports up front (``{"in": ("vinp", "vinn"), "out": ("vout",
    "0")}``); they can also be supplied later at ``extract_tf`` time. ``ground`` is the canonical
    reference-node name.

    ``flatten`` (default on) steps into every resolvable ``X…`` subckt instance and splices its
    devices in with a ``_<inst>`` postfix on internal nets/refs, so a *testbench-level* netlist
    ingests as one flat circuit. An instance whose definition can't be resolved stays opaque (the
    pre-flatten behavior), as does any subckt named in ``keep_opaque`` (case-insensitive) — the
    hook for behavioral/registered models.
    """
    keep = {k.lower() for k in keep_opaque}
    devices_list: list[Device] = []
    for ref in view.get_components():
        d = build_device(view, ref)
        if flatten and d.kind is DeviceKind.SUBCKT and (d.model or "").lower() not in keep:
            expanded = _flatten_subckt(view, d, keep_opaque=keep, depth=_FLATTEN_MAX_DEPTH)
            if expanded is not None:
                devices_list.extend(expanded)
                continue
            logger.warning("subckt instance %s (%s) not flattened; kept opaque", d.ref, d.model)
        devices_list.append(d)
    devices = tuple(devices_list)

    nets = {n: Net(n, classify_net_role(n)) for n in view.get_all_nodes()}
    for d in devices:  # flattened-internal nets exist only on devices, not on the top view
        for t in d.terminals:
            if t.net not in nets:
                nets[t.net] = Net(t.net, classify_net_role(t.net))
    port_pairs = {k: PortPair(*v) for k, v in (ports or {}).items()}
    params = _global_params(view)

    ir = Circuit2TF(
        name=name,
        nets=nets,
        devices=devices,
        ports=port_pairs,
        params=params,
        ground=ground,
    )
    # The keep-symbolic allow-list: every symbol that survived ingestion (device + global params).
    ir.symbolic = ir.free_symbols
    return ir


def from_file(
    path: str | Path,
    *,
    name: str | None = None,
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    flatten: bool = True,
    keep_opaque: tuple[str, ...] = (),
) -> Circuit2TF:
    """Ingest a netlist file (builds the ``NetlistView`` first)."""
    view = NetlistView.from_file(path)
    return ingest_netlist(view, name=name or Path(path).stem, ports=ports, ground=ground,
                          flatten=flatten, keep_opaque=keep_opaque)


def from_string(
    text: str,
    *,
    name: str = "circuit",
    ports: dict[str, tuple[str, str]] | None = None,
    ground: str = "0",
    flatten: bool = True,
    keep_opaque: tuple[str, ...] = (),
) -> Circuit2TF:
    """Ingest raw SPICE text (builds the ``NetlistView`` first).

    SPICE treats the first line as an ignored *title*; a convenience title comment is prepended when
    the text doesn't already start with one, so a bare fragment (first line is a real element) keeps
    that element instead of losing it to the title slot.
    """
    first = next((ln for ln in text.lstrip().splitlines() if ln.strip()), "")
    if not first.lstrip().startswith("*"):
        text = f"* {name}\n{text}"
    return ingest_netlist(NetlistView.from_string(text), name=name, ports=ports, ground=ground,
                          flatten=flatten, keep_opaque=keep_opaque)
