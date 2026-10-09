"""Write the synthetic block-diagram fixture of issue #243 (run from anywhere; writes beside itself).

A top level of 40 instances of nine generic cells, ``blk_a`` … ``blk_i``, each cell a placeholder
resistor, plus one generated block symbol per cell: inputs on the left, outputs on the right,
``vdd`` on top, ``vss`` at the bottom. Nothing here comes from a design or a kit.

    uv run --no-sync python packages/spicexplorer-netlist2xschem/tests/fixtures/blockdiag/make_fixture.py
"""

from __future__ import annotations

from pathlib import Path

from spicexplorer_netlist2xschem import BlockPin, generate_block_symbol

OUT = Path(__file__).parent

#: cell -> (inputs, outputs); every cell also has vdd and vss
CELLS: dict[str, tuple[list[str], list[str]]] = {
    "blk_a": (["clk", "rst", "vin"], ["q"]),
    "blk_b": (["clk", "din", "en"], ["dout"]),
    "blk_c": (["din", "rst", "bias"], ["dout"]),
    "blk_d": (["in0", "in1", "ck"], ["dout"]),
    "blk_e": (["in0", "in1", "rst"], ["dout"]),
    "blk_f": (["in0", "in1", "clk"], ["dout"]),
    "blk_g": (["ib"], ["bias"]),
    "blk_h": (["clk", "en"], ["ck"]),
    "blk_i": (["rst"], ["ib", "en"]),
}
TOP_PORTS = ["clk", "rst", "vin", "dout", "vdd", "vss"]


def ports(cell: str) -> list[str]:
    left, right = CELLS[cell]
    return [*left, *right, "vdd", "vss"]


def instances() -> list[tuple[str, str, dict[str, str]]]:
    """(ref, cell, port -> net), in placement order: 5 rows of 8."""
    out: list[tuple[str, str, dict[str, str]]] = []

    def add(cell: str, **nets: str) -> None:
        out.append((f"XU{len(out):02d}", cell, {**nets, "vdd": "vdd", "vss": "vss"}))

    for i in range(8):
        add("blk_a", clk="clk", rst="rst", vin="vin", q=f"a{i}")
    for i in range(8):
        add("blk_b", clk="clk", din=f"a{i}", en="en", dout=f"d{i}")
    for i in range(8):
        add("blk_c", din=f"d{i}", rst="rst", bias=f"bias{i // 2}", dout=f"o{i}")
    for k in range(4):
        add("blk_g", ib="ib", bias=f"bias{k}")
        add("blk_d", in0=f"o{2 * k}", in1=f"o{2 * k + 1}", ck=f"ck{k}", dout=f"p{k}")
    for k in range(4):
        add("blk_h", clk="clk", en="en", ck=f"ck{k}")
    for j in range(2):
        add("blk_e", in0=f"p{2 * j}", in1=f"p{2 * j + 1}", rst="rst", dout=f"s{j}")
    add("blk_f", in0="s0", in1="s1", clk="clk", dout="dout")
    add("blk_i", rst="rst", ib="ib", en="en")
    return out


def main() -> None:
    lines = [
        "* Synthetic block-diagram top level: 40 instances of 9 generic cells (issue #243 fixture).",
        "* Written by make_fixture.py from fixed rules; no design, no kit. Each cell body is a "
        "placeholder resistor.",
    ]
    for cell, (_left, right) in CELLS.items():
        lines += [
            f".subckt {cell} {' '.join(ports(cell))}",
            f"R1 {right[0]} vss 1k",
            f".ends {cell}",
        ]
    lines.append(f".subckt blockdiag_top {' '.join(TOP_PORTS)}")
    for ref, cell, nets in instances():
        lines.append(f"{ref} {' '.join(nets[p] for p in ports(cell))} {cell}")
    lines += [".ends blockdiag_top", f"xtop {' '.join(TOP_PORTS)} blockdiag_top", ".end"]
    (OUT / "blockdiag_top.spice").write_text("\n".join(lines) + "\n")
    for cell, (left, right) in CELLS.items():
        pins = [BlockPin(p, "left") for p in left] + [BlockPin(p, "right") for p in right]
        pins += [BlockPin("vdd", "top"), BlockPin("vss", "bottom")]
        (OUT / f"{cell}.sym").write_text(generate_block_symbol(cell, pins).text)


if __name__ == "__main__":
    main()
