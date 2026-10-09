"""Default arguments draw every sheet byte for byte as the code before channel routing did.

Channel routing (issue #243) and ``--collapse`` (issue #264) are helpers a schematic agent asks
for; they are off by default. This module pins that: each case below is drawn with the default
routing arguments, and the SHA-256 of its ``.sch`` text must equal the digest recorded in
``fixtures/golden/default_output.json``. Those digests were written by the code before either
change (platform commit ``c6549d9``), by running this file as a script against that commit's
``src/``::

    PYTHONPATH=<c6549d9>/packages/spicexplorer-netlist2xschem/src \\
        python tests/test_default_output.py > tests/fixtures/golden/default_output.json

so the module uses no name that commit lacks. Most cases are the ones that commit draws
differently once a sheet is taken for a block diagram: the 40-block fixture (default placer and
four hand floorplans), the 2- and 7-block arrays, one block with a resistor at each of 72
positions around it, plus sheets that were never block diagrams (two blocks with a MOSFET, an HBT
pair with no MOSFET, a placer that places a device the emitter skips, and the four circuit
fixtures under each placer that draws them, 11 sheets). Every symbol comes from the checked-in ``fixtures/`` libraries, so no
installed library changes a digest.

If a default-output change is ever intended, regenerate the file from the new code and say so in
the PR; the test otherwise names every case whose bytes moved.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from spicexplorer_netlist2xschem import (
    GridPlacer,
    PhasedPlacer,
    SymLibrary,
    TopologyPlacer,
    build_sch,
    from_file,
    from_string,
)
from spicexplorer_netlist2xschem.geometry import Transform
from spicexplorer_netlist2xschem.ingest import Device, DeviceKind, MosPolarity, N2XCircuit
from spicexplorer_netlist2xschem.mapping import register_subckt_symbol

FIXTURES = Path(__file__).parent / "fixtures"
BLOCKDIAG = FIXTURES / "blockdiag"
GOLDEN = FIXTURES / "golden" / "default_output.json"
PDK = "default-output-fixture"  # a token of its own: the subckt symbol table is module-global
for _cell in (f"blk_{c}" for c in "abcdefghi"):
    register_subckt_symbol(PDK, _cell, f"blockdiag/{_cell}.sym")

ONE_BLOCK = """* one block, a resistor between two of its pins, two sources (synthetic)
XA0 a b c d vdd vss blk_a
R1 a d 1k
V1 vdd vss 1.2
V2 b vss 0.6
.end
"""

HBT_PAIR = """* two HBTs, two poly resistors, no MOSFET, no design block (synthetic)
XQ1 c1 b e 0 npn13G2 Nx=1
XQ2 c2 b e 0 npn13G2 Nx=1
XR1 vdd c1 rsil w=0.5e-6 l=1e-6
XR2 vdd c2 rsil w=0.5e-6 l=1e-6
V1 vdd 0 1.2
.end
"""

SKIPPED_DEVICE = """* a resistor, a source and a subcircuit with no symbol (synthetic)
R1 a b 1k
V1 a 0 1
XU1 a b nosuchcell
.end
"""

BLOCKS_AND_MOSFET = """* two blocks and a MOSFET (synthetic)
XB0 clk rst n0 n1 vdd vss blk_a
XB1 clk rst n1 n2 vdd vss blk_a
M1 n2 clk vss vss sg13_lv_nmos w=1u l=0.13u
.end
"""


@dataclass
class FixedPlacer:
    """A hand floorplan: the exact transform per instance."""

    at: dict[str, Transform]

    def place(self, circuit, lib=None, *, hints=None) -> dict[str, Transform]:  # noqa: ARG002
        return dict(self.at)


def _grid_at(circuit: N2XCircuit, pitch: int, cols: int = 8) -> dict[str, Transform]:
    refs = sorted(d.ref for d in circuit.devices)
    return {r: Transform((i % cols) * pitch, (i // cols) * pitch) for i, r in enumerate(refs)}


def _array(n: int) -> N2XCircuit:
    """``n`` blk_a cells in a row: shared clk/rst/vdd/vss, each output the next one's input."""
    devs = [
        Device(
            ref=f"XB{i}",
            kind=DeviceKind.SUBCKT,
            model="blk_a",
            polarity=MosPolarity.UNKNOWN,
            pins=("clk", "rst", "vin", "q", "vdd", "vss"),
            nets={
                "clk": "clk",
                "rst": "rst",
                "vin": f"n{i}",
                "q": f"n{i + 1}",
                "vdd": "vdd",
                "vss": "vss",
            },
            params={},
        )
        for i in range(n)
    ]
    nets = sorted({v for d in devs for v in d.nets.values()})
    return N2XCircuit("array", tuple(devs), tuple(nets), {"vdd": "VDD", "vss": "VSS"})


def one_block_positions() -> list[tuple[int, int]]:
    """R1 on a 100-unit grid from -400 to 400, outside the block's 3 x 3 centre: 72 positions."""
    return [
        (x, y)
        for y in range(-400, 401, 100)
        for x in range(-400, 401, 100)
        if not (abs(x) <= 100 and abs(y) <= 100)
    ]


def default_sheets() -> dict[str, str]:
    """Every case drawn with the default routing arguments: case id -> ``.sch`` text."""
    out: dict[str, str] = {}
    blocks = SymLibrary([FIXTURES / "sym", FIXTURES])
    top = from_file(BLOCKDIAG / "blockdiag_top.spice", into="xtop", name="blockdiag_top")
    out["blockdiag/default-placer"] = build_sch(top, pdk=PDK, lib=blocks).text
    for pitch in (240, 300, 360, 500):
        placer = FixedPlacer(_grid_at(top, pitch))
        out[f"blockdiag/pitch-{pitch}"] = build_sch(top, pdk=PDK, lib=blocks, placer=placer).text
    for n in (2, 7):
        arr = _array(n)
        row = FixedPlacer({d.ref: Transform(i * 360, 0) for i, d in enumerate(arr.devices)})
        out[f"array-{n}/row-360"] = build_sch(arr, pdk=PDK, lib=blocks, placer=row).text
        out[f"array-{n}/default-placer"] = build_sch(arr, pdk=PDK, lib=blocks).text
    one = from_string(ONE_BLOCK, name="one_block")
    for x, y in one_block_positions():
        at = {
            "XA0": Transform(0, 0),
            "R1": Transform(x, y),
            "V1": Transform(-700, 0),
            "V2": Transform(700, 0),
        }
        out[f"one-block/r1-at-{x}-{y}"] = build_sch(
            one, pdk=PDK, lib=blocks, placer=FixedPlacer(at)
        ).text
    mixed = from_string(BLOCKS_AND_MOSFET, name="mixed_blocks")
    out["blocks-and-mosfet/default-placer"] = build_sch(mixed, pdk=PDK, lib=blocks).text
    kit = SymLibrary([FIXTURES / "sym"])
    hbt = from_string(HBT_PAIR, name="hbt_pair")
    out["hbt-pair/default-placer"] = build_sch(hbt, pdk="ihp-sg13g2", lib=kit).text
    # The placer places XU1, which has no symbol and is skipped: the loose title is still placed
    # clear of every transform the placer returned.
    skipped = from_string(SKIPPED_DEVICE, name="skipped_device")
    at = {"R1": Transform(0, 0), "V1": Transform(300, 0), "XU1": Transform(-900, -900)}
    out["skipped-device/title"] = build_sch(
        skipped, pdk="ihp-sg13g2", lib=kit, placer=FixedPlacer(at), title="skipped_device"
    ).text
    for name, into in (
        ("ota-improved", None),
        ("ota-5t_tb-ac", "xota"),
        ("mixed_devices", None),
        ("folded_cascode", None),
    ):
        circuit = from_file(FIXTURES / f"{name}.spice", name=name, into=into)
        for pname, placer in (
            ("phased", PhasedPlacer()),
            ("topology", TopologyPlacer()),
            ("grid", GridPlacer()),
        ):
            try:
                doc = build_sch(circuit, pdk="ihp-sg13g2", lib=kit, placer=placer, title=name)
            except ValueError:
                continue  # TopologyPlacer on a sheet with no drawable device (folded_cascode)
            out[f"{name}/{pname}"] = doc.text
    return out


def _digests(sheets: dict[str, str]) -> dict[str, str]:
    return {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sorted(sheets.items())}


def test_default_arguments_draw_every_sheet_as_before():
    """95 sheets; the assertion names every case whose bytes differ from the recorded digest."""
    expected = json.loads(GOLDEN.read_text())
    got = _digests(default_sheets())
    assert set(got) == set(expected)
    assert len(got) == 95
    moved = sorted(k for k in got if got[k] != expected[k])
    assert not moved, f"{len(moved)} of {len(got)} sheets differ: {', '.join(moved)}"


if __name__ == "__main__":  # write the digests of whatever src/ is first on the path
    sys.stdout.write(json.dumps(_digests(default_sheets()), indent=1) + "\n")
