"""Two harness gaps the first X-card-passive circuit (ldo_010_capless_lowiq) exposed.

1. **A PDK device SUBCKT instantiated as a passive.** circuitgraph types a 2-node
   ``XCC a b cap_cmim w= l=`` as ``CAP`` and a 3-node ``XR1 a b sub rhigh w= l=`` as ``RES``,
   not as ``SUBCKT`` — so the master name landed in ``params:`` under ``Value`` and the
   parameterization layer read it as a free knob named ``cap_cmim``/``rhigh``. It then
   demanded a ``sizing.yaml`` row for it (there can be none: it is a device reference).
   A PRIMITIVE ``R1 a b 'r_top'`` must keep its ``Value`` — that one IS a knob — so the
   discriminator is the ``X`` prefix, exactly as in SPICE.

2. **Several bindings of one class template.** A circuit may bind the same class testbench at
   several operating points (``psrr`` at 1 kHz and ``psrr_1m`` at 1 MHz; ``ac_loopgain{,_lo,_hi}``
   at three loads). The Tier-0 ``xref:analyses_in_class`` row compared the analysis ID against the
   class template names, so the extra bindings failed even though their own ``analyses/<id>.yaml``
   names a real class template in ``template:`` — which the sibling ``xref:template:<id>`` row
   was already resolving correctly.

3. **A drawn passive is not gate area.** ``ppa.area_report`` booked every card carrying ``w``/``l``
   as a transistor, so the MIM plates and the two poly-resistor chains landed on the scoreboard's
   ACTIVE GATE AREA axis: 16937 um2 against a true 91.8 um2 of gate, a Pareto axis wrong by 184x.
   The instance letter cannot decide this (every device is an ``X``-card here); the master name can.
"""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import model, params, ppa, verify


def _graph(components):
    return {"components": components, "nets": {}, "meta": {}}


def test_xcard_passive_master_is_not_a_knob():
    """``Value`` is a device reference on an X-card CAP/RES, a free knob on a primitive."""
    g = _graph(
        [
            {
                "id": "XCC",
                "device_type": "CAP",
                "params": {"Value": "cap_cmim", "w": "c_w", "l": "c_w"},
            },
            {
                "id": "XR1",
                "device_type": "RES",
                "params": {"Value": "rhigh", "w": "r_w", "l": "r_l"},
            },
            {"id": "C1", "device_type": "CAP", "params": {"Value": "c_out"}},
            {"id": "R1", "device_type": "RES", "params": {"Value": "r_top"}},
        ]
    )
    inv = params.atomic_inventory(g)
    assert "Value" not in inv["XCC"] and "Value" not in inv["XR1"]
    assert inv["C1"] == {"Value": "c_out"} and inv["R1"] == {"Value": "r_top"}
    # the symbol closure must not demand a sizing row for the master names either
    syms = params.netlist_symbols(g)
    assert "cap_cmim" not in syms and "rhigh" not in syms
    assert {"c_w", "r_w", "r_l", "c_out", "r_top"} <= syms


def test_analysis_id_may_bind_a_class_template_under_another_name():
    """The ported LDO binds three ``ac_loopgain`` loads and two ``psrr`` frequencies."""
    c = model.load_circuit("ldo_010_capless_lowiq")
    templates = set(model.class_templates(c.klass))
    extras = [a for a in c.analyses if a not in templates]
    assert extras, "the fixture circuit no longer has alias-bound analyses"
    for aid in extras:
        assert c.analysis(aid)["template"] in templates
    rows = {r.check: r for r in verify.run_tier0([c.id])}
    assert rows["xref:analyses_in_class"].status == "pass"


def test_drawn_passives_are_not_booked_as_gate_area():
    """The MIM caps and the two rhigh chains are inventory, not transistor gate."""
    c = model.load_circuit("ldo_010_capless_lowiq")
    rep = ppa.area_report(c, "ihp-sg13g2")
    assert rep["mos_count"] == 24  # 24 MOS cards, common-centroid halves included
    assert rep["c_count"] == 3 and rep["r_count"] == 21  # XCC/XCFF/XCOUT + 8+8 divider + 5 bias
    assert rep["active_gate_area_um2"] == pytest.approx(91.834, abs=0.01)
    assert rep["active_gate_area_um2"] < 200, "a drawn passive is being read as a gate again"
    # the passives resolve through the registry's measured tt constants, not as zeroes
    assert rep["c_total_f"] == pytest.approx(2.498272e-11, rel=1e-6)
    assert rep["r_total_ohm"] == pytest.approx(2480055.0, rel=1e-6)


def test_every_lowered_wl_card_names_a_declared_device():
    """Corpus guard: an unclassifiable ``X`` master must fail loudly, never default to MOS."""
    for cid in model.list_circuit_ids():
        c = model.load_circuit(cid)
        if c.is_reference_only:
            continue
        for pdk in c.pdks:
            ppa.area_report(c, pdk)  # raises PpaError on an undeclared subckt master
