"""Ax-backend revival + area/power integration tests (no SPICE).

Mirrors ``test_smoke_optimization.py``'s no-SPICE pattern: every optimizer here is built with
an EMPTY ``spicelib_wrappers`` dict, so ``parameterize()`` / ``denormalize_params()`` /
``_create_optimizer_obj()`` exercise the full proposer path without running ngspice. The Ax
cases are gated on the optional ``ax`` extra (Python 3.11+); they skip cleanly where it is
absent. Live end-to-end scoring is covered by the container-only demo (`examples/ax_area_power`).
"""
import pytest
from _spicexplorer_fixtures import REPO_ROOT
from spicexplorer.core.domains import Project_Setup

BASELINE_YAML = REPO_ROOT / "examples/ax_area_power/amp_020_baseline.yaml"
AREA_POWER_YAML = REPO_ROOT / "examples/ax_area_power/amp_020_area_power.yaml"


def _searched_frozen(setup):
    searched = [p for p in setup.dut_params if not p.freeze]
    frozen = [p for p in setup.dut_params if p.freeze]
    return searched, frozen


def _assert_denorm_in_bounds(setup, denorm):
    byname = {p.name: p for p in setup.dut_params}
    for name, v in denorm.items():
        p = byname[name]
        if p.freeze:
            continue
        lo, hi = float(p.min_val), float(p.max_val)
        assert lo - 1e-18 <= float(v) <= hi + 1e-18, (name, float(v), lo, hi)


# ── engine selection — no ax required ──────────────────────────────────

def test_optimizer_type_from_config_resolves_engine():
    from spicexplorer.optimization.orchestrator import (
        Optimizer_Type_Enum,
        optimizer_type_from_config,
    )

    setup = Project_Setup.from_yaml(BASELINE_YAML)
    assert optimizer_type_from_config(setup) == Optimizer_Type_Enum.NEVERGRAD_SINGLE
    setup.optimizer_config.type = "bayesian_ax"
    assert optimizer_type_from_config(setup) == Optimizer_Type_Enum.AX_SINGLE


@pytest.mark.parametrize("bad", ["nope", "reinforcement_learning"])
def test_optimizer_type_from_config_fails_loud(bad):
    from spicexplorer.optimization.orchestrator import optimizer_type_from_config

    setup = Project_Setup.from_yaml(BASELINE_YAML)
    setup.optimizer_config.type = bad
    with pytest.raises(ValueError):
        optimizer_type_from_config(setup)


# ── area/power specs load + derived-metric context (no ax, no SPICE) ──────────

def test_area_power_yaml_specs_and_derived_context():
    from spicexplorer.optimization.derived_integration import DerivedMetricContext

    setup = Project_Setup.from_yaml(AREA_POWER_YAML)
    names = setup.optimizer_config.target_specs.list_target_names()
    assert {"power", "active_area"}.issubset(set(names))

    # the power spec carries a Tier-1 recipe; active_area a param-derived one
    by = {t.name: t for t in setup.optimizer_config.target_specs.targets}
    assert by["power"].has_python_measurement()
    assert by["active_area"].has_derived_measurement()

    # active_area is now scored by the recursive NETLIST WALK (no `devices:` list) — build with
    # the resolved DUT deck so the walk can discover every transistor.
    from pathlib import Path

    deck = Path(setup.ws_root) / setup.netlist
    ctx = DerivedMetricContext.build(setup.optimizer_config.target_specs, netlist_path=deck)
    assert ctx is not None and ctx.spec_names == frozenset({"active_area"})
    # With the deck's own default sizing, every device resolves and area is a positive µm² number.
    frozen_only = {p.name: float(p.val) for p in setup.dut_params
                   if p.freeze and p.val is not None}
    rep = ctx.report(frozen_only)
    assert rep["transistor_count"] == 10 and rep["coverage"]["complete"]  # all 10, incl. XM9/XM10
    assert ctx.compute(frozen_only)["active_area"] == pytest.approx(20.8, rel=1e-3)


def test_baseline_yaml_has_no_derived_context():
    from spicexplorer.optimization.derived_integration import DerivedMetricContext

    setup = Project_Setup.from_yaml(BASELINE_YAML)
    assert DerivedMetricContext.build(setup.optimizer_config.target_specs) is None


# ── Ax parameterize / denorm parity (gated on the ax extra) ───────────────────

def test_ax_parameterize_excludes_frozen_and_denorm_in_bounds():
    pytest.importorskip("ax")
    from spicexplorer.optimization.stochastic.bayesian_ax import Ax_Spice_Single_Objective

    setup = Project_Setup.from_yaml(AREA_POWER_YAML)
    searched, frozen = _searched_frozen(setup)

    opt = Ax_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    cfgs = opt.parameterize()
    assert len(cfgs) == len(searched), "Ax search space must exclude frozen params"
    assert set(opt._frozen_params) == {
        p.name for p in frozen if (p.val is not None or p.init is not None)
    }

    # pull a real Ax candidate, denormalize, re-inject frozen
    assert opt._create_optimizer_obj()
    trials = opt.optimizer.get_next_trials(max_trials=1)
    cand = next(iter(trials.values()))
    denorm = opt._reinject_frozen_params(opt.denormalize_params(cand))

    _assert_denorm_in_bounds(setup, denorm)
    assert set(denorm) == {p.name for p in setup.dut_params}
    for p in frozen:
        if p.val is not None:
            assert float(denorm[p.name]) == pytest.approx(float(p.val))


def test_ax_integer_and_log_param_types():
    """Integer params → Ax int ranges over physical bounds; log params → log-scaled float
    ranges over the log box (parity with Nevergrad's coordinate convention)."""
    pytest.importorskip("ax")
    from spicexplorer.optimization.stochastic.bayesian_ax import Ax_Spice_Single_Objective

    setup = Project_Setup.from_yaml(BASELINE_YAML)
    # promote one param to integer and one to log-scale to exercise both branches
    by = {p.name: p for p in setup.dut_params}
    by["x_dut_xm1_w"].is_integer = True
    by["x_dut_xm1_w"].min_val, by["x_dut_xm1_w"].max_val = 1, 8
    by["i_bias"].log_scale = True

    opt = Ax_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    cfgs = {c.name: c for c in opt.parameterize()}
    assert cfgs["x_dut_xm1_w"].parameter_type == "int"
    assert tuple(cfgs["x_dut_xm1_w"].bounds) == (1, 8)  # physical integer range
    assert cfgs["i_bias"].scaling == "log"
    log_lo, log_hi = setup.optimizer_config.get_log_min_max()
    assert tuple(cfgs["i_bias"].bounds) == (log_lo, log_hi)


# ── backend equivalence: same YAML, both engines, same contract ───────────────

def test_backend_equivalence_search_space_and_frozen():
    """Nevergrad and Ax, built from the SAME YAML, expose the SAME searched-param set and the
    SAME frozen map, and both denormalize into bounds — the engine-swap guarantee."""
    pytest.importorskip("ax")
    from spicexplorer.optimization.stochastic.bayesian_ax import Ax_Spice_Single_Objective
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

    setup = Project_Setup.from_yaml(AREA_POWER_YAML)
    searched, _ = _searched_frozen(setup)
    searched_names = {p.name for p in searched}

    ng_opt = Nevergrad_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    ng_space = ng_opt.parameterize()
    assert set(ng_space.keys()) == searched_names

    ax_opt = Ax_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    ax_cfgs = ax_opt.parameterize()
    assert {c.name for c in ax_cfgs} == searched_names

    # identical frozen contract
    assert ng_opt._frozen_params == ax_opt._frozen_params


# ── review fixes: derived-metric robustness + OCEAN tier filter ───────────────

def test_derived_metric_netlist_mode_resolves_partial_vector_and_overrides():
    """A bare `evaluate()` (manual sim / sensitivity) may pass only the SEARCHED knobs. In
    netlist-walk mode the un-passed symbols (frozen multipliers, tied twins) resolve from the
    DECK's own `.param` block, so a partial vector still scores a FINITE area — strictly more
    robust than the old hand-list path, which NaN'd on any absent symbol. Overrides that ARE
    passed still win and flow through the deck's ties. No SPICE needed."""
    from pathlib import Path

    from spicexplorer.optimization.derived_integration import DerivedMetricContext
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

    setup = Project_Setup.from_yaml(AREA_POWER_YAML)
    opt = Nevergrad_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    assert opt._frozen_param_defaults()["x_dut_xm1_m"] == 1.0  # frozen multipliers still available

    deck = Path(setup.ws_root) / setup.netlist
    ctx = DerivedMetricContext.build(setup.optimizer_config.target_specs, netlist_path=deck)
    assert ctx is not None

    partial = {p.name: 2e-6 for p in setup.dut_params if not p.freeze}  # searched knobs only
    area_partial = ctx.compute(partial)["active_area"]
    assert area_partial > 0.0  # finite — deck .param fills the symbols not in the partial vector

    # An override on a searched knob (XM5 width) changes the area AND drags its tied twin XM9
    # (x_dut_xm9_w = {x_dut_xm5_w}) along — both grow, so the total moves.
    bigger = ctx.compute({**partial, "x_dut_xm5_w": 20e-6})["active_area"]
    assert bigger > area_partial


def test_ocean_build_recipes_skips_python_and_derived_recipes():
    """`ocean_integration.build_recipes` must pick up ONLY OCEAN-tier recipes; a Tier-1 `{meas}`
    or param-derived `{derived}` spec on a `sim_engine: spectre` run must be skipped (else it is
    fed to the OCEAN builder and KeyErrors on the missing `result`)."""
    from spicexplorer.core.domains import ListTargetSpec, TargetSpec
    from spicexplorer.optimization.ocean_integration import build_recipes

    specs = ListTargetSpec([
        TargetSpec(name="pm_py", testbench="tb", target=60, goal="exact", sim_type="ac",
                   measurement={"meas": "pm", "out": "out"}),
        TargetSpec(name="area", testbench="tb", target=4, goal="minimize", sim_type="op",
                   measurement={"derived": "active_area", "devices": [{"w": "w", "l": "l"}]}),
    ])
    assert build_recipes(specs) == {}  # neither is OCEAN-tier → no wiring, no KeyError


# ── batched Ax generation (max_trials > 1): budget-preserving, serial-parity default ──────────

def _make_ax_opt(batch_size=None):
    pytest.importorskip("ax")
    from spicexplorer.optimization.stochastic.bayesian_ax import Ax_Spice_Single_Objective

    setup = Project_Setup.from_yaml(BASELINE_YAML)
    if batch_size is not None:
        setup.optimizer_config.optimizer_kwargs = {"batch_size": batch_size}
    opt = Ax_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    opt.parameterize()
    assert opt._create_optimizer_obj()
    return opt


def test_ax_batch_size_reads_optimizer_kwargs():
    assert _make_ax_opt()._ax_batch_size() == 1            # default = serial parity
    assert _make_ax_opt(4)._ax_batch_size() == 4
    assert _make_ax_opt(0)._ax_batch_size() == 1           # clamped to >= 1
    assert _make_ax_opt("nope")._ax_batch_size() == 1      # non-int → 1


def _spy_and_stub(opt, monkeypatch):
    """Count get_next_trials calls and stub evaluate (no SPICE). Returns the call counter."""
    import numpy as np
    calls = {"gen": 0}
    real_get = opt.optimizer.get_next_trials

    def counting_get(*a, **k):
        calls["gen"] += 1
        return real_get(*a, **k)

    monkeypatch.setattr(opt.optimizer, "get_next_trials", counting_get)
    score = iter(range(1, 999))
    monkeypatch.setattr(opt, "evaluate", lambda parameterization: (np.float64(next(score)), {}))
    return calls


def test_ax_batched_generation_drains_one_trial_per_step(monkeypatch):
    """A batch_size=3 run pulls all three candidates in ONE generation call, then drains one per
    base-loop step — so budget still counts individual trials and best-tracking is per-step."""
    opt = _make_ax_opt(3)
    calls = _spy_and_stub(opt, monkeypatch)

    names = {c.name for c in (opt.parametrization or [])}
    for _ in range(3):
        params, _score, _meta = opt.optimization_step()
        assert set(params) == names            # a coordinate-space candidate each step
    assert calls["gen"] == 1                    # all three came from ONE get_next_trials(max_trials=3)
    assert opt._trial_queue == []               # fully drained

    opt.optimization_step()                     # a 4th step starts the next batch
    assert calls["gen"] == 2


def test_ax_batch_size_one_generates_each_step(monkeypatch):
    """batch_size=1 is exact serial parity — one generation call per step."""
    opt = _make_ax_opt(1)
    calls = _spy_and_stub(opt, monkeypatch)
    for _ in range(3):
        opt.optimization_step()
    assert calls["gen"] == 3


def test_nevergrad_ignores_batch_size_kwarg():
    """`batch_size` is Ax-only; a YAML shared between backends that carries it must NOT break
    Nevergrad — its registry presets (NGOpt) reject unknown kwargs, so the backend strips it."""
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

    setup = Project_Setup.from_yaml(BASELINE_YAML)
    setup.optimizer_config.optimizer_kwargs = {"batch_size": 3}
    opt = Nevergrad_Spice_Single_Objective(setup_obj=setup, spicelib_wrappers={})
    opt.parameterize()
    assert opt._create_optimizer_obj()  # constructs cleanly despite the Ax-only batch_size kwarg
