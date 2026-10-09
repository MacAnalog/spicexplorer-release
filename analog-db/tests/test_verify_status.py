"""The committed verify record and the catalog's ``derived_status`` (MacAnalog/spicexplorer-analog-db#74).

Acceptance of #74, one block each below:

* ``derived_status`` appears only when a record is present (and still holds);
* ``validated`` appears only when every ``conform:*`` row of the recorded run passed;
* a T1 drift voids a recorded rung: any change to the circuit's files, or, for a composite, to
  the files of a block its composition.yaml instantiates;
* the catalog reads the committed record and never runs a tier; ``status`` stays AUTHORED.
"""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from spicexplorer_analog_db import catalog, cli, export, model, paths, verify, verify_status

CID = "amp_001_5t"
REF = "ferrosim_inbuf"


def _row(cid: str, tier: int, check: str, status: str, reason: str = "") -> dict:
    return {"circuit": cid, "tier": tier, "check": check, "status": status, "reason": reason}


def _t012(cid: str = CID) -> list[dict]:
    return [_row(cid, t, f"synthetic:t{t}", "pass") for t in (0, 1, 2)]


def _t34(cid: str = CID, *conform: str) -> list[dict]:
    rows = [_row(cid, 3, "sim:ac_open_loop@ihp-sg13g2/tt", "pass")]
    rows += [_row(cid, 4, f"conform:m{i}@ihp-sg13g2", st) for i, st in enumerate(conform)]
    return rows


def _reduce(rows: list[dict]) -> dict[str, dict]:
    return verify_status.reduce_report(rows, date="2026-09-25", platform="abc123def456")


@pytest.fixture()
def record_file(tmp_path, monkeypatch) -> Path:
    """Point the committed-record path at a tmp file (absent until a test writes it)."""
    path = tmp_path / "verify_status.json"
    monkeypatch.setattr(paths, "verify_status_path", lambda: path)
    return path


@pytest.fixture()
def circuit_copy(tmp_path) -> Path:
    dst = tmp_path / CID
    shutil.copytree(model.load_circuit(CID).dir, dst)
    return dst


# --------------------------------------------------------------------------- fingerprint


def test_fingerprint_is_stable_and_16_hex(circuit_copy):
    fp = verify_status.fingerprint(circuit_copy)
    assert fp == verify_status.fingerprint(circuit_copy)
    assert len(fp) == 16 and int(fp, 16) >= 0
    assert fp == verify_status.fingerprint(model.load_circuit(CID).dir)


@pytest.mark.parametrize(
    "rel",
    [
        "abstract/topology.cgraph.json",  # a T1-generated file (regenerated or hand-edited)
        "abstract/netlist.spice",  # the authored source (a stale generated file = T1 drift)
        "pdk/ihp-sg13g2/netlist.spice",  # the lowered netlist
        "pdk/ihp-sg13g2/sizing.yaml",
        "circuit.yaml",
    ],
)
def test_an_edit_to_a_tier_input_changes_the_fingerprint(circuit_copy, rel):
    before = verify_status.fingerprint(circuit_copy)
    with (circuit_copy / rel).open("a") as fh:
        fh.write("\n* edited\n")
    assert verify_status.fingerprint(circuit_copy) != before


def test_a_new_or_renamed_file_changes_the_fingerprint(circuit_copy):
    before = verify_status.fingerprint(circuit_copy)
    (circuit_copy / "analyses" / "extra.yaml").write_text("id: extra\n")
    added = verify_status.fingerprint(circuit_copy)
    assert added != before
    (circuit_copy / "analyses" / "extra.yaml").rename(circuit_copy / "analyses" / "extra2.yaml")
    assert verify_status.fingerprint(circuit_copy) not in (before, added)


@pytest.mark.parametrize(
    "rel",
    [
        "scoreboard/ihp-sg13g2/0123456789.json",
        "README.md",
        "abstract/schematic.svg",
        "notes.png",
        "abstract/__pycache__/x.pyc",
        "pdk/ihp-sg13g2/layout-999-probe/cell.gds",
        "run.log",
        ".DS_Store",
    ],
)
def test_files_no_tier_reads_leave_the_fingerprint_alone(circuit_copy, rel):
    before = verify_status.fingerprint(circuit_copy)
    target = circuit_copy / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("not a tier input\n")
    assert verify_status.fingerprint(circuit_copy) == before


def test_a_top_level_file_named_like_a_layout_entry_still_counts(circuit_copy):
    before = verify_status.fingerprint(circuit_copy)
    (circuit_copy / "pdk" / "ihp-sg13g2" / "layout-notes.yaml").write_text("x: 1\n")
    assert verify_status.fingerprint(circuit_copy) != before


# --------------------------------------------------------------------------- composites

COMPOSITE = "amp_030_miller_cmfb_composite"
CORE, SERVO = "amp_029_two_stage_miller_comp", "cmfb_001_ideal_rsense_servo"
CORE_SIZING = Path("pdk") / "ihp-sg13g2" / "sizing.yaml"


def _widen_core_input_pair(circuits: Path) -> None:
    """The edit a designer makes to the block alone: its input-pair width 10u -> 12.5u."""
    path = circuits / CORE / CORE_SIZING
    text = path.read_text()
    old = '{name: x_dut_xm1_w,  description: "NMOS input pair width", default: 10u,'
    assert old in text
    path.write_text(text.replace(old, old.replace("default: 10u,", "default: 12.5u,")))


@pytest.fixture()
def composite_copy(tmp_path) -> Path:
    """amp_030 and the two blocks its composition.yaml instantiates, side by side as under
    circuits/. A copy, never the committed files: another -n worker may fingerprint them."""
    for cid in (COMPOSITE, CORE, SERVO):
        shutil.copytree(model.load_circuit(cid).dir, tmp_path / cid)
    return tmp_path / COMPOSITE


def test_a_composite_copy_fingerprints_like_the_committed_composite(composite_copy):
    assert verify_status.fingerprint(composite_copy) == verify_status.fingerprint(
        model.load_circuit(COMPOSITE).dir
    )


@pytest.mark.parametrize("block", [CORE, SERVO])
def test_an_edit_to_a_composed_block_changes_the_composite_fingerprint(composite_copy, block):
    before = verify_status.fingerprint(composite_copy)
    with (composite_copy.parent / block / "circuit.yaml").open("a") as fh:
        fh.write("# edited\n")
    assert verify_status.fingerprint(composite_copy) != before


def test_a_block_edit_voids_the_composites_recorded_rung(composite_copy):
    record = _record(fingerprint=verify_status.fingerprint(composite_copy))
    assert verify_status.published(record, composite_copy)["derived_status"] == "generated"
    _widen_core_input_pair(composite_copy.parent)
    out = verify_status.published(record, composite_copy)
    assert "derived_status" not in out
    assert "a block its composition.yaml instantiates" in out["derived_from"]["invalidated"]


@pytest.mark.parametrize("rel", ["README.md", "scoreboard/ihp-sg13g2/0123456789.json"])
def test_a_block_file_no_tier_reads_leaves_the_composite_alone(composite_copy, rel):
    before = verify_status.fingerprint(composite_copy)
    target = composite_copy.parent / CORE / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("not a tier input\n")
    assert verify_status.fingerprint(composite_copy) == before


def test_a_block_that_is_gone_is_folded_as_absent(composite_copy):
    before = verify_status.fingerprint(composite_copy)
    shutil.rmtree(composite_copy.parent / SERVO)
    gone = verify_status.fingerprint(composite_copy)
    assert gone != before
    # a directory without circuit.yaml is not a circuit (model.load_circuit refuses it too)
    (composite_copy.parent / SERVO).mkdir()
    (composite_copy.parent / SERVO / "notes.yaml").write_text("x: 1\n")
    assert verify_status.fingerprint(composite_copy) == gone


def test_only_the_blocks_the_composite_names_are_folded(composite_copy):
    before = verify_status.fingerprint(composite_copy)
    shutil.copytree(model.load_circuit(CID).dir, composite_copy.parent / CID)  # a sibling
    with (composite_copy.parent / CID / "circuit.yaml").open("a") as fh:
        fh.write("# edited\n")
    assert verify_status.fingerprint(composite_copy) == before


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("instances: [\n", id="not-yaml"),
        pytest.param("- a list\n", id="not-a-mapping"),
        pytest.param("instances: amp_029_two_stage_miller_comp\n", id="instances-not-a-list"),
        pytest.param("instances:\n  - just-a-name\n  - {name: core}\n", id="rows-name-no-block"),
    ],
)
def test_a_composition_that_names_no_block_folds_none(composite_copy, text):
    """T1 ``gen:compose`` reports the broken composition.yaml; the fingerprint must not raise."""
    (composite_copy / "composition.yaml").write_text(text)
    before = verify_status.fingerprint(composite_copy)
    _widen_core_input_pair(composite_copy.parent)
    assert verify_status.fingerprint(composite_copy) == before


def test_the_folded_block_is_the_blocks_own_files_one_level_deep(tmp_path):
    """A block that is itself a composite is read through its committed flat netlist (compose
    module doc), so the outer composite's fingerprint includes that block's files, not those of the
    blocks under it."""
    for cid, blocks in (("outer", ["middle"]), ("middle", ["inner"]), ("inner", [])):
        (tmp_path / cid).mkdir()
        (tmp_path / cid / "circuit.yaml").write_text(f"id: {cid}\n")
        if blocks:
            rows = "".join(f"  - {{name: i, block: {b}}}\n" for b in blocks)
            (tmp_path / cid / "composition.yaml").write_text("instances:\n" + rows)
    outer = tmp_path / "outer"
    before = verify_status.fingerprint(outer)
    (tmp_path / "inner" / "circuit.yaml").write_text("id: inner\n# edited\n")
    assert verify_status.fingerprint(outer) == before  # middle's T1 fails, outer's does not
    (tmp_path / "middle" / "abstract").mkdir()
    (tmp_path / "middle" / "abstract" / "netlist.spice").write_text("* regenerated\n")
    assert verify_status.fingerprint(outer) != before  # middle regenerated: outer's T1 input


def test_a_self_referencing_composition_terminates(tmp_path):
    (tmp_path / "loop").mkdir()
    (tmp_path / "loop" / "circuit.yaml").write_text("id: loop\n")
    (tmp_path / "loop" / "composition.yaml").write_text("instances:\n  - {name: a, block: loop}\n")
    assert len(verify_status.fingerprint(tmp_path / "loop")) == 16


@pytest.fixture()
def composite_db(tmp_path, monkeypatch) -> Path:
    """A database holding amp_030 and its two blocks, with the full ``_shared/`` tree."""
    shutil.copytree(paths.shared_root(), tmp_path / "_shared")
    for cid in (COMPOSITE, CORE, SERVO):
        shutil.copytree(model.load_circuit(cid).dir, tmp_path / "circuits" / cid)
    monkeypatch.setenv(paths.ENV_VAR, str(tmp_path))
    return tmp_path


def test_a_block_edit_that_turns_the_composites_t1_red_voids_its_rung(composite_db):
    """#74: a T1 drift on a circuit voids its recorded rung, also when a block caused it."""

    def t1_fails() -> list[str]:
        return [r.check for r in verify.run_tier1([COMPOSITE]) if r.status == "fail"]

    composite = model.load_circuit(COMPOSITE)
    record = _record(fingerprint=verify_status.fingerprint(composite.dir))
    assert t1_fails() == []
    assert verify_status.published(record, composite.dir)["derived_status"] == "generated"
    _widen_core_input_pair(composite_db / "circuits")
    assert "gen:compose_sizing:ihp-sg13g2" in t1_fails()
    assert "derived_status" not in verify_status.published(record, composite.dir)


# --------------------------------------------------------------------------- platform pin


def _git(repo: Path, *argv: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *argv], check=True, capture_output=True, text=True
    ).stdout.strip()


def test_git_pin_reads_head_and_flags_uncommitted_changes(tmp_path):
    repo = tmp_path / "platform"
    (repo / "pkg").mkdir(parents=True)
    _git(repo, "init", "-q")
    (repo / "pkg" / "m.py").write_text("x = 1\n")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c")
    head = _git(repo, "rev-parse", "--short=12", "HEAD")
    assert verify_status.git_pin(repo / "pkg") == head
    (repo / "pkg" / "m.py").write_text("x = 2\n")
    assert verify_status.git_pin(repo / "pkg") == f"{head}-modified"


def test_git_pin_outside_a_checkout_or_without_git_is_unknown(tmp_path, monkeypatch):
    assert verify_status.git_pin(tmp_path) == "unknown"

    def no_git(*_a, **_k):
        raise FileNotFoundError("git")

    monkeypatch.setattr(verify_status.subprocess, "run", no_git)
    assert verify_status.git_pin(Path.cwd()) == "unknown"


def test_platform_pin_is_the_checkout_holding_spicexplorer_core(monkeypatch):
    import spicexplorer_core

    core_dir = Path(spicexplorer_core.__file__).resolve().parent
    assert verify_status.platform_pin() == verify_status.git_pin(core_dir)
    monkeypatch.setitem(sys.modules, "spicexplorer_core", None)  # import now raises ImportError
    assert verify_status.platform_pin() == "unknown"


# --------------------------------------------------------------------------- reduce


def test_a_t0_t2_run_records_generated_with_its_provenance():
    rows = [*_t012(), _row(CID, 3, "sim", "skip", "opt-in"), _row(CID, 4, "conform", "skip")]
    (rec,) = _reduce(rows).values()
    assert rec == {
        "status": "generated",
        "tiers": [0, 1, 2],  # the all-skip opt-in tiers did not run
        "date": "2026-09-25",
        "platform": "abc123def456",
        "fingerprint": verify_status.fingerprint(model.load_circuit(CID).dir),
    }


@pytest.mark.parametrize(
    ("conform", "status", "tally"),
    [
        pytest.param(("pass", "pass"), "validated", {"passed": 2, "total": 2}, id="all-pass"),
        pytest.param(
            ("pass", "skip"), "simulated", {"passed": 1, "total": 2}, id="one-out-of-spec"
        ),
        pytest.param(("pass", "fail"), "simulated", {"passed": 1, "total": 2}, id="one-fails"),
    ],
)
def test_a_t0_t4_run_records_the_conform_tally(conform, status, tally):
    (rec,) = _reduce([*_t012(), *_t34(CID, *conform)]).values()
    assert (rec["status"], rec["tiers"], rec["conform"]) == (status, [0, 1, 2, 3, 4], tally)


def test_a_t1_failure_in_the_run_records_draft():
    rows = [
        _row(CID, 0, "a", "pass"),
        _row(CID, 1, "gen:cgraph", "fail", "stale"),
        _row(CID, 2, "c", "pass"),
    ]
    assert _reduce(rows)[CID]["status"] == "draft"


def test_a_reference_circuit_records_reference_on_tier_0():
    rows = [
        _row(REF, 0, "schema:circuit", "pass"),
        _row(REF, 1, "gen:reference", "skip"),
        _row(REF, 2, "asm:reference", "skip"),
    ]
    assert _reduce(rows)[REF]["status"] == "reference"
    assert _reduce(rows)[REF]["tiers"] == [0]


def test_db_level_rows_the_reduction_replaces_do_not_block_it():
    rows = [
        *_t012(),
        _row("", 0, "catalog:determinism", "fail", "stale"),
        _row("", 0, "verify_status:record", "fail", "old record"),
    ]
    assert _reduce(rows)[CID]["status"] == "generated"


@pytest.mark.parametrize(
    ("report", "message"),
    [
        pytest.param({"rows": []}, "JSON list", id="not-a-list"),
        pytest.param(
            [{"circuit": CID, "tier": "0", "check": "a", "status": "pass"}],
            "not a verify result row",
            id="tier-not-int",
        ),
        pytest.param(
            [{"circuit": CID, "tier": 0, "check": "a", "status": "ok"}],
            "not a verify result row",
            id="unknown-status",
        ),
        pytest.param(
            [{**_row(CID, 0, "a", "pass"), "pdk_scope": "requested"}],
            "--pdk",
            id="narrowed-pdk-view",
        ),
        pytest.param(
            [*_t012(), _row("", 1, "raw:drift", "fail", "3 stale")], "raw:drift", id="red-db-row"
        ),
        pytest.param(_t012("zz_not_a_circuit"), "zz_not_a_circuit", id="unknown-circuit"),
    ],
)
def test_a_report_that_cannot_back_a_record_is_refused(report, message):
    with pytest.raises(verify_status.ReportError, match=message):
        _reduce(report)


def test_the_document_is_sorted_and_byte_stable():
    recs = _reduce([*_t012(REF), *_t012(CID)])
    text = verify_status.to_json(verify_status.document(recs))
    assert list(json.loads(text)["circuits"]) == sorted([CID, REF])
    assert text == verify_status.to_json(verify_status.document(dict(reversed(recs.items()))))
    assert not verify_status.problems(json.loads(text))


# --------------------------------------------------------------------------- the published fields


def _record(**over) -> dict:
    rec = {
        "status": "generated",
        "tiers": [0, 1, 2],
        "date": "2026-09-25",
        "platform": "abc123def456",
    }
    if "fingerprint" not in over:
        rec["fingerprint"] = verify_status.fingerprint(model.load_circuit(CID).dir)
    return {**rec, **over}


def test_no_record_publishes_nothing():
    assert verify_status.published(None, model.load_circuit(CID).dir) == {}


def test_a_holding_record_publishes_the_rung_and_its_source():
    assert verify_status.published(_record(), model.load_circuit(CID).dir) == {
        "derived_status": "generated",
        "derived_from": {"date": "2026-09-25", "platform": "abc123def456", "tiers": [0, 1, 2]},
    }


def test_a_t1_drift_after_the_run_voids_the_rung(circuit_copy):
    record = _record(fingerprint=verify_status.fingerprint(circuit_copy))
    assert verify_status.published(record, circuit_copy)["derived_status"] == "generated"
    # the committed generated graph no longer matches what was verified
    with (circuit_copy / "abstract" / "topology.cgraph.json").open("a") as fh:
        fh.write("\n")
    out = verify_status.published(record, circuit_copy)
    assert "derived_status" not in out
    assert "changed after the verify run of 2026-09-25" in out["derived_from"]["invalidated"]


@pytest.mark.parametrize(
    ("over", "published", "reason"),
    [
        pytest.param(
            {"status": "generated", "tiers": [0]},
            None,
            "needs tier(s) [1, 2]",
            id="generated-on-t0-only",
        ),
        pytest.param(
            {"status": "simulated", "tiers": [0, 1, 2]},
            None,
            "needs tier(s) [3]",
            id="simulated-without-t3",
        ),
        pytest.param(
            {"status": "reference", "tiers": []},
            None,
            "needs tier(s) [0]",
            id="reference-without-t0",
        ),
        pytest.param(
            {"status": "validated", "tiers": [0, 1, 2, 3, 4], "conform": {"passed": 2, "total": 2}},
            "validated",
            None,
            id="validated-every-conform-row-passed",
        ),
        pytest.param(
            {"status": "validated", "tiers": [0, 1, 2, 3, 4], "conform": {"passed": 1, "total": 2}},
            None,
            "passed 1 of 2",
            id="validated-one-conform-row-short",
        ),
        pytest.param(
            {"status": "validated", "tiers": [0, 1, 2, 3, 4], "conform": {"passed": 0, "total": 0}},
            None,
            "passed 0 of 0",
            id="validated-no-conform-row",
        ),
        pytest.param(
            {"status": "validated", "tiers": [0, 1, 2, 3, 4]},
            None,
            "passed 0 of 0",
            id="validated-no-tally",
        ),
        pytest.param({"status": "draft", "tiers": [0]}, "draft", None, id="draft-needs-nothing"),
    ],
)
def test_a_rung_is_published_only_when_the_run_backs_it(over, published, reason):
    out = verify_status.published(_record(**over), model.load_circuit(CID).dir)
    assert out.get("derived_status") == published
    assert (
        out["derived_from"].get("invalidated") is None
        if reason is None
        else (reason in out["derived_from"]["invalidated"])
    )


# --------------------------------------------------------------------------- reading the file


def test_load_is_empty_without_a_usable_file(record_file):
    assert verify_status.load() == {}  # absent
    record_file.write_text("{ not json")
    assert verify_status.load() == {}
    record_file.write_text(json.dumps({"schema": verify_status.SCHEMA, "circuits": {CID: {}}}))
    assert verify_status.load() == {}  # schema-invalid record
    gone = {"schema": verify_status.SCHEMA, "circuits": {"zz_gone": _record()}}
    record_file.write_text(json.dumps(gone))
    assert verify_status.load() == {}
    good = {"schema": verify_status.SCHEMA, "circuits": {CID: _record()}}
    record_file.write_text(json.dumps(good))
    assert verify_status.load() == {CID: _record()}


def test_problems_names_what_is_wrong():
    assert verify_status.problems([]) == ["not a JSON object"]
    bad = verify_status.problems(
        {"schema": verify_status.SCHEMA, "circuits": {CID: {"status": "x"}}}
    )
    assert bad and all(CID in e for e in bad)
    gone = verify_status.problems(
        {"schema": verify_status.SCHEMA, "circuits": {"zz_gone": _record()}}
    )
    assert gone == ["records circuits the database no longer has: ['zz_gone']"]


@pytest.mark.parametrize(
    ("content", "status", "reason"),
    [
        pytest.param(None, "skip", "no committed verify_status.json", id="absent"),
        pytest.param("{ not json", "fail", "not JSON", id="not-json"),
        pytest.param(json.dumps({"schema": "x", "circuits": {}}), "fail", "schema", id="schema"),
        pytest.param(
            json.dumps({"schema": verify_status.SCHEMA, "circuits": {"zz_gone": _record()}}),
            "fail",
            "zz_gone",
            id="gone-circuit",
        ),
        pytest.param(
            json.dumps({"schema": verify_status.SCHEMA, "circuits": {CID: _record()}}),
            "pass",
            "",
            id="valid",
        ),
    ],
)
def test_tier0_checks_the_committed_record(record_file, content, status, reason):
    if content is not None:
        record_file.write_text(content)
    row = verify._tier0_verify_status()
    assert (row.check, row.status) == ("verify_status:record", status)
    assert reason in row.reason


# --------------------------------------------------------------------------- the catalog


@pytest.fixture()
def one_circuit_catalog(monkeypatch, record_file):
    c = model.load_circuit(CID)
    monkeypatch.setattr(catalog, "load_all_circuits", lambda: [c])
    monkeypatch.setattr(export, "deck_index", lambda: {})
    return record_file


def _entry() -> dict:
    (entry,) = catalog.build_catalog()["circuits"]
    return entry


def test_catalog_has_no_derived_status_without_a_record(one_circuit_catalog):
    entry = _entry()
    assert "derived_status" not in entry and "derived_from" not in entry
    assert entry["status"] == model.load_circuit(CID).status


def test_catalog_publishes_the_recorded_rung_beside_the_authored_status(one_circuit_catalog):
    doc = {"schema": verify_status.SCHEMA, "circuits": {CID: _record()}}
    one_circuit_catalog.write_text(json.dumps(doc))
    entry = _entry()
    assert entry["derived_status"] == "generated"
    assert entry["derived_from"] == {
        "date": "2026-09-25",
        "platform": "abc123def456",
        "tiers": [0, 1, 2],
    }
    assert entry["status"] == "draft"  # authored, unchanged for API/UI consumers


def test_catalog_drops_a_rung_whose_circuit_changed(one_circuit_catalog):
    doc = {"schema": verify_status.SCHEMA, "circuits": {CID: _record(fingerprint="0" * 16)}}
    one_circuit_catalog.write_text(json.dumps(doc))
    entry = _entry()
    assert "derived_status" not in entry
    assert "changed after the verify run" in entry["derived_from"]["invalidated"]


def test_the_catalog_build_runs_no_tier(one_circuit_catalog, monkeypatch):
    """The determinism guard compares against the committed record, never a fresh verify run."""

    def boom(*_a, **_k):
        raise AssertionError("the catalog build ran a verify tier")

    for name in (
        "run",
        "run_tier0",
        "run_tier1",
        "run_tier2",
        "run_tier3",
        "run_tier4",
        "derive_status",
    ):
        monkeypatch.setattr(verify, name, boom)
    one_circuit_catalog.write_text(
        json.dumps({"schema": verify_status.SCHEMA, "circuits": {CID: _record()}})
    )
    assert _entry()["derived_status"] == "generated"


@pytest.mark.corpus
def test_the_committed_record_is_valid_and_the_catalog_reflects_it():
    doc = verify_status.read_committed()
    assert doc is not None, "no committed verify_status.json (analog-db verify-status --write)"
    assert verify_status.problems(doc) == []
    entries = {e["id"]: e for e in json.loads(paths.catalog_path().read_text())["circuits"]}
    for cid, record in doc["circuits"].items():
        expected = verify_status.published(record, model.load_circuit(cid).dir)
        got = {k: entries[cid][k] for k in ("derived_status", "derived_from") if k in entries[cid]}
        assert got == expected, cid


# --------------------------------------------------------------------------- CLI


def _report(tmp_path: Path, rows: list[dict]) -> Path:
    path = tmp_path / "matrix.json"
    path.write_text(json.dumps(rows))
    return path


def test_cli_prints_the_record_to_stdout(tmp_path, capsys):
    rc = cli.main(
        [
            "verify-status",
            "--from",
            str(_report(tmp_path, _t012())),
            "--date",
            "2026-09-25",
            "--platform",
            "abc123def456",
        ]
    )
    doc = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert doc == verify_status.document({CID: _record()})


def test_cli_reads_stdin_and_records_today_and_the_detected_pin(monkeypatch, capsys):
    from datetime import datetime, timezone

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(_t012())))
    monkeypatch.setattr(verify_status, "platform_pin", lambda: "feedfacecafe")
    assert cli.main(["verify-status", "--from", "-"]) == 0
    (rec,) = json.loads(capsys.readouterr().out)["circuits"].values()
    assert rec["platform"] == "feedfacecafe"
    assert rec["date"] == datetime.now(timezone.utc).date().isoformat()


def test_cli_write_and_merge(tmp_path, record_file, capsys):
    other = {
        "schema": verify_status.SCHEMA,
        "circuits": {REF: {**_record(), "status": "reference", "tiers": [0]}},
    }
    record_file.write_text(json.dumps(other))
    report = str(_report(tmp_path, _t012()))
    assert cli.main(["verify-status", "--from", report, "--merge", "--write"]) == 0
    assert "now run `analog-db catalog --write`" in capsys.readouterr().out
    assert sorted(json.loads(record_file.read_text())["circuits"]) == [CID, REF]
    assert cli.main(["verify-status", "--from", report, "--write"]) == 0  # no --merge: replaced
    assert sorted(json.loads(record_file.read_text())["circuits"]) == [CID]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        pytest.param(["--date", "25-09-2026"], "is not YYYY-MM-DD", id="bad-date"),
        pytest.param(["--from-missing"], "No such file", id="missing-report"),
        pytest.param(["--pdk-view"], "--pdk", id="narrowed-report"),
        pytest.param(["--merge-broken"], "cannot merge", id="broken-committed-record"),
    ],
)
def test_cli_refusals_exit_2_and_write_nothing(tmp_path, record_file, capsys, argv, message):
    report = _report(tmp_path, _t012())
    if argv == ["--from-missing"]:
        argv, report = [], tmp_path / "missing.json"
    elif argv == ["--pdk-view"]:
        argv, report = [], _report(tmp_path, [{**r, "pdk_scope": "any"} for r in _t012()])
    elif argv == ["--merge-broken"]:
        record_file.write_text("{ not json")
        argv = ["--merge"]
    rc = cli.main(["verify-status", "--from", str(report), "--write", *argv])
    assert rc == 2
    assert message in capsys.readouterr().err
    assert not record_file.exists() or record_file.read_text() == "{ not json"
