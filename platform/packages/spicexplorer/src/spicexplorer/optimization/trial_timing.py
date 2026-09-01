"""Per-trial wall-time telemetry for the optimization loop.

A trial's cost is not constant across a run, and nothing in the loop said so. Measured on the
TCAS-2026 campaign (ledger E-049), an Ax/BoTorch run's per-trial wall time grew **27 s -> 117 s ->
200-292 s** as the GP refit cost climbed with the observation count; `bo_nevergrad` shows the same
late-run growth. The simulation cost per trial had not changed at all — the search backend had
become the bottleneck. With no signal in the log, the only way to notice was to watch the progress
bar, and those runs had to be killed by hand.

This module is the measurement half of that: a small, pure accumulator the loop feeds one duration
per trial. It computes a rolling median (robust to the one slow trial a flaky sim produces),
compares it against the run's own early-trial baseline, and reports a verdict. It performs NO
logging and NO I/O, so the loop decides what to say and the tests can drive it with a list of
numbers instead of a clock.

Everything is OFF by default: with no thresholds configured the verdict never warns and never
stops, so an existing project's run is unchanged apart from a periodic INFO line reporting the
rolling cost.

Thresholds (all `None` = off, set from `optimizer_config`):

* ``trial_time_warn_s``      — absolute: warn once the rolling median exceeds this many seconds.
* ``trial_time_warn_factor`` — relative: warn once the rolling median exceeds this multiple of the
  run's own baseline median. The honest one for E-049, whose signature is *growth*, not an
  absolute number — a 27 s trial is fine, a 27 s trial that became 200 s is not.
* ``trial_time_stop_s``      — hard stop: end the run gracefully once the rolling median exceeds
  this. Deliberately the ROLLING MEDIAN, not a single trial: one slow trial is a hiccup (a retried
  sim, a loaded host), a sustained cost is the wall. A run stopped this way is *stopped*, not
  crashed — the loop records the reason and takes its normal final checkpoint.

A warning LATCHES: it fires on the crossing and stays quiet until the rolling median recovers back
below the threshold, so a run that is simply slow does not emit one WARNING per trial.
"""
from __future__ import annotations

import statistics
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional

#: Trials in the rolling window. Wide enough that a single slow trial cannot move the median,
#: short enough to track growth within a few tens of trials.
DEFAULT_TRIAL_TIME_WINDOW: int = 20

#: Trials that define the run's own baseline cost for `trial_time_warn_factor`. Measured from the
#: START of the run, where a Bayesian backend has not yet accumulated its refit cost.
DEFAULT_TRIAL_TIME_BASELINE: int = 10

#: How often the rolling cost is reported. Every trial would drown the log.
DEFAULT_TRIAL_TIME_REPORT_EVERY: int = 25


@dataclass(frozen=True)
class TrialTimeVerdict:
    """What the monitor concluded after one trial. The loop turns this into log lines."""

    trial: int                                   # 1-based count of trials recorded so far
    elapsed_s: float                             # this trial's wall time
    rolling_median_s: float                      # median over the last `window` trials
    baseline_median_s: Optional[float] = None    # median over the first `baseline_trials`, once known
    #: A WARNING to emit, or None. Non-None only on the trial that CROSSES a threshold.
    warning: Optional[str] = None
    #: A periodic INFO line, or None on trials that are not a reporting cadence tick.
    report: Optional[str] = None
    #: True once `trial_time_stop_s` is crossed — the loop should end the run gracefully.
    stop: bool = False

    @property
    def growth_factor(self) -> Optional[float]:
        """Rolling median as a multiple of the baseline median; None until the baseline exists."""
        if not self.baseline_median_s:
            return None
        return self.rolling_median_s / self.baseline_median_s


@dataclass
class TrialTimeMonitor:
    """Rolling per-trial wall-time tracker. Pure: feed it durations, read verdicts.

    Constructed from `optimizer_config`'s three (optional) thresholds; every one of them defaults
    to `None`, which is off. See the module docstring for the semantics of each.
    """

    warn_s: Optional[float] = None
    warn_factor: Optional[float] = None
    stop_s: Optional[float] = None
    window: int = DEFAULT_TRIAL_TIME_WINDOW
    baseline_trials: int = DEFAULT_TRIAL_TIME_BASELINE
    report_every: int = DEFAULT_TRIAL_TIME_REPORT_EVERY

    n: int = field(default=0, init=False)
    _total_s: float = field(default=0.0, init=False, repr=False)
    _recent: Deque[float] = field(init=False, repr=False)
    _first: List[float] = field(default_factory=list, init=False, repr=False)
    _warned_absolute: bool = field(default=False, init=False, repr=False)
    _warned_relative: bool = field(default=False, init=False, repr=False)
    stopped: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self.window = max(1, int(self.window))
        self.baseline_trials = max(1, int(self.baseline_trials))
        self.report_every = max(0, int(self.report_every))
        self._recent = deque(maxlen=self.window)

    # ----------------------------
    # --- Read-only statistics ---
    # ----------------------------
    @property
    def rolling_median_s(self) -> Optional[float]:
        """Median of the last `window` trials; None before any trial is recorded."""
        return statistics.median(self._recent) if self._recent else None

    @property
    def baseline_median_s(self) -> Optional[float]:
        """Median of the first `baseline_trials` trials; None until that many are recorded.

        Withheld until the window is full on purpose: a baseline built from one or two trials is
        noise, and dividing by it would make `warn_factor` fire on jitter."""
        if len(self._first) < self.baseline_trials:
            return None
        return statistics.median(self._first)

    @property
    def total_s(self) -> float:
        """Wall time spent in trials so far (not the run's wall time — it excludes setup)."""
        return self._total_s

    # ----------------------------
    # --- The one hot-path call ---
    # ----------------------------
    def record(self, elapsed_s: float) -> TrialTimeVerdict:
        """Record one trial's wall time and return the verdict for it.

        Never raises on a nonsensical duration (a clock that went backwards yields a negative
        span on some platforms): it is clamped to 0 rather than poisoning the median."""
        elapsed_s = max(0.0, float(elapsed_s))
        self.n += 1
        self._total_s += elapsed_s
        self._recent.append(elapsed_s)
        if len(self._first) < self.baseline_trials:
            self._first.append(elapsed_s)

        rolling = statistics.median(self._recent)
        baseline = self.baseline_median_s

        warning = self._check_thresholds(rolling, baseline)
        stop = False
        if self.stop_s is not None and rolling > self.stop_s and not self.stopped:
            self.stopped = stop = True

        report = None
        if self.report_every and self.n % self.report_every == 0:
            report = (f"⏱️  trial {self.n}: {elapsed_s:.1f} s "
                      f"(rolling median over the last {len(self._recent)} trial(s): "
                      f"{rolling:.1f} s/trial{self._growth_suffix(rolling, baseline)})")

        return TrialTimeVerdict(
            trial=self.n, elapsed_s=elapsed_s, rolling_median_s=rolling,
            baseline_median_s=baseline, warning=warning, report=report, stop=stop)

    # ----------------------------
    # --- Helpers ---
    # ----------------------------
    def _growth_suffix(self, rolling: float, baseline: Optional[float]) -> str:
        if not baseline:
            return ""
        return f", {rolling / baseline:.1f}x the first-{self.baseline_trials}-trial baseline"

    def _check_thresholds(self, rolling: float, baseline: Optional[float]) -> Optional[str]:
        """One warning per crossing, re-armed when the rolling median recovers (see module doc)."""
        if self.warn_s is not None:
            if rolling > self.warn_s:
                if not self._warned_absolute:
                    self._warned_absolute = True
                    return (f"per-trial wall time has grown past the configured budget: rolling "
                            f"median {rolling:.1f} s/trial > trial_time_warn_s={self.warn_s:.1f} s "
                            f"at trial {self.n}. The search backend, not the simulation, is the "
                            f"usual cause late in a run (GP refit cost — ledger E-049).")
            else:
                self._warned_absolute = False

        if self.warn_factor is not None and baseline:
            if rolling > self.warn_factor * baseline:
                if not self._warned_relative:
                    self._warned_relative = True
                    return (f"per-trial wall time is growing: rolling median {rolling:.1f} s/trial "
                            f"is {rolling / baseline:.1f}x this run's own first-"
                            f"{self.baseline_trials}-trial baseline of {baseline:.1f} s "
                            f"(trial_time_warn_factor={self.warn_factor:g}) at trial {self.n}.")
            else:
                self._warned_relative = False
        return None
