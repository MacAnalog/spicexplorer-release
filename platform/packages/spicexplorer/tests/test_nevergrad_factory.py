"""create_optimizer construction contract (the Run-popover override failure).

A registry preset (e.g. ``LhsDE``) is pre-configured and rejects algorithmic
kwargs; a project YAML authored for a Family (``SamplingSearch`` +
``sampler=Hammersley``) combined with an ephemeral algorithm override used to
crash construction before a single trial ran. The factory now drops the kwargs
with a warning and constructs the preset bare.
"""
import nevergrad as ng
import pytest
from spicexplorer.optimization.stochastic.nevergrad import create_optimizer


def _param() -> ng.p.Dict:
    return ng.p.Dict(x=ng.p.Scalar(lower=0.0, upper=1.0))


def test_registry_preset_drops_rejected_kwargs():
    # The exact kwargs the SamplingSearch-configured examples carry.
    opt = create_optimizer(
        "LhsDE", _param(), budget=4,
        optimizer_kwargs={"sampler": "Hammersley", "scrambled": True, "rescaled": True},
    )
    assert opt is not None
    assert opt.budget == 4


def test_family_with_its_own_kwargs_still_constructs():
    opt = create_optimizer(
        "SamplingSearch", _param(), budget=4,
        optimizer_kwargs={"sampler": "Hammersley", "scrambled": True, "rescaled": True},
    )
    assert opt is not None


def test_unknown_algorithm_still_raises():
    with pytest.raises(ValueError, match="not found"):
        create_optimizer("NoSuchOptimizer", _param(), budget=4)


def test_rescaled_sampling_at_budget_1_yields_finite_candidates():
    # Nevergrad's Rescaler normalizes across the planned sample grid; with a
    # single sample it divides by zero and ask() returns NaN — which then lands
    # as `w=nan` in the SPICE deck (the "Run & open" budget-1 failure). The
    # factory must drop `rescaled` for budget < 2.
    import math

    opt = create_optimizer(
        "SamplingSearch", _param(), budget=1,
        optimizer_kwargs={"sampler": "Hammersley", "scrambled": True, "rescaled": True},
    )
    value = opt.ask().value
    assert all(math.isfinite(v) for v in value.values()), value
