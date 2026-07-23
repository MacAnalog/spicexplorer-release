"""The pluggable serialization-strategy framework + comparison harness."""

from pathlib import Path

import pytest
from spicexplorer_circuitgraph import (
    IHP_SG13G2,
    CircuitGraph,
    Serializer,
    evaluate_strategies,
    get_strategy,
    list_strategies,
    register,
    serialize,
    unregister,
)
from spicexplorer_core.spice_engine import NetlistView

_FIX = Path(__file__).resolve().parent / "fixtures"
CASCODE_FLAT = _FIX / "ota-improved.spice"
FOLDED_TB = _FIX / "cora_testbench_ac.spice"

_BUILTINS = {
    "flat",
    "nested",
    "net_centric",
    "llm_description",
    "role_detection",
    "topology",
    "structural_role_summary",
}


def _flat() -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_file(CASCODE_FLAT), pdk=IHP_SG13G2)


def _subckt() -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_file(FOLDED_TB), pdk=IHP_SG13G2)


# --- registry ------------------------------------------------------------------------------
def test_all_builtin_strategies_registered():
    assert set(list_strategies()) == _BUILTINS


@pytest.mark.parametrize("name", sorted(_BUILTINS))
def test_every_strategy_renders_flat_and_subckt_graphs(name):
    for g in (_flat(), _subckt()):
        out = serialize(g, name)
        assert isinstance(out, (dict, str))
        assert out  # non-empty
        assert get_strategy(name).kind in {"json", "text"}


def test_unknown_strategy_raises_with_known_names():
    with pytest.raises(KeyError, match="unknown serializer"):
        serialize(_flat(), "does_not_exist")


def test_registering_a_new_strategy_is_a_one_object_change():
    @register
    class _Toy(Serializer):
        name = "toy_test_only"
        kind = "text"

        # A strategy accepts **_ for forward-compat with new render kwargs (e.g. include_spice_model).
        def render(self, graph, *, include_params=False, include_body=False, **_):
            return f"toy:{graph.component_count}"

    try:
        assert "toy_test_only" in list_strategies()  # auto-discovered
        assert serialize(_flat(), "toy_test_only") == "toy:24"
        # the harness picks it up automatically
        assert any(m.name == "toy_test_only" for m in evaluate_strategies(_flat()))
    finally:
        unregister("toy_test_only")  # keep the global registry clean for other tests

    with pytest.raises(ValueError, match="duplicate serializer"):

        @register
        class _Dup(Serializer):
            name = "flat"  # collides with a builtin
            kind = "json"

            def render(self, graph, *, include_params=False, include_body=False):
                return {}


# --- golden output (locks the canonical view shapes; flat + subckt-aware) ------------------
def test_golden_flat_primitive():
    # Body pin is dropped by default — descriptions omit the BULK tie to avoid clutter.
    flat = serialize(_flat(), "flat")
    assert flat["XM1"] == {
        "DRAIN": "net4", "GATE": "vinp", "SOURCE": "tail",
        "type": "Nmos_Mosfet", "spice_model": "sg13_lv_nmos",
    }


def test_flat_include_body_restores_bulk():
    # Opt-in include_body=True brings the MOSFET BULK terminal back into the view.
    flat = serialize(_flat(), "flat", include_body=True)
    assert flat["XM1"] == {
        "DRAIN": "net4", "GATE": "vinp", "SOURCE": "tail", "BULK": "vss",
        "type": "Nmos_Mosfet", "spice_model": "sg13_lv_nmos",
    }


def test_golden_flat_subckt_instance():
    flat = serialize(_subckt(), "flat")
    assert flat["X1"] == {
        "vin-": "vin-", "vin+": "vin+", "vout": "out", "vdd": "vdd", "ib": "ib", "vss": "GND",
        "type": "SubcktInstance", "subckt_name": "opamp",
        "port_roles": {
            "vin-": "input", "vin+": "input", "vout": "output",
            "vdd": "power", "ib": "bias", "vss": "ground",
        },
    }


def test_golden_topology_text_is_stable():
    text = serialize(_subckt(), "topology")
    assert "- SubcktInstance X1 (None): ib=ib, vdd=vdd, vin+=vin+, vin-=vin-, vout=out, vss=GND" in text
    assert "- out: C2.P, X1.vout" in text  # net-to-component adjacency (sorted)


# --- NDA-safe projection (plan B2): omit the foundry model name by construction ------------
def test_nda_safe_projection_omits_spice_model_across_views():
    g = _flat()
    # default: the model rides in the JSON view (golden covers XM1 == sg13_lv_nmos)
    assert "spice_model" in serialize(g, "flat")["XM1"]

    # flat + net_centric drop spice_model entirely when include_spice_model=False ...
    safe = serialize(g, "flat", include_spice_model=False)
    assert "spice_model" not in safe["XM1"]
    # ... while connectivity + type are preserved (the topology the annotation task needs)
    assert safe["XM1"]["type"] == "Nmos_Mosfet" and safe["XM1"]["GATE"] == "vinp"
    nc = serialize(g, "net_centric", include_spice_model=False)
    assert all("spice_model" not in e for entries in nc.values() for e in entries)

    # the two text views that inline the model drop it too — no model token survives
    assert "sg13_lv_nmos" not in serialize(g, "role_detection", include_spice_model=False)
    assert "sg13_lv_nmos" not in serialize(g, "topology", include_spice_model=False)
    # sanity: the model IS present in the default text views (so the test can regress)
    assert "sg13_lv_nmos" in serialize(g, "role_detection")


def test_nda_safe_projection_composes_with_params_off():
    # The full NDA-safe payload = no model AND no params (params already default off).
    g = _flat()
    safe = serialize(g, "flat", include_spice_model=False, include_params=False)
    for entry in safe.values():
        assert "spice_model" not in entry and "params" not in entry


def test_nda_safe_projection_omits_subckt_master_name():
    # A foundry device is often a SUBCKT instance — its master name (subckt_name) is a
    # foundry-identifying token and must drop under the NDA-safe projection, while the
    # neutral port_roles + type are kept. (Regression: subckt_name used to leak the master.)
    g = _subckt()
    full = serialize(g, "flat")["X1"]
    assert full["subckt_name"] == "opamp"  # present by default
    for view in ("flat", "nested"):
        out = serialize(g, view, include_spice_model=False)
        x1 = out["X1"] if view == "flat" else next(c for c in out["components"] if c["id"] == "X1")
        assert "subckt_name" not in x1
        assert x1["type"] == "SubcktInstance" and "port_roles" in x1  # structure preserved


# --- comparison harness --------------------------------------------------------------------
def test_harness_covers_all_strategies_with_deterministic_metrics():
    metrics = {m.name: m for m in evaluate_strategies(_flat())}
    assert set(metrics) == _BUILTINS
    for m in metrics.values():
        assert m.char_count > 0
        assert m.token_estimate == m.char_count // 4
        assert m.component_coverage == 1.0  # every view names every component
    # determinism: same graph → identical metrics
    assert evaluate_strategies(_flat()) == evaluate_strategies(_flat())


def test_harness_net_coverage_distinguishes_views():
    metrics = {m.name: m for m in evaluate_strategies(_flat())}
    assert metrics["net_centric"].net_coverage == 1.0
    assert metrics["structural_role_summary"].net_coverage == 0.0  # lists components only


def test_coverage_uses_token_membership_not_substring():
    # 'net1' must NOT be reported covered just because the connected net 'net12' is in the output,
    # and an isolated net '0' must NOT match digits inside other tokens (e.g. 'R10', '100').
    nl = "* sub\n.subckt s a b\nR10 a b 100\n.ends\nX1 net1 net12 s\nR1 net12 net12 1k\n.end\n"
    g = CircuitGraph.from_netlist(NetlistView.from_string(nl), pdk=IHP_SG13G2)
    # net1 is wired only to X1.a; net12 to X1.b/R1 — both appear, '0' is not a net here.
    nc = {m.name: m for m in evaluate_strategies(g)}["net_centric"]
    assert nc.net_coverage == 1.0  # both nets genuinely present (not a substring artifact)
    # a view that omits a net scores < 1.0 (structural_role_summary names no nets at all)
    assert {m.name: m for m in evaluate_strategies(g)}["structural_role_summary"].net_coverage == 0.0
