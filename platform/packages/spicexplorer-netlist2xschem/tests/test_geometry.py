"""Transform math — the highest-risk correctness area.

xschem applies **flip before rotate**; one ``rot`` step maps ``(x, y) → (-y, x)`` in the file's
y-down frame (on-screen clockwise). The sense is pinned by corpus ground truth (sense corrected
2026-07-16 — see the regression test at the bottom), so we pin the full
``(rot, flip) ∈ {0..3} × {0,1}`` table against hand-computed expectations for a known pin, and add
the algebraic invariants (translation, flip is its own inverse, four rotations = identity).
"""

import pytest
from spicexplorer_netlist2xschem.geometry import Transform, apply_transform, snap

# A point clearly off both axes so every rotation/flip is distinguishable.
PX, PY = 20, -30

# Expected absolute coords at origin (0,0) for each (rot, flip). flip negates x first, then
# rotate with (x, y) -> (-y, x) per step.
EXPECTED = {
    (0, 0): (20, -30),
    (1, 0): (30, 20),
    (2, 0): (-20, 30),
    (3, 0): (-30, -20),
    (0, 1): (-20, -30),
    (1, 1): (30, -20),
    (2, 1): (20, 30),
    (3, 1): (-30, 20),
}


@pytest.mark.parametrize(("rot", "flip"), sorted(EXPECTED))
def test_transform_table(rot: int, flip: int):
    assert apply_transform(Transform(0, 0, rot, flip), PX, PY) == EXPECTED[(rot, flip)]


def test_translation_adds_after_transform():
    # rot=flip=0 is identity-then-translate.
    assert apply_transform(Transform(100, 200, 0, 0), PX, PY) == (100 + PX, 200 + PY)
    # with rotation, the translation is applied last.
    rx, ry = EXPECTED[(1, 0)]
    assert apply_transform(Transform(100, 200, 1, 0), PX, PY) == (100 + rx, 200 + ry)


def test_flip_is_its_own_inverse():
    once = apply_transform(Transform(0, 0, 0, 1), PX, PY)
    # applying flip to the flipped x returns the original
    assert apply_transform(Transform(0, 0, 0, 1), once[0], once[1]) == (PX, PY)


def test_four_rotations_return_to_origin_point():
    x, y = PX, PY
    for _ in range(4):
        x, y = apply_transform(Transform(0, 0, 1, 0), x, y)
    assert (x, y) == (PX, PY)


def test_rot_wraps_mod_4():
    assert apply_transform(Transform(0, 0, 5, 0), PX, PY) == apply_transform(
        Transform(0, 0, 1, 0), PX, PY
    )


def test_snap_to_grid():
    assert snap(12, 5) == 10
    assert snap(13, 5) == 15
    assert snap(-12, 5) == -10
    assert snap(240, 10) == 240


def test_rotation_sense_matches_corpus_transmission_gate():
    """Corpus ground truth for the rotation *sense* (fixed 2026-07-16).

    analog-db ``transmission_gate_pair.sch`` places its NMOS at ``(590, -260) rot=3 flip=0``.
    The IHP symbol's pins are G(-20,0) D(20,-30) S(20,30) B(20,0); the drawing's labeled wires
    put the gate on ``vctl`` at (590,-240), bulk on ``VSS`` at (590,-280), and D/S on
    ``port_A``/``port_B`` at (560,-280)/(620,-280). The previous ``(y, -x)`` sense swapped
    G and B (a gate wired to VSS — electrically impossible for a transmission gate).
    """
    t = Transform(590, -260, rot=3, flip=0)
    assert apply_transform(t, -20, 0) == (590, -240)  # G -> vctl
    assert apply_transform(t, 20, 0) == (590, -280)  # B -> VSS
    assert apply_transform(t, 20, -30) == (560, -280)  # D -> port_A
    assert apply_transform(t, 20, 30) == (620, -280)  # S -> port_B
