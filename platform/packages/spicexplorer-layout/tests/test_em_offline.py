"""Solver-free tests of spicexplorer_layout.em: net cutting (klayout), the
vector-fit exporter (scikit-rf), and the informative failures. A live
openEMS run needs the from-source solver (em.OPENEMS_RECIPE) and a PDK
openEMS workflow, so it is exercised by a block's own EM lane, not here.

NOTE for CI: the klayout importorskip below is MODULE level — without the
``gds`` extra every test here skips silently; ``scikit-rf`` (the ``em``
extra) additionally gates the vector-fit test."""
import os

import numpy as np
import pytest
from spicexplorer_layout import em

klayout = pytest.importorskip("klayout.db", reason="needs the gds extra")

TOY_TECH = em.EmTech(metals={"Metal1": 8, "Metal2": 10},
                     vias={"Via1": 19},
                     via_stack={"Via1": ("Metal1", "Metal2")},
                     subgnd_layer=210)


def _toy_gds(path: str) -> str:
    """Two labelled nets: `sig` = M1 strip + Via1 + M2 strip, `gnd` = M1 ring
    segment. Labels on the metal text datatype (25)."""
    ly = klayout.Layout()
    ly.dbu = 0.001
    top = ly.create_cell("toy")
    m1 = ly.layer(8, 0)
    v1 = ly.layer(19, 0)
    m2 = ly.layer(10, 0)
    t1 = ly.layer(8, 25)
    box = klayout.DBox
    top.shapes(m1).insert(box(0, 0, 10, 1))
    top.shapes(v1).insert(box(9, 0.2, 9.8, 0.8))
    top.shapes(m2).insert(box(9, -2, 10, 2))
    top.shapes(m1).insert(box(0, 5, 10, 6))
    top.shapes(t1).insert(klayout.DText("sig", klayout.DTrans(klayout.DVector(1, 0.5))))
    top.shapes(t1).insert(klayout.DText("gnd", klayout.DTrans(klayout.DVector(1, 5.5))))
    ly.write(path)
    return path


def test_extract_net_gds_selects_traced_net(tmp_path):
    src = _toy_gds(str(tmp_path / "toy.gds"))
    out = str(tmp_path / "cut.gds")
    ports = [dict(num=1, kind="via", rect=[0, 0, 0.5, 1], from_layer="Metal1",
                  to_layer="Metal2", direction="z", subgnd=True)]
    man = em.extract_net_gds(src, ["sig"], out, ports, tech=TOY_TECH)
    assert man["nets"]["sig"] == ["Metal1", "Metal2", "Via1"]
    ly = klayout.Layout()
    ly.read(out)
    def region(layer, dt):
        li = ly.find_layer(layer, dt)
        return klayout.Region(ly.top_cell().begin_shapes_rec(ly.layer(layer, dt))) if li is not None else klayout.Region()
    # the gnd strip (y 5..6) must NOT be in the cut
    assert region(8, 0).bbox().top <= 1000    # dbu units: 1 um
    # port rectangle on tech.port_layer_base+1 and its SUBGND twin on 210
    assert not region(TOY_TECH.port_layer_base + 1, 0).is_empty()
    assert not region(210, 0).is_empty()
    # via cuts became mesh-robust bars: min side >= 0.55 um (dbu 0.001)
    vb = region(19, 0).bbox()
    assert vb.right - vb.left >= 550 and vb.top - vb.bottom >= 550


def test_extract_net_gds_unknown_net_lists_labels(tmp_path):
    src = _toy_gds(str(tmp_path / "toy.gds"))
    with pytest.raises(ValueError, match="labelled nets.*gnd.*sig"):
        em.extract_net_gds(src, ["outp"], str(tmp_path / "x.gds"), tech=TOY_TECH)


def test_em_sparams_needs_pdk_workflow(tmp_path, monkeypatch):
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    tech = em.EmTech(metals={}, vias={}, via_stack={},
                     workflow="nope/libs.tech/openems/workflow")
    with pytest.raises(FileNotFoundError, match="openEMS workflow"):
        em.em_sparams("x.gds", [], str(tmp_path / "out"), tech=tech)


def test_em_tech_from_yaml_roundtrip(tmp_path):
    pytest.importorskip("yaml")
    assert "ihp-sg13g2" in em.builtin_techs()
    tech = em.EmTech.builtin("ihp-sg13g2")
    assert tech.metals["TopMetal2"] == 134
    assert tech.via_stack["TopVia2"] == ("TopMetal1", "TopMetal2")
    assert tech.subgnd_layer == 210
    # every port layer must stay clear of the stackup layer numbers
    taken = set(tech.metals.values()) | set(tech.vias.values()) | {tech.subgnd_layer}
    assert not taken & set(range(tech.port_layer_base + 1, tech.port_layer_base + 33))


def test_em_to_subckt_rc_network(tmp_path):
    skrf = pytest.importorskip("skrf")
    # canned 2-port: series R=10 with shunt C=50 fF at port 2, analytic ABCD -> S
    f = np.linspace(1e8, 60e9, 121)
    w = 2 * np.pi * f
    z0 = 50.0
    r, c = 10.0, 50e-15
    a = np.empty((f.size, 2, 2), complex)
    a[:, 0, 0] = 1 + 1j * w * c * r
    a[:, 0, 1] = r
    a[:, 1, 0] = 1j * w * c
    a[:, 1, 1] = 1
    d = a[:, 0, 0] * z0 + a[:, 0, 1] + a[:, 1, 0] * z0 * z0 + a[:, 1, 1] * z0
    s = np.empty_like(a)
    s[:, 0, 0] = (a[:, 0, 0] * z0 + a[:, 0, 1] - a[:, 1, 0] * z0 * z0 - a[:, 1, 1] * z0) / d
    s[:, 0, 1] = 2 * (a[:, 0, 0] * a[:, 1, 1] - a[:, 0, 1] * a[:, 1, 0]) * z0 / d
    s[:, 1, 0] = 2 * z0 / d
    s[:, 1, 1] = (-a[:, 0, 0] * z0 + a[:, 0, 1] - a[:, 1, 0] * z0 * z0 + a[:, 1, 1] * z0) / d
    nw = skrf.Network(f=f, s=s, z0=z0, f_unit="hz")
    ts = str(tmp_path / "rc.s2p")
    nw.write_touchstone(ts[:-4])
    out = em.em_to_subckt(ts, str(tmp_path / "rc.sub"), name="rc_fit",
                          n_poles=2, dc_r={(1, 2): r})
    txt = open(out).read()
    assert ".subckt rc_fit" in txt.lower()
    assert os.path.getsize(out) > 200


def test_em_sim_from_yaml_combined_file(tmp_path):
    pytest.importorskip("yaml")
    cfg = tmp_path / "em.yaml"
    cfg.write_text(
        "tech: {metals: {Metal1: 8}, vias: {}, via_stack: {}}\n"
        "sim: {fstop: 50e9, numfreq: 101, cellsize_um: 0.4,\n"
        "      boundary: [PEC, PEC, PEC, PEC, PEC, MUR],\n"
        "      excite_ports: [1, 2]}\n")
    tech = em.EmTech.from_yaml(str(cfg))
    sim = em.EmSim.from_yaml(str(cfg))
    assert tech.metals == {"Metal1": 8}
    assert sim.fstop == 50e9 and sim.numfreq == 101
    assert sim.boundary[-1] == "MUR" and sim.excite_ports == (1, 2)
    assert em.EmSim().energy_limit_db == -40.0


def test_em_config_loading_is_loud_and_overridable(tmp_path, caplog):
    import logging

    pytest.importorskip("yaml")
    cfg = tmp_path / "sim.yaml"
    cfg.write_text("fstop: 50e9\n")
    with caplog.at_level(logging.WARNING, logger="spicexplorer_layout.em"):
        sim = em.EmSim.from_yaml(str(cfg), numfreq=101)
    assert sim.fstop == 50e9 and sim.numfreq == 101     # override beats file
    msg = " ".join(r.message for r in caplog.records)
    assert "DEFAULTS" in msg and "cellsize_um" in msg   # silent fallbacks named
    assert "numfreq" not in msg.split("DEFAULTS")[1]    # overridden != defaulted
    with pytest.raises(ValueError, match="unknown keys.*cellsize"):
        cfg2 = tmp_path / "bad.yaml"
        cfg2.write_text("cellsize: 0.4\n")             # wrong key name -> loud error
        em.EmSim.from_yaml(str(cfg2))
