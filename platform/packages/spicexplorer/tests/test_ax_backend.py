"""Ax backend: the AX-5 integration tests, the ax-free tracking-metric helper, and the no-skip guard.

No SPICE anywhere: every optimizer is built with an EMPTY ``spicelib_wrappers`` dict and the
simulation (or the whole ``evaluate``) is stubbed, the ``test_smoke_optimization.py`` pattern.

  * **Tracking helper** (``optimization.ax_tracking``): pure numpy, NOT ``ax``-marked, so the fold
    of single- and multi-corner fit summaries into Ax's ``raw_data`` runs without the extra.
  * **AX-5** (``ax``-marked; ``uv sync --extra ax``, ``-m ax`` selects them):
    (a) 50 candidates per backend with integer/log/linear/frozen knobs: every one inside
    ``[min_val, max_val]``, frozen values exact, and the log knob at the same position in
    decades as its coordinate in the log box (OPT-03); the Nevergrad half needs no extra;
    (b) a 3-trial ``Ax_Spice_Constraint_Satisfaction`` run, single and multi-corner, hands Ax a
    tracking value for every spec;
    (c) Nevergrad and Ax checkpoints of one YAML share one schema and load into each other.
  * **No-skip guard**: every Ax case is ``ax``-marked and imports the backend through
    ``require_ax()``, which fails instead of skipping when the extra is installed (OPT-F1).
"""

import ast
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import _spicexplorer_fixtures as fixtures
import numpy as np
import pytest
from _spicexplorer_fixtures import REPO_ROOT, ax_extra_installed, require_ax
from spicexplorer.core.domains import Project_Setup
from spicexplorer.optimization.ax_tracking import extract_tracking_metrics

TESTS_DIR = Path(__file__).resolve().parent
BASELINE_YAML = REPO_ROOT / "examples/ax_area_power/amp_029_baseline.yaml"
FC_YAML = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml"


# ── the ax-free tracking-metric helper (no ax needed) ───────────────────────────────────────────

TARGETS = ("gain", "ugf", "pm")


def test_tracking_single_mode_reads_bare_spec_keys():
    fit = {
        "gain": {"curr_val": 60.0, "score": 0.1},
        "ugf": {"curr_val": 1.0e6, "score": -0.2},
        "pm": {"curr_val": 55.0, "score": 0.0},
    }
    raw = {"score": 1.5}
    out = extract_tracking_metrics(fit, TARGETS, save_in_dict=raw)
    assert out is raw  # the caller's raw_data, with its `score` objective kept
    assert out == {"score": 1.5, "gain": 60.0, "ugf": 1.0e6, "pm": 55.0}


def test_tracking_multi_mode_averages_each_spec_over_its_corners():
    fit = {
        "tt::gain": {"curr_val": 60.0},
        "ss::gain": {"curr_val": 40.0},
        "tt::pm": {"curr_val": 50.0},
        "ss::pm": {"curr_val": 70.0},
        "tt::ugf": {"curr_val": 2.0e6},
        "ss::ugf": {"curr_val": 1.0e6},
    }
    out = extract_tracking_metrics(fit, TARGETS, save_in_dict={})
    assert out == pytest.approx({"gain": 50.0, "pm": 60.0, "ugf": 1.5e6})


def test_tracking_skips_non_dict_missing_and_non_finite_values():
    """A per-corner total (not a dict) is skipped; a NaN corner drops out of its spec's mean; a
    spec with no finite value anywhere is left out rather than sent as NaN (Ax rejects NaN)."""
    fit = {
        "total": -3.2,
        "tt::gain": {"curr_val": math.nan},
        "ss::gain": {"curr_val": 40.0},
        "ugf": {"score": 0.0},
        "tt::pm": {"curr_val": None},
        "ss::pm": {"curr_val": math.inf},
    }
    assert extract_tracking_metrics(fit, TARGETS, save_in_dict={}) == {"gain": 40.0}


def test_tracking_ignores_names_that_are_not_target_specs():
    fit = {"gain": {"curr_val": 1.0}, "offset": {"curr_val": 2.0}, "tt::offset": {"curr_val": 3.0}}
    assert extract_tracking_metrics(fit, TARGETS, save_in_dict={}) == {"gain": 1.0}


def test_tracking_helper_imports_without_ax_or_torch():
    """The helper's point is that it needs no extra: importing it loads neither ax nor torch."""
    code = (
        "import sys, spicexplorer.optimization.ax_tracking; "
        "print(sorted(m for m in ('ax', 'botorch', 'torch') if m in sys.modules))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]"


# ── AX-5 (a): 50 candidates per backend, four kinds of knob ─────────────────────────────────────

N_CANDIDATES = 50
INT_KNOB, LOG_KNOB = "x_dut_xm1_w", "i_bias"
LOG_MIN, LOG_MAX = 1e-6, 1e-3  # three decades: a knob warped twice piles into the lowest one


def _four_flavor_setup() -> Project_Setup:
    """amp_029 baseline: linear knobs on a [0, 100] lin box and six frozen ones, plus one knob
    made an integer [1, 8] and ``i_bias`` made a three-decade log knob."""
    setup = Project_Setup.from_yaml(BASELINE_YAML)
    by = {p.name: p for p in setup.dut_params}
    by[INT_KNOB].is_integer = True
    by[INT_KNOB].min_val, by[INT_KNOB].max_val = np.float64(1), np.float64(8)
    by[LOG_KNOB].log_scale = True
    by[LOG_KNOB].min_val, by[LOG_KNOB].max_val = np.float64(LOG_MIN), np.float64(LOG_MAX)
    return setup


def _draw(opt, monkeypatch, n: int) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Run ``n`` real ``optimization_step``s with ``evaluate`` stubbed. Returns, per step, the
    coordinate-space candidate and the physical parameterization ``evaluate`` received."""
    seen: list[dict[str, Any]] = []

    def fake_evaluate(parameterization):
        seen.append(dict(parameterization))
        return np.float64(-len(seen)), {}

    monkeypatch.setattr(opt, "evaluate", fake_evaluate)
    draws = []
    for _ in range(n):
        coords, _score, _meta = opt.optimization_step()
        draws.append((dict(coords), seen[-1]))
    return draws


def _decades(value: float, lo: float, hi: float) -> float:
    return (math.log10(value) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))


def _assert_candidates(setup: Project_Setup, draws) -> None:
    cfg = setup.optimizer_config
    lin_lo, lin_hi = cfg.get_lin_min_max()
    box_lo, box_hi = cfg.get_log_min_max()
    params = {p.name: p for p in setup.dut_params}
    searched = {name for name, p in params.items() if not p.freeze}
    frozen = {name: float(p.val) for name, p in params.items() if p.freeze}  # type: ignore[arg-type]
    assert frozen and {INT_KNOB, LOG_KNOB} < searched and len(searched) > 2

    assert len(draws) == N_CANDIDATES
    for coords, phys in draws:
        assert set(coords) == searched  # frozen knobs are not in the search space ...
        assert set(phys) == searched | set(frozen)  # ... and are re-injected before evaluate
        for name, val in frozen.items():
            assert phys[name] == val, name  # exactly the YAML value, every trial
        for name in searched:
            lo, hi, v = float(params[name].min_val), float(params[name].max_val), float(phys[name])  # type: ignore[arg-type]
            assert lo * (1 - 1e-12) <= v <= hi * (1 + 1e-12), (name, v, lo, hi)
            if name == INT_KNOB:  # physical integer range, passed through unchanged
                assert v.is_integer() and v == float(coords[name])
            elif name == LOG_KNOB:  # the same position in decades on both sides of the map
                assert _decades(v, lo, hi) == pytest.approx(
                    _decades(float(coords[name]), box_lo, box_hi), abs=1e-9
                )
            else:
                assert (v - lo) / (hi - lo) == pytest.approx(
                    (float(coords[name]) - lin_lo) / (lin_hi - lin_lo), abs=1e-9
                )
    assert len({float(phys[LOG_KNOB]) for _, phys in draws}) > 1  # a spread, not one point


def test_nevergrad_candidates_in_bounds_with_log_coordinate(monkeypatch):
    """The Nevergrad half of the property; it needs no extra, so it is not ``ax``-marked."""
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

    setup = _four_flavor_setup()
    setup.optimizer_config.budget = N_CANDIDATES
    opt = Nevergrad_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    opt.parameterize()
    assert opt._create_optimizer_obj()
    _assert_candidates(setup, _draw(opt, monkeypatch, N_CANDIDATES))


def test_normalize_params_inverts_denormalize_for_every_knob_flavor(monkeypatch):
    """A resumed run tells the engine its prior trials by mapping their PHYSICAL params back to
    the search coordinates (#308): integer, log and linear knobs round-trip within 1e-9, frozen
    knobs are dropped, and a point outside a knob's bounds is refused."""
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

    setup = _four_flavor_setup()
    setup.optimizer_config.budget = 20
    opt = Nevergrad_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    opt.parameterize()
    assert opt._create_optimizer_obj()
    for coords, phys in _draw(opt, monkeypatch, 20):
        back = opt.normalize_params(phys)
        assert set(back) == set(coords)  # the frozen knobs in `phys` are not in the space
        for name, v in back.items():
            assert v == pytest.approx(float(coords[name]), rel=1e-9, abs=1e-12), name
    hi = float(next(p for p in setup.dut_params if p.name == LOG_KNOB).max_val)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match=f"{LOG_KNOB}=.* is outside its bounds"):
        opt.normalize_params({**phys, LOG_KNOB: hi * 2})


@pytest.mark.ax
def test_ax_candidates_in_bounds_with_log_coordinate(monkeypatch):
    """One ``get_next_trials(50)`` (``batch_size``) draw, so no surrogate is fitted; its Sobol
    points also spread the log knob evenly over its three decades."""
    require_ax()
    from spicexplorer.optimization.stochastic.bayesian_ax import Ax_Spice_Single_Objective

    setup = _four_flavor_setup()
    setup.optimizer_config.optimizer_kwargs = {"batch_size": N_CANDIDATES}
    opt = Ax_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    opt.parameterize()
    assert opt._create_optimizer_obj()
    draws = _draw(opt, monkeypatch, N_CANDIDATES)
    _assert_candidates(setup, draws)
    decade = np.floor(
        np.log10([float(phys[LOG_KNOB]) for _, phys in draws]) - math.log10(LOG_MIN)
    ).clip(0, 2)
    np.testing.assert_allclose(
        np.bincount(decade.astype(int), minlength=3) / N_CANDIDATES, 1 / 3, atol=0.15
    )


# ── AX-5 (b) + (c): 3-trial constraint-satisfaction runs on the folded-cascode YAML ─────────────

# Canned per-spec readings; each corner scales them, so a corner MEAN differs from every corner.
READING = {"ugf": 2.0e6, "dcgain": 60.0, "pm": 70.0}
CORNER_SCALE = {"tt_27C_1V8": 1.0, "ss_125C_1V62": 0.5}
SINGLE_SCALE = 0.8


class _FakeSimResult:
    """Structural ``SimResult``: every spec reads its canned value times the corner's scale."""

    def __init__(self, scale: float):
        self._scale = scale

    def scalar(self, name, analysis):
        return READING[name] * self._scale

    def wave(self, name, analysis):
        raise KeyError(name)


def _fc_setup(mode: str) -> Project_Setup:
    setup = Project_Setup.from_yaml(FC_YAML)
    setup.parallel_sim = False  # the sequential corner loop is the one that calls simulate_circuit
    assert setup.pvt is not None
    setup.pvt.mode = mode
    setup.optimizer_config.budget = 3
    assert [c.name for c in setup.pvt.corners_to_run()] == (
        list(CORNER_SCALE) if mode == "multi" else ["tt_27C_1V8"]
    )
    assert set(setup.optimizer_config.target_specs.list_target_names()) == set(READING)
    return setup


def _stub_sims(monkeypatch, opt, setup: Project_Setup) -> None:
    """Stub only the simulation, so the REAL ``evaluate`` builds the fit summary: bare spec keys
    in single mode, ``"<corner>::<spec>"`` in multi mode (where ``run_label`` is the corner)."""
    benches = {t.testbench for t in setup.optimizer_config.target_specs.enabled_targets()}

    def fake_simulate(parameterization, run_label=None):
        scale = SINGLE_SCALE if run_label is None else CORNER_SCALE[run_label]
        return {tb: _FakeSimResult(scale) for tb in benches}

    monkeypatch.setattr(opt, "simulate_circuit", fake_simulate)


@pytest.mark.ax
@pytest.mark.parametrize("mode", ["single", "multi"])
def test_ax_constraint_satisfaction_run_reports_every_spec_to_ax(mode, monkeypatch, tmp_path):
    """AX-3's exit through a real 3-trial ``optimize()``: every completed Ax trial carries the
    ``score`` objective AND a tracking value per spec (the corner mean in multi mode); the
    pre-B4 extractor sent Ax no tracking metric at all in multi mode."""
    require_ax()
    from ax.api.client import Client
    from ax.core.trial_status import TrialStatus
    from spicexplorer.optimization.stochastic.bayesian_ax import Ax_Spice_Constraint_Satisfaction

    completed: list[tuple[dict[str, Any], Any]] = []
    real_complete = Client.complete_trial

    def spy_complete(self, trial_index, raw_data=None, progression=None):
        status = real_complete(
            self, trial_index=trial_index, raw_data=raw_data, progression=progression
        )
        completed.append((dict(raw_data or {}), status))
        return status

    monkeypatch.setattr(Client, "complete_trial", spy_complete)

    setup = _fc_setup(mode)
    opt = Ax_Spice_Constraint_Satisfaction(
        setup_obj=setup, spicelib_wrappers={}, output_root=tmp_path
    )
    _stub_sims(monkeypatch, opt, setup)
    opt.parameterize()
    opt.optimize()

    scale = float(np.mean(list(CORNER_SCALE.values()))) if mode == "multi" else SINGLE_SCALE
    expected = {spec: value * scale for spec, value in READING.items()}
    assert len(completed) == len(opt.optimization_log) == 3
    for (raw, status), entry in zip(completed, opt.optimization_log):
        assert status == TrialStatus.COMPLETED
        assert entry.fit_summary
        assert all(("::" in key) == (mode == "multi") for key in entry.fit_summary)
        assert raw.pop("score") == pytest.approx(float(entry.point.score))
        assert raw == pytest.approx(expected)


def _entry_shape(entry: dict[str, Any]) -> dict[str, Any]:
    point = entry["point"]
    return {
        "entry": set(entry),
        "point": set(point),
        "params": set(point["params"]),
        "metadata": set(point["metadata"]),
        "fit_summary": set(entry["fit_summary"]),
        "per_spec": {frozenset(v) for v in entry["fit_summary"].values()},
    }


@pytest.mark.ax
def test_nevergrad_and_ax_checkpoints_of_one_yaml_share_one_schema(monkeypatch, tmp_path):
    """The engine-swap promise for checkpoints: the same multi-corner YAML run for 3 trials under
    each engine writes a ``_FINAL`` checkpoint with the same top-level keys and the same keys in
    every entry, and each checkpoint loads through the OTHER engine's class."""
    require_ax()
    from spicexplorer.optimization.stochastic.bayesian_ax import Ax_Spice_Constraint_Satisfaction
    from spicexplorer.optimization.stochastic.nevergrad import (
        Nevergrad_Spice_Constraint_Satisfaction,
    )

    engines = {
        "nevergrad": Nevergrad_Spice_Constraint_Satisfaction,
        "ax": Ax_Spice_Constraint_Satisfaction,
    }
    paths: dict[str, Path] = {}
    for engine, cls in engines.items():
        setup = _fc_setup("multi")
        opt = cls(setup_obj=setup, spicelib_wrappers={}, output_root=tmp_path / engine)
        _stub_sims(monkeypatch, opt, setup)
        opt.parameterize()
        opt.optimize()
        (paths[engine],) = (tmp_path / engine).glob("*_FINAL_*.json")
    ng, ax_ = (json.loads(paths[e].read_text()) for e in engines)

    assert set(ng) == set(ax_) == {"schema_version", "timestamp", "optimization_log"}
    assert ng["schema_version"] == ax_["schema_version"]
    assert len(ng["optimization_log"]) == len(ax_["optimization_log"]) == 3
    ng_shapes = [_entry_shape(e) for e in ng["optimization_log"]]
    assert ng_shapes == [_entry_shape(e) for e in ax_["optimization_log"]]
    setup = _fc_setup("multi")
    physical = {
        p.name for p in setup.dut_params if not p.freeze or p.val is not None or p.init is not None
    }
    assert ng_shapes[0]["params"] == physical  # physical knob names, frozen ones included
    assert ng_shapes[0]["fit_summary"] == {f"{c}::{s}" for c in CORNER_SCALE for s in READING}

    for source, cls in (
        ("nevergrad", Ax_Spice_Constraint_Satisfaction),
        ("ax", Nevergrad_Spice_Constraint_Satisfaction),
    ):
        loaded = cls.load_checkpoint(_fc_setup("multi"), paths[source], spicelib_wrappers={})
        assert [set(e.point.params) for e in loaded.optimization_log] == [physical] * 3


# ── the no-skip guard (OPT-F1) ──────────────────────────────────────────────────────────────────

_AX_REFERENCES = {"bayesian_ax", "require_ax"}


def _is_importorskip_ax(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and ast.unparse(node.func).endswith("importorskip")
        and bool(node.args)
        and isinstance(node.args[0], ast.Constant)
        and str(node.args[0].value).split(".")[0] == "ax"
    )


def _references(fn: ast.AST) -> set:
    """Every name, attribute and imported-module component ``fn`` uses."""
    names = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.ImportFrom):
            names.update((node.module or "").split("."))
        elif isinstance(node, ast.Import):
            names.update(part for alias in node.names for part in alias.name.split("."))
        if _is_importorskip_ax(node):
            names.add("bayesian_ax")
    return names


def _ax_cases(tree: ast.Module) -> dict[str, bool]:
    """``{test name: ax-marked}`` for every test that needs the Ax backend, directly or through a
    module-level helper that does (``_make_ax_opt`` in ``test_ax_area_power.py``)."""
    funcs = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    refs = {name: _references(fn) for name, fn in funcs.items()}
    needs_ax = {name for name, r in refs.items() if r & _AX_REFERENCES}
    while more := {name for name, r in refs.items() if name not in needs_ax and r & needs_ax}:
        needs_ax |= more
    module_marked = any(
        isinstance(n, ast.Assign)
        and "pytestmark" in {ast.unparse(t) for t in n.targets}
        and "pytest.mark.ax" in ast.unparse(n.value)
        for n in tree.body
    )

    def marked(fn) -> bool:
        return module_marked or any(
            ast.unparse(d.func if isinstance(d, ast.Call) else d) == "pytest.mark.ax"
            for d in fn.decorator_list
        )

    return {name: marked(funcs[name]) for name in needs_ax if name.startswith("test_")}


@pytest.mark.ax
def test_no_ax_case_can_skip_while_the_extra_is_installed():
    """OPT-F1's guard. Every Ax case in this package (i) carries ``@pytest.mark.ax``, so the
    ``-m ax`` selection runs all of them, and (ii) imports the backend through ``require_ax()``,
    which FAILS when ``ax-platform`` is installed but does not import; ``pytest.importorskip("ax")``
    would skip it. With the extra installed, the backend must import here too."""
    cases: dict[str, bool] = {}
    silent: list[str] = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        cases.update({f"{path.name}::{name}": m for name, m in _ax_cases(tree).items()})
        silent += [
            f"{path.name}:{n.lineno}"
            for n in ast.walk(tree)
            if isinstance(n, ast.Call) and _is_importorskip_ax(n)
        ]

    # The scan must see the known Ax cases, a direct one and one reached through a helper;
    # a scan that found nothing would pass vacuously.
    assert {
        "test_ax_area_power.py::test_ax_parameterize_excludes_frozen_and_denorm_in_bounds",
        "test_ax_area_power.py::test_ax_batch_size_reads_optimizer_kwargs",
        "test_ax_backend.py::test_ax_candidates_in_bounds_with_log_coordinate",
    } <= set(cases)
    assert (
        "test_ax_backend.py::test_nevergrad_candidates_in_bounds_with_log_coordinate" not in cases
    )
    assert not silent, (
        f"pytest.importorskip('ax') skips even with the extra installed; "
        f"call require_ax() instead: {silent}"
    )
    unmarked = sorted(case for case, is_marked in cases.items() if not is_marked)
    assert not unmarked, f"Ax cases outside the `-m ax` selection (add @pytest.mark.ax): {unmarked}"

    if ax_extra_installed():
        backend = require_ax()
        assert hasattr(backend, "Ax_Spice_Constraint_Satisfaction")
        assert hasattr(backend, "Ax_Spice_Single_Objective")


@pytest.mark.ax
@pytest.mark.parametrize(
    "installed, outcome",
    [(True, pytest.fail.Exception), (False, pytest.skip.Exception)],
    ids=["extra-installed-fails", "extra-absent-skips"],
)
def test_require_ax_fails_rather_than_skips_when_the_extra_is_installed(
    monkeypatch, installed, outcome
):
    """The guard's core, checked without a broken install: the backend import fails (a ``None``
    entry in ``sys.modules`` makes ``import`` raise), and ``require_ax()`` fails the test when
    ``ax-platform`` is installed and skips it only when it is not."""
    monkeypatch.setitem(sys.modules, fixtures.AX_BACKEND_MODULE, None)
    monkeypatch.setattr(fixtures, "ax_extra_installed", lambda: installed)
    with pytest.raises(outcome):
        fixtures.require_ax()
