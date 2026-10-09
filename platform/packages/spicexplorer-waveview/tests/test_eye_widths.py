"""The two eye widths, and why there are two.

`eye_w_ui_1s` counts the sampling phases at which every adjacent level pair is open, measured over a
+-ONE-SAMPLE window. `eye_w_ui_sample_window` counts the same thing over the +-SAMPLE_HALF_UI
window the eye HEIGHT statistic uses. They are different measurements of the same eye and the
second is always the stricter one; a design scored on one and compared against the other looks
like it changed when it did not.
"""

from __future__ import annotations

import numpy as np
from spicexplorer_waveview.eye import SAMPLE_HALF_UI, eye_metrics
from spicexplorer_waveview.stimulus import Data, ideal_waveform


def _ideal_eye(fmt: str = "nrz", rate_gbd: float = 10.0):
    d = Data(fmt=fmt, rate_gbd=rate_gbd, order=7, seed=1)
    t = np.arange(0.0, d.t0 + d.n * d.ui, d.ui / 400.0)
    return t, ideal_waveform(t, d), d


def test_both_widths_are_reported_and_the_sample_window_one_is_never_wider():
    t, x, d = _ideal_eye()
    m = eye_metrics(t, x, d, filtered=False)
    assert m["ok"] == 1
    assert 0.0 <= m["eye_w_ui_sample_window"] <= m["eye_w_ui_1s"] <= 1.0


def test_the_two_widths_actually_differ_on_an_ideal_eye():
    """If they agreed there would be no reason for two names -- and no trap to document."""
    t, x, d = _ideal_eye()
    m = eye_metrics(t, x, d, filtered=False)
    assert m["eye_w_ui_1s"] - m["eye_w_ui_sample_window"] > 0.05


def test_the_sample_window_width_matches_the_window_the_height_is_measured_over():
    """A phase counted open must have every level separated over the SAME +-0.1 UI span the
    height statistic uses, so a positive height at the best phase implies a positive width."""
    t, x, d = _ideal_eye()
    m = eye_metrics(t, x, d, filtered=False)
    assert SAMPLE_HALF_UI == 0.1
    assert m["eye_h_norm"] > 0 and m["eye_w_ui_sample_window"] > 0


def test_a_closed_eye_reports_both_widths_as_zero_rather_than_raising():
    t, x, d = _ideal_eye()
    m = eye_metrics(t, np.zeros_like(x), d, filtered=False)
    assert m["eye_w_ui_1s"] == 0.0 and m["eye_w_ui_sample_window"] == 0.0


def test_pam4_reports_both_widths_too():
    t, x, d = _ideal_eye(fmt="pam4")
    m = eye_metrics(t, x, d, filtered=False)
    assert m["ok"] == 1
    assert m["eye_w_ui_sample_window"] <= m["eye_w_ui_1s"]
    assert "rlm" in m


def test_bare_eye_w_ui_is_a_pinned_alias_of_the_wide_metric_not_a_third_measurement():
    """`eye_w_ui` has meant BOTH the wide and the strict metric in this module's design lineage
    (reuse review F2). Retiring it broke a live consumer (agentic-design-template's
    `tests/test_design.py`), so it stays -- but pinned to a SPECIFIC one of the two (the wide
    metric, `eye_w_ui_1s`) rather than left ambiguous. Both explicit names are still reported so
    a new reader never has to rely on the bare spelling."""
    t, x, d = _ideal_eye()
    m = eye_metrics(t, x, d, filtered=False)
    assert "eye_w_ui_1s" in m and "eye_w_ui_sample_window" in m
    assert m["eye_w_ui"] == m["eye_w_ui_1s"]


def test_sample_phase_count_is_a_parameter_and_is_recorded_in_the_result():
    """The sampling-phase count is not a hidden module constant: a caller can change it, and the
    value actually used rides in the result as `sample_phases` (reuse review F2)."""
    from spicexplorer_waveview.eye import PHASES

    t, x, d = _ideal_eye()
    default = eye_metrics(t, x, d, filtered=False)
    assert default["sample_phases"] == PHASES
    assert default["sample_half_ui"] == SAMPLE_HALF_UI

    coarse = eye_metrics(t, x, d, filtered=False, n_phases=10)
    assert coarse["sample_phases"] == 10
    # a coarser phase grid quantizes the same eye onto fewer possible width values
    assert coarse["eye_w_ui_1s"] in {k / 10 for k in range(11)}
