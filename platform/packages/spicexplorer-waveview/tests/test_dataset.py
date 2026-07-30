"""WaveDataset resolution + the DatasetResult SimResult-protocol semantics."""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_waveview import DatasetResult, WaveAnalysis, WaveDataset, WaveSignal


@pytest.fixture()
def ds() -> WaveDataset:
    ac = WaveAnalysis(analysis="ac", native_name="AC Analysis", sweep="frequency")
    f = np.logspace(0, 6, 11)
    ac.signals["frequency"] = WaveSignal("frequency", f, units="Hz")
    ac.signals["v(vout)"] = WaveSignal("v(vout)", 10.0 / (1 + 1j * f / 1e3), units="V")
    op = WaveAnalysis(analysis="op", native_name="Operating Point")
    op.signals["v(vdd)"] = WaveSignal("v(vdd)", np.array([1.8]))
    op.scalars["v(vdd)"] = 999.0  # scalars are authoritative over same-named signals
    op.scalars["M0:gm"] = 2e-3
    return WaveDataset(source="mem", engine="ngspice", analyses={"ac": ac, "op": op})


def test_resolve_common_aliases(ds):
    assert ds.resolve_analysis("oppoint") is ds.analyses["op"]
    assert ds.resolve_analysis("AC") is ds.analyses["ac"]
    assert ds.resolve_analysis("nope") is None


def test_engine_alias_layer():
    noise = WaveAnalysis(analysis="noise", native_name="noise.noise", sweep="freq")
    d = WaveDataset(
        source="mem", engine="spectre",
        analyses={"noise": noise},
        aliases={"noise_spectrum": "noise", "noise_spectral": "noise"},
    )
    assert d.resolve_analysis("noise_spectrum") is noise
    assert d.resolve_analysis("noise_spectral") is noise  # via common → engine alias chain


def test_find_signal_tolerance(ds):
    assert ds.find_signal("ac", "v(vout)") is not None  # exact
    assert ds.find_signal("ac", "V(VOUT)") is not None  # case-insensitive
    assert ds.find_signal("ac", "vout") is not None  # bare → v(...) wrap
    assert ds.find_signal("ac", "missing") is None


def test_find_signal_unwrap():
    an = WaveAnalysis(analysis="ac", native_name="ac.ac", sweep="freq")
    an.signals["vout"] = WaveSignal("vout", np.ones(3))
    d = WaveDataset(source="mem", engine="spectre", analyses={"ac": an})
    assert d.find_signal("ac", "v(vout)") is not None  # wrapped → bare


def test_result_scalar_semantics(ds):
    r = DatasetResult(ds)
    assert r.scalar("v(vdd)", "op") == 999.0  # scalars win over the signal
    assert r.scalar("M0:gm", "op") == pytest.approx(2e-3)
    # inst:param op scalars are reachable from any analysis (op fallback)
    assert r.scalar("M0:gm", "ac") == pytest.approx(2e-3)
    assert np.isnan(r.scalar("missing", "op"))
    assert np.isnan(r.scalar("anything", "no_such_analysis"))


def test_result_wave_semantics(ds):
    r = DatasetResult(ds)
    w = r.wave("v(vout)", "ac")
    assert np.iscomplexobj(w) and w.size == 11
    with pytest.raises(KeyError, match="no signal 'missing'"):
        r.wave("missing", "ac")
    with pytest.raises(KeyError, match="analysis not in dataset"):
        r.wave("v(vout)", "tran")


def test_registry_protocol_conformance(ds):
    """DatasetResult must satisfy core's runtime-checkable SimResult protocol."""
    from spicexplorer_core.spice_engine.protocol import SimResult

    assert isinstance(DatasetResult(ds), SimResult)
