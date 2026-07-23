"""Data-driven Spectre analysis configs + SKILL calculator expressions (the template DB).

The analog-db repo carries an **engine-level template database** the closed (Spectre)
lane composes from — the ADE analogue of "analysis configs + calculator expressions",
kept as *data* so a new analysis type or metric expression is a YAML edit, not a code
change:

* ``_shared/engines/spectre/analyses.yaml`` — analysis **statement templates** (``ac``,
  ``dc_op``, ``dc_sweep``, ``noise``, ``tran``, ``pss``, ``stb``, …) with ``{NAME}``
  placeholders and ``[ optional ]`` segments.
* ``_shared/engines/spectre/calculator.yaml`` — named **SKILL calculator expressions**
  (each an OCEAN ``result`` + one SKILL line) for the headless OCEAN Tier-2 route.
* ``_shared/classes/<class>/spectre-benches.yaml`` — the per-**testbench** wiring: which
  analysis templates a bench composes and which calculator expressions read its results.

This module renders those files: :func:`bench_analyses` → the analysis-statement tuple a
deck composes (consumed by ``backends.analog_db._spectre_analyses``, which keeps a
built-in fallback for checkouts without the DB), and :func:`bench_measurements` → the
:class:`~spicexplorer.backends.ocean_metrics.OceanMeasurement` list for
``OceanMetricsSession.measure``/``measure_batch`` (the PSS+SKILL path for THD/IIP3 and
the stb path for loop-gain PM). Render contexts are the bench's ``analyses/<tb>.yaml``
params (numeric) plus platform-computed extras (``RAIL``, ``IIP3_*``) — see
``analog_db._spectre_context``.

Template syntax rules (mirrors the DB header): ``{NAME}`` substitutes from the context
(floats render ``%.10g`` — never SPICE eng suffixes, the Spectre ``M``/``m`` landmine);
a ``[ … ]`` segment is kept only when every placeholder inside it resolves; a ``$NAME``
value in the bench map's ``args:`` pulls from the context, anything else is a literal.
Missing placeholders raise :class:`SpectreTemplateError` (a config error — never silently
skipped); a missing DB file raises ``AnalogDbUnavailable`` (callers may fall back).
"""

from __future__ import annotations

import os
import re
from typing import Any, Mapping

__all__ = [
    "SpectreTemplateError",
    "load_analysis_templates",
    "load_calculator_table",
    "load_bench_config",
    "render_template",
    "bench_analyses",
    "bench_measurements",
]

_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
_OPTIONAL = re.compile(r"\[([^\[\]]*)\]")


class SpectreTemplateError(RuntimeError):
    """A template-DB config error (unknown template/expression, unresolved placeholder)."""


def _fmt(value: Any) -> str:
    if isinstance(value, bool):  # bool is an int subclass — reject rather than emit "True"
        raise SpectreTemplateError(f"boolean has no Spectre statement rendering: {value!r}")
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def render_template(template: str, context: Mapping[str, Any]) -> str:
    """Render one statement/expression template against ``context``.

    ``[ optional ]`` segments drop when any placeholder inside is missing from the
    context; a missing placeholder *outside* an optional segment raises
    :class:`SpectreTemplateError` naming it.
    """

    def _optional(m: re.Match[str]) -> str:
        body = m.group(1)
        if all(name in context for name in _PLACEHOLDER.findall(body)):
            return body
        return ""

    text = _OPTIONAL.sub(_optional, template)
    missing = [name for name in _PLACEHOLDER.findall(text) if name not in context]
    if missing:
        raise SpectreTemplateError(
            f"template {template!r}: unresolved placeholder(s) {missing} "
            f"(context has {sorted(context)})"
        )
    return _PLACEHOLDER.sub(lambda m: _fmt(context[m.group(1)]), text)


def _resolve(value: Any, context: Mapping[str, Any]) -> Any:
    """A bench-map ``args:`` value: ``$NAME`` pulls from the context, else the literal."""
    if isinstance(value, str) and value.startswith("$"):
        name = value[1:]
        if name not in context:
            raise SpectreTemplateError(
                f"args reference {value!r} not in the render context ({sorted(context)})"
            )
        return context[name]
    return value


def _engine_yaml(name: str, root: str | os.PathLike[str] | None) -> dict[str, Any]:
    from .analog_db import _load_yaml, analog_db_root

    return _load_yaml(analog_db_root(root) / "_shared/engines/spectre" / name)


def load_analysis_templates(*, root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """``{name: {statement, defaults?, psf?, notes?}}`` from the engine analyses DB."""
    data = _engine_yaml("analyses.yaml", root).get("templates")
    if not isinstance(data, dict):
        from .analog_db import AnalogDbUnavailable

        raise AnalogDbUnavailable("spectre analyses.yaml has no templates: mapping")
    return data


def load_calculator_table(*, root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """``{name: {result, expr, notes?}}`` from the engine calculator DB."""
    data = _engine_yaml("calculator.yaml", root).get("expressions")
    if not isinstance(data, dict):
        from .analog_db import AnalogDbUnavailable

        raise AnalogDbUnavailable("spectre calculator.yaml has no expressions: mapping")
    return data


def load_bench_config(
    circuit_class: str = "amplifier", *, root: str | os.PathLike[str] | None = None
) -> dict[str, Any]:
    """``{testbench: {analyses: […], calculator: […]}}`` from the class bench map."""
    from .analog_db import AnalogDbUnavailable, _load_yaml, analog_db_root

    path = analog_db_root(root) / "_shared/classes" / circuit_class / "spectre-benches.yaml"
    data = _load_yaml(path).get("benches")
    if not isinstance(data, dict):
        raise AnalogDbUnavailable(f"{path} has no benches: mapping")
    return data


def bench_analyses(
    testbench: str,
    context: Mapping[str, Any],
    *,
    circuit_class: str = "amplifier",
    root: str | os.PathLike[str] | None = None,
) -> tuple[str, ...]:
    """The Spectre analysis-statement tuple the template DB configures for a testbench.

    Raises ``KeyError`` when the bench map has no entry for ``testbench`` (callers may
    fall back to a built-in composition), ``AnalogDbUnavailable`` when the DB itself is
    absent, and :class:`SpectreTemplateError` for a real config error (unknown template
    name, unresolved placeholder) — those must surface, not silently degrade.
    """
    bench = load_bench_config(circuit_class, root=root)[testbench]
    templates = load_analysis_templates(root=root)
    statements: list[str] = []
    for entry in bench.get("analyses") or []:
        name = str(entry.get("template", ""))
        if name not in templates:
            raise SpectreTemplateError(
                f"{testbench}: unknown analysis template {name!r} "
                f"(engine DB has {sorted(templates)})"
            )
        tpl = templates[name]
        args = {k: _resolve(v, context) for k, v in (entry.get("args") or {}).items()}
        merged = {**(tpl.get("defaults") or {}), **context, **args}
        statement = render_template(str(tpl["statement"]), merged)
        from .spectre_deck import _check_analysis_contract

        _check_analysis_contract(statement)
        statements.append(statement)
    if not statements:
        raise SpectreTemplateError(f"{testbench}: the bench map lists no analyses")
    return tuple(statements)


def bench_measurements(
    testbench: str,
    context: Mapping[str, Any],
    *,
    circuit_class: str = "amplifier",
    root: str | os.PathLike[str] | None = None,
) -> list[Any]:
    """The rendered ``OceanMeasurement`` list (the SKILL calculator route) for a testbench.

    Each bench-map ``calculator:`` row names an expression from the engine calculator
    table; its ``args:`` (after ``$`` resolution) fill the expression's placeholders.
    Returns ``[]`` when the bench configures no calculator set. Exceptions as in
    :func:`bench_analyses`.
    """
    from .ocean_metrics import OceanMeasurement

    bench = load_bench_config(circuit_class, root=root)[testbench]
    rows = bench.get("calculator") or []
    if not rows:
        return []
    table = load_calculator_table(root=root)
    out: list[Any] = []
    for row in rows:
        expr_name = str(row.get("expr", ""))
        if expr_name not in table:
            raise SpectreTemplateError(
                f"{testbench}: unknown calculator expression {expr_name!r} "
                f"(engine DB has {sorted(table)})"
            )
        entry = table[expr_name]
        args = {k: _resolve(v, context) for k, v in (row.get("args") or {}).items()}
        merged = {**context, **args}
        expr = render_template(str(entry["expr"]).strip(), merged)
        out.append(
            OceanMeasurement(
                name=str(row.get("name", expr_name)),
                result=str(entry["result"]),
                expr=expr,
            )
        )
    return out
