"""Shared library + agent context surface: decisions → PROJECT.md."""
from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_core.workspace import (
    append_decision,
    import_cell,
    list_library,
    publish_cell,
    read_decisions,
    render_project_md,
    write_manifest,
)


def _cell(pdir: Path, name: str, *, sizing="W: 10u\n"):
    c = pdir / "design" / "cells" / name
    (c / "bindings").mkdir(parents=True, exist_ok=True)
    (c / "netlist.spice").write_text("* net\n")
    (c / "sizing.yaml").write_text(sizing)
    (c / "bindings" / "ihp-sg13g2.yaml").write_text("{}\n")


# ---------- shared library ----------
def test_publish_then_import_is_copy_with_provenance(tmp_path: Path):
    src_proj = tmp_path / "projects" / "src-000000aa"
    src_proj.mkdir(parents=True)
    _cell(src_proj, "ota", sizing="W: 42u\n")

    rec = publish_cell(src_proj, "ota", version="v1", root=tmp_path, source={"from_run": "r1"})
    assert rec["captured"] == ["netlist.spice", "sizing.yaml", "bindings/"]
    assert (tmp_path / "shared" / "lib" / "ota" / "v1" / "lib_meta.json").is_file()

    dst_proj = tmp_path / "projects" / "dst-000000bb"
    dst_proj.mkdir(parents=True)
    marker = import_cell("ota", "v1", dst_proj, root=tmp_path, as_name="input_stage")
    # copy-on-import: concrete files land in the importer, with a provenance marker
    assert (dst_proj / "design" / "cells" / "input_stage" / "sizing.yaml").read_text() == "W: 42u\n"
    assert marker["cell"] == "ota" and marker["version"] == "v1"
    assert (dst_proj / "design" / "cells" / "input_stage" / ".imported_from.json").is_file()


def test_published_versions_are_immutable(tmp_path: Path):
    proj = tmp_path / "projects" / "p-000000cc"
    proj.mkdir(parents=True)
    _cell(proj, "ota")
    publish_cell(proj, "ota", version="v1", root=tmp_path)
    with pytest.raises(FileExistsError):
        publish_cell(proj, "ota", version="v1", root=tmp_path)   # can't overwrite a version
    publish_cell(proj, "ota", version="v2", root=tmp_path)       # a new version is fine
    lib = list_library(tmp_path)
    assert {(e["cell"], e["version"]) for e in lib} == {("ota", "v1"), ("ota", "v2")}


def test_import_refuses_to_clobber_existing_local_cell(tmp_path: Path):
    src = tmp_path / "projects" / "src-000000ee"
    src.mkdir(parents=True)
    _cell(src, "ota", sizing="W: 42u\n")
    publish_cell(src, "ota", version="v1", root=tmp_path)

    dst = tmp_path / "projects" / "dst-000000ff"
    dst.mkdir(parents=True)
    _cell(dst, "ota", sizing="W: 99u (hand-tuned)\n")   # a precious local cell
    with pytest.raises(FileExistsError):
        import_cell("ota", "v1", dst, root=tmp_path)     # must NOT silently clobber
    assert (dst / "design" / "cells" / "ota" / "sizing.yaml").read_text() == "W: 99u (hand-tuned)\n"
    # explicit opt-in replaces it
    import_cell("ota", "v1", dst, root=tmp_path, overwrite=True)
    assert (dst / "design" / "cells" / "ota" / "sizing.yaml").read_text() == "W: 42u\n"


def test_publish_leaves_no_partial_wedge(tmp_path: Path):
    # A successful publish leaves no .staging sibling; the version dir has its lib_meta.json.
    proj = tmp_path / "projects" / "p-00000011"
    proj.mkdir(parents=True)
    _cell(proj, "ota")
    publish_cell(proj, "ota", version="v1", root=tmp_path)
    cell_dir = tmp_path / "shared" / "lib" / "ota"
    assert [p.name for p in cell_dir.iterdir()] == ["v1"]          # no leftover .staging dir
    assert (cell_dir / "v1" / "lib_meta.json").is_file()


# ---------- agent context ----------
def test_decisions_are_append_only(tmp_path: Path):
    pdir = tmp_path / "projects" / "ota-000000dd"
    pdir.mkdir(parents=True)
    append_decision(pdir, {"kind": "topology", "summary": "chose folded cascode", "by": "agent"})
    append_decision(pdir, {"kind": "sizing", "summary": "gm/ID sized input pair", "by": "human"})
    evs = read_decisions(pdir)
    assert [e["summary"] for e in evs] == ["chose folded cascode", "gm/ID sized input pair"]
    assert all("at" in e for e in evs)  # timestamp stamped


def test_project_md_is_generated_from_state_and_decisions(tmp_path: Path):
    pdir = tmp_path / "projects" / "ota-000000ee"
    pdir.mkdir(parents=True)
    write_manifest(pdir, {"id": "ota-000000ee", "name": "Folded-Cascode OTA"})
    _cell(pdir, "ota")
    (pdir / "verify").mkdir()
    (pdir / "verify" / "plan.yaml").write_text(
        "specs:\n  gain_db:\n    measurement: dcgain\n    corners: [tt]\n"
        "    aggregate: min\n    target: \">= 40\"\n")
    rd = pdir / "runs" / "20260715-100000_optimize_abcd1234"
    rd.mkdir(parents=True)
    (rd / "run.json").write_text(
        '{"run_id": "20260715-100000_optimize_abcd1234", "status": "done",'
        ' "best_score": -0.4, "kind": "optimize", "envelope": 1,'
        ' "metrics": {"dcgain": 44.0}, "coordinates": {"corner": "tt"}}')
    append_decision(pdir, {"summary": "accepted the 44 dB sizing", "by": "human"})

    md = render_project_md(pdir)
    assert (pdir / "context" / "PROJECT.md").is_file()
    assert "# Folded-Cascode OTA" in md
    assert "GENERATED" in md
    assert "✅" in md and "gain_db" in md            # compliance rendered (44 >= 40)
    assert "abcd1234" in md                          # best run
    assert "accepted the 44 dB sizing" in md         # recent decision
