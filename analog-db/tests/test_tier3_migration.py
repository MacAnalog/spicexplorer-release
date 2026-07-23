"""Phase-3 gate: the loss-less migration of the 3 in-repo OTAs + the optimizer projection
generator + the NEWCAS regression gate. PDK-free."""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import generate, model, verify
from spicexplorer_analog_db.extends import generate_project_setup

MIGRATED = ["amp_018_telescopic_cascode", "amp_004_folded_cascode", "amp_001_5t"]
Project_Setup = pytest.importorskip("spicexplorer.core.domains").Project_Setup


def _platform_legacy_ota():
    """The platform's legacy ``examples/OTA/`` dir, or None when it's absent.

    The migration-fidelity tests below compare this DB against the platform's pre-migration
    netlists/configs. That legacy lives in spicexplorer-platform, NOT in this (extracted) DB
    repo — so when the DB is checked out standalone (its own CI) these tests skip cleanly. When
    the DB is mounted as the platform's examples/analog-db/ submodule, project_root() finds the
    platform root and the legacy is present, so the regression gate runs.
    """
    try:
        from spicexplorer_core import project_root
    except Exception:
        return None
    try:
        ota = project_root() / "examples" / "OTA"
    except Exception:
        return None
    return ota if (ota / "cascode").is_dir() else None


@pytest.mark.parametrize("cid", MIGRATED)
def test_migrated_circuit_clears_t0_t2(cid):
    results = verify.run_tier0([cid]) + verify.run_tier1([cid]) + verify.run_tier2([cid])
    failures = [r for r in results if r.status == "fail"]
    assert not failures, "\n".join(f"{r.tier} {r.check}: {r.reason}" for r in failures)


@pytest.mark.parametrize("cid", MIGRATED)
def test_generated_project_setup_is_current_and_loads(cid):
    c = model.load_circuit(cid)
    committed = (c.dir / "project_setup.yaml").read_text()
    assert committed == generate_project_setup(c.dir), f"{cid}: project_setup.yaml stale"
    proj = Project_Setup.from_yaml(str(c.dir / "project_setup.yaml"))
    assert proj.dut_params and proj.optimizer_config.target_specs.targets


# P4 atomic sweep: the legacy pair-encoded NEWCAS knobs map 1:1 onto the atomic FIRST-member
# symbols (the pair/mirror ties now live in abstract/params.yaml, not in the knob names).
_NEWCAS_KNOB_MAP = {
    "x_dut_m1m2_w": "x_dut_xm1_w", "x_dut_m1m2_l": "x_dut_xm1_l",
    "x_dut_m1cm2c_w": "x_dut_xm1c_w", "x_dut_m1cm2c_l": "x_dut_xm1c_l",
    "x_dut_m3m4_w": "x_dut_xm3_w", "x_dut_m3m4_l": "x_dut_xm3_l",
    "x_dut_m3cm4c_w": "x_dut_xm3c_w", "x_dut_m3cm4c_l": "x_dut_xm3c_l",
    "x_dut_m5_w": "x_dut_xm5_w", "x_dut_m5_l": "x_dut_xm5_l", "x_dut_m5_ng": "x_dut_xm5_ng",
    "x_dut_m6_w": "x_dut_xm6_w", "x_dut_m6_l": "x_dut_xm6_l",
    "x_dut_v_bias_1": "x_dut_v_bias_1", "x_dut_v_bias_2": "x_dut_v_bias_2",
}


def test_cascode_reproduces_newcas_baseline():
    """The generated telescopic config must span the SAME search space as the committed NEWCAS
    baseline (legacy examples/OTA/cascode project_setup.yaml): every legacy knob maps 1:1 onto
    an atomic knob with identical bounds/typing, and any extra atomic knobs are frozen (the
    P4 symbolized m literals — never searched). target_specs stay identical.
    Skips when the platform legacy is absent (standalone DB checkout)."""
    ota = _platform_legacy_ota()
    if ota is None:
        pytest.skip("platform examples/OTA legacy absent (standalone DB checkout)")
    c = model.load_circuit("amp_018_telescopic_cascode")
    legacy = Project_Setup.from_yaml(str(ota / "cascode/ihp-sg13g2/sizing/project_setup.yaml"))
    gen = Project_Setup.from_yaml(str(c.dir / "project_setup.yaml"))

    def knobs(p):
        return {dp.name.lower(): (round(dp.min_val, 12), round(dp.max_val, 12), getattr(dp, "is_integer", False))
                for dp in p.dut_params}

    def specs(p):
        return {t.name: (t.goal, float(t.target), t.sim_type, t.testbench, float(t.weight))
                for t in p.optimizer_config.target_specs.targets}

    frozen = {v["name"].lower() for v in c.sizing("ihp-sg13g2")["variables"] if v.get("freeze")}
    searched = {n: v for n, v in knobs(gen).items() if n not in frozen}
    mapped_legacy = {_NEWCAS_KNOB_MAP[n]: v for n, v in knobs(legacy).items()}
    assert searched == mapped_legacy, "searched dut_params drifted from the NEWCAS baseline"
    assert specs(gen) == specs(legacy), "target_specs drifted from the NEWCAS baseline"


def test_newcas_appendix_preserved_verbatim():
    """The research traces are migrated byte-for-byte (preserved verbatim).
    Skips when the platform legacy is absent (standalone DB checkout)."""
    import filecmp

    ota = _platform_legacy_ota()
    if ota is None:
        pytest.skip("platform examples/OTA legacy absent (standalone DB checkout)")
    src = ota / "cascode/NEWCAS_SUBMISSION_APPENDIX"
    dst = model.load_circuit("amp_018_telescopic_cascode").dir / "artifacts/newcas2026"
    names = [p.name for p in src.iterdir() if p.is_file()]
    match, mismatch, errors = filecmp.cmpfiles(src, dst, names, shallow=False)
    assert not mismatch and not errors, f"appendix not verbatim: mismatch={mismatch} errors={errors}"
    assert set(match) == set(names) and len(match) >= 15


def test_legacy_netlist_preserved_verbatim():
    """Skips when the platform legacy is absent (standalone DB checkout)."""
    ota = _platform_legacy_ota()
    if ota is None:
        pytest.skip("platform examples/OTA legacy absent (standalone DB checkout)")
    legacy = (ota / "cascode/ihp-sg13g2/spice/ota-improved.spice").read_text()
    migrated = (model.load_circuit("amp_018_telescopic_cascode").dir
                / "pdk/ihp-sg13g2/netlist.legacy.spice").read_text()
    assert legacy == migrated


def test_abstract_lowers_to_committed_pdk_netlist():
    """The migrated abstract cores still round-trip through circuitgraph lowering (drift guard)."""
    for cid in ["amp_018_telescopic_cascode", "amp_004_folded_cascode"]:
        c = model.load_circuit(cid)
        for pdk in c.pdks:
            assert (c.dir / "pdk" / pdk / "netlist.spice").read_text() == generate.lowered_netlist(c, pdk)
