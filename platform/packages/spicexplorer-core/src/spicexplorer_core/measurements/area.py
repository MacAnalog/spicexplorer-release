"""Recursive netlist-driven active-area computation.

Walks **every** device in a (possibly hierarchical) SPICE netlist, resolves each
MOSFET's ``W``, ``L`` and ``m`` from the deck's ``.param`` map — evaluating ``{…}`` brace
expressions and following symbol ties/ratios — and sums gate area ``Σ Wᵢ·Lᵢ·mᵢ`` over the
transistors, threading each subckt instance's own ``m`` multiplier down the hierarchy.
Non-MOS devices (R, C, sources, geometry-less blocks) are reported **separately** so the
breakdown accounts for every instance in the deck: you can verify nothing was silently
dropped.

This supersedes the hand-authored ``{derived: active_area, devices: [...]}`` recipe. A
listed-device recipe can silently omit a device — or, worse, a device's ``m`` multiplier
(the two demo decks size 8-of-10 and 7-of-24 transistors respectively, with multipliers up
to ×32) — and still score a plausible-looking number. A netlist walk cannot: the device
set *is* the netlist.

Layering: lives in ``spicexplorer-core`` on top of the **parse-only**
:class:`~spicexplorer_core.spice_engine.NetlistView` (needs neither ngspice nor a PDK) and
:func:`~spicexplorer_core.eng.parse_value`. No ``circuitgraph`` / optimizer dependency, so it
is engine-agnostic and unit-testable in isolation. The pure ``Σ`` arithmetic for the legacy
listed-device recipe stays in :mod:`spicexplorer_core.measurements.derived`; this module owns
the netlist-derived path.
"""

from __future__ import annotations

import ast
import json
import logging
import operator
import re
from typing import Any, Dict, List, Mapping, Optional

from spicexplorer_core.eng import parse_value

__all__ = [
    "active_area_report",
    "format_area_table",
    "resolve_param_value",
    "is_mosfet",
]

logger = logging.getLogger(__name__)

# Arithmetic supported inside a `{…}` .param expression (e.g. `{x_dut_xm14_m*8}`). A closed
# set — no calls, attributes, comparisons — so evaluating a deck's own expressions can never
# execute arbitrary code.
_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

# An eng-suffixed numeric literal appearing *inside* an expression (`{1u+2u}`) — number-led,
# ending in suffix letters. ngspice allows these; Python's parser does not, so we pre-convert
# them before ast.parse. A plain `4` or `1.5e-6` (no trailing alpha) is left for ast.
_ENG_LITERAL = re.compile(r"(?<![A-Za-z0-9_.])(\d+\.?\d*(?:[eE][+-]?\d+)?)([fpnumkMGT]|meg|MEG)(?![A-Za-z0-9_])")


class _ParamResolver:
    """Resolve a device geometry symbol (or a ``.param`` value string) to a float against a
    ``{name: value}`` map, evaluating brace expressions and following ties to a fixed point.

    A ``name → value`` where the value is itself a symbol (``x_dut_xm2_w = {x_dut_xm1_w}``) or a
    scaled ratio (``x_dut_xm4_m = {x_dut_xm7_m*4}``) is chased recursively with a cycle guard.
    Unresolvable tokens return ``None`` and append a human-readable note to :attr:`warnings`
    rather than raising, so one bad symbol never aborts the whole walk.
    """

    def __init__(self, params: Mapping[str, Any]) -> None:
        # Case-insensitive: spicelib may echo card symbols in a different case than the `.param`
        # names, and optimizer overrides arrive lower-cased.
        self._params: Dict[str, Any] = {str(k).lower(): v for k, v in params.items()}
        self._cache: Dict[str, Optional[float]] = {}
        self.warnings: List[str] = []

    def resolve(self, token: Any) -> Optional[float]:
        """A device field (a param NAME like ``x_dut_xm1_w``, a literal ``2u``, or an inline
        expression) → float, or ``None`` if it cannot be resolved."""
        return self._eval(token, frozenset())

    def _eval(self, token: Any, stack: frozenset[str]) -> Optional[float]:
        if token is None:
            return None
        if not isinstance(token, str):
            try:
                return float(token)  # already numeric (int/float/np.floating/override)
            except (TypeError, ValueError):
                return None
        s = _strip_braces(token)
        if not s:
            return None
        # A bare numeric/eng literal is the common leaf — try it first.
        try:
            return float(parse_value(s))
        except (ValueError, TypeError):
            pass
        # Otherwise an identifier or an arithmetic expression.
        try:
            tree = ast.parse(s, mode="eval")
        except SyntaxError:
            try:
                tree = ast.parse(_sub_eng_literals(s), mode="eval")
            except SyntaxError as exc:
                self.warnings.append(f"cannot parse expression {token!r}: {exc}")
                return None
        try:
            return self._eval_ast(tree.body, stack)
        except _ResolveError as exc:
            self.warnings.append(f"cannot resolve {token!r}: {exc}")
            return None

    def _eval_ast(self, node: ast.AST, stack: frozenset[str]) -> float:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise _ResolveError(f"non-numeric constant {node.value!r}")
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            return _BIN_OPS[type(node.op)](
                self._eval_ast(node.left, stack), self._eval_ast(node.right, stack)
            )
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](self._eval_ast(node.operand, stack))
        if isinstance(node, ast.Name):
            return self._resolve_name(node.id, stack)
        raise _ResolveError(f"unsupported expression element {type(node).__name__}")

    def _resolve_name(self, name: str, stack: frozenset[str]) -> float:
        key = name.lower()
        if key in stack:
            raise _ResolveError(f"cyclic parameter reference through {name!r}")
        if key not in self._params:
            raise _ResolveError(f"undefined parameter {name!r}")
        if key in self._cache and self._cache[key] is not None:
            return self._cache[key]  # type: ignore[return-value]
        val = self._eval(self._params[key], stack | {key})
        if val is None:
            raise _ResolveError(f"parameter {name!r} did not resolve to a number")
        self._cache[key] = val
        return val


class _ResolveError(Exception):
    """Internal — an expression could not be resolved to a number."""


def _strip_braces(token: str) -> str:
    """Drop the ngspice ``{…}`` / single-quote wrappers SPICE uses around an expression value."""
    s = token.strip()
    if len(s) >= 2 and ((s[0] == "{" and s[-1] == "}") or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1].strip()
    return s


def _sub_eng_literals(expr: str) -> str:
    """Rewrite eng-suffixed numeric literals inside an expression to plain floats so Python's
    parser accepts them (`{2u*3}` → `{2e-06*3}`). Identifiers are untouched."""

    def repl(m: re.Match[str]) -> str:
        return repr(float(parse_value(m.group(1) + m.group(2))))

    return _ENG_LITERAL.sub(repl, expr)


# Device classification -------------------------------------------------------------------

# A transistor is what we sum. Match on the reference prefix (`M…`, `XM…`) OR a MOS model name
# (`sg13_lv_nmos`, `nfet_…`, `pmos`, …) so both native-primitive and subckt-model MOS count.
_MOS_MODEL = re.compile(r"(?i)(?:^|[^a-z])(?:n|p)?mos|(?:^|[^a-z])[np]fet|(?:^|[^a-z])mosfet")


def is_mosfet(reference: str, model: Optional[str], params: Mapping[str, Any]) -> bool:
    """A device counts as a transistor when it exposes both ``w`` and ``l`` geometry AND looks
    like a MOS (by ``M``/``XM`` reference prefix or by MOS model name)."""
    lp = {str(k).lower() for k in params}
    if not ("w" in lp and "l" in lp):
        return False
    ref = reference.upper()
    if ref.startswith("XM") or (ref.startswith("M") and not ref.startswith("MX")):
        return True
    return bool(model and _MOS_MODEL.search(model))


def _lower_params(raw: Mapping[str, Any]) -> Dict[str, Any]:
    return {str(k).lower(): v for k, v in raw.items() if str(k).lower() != "value"}


def _walk(
    view: Any,
    resolver: _ParamResolver,
    *,
    path: str,
    inst_mult: float,
    seen: frozenset[str],
    devices: List[dict],
    others: List[dict],
    warnings: List[str],
) -> None:
    """Recurse one hierarchy level, classifying each component into ``devices`` (transistors)
    or ``others``, and stepping into subckt instances with the cumulative ``inst_mult``."""
    subckt_names = {n.lower() for n in view.get_subcircuit_names()}
    for ref in view.get_components():
        full = f"{path}/{ref}" if path else ref
        params = view.get_component_parameters(ref)
        model = _as_str(view.get_component_value(ref))
        lp = _lower_params(params)

        if is_mosfet(ref, model, lp):
            w = resolver.resolve(lp.get("w"))
            length = resolver.resolve(lp.get("l"))
            m = resolver.resolve(lp["m"]) if "m" in lp else 1.0
            entry: Dict[str, Any] = {
                "path": full,
                "ref": ref,
                "model": model,
                "kind": _mos_kind(model),
                "w": w,
                "l": length,
                "m": m,
                "inst_mult": inst_mult,
            }
            if w is None or length is None or m is None:
                entry["area"] = None
                entry["counted"] = False
                entry["reason"] = "unresolved w/l/m"
                warnings.append(f"{full}: unresolved geometry (w={w}, l={length}, m={m})")
            else:
                entry["area"] = w * length * m * inst_mult
                entry["counted"] = True
            devices.append(entry)
            continue

        # A subckt *instance* that resolves to a definition in this deck → recurse, folding in
        # this instance's own m-multiplier. (A MOS subckt-model instance already matched above.)
        value = model or ""
        is_subckt_instance = ref.upper().startswith("X") and value.lower() in subckt_names
        if is_subckt_instance:
            if value.lower() in seen:
                warnings.append(f"{full}: cyclic subckt reference to {value!r}; not expanded")
                others.append({"path": full, "ref": ref, "kind": "subckt", "model": model,
                               "area": None, "reason": "cyclic reference"})
                continue
            child_mult = resolver.resolve(lp["m"]) if "m" in lp else 1.0
            if child_mult is None:
                child_mult = 1.0
                warnings.append(f"{full}: subckt multiplier unresolved; assuming 1")
            try:
                child = view.get_subcircuit(ref)
            except Exception as exc:  # pragma: no cover - defensive
                warnings.append(f"{full}: cannot step into {value!r}: {exc}")
                others.append({"path": full, "ref": ref, "kind": "subckt", "model": model,
                               "area": None, "reason": f"cannot expand: {exc}"})
                continue
            others.append({"path": full, "ref": ref, "kind": "subckt", "model": model,
                           "m": child_mult, "area": None, "reason": "container (expanded)"})
            _walk(child, resolver, path=full, inst_mult=inst_mult * child_mult,
                  seen=seen | {value.lower()}, devices=devices, others=others, warnings=warnings)
            continue

        # A non-MOS leaf (R, C, source, or a geometry-less block). Report it; if it happens to
        # carry w/l geometry (e.g. a PDK passive subckt device), report an area estimate in the
        # separate bucket — never folded into the transistor total.
        other: Dict[str, Any] = {
            "path": full, "ref": ref, "kind": _passive_kind(ref, model), "model": model,
            "value": _as_str(params.get("Value")) if "Value" in params else None,
        }
        if "w" in lp and "l" in lp:
            w = resolver.resolve(lp.get("w"))
            length = resolver.resolve(lp.get("l"))
            m = resolver.resolve(lp["m"]) if "m" in lp else 1.0
            other["w"], other["l"], other["m"] = w, length, m
            if w is not None and length is not None and m is not None:
                other["area"] = w * length * m * inst_mult
            else:
                other["area"] = None
                other["reason"] = "unresolved w/l/m"
        else:
            other["area"] = None
            other["reason"] = "no gate geometry"
        others.append(other)


def active_area_report(
    netlist: Any,
    *,
    overrides: Optional[Mapping[str, Any]] = None,
    scale: float = 1.0,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Walk ``netlist`` recursively and return a JSON-serializable active-area report.

    Args:
        netlist: a deck path (``str``/``Path``), raw netlist text, or a ready
            ``NetlistView``/``NetlistViewLike``. Parse-only — no ngspice or PDK needed.
        overrides: candidate sizing ``{param: value}`` (e.g. the optimizer's free+frozen
            knobs) that WIN over the deck's ``.param`` defaults; ties/ratios in the deck then
            resolve against them. Numbers or eng-strings.
        scale: multiply the summed SI area (m²) into the reporting unit — ``1e12`` for µm².
        verbose: also emit the per-device table to the module logger at INFO.

    Returns a dict with the scored ``active_area`` (scaled Σ W·L·m over transistors), a
    ``devices`` breakdown (every transistor, counted or not), an ``others`` list (every non-MOS
    instance, so the accounting is complete), a ``coverage`` tally, and any ``warnings``.
    """
    view = _as_view(netlist)
    global_params = view.get_parameters()
    merged: Dict[str, Any] = dict(global_params)
    if overrides:
        merged.update({str(k): v for k, v in overrides.items()})
    resolver = _ParamResolver(merged)

    devices: List[dict] = []
    others: List[dict] = []
    warnings: List[str] = []
    _walk(view, resolver, path="", inst_mult=1.0, seen=frozenset(),
          devices=devices, others=others, warnings=warnings)
    warnings.extend(resolver.warnings)

    counted = [d for d in devices if d.get("counted")]
    raw_area = sum(d["area"] for d in counted)  # m² (W,L in metres)
    uncounted = [d for d in devices if not d.get("counted")]
    container_others = [o for o in others if o.get("kind") == "subckt"]

    # Express each per-device `area` in the SAME reporting unit as the total (scaled), so the
    # JSON breakdown is self-consistent — `active_area == Σ devices[i].area` exactly.
    for d in devices:
        if d.get("area") is not None:
            d["area"] *= scale
    for o in others:
        if o.get("area") is not None:
            o["area"] *= scale

    report: Dict[str, Any] = {
        "active_area": scale * raw_area,
        "scale": scale,
        "unit": "um^2" if scale == 1e12 else ("m^2" if scale == 1.0 else f"m^2 * {scale:g}"),
        "raw_area_m2": raw_area,
        "transistor_count": len(counted),
        "devices": devices,
        "others": others,
        "warnings": warnings,
        "coverage": {
            "transistors_counted": len(counted),
            "transistors_unresolved": len(uncounted),
            "other_instances": len(others) - len(container_others),
            "subckt_containers": len(container_others),
            "total_instances": len(devices) + len(others),
            "complete": not uncounted and not warnings,
        },
    }
    if verbose:
        logger.info("active-area report:\n%s", format_area_table(report))
    return report


def format_area_table(report: Mapping[str, Any]) -> str:
    """A human-readable per-device table for debug logs / CLI ``--table``."""
    unit = report.get("unit", "")
    lines: List[str] = []
    lines.append(f"{'device':<28}{'kind':<10}{'W':>12}{'L':>12}{'m':>8}{'mult':>7}{'area['+unit+']':>16}")
    lines.append("-" * 93)
    for d in report.get("devices", []):
        area = d.get("area")  # already in the report's unit (scaled)
        area_s = "  (skipped)" if area is None else f"{area:>15.5g}"
        lines.append(
            f"{d['path']:<28}{str(d.get('kind','mos')):<10}"
            f"{_fmt(d.get('w')):>12}{_fmt(d.get('l')):>12}"
            f"{_fmt(d.get('m')):>8}{_fmt(d.get('inst_mult')):>7}{area_s:>16}"
        )
    if report.get("others"):
        lines.append("-" * 93)
        for o in report["others"]:
            lines.append(f"{o['path']:<28}{str(o.get('kind','?')):<10}"
                         f"{'':>12}{'':>12}{'':>8}{'':>7}{('  '+(o.get('reason') or '')):>16}")
    cov = report.get("coverage", {})
    lines.append("-" * 93)
    lines.append(
        f"TOTAL active_area = {report.get('active_area', 0.0):.6g} {unit}   "
        f"({cov.get('transistors_counted', 0)} transistors; "
        f"{cov.get('other_instances', 0)} other; "
        f"{cov.get('transistors_unresolved', 0)} unresolved; "
        f"complete={cov.get('complete')})"
    )
    return "\n".join(lines)


def resolve_param_value(token: Any, params: Mapping[str, Any]) -> Optional[float]:
    """Standalone helper: resolve one symbol/expression ``token`` against a ``.param`` map.
    Exposed for testing and reuse; returns ``None`` (not raise) when unresolvable."""
    return _ParamResolver(params).resolve(token)


# Small helpers ---------------------------------------------------------------------------


def _as_view(netlist: Any) -> Any:
    """Coerce a path / text / view into a NetlistView (imported lazily to keep the module light
    and to avoid any import cycle with the spice_engine package at import time)."""
    from spicexplorer_core.spice_engine.netlist_view import NetlistView

    if hasattr(netlist, "get_components") and hasattr(netlist, "get_parameters"):
        return netlist  # already a NetlistViewLike
    from pathlib import Path

    if isinstance(netlist, Path):
        return NetlistView.from_file(netlist)
    if isinstance(netlist, str):
        # A path if it points at a file; otherwise treat as raw netlist text.
        if "\n" not in netlist and Path(netlist).exists():
            return NetlistView.from_file(netlist)
        return NetlistView.from_string(netlist)
    raise TypeError(f"active_area_report: unsupported netlist source {type(netlist).__name__}")


def _as_str(v: Any) -> Optional[str]:
    return None if v is None else str(v)


def _mos_kind(model: Optional[str]) -> str:
    m = (model or "").lower()
    if "pmos" in m or "pfet" in m:
        return "pmos"
    if "nmos" in m or "nfet" in m:
        return "nmos"
    return "mos"


def _passive_kind(reference: str, model: Optional[str]) -> str:
    c = reference[:1].upper()
    return {
        "R": "resistor", "C": "capacitor", "L": "inductor",
        "V": "vsource", "I": "isource", "D": "diode", "Q": "bjt",
    }.get(c, "subckt" if c == "X" else "other")


def _fmt(v: Any) -> str:
    if v is None:
        return "-"
    try:
        return f"{float(v):.4g}"
    except (TypeError, ValueError):
        return str(v)


# CLI ------------------------------------------------------------------------------------


def _parse_overrides(items: Optional[List[str]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"--set expects name=value, got {item!r}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def main(argv: Optional[List[str]] = None) -> int:
    """``python -m spicexplorer_core.measurements.area <deck.spice> [options]`` — walk a deck and
    print the active-area report as JSON (and, with ``--table``, the debug table)."""
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m spicexplorer_core.measurements.area",
        description="Recursively sum MOSFET gate area (Σ W·L·m) over every device in a netlist.",
    )
    ap.add_argument("netlist", help="deck path (.spice/.cir/.net/.sp)")
    ap.add_argument("--scale", type=float, default=1e12,
                    help="area scale (default 1e12 → µm²; use 1 for m²)")
    ap.add_argument("--set", action="append", metavar="NAME=VALUE", dest="overrides",
                    help="override a .param (repeatable), e.g. --set x_dut_xm1_w=3u")
    ap.add_argument("--table", action="store_true", help="also print the per-device table")
    ap.add_argument("--json", metavar="PATH", help="write the JSON report to PATH (else stdout)")
    args = ap.parse_args(argv)

    report = active_area_report(
        args.netlist, overrides=_parse_overrides(args.overrides), scale=args.scale
    )
    if args.table:
        print(format_area_table(report))
    payload = json.dumps(report, indent=2)
    if args.json:
        from pathlib import Path

        Path(args.json).write_text(payload, encoding="utf-8")
        print(f"wrote {args.json}")
    else:
        print(payload)
    # Non-zero exit if the accounting is incomplete — handy in CI / verification scripts.
    return 0 if report["coverage"]["complete"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
