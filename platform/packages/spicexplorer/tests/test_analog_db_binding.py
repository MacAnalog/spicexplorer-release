"""Offline: the analog-db Spectre binding reader reproduces the amp_022 hand-transcribed dicts.

Proves the config-driven path (`backends.analog_db`) resolves the SAME sizing / supply /
corner / metric numbers the live tests used to hardcode — read from the committed, NDA-clean
binding YAMLs. No SPICE, no bridge, no kit; gated only on the analog-db submodule being present
(point `SPICEXPLORER_ANALOG_DB` at a populated checkout from a worktree with an empty submodule).
"""

from __future__ import annotations

import pytest
from spicexplorer.backends.analog_db import (
    MetricTarget,
    analog_db_root,
    load_analysis,
    load_datasheet_metrics,
    load_sizing,
    pdk_supply,
    raw_deck_path,
    resolve_corner,
)

_CIRCUIT = "amp_022_fer_two_stage"
_PDK = "FOUNDRY-n65"


def _have_binding() -> bool:
    try:
        return (analog_db_root() / "circuits" / _CIRCUIT / "pdk" / _PDK / "sizing.yaml").is_file()
    except Exception:
        return False


_needs_db = pytest.mark.skipif(
    not _have_binding(),
    reason="analog-db amp_022 FOUNDRY-n65 binding not checked out (set SPICEXPLORER_ANALOG_DB)",
)


# ---------------------------------------------------------------- pure (no analog-db)
def test_metric_target_band_and_nan():
    t = MetricTarget("dc_gain_db", {"meas": "dcgain", "out": "vout"}, "ac", spec_min=40.0)
    assert t.satisfied(47.4)
    assert not t.satisfied(30.0)  # below min
    assert not t.satisfied(float("nan"))  # NaN never satisfies
    imax = MetricTarget("i_supply", {"meas": "i_supply", "probe": "i(vvdd)"}, "op", spec_max=5.0e-4)
    assert imax.satisfied(2.5e-4)
    assert not imax.satisfied(6.0e-4)  # above max


# ------------------------------------------------------------ reproduce the hardcoded dicts
@_needs_db
def test_load_sizing_matches_committed_defaults():
    # Pins the binding reader against the committed sizing.yaml (post the 2026-07-13
    # parameterization knob rename: atomic per-instance x_dut_* symbols, incl. the
    # frozen finger counts). The live tests now DERIVE their sizing from this same
    # loader — hand-transcribed dicts drift. The binding carries the current
    # gm/ID re-sizing.
    assert load_sizing(_CIRCUIT, _PDK) == {
        "x_dut_xmbd_w": "4u", "x_dut_xm7_w": "4u", "x_dut_xm0_w": "10u",
        "x_dut_xm3_w": "1u",
        "x_dut_xm7_l": "4.5u", "x_dut_xm0_l": "3u", "x_dut_xm3_l": "3u",
        "x_dut_xm2_l": "1u", "x_dut_xmbd_l": "4u",
        "x_dut_cc_value": "2e-12",
        "x_dut_xm0_m": "5", "x_dut_xm3_m": "2", "x_dut_xm2_m": "24",
        "x_dut_xm7_m": "3", "x_dut_xmbd_m": "1",
    }


@_needs_db
def test_pdk_supply_is_core_rail():
    # the `vdd: 1.2` the tests hardcoded (KIT65 core rail), overriding the datasheet's 1.5 V default
    assert pdk_supply(_PDK) == pytest.approx(1.2)


@_needs_db
def test_resolve_corner_is_generic_and_neutral():
    c = resolve_corner(_CIRCUIT, _PDK, "tt")
    assert c.name == "FOUNDRY-n65_tt"
    assert c.temp == 27.0
    # generic label + NEUTRAL wrapper — the kit-native `tt_lvt` never appears (operator wrapper maps it)
    assert [(i.lib_file, i.section) for i in c.model_includes] == [("FOUNDRY_n65_models.scs", "tt")]
    assert all("lvt" not in i.section for i in c.model_includes)
    assert [(s.node, s.value) for s in c.supplies] == [("VDD", 1.2)]


@_needs_db
def test_resolve_corner_unknown_label_raises():
    with pytest.raises(KeyError):
        resolve_corner(_CIRCUIT, _PDK, "zz")


@_needs_db
def test_raw_deck_path_resolves():
    p = raw_deck_path(_CIRCUIT, _PDK, "ac_open_loop")
    assert p.is_file() and p.name == "ac_open_loop.spice"


@_needs_db
def test_load_datasheet_ac_metrics_recipes_and_bands():
    by = {t.name: t for t in load_datasheet_metrics(_CIRCUIT, only={"dc_gain_db", "ugf_hz", "pm_deg"})}
    assert set(by) == {"dc_gain_db", "ugf_hz", "pm_deg"}
    assert by["dc_gain_db"].recipe == {"meas": "dcgain", "out": "vout"}
    assert by["dc_gain_db"].analysis == "ac"
    assert by["dc_gain_db"].spec_min == 40.0
    assert by["ugf_hz"].recipe["meas"] == "ugf" and by["ugf_hz"].spec_min == pytest.approx(5.0e6)
    assert by["pm_deg"].recipe["meas"] == "pm" and by["pm_deg"].spec_min == 60.0


@_needs_db
def test_load_analysis_ac_open_loop_params():
    a = load_analysis(_CIRCUIT, "ac_open_loop")
    assert a["id"] == "ac_open_loop"
    params = a["params"]
    # the AC sweep the live test hand-set as ac_analysis(1, 1e9, …) — here from the descriptor
    assert params["FSTART"] == 1
    assert str(params["FSTOP"]) == "1G"
    assert params["PPD"] == 50


# ---------------- engine-driven Spectre calculator route + FD (offline render checks) --------
@_needs_db
def test_differential_output_detection():
    """circuit.yaml ports drive FD detection: a diff-output DUT vs a single-ended one."""
    from spicexplorer.backends.analog_db import differential_output

    assert differential_output("amp_022_fer_two_stage") is None  # single-ended vout
    assert differential_output("amp_020_two_stage_miller_cmfb") == ("voutp", "voutn")


@_needs_db
def test_spectre_calculator_covers_ac_and_noise_and_pm_is_dc_referenced():
    """The class calculator (the Spectre metric path) renders dcgain/ugf/pm + inoise_total,
    and pm is the DC-referenced expression (not OCEAN's phaseMargin, which is 180° off for
    inverting amps)."""
    from spicexplorer.backends.analog_db import bench_ocean_measurements

    ac = {m.name: m for m in bench_ocean_measurements("amp_022_fer_two_stage", "ac_open_loop", pdk=_PDK)}
    assert {"dcgain", "ugf", "pm"} <= set(ac)
    assert "phaseMargin" not in ac["pm"].expr  # the buggy builtin is gone
    assert "phase(value(" in ac["pm"].expr and "180" in ac["pm"].expr  # DC-referenced form
    noise = {m.name: m for m in bench_ocean_measurements("amp_022_fer_two_stage", "noise", pdk=_PDK)}
    assert "inoise_total" in noise and 'getData("in")' in noise["inoise_total"].expr


@_needs_db
def test_fd_ac_metrics_use_differential_output():
    """A fully-differential DUT's AC calculator exprs read v(voutp)-v(voutn), not v(vout)."""
    from spicexplorer.backends.analog_db import bench_ocean_measurements

    ac = {m.name: m for m in bench_ocean_measurements("amp_020_two_stage_miller_cmfb", "ac_open_loop", pdk=_PDK)}
    assert '(v("voutp")-v("voutn"))' in ac["dcgain"].expr
    assert 'v("vout")' not in ac["dcgain"].expr and 'v("vout")' not in ac["pm"].expr
