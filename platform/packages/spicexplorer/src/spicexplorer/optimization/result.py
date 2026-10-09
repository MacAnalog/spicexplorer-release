"""The typed result of one optimizer run — what `run_project.run()` returns.

`spicexplorer-optimize` used to be the only way to run a project end to end, and its only
output was its printed lines; a workflow step (orchestration's size -> optimize -> sign-off
chain) had to parse them from stdout. `run()` now returns an `OptimizeResult` instead, and the
CLI's `main()` only prints it.

Plain frozen dataclasses (the `SimTimeReport` precedent in this package): `spicexplorer` does not
depend on pydantic. `to_dict()` is the JSON-ready form for a ledger row or an MCP payload.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RunPlan:
    """What a run is about to do, after the per-run overrides (CLI flags) are applied.

    Handed to `run(on_start=...)` before the first trial, so a caller can report where the
    artifacts and checkpoints will land while the run is still going (the CLI prints it)."""

    name: str
    sim_engine: str
    optimizer: str  # optimizer_config.name (the Nevergrad/Ax algorithm)
    budget: int
    seed: int | None  # optimizer_config.random_seed
    outdir: Path  # ws_root / project.outdir: the per-run simulation artifacts
    checkpoint_dir: Path  # where the optimizer autosaves its checkpoint JSON

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["outdir"] = str(self.outdir)
        d["checkpoint_dir"] = str(self.checkpoint_dir)
        return d


@dataclass(frozen=True)
class OptimizeResult(RunPlan):
    """A finished run: the plan it ran plus the best point it found.

    `best_knobs` are the physical (denormalized) design-variable values of the best trial, the
    same dict the checkpoint logs as `point.params`. `best_metrics` is each spec's measured value
    (`fit_summary[spec]["curr_val"]`; multi-corner keys read `<corner>::<spec>`; an old checkpoint
    may hold bare scalars) — NaN when the spec went unmeasured. `n_trials` counts every completed
    trial of the run, not just the last autosave chunk; `stop_reason` is None for a run that
    spent its budget and a sentence for one a guard ended early. `resumed_from` names the prior
    segments a resumed run continued (resolved paths, in trial order); empty for a fresh run."""

    n_trials: int
    best_score: float
    best_knobs: dict[str, float]
    best_metrics: dict[str, float]
    stop_reason: str | None = None
    resumed_from: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """JSON-clean: paths as strings and a non-finite metric (an unmeasured spec) as None.
        `resumed_from` is a list, present only for a resumed run (a fresh run's record is the
        one it always was)."""
        d = super().to_dict()
        if self.resumed_from:
            d["resumed_from"] = list(self.resumed_from)
        else:
            d.pop("resumed_from", None)
        d["best_metrics"] = {k: _finite_or_none(v) for k, v in self.best_metrics.items()}
        d["best_score"] = _finite_or_none(self.best_score)
        return d


def _finite_or_none(v: float) -> float | None:
    return v if math.isfinite(v) else None


class NoTrialCompleted(RuntimeError):
    """The optimizer finished without a single completed trial (so there is no best point).

    Carries the run's dirs so a caller can still point at the (empty) artifacts."""

    def __init__(self, message: str, *, outdir: Path, checkpoint_dir: Path):
        super().__init__(message)
        self.outdir = outdir
        self.checkpoint_dir = checkpoint_dir
