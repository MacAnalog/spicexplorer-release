"""Sub-circuit detection E2E: re-run functional block detection (circuitgraph
``annotate_subcircuits`` over the abstract netlist) for every circuit with a committed
structural analysis and require deep equality with ``raw/<id>/<id>.structural.json``.

Same ground truth as the T1 raw-drift byte guard, but independent of the export/writer
path and with a readable JSON diff on failure. Pure python — no SPICE, no xschem.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("spicexplorer_circuitgraph")
pytest.importorskip("spicexplorer_netlist2xschem")

from spicexplorer_analog_db import export, model  # noqa: E402

pytestmark = pytest.mark.corpus  # one detection re-run per committed structural analysis

_REPO = Path(__file__).resolve().parents[1]
_STRUCTURALS = sorted((_REPO / "raw").glob("*/*.structural.json"))


def test_structural_corpus_is_present() -> None:
    # guard the parametrized sweep below against silently running over nothing
    assert len(_STRUCTURALS) >= 20, "expected a structural.json for every verifiable circuit"


@pytest.mark.parametrize("spath", _STRUCTURALS, ids=[p.parent.name for p in _STRUCTURALS])
def test_detection_matches_committed_structural(spath: Path) -> None:
    circuit = model.load_circuit(spath.parent.name)
    graph, groups = export._dut_graph(circuit)
    regenerated = json.loads(export.render_structural(circuit, graph, groups))
    committed = json.loads(spath.read_text())
    assert regenerated == committed
