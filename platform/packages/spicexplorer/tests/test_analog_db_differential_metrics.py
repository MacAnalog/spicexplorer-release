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
from spicexplorer_core.measurements import waveforms as wf

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


def _crossing_rel_tolerance(freq: np.ndarray) -> float:
    """How far apart the registry's log-f read and ngspice's linear-f ``meas … WHEN`` read of the
    SAME crossing can be on the ``ac dec`` grid ``freq``, relative (see the live test below).

    Both place the crossing at the same fraction t of one grid cell [f0, r·f0]: the registry at
    f0·r^t, ngspice at f0·(1 + t(r - 1)). The bound is the supremum over t of the ratio minus 1,
    plus 1e-6 for the 7 significant digits the deck's ``.meas`` scalar is stored with.
    """
    cell_ratio = freq[1:] / freq[:-1]
    assert np.allclose(cell_ratio, cell_ratio[0], rtol=1e-6), "expected a log (`ac dec`) grid"
    r = float(cell_ratio[0])
    # sup over t of (1 + t(r - 1))/r^t - 1, attained where the derivative of its log vanishes
    t_star = ((r - 1.0) / math.log(r) - 1.0) / (r - 1.0)
    return math.expm1(math.log((r - 1.0) / math.log(r)) - t_star * math.log(r)) + 1e-6


def _dec_grid(points_per_decade: int, decades: int = 9) -> np.ndarray:
    """An ngspice ``ac dec N 1 10^decades`` frequency axis: N points per decade, ends included."""
    return np.logspace(0.0, float(decades), points_per_decade * decades + 1)


def _ac_metrics(out: str) -> list[MetricTarget]:
    return [
        MetricTarget(
            "dc_gain_db",
            {"meas": "dcgain", "out": out},
            "ac",
            spec_min=50.0,
            analysis_id="ac_open_loop",
        ),
        MetricTarget(
            "ugf_hz", {"meas": "ugf", "out": out}, "ac", spec_min=5.0e6, analysis_id="ac_open_loop"
        ),
    ]


# --------------------------------------------------------- run_circuit resolves the FD pair
@_needs_db
def test_run_circuit_resolves_the_differential_pair_not_vout(monkeypatch):
    """The registry route must bind the DUT's own output pair, and measure their DIFFERENCE.

    BEFORE: ``run.metrics`` all carried ``out='vout'`` and ``evaluate()`` raised
    ``IndexError: ... "v(vout)"`` on the first metric — the circuit was unusable end-to-end."""
    import spicexplorer.backends.analog_db as adb

    monkeypatch.setattr(
        adb,
        "probe_engine",
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
    run = CircuitRun(
        _FD_CIRCUIT,
        _PDK,
        "ngspice",
        "ac_open_loop",
        "tt",
        _fd_ac_result(),
        _ac_metrics("voutp"),
        differential=("voutp", "voutn"),
    )
    evals = run.evaluate()
    assert evals["dc_gain_db"].value == pytest.approx(20 * math.log10(_A0), abs=1e-6)
    assert evals["dc_gain_db"].satisfied
    assert evals["ugf_hz"].value == pytest.approx(_A0 * _FP, rel=1e-3)

    # a single-ended run over the SAME traces is untouched by the differential view
    single = CircuitRun(
        _FD_CIRCUIT,
        _PDK,
        "ngspice",
        "ac_open_loop",
        "tt",
        _StubResult(
            {
                "frequency": np.logspace(0, 9, 400),
                "v(vout)": _A0 / (1.0 + 1j * np.logspace(0, 9, 400) / _FP),
            }
        ),
        _ac_metrics("vout"),
    )
    assert single.default_out() == "vout"
    assert single.evaluate()["dc_gain_db"].value == pytest.approx(20 * math.log10(_A0), abs=1e-6)


# ------------------------------------------------------- per-metric isolation (no FD needed)
def test_one_broken_metric_degrades_to_nan_and_spares_the_others():
    """BEFORE: the unknown ``meas`` raised out of ``evaluate()`` and NO metric was reported."""
    metrics = [
        MetricTarget(
            "dc_gain_db",
            {"meas": "dcgain", "out": "vout"},
            "ac",
            spec_min=50.0,
            analysis_id="ac_open_loop",
        ),
        MetricTarget(
            "bogus",
            {"meas": "not_a_measurement", "out": "vout"},
            "ac",
            spec_max=1.0,
            analysis_id="ac_open_loop",
        ),
        MetricTarget(
            "absent_trace",
            {"meas": "dcgain", "out": "vmissing"},
            "ac",
            spec_min=0.0,
            analysis_id="ac_open_loop",
        ),
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

    # How close "the same number" can be depends on the metric, because the registry and the
    # deck interpolate BETWEEN sweep points on different axes:
    #
    # * dc_gain_db is read AT a grid point (FSTART) — no interpolation, so 1e-4 is exact.
    # * ugf_hz is a CROSSING. Both reads bracket the 0 dB crossing in the same grid cell
    #   [f0, f1 = r·f0] and place it at the same fraction t = d0/(d0 - d1) of the dB drop, but
    #   the registry takes that fraction along log10(f) (waveforms._log_interp_crossing — the
    #   natural Bode axis) while ngspice's `meas … WHEN` takes it along linear f. The two
    #   answers are f0·r^t and f0·(1 + t(r - 1)); they differ by ≈ (ln r)²·t(1 - t)/2, at most
    #   ≈ (ln r)²/8 near mid-cell (the exact supremum over t is computed below, plus the 7
    #   significant digits the deck's `.meas` scalar is stored with). That is grid
    #   quantisation, not a definition mismatch: measured 2026-09-25 on this circuit
    #   (ihp-sg13g2, `ac dec 50`, r = 10^(1/50)), the cell was 25.119..26.303 MHz with t = 0.11,
    #   the registry read 25 246 617 Hz, the deck 25 249 270 Hz (rel 1.05e-4; the formula
    #   predicts 1.04e-4), and a 20 001-point linear sweep of that cell put the true crossing at
    #   25 247 130 Hz — the log-f read is the CLOSER of the two (2.0e-5 vs 8.5e-5). A flat
    #   rel=1e-4 therefore failed whenever t drifted towards mid-cell; the bound below is
    #   derived from the grid the deck actually swept, so it cannot hide a wrong read (the
    #   ratio-vs-difference defect this test guards is off by orders of magnitude).
    # * pm_deg is axis-INDEPENDENT: each side reads the phase at the same fraction t of the same
    #   cell on the same axis it used for the crossing (phase linear in f at the linear-f
    #   crossing, linear in log f at the log-f crossing), so both give φ0 + t·Δφ. It keeps the
    #   tight tolerance — and matched to 7 digits in the run above.
    freq = np.real(np.asarray(run.result.wave("frequency", "ac"), dtype=complex))
    crossing_rel = _crossing_rel_tolerance(freq)  # checked offline by the tests below
    tolerance = {"dc_gain_db": 1e-4, "ugf_hz": crossing_rel, "pm_deg": 1e-4}

    for metric, deck_meas in (("dc_gain_db", "dcgain"), ("ugf_hz", "ugf"), ("pm_deg", "pm")):
        expected = run.result.scalar(deck_meas, "ac")
        assert evals[metric].value == pytest.approx(expected, rel=tolerance[metric]), metric
    assert evals["dc_gain_db"].value > 60.0  # the ref-divide read would be ~0 dB
    assert evals["pm_deg"].value < 100.0  # the ref-divide read would be 180°


# ----------------------------------- the live test's ugf_hz tolerance, checked offline (no SPICE)
# The live comparison above is only as good as its premise (the registry reads a crossing along
# log f, ngspice along linear f) and its bound (the exact grid-cell gap between those two reads).
# A registry that silently switched axes would still pass it; a bound that drifted loose would
# hide a wrong read. The tests below check both without a simulator.
_DEC50 = 10.0 ** (1.0 / 50.0)  # the cell ratio of amp_023's `ac dec 50` sweep


def _linear_f_read(f0: float, r: float, t: float) -> float:
    """ngspice's ``meas … WHEN``: the crossing at fraction ``t`` of the cell [f0, r·f0], along
    LINEAR frequency."""
    return f0 * (1.0 + t * (r - 1.0))


@pytest.mark.parametrize("t", [0.11, 0.5, 0.9])
def test_registry_ugf_is_the_log_f_read_of_the_crossing_cell(t):
    """One grid cell whose dB drop puts 0 dB at fraction ``t``: the registry's UGF is f0·r^t
    exactly (the log-f read), not the linear-f read ngspice's ``.meas`` would give."""
    f0 = 10.0**7.4  # amp_023's crossing cell, 25.119..26.303 MHz
    freq = np.array([f0, f0 * _DEC50])
    h = 10.0 ** (np.array([2.0 * t, -2.0 * (1.0 - t)]) / 20.0)  # +2t dB → −2(1−t) dB
    ugf = wf.unity_gain_freq(freq, h)
    assert ugf == pytest.approx(f0 * _DEC50**t, rel=1e-12)
    assert _linear_f_read(f0, _DEC50, t) / ugf - 1.0 <= _crossing_rel_tolerance(freq)


def test_registry_ugf_of_an_integrator_is_exact_where_the_linear_read_is_not():
    """Through the route the live test compares (CircuitRun → registry ``ugf`` on the differential
    view): a −20 dB/dec integrator's dB is linear in log f, so the registry's read is exact on
    the deck's own grid, while the linear-f read of that cell misses by more than the old flat
    1e-4 — and by no more than the grid bound."""
    freq = _dec_grid(50)
    k = 370  # 7.4 decades × 50/dec: the cell starting at 10^7.4 Hz ≈ 25.1 MHz
    t = 0.5  # mid-cell, where the two reads are furthest apart
    fu = float(freq[k]) * _DEC50**t
    h = fu / (1j * freq)
    run = CircuitRun(
        _FD_CIRCUIT,
        _PDK,
        "ngspice",
        "ac_open_loop",
        "tt",
        _StubResult({"frequency": freq, "v(voutp)": h / 2.0, "v(voutn)": -h / 2.0}),
        _ac_metrics("voutp"),
        differential=("voutp", "voutn"),
    )
    ugf = run.evaluate()["ugf_hz"].value
    assert ugf == pytest.approx(fu, rel=1e-9)
    gap = _linear_f_read(float(freq[k]), _DEC50, t) / ugf - 1.0
    assert 1.0e-4 < gap <= _crossing_rel_tolerance(freq)


def test_registry_phase_margin_reads_the_phase_at_the_same_cell_fraction():
    """Why pm_deg keeps the tight 1e-4: the registry reads the phase at its log-f crossing by
    interpolating in log f too, so it lands on φ0 + t·Δφ — the value ngspice reaches along
    linear f. A one-decade cell makes any axis mix-up large (linear-f phase at the log-f
    crossing of t = 0.5 would sit at 24 % of the cell, not 50 %)."""
    freq = np.array([1.0, 1.0e3, 1.0e4])
    mag_db = np.array([40.0, 1.0, -1.0])  # 0 dB at t = 0.5 of [1 k, 10 k]
    phase = np.radians([-5.0, -100.0, -140.0])
    h = 10.0 ** (mag_db / 20.0) * np.exp(1j * phase)
    t = 0.5
    assert wf.unity_gain_freq(freq, h) == pytest.approx(1.0e3 * 10.0**t, rel=1e-12)
    assert wf.phase_margin(freq, h) == pytest.approx(180.0 + 5.0 + (-100.0 + t * -40.0), abs=1e-9)


@pytest.mark.parametrize("n", [10, 20, 50, 100])
def test_crossing_tolerance_is_the_tight_supremum_of_the_two_reads(n):
    """The bound is the exact max over t of the linear-f/log-f gap on an ``ac dec n`` grid (plus
    the 1e-6 storage allowance): conservative, but not loose enough to hide a wrong read."""
    freq = _dec_grid(n)
    r = 10.0 ** (1.0 / n)
    bound = _crossing_rel_tolerance(freq)
    t = np.linspace(0.0, 1.0, 200_001)
    gap = (1.0 + t * (r - 1.0)) / r**t - 1.0
    assert gap.min() >= 0.0  # the chord (linear f) never falls below the log-f read
    assert gap.max() <= bound  # conservative …
    assert bound - 1.0e-6 == pytest.approx(gap.max(), rel=1e-9)  # … and tight
    assert bound - 1.0e-6 == pytest.approx(math.log(r) ** 2 / 8.0, rel=5e-3)  # the (ln r)²/8


def test_crossing_tolerance_reproduces_the_measured_amp_023_pair():
    """The live failure, by its numbers (2026-09-25, ihp-sg13g2, ``ac dec 50``): the registry
    read 25 246 616.73 Hz, the deck's ``.meas`` 25 249 270 Hz. Placing the registry value in its
    cell recovers t ≈ 0.11, from which the linear-f read predicts the deck's value to its 7
    stored digits; the gap (1.05e-4) is over the old flat 1e-4 and inside the dec-50 bound."""
    freq = _dec_grid(50)
    registry, deck = 25_246_616.732029554, 25_249_270.0
    f0 = 10.0**7.4
    t = math.log(registry / f0) / math.log(_DEC50)
    assert t == pytest.approx(0.11, abs=0.005)
    assert _linear_f_read(f0, _DEC50, t) == pytest.approx(deck, rel=1e-6)
    bound = _crossing_rel_tolerance(freq)
    assert bound == pytest.approx(2.66e-4, rel=5e-3)
    assert 1.0e-4 < deck / registry - 1.0 <= bound


def test_crossing_tolerance_refuses_a_grid_that_is_not_ac_dec():
    """The bound is derived for a constant cell RATIO; an ``ac lin`` sweep has none."""
    with pytest.raises(AssertionError, match="log"):
        _crossing_rel_tolerance(np.linspace(1.0e3, 1.0e9, 601))


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
