"""Where the GENERIC MOS symbols draw their parameter text, and that they draw the model at all.

Two defects live in the same three text records of ``devices/nmos4.sym`` / ``devices/pmos4.sym``,
the symbols every commercial-kit ("generic lane") sheet is drawn with:

* **#244** — the ``@w/@l/@m`` line started at local ``x=7.5`` and ran right at ~8 units per
  character, straight across the drain/source pin column at ``x=+-20``. Every wire, lead and label
  stub the wiring layer puts on that column was therefore drawn through the device's own sizing
  string (250 of them on one 67-sheet design; two lost a leading digit outright).
* **#249** — the symbols never drew ``@model``, so a mixed-flavour sheet could not show which
  device is which; on the generic lane the kit's device rides on the instance and the render is the
  artefact a human reviews.

The geometry asserted here is the fix: both parameter rows are anchored PAST the pin column, and
both sit ABOVE ``y=0`` — the half-plane the wiring layer leaves alone on the text side (the bulk
pin's label stub steps out to ``x=+-80`` and then always drops DOWNWARD, see
``wiring._label_candidates``). The two vendored copies must not drift apart, and the default
(no-params) lane must stay untouched: ``clean_symbol`` drops every parameter row, so the committed
``*_np.sym`` twins are reproduced byte for byte.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem.symbol_gen import clean_symbol

#: The platform's vendored library — the copy the container and the native lane actually read.
DOCKER_DEVICES = Path(__file__).resolve().parents[3] / "docker" / "xschem_library" / "devices"
#: The hermetic copy the test suite parses (``tests/fixtures/sym/``).
FIXTURE_DEVICES = Path(__file__).resolve().parent / "fixtures" / "sym" / "devices"

#: ``T {text} x y rot flip hsize vsize {props}``
_T = re.compile(r"^T \{(?P<text>.*)\} (?P<x>-?[\d.]+) (?P<y>-?[\d.]+) (?P<rot>\d+) (?P<flip>\d+) ")
#: An attribute the symbol *displays* (the same set ``symbol_gen._PARAM_DISPLAY`` strips).
_PARAM = re.compile(r"@(model|value|w|l|ng|m)\b")

SYMBOLS = ("nmos4.sym", "pmos4.sym")

#: Half-width of the symbol body: the drain/source/bulk pin column sits at local ``x=+-20`` and the
#: pin boxes reach ``22.5``. Nothing the parameter text draws may start inside that.
PIN_COLUMN_X = 22.5


def _rows(text: str) -> list[tuple[str, float, float]]:
    out = []
    for line in text.splitlines():
        m = _T.match(line.strip())
        if m:
            out.append((m["text"], float(m["x"]), float(m["y"])))
    return out


def _param_rows(text: str) -> list[tuple[str, float, float]]:
    return [r for r in _rows(text) if _PARAM.search(r[0])]


@pytest.mark.parametrize("name", SYMBOLS)
def test_the_two_vendored_copies_are_identical(name: str) -> None:
    """The test fixture copy is the library copy; a fix applied to one only is the bug coming back."""
    assert (FIXTURE_DEVICES / name).read_text() == (DOCKER_DEVICES / name).read_text()


@pytest.mark.parametrize("name", SYMBOLS)
def test_parameter_text_clears_the_drain_source_pin_column(name: str) -> None:
    """#244: no parameter row may start inside the pin column, on either side of a flipped device.

    A device is placed with ``flip=0`` or ``flip=1``; a flip mirrors the anchor to ``-x``, so the
    single sign-independent condition is that the anchor is outside the pin boxes.
    """
    rows = _param_rows((DOCKER_DEVICES / name).read_text())
    assert rows, f"{name} draws no parameter text at all"
    for text, x, _ in rows:
        assert x > PIN_COLUMN_X, (
            f"{name}: {text!r} is anchored at x={x}, inside the drain/source pin column "
            f"(|x| <= {PIN_COLUMN_X}) — a wire on that column is drawn through it (#244)"
        )


@pytest.mark.parametrize("name", SYMBOLS)
def test_parameter_text_stays_above_the_bulk_label_stub(name: str) -> None:
    """The bulk pin's stub drops from ``y=0`` to ``y=+94`` at ``x=+-80``; text below 0 is crossed.

    Both of ``wiring._label_candidates``' bulk candidates go DOWNWARD (the ``vdir=-1`` branch
    double-negates), and ``_accept`` exempts a stub from its OWN device's boxes — so nothing else
    keeps that wire off the device's own text.
    """
    for text, _, y in _param_rows((DOCKER_DEVICES / name).read_text()):
        assert y < 0, f"{name}: {text!r} sits at y={y}, in the bulk label stub's half-plane"


@pytest.mark.parametrize("name", SYMBOLS)
def test_the_model_is_drawn(name: str) -> None:
    """#249: the flavour a generic-lane instance carries must appear on the render."""
    texts = [t for t, _, _ in _rows((DOCKER_DEVICES / name).read_text())]
    assert "@model" in texts, f"{name} draws no @model row — a mixed-flavour sheet cannot be read"


@pytest.mark.parametrize("name", SYMBOLS)
def test_the_no_params_twin_is_unchanged(name: str) -> None:
    """The DEFAULT lane draws ``*_np.sym``; adding a parameter row must not reach it.

    ``clean_symbol`` strips every ``T`` record that displays a parameter (``@model`` included), so
    the committed twin has to come back byte for byte — otherwise every sheet drawn without
    ``--show-params`` moves too.
    """
    src = (DOCKER_DEVICES / name).read_text()
    twin = (DOCKER_DEVICES / name.replace(".sym", "_np.sym")).read_text()
    assert clean_symbol(src) == twin
    # The K-block `format=` still uses @model (it netlists the device); only the DISPLAY row goes.
    assert not [t for t, _, _ in _rows(clean_symbol(src)) if _PARAM.search(t)]


def test_the_text_lane_constants_agree_with_the_symbol() -> None:
    """The keep-out/pitch math lives in three modules; the symbol is the fourth source of truth.

    They drifted before (22 against a symbol that drew from 7.5), which is how a net label landed on
    a neighbour's size text (#159). Pin them to each other so the next move of the text has to move
    them too.
    """
    from spicexplorer_netlist2xschem.emit import _PARAM_X0
    from spicexplorer_netlist2xschem.placement import _TEXT_X0 as PLACEMENT_X0
    from spicexplorer_netlist2xschem.placement import PhasedPlacer
    from spicexplorer_netlist2xschem.wiring import _TEXT_X0 as WIRING_X0

    anchors = {x for _, x, _ in _param_rows((DOCKER_DEVICES / "nmos4.sym").read_text())}
    assert len(anchors) == 1, f"the parameter rows no longer share one anchor: {anchors}"
    anchor = anchors.pop()
    assert WIRING_X0 == PLACEMENT_X0 == PhasedPlacer._TEXT_X0 == _PARAM_X0 == anchor
