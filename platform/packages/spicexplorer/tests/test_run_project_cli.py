"""`spicexplorer-optimize` flags beyond the run overrides (OPT-F7): `--engine`, `--resume`,
`--checkpoint-dir`, `--report`, and a clean exit 2 on a bad project path.

`test_run_contract.py` covers `run()` -> `OptimizeResult` and the printed lines; this module covers
the flags built on top of it. The stdout contract (the three `best …` lines a design's run script
parses with a regex) is pinned again here with every new flag given.

OFFLINE: the orchestrator's simulators are the fake Spectre bridge of `test_run_contract.py`, so a
real Nevergrad loop runs with no ngspice binary, no PDK and no Cadence. The engine-switch tests
register a Nevergrad stand-in under the Ax slot, so they need no extra; the one `ax`-marked resume
test runs the real Ax client (`uv sync --extra ax`, `-m ax`).
"""

from __future__ import annotations

import json
import logging
import math
import re
import sys
from concurrent.futures import Future
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import spicexplorer.optimization.run_project as run_project
from _spicexplorer_fixtures import EXAMPLE_YAML
from spicexplorer.backends.spectre import SpectreSimulator
from spicexplorer.core.domains import OptimizerType, Project_Setup
from spicexplorer.core.utils import EPSILON
from spicexplorer.optimization import (
    SPICE_OPTIMIZER_CLASSES,
    Circuit_Optimizer_Orchestrator_with_SPICE,
    Optimizer_Type_Enum,
    summarize_checkpoint,
)
from spicexplorer.optimization.result import OptimizeResult
from spicexplorer.optimization.run_project import ResumeError, main, run
from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

PREFIX = "[spicexplorer-optimize]"


class _FakeBridge:
    """The bridge methods `SpectreSimulator` calls; values rise with the staged design params."""

    def __init__(self, spec_names):
        self.spec_names = list(spec_names)

    def run_simulation(self, netlist, params):
        design = params.get("design_params") or {}
        knob = float(sum(design.values())) if design else 0.0
        data = {name: 1.0 + 0.1 * knob for name in self.spec_names}
        return type("FakeSimulationResult", (), {"data": data})()

    def submit(self, netlist, params):
        fut: Future = Future()
        fut.set_result(self.run_simulation(netlist, params))
        return fut


@dataclass
class _Offline:
    root: Path
    wrapper_builds: int = 0  # orchestrator.initialize() calls: 0 means no simulator was built


@pytest.fixture
def offline(monkeypatch, tmp_path) -> _Offline:
    """Route the orchestrator's simulators to the fake bridge and WORK_ROOT into tmp_path."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "work"))
    state = _Offline(root=tmp_path)

    def _fake_wrappers(self):
        state.wrapper_builds += 1
        p = self.project_setup
        p.parallel_sim = False
        bridge = _FakeBridge([t.name for t in p.optimizer_config.target_specs.enabled_targets()])
        return {
            tb.name: SpectreSimulator(bridge, netlist=Path(p.ws_root) / Path(tb.netlist))
            for tb in p.testbenches
            if tb.enable
        }

    monkeypatch.setattr(
        Circuit_Optimizer_Orchestrator_with_SPICE, "create_spicelib_wrappers", _fake_wrappers
    )
    return state


@pytest.fixture
def cli(monkeypatch, tmp_path):
    """`main()` sets up process-global logging, whose log file goes to `WORK_ROOT/logs/`: point
    WORK_ROOT at tmp_path/work, run from tmp_path and put the loggers back afterwards (the `cli`
    fixture of `test_run_contract.py`)."""
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
    orch: Any = None
    opt: Any = None
    autosave_every: int | None = None  # set: every optimizer built autosaves a chunk this often


@pytest.fixture
def built(monkeypatch) -> _Built:
    """The orchestrator and optimizer `run()` built (the last ones, when it runs twice)."""
    seen = _Built()
    real_get_optimizer = Circuit_Optimizer_Orchestrator_with_SPICE.get_optimizer

    def _get_optimizer(self):
        opt = real_get_optimizer(self)
        if seen.autosave_every is not None:
            opt.autosave_checkpoint_freqeucny = seen.autosave_every
        seen.orch, seen.opt = self, opt
        return opt

    monkeypatch.setattr(Circuit_Optimizer_Orchestrator_with_SPICE, "get_optimizer", _get_optimizer)
    return seen


@dataclass
class _Steps:
    """Counts optimizer steps; the step numbered `crash_at` (1-based) raises like a backend error."""

    n: int = 0
    crash_at: int | None = None


@pytest.fixture
def steps(monkeypatch) -> _Steps:
    s = _Steps()
    real_step = Nevergrad_Spice_Single_Objective.optimization_step

    def _step(self):
        s.n += 1
        if s.crash_at is not None and s.n == s.crash_at:
            raise RuntimeError("backend died")
        return real_step(self)

    monkeypatch.setattr(Nevergrad_Spice_Single_Objective, "optimization_step", _step)
    return s


class _AxStandIn(Nevergrad_Spice_Single_Objective):
    """Registered under the Ax slot: the Ax extra is not installed in this environment."""


def _example_copy(
    dst: Path, *, outdir: Path, engine: str = "nevergrad", multi: bool = False
) -> Path:
    """A copy of the example YAML with `outdir:` at `outdir`, `optimizer_config.type: <engine>`
    and, with `multi`, `pvt.mode: multi` (tt + ss enabled, ff disabled)."""
    text = EXAMPLE_YAML.read_text()
    anchors = (
        "ws_root : ..\n",
        "outdir  : spice/temp_spice_out\n",
        "    type: nevergrad\n",
        "    active_corner: tt_27C_1V5\n",
    )
    assert all(text.count(a) == 1 for a in anchors)
    text = (
        text.replace(anchors[0], f"ws_root : {EXAMPLE_YAML.parent.parent}\n")
        .replace(anchors[1], f"outdir  : {outdir}\n")
        .replace(anchors[2], f"    type: {engine}\n")
    )
    if multi:
        text = text.replace(anchors[3], anchors[3] + "    mode: multi\n")
    dst.write_text(text)
    return dst


def _enabled_specs(setup: Project_Setup) -> list[Any]:
    return setup.optimizer_config.target_specs.enabled_targets()


def _result(**overrides: Any) -> OptimizeResult:
    fields: dict[str, Any] = dict(
        name="OTA",
        sim_engine="ngspice",
        optimizer="NGOpt",
        budget=8,
        seed=None,
        outdir=Path("/runs/OTA_out"),
        checkpoint_dir=Path("/work/auto_save/OTA"),
        n_trials=8,
        best_score=1.5,
        best_knobs={"W": 2e-6},
        best_metrics={"gain": 42.0},
    )
    fields.update(overrides)
    return OptimizeResult(**fields)


def _spy_run(monkeypatch, result: OptimizeResult) -> list[tuple[Any, dict[str, Any]]]:
    """Replace `run_project.run` (what main() calls) with a recorder returning `result`."""
    calls: list[tuple[Any, dict[str, Any]]] = []

    def _run(project_setup, **kwargs):
        calls.append((project_setup, kwargs))
        return result

    monkeypatch.setattr(run_project, "run", _run)
    return calls


def _entry(params: dict[str, float], score: float, fit_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "point": {"params": params, "score": score, "metadata": {}},
        "fit_summary": fit_summary,
        "log_file": None,
    }


def _write_checkpoint(path: Path, entries: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": "1.0.0", "timestamp": "x", "optimization_log": entries})
    )
    return path


def _table_rows(markdown: str) -> list[dict[str, str]]:
    """The report's table as one dict per row, keyed by the header cells."""
    table = [ln for ln in markdown.splitlines() if ln.startswith("|")]
    header = [c.strip() for c in table[0].strip("|").split("|")]
    return [dict(zip(header, (c.strip() for c in ln.strip("|").split("|")))) for ln in table[2:]]


# The design-side parser of the three `best …` lines (an LDO sizing experiment's run_opt.py).
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


# ------------------------------------------------------------------------------------------
# argument handling: --help, a bad project path, the engine choices, forwarding to run()
# ------------------------------------------------------------------------------------------
def test_help_lists_the_new_flags_and_exits_0(cli, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for flag in ("--engine", "--resume", "--checkpoint-dir", "--report"):
        assert flag in out
    assert "{nevergrad,bayesian_ax}" in out


@pytest.mark.parametrize("kind", ["missing-file", "a-directory"])
def test_a_bad_project_path_exits_2_with_one_line(cli, capsys, tmp_path, kind):
    path = tmp_path / "no_such_project.yaml"
    if kind == "a-directory":
        path.mkdir()
    rc = main([str(path), "--budget", "2"])
    assert rc == 2
    captured = capsys.readouterr()
    assert captured.err == f"{PREFIX} no project YAML at {path}\n"
    assert captured.out == ""
    assert not (tmp_path / "work" / "logs").exists(), "it stops before the logging setup"


def test_an_unknown_engine_is_a_usage_error(cli, capsys):
    with pytest.raises(SystemExit) as exc:
        main([str(EXAMPLE_YAML), "--engine", "reinforcement_learning"])
    assert exc.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_the_engine_choices_are_the_dsl_engines():
    parser = run_project._build_parser()
    [engine] = [a for a in parser._actions if a.dest == "engine"]
    assert list(engine.choices or []) == [t.value for t in OptimizerType]


def test_main_forwards_the_new_flags_to_run(cli, monkeypatch, tmp_path):
    calls = _spy_run(monkeypatch, _result())
    assert (
        main(
            [
                str(EXAMPLE_YAML),
                "--engine",
                "bayesian_ax",
                "--resume",
                "ckpts/a",
                "--resume",
                "ckpts/b/run_CRASH.json",
                "--checkpoint-dir",
                "~/ckpts",
                "--report",
                "out/best.md",
            ]
        )
        == 0
    )
    [(project_setup, kwargs)] = calls
    assert project_setup == EXAMPLE_YAML
    assert {k: kwargs[k] for k in ("engine", "resume", "checkpoint_dir", "report")} == {
        "engine": "bayesian_ax",
        "resume": ["ckpts/a", "ckpts/b/run_CRASH.json"],
        "checkpoint_dir": "~/ckpts",
        "report": "out/best.md",
    }
    # where the logging setup writes: the bad-path test checks that this dir stays absent
    assert (tmp_path / "work" / "logs").is_dir()


# ------------------------------------------------------------------------------------------
# --engine
# ------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "yaml_engine, flag, expected_cls, label",
    [
        ("nevergrad", "bayesian_ax", _AxStandIn, "bayesian_ax"),
        ("bayesian_ax", "nevergrad", Nevergrad_Spice_Single_Objective, "TwoPointsDE"),
        ("bayesian_ax", None, _AxStandIn, "bayesian_ax"),  # no flag: the YAML's type decides
    ],
    ids=["nevergrad-yaml-to-ax", "ax-yaml-to-nevergrad", "ax-yaml-no-flag"],
)
def test_engine_switches_the_optimizer_class(
    offline, cli, built, monkeypatch, capsys, yaml_engine, flag, expected_cls, label
):
    monkeypatch.setitem(SPICE_OPTIMIZER_CLASSES, Optimizer_Type_Enum.AX_SINGLE, _AxStandIn)
    yaml_copy = _example_copy(
        offline.root / "project_setup.yaml", outdir=offline.root / "out", engine=yaml_engine
    )
    before = yaml_copy.read_text()

    rc = main(
        [
            str(yaml_copy),
            *(["--engine", flag] if flag else []),
            "--budget",
            "2",
            "--algo",
            "TwoPointsDE",
            "--no-timestamp",
            "--quiet",
        ]
    )

    assert rc == 0
    assert type(built.opt) is expected_cls
    assert built.orch.project_setup.optimizer_config.type == (flag or yaml_engine)
    assert yaml_copy.read_text() == before, "the override is ephemeral"
    # the start line names the engine, not a Nevergrad algorithm Ax ignores
    start = [
        ln for ln in capsys.readouterr().out.splitlines() if ln.startswith(f"{PREFIX} CASCODE-OTA:")
    ]
    assert start == [f"{PREFIX} CASCODE-OTA: engine=ngspice optimizer={label} budget=2"]


# ------------------------------------------------------------------------------------------
# --checkpoint-dir
# ------------------------------------------------------------------------------------------
def test_checkpoint_dir_is_the_exact_checkpoint_dir(offline, monkeypatch):
    monkeypatch.setenv("HOME", str(offline.root / "home"))
    result = run(
        EXAMPLE_YAML,
        budget=3,
        algo="TwoPointsDE",
        outdir=offline.root / "out",
        verbose=False,
        checkpoint_dir="~/ckpts/run1",
    )
    assert result.checkpoint_dir == offline.root / "home" / "ckpts" / "run1"
    assert summarize_checkpoint(result.checkpoint_dir).n_trials == 3
    assert not (offline.root / "work" / "auto_save").exists(), "nothing went to the default dir"


# ------------------------------------------------------------------------------------------
# --report
# ------------------------------------------------------------------------------------------
def test_report_writes_one_row_per_enabled_spec(offline, cli, built, capsys):
    report = offline.root / "reports" / "best.md"  # its parent does not exist yet
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "3",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(offline.root / "out"),
            "--report",
            str(report),
            "--quiet",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out

    text = report.read_text()
    assert text.startswith("# CASCODE-OTA: spec vs achieved\n")
    rows = _table_rows(text)
    specs = _enabled_specs(built.orch.project_setup)
    assert [r["spec"] for r in rows] == [s.name for s in specs]
    best = _design_side_parse(out)
    fit = built.opt.global_best_entry.fit_summary
    for row, spec in zip(rows, specs):
        assert row["goal"] == spec.goal.value
        assert float(row["target"]) == pytest.approx(float(spec.target), rel=1e-5)
        assert float(row["tol"]) == pytest.approx(float(spec.tolerance), rel=1e-5)
        # the same reading the `best metrics` line prints, and the scorer's own verdict
        assert float(row["achieved"]) == pytest.approx(best["metrics"][spec.name], rel=1e-5)
        assert row["pass"] == ("yes" if float(fit[spec.name]["score"]) > -float(EPSILON) else "no")
    # the report line follows the three best lines and is not one the design regex reads
    lines = [
        ln
        for ln in out.splitlines()
        if ln.startswith(f"{PREFIX} best ") or ln.startswith(f"{PREFIX} report")
    ]
    assert lines[-1] == f"{PREFIX} report: {report}"
    assert [ln.split()[2] for ln in lines[:-1]] == ["score", "knobs:", "metrics:"]


def test_report_rows_are_namespaced_per_corner_in_multi_mode(tmp_path):
    setup = Project_Setup.from_yaml(
        _example_copy(tmp_path / "p.yaml", outdir=tmp_path / "o", multi=True)
    )
    assert setup.pvt is not None
    corners = [c.name for c in setup.pvt.corners_to_run()]
    specs = [s.name for s in _enabled_specs(setup)]
    assert len(corners) == 2 and len(specs) >= 3
    fit: dict[str, Any] = {
        f"{c}::{s}": {"curr_val": 2.5, "score": 0.0} for c in corners for s in specs
    }
    fit[f"{corners[1]}::{specs[0]}"] = {"curr_val": float("nan"), "score": -1e6}  # unmeasured
    fit[f"{corners[0]}::{specs[2]}"] = 0.25  # a bare scalar (the Bode fitter's shape)
    del fit[f"{corners[0]}::{specs[1]}"]  # a key the run never logged

    text = run_project._spec_report(setup, _result(name=setup.name), fit)

    rows = {r["spec"]: r for r in _table_rows(text)}
    assert list(rows) == [f"{c}::{s}" for c in corners for s in specs]
    assert (
        rows[f"{corners[1]}::{specs[0]}"]["achieved"],
        rows[f"{corners[1]}::{specs[0]}"]["pass"],
    ) == ("n/a", "no")
    assert (
        rows[f"{corners[0]}::{specs[2]}"]["achieved"],
        rows[f"{corners[0]}::{specs[2]}"]["pass"],
    ) == ("0.25", "n/a")
    assert (
        rows[f"{corners[0]}::{specs[1]}"]["achieved"],
        rows[f"{corners[0]}::{specs[1]}"]["pass"],
    ) == ("n/a", "n/a")
    assert (
        rows[f"{corners[1]}::{specs[1]}"]["achieved"],
        rows[f"{corners[1]}::{specs[1]}"]["pass"],
    ) == ("2.5", "yes")


def test_report_names_the_run_and_an_early_stop(tmp_path):
    setup = Project_Setup.from_yaml(_example_copy(tmp_path / "p.yaml", outdir=tmp_path / "o"))
    result = _result(
        name=setup.name,
        optimizer="bayesian_ax",
        n_trials=3,
        budget=8,
        best_score=-0.123456789,
        stop_reason="stopped by the per-trial time guard",
    )
    text = run_project._spec_report(setup, result, None)
    assert "engine ngspice, optimizer bayesian_ax, 3 of 8 trials, best score -0.123457" in text
    assert "Stopped early: stopped by the per-trial time guard" in text
    rows = _table_rows(text)
    assert [r["spec"] for r in rows] == [s.name for s in _enabled_specs(setup)]
    assert {(r["achieved"], r["pass"]) for r in rows} == {("n/a", "n/a")}  # no fit_summary


# ------------------------------------------------------------------------------------------
# --resume
# ------------------------------------------------------------------------------------------
def test_resume_from_a_crash_checkpoint_runs_only_the_remaining_budget(offline, steps):
    """G3: a run killed mid-way resumes from its `_CRASH` checkpoint, spends only the budget the
    crash left, and writes no prior trial a second time."""
    first_dir: list[Path] = []
    steps.crash_at = 4  # trials 1..3 complete, the 4th raises
    with pytest.raises(RuntimeError, match="backend died"):
        run(
            EXAMPLE_YAML,
            budget=10,
            algo="TwoPointsDE",
            outdir=offline.root / "out1",
            verbose=False,
            on_start=lambda plan: first_dir.append(plan.checkpoint_dir),
        )
    [crash] = first_dir[0].glob("*_trial4_CRASH_*.json")
    crash_bytes = crash.read_bytes()
    prior = summarize_checkpoint(crash)
    assert prior.n_trials == 3

    steps.n, steps.crash_at = 0, None
    result = run(
        EXAMPLE_YAML,
        budget=10,
        algo="TwoPointsDE",
        outdir=offline.root / "out2",
        verbose=False,
        resume=crash,
        checkpoint_dir=offline.root / "resumed",
    )

    assert steps.n == 7, "only the remaining budget ran"
    assert (result.budget, result.n_trials) == (10, 10)
    new = summarize_checkpoint(offline.root / "resumed", top=10)
    assert new.n_trials == 7, "the resumed segment's checkpoints hold only its own trials"
    assert crash.read_bytes() == crash_bytes
    assert sorted(first_dir[0].iterdir()) == [crash], "the crashed run's dir is untouched"
    best_of_both = max(t.score for t in [*prior.top, *new.top] if t.score is not None)
    assert result.best_score == pytest.approx(best_of_both)


def test_resume_reads_a_checkpoint_dir_and_keeps_a_better_prior_best(offline, steps, built):
    # a long run's trials are split across autosave chunks; the dir is the whole prior run
    setup = Project_Setup.from_yaml(EXAMPLE_YAML)
    knob = setup.dut_params[0].name
    specs = [s.name for s in _enabled_specs(setup)]
    prior_best_fit = {s: {"curr_val": 7.0, "score": 0.0} for s in specs}
    ckpts = offline.root / "prior"
    _write_checkpoint(
        ckpts / "CASCODE-OTA_TwoPointsDE_5_trial2_2026-01-01_00-00-00.json",
        [_entry({knob: 1.0}, -5.0, {}), _entry({knob: 2.0}, 1e9, prior_best_fit)],
    )
    _write_checkpoint(
        ckpts / "CASCODE-OTA_TwoPointsDE_5_trial3_CRASH_2026-01-01_00-00-01.json",
        [_entry({knob: 3.0}, -4.0, {})],
    )
    report = offline.root / "best.md"

    result = run(
        EXAMPLE_YAML,
        budget=5,
        algo="TwoPointsDE",
        outdir=offline.root / "out",
        verbose=False,
        resume=ckpts,
        checkpoint_dir=offline.root / "resumed",
        report=report,
    )

    assert steps.n == 2 and (result.budget, result.n_trials) == (5, 5)
    assert (result.best_score, result.best_knobs) == (1e9, {knob: 2.0})
    assert result.best_metrics == {s: 7.0 for s in specs}
    assert built.opt.global_best_entry.point.score == 1e9
    assert {(r["achieved"], r["pass"]) for r in _table_rows(report.read_text())} == {("7", "yes")}
    assert summarize_checkpoint(offline.root / "resumed").n_trials == 2


def test_resume_refuses_the_last_chunk_alone_and_reads_the_dir_as_the_whole_run(
    offline, steps, built
):
    # a run that autosaved: its _CRASH file holds only the trials since the last chunk
    built.autosave_every = 2
    steps.crash_at = 6  # trials 1..5 complete: chunks trial2 + trial4, the CRASH holds trial 5
    with pytest.raises(RuntimeError, match="backend died"):
        run(
            EXAMPLE_YAML,
            budget=10,
            algo="TwoPointsDE",
            outdir=offline.root / "out1",
            verbose=False,
            checkpoint_dir=offline.root / "a",
        )
    [crash] = (offline.root / "a").glob("*_trial6_CRASH_*.json")
    assert (
        summarize_checkpoint(crash).n_trials,
        summarize_checkpoint(offline.root / "a").n_trials,
    ) == (1, 5)
    builds = offline.wrapper_builds

    steps.n, steps.crash_at = 0, None
    with pytest.raises(
        ResumeError,
        match=rf"holds only 1 trial\(s\), but the run had completed "
        rf"at least 5 .* pass its checkpoint dir "
        rf"{re.escape(str(offline.root / 'a'))}$",
    ):
        run(
            EXAMPLE_YAML,
            budget=10,
            algo="TwoPointsDE",
            outdir=offline.root / "out2",
            verbose=False,
            resume=crash,
            checkpoint_dir=offline.root / "resumed",
        )
    assert offline.wrapper_builds == builds and steps.n == 0, "refused before any simulator"

    result = run(
        EXAMPLE_YAML,
        budget=10,
        algo="TwoPointsDE",
        outdir=offline.root / "out3",
        verbose=False,
        resume=offline.root / "a",
        checkpoint_dir=offline.root / "resumed",
    )
    assert steps.n == 5 and (result.budget, result.n_trials) == (10, 10)
    trials = [
        *summarize_checkpoint(offline.root / "a", top=10).top,
        *summarize_checkpoint(offline.root / "resumed", top=10).top,
    ]
    assert len(trials) == 10
    assert result.best_score == pytest.approx(max(t.score for t in trials if t.score is not None))


def test_a_chain_of_resumed_segments_resumes_from_every_segment(offline, steps):
    """A crashes, B resumed from A crashes too, C resumes from both: a resumed segment's
    checkpoints hold only its own trials, so C is given every segment and none is lost."""
    steps.crash_at = 4  # A: trials 1..3
    with pytest.raises(RuntimeError, match="backend died"):
        run(
            EXAMPLE_YAML,
            budget=10,
            algo="TwoPointsDE",
            outdir=offline.root / "outA",
            verbose=False,
            checkpoint_dir=offline.root / "a",
        )
    steps.n, steps.crash_at = 0, 3  # B: 2 more trials
    with pytest.raises(RuntimeError, match="backend died"):
        run(
            EXAMPLE_YAML,
            budget=10,
            algo="TwoPointsDE",
            outdir=offline.root / "outB",
            verbose=False,
            resume=offline.root / "a",
            checkpoint_dir=offline.root / "b",
        )
    [crash_b] = (offline.root / "b").glob("*_CRASH_*.json")
    assert [summarize_checkpoint(offline.root / d).n_trials for d in ("a", "b")] == [3, 2]

    steps.n, steps.crash_at = 0, None
    result = run(
        EXAMPLE_YAML,
        budget=10,
        algo="TwoPointsDE",
        outdir=offline.root / "outC",
        verbose=False,
        resume=[offline.root / "a", crash_b],
        checkpoint_dir=offline.root / "c",
    )

    assert steps.n == 5, "only what A and B left of the budget ran"
    assert (result.budget, result.n_trials) == (10, 10)
    trials = [
        t for d in ("a", "b", "c") for t in summarize_checkpoint(offline.root / d, top=10).top
    ]
    assert len(trials) == 10
    assert result.best_score == pytest.approx(max(t.score for t in trials if t.score is not None))


def test_main_resumes_and_keeps_the_best_lines(offline, cli, steps, capsys):
    # prior trials far below any new one, so the three lines report a trial of the new segment
    ckpt = _write_checkpoint(
        offline.root / "c" / "OTA_TwoPointsDE_6_trial3_CRASH_x.json",
        [_entry({"W1": 1.0}, -1e12, {}), _entry({"W1": 2.0}, -1e12, {})],
    )
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "6",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(offline.root / "out"),
            "--resume",
            str(ckpt),
            "--checkpoint-dir",
            str(offline.root / "resumed"),
            "--quiet",
        ]
    )
    assert rc == 0
    assert steps.n == 4
    best = _design_side_parse(capsys.readouterr().out)
    assert set(best) == {"score", "knobs", "metrics"} and best["score"] > -1e12
    assert set(best["metrics"]) == {
        s.name for s in _enabled_specs(Project_Setup.from_yaml(EXAMPLE_YAML))
    }


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "not-a-checkpoint",
        "torn",
        "no-point",
        "spent",
        "last-chunk-only",
        "given-twice",
        "unreadable-chunk",
    ],
)
def test_a_checkpoint_it_cannot_resume_exits_2_before_any_simulation(
    offline, cli, steps, capsys, case
):
    ckpt = offline.root / "ckpt.json"
    resume_args = ["--resume", str(ckpt)]
    if case == "not-a-checkpoint":
        ckpt.write_text(json.dumps({"timings": []}))
    elif case == "torn":
        ckpt.write_text('{"optimization_log": [')
    elif case == "no-point":
        ckpt.write_text(json.dumps({"optimization_log": [{"fit_summary": {}}]}))
    elif case == "spent":
        _write_checkpoint(ckpt, [_entry({"W1": float(i)}, float(i), {}) for i in range(3)])
    elif case == "last-chunk-only":  # trials 1..4 are in earlier autosave chunks
        ckpt = _write_checkpoint(
            offline.root / "OTA_TwoPointsDE_10_trial6_CRASH_x.json", [_entry({"W1": 5.0}, 5.0, {})]
        )
        resume_args = ["--resume", str(ckpt)]
    elif case == "given-twice":  # a file inside a dir given before it: read twice
        ckpt = _write_checkpoint(
            offline.root / "c" / "OTA_TwoPointsDE_10_trial1_FINAL_x.json",
            [_entry({"W1": 1.0}, 1.0, {})],
        )
        resume_args = ["--resume", str(ckpt.parent), "--resume", str(ckpt)]
    elif case == "unreadable-chunk":  # summarize_checkpoint skips it; a resume must not
        ckpt = offline.root / "d"
        _write_checkpoint(ckpt / "OTA_TwoPointsDE_10_trial1_x.json", [_entry({"W1": 1.0}, 1, {})])
        (ckpt / "OTA_TwoPointsDE_10_trial2_x.json").write_bytes(b"\xff not utf-8")
        resume_args = ["--resume", str(ckpt)]

    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "3",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(offline.root / "out"),
            *resume_args,
            "--quiet",
        ]
    )

    assert rc == 2
    err = capsys.readouterr().err
    assert err.count("\n") == 1 and err.startswith(f"{PREFIX} cannot resume from {ckpt}: ")
    if case == "spent":
        assert "already holds 3 trial(s) and the budget is 3" in err
    elif case == "last-chunk-only":
        assert f"pass its checkpoint dir {offline.root}" in err
    elif case == "given-twice":
        assert f"overlaps {ckpt.parent}" in err
    elif case == "unreadable-chunk":
        assert "OTA_TwoPointsDE_10_trial2_x.json cannot be read (UnicodeDecodeError" in err
    assert offline.wrapper_builds == 0 and steps.n == 0, "it fails before building a simulator"


@pytest.mark.parametrize("given", ["dir", "file-in-it"])
def test_resume_refuses_to_write_into_the_checkpoint_dir_it_resumes_from(
    offline, cli, steps, capsys, given
):
    """`--resume X --checkpoint-dir X` would put a second segment's chunks and lineage marker into
    X (L-PF-14; kept with #308's continued numbering, see `_refuse_writing_into`). Refused before
    any simulator is built."""
    prior = offline.root / "prior"
    ckpt = _write_checkpoint(
        prior / "OTA_TwoPointsDE_10_trial1_FINAL_x.json", [_entry({"W1": 1.0}, 1.0, {})]
    )
    resume = prior if given == "dir" else ckpt
    flags = ["--budget", "3", "--algo", "TwoPointsDE", "--outdir", str(offline.root / "out")]
    rc = main([str(EXAMPLE_YAML), *flags, "--resume", str(resume), "--checkpoint-dir", str(prior)])

    assert rc == 2
    err = capsys.readouterr().err
    assert err.count("\n") == 1 and err.startswith(f"{PREFIX} cannot resume from {resume}: ")
    assert f"--checkpoint-dir {prior}" in err and "trial order" in err
    assert offline.wrapper_builds == 0 and steps.n == 0, "it fails before building a simulator"
    assert sorted(prior.iterdir()) == [ckpt], "nothing was written into the prior dir"


def test_a_zero_budget_without_resume_still_exits_1(offline, cli, capsys):
    # the spent-budget check belongs to --resume: a plain run with nothing to do is "no trial"
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "0",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(offline.root / "out"),
            "--quiet",
        ]
    )
    assert rc == 1
    assert capsys.readouterr().err.endswith(f"{PREFIX} no trial completed\n")


# ------------------------------------------------------------------------------------------
# the stdout contract: design repos regex-parse the three `best …` lines
# ------------------------------------------------------------------------------------------
def test_the_best_lines_are_byte_stable_with_every_new_flag(cli, monkeypatch, capsys, tmp_path):
    _spy_run(
        monkeypatch,
        _result(
            best_score=-0.81,
            best_knobs={"w": 1e-6, "nf": 4.0},
            best_metrics={"gain_db": 40.0, "pm": float("nan")},
        ),
    )
    report = tmp_path / "r.md"
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--engine",
            "bayesian_ax",
            "--resume",
            str(tmp_path / "c.json"),
            "--checkpoint-dir",
            str(tmp_path / "ck"),
            "--report",
            str(report),
            "--quiet",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert [ln for ln in out.splitlines() if ln.startswith(PREFIX)] == [
        "[spicexplorer-optimize] best score -0.81",
        '[spicexplorer-optimize] best knobs: {"w": 1e-06, "nf": 4.0}',
        '[spicexplorer-optimize] best metrics: {"gain_db": 40.0, "pm": NaN}',
        f"[spicexplorer-optimize] report: {report}",
    ]
    best = _design_side_parse(out)
    assert best["score"] == -0.81 and best["knobs"] == {"w": 1e-6, "nf": 4.0}
    assert best["metrics"]["gain_db"] == 40.0 and math.isnan(best["metrics"]["pm"])


# ------------------------------------------------------------------------------------------
# resume continuity (#308): lineage marker, prior trials told to the engine, trial numbering,
# the Ax run label
# ------------------------------------------------------------------------------------------
_TS = re.compile(r"_\d{4}-\d\d-\d\d_\d\d-\d\d-\d\d")


def _names(d: Path) -> list[str]:
    """The checkpoint names in `d` without their timestamps, in the order the chunk reader uses."""
    from spicexplorer.optimization.summary import _chunk_order

    return [
        _TS.sub("", p.name)
        for p in sorted(d.glob("*.json"), key=_chunk_order)
        if p.name != run_project.LINEAGE_MARKER
    ]


def _marker(d: Path) -> dict[str, Any]:
    return json.loads((d / run_project.LINEAGE_MARKER).read_text())


def _crash_run(offline, steps, d: Path, *, crash_at: int, resume: Any = None) -> None:
    steps.n, steps.crash_at = 0, crash_at
    with pytest.raises(RuntimeError, match="backend died"):
        run(
            EXAMPLE_YAML,
            budget=10,
            algo="TwoPointsDE",
            outdir=offline.root / f"out_{d.name}",
            verbose=False,
            resume=resume,
            checkpoint_dir=d,
        )
    steps.n, steps.crash_at = 0, None


def test_a_fresh_run_writes_no_marker_and_names_trials_from_1(offline, built):
    built.autosave_every = 2
    result = run(
        EXAMPLE_YAML,
        budget=5,
        algo="TwoPointsDE",
        outdir=offline.root / "out",
        verbose=False,
        checkpoint_dir=offline.root / "fresh",
    )
    assert _names(offline.root / "fresh") == [
        "CASCODE-OTA_TwoPointsDE_5_trial2.json",
        "CASCODE-OTA_TwoPointsDE_5_trial4.json",
        "CASCODE-OTA_TwoPointsDE_5_trial5_FINAL.json",
    ]
    assert not (offline.root / "fresh" / run_project.LINEAGE_MARKER).exists()
    assert result.resumed_from == () and "resumed_from" not in result.to_dict()


def test_a_resumed_segment_continues_the_trial_numbering_and_records_its_lineage(
    offline, steps, built
):
    """Budget 10, crashed after 3 trials: the resumed segment's chunks are `_10_trial4…` onward
    (the whole budget in the name), sort after the prior chunks in one dir, and the segment's
    marker names the prior dir and its 3 trials."""
    from spicexplorer.optimization.summary import _read_entries

    built.autosave_every = 2
    a, b = offline.root / "a", offline.root / "b"
    _crash_run(offline, steps, a, crash_at=4)  # chunk trial2 + trial4_CRASH (trial 3)
    assert _names(a) == [
        "CASCODE-OTA_TwoPointsDE_10_trial2.json",
        "CASCODE-OTA_TwoPointsDE_10_trial4_CRASH.json",
    ]
    report = offline.root / "b.md"
    result = run(
        EXAMPLE_YAML,
        budget=10,
        algo="TwoPointsDE",
        outdir=offline.root / "outb",
        verbose=False,
        resume=a,
        checkpoint_dir=b,
        report=report,
    )

    assert steps.n == 7 and (result.budget, result.n_trials) == (10, 10)
    assert _names(b) == [f"CASCODE-OTA_TwoPointsDE_10_trial{n}.json" for n in (4, 6, 8, 10)]
    assert _marker(b) == {
        "schema_version": "1.0",
        "trial_offset": 3,
        "segments": [{"path": str(a.resolve()), "trials": 3}],
    }
    assert result.resumed_from == (str(a.resolve()),)
    assert result.to_dict()["resumed_from"] == [str(a.resolve())]
    assert f"Resumed from: {a.resolve()}" in report.read_text()

    merged = offline.root / "merged"  # both segments' chunks in one dir read in trial order
    merged.mkdir()
    for f in [*a.glob("*.json"), *b.glob("*.json")]:
        if f.name != run_project.LINEAGE_MARKER:
            (merged / f.name).write_bytes(f.read_bytes())
    order = [e["point"]["params"] for e in _read_entries(merged)[0]]
    assert order == [e["point"]["params"] for d in (a, b) for e in _read_entries(d)[0]]
    assert summarize_checkpoint(merged).n_trials == 10


def test_the_last_segment_alone_resumes_the_whole_chain(offline, steps):
    """A crashes, B resumes A and crashes, C is given only B: C runs exactly what A and B left,
    and the three dirs hold the whole budget with no trial counted twice."""
    a, b, c = (offline.root / n for n in "abc")
    _crash_run(offline, steps, a, crash_at=4)  # A: trials 1..3
    _crash_run(offline, steps, b, crash_at=3, resume=a)  # B: trials 4, 5
    assert [summarize_checkpoint(d).n_trials for d in (a, b)] == [3, 2]
    assert _names(b) == ["CASCODE-OTA_TwoPointsDE_10_trial6_CRASH.json"]

    result = run(
        EXAMPLE_YAML,
        budget=10,
        algo="TwoPointsDE",
        outdir=offline.root / "outc",
        verbose=False,
        resume=b,
        checkpoint_dir=c,
    )

    assert steps.n == 5, "only what A and B left of the budget ran"
    assert (result.budget, result.n_trials) == (10, 10)
    assert result.resumed_from == (str(a.resolve()), str(b.resolve()))
    assert _marker(c)["trial_offset"] == 5
    assert _marker(c)["segments"] == [
        {"path": str(a.resolve()), "trials": 3},
        {"path": str(b.resolve()), "trials": 2},
    ]
    assert _names(c) == ["CASCODE-OTA_TwoPointsDE_10_trial10_FINAL.json"]
    trials = [t for d in (a, b, c) for t in summarize_checkpoint(d, top=10).top]
    assert len(trials) == 10
    # the YAML's seed is fixed: each resumed segment samples from a seed derived from it, so it
    # does not replay the first segment's proposals
    assert len({json.dumps(t.params, sort_keys=True) for t in trials}) == 10, "no point twice"
    assert result.best_score == pytest.approx(max(t.score for t in trials if t.score is not None))


@pytest.mark.parametrize("order", ["a-then-b", "b-then-a", "a-then-crash-file-of-b"])
def test_giving_every_segment_still_counts_each_once(offline, steps, order):
    a, b = offline.root / "a", offline.root / "b"
    _crash_run(offline, steps, a, crash_at=4)
    _crash_run(offline, steps, b, crash_at=3, resume=a)
    [crash_b] = b.glob("*_CRASH_*.json")
    resume = {"a-then-b": [a, b], "b-then-a": [b, a], "a-then-crash-file-of-b": [a, crash_b]}[order]
    result = run(
        EXAMPLE_YAML,
        budget=10,
        algo="TwoPointsDE",
        outdir=offline.root / "outc",
        verbose=False,
        resume=resume,
        checkpoint_dir=offline.root / "c",
    )
    assert steps.n == 5 and result.n_trials == 10
    assert [Path(p).name for p in result.resumed_from][0] == "a"


def test_a_resume_reads_dirs_written_before_the_marker_existed(offline, steps, built):
    """Old-format segments: A's chunks named for a budget of 10, B (an old resumed segment, never
    autosaved) named from trial1 again for its remaining budget of 7, neither with a marker. They
    resume as before; the new segment names on from trial 6 and its marker names both, so a later
    resume of the new dir alone counts all three."""
    setup = Project_Setup.from_yaml(EXAMPLE_YAML)
    knob = setup.dut_params[0].name
    lo = float(setup.dut_params[0].min_val)  # type: ignore[arg-type]
    a, b, c = offline.root / "old_a", offline.root / "old_b", offline.root / "c"
    _write_checkpoint(
        a / "CASCODE-OTA_TwoPointsDE_10_trial2_2026-01-01_00-00-00.json",
        [_entry({knob: lo * 1.1}, -9.0, {}), _entry({knob: lo * 1.2}, -8.0, {})],
    )
    _write_checkpoint(
        a / "CASCODE-OTA_TwoPointsDE_10_trial4_CRASH_2026-01-01_00-00-01.json",
        [_entry({knob: lo * 1.3}, -7.0, {})],
    )
    crash_b = _write_checkpoint(
        b / "CASCODE-OTA_TwoPointsDE_7_trial3_CRASH_2026-01-02_00-00-00.json",
        [_entry({knob: lo * 1.4}, -6.0, {}), _entry({knob: lo * 1.5}, -5.0, {})],
    )
    built.autosave_every = 2

    result = run(
        EXAMPLE_YAML,
        budget=10,
        algo="TwoPointsDE",
        outdir=offline.root / "outc",
        verbose=False,
        resume=[a, crash_b],
        checkpoint_dir=c,
    )

    assert steps.n == 5 and (result.budget, result.n_trials) == (10, 10)
    assert _names(c) == [
        "CASCODE-OTA_TwoPointsDE_10_trial6.json",
        "CASCODE-OTA_TwoPointsDE_10_trial8.json",
        "CASCODE-OTA_TwoPointsDE_10_trial10.json",
    ]
    assert _marker(c) == {
        "schema_version": "1.0",
        "trial_offset": 5,
        "segments": [
            {"path": str(a.resolve()), "trials": 3},
            {"path": str(crash_b.resolve()), "trials": 2},
        ],
    }
    assert (
        not (a / run_project.LINEAGE_MARKER).exists()
        and not (b / run_project.LINEAGE_MARKER).exists()
    )

    steps.n = 0
    later = run(
        EXAMPLE_YAML,
        budget=12,
        algo="TwoPointsDE",
        outdir=offline.root / "outd",
        verbose=False,
        resume=c,
        checkpoint_dir=offline.root / "d",
    )
    assert steps.n == 2 and later.n_trials == 12
    assert _names(offline.root / "d") == ["CASCODE-OTA_TwoPointsDE_12_trial12.json"]


def test_a_marker_naming_a_segment_that_is_gone_exits_2(offline, cli, steps, capsys):
    import shutil

    a, b = offline.root / "a", offline.root / "b"
    _crash_run(offline, steps, a, crash_at=4)
    _crash_run(offline, steps, b, crash_at=3, resume=a)
    shutil.rmtree(a)
    builds = offline.wrapper_builds
    capsys.readouterr()
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "10",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(offline.root / "out"),
            "--resume",
            str(b),
            "--quiet",
        ]
    )
    assert rc == 2
    err = capsys.readouterr().err
    assert err.count("\n") == 1 and err.startswith(f"{PREFIX} cannot resume from {b}: ")
    assert f"names {a.resolve()}, which is gone" in err
    assert offline.wrapper_builds == builds and steps.n == 0


def test_writing_into_a_segment_the_lineage_reaches_is_refused(offline, cli, steps, capsys):
    a, b = offline.root / "a", offline.root / "b"
    _crash_run(offline, steps, a, crash_at=4)
    _crash_run(offline, steps, b, crash_at=3, resume=a)
    before = sorted(a.iterdir())
    capsys.readouterr()
    rc = main(
        [
            str(EXAMPLE_YAML),
            "--budget",
            "10",
            "--algo",
            "TwoPointsDE",
            "--outdir",
            str(offline.root / "out"),
            "--resume",
            str(b),
            "--checkpoint-dir",
            str(a),
            "--quiet",
        ]
    )
    assert rc == 2
    err = capsys.readouterr().err
    assert err.startswith(f"{PREFIX} cannot resume from {a.resolve()}: --checkpoint-dir {a} ")
    assert sorted(a.iterdir()) == before and steps.n == 0


@dataclass
class _EngineSpy:
    events: list[tuple[str, Any]]


@pytest.fixture
def ng_spy(monkeypatch) -> _EngineSpy:
    """Record every `ask` and `tell` on the Nevergrad optimizer each run builds."""
    from spicexplorer.optimization.stochastic.nevergrad import NevergradMixin

    spy = _EngineSpy(events=[])
    real_create = NevergradMixin._create_optimizer_obj

    def _create(self):
        ok = real_create(self)
        opt, real_ask, real_tell = self.optimizer, self.optimizer.ask, self.optimizer.tell

        def ask(*a, **k):
            cand = real_ask(*a, **k)
            spy.events.append(("ask", cand.uid))
            return cand

        def tell(cand, loss, *a, **k):
            spy.events.append(("tell", (cand.uid, dict(cand.value), float(loss))))
            return real_tell(cand, loss, *a, **k)

        opt.ask, opt.tell = ask, tell
        return ok

    monkeypatch.setattr(NevergradMixin, "_create_optimizer_obj", _create)
    return spy


def test_nevergrad_is_told_every_prior_trial_before_its_first_ask(offline, steps, built, ng_spy):
    a = offline.root / "a"
    _crash_run(offline, steps, a, crash_at=6)  # 5 prior trials
    prior = [
        e["point"]
        for e in json.loads(next(a.glob("*_CRASH_*.json")).read_text())["optimization_log"]
    ]
    assert len(prior) == 5
    ng_spy.events.clear()

    run(
        EXAMPLE_YAML,
        budget=8,
        algo="TwoPointsDE",
        outdir=offline.root / "outb",
        verbose=False,
        resume=a,
        checkpoint_dir=offline.root / "b",
    )

    asked = {uid for kind, uid in ng_spy.events if kind == "ask"}
    first_ask = next(i for i, (kind, _) in enumerate(ng_spy.events) if kind == "ask")
    told_first = [v for kind, v in ng_spy.events[:first_ask] if kind == "tell"]
    assert len(told_first) == 5 and all(uid not in asked for uid, _, _ in told_first)
    assert len(asked) == 3, "then only the remaining budget is asked"
    for (_uid, coords, loss), point in zip(told_first, prior):
        assert loss == pytest.approx(-point["score"], rel=1e-12)
        phys = built.opt.denormalize_params(coords)
        for name, v in phys.items():
            assert float(v) == pytest.approx(float(point["params"][name]), rel=1e-9), name


def test_a_prior_point_outside_the_bounds_is_skipped_and_logged(offline, steps, ng_spy, caplog):
    setup = Project_Setup.from_yaml(EXAMPLE_YAML)
    params = {p.name: float(p.min_val) * 2 if not p.is_integer else 2.0 for p in setup.dut_params}  # type: ignore[arg-type]
    first = setup.dut_params[0]
    outside = {**params, first.name: float(first.max_val) * 10}  # type: ignore[arg-type]
    ckpt = _write_checkpoint(
        offline.root / "p" / "CASCODE-OTA_TwoPointsDE_10_trial3_CRASH_x.json",
        [_entry(params, -3.0, {}), _entry(outside, -2.0, {}), _entry(params, float("nan"), {})],
    )
    with caplog.at_level(logging.INFO, logger="spicexplorer"):
        result = run(
            EXAMPLE_YAML,
            budget=5,
            algo="TwoPointsDE",
            outdir=offline.root / "out",
            verbose=False,
            resume=ckpt,
            checkpoint_dir=offline.root / "b",
        )
    assert result.n_trials == 5 and steps.n == 2
    first_ask = next(i for i, (kind, _) in enumerate(ng_spy.events) if kind == "ask")
    assert [kind for kind, _ in ng_spy.events[:first_ask]] == ["tell"]
    assert f"prior trial 2: {first.name}=" in caplog.text and "outside its bounds" in caplog.text
    assert "prior trial 3: score nan is not finite; not told" in caplog.text
    assert "told the optimizer 1 of the 3 prior trial(s)" in caplog.text


def test_an_engine_with_no_tell_api_is_skipped_and_says_so(caplog):
    from spicexplorer.optimization.base import Base_Optimizer

    class _NoTell:  # the base default, called on a stand-in carrying only what it reads
        _tell_prior_trials = Base_Optimizer._tell_prior_trials

    with caplog.at_level(logging.INFO, logger="spicexplorer"):
        assert _NoTell()._tell_prior_trials([object(), object()]) == 0  # type: ignore[list-item]
    assert "cannot be told the 2 prior trial(s)" in caplog.text and "afresh" in caplog.text


@pytest.mark.ax
def test_ax_is_told_every_prior_trial_and_names_its_checkpoints_bayesian_ax(
    offline, steps, monkeypatch
):
    """Ax: `attach_trial` + `complete_trial` once per prior trial before the first
    `get_next_trials`, each attached point the prior trial's own; the checkpoint names start
    `<project>_bayesian_ax_` even with `optimizer_config.name: NGOpt`."""
    from _spicexplorer_fixtures import require_ax

    require_ax()
    from ax.api.client import Client  # pyright: ignore[reportMissingImports]

    a = offline.root / "a"
    _crash_run(offline, steps, a, crash_at=4)  # 3 prior trials, Nevergrad
    prior = [
        e["point"]
        for e in json.loads(next(a.glob("*_CRASH_*.json")).read_text())["optimization_log"]
    ]
    events: list[tuple[str, Any]] = []
    real_attach, real_complete, real_next = (
        Client.attach_trial,
        Client.complete_trial,
        Client.get_next_trials,
    )

    def attach(self, parameters, arm_name=None):
        idx = real_attach(self, parameters=parameters, arm_name=arm_name)
        events.append(("attach", (idx, dict(parameters))))
        return idx

    def complete(self, trial_index, raw_data=None, progression=None):
        events.append(("complete", (trial_index, dict(raw_data or {}))))
        return real_complete(
            self, trial_index=trial_index, raw_data=raw_data, progression=progression
        )

    def next_trials(self, *args, **kwargs):
        events.append(("next", None))
        return real_next(self, *args, **kwargs)

    monkeypatch.setattr(Client, "attach_trial", attach)
    monkeypatch.setattr(Client, "complete_trial", complete)
    monkeypatch.setattr(Client, "get_next_trials", next_trials)
    built_opts: list[Any] = []
    real_get = Circuit_Optimizer_Orchestrator_with_SPICE.get_optimizer
    monkeypatch.setattr(
        Circuit_Optimizer_Orchestrator_with_SPICE,
        "get_optimizer",
        lambda self: built_opts.append(real_get(self)) or built_opts[-1],
    )

    b = offline.root / "b"
    result = run(
        EXAMPLE_YAML,
        budget=5,
        algo="NGOpt",
        engine="bayesian_ax",
        outdir=offline.root / "outb",
        verbose=False,
        resume=a,
        checkpoint_dir=b,
    )

    assert result.optimizer == "bayesian_ax" and result.n_trials == 5
    first_next = next(i for i, (kind, _) in enumerate(events) if kind == "next")
    before = events[:first_next]
    assert [kind for kind, _ in before] == ["attach", "complete"] * 3
    opt = built_opts[-1]
    for (_, (idx, coords)), (_, (cidx, raw)), point in zip(before[::2], before[1::2], prior):
        assert cidx == idx and raw["score"] == pytest.approx(point["score"], rel=1e-12)
        for name, v in opt.denormalize_params(coords).items():
            assert float(v) == pytest.approx(float(point["params"][name]), rel=1e-9), name
    assert _names(b) == ["CASCODE-OTA_bayesian_ax_5_trial5_FINAL.json"]
    assert _names(a)[0].startswith("CASCODE-OTA_TwoPointsDE_10_trial")


def test_the_chunk_order_puts_a_crash_file_at_the_trial_it_ended_on(tmp_path):
    """`trial<N>_CRASH` / `_FINAL` hold trials up to N-1: they sort after a plain chunk N-1 and
    before a chunk N (a resumed segment's first chunk), also across a digit-count change."""
    from spicexplorer.optimization.summary import _chunk_order

    names = [
        "r_10_trial10_CRASH_2026-01-01_00-00-00.json",
        "r_10_trial4_2026-01-01_00-00-00.json",
        "r_10_trial9_2026-01-01_00-00-00.json",
        "r_10_trial4_CRASH_2026-01-01_00-00-00.json",
        "r_10_trial3_2026-01-01_00-00-00.json",
        "r_10_trial12_FINAL_2026-01-01_00-00-00.json",
        "r_10_trial11_2026-01-01_00-00-00.json",
        "notes.json",
    ]
    assert sorted((tmp_path / n for n in names), key=_chunk_order) == [
        tmp_path / n
        for n in (
            "notes.json",
            "r_10_trial3_2026-01-01_00-00-00.json",
            "r_10_trial4_CRASH_2026-01-01_00-00-00.json",
            "r_10_trial4_2026-01-01_00-00-00.json",
            "r_10_trial9_2026-01-01_00-00-00.json",
            "r_10_trial10_CRASH_2026-01-01_00-00-00.json",
            "r_10_trial11_2026-01-01_00-00-00.json",
            "r_10_trial12_FINAL_2026-01-01_00-00-00.json",
        )
    ]
