"""Guard: a FROZEN-operating-point small-signal analysis (``.ac`` / ``.noise``) must never be
assembled, run, or declared on a CLOCKED (chopper / switched-capacitor) circuit — it freezes the
switches, so the figure is physically wrong. The in-operation replacements are the transient
benches (native) and PSS/PAC/pnoise (Spectre). All PDK-free.

Enforced in two places (both covered here):
  * runtime  — ``assemble()`` raises ``AssembleError`` (the universal bind/run/export chokepoint);
  * authored — ``verify`` Tier-0 ``xref:no_frozen_ss_on_clocked``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spicexplorer_analog_db import model, verify
from spicexplorer_analog_db.assemble import AssembleError, assemble

CLOCKED = ["ia_002_fan_chopper_simple", "ia_003_fan_chopper_pf", "ia_004_fan_chopper_rrl"]


def _synthetic_clocked(analyses: list[str]) -> model.Circuit:
    """A minimal in-memory clocked circuit (has clk_* ports) — the assemble guard fires before
    any file is read, so no on-disk fixture is needed."""
    return model.Circuit(
        id="synthetic_clocked",
        dir=Path("/nonexistent"),
        manifest={
            "class": "ia",
            "ports": ["vinp", "vinn", "voutp", "voutn", "clk_chin", "clk_chin_not", "vdd", "vss"],
            "analyses": analyses,
        },
    )


def test_frozen_smallsignal_classification():
    for a in ("ac_closed_loop", "ac_zin_diff", "ac_open_loop", "cmrr_vcm", "psrr_vdd", "stb", "noise"):
        assert model.is_frozen_smallsignal_analysis(a), f"{a} should be frozen-SS"
    for a in ("pac_gain", "pac_zin", "pnoise_chopped", "tran_chopper_ripple", "dc_op", "tran_zin_chopped"):
        assert not model.is_frozen_smallsignal_analysis(a), f"{a} should NOT be frozen-SS"


def test_is_clocked_predicate():
    # clocked: exposes a chopper/SC clock port
    for cid in CLOCKED + ["sup_003_rrl_sc_integrator"]:
        assert model.load_circuit(cid).is_clocked, f"{cid} should be clocked"
    # continuous IA and the statically-transparent chopper core are NOT clocked (no clk_* port)
    for cid in ("ia_001_hsu_bandpass_classab", "amp_026_fan_chopper_ota", "amp_001_5t"):
        assert not model.load_circuit(cid).is_clocked, f"{cid} should NOT be clocked"


def test_assemble_refuses_ac_and_noise_on_clocked():
    c = _synthetic_clocked(["ac_closed_loop"])
    with pytest.raises(AssembleError, match="clocked"):
        assemble(c, "ac_closed_loop", "ihp-sg13g2")
    with pytest.raises(AssembleError, match="clocked"):
        assemble(c, "noise", "ihp-sg13g2")
    with pytest.raises(AssembleError, match="clocked"):
        assemble(c, "ac_zin_diff", "ihp-sg13g2")


def test_assemble_allows_transient_on_clocked():
    # a real transient bench on a real clocked circuit assembles fine — the guard is scoped to the
    # frozen-OP small-signal family only, not to the in-operation (transient/PSS) benches.
    c = model.load_circuit("ia_002_fan_chopper_simple")
    nl = assemble(c, "tran_chopper_ripple", "ihp-sg13g2")
    assert "XDUT" in nl and "${" not in nl


def test_corpus_has_no_ac_on_clocked():
    """Invariant: no clocked circuit declares a frozen-OP small-signal analysis."""
    offenders = {
        c.id: [a for a in c.analyses if model.is_frozen_smallsignal_analysis(a)]
        for c in model.load_all_circuits()
        if c.is_clocked and any(model.is_frozen_smallsignal_analysis(a) for a in c.analyses)
    }
    assert not offenders, f"clocked circuits declaring AC/.noise analyses: {offenders}"


def test_tier0_guard_check_runs_and_passes():
    results = [r for r in verify.run_tier0(CLOCKED) if r.check == "xref:no_frozen_ss_on_clocked"]
    assert results, "xref:no_frozen_ss_on_clocked did not run for the chopper circuits"
    fails = [r for r in results if r.status == "fail"]
    assert not fails, f"unexpected guard fails: {[(r.circuit, r.reason) for r in fails]}"
