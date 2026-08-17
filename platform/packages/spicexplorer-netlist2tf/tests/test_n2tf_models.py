"""Stage-2 small-signal modeling tests — fidelity ladder, registry, and real-fixture expansion."""

from __future__ import annotations

from pathlib import Path

import pytest
import sympy as sp
from spicexplorer_core.spice_engine import NetlistView
from spicexplorer_netlist2tf import (
    DeviceKind,
    Fidelity,
    SmallSignalModel,
    ingest_netlist,
    register_model,
    small_signal_model,
)
from spicexplorer_netlist2tf.model.primitives import (
    VCCS,
    Capacitor,
    Conductance,
    IndependentV,
)
from spicexplorer_netlist2tf.models import MODEL_REGISTRY, SymbolMint, expand_mosfet

_FIX = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="module")
def ota5t():
    tb = _FIX / "ota-5t_tb-ac.spice"
    ota = NetlistView.from_file(tb).get_subcircuit_named("ota")
    assert ota is not None
    return ingest_netlist(ota, name="ota5t")


# ------------------------------------------------------------------------
# Fidelity ladder = primitive selection
# ------------------------------------------------------------------------
def _mosfet(ir):
    return ir.device("XM1")


def test_ideal_is_gm_only(ota5t):
    prims, syms = expand_mosfet(_mosfet(ota5t), SymbolMint(), Fidelity.IDEAL)
    assert [type(p) for p in prims] == [VCCS]
    assert set(syms) == {"gm"}
    # gm VCCS controlled by gate-source, output drain-source
    g = prims[0]
    assert isinstance(g, VCCS) and g.value == sp.Symbol("gm_m1", positive=True)
    # XM1 nodes d,g,s,b = gate_p,vinp,tail,vss → I(d->s)=gm·(V[g]-V[s]): np=d,nn=s,cp=g,cn=s
    assert (g.np, g.nn, g.cp, g.cn) == ("gate_p", "tail", "vinp", "tail")


def test_some_parasitic_adds_ro(ota5t):
    prims, syms = expand_mosfet(_mosfet(ota5t), SymbolMint(), Fidelity.SOME_PARASITIC)
    kinds = [type(p) for p in prims]
    assert kinds == [VCCS, Conductance]
    assert set(syms) == {"gm", "ro"}
    ro_cond = prims[1]
    assert isinstance(ro_cond, Conductance)
    assert ro_cond.value == 1 / sp.Symbol("ro_m1", positive=True)


def test_full_adds_gmb_and_four_caps(ota5t):
    prims, syms = expand_mosfet(_mosfet(ota5t), SymbolMint(), Fidelity.FULL)
    assert sum(isinstance(p, VCCS) for p in prims) == 2  # gm + gmb
    assert sum(isinstance(p, Conductance) for p in prims) == 1  # ro
    assert sum(isinstance(p, Capacitor) for p in prims) == 4  # Cgs/Cgd/Cdb/Csb
    assert set(syms) == {"gm", "ro", "gmb", "cgs", "cgd", "cdb", "csb"}


def test_three_terminal_mos_bulk_ties_to_source():
    # A 3-terminal MOS: bulk defaults to source so gmb is inert and caps reference source.
    from spicexplorer_netlist2tf import from_string

    ir = from_string("* 3-terminal nmos\nM1 d g s nmosmod\n.end", name="m3")
    prims, _ = expand_mosfet(ir.device("M1"), SymbolMint(), Fidelity.FULL)
    csb = next(p for p in prims if p.name.startswith("csb@"))
    assert isinstance(csb, Capacitor)
    assert csb.n1 == "s" and csb.n2 == "s"  # source==bulk


# ------------------------------------------------------------------------
# Symbol minting: per-instance unique
# ------------------------------------------------------------------------
def test_symbols_unique_per_instance(ota5t):
    ssir = small_signal_model(ota5t, level=Fidelity.SOME_PARASITIC)
    assert ssir.symbols["XM1"]["gm"] != ssir.symbols["XM2"]["gm"]
    assert ssir.symbols["XM1"]["gm"] == sp.Symbol("gm_m1", positive=True)
    assert ssir.symbols["XM2"]["gm"] == sp.Symbol("gm_m2", positive=True)


# ------------------------------------------------------------------------
# Stage function over a real fixture
# ------------------------------------------------------------------------
def test_small_signal_model_over_ota5t(ota5t):
    ssir = small_signal_model(ota5t, level=Fidelity.SOME_PARASITIC)
    # 13 MOSFETs × (gm VCCS + ro conductance) = 26 primitives, no skips.
    assert sum(isinstance(p, VCCS) for p in ssir.primitives) == 13
    assert sum(isinstance(p, Conductance) for p in ssir.primitives) == 13
    assert len(ssir.symbols) == 13
    assert ssir.introduced_symbols >= {"gm_m1", "ro_m1", "gm_m5"}
    assert ssir.primitives_of("XM1")  # traceable back to the device


def test_full_fidelity_symbol_count(ota5t):
    ssir = small_signal_model(ota5t, level=Fidelity.FULL)
    # 13 devices × 7 symbols (gm, ro, gmb, 4 caps)
    assert len(ssir.introduced_symbols) == 13 * 7


# ------------------------------------------------------------------------
# Independent-source passthrough
# ------------------------------------------------------------------------
def test_sources_carried_through():
    from spicexplorer_netlist2tf import from_string

    ir = from_string("* rc\nV1 in 0 dc 0 ac 1\nR1 in out 10k\nC1 out 0 1u\n.end", name="rc")
    ssir = small_signal_model(ir, level=Fidelity.SOME_PARASITIC)
    vs = [p for p in ssir.primitives if isinstance(p, IndependentV)]
    assert len(vs) == 1 and vs[0].ac == sp.Integer(1)
    assert sum(isinstance(p, Conductance) for p in ssir.primitives) == 1  # R1 → 1/10k
    assert sum(isinstance(p, Capacitor) for p in ssir.primitives) == 1


# ------------------------------------------------------------------------
# Registry extensibility — a new family needs no core/MNA change
# ------------------------------------------------------------------------
def test_register_custom_family():
    # A toy "diode as small-signal conductance" model for an otherwise-unmodeled kind.
    from spicexplorer_netlist2tf.model.primitives import Primitive

    def expand_diode(dev, mint, fidelity):
        p, n = dev.nets[0], dev.nets[1]
        gd = mint.sym("gd", dev.ref)
        prims: list[Primitive] = [Conductance(name=f"gd@{dev.ref}", n1=p, n2=n, value=gd)]
        return prims, {"gd": gd}

    model = SmallSignalModel("diode.gd", frozenset({DeviceKind.DIODE}), expand_diode)
    register_model(model)
    try:
        assert MODEL_REGISTRY[DeviceKind.DIODE] is model
    finally:
        del MODEL_REGISTRY[DeviceKind.DIODE]
