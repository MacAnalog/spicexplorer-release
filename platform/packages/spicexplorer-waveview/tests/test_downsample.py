"""Downsampling invariants: envelopes survive, endpoints stay, budgets hold."""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_waveview import downsample_indices, lttb_indices, minmax_indices


@pytest.fixture()
def spiky():
    rng = np.random.default_rng(42)
    x = np.linspace(0, 1, 100_000)
    y = np.sin(2 * np.pi * 5 * x) * 0.5
    spikes = rng.choice(y.size - 2, size=20, replace=False) + 1
    y[spikes] += 10.0  # glitches a naive stride would lose
    return x, y


def test_minmax_preserves_extremes(spiky):
    x, y = spiky
    idx = minmax_indices(y, 500)
    assert y[idx].max() == y.max()
    assert y[idx].min() == y.min()
    assert idx[0] == 0 and idx[-1] == y.size - 1
    assert len(idx) <= 502
    assert np.all(np.diff(idx) > 0)  # sorted unique


def test_minmax_small_input_passthrough():
    y = np.arange(10.0)
    assert minmax_indices(y, 100).size == 10


def test_lttb_endpoints_and_budget(spiky):
    x, y = spiky
    idx = lttb_indices(x, y, 500)
    assert idx[0] == 0 and idx[-1] == y.size - 1
    assert len(idx) <= 500
    assert np.all(np.diff(idx) > 0)


def test_lttb_passthrough_small():
    x = np.arange(5.0)
    assert lttb_indices(x, x, 100).size == 5


def test_stride_and_none(spiky):
    x, y = spiky
    idx = downsample_indices(x, y, 100, "stride")
    assert idx[0] == 0 and idx[-1] == y.size - 1 and len(idx) <= 100
    assert downsample_indices(x, y, 100, "none").size == y.size


def test_unknown_method_raises(spiky):
    x, y = spiky
    with pytest.raises(ValueError, match="unknown downsample method"):
        downsample_indices(x, y, 100, "bogus")
