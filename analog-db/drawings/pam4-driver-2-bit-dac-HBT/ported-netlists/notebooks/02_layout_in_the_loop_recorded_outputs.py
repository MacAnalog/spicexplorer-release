"""Recorded outputs of the last Jupyter run of notebook 02 (layout in the loop).

This script replaces ``02_layout_in_the_loop.recorded-outputs.html``. It records the saved outputs
of ``02_layout_in_the_loop.ipynb`` at analog-db ``d5c63b38``, the last Jupyter run of the notebook
that ``02_layout_in_the_loop.py`` (marimo) now holds: the baseline gdsfactory layouts of the three
DUTs, their DRC/LVS signoff, the pre- vs post-layout (kpex) metrics, **8 optimizer trials**
(nevergrad TwoPointsDE, ``NB_BUDGET`` default 8, warm-started with two suggested points, the
directed-search winner and the paper-nominal electrical point; no RNG seed), the winning trial
``t001`` and the schematic-vs-post-layout summary.

The record is static: the notebook runs only on the layout lane (gdsfactory with ihp-gdsfactory,
kpex, KLayout DRC/LVS, ngspice and the IHP SG13G2 open PDK), and its optimizer is stochastic, so a
re-run gives a different trial table. Home paths read ``/home/<user>/``.

The data lives in ``02_layout_in_the_loop.recorded-outputs.json`` beside this file: per executed
cell, its stdout, Markdown lines, tables and figures. The figures are the notebook's saved layout
renders (PNG), committed in ``report_figs/``: the three baseline layouts
(``layout_dut_{lsb,msb,pam4}_baseline.png``) and the best-trial layout
(``pam4_layout_final.png``); each is checked against its recorded MD5.

Usage::

    python 02_layout_in_the_loop_recorded_outputs.py                     # print the record
    python 02_layout_in_the_loop_recorded_outputs.py --figures OUT_DIR   # also write the PNGs
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DATA = HERE / "02_layout_in_the_loop.recorded-outputs.json"


def load_record(path: Path = DATA) -> dict[str, Any]:
    """Return the recorded run, as stored in the JSON data file."""
    return json.loads(path.read_text(encoding="utf-8"))


def format_table(header: list[str], rows: list[list[str]]) -> str:
    """Render one recorded table as aligned plain text."""
    widths = [max(len(r[i]) for r in [header, *rows]) for i in range(len(header))]

    def line(cells: list[str]) -> str:
        return "  ".join(c.ljust(w) for c, w in zip(cells, widths, strict=True)).rstrip()

    rule = "  ".join("-" * w for w in widths)
    return "\n".join([line(header), rule, *(line(r) for r in rows)])


def image_bytes(output: dict[str, Any]) -> bytes:
    """Return the PNG bytes of one recorded figure, checked against its recorded MD5."""
    png = (HERE / output["file"]).read_bytes()
    if hashlib.md5(png).hexdigest() != output["md5"]:
        msg = f"figure {output['name']}: bytes differ from the recorded run"
        raise ValueError(msg)
    return png


def print_record(record: dict[str, Any], figures: Path | None = None) -> None:
    """Print every recorded output in cell order; write the figures to ``figures`` when given."""
    print(f"Recorded outputs of {record['source']}\n")
    if figures is not None:
        figures.mkdir(parents=True, exist_ok=True)
    for cell in record["cells"]:
        print(f"===== In [{cell['execution_count']}] (cell {cell['cell']}) =====")
        for out in cell["outputs"]:
            kind = out["kind"]
            if kind == "stdout":
                print(out["text"].rstrip("\n"))
            elif kind == "markdown":
                print(out["text"])
            elif kind == "table":
                print(format_table(out["header"], out["rows"]))
            elif kind == "image":
                png = image_bytes(out)
                if figures is None:
                    print(f"[figure {out['name']}: {len(png)} B PNG; --figures DIR writes it]")
                else:
                    target = figures / f"{out['name']}.png"
                    target.write_bytes(png)
                    print(f"[figure {out['name']} -> {target}]")
            else:
                msg = f"unknown output kind {kind!r}"
                raise ValueError(msg)
        print()


def main() -> None:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--figures",
        type=Path,
        default=None,
        metavar="DIR",
        help="copy the recorded layout renders as PNGs into DIR (keep DIR out of git)",
    )
    args = parser.parse_args()
    print_record(load_record(), args.figures)


if __name__ == "__main__":
    main()
