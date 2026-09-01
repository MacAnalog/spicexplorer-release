"""Per-trial wall-time telemetry and the optional cost guard (ledger E-049).

An optimizer's per-trial cost is not constant. In a TCAS-2026 campaign run the Ax/BoTorch
per-trial wall time grew **27 s -> 117 s -> 200-292 s** as the GP refit cost climbed with the
observation count — the SPICE cost per trial never moved. `bo_nevergrad` shows the same late-run
growth. Nothing in the loop said so, so the runs were noticed only by watching the progress bar and
had to be killed by hand.

`optimization.trial_timing.TrialTimeMonitor` is the measurement half: a pure accumulator fed one
duration per trial, so this suite drives it with lists of numbers rather than a clock. The loop
wiring is exercised separately against a fake clock, which is the only place a clock appears.

Organised around what makes a telemetry feature worthless:

1. **Wrong statistics.** A rolling median that is not a rolling median, or a baseline built from
   too few trials, produces confident nonsense.
2. **A threshold that fires at the wrong time** — before it is crossed (cries wolf), or once per
   trial forever (drowns the log nobody then reads).
3. **A default that is not free.** The whole feature is opt-in; a project that configures nothing
   must score identically, log no warnings and run its full budget.

No SPICE, no PDK.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import pytest
from _spicexplorer_fixtures import REPO_ROOT
from spicexplorer.core.domains import (
    OptimizationLogEntry,
    OptimizationPoint,
    OptimizerConfig,
    Project_Setup,
)
from spicexplorer.optimization.base import Base_Optimizer
from spicexplorer.optimization.trial_timing import (
    DEFAULT_TRIAL_TIME_REPORT_EVERY,
    TrialTimeMonitor,
)

CASCODE_YAML = REPO_ROOT / "examples" / "OTA" / "cascode" / "ihp-sg13g2" / "sizing" / "project_setup.yaml"


def _monitor(**kw) -> TrialTimeMonitor:
    """A monitor with SMALL windows so a test reads as a handful of durations, not fifty."""
    kw.setdefault("window", 4)
    kw.setdefault("baseline_trials", 4)
    kw.setdefault("report_every", 0)          # silence the cadence unless a test asks for it
    return TrialTimeMonitor(**kw)


def _feed(monitor: TrialTimeMonitor, durations) -> List[Any]:
    return [monitor.record(d) for d in durations]


# =========================================================== 1. the statistics
def test_rolling_median_over_a_partial_window():
    m = _monitor()
    assert m.rolling_median_s is None                      # nothing recorded yet
    assert [v.rolling_median_s for v in _feed(m, [10.0, 20.0, 60.0])] == [10.0, 15.0, 20.0]


def test_the_window_evicts_old_trials():
    """The point of a ROLLING median: an early cheap phase must stop propping the number up."""
    m = _monitor(window=4)
    _feed(m, [1.0, 1.0, 1.0, 1.0])
    assert m.rolling_median_s == 1.0
    _feed(m, [9.0, 9.0, 9.0, 9.0])
    assert m.rolling_median_s == 9.0


def test_one_slow_trial_cannot_move_the_median():
    """Robustness is the reason it is a median and not a mean — a retried sim or a loaded host
    produces exactly one outlier, and that must not read as the refit wall."""
    m = _monitor(window=4)
    verdicts = _feed(m, [2.0, 2.0, 900.0, 2.0])
    assert verdicts[-1].rolling_median_s == 2.0


def test_the_baseline_is_withheld_until_enough_trials_exist():
    """Dividing by a one-trial baseline would make `warn_factor` fire on jitter."""
    m = _monitor(baseline_trials=4)
    got = [v.baseline_median_s for v in _feed(m, [4.0, 6.0, 8.0, 10.0, 500.0])]
    assert got == [None, None, None, 7.0, 7.0]


def test_the_baseline_is_frozen_at_the_start_of_the_run():
    """It is the run's OWN early cost; later trials must not be able to redefine it upward and
    hide the very growth it exists to measure."""
    m = _monitor(baseline_trials=3)
    _feed(m, [1.0, 1.0, 1.0] + [300.0] * 20)
    assert m.baseline_median_s == 1.0


def test_growth_factor_is_the_ratio_and_is_none_without_a_baseline():
    m = _monitor(baseline_trials=2, window=2)
    first = m.record(4.0)
    assert first.growth_factor is None
    m.record(4.0)
    assert _feed(m, [16.0, 16.0])[-1].growth_factor == pytest.approx(4.0)


def test_totals_and_counts_track_every_trial():
    m = _monitor()
    _feed(m, [1.5, 2.5, 6.0])
    assert (m.n, m.total_s) == (3, 10.0)


def test_a_backwards_clock_is_clamped_rather_than_poisoning_the_median():
    m = _monitor()
    assert m.record(-5.0).elapsed_s == 0.0
    assert m.rolling_median_s == 0.0


# =========================================================== 2. the thresholds
def test_the_absolute_warning_fires_on_the_crossing_and_not_before():
    m = _monitor(warn_s=10.0, window=1)
    verdicts = _feed(m, [9.0, 9.9, 10.0, 10.1])
    assert [v.warning is not None for v in verdicts] == [False, False, False, True]
    assert "trial_time_warn_s" in verdicts[-1].warning


def test_the_absolute_warning_latches_and_re_arms_on_recovery():
    """One WARNING per crossing. A run that is simply slow must not emit one per trial — and a
    run that recovers and degrades again must say so a second time."""
    m = _monitor(warn_s=10.0, window=1)
    fired = [v.warning is not None for v in _feed(m, [50.0, 50.0, 50.0, 1.0, 1.0, 50.0])]
    assert fired == [True, False, False, False, False, True]


def test_the_relative_warning_measures_growth_against_the_runs_own_baseline():
    """The E-049 signature: the absolute number is unremarkable, the GROWTH is the finding."""
    m = _monitor(warn_factor=3.0, baseline_trials=4, window=2)
    verdicts = _feed(m, [10.0, 10.0, 10.0, 10.0,   # baseline = 10 s
                         20.0, 20.0,               # rolling 20 s -> 2.0x, under the factor
                         40.0,                     # rolling median of [20, 40] = 30 -> 3.0x, NOT >
                         40.0])                    # rolling 40 s -> 4.0x, over it
    assert [v.warning is not None for v in verdicts] == [False] * 7 + [True]
    assert "4.0x" in verdicts[-1].warning


def test_the_relative_warning_stays_silent_until_the_baseline_exists():
    """Before `baseline_trials` there is nothing to grow FROM; a warning then would be arbitrary."""
    m = _monitor(warn_factor=1.5, baseline_trials=6)
    assert all(v.warning is None for v in _feed(m, [1.0, 1.0, 500.0, 500.0, 500.0]))


def test_both_warnings_can_be_configured_together():
    m = _monitor(warn_s=100.0, warn_factor=2.0, baseline_trials=2, window=1)
    verdicts = _feed(m, [10.0, 10.0, 30.0, 500.0])
    assert verdicts[2].warning is not None and "warn_factor" in verdicts[2].warning
    assert verdicts[3].warning is not None and "warn_s" in verdicts[3].warning


# =========================================================== 3. the hard stop
def test_the_stop_fires_once_on_the_crossing():
    m = _monitor(stop_s=100.0, window=1)
    stops = [v.stop for v in _feed(m, [50.0, 150.0, 200.0])]
    assert stops == [False, True, False]           # the loop breaks on the True; sticky after
    assert m.stopped is True


def test_the_stop_follows_the_rolling_median_not_a_single_trial():
    """One 900 s trial is a hiccup; a sustained 900 s/trial is the wall. Killing a run on the
    former would be worse than the problem."""
    m = _monitor(stop_s=100.0, window=4)
    assert not any(v.stop for v in _feed(m, [2.0, 2.0, 900.0, 2.0]))
    assert any(v.stop for v in _feed(m, [900.0, 900.0, 900.0]))


# =========================================================== 4. the default is free
def test_a_monitor_with_no_thresholds_never_warns_and_never_stops():
    m = _monitor()
    verdicts = _feed(m, [1.0, 5.0, 50.0, 5000.0, 500000.0])
    assert all(v.warning is None and not v.stop for v in verdicts)
    assert m.stopped is False


def test_the_cadence_line_appears_only_on_its_tick_and_can_be_silenced():
    m = _monitor(report_every=3)
    assert [v.report is not None for v in _feed(m, [1.0] * 7)] == [
        False, False, True, False, False, True, False]
    assert all(v.report is None for v in _feed(_monitor(report_every=0), [1.0] * 10))


def test_the_cadence_line_states_the_rolling_median_and_the_growth():
    m = _monitor(report_every=4, baseline_trials=2, window=4)
    report = _feed(m, [10.0, 10.0, 40.0, 40.0])[-1].report
    assert "rolling median" in report and "25.0 s/trial" in report and "2.5x" in report


# =========================================================== 5. config plumbing
def _config(**kw) -> OptimizerConfig:
    from types import SimpleNamespace
    base = dict(name="NGOpt", type="nevergrad", budget=10, optimizer_kwargs=None,
                target_specs=SimpleNamespace(targets=[]), lin_variable_bounds=None,
                log_variable_bounds=None, loss_function_config=None, random_seed=None)
    base.update(kw)
    return OptimizerConfig(**base)


def test_the_guards_default_to_off():
    cfg = _config()
    assert cfg.trial_time_warn_s is None
    assert cfg.trial_time_warn_factor is None
    assert cfg.trial_time_stop_s is None
    assert cfg.trial_time_report_every == DEFAULT_TRIAL_TIME_REPORT_EVERY


@pytest.mark.parametrize("key", ("trial_time_warn_s", "trial_time_warn_factor",
                                 "trial_time_stop_s"))
@pytest.mark.parametrize("bad", (0, -1.0, float("nan"), float("inf")))
def test_a_degenerate_threshold_is_rejected_at_load(key, bad):
    """A closed, validated vocabulary like every other knob here: a typo must fail at load, not
    silently disable the guard that a long run was relying on."""
    with pytest.raises(ValueError, match=key):
        _config(**{key: bad})


def test_a_negative_report_cadence_is_rejected_but_zero_silences():
    with pytest.raises(ValueError, match="trial_time_report_every"):
        _config(trial_time_report_every=-1)
    assert _config(trial_time_report_every=0).trial_time_report_every == 0


# =========================================================== 6. wiring into the loop
#: Only the wiring tests below need the example project on disk — the ~32 `TrialTimeMonitor`
#: tests above are pure. A module-level `pytestmark` would skip those too, and a suite that
#: silently skips is worse than one that fails, so the mark is bound to a name and applied
#: per test.
requires_cascode = pytest.mark.skipif(not CASCODE_YAML.exists(),
                                      reason="cascode example project missing")


class _FakeClock:
    """A clock the TRIAL advances, so a test states per-trial durations directly."""

    def __init__(self, durations):
        self.now = 1000.0
        self._durations = list(durations)
        self.trials = 0

    def __call__(self) -> float:
        return self.now

    def spend_one_trial(self) -> None:
        self.now += self._durations[min(self.trials, len(self._durations) - 1)]
        self.trials += 1


class _TimedOpt(Base_Optimizer):
    """Base_Optimizer whose one step costs whatever the injected clock says it costs."""

    clock: _FakeClock

    def _create_optimizer_obj(self) -> bool:
        self.optimizer = object()
        return True

    def parameterize(self) -> Any:
        return {}

    def evaluate(self, parameterization) -> Tuple[np.floating, Dict[str, Any]]:
        return np.float64(0.0), {}

    def compute_fitness(self, performance_array):
        return np.float64(0.0), {}

    def optimization_step(self):
        self.clock.spend_one_trial()
        score = np.float64(float(self.clock.trials))
        self.optimization_log.log.append(
            OptimizationLogEntry(point=OptimizationPoint(params={}, score=score), fit_summary={}))
        return {}, score, {}

    def plot_solution(self, parameterization, **kwargs):
        return None

    def save_checkpoint(self, name=None):        # no file IO in these tests
        return None


def _run(tmp_path, monkeypatch, durations, budget, **cfg) -> _TimedOpt:
    import spicexplorer.optimization.base as base_mod

    proj = Project_Setup.from_yaml(CASCODE_YAML)
    opt = _TimedOpt(proj, output_root=tmp_path / "ck")
    opt.clock = _FakeClock(durations)
    opt.optimizer_config.budget = budget
    for key, value in cfg.items():
        setattr(opt.optimizer_config, key, value)
    monkeypatch.setattr(base_mod, "monotonic", opt.clock)
    opt.optimize()
    return opt


@requires_cascode
def test_the_loop_measures_each_trial(tmp_path, monkeypatch):
    opt = _run(tmp_path, monkeypatch, [3.0, 3.0, 9.0, 9.0], budget=4,
               trial_time_report_every=0)
    monitor = opt.trial_time_monitor
    assert monitor is not None and monitor.n == 4
    assert monitor.total_s == pytest.approx(24.0)
    assert monitor.rolling_median_s == pytest.approx(6.0)


@requires_cascode
def test_the_default_run_is_unchanged_and_silent(tmp_path, monkeypatch, caplog):
    """The feature is opt-in: with nothing configured a run must still complete its whole budget,
    log no WARNING, and record no stop reason."""
    with caplog.at_level("WARNING", logger="spicexplorer.optimization.base"):
        opt = _run(tmp_path, monkeypatch, [1.0, 1.0, 1.0, 5000.0, 5000.0, 5000.0], budget=6,
                   trial_time_report_every=0)
    assert opt.clock.trials == 6                      # full budget, nothing cut short
    assert opt.stop_reason is None
    assert opt.trial_time_monitor is not None and not opt.trial_time_monitor.stopped
    # Only this loop's own records — loading the example project warns about its own config.
    assert [r.message for r in caplog.records
            if r.name == "spicexplorer.optimization.base"] == []


@requires_cascode
def test_the_loop_warns_when_the_threshold_is_crossed_and_not_before(tmp_path, monkeypatch, caplog):
    with caplog.at_level("WARNING", logger="spicexplorer.optimization.base"):
        opt = _run(tmp_path, monkeypatch, [1.0] * 5 + [400.0] * 5, budget=10,
                   trial_time_warn_s=100.0, trial_time_report_every=0)
    warnings = [r.message for r in caplog.records if "per-trial wall time" in r.message]
    assert len(warnings) == 1, warnings                # latched: one WARNING, not one per trial
    assert opt.clock.trials == 10                      # warn-only: the budget still runs out


@requires_cascode
def test_the_loop_reports_the_rolling_cost_at_the_configured_cadence(tmp_path, monkeypatch, caplog):
    with caplog.at_level("INFO", logger="spicexplorer.optimization.base"):
        _run(tmp_path, monkeypatch, [2.0] * 9, budget=9, trial_time_report_every=3)
    ticks = [r.message for r in caplog.records if "rolling median" in r.message]
    assert len(ticks) == 3
    assert "2.0 s/trial" in ticks[-1]


@requires_cascode
def test_the_guard_stops_the_run_gracefully(tmp_path, monkeypatch, caplog):
    """A guard stop is a STOP, not a crash: `optimize()` returns normally, the reason is on the
    instance, and the best-so-far is still reportable — which a hand-killed run cannot give you."""
    with caplog.at_level("WARNING", logger="spicexplorer.optimization.base"):
        opt = _run(tmp_path, monkeypatch, [1.0] * 4 + [500.0] * 40, budget=200,
                   trial_time_stop_s=100.0, trial_time_report_every=0)
    assert opt.clock.trials < 200, "the guard never fired"
    assert opt.stop_reason is not None and "per-trial time guard" in opt.stop_reason
    assert any("per-trial time guard" in r.message for r in caplog.records)
    assert opt.get_best_params() is not None


@requires_cascode
def test_no_stop_threshold_means_no_stop_however_slow_it_gets(tmp_path, monkeypatch):
    opt = _run(tmp_path, monkeypatch, [1e6] * 5, budget=5,
               trial_time_warn_s=1.0, trial_time_report_every=0)
    assert opt.clock.trials == 5
    assert opt.stop_reason is None
