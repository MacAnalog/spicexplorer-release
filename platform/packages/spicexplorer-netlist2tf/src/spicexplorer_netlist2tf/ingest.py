"""Stage 1 — ingestion: a parsed netlist (``NetlistView``) → the typed internal IR (``Circuit2TF``).

This is the single ingestion seam. It starts at a :class:`~spicexplorer_core.spice_engine.NetlistView`
(core owns all SPICE text parsing) and maps the string-level accessors into netlist2tf's **own**
typed IR — it never re-parses SPICE and never imports the circuitgraph peer (the device-typing logic
here is re-implemented, not borrowed; only *parsing* lives in core — ``doc/archive/plan_netlist2tf.md`` §1/OD-5).

Front-ends, all producing the same IR:

* :func:`ingest_netlist` — from an already-built ``NetlistView`` (at whatever hierarchy level it sits).
* :func:`from_file` / :func:`from_string` — convenience wrappers that build the ``NetlistView`` first.

Everything is **sympified once** here (plan §4): geometry/value param strings → sympy ``Expr`` (numeric
→ an exact ``Rational``; symbolic reference → ``Symbol``), with all netlist-derived symbol names
lower-cased (SPICE is case-insensitive, so this is collision-free and makes device-card refs match
global ``.param`` names). Net names are case-insensitive for the same reason: spellings that differ
only in case are one net, which keeps the deck's first top-level spelling (device order). A subckt
body may spell a formal port in either case, and the ``ports=`` nets and ``ground`` take the deck's
spelling.
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import replace
from pathlib import Path

import sympy as sp
from spicexplorer_core.eng import parse_value
from spicexplorer_core.spice_eng import spice_number
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
# (XM/XR/XC/XL) are treated as the primitive they wrap; a bare X… is an opaque subckt instance —
# unless its MODEL name names a MOS, which wins over the prefix (see `_x_wrapped_mos`).
_MOS_PREFIXES = ("M", "XM")
_RES_PREFIXES = ("R", "XR")
_CAP_PREFIXES = ("C", "XC")
_IND_PREFIXES = ("L", "XL")

# MOSFET / BJT pin orders (spicelib's node order for an M/Q card).
_MOS_PINS = (PinRole.DRAIN, PinRole.GATE, PinRole.SOURCE, PinRole.BULK)
_MOS_PINS_NO_BULK = (PinRole.DRAIN, PinRole.GATE, PinRole.SOURCE)
_TWO_TERMINAL = (PinRole.PLUS, PinRole.MINUS)
_CONTROLLED = (PinRole.PLUS, PinRole.MINUS, PinRole.CONTROL_PLUS, PinRole.CONTROL_MINUS)
#: The forms of a ``G`` card that are not one linear gain (behavioral, polynomial, table, Laplace).
_NONLINEAR_G = re.compile(r"(value|poly|table|laplace|freq|cur|vccs)\b", re.IGNORECASE)

# A source spec that opens with a transient function (``pulse(0 1 …)``, ``sin({VCM} …)``) has no
# bare DC token to read — its small-signal value is 0 either way.
_TRANSIENT_FN = re.compile(r"(pulse|sin|exp|pwl|sffm|am|trnoise|trrandom)\s*\(", re.IGNORECASE)
_SIGNED_INF = re.compile(r"([+-]?)inf(inity)?", re.IGNORECASE)


# ------------------------------------------------------------------------
# Value sympification
# ------------------------------------------------------------------------
def _lower_symbols(expr: sp.Expr) -> sp.Expr:
    """Lower-case every symbol name in ``expr`` (SPICE is case-insensitive → canonical form)."""
    subs = {s: sp.Symbol(str(s).lower()) for s in expr.free_symbols if str(s) != str(s).lower()}
    return expr.xreplace(subs) if subs else expr


def _try_eng(s: str) -> float | None:
    """SPICE-correct, case-insensitive engineering parse; ``None`` if ``s`` is not numeric.

    Delegates to the workspace's one netlist-value table
    (:func:`spicexplorer_core.spice_eng.spice_number`). This was a second, private copy of those
    scale factors, and it was only ever reached as a FALLBACK — the DSL parser ran first, so an
    upper-case ``M`` never got here and was read as *mega* where the rest of the workspace reads a
    netlist ``M`` as *milli* (Codex review, item TF-01).

    ``spice_number`` raises on a token written entirely out of number characters that is still not a
    number (``1.2.3``). Here that is not an error: the caller falls through to a symbolic parse for
    anything non-numeric, and ``None`` keeps that path open.
    """
    try:
        return spice_number(s)
    except ValueError:
        return None


def _as_number(num: float) -> sp.Expr:
    """A parsed netlist number as an EXACT sympy number — ``Integer``/``Rational``, never ``Float``.

    ``spice_number`` scales the token's decimal mantissa in ``Decimal`` and returns the nearest
    double; that double's ``repr`` is its shortest round-tripping decimal, which is the literal the
    deck wrote (``2.7p`` → ``27/10**13``) for any value of up to 15 significant digits. Not
    ``sp.Rational(num)`` (the double's exact binary fraction) and not ``nsimplify`` (a heuristic).

    With ``Float`` entries ``cancel`` could not cancel exactly: its round-off survived as tiny
    leading coefficients, and ``describe_tf`` rooted them into phantom poles/zeros at 1e18..1e32
    rad/s — a passive RC ladder grew two zeros, a capacitor loop a fourth pole (audit LEAF-F06).
    Numbers become floats only where they are evaluated (describe / numeric / pencil).
    """
    if math.isinf(num):  # int(inf) raises OverflowError, which no caller's except tuple catches
        return sp.oo if num > 0 else -sp.oo
    if math.isnan(num):  # sp.Rational raises TypeError here; keep the ValueError callers expect
        raise ValueError(f"{num!r} is not a value")
    return sp.Rational(repr(num))


def _unwrap(s: str) -> str:
    """Strip SPICE expression delimiters: braces, and a matching pair of single or double quotes.

    analog-db exports design variables quoted (``C0 a b 'CAPACITOR_0'``); left on, the quotes made
    sympy read a Python string literal and ingestion crashed (audit item ROAD-02).
    """
    while True:
        s = s.strip("{}").strip()  # SPICE brace-expressions
        if len(s) >= 2 and s[0] == s[-1] and s[0] in "'\"":
            s = s[1:-1].strip()
            continue
        return s


def sympify_value(raw: object) -> sp.Expr:
    """Parse one SPICE value token into a sympy ``Expr``.

    Numeric (with optional engineering suffix, e.g. ``"50f"``, ``"0.18u"``, ``"0P"``, ``1.5``) → an
    exact sympy ``Rational``/``Integer`` (``"inf"`` and ``"+inf"`` → ``sp.oo``, ``"-inf"`` →
    ``-sp.oo``). A symbolic reference or expression (``"CL"``, ``"{2*W}"``, ``"'2*W'"``,
    ``"x_dut_nfet_input_w"``) → the corresponding symbolic ``Expr`` with lower-cased symbol names.
    A token that parses to something other than an expression (a bool, a tuple), or to NaN or a
    complex infinity (``"nan"``, ``"1/0"``), raises ``ValueError``.
    """
    if isinstance(raw, bool):  # guard: bool is an int subclass
        return sp.Integer(int(raw))
    if isinstance(raw, (int, float)):
        return _as_number(float(raw))
    s = str(raw).strip()
    if not s:
        raise ValueError("empty value token")
    s = _unwrap(s)
    if not s:
        raise ValueError(f"empty value token {raw!r}")
    # SPICE semantics FIRST. This function parses NETLIST tokens, and in a netlist the scale
    # factors are case-insensitive with `M` = milli and `meg` the only mega. Trying core's
    # parse_value first instead — the YAML DSL's parser, deliberately case-SENSITIVE with
    # `M` = mega — meant `1M` came back as 1e6, a factor of 10⁹ away from what circuitgraph reads
    # from the same token (Codex review, item TF-01).
    eng = _try_eng(s)
    if eng is not None:
        return _as_number(eng)
    # A signed infinity, as 'inf' is read: the DSL parser below reads '-inf' as '-in' femto and
    # fails, and the symbolic parse took the 'inf' of '-inf' for a name (L-PF-5).
    inf = _SIGNED_INF.fullmatch(s)
    if inf:
        return -sp.oo if inf.group(1) == "-" else sp.oo
    # Then the DSL parser, for the forms it alone accepts.
    try:
        return _as_number(float(parse_value(s)))
    except (ValueError, TypeError):
        pass
    # Symbolic reference / expression.
    expr = sp.sympify(s, rational=True)  # type: ignore[call-overload]
    if not isinstance(expr, sp.Expr):
        # e.g. 'True' → a sympy bool, '(1, 2)' → a Tuple; _lower_symbols needs an Expr
        raise ValueError(
            f"value token {raw!r} is not an expression (parsed as {type(expr).__name__})"
        )
    if expr.has(sp.nan, sp.zoo):  # 'nan', '1/0': refused, as a NaN number is by _as_number
        raise ValueError(f"value token {raw!r} is not a value (parsed as {expr})")
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


def _x_wrapped_mos(view: NetlistView, ref: str, nets: list[str]) -> str | None:
    """The MOS model an ``X…`` instance wraps, or ``None`` if it does not wrap one.

    PDK primitives ship as subckt wrappers, so a MOSFET's reference designator is only *by
    convention* ``XM…``: a replica device called ``xr1`` or a dummy called ``xd3`` is still a
    transistor. Type those by the **model name** — the letter after the ``X`` carries no
    information — so ``xr1 … sg13_hv_pmos`` lands as a PMOS exactly like ``xm1 … sg13_hv_pmos``
    already does. Deliberately strict: 3–4 terminals, and the model must actually match
    :func:`_mos_kind`'s ``nmos``/``pmos``/``nfet``/``pfet`` patterns.
    """
    if not ref.upper().startswith("X") or len(nets) not in (3, 4):
        return None
    model = view.get_component_value(ref)
    # _mos_kind falls back to the untyped DeviceKind.MOS; anything else is a positive match.
    return model if model and _mos_kind(model) is not DeviceKind.MOS else None


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
                # a dropped `ac` hides the stimulus from detect_ac_input — say so (audit TF-4)
                logger.warning("ref %s: could not parse %s value %r; dropped", ref, kw, toks[i + 1])
            i += 2
            continue
        i += 1
    # A bare leading token (no dc/ac keyword) is the DC value, e.g. 'IBIAS' or '0'. A transient
    # function is not one: skipping it is not a dropped token, so it does not warn.
    if not saw_kw and toks and not _TRANSIENT_FN.match(spec):
        try:
            out["dc"] = sympify_value(toks[0])
        except (ValueError, TypeError, sp.SympifyError):
            logger.warning("ref %s: could not parse dc value %r; dropped", ref, toks[0])
    return out


def _terminals(roles: tuple[PinRole, ...], nets: list[str]) -> tuple[Terminal, ...]:
    return tuple(Terminal(role, net) for role, net in zip(roles, nets))


def build_device(view: NetlistView, ref: str) -> Device:
    """Type one reference designator into a :class:`Device` (dispatch by prefix)."""
    ref_u = ref.upper()
    nets = view.get_component_nodes(ref)

    if ref_u.startswith(_MOS_PREFIXES) or _x_wrapped_mos(view, ref, nets):
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

    if ref_u.startswith("G") and len(nets) == 2:
        vccs = _vccs(view, ref, nets)
        if vccs is not None:
            return vccs

    if ref_u.startswith("V") and len(nets) == 2:
        return Device(
            ref,
            DeviceKind.VSOURCE,
            _terminals(_TWO_TERMINAL, nets),
            model=None,
            params=_source_params(view, ref),
        )
    if ref_u.startswith("I") and len(nets) == 2:
        return Device(
            ref,
            DeviceKind.ISOURCE,
            _terminals(_TWO_TERMINAL, nets),
            model=None,
            params=_source_params(view, ref),
        )

    return _opaque_device(view, ref, nets)


def _two_terminal(view: NetlistView, ref: str, nets: list[str], kind: DeviceKind) -> Device:
    """An R/C/L: the element value is its ``get_component_value`` token, kept under ``params['value']``."""
    params = _geometry_params(view, ref)
    try:
        params["value"] = sympify_value(view.get_component_value(ref))
    except (ValueError, TypeError, sp.SympifyError):
        params["value"] = sp.Symbol(f"{ref.lower()}_value")
    return Device(ref, kind, _terminals(_TWO_TERMINAL, nets), model=None, params=params)


def _vccs(view: NetlistView, ref: str, nets: list[str]) -> Device | None:
    """A linear ``G`` card (``G1 n+ n- nc+ nc- value``) as a :class:`DeviceKind.VCCS`, or ``None``.

    The parser hands back the output pair as the nodes and ``nc+ nc- value`` as the value string;
    the value is sympified like any other (``{gm_val}`` → the symbol ``gm_val``). A behavioral,
    polynomial, table or Laplace form is not one linear gain and returns ``None`` (it stays an
    unmodelled ``UNKNOWN`` device, listed in ``unmodelled``).
    """
    toks = str(view.get_component_value(ref)).split(None, 2)
    if len(toks) != 3 or _NONLINEAR_G.match(toks[0]) or "=" in toks[2]:
        return None
    try:
        value = sympify_value(toks[2])
    except (ValueError, TypeError, sp.SympifyError):
        logger.warning("ref %s: could not sympify the VCCS gain %r; kept unmodelled", ref, toks[2])
        return None
    return Device(
        ref,
        DeviceKind.VCCS,
        _terminals(_CONTROLLED, [*nets, toks[0], toks[1]]),
        model=None,
        params={"value": value},
    )


def _opaque_device(view: NetlistView, ref: str, nets: list[str]) -> Device:
    """A subckt instance or an unhandled element: positional PORT terminals, model = referenced name."""
    kind = DeviceKind.SUBCKT if ref.upper().startswith("X") else DeviceKind.UNKNOWN
    roles = tuple(PinRole.PORT for _ in nets)
    model = view.get_component_value(ref) if kind is DeviceKind.SUBCKT else None
    logger.debug("ref %s typed as %s (%d ports)", ref, kind.value, len(nets))
    return Device(
        ref, kind, _terminals(roles, nets), model=model, params=_geometry_params(view, ref)
    )


# ------------------------------------------------------------------------
# Subckt flatten (plan §4: flatten via get_subcircuit, rename with a `_<inst>` postfix)
# ------------------------------------------------------------------------
_FLATTEN_MAX_DEPTH = 8


def _rename_for_instance(dev: Device, suffix: str, net_map: dict[str, str]) -> Device:
    """Re-home a definition-level device into the parent level: formal-port nets map to the
    instance's actual nets, AC-ground nets (global by convention) keep their names, and every
    other (internal) net/ref gets the per-instance postfix so instances never collide."""

    def map_net(n: str) -> str:
        if n.lower() in net_map:  # net_map is keyed lower-case (SPICE names are case-insensitive)
            return net_map[n.lower()]
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
            dev.ref,
            dev.model,
            formals,
            len(actuals),
        )
        return None

    suffix = f"_{dev.ref.lower()}"
    # keyed by the lower-cased formal: a body may spell a port in another case than its header
    net_map = {f.lower(): a for f, a in zip(formals, actuals)}
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


def _fold_nets(dev: Device, canon: dict[str, str]) -> Device:
    """``dev`` with every terminal net replaced by its canonical spelling (``canon`` is keyed by the
    lower-cased name)."""
    terminals = tuple(Terminal(t.role, canon[t.net.lower()]) for t in dev.terminals)
    return dev if terminals == dev.terminals else replace(dev, terminals=terminals)


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
    reference-node name. Net names are case-insensitive: each net keeps the deck's first spelling,
    and the ``ports`` nets and ``ground`` are stored in that spelling.

    ``flatten`` (default on) steps into every resolvable ``X…`` subckt instance and splices its
    devices in with a ``_<inst>`` postfix on internal nets/refs, so a *testbench-level* netlist
    ingests as one flat circuit. An instance whose definition can't be resolved stays opaque (the
    pre-flatten behavior), as does any subckt named in ``keep_opaque`` (case-insensitive) — the
    hook for behavioral/registered models.
    """
    keep = {k.lower() for k in keep_opaque}
    canon: dict[str, str] = {}  # lower-cased net name -> the one spelling kept for it
    devices_list: list[Device] = []
    for ref in view.get_components():
        d = build_device(view, ref)
        for t in d.terminals:  # top-level spellings first: a subckt body never renames a deck net
            canon.setdefault(t.net.lower(), t.net)
        if flatten and d.kind is DeviceKind.SUBCKT and (d.model or "").lower() not in keep:
            expanded = _flatten_subckt(view, d, keep_opaque=keep, depth=_FLATTEN_MAX_DEPTH)
            if expanded is not None:
                devices_list.extend(expanded)
                continue
            logger.warning("subckt instance %s (%s) not flattened; kept opaque", d.ref, d.model)
        devices_list.append(d)
    # SPICE net names are case-insensitive: spellings that differ only in case are one net. It keeps
    # the first top-level spelling in device order, else a subckt body's first one, so a deck
    # spelled in one case comes through unchanged.
    for n in sorted(view.get_all_nodes()):
        canon.setdefault(n.lower(), n)
    for d in devices_list:
        for t in d.terminals:
            canon.setdefault(t.net.lower(), t.net)
    devices = tuple(_fold_nets(d, canon) for d in devices_list)

    nets = {
        canon[n.lower()]: Net(canon[n.lower()], classify_net_role(n)) for n in view.get_all_nodes()
    }
    for d in devices:  # flattened-internal nets exist only on devices, not on the top view
        for t in d.terminals:
            if t.net not in nets:
                nets[t.net] = Net(t.net, classify_net_role(t.net))
    port_pairs = {
        k: PortPair(canon.get(v[0].lower(), v[0]), canon.get(v[1].lower(), v[1]))
        for k, v in (ports or {}).items()
    }
    params = _global_params(view)

    ir = Circuit2TF(
        name=name,
        nets=nets,
        devices=devices,
        ports=port_pairs,
        params=params,
        ground=canon.get(ground.lower(), ground),
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
    return ingest_netlist(
        view,
        name=name or Path(path).stem,
        ports=ports,
        ground=ground,
        flatten=flatten,
        keep_opaque=keep_opaque,
    )


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
    return ingest_netlist(
        NetlistView.from_string(text),
        name=name,
        ports=ports,
        ground=ground,
        flatten=flatten,
        keep_opaque=keep_opaque,
    )
