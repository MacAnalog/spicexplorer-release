"""Offline: the Spectre template DB (analysis configs + SKILL calculator expressions).

Renders a miniature engine DB (the same shapes analog-db commits under
`_shared/engines/spectre/` + `_shared/classes/amplifier/spectre-benches.yaml`) and pins:
the placeholder/optional-segment grammar, `$context` resolution, bench composition
PARITY with the built-in `_spectre_analyses` fallback (same statements, byte-for-byte),
and the calculator rows rendering into valid `OceanMeasurement`s. No SPICE, no bridge.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer.backends.spectre_templates import (
    SpectreTemplateError,
    bench_analyses,
    bench_measurements,
    load_analysis_templates,
    render_template,
)

_ENGINE_YAML = """\
schema: spicexplorer/spectre-analyses@1
templates:
  dc_op: {statement: "dcOp dc"}
  ac: {statement: "ac ac start={FSTART} stop={FSTOP} dec={PPD}"}
  dc_sweep: {statement: "dc dc dev={DEV} param=dc start={START} stop={STOP} step={STEP}"}
  noise: {statement: "noise ( {OUT} 0 ) noise start={FSTART} stop={FSTOP} dec={PPD}[ iprobe={IPROBE}]"}
  tran: {statement: "tran tran stop={TSTOP}[ step={TSTEP}] errpreset=conservative"}
  pss:
    statement: "pss pss fund={FUND} harms={HARMS}[ tstab={TSTAB}] errpreset=conservative"
    defaults: {HARMS: 7}
  stb: {statement: "stb stb probe={PROBE} start={FSTART} stop={FSTOP} dec={PPD}"}
"""

_CALC_YAML = """\
schema: spicexplorer/spectre-calculator@1
expressions:
  gain_db_at: {result: ac, expr: 'value(dB20(v("{OUT}")) {FREQ})'}
  neg_gain_db_at: {result: ac, expr: '-value(dB20(v("{OUT}")) {FREQ})'}
  hd2_db: {result: pss_fd, expr: 'dB20(mag(harmonic(v("{OUT}") 2)) / mag(harmonic(v("{OUT}") 1)))'}
  pm_loop: {result: stb, expr: 'phaseMargin(getData("loopGain"))'}
"""

_BENCHES_YAML = """\
schema: spicexplorer/spectre-benches@1
class: amplifier
benches:
  ac_open_loop:
    analyses: [{template: dc_op}, {template: ac}]
    calculator:
      - {name: dcgain, expr: gain_db_at, args: {OUT: vout, FREQ: $FSTART}}
  cmrr_vcm:
    analyses: [{template: dc_op}, {template: ac}]
    calculator:
      - {name: cmrr_db, expr: neg_gain_db_at, args: {OUT: vout, FREQ: $FSTART}}
  noise:
    analyses: [{template: dc_op}, {template: noise, args: {OUT: vout, IPROBE: VINP}}]
  tran_step:
    analyses: [{template: dc_op}, {template: tran}]
  linearity:
    analyses: [{template: dc_sweep, args: {DEV: VINP, START: 0, STOP: $RAIL, STEP: $VSWEEP_STEP}}]
  thd:
    analyses: [{template: pss, args: {FUND: $F0}}]
    calculator:
      - {name: hd2_db, expr: hd2_db, args: {OUT: vout}}
  iip3:
    analyses: [{template: pss, args: {FUND: $IIP3_FUND, HARMS: $IIP3_HARMS}}]
  stb:
    analyses: [{template: dc_op}, {template: stb, args: {PROBE: VIPRB}}]
    calculator:
      - {name: pm_loop, expr: pm_loop}
"""


@pytest.fixture()
def mini_db(tmp_path: Path) -> Path:
    engine = tmp_path / "_shared/engines/spectre"
    engine.mkdir(parents=True)
    (engine / "analyses.yaml").write_text(_ENGINE_YAML)
    (engine / "calculator.yaml").write_text(_CALC_YAML)
    cls = tmp_path / "_shared/classes/amplifier"
    cls.mkdir(parents=True)
    (cls / "spectre-benches.yaml").write_text(_BENCHES_YAML)
    return tmp_path


# ------------------------------------------------------------------ template grammar
def test_render_template_substitutes_and_formats():
    ctx = {"FSTART": 1000.0, "FSTOP": 1e9, "PPD": 101.0}
    got = render_template("ac ac start={FSTART} stop={FSTOP} dec={PPD}", ctx)
    # %.10g — plain numerics, never SPICE eng suffixes (the Spectre M/m landmine)
    assert got == "ac ac start=1000 stop=1000000000 dec=101"


def test_render_template_optional_segment_drops_when_unresolved():
    tpl = "tran tran stop={TSTOP}[ step={TSTEP}] errpreset=conservative"
    assert render_template(tpl, {"TSTOP": 5e-6, "TSTEP": 1e-9}) == (
        "tran tran stop=5e-06 step=1e-09 errpreset=conservative"
    )
    assert render_template(tpl, {"TSTOP": 5e-6}) == (
        "tran tran stop=5e-06 errpreset=conservative"
    )


def test_render_template_missing_placeholder_raises():
    with pytest.raises(SpectreTemplateError, match="FSTOP"):
        render_template("ac ac start={FSTART} stop={FSTOP}", {"FSTART": 1.0})


# ------------------------------------------------------------------ bench composition
def test_bench_analyses_parity_with_builtin_fallback(mini_db: Path):
    """The template DB must reproduce the built-in composition byte-for-byte."""
    from spicexplorer.backends.analog_db import _spectre_analyses, _spectre_context

    cases = [
        ("ac_open_loop", {"FSTART": "1k", "FSTOP": "1G", "PPD": 101}, None),
        ("cmrr_vcm", {"FSTART": "1k", "FSTOP": "1G", "PPD": 101}, None),
        ("noise", {"FSTART": "1k", "FSTOP": "100MEG", "PPD": 50}, None),
        ("tran_step", {"TSTOP": "5u", "TSTEP": "1n"}, None),
        ("linearity", {"VDD": 1.5, "VSWEEP_STEP": "5m"}, 1.2),
        ("thd", {"F0": "1.0e6", "HARMS": 7}, None),
        ("iip3", {"F1": "0.9e6", "F2": "1.0e6"}, None),
        ("stb", {"FSTART": "1k", "FSTOP": "1G", "PPD": 101}, None),
    ]
    for tb, params, supply in cases:
        ctx = _spectre_context(tb, params, supply=supply)
        data_driven = bench_analyses(tb, ctx, root=mini_db)
        builtin = _spectre_analyses(tb, params, supply=supply, root=mini_db / "nonexistent")
        assert data_driven == builtin, f"{tb}: template DB diverged from the built-in composition"


def test_spectre_analyses_prefers_the_template_db(mini_db: Path, monkeypatch):
    """With a DB present, composition is data-driven (probe: a DB-only statement tweak shows up)."""
    from spicexplorer.backends.analog_db import _spectre_analyses

    engine = mini_db / "_shared/engines/spectre/analyses.yaml"
    engine.write_text(_ENGINE_YAML.replace("dcOp dc", "dcOp dc oppoint=logfile"))
    op, _ac = _spectre_analyses("ac_open_loop", {"FSTART": "1k", "FSTOP": "1G", "PPD": 101}, root=mini_db)
    assert op == "dcOp dc oppoint=logfile"


def test_bench_analyses_unknown_bench_raises_keyerror(mini_db: Path):
    with pytest.raises(KeyError):
        bench_analyses("no_such_bench", {}, root=mini_db)


def test_bench_analyses_unknown_template_is_a_config_error(mini_db: Path):
    benches = mini_db / "_shared/classes/amplifier/spectre-benches.yaml"
    benches.write_text(_BENCHES_YAML.replace("{template: dc_op}, {template: ac}", "{template: nope}", 1))
    with pytest.raises(SpectreTemplateError, match="nope"):
        bench_analyses("ac_open_loop", {"FSTART": 1.0, "FSTOP": 2.0, "PPD": 3}, root=mini_db)


def test_iip3_context_derives_the_pss_plan():
    """F1/F2 → common fundamental, harmonic budget, tone + IM3 indices (the QPSS dodge)."""
    from spicexplorer.backends.analog_db import _spectre_context

    ctx = _spectre_context("iip3", {"F1": "0.9e6", "F2": "1.0e6", "ASIG": 0.05})
    assert ctx["IIP3_FUND"] == pytest.approx(1e5)
    assert (ctx["IIP3_N1"], ctx["IIP3_N2"]) == (9, 10)
    assert (ctx["IIP3_NIM3A"], ctx["IIP3_NIM3B"]) == (8, 11)
    assert ctx["IIP3_HARMS"] == 21


# ------------------------------------------------------------------ calculator route
def test_bench_measurements_render_ocean_rows(mini_db: Path):
    from spicexplorer.backends.analog_db import _spectre_context

    ctx = _spectre_context("cmrr_vcm", {"FSTART": "1k", "FSTOP": "1G", "PPD": 101})
    (m,) = bench_measurements("cmrr_vcm", ctx, root=mini_db)
    assert (m.name, m.result) == ("cmrr_db", "ac")
    assert m.expr == '-value(dB20(v("vout")) 1000)'

    (pm,) = bench_measurements("stb", ctx, root=mini_db)
    assert (pm.name, pm.result) == ("pm_loop", "stb")
    assert pm.expr == 'phaseMargin(getData("loopGain"))'

    # a bench with no calculator rows renders an empty set, not an error
    assert bench_measurements("noise", ctx, root=mini_db) == []


def test_bench_measurements_unresolved_context_reference_raises(mini_db: Path):
    with pytest.raises(SpectreTemplateError, match="FSTART"):
        bench_measurements("cmrr_vcm", {"PPD": 101}, root=mini_db)


def test_real_db_parity_if_checked_out():
    """When a populated analog-db (with the engine DB) is reachable, the committed YAMLs
    must reproduce the built-in composition too — the same parity the mini DB pins."""
    from spicexplorer.backends.analog_db import _spectre_analyses, _spectre_context, analog_db_root

    root = analog_db_root()
    if not (root / "_shared/engines/spectre/analyses.yaml").is_file():
        pytest.skip("no analog-db checkout with the Spectre engine template DB")
    for tb, params, supply in [
        ("ac_open_loop", {"FSTART": "1k", "FSTOP": "1G", "PPD": 101}, None),
        ("thd", {"F0": "1.0e6", "HARMS": 7}, None),
        ("iip3", {"F1": "0.9e6", "F2": "1.0e6"}, None),
        ("linearity", {"VDD": 1.5, "VSWEEP_STEP": "5m"}, 1.2),
        ("stb", {"FSTART": "1k", "FSTOP": "1G", "PPD": 101}, None),
    ]:
        ctx = _spectre_context(tb, params, supply=supply)
        assert bench_analyses(tb, ctx, root=root) == _spectre_analyses(
            tb, params, supply=supply, root=root / "nonexistent"
        )


def test_load_analysis_templates_missing_db_raises_unavailable(tmp_path: Path):
    from spicexplorer.backends.analog_db import AnalogDbUnavailable

    with pytest.raises(AnalogDbUnavailable):
        load_analysis_templates(root=tmp_path)
