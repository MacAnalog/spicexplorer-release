"""No testbench template may demand a binding it does not use.

``assemble()`` renders the template with ``Template.safe_substitute`` and then scans the
**rendered text, comments included**, for leftover ``${...}`` — deliberately, because a
placeholder that slipped through into a comment is still evidence the deck was not fully bound.
The consequence is that a ``${NAME}`` written into a template's *prose header* becomes a
**required** parameter every consuming circuit must bind, forever, with nothing reading it.

That happened to the ldo/dropout template: the 2026-07-21 rewrite dropped the threshold
criterion from the bench but quoted the superseded lines verbatim in the header, ``${VOUT_THRESH}``
and all. Deleting the now-dead binding from a circuit made it un-assemblable
(``unresolved placeholders ['VOUT_THRESH']``), so nine circuits carried a dead parameter and
ldo_010 carried a comment explaining why it could not be removed.
"""

from __future__ import annotations

import re

import pytest

from spicexplorer_analog_db import model, paths
from spicexplorer_analog_db.assemble import _PLACEHOLDER, AssembleError, assemble

_COMMENT = ("*", "**")


def _template_files():
    roots = [paths.classes_root(), paths.shared_templates_root()]
    seen = []
    for root in roots:
        if root.is_dir():
            seen += sorted(root.rglob("*.spice"))
    return seen


def _template_id(path) -> str:
    """``ldo/dropout.spice`` — the basename alone repeats across classes, so a failing
    parametrize id like ``dc_op.spice3`` would not name the offending template."""
    return f"{path.parent.parent.name}/{path.name}"


@pytest.mark.parametrize("path", _template_files(), ids=_template_id)
def test_no_template_placeholder_lives_only_in_a_comment(path) -> None:
    """A ``${NAME}`` that no live line uses is a required parameter with no reader."""
    lines = path.read_text().splitlines()
    live = {
        n for ln in lines if not ln.lstrip().startswith(_COMMENT) for n in _PLACEHOLDER.findall(ln)
    }
    commented = {
        n for ln in lines if ln.lstrip().startswith(_COMMENT) for n in _PLACEHOLDER.findall(ln)
    }
    dead = sorted(commented - live)
    assert not dead, (
        f"{path}: {dead} appear only in comments — every consuming circuit is forced to bind "
        f"them and nothing reads the value. Write the name as prose, not as a placeholder."
    )


def test_ldo_dropout_assembles_without_the_dead_vout_thresh(monkeypatch) -> None:
    """The bench reads VOUT_NOM/VREG_TOL/REG_SLOPE_MAX; VOUT_THRESH must not be needed."""
    c = model.load_circuit("ldo_010_capless_lowiq")
    real = model.Circuit.analysis

    def _without_thresh(self, analysis_id: str):
        doc = real(self, analysis_id)
        (doc.get("params") or {}).pop("VOUT_THRESH", None)
        return doc

    monkeypatch.setattr(model.Circuit, "analysis", _without_thresh)
    try:
        deck = assemble(c, "dropout", "ihp-sg13g2")
    except AssembleError as exc:  # pragma: no cover - the pre-fix path
        pytest.fail(f"dropout still demands a dead binding: {exc}")

    # Not "no leftover placeholder" — assemble() already raises on those, so such an assertion
    # could never fire. Assert instead that the criterion the deck actually evaluates is the
    # regulation window AND the slope test, both bound to numbers: a template rewired back to a
    # single threshold would still assemble, and only this line would catch it.
    inreg = next(ln for ln in deck.splitlines() if ln.strip().startswith("let inreg"))
    assert re.search(r"abs\(vo - [-+0-9.eE]+\)", inreg), inreg
    assert re.search(r"abs\(slope\) <= [-+0-9.eE]+", inreg), inreg
    assert "THRESH" not in inreg, inreg


def test_no_circuit_metadata_still_names_the_retired_vout_thresh() -> None:
    """The retired parameter must be gone from the AUTHORED circuit tree, prose included.

    Deleting the binding from ``analyses/dropout.yaml`` is only half the retirement: three
    ``datasheet.yaml`` metric descriptions went on reading "Vin - Vout at which Vout has fallen to
    VOUT_THRESH under heavy load" and ldo_004's README pointed at a comment the same change deleted,
    so the user-facing text still promised a criterion no bench applies. ``raw/`` is excluded on
    purpose: those decks are rendered from the template, whose header names VOUT_THRESH as prose
    (the history of why the threshold criterion was dropped).
    """
    offenders = sorted(
        str(f.relative_to(paths.db_root()))
        for f in paths.circuits_root().rglob("*")
        if f.is_file()
        and f.suffix in {".yaml", ".yml", ".md"}
        and "VOUT_THRESH" in f.read_text(errors="ignore")
    )
    assert not offenders, (
        f"{offenders}: the dropout bench reads VOUT_NOM/VREG_TOL/REG_SLOPE_MAX — a circuit's "
        f"metadata or README must not promise the retired VOUT_THRESH reading."
    )
