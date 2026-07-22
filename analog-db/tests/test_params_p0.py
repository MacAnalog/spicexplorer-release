"""Parameterization P0 (meta plan_parameterization.md §5 P0).

Locks the ``spicexplorer/params@1`` contract and proves the group-detection spike on the
``amp_001_5t`` committed graph: pairs + mirrors found structurally, the proposed document is
schema-valid + deterministic, and the optional Tier-0 ``abstract/params.yaml`` hook works.
"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from spicexplorer_analog_db import model, params, schema, verify

CIRCUIT = "amp_001_5t"


@pytest.fixture(scope="module")
def graph() -> dict:
    c = model.load_circuit(CIRCUIT)
    return params.load_graph(c.dir / "abstract" / "topology.cgraph.json")


@pytest.fixture(scope="module")
def proposed(graph) -> dict:
    return params.propose_params_doc(graph)


# --------------------------------------------------------------------------- schema contract


def test_schema_registered_and_loads():
    s = schema.load_schema("params")
    assert s["$id"] == "spicexplorer/params@1"


def test_plan_d2_example_validates():
    # the exact shape from plan_parameterization.md D-2
    doc = {
        "schema": "spicexplorer/params@1",
        "devices": {
            "XM1": {"w": "x_dut_xm1_w", "l": "x_dut_xm1_l", "m": "x_dut_xm1_m"},
            "XM2": {"w": "x_dut_xm2_w", "l": "x_dut_xm2_l", "m": "x_dut_xm2_m"},
            "XM3": {"l": "x_dut_xm3_l"},
            "XM4": {"l": "x_dut_xm4_l"},
            "XM6": {"m": 3},
            "XM7": {"m": "x_dut_xm7_m"},
        },
        "groups": [
            {"name": "input_pair", "kind": "matched_pair", "members": ["XM1", "XM2"], "tie": ["w", "l", "m"]},
            {"name": "nmos_mirror_l", "kind": "mirror_length", "members": ["XM3", "XM4"], "tie": ["l"]},
        ],
        "ratios": [{"param": "m", "ref": "XM7", "of": "XM6", "ratio": "17/3"}],
    }
    assert schema.validation_errors(doc, "params") == []


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.pop("devices"),  # inventory is required
        lambda d: d.pop("schema"),
        lambda d: d.update(schema="spicexplorer/params@2"),
        lambda d: d.update(bogus=1),  # additionalProperties: false
        lambda d: d["groups"].append(
            {"name": "x", "kind": "because_i_said_so", "members": ["XM1", "XM2"], "tie": ["l"]}
        ),  # kind is a closed vocabulary
        lambda d: d["groups"].append(
            {"name": "x", "kind": "matched_pair", "members": ["XM1"], "tie": ["l"]}
        ),  # a group needs >= 2 members
        lambda d: d["ratios"].append({"param": "m", "ref": "XM7", "of": "XM6"}),  # ratio required
    ],
)
def test_schema_rejects_malformed(mutate):
    doc = {
        "schema": "spicexplorer/params@1",
        "devices": {"XM1": {"w": "x_dut_xm1_w"}},
        "groups": [],
        "ratios": [],
    }
    mutate(doc)
    assert schema.validation_errors(doc, "params") != []


# --------------------------------------------------------------------------- atomic inventory


def test_atomic_inventory_is_exhaustive_and_mechanical(graph):
    inv = params.atomic_inventory(graph)
    assert set(inv) == {"XM1", "XM2", "XM3", "XM4", "XM5", "XM6"}
    for cid, fields in inv.items():
        assert set(fields) == {"w", "l", "m"}
        for f, sym in fields.items():
            assert sym == f"x_dut_{cid.lower()}_{f}"  # plan D-1, collision-free by construction
    syms = [s for fields in inv.values() for s in fields.values()]
    assert len(syms) == len(set(syms)) == 18  # a 5T OTA is 18 atomic knobs


# --------------------------------------------------------------------------- structural detection


def test_detects_the_input_pair(graph):
    pairs = params.detect_matched_pairs(graph)
    assert [(p.a, p.b) for p in pairs] == [("XM1", "XM2")]
    assert pairs[0].polarity == "NMOS"


def test_detects_both_mirrors(graph):
    mirrors = {m.ref: m for m in params.detect_mirrors(graph)}
    # PMOS load: XM3 diode-connected, XM4 the output half
    assert mirrors["XM3"].outputs == ("XM4",)
    assert mirrors["XM3"].polarity == "PMOS"
    # NMOS tail: XM6 diode reference, XM5 the tail device
    assert mirrors["XM6"].outputs == ("XM5",)
    assert mirrors["XM6"].polarity == "NMOS"
    assert set(mirrors) == {"XM3", "XM6"}


def test_diode_halves_are_not_matched_pairs(graph):
    # XM3/XM4 share source vdd but XM3 is diode-connected AND vdd is a supply — a mirror, not a pair
    ids = {p.a for p in params.detect_matched_pairs(graph)} | {
        p.b for p in params.detect_matched_pairs(graph)
    }
    assert "XM3" not in ids and "XM4" not in ids and "XM5" not in ids and "XM6" not in ids


# --------------------------------------------------------------------------- proposed document


def test_proposed_doc_is_schema_valid(proposed):
    assert schema.validation_errors(proposed, "params") == []


def test_proposed_doc_covers_todays_symmetries(proposed):
    by_name = {g["name"]: g for g in proposed["groups"]}
    assert by_name["pair_xm1_xm2"]["kind"] == "matched_pair"
    assert by_name["pair_xm1_xm2"]["members"] == ["XM1", "XM2"]
    assert by_name["pair_xm1_xm2"]["tie"] == ["w", "l", "m"]
    assert by_name["mirror_xm3_l"]["members"] == ["XM3", "XM4"]
    assert by_name["mirror_xm6_l"]["members"] == ["XM6", "XM5"]
    # since the D-1 atomic migration, m is SYMBOLIC (x_dut_xm*_m) in the graph, so no numeric
    # m-ratio is detectable — ratios stay a reviewed/authored affair (covered by fixtures)
    assert "ratios" not in proposed


def test_proposed_doc_is_deterministic(graph):
    a = json.dumps(params.propose_params_doc(graph), sort_keys=False)
    b = json.dumps(params.propose_params_doc(graph), sort_keys=False)
    assert a == b


def test_ratio_value_reduces_fractions():
    assert params._ratio_value(17.0, 3.0) == "17/3"
    assert params._ratio_value(24, 3) == 8
    assert params._ratio_value("x_dut_xm7_m", 3) is None


# --------------------------------------------------------------------------- Tier-0 hook


def test_tier0_params_absent_is_no_row(tmp_path):
    # adoption is per circuit: a circuit without abstract/params.yaml contributes no row …
    (tmp_path / "abstract").mkdir()
    fake = SimpleNamespace(id="fake", dir=tmp_path)
    assert verify._tier0_params_yaml(fake) == []
    # … while the migrated amp_001_5t (P2 dry run) has adopted the layer and validates
    c = model.load_circuit(CIRCUIT)
    assert (c.dir / "abstract" / "params.yaml").is_file()
    (row,) = verify._tier0_params_yaml(c)
    assert row.status == "pass" and row.check == "schema:params"


def test_tier0_params_valid_and_invalid(tmp_path, proposed):
    import yaml

    (tmp_path / "abstract").mkdir()
    f = tmp_path / "abstract" / "params.yaml"
    fake = SimpleNamespace(id="fake", dir=tmp_path)

    f.write_text(yaml.safe_dump(proposed, sort_keys=False))
    (good,) = verify._tier0_params_yaml(fake)
    assert good.status == "pass" and good.check == "schema:params"

    f.write_text("schema: spicexplorer/params@1\n")  # missing devices
    (bad,) = verify._tier0_params_yaml(fake)
    assert bad.status == "fail" and "devices" in (bad.reason or "")

    f.write_text(": : not yaml [")
    (ugly,) = verify._tier0_params_yaml(fake)
    assert ugly.status == "fail"
