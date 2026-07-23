"""Scoring-math boundaries + corner-apply byte-identity + the ListTargetSpec API boundary."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from spicexplorer.core.domains import ListTargetSpec, Project_Setup, TargetSpec
from spicexplorer.core.utils import (
    compute_relative_absolute_error,
    compute_relative_exponential_error,
    compute_relative_sigmoid_error,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FC_YAML = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/sizing/project_setup.yaml"


# ── scoring-math boundaries ───────────────────────────────────────────────────────────────────
def test_zero_normalizing_coeff_yields_inf_not_nan():
    """coeff=0 divides to **inf** (a maximal, orderable penalty) — never NaN. The normal path
    can't produce coeff=0 (TargetSpec guarantees a positive tolerance even for target=0);
    this pins the function contract that backs that reliance."""
    err = compute_relative_absolute_error(np.float64(1.0), np.float64(2.0), np.float64(0.0))
    assert np.isinf(err) and not np.isnan(err)


def test_nan_measure_propagates_as_nan():
    """A NaN measure stays NaN through the error fn (the scorer layer is responsible for
    rejecting it — pinned so NaN never silently compares as a finite score here)."""
    err = compute_relative_absolute_error(np.float64("nan"), np.float64(2.0), np.float64(1.0))
    assert np.isnan(err)


def test_exponential_error_is_overflow_capped():
    """A raw-SI-magnitude miss must saturate (the clamp), not overflow to inf and flatten
    the optimizer's gradient ordering."""
    huge = compute_relative_exponential_error(np.float64(1e9), np.float64(0.0), np.float64(1e-6))
    big = compute_relative_exponential_error(np.float64(1e6), np.float64(0.0), np.float64(1e-3))
    assert np.isfinite(huge) and huge == big          # both hit the cap — same saturated penalty


def test_sigmoid_error_bounded():
    e = compute_relative_sigmoid_error(np.float64(1e12), np.float64(0.0), np.float64(1.0))
    assert 0.0 <= e <= 1.0


# ── ListTargetSpec API boundary (the documented `.targets` gotcha) ────────────────────────────
def test_target_specs_is_listtargetspec_not_list():
    """`optimizer_config.target_specs` is a ListTargetSpec — consumers must use `.targets`.
    Direct indexing raises; pinned so a 'simplification' back to a plain list is a conscious
    breaking change (CLAUDE.md gotcha)."""
    p = Project_Setup.from_yaml(FC_YAML)
    ts = p.optimizer_config.target_specs
    assert isinstance(ts, ListTargetSpec) and not isinstance(ts, list)
    assert isinstance(ts.targets, list) and ts.targets
    with pytest.raises(TypeError):
        ts[0]  # noqa: B018 — the boundary under test


def test_duplicate_target_spec_names_rejected():
    """Two specs sharing a name would silently overwrite each other in the performance map
    — construction must refuse."""
    a = TargetSpec(name="gain", testbench="tb_ac", target=60.0, goal="minimize", sim_type="AC")
    b = TargetSpec(name="gain", testbench="tb_ac", target=10.0, goal="minimize", sim_type="AC")
    with pytest.raises(ValueError, match="duplicate target_spec"):
        ListTargetSpec(targets=[a, b])


# ── apply_corner: same corner twice is byte-identical ─────────────────────────────────────────
def test_apply_corner_same_corner_twice_byte_identical(tmp_path):
    """Re-applying the SAME corner must reproduce the identical netlist (no accumulated
    directives, no double-stripping). The switching case is covered elsewhere; this pins the
    repeat case the docs promise."""
    from spicexplorer_core.spice_engine import NGSpice_Wrapper

    p = Project_Setup.from_yaml(FC_YAML)
    ss = p.pvt.get("ss_125C_1V62")
    netlist = REPO_ROOT / "examples/OTA/folded_cascode/ihp-sg13g2/spice/cora_testbench.spice"

    work = tmp_path / "n.spice"
    work.write_text(netlist.read_text())
    w = NGSpice_Wrapper(netlist_filename=work, output_folder=tmp_path / "runs",
                        testbench_name="idem")
    def joined() -> str:
        return "\n".join(ln for ln in w.editor.netlist if isinstance(ln, str))

    w.apply_corner(ss)
    first = joined()
    w.apply_corner(ss)
    assert joined() == first
