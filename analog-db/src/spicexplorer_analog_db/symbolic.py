"""The netlist2tf symbolic cross-check (plan D-5, Phase 2).

The datasheet declares per-metric ``symbolic`` entries (tool + call + port args). This module
executes them against the **abstract** netlist and — when a measured operating point is
available — compares the numeric prediction with the simulated ``extract`` value.

The operating point is *measured, not guessed*: after ``.op`` in the container, the PDK's MOS
small-signal params are read via the ``op_probe`` convention in ``_shared/pdk/<pdk>.yaml``
(IHP: OSDI PSP exposes ``@n.<path>.n<model>[gm|gds]``), giving real ``gm_<dev>``/``ro_<dev>``
substitutions for the symbolic TF. That makes the check honest: symbolic structure × measured
bias vs the measured transfer — two independent paths to the same number.

Requires the ``[symbolic]`` extra (spicexplorer-netlist2tf).
"""

from __future__ import annotations

import math
import re
from typing import Any

from .assemble import assemble
from .model import Circuit
from .pdks import load_registry
from .runner import SpiceRunner, local_runner

# probe output: "@n.xdut.xm1.nsg13_lv_nmos[gm] = 1.548019e-05"
_PROBE = re.compile(r"@n\.xdut\.([a-z0-9_]+)\.[a-z0-9_]+\[(gm|gds)\]\s*=\s*([-+0-9.eE]+)")


class CrossCheckError(RuntimeError):
    pass


def _mos_instances(circuit: Circuit, pdk: str) -> list[tuple[str, str]]:
    """(ref, model) for every MOS X-card in the lowered netlist."""
    lowered = (circuit.dir / "pdk" / pdk / "netlist.spice").read_text()
    out = []
    for ln in lowered.splitlines():
        tok = ln.split()
        if tok and tok[0].upper().startswith("XM") and len(tok) >= 6:
            out.append((tok[0], tok[5]))
    return out


def _n2tf_label(ref: str) -> str:
    """Mirror netlist2tf's symbol label: strip the X wrapper (XM1 → m1)."""
    return ref[1:].lower() if ref.upper().startswith("XM") else ref.lower()


def op_probe_netlist(circuit: Circuit, pdk: str, corner: str) -> str:
    """The assembled dc_op netlist with per-device gm/gds probes injected after ``op``."""
    reg = load_registry(pdk)
    probe = reg.get("op_probe")
    if not probe:
        raise CrossCheckError(f"_shared/pdk/{pdk}.yaml has no op_probe convention")
    prefix = probe["inner_prefix"]
    lines = ["  op"]
    for ref, mdl in _mos_instances(circuit, pdk):
        for p in probe["params"]:
            lines.append(f"  print @n.xdut.{ref.lower()}.{prefix}{mdl.lower()}[{p}]")
    netlist = assemble(circuit, "dc_op", pdk, corner)
    if "  op\n" not in netlist:
        raise CrossCheckError("dc_op template has no `op` control line to instrument")
    return netlist.replace("  op\n", "\n".join(lines) + "\n", 1)


def extract_operating_point(
    circuit: Circuit, pdk: str, corner: str, runner: SpiceRunner = local_runner
) -> dict[str, float]:
    """Measured small-signal substitutions {gm_<dev>, ro_<dev>} from a container ``.op``."""
    output = runner(op_probe_netlist(circuit, pdk, corner))
    subs: dict[str, float] = {}
    for ref, param, value in _PROBE.findall(output):
        label = _n2tf_label(ref)
        v = float(value)
        if param == "gm":
            subs[f"gm_{label}"] = v
        elif param == "gds" and v != 0.0:
            subs[f"ro_{label}"] = 1.0 / v
    if not subs:
        raise CrossCheckError(f"no op probes parsed from ngspice output:\n{output[-1500:]}")
    return subs


def evaluate_symbolic_metric(
    circuit: Circuit, metric_id: str, subs: dict[str, float] | None = None
) -> dict[str, Any]:
    """Execute one datasheet metric's ``symbolic`` entry on the abstract netlist."""
    import spicexplorer_netlist2tf as n2tf

    spec = circuit.datasheet()["metrics"][metric_id]
    sym = spec.get("symbolic")
    if not sym:
        raise CrossCheckError(f"{circuit.id}.{metric_id} declares no symbolic entry")
    call = getattr(n2tf, sym["call"])
    args = dict(sym.get("args", {}))
    scale = args.pop("scale", None)
    output = tuple(args.pop("output"))
    input_ = tuple(args.pop("input")) if "input" in args else None

    abstract = str(circuit.dir / "abstract" / "netlist.spice")
    res = call(abstract, output, input_, subs=subs, **args) if input_ else call(abstract, output, subs=subs, **args)

    value = res.dc_gain.value
    if value is not None and scale == "db":
        value = 20.0 * math.log10(abs(value))
    return {
        "call": sym["call"],
        "tf": res.tf_simplified_expr,
        "value": value,
        "scale": scale or "linear",
        "kept_symbolic": res.kept_symbolic,
    }


def crosscheck(
    circuit: Circuit,
    pdk: str,
    corner: str,
    sim_measures: dict[str, dict[str, Any]],
    runner: SpiceRunner = local_runner,
    rel_tol: float = 0.05,
) -> dict[str, Any]:
    """Compare every symbolic-declaring metric against its simulated extract value.

    ``sim_measures`` is the results document's ``analyses`` block. Tolerance is relative on the
    metric's natural scale (dB metrics compare in dB with ``rel_tol·|sim|`` floored at 0.5 dB).
    """
    subs = extract_operating_point(circuit, pdk, corner, runner)
    report: dict[str, Any] = {"operating_point": subs, "metrics": {}}
    ds = circuit.datasheet()
    for mid, spec in ds["metrics"].items():
        if "symbolic" not in spec:
            continue
        sym = evaluate_symbolic_metric(circuit, mid, subs)
        meas_name = spec.get("extract", {}).get("meas")
        analysis = spec.get("analysis")
        sim_val = None
        if analysis and analysis in sim_measures:
            sim_val = sim_measures[analysis].get("measures", {}).get(meas_name)
        entry: dict[str, Any] = {"symbolic": sym["value"], "sim": sim_val, "call": sym["call"]}
        if sym["value"] is not None and sim_val is not None:
            tol = max(rel_tol * abs(sim_val), 0.5 if sym["scale"] == "db" else 0.0)
            entry["abs_error"] = abs(sym["value"] - sim_val)
            entry["tolerance"] = tol
            entry["agrees"] = entry["abs_error"] <= tol
        report["metrics"][mid] = entry
    return report
