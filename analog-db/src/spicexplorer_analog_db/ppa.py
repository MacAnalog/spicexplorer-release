"""PPA extraction — the scoreboard's Power / Performance / Area axes.

Pure functions over committed artifacts; no simulation:

  - :func:`area_report` — **active gate area** = Σ (w · l · m) over the MOS devices of the
    lowered ``pdk/<pdk>/netlist.spice``, with geometry expressions (``w='sym*1'``, ``m='4*sym'``,
    bare ``w=sym``) resolved against the ``sizing.yaml`` defaults. Honestly a *gate*-area proxy
    (no spacing/routing/wells); passive totals (ΣC, ΣR) are recorded alongside so a real passive
    area can be estimated later — in many of these circuits the mim caps/dividers dominate silicon.
  - :func:`metric_values` — one corner's recorded measures mapped to the datasheet's canonical
    metrics, each with a ``pass``/``fail``/``none`` verdict against its ``spec``.
  - :func:`ppa_rollup` — the class-declared PPA vector (``ppa:`` block in
    ``_shared/classes/<class>/metrics.yaml``): canonical power (worst corner), the headline
    performance metrics at their worst corner (direction-aware), plus the area.

Unit convention: sky130 decks run under ``.option scale=1u`` so sizing geometry is bare microns;
ihp-sg13g2 / gf180mcu sizing carries explicit SI suffixes (``0.5u``) — same rule as
``bindings._SCALE_UM_PDKS``.
"""

from __future__ import annotations

import ast
import re
from typing import Any

from .bindings import _SCALE_UM_PDKS
from .model import Circuit, load_class
from .raw_project import _eng

_ENG = {
    "t": 1e12, "g": 1e9, "meg": 1e6, "k": 1e3, "m": 1e-3, "u": 1e-6,
    "n": 1e-9, "p": 1e-12, "f": 1e-15, "a": 1e-18,
}
_NUM = re.compile(r"^([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)(meg|[tgkmunpfa])?$", re.I)
_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_GEOM = re.compile(r"\b([wlm])=('[^']*'|\{[^}]*\}|\S+)")
_GEOM_NG = re.compile(r"\b(w|l|m|ng)=('[^']*'|\{[^}]*\}|\S+)", re.I)
_PARAM_LINE = re.compile(r"^\.param\s+([A-Za-z_]\w*)\s*=\s*(.+?)\s*$", re.MULTILINE | re.I)


class PpaError(ValueError):
    pass


def parse_eng(token: str) -> float | None:
    """``0.5u`` → 5e-7, ``300k`` → 3e5, ``2`` → 2.0; ``None`` if not a plain eng number."""
    m = _NUM.match(token.strip())
    if not m:
        return None
    return float(m.group(1)) * (_ENG[m.group(2).lower()] if m.group(2) else 1.0)


def _eval_expr(expr: str, symbols: dict[str, float], context: str) -> float:
    """Evaluate a netlist parameter expression (``4*sym``, ``sym*1``, ``0.5u``) numerically.

    Identifiers resolve through ``symbols``; only arithmetic is allowed (ast-checked)."""
    text = expr.strip().strip("'\"{}").strip()
    direct = parse_eng(text)
    if direct is not None:
        return direct

    def sub(m: re.Match[str]) -> str:
        name = m.group(0)
        if name.lower() in _ENG and re.match(r"^[0-9.]", text[: m.start()][-1:] or ""):
            return name  # an eng suffix glued to a number, handled below
        if name not in symbols:
            raise PpaError(f"{context}: unresolved symbol {name!r} in {expr!r}")
        return repr(symbols[name])

    substituted = _IDENT.sub(sub, text)
    # eng-suffixed literals inside arithmetic (e.g. 0.5u*2) → plain floats
    substituted = re.sub(
        r"([0-9][0-9.]*(?:[eE][-+]?[0-9]+)?)(meg|[tgkmunpfa])\b",
        lambda m: repr(float(m.group(1)) * _ENG[m.group(2).lower()]),
        substituted,
    )
    try:
        node = ast.parse(substituted, mode="eval")
        for sub_node in ast.walk(node):
            if not isinstance(
                sub_node,
                (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                 ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd),
            ):
                raise PpaError(f"{context}: unsupported expression {expr!r}")
        return float(eval(compile(node, "<ppa>", "eval"), {"__builtins__": {}}))
    except PpaError:
        raise
    except Exception as exc:
        raise PpaError(f"{context}: cannot evaluate {expr!r}: {exc}") from None


def sizing_symbols(circuit: Circuit, pdk: str) -> dict[str, float]:
    """The sizing variables' defaults as numbers (eng-parsed, units as authored), plus the
    TIED symbols resolved through the ``abstract/params.yaml`` tie graph: sizing
    keys on the free symbols only, so a numeric resolver must evaluate the generated ties
    (``x_dut_xm2_w = x_dut_xm1_w``, ratio refs) to cover every netlist symbol."""
    from .params import load_params_doc, tie_expressions

    out: dict[str, float] = {}
    for var in circuit.sizing(pdk).get("variables", []):
        val = parse_eng(str(var.get("default", "")))
        if val is not None:
            out[str(var["name"])] = val
    doc = load_params_doc(circuit.dir)
    if doc:
        pending = tie_expressions(doc)
        for _ in range(len(pending) + 1):  # fixpoint: ties may chain (group tie → ratio ref)
            progressed = False
            for sym, expr in list(pending.items()):
                try:
                    out[sym] = _eval_expr(expr, out, f"{circuit.id}@{pdk}: tie {sym}")
                except PpaError:
                    continue
                del pending[sym]
                progressed = True
            if not pending or not progressed:
                break
    return out


def resolve_deck_geometry(deck_text: str) -> dict[str, dict[str, float]]:
    """Numerically resolve a committed deck's per-device parameters.

    Resolves the deck's ``.param`` graph (sizing defaults + generated tie lines, fixpoint over
    chained ties) and returns ``{DEVICE: {field: value}}`` for every card in the ``.subckt``
    body: MOS geometry (``w``/``l``/``m``/``ng``, whichever the card carries — quoted
    expressions like ``w='sym*1'`` included) and single-value passive/source cards (``C``/
    ``R``/``L`` value, ``V``/``I`` dc value) as ``{"value": …}``. Unresolvable card values are
    skipped, never fatal — this is the migration parity oracle, not a SPICE parser.
    """
    symbols: dict[str, float] = {}
    pending: dict[str, str] = {}
    for name, rhs in _PARAM_LINE.findall(deck_text):
        val = parse_eng(rhs.strip().strip("'\"{}"))
        if val is not None:
            symbols[name] = val
        else:
            pending[name] = rhs
    for _ in range(len(pending) + 1):  # ties may chain — fixpoint
        progressed = False
        for name, expr in list(pending.items()):
            try:
                symbols[name] = _eval_expr(expr, symbols, name)
            except PpaError:
                continue
            del pending[name]
            progressed = True
        if not pending or not progressed:
            break

    out: dict[str, dict[str, float]] = {}
    in_subckt = False
    for ln in deck_text.splitlines():
        s = ln.strip()
        low = s.lower()
        if low.startswith(".subckt"):
            in_subckt = True
            continue
        if low.startswith(".ends"):
            in_subckt = False
            continue
        if not in_subckt or not s or s.startswith("*") or s.startswith("."):
            continue
        dev = s.split()[0].upper()
        fields = {k.lower(): v for k, v in _GEOM_NG.findall(s)}
        if "w" in fields and "l" in fields:
            resolved: dict[str, float] = {}
            for f, expr in fields.items():
                try:
                    resolved[f] = _eval_expr(expr, symbols, f"{dev}.{f}")
                except PpaError:
                    continue
            out[dev] = resolved
            continue
        if dev[0] in "CRLVI":
            toks = s.split()
            tok = toks[-1]
            for i, t in enumerate(toks):  # `V… dc {sym}` / `I… dc {sym}` forms
                if t.lower() == "dc" and i + 1 < len(toks):
                    tok = toks[i + 1]
                    break
            try:
                out[dev] = {"value": _eval_expr(tok, symbols, f"{dev}.value")}
            except PpaError:
                continue
    return out


def area_report(circuit: Circuit, pdk: str) -> dict[str, Any]:
    """Active gate area + passive inventory from the lowered netlist."""
    symbols = sizing_symbols(circuit, pdk)
    um = 1.0 if pdk in _SCALE_UM_PDKS else 1e6  # geometry value → µm
    area_um2 = 0.0
    mos = 0
    c_total = 0.0
    c_count = 0
    r_total = 0.0
    r_count = 0
    for ln in circuit.netlist(pdk).read_text().splitlines():
        line = ln.strip()
        if not line or line.startswith("*") or line.startswith("."):
            continue
        ctx = f"{circuit.id}@{pdk}: {line.split()[0]}"
        geom = dict(_GEOM.findall(line))
        if "w" in geom and "l" in geom:
            w = _eval_expr(geom["w"], symbols, ctx) * um
            length = _eval_expr(geom["l"], symbols, ctx) * um
            m = _eval_expr(geom["m"], symbols, ctx) if "m" in geom else 1.0
            area_um2 += w * length * m
            mos += 1
            continue
        kind = line[0].upper()
        if kind in ("C", "R"):
            # The value is the last non-assignment token — trailing key=value
            # params (e.g. `m=x_dut_c1_m`) are instance params, not the value.
            tokens = [t for t in line.split()[1:] if "=" not in t]
            value = _eval_expr(tokens[-1], symbols, ctx)
            m = _eval_expr(geom["m"], symbols, ctx) if "m" in geom else 1.0
            if kind == "C":
                c_total += value * m  # m parallel devices add
                c_count += 1
            else:
                r_total += value / m  # m parallel devices divide
                r_count += 1
    return {
        "active_gate_area_um2": round(area_um2, 3),
        "mos_count": mos,
        "c_total_f": c_total,
        "c_count": c_count,
        "r_total_ohm": r_total,
        "r_count": r_count,
    }


# --------------------------------------------------------------------------- metric mapping


def _bound(x: Any) -> float | None:
    """A numeric spec bound, or ``None`` for absent/non-numeric markers (e.g. ``min: any``)."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _spec_verdict(value: float, spec: dict[str, Any] | None) -> str:
    if not spec:
        return "none"
    lo, hi = _bound(spec.get("min")), _bound(spec.get("max"))
    if lo is None and hi is None:
        return "none"
    if lo is not None and value < lo:
        return "fail"
    if hi is not None and value > hi:
        return "fail"
    return "pass"


def metric_values(circuit: Circuit, analyses_block: dict[str, Any]) -> dict[str, Any]:
    """One corner's recorded ``analyses`` block → ``{canonical metric: {value, spec}}``.

    Metrics whose analysis didn't run at all are omitted — the rollup marks them
    absent rather than guessing. A metric whose analysis ran CLEAN but whose measure
    is missing or NaN is a spec FAILURE (value ``None``): the bench's honest-NaN
    paths (e.g. dropout's "never regulates in the swept range") and ngspice
    ``failed`` measures land here, and a silently-missing key used to be misread as
    a pass downstream (found on ldo_005@ihp, 2026-07-25)."""
    out: dict[str, Any] = {}
    for name, mspec in circuit.datasheet().get("metrics", {}).items():
        aid = mspec.get("analysis")
        meas = (mspec.get("extract") or {}).get("meas")
        if not aid or not meas:
            continue
        ablock = analyses_block.get(aid) or {}
        if ablock.get("status") != "ok":
            continue
        value = (ablock.get("measures") or {}).get(meas)
        if value is None or value != value:  # missing or NaN
            if mspec.get("spec"):
                out[name] = {"value": None, "spec": "fail"}
            continue
        out[name] = {"value": value, "spec": _spec_verdict(float(value), mspec.get("spec"))}
    return out


def class_ppa(class_id: str) -> dict[str, Any]:
    """The class's ``ppa:`` declaration (power metric + directed headline performance set)."""
    return load_class(class_id).get("ppa") or {}


def ppa_rollup(
    circuit: Circuit,
    corners_metrics: dict[str, dict[str, Any]],
    area: dict[str, Any],
    analysis_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The PPA vector over the recorded corners (worst case, direction-aware).

    ``analysis_params`` is the binding's per-PDK testbench-condition override block
    (``sizing.yaml analysis_params``); a ``VDD`` there is the rail the entry was
    actually simulated at and takes precedence over the datasheet typical for
    ``times_vdd`` power.
    """
    decl = class_ppa(circuit.klass)
    out: dict[str, Any] = {
        "active_gate_area_um2": area.get("active_gate_area_um2"),
        "corners_run": sorted(corners_metrics),
    }
    power = decl.get("power") or {}
    pvals = [
        m[power.get("metric", "")]["value"]
        for m in corners_metrics.values()
        if power.get("metric") in m and m[power.get("metric", "")]["value"] is not None
    ]
    if pvals:
        worst = max(pvals)  # power: higher is worse
        if power.get("times_vdd"):
            vdd = (
                circuit.datasheet()
                .get("default_conditions", {})
                .get("supply", {})
                .get("typical")
            )
            for k, v in (analysis_params or {}).items():
                if str(k).upper() == "VDD":
                    try:
                        vdd = _eng(v)
                    except (TypeError, ValueError):
                        pass
            out["power_w"] = worst * float(vdd) if vdd is not None else None
        else:
            out["power_w"] = worst
    performance: dict[str, float] = {}
    for perf in decl.get("performance") or []:
        vals = [
            m[perf["metric"]]["value"]
            for m in corners_metrics.values()
            if perf["metric"] in m and m[perf["metric"]]["value"] is not None
        ]
        if vals:
            performance[perf["metric"]] = min(vals) if perf.get("better") == "max" else max(vals)
    out["performance"] = performance
    return out
