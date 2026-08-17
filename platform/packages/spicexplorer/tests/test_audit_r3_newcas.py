"""Regression tests for the 2026-06 audit r3 **NEWCAS-core** majors (B5-B10).

These exercise the core library on the `examples/OTA/cascode` path — no ngspice / PDK / live sim:
- BUG-B5  base optimize() autosave reset no longer IndexErrors (log reset also resets best index).
- BUG-B6  denormalize_params maps the nevergrad bounds to [0,1] via (val-min)/range (lower offset kept).
- BUG-B7  a YAML `target` in XeY notation (parsed as str) is coerced; no crash on the tolerance fallback.
- BUG-B8  numeric `min_val >= max_val` is rejected at load (not only string-bound params).
- BUG-B9  a null / non-finite target-spec `weight` is coerced to 1.0 (was NaN-poisoning the score).
- BUG-B10 a frozen dut_param given only an eng-string `val`/`init` (no min/max) loads instead of crashing.
"""
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pytest
import yaml
from _spicexplorer_fixtures import REPO_ROOT
from spicexplorer.core.domains import Project_Setup, TargetSpec
from spicexplorer.optimization.base import Base_Optimizer

sys.path.insert(0, str(REPO_ROOT))

CASCODE_YAML = REPO_ROOT / "examples" / "OTA" / "cascode" / "ihp-sg13g2" / "sizing" / "project_setup.yaml"
pytestmark = pytest.mark.skipif(not CASCODE_YAML.exists(), reason="cascode example missing")


def _find(o, key):
    """Recursively locate a key's value in the nested YAML dict (returns the live object)."""
    if isinstance(o, dict):
        if key in o:
            return o[key]
        for v in o.values():
            r = _find(v, key)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = _find(v, key)
            if r is not None:
                return r
    return None


def _load_mutated(tmp_path: Path, mutate) -> Project_Setup:
    d = yaml.safe_load(CASCODE_YAML.read_text())
    mutate(d)
    p = tmp_path / "project_setup.yaml"
    p.write_text(yaml.safe_dump(d, sort_keys=False))
    return Project_Setup.from_yaml(p)


# ---------- BUG-B7: XeY string target ----------

def test_targetspec_string_target_is_parsed():
    spec = TargetSpec(name="ugf", testbench="tb", target="200e6", goal="exceed", sim_type="ac")
    assert not isinstance(spec.target, str)
    assert float(spec.target) == pytest.approx(200e6)
    # downstream arithmetic (value - target) must not raise on a once-string target
    _ = spec.get_simple_penalty(np.float64(1.0e8))


def test_eY_target_without_tolerance_loads(tmp_path):
    """An omitted tolerance must not crash on an `XeY` target that YAML 1.1 leaves as a STRING.

    The original bug was `abs(0.05 * target)` raising TypeError on that string. The default is
    now 0 rather than 5 % of target, so the multiply is gone — but the coercion it depended on
    still has to happen, because `target` itself is used in arithmetic everywhere downstream."""
    def mut(d):
        for s in _find(d, "target_specs"):
            s.pop("tolerance", None)
    proj = _load_mutated(tmp_path, mut)  # previously: TypeError can't multiply str
    ugf = next(s for s in proj.optimizer_config.target_specs.targets if s.name == "ugf")
    assert not isinstance(ugf.target, str)
    assert float(ugf.target) == pytest.approx(200e6)
    assert ugf.tolerance is not None and float(ugf.tolerance) == 0.0  # the default is exact


# ---------- BUG-B9: null / non-finite weight ----------

def test_null_weight_coerced_to_one():
    spec = TargetSpec(name="g", testbench="tb", target=1.0, goal="exceed", sim_type="ac", weight=None)
    assert spec.weight is not None and float(spec.weight) == 1.0
    assert np.isfinite(np.float64(spec.weight))


def test_nan_weight_coerced_to_one():
    spec = TargetSpec(name="g", testbench="tb", target=1.0, goal="exceed", sim_type="ac",
                      weight=float("nan"))
    assert spec.weight is not None and float(spec.weight) == 1.0


def test_explicit_weight_preserved():
    spec = TargetSpec(name="g", testbench="tb", target=1.0, goal="exceed", sim_type="ac", weight=2.5)
    assert spec.weight is not None and float(spec.weight) == 2.5


# ---------- BUG-B8: numeric min>=max rejected ----------

def test_numeric_inverted_range_rejected(tmp_path):
    def mut(d):
        dps = _find(d, "dut_params")
        dps[0]["min_val"] = 5      # plain numbers (previously skipped the min>=max check)
        dps[0]["max_val"] = 1
    with pytest.raises(ValueError):
        _load_mutated(tmp_path, mut)


def test_numeric_equal_min_max_rejected(tmp_path):
    def mut(d):
        dps = _find(d, "dut_params")
        dps[0]["min_val"] = 3
        dps[0]["max_val"] = 3
    with pytest.raises(ValueError):
        _load_mutated(tmp_path, mut)


def test_valid_example_still_loads(tmp_path):
    """The shipped example (mixed string-ref + numeric bounds) must still load unchanged."""
    proj = _load_mutated(tmp_path, lambda d: None)
    assert len(proj.dut_params) > 0


# ---------- BUG-B10: frozen eng-string constant, no bounds ----------

def test_frozen_eng_string_val_no_bounds_loads(tmp_path):
    def mut(d):
        _find(d, "dut_params").append({"name": "X_DUT_FROZEN_L", "freeze": True, "val": "0.18u"})
    proj = _load_mutated(tmp_path, mut)  # previously: ValueError "missing min or max value"
    frozen = next(p for p in proj.dut_params if p.name == "X_DUT_FROZEN_L")
    assert frozen.freeze is True
    assert frozen.val is not None and not isinstance(frozen.val, str)
    assert float(frozen.val) == pytest.approx(0.18e-6)


def test_frozen_eng_string_init_no_bounds_loads(tmp_path):
    def mut(d):
        _find(d, "dut_params").append({"name": "X_DUT_FROZEN_I", "freeze": True, "init": "50f"})
    proj = _load_mutated(tmp_path, mut)
    frozen = next(p for p in proj.dut_params if p.name == "X_DUT_FROZEN_I")
    assert frozen.init is not None and not isinstance(frozen.init, str)
    assert float(frozen.init) == pytest.approx(50e-15)


# ---------- BUG-B6 / B5: optimizer-level (no SPICE) ----------

class _NoopOpt(Base_Optimizer):
    """Concrete Base_Optimizer with no-op abstracts (mirrors test_ws_root_contract)."""
    def _create_optimizer_obj(self) -> bool:
        return True

    def parameterize(self) -> Any:
        return {}

    def evaluate(self, parameterization: Dict[str, float]) -> Tuple[np.floating, Dict[str, Any]]:
        return np.float64(0.0), {}

    def compute_fitness(self, performance_array):
        return np.float64(0.0), {}

    def optimization_step(self):
        return {}, np.float64(0.0), {}

    def plot_solution(self, parameterization, **kwargs):
        return None


def test_denormalize_keeps_lower_bound_offset_log(tmp_path):
    """A log-scale param's candidate at the bound endpoints must map exactly to [min_val, max_val]
    — i.e. the normalized coordinate is (val-min)/range, not val/range (BUG-B6)."""
    proj = Project_Setup.from_yaml(CASCODE_YAML)
    param = proj.dut_params[0]
    param.log_scale = True
    param.is_integer = False
    param.min_val = np.float64(1.8e-7)
    param.max_val = np.float64(1.0e-4)
    opt = _NoopOpt(proj, output_root=tmp_path / "ck")
    lb = proj.optimizer_config.log_variable_bounds
    lo = opt.denormalize_params({param.name: np.float64(lb.min)})[param.name]
    hi = opt.denormalize_params({param.name: np.float64(lb.max)})[param.name]
    assert float(lo) == pytest.approx(float(param.min_val), rel=1e-9)
    assert float(hi) == pytest.approx(float(param.max_val), rel=1e-9)


def test_denormalize_linear_endpoints(tmp_path):
    """Linear endpoints map to [min_val, max_val] too (regression: still correct when min==0)."""
    proj = Project_Setup.from_yaml(CASCODE_YAML)
    param = proj.dut_params[0]
    param.log_scale = False
    param.is_integer = False
    param.min_val = np.float64(2.0)
    param.max_val = np.float64(8.0)
    opt = _NoopOpt(proj, output_root=tmp_path / "ck")
    lb = proj.optimizer_config.lin_variable_bounds
    lo = opt.denormalize_params({param.name: np.float64(lb.min)})[param.name]
    hi = opt.denormalize_params({param.name: np.float64(lb.max)})[param.name]
    assert float(lo) == pytest.approx(2.0, rel=1e-9)
    assert float(hi) == pytest.approx(8.0, rel=1e-9)


class _CountingOpt(Base_Optimizer):
    """Appends one real log entry per step so the optimize() loop's indexing is exercised."""
    def _create_optimizer_obj(self) -> bool:
        self.optimizer = object()
        return True

    def parameterize(self) -> Any:
        return {}

    def evaluate(self, parameterization):
        return np.float64(0.0), {}

    def compute_fitness(self, performance_array):
        return np.float64(0.0), {}

    def optimization_step(self):
        from spicexplorer.core.domains import OptimizationLogEntry, OptimizationPoint
        # GLOBALLY increasing score (instance step counter, not len(log)) so the best is
        # well-defined across autosave resets and "new best" fires every trial.
        step = getattr(self, "_step", 0)
        self._step = step + 1
        score = np.float64(float(step))
        self.optimization_log.log.append(
            OptimizationLogEntry(point=OptimizationPoint(params={}, score=score), fit_summary={})
        )
        return {}, score, {}

    def plot_solution(self, parameterization, **kwargs):
        return None

    def save_checkpoint(self, name=None):  # no file IO in the test
        return None


def test_optimize_autosave_reset_does_not_indexerror(tmp_path):
    """budget > autosave cadence triggers a mid-loop log reset; previously the next index read of
    the now-empty log raised IndexError (BUG-B5)."""
    proj = Project_Setup.from_yaml(CASCODE_YAML)
    opt = _CountingOpt(proj, output_root=tmp_path / "ck")
    opt.optimizer_config.budget = 12
    opt.autosave_checkpoint_freqeucny = 5  # resets at trial 4 and 9
    log = opt.optimize()  # must NOT raise
    assert log is not None
    # best index is valid within the final in-memory chunk
    best = opt.get_best_params()
    assert best is not None


def test_optimize_best_survives_reset_on_boundary(tmp_path):
    """budget lands EXACTLY on an autosave boundary → the final in-memory log is empty, but the
    best must still be reported from the instance-tracked entry (BUG-B5; the case real SPICE hit)."""
    proj = Project_Setup.from_yaml(CASCODE_YAML)
    opt = _CountingOpt(proj, output_root=tmp_path / "ck")
    opt.optimizer_config.budget = 6
    opt.autosave_checkpoint_freqeucny = 3  # resets at trial 2 AND trial 5 (the last) → empty chunk
    log = opt.optimize()
    assert log is not None and len(log) == 0  # final chunk emptied by the boundary reset
    best = opt.get_best_params()
    assert best is not None, "best lost when the run ends on a reset boundary"
    _params, score, _meta = best
    assert float(score) == 5.0  # strictly-increasing scores → trial 5 (score 5) is the global best


def test_optimize_runs_clean_without_autosave_reset(tmp_path):
    """Sanity: a budget below the cadence (no reset) still completes and tracks a best."""
    proj = Project_Setup.from_yaml(CASCODE_YAML)
    opt = _CountingOpt(proj, output_root=tmp_path / "ck")
    opt.optimizer_config.budget = 4
    opt.autosave_checkpoint_freqeucny = 100
    log = opt.optimize()
    assert log is not None and len(log) == 4
    assert opt.global_best_index == 3  # strictly-increasing scores → last entry is best
