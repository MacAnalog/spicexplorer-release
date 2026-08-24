"""DUT parameterization — atomic inventory + structural group detection + tie lowering.

This module separates what CAN vary (the atomic
per-instance inventory, a physical fact of the topology) from what SHOULD vary together
(``groups:``/``ratios:`` — shipped *default* tying, tagged with machine-readable reasons).
The contract is ``_shared/schema/params.schema.json`` (``spicexplorer/params@1``).

Pure functions over a committed ``abstract/topology.cgraph.json`` document that

- derive the mechanical atomic symbol inventory (``x_dut_<id>_<field>``),
- structurally detect the default-tying candidates (matched pairs + current mirrors),
- assemble / refresh a schema-valid ``spicexplorer/params@1`` document (``gen-params``:
  generated-then-reviewed — ``devices:`` is regenerated mechanically, authored ``groups:``/
  ``ratios:`` are preserved verbatim), and
- lower the tying layer to ``.param`` lines: one
  ``.param <member_sym> = {<first_member_sym>}`` per tied member-field plus
  ``.param <ref_sym> = {<of_sym>*N/D}`` per ratio. A tied symbol is defined exactly ONCE (by
  its tie line), so redefining the atomic symbol upstream overrides just that symbol
  (*untying = shadowing*); the FREE symbols (:func:`free_symbols`) are the knobs
  ``pdk/<pdk>/sizing.yaml`` keys on.

Nothing here writes files (the CLI does).

Settled decisions: per-finger ``(w, m)`` is canonical (total-W is derived, never
stored); generation lives in this package (the artifact owner); ties lower to ``.param`` lines
referencing the FIRST member's atomic symbols (group names never appear in decks).

Detection heuristics (deliberately structural, no design opinion):

- **current mirror** — a diode-connected MOS reference (gate net == drain net) plus every
  same-polarity, non-diode MOS sharing its gate AND source nets → ``kind: mirror_length``
  group tying ``[l]``, plus one ``ratios:`` entry per output when both ``m`` are numeric.
- **matched pair** — exactly two same-polarity, non-diode MOS sharing source and bulk nets
  (the shared source must NOT be a supply — a differential/tail node) with distinct gate and
  distinct drain nets → ``kind: matched_pair`` group tying ``[w, l, m]``.

A detected-but-untied symmetry is a *warning* upstream, never a failure — these are
proposals to be reviewed, not truths.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from . import yamlio

__all__ = [
    "atomic_symbol",
    "knob_symbol",
    "value_symbols",
    "atomic_inventory",
    "detect_mirrors",
    "detect_matched_pairs",
    "propose_params_doc",
    "refresh_params_doc",
    "render_params_yaml",
    "load_graph",
    "load_params_doc",
    "tie_param_lines",
    "tied_symbols",
    "free_symbols",
    "netlist_symbols",
    "untied_symmetries",
]

SCHEMA_ID = "spicexplorer/params@1"

# a params value that is a SYMBOL (vs a frozen numeric literal, which may also be a string
# like "0.5u" in foreign netlists — an identifier never starts with a digit).
_SYMBOL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load_graph(path: str | Path) -> dict[str, Any]:
    """Load a committed ``abstract/topology.cgraph.json`` document."""
    with Path(path).open() as fh:
        return json.load(fh)


def load_params_doc(circuit_dir: str | Path) -> dict[str, Any] | None:
    """The committed ``abstract/params.yaml``, or ``None`` where the circuit hasn't adopted the
    tying layer yet (adoption is per circuit — absence is not an error)."""
    p = Path(circuit_dir) / "abstract" / "params.yaml"
    if not p.is_file():
        return None
    doc = yamlio.read_yaml(p)
    if not isinstance(doc, dict):
        raise ValueError(f"{p}: expected a YAML mapping, got {type(doc).__name__}")
    return doc


# --------------------------------------------------------------------------- atomic inventory


def atomic_symbol(instance_id: str, field: str) -> str:
    """The mechanically-derived, collision-free atomic symbol for one device field.

    The ``x_dut_`` prefix is kept only for the platform's display grouping heuristic
    (``_is_dut_param`` is DISPLAY-ONLY); nothing in the run path branches on it.
    """
    return f"x_dut_{instance_id.lower()}_{field.lower()}"


def knob_symbol(value: Any) -> str | None:
    """The single free-knob symbol a netlist parameter value binds, or ``None``.

    Handles the value forms the corpus actually uses: a bare symbol (``x_rl``), a quoted
    symbol (``'c_comp'`` — ngspice needs the quotes on R/C value fields), and a source's
    dc-braced form (``dc {i_tail}`` / ``{vref_val}``). Numbers and real expressions
    (``'sym*8'``) yield ``None``."""
    if isinstance(value, (int, float)):
        return None
    s = str(value).strip()
    if len(s) >= 2 and s.startswith("'") and s.endswith("'"):
        s = s[1:-1].strip()
    s = re.sub(r"^dc\s+", "", s, flags=re.I)
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1].strip()
    return s if _SYMBOL_RE.match(s) else None


# A SUBCKT instance's master/model name rides in its ``Value`` param (e.g.
# ``XQ1 c b e s npn13G2 Nx=3`` -> params {Nx: x_dut_nx, Value: 'npn13G2'}). It
# is a device reference, NOT a tunable knob — excluded from the inventory and
# the symbol closure so it never looks like a free ``.param``.
_SUBCKT_MASTER_FIELD = "Value"

# Identifiers inside a braced engineering expression. A unit-suffixed literal
# like ``1f`` / ``2e-12`` is not a leading-letter token, so it is not matched.
_EXPR_SYMBOL_RE = re.compile(r"\b[A-Za-z_]\w*\b")


def value_symbols(value: Any) -> set[str]:
    """Every free-knob symbol a netlist parameter value binds.

    The single symbol of the simple forms :func:`knob_symbol` handles (bare,
    quoted, ``dc {..}``, ``{sym}``), PLUS symbols embedded in a braced
    ENGINEERING EXPRESSION (``{x_dut_cdeg_ff*1f}`` -> ``{"x_dut_cdeg_ff"}``).
    Numeric literals and plain non-symbol strings yield the empty set. This is
    the expression-aware superset of :func:`knob_symbol` used by the symbol
    closure + free-symbol machinery (a knob may hide inside a unit conversion)."""
    one = knob_symbol(value)
    if one is not None:
        return {one}
    if isinstance(value, (int, float)):
        return set()
    s = str(value).strip()
    if len(s) >= 2 and s.startswith("{") and s.endswith("}"):
        return set(_EXPR_SYMBOL_RE.findall(s[1:-1]))
    return set()


def atomic_inventory(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The exhaustive atomic inventory: instance id -> {field -> atomic symbol or literal}.

    One row per component in the graph, one entry per parameter field the component's netlist
    card carries. Purely mechanical — no design opinion, no tying:

    - **MOS** geometry fields always get the mechanical ``x_dut_<id>_<field>`` symbol —
      on an unmigrated netlist this IS the migration proposal.
    - **Everything else** (passives, V/I bias sources) is echoed honestly from the netlist:
      the free-knob symbol the card already binds (``i_tail``, ``vref_val``, ``'c_comp'`` —
      bias-branch values are already free params and stay first-class knobs), a
      numeric literal verbatim, or the raw value string when nothing extractable remains.
    """
    inv: dict[str, dict[str, Any]] = {}
    for comp in sorted(graph["components"], key=lambda c: c["id"]):
        cid = comp["id"]
        params = comp.get("params") or {}
        if comp.get("device_type") == "MOS":
            inv[cid] = {f: atomic_symbol(cid, f) for f in sorted(params)}
        else:
            is_subckt = comp.get("device_type") == "SUBCKT"
            row: dict[str, Any] = {}
            for f in sorted(params):
                if is_subckt and f == _SUBCKT_MASTER_FIELD:
                    continue  # master/model name is a device ref, not a knob
                v = params[f]
                if isinstance(v, (int, float)):
                    row[f] = v
                else:
                    row[f] = knob_symbol(v) or str(v)
            inv[cid] = row
    return inv


# --------------------------------------------------------------------------- structure helpers


def _mos(graph: dict[str, Any]) -> list[dict[str, Any]]:
    return [c for c in graph["components"] if c.get("device_type") == "MOS"]


def _is_diode_connected(comp: dict[str, Any]) -> bool:
    conn = comp.get("connections") or {}
    gate, drain = conn.get("GATE"), conn.get("DRAIN")
    return gate is not None and gate == drain


def _supply_nets(graph: dict[str, Any]) -> set[str]:
    return {n["name"] for n in graph.get("nets", []) if n.get("is_supply")}


@dataclass(frozen=True)
class Mirror:
    """A structurally-detected current mirror: diode reference + its output devices."""

    ref: str
    outputs: tuple[str, ...]
    polarity: str


@dataclass(frozen=True)
class MatchedPair:
    """A structurally-detected symmetric pair (shared non-supply source, distinct gates/drains)."""

    a: str
    b: str
    polarity: str


def detect_mirrors(graph: dict[str, Any]) -> list[Mirror]:
    """Every diode-connected MOS + the same-polarity non-diode devices on its gate/source nets."""
    mos = _mos(graph)
    out: list[Mirror] = []
    for ref in sorted(mos, key=lambda c: c["id"]):
        if not _is_diode_connected(ref):
            continue
        rconn = ref["connections"]
        outputs = sorted(
            c["id"]
            for c in mos
            if c["id"] != ref["id"]
            and c.get("polarity") == ref.get("polarity")
            and not _is_diode_connected(c)
            and c["connections"].get("GATE") == rconn.get("GATE")
            and c["connections"].get("SOURCE") == rconn.get("SOURCE")
        )
        if outputs:
            out.append(Mirror(ref=ref["id"], outputs=tuple(outputs), polarity=ref["polarity"]))
    return out


def detect_matched_pairs(graph: dict[str, Any]) -> list[MatchedPair]:
    """Exactly-two same-polarity non-diode MOS sharing a NON-supply source net + bulk net."""
    supplies = _supply_nets(graph)
    buckets: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for c in _mos(graph):
        if _is_diode_connected(c):
            continue
        conn = c["connections"]
        src = conn.get("SOURCE")
        if src is None or src in supplies:
            continue
        key = (c.get("polarity") or "", src, conn.get("BULK") or "")
        buckets.setdefault(key, []).append(c)

    pairs: list[MatchedPair] = []
    for (pol, _src, _blk), members in sorted(buckets.items()):
        if len(members) != 2:
            continue  # spike scope: only unambiguous 2-member symmetry
        a, b = sorted(members, key=lambda c: c["id"])
        if a["connections"].get("GATE") == b["connections"].get("GATE"):
            continue  # same gate = mirror-like, not a differential pair
        if a["connections"].get("DRAIN") == b["connections"].get("DRAIN"):
            continue
        pairs.append(MatchedPair(a=a["id"], b=b["id"], polarity=pol))
    return pairs


# --------------------------------------------------------------------------- proposed document


def _ratio_value(m_out: Any, m_ref: Any) -> int | str | None:
    """Exact m-ratio as an int or reduced-fraction string; None if either m is symbolic."""
    if not isinstance(m_out, (int, float)) or not isinstance(m_ref, (int, float)):
        return None
    frac = Fraction(m_out).limit_denominator(10**6) / Fraction(m_ref).limit_denominator(10**6)
    if frac.denominator == 1:
        return int(frac)
    return f"{frac.numerator}/{frac.denominator}"


def propose_params_doc(graph: dict[str, Any]) -> dict[str, Any]:
    """Assemble a deterministic, schema-valid proposed ``spicexplorer/params@1`` document.

    ``devices:`` is the mechanical truth; ``groups:``/``ratios:`` are *proposals* from the
    structural detectors, meant to be reviewed by a human (generated-then-reviewed)
    so the shipped defaults reproduce today's knob set before they land.
    """
    by_id = {c["id"]: c for c in graph["components"]}
    groups: list[dict[str, Any]] = []
    ratios: list[dict[str, Any]] = []

    for p in detect_matched_pairs(graph):
        groups.append(
            {
                "name": f"pair_{p.a.lower()}_{p.b.lower()}",
                "kind": "matched_pair",
                "members": [p.a, p.b],
                "tie": ["w", "l", "m"],
            }
        )

    for m in detect_mirrors(graph):
        groups.append(
            {
                "name": f"mirror_{m.ref.lower()}_l",
                "kind": "mirror_length",
                "members": [m.ref, *m.outputs],
                "tie": ["l"],
            }
        )
        ref_m = (by_id[m.ref].get("params") or {}).get("m")
        for out_id in m.outputs:
            val = _ratio_value((by_id[out_id].get("params") or {}).get("m"), ref_m)
            if val is not None:
                ratios.append({"param": "m", "ref": out_id, "of": m.ref, "ratio": val})

    doc: dict[str, Any] = {"schema": SCHEMA_ID, "devices": atomic_inventory(graph)}
    if groups:
        doc["groups"] = sorted(groups, key=lambda g: g["name"])
    if ratios:
        doc["ratios"] = sorted(ratios, key=lambda r: (r["of"], r["ref"], r["param"]))
    return doc


def refresh_params_doc(existing: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    """Generated-then-reviewed refresh (P1): ``devices:`` is re-derived mechanically from the
    graph; the AUTHORED ``groups:``/``ratios:`` are preserved verbatim (they are the human
    review the generator must never clobber)."""
    doc: dict[str, Any] = {"schema": SCHEMA_ID, "devices": atomic_inventory(graph)}
    if existing.get("groups"):
        doc["groups"] = existing["groups"]
    if existing.get("ratios"):
        doc["ratios"] = existing["ratios"]
    return doc


_PARAMS_HEADER = (
    "# {cid} — DUT parameterization (spicexplorer/params@1; contract: _shared/PARAMS.md).\n"
    "# `devices:` is GENERATED from abstract/topology.cgraph.json — refresh with\n"
    "# `analog-db gen-params --circuit {cid} --write` (it preserves the authored sections).\n"
    "# `groups:`/`ratios:` are AUTHORED default tying, reviewed by a human (plan D-2):\n"
    "# recommendations tagged with WHY, which an upstream user may accept, edit, or dissolve.\n"
)


def render_params_yaml(doc: dict[str, Any], circuit_id: str) -> str:
    """Deterministic YAML for ``abstract/params.yaml``: canonical top-level key order
    (schema, devices, groups, ratios), sorted inventory (by construction), authored group/ratio
    order preserved, ``yaml.safe_dump``-stable."""
    ordered: dict[str, Any] = {"schema": doc["schema"], "devices": doc["devices"]}
    for key in ("groups", "ratios"):
        if doc.get(key):
            ordered[key] = doc[key]
    return _PARAMS_HEADER.format(cid=circuit_id) + yaml.safe_dump(
        ordered, sort_keys=False, width=100, default_flow_style=None, allow_unicode=True
    )


# --------------------------------------------------------------------------- lowering


def tie_param_lines(doc: dict[str, Any]) -> list[str]:
    """The generated tie block, one ``.param`` line per tied member-field (P2, PARAMS.md §3).

    Group ties reference the FIRST member's atomic symbol (group names never appear in decks);
    ratios lower to ``.param <ref_sym> = {<of_sym>*<ratio>}``. A frozen numeric literal in a
    ``devices:`` row has no symbol, so it never produces (or anchors) a tie line."""
    devices: dict[str, Any] = doc.get("devices") or {}

    def _sym(instance: Any, field: Any) -> str | None:
        val = (devices.get(instance) or {}).get(field)
        return val if isinstance(val, str) and _SYMBOL_RE.match(val) else None

    lines: list[str] = []
    for g in doc.get("groups") or []:
        members = g.get("members") or []
        if len(members) < 2:
            continue
        for field in g.get("tie") or []:
            first_sym = _sym(members[0], field)
            if first_sym is None:
                continue
            for member in members[1:]:
                sym = _sym(member, field)
                if sym is not None and sym != first_sym:
                    lines.append(f".param {sym} = {{{first_sym}}}")
    for rt in doc.get("ratios") or []:
        ref_sym = _sym(rt.get("ref"), rt.get("param"))
        of_sym = _sym(rt.get("of"), rt.get("param"))
        if ref_sym is not None and of_sym is not None:
            lines.append(f".param {ref_sym} = {{{of_sym}*{rt.get('ratio')}}}")
    return lines


def tie_expressions(doc: dict[str, Any]) -> dict[str, str]:
    """The tie block as data: ``{tied symbol: defining expression}`` (``x_dut_xm2_w`` →
    ``"x_dut_xm1_w"``, a ratio ref → ``"<of_sym>*17/3"``) — for numeric resolvers (PPA area,
    parity checks) that must see through the ties without running SPICE."""
    out: dict[str, str] = {}
    for ln in tie_param_lines(doc):
        head, _, rhs = ln.partition("=")
        out[head.split()[1]] = rhs.strip().strip("{}")
    return out


def tied_symbols(doc: dict[str, Any]) -> set[str]:
    """The symbols DEFINED by the generated tie block (non-first tied members + ratio refs) —
    exactly the inventory symbols that must NOT get a ``sizing.yaml`` row (they'd be
    double-defined)."""
    return {ln.split()[1] for ln in tie_param_lines(doc)}


def free_symbols(doc: dict[str, Any]) -> set[str]:
    """The FREE symbols after default tying — the knobs ``sizing.yaml`` keys on:
    every inventory symbol not defined by a tie line (first members + untied atomics)."""
    inventory: set[str] = set()
    for fields in (doc.get("devices") or {}).values():
        if isinstance(fields, dict):
            for v in fields.values():
                inventory |= value_symbols(v)
    return inventory - tied_symbols(doc)


def ratio_symbols(doc: dict[str, Any]) -> set[str]:
    """The symbols defined by ``ratios:`` lines (the derived ``ref`` instances) — a subset of
    :func:`tied_symbols`, split out so provenance reporting can tell ties from ratio gains."""
    devices: dict[str, Any] = doc.get("devices") or {}

    def _sym(instance: Any, field: Any) -> str | None:
        val = (devices.get(instance) or {}).get(field)
        return val if isinstance(val, str) and _SYMBOL_RE.match(val) else None

    out: set[str] = set()
    for rt in doc.get("ratios") or []:
        ref_sym, of_sym = _sym(rt.get("ref"), rt.get("param")), _sym(rt.get("of"), rt.get("param"))
        if ref_sym is not None and of_sym is not None:
            out.add(ref_sym)
    return out


def classify_symbols(
    doc: dict[str, Any], sizing_variables: list[dict[str, Any]] | None = None
) -> dict[str, tuple[str, ...]]:
    """Provenance classes for every inventory symbol — the info surface the owner reviews
    (per-circuit in ``catalog.json``, per-PDK in Tier-1, per-deck in the banner).

    - ``free``   — the optimizer-addressable knobs (``sizing.yaml`` rows, ``freeze`` falsy)
    - ``frozen`` — value-defined but excluded from search (``freeze: true`` sizing rows)
    - ``tied``   — defined once by a group tie line (``{first member's symbol}``)
    - ``ratio``  — defined once by a ``ratios:`` gain line (``{of_symbol*N/D}``)

    Without ``sizing_variables`` (the PDK-neutral view, e.g. ``gen-params``) every non-tied
    symbol lands in ``free`` — freeze flags are a per-PDK ``sizing.yaml`` fact.
    """
    ratio = ratio_symbols(doc)
    tied = tied_symbols(doc) - ratio
    free = free_symbols(doc)
    frozen: set[str] = set()
    if sizing_variables:
        frozen = {v["name"] for v in sizing_variables if v.get("freeze") and v.get("name") in free}
    return {
        "free": tuple(sorted(free - frozen)),
        "frozen": tuple(sorted(frozen)),
        "tied": tuple(sorted(tied)),
        "ratio": tuple(sorted(ratio)),
    }


def counts_line(cls: dict[str, tuple[str, ...]], tb_params: int | None = None) -> str:
    """One human line for a classification, e.g.
    ``8 free + 4 frozen knobs (sizing.yaml) · 6 tied · 0 ratio-derived (abstract/params.yaml)``,
    plus ``· N testbench params`` when a deck-level count is supplied."""
    line = (
        f"{len(cls['free'])} free + {len(cls['frozen'])} frozen knobs (sizing.yaml) · "
        f"{len(cls['tied'])} tied · {len(cls['ratio'])} ratio-derived (abstract/params.yaml)"
    )
    if tb_params is not None:
        line += f" · {tb_params} testbench params"
    return line


def netlist_symbols(graph: dict[str, Any]) -> set[str]:
    """Every parameter SYMBOL the abstract netlist cards actually use (numeric literals and
    engineering strings excluded) — must be covered by the inventory (Tier-1 symbol closure)."""
    out: set[str] = set()
    for comp in graph.get("components", []):
        is_subckt = comp.get("device_type") == "SUBCKT"
        for f, val in (comp.get("params") or {}).items():
            if is_subckt and f == _SUBCKT_MASTER_FIELD:
                continue  # subckt master/model name is a device ref, not a symbol
            out |= value_symbols(val)
    return out


# --------------------------------------------------------------------------- untied symmetry


def detected_tie_candidates(graph: dict[str, Any]) -> list[tuple[str, frozenset[str], frozenset[str]]]:
    """``(label, members, tie-fields)`` for every structurally detected symmetry — the
    candidates a ``groups:`` review either ties or (deliberately) leaves atomic."""
    out: list[tuple[str, frozenset[str], frozenset[str]]] = []
    for p in detect_matched_pairs(graph):
        out.append(
            (f"matched_pair {p.a}+{p.b}", frozenset({p.a, p.b}), frozenset({"w", "l", "m"}))
        )
    for m in detect_mirrors(graph):
        out.append(
            (
                f"mirror {m.ref}→{','.join(m.outputs)}",
                frozenset({m.ref, *m.outputs}),
                frozenset({"l"}),
            )
        )
    return out


def untied_symmetries(graph: dict[str, Any], doc: dict[str, Any]) -> list[str]:
    """Detected-but-untied symmetry candidates: a WARNING upstream,
    never a failure — these are proposals a reviewer may have deliberately declined (e.g. a tail
    mirror shipped as independent knobs)."""
    groups = doc.get("groups") or []
    out: list[str] = []
    for label, members, fields in detected_tie_candidates(graph):
        covered = any(
            members <= set(g.get("members") or []) and fields <= set(g.get("tie") or [])
            for g in groups
        )
        if not covered:
            out.append(f"{label} (tie {','.join(sorted(fields))})")
    return out
