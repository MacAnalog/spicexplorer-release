"""What of `placement.py` is actually live (#177 SCH-02).

A review measured this module at 1,078 lines — multiple placement algorithms while the README
documented one — and asked for the surface to be reduced to whatever use proves live. The
measurement says all three placers ARE live and no function in the file is unreferenced, so the
answer is not a deletion: it is this test, which keeps the claim true.

That matters more than the line count. The module's docstring had gone stale in exactly the way
that makes live code look dead — it still said `TopologyPlacer` was the default two placers later
— and a stale claim is what invites someone to delete a working algorithm.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import SymLibrary, placement
from spicexplorer_netlist2xschem.cli import PLACERS
from spicexplorer_netlist2xschem.ingest import from_string

SOURCE = Path(placement.__file__)

DECK = """* a small amplifier
M1 n1 vin vss vss nmos w=2u l=0.15u
M2 vout n1 vss vss nmos w=4u l=0.15u
M3 n1 nb vdd vdd pmos w=8u l=0.3u
M4 vout nb vdd vdd pmos w=8u l=0.3u
R1 vout vss 10k
C1 vout vss 100f
.end
"""


def _place(name: str):
    return PLACERS[name]().place(from_string(DECK, name="amp"), SymLibrary.default())


@pytest.mark.parametrize("name", sorted(PLACERS))
def test_every_placer_the_cli_offers_places_every_device(name):
    """Reachable from the command line AND able to place a real circuit.

    The three answer different questions — phased draws the readable sheet, topology the compact
    one a wide commercial-kit drawing needs (#159), grid the deterministic fallback a suspected
    placer bug is diffed against — so each is exercised rather than assumed.
    """
    circuit = from_string(DECK, name="amp")
    assert circuit.devices, "the fixture deck itself parsed to nothing"
    placed = PLACERS[name]().place(circuit, SymLibrary.default())
    assert set(placed) == {d.ref for d in circuit.devices}
    assert len({(t.x, t.y) for t in placed.values()}) == len(placed)  # no two devices stacked


def test_the_three_placers_draw_three_different_sheets():
    """Three distinct layouts is the evidence that three algorithms are live.

    `TopologyPlacer._columns` alone is 234 of this module's lines; a test that only checked "it
    returns a placement" would pass on a stub. Different coordinates for the same circuit cannot
    come from one algorithm wearing three names.
    """
    sheets = {
        name: tuple(sorted((r, t.x, t.y) for r, t in _place(name).items()))
        for name in ("phased", "topology", "grid")
    }
    assert len(set(sheets.values())) == 3, "two placers produced the identical sheet"


def test_no_function_in_this_module_is_unreferenced():
    """The dead-code guard: this is the check the review's finding actually asked for.

    Every function defined in `placement.py` must be named somewhere in the package besides its
    own `def`. Not a style rule — an unreferenced 234-line helper is what made the whole module
    look like carried weight, and the cost of that ambiguity was a review round.
    """
    tree = ast.parse(SOURCE.read_text())
    defined = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("__")
    }
    package = "\n".join(p.read_text() for p in sorted(SOURCE.parent.parent.rglob("*.py")))
    orphans = sorted(n for n in defined if package.count(n) <= 1)
    assert orphans == [], (
        f"placement.py defines {orphans} and nothing calls them. Delete them (git keeps the "
        "history) or wire them up — a helper nothing reaches is the surface this test exists to "
        "keep off the file."
    )


# --- a source's stimulus text needs a lane of its own (issue #223) -----------------------------

STIM_DECK = """* a transient bench: four pulse sources on one sheet
M1 d1 g1 vss vss nmos w=2u l=0.15u
M2 d1 g2 vss vss nmos w=2u l=0.15u
R1 d1 vdd 10k
V1 g1 vss PULSE(0 1.8 120.5n 100.25p 100.25p 666.125n 1332.25n)
V2 g2 vss PULSE(1 0 120n 100p 100p 666n 1332n)
V3 vdd vss PULSE(0 1.2 0 1n 1n 500n 1u)
V4 g3 vss PULSE(0 1 10n 100p 100p 666n 1332n)
.end
"""


@pytest.mark.parametrize("placer_name", ["grid", "phased"])
def test_a_sources_stimulus_text_does_not_run_over_the_next_source(placer_name):
    """A ``vsource``'s symbol draws ``@value``, and a pulse specification is ~40 characters wide —
    several times the column pitch the placers stacked sources at, so on a transient bench one
    source's stimulus was drawn straight through the next one (issue #223). The stimulus is the one
    thing a reviewer opens a transient sheet to read.
    """
    from spicexplorer_netlist2xschem.placement import text_reach

    circuit = from_string(STIM_DECK, name="stim")
    placement_map = PLACERS[placer_name]().place(circuit, SymLibrary([]))
    by_ref = {d.ref: d for d in circuit.devices}
    assert {"V1", "V2", "V3", "V4"} <= set(placement_map)

    rows: dict[int, list[tuple[int, str]]] = {}
    for ref, t in placement_map.items():
        rows.setdefault(t.y, []).append((t.x, ref))
    shared = 0
    for row in rows.values():
        row.sort()
        for (x_left, left), (x_right, _right) in zip(row, row[1:]):
            shared += 1
            assert x_right >= x_left + text_reach(by_ref[left]), (
                f"{left}'s text lane reaches x={x_left + text_reach(by_ref[left])}, "
                f"past the next device's origin at x={x_right}"
            )
    assert shared, "the deck placed nothing on a shared row — the test would prove nothing"


def test_text_reach_measures_what_the_symbol_draws():
    """A source's lane is sized from its VALUE (what ``vsource.sym`` draws as ``@value``), not from
    its model name, which an independent source does not have."""
    from spicexplorer_netlist2xschem.placement import text_reach

    circuit = from_string(STIM_DECK, name="stim")
    by_ref = {d.ref: d for d in circuit.devices}
    assert text_reach(by_ref["V1"]) > text_reach(by_ref["R1"])
    assert (
        text_reach(by_ref["V1"]) >= len("PULSE(0 1.8 120.5n 100.25p 100.25p 666.125n 1332.25n)") * 8
    )
