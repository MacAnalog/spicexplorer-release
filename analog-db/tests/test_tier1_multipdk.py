"""Phase-1 gate: multi-PDK lowering + the Tier-1 generation drift guard.

Proves one abstract topology lowers to BOTH PDKs, both re-parse isomorphically, the committed
GENERATED artifacts are current, and Tier 1 is green.
"""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import generate, model, pdks

CIRCUIT = "amp_001_5t"


@pytest.fixture(scope="module")
def circuit() -> model.Circuit:
    return model.load_circuit(CIRCUIT)


def test_circuit_binds_all_pdks(circuit):
    assert {"ihp-sg13g2", "sky130", "gf180mcu"} <= set(circuit.pdks)


@pytest.mark.corpus
def test_tier1_is_fully_green(tier1_results):
    failures = [r for r in tier1_results if r.status == "fail"]
    assert not failures, "Tier 1 failures:\n" + "\n".join(f"{r.circuit} {r.check}: {r.reason}" for r in failures)
    assert any(r.circuit == CIRCUIT and r.status == "pass" for r in tier1_results)


def test_devices_map_loader_overrides_builtin(circuit):
    """The per-topology devices.map.yaml drives the lowered device names."""
    from spicexplorer_circuitgraph.model.nodes import DeviceType, MosPolarityType

    ihp = pdks.load_pdk(circuit, "ihp-sg13g2")
    sky = pdks.load_pdk(circuit, "sky130")
    gf = pdks.load_pdk(circuit, "gf180mcu")
    assert ihp.model_for(DeviceType.MOS, MosPolarityType.NMOS) == "sg13_lv_nmos"
    assert sky.model_for(DeviceType.MOS, MosPolarityType.NMOS) == "sky130_fd_pr__nfet_01v8"
    assert gf.model_for(DeviceType.MOS, MosPolarityType.NMOS) == "nfet_03v3"
    # gf180 inherits the `nf` finger convention from the circuitgraph built-in (Phase-1 loader);
    # like sky130 it is BSIM4 whose instance `w` is the TOTAL width (BSIM4 divides by `nf` internally),
    # so emit keeps `w` total and only renames ng→nf — width_per_finger=False. Verified by ngspice on
    # nfet_03v3: splitting a fixed `w` across nf=4 leaves Id ~unchanged (i(w=8u,nf=4)/i(w=8u,nf=1)≈0.97,
    # NOT 4×) and Id scales linearly with the instance `w` (i(w=8u)/i(w=2u)=4.00). See circuitgraph
    # pdk.py SKYWATER_SKY130: dividing here would double-divide → sub-µm per-finger device, bad bin.
    assert gf.finger_param == "nf" and not gf.width_per_finger


def test_both_lowerings_retarget_and_reparse(circuit):
    from spicexplorer_circuitgraph import CircuitGraph
    from spicexplorer_core.spice_engine import NetlistView

    abstract = CircuitGraph.from_netlist(
        NetlistView.from_file(str(circuit.dir / "abstract" / "netlist.spice")), name=CIRCUIT
    )
    expect = {
        "ihp-sg13g2": ("sg13_lv_nmos", "sg13_lv_pmos"),
        "sky130": ("sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"),
        "gf180mcu": ("nfet_03v3", "pfet_03v3"),
    }
    for pdk, (nfet, pfet) in expect.items():
        text = (circuit.dir / "pdk" / pdk / "netlist.spice").read_text()
        assert nfet in text and pfet in text
        # committed == regenerated (drift guard)
        assert text == generate.lowered_netlist(circuit, pdk)
        # isomorphic re-parse
        lg = CircuitGraph.from_netlist(NetlistView.from_string(text), name=CIRCUIT)
        assert lg.component_count == abstract.component_count
        assert lg.net_count == abstract.net_count


def test_pdk_registries_present():
    assert {"ihp-sg13g2", "sky130", "gf180mcu"} <= set(pdks.registry_ids())
    assert pdks.load_registry("sky130")["supply"]["default"] == 1.8
    assert pdks.load_registry("gf180mcu")["supply"]["default"] == 3.3
