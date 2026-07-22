"""The analysis resolver (plan D-4, Phase 2).

``assemble(circuit, analysis_id, pdk, corner)`` renders one (circuit × analysis × pdk × corner)
cell of the matrix into a **complete runnable netlist**:

  template (class-scoped or universal)            ← resolve_template
    + ``${...}`` bindings from the analysis params + datasheet default_conditions
    + ``${PDK_INCLUDE}``  ← pdk/<pdk>/corners.yaml (the named corner's .lib lines) + .temp
    + ``${PORT_LINE}/${DUT}`` ← circuit.yaml ports + id
    + the DUT ``.subckt`` body  ← the GENERATED lowered pdk/<pdk>/netlist.spice

Tier 2 (assembly) asserts every cell renders with **no unresolved placeholders** and re-parses.
"""

from __future__ import annotations

import re
from string import Template
from typing import Any

import yaml

from .model import Circuit, resolve_template

_PLACEHOLDER = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class AssembleError(ValueError):
    pass


def _corner_includes(circuit: Circuit, pdk: str, corner: str) -> str:
    path = circuit.dir / "pdk" / pdk / "corners.yaml"
    if not path.is_file():
        raise AssembleError(f"{circuit.id}: pdk/{pdk}/corners.yaml missing")
    with path.open() as fh:
        doc = yaml.safe_load(fh) or {}
    bundles = (doc.get("corners") or {}).get(corner)
    if not bundles:
        raise AssembleError(f"{circuit.id}: corner {corner!r} not in pdk/{pdk}/corners.yaml")
    # A bundle with a `section` is a `.lib FILE SECTION`; a sectionless bundle is a plain
    # `.include FILE` (e.g. gf180's design.ngspice global stat switches, which carry no section).
    lines = [
        f".lib {b['lib_file']} {b['section']}" if b.get("section") else f".include {b['lib_file']}"
        for b in bundles
    ]
    return "\n".join(lines)


def _sizing_params(circuit: Circuit, pdk: str) -> str:
    """``.param`` lines binding the design variables to their sizing.yaml defaults."""
    sizing = circuit.sizing(pdk)
    lines = []
    for var in sizing.get("variables", []):
        if "default" not in var:
            raise AssembleError(f"{circuit.id}: sizing variable {var['name']!r} has no default")
        lines.append(f".param {var['name']}={var['default']}")
    return "\n".join(lines)


def _tie_block(circuit: Circuit) -> str:
    """The GENERATED parameter-tie block (plan_parameterization D-3, P2 lowering).

    Empty (and the deck byte-identical to the pre-params rendering) unless the circuit adopted
    ``abstract/params.yaml``. Each tied symbol is defined exactly ONCE, here — so an upstream
    project (or the optimizer's verbatim ``.param`` rewrite) that redefines the atomic symbol
    overrides just that symbol: *untying = shadowing*, no code path involved."""
    from .params import load_params_doc, tie_param_lines

    doc = load_params_doc(circuit.dir)
    if not doc:
        return ""
    lines = tie_param_lines(doc)
    if not lines:
        return ""
    return (
        "\n* ---- GENERATED parameter ties (abstract/params.yaml groups/ratios) ----\n"
        "* Each tied symbol is defined exactly once, by its line below; rewrite that\n"
        "* .param to untie just that symbol (untying = shadowing, plan D-3).\n" + "\n".join(lines)
    )


def dut_subckt(circuit: Circuit, pdk: str) -> str:
    """The DUT definition: sizing-variable ``.param`` defaults (global scope, the FREE symbols)
    + the generated tie block (tied symbols, when ``abstract/params.yaml`` is adopted) + the
    GENERATED lowered netlist body wrapped in a real ``.subckt <id> <ports>`` block."""
    lowered = circuit.dir / "pdk" / pdk / "netlist.spice"
    if not lowered.is_file():
        raise AssembleError(f"{circuit.id}: pdk/{pdk}/netlist.spice missing (run `analog-db generate`)")
    body = [
        ln
        for ln in lowered.read_text().splitlines()
        if ln.strip() and not ln.startswith("*") and ln.strip().lower() != ".end"
    ]
    ports = " ".join(circuit.manifest["ports"])
    return (
        _sizing_params(circuit, pdk)
        + _tie_block(circuit)
        + f"\n.subckt {circuit.id} {ports}\n"
        + "\n".join(body)
        + "\n.ends\n"
    )


def _conditions(circuit: Circuit, analysis: dict[str, Any], pdk: str) -> dict[str, str]:
    """Template bindings: datasheet default_conditions (fallback) under the analysis params (primary).

    If ``sizing.yaml`` contains a top-level ``analysis_params`` mapping, those key/value pairs
    override the shared ``analyses/<id>.yaml`` params for this PDK only.  This lets a PDK binding
    specify a different ``IBIAS`` (or any other testbench parameter) without touching the
    cross-PDK analysis YAML.

    Precedence (lowest → highest):
      datasheet default_conditions  →  analyses/<id>.yaml params  →  sizing.yaml analysis_params
    """
    out: dict[str, str] = {}
    ds = circuit.datasheet()
    defaults = ds.get("default_conditions", {})
    # the universal fallbacks every template may reference
    fallback_map = {"VDD": "supply", "VCM": "vcm", "IBIAS": "ibias", "CL": "cload", "TEMP": "temp"}
    for var, cond in fallback_map.items():
        if cond in defaults and "typical" in defaults[cond]:
            out[var] = str(defaults[cond]["typical"])
    for k, v in (analysis.get("params") or {}).items():
        out[str(k)] = str(v)
    # Per-PDK overrides from sizing.yaml (highest precedence)
    sizing = circuit.sizing(pdk)
    for k, v in (sizing.get("analysis_params") or {}).items():
        out[str(k)] = str(v)
    return out


def assemble(circuit: Circuit, analysis_id: str, pdk: str, corner: str = "tt") -> str:
    """Render one matrix cell into a complete runnable netlist (raises ``AssembleError``)."""
    adoc = circuit.analysis(analysis_id)
    template_id = adoc.get("template", analysis_id)
    tpath = resolve_template(circuit.klass, template_id)
    if tpath is None:
        raise AssembleError(f"{circuit.id}/{analysis_id}: template {template_id!r} resolves to no file")

    ds = circuit.datasheet()
    temp = ds.get("default_conditions", {}).get("temp", {}).get("typical", 27)
    mapping: dict[str, str] = {
        "DUT": circuit.id,
        "PORT_LINE": "XDUT " + " ".join(circuit.manifest["ports"]),
        "PDK_INCLUDE": _corner_includes(circuit, pdk, corner) + f"\n.temp {temp}",
        **_conditions(circuit, adoc, pdk),
    }
    rendered = Template(tpath.read_text()).safe_substitute(mapping)

    unresolved = sorted(set(_PLACEHOLDER.findall(rendered)))
    if unresolved:
        raise AssembleError(
            f"{circuit.id}/{analysis_id}@{pdk}/{corner}: unresolved placeholders {unresolved} "
            f"(bind them in analyses/{analysis_id}.yaml params or datasheet default_conditions)"
        )

    # the DUT definition goes before the final .end (which must be the template's last line)
    body = rendered.rstrip()
    if not body.endswith("\n.end"):
        raise AssembleError(f"template {template_id!r} does not end with a final .end line")
    head = body[: -len(".end")]
    return (
        f"** ASSEMBLED by analog-db — {circuit.id} × {analysis_id} × {pdk} × {corner}\n"
        + head
        + dut_subckt(circuit, pdk)
        + ".end\n"
    )
