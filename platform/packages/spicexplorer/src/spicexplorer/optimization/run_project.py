"""`spicexplorer-optimize` — run ONE project YAML through the orchestrator from the shell.

    uv run spicexplorer-optimize path/to/project_setup.yaml [--budget N] [--workers K]
                                 [--outdir DIR] [--seed S] [--algo NAME] [--quiet]
                                 [--engine {nevergrad,bayesian_ax}] [--resume CKPT]...
                                 [--checkpoint-dir DIR] [--report OUT.md]

Engine-agnostic: whatever `sim_engine:` the YAML names (ngspice / spectre / layout) is built
by the backend factory; the optimizer type comes from `optimizer_config.type`. The overrides
are EPHEMERAL (applied in memory, like the API's run-config overrides — the YAML on disk is
never rewritten). Prints the best point + its metrics at the end and returns 0; a project
whose optimizer never produced a trial exits 1; a missing project YAML, or a `--resume` checkpoint
it cannot continue from, exits 2 with one line on stderr.

This is the thin CLI equivalent of `examples/OTA/cascode/ihp-sg13g2/sizing/nevergrad_single_obj_opt.py`
(the reference script) — it exists so an example (e.g. a `sim_engine: layout` project) is
runnable with no per-example driver script.

The run itself is `run()`, callable without the CLI: it returns a typed `OptimizeResult`
(`optimization/result.py`) and raises `NoTrialCompleted` when there is no best point. `main()`
only parses the flags, sets up logging and prints.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import re
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from spicexplorer.core.domains import OptimizerType
from spicexplorer.optimization.result import NoTrialCompleted, OptimizeResult, RunPlan

if TYPE_CHECKING:
    from spicexplorer.core.domains import OptimizationLog, Project_Setup

logger = logging.getLogger("spicexplorer.optimization.run_project")


class ResumeError(ValueError):
    """`resume=` names nothing `run()` can continue from: no checkpoint there, a file that is not
    one, one checkpoint file of a run that autosaved (the rest are in its dir), a path given twice,
    a lineage marker naming a segment that is gone, checkpoints that already hold the whole budget,
    or a `checkpoint_dir` that is where resumed checkpoints are. Raised before any simulator is
    built."""


# `..._trial<N>_<ts>.json` is an autosave chunk written after trial N; `..._trial<N>_CRASH_<ts>` /
# `..._trial<N>_FINAL_<ts>` is named for trial N, which raised or was interrupted (Ctrl-C) or ran last.
_CHECKPOINT_NAME = re.compile(r"_trial(\d+)(_CRASH|_FINAL)?_")

# A resumed segment's lineage, written into its checkpoint dir before its first trial:
#   {"schema_version": "1.0", "trial_offset": N,
#    "segments": [{"path": "<resolved prior segment>", "trials": <its own trial count>}, ...]}
# `segments` is the whole chain in trial order and N the trials it holds, so the segment's first
# trial is N+1 (its checkpoint names continue from there). Not a checkpoint (no
# `optimization_log`), so `summarize_checkpoint` and the chunk reader pass over it.
LINEAGE_MARKER = "resumed_from.json"


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="spicexplorer-optimize", description=(__doc__ or "").split("\n\n")[0]
    )
    ap.add_argument("project_setup", type=Path, help="the project_setup.yaml")
    ap.add_argument("--budget", type=int, default=None, help="override optimizer_config.budget")
    ap.add_argument(
        "--workers",
        type=int,
        default=None,
        help="optimizer_kwargs.num_workers (Nevergrad's batch hint; the trial loop itself is sequential)",
    )
    ap.add_argument("--seed", type=int, default=None, help="override optimizer_config.random_seed")
    ap.add_argument(
        "--algo", default=None, help="override optimizer_config.name (e.g. TwoPointsDE, NGOpt)"
    )
    ap.add_argument(
        "--outdir",
        default=None,
        help="override project.outdir (default: <outdir>_<timestamp>, relative to ws_root)",
    )
    ap.add_argument("--no-timestamp", action="store_true", help="keep project.outdir verbatim")
    ap.add_argument("--quiet", action="store_true", help="less orchestrator logging")
    ap.add_argument(
        "--engine",
        default=None,
        choices=[t.value for t in OptimizerType],
        help="override optimizer_config.type (the optimizer engine)",
    )
    ap.add_argument(
        "--resume",
        default=None,
        action="append",
        metavar="CKPT",
        help="continue from a run's checkpoint dir, or from a checkpoint JSON (e.g. a "
        "_CRASH one) of a run that never autosaved: runs only the budget they have "
        "not spent. A segment that was itself resumed names the segments before it "
        f"({LINEAGE_MARKER}), so its dir alone resumes the whole chain; repeat the "
        "flag for segments written before that marker existed",
    )
    ap.add_argument(
        "--checkpoint-dir",
        default=None,
        help="where the checkpoints go (default: WORK_ROOT/auto_save/<run>_<timestamp>)",
    )
    ap.add_argument(
        "--report",
        default=None,
        metavar="OUT.md",
        help="write the best point's spec-vs-achieved table (Markdown)",
    )
    return ap


def run(
    project_setup: str | Path,
    *,
    budget: int | None = None,
    seed: int | None = None,
    algo: str | None = None,
    workers: int | None = None,
    outdir: str | Path | None = None,
    timestamp_outdir: bool = True,
    verbose: bool = True,
    on_start: Callable[[RunPlan], None] | None = None,
    engine: str | None = None,
    resume: str | Path | Sequence[str | Path] | None = None,
    checkpoint_dir: str | Path | None = None,
    report: str | Path | None = None,
) -> OptimizeResult:
    """Run one project YAML through the orchestrator and return its best point.

    The keyword overrides are the CLI flags and apply to this run only (the YAML is not rewritten).
    `outdir` replaces `project.outdir` verbatim; without it the YAML's outdir gets a
    `_<timestamp>` suffix unless `timestamp_outdir=False`. `engine` replaces
    `optimizer_config.type`. `checkpoint_dir` is the exact dir the checkpoints go to (default:
    `WORK_ROOT/auto_save/<run>_<timestamp>`). `on_start` receives the resolved `RunPlan` once the
    optimizer is built, before the first trial. `report` writes the best point's spec-vs-achieved
    table there (Markdown, see `_spec_report`).

    `resume` continues a run from what its checkpoints hold: a run's checkpoint dir (every
    autosave chunk in it), or one checkpoint JSON (a `_CRASH` or `_FINAL` one) of a run that never
    autosaved; a file of a run that did is refused, since it holds only the trials since the last
    chunk. Only the budget those trials have not spent runs, so a larger `budget` also extends a
    finished run. The new checkpoints hold only the new trials, in `checkpoint_dir` or a fresh
    default dir, named on from the prior trial count (`..._<budget>_trial<K+1>...` after K prior
    trials), and that dir gets a lineage marker (`LINEAGE_MARKER`) naming every prior segment, so
    a later resume of it alone counts the whole chain. `resume` also takes a sequence of paths,
    read in turn: the way to resume segments written before the marker existed (a path given
    twice, or a file inside a dir also given, is refused; a segment both given and named by a
    marker is read once). A `checkpoint_dir` that is a resumed dir (or a resumed file's dir) is
    refused (see `_refuse_writing_into`). The engine is told the prior trials before its first
    ask (Nevergrad's tell, Ax's attach_trial; see `Base_Optimizer._tell_prior_trials`). The
    result's best point is the best of the prior and the new trials, `n_trials` counts them all,
    and `resumed_from` names the prior segments.

    Raises `NoTrialCompleted` when the optimizer ends without a completed trial, and
    `ResumeError` (before any simulator is built) when `resume` cannot be continued from."""
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
        optimizer_type_from_config,
    )

    orch = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=project_setup, auto_load=False, verbose=verbose
    )
    cfg = orch.project_setup.optimizer_config
    if engine is not None:
        # the same D-1 resolution the constructor ran on the YAML's `type:`
        cfg.type = engine
        orch.optimizer_type = optimizer_type_from_config(orch.project_setup)
    if budget is not None:
        cfg.budget = int(budget)
    if seed is not None:
        cfg.random_seed = int(seed)
    if algo:
        cfg.name = algo
    if workers is not None:
        cfg.optimizer_kwargs = {**(cfg.optimizer_kwargs or {}), "num_workers": int(workers)}
    if outdir:
        orch.project_setup.outdir = Path(os.path.expanduser(outdir))
    elif timestamp_outdir:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        orch.project_setup.outdir = Path(f"{orch.project_setup.outdir}_{ts}")
    paths = (
        []
        if resume is None
        else [resume]
        if isinstance(resume, (str, os.PathLike))
        else list(resume)
    )
    prior, segments = _prior_trials(paths) if paths else ([], [])
    if paths and checkpoint_dir:
        _refuse_writing_into([*paths, *(s["path"] for s in segments)], checkpoint_dir)
    if paths and len(prior) >= cfg.budget:
        raise ResumeError(
            f"cannot resume from {_joined(paths)}: it already holds {len(prior)} "
            f"trial(s) and the budget is {cfg.budget}; raise the budget to extend the run"
        )
    orch.initialize()

    opt = orch.get_optimizer()
    if checkpoint_dir:
        # used AS the checkpoint dir, like the `output_root` a caller passes an optimizer
        opt.autosave_checkpoint_dir = Path(os.path.expanduser(checkpoint_dir))
    opt.parameterize()
    is_ax = orch.optimizer_type in (
        Optimizer_Type_Enum.AX_SINGLE,
        Optimizer_Type_Enum.AX_CONSTRAINT,
    )
    plan = RunPlan(
        name=orch.project_setup.name,
        sim_engine=str(orch.project_setup.sim_engine),
        # Ax does not read `name` (a YAML switched to Ax still carries e.g. NGOpt): name the engine
        optimizer=OptimizerType.BAYESIAN_AX.value if is_ax else str(cfg.name),
        budget=int(cfg.budget),
        seed=cfg.random_seed,
        outdir=Path(orch.project_setup.ws_root) / orch.project_setup.outdir,
        checkpoint_dir=Path(opt.autosave_checkpoint_dir),
    )
    if paths:
        logger.info(
            f"resuming from {_joined(paths)}: {len(prior)} prior trial(s) in "
            f"{len(segments)} segment(s), trials {len(prior) + 1}..{plan.budget} of the "
            f"budget of {plan.budget} to run"
        )
        _write_lineage(plan.checkpoint_dir, segments, len(prior))
    if on_start is not None:
        on_start(plan)
    if paths:
        if cfg.random_seed is not None:
            # A seeded engine would replay the prior segment's first proposals (being told them
            # does not move its sampler), so the segment samples from a seed derived from the
            # run's seed and its first trial: reproducible, and new points.
            cfg.random_seed = _segment_seed(int(cfg.random_seed), len(prior))
            logger.info(
                f"resumed segment: the engine's random seed is {cfg.random_seed}, derived "
                f"from the run's seed {plan.seed} and the {len(prior)} prior trial(s)"
            )
        # The loop runs trials len(prior)+1..budget from an empty log (keep_history=True would
        # write the prior trials into the new checkpoints a second time); the engine is told them.
        opt.optimize(
            render_optimization_trace=False,
            keep_history=False,
            trial_offset=len(prior),
            prior_trials=list(prior),
        )
    else:
        opt.optimize(render_optimization_trace=False, keep_history=False)

    prior_best = max(
        (e for e in prior if _finite(e.point.score)),
        key=lambda e: float(e.point.score),
        default=None,
    )
    new_best = getattr(opt, "global_best_entry", None)
    if prior_best is not None and (
        new_best is None or float(prior_best.point.score) > float(new_best.point.score)
    ):
        opt.global_best_entry = prior_best
    best = opt.get_best_params()
    if best is None:
        raise NoTrialCompleted(
            f"{plan.name}: no trial completed",
            outdir=plan.outdir,
            checkpoint_dir=plan.checkpoint_dir,
        )
    params, score, _meta = best
    entry = getattr(opt, "global_best_entry", None)
    metrics: dict[str, Any] = {}
    fit_summary = getattr(entry, "fit_summary", None) if entry is not None else None
    if isinstance(fit_summary, dict):
        metrics = {
            k: (v.get("curr_val") if isinstance(v, dict) else v) for k, v in fit_summary.items()
        }
    # `optimization_log` is emptied on every autosave, so its length undercounts a long run;
    # the trial-time monitor counts every completed trial of the whole run.
    monitor = getattr(opt, "trial_time_monitor", None)
    n_trials = monitor.n if monitor is not None else len(opt.optimization_log)
    result = OptimizeResult(
        **vars(plan),
        n_trials=len(prior) + int(n_trials),
        best_score=float(score),
        best_knobs={k: float(v) for k, v in params.items()},
        best_metrics={k: _as_float(v) for k, v in metrics.items()},
        stop_reason=getattr(opt, "stop_reason", None),
        resumed_from=tuple(s["path"] for s in segments),
    )
    if report is not None:
        path = Path(os.path.expanduser(report))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_spec_report(orch.project_setup, result, fit_summary))
    return result


def _prior_trials(paths: Sequence[str | Path]) -> tuple[OptimizationLog, list[dict[str, Any]]]:
    """The trials the checkpoints hold, path after path, and the segments they came from.

    Each path is one checkpoint JSON, or a run's checkpoint dir read as its autosave chunks in
    trial order (the reader `summarize_checkpoint` uses). A segment whose dir (the path, or a
    file's dir) holds a lineage marker (`LINEAGE_MARKER`) is read after the segments the marker
    names, so the last segment of a chain resumes the whole chain; a segment reached twice is read
    once. A dir written before the marker existed (chunk names restarting at `trial1`) is read as
    it always was. `log_file` is dropped: the per-trial sim log paths are not needed to resume,
    and a legacy checkpoint stored them as a repr string.

    Returns the trials and `[{"path": <resolved segment>, "trials": <its own count>}, ...]` in
    trial order. Raises `ResumeError` for anything that is not a readable checkpoint, for a given
    path that overlaps one given before it (its trials would count twice), for a marker naming a
    segment that is gone, and for a file holding fewer trials than its name says its segment had
    run: the file of a run that autosaved, whose earlier trials are in the chunks beside it."""
    from dacite import Config, DaciteError, from_dict
    from spicexplorer.core.domains import OptimizationLog, OptimizationLogEntry
    from spicexplorer.optimization.summary import _read_entries

    log: list[OptimizationLogEntry] = []
    segments: list[dict[str, Any]] = []
    seen: dict[
        Path, tuple[str | Path, bool]
    ] = {}  # resolved path -> (as given, given by the caller)

    def read(given: str | Path, explicit: bool, via: str | Path) -> None:
        path = Path(os.path.expanduser(given))
        where = path.resolve()
        for p, (g, p_explicit) in seen.items():
            if not (p == where or p in where.parents or where in p.parents):
                continue
            if explicit and p_explicit:
                raise ResumeError(
                    f"cannot resume from {given}: it overlaps {g}, so its trials would count twice"
                )
            if where in p.parents:  # it holds a segment already read, and maybe more
                raise ResumeError(
                    f"cannot resume from {via}: its lineage reaches {given}, which "
                    f"holds {g}, already read, so those trials would count twice"
                )
            logger.info(f"{given} was read already (via {g}); its trials are counted once")
            return
        seen[where] = (given, explicit)
        seg_dir = where if where.is_dir() else where.parent
        marker = _read_lineage(seg_dir, given)
        offset = 0
        if marker is not None:
            for seg in marker["segments"]:
                if not Path(seg["path"]).exists():
                    raise ResumeError(
                        f"cannot resume from {via}: its lineage ({seg_dir / LINEAGE_MARKER}) "
                        f"names {seg['path']}, which is gone; its trials would not "
                        f"be counted"
                    )
                read(seg["path"], False, via)
            offset = int(marker["trial_offset"])
        try:
            entries, _version, skipped = _read_entries(path)
            own = [
                from_dict(OptimizationLogEntry, {**e, "log_file": None}, Config(strict=False))
                for e in entries
            ]
        except FileNotFoundError as exc:
            if marker is None or not path.is_dir():
                raise ResumeError(f"cannot resume from {given}: {exc}") from exc
            entries, own, skipped = (
                [],
                [],
                {},
            )  # a resumed segment that ended before its first chunk
        except (OSError, ValueError, DaciteError) as exc:
            raise ResumeError(f"cannot resume from {given}: {exc}") from exc
        if skipped:  # a chunk nobody can read holds trials the resumed run would not count
            raise ResumeError(
                f"cannot resume from {given}: "
                + "; ".join(f"{name} cannot be read ({why})" for name, why in skipped.items())
            )
        m = _CHECKPOINT_NAME.search(path.name) if path.is_file() else None
        # trial N of a _CRASH/_FINAL may not have completed, so N-1 trials had run; a resumed
        # segment's names count on from its lineage's `trial_offset`
        ran = 0 if m is None else int(m.group(1)) - (1 if m.group(2) else 0) - offset
        if len(entries) < ran:
            raise ResumeError(
                f"cannot resume from {given}: it holds only {len(entries)} trial(s), "
                f"but the run had completed at least {ran} when it was written (the "
                f"others are in its earlier autosave chunks); pass its checkpoint dir "
                f"{path.parent}"
            )
        log.extend(own)
        segments.append({"path": str(where), "trials": len(own)})

    for given in paths:
        read(given, True, given)
    return OptimizationLog(log), segments


def _segment_seed(seed: int, trial_offset: int) -> int:
    """The engine seed of a resumed segment whose first trial is `trial_offset + 1`: a function
    of the run's seed and the offset (so a resume is reproducible), in [0, 2**32)."""
    import numpy as np

    return int(np.random.SeedSequence([seed & 0xFFFFFFFF, trial_offset]).generate_state(1)[0])


def _read_lineage(seg_dir: Path, given: str | Path) -> dict[str, Any] | None:
    """The lineage marker in `seg_dir`, or None when there is none (a segment that was not
    resumed, or one written before the marker existed). Raises `ResumeError` for one it cannot
    read."""
    marker = seg_dir / LINEAGE_MARKER
    if not marker.is_file():
        return None
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
        segs = data["segments"]
        ok = (
            isinstance(segs, list)
            and all(isinstance(s, dict) and isinstance(s.get("path"), str) for s in segs)
            and int(data["trial_offset"]) >= 0
        )
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ResumeError(
            f"cannot resume from {given}: its lineage marker {marker} cannot be "
            f"read ({type(exc).__name__}: {exc})"
        ) from exc
    if not ok:
        raise ResumeError(
            f"cannot resume from {given}: its lineage marker {marker} is not one "
            f"(expected trial_offset and a list of segment paths)"
        )
    return data


def _write_lineage(
    checkpoint_dir: Path, segments: Sequence[Mapping[str, Any]], trial_offset: int
) -> None:
    """Write the new segment's lineage marker before its first trial, so a segment that crashes
    early still names what it resumed."""
    from spicexplorer_core.atomic_io import atomic_write_json

    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
    atomic_write_json(
        Path(checkpoint_dir) / LINEAGE_MARKER,
        {
            "schema_version": "1.0",
            "trial_offset": int(trial_offset),
            "segments": [
                {"path": str(seg["path"]), "trials": int(seg["trials"])} for seg in segments
            ],
        },
    )


def _refuse_writing_into(paths: Sequence[str | Path], checkpoint_dir: str | Path) -> None:
    """Raise `ResumeError` when `checkpoint_dir` is a resumed dir, or the dir of a resumed file
    (`paths` holds the given ones and every segment their lineage reached).

    The new segment's chunk names continue the numbering, so they would sort after the prior
    chunks; the dir is still refused. Its lineage marker would name the dir itself, and a later
    resume of the dir would read the marker's segments AND the same chunks again under one name
    (the old segment's own marker, when it has one, is also overwritten). One segment per dir
    keeps every segment's trials countable once."""
    target = Path(os.path.expanduser(checkpoint_dir)).resolve()
    for given in paths:
        path = Path(os.path.expanduser(given)).resolve()
        if target == (path if path.is_dir() else path.parent):
            raise ResumeError(
                f"cannot resume from {given}: --checkpoint-dir {checkpoint_dir} is "
                f"where its checkpoints are; a resumed run writes one new segment "
                f"per dir (its lineage marker names the dirs before it, and the "
                f"chunks of two segments in one dir would mix their trial order "
                f"and lineage); pass a new --checkpoint-dir"
            )


def _joined(paths: Sequence[str | Path]) -> str:
    return ", ".join(map(str, paths))


def _spec_report(
    setup: Project_Setup, result: OptimizeResult, fit_summary: Mapping[str, Any] | None
) -> str:
    """The best point's spec-vs-achieved table (Markdown): one row per enabled spec, and in
    `pvt.mode: multi` one per enabled corner and spec, named `<corner>::<spec>` like its
    `fit_summary` key. `pass` is the scorer's own verdict, spec score > -EPSILON (the threshold
    `summarize_checkpoint` uses). A spec the best trial did not log, or logged as a bare scalar
    (an old checkpoint may hold one), has no verdict (n/a); an unmeasured reading shows n/a."""
    from spicexplorer.core.utils import EPSILON

    fit = fit_summary if isinstance(fit_summary, Mapping) else {}
    pvt = getattr(setup, "pvt", None)
    corners = (
        [c.name for c in pvt.corners_to_run()] if pvt is not None and pvt.is_multi() else [None]
    )
    lines = [
        f"# {result.name}: spec vs achieved",
        "",
        f"engine {result.sim_engine}, optimizer {result.optimizer}, {result.n_trials} of "
        f"{result.budget} trials, best score {result.best_score:.6g}",
        "",
    ]
    if result.resumed_from:
        lines += ["Resumed from: " + ", ".join(result.resumed_from), ""]
    if result.stop_reason:
        lines += [f"Stopped early: {result.stop_reason}", ""]
    lines += [
        "| spec | goal | target | tol | achieved | pass |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for corner in corners:
        for spec in setup.optimizer_config.target_specs.enabled_targets():
            key = spec.name if corner is None else f"{corner}::{spec.name}"
            info = fit.get(key)
            achieved, score = (
                (info.get("curr_val"), info.get("score"))
                if isinstance(info, Mapping)
                else (info, None)
            )
            verdict = (
                "n/a"
                if not _finite(score)
                else ("yes" if _as_float(score) > -float(EPSILON) else "no")
            )
            lines.append(
                f"| {key} | {getattr(spec.goal, 'value', spec.goal)} | {_fmt(spec.target)} "
                f"| {_fmt(spec.tolerance)} | {_fmt(achieved)} | {verdict} |"
            )
    return "\n".join(lines) + "\n"


def _as_float(v: Any) -> float:
    """A metric reading as a float; NaN for a missing or non-numeric one (never raises)."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def _finite(v: Any) -> bool:
    """A finite number (a bool is not one)."""
    return not isinstance(v, bool) and math.isfinite(_as_float(v))


def _fmt(v: Any) -> str:
    return f"{_as_float(v):.6g}" if _finite(v) else "n/a"


def _print_start(plan: RunPlan) -> None:
    print(
        f"[spicexplorer-optimize] {plan.name}: engine={plan.sim_engine} "
        f"optimizer={plan.optimizer} budget={plan.budget}",
        flush=True,
    )
    print(f"[spicexplorer-optimize] artifacts: {plan.outdir}", flush=True)
    print(f"[spicexplorer-optimize] checkpoints: {plan.checkpoint_dir}", flush=True)


def main(argv: list[str] | None = None) -> int:
    a = _build_parser().parse_args(argv)
    if not a.project_setup.is_file():  # before the logging setup, which writes WORK_ROOT/logs/
        print(f"[spicexplorer-optimize] no project YAML at {a.project_setup}", file=sys.stderr)
        return 2
    from spicexplorer_core.logging.logger_setup import setup_loggers_with_spicelib_suppression

    setup_loggers_with_spicelib_suppression()
    if a.quiet:
        logging.getLogger("spicexplorer").setLevel(logging.WARNING)

    try:
        result = run(
            a.project_setup,
            budget=a.budget,
            seed=a.seed,
            algo=a.algo,
            workers=a.workers,
            outdir=a.outdir,
            timestamp_outdir=not a.no_timestamp,
            verbose=not a.quiet,
            on_start=_print_start,
            engine=a.engine,
            resume=a.resume,
            checkpoint_dir=a.checkpoint_dir,
            report=a.report,
        )
    except NoTrialCompleted:
        print("[spicexplorer-optimize] no trial completed", file=sys.stderr)
        return 1
    except ResumeError as exc:
        print(f"[spicexplorer-optimize] {exc}", file=sys.stderr)
        return 2
    # Design repos parse these three lines back into JSON with a regex (test_run_contract
    # checks them with that same regex). Keep the prefix, `best <field>` and the JSON-object
    # payloads unchanged.
    print(f"[spicexplorer-optimize] best score {result.best_score:.6g}")
    print("[spicexplorer-optimize] best knobs: " + json.dumps(result.best_knobs, default=str))
    if result.best_metrics:
        print(
            "[spicexplorer-optimize] best metrics: " + json.dumps(result.best_metrics, default=str)
        )
    if a.report is not None:  # after the three lines above, and not a `best …` line
        print(f"[spicexplorer-optimize] report: {a.report}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
