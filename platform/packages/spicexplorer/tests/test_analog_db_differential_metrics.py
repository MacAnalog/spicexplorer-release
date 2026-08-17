"""Regression: a fully-differential analog-db circuit must be measurable through the REGISTRY route,
and one broken metric recipe must not sink the whole bench.

cross_repo_audit finding (O-2) — ``differential_output()`` reports a DUT's ``(voutp, voutn)`` pair,
but only the **Spectre calculator** route consulted it (``bench_ocean_measurements``). The registry
route kept ``load_datasheet_metrics``' single-ended ``out='vout'`` default, so every metric of a
fully-differential circuit raised ``IndexError: PlotData object doesn't contain trace "v(vout)"`` —
17 analog-db circuits (amp_020/023/025/026/027/028/029/030/031, cmp_002, dp_001, ia_001..005,
sup_003), most of them on the open ngspice lane. Compounding it, ``evaluate()`` had no per-metric guard,
so ONE bad recipe aborted the circuit instead of that one metric.

The fix resolves the pair in ``run_circuit`` and reads the DIFFERENCE across it
(``_DifferentialSimResult``). The registry's own ``ref`` key cannot express that: it SUBTRACTS on
the transient path but DIVIDES on the AC path (the series-sense ``zin_mag`` ratio), so an AC recipe
with ``ref=voutn`` would silently return ``voutp/voutn`` ≈ -1. Measured live on
amp_023/ihp-sg13g2: the ratio reads dcgain = -4.5e-13 dB / PM = 180°, the difference reads
65.93 dB / 71.89° — matching the deck's own in-deck ``.meas`` scalars. This test pins the
difference, not the ratio.

Offline: a synthetic ``SimResult`` stands in for a run, so no SPICE/PDK is needed.
"""
from __future__ import annotations

import math
import shutil

import numpy as np
import pytest
from spicexplorer.backends.analog_db import (
    CircuitRun,
    EngineCapability,
    MetricTarget,
    _DifferentialSimResult,
    analog_db_root,
)

_FD_CIRCUIT = "amp_023_fer_fd2s"
_PDK = "ihp-sg13g2"

# The synthetic differential transfer the stub result carries: a single-pole 60 dB / 10 kHz amp,
# so UGF = A0·fp = 10 MHz and the phase margin of the one pole is 90°.
_A0, _FP = 1000.0, 1.0e4


def _have_fd_circuit() -> bool:
    try:
        return (analog_db_root() / "circuits" / _FD_CIRCUIT / "circuit.yaml").is_file()
    except Exception:
        return False


_needs_db = pytest.mark.skipif(
    not _have_fd_circuit(),
    reason=f"analog-db {_FD_CIRCUIT} not checked out (set SPICEXPLORER_ANALOG_DB)",
)


class _StubResult:
    """A minimal ngspice-shaped ``SimResult``: named traces only, and an ``IndexError`` for any
    other name — exactly how spicelib's ``PlotData.get_wave`` reports an absent trace."""

    def __init__(self, traces: dict[str, np.ndarray]) -> None:
        self._traces = traces

    def wave(self, name: str, analysis: str, is_real: bool = False) -> np.ndarray:
        if name not in self._traces:
            raise IndexError(f'PlotData object doesn\'t contain trace "{name}"')
        return self._traces[name]

    def scalar(self, name: str, analysis: str, is_real: bool = True) -> float:
        wave = self._traces.get(name)
        return float(np.real(wave[0])) if wave is not None else float("nan")


def _fd_ac_result() -> _StubResult:
    """An AC sweep in which ONLY the differential pair exists (no single-ended ``v(vout)``).
    Each leg carries half the differential transfer with opposite sign, so ``voutp - voutn``
    is the true response and ``voutp / voutn`` is a flat -1."""
    freq = np.logspace(0, 9, 400)
    h = _A0 / (1.0 + 1j * freq / _FP)
    return _StubResult({"frequency": freq, "v(voutp)": h / 2.0, "v(voutn)": -h / 2.0})


def _ac_metrics(out: str) -> list[MetricTarget]:
    return [
        MetricTarget("dc_gain_db", {"meas": "dcgain", "out": out}, "ac", spec_min=50.0,
                     analysis_id="ac_open_loop"),
        MetricTarget("ugf_hz", {"meas": "ugf", "out": out}, "ac", spec_min=5.0e6,
                     analysis_id="ac_open_loop"),
    ]


# --------------------------------------------------------- run_circuit resolves the FD pair
@_needs_db
def test_run_circuit_resolves_the_differential_pair_not_vout(monkeypatch):
    """The registry route must bind the DUT's own output pair, and measure their DIFFERENCE.

    BEFORE: ``run.metrics`` all carried ``out='vout'`` and ``evaluate()`` raised
    ``IndexError: ... "v(vout)"`` on the first metric — the circuit was unusable end-to-end."""
    import spicexplorer.backends.analog_db as adb

    monkeypatch.setattr(
        adb, "probe_engine",
        lambda circuit, pdk, **kw: EngineCapability(circuit, pdk, "ngspice", True, "stub"),
    )
    monkeypatch.setattr(adb, "build_ngspice_run", lambda *a, **kw: _fd_ac_result())

    run = adb.run_circuit(_FD_CIRCUIT, _PDK, testbench="ac_open_loop")

    # the reported defect: this raised IndexError: PlotData object doesn't contain trace "v(vout)"
    evals = run.evaluate()
    assert {"dc_gain_db", "ugf_hz", "pm_deg"} <= set(evals)
    assert run.differential == ("voutp", "voutn")
    assert run.default_out() == "voutp"
    assert {str(m.recipe["out"]) for m in run.metrics} == {"voutp"}  # was {"vout"}
    # the DIFFERENCE: 60 dB / 10 MHz. The ratio voutp/voutn would read 0 dB (and PM 180°).
    assert evals["dc_gain_db"].value == pytest.approx(20 * math.log10(_A0), abs=1e-6)
    assert evals["ugf_hz"].value == pytest.approx(_A0 * _FP, rel=1e-3)
    assert evals["pm_deg"].value == pytest.approx(90.0, abs=1.0)


def test_differential_read_is_the_difference_not_the_ratio():
    """Directly on the CircuitRun seam: the `ref`-divide the AC registry path implements would
    give 0 dB for a balanced pair. Pin the difference."""
    run = CircuitRun(_FD_CIRCUIT, _PDK, "ngspice", "ac_open_loop", "tt", _fd_ac_result(),
                     _ac_metrics("voutp"), differential=("voutp", "voutn"))
    evals = run.evaluate()
    assert evals["dc_gain_db"].value == pytest.approx(20 * math.log10(_A0), abs=1e-6)
    assert evals["dc_gain_db"].satisfied
    assert evals["ugf_hz"].value == pytest.approx(_A0 * _FP, rel=1e-3)

    # a single-ended run over the SAME traces is untouched by the differential view
    single = CircuitRun(_FD_CIRCUIT, _PDK, "ngspice", "ac_open_loop", "tt",
                        _StubResult({"frequency": np.logspace(0, 9, 400),
                                     "v(vout)": _A0 / (1.0 + 1j * np.logspace(0, 9, 400) / _FP)}),
                        _ac_metrics("vout"))
    assert single.default_out() == "vout"
    assert single.evaluate()["dc_gain_db"].value == pytest.approx(20 * math.log10(_A0), abs=1e-6)


# ------------------------------------------------------- per-metric isolation (no FD needed)
def test_one_broken_metric_degrades_to_nan_and_spares_the_others():
    """BEFORE: the unknown ``meas`` raised out of ``evaluate()`` and NO metric was reported."""
    metrics = [
        MetricTarget("dc_gain_db", {"meas": "dcgain", "out": "vout"}, "ac", spec_min=50.0,
                     analysis_id="ac_open_loop"),
        MetricTarget("bogus", {"meas": "not_a_measurement", "out": "vout"}, "ac",
                     spec_max=1.0, analysis_id="ac_open_loop"),
        MetricTarget("absent_trace", {"meas": "dcgain", "out": "vmissing"}, "ac",
                     spec_min=0.0, analysis_id="ac_open_loop"),
    ]
    freq = np.logspace(0, 9, 400)
    result = _StubResult({"frequency": freq, "v(vout)": _A0 / (1.0 + 1j * freq / _FP)})
    run = CircuitRun("stub_amp", _PDK, "ngspice", "ac_open_loop", "tt", result, metrics)

    evals = run.evaluate()
    assert set(evals) == {"dc_gain_db", "bogus", "absent_trace"}
    assert evals["dc_gain_db"].value == pytest.approx(20 * math.log10(_A0), abs=1e-6)
    assert evals["dc_gain_db"].satisfied
    for broken in ("bogus", "absent_trace"):
        assert math.isnan(evals[broken].value)
        assert not evals[broken].satisfied  # NaN never passes a spec band


# ----------------------------------------------------------------- LIVE (open ngspice lane)
@pytest.mark.slow
@_needs_db
@pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice not on PATH")
def test_fd_registry_metrics_match_the_decks_own_meas_live(tmp_path):
    """End-to-end on the open lane: the registry's differential read must reproduce the deck's
    OWN in-deck ``.meas`` scalars (which ngspice computes on ``let vodm = v(voutp) - v(voutn)``).

    This is the oracle that distinguishes the two candidate fixes: the ``ref``-divide would read
    dcgain ≈ -4.5e-13 dB / PM = 180°, the difference reads the deck's 65.93 dB / 71.89°."""
    import spicexplorer.backends.analog_db as adb

    cap = adb.probe_engine(_FD_CIRCUIT, _PDK)
    if not cap.available:
        pytest.skip(f"open lane unavailable: {cap.reason}")

    run = adb.run_circuit(_FD_CIRCUIT, _PDK, testbench="ac_open_loop", output_dir=tmp_path)
    assert run.differential == ("voutp", "voutn")
    evals = run.evaluate()

    for metric, deck_meas in (("dc_gain_db", "dcgain"), ("ugf_hz", "ugf"), ("pm_deg", "pm")):
        expected = run.result.scalar(deck_meas, "ac")
        assert evals[metric].value == pytest.approx(expected, rel=1e-4), metric
    assert evals["dc_gain_db"].value > 60.0  # the ref-divide read would be ~0 dB
    assert evals["pm_deg"].value < 100.0     # the ref-divide read would be 180°


# ------------------------------------------------------- scalar delegation (protocol contract)
def test_differential_view_delegates_scalars_on_the_protocol_signature():
    """The FD wrapper substitutes the differential WAVE; scalars must pass straight through.

    It used to forward a third ``is_real`` argument. ngspice's result accepts one, so the
    open PDKs never noticed — but the SimResult PROTOCOL declares ``scalar(name, analysis)``
    and Spectre implements exactly that, so on the licensed lane every scalar read of a
    fully-differential cell raised TypeError and was recorded as NaN: i_supply (hence
    power), vos and t_settle went missing on 8 Spectre-routed amplifiers while the AC metrics
    beside them looked healthy.
    """

    class _ProtocolOnlyResult:
        """Implements the protocol EXACTLY — two positional arguments, like Spectre's."""

        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def scalar(self, name: str, analysis: str) -> float:
            self.calls.append((name, analysis))
            return -9.53e-05

        def wave(self, name: str, analysis: str, is_real: bool = False) -> np.ndarray:
            return np.zeros(4)

    inner = _ProtocolOnlyResult()
    view = _DifferentialSimResult(inner, "voutp", "voutn")

    assert view.scalar("VDD:p", "op") == pytest.approx(-9.53e-05)
    assert inner.calls == [("VDD:p", "op")]


# ------------------------------------------------- noise input probe follows the deck variant
@pytest.mark.parametrize(
    ("template", "expected"),
    [
        ("noise", "VINP"),
        ("noise_diff", "VINP"),
        ("noise_biaswrap", "VAC"),
        ("noise_biaswrap_ibias", "VAC"),
        (None, "VINP"),
    ],
)
def test_noise_iprobe_follows_the_testbench_template(template, expected):
    """`iprobe` names a source INSTANCE, so it must track the template variant.

    The closed-lane deck is a translation of the ngspice testbench, and the self-biased
    (biaswrap) variants drive through `VAC` on `sigin` — they contain no `VINP` at all. The
    class bench hardcoded `IPROBE: VINP`, so on those cells Spectre referred the noise to an
    instance that did not exist: it produced no input-referred density and `inoise_total` came
    back NaN, while the analysis still reported status ok. That silent shape hid a missing
    noise measurement on 16 Spectre-routed amplifiers until someone read the published table.
    """
    from spicexplorer.backends.analog_db import _spectre_context

    ctx = _spectre_context("noise", {"FSTART": 1, "FSTOP": "1MEG"}, template=template)
    assert ctx["NOISE_IPROBE"] == expected
