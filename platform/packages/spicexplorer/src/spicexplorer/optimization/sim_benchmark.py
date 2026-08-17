"""Per-testbench simulation-time benchmarking.

The optimizer treats every testbench as equally cheap, but a transient bench can
cost 100x an AC bench. This module measures the wall-clock cost of each
testbench so a project's sim budget is visible up front — and so a follow-on
feature can gate long-running sims on the fast ones passing first.

Everything here speaks only the engine-neutral `Simulator` protocol, so the
same benchmark runs on the ngspice lane and the Spectre/virtuoso-bridge lane.

Timing semantics:

* **sequential** — each testbench's blocking ``run()`` is timed on its own; the
  elapsed time is that testbench's full cost (deck write + engine run + read).
* **parallel** — every testbench is ``submit()``-ed first, then one poll loop
  records the moment each handle's ``is_done()`` flips true. Each testbench's
  elapsed time is its own submit→done span (poll resolution ~10 ms), NOT the
  batch wall time — so a fast bench is not billed for a slow sibling. Note the
  span *includes* any wait in the backend's runner queue when more sims are
  submitted than the runner's concurrency allows.
"""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from time import monotonic, perf_counter, sleep
from typing import Dict, List, Tuple

from spicexplorer_core.atomic_io import atomic_write_json
from spicexplorer_core.spice_engine import SimHandle, Simulator

logger = logging.getLogger("spicexplorer.optimization.sim_benchmark")

_POLL_INTERVAL_S = 0.01


@dataclass
class TestbenchSimTiming:
    """One timed simulation of one testbench."""

    # Not a test class — the "Test" prefix otherwise trips pytest collection.
    __test__ = False

    testbench: str
    elapsed_s: float
    ok: bool
    # How the sim was dispatched: "sequential" | "parallel" | "sanity".
    mode: str = "sequential"
    # Optional run tag (e.g. the PVT corner name, or "run 2/3" of a repeat).
    label: str | None = None


@dataclass
class SimTimeReport:
    """All timings from one benchmark pass, with per-testbench aggregation."""

    timings: List[TestbenchSimTiming] = field(default_factory=list)

    def per_testbench(self) -> Dict[str, List[TestbenchSimTiming]]:
        out: Dict[str, List[TestbenchSimTiming]] = {}
        for t in self.timings:
            out.setdefault(t.testbench, []).append(t)
        return out

    def mean_elapsed_s(self) -> Dict[str, float]:
        return {
            tb: sum(t.elapsed_s for t in runs) / len(runs)
            for tb, runs in self.per_testbench().items()
        }

    def all_ok(self) -> bool:
        return all(t.ok for t in self.timings)

    def to_dict(self) -> dict:
        return {
            "timings": [asdict(t) for t in self.timings],
            "mean_elapsed_s": self.mean_elapsed_s(),
        }

    def save(self, path: str | Path) -> Path:
        """Persist the report as JSON (atomic — same discipline as checkpoints)."""
        p = Path(path).with_suffix(".json")
        p.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(p, self.to_dict(), indent=2)
        logger.info(f"⏱️  sim-time report saved to {p}")
        return p

    def format_table(self) -> str:
        """A log-friendly table of per-testbench mean sim time, slowest first."""
        means = self.mean_elapsed_s()
        by_tb = self.per_testbench()
        if not means:
            return "(no testbench timings recorded)"
        total = sum(means.values())
        width = max(len(tb) for tb in means)
        lines = [f"{'testbench':<{width}}  {'mean sim time':>13}  {'share':>6}  runs  ok"]
        for tb, mean_s in sorted(means.items(), key=lambda kv: -kv[1]):
            runs = by_tb[tb]
            ok = "yes" if all(t.ok for t in runs) else "NO"
            share = (mean_s / total * 100.0) if total > 0 else 0.0
            lines.append(
                f"{tb:<{width}}  {mean_s:>11.3f} s  {share:>5.1f}%  {len(runs):>4}  {ok}"
            )
        lines.append(f"{'TOTAL (sum of means)':<{width}}  {total:>11.3f} s")
        return "\n".join(lines)


def wait_for_handles_timed(
    handles: Dict[str, SimHandle], timeout_s: float | None = None
) -> Tuple[List[str], Dict[str, float]]:
    """Poll ``handles`` until all are done or ``timeout_s`` elapses, recording WHEN
    each one finished.

    Returns ``(timed_out_keys, done_at)`` where ``done_at`` maps each completed
    handle's key to the ``time.monotonic()`` stamp at which its ``is_done()`` flip was
    observed (poll resolution ``_POLL_INTERVAL_S``). Pairing those stamps with each
    handle's own submit stamp gives a per-testbench span even though the sims ran
    concurrently. Keys that time out are absent from ``done_at``. ``timeout_s`` of
    ``None``/``<= 0`` waits forever.
    """
    deadline = (monotonic() + timeout_s) if timeout_s and timeout_s > 0 else None
    done_at: Dict[str, float] = {}
    while True:
        now = monotonic()
        for key, h in handles.items():
            if key not in done_at and h.is_done():
                done_at[key] = now
        pending = [k for k in handles if k not in done_at]
        if not pending:
            return [], done_at
        if deadline is not None and now >= deadline:
            return pending, done_at
        sleep(_POLL_INTERVAL_S)


def benchmark_simulators(
    simulators: Dict[str, Simulator],
    runs: int = 1,
    parallel: bool = False,
    timeout_s: float | None = None,
) -> SimTimeReport:
    """Time every testbench's simulation ``runs`` times and return a `SimTimeReport`.

    Engine-neutral: drives only the `Simulator` protocol (``run``/``submit``), so it
    works identically for ngspice wrappers and the Spectre bridge adapter. Params and
    PVT corner are whatever each wrapper's netlist currently carries — the benchmark
    measures cost, it does not restage the design point.

    :param simulators: testbench name → `Simulator` (e.g. the orchestrator's wrappers).
    :param runs: repeat count per testbench (means smooth out engine start-up jitter).
    :param parallel: dispatch each round via ``submit()`` and time per-handle
        completion (see module docstring for what the parallel span includes).
    :param timeout_s: parallel-mode bound per round; a testbench that misses it is
        recorded with ``ok=False`` and the elapsed time at the bound.
    """
    report = SimTimeReport()
    for run_idx in range(runs):
        label = f"run {run_idx + 1}/{runs}" if runs > 1 else None
        if not parallel:
            for tb, sim in simulators.items():
                t0 = perf_counter()
                ok = True
                try:
                    result = sim.run(label=None)
                    # ngspice signals a failed/diverged sim by a None RAW; engines
                    # without that attribute count as ok unless they raised.
                    ok = getattr(result, "raw", True) is not None
                except Exception as exc:
                    ok = False
                    logger.warning(f"⏱️  benchmark run failed for testbench '{tb}': {exc}")
                report.timings.append(TestbenchSimTiming(
                    testbench=tb, elapsed_s=perf_counter() - t0, ok=ok,
                    mode="sequential", label=label,
                ))
        else:
            handles: Dict[str, SimHandle] = {}
            submitted_at: Dict[str, float] = {}
            failed_submit: List[str] = []
            for tb, sim in simulators.items():
                try:
                    submitted_at[tb] = monotonic()
                    handles[tb] = sim.submit(label=None)
                except Exception as exc:
                    failed_submit.append(tb)
                    logger.warning(f"⏱️  benchmark submit failed for testbench '{tb}': {exc}")
            timed_out, done_at = wait_for_handles_timed(handles, timeout_s=timeout_s)
            t_end = monotonic()
            for tb in simulators:
                if tb in failed_submit:
                    report.timings.append(TestbenchSimTiming(
                        testbench=tb, elapsed_s=0.0, ok=False, mode="parallel", label=label))
                elif tb in timed_out:
                    report.timings.append(TestbenchSimTiming(
                        testbench=tb, elapsed_s=t_end - submitted_at[tb], ok=False,
                        mode="parallel", label=label))
                else:
                    report.timings.append(TestbenchSimTiming(
                        testbench=tb, elapsed_s=done_at[tb] - submitted_at[tb], ok=True,
                        mode="parallel", label=label))
    return report


__all__ = [
    "TestbenchSimTiming",
    "SimTimeReport",
    "benchmark_simulators",
    "wait_for_handles_timed",
]
