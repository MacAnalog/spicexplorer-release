"""Spectre deck composition + `parameters` injection (Cadence-free).

Covers `render_spectre_deck` (injection precedence, corner-include replacement, temp,
the analysis-name contract warning) and `deck_spec_from_ngspice` (the lazy
circuitgraph-backed translation into a composable spec).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from spicexplorer.backends.spectre_deck import (
    DEFAULT_SIMULATOR_OPTIONS,
    OPPOINT_INFO_LINE,
    SAVE_OPTIONS_LINE,
    SpectreDeckSpec,
    ac_analysis,
    dc_oppoint_analysis,
    dc_sweep_analysis,
    deck_spec_from_ngspice,
    pac_analysis,
    pss_analysis,
    render_spectre_deck,
    sine_source,
    transient_analysis,
)

_SPEC = SpectreDeckSpec(
    title="tb",
    stimulus="V1 (vdd 0) vsource dc=vdd",
    subckt_blocks=("subckt d a b\nR1 (a b) resistor r=1k\nends d",),
    analyses=(dc_oppoint_analysis(), ac_analysis(1e3, 1e8, 101)),
    parameters={"vdd": 1.5, "w1": 1e-6},
    includes=('include "default.scs" section=tt_lvt',),
)


def test_render_layout_and_defaults() -> None:
    text = render_spectre_deck(_SPEC)
    lines = text.splitlines()
    assert lines[0] == "// tb"
    assert lines[1] == "simulator lang=spectre"
    assert lines[2] == "global 0"
    assert 'include "default.scs" section=tt_lvt' in text
    assert "parameters vdd=1.5 w1=1e-06" in text
    assert "subckt d a b" in text and "V1 (vdd 0) vsource dc=vdd" in text
    assert DEFAULT_SIMULATOR_OPTIONS in text
    assert "dcOp dc" in text
    assert "ac ac start=1000 stop=100000000 dec=101" in text
    # the measurement half never lands in the deck; the op dump + save options do
    assert OPPOINT_INFO_LINE in text and SAVE_OPTIONS_LINE in text
    assert "tempOptions" not in text  # only emitted when a corner temp is given


def test_injection_wins_and_keys_fold_to_lowercase() -> None:
    text = render_spectre_deck(_SPEC, parameters={"W1": 2e-6, "VDD": 1.35})
    assert "parameters vdd=1.35 w1=2e-06" in text
    assert "w1=1e-06" not in text


def test_corner_includes_replace_spec_defaults_and_temp_is_emitted() -> None:
    text = render_spectre_deck(
        _SPEC,
        corner_includes=['include "models.scs" section=ss_lvt'],
        temp=125.0,
    )
    assert 'include "models.scs" section=ss_lvt' in text
    assert "default.scs" not in text  # replaced, not accumulated (apply_corner semantics)
    assert "tempOptions options temp=125" in text


def test_misnamed_analysis_warns_about_the_psf_key_contract(caplog) -> None:
    spec = SpectreDeckSpec(title="t", stimulus="", analyses=("myac ac start=1 stop=10",))
    with caplog.at_level(logging.WARNING):
        render_spectre_deck(spec)
    assert any("must be NAMED" in r.message for r in caplog.records)


def test_pss_riders_require_a_preceding_pss() -> None:
    """`pac`/`pnoise` ride a periodic steady state — composing one without a pss BEFORE
    it must fail at render time, not cryptically inside
    Spectre. A pss composed first (or an `hb` base) passes."""
    from spicexplorer.backends.spectre_deck import pac_analysis, pnoise_analysis, pss_analysis

    pac, pn, pss = pac_analysis(), pnoise_analysis("out"), pss_analysis(1e6)
    for rider in (pac, pn):
        spec = SpectreDeckSpec(title="t", stimulus="", analyses=(rider,))
        with pytest.raises(ValueError, match="rides a periodic steady state"):
            render_spectre_deck(spec)
        # rider before the base is still wrong — the ORDER is the contract
        spec = SpectreDeckSpec(title="t", stimulus="", analyses=(rider, pss))
        with pytest.raises(ValueError, match="BEFORE"):
            render_spectre_deck(spec)
    ok = SpectreDeckSpec(title="t", stimulus="", analyses=(pss, pac, pn))
    assert "pac pac" in render_spectre_deck(ok)


def test_transient_analysis_builder_named_tran() -> None:
    # named `tran` so the result lands in a `tran.tran` PSF the swept reader picks up
    line = transient_analysis(1e-6, step=1e-9)
    assert line == "tran tran stop=1e-06 step=1e-09 errpreset=conservative"
    assert transient_analysis(2e-6).startswith("tran tran stop=2e-06")
    assert "errpreset" not in transient_analysis(1e-6, errpreset=None)
    assert "start=5e-07" in transient_analysis(1e-6, start=5e-7)


def test_sine_source_builder_large_signal_stimulus() -> None:
    line = sine_source("VINP", "vinp", "vcm", dc=0.6, ampl=0.1, freq=1e6)
    assert line == "VINP ( vinp vcm ) vsource type=sine dc=0.6 ampl=0.1 freq=1000000"
    # default reference node is ground
    assert sine_source("V1", "in", ampl=0.05, freq=2e3).startswith("V1 ( in 0 ) vsource type=sine")


def test_pss_analysis_builder_named_pss() -> None:
    # named `pss` so the harmonics land in the `pss.fd.pss` fd-PSF the swept reader picks up
    line = pss_analysis(1e6, harms=7, tstab=1e-5)
    assert line == "pss pss fund=1000000 harms=7 tstab=1e-05 errpreset=conservative"
    assert pss_analysis(2e6).startswith("pss pss fund=2000000 harms=7")
    assert "errpreset" not in pss_analysis(1e6, errpreset=None)
    assert "tstab" not in pss_analysis(1e6)  # optional


def test_pac_analysis_builder_named_pac() -> None:
    # named `pac` so the periodic transfer lands in the `pac.pac` PSF the swept reader picks up
    line = pac_analysis(start=1.0, stop=1e5, dec=20, maxsideband=7)
    assert line == "pac pac start=1 stop=100000 dec=20 maxsideband=7"
    assert pac_analysis().startswith("pac pac start=")
    # maxsideband=0 = driven baseband only (no fold-in)
    assert "maxsideband=0" in pac_analysis(maxsideband=0)


_TB = """* tiny tb
Vdd v_dd GND VDD
C1 v_out 0 CL
.param VDD=1.5
.param CL=50f
.end
"""


def test_deck_spec_from_ngspice_translates_and_injects(tmp_path: Path) -> None:
    deck = tmp_path / "tb.spice"
    deck.write_text(_TB)
    spec = deck_spec_from_ngspice(
        deck,
        pdk="tsmc-n65",
        analyses=(dc_oppoint_analysis(),),
        parameters={"VDD": 1.2},  # injection folds to the lowercase namespace
    )
    assert spec.parameters["vdd"] == 1.2
    assert spec.parameters["cl"] == pytest.approx(50e-15)
    assert "capacitor c=cl" in spec.stimulus
    assert "V_tie_GND (gnd 0) vsource dc=0" in spec.stimulus
    text = render_spectre_deck(spec, corner_includes=['include "m.scs" section=tt_lvt'])
    assert "vdd=1.2" in text and "section=tt_lvt" in text


def test_dc_sweep_analysis_builder_named_dc() -> None:
    # named `dc` so the swept transfer lands in the `dc.dc` PSF the swept reader prefers
    line = dc_sweep_analysis("VINP", 0.0, 1.2, 0.005)
    assert line == "dc dc dev=VINP param=dc start=0 stop=1.2 step=0.005"
