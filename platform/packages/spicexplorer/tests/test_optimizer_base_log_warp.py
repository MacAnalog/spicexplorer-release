"""OPT-03 regression: a ``log_scale`` dut_param is warped ONCE, in both backends.

Nevergrad (``ng.p.Log``) and Ax (``scaling="log"``) already sample the candidate log-uniformly in
the log box ``[log_bounds.min, log_bounds.max]``. ``denormalize_params`` used to map that value
LINEARLY to ``x = (val - min) / range`` and then apply ``log_denormalize`` again, so a log param's
physical distribution piled up at ``min_val`` (~3/4 of the samples in the lowest of three decades,
median ~1.9e-6 on ``[1e-6, 1e-3]``). The coordinate is now the candidate's position in decades
across the log box, so the physical value is log-uniform over ``[min_val, max_val]``.

The deterministic tests run over the YAML's default box ``[1, 100]`` AND over boxes whose lower
edge is not 1 (``log10(min) != 0``): on ``[1, 100]`` a map that forgets the ``- log10(min)`` offset,
or hard-codes two decades, is indistinguishable from the correct one.

Library-level only: the optimizers are built with an empty ``spicelib_wrappers`` dict (no sim).
"""

from __future__ import annotations

from typing import Any, cast

import numpy as np
import pytest
from _spicexplorer_fixtures import EXAMPLE_YAML, require_ax
from spicexplorer.core.domains import Param, Project_Setup, VariableBoundConfig

pytestmark = pytest.mark.skipif(not EXAMPLE_YAML.exists(), reason="cascode example missing")

P_MIN, P_MAX = 1e-6, 1e-3  # three decades

# None = the example YAML's own log box ([1, 100]); the others move log10(min) off zero and change
# the number of decades (3, and a fractional 0.6).
LOG_BOXES = [None, (10.0, 1e4), (0.5, 2.0)]


def _log_setup(box: tuple[float, float] | None = None) -> tuple[Project_Setup, Param]:
    """The cascode example with its first searched, non-integer param promoted to log scale."""
    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    if box is not None:
        proj.optimizer_config.log_variable_bounds = VariableBoundConfig(min=box[0], max=box[1])
    param = next(p for p in proj.dut_params if not p.freeze and not p.is_integer)
    param.log_scale = True
    param.min_val = np.float64(P_MIN)
    param.max_val = np.float64(P_MAX)
    return proj, param


def _ng(proj: Project_Setup):
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

    return Nevergrad_Spice_Single_Objective(setup_obj=proj, spicelib_wrappers={})


def _decade_fractions(values: np.ndarray) -> np.ndarray:
    decades = np.log10(values)
    return np.array(
        [
            np.mean(decades < -5),
            np.mean((decades >= -5) & (decades < -4)),
            np.mean(decades >= -4),
        ]
    )


@pytest.mark.parametrize("box", LOG_BOXES, ids=["yaml-1-100", "10-1e4", "0.5-2"])
def test_log_box_geometric_midpoint_maps_to_physical_geometric_midpoint(box):
    """Deterministic core of the fix: the geometric midpoint of the log box ([1,100] → 10) is the
    geometric midpoint of [min_val, max_val] (sqrt(1e-6*1e-3) ≈ 3.16e-5). The double warp gave
    ≈ 1.87e-6; the box endpoints still map exactly onto the physical bounds (BUG-B6)."""
    proj, param = _log_setup(box)
    opt = _ng(proj)
    lo, hi = proj.optimizer_config.get_log_min_max()
    mid = float(np.sqrt(lo * hi))
    phys = {
        v: float(opt.denormalize_params({param.name: np.float64(v)})[param.name])
        for v in (lo, mid, hi)
    }
    assert phys[mid] == pytest.approx(np.sqrt(P_MIN * P_MAX), rel=1e-9)
    assert phys[lo] == pytest.approx(P_MIN, rel=1e-9)
    assert phys[hi] == pytest.approx(P_MAX, rel=1e-9)


@pytest.mark.parametrize("box", LOG_BOXES, ids=["yaml-1-100", "10-1e4", "0.5-2"])
def test_equal_decades_in_the_box_are_equal_decades_in_physical_units(box):
    """The map is log-linear end to end: a point ``f`` of the way across the box in decades lands
    ``f`` of the way across ``[min_val, max_val]`` in decades, for every ``f`` on a grid — and the
    result is strictly increasing and in bounds."""
    proj, param = _log_setup(box)
    opt = _ng(proj)
    lo, hi = proj.optimizer_config.get_log_min_max()
    fracs = np.linspace(0.0, 1.0, 13)
    box_vals = 10.0 ** (np.log10(lo) + fracs * (np.log10(hi) - np.log10(lo)))
    phys = np.array(
        [float(opt.denormalize_params({param.name: np.float64(v)})[param.name]) for v in box_vals]
    )
    np.testing.assert_allclose(np.log10(phys), np.log10(P_MIN) + fracs * 3.0, rtol=0, atol=1e-9)
    assert np.all(np.diff(phys) > 0)
    assert np.all((phys >= P_MIN * (1 - 1e-9)) & (phys <= P_MAX * (1 + 1e-9)))


def test_log_fix_leaves_linear_and_integer_params_on_their_own_maps():
    """One vector, three kinds of param: only the ``log_scale`` one takes the log-box coordinate;
    a linear param still maps linearly from the lin box and an integer passes through untouched."""
    proj, log_param = _log_setup()
    opt = _ng(proj)
    lin_param = next(
        p for p in proj.dut_params if not p.freeze and not p.is_integer and not p.log_scale
    )
    int_param = next(p for p in proj.dut_params if p.is_integer)
    lin_lo, lin_hi = proj.optimizer_config.get_lin_min_max()
    lo, hi = proj.optimizer_config.get_log_min_max()
    lin_val = lin_lo + 0.25 * (lin_hi - lin_lo)
    out = opt.denormalize_params(
        {
            log_param.name: np.float64(np.sqrt(lo * hi)),
            lin_param.name: np.float64(lin_val),
            int_param.name: 3,
        }
    )
    assert float(out[log_param.name]) == pytest.approx(np.sqrt(P_MIN * P_MAX), rel=1e-9)
    lmin, lmax = float(lin_param.min_val), float(lin_param.max_val)  # type: ignore[arg-type]
    assert float(out[lin_param.name]) == pytest.approx(lmin + 0.25 * (lmax - lmin), rel=1e-12)
    assert out[int_param.name] == 3


def test_denormalize_rejects_an_unknown_param_name():
    """The rewritten setup lines sit above the name lookup; an unknown key still raises KeyError
    rather than being silently mapped or dropped."""
    proj, _param = _log_setup()
    with pytest.raises(KeyError, match="NOT_A_PARAM"):
        _ng(proj).denormalize_params({"NOT_A_PARAM": np.float64(1.0)})


def test_nevergrad_log_param_samples_are_log_uniform_and_in_bounds():
    """3000 seeded draws from the Nevergrad parametrization, denormalized: each decade of
    [1e-6, 1e-3] holds ~1/3 of them (the double warp put ~0.76 in the lowest). One box only
    (~10 s); the other boxes are covered by the deterministic grid test above."""
    proj, param = _log_setup()
    opt = _ng(proj)
    space = opt.parameterize()
    space.random_state.seed(0)
    values = np.array(
        [float(opt.denormalize_params(space.sample().value)[param.name]) for _ in range(3000)]
    )
    assert np.all((values >= P_MIN * (1 - 1e-9)) & (values <= P_MAX * (1 + 1e-9)))
    np.testing.assert_allclose(_decade_fractions(values), 1 / 3, atol=0.05)


@pytest.mark.ax
def test_ax_log_param_sobol_trials_are_log_uniform_and_in_bounds():
    """Same property on the Ax path: its Sobol trials over a ``scaling="log"`` range, run through
    the shared ``denormalize_params``, spread evenly over the three decades."""
    require_ax()
    from spicexplorer.optimization.stochastic.bayesian_ax import Ax_Spice_Single_Objective

    proj, param = _log_setup()
    proj.optimizer_config.random_seed = 0
    opt = Ax_Spice_Single_Objective(setup_obj=proj, spicelib_wrappers={})
    opt.parameterize()
    assert opt._create_optimizer_obj()
    trials = opt.optimizer.get_next_trials(max_trials=48)
    values = np.array(
        [
            float(opt.denormalize_params(cast("dict[str, float | np.floating]", c))[param.name])
            for c in trials.values()
        ]
    )
    assert len(values) == 48
    assert np.all((values >= P_MIN * (1 - 1e-9)) & (values <= P_MAX * (1 + 1e-9)))
    np.testing.assert_allclose(_decade_fractions(values), 1 / 3, atol=0.1)


def _suggested_init(proj: Project_Setup) -> dict[str, Any]:
    """Run ``_suggest_init_point`` against a capture stub; return the point it suggested."""
    opt = _ng(proj)
    opt.parameterize()
    suggested: dict[str, Any] = {}

    class _Capture:
        def suggest(self, point):
            suggested.update(point)

    opt.optimizer = _Capture()
    opt._suggest_init_point()
    return suggested


@pytest.mark.parametrize("box", LOG_BOXES, ids=["yaml-1-100", "10-1e4", "0.5-2"])
@pytest.mark.parametrize("init", [P_MIN, 4.7e-5, P_MAX])
def test_seed_from_init_point_round_trips_through_denormalize(box, init):
    """``_suggest_init_point`` is the inverse of ``denormalize_params``: the point it suggests for
    a log param's ``init`` must lie in the log box and denormalize back to that ``init`` (so the
    inverse must use the log-box coordinate), including at both physical bounds."""
    proj, param = _log_setup(box)
    param.init = np.float64(init)
    suggested = _suggested_init(proj)
    assert param.name in suggested
    lo, hi = proj.optimizer_config.get_log_min_max()
    assert lo * (1 - 1e-12) <= suggested[param.name] <= hi * (1 + 1e-12)
    back = _ng(proj).denormalize_params({param.name: suggested[param.name]})[param.name]
    assert float(back) == pytest.approx(init, rel=1e-9)


@pytest.mark.parametrize("box", LOG_BOXES, ids=["yaml-1-100", "10-1e4", "0.5-2"])
def test_seed_inverse_maps_the_geometric_midpoint_to_the_box_midpoint(box):
    """Checks the inverse on its own (a round trip alone passes if both directions share one
    mistake): the physical geometric midpoint seeds the log box's geometric midpoint."""
    proj, param = _log_setup(box)
    param.init = np.float64(np.sqrt(P_MIN * P_MAX))
    suggested = _suggested_init(proj)
    lo, hi = proj.optimizer_config.get_log_min_max()
    assert suggested[param.name] == pytest.approx(np.sqrt(lo * hi), rel=1e-9)
