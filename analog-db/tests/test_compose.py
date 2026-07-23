"""Composer / flattener unit contract (plan_hierarchical_composition §5, P4).

Offline: locks the deterministic renaming rules (device suffix, net prefix, mechanical
x_dut_* symbol re-derivation, free-knob suffix), the card parser, the validators'
failure modes, and — against the real committed registry — that the two landed
composites regenerate byte-identically (the same drift contract T1 enforces).
"""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import compose, model, schema

# --------------------------------------------------------------------- renaming


def test_rename_symbol_mechanical_reinserts_instance_before_field():
    assert compose.rename_symbol("x_dut_xm1_w", "core") == "x_dut_xm1_core_w"
    # an already-suffixed hand-flatten symbol nests one more level
    assert compose.rename_symbol("x_dut_xm1_chrrl_1_w", "rrl") == "x_dut_xm1_chrrl_1_rrl_w"


def test_rename_symbol_free_knob_suffixes():
    assert compose.rename_symbol("vbl", "core") == "vbl_core"
    assert compose.rename_symbol("gm_val", "servo") == "gm_val_servo"


def test_value_token_rules():
    f = compose._rename_value_token
    assert f("w=x_dut_xm1_w", "core") == "w=x_dut_xm1_core_w"
    assert f("{vbl}", "core") == "{vbl_core}"
    assert f("'rout_val'", "servo") == "'rout_val_servo'"
    # numbers and keywords are untouched
    assert f("10u", "core") == "10u"
    assert f("2.5p", "core") == "2.5p"
    assert f("1e12", "core") == "1e12"
    assert f("dc", "core") == "dc"


# ------------------------------------------------------------------ card parser


def test_parse_cards_shapes():
    text = (
        "** comment\n"
        "XM1 d g s b nmos w=x_dut_xm1_w l=x_dut_xm1_l m=1\n"
        "R1 a b 'x_dut_r1_value'\n"
        "Gm_servo vss out inp inn {gm_val}\n"
        "Vb1 vb1 vss dc {vb1}\n"
        ".end\n"
    )
    cards = compose._parse_cards(text, "t")
    assert [c.name for c in cards] == ["XM1", "R1", "Gm_servo", "Vb1"]
    assert cards[0].nets == ("d", "g", "s", "b") and cards[0].model_token == "nmos"
    assert cards[2].nets == ("vss", "out", "inp", "inn")  # G-card: 4 net tokens
    assert cards[3].rest == ("dc", "{vb1}")


def test_parse_cards_rejects_directives_and_continuations():
    with pytest.raises(compose.ComposeError):
        compose._parse_cards(".param x=1\n", "t")
    with pytest.raises(compose.ComposeError):
        compose._parse_cards("R1 a b\n+ 10k\n", "t")


# ---------------------------------------------------- registry-level contract


def _composites() -> list[model.Circuit]:
    return [c for c in model.load_all_circuits() if compose.is_composite(c)]


def test_schema_registered():
    s = schema.load_schema("composition")
    assert s["$id"] == "spicexplorer/composition@1"


def test_registry_composites_validate_and_regenerate_byte_identical():
    comps = _composites()
    if not comps:
        pytest.skip("no composites in the registry yet")
    for c in comps:
        assert compose.validate(c) == [], f"{c.id} composition invalid"
        fresh = compose.compose_netlist(c)
        assert (c.dir / "abstract" / "netlist.spice").read_text() == fresh, f"{c.id} netlist drift"
        for pdk in c.pdks:
            assert (c.dir / "pdk" / pdk / "sizing.yaml").read_text() == compose.compose_sizing(
                c, pdk, fresh
            ), f"{c.id} {pdk} sizing drift"


def test_pin_mismatch_is_reported():
    comps = _composites()
    if not comps:
        pytest.skip("no composites in the registry yet")
    c = comps[0]
    doc = compose.load_composition(c)
    doc["instances"][0]["pin"] = "0" * 12
    import yaml

    bad = c.dir / "composition.yaml"
    original = bad.read_text()
    try:
        bad.write_text(yaml.safe_dump(doc))
        errs = compose.validate(c)
        assert any("pin" in e for e in errs)
    finally:
        bad.write_text(original)


def test_composed_block_groups_port_through_rename():
    comps = _composites()
    if not comps:
        pytest.skip("no composites in the registry yet")
    for c in comps:
        groups = compose.composed_block_groups(c)
        if not groups:
            continue
        doc = compose.load_composition(c)
        insts = {row["name"] for row in doc["instances"]}
        for g in groups:
            assert len(g["members"]) >= 2
            assert any(g["name"].endswith("_" + i) for i in insts), g["name"]
            for m in g["members"]:
                assert any(m.endswith("_" + i.upper()) for i in insts), m
