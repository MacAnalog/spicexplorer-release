"""What ``catalog.json`` and the README publish must be true of the corpus (audit 2026-09-24).

* **DATA-D6** the catalog module promised "derived status" but publishes the AUTHORED
  ``circuit.yaml`` ``status`` — and ``amp_017_tan_clia`` still carried the importer's
  ``incomplete`` long after every bound PDK recorded a working baseline.
* **DATA-D7** ``untied_symmetries`` demanded ``{w, l, m}`` of every matched pair from ONE group.
  A pair whose devices declare only ``{l, w}``, a pair tied on ``ng`` (the finger analogue of
  ``m``) and a pair tied ``[w]`` by one group and ``[l]`` by another were all published as
  "detected-but-untied" — 9 false warnings in the catalog (and the release notes quoting it).
* **DATA-D11** the README headline said 65 verifiable circuits / fifteen classes / 22 reference
  circuits / 2 composites while the catalog held 72 / 16 / 13 and the tree 5. Every count the
  README states is now checked against ``catalog.json`` (composites: ``composition.yaml`` on disk).
  The new ``CLAUDE.md`` must keep pointing at TESTING.md's borrow-venv recipe through links that
  resolve.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import re
from collections import Counter

import pytest

from spicexplorer_analog_db import catalog, export, model, params, paths, scoreboard

# --------------------------------------------------------------------------- DATA-D6


@pytest.mark.corpus
def test_catalog_status_is_the_authored_circuit_status():
    """What the module doc now says: ``status`` is circuit.yaml's, never a derived rung (that is
    ``verify.derive_status``, which needs a verify run a deterministic build cannot redo)."""
    assert "AUTHORED" in (catalog.__doc__ or "")
    entries = {e["id"]: e for e in json.loads(paths.catalog_path().read_text())["circuits"]}
    for cid in model.list_circuit_ids():
        assert entries[cid]["status"] == model.load_circuit(cid).status, cid


@pytest.mark.parametrize("authored", ["incomplete", "draft"])
def test_build_catalog_publishes_the_authored_status_verbatim(monkeypatch, authored):
    """The builder itself, not the committed file: ``status`` is copied from circuit.yaml as
    authored. amp_001_5t derives ``generated`` from T0-T2, so a derived or a constant status
    would show here (the committed-file test above cannot see a builder change)."""
    c = model.load_circuit("amp_001_5t")
    fake = dataclasses.replace(c, manifest={**c.manifest, "status": authored})
    monkeypatch.setattr(catalog, "load_all_circuits", lambda: [fake])
    monkeypatch.setattr(export, "deck_index", lambda: {})
    built = catalog.build_catalog()["circuits"]
    assert [(e["id"], e["status"]) for e in built] == [("amp_001_5t", authored)]


def test_amp_017_is_not_published_incomplete():
    """The import-time ``incomplete`` (an ngspice model-resolution error) is stale: every bound PDK
    has a named baseline whose analyses all ran. If a baseline breaks again, this test fails."""
    c = model.load_circuit("amp_017_tan_clia")
    assert c.status == "draft", "circuit.yaml is the authored source of the published status"
    base = scoreboard.baselines(c)
    assert sorted(base) == sorted(c.pdks)
    for pdk, did in base.items():
        entry = json.loads(scoreboard.entry_path(c, pdk, did).read_text())
        runs = [
            a["status"] for corner in entry["corners"].values() for a in corner["analyses"].values()
        ]
        assert runs and set(runs) <= {"ok", "disabled"}, (pdk, did, runs)
    entry = next(
        e for e in json.loads(paths.catalog_path().read_text())["circuits"] if e["id"] == c.id
    )
    assert entry["status"] == "draft"


# --------------------------------------------------------------------------- DATA-D7


def _params_doc(cid: str) -> dict:
    doc = params.load_params_doc(model.load_circuit(cid).dir)
    assert doc is not None, f"{cid} has no abstract/params.yaml"
    return doc


def _untied(cid: str, doc: dict | None = None) -> list[str]:
    c = model.load_circuit(cid)
    graph = params.load_graph(c.dir / "abstract" / "topology.cgraph.json")
    return params.untied_symmetries(graph, doc if doc is not None else _params_doc(cid))


def test_a_pair_that_declares_no_m_is_tied_by_w_and_l():
    """amp_019's XM1/XM2 carry only ``{l, w}`` and ``pair_xm1_xm2`` ties ``[w, l]``."""
    assert _untied("amp_019_ti_ldo_error") == []


def test_the_demand_is_the_fields_the_members_declare():
    """Remove the pair's group: the warning asks for the two fields that exist, not ``m``."""
    doc = copy.deepcopy(_params_doc("amp_019_ti_ldo_error"))
    doc["groups"] = [g for g in doc["groups"] if g["name"] != "pair_xm1_xm2"]
    assert _untied("amp_019_ti_ldo_error", doc) == ["matched_pair XM1+XM2 (tie l,w)"]


def test_a_tie_on_ng_satisfies_the_multiplier():
    """amp_004's input pair ties ``[w, l, ng]``; its tail mirror (untied ``l``) stays reported."""
    assert _untied("amp_004_folded_cascode") == ["mirror XM11→XM0,XM12 (tie l)"]


def test_ties_from_two_groups_count_together_and_only_the_rest_is_reported():
    """amp_023 ties XMEA1/XMEA2 ``[w]`` in one group and ``[l]`` in another: only ``m`` is left."""
    assert _untied("amp_023_fer_fd2s") == [
        "matched_pair XMEA1+XMEA2 (tie m)",
        "matched_pair XMI1+XMI2 (tie m)",
    ]


def test_a_real_untied_mirror_is_still_a_warning():
    assert _untied("amp_001_5t") == ["mirror XM6→XM5 (tie l)"]


# The demand/tie arithmetic alone, one row per rule: the detector is stubbed to a fixed candidate
# list, so a row cannot pass by an accident of the corpus.
_PAIR = ("matched_pair A+B", frozenset({"A", "B"}), frozenset({"w", "l", "m"}))
_MIRROR = ("mirror R→O1,O2", frozenset({"R", "O1", "O2"}), frozenset({"l"}))
_FULL = "matched_pair A+B (tie l,m,w)"


def _dev(*fields: str) -> dict[str, str]:
    return {f: f"sym_{f}" for f in fields}


def _group(members: list[str], tie: list[str]) -> dict:
    return {"name": "g", "kind": "matched_pair", "members": members, "tie": tie}


def _both(*fields: str) -> dict[str, dict[str, str]]:
    return {"A": _dev(*fields), "B": _dev(*fields)}


def _stub_candidates(monkeypatch, *cands) -> None:
    monkeypatch.setattr(params, "detected_tie_candidates", lambda _graph: list(cands))


@pytest.mark.parametrize(
    ("doc", "expected"),
    [
        # no inventory to intersect with: the old full demand, and no KeyError on a missing key
        pytest.param({}, [_FULL], id="no-devices-no-groups"),
        pytest.param({"devices": None, "groups": None}, [_FULL], id="null-devices-and-groups"),
        # a member missing from devices: (stale inventory) does not narrow the demand
        pytest.param({"devices": {"X": _dev("w")}}, [_FULL], id="both-members-absent"),
        pytest.param(
            {"devices": {"A": None, "B": "stale"}}, [_FULL], id="non-mapping-entry-is-absent"
        ),
        pytest.param(
            {"devices": {"B": _dev("w", "l")}},
            ["matched_pair A+B (tie l,w)"],
            id="one-absent-the-other-narrows",
        ),
        # the demand is what EVERY member declares (intersection, not union)
        pytest.param(
            {
                "devices": {"A": _dev("w", "l", "m"), "B": _dev("w", "l")},
                "groups": [_group(["A", "B"], ["w", "l"])],
            },
            [],
            id="m-declared-by-one-member",
        ),
        pytest.param({"devices": _both()}, [], id="members-declare-none-of-the-fields"),
        pytest.param(
            {"devices": _both("w", "l", "m"), "groups": [_group(["A", "B"], ["w", "l"])]},
            ["matched_pair A+B (tie m)"],
            id="declared-m-left-untied",
        ),
        # ng is m's analogue — but only where the members declare ng
        pytest.param(
            {
                "devices": _both("w", "l", "m", "ng"),
                "groups": [_group(["A", "B"], ["w", "l", "m"])],
            },
            [],
            id="m-tied-directly",
        ),
        pytest.param(
            {
                "devices": _both("w", "l", "m", "ng"),
                "groups": [_group(["A", "B"], ["w", "l", "ng"])],
            },
            [],
            id="ng-tie-satisfies-m",
        ),
        pytest.param(
            {"devices": _both("w", "l", "ng"), "groups": [_group(["A", "B"], ["w", "l", "ng"])]},
            [],
            id="ng-only-pair-tied-on-ng",
        ),
        pytest.param(
            {"devices": _both("w", "l", "ng"), "groups": [_group(["A", "B"], ["w", "l"])]},
            ["matched_pair A+B (tie m)"],
            id="ng-only-pair-still-owes-its-finger-tie",
        ),
        pytest.param(
            {"devices": _both("w", "l", "m"), "groups": [_group(["A", "B"], ["w", "l", "ng"])]},
            ["matched_pair A+B (tie m)"],
            id="undeclared-ng-tie-does-not-satisfy-m",
        ),
        # which groups count: those holding ALL the members, their ties unioned
        pytest.param(
            {
                "devices": _both("w", "l", "m"),
                "groups": [_group(["A"], ["w", "l", "m"]), _group(["B"], ["w", "l", "m"])],
            },
            [_FULL],
            id="a-group-holding-one-member-ties-nothing",
        ),
        pytest.param(
            {"devices": _both("w", "l", "m"), "groups": [_group(["C", "B", "A"], ["w", "l", "m"])]},
            [],
            id="a-superset-group-ties",
        ),
        pytest.param(
            {
                "devices": _both("w", "l", "m"),
                "groups": [
                    _group(["A", "B"], ["w"]),
                    _group(["B", "A"], ["l"]),
                    _group(["A", "B"], ["m"]),
                ],
            },
            [],
            id="three-groups-one-field-each",
        ),
        pytest.param(
            {
                "devices": _both("w", "l", "m"),
                "groups": [_group(["A", "B"], ["w"]), _group(["B", "A"], ["l"])],
            },
            ["matched_pair A+B (tie m)"],
            id="two-groups-leave-m",
        ),
        pytest.param(
            {
                "devices": _both("w", "l", "m"),
                "groups": [
                    {"name": "g"},
                    {"name": "h", "members": None, "tie": None},
                    {"name": "k", "members": ["A", "B"], "tie": None},
                ],
            },
            [_FULL],
            id="groups-without-members-or-tie",
        ),
    ],
)
def test_untied_symmetries_demand_and_tie_rules(monkeypatch, doc, expected):
    _stub_candidates(monkeypatch, _PAIR)
    assert params.untied_symmetries({}, doc) == expected


_MIRROR_MEMBERS = ("R", "O1", "O2")


@pytest.mark.parametrize(
    ("declares", "groups", "expected"),
    [
        pytest.param(
            ("w", "l"), [_group(list(_MIRROR_MEMBERS), ["l"])], [], id="whole-mirror-tied"
        ),
        pytest.param(
            ("w", "l"),
            [_group(["R", "O1"], ["w", "l"])],
            ["mirror R→O1,O2 (tie l)"],
            id="a-group-missing-one-output",
        ),
        pytest.param(("w",), [], [], id="no-l-declared-no-demand"),
    ],
)
def test_a_mirror_demands_its_length_from_one_group_holding_ref_and_every_output(
    monkeypatch, declares, groups, expected
):
    _stub_candidates(monkeypatch, _MIRROR)
    doc = {"devices": {m: _dev(*declares) for m in _MIRROR_MEMBERS}, "groups": groups}
    assert params.untied_symmetries({}, doc) == expected


def test_untied_symmetries_keeps_detection_order_and_leaves_the_doc_alone(monkeypatch):
    _stub_candidates(monkeypatch, _MIRROR, _PAIR)
    doc = {
        "devices": {m: _dev("w", "l", "m") for m in ("A", "B", *_MIRROR_MEMBERS)},
        "groups": [_group(["A", "B"], ["w"])],
    }
    before = copy.deepcopy(doc)
    first = params.untied_symmetries({}, doc)
    assert first == ["mirror R→O1,O2 (tie l)", "matched_pair A+B (tie l,m)"]
    assert params.untied_symmetries({}, doc) == first  # a second call returns the same list
    assert doc == before


_ANALOGUES = {"m": {"m", "ng"}}


@pytest.mark.corpus
def test_no_symmetry_warning_in_the_corpus_names_an_undeclared_or_tied_field():
    """The audit's complaint, corpus-wide: every field a warning names is declared (or its
    analogue is) by every inventoried member and tied by no group holding all the members — and
    the warnings ``catalog.json`` publishes are exactly these."""
    published = {
        e["id"]: (e.get("params") or {}).get("untied_symmetries", [])
        for e in json.loads(paths.catalog_path().read_text())["circuits"]
    }
    checked = 0
    for c in model.load_all_circuits():
        doc = params.load_params_doc(c.dir)
        cg = c.dir / "abstract" / "topology.cgraph.json"
        if not doc or not cg.is_file():
            continue
        graph = params.load_graph(cg)
        warnings = params.untied_symmetries(graph, doc)
        assert warnings == published[c.id], c.id
        devices = doc.get("devices") or {}
        members_of = {label: mem for label, mem, _f in params.detected_tie_candidates(graph)}
        for w in warnings:
            found = re.fullmatch(r"(.+) \(tie ([a-z,]+)\)", w)
            assert found, w
            members = members_of[found[1]]
            tied: set[str] = set()
            for g in doc.get("groups") or []:
                if members <= set(g.get("members") or []):
                    tied |= set(g.get("tie") or [])
            for f in found[2].split(","):
                alts = _ANALOGUES.get(f, {f})
                inventoried = [m for m in members if isinstance(devices.get(m), dict)]
                assert all(alts & set(devices[m]) for m in inventoried), (c.id, w, f)
                assert not alts & tied, (c.id, w, f)
            checked += 1
    assert checked, "no warning left in the corpus to check"


# --------------------------------------------------------------------------- DATA-D11

# the headline's "<N> <label>" phrases → catalog class; every other verifiable class has ONE cell
# and is named in the "plus one cell each of …" list
_README_CLASS_LABELS = {
    "OTAs/amplifiers": "amplifier",
    "instrumentation amplifiers": "ia",
    "LDOs": "ldo",
    "CMFB networks": "cmfb",
    "switches": "switch",
    "temperature sensors": "temp_sensor",
    "comparators": "comparator",
    "support blocks": "support",
}
# a "one cell each of" name is its class key spelled for prose (lower-case, ``_`` → ``-``) except:
_README_SINGLE_ALIASES = {"driver": "drv"}


def _one(pattern: str, text: str) -> re.Match:
    found = re.search(pattern, text)
    assert found, f"README no longer states {pattern!r}"
    return found


def test_readme_counts_are_the_catalogs():
    readme = (paths.db_root() / "README.md").read_text()
    entries = json.loads(paths.catalog_path().read_text())["circuits"]
    by_class = Counter(e["class"] for e in entries if e["kind"] == "verifiable")
    ref = [e["id"] for e in entries if e["kind"] == "reference"]
    n_ver = sum(by_class.values())
    composites = sorted((paths.db_root() / "circuits").glob("*/composition.yaml"))

    head = _one(
        r"\*\*(\d+) verifiable circuits\*\* across\s+\*\*(\d+) classes\*\* \(([^)]*)\)", readme
    )
    assert (int(head[1]), int(head[2])) == (n_ver, len(by_class))
    listed = {}
    for label, klass in _README_CLASS_LABELS.items():
        phrase = r"\s+".join(re.escape(w) for w in label.split())  # a phrase may wrap a line
        listed[klass] = int(_one(rf"(\d+)\s+{phrase}\b", head[3])[1])
    assert listed == {k: by_class[k] for k in listed}
    singles = _one(r"plus\s+one\s+cell\s+each\s+of\s+([^.;)]*)", head[3])[1]
    names = [n.strip() for n in re.split(r",\s*|\s+and\s+", singles.strip())]
    keys = [_README_SINGLE_ALIASES.get(n, n.lower().replace("-", "_")) for n in names]
    assert sorted(keys) == sorted(k for k in by_class if k not in listed), names
    assert all(by_class[k] == 1 for k in keys)

    reference = _one(
        r"\*\*(\d+) `kind: reference` circuits\*\* \(plan D-9; (\d+) `ferrosim_\*` \+ (\d+) `sfe_\*`\)",
        readme,
    )
    assert [int(g) for g in reference.groups()] == [
        len(ref),
        sum(r.startswith("ferrosim_") for r in ref),
        sum(r.startswith("sfe_") for r in ref),
    ]
    assert int(_one(r"# one self-contained circuit\s+\(×(\d+)\)", readme)[1]) == n_ver
    assert int(_one(r"COMPOSITES only \(×(\d+)\)", readme)[1]) == len(composites)
    assert int(_one(r"a kind: reference circuit \(D-9\)\s+\(×(\d+):", readme)[1]) == len(ref)


def _anchor(heading: str) -> str:
    """GitHub's heading anchor: lower-case, punctuation dropped, each space a hyphen."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
