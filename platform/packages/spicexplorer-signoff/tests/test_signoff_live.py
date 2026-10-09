"""Live signoff on the prototype 5T-OTA GDS — needs klayout + the IHP PDK (+ kpex for PEX).

Marked ``slow``; each test skips with the missing capability as the reason.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_core import project_root
from spicexplorer_signoff import probe, run_drc, run_lvs, run_pex
from spicexplorer_signoff.pdk import for_pdk, klayout_exe

EX = project_root() / "examples" / "layout" / "ihp-sg13g2" / "5t_ota_gf"
GDS, NET, CELL = EX / "ota_5t_gf.gds", EX / "ota_5t_gf_lvs.spice", "ota_5t_gf"
P = probe()

pytestmark = pytest.mark.slow


@pytest.mark.skipif(
    not (P.drc_ok and GDS.is_file()), reason="klayout + PDK DRC deck + example GDS needed"
)
def test_drc_live(tmp_path):
    r = run_drc(GDS, CELL, tmp_path / "drc")
    assert r.available and r.passed and r.n_violations == 0 and r.report_path


# --- DRC on a drawn wire, with whichever deck this checkout ships (#277) -----------------------

_DRC_DIR = for_pdk().klayout_tech / "drc"


def _metal1_wire(path: Path, width_um: float) -> Path:
    """One 2 um long Metal1 (GDS 8/0) wire of the given width in a cell named ``probe``."""
    import klayout.db as db

    ly = db.Layout()
    ly.dbu = 0.001
    top = ly.create_cell("probe")
    top.shapes(ly.layer(8, 0)).insert(db.DBox(0, 0, width_um, 2.0))
    ly.write(str(path))
    return path


@pytest.mark.skipif(
    not (klayout_exe() and _DRC_DIR.is_dir()), reason="klayout + the PDK's drc/ directory needed"
)
def test_drc_live_on_a_drawn_metal1_wire(tmp_path):
    """SG13G2 rule M1.a sets the minimum Metal1 width to 0.16 um (both .lydrc decks describe it as
    "Min. Metal1 width = 0.16"): a 1.0 um wire is clean and a 0.10 um wire violates M1.a.

    On a checkout with only the .lydrc decks (the lab workstation) the base returned
    ``available=False`` here. The skip condition does not use ``probe().drc_ok``, because that was
    False on the same checkout."""
    pytest.importorskip("klayout.db")
    wide = run_drc(_metal1_wire(tmp_path / "wide.gds", 1.0), "probe", tmp_path / "drc_wide")
    assert wide.available, wide.reason
    assert wide.passed and wide.n_violations == 0 and wide.deck, wide.reason
    narrow = run_drc(_metal1_wire(tmp_path / "narrow.gds", 0.10), "probe", tmp_path / "drc_narrow")
    assert narrow.available and not narrow.passed
    assert "M1.a" in {v.rule for v in narrow.violations}, narrow.violations


@pytest.mark.skipif(
    not (P.lvs_ok and GDS.is_file()), reason="klayout + PDK LVS deck + example GDS needed"
)
def test_lvs_live(tmp_path):
    r = run_lvs(GDS, NET, CELL, tmp_path / "lvs")
    assert r.available and r.passed and r.matched and r.netlist_sha


# --- LVS against a deliberately wrong reference (#278) -----------------------------------------


def _two_labelled_wires(path: Path) -> Path:
    """Two 10 x 1 um Metal1 wires labelled ``a`` and ``b`` (text on 8/25), no devices."""
    import klayout.db as db

    ly = db.Layout()
    ly.dbu = 0.001
    top = ly.create_cell("probe")
    for name, y in (("a", 0.0), ("b", 3.0)):
        top.shapes(ly.layer(8, 0)).insert(db.DBox(0, y, 10, y + 1))
        top.shapes(ly.layer(8, 25)).insert(db.DText(name, 5, y + 0.5))
    ly.write(str(path))
    return path


@pytest.mark.skipif(not P.lvs_ok, reason="klayout + the PDK LVS runner needed")
def test_lvs_live_wrong_reference_is_a_mismatch_not_a_runner_failure(tmp_path):
    """The layout has two nets and no device. A reference with no device matches it; one with an
    extra NMOS between the two nets does not, and the IHP deck says so with "Netlists don't
    match" and exit 0. The base reported that as "neither a verdict nor unmatched counts"."""
    pytest.importorskip("klayout.db")
    gds = _two_labelled_wires(tmp_path / "probe.gds")
    good = tmp_path / "good.sp"
    good.write_text(".subckt probe a b\n.ends\n")
    wrong = tmp_path / "wrong.sp"
    wrong.write_text(".subckt probe a b\nM1 a b a a sg13_lv_nmos w=1u l=0.13u\n.ends\n")
    ok = run_lvs(gds, good, "probe", tmp_path / "lvs_good")
    assert ok.available and ok.passed and ok.matched, ok.reason
    bad = run_lvs(gds, wrong, "probe", tmp_path / "lvs_wrong")
    assert bad.available and not bad.passed and bad.matched is False
    assert "does not match the reference netlist wrong.sp" in bad.reason, bad.reason
    assert "neither" not in bad.reason


@pytest.mark.skipif(not (P.pex_ok and GDS.is_file()), reason="kpex (+ ruby>=2.6 klayout) needed")
def test_pex_live(tmp_path):
    r = run_pex(GDS, CELL, NET, tmp_path / "pex", mode="CC")
    assert r.ok and r.n_c > 0 and r.netlist_path and Path(r.netlist_path).is_file()
    assert 0.5 < r.per_net_c_ff["vinp"] < 5.0  # ~1.2 fF on the prototype


@pytest.mark.skipif(not (P.pex_ok and GDS.is_file()), reason="kpex (+ ruby>=2.6 klayout) needed")
def test_pex_rc_live_mesh_is_connected(tmp_path):
    """RC mode: kpex's raw netlist has ZERO device pins on the resistor mesh (8 open nets on this
    cell); after the stitch every net's mesh is on the circuit and the verdict may pass."""
    from spicexplorer_signoff.pex import check_mesh_connectivity

    r = run_pex(GDS, CELL, NET, tmp_path / "pex_rc", mode="RC")
    assert r.ok and r.n_r > 0 and r.mesh_connected and r.mesh["n_open_nets"] == 0
    assert r.mesh["n_pins_on_mesh"] > 0
    # and no 0 Ω card reaches the consumer: ngspice would clamp it to 1e-12 Ω and solve a
    # different circuit. The raw netlist has plenty (nSD/pSD are 0.0 Ω/square).
    assert r.mesh["n_zero_r_cards"] == 0
    assert r.raw_netlist_path and r.netlist_path != r.raw_netlist_path
    raw_ok, raw = check_mesh_connectivity(Path(r.raw_netlist_path))
    assert (
        not raw_ok and raw["n_pins_on_mesh"] == 0 and raw["n_open_nets"] == raw["n_nets_with_mesh"]
    )


# --- the strap probe: kpex's metal R against a hand value, and what makes a `[Pin]` node --------

_STRAP_W, _STRAP_LEN, _STRAP_TOP = 5.0, 100.0, -2.0  # um; the OTA's `vss` rail reaches y = -2.65
_PIN_Y = _STRAP_TOP - _STRAP_LEN + 1.0
_M1_SHEET = 0.11  # Ohm/square, SG13G2 Metal1 (kpex's own conductor table; magic tech: 110 mOhm/sq)


def _ota_with_strap(out, *, pin: bool):
    """The committed OTA GDS plus a 100 x 5 um Metal1 strap hanging off its `vss` rail.

    Extra metal on an EXISTING net leaves connectivity alone, so the committed LVS reference still
    matches. The cell's own `vss` text is MOVED to the far end of the strap (the LVS-annotated
    layout keeps one text per net, so a second `vss` label never reaches kpex) and, when ``pin``,
    a polygon is drawn on the Metal1 PIN purpose (8/2) under it.
    """
    import klayout.db as db

    ly = db.Layout()
    ly.read(str(GDS))
    top = ly.top_cell()
    m1, m1_pin, m1_lbl = ly.layer(8, 0), ly.layer(8, 2), ly.layer(8, 25)
    x0, y_bot = -_STRAP_W / 2, _STRAP_TOP - _STRAP_LEN
    top.shapes(m1).insert(db.DBox(x0, y_bot, x0 + _STRAP_W, _STRAP_TOP))
    keep = [
        s.text.dup() for s in top.shapes(m1_lbl).each() if s.is_text() and s.text.string != "vss"
    ]
    top.shapes(m1_lbl).clear()
    for t in keep:
        top.shapes(m1_lbl).insert(t)
    if pin:
        top.shapes(m1_pin).insert(db.DBox(-0.5, _PIN_Y - 0.5, 0.5, _PIN_Y + 0.5))
    top.shapes(m1_lbl).insert(db.DText("vss", 0.0, _PIN_Y))  # DText is in MICRONS
    ly.write(str(out))
    return out


def _cards_touching(netlist, node):
    from spicexplorer_signoff.pex import _cards, _net

    out = []
    for _, card in _cards(Path(netlist).read_text()):
        t = card.split()
        if t[0].lower().startswith("rext_") and (node is None or node in (_net(t[1]), _net(t[2]))):
            out.append((t[0], _net(t[1]), _net(t[2]), float(t[3])))
    return out


@pytest.mark.skipif(not (P.pex_ok and GDS.is_file()), reason="kpex (+ ruby>=2.6 klayout) needed")
def test_pex_rc_live_metal_resistance_matches_the_hand_value(tmp_path):
    """A 100 x 5 um Metal1 strap with a PIN at its far end: kpex names the mesh node at a `[Pin]`
    with the plain net name, so the strap lands as ONE card straight off the subckt port, and its
    value is the hand model 0.11 Ohm/sq * L / W. This is the calibration the LDO's 49 Ohm never
    was — the extractor's metal is right; only where the port was tied was wrong."""
    pytest.importorskip("klayout.db")
    gds = _ota_with_strap(tmp_path / "ota_strap_pin.gds", pin=True)
    r = run_pex(gds, CELL, NET, tmp_path / "pex_pin", mode="RC")
    assert r.ok and r.mesh_connected
    # kpex saw the pin, so the tie is the port itself, not a proxy on some other node
    assert r.mesh["anchors"]["vss"] == ["vss", "Metal1", "pin"]
    assert r.mesh["n_anchor_pins"] == 1
    strap = _cards_touching(r.netlist_path, "vss")
    assert len(strap) == 1, strap  # the port sees the strap and nothing else
    length = abs(_PIN_Y - _STRAP_TOP) - 0.65  # the junction sits on the rail, not at its edge
    hand = _M1_SHEET * length / _STRAP_W
    assert 0.8 * hand < strap[0][3] < 1.2 * hand, (strap, hand)


@pytest.mark.skipif(not (P.pex_ok and GDS.is_file()), reason="kpex (+ ruby>=2.6 klayout) needed")
def test_pex_rc_live_without_a_pin_polygon_kpex_emits_no_pin_node(tmp_path):
    """The same GDS with the same label and NO polygon on the pin purpose: kpex emits zero `[Pin]`
    nodes, because `pins_of_layer(...) & labels_of_layer(...)` is what makes one
    (`klayout_pex/klayout/lvsdb_extractor.py`). The anchor then falls back to a proxy 100 um away
    from where the port is drawn — the LDO's situation exactly."""
    pytest.importorskip("klayout.db")
    gds = _ota_with_strap(tmp_path / "ota_strap_nopin.gds", pin=False)
    r = run_pex(gds, CELL, NET, tmp_path / "pex_nopin", mode="RC")
    assert r.ok and r.mesh_connected and r.mesh["n_anchor_pins"] == 0
    node, _layer, kind = r.mesh["anchors"]["vss"]
    assert kind == "proxy" and node != "vss"
    # the strap is still extracted at its right value -- it is simply not on the port's path any
    # more: the port hangs 100 um away, at whatever node the proxy rule picked
    hand = _M1_SHEET * (abs(_PIN_Y - _STRAP_TOP) - 0.65) / _STRAP_W
    everywhere = [c[3] for c in _cards_touching(r.netlist_path, None)]
    assert any(abs(v - hand) < 0.2 * hand for v in everywhere)
    assert all(abs(c[3] - hand) > 0.5 * hand for c in _cards_touching(r.netlist_path, "vss"))
