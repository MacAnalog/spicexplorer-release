"""Simulator-log parsing: both engines' dialects classify correctly."""

from __future__ import annotations

import pytest
from spicexplorer_waveview import classify_line, discover_log, parse_log_text, parse_sim_log
from spicexplorer_waveview.testing import synth_ac_raw

NGSPICE_LOG = """\
Note: Compatibility modes selected: a
Circuit: * 5t ota testbench
Warning: Model issued on line 42
Error: unknown subckt: xdut a b c
No. of Data Rows : 601
Note: Simulation executed
"""

SPECTRE_LOG = """\
Loading /opt/cadence/spectre.so ...
Notice (SPICE_COMPAT-1): compatibility mode enabled.
WARNING (SPECTRE-16912): rising delay is negative.
ERROR (SFE-23): "amp.scs" 12: unknown parameter 'wibble'.
Aggregate audit (7:11:03 PM):
"""


@pytest.mark.parametrize(
    "line,level",
    [
        ("Error: unknown subckt", "error"),
        ("ERROR (SFE-23): bad param", "error"),
        ("Fatal error: out of memory", "error"),
        ("Warning: model issued", "warning"),
        ("WARNING (SPECTRE-16912): negative delay", "warning"),
        ("Note: Compatibility modes selected: a", "note"),
        ("Notice (SPICE_COMPAT-1): enabled", "note"),
        ("No. of Data Rows : 601", "info"),
        ("tran: time = 5.2 us", "info"),
        ("Transient analysis failed", "error"),
        ("gmin stepping: no convergence", "error"),
    ],
)
def test_classify_line(line, level):
    assert classify_line(line) == level


def test_parse_counts_ngspice():
    s = parse_log_text(NGSPICE_LOG)
    assert s.counts["error"] == 1
    assert s.counts["warning"] == 1
    assert s.counts["note"] == 2
    assert s.n_lines == 6
    assert s.lines[3].level == "error" and s.lines[3].no == 4


def test_parse_counts_spectre():
    s = parse_log_text(SPECTRE_LOG)
    assert s.counts["error"] == 1
    assert s.counts["warning"] == 1
    assert s.counts["note"] == 1


def test_filtered_floor():
    s = parse_log_text(NGSPICE_LOG)
    assert [ln.level for ln in s.filtered("warning")] == ["warning", "error"]
    assert len(s.filtered("info")) == s.n_lines


def test_parse_sim_log_reads_file(tmp_path):
    p = tmp_path / "run.log"
    p.write_text(NGSPICE_LOG)
    s = parse_sim_log(p)
    assert s.path == str(p)
    assert s.counts["error"] == 1


def test_discover_log_ngspice_sibling(tmp_path):
    raw = tmp_path / "tb.raw"
    synth_ac_raw(raw)
    log = tmp_path / "tb.log"
    log.write_text("Note: ok\n")
    assert discover_log(raw, "ngspice") == str(log)


def test_discover_log_spectre_parent(tmp_path):
    rawdir = tmp_path / "amp-raw"
    rawdir.mkdir()
    out = tmp_path / "spectre.out"
    out.write_text("Aggregate audit\n")
    assert discover_log(rawdir, "spectre") == str(out)


def test_discover_log_none(tmp_path):
    raw = tmp_path / "tb.raw"
    synth_ac_raw(raw)
    assert discover_log(raw, "ngspice") is None


# The line rules are core's `spice_engine.sim_log`, re-exported here beside `parse_log_text`.


def test_parse_measures_and_fatal_lines_reexported():
    from spicexplorer_core.spice_engine import sim_log
    from spicexplorer_waveview import fatal_lines, parse_measures
    from spicexplorer_waveview.logs import fatal_lines as fl2
    from spicexplorer_waveview.logs import parse_measures as pm2

    assert parse_measures is sim_log.parse_measures is pm2
    assert fatal_lines is sim_log.fatal_lines is fl2
    log = (
        "Error: measure  bad  when(WHEN) : out of interval\n"
        " meas tran bad when v(a)=5 failed!\n"
        "good                =  1.500000e-09\n"
        "Warning: singular matrix:  check nodes a and b\n"
    )
    assert parse_measures(log) == ({"good": 1.5e-9}, ["bad"])
    assert fatal_lines(log) == []
    s = parse_log_text(log)
    assert s.counts == {"error": 1, "warning": 1, "note": 0, "info": 2}


@pytest.mark.parametrize(
    "line,level",
    [
        ("doAnalyses: iteration limit reached", "error"),
        ("Transient solution failed", "error"),
        ("doAnalyses: TRAN:  Timestep too small; time = 1e-9", "error"),
        ("singular matrix: check nodes a and b", "error"),
        ("Warning: singular matrix:  check nodes a and b", "warning"),
        ("Warning: 'r1 a 0' is not a valid resistor instance line, ignored!", "error"),
        ("Error on line 12 : xm1 ... Unknown model type xyz", "error"),
    ],
)
def test_classify_fatal_forms(line, level):
    assert classify_line(line) == level
