"""Which extracted netlist was measured, and the what-ifs an extraction invites.

All offline: synthetic netlist text and empty files in tmp dirs — no kpex, no klayout, no GDS.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from spicexplorer_signoff.postlayout import select_pex_netlist
from spicexplorer_signoff.sensitivity import (
    filter_caps,
    find_mos_cards,
    inject_threshold_offset,
    insert_series_return,
)

BLOCK = """.subckt cell vdd vout vss
XMn_1 ea_n ea_n vss vss sg13_lv_nmos w=1u l=0.5u
XMn_2 ea_n ea_n vss vss sg13_lv_nmos w=1u l=0.5u
XMn_3 ea_o1 ea_n vss vss sg13_lv_nmos w=1u l=0.5u
XMp_1 ea_out pbias vdd vdd sg13_lv_pmos w=2u l=0.5u
Cext_1 ea_n vss 1.5e-15
Cext_2 ea_o1 vout 0.4e-15
Cext_3 vout vss 3.0e-15
XCOUT vout vss cap_cmim w=10u l=10u
.ends
"""


# --------------------------------------------------------------- select_pex_netlist ----


def _touch(d: Path, *names: str) -> None:
    d.mkdir(parents=True, exist_ok=True)
    for n in names:
        (d / n).write_text("* extracted\n")


def test_a_matched_rc_pair_answers_in_favour_of_the_stitched_one(tmp_path: Path):
    """The bug this exists for: a `*_pex_netlist.spice` glob does NOT match the stitched name,
    so with both files present the old rule found 'exactly one' and measured the wrong one."""
    _touch(tmp_path, "cell_k25d_pex_netlist.spice", "cell_k25d_pex_netlist_stitched.spice")
    m = select_pex_netlist(tmp_path)
    assert m.kind == "stitched" and m.how == "directory"
    assert m.path.name.endswith("_stitched.spice")
    assert "RC pair" in m.note


def test_a_single_netlist_needs_no_note(tmp_path: Path):
    _touch(tmp_path, "cell_k25d_pex_netlist.spice")
    m = select_pex_netlist(tmp_path)
    assert (m.kind, m.how, m.note) == ("raw", "directory", "")


def test_two_runs_under_one_directory_raise_instead_of_choosing(tmp_path: Path):
    _touch(tmp_path / "a", "cell_k25d_pex_netlist.spice")
    _touch(tmp_path / "b", "other_k25d_pex_netlist.spice")
    with pytest.raises(ValueError, match="2 extracted netlists"):
        select_pex_netlist(tmp_path)


def test_an_empty_directory_says_to_run_the_pex_stage(tmp_path: Path):
    tmp_path.joinpath("empty").mkdir()
    with pytest.raises(FileNotFoundError, match="run the PEX stage"):
        select_pex_netlist(tmp_path / "empty")


def test_an_explicit_path_wins_and_a_missing_one_raises(tmp_path: Path):
    _touch(tmp_path, "cell_k25d_pex_netlist.spice", "cell_k25d_pex_netlist_stitched.spice")
    m = select_pex_netlist(tmp_path, explicit=tmp_path / "cell_k25d_pex_netlist.spice")
    assert (m.kind, m.how) == ("raw", "explicit")
    with pytest.raises(FileNotFoundError):
        select_pex_netlist(tmp_path, explicit=tmp_path / "nope.spice")


def test_the_pex_stages_own_record_is_honoured_when_it_points_inside_the_directory(tmp_path: Path):
    rc = tmp_path / "pex_rc"
    _touch(rc, "cell_k25d_pex_netlist.spice", "cell_k25d_pex_netlist_stitched.spice")
    rec = tmp_path / "signoff.json"
    rec.write_text(
        json.dumps({"pex": {"netlist": str(rc / "cell_k25d_pex_netlist_stitched.spice")}})
    )
    m = select_pex_netlist(rc, record=rec)
    assert (m.kind, m.how) == ("stitched", "record")


def test_a_record_naming_another_stage_does_not_win_and_says_so(tmp_path: Path):
    """One run dir, two stages, ONE signoff.json: honouring it while the caller asked for the
    other stage's directory measures the wrong extraction and reports the right name."""
    cc, rc = tmp_path / "pex_cc", tmp_path / "pex_rc"
    _touch(cc, "cell_k25d_pex_netlist.spice")
    _touch(rc, "cell_rc_k25d_pex_netlist.spice")
    rec = tmp_path / "signoff.json"
    rec.write_text(json.dumps({"pex": {"netlist": str(cc / "cell_k25d_pex_netlist.spice")}}))
    m = select_pex_netlist(rc, record=rec)
    assert m.path.parent == rc and m.how == "directory"
    assert "not under the requested" in m.note


def test_the_record_is_a_provenance_row(tmp_path: Path):
    _touch(tmp_path, "cell_k25d_pex_netlist.spice")
    d = select_pex_netlist(tmp_path).as_dict()
    assert set(d) == {"pex_netlist", "pex_netlist_kind", "pex_netlist_how"}


# ------------------------------------------------------------- extracted-block helpers ----


def test_find_mos_cards_locates_a_device_class_by_connectivity():
    """The extraction has no design-device names; the nets are what survive."""
    assert find_mos_cards(BLOCK, family="nmos", drain="ea_n", gate="ea_n", source="vss") == [
        "XMn_1",
        "XMn_2",
    ]
    assert find_mos_cards(BLOCK, family="pmos", drain="ea_out", gate="pbias", source="vdd") == [
        "XMp_1"
    ]
    assert find_mos_cards(BLOCK, family="pmos", drain="ea_n", gate="ea_n", source="vss") == []
    assert find_mos_cards(BLOCK, family="nmos", drain="nope", gate="ea_n", source="vss") == []


def test_a_threshold_increase_is_injected_as_a_negative_gate_source():
    out = inject_threshold_offset(BLOCK, "cell", ["XMn_1"], 2e-3)
    lines = [ln for ln in out.splitlines() if ln.strip().upper().startswith("V")]
    assert len(lines) == 1
    assert "-0.002" in lines[0].replace(" ", "") or "-2e-03" in lines[0]
    assert "XMn_1" in out  # the device is still there, now on a shifted gate node


def test_filter_caps_keeps_or_drops_exactly_the_named_nets():
    kept, n_left, n_gone = filter_caps(BLOCK, keep=["ea_n"])
    assert (n_left, n_gone) == (1, 2)
    assert "Cext_1" in kept and "Cext_2" not in kept
    assert "XCOUT" in kept  # a re-inserted device is an X call, never a C card

    dropped, n_left, n_gone = filter_caps(BLOCK, drop=["vout"])
    assert (n_left, n_gone) == (1, 2)
    assert "Cext_1" in dropped and "Cext_3" not in dropped

    same, n_left, n_gone = filter_caps(BLOCK)
    assert (n_left, n_gone) == (3, 0)


def test_insert_series_return_moves_the_cards_and_spares_the_kelvin_ones():
    out, moved = insert_series_return(BLOCK, "vss", 0.35, kelvin=["XCOUT"])
    assert "Rvssret vss_ret vss 0.35" in out
    assert ".subckt cell vdd vout vss" in out  # the header keeps the pin
    assert "XCOUT vout vss cap_cmim" in out  # the Kelvin device still reaches the pin
    assert "XMn_1 ea_n ea_n vss_ret vss_ret" in out
    assert moved == 5  # four MOS cards + Cext_3; XCOUT is spared
