"""Phase-2 gate: the analysis resolver, Tier 2 assembly, the runner's parsing, the symbolic
cross-check plumbing, and the D-10 LDO stub. All PDK-free (the container exit runs under
``slow`` in test_slow_sim.py)."""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import model, verify
from spicexplorer_analog_db.assemble import AssembleError, assemble, dut_subckt
from spicexplorer_analog_db.runner import parse_measures
from spicexplorer_analog_db.symbolic import _mos_instances, _n2tf_label, op_probe_netlist

CIRCUIT = "amp_001_5t"


@pytest.fixture(scope="module")
def ota() -> model.Circuit:
    return model.load_circuit(CIRCUIT)


@pytest.fixture(scope="module")
def ldo() -> model.Circuit:
    return model.load_circuit("ldo_006_stub")


# ---------------------------------------------------------------- resolver / Tier 2


def test_tier2_is_fully_green():
    results = verify.run_tier2()
    failures = [r for r in results if r.status == "fail"]
    assert not failures, "Tier 2 failures:\n" + "\n".join(
        f"{r.circuit} {r.check}: {r.reason}" for r in failures
    )


def test_assemble_binds_everything(ota):
    nl = assemble(ota, "ac_open_loop", "ihp-sg13g2", "tt")
    assert "${" not in nl
    assert ".lib cornerMOSlv.lib mos_tt" in nl
    assert "XDUT vdd vout vinp vinn ibias vss amp_001_5t" in nl
    assert ".subckt amp_001_5t vdd vout vinp vinn ibias vss" in nl
    # sizing defaults injected as global .param (the FREE atomic symbols, plan_parameterization D-4)
    assert ".param x_dut_xm1_w=10.0u" in nl
    # the adopted params.yaml tying layer lowers to a generated tie block (plan D-3)
    assert ".param x_dut_xm2_w = {x_dut_xm1_w}" in nl


def test_assemble_unknown_corner_fails(ota):
    with pytest.raises(AssembleError, match="corner 'xx'"):
        assemble(ota, "ac_open_loop", "ihp-sg13g2", "xx")


def test_dut_subckt_strips_comments_and_end(ota):
    block = dut_subckt(ota, "sky130")
    assert block.count(".subckt") == 1 and block.rstrip().endswith(".ends")
    assert ".end\n" not in block.replace(".ends", "")
    assert "sky130_fd_pr__nfet_01v8" in block


def test_class_template_shadows_universal(ota, ldo):
    """D-10: amplifier dc_op (ibias + inputs) shadows the supply-only universal dc_op."""
    amp = assemble(ota, "dc_op", "ihp-sg13g2", "tt")
    stub = assemble(ldo, "dc_op", "ihp-sg13g2", "tt")
    assert "Ibias" in amp and "Vinp" in amp
    assert "Ibias" not in stub and "Vinp" not in stub


# ---------------------------------------------------------------- runner parsing


def test_parse_measures():
    out = """
dcgain              =  2.977862e+01
ugf                 =  3.014815e+07
meas tran tsettle when verr=2m fall=last failed!
tcross              =  failed
"""
    measures, failed = parse_measures(out)
    assert measures == {"dcgain": 29.77862, "ugf": 30148150.0}
    assert failed == ["tcross"]


# ---------------------------------------------------------------- symbolic cross-check plumbing


def test_mos_instances_and_labels(ota):
    inst = _mos_instances(ota, "ihp-sg13g2")
    assert [r for r, _ in inst] == ["XM1", "XM2", "XM3", "XM4", "XM5", "XM6"]
    assert all(m.startswith("sg13_lv_") for _, m in inst)
    assert _n2tf_label("XM1") == "m1"  # mirrors netlist2tf's symbol minting


def test_op_probe_netlist_instruments_every_device(ota):
    nl = op_probe_netlist(ota, "ihp-sg13g2", "tt")
    for ref in ("xm1", "xm6"):
        assert f"print @n.xdut.{ref}.nsg13_lv_" in nl


def test_symbolic_metric_evaluates_pdk_free(ota):
    """The datasheet's symbolic entry executes on the abstract netlist (netlist2tf, no PDK)."""
    pytest.importorskip("spicexplorer_netlist2tf")
    from spicexplorer_analog_db.symbolic import evaluate_symbolic_metric

    # symbolic-only (no subs): a fully symbolic TF, value None
    sym = evaluate_symbolic_metric(ota, "dc_gain_db")
    assert sym["call"] == "open_loop_gain" and sym["value"] is None
    assert "gm_m1" in sym["tf"]
    # with a numeric bias point: a finite dB value
    subs = {f"gm_m{i}": 1.5e-5 for i in range(1, 7)} | {f"ro_m{i}": 2e6 for i in range(1, 7)}
    sym = evaluate_symbolic_metric(ota, "dc_gain_db", subs)
    assert sym["scale"] == "db" and 20 < sym["value"] < 40


# ---------------------------------------------------------------- D-10 LDO stub


def test_ldo_stub_proves_class_abstraction(ldo):
    assert ldo.klass == "ldo" and ldo.status == "incomplete"
    results = verify.run_tier0(["ldo_006_stub"]) + verify.run_tier1(["ldo_006_stub"]) + verify.run_tier2(["ldo_006_stub"])
    failures = [r for r in results if r.status == "fail"]
    assert not failures, "\n".join(f"{r.check}: {r.reason}" for r in failures)
    # its class-scoped template resolves from the ldo library, not amplifier's
    nl = assemble(ldo, "load_regulation", "ihp-sg13g2", "tt")
    assert "dc Iload" in nl and "XDUT vdd vout vss ldo_006_stub" in nl
