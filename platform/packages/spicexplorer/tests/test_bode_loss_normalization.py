"""Bode-fit loss: the `min-max` normalizer must not divide by zero (O-5).

`weighted_mse_loss` / `weighted_mae_loss` scale the `min-max` branch by
``(max(target) - min(target)) ** 0.5``. Both functions already take an ``epsilon`` and
the sibling `z-score` branch clamps ``std`` with it, but the span was used raw — so a
FLAT target response (max == min), exactly what a broken candidate sizing or a
constant-magnitude target produces, returned inf/NaN and poisoned the ranking of every
candidate scored against it. The span is now clamped with the same ``epsilon``.
"""

from __future__ import annotations

import pytest

torch = pytest.importorskip(
    "torch", reason="the Bode loss path requires: pip install 'spicexplorer[torch]'"
)

from spicexplorer.core.utils import weighted_mae_loss, weighted_mse_loss  # noqa: E402

_LOSS_FNS = pytest.mark.parametrize(
    "loss_fn", [weighted_mse_loss, weighted_mae_loss], ids=["mse", "mae"]
)


def _flat_case(n: int = 8):
    """A flat target (max == min) against a non-matching response."""
    target = torch.full((n,), 3.0)
    response = torch.linspace(0.0, 1.0, n)
    weights = torch.ones(n)
    return response, target, weights


@_LOSS_FNS
def test_min_max_on_a_flat_target_is_finite(loss_fn):
    response, target, weights = _flat_case()
    loss, norm_params = loss_fn(response, target, weights, normalize_method="min-max")
    assert torch.isfinite(loss), f"flat target produced {loss}"
    assert loss > 0  # the candidate does NOT match the target — it must still be penalized
    assert norm_params == {"min": target.min(), "max": target.max()}


@_LOSS_FNS
def test_min_max_flat_target_respects_the_epsilon_argument(loss_fn):
    """The clamp uses the caller's `epsilon`, exactly like the z-score branch's std clamp:
    a 100x larger epsilon divides by a 10x larger sqrt -> a 10x smaller loss."""
    response, target, weights = _flat_case()
    tight, _ = loss_fn(response, target, weights, normalize_method="min-max", epsilon=1e-10)
    loose, _ = loss_fn(response, target, weights, normalize_method="min-max", epsilon=1e-8)
    assert torch.isfinite(tight) and torch.isfinite(loose)
    assert loose == pytest.approx(float(tight) / 10.0, rel=1e-6)


@_LOSS_FNS
def test_min_max_on_a_flat_target_still_orders_candidates(loss_fn):
    """The point of the clamp: a flat target must keep producing an ORDERABLE loss, so a
    closer candidate still outranks a worse one (inf == inf ranked them as equals)."""
    n = 8
    target = torch.full((n,), 3.0)
    weights = torch.ones(n)
    near, _ = loss_fn(torch.full((n,), 3.1), target, weights, normalize_method="min-max")
    far, _ = loss_fn(torch.full((n,), 9.0), target, weights, normalize_method="min-max")
    assert torch.isfinite(near) and torch.isfinite(far)
    assert near < far


@_LOSS_FNS
def test_min_max_on_a_non_flat_target_is_unchanged(loss_fn):
    """The clamp is inert whenever the span exceeds epsilon — pinned so the fix can't
    silently re-scale the healthy path."""
    target = torch.tensor([1.0, 2.0, 5.0, 10.0])
    response = torch.tensor([1.2, 2.4, 4.0, 9.0])
    weights = torch.ones(4)
    loss, _ = loss_fn(response, target, weights, normalize_method="min-max")
    span = (target.max() - target.min()) ** 0.5
    if loss_fn is weighted_mse_loss:
        expected = torch.mean(weights * (response - target) ** 2 / span)
    else:
        expected = torch.mean(weights * torch.abs(response - target) / span)
    assert loss == pytest.approx(float(expected), rel=1e-12)
