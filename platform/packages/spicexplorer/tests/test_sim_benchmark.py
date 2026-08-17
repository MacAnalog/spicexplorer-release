"""Offline tests for per-testbench sim-time benchmarking (no SPICE engine needed).

Fake `Simulator`s with known, distinct durations prove the core contract: each
testbench is billed its OWN sim time — in sequential mode by timing the blocking
``run()``, in parallel mode by pairing each handle's submit stamp with its
``is_done()`` flip — so a fast bench is never billed for a slow sibling's wall time.
"""
from __future__ import annotations

import logging
from time import monotonic, sleep

from spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE
from spicexplorer.optimization.sim_benchmark import (
    SimTimeReport,
    TestbenchSimTiming,
    benchmark_simulators,
    wait_for_handles_timed,
)

# Fake sim durations (seconds). Big enough to dominate the 10 ms poll resolution,
# small enough to keep the suite fast.
FAST_S = 0.05
SLOW_S = 0.25


class _FakeResult:
    raw = object()  # non-None → "sim produced output" on the ngspice ok-probe


class _TimedHandle:
    """A handle that reports done once its (fake) sim duration has elapsed."""

    def __init__(self, duration_s: float):
        self._t_done = monotonic() + duration_s

    def is_done(self) -> bool:
        return monotonic() >= self._t_done

    def result(self) -> _FakeResult:
        return _FakeResult()


class _FakeSimulator:
    """Protocol-shaped fake whose run/submit take a known duration."""

    def __init__(self, duration_s: float):
        self.duration_s = duration_s

    def update_params(self, params, /) -> bool:
        return True

    def apply_corner(self, corner, /, *, model_lib_root=None) -> None:
        pass

    def run(self, *, label=None) -> _FakeResult:
        sleep(self.duration_s)
        return _FakeResult()

    def submit(self, *, label=None) -> _TimedHandle:
        return _TimedHandle(self.duration_s)


class _SanityWrapper(_FakeSimulator):
    """Adds the ngspice-only `run_sanity_check` extra the orchestrator duck-types."""

    def __init__(self, duration_s: float, ok: bool = True):
        super().__init__(duration_s)
        self.ok = ok

    def run_sanity_check(self, use_editor=True, sim_execution_t=None) -> bool:
        sleep(self.duration_s)
        return self.ok


def _bare_orchestrator(wrappers) -> Circuit_Optimizer_Orchestrator_with_SPICE:
    """An orchestrator with wrappers injected directly — no YAML/project load."""
    orch = object.__new__(Circuit_Optimizer_Orchestrator_with_SPICE)
    orch.spicelib_wrappers = wrappers
    return orch


# ---------------------------------------------------------------------------
# wait_for_handles_timed
# ---------------------------------------------------------------------------

def test_wait_records_a_done_stamp_per_handle():
    t0 = monotonic()
    handles = {"fast": _TimedHandle(FAST_S), "slow": _TimedHandle(SLOW_S)}
    pending, done_at = wait_for_handles_timed(handles, timeout_s=5.0)
    assert pending == []
    assert set(done_at) == {"fast", "slow"}
    # The fast handle's stamp must land well before the slow one's duration —
    # i.e. per-handle stamps, not one batch-completion stamp for everybody.
    assert done_at["fast"] - t0 < SLOW_S
    assert done_at["slow"] >= done_at["fast"]


def test_wait_timeout_returns_pending_without_stamps():
    handles = {"done": _TimedHandle(0.0), "hung": _TimedHandle(60.0)}
    pending, done_at = wait_for_handles_timed(handles, timeout_s=FAST_S)
    assert pending == ["hung"]
    assert set(done_at) == {"done"}


# ---------------------------------------------------------------------------
# benchmark_simulators
# ---------------------------------------------------------------------------

def test_sequential_benchmark_times_each_testbench():
    sims = {"tb_fast": _FakeSimulator(FAST_S), "tb_slow": _FakeSimulator(SLOW_S)}
    report = benchmark_simulators(sims, runs=1, parallel=False)
    means = report.mean_elapsed_s()
    assert set(means) == {"tb_fast", "tb_slow"}
    assert FAST_S <= means["tb_fast"] < SLOW_S
    assert means["tb_slow"] >= SLOW_S
    assert report.all_ok()
    assert all(t.mode == "sequential" for t in report.timings)


def test_parallel_benchmark_bills_each_testbench_its_own_span():
    sims = {"tb_fast": _FakeSimulator(FAST_S), "tb_slow": _FakeSimulator(SLOW_S)}
    report = benchmark_simulators(sims, runs=1, parallel=True)
    means = report.mean_elapsed_s()
    # The core parallel contract: the fast bench's span is its own, NOT the batch
    # wall time (which is >= SLOW_S because both ran concurrently).
    assert means["tb_fast"] < SLOW_S
    assert means["tb_slow"] >= SLOW_S
    assert report.all_ok()
    assert all(t.mode == "parallel" for t in report.timings)


def test_parallel_benchmark_marks_timeouts_not_ok():
    sims = {"tb_ok": _FakeSimulator(0.0), "tb_hung": _FakeSimulator(60.0)}
    report = benchmark_simulators(sims, runs=1, parallel=True, timeout_s=FAST_S)
    by_tb = {t.testbench: t for t in report.timings}
    assert by_tb["tb_ok"].ok
    assert not by_tb["tb_hung"].ok
    assert not report.all_ok()


def test_repeat_runs_accumulate_per_testbench():
    sims = {"tb": _FakeSimulator(0.0)}
    report = benchmark_simulators(sims, runs=3, parallel=False)
    assert len(report.per_testbench()["tb"]) == 3


def test_sequential_benchmark_run_exception_is_not_ok():
    class _Boom(_FakeSimulator):
        def run(self, *, label=None):
            raise RuntimeError("engine exploded")

    report = benchmark_simulators({"tb": _Boom(0.0)}, runs=1, parallel=False)
    assert not report.timings[0].ok


# ---------------------------------------------------------------------------
# SimTimeReport
# ---------------------------------------------------------------------------

def test_report_table_and_dict_roundtrip(tmp_path):
    report = SimTimeReport(timings=[
        TestbenchSimTiming("ac", 0.5, True, mode="sanity"),
        TestbenchSimTiming("tran", 5.0, True, mode="sanity"),
    ])
    table = report.format_table()
    # Slowest first, with a share column and total.
    assert table.index("tran") < table.index("ac")
    assert "TOTAL" in table
    saved = report.save(tmp_path / "simtime")
    assert saved.exists()
    d = report.to_dict()
    assert d["mean_elapsed_s"]["tran"] == 5.0


# ---------------------------------------------------------------------------
# Orchestrator surface: sanity timing + benchmark_testbenches
# ---------------------------------------------------------------------------

def test_sanity_run_logs_and_stores_per_testbench_times(caplog):
    orch = _bare_orchestrator({
        "tb_ac": _SanityWrapper(FAST_S),
        "tb_tran": _SanityWrapper(SLOW_S),
    })
    with caplog.at_level(logging.INFO, logger="spicexplorer.optimization.orchestrator"):
        assert orch.run_sanity_on_spicelib_wrapper(use_editor=False) is True
    timings = {t.testbench: t for t in orch.last_sanity_timings}
    assert set(timings) == {"tb_ac", "tb_tran"}
    assert timings["tb_ac"].elapsed_s >= FAST_S
    assert timings["tb_tran"].elapsed_s >= SLOW_S
    assert all(t.mode == "sanity" and t.ok for t in orch.last_sanity_timings)
    assert "sanity sim time for testbench 'tb_ac'" in caplog.text
    assert "per-testbench sanity sim times" in caplog.text


def test_sanity_run_failure_still_records_the_failed_bench(caplog):
    orch = _bare_orchestrator({
        "tb_good": _SanityWrapper(0.0, ok=True),
        "tb_bad": _SanityWrapper(0.0, ok=False),
        "tb_never_run": _SanityWrapper(0.0, ok=True),
    })
    with caplog.at_level(logging.INFO, logger="spicexplorer.optimization.orchestrator"):
        assert orch.run_sanity_on_spicelib_wrapper(use_editor=False) is False
    by_tb = {t.testbench: t for t in orch.last_sanity_timings}
    # The failing bench is timed too; the loop still stops there (legacy behavior).
    assert set(by_tb) == {"tb_good", "tb_bad"}
    assert by_tb["tb_bad"].ok is False


def test_sanity_run_skips_backends_without_checker():
    orch = _bare_orchestrator({"tb_spectre": _FakeSimulator(0.0)})
    assert orch.run_sanity_on_spicelib_wrapper() is True
    assert orch.last_sanity_timings == []


def test_orchestrator_benchmark_testbenches(tmp_path):
    orch = _bare_orchestrator({
        "tb_fast": _FakeSimulator(FAST_S),
        "tb_slow": _FakeSimulator(SLOW_S),
    })
    # No project_setup on the bare instance — pass parallel explicitly.
    report = orch.benchmark_testbenches(
        runs=1, parallel=True, save_path=tmp_path / "bench")
    assert (tmp_path / "bench.json").exists()
    means = report.mean_elapsed_s()
    assert means["tb_fast"] < SLOW_S <= means["tb_slow"] + 1e-9
