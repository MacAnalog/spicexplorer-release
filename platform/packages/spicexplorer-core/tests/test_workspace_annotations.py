"""Curated vs. derived annotations — regeneration is a merge proposal (workspace.annotations)."""
from __future__ import annotations

from pathlib import Path

from spicexplorer_core.workspace import (
    merge_curated,
    merge_proposal,
    read_curated,
    write_curated,
)


def test_human_override_survives_regeneration(tmp_path: Path):
    curated = {"M1": {"role": "input_pair", "reviewed_by": "human"}}
    raw = {"M1": "input_diff"}  # the machine disagrees
    merged = merge_curated(curated, raw)
    assert merged["M1"]["role"] == "input_pair"     # human call preserved
    assert merged["M1"]["overrides"] == "input_diff"  # what raw proposed is recorded

    prop = merge_proposal(curated, raw)
    assert prop["conflict"][0]["protected"] is True


def test_agent_labels_update_and_new_ones_are_added(tmp_path: Path):
    curated = {"M1": {"role": "old", "reviewed_by": "agent"}}
    raw = {"M1": "new", "M2": {"role": "mirror", "derived_from": {"model": "opus"}}}
    merged = merge_curated(curated, raw)
    assert merged["M1"]["role"] == "new"                       # agent-owned → updated
    assert merged["M2"]["role"] == "mirror"                    # added
    assert merged["M2"]["reviewed_by"] == "agent"
    assert merged["M2"]["derived_from"] == {"model": "opus"}

    prop = merge_proposal(curated, raw)
    assert {a["id"] for a in prop["add"]} == {"M2"}
    assert {c["id"] for c in prop["conflict"]} == {"M1"}


def test_agree_and_stale_classification(tmp_path: Path):
    curated = {"M1": {"role": "mirror", "reviewed_by": "agent"},
               "M9": {"role": "was_here", "reviewed_by": "human"}}
    raw = {"M1": "mirror"}  # M9 no longer produced
    prop = merge_proposal(curated, raw)
    assert [a["id"] for a in prop["agree"]] == ["M1"]
    assert [s["id"] for s in prop["stale"]] == ["M9"]
    # stale curated entries are KEPT by a merge (curated data is precious)
    assert "M9" in merge_curated(curated, raw)


def test_hand_authored_entry_without_reviewer_is_protected(tmp_path: Path):
    # A human hand-edits annotations.yaml adding an entry with NO reviewed_by (the shape
    # read_curated invites). Regeneration must NOT clobber it (default-protected).
    curated = {"M7": {"role": "cascode"}}          # no reviewed_by field
    raw = {"M7": "diode"}                           # the machine disagrees
    merged = merge_curated(curated, raw)
    assert merged["M7"]["role"] == "cascode"        # preserved, not overwritten
    assert merged["M7"]["overrides"] == "diode"     # raw proposal recorded
    assert merge_proposal(curated, raw)["conflict"][0]["protected"] is True


def test_round_trip_read_write(tmp_path: Path):
    ann = {"M1": {"role": "input_pair", "reviewed_by": "human", "overrides": "input_diff"}}
    write_curated(tmp_path, "ota", ann)
    assert (tmp_path / "design" / "cells" / "ota" / "annotations.yaml").is_file()
    assert read_curated(tmp_path, "ota")["M1"]["role"] == "input_pair"
    assert read_curated(tmp_path, "missing_cell") == {}
