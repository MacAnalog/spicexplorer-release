"""Foreign-dialect ingest end-to-end: real Spectre/HSPICE decks → NetlistView → CircuitGraph →
find_subcircuits — the full "read, hand to circuitgraph, process" chain on committed fixtures
(verbatim AnalogGym sensing-front-end decks; see fixtures/README.md)."""

from pathlib import Path

import pytest
from spicexplorer_circuitgraph import (
    ANALOGGYM_FOUNDRY,
    CircuitGraph,
    annotate_subcircuits,
    graphs_equivalent,
    to_netlist,
)
from spicexplorer_circuitgraph.model.nodes import MosfetNode, MosPolarityType
from spicexplorer_core.spice_engine import NetlistDialect, NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures" / "dialects"
PTAT_SCS = _FIX / "ptat_65_classic.scs"
AMP_SCS = _FIX / "smcnr_se_2st_amp.scs"
AMP_SP = _FIX / "smcnr_se_2st_amp.orig.sp"
TB_SP = _FIX / "tb_ac_smcnr_se_2st_amp.sp"


def _cell_graph(path, dialect="auto"):
    v = NetlistView.from_file(path, dialect=dialect)
    name = v.get_subcircuit_names()[0]
    sub = v.get_subcircuit_named(name)
    assert sub is not None
    return CircuitGraph.from_netlist(sub, name=name)


def test_verbatim_spectre_deck_builds_typed_graph():
    g = _cell_graph(PTAT_SCS)
    mos = {c.name: c for c in g.get_components() if isinstance(c, MosfetNode)}
    assert len(mos) == 4
    # nch_mac/pch_mac classified by the token-prefix fallback — no PDK map needed
    assert mos["M1"].polarity is MosPolarityType.NMOS
    assert mos["M3"].polarity is MosPolarityType.PMOS


def test_hspice_and_spectre_forms_of_the_same_dut_are_equivalent():
    a = _cell_graph(AMP_SCS)
    b = _cell_graph(AMP_SP, dialect="hspice")
    assert graphs_equivalent(a, b)


def test_hspice_testbench_graphs_with_directives():
    v = NetlistView.from_file(TB_SP)  # auto-detects hspice on the strong cards
    assert v.dialect is NetlistDialect.HSPICE
    g = CircuitGraph.from_netlist(v, name="tb")
    assert len(g.get_components()) >= 20
    assert {d.kind for d in v.directives} >= {"option", "include", "measure", "analysis", "alter"}


def test_find_subcircuits_on_foreign_dialect_amp():
    """The 'hand it to circuitgraph for processing' proof: structure detection works on a
    Spectre-read graph — the SMCNR amp's PMOS mirror bank and PMOS diff pair are found."""
    v = NetlistView.from_file(AMP_SCS)
    name = v.get_subcircuit_names()[0]
    sub = v.get_subcircuit_named(name)
    assert sub is not None
    g = CircuitGraph.from_netlist(sub, name=name, pdk=ANALOGGYM_FOUNDRY)
    try:
        groups = annotate_subcircuits(g)
    except FileNotFoundError:
        pytest.skip("subcircuit template catalogue not present (analog-db examples not checked out)")
    classes = {(grp.mirror_class, grp.polarity) for grp in groups}
    assert any(cls == "simple" and pol == "pmos" for cls, pol in classes), classes
    assert any("pair" in cls or "diff" in cls for cls, _ in classes), classes


def test_foreign_graph_reemits_in_every_dialect():
    g = _cell_graph(AMP_SP, dialect="hspice")
    for dialect in ("spice", "spectre", "hspice"):
        text = to_netlist(g, dialect=dialect, subckt="smcnr_amp",
                          ports=["vdda", "gnda", "vin", "vip", "vout"])
        wrapped = NetlistView.from_string(text, dialect=dialect).get_subcircuit_named("smcnr_amp")
        assert wrapped is not None
        g2 = CircuitGraph.from_netlist(wrapped, name="reparse")
        assert graphs_equivalent(g, g2), dialect
