"""``runner.parse_measures`` is the platform's, not a third private copy — and losing nothing.

``spicexplorer_analog_db.runner`` used to carry its own ``_MEASURE``/``_FAILED`` regexes: the third
copy of the ngspice scalar-scrape rules, after ``spicexplorer_core.spice_engine.sim_log`` and the
waveform viewer's log panel (which already re-exports sim_log's). It is now a re-export of
sim_log's.

This module pins that. The first test is the one that matters: every line form the analog-db copy
used to handle must parse IDENTICALLY through the platform's, so the swap can't quietly drop a
measure the corpus depends on. The second records what the platform's regexes ADD, so a future
reader can see the swap was a widening and not a rewrite — including one form analog-db was
silently BLIND to (ngspice-45 reports a failed ``.meas`` as ``meas tran <name> … failed!``; the
old copy matched only the older ``<name> = failed`` line, so such a measure was neither recorded
nor reported as failed — it simply vanished).
"""

from __future__ import annotations

import math

import pytest
from spicexplorer_core.spice_engine import sim_log

from spicexplorer_analog_db import runner

# Every line form the retired analog-db copy accepted, drawn from its own regexes, its docstring
# examples, and the cases already asserted in test_robustness.py / test_tier2_analyses.py.
_LEGACY_CASES: list[tuple[str, dict[str, float], list[str]]] = [
    ("dcgain = 29.78", {"dcgain": 29.78}, []),
    ("ugf = 1e7", {"ugf": 1e7}, []),  # exponent without sign
    ("ugf = 1.5e+07", {"ugf": 1.5e7}, []),  # signed exponent
    ("vos = -1.2e-3", {"vos": -1.2e-3}, []),  # negative mantissa
    ("  pm   =   61.4  ", {"pm": 61.4}, []),  # whitespace variants
    ("dcgain              =  2.977862e+01", {"dcgain": 29.77862}, []),  # the real column layout
    ("ONOISE_TOTAL = 4.071369e-06", {"onoise_total": 4.071369e-06}, []),  # names lower-cased
    ("name = 4.8e-01 at=  4.34e-06", {"name": 0.48}, []),  # MIN/MAX/PP location tail
    ("v_line_pp = 5.492e-03 from= 1e-6 to= 2e-6", {"v_line_pp": 0.005492}, []),  # AVG/INTEG tail
    ("tcross              =  failed", {}, ["tcross"]),  # the failed-measure line
    ("ngspice chatter\nnothing here", {}, []),  # non-measure noise
    ("-i(v1) = 2.0", {}, []),  # `print <expression>` echoes the expression — NOT a measure
    ("i_ma*2 = 4.0", {}, []),
]


@pytest.mark.parametrize("text,measures,failed", _LEGACY_CASES)
def test_platform_parse_measures_handles_every_legacy_form(text, measures, failed) -> None:
    assert runner.parse_measures(text + "\n") == (measures, failed)


def test_runner_reexports_the_platform_implementation() -> None:
    """Not a copy that happens to agree — literally the same function object."""
    assert runner.parse_measures is sim_log.parse_measures


def test_platform_adds_forms_the_analog_db_copy_missed() -> None:
    """The widening, recorded. Each of these was invisible to the retired regexes."""
    # ngspice-45's failed-`.meas` report — the form analog-db could not see at all
    assert runner.parse_measures("meas tran tsettle when verr=2m fall=last failed!\n") == (
        {},
        ["tsettle"],
    )
    assert runner.parse_measures(".meas tran bad when v(a)=5 failed!\n") == ({}, ["bad"])
    # a trig/targ delay measure's location tail (the old copy accepted only at=/from=/to=)
    assert runner.parse_measures("tdelay = 1.2e-9 trig= 1e-9 targ= 2.2e-9\n") == (
        {"tdelay": 1.2e-9},
        [],
    )
    # dotted names
    assert runner.parse_measures("m.dot = 3.0\n") == ({"m.dot": 3.0}, [])
    # non-finite scalars come through as floats rather than being skipped, so `run_text`'s NaN
    # gate can see them instead of the metric silently going missing
    measures, _ = runner.parse_measures("x = nan\ny = inf\nz = -inf\n")
    assert math.isnan(measures["x"]) and measures["y"] == math.inf and measures["z"] == -math.inf


def test_fatal_lines_now_covers_both_markers_run_text_scans_for() -> None:
    """Platform 2430bfc closed both CONTAINMENT gaps — pinned so the history stays legible.

    These two used to return ``[]``: the lowercase ``fatal: ngspice timed out after …`` marker
    :func:`runner.native_pdk_runner` appends on timeout (``fatal_lines``' ``Fatal`` pattern was
    case-sensitive and line-anchored), and every ``cannot open`` form (no pattern at all).
    """
    assert sim_log.fatal_lines("fatal: ngspice timed out after 300s") != []
    assert sim_log.fatal_lines("cannot open file /opt/pdk/foo.lib") != []
    assert sim_log.fatal_lines("Error: cannot open output file") != []
    # and run_text's own scan still catches them, so the two agree on every real dead-run marker
    for line in (
        "fatal: ngspice timed out after 300s\n",
        "cannot open file /opt/pdk/foo.lib\n",
        "simulation interrupted\n",
    ):
        with pytest.raises(runner.SimError, match="ngspice error"):
            runner.run_text("deck", "<t>", runner=lambda _n, _l=line: _l)


def test_run_text_keeps_its_narrow_scan_because_fatal_lines_is_broader() -> None:
    """``fatal_lines`` is a superset, and that is exactly why it must NOT gate ``run_text``.

    It reports every error-level line, including the degenerate-sizing signatures this database
    treats as RECORDED FLOORS rather than dead runs (TESTING.md §3). Gating a recording on it
    would raise on a deck that still produced usable measures — marking the whole analysis
    ``sim_error`` so ``metric_values`` skips it and every SIBLING metric silently vanishes, the
    very leniency :func:`runner.run_text`'s failed-measure handling exists to prevent.
    """
    floor_lines = [
        "could not find a valid modelname",
        "singular matrix",
        "doAnalyses: iteration limit reached",
        "Transient solution failed",
        "timestep too small",
    ]
    for line in floor_lines:
        assert sim_log.fatal_lines(line) != [], f"{line!r} should be error-level for the log panel"

    # a floor line NEXT TO a good measure: run_text must still return the measure, not raise
    log = "could not find a valid modelname\ndcgain = 29.78\n"
    assert runner.run_text("deck", "<t>", runner=lambda _n: log) == {"dcgain": 29.78}
