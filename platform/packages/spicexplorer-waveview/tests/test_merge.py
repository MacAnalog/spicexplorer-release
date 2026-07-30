"""merge_datasets — several artifacts into one multi-analysis dataset.

Pure model-level semantics (no API): key collisions get stable ``#n`` suffixes,
provenance labels ride ``native_name``, arrays are shared (never copied), and
engine/log/warning aggregation stays predictable.
"""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_waveview import WaveAnalysis, WaveDataset, WaveSignal, merge_datasets


def _ds(engine: str, key: str, native: str, *, sweep: str = "frequency") -> WaveDataset:
    x = np.linspace(1.0, 1e6, 32)
    an = WaveAnalysis(
        analysis=key,
        native_name=native,
        signals={
            sweep: WaveSignal(sweep, x),
            "out": WaveSignal("out", 1.0 / (1.0 + 1j * x / 1e3)),
        },
        sweep=sweep,
    )
    return WaveDataset(source=f"/tmp/{native}.raw", engine=engine, analyses={key: an})


def test_union_of_distinct_analyses_keeps_bare_keys():
    ac = _ds("ngspice", "ac", "AC Analysis")
    tran = _ds("ngspice", "tran", "Transient", sweep="time")
    merged = merge_datasets([("run_1_tb_ac", ac), ("run_1_tb_tran", tran)], source="/tmp/run")
    assert set(merged.analyses) == {"ac", "tran"}
    assert merged.engine == "ngspice"
    assert merged.source == "/tmp/run"
    # provenance label lands in native_name; the member's own object is untouched
    assert merged.analyses["ac"].native_name == "AC Analysis · run_1_tb_ac"
    assert ac.analyses["ac"].native_name == "AC Analysis"


def test_collision_gets_stable_suffix_and_matching_analysis_field():
    a1 = _ds("ngspice", "ac", "AC tt")
    a2 = _ds("ngspice", "ac", "AC ss")
    a3 = _ds("ngspice", "ac", "AC ff")
    merged = merge_datasets([("tt", a1), ("ss", a2), ("ff", a3)], source="/tmp/run")
    assert list(merged.analyses) == ["ac", "ac#2", "ac#3"]
    # the analysis field mirrors its (possibly suffixed) dict key — /wave echoes it
    assert merged.analyses["ac#2"].analysis == "ac#2"
    # first member wins the bare key
    assert merged.analyses["ac"].native_name.startswith("AC tt")


def test_arrays_are_shared_not_copied():
    ac = _ds("ngspice", "ac", "AC Analysis")
    merged = merge_datasets([("", ac)], source="/tmp/run")
    assert merged.analyses["ac"].signals is ac.analyses["ac"].signals
    # empty label → native_name unchanged
    assert merged.analyses["ac"].native_name == "AC Analysis"


def test_mixed_engines_and_warning_prefixes_and_log_fallback():
    a = _ds("ngspice", "ac", "AC")
    a.warnings.append("unknown plot kept")
    a.log_path = "/tmp/a.log"
    b = _ds("spectre", "tran", "tran.tran", sweep="time")
    merged = merge_datasets([("ac_tb", a), ("tran_tb", b)], source="/tmp/run")
    assert merged.engine == "mixed"
    assert merged.warnings == ["ac_tb: unknown plot kept"]
    assert merged.log_path == "/tmp/a.log"  # falls back to the first member's log
    explicit = merge_datasets([("x", a)], source="/tmp/run", log_path="/tmp/run/run.log")
    assert explicit.log_path == "/tmp/run/run.log"


def test_empty_members_rejected():
    with pytest.raises(ValueError):
        merge_datasets([], source="/tmp/run")


def test_measure_resolves_on_merged_dataset():
    """The Tier-1 seam keeps working: resolve_analysis('ac') finds the primary."""
    ac = _ds("ngspice", "ac", "AC")
    tran = _ds("ngspice", "tran", "Transient", sweep="time")
    merged = merge_datasets([("a", ac), ("t", tran)], source="/tmp/run")
    an = merged.resolve_analysis("ac")
    assert an is not None and an.native_name.startswith("AC")
    assert merged.find_signal("ac", "out") is not None
