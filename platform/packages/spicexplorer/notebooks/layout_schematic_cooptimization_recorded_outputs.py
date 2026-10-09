"""Recorded outputs of the last live run of ``layout_schematic_cooptimization.py``.

The co-optimization notebook's live outputs reproduce only on the layout lane (the
``live_layout`` gate of ``tests/test_notebooks.py``: a gdsfactory interpreter with
ihp-gdsfactory at ``$GDS_PYTHON``, KLayout with the PDK's DRC and LVS decks, kpex, and live
ngspice with the PDK). This script holds the saved outputs of its last Jupyter run on that
lane: ``packages/spicexplorer/notebooks/layout_schematic_cooptimization.ipynb`` at
``d85614c`` (2026-09-25), before the conversion to marimo. ``layout_schematic_cooptimization.py``
has not been re-run on that lane since.

The run: the 5T OTA ``amp_001_5t`` in IHP SG13G2, project ``OTA5T-GF-COOPT``, Nevergrad
``OnePlusOne`` with a budget of 16 trials and ``seed_from_init: true`` (trial 0 is the init
point), nine dimensions (three sizing widths and six layout knobs), 16 trials in 9.3 min
(35 s per trial). Best: trial 14, 208.3 um2 at 32.61 MHz post-layout UGF.

It replaces ``layout_schematic_cooptimization.recorded-outputs.html``. The data is in
``layout_schematic_cooptimization.recorded-outputs.json`` beside this file: every stdout and
stderr stream and every table each code cell printed, keyed by its execution count. The
trial scatter (area against post-layout UGF) is re-drawn from the recorded trials table. The
two KLayout layout renders of the HTML are not kept: they are pictures of GDS files that the
layout lane rebuilds from the generator defaults and from trial 14's vector in
``examples/layout/ihp-sg13g2/5t_ota_gf/coopt/coopt_replay.json``. Home and scratch paths read
``/home/<user>/``.

Usage::

    python layout_schematic_cooptimization_recorded_outputs.py            # print the record
    python layout_schematic_cooptimization_recorded_outputs.py --out DIR  # also save the figure
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DATA = Path(__file__).with_name("layout_schematic_cooptimization.recorded-outputs.json")
TRIALS_CELL = 12


def load_record(path: Path = DATA) -> dict[str, Any]:
    """Return the recorded run as the dict stored in the sibling JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def format_table(table: dict[str, Any]) -> str:
    """Return a recorded table as right-aligned text, the way pandas printed it."""
    header = ["", *table["columns"]]
    body = [[idx, *row] for idx, row in zip(table["index"], table["rows"], strict=True)]
    widths = [max(len(str(r[c])) for r in [header, *body]) for c in range(len(header))]
    lines = [
        "  ".join(str(v).rjust(w) for v, w in zip(r, widths, strict=True)) for r in [header, *body]
    ]
    return "\n".join(lines)


def trials(record: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the recorded trials table (cell ``In [12]``) as typed rows."""
    cell = next(c for c in record["cells"] if c["exec_count"] == TRIALS_CELL)
    table = next(o["table"] for o in cell["outputs"] if "table" in o)
    rows = []
    for raw in table["rows"]:
        row: dict[str, Any] = {}
        for name, value in zip(table["columns"], raw, strict=True):
            row[name] = value == "True" if name == "feasible" else float(value)
        rows.append(row)
    return rows


def trials_figure(record: dict[str, Any]) -> Any:
    """Re-draw the notebook's area-against-post-layout-UGF trial scatter (cell ``In [13]``)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = trials(record)
    spec = record["scatter"]["ugf_spec_MHz"]
    base = record["scatter"]["baseline"]
    feasible = [r for r in rows if r["feasible"]]
    best = min(feasible, key=lambda r: r["area_um2"])

    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.axvspan(spec, max(r["ugf_MHz"] for r in rows) * 1.02, color="#2e7d32", alpha=0.06, zorder=0)
    ax.axvline(spec, color="#2e7d32", lw=1.2, ls="--", zorder=1, label=f"UGF spec ({spec:.0f} MHz)")
    for flag, colour, marker, label in (
        (False, "#b0563a", "x", "violates a spec"),
        (True, "#2c5f8a", "o", "feasible"),
    ):
        sel = [r for r in rows if r["feasible"] is flag]
        ax.scatter(
            [r["ugf_MHz"] for r in sel],
            [r["area_um2"] for r in sel],
            c=colour,
            marker=marker,
            s=54,
            alpha=0.85,
            linewidths=1.4,
            label=label,
            zorder=3,
        )
    ax.scatter(
        best["ugf_MHz"],
        best["area_um2"],
        s=230,
        facecolors="none",
        edgecolors="#c9a227",
        linewidths=2.2,
        zorder=4,
        label="best (min area, feasible)",
    )
    ax.scatter(
        base["ugf_MHz"],
        base["area_um2"],
        marker="*",
        s=280,
        c="#555",
        zorder=4,
        label="baseline (layout of record)",
    )
    for r in rows:
        ax.annotate(
            str(int(r["trial"])),
            (r["ugf_MHz"], r["area_um2"]),
            fontsize=7.5,
            xytext=(4, 4),
            textcoords="offset points",
            color="#666",
        )
    ax.set_xlabel("post-layout UGF  [MHz]")
    ax.set_ylabel("core area  [µm²]")
    ax.set_title("Co-optimization trials — area vs post-layout UGF", fontsize=11)
    ax.grid(alpha=0.25, lw=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.tight_layout()
    return fig


def main(argv: list[str] | None = None) -> int:
    """Print every recorded output, cell by cell, and build the figure (saved with ``--out``)."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    parser.add_argument("--out", type=Path, help="directory to write the trial scatter PNG into")
    args = parser.parse_args(argv)

    record = load_record()
    print(f"source: {record['source']}\n")
    for cell in record["cells"]:
        print(f"=== In [{cell['exec_count']}] (cell {cell['cell']})")
        for out in cell["outputs"]:
            if "stream" in out:
                prefix = "[stderr] " if out["stream"] == "stderr" else ""
                print(prefix + out["text"].rstrip("\n"))
            elif "table" in out:
                print(format_table(out["table"]))
            elif "figure" in out:
                print(f"[figure: {out['figure']}, re-drawn from the trials table]")
            else:
                print(f"[not kept: {out['dropped_render']}]")
        print()

    fig = trials_figure(record)
    if args.out is not None:
        args.out.mkdir(parents=True, exist_ok=True)
        path = args.out / "trials_scatter.png"
        fig.savefig(path, dpi=110)
        print(f"wrote {path}")
    else:
        print("trial scatter built (pass --out DIR to save it)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
