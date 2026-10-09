"""The case `review-002` **M8** asked for: a collision that only `stub_clear` prevents.

M8: "The Metal1 short reproduces only when *both* committed changes are reverted. Reverting
`stub_clear` alone (leaving the two-directional column search) still gives 0 rule violations and a
matched netlist at the record sizing. So no committed sizing exercises the obstacle map ... a
regression that no case exercises will rot."

These tests build the collision by hand, so it does not depend on a sizing point ever producing
it. They import `router.py` only — no gdsfactory, so they run in the repo venv under
`make test`.

Run them directly (``python test_builder.py``) or under pytest; the
sign-off driver runs them as its first, blocking stage, so the guard is exercised every round.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from router import ObstacleMap  # noqa: E402

Y = 4.0          # the y two neighbouring devices share for their gate bars
GATE_BAR = 0.5   # gate-bar height


def _map_with_a_neighbours_gate_bar() -> ObstacleMap:
    """`vref`'s terminal is at x = 3.0, its own column is taken by `ea_n`, and `fb`'s gate bar
    occupies x in [1.2, 2.6] at the same y -- i.e. the preferred direction of the walk.

    The *column* check accepts x = 2.4 (no Metal2 there); only the Metal1 stub the walk would drag
    across the gate bar can refuse it. This is the LDO 005 failure exactly: a 50 nm length change
    in another row pushed XM2's gate stub through XM1's gate bar, and DRC reported 0 violations on
    a shorted netlist.
    """
    m = ObstacleMap()
    m.m1_claim("fb", Y, 1.2, 2.6, GATE_BAR)
    m.verticals.append(("ea_n", 3.0, 0.0, 10.0))   # the terminal's own column is busy
    return m


def test_stub_clear_refuses_a_stub_that_crosses_a_foreign_gate_bar():
    m = _map_with_a_neighbours_gate_bar()
    assert m.stub_clear("vref", Y, 3.0, 3.0)          # no walk: nothing crossed
    assert not m.stub_clear("vref", Y, 3.0, 2.4)      # walks INTO the bar
    assert not m.stub_clear("vref", Y, 3.0, 0.6)      # walks straight THROUGH it
    assert m.stub_clear("fb", Y, 3.0, 0.6)            # same net: a merge, not a short
    assert m.stub_clear("vref", Y + 1.2, 3.0, 0.6)    # a different row is not blocked


def test_alloc_turns_round_instead_of_marching_into_the_neighbour():
    """With the preferred direction blocked by Metal1 only, `alloc` must come back the other way."""
    m = _map_with_a_neighbours_gate_bar()
    x = m.alloc("vref", 3.0, Y, 10.0, step=-0.6)      # preferred direction is LEFT, into `fb`
    assert x > 2.6 + 0.28, f"alloc returned {x}: the stub would cross fb's gate bar"
    assert x != 3.0, "x = 3.0 is taken by ea_n's Metal2 column"
    assert m.stub_clear("vref", Y, 3.0, x)


def test_without_stub_clear_the_allocator_would_short_the_two_nets():
    """The regression itself: with the Metal1 check disabled, the same call returns a column whose
    stub lands on `fb` -- a short DRC cannot see, because the two Metal1 shapes merge."""
    m = _map_with_a_neighbours_gate_bar()
    m.stub_clear = lambda *a, **k: True  # type: ignore[method-assign]
    x = m.alloc("vref", 3.0, Y, 10.0, step=-0.6)
    assert abs(x - 2.4) < 1e-9, "the unguarded walk should take the first free Metal2 column"
    assert not _map_with_a_neighbours_gate_bar().stub_clear("vref", Y, 3.0, x)


def test_column_free_still_keeps_two_nets_off_one_metal2_column():
    m = ObstacleMap()
    m.verticals.append(("fb", 3.0, 0.0, 10.0))
    assert not m.column_free("vref", 3.0, 4.0, 6.0)
    assert not m.column_free("vref", 3.4, 4.0, 6.0)   # inside the 0.6 um pad+space pitch
    assert m.column_free("vref", 3.6, 4.0, 6.0)
    assert m.column_free("fb", 3.0, 4.0, 6.0)         # same net shares its own column
    assert m.column_free("vref", 3.0, 20.0, 30.0)     # no y overlap


# --------------------------------------------------------------------- review-003 F7 ----
# The same hole one layer up: the pass array's Metal2 comb is drawn by the power path as plain
# rectangles.  Before F7 the router never saw it, `column_free` compared routed columns only, and
# `col_vias` in {3, 4} put a `gate` column straight through the `vout` spine — a merge of two
# legal polygons, so DRC reported 0 on a shorted netlist and only LVS caught it.

COMB_Y0, COMB_Y1 = 52.0, 58.0     # a 6 um Metal2 spine, as `pwr_band_w` draws it
COMB_X0, COMB_X1 = 44.0, 90.0


def _map_with_the_pass_arrays_metal2_comb() -> ObstacleMap:
    m = ObstacleMap()
    m.claim_box("Metal2", "vout", COMB_X0, COMB_Y0, COMB_X1, COMB_Y1)
    return m


def test_a_metal2_column_may_not_run_through_the_power_comb():
    m = _map_with_the_pass_arrays_metal2_comb()
    # `gate` leaves the array at x = 44.1 and drops to a track at y = 21: straight down is a short
    assert not m.column_free("gate", 44.1, 21.0, 60.0)
    assert not m.column_free("gate", 60.0, 21.0, 60.0)     # anywhere under the spine
    assert m.column_free("gate", 43.5, 21.0, 60.0)         # clear of it to the left
    assert m.column_free("vout", 60.0, 21.0, 60.0)         # its own comb: a merge, not a short
    assert m.column_free("gate", 60.0, 0.0, 20.0)          # no y overlap


def test_a_metal3_column_is_not_refused_by_a_metal2_obstacle():
    """Layer-awareness is what removed the hard-coded Metal3 hop: `gate`'s track is Metal3, so
    the Metal2 comb is simply not an obstacle for it."""
    m = _map_with_the_pass_arrays_metal2_comb()
    assert m.column_free("gate", 60.0, 21.0, 60.0, "Metal3")
    m.claim_box("Metal3", "vout", COMB_X0, COMB_Y0, COMB_X1, COMB_Y1)
    assert not m.column_free("gate", 60.0, 21.0, 60.0, "Metal3")


def test_without_the_claim_the_allocator_walks_into_the_comb():
    """The regression itself: drop the comb from the map and the walk takes the first column,
    which is inside the spine — the it02 -> it03 `gate` | `vout` short, reproduced."""
    m = _map_with_the_pass_arrays_metal2_comb()
    x_guarded = m.alloc("gate", 44.1, 60.0, 21.0, step=-0.6)
    assert x_guarded < COMB_X0 - 0.3 + 1e-6, f"alloc returned {x_guarded}, inside the comb"
    bare = ObstacleMap()
    assert bare.alloc("gate", 44.1, 60.0, 21.0, step=-0.6) == 44.1


def test_two_columns_of_one_net_still_keep_the_via_pad_pitch():
    """Same net is not the same column: two `ea_n` columns 0.38 um apart merge on Metal2 but put
    their Via1 cuts 0.19 um apart, which is V1.b (0.22).  Coincident is a merge; 0.38 is not."""
    m = ObstacleMap()
    m.claim_vertical("ea_n", 20.07, 4.5, 14.93)
    assert m.column_free("ea_n", 20.07, 14.93, 26.0)      # the same column: a merge
    assert not m.column_free("ea_n", 20.45, 14.93, 26.0)  # 0.38 apart: V1.b
    assert m.column_free("ea_n", 20.67, 14.93, 26.0)      # a full pitch away


def test_retag_follows_the_claimed_shapes_too():
    """`m1_retag` renames the placeholder tags a device is drawn under; a claim left under the
    old tag would be an obstacle nobody owns."""
    m = ObstacleMap()
    m.claim_box("Metal2", "@g:XM1", 0.0, 0.0, 1.0, 1.0)
    m.claim_vertical("@g:XM1", 5.0, 0.0, 10.0)
    m.m1_retag("@g:XM1", "fb")
    assert m.boxes[0][1] == "fb" and m.verticals[0][0] == "fb"
    assert m.column_free("fb", 5.0, 2.0, 4.0)


def test_alloc_raises_with_a_hint_when_nothing_fits():
    m = ObstacleMap()
    m.m1_claim("fb", Y, -100.0, 100.0, GATE_BAR)
    try:
        m.alloc("vref", 0.0, Y, 10.0)
    except AssertionError as exc:
        assert "widen dev_gap" in str(exc)
    else:
        raise AssertionError("alloc should have refused every column")


# ---------------------------------------------------------------------------------------------
# review-004 **F27**: which extracted netlist do the benches measure?
#
# The platform writes TWO files for an RC run -- `..._k25d_pex_netlist.spice` (kpex's own, whose
# resistor mesh is an electrical island) and `..._k25d_pex_netlist_stitched.spice` (the repaired
# one `PexResult.netlist_path` names).  `pex_sim.py` (`postlayout.py` upstream) used to glob `*_pex_netlist.spice`, which
# does NOT match the stitched name: with both files present it found exactly one, reported no
# ambiguity, and measured the file the extractor did not name.  These cases pin the selection
# rule.  They import this entry's `pex_sim.py` (the source repo's `layout/postlayout.py`),
# so they run in the same interpreter as the rest of the sign-off chain.
def _select(**kw):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from pex_sim import select_pex_netlist
    return select_pex_netlist(**kw)


def _pex_dir(raw: bool, stitched: bool):
    import tempfile
    d = Path(tempfile.mkdtemp(prefix="pextest_"))
    if raw:
        (d / "cell_k25d_pex_netlist.spice").write_text("* raw\n")
    if stitched:
        (d / "cell_k25d_pex_netlist_stitched.spice").write_text("* stitched\n")
    return d


def test_an_rc_pair_resolves_to_the_stitched_netlist_never_the_raw_one():
    d = _pex_dir(raw=True, stitched=True)
    path, kind = _select(pex_dir=d)
    assert kind == "stitched" and path.name.endswith("_stitched.spice"), (path, kind)


def test_two_unrelated_netlists_are_an_error_not_a_silent_choice():
    d = _pex_dir(raw=True, stitched=True)
    (d / "other_k25d_pex_netlist.spice").write_text("* a second run\n")
    try:
        got = _select(pex_dir=d)
    except SystemExit as exc:
        assert "stitched" in str(exc) and "other" in str(exc), exc
        return
    raise AssertionError(f"selection must refuse to guess between two runs; it returned {got}")


def test_a_lone_stitched_netlist_is_the_one_measured():
    d = _pex_dir(raw=False, stitched=True)
    path, kind = _select(pex_dir=d)
    assert kind == "stitched" and path.name.endswith("_stitched.spice"), (path, kind)


def test_a_lone_raw_netlist_still_works():
    d = _pex_dir(raw=True, stitched=False)
    path, kind = _select(pex_dir=d)
    assert kind == "raw" and path.name == "cell_k25d_pex_netlist.spice", (path, kind)


def test_an_explicit_netlist_wins_over_both():
    d = _pex_dir(raw=True, stitched=True)
    want = d / "cell_k25d_pex_netlist_stitched.spice"
    path, kind = _select(pex_dir=d, explicit=str(want))
    assert path == want and kind == "stitched", (path, kind)


def test_the_signoff_record_names_the_netlist():
    import json
    d = _pex_dir(raw=True, stitched=True)
    rec = d / "signoff.json"
    rec.write_text(json.dumps(
        {"pex": {"netlist": str(d / "cell_k25d_pex_netlist_stitched.spice"), "mode": "RC"}}))
    path, kind = _select(pex_dir=d, record=str(rec))
    assert path.name.endswith("_stitched.spice") and kind == "stitched", (path, kind)


# review-004 **F26**/**F24**: the sign-off record must say whether an RC mesh was connected, and
# must not lose the stages a previous invocation of the same round wrote.
def _signoff():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import signoff
    return signoff


class _FakePex:
    """The fields `spicexplorer_signoff.results.PexResult` carries, with nothing else."""
    def __init__(self, **kw):
        d = dict(ok=True, available=True, mode="CC", netlist_path="/x/n.spice",
                 raw_netlist_path=None, n_c=3, n_r=0, per_net_c_ff={"vdd": 1.5, "vss": 0.25},
                 coupling_ff={}, log="", reason="", mesh_connected=None, mesh={})
        d.update(kw)
        self.__dict__.update(d)


def test_the_pex_record_carries_the_mesh_verdict():
    sg = _signoff()
    rec = sg._pex_record(_FakePex(mode="RC", n_r=8548, mesh_connected=True,
                                  mesh={"device_pins": 243, "device_pins_on_mesh": 220,
                                        "n_open_nets": 0, "n_stub_nets": 19},
                                  raw_netlist_path="/x/raw.spice"))
    assert rec["mesh_connected"] is True, rec
    assert rec["mesh"]["device_pins_on_mesh"] == 220 and rec["mesh"]["n_stub_nets"] == 19, rec
    assert rec["raw_netlist"] == "/x/raw.spice", rec


def test_an_open_rc_mesh_is_refused_and_a_cc_run_is_not():
    sg = _signoff()
    open_rc = sg._pex_record(_FakePex(mode="RC", n_r=8548, mesh_connected=False,
                                      mesh={"device_pins": 243, "device_pins_on_mesh": 0,
                                            "n_open_nets": 33}))
    why = sg.pex_gate(open_rc)
    assert why and "not connected" in why, why
    assert sg.pex_gate(sg._pex_record(_FakePex())) == "", "CC has no mesh — it must pass"


def test_a_second_invocation_does_not_erase_the_first_stages():
    import json, tempfile
    sg = _signoff()
    d = Path(tempfile.mkdtemp(prefix="signoffrec_"))
    sg._write_record(d, {"build": {"area_um2": 44266}, "lvs": {"matched": True}})
    sg._write_record(d, {"pex": {"mode": "RC", "ok": True}})
    got = json.loads((d / "signoff.json").read_text())
    assert set(got) == {"build", "lvs", "pex"}, got
    assert got["lvs"]["matched"] is True and got["pex"]["mode"] == "RC", got


def test_a_record_from_another_stage_does_not_win_over_the_directory_asked_for():
    """review-005: one run dir, two PEX stages, one `signoff.json`.

    `--pex <dir>/pex_rc --record <dir>/signoff.json` scored the CC netlist, because the record's
    `pex.netlist` was whatever stage ran last. A record that names a file outside the requested
    directory is evidence about a different stage and must be ignored, out loud.
    """
    import json
    import tempfile

    import pex_sim as pl

    d = Path(tempfile.mkdtemp(prefix="pexrec_"))
    cc, rc = d / "pex", d / "pex_rc"
    cc.mkdir(); rc.mkdir()
    (cc / "cell_k25d_pex_netlist.spice").write_text("* cc\n")
    (rc / "cell_k25d_pex_netlist_stitched.spice").write_text("* rc\n")
    (d / "signoff.json").write_text(json.dumps(
        {"pex": {"netlist": str(cc / "cell_k25d_pex_netlist.spice")}}))
    got, kind = pl.select_pex_netlist(rc, record=str(d / "signoff.json"))
    assert got.parent == rc and kind == "stitched", (got, kind)
    got, kind = pl.select_pex_netlist(cc, record=str(d / "signoff.json"))
    assert got.parent == cc and kind == "raw", (got, kind)


def test_a_zero_ohm_mesh_tie_is_floored_and_a_device_resistor_is_not():
    """review-005: kpex writes the `[Pin]` anchor as a 0-ohm resistor meaning "merge these two".

    ngspice clamps it to 1e-12 ohm instead, and the 1e12 S entry wrecks the conductance matrix:
    the LDO's sixteen identical divider segments then report 186 mV of drop across the top eight
    and 1.2 mV across the bottom eight, which violates KCL at `fb` by 1.5 uA. The floor is the
    repair; it must NOT touch a `rhigh`/`XR` device card, whose value is a real design value.
    """
    import pex_sim as pl

    txt, n = pl.floor_zero_r(
        "Rext_971 fb fb.n_24.18 0 R\n"
        "Rext_1 a b 9 R\n"
        "Rext_2 c d 0.0\n"
        "XRn_101 n_30 fb vss rhigh w=0.5u l=42.5u m=1\n"
        "Rdiv x y 0\n")
    assert n == 2, n            # only the extractor's own mesh cards, by name
    assert "Rext_971 fb fb.n_24.18 0.001 R" in txt, txt
    assert "Rext_1 a b 9 R" in txt, txt
    assert "XRn_101 n_30 fb vss rhigh w=0.5u l=42.5u m=1" in txt, txt
    assert "Rdiv x y 0" in txt, txt    # not a mesh tie: left exactly as written


def main() -> int:
    fails = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
            print(f"  ok   {name}")
        except Exception as exc:  # noqa: BLE001
            fails += 1
            print(f"  FAIL {name}: {type(exc).__name__}: {exc}")
    print(f"{'FAILED' if fails else 'passed'}: {fails} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
