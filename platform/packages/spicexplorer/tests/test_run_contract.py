"""The typed optimizer run result: `run_project.run()` -> `OptimizeResult`, and
`spicexplorer.optimization.summarize_checkpoint` over the checkpoint JSON a run leaves.

`run()` is the library half of `spicexplorer-optimize`: a workflow step (orchestration's
sizing -> optimize -> sign-off chain) calls it in-process and reads a typed result instead of
parsing the CLI's stdout. `main()` only prints that result, so these tests check the CLI's
printed lines too.

OFFLINE: every simulation is served by a fake Spectre bridge through the real `SpectreSimulator`
adapter (the pattern of `test_spectre_loop_offline.py`), so a real Nevergrad loop runs with no
ngspice binary, no PDK and no Cadence.
"""

from __future__ import annotations

import ast
import json
import logging
import math
import re
import sys
from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import FrozenInstanceError, dataclass, field, fields
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import spicexplorer.optimization.run_project as run_project
from _spicexplorer_fixtures import EXAMPLE_YAML
from spicexplorer.backends.spectre import SpectreSimulator
from spicexplorer.core.domains import OptimizationLogEntry
from spicexplorer.core.utils import EPSILON
from spicexplorer.optimization import (
    Circuit_Optimizer_Orchestrator_with_SPICE,
    summarize_checkpoint,
)
from spicexplorer.optimization.result import NoTrialCompleted, OptimizeResult, RunPlan
from spicexplorer.optimization.run_project import main, run
from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective
from spicexplorer.optimization.summary import CheckpointSummary

PREFIX = "[spicexplorer-optimize]"


class _FakeBridge:
    """The bridge methods `SpectreSimulator` calls. Values rise with the staged design
    params, so the score varies with the design instead of staying constant."""

    def __init__(self, spec_names):
        self.spec_names = list(spec_names)
        self.calls = 0

    def run_simulation(self, netlist, params):
        self.calls += 1
        design = params.get("design_params") or {}
        knob = float(sum(design.values())) if design else 0.0
        data = {name: 1.0 + 0.1 * knob for name in self.spec_names}
        return type("FakeSimulationResult", (), {"data": data})()

    def submit(self, netlist, params):
        fut: Future = Future()
        fut.set_result(self.run_simulation(netlist, params))
        return fut


@pytest.fixture
def offline(monkeypatch, tmp_path):
    """Route the orchestrator's simulators to the fake bridge and every WORK_ROOT write
    (the default checkpoint dir) into tmp_path."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))

    def _fake_wrappers(self):
        p = self.project_setup
        p.parallel_sim = False
        spec_names = [t.name for t in p.optimizer_config.target_specs.enabled_targets()]
        bridge = _FakeBridge(spec_names)
        return {
            tb.name: SpectreSimulator(bridge, netlist=Path(p.ws_root) / Path(tb.netlist))
            for tb in p.testbenches
            if tb.enable
        }

    monkeypatch.setattr(
        Circuit_Optimizer_Orchestrator_with_SPICE, "create_spicelib_wrappers", _fake_wrappers
    )
    return tmp_path


@pytest.fixture
def cli(monkeypatch, tmp_path):
    """`main()` sets up process-global logging (handlers, levels, `propagate`, a stdout proxy)
    whose log file goes to `WORK_ROOT/logs/`: point WORK_ROOT at tmp_path/work, run from tmp_path
    and put the loggers back afterwards, so later tests (caplog) see the logging they expect."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    monkeypatch.chdir(tmp_path)
    names = ("spicexplorer", "spicelib", "std_redirect")
    saved = {
        n: (lg.level, lg.propagate, list(lg.handlers))
        for n in names
        for lg in [logging.getLogger(n)]
    }
    yield
    if hasattr(sys.stdout, "_original_stream"):  # the logger setup's stdout proxy
        sys.stdout = getattr(sys.stdout, "_original_stream")
    for n, (level, propagate, handlers) in saved.items():
        lg = logging.getLogger(n)
        for h in lg.handlers:
            if h not in handlers:
                h.close()
        lg.setLevel(level)
        lg.propagate = propagate
        lg.handlers[:] = handlers


@dataclass
class _Built:
    """What `run()` built: the orchestrator and its optimizer, captured by the `built` fixture."""

    orch: Any = None
    opt: Any = None
    # hooks run on (orch, opt) right after get_optimizer(), before parameterize()/optimize()
    tweaks: list[Callable[[Any, Any], None]] = field(default_factory=list)


@pytest.fixture
def built(monkeypatch) -> _Built:
    seen = _Built()
    real_get_optimizer = Circuit_Optimizer_Orchestrator_with_SPICE.get_optimizer

    def _get_optimizer(self):
        opt = real_get_optimizer(self)
        seen.orch, seen.opt = self, opt
        for tweak in seen.tweaks:
            tweak(self, opt)
        return opt

    monkeypatch.setattr(Circuit_Optimizer_Orchestrator_with_SPICE, "get_optimizer", _get_optimizer)
    return seen


def _enabled_spec_names() -> set[str]:
    from spicexplorer.core.domains import Project_Setup

    p = Project_Setup.from_yaml(EXAMPLE_YAML)
    return {t.name for t in p.optimizer_config.target_specs.enabled_targets()}


def _example_copy(dst: Path, *, outdir: Path, optimizer_yaml: str = "", budget: int = 2000) -> Path:
    """A copy of the example YAML whose `outdir:` points at `outdir` (so nothing lands in
    examples/), with its `optimizer_config:` budget set to `budget` and `optimizer_yaml` lines
    appended to that block."""
    text = EXAMPLE_YAML.read_text()
    anchors = (
        "ws_root : ..\n",
        "outdir  : spice/temp_spice_out\n",
        "    random_seed: 48\n",
        "    budget: 2000\n",
    )
    assert all(text.count(a) == 1 for a in anchors)
    text = (
        text.replace(anchors[0], f"ws_root : {EXAMPLE_YAML.parent.parent}\n")
        .replace(anchors[1], f"outdir  : {outdir}\n")
        .replace(anchors[2], anchors[2] + optimizer_yaml)
        .replace(anchors[3], f"    budget: {budget}\n")
    )
    dst.write_text(text)
    return dst


def _result(
    *,
    best_score: float = 1.5,
    best_metrics: dict[str, float] | None = None,
    best_knobs: dict[str, float] | None = None,
    stop_reason: str | None = None,
) -> OptimizeResult:
    return OptimizeResult(
        name="OTA",
        sim_engine="spectre",
        optimizer="NGOpt",
        budget=8,
        seed=None,
        outdir=Path("/runs/OTA_out"),
        checkpoint_dir=Path("/work/auto_save/OTA"),
        n_trials=8,
        best_score=best_score,
        best_knobs={"W": 2e-6} if best_knobs is None else best_knobs,
        best_metrics={"gain": 42.0} if best_metrics is None else best_metrics,
        stop_reason=stop_reason,
    )


# ------------------------------------------------------------------------------------------
# run() -> OptimizeResult
# ------------------------------------------------------------------------------------------
def test_run_returns_a_typed_result_with_the_overrides_applied(offline):
    yaml_before = EXAMPLE_YAML.read_text()
    starts: list[RunPlan] = []

    result = run(
        EXAMPLE_YAML,
        budget=4,
        seed=3,
        algo="TwoPointsDE",
        workers=1,
        outdir=offline / "out",
        verbose=False,
        on_start=starts.append,
    )

    assert isinstance(result, OptimizeResult)
    assert result.name == "CASCODE-OTA"
    assert result.sim_engine == "ngspice"
    assert (result.optimizer, result.budget, result.seed) == ("TwoPointsDE", 4, 3)
    assert result.n_trials == 4
    assert result.stop_reason is None
    # the outdir override is taken verbatim (no timestamp suffix); checkpoints land under WORK_ROOT
    assert result.outdir == offline / "out"
    assert result.checkpoint_dir.is_relative_to(offline / "work" / "auto_save")
    assert list(result.checkpoint_dir.glob("*_FINAL_*.json")), "the final checkpoint was written"
    # best point: physical knob values, a finite score, one metric per enabled spec
    assert result.best_knobs and all(type(v) is float for v in result.best_knobs.values())
    assert math.isfinite(result.best_score)
    assert set(result.best_metrics) == _enabled_spec_names()
    assert all(type(v) is float for v in result.best_metrics.values())
    # on_start saw the same plan before the loop ran
    assert len(starts) == 1 and starts[0].checkpoint_dir == result.checkpoint_dir
    assert starts[0].outdir == result.outdir and starts[0].budget == 4
    # the overrides apply to this run only: the YAML on disk is untouched
    assert EXAMPLE_YAML.read_text() == yaml_before

    payload = result.to_dict()
    json.dumps(payload, allow_nan=False)  # JSON-clean (paths as strings)
    assert payload["outdir"] == str(offline / "out") and payload["n_trials"] == 4


def test_run_timestamps_the_yaml_outdir_by_default(offline):
    yaml_copy = _example_copy(offline / "project_setup.yaml", outdir=offline / "yaml_out")

    result = run(yaml_copy, budget=2, algo="TwoPointsDE", verbose=False)
    assert re.fullmatch(r"yaml_out_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", result.outdir.name)
    kept = run(yaml_copy, budget=2, algo="TwoPointsDE", verbose=False, timestamp_outdir=False)
    assert kept.outdir == offline / "yaml_out"


def test_run_without_overrides_runs_the_yaml_optimizer_config(offline):
    # as before run() existed: with no flags the YAML's optimizer_config decides the run
    yaml_copy = _example_copy(offline / "project_setup.yaml", outdir=offline / "yaml_out", budget=3)
    result = run(yaml_copy, verbose=False, timestamp_outdir=False)
    assert (result.optimizer, result.budget, result.seed) == ("LogBFGSCMAPlus", 3, 48)
    assert result.n_trials == 3
    assert result.outdir == offline / "yaml_out"


def test_run_raises_when_no_trial_completes(offline, monkeypatch):
    def _interrupted(self):
        raise KeyboardInterrupt  # optimize() swallows it: the loop ends with zero trials

    monkeypatch.setattr(Nevergrad_Spice_Single_Objective, "optimization_step", _interrupted)
    with pytest.raises(NoTrialCompleted) as exc:
        run(EXAMPLE_YAML, budget=3, algo="TwoPointsDE", outdir=offline / "out", verbose=False)
    assert isinstance(exc.value, RuntimeError)
    assert str(exc.value) == "CASCODE-OTA: no trial completed"
    assert exc.value.outdir == offline / "out"
    assert exc.value.checkpoint_dir.is_relative_to(offline / "work" / "auto_save")


@pytest.mark.parametrize("budget, every", [(10, 3), (4, 2)], ids=["tail-chunk", "on-boundary"])
def test_run_counts_every_trial_across_autosave_chunks(offline, built, monkeypatch, budget, every):
    # The optimizer empties its in-memory log on every autosave, so `optimization_log` holds
    # only the last chunk (and nothing at all when the run ends on a boundary): n_trials must
    # come from the whole run. trial10 < trial3 < trial6 < trial9 by NAME, so the summary of
    # the (10, 3) run also checks the chunks are read in trial order.
    trials: list[dict[str, float]] = []
    real_step = Nevergrad_Spice_Single_Objective.optimization_step

    def _recorded(self):
        out = real_step(self)
        trials.append(dict(self.optimization_log[-1].point.params))  # before any autosave reset
        return out

    monkeypatch.setattr(Nevergrad_Spice_Single_Objective, "optimization_step", _recorded)
    built.tweaks.append(lambda orch, opt: setattr(opt, "autosave_checkpoint_freqeucny", every))

    result = run(
        EXAMPLE_YAML, budget=budget, algo="TwoPointsDE", outdir=offline / "out", verbose=False
    )

    assert len(trials) == budget
    assert result.n_trials == budget
    assert len(built.opt.optimization_log) == budget % every  # only the unsaved tail is in memory
    n_chunks = budget // every + (1 if budget % every else 0)
    assert len(list(result.checkpoint_dir.glob("*.json"))) == n_chunks

    s = summarize_checkpoint(result.checkpoint_dir, top=budget)
    assert s.n_trials == budget and len(s.best_score_trace) == budget
    assert s.best_score_trace[-1] == pytest.approx(result.best_score)
    assert [t.params for t in sorted(s.top, key=lambda t: t.trial)] == trials


def test_run_reports_why_a_guard_ended_the_run_early(offline, built):
    # the per-trial time guard is read at optimize() time; 1 ns trips it on the first trial
    built.tweaks.append(lambda orch, opt: setattr(opt.optimizer_config, "trial_time_stop_s", 1e-9))

    result = run(EXAMPLE_YAML, budget=5, algo="TwoPointsDE", outdir=offline / "out", verbose=False)

    assert result.stop_reason is not None
    assert result.stop_reason.startswith("stopped by the per-trial time guard at trial 1/5")
    assert result.stop_reason == built.opt.stop_reason
    # the plan's budget, but only the trials that actually ran
    assert (result.budget, result.n_trials) == (5, 1)
    assert math.isfinite(result.best_score) and result.best_knobs
    assert result.to_dict()["stop_reason"] == result.stop_reason


def test_run_merges_workers_into_the_yaml_optimizer_kwargs(offline, built):
    # `batch_size` is an Ax knob Nevergrad drops, so a YAML may carry it harmlessly
    yaml_copy = _example_copy(
        offline / "project_setup.yaml",
        outdir=offline / "yaml_out",
        optimizer_yaml="    optimizer_kwargs:\n      batch_size: 3\n",
    )

    run(yaml_copy, budget=2, algo="TwoPointsDE", workers=2, outdir=offline / "o1", verbose=False)
    assert built.orch.project_setup.optimizer_config.optimizer_kwargs == {
        "batch_size": 3,
        "num_workers": 2,
    }
    assert built.opt.optimizer.num_workers == 2, "the override reached Nevergrad"

    run(yaml_copy, budget=2, algo="TwoPointsDE", outdir=offline / "o2", verbose=False)
    assert built.orch.project_setup.optimizer_config.optimizer_kwargs == {"batch_size": 3}
    assert built.opt.optimizer.num_workers == 1


def test_run_expands_a_home_relative_outdir(offline, monkeypatch):
    monkeypatch.setenv("HOME", str(offline / "home"))
    result = run(EXAMPLE_YAML, budget=2, algo="TwoPointsDE", outdir="~/sized", verbose=False)
    assert result.outdir == offline / "home" / "sized"


def _best_entry_replaced(monkeypatch, make_entry: Callable[[Any], Any]) -> None:
    """After the real loop, swap the optimizer's global best entry for `make_entry(best)`."""
    real_optimize = Nevergrad_Spice_Single_Objective.optimize

    def _optimize(self, *a, **k):
        out = real_optimize(self, *a, **k)
        self.global_best_entry = make_entry(self.global_best_entry)
        return out

    monkeypatch.setattr(Nevergrad_Spice_Single_Objective, "optimize", _optimize)


def test_run_reads_each_specs_measured_value_from_the_best_fit_summary(offline, monkeypatch):
    fit_summary: dict[str, Any] = {
        "gain": {"curr_val": 42.0, "score": -1.0},  # the reading, not the spec score
        "tt_27C::pm": {"curr_val": np.float64(61.5), "score": 0.0},  # corner key, numpy scalar
        "bode_loss": 0.25,  # the Bode fitter logs bare scalars
        "ugf": {"curr_val": "n/a", "score": -5.0},  # a non-numeric reading
        "noise": {"score": -2.0},  # an unmeasured spec
        "tsettle": {"curr_val": None, "score": -3.0},
    }
    best_point: list[Any] = []

    def _entry_with_summary(best):
        best_point.append(best.point)
        return OptimizationLogEntry(point=best.point, fit_summary=fit_summary)

    _best_entry_replaced(monkeypatch, _entry_with_summary)
    result = run(EXAMPLE_YAML, budget=2, algo="TwoPointsDE", outdir=offline / "out", verbose=False)

    assert list(result.best_metrics) == list(fit_summary)
    assert all(type(v) is float for v in result.best_metrics.values())
    assert {k: v for k, v in result.best_metrics.items() if math.isfinite(v)} == {
        "gain": 42.0,
        "tt_27C::pm": 61.5,
        "bode_loss": 0.25,
    }
    assert all(math.isnan(result.best_metrics[k]) for k in ("ugf", "noise", "tsettle"))
    assert result.to_dict()["best_metrics"] == {
        "gain": 42.0,
        "tt_27C::pm": 61.5,
        "bode_loss": 0.25,
        "ugf": None,
        "noise": None,
        "tsettle": None,
    }
    # knobs and score come from the same best entry
    assert result.best_knobs == {k: float(v) for k, v in best_point[0].params.items()}
    assert result.best_score == float(best_point[0].score)


@pytest.mark.parametrize("state", ["fit_summary-null", "no-best-entry-no-monitor"])
def test_run_tolerates_an_optimizer_without_best_entry_details(offline, monkeypatch, state):
    # A backend that logs no fit_summary, or tracks neither the global best entry nor the
    # trial-time monitor: run() still returns (no metrics; n_trials from the in-memory log).
    def _degrade(best):
        if state == "fit_summary-null":
            return OptimizationLogEntry(point=best.point, fit_summary=None)
        return None

    _best_entry_replaced(monkeypatch, _degrade)
    if state == "no-best-entry-no-monitor":
        real_optimize = Nevergrad_Spice_Single_Objective.optimize

        def _no_monitor(self, *a, **k):
            out = real_optimize(self, *a, **k)
            self.trial_time_monitor = None
            return out

        monkeypatch.setattr(Nevergrad_Spice_Single_Objective, "optimize", _no_monitor)

    result = run(EXAMPLE_YAML, budget=3, algo="TwoPointsDE", outdir=offline / "out", verbose=False)
    assert result.best_metrics == {}
    assert result.n_trials == 3
    assert math.isfinite(result.best_score) and result.best_knobs


# ------------------------------------------------------------------------------------------
# OptimizeResult / RunPlan / NoTrialCompleted
# ------------------------------------------------------------------------------------------
def test_optimize_result_to_dict_scrubs_non_finite_readings_to_none():
    r = _result(
        best_score=float("inf"),
        best_metrics={"gain": 42.0, "pm": float("nan"), "ugf": float("-inf")},
    )
    d = r.to_dict()
    assert d["best_score"] is None
    assert d["best_metrics"] == {"gain": 42.0, "pm": None, "ugf": None}
    json.dumps(d, allow_nan=False)
    # only the payload is scrubbed: the result keeps its readings
    assert r.best_score == float("inf") and math.isnan(r.best_metrics["pm"])


def test_optimize_result_to_dict_is_the_full_json_ready_record():
    assert _result(stop_reason="stopped early").to_dict() == {
        "name": "OTA",
        "sim_engine": "spectre",
        "optimizer": "NGOpt",
        "budget": 8,
        "seed": None,
        "outdir": "/runs/OTA_out",
        "checkpoint_dir": "/work/auto_save/OTA",
        "n_trials": 8,
        "best_score": 1.5,
        "best_knobs": {"W": 2e-6},
        "best_metrics": {"gain": 42.0},
        "stop_reason": "stopped early",
    }
    assert _result().stop_reason is None  # the default: a run that spent its budget


def test_run_plan_is_the_frozen_prefix_of_the_result():
    r = _result()
    assert isinstance(r, RunPlan)
    plan_fields = [f.name for f in fields(RunPlan)]
    assert list(r.to_dict())[: len(plan_fields)] == plan_fields
    plan = RunPlan(**{f: getattr(r, f) for f in plan_fields})
    assert plan.to_dict() == {k: v for k, v in r.to_dict().items() if k in plan_fields}
    json.dumps(plan.to_dict(), allow_nan=False)
    with pytest.raises(FrozenInstanceError):
        setattr(r, "best_score", 0.0)
    with pytest.raises(FrozenInstanceError):
        setattr(plan, "outdir", Path("/elsewhere"))


def test_no_trial_completed_carries_the_run_dirs():
    err = NoTrialCompleted("OTA: no trial completed", outdir=Path("/o"), checkpoint_dir=Path("/c"))
    assert isinstance(err, RuntimeError) and str(err) == "OTA: no trial completed"
    assert (err.outdir, err.checkpoint_dir) == (Path("/o"), Path("/c"))


# ------------------------------------------------------------------------------------------
# main(): the unchanged CLI over run()
# ------------------------------------------------------------------------------------------
def test_main_prints_the_cli_lines_around_the_run(offline, cli, monkeypatch, capsys):
    real_optimize = Nevergrad_Spice_Single_Objective.optimize

    def _marked_optimize(self, *a, **k):
        print("<<optimize>>", flush=True)
        return real_optimize(self, *a, **k)

    monkeypatch.setattr(Nevergrad_Spice_Single_Objective, "optimize", _marked_optimize)
    out_dir = offline / "out"
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "3",
            "--seed",
            "5",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(out_dir),
            "--quiet",
        ]
    )
    assert rc == 0

    lines = [
        ln
        for ln in capsys.readouterr().out.splitlines()
        if ln.startswith(PREFIX) or ln == "<<optimize>>"
    ]
    assert len(lines) == 7, lines
    head, marker, tail = lines[:3], lines[3], lines[4:]
    assert head[0] == f"{PREFIX} CASCODE-OTA: engine=ngspice optimizer=TwoPointsDE budget=3"
    assert head[1] == f"{PREFIX} artifacts: {out_dir}"
    assert head[2].startswith(f"{PREFIX} checkpoints: {offline / 'work' / 'auto_save'}")
    assert marker == "<<optimize>>", "the start lines print BEFORE the optimization loop"
    assert re.fullmatch(rf"{re.escape(PREFIX)} best score \S+", tail[0])
    knobs = json.loads(tail[1].removeprefix(f"{PREFIX} best knobs: "))
    assert knobs and all(isinstance(v, float) for v in knobs.values())
    metrics = json.loads(tail[2].removeprefix(f"{PREFIX} best metrics: "))
    assert set(metrics) == _enabled_spec_names()


def test_main_exits_1_when_no_trial_completes(offline, cli, monkeypatch, capsys):
    def _interrupted(self):
        raise KeyboardInterrupt

    monkeypatch.setattr(Nevergrad_Spice_Single_Objective, "optimization_step", _interrupted)
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "2",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(offline / "out"),
            "--quiet",
        ]
    )
    assert rc == 1
    captured = capsys.readouterr()
    assert f"{PREFIX} no trial completed" in captured.err
    assert "best score" not in captured.out


def _spy_run(monkeypatch, result: OptimizeResult) -> list[tuple[Any, dict[str, Any]]]:
    """Replace `run_project.run` (what main() calls) with a recorder returning `result`."""
    calls: list[tuple[Any, dict[str, Any]]] = []

    def _run(project_setup, **kwargs):
        calls.append((project_setup, kwargs))
        return result

    monkeypatch.setattr(run_project, "run", _run)
    return calls


@pytest.mark.parametrize(
    "flags, expected",
    [
        (
            [
                "--budget",
                "7",
                "--seed",
                "11",
                "--algo",
                "NGOpt",
                "--workers",
                "3",
                "--outdir",
                "~/sized",
                "--no-timestamp",
                "--quiet",
            ],
            dict(
                budget=7,
                seed=11,
                algo="NGOpt",
                workers=3,
                outdir="~/sized",
                timestamp_outdir=False,
                verbose=False,
                engine=None,
                resume=None,
                checkpoint_dir=None,
                report=None,
            ),
        ),
        (
            [],
            dict(
                budget=None,
                seed=None,
                algo=None,
                workers=None,
                outdir=None,
                timestamp_outdir=True,
                verbose=True,
                engine=None,
                resume=None,
                checkpoint_dir=None,
                report=None,
            ),
        ),
    ],
    ids=["every-flag", "no-flags"],
)
def test_main_forwards_every_flag_to_run(cli, monkeypatch, flags, expected):
    calls = _spy_run(monkeypatch, _result())
    assert main([str(EXAMPLE_YAML), *flags]) == 0

    [(project_setup, kwargs)] = calls
    assert project_setup == EXAMPLE_YAML
    assert kwargs.pop("on_start") is run_project._print_start
    assert kwargs == expected
    if "--quiet" in flags:
        assert logging.getLogger("spicexplorer").level == logging.WARNING


def test_the_cli_fixture_keeps_main_s_log_file_under_tmp_path(cli, monkeypatch, tmp_path):
    """main() opens a log file under WORK_ROOT/logs; without WORK_ROOT that is the checkout's
    work/logs, so every test using `cli` left a SpiceXplorer_*.log there (L-PF-13)."""
    _spy_run(monkeypatch, _result())
    assert main([str(EXAMPLE_YAML), "--quiet"]) == 0
    assert sorted((tmp_path / "work" / "logs").glob("SpiceXplorer_*.log"))


@pytest.mark.parametrize(
    "metrics, metrics_line",
    [
        ({}, None),  # no metrics line at all, not an empty dict
        ({"gain": 42.0, "pm": float("nan")}, '{"gain": 42.0, "pm": NaN}'),  # an unmeasured spec
    ],
    ids=["no-metrics", "nan-metric"],
)
def test_main_prints_the_result_lines(cli, monkeypatch, capsys, metrics, metrics_line):
    _spy_run(
        monkeypatch,
        _result(best_score=1.23456789, best_metrics=metrics, best_knobs={"W": 2e-6, "L": 1.5e-7}),
    )
    assert main([str(EXAMPLE_YAML)]) == 0

    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.startswith(PREFIX)]
    expected = [
        f"{PREFIX} best score 1.23457",
        f'{PREFIX} best knobs: {{"W": 2e-06, "L": 1.5e-07}}',
    ]
    if metrics_line is not None:
        expected.append(f"{PREFIX} best metrics: {metrics_line}")
    assert lines == expected


# ------------------------------------------------------------------------------------------
# summarize_checkpoint
# ------------------------------------------------------------------------------------------
def _entry(params, score, fit_summary, log_file=None):
    return {
        "point": {"params": params, "score": score, "metadata": {}},
        "fit_summary": fit_summary,
        "log_file": log_file,
    }


def _write_checkpoint(path: Path, entries, version: Any = "1.0.0") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": version, "timestamp": "x", "optimization_log": entries})
    )
    return path


def test_summarize_checkpoint_on_a_synthetic_json(tmp_path):
    ckpt = _write_checkpoint(
        tmp_path / "ckpt.json",
        [
            _entry(
                {"W1": 2.0, "L1": 0.5},
                -3.0,
                {"gain": {"curr_val": 40.0, "score": -3.0}, "pm": {"curr_val": 70.0, "score": 0.0}},
                log_file={"tb_ac": "/abs/run/tb_ac.log"},
            ),
            # a LEGACY checkpoint stored log_file as the repr of the whole dict
            _entry(
                {"W1": 8.0, "L1": 0.2},
                5.0,
                {"gain": {"curr_val": 62.0, "score": 2.5}, "pm": {"curr_val": 61.0, "score": 2.5}},
                log_file="{'tb_ac': PosixPath('/abs/run/tb_ac.log')}",
            ),
            _entry(
                {"W1": 4.0, "L1": 1.0},
                1.0,
                {"gain": {"curr_val": float("nan"), "score": -1e6}, "pm": {"curr_val": 65.0}},
            ),
        ],
    )

    s = summarize_checkpoint(ckpt, top=2)

    assert isinstance(s, CheckpointSummary)
    assert s.schema_version == "1.0.0" and s.n_trials == 3
    assert s.best_score_trace == [-3.0, 5.0, 5.0]  # monotone best-so-far
    assert [t.trial for t in s.top] == [1, 2] and [t.score for t in s.top] == [5.0, 1.0]
    best, second = s.top
    assert best.params == {"W1": 8.0, "L1": 0.2}
    assert best.metrics == {"gain": 62.0, "pm": 61.0}
    assert best.passed == {"gain": True, "pm": True}
    # NaN curr_val -> None; a spec with no recorded score has no verdict (None, not False)
    assert second.metrics == {"gain": None, "pm": 65.0}
    assert second.passed == {"gain": False, "pm": None}
    assert s.knob_ranges == {"W1": (2.0, 8.0), "L1": (0.2, 1.0)}

    payload = s.to_dict()
    text = json.dumps(payload, allow_nan=False)
    assert "log_file" not in text and "/" not in text, "no log paths leak into the payload"


def test_summarize_checkpoint_top_zero_and_bad_input(tmp_path):
    ckpt = _write_checkpoint(tmp_path / "c.json", [_entry({"x": 1.0}, 0.5, {})])
    s = summarize_checkpoint(ckpt, top=0)
    assert s.top == [] and s.n_trials == 1 and s.best_score_trace == [0.5]
    with pytest.raises(ValueError):
        summarize_checkpoint(ckpt, top=-1)
    not_a_ckpt = tmp_path / "other.json"
    not_a_ckpt.write_text(json.dumps({"timings": []}))
    with pytest.raises(ValueError):
        summarize_checkpoint(not_a_ckpt)


def test_summarize_checkpoint_reads_a_run_dir_as_its_chunks_in_trial_order(tmp_path):
    # The optimizer empties its in-memory log after each autosave, so a long run's trials are
    # split across `<name>_<algo>_<budget>_trial<N>[_FINAL]_<ts>.json` files in its checkpoint dir.
    d = tmp_path / "ckpts"
    _write_checkpoint(
        d / "OTA_NGOpt_25_trial25_FINAL_2026-01-01_00-00-09.json", [_entry({"x": 9.0}, 9.0, {})]
    )
    _write_checkpoint(
        d / "OTA_NGOpt_25_trial10_2026-01-01_00-00-01.json",
        [_entry({"x": 1.0}, 1.0, {}), _entry({"x": 2.0}, -2.0, {})],
    )
    _write_checkpoint(
        d / "OTA_NGOpt_25_trial20_2026-01-01_00-00-05.json", [_entry({"x": 3.0}, 3.0, {})]
    )
    (d / "sim_time_report.json").write_text(json.dumps({"timings": []}))  # not a checkpoint

    s = summarize_checkpoint(d, top=1)
    assert s.n_trials == 4
    assert s.best_score_trace == [1.0, 1.0, 3.0, 9.0]
    assert s.top[0].trial == 3 and s.top[0].params == {"x": 9.0}
    with pytest.raises(FileNotFoundError, match="no checkpoint at"):
        summarize_checkpoint(tmp_path / "no_such_path")


def test_summarize_checkpoint_skips_and_names_an_unreadable_file_in_a_run_dir(tmp_path):
    """One corrupt *.json in a run's checkpoint dir (not UTF-8, or torn mid-write) refused the
    whole dir with a UnicodeDecodeError (L-PF-35). It is skipped and named, by file name only, in
    `skipped`, and the readable chunks are summarized. A lone unreadable file is still refused."""
    d = tmp_path / "ckpts"
    _write_checkpoint(
        d / "OTA_NGOpt_5_trial2_2026-01-01_00-00-01.json",
        [_entry({"x": 1.0}, 1.0, {}), _entry({"x": 2.0}, 2.0, {})],
    )
    binary = d / "OTA_NGOpt_5_trial4_2026-01-01_00-00-02.json"
    binary.write_bytes(b"\xff\xfe{ not utf-8")
    torn = d / "OTA_NGOpt_5_trial5_FINAL_2026-01-01_00-00-03.json"
    torn.write_text('{"optimization_log": [')

    s = summarize_checkpoint(d)
    assert s.n_trials == 2 and s.best_score_trace == [1.0, 2.0]
    assert sorted(s.skipped) == [binary.name, torn.name]
    assert s.skipped[binary.name].startswith("UnicodeDecodeError")
    assert s.skipped[torn.name].startswith("JSONDecodeError")
    assert str(tmp_path) not in json.dumps(s.to_dict())
    with pytest.raises(ValueError):
        summarize_checkpoint(binary)


def test_summarize_checkpoint_reads_what_run_wrote(offline):
    result = run(EXAMPLE_YAML, budget=4, algo="TwoPointsDE", outdir=offline / "out", verbose=False)
    s = summarize_checkpoint(result.checkpoint_dir, top=2)
    assert s.n_trials == result.n_trials == 4
    assert s.top[0].score == pytest.approx(result.best_score)
    assert s.top[0].params == pytest.approx(result.best_knobs)
    assert s.best_score_trace[-1] == pytest.approx(result.best_score)
    # the same curr_val readings, read from the checkpoint JSON instead of the live entry
    assert s.top[0].metrics == pytest.approx(result.best_metrics)


def test_summarize_checkpoint_verdict_is_the_scorers_epsilon_threshold(tmp_path):
    # passed = spec score > -EPSILON, strictly: the scorer's feasibility band, not `>= 0`
    eps = float(EPSILON)
    specs = {"met": 0.0, "over": 3.0, "within_eps": -eps / 2, "at_eps": -eps, "beyond": -2 * eps}
    ckpt = _write_checkpoint(
        tmp_path / "c.json",
        [_entry({"x": 1.0}, 0.0, {k: {"curr_val": 1.0, "score": v} for k, v in specs.items()})],
    )

    [trial] = summarize_checkpoint(ckpt).top
    assert trial.passed == {
        "met": True,
        "over": True,
        "within_eps": True,
        "at_eps": False,
        "beyond": False,
    }


def test_summarize_checkpoint_bare_scalar_specs_carry_a_value_but_no_verdict(tmp_path):
    # the Bode fitter logs each spec as a bare loss, not a {"curr_val", "score"} dict
    ckpt = _write_checkpoint(
        tmp_path / "c.json",
        [_entry({"x": 1.0}, -0.3, {"bode_loss": 0.25, "phase_loss": float("nan"), "gain": 7})],
    )

    [trial] = summarize_checkpoint(ckpt).top
    assert trial.metrics == {"bode_loss": 0.25, "phase_loss": None, "gain": 7.0}
    assert trial.passed == {"bode_loss": None, "phase_loss": None, "gain": None}


def test_summarize_checkpoint_ranks_unscored_trials_last_and_ties_in_trial_order(tmp_path):
    ckpt = _write_checkpoint(
        tmp_path / "c.json",
        [
            _entry({"x": 0.0}, -5.0, {}),  # 0: scored, but worse than an unscored "0"
            _entry({"x": 1.0}, None, {}),  # 1: unscored
            _entry({"x": 2.0}, 2.0, {}),  # 2: best, tied ...
            _entry({"x": 3.0}, "high", {}),  # 3: a non-numeric score is unscored
            _entry({"x": 4.0}, 2.0, {}),  # 4: ... with this later trial
            _entry({"x": True, "y": "wide"}, True, {}),  # 5: a bool is not a number
        ],
    )

    s = summarize_checkpoint(ckpt, top=6)
    assert [t.trial for t in s.top] == [2, 4, 0, 1, 3, 5]
    assert [t.score for t in s.top] == [2.0, 2.0, -5.0, None, None, None]
    assert s.best_score_trace == [-5.0, -5.0, 2.0, 2.0, 2.0, 2.0]
    assert s.top[-1].params == {"x": None, "y": None}
    assert s.knob_ranges == {"x": (0.0, 4.0)}, "unreadable knob values do not widen the range"


def test_summarize_checkpoint_skips_malformed_entries(tmp_path):
    ckpt = tmp_path / "legacy.json"
    ckpt.write_text(
        json.dumps(
            {
                "optimization_log": [  # no schema_version at all
                    None,
                    "trial 3",
                    7,  # not entries: skipped
                    {"fit_summary": {"gain": {"curr_val": 1.0}}},  # no point
                    {"point": None, "fit_summary": None},
                    {
                        "point": {"params": [1, 2], "score": 0.5},
                        "fit_summary": ["gain"],
                    },  # wrong shapes
                    _entry({"x": 1.0}, 0.75, {"gain": {"curr_val": 3.0, "score": 1.0}}),
                ]
            }
        )
    )

    s = summarize_checkpoint(str(ckpt))  # a str path works too
    assert s.schema_version is None
    assert s.n_trials == 4
    assert [t.trial for t in s.top] == [3, 2, 0, 1]
    assert [t.score for t in s.top] == [0.75, 0.5, None, None]
    no_point = s.top[2]
    assert (no_point.params, no_point.metrics, no_point.passed) == (
        {},
        {"gain": 1.0},
        {"gain": None},
    )
    assert s.top[1].params == {} and s.top[1].metrics == {}
    assert s.knob_ranges == {"x": (1.0, 1.0)}
    json.dumps(s.to_dict(), allow_nan=False)


def test_summarize_checkpoint_defaults_to_the_top_five(tmp_path):
    ckpt = _write_checkpoint(
        tmp_path / "c.json", [_entry({"x": float(i)}, float(i), {}) for i in range(7)], version=2
    )
    s = summarize_checkpoint(ckpt)
    assert [t.trial for t in s.top] == [6, 5, 4, 3, 2]
    assert s.n_trials == 7
    assert s.schema_version == "2"  # reported as read, as a string; a mismatch does not raise


def test_summarize_checkpoint_orders_chunks_by_trial_number_not_file_name(tmp_path):
    # by NAME trial10 < trial12_FINAL < trial9, and the equal timestamps do not help
    d = tmp_path / "ckpts"
    _write_checkpoint(
        d / "OTA_NGOpt_12_trial10_2026-01-01_00-00-00.json", [_entry({"x": 10.0}, 5.0, {})]
    )
    _write_checkpoint(
        d / "OTA_NGOpt_12_trial12_FINAL_2026-01-01_00-00-00.json", [_entry({"x": 12.0}, 3.0, {})]
    )
    _write_checkpoint(
        d / "OTA_NGOpt_12_trial9_2026-01-01_00-00-00.json", [_entry({"x": 9.0}, 1.0, {})]
    )

    s = summarize_checkpoint(d, top=3)
    assert s.best_score_trace == [1.0, 5.0, 5.0]
    assert [(t.trial, t.params["x"]) for t in s.top] == [(1, 10.0), (2, 12.0), (0, 9.0)]


def test_summarize_checkpoint_rejects_what_is_not_a_checkpoint(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(FileNotFoundError, match="no checkpoint JSON in"):
        summarize_checkpoint(empty)
    only_reports = tmp_path / "reports"
    only_reports.mkdir()
    (only_reports / "sim_time_report.json").write_text(json.dumps({"timings": []}))
    (only_reports / "notes.txt").write_text("not json")
    with pytest.raises(FileNotFoundError, match="no checkpoint JSON in"):
        summarize_checkpoint(only_reports)

    for name, text in [
        ("list.json", "[1, 2]"),
        ("log_not_a_list.json", '{"optimization_log": {}}'),
        ("torn.json", '{"optimization_log": ['),
    ]:
        (tmp_path / name).write_text(text)
        with pytest.raises(ValueError):
            summarize_checkpoint(tmp_path / name)


# ------------------------------------------------------------------------------------------
# Design repos parse the three `best …` lines with a regex (an LDO sizing experiment's
# run_opt.py reads score / knobs / metrics back into a JSON file). These tests use that
# consumer's OWN regex and value parser, so a reworded prefix, a dropped colon or a non-JSON
# payload fails here instead of leaving a design's best.json empty with no error.
# ------------------------------------------------------------------------------------------
_DESIGN_SIDE = re.compile(r"\[spicexplorer-optimize\] best (score|knobs|metrics):? (.*)$")


def _design_side_parse(out: str) -> dict[str, Any]:
    best: dict[str, Any] = {}
    for ln in out.splitlines():
        m = _DESIGN_SIDE.match(ln.strip())
        if m:
            best[m.group(1)] = (
                json.loads(m.group(2)) if m.group(2).startswith("{") else float(m.group(2))
            )
    return best


def test_the_best_lines_parse_with_the_design_side_regex(offline, cli, capsys):
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "3",
            "--seed",
            "5",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(offline / "out"),
            "--quiet",
        ]
    )
    assert rc == 0
    best = _design_side_parse(capsys.readouterr().out)
    assert set(best) == {"score", "knobs", "metrics"}
    assert isinstance(best["score"], float) and math.isfinite(best["score"])
    assert best["knobs"] and all(isinstance(v, float) for v in best["knobs"].values())
    assert set(best["metrics"]) == _enabled_spec_names()


@pytest.mark.parametrize("score", [-0.81, 0.0, 1e-9, float("inf"), float("nan")])
def test_every_printed_score_is_one_the_design_side_float_parse_accepts(
    cli, monkeypatch, capsys, score
):
    """`.6g` of a non-finite score prints `inf` / `nan`, which float() still reads; the knobs and
    metrics payloads stay JSON objects (they start with `{`, the consumer's switch)."""
    result = _result(best_score=score, best_knobs={"w": 1e-6}, best_metrics={"gain_db": 40.0})
    _spy_run(monkeypatch, result)
    assert main([str(EXAMPLE_YAML), "--quiet"]) == 0
    best = _design_side_parse(capsys.readouterr().out)
    assert set(best) == {"score", "knobs", "metrics"}
    assert (math.isnan(best["score"]) and math.isnan(score)) or best["score"] == pytest.approx(
        score, rel=1e-5
    )
    assert best["knobs"] == {"w": 1e-6} and best["metrics"] == {"gain_db": 40.0}


def test_every_test_that_calls_main_runs_it_through_the_cli_fixture():
    """`main()` writes `./logs/` and changes process-wide logging. A test that calls it without the
    `cli` fixture writes a log file into the checkout and leaves a file handler open on the
    `spicexplorer` logger, which later tests on the same worker then write into."""
    tree = ast.parse(Path(__file__).read_text())
    missing = [
        f.name
        for f in tree.body
        if isinstance(f, ast.FunctionDef)
        and f.name.startswith("test_")
        and any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "main"
            for n in ast.walk(f)
        )
        and "cli" not in [a.arg for a in f.args.args]
    ]
    assert missing == []
