"""Committed notebook artefacts must equal what their notebook writes today.

Some guide notebooks write a file beside themselves that is also COMMITTED (the rendered
example a reader opens without running anything). The notebook test (``tests/test_notebooks.py``)
executes every notebook in a throwaway copy, so nothing ever compared that output with the
committed file: when the placer changed, ``folded_cascode_annotated.sch`` went out of date and no
test failed; the difference appeared only as a "modified" tracked file after somebody ran the
notebook in place.

Each row below executes its notebook in an empty directory under ``tmp_path`` (the artefact is
not pre-seeded, so a notebook that stops writing it fails too) and compares the file it wrote
with the committed one, byte for byte. The notebooks listed address their inputs through
``project_root()``, never by a path relative to their folder, so an empty directory is enough.

A row names the notebook by its stem: the runner (``tests/notebook_lane.py``) takes whichever
format is on disk, a marimo ``<stem>.py`` or a Jupyter ``<stem>.ipynb``.
"""

from __future__ import annotations

import difflib
import shutil
from pathlib import Path

import pytest
from spicexplorer_core import project_root

pytest.importorskip("spicexplorer_circuitgraph", reason="circuitgraph (the detector) not installed")
# the notebook runner lives in the workspace-root tests/, which the public tree does not ship
_lane = pytest.importorskip(
    "notebook_lane", reason="the workspace-root notebook runner is not in this tree"
)
notebook_path, run_notebook = _lane.notebook_path, _lane.run_notebook

NOTEBOOKS = Path(__file__).resolve().parents[1] / "notebooks"

# (notebook stem, the committed file it writes beside itself)
ARTEFACTS = [
    ("annotation_demo", "folded_cascode_annotated.sch"),
]


@pytest.mark.notebooks
@pytest.mark.parametrize(("notebook", "artefact"), ARTEFACTS, ids=[a for _, a in ARTEFACTS])
def test_committed_artefact_matches_a_fresh_run(notebook: str, artefact: str, tmp_path: Path):
    if not (project_root() / "examples/analog-db/circuits").is_dir():
        pytest.skip(
            "examples/analog-db submodule not checked out (the notebook reads its netlists)"
        )
    source = notebook_path(f"packages/spicexplorer-netlist2xschem/notebooks/{notebook}")
    work = tmp_path / "nb"
    work.mkdir()
    shutil.copy2(source, work / source.name)

    run_notebook(work / source.name, work, tmp_path, timeout=300)

    produced = work / artefact
    assert produced.is_file(), (
        f"{source.name} no longer writes {artefact}: stop tracking the committed copy "
        "(or restore the cell that writes it)"
    )
    committed = (NOTEBOOKS / artefact).read_text()
    fresh = produced.read_text()
    if fresh != committed:
        diff = list(
            difflib.unified_diff(
                committed.splitlines(), fresh.splitlines(), "committed", "fresh run", lineterm=""
            )
        )
        pytest.fail(
            f"notebooks/{artefact} is stale against a fresh run of {source.name} "
            f"({len(diff)}-line diff). Refresh it in your own working tree with\n"
            "  uv run python scripts/refresh_notebooks.py "
            f"packages/spicexplorer-netlist2xschem/notebooks/{source.name}\n"
            "and commit the notebook and the artefact together.\n" + "\n".join(diff[:40])
        )
