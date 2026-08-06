"""Parameterization P1 + P2.

P1 — the ``gen-params`` generator (generated-then-reviewed refresh) + the Tier-1 verify
checks (referential soundness, kind coherence, symbol closure, detected-but-untied WARNING).

P2 — lowering the tying layer to ``.param`` tie blocks (untying = shadowing) + the numeric
parity acceptance for the ``amp_001_5t`` dry-run migration: the NEW atomic deck resolves to
exactly the OLD committed per-device geometry on every PDK binding.
"""

from __future__ import annotations

import re

import pytest
import yaml

from spicexplorer_analog_db import model, params, ppa, schema, verify

# --------------------------------------------------------------------------- synthetic fixtures


def _mos(cid, drain, gate, source, bulk, polarity="NMOS", w=None, l=None, m=None):  # noqa: E741
    return {
        "id": cid,
        "device_type": "MOS",
        "polarity": polarity,
        "connections": {"DRAIN": drain, "GATE": gate, "SOURCE": source, "BULK": bulk},
        "params": {
            "w": w or f"x_dut_{cid.lower()}_w",
            "l": l or f"x_dut_{cid.lower()}_l",
            "m": m if m is not None else f"x_dut_{cid.lower()}_m",
        },
    }


def _graph(components, supplies=("vdd", "vss")):
    nets = sorted(
        {n for c in components for n in (c.get("connections") or {}).values() if n is not None}
    )
    return {
        "components": components,
        "nets": [{"name": n, "is_supply": n in supplies, "supply_type": ""} for n in nets],
        "meta": {},
    }


@pytest.fixture()
def five_t_graph():
    """A synthetic 5T OTA graph (same shape as amp_001_5t's committed cgraph)."""
    return _graph(
        [
            _mos("XM1", "outm", "vinp", "tail", "vss"),
            _mos("XM2", "vout", "vinn", "tail", "vss"),
            _mos("XM3", "outm", "outm", "vdd", "vdd", polarity="PMOS"),
            _mos("XM4", "vout", "outm", "vdd", "vdd", polarity="PMOS"),
            _mos("XM5", "tail", "ibias", "vss", "vss"),
            _mos("XM6", "ibias", "ibias", "vss", "vss"),
        ]
    )


def _doc(graph, groups=None, ratios=None):
    doc = {"schema": params.SCHEMA_ID, "devices": params.atomic_inventory(graph)}
    if groups:
        doc["groups"] = groups
    if ratios:
        doc["ratios"] = ratios
    return doc


# --------------------------------------------------------------------------- P1: generator


def test_refresh_preserves_authored_groups_and_ratios(five_t_graph):
    authored = _doc(
        five_t_graph,
        groups=[{"name": "input_pair", "kind": "matched_pair", "members": ["XM1", "XM2"], "tie": ["w", "l", "m"]}],
        ratios=[{"param": "m", "ref": "XM5", "of": "XM6", "ratio": "17/3"}],
    )
    authored["devices"] = {"stale": {"w": "gone"}}  # a stale inventory must be regenerated …
    doc = params.refresh_params_doc(authored, five_t_graph)
    assert set(doc["devices"]) == {"XM1", "XM2", "XM3", "XM4", "XM5", "XM6"}
    # … while the AUTHORED sections come through verbatim (the human review is never clobbered)
    assert doc["groups"] == authored["groups"]
    assert doc["ratios"] == authored["ratios"]


def test_render_params_yaml_is_deterministic_and_roundtrips(five_t_graph):
    doc = params.propose_params_doc(five_t_graph)
    a = params.render_params_yaml(doc, "fake")
    b = params.render_params_yaml(params.propose_params_doc(five_t_graph), "fake")
    assert a == b
    parsed = yaml.safe_load(a)
    assert schema.validation_errors(parsed, "params") == []
    assert parsed == doc


def test_committed_amp_001_5t_params_yaml_is_generator_stable():
    """The committed dry-run file == its own gen-params refresh (drift-free adoption)."""
    c = model.load_circuit("amp_001_5t")
    graph = params.load_graph(c.dir / "abstract" / "topology.cgraph.json")
    committed = (c.dir / "abstract" / "params.yaml").read_text()
    doc = params.refresh_params_doc(yaml.safe_load(committed), graph)
    assert params.render_params_yaml(doc, c.id) == committed


# --------------------------------------------------------------------------- P1: Tier-1 checks


class _FakeCircuit:
    """The minimal Circuit surface `_tier1_params_checks` consumes."""

    def __init__(self, tmp_path, graph, doc, sizing_vars, pdks=("fake",)):
        import json

        self.id = "fake"
        self.dir = tmp_path
        self.pdks = list(pdks)
        (tmp_path / "abstract").mkdir(parents=True, exist_ok=True)
        (tmp_path / "abstract" / "topology.cgraph.json").write_text(json.dumps(graph))
        (tmp_path / "abstract" / "params.yaml").write_text(
            yaml.safe_dump(doc, sort_keys=False)
        )
        self._sizing = {"variables": [{"name": n, "default": 1} for n in sizing_vars]}
        for pdk in self.pdks:
            (tmp_path / "pdk" / pdk).mkdir(parents=True, exist_ok=True)
            (tmp_path / "pdk" / pdk / "sizing.yaml").write_text(yaml.safe_dump(self._sizing))

    def sizing(self, pdk):
        return self._sizing


def _by_check(results):
    return {r.check: r for r in results}


def _free_sizing(doc):
    return sorted(params.free_symbols(doc))


def test_tier1_all_green_with_untied_warning(tmp_path, five_t_graph):
    """The dry-run posture: pairs tied, tail mirror deliberately untied → all checks pass and
    the untied mirror surfaces as a WARNING (skip), never a failure."""
    doc = _doc(
        five_t_graph,
        groups=[
            {"name": "input_pair", "kind": "matched_pair", "members": ["XM1", "XM2"], "tie": ["w", "l", "m"]},
            {"name": "load_pair", "kind": "matched_pair", "members": ["XM3", "XM4"], "tie": ["w", "l", "m"]},
        ],
    )
    c = _FakeCircuit(tmp_path, five_t_graph, doc, _free_sizing(doc))
    res = _by_check(verify._tier1_params_checks(c))
    assert res["params:refs"].status == "pass"
    assert res["params:kind:input_pair"].status == "pass"
    assert res["params:kind:load_pair"].status == "pass"  # diode half + supply source: still a pair
    assert res["params:symbols"].status == "pass"
    assert res["params:sizing:fake"].status == "pass"
    warn = res["params:untied_symmetry"]
    assert warn.status == "skip" and "XM6" in warn.reason  # the untied tail mirror — a warning


def test_tier1_missing_member_and_tie_field_fail(tmp_path, five_t_graph):
    doc = _doc(
        five_t_graph,
        groups=[{"name": "ghost", "kind": "shared_geometry", "members": ["XM1", "XM9"], "tie": ["w", "ng"]}],
        ratios=[{"param": "m", "ref": "XM8", "of": "XM6", "ratio": 2}],
    )
    c = _FakeCircuit(tmp_path, five_t_graph, doc, _free_sizing(doc))
    row = _by_check(verify._tier1_params_checks(c))["params:refs"]
    assert row.status == "fail"
    assert "XM9" in row.reason and "ng" in row.reason and "XM8" in row.reason


@pytest.mark.parametrize(
    "group,why",
    [
        # three members can't be a matched_pair
        ({"name": "g", "kind": "matched_pair", "members": ["XM1", "XM2", "XM5"], "tie": ["w"]}, "exactly 2"),
        # NMOS+PMOS is not a pair
        ({"name": "g", "kind": "matched_pair", "members": ["XM1", "XM3"], "tie": ["w"]}, "polarit"),
        # distinct source nets (XM1 on tail, XM6 on vss)
        ({"name": "g", "kind": "matched_pair", "members": ["XM1", "XM6"], "tie": ["w"]}, "SOURCE"),
        # input pair claimed as a mirror: no diode-connected member
        ({"name": "g", "kind": "mirror_length", "members": ["XM1", "XM2"], "tie": ["l"]}, "GATE"),
        # mirror halves on different gates
        ({"name": "g", "kind": "mirror_length", "members": ["XM3", "XM6"], "tie": ["l"]}, "polarit"),
    ],
)
def test_tier1_kind_incoherence_fails(tmp_path, five_t_graph, group, why):
    doc = _doc(five_t_graph, groups=[group])
    c = _FakeCircuit(tmp_path, five_t_graph, doc, _free_sizing(doc))
    row = _by_check(verify._tier1_params_checks(c))["params:kind:g"]
    assert row.status == "fail" and why.lower() in row.reason.lower()


def test_tier1_mirror_kind_coherent(tmp_path, five_t_graph):
    doc = _doc(
        five_t_graph,
        groups=[{"name": "tail_mirror", "kind": "mirror_length", "members": ["XM6", "XM5"], "tie": ["l"]}],
    )
    c = _FakeCircuit(tmp_path, five_t_graph, doc, _free_sizing(doc))
    res = _by_check(verify._tier1_params_checks(c))
    assert res["params:kind:tail_mirror"].status == "pass"


def test_tier1_symbol_closure_catches_uninventoried_netlist_symbol(tmp_path, five_t_graph):
    doc = _doc(five_t_graph)
    del doc["devices"]["XM6"]  # netlist still uses x_dut_xm6_* → closure must fail
    c = _FakeCircuit(tmp_path, five_t_graph, doc, _free_sizing(doc))
    row = _by_check(verify._tier1_params_checks(c))["params:symbols"]
    assert row.status == "fail" and "x_dut_xm6_w" in row.reason


def test_tier1_sizing_closure_failures(tmp_path, five_t_graph):
    doc = _doc(
        five_t_graph,
        groups=[{"name": "input_pair", "kind": "matched_pair", "members": ["XM1", "XM2"], "tie": ["w", "l", "m"]}],
    )
    free = _free_sizing(doc)
    # missing free symbol → the deck's .param would be undefined → FAIL
    c = _FakeCircuit(tmp_path / "a", five_t_graph, doc, [s for s in free if s != "x_dut_xm5_w"])
    row = _by_check(verify._tier1_params_checks(c))["params:sizing:fake"]
    assert row.status == "fail" and "x_dut_xm5_w" in row.reason and "undefined" in row.reason
    # a sizing row for a TIED symbol double-defines it → FAIL
    c = _FakeCircuit(tmp_path / "b", five_t_graph, doc, [*free, "x_dut_xm2_w"])
    row = _by_check(verify._tier1_params_checks(c))["params:sizing:fake"]
    assert row.status == "fail" and "x_dut_xm2_w" in row.reason
    # a sizing row for a symbol the inventory doesn't know → FAIL
    c = _FakeCircuit(tmp_path / "c", five_t_graph, doc, [*free, "x_dut_bogus"])
    row = _by_check(verify._tier1_params_checks(c))["params:sizing:fake"]
    assert row.status == "fail" and "x_dut_bogus" in row.reason


def test_tier1_no_params_yaml_no_rows(tmp_path):
    from types import SimpleNamespace

    (tmp_path / "abstract").mkdir()
    fake = SimpleNamespace(id="fake", dir=tmp_path, pdks=[])
    assert verify._tier1_params_checks(fake) == []


# --------------------------------------------------------------------------- P2: tie lowering


def test_tie_param_lines_groups_and_ratios(five_t_graph):
    doc = _doc(
        five_t_graph,
        groups=[
            {"name": "input_pair", "kind": "matched_pair", "members": ["XM1", "XM2"], "tie": ["w", "l", "m"]},
            {"name": "mirror_l", "kind": "mirror_length", "members": ["XM6", "XM5"], "tie": ["l"]},
        ],
        ratios=[{"param": "m", "ref": "XM5", "of": "XM6", "ratio": "17/3"}],
    )
    lines = params.tie_param_lines(doc)
    assert lines == [
        ".param x_dut_xm2_w = {x_dut_xm1_w}",
        ".param x_dut_xm2_l = {x_dut_xm1_l}",
        ".param x_dut_xm2_m = {x_dut_xm1_m}",
        ".param x_dut_xm5_l = {x_dut_xm6_l}",
        ".param x_dut_xm5_m = {x_dut_xm6_m*17/3}",
    ]
    assert params.tied_symbols(doc) == {
        "x_dut_xm2_w", "x_dut_xm2_l", "x_dut_xm2_m", "x_dut_xm5_l", "x_dut_xm5_m",
    }
    # free = first members + untied atomics; sizing keys on exactly these
    free = params.free_symbols(doc)
    assert "x_dut_xm1_w" in free and "x_dut_xm6_l" in free and "x_dut_xm5_w" in free
    assert free.isdisjoint(params.tied_symbols(doc))
    assert params.tie_expressions(doc)["x_dut_xm5_m"] == "x_dut_xm6_m*17/3"


def test_tie_lines_skip_frozen_literals(five_t_graph):
    doc = _doc(
        five_t_graph,
        groups=[{"name": "p", "kind": "matched_pair", "members": ["XM1", "XM2"], "tie": ["w", "m"]}],
    )
    doc["devices"]["XM1"]["m"] = 1  # frozen literal anchor → no m tie emitted
    doc["devices"]["XM2"]["m"] = 1
    assert params.tie_param_lines(doc) == [".param x_dut_xm2_w = {x_dut_xm1_w}"]


def test_dut_subckt_without_params_yaml_is_unchanged(tmp_path):
    """Zero churn for a non-adopted circuit: no params.yaml → no tie block. Post-P4 the whole
    verifiable catalog has adopted the layer, so the contract is exercised synthetically."""
    from types import SimpleNamespace

    from spicexplorer_analog_db.assemble import _tie_block

    (tmp_path / "abstract").mkdir()
    assert _tie_block(SimpleNamespace(dir=tmp_path)) == ""


def test_dut_subckt_defines_each_tied_symbol_exactly_once():
    """Untying-by-shadowing precondition: one definition per tied symbol, from its tie line."""
    from spicexplorer_analog_db.assemble import dut_subckt

    c = model.load_circuit("amp_001_5t")
    text = dut_subckt(c, "ihp-sg13g2")
    doc = params.load_params_doc(c.dir)
    assert doc is not None
    for sym in sorted(params.tied_symbols(doc)):
        assert len(re.findall(rf"^\.param {sym}\b", text, re.MULTILINE)) == 1, sym
    for sym in sorted(params.free_symbols(doc)):
        assert len(re.findall(rf"^\.param {sym}=", text, re.MULTILINE)) == 1, sym


# --------------------------------------------------------------------------- P2: numeric parity
#
# The dry-run acceptance: the NEW atomic deck at default ties resolves to the SAME
# per-device {w, l, m} as the OLD committed deck (pre-migration main). The OLD geometry below is
# the resolved `git show main:raw/amp_001_5t/<pdk>/_dut.spice` param header — hardcoded so the
# gate needs no git history at test time.

_UM = 1e-6
_OLD_GEOMETRY = {
    # pdk: {device: (w, l, m)} — resolved values in the deck's own unit convention
    "ihp-sg13g2": {  # gm/ID re-size (2026-07-22): sizing.yaml defaults, XM2/XM4 tied
        "XM1": (10.0 * _UM, 10.0 * _UM, 1), "XM2": (10.0 * _UM, 10.0 * _UM, 1),
        "XM3": (10.0 * _UM, 7.0 * _UM, 1), "XM4": (10.0 * _UM, 7.0 * _UM, 1),
        "XM5": (3.8 * _UM, 1.0 * _UM, 1), "XM6": (3.8 * _UM, 1.0 * _UM, 1),
    },
    "sky130": {  # bare-µm convention (.option scale=1u decks)
        "XM1": (1.0, 2.0, 1), "XM2": (1.0, 2.0, 1),
        "XM3": (2.0, 2.0, 1), "XM4": (2.0, 2.0, 1),
        "XM5": (3.0, 2.0, 1), "XM6": (3.0, 2.0, 1),
    },
    "gf180mcu": {  # refreshed 2026-08-03: honest-gf-round winner committed as defaults
        "XM1": (0.5 * _UM, 5 * _UM, 1),
        "XM2": (0.5 * _UM, 5 * _UM, 1),
        "XM3": (1.5 * _UM, 5 * _UM, 1),
        "XM4": (1.5 * _UM, 5 * _UM, 1),
        "XM5": (2 * _UM, 5 * _UM, 1),
        # m was transcribed as a width-shaped 1.17172e-05 in the 2026-08-03 refresh; the deck
        # (and every sibling PDK) carries x_dut_xm6_m=1.
        "XM6": (2 * _UM, 5 * _UM, 1),
    },
    "FOUNDRY-n65": {
        "XM1": (0.5 * _UM, 5 * _UM, 1), "XM2": (0.5 * _UM, 5 * _UM, 1),
        "XM3": (1.5 * _UM, 5 * _UM, 1), "XM4": (1.5 * _UM, 5 * _UM, 1),
        "XM5": (2 * _UM, 5 * _UM, 1), "XM6": (2 * _UM, 5 * _UM, 1),
    },
}

_PARAM_LINE = re.compile(r"^\.param\s+(\w+)\s*=\s*(.+?)\s*$", re.MULTILINE)
_FIELD = re.compile(r"\b([wlm])=(\S+)")


def resolve_deck_geometry(deck_text: str) -> dict[str, tuple[float, float, float]]:
    """Resolve a ``_dut.spice`` param graph (defaults + tie lines) to per-device {w, l, m}."""
    symbols: dict[str, float] = {}
    pending: dict[str, str] = {}
    for name, rhs in _PARAM_LINE.findall(deck_text):
        val = ppa.parse_eng(rhs)
        if val is not None:
            symbols[name] = val
        else:
            pending[name] = rhs.strip().strip("{}")
    for _ in range(len(pending) + 1):  # ties may chain — fixpoint
        for name, expr in list(pending.items()):
            try:
                symbols[name] = ppa._eval_expr(expr, symbols, name)
                del pending[name]
            except ppa.PpaError:
                continue
        if not pending:
            break
    assert not pending, f"unresolvable .param graph: {pending}"

    out: dict[str, tuple[float, float, float]] = {}
    in_subckt = False
    for ln in deck_text.splitlines():
        s = ln.strip()
        if s.lower().startswith(".subckt"):
            in_subckt = True
            continue
        if not in_subckt or not s or s.startswith("*") or s.startswith("."):
            continue
        fields = dict(_FIELD.findall(s))
        if {"w", "l"} <= set(fields):
            resolved = tuple(
                ppa._eval_expr(fields.get(f, "1"), symbols, s.split()[0]) for f in ("w", "l", "m")
            )
            out[s.split()[0].upper()] = resolved
    return out


@pytest.mark.parametrize("pdk", sorted(_OLD_GEOMETRY))
def test_amp_001_5t_numeric_parity_with_pre_migration_deck(pdk):
    from spicexplorer_analog_db import export

    c = model.load_circuit("amp_001_5t")
    new = resolve_deck_geometry(export.dut_path(c, pdk).read_text())
    old = _OLD_GEOMETRY[pdk]
    assert set(new) == set(old)
    for dev, (w, length, m) in old.items():
        nw, nl, nm = new[dev]
        assert nw == pytest.approx(w, rel=1e-12), (pdk, dev, "w")
        assert nl == pytest.approx(length, rel=1e-12), (pdk, dev, "l")
        assert nm == pytest.approx(m, rel=1e-12), (pdk, dev, "m")


# ---------------------------------------------------------------- provenance info surfaces


def test_classify_symbols_and_counts_line(five_t_graph):
    from spicexplorer_analog_db import params as par

    doc = par.propose_params_doc(five_t_graph)
    sizing_vars = [
        {"name": sym, "freeze": sym.endswith("_m")} for sym in par.free_symbols(doc)
    ]
    cls = par.classify_symbols(doc, sizing_vars)
    all_syms = {s for v in cls.values() for s in v}
    assert all_syms == par.free_symbols(doc) | par.tied_symbols(doc)
    assert set(cls["frozen"]) == {s for s in par.free_symbols(doc) if s.endswith("_m")}
    assert not set(cls["free"]) & set(cls["frozen"])
    line = par.counts_line(cls)
    assert "free" in line and "tied" in line and "testbench" not in line
    assert "4 testbench params" in par.counts_line(cls, tb_params=4)


def test_amp_001_5t_deck_banner_counts_and_catalog_block():
    from spicexplorer_analog_db import catalog, export, model

    c = model.load_circuit("amp_001_5t")
    dut = export.render_dut(c, "ihp-sg13g2")
    assert "** params: 8 free + 4 frozen knobs" in dut
    assert "testbench params" not in dut  # DUT-only file: no TB param count
    deck = export.render_deck(c, "ac_open_loop", "ihp-sg13g2")
    assert "· 6 tied · 0 ratio-derived" in deck
    assert "testbench params" in deck

    entry = next(e for e in catalog.build_catalog()["circuits"] if e["id"] == "amp_001_5t")
    block = entry["params"]
    assert block["devices"] == 6
    assert block["groups"] == {"input_pair": "matched_pair", "load_pair": "matched_pair"}
    assert block["symbols"]["ihp-sg13g2"] == {"free": 8, "frozen": 4, "tied": 6, "ratio": 0}
    assert any("XM6" in w and "XM5" in w for w in block["untied_symmetries"])


def test_non_adopted_circuit_renders_without_params_line(monkeypatch):
    """A circuit without abstract/params.yaml renders with NO provenance line (byte-identical
    legacy output). Synthetic — every corpus circuit is adopted."""
    from spicexplorer_analog_db import export, model, params

    monkeypatch.setattr(params, "load_params_doc", lambda _dir: None)
    c = model.load_circuit("amp_001_5t")
    dut = export.render_dut(c, "ihp-sg13g2")
    assert "** params:" not in dut
    assert ".subckt amp_001_5t" in dut


def test_tier1_inventory_info_row():
    from spicexplorer_analog_db import model, verify

    c = model.load_circuit("amp_001_5t")
    rows = [r for r in verify._tier1_params_checks(c) if r.check.startswith("params:inventory")]
    assert {r.check.rsplit(":", 1)[1] for r in rows} == set(c.pdks)
    assert all(r.status == "pass" for r in rows)
    assert all("8 free + 4 frozen" in r.reason for r in rows)
