"""Robustness edges: path overrides, unknown circuits, measure-parsing formats, assemble error
paths (test-suite review 2026-06-11, analog-db backlog). All PDK-free."""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import assemble, model, paths, runner


# ── paths: the env-var override seam ──────────────────────────────────────────────────────────
def test_env_override_is_honored_verbatim_even_if_nonexistent(tmp_path, monkeypatch):
    """$SPICEXPLORER_ANALOG_DB wins unconditionally; a nonexistent target resolves (no eager
    existence check) and downstream listing degrades to empty, not a crash."""
    ghost = tmp_path / "not" / "a" / "db"
    monkeypatch.setenv(paths.ENV_VAR, str(ghost))
    assert paths.db_root() == ghost.resolve()
    assert model.list_circuit_ids() == []          # missing circuits/ → empty, not raise


def test_env_override_expands_user_and_resolves_relative(tmp_path, monkeypatch):
    monkeypatch.setenv(paths.ENV_VAR, str(tmp_path / "sub" / ".." / "db"))
    assert paths.db_root() == (tmp_path / "db").resolve()   # `..` collapsed by resolve()


# ── model: unknown circuit is a clear error ───────────────────────────────────────────────────
def test_load_circuit_unknown_id_names_known_ids():
    with pytest.raises(KeyError, match="unknown circuit 'nope'.*amp_001_5t"):
        model.load_circuit("nope")


# ── model: Circuit.netlist(pdk) parity with sizing(pdk); clear errors ─────────────────────────
def test_circuit_netlist_and_pdk_dir_accessors():
    c = model.load_circuit("amp_001_5t")
    pdk = c.pdks[0]
    assert c.pdk_dir(pdk).is_dir()
    assert c.netlist(pdk).is_file() and c.netlist(pdk).name == "netlist.spice"
    assert c.abstract_netlist().is_file()
    # an unbound PDK names the available bindings instead of leaking a raw path
    with pytest.raises(FileNotFoundError, match="not bound to pdk 'nope'"):
        c.netlist("nope")


# ── runner: measure-line formats ──────────────────────────────────────────────────────────────
@pytest.mark.parametrize("line,name,value", [
    ("dcgain = 29.78", "dcgain", 29.78),
    ("ugf = 1e7", "ugf", 1e7),                  # exponent without sign
    ("ugf = 1.5e+07", "ugf", 1.5e7),            # signed exponent
    ("vos = -1.2e-3", "vos", -1.2e-3),          # negative mantissa
    ("  pm   =   61.4  ", "pm", 61.4),          # whitespace variants
])
def test_parse_measures_numeric_formats(line, name, value):
    measures, failed = runner.parse_measures(line)
    assert measures == {name: pytest.approx(value)} and failed == []


def test_parse_measures_empty_and_failed():
    measures, failed = runner.parse_measures("ngspice chatter\nnothing here\n")
    assert measures == {} and failed == []
    measures, failed = runner.parse_measures("tcross = failed\ndcgain = 30.0\n")
    assert measures == {"dcgain": 30.0} and failed == ["tcross"]


# ── assemble: error paths are loud and named ──────────────────────────────────────────────────
def test_assemble_unknown_analysis_raises_with_path():
    ckt = model.load_circuit("amp_001_5t")
    with pytest.raises(FileNotFoundError, match="nonexistent_analysis"):
        assemble.assemble(ckt, "nonexistent_analysis", "ihp-sg13g2", "tt")


def test_assemble_missing_lowered_netlist_raises(tmp_path):
    """A circuit bound to a PDK whose lowered netlist file is absent must fail clearly at the
    DUT-subckt step, not emit a deck with a hole in it."""
    ckt = model.load_circuit("amp_001_5t")
    with pytest.raises(Exception, match="gf999|No such file|netlist"):
        assemble.dut_subckt(ckt, "gf999-nonexistent-pdk")
