"""Recorded outputs of the last Jupyter run of notebook 03 (PAM-4 driver signoff).

This script replaces ``03_signoff.recorded-outputs.html``. It holds the saved outputs of
``03_signoff.ipynb`` at commit ``d5c63b38`` (the Jupyter predecessor of the marimo notebook
``03_signoff.py`` beside this file), each keyed by the notebook section and execution count that
produced it. Home and scratch paths read ``/home/<user>/`` and ``/scratch/<user>/``.

It is a static record: these outputs cannot be reproduced by re-running the notebook. Two cells
read files that are in no repository: section 0 reads the EIC-designer project
(``~/code/EIC-designer/projects/lumped-broadband-driver/``), and section 0b reads the uncommitted
kpex netlist
``layout/out/pex/pam4/dut_pam4_nomim__pam4drv_pam4_lay/pam4drv_pam4_lay_k25d_pex_netlist.spice``.
Their outputs below are the only record. The other cells re-ran on 2026-09-25 (ngspice and the
IHP SG13G2 open PDK) and gave the same table values as below.

The five figures of that run are the committed PNGs in ``report_figs/`` (byte-identical to the
images the HTML embedded); this script checks their SHA-256 and lists them. The code and prose
cells are the notebook's own, in ``03_signoff.py``.

Usage::

    python 03_signoff_recorded_outputs.py          # print every recorded output, check figures
    python 03_signoff_recorded_outputs.py --show   # also display the figures (matplotlib)
"""

from __future__ import annotations

import argparse
import hashlib
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIG_DIR = HERE / "report_figs"

NAN = math.nan

# (section, execution count, title, stdout text)
TEXT_OUTPUTS: list[tuple[str, int, str, str]] = [
    (
        "0",
        2,
        "EIC layout and DRC report (reads the EIC-designer project; only record)",
        """\
EIC layout.gds: 616 bytes, cell 'top': 10 shapes, bbox (0,0;980000,120000) (dbu)

EIC DRC report header:
pdk: ihp_sg13g2
passed: false
total_violations: 0
drc:
  status: error
  deck: /home/<user>/pdks/IHP-Open-PDK/ihp-sg13g2/libs.tech/klayout/tech/drc/ihp-sg13g2.drc
""",
    ),
    (
        "0b",
        4,
        "npn13G2 model card vs the kpex netlist (reads the uncommitted kpex netlist; only record)",
        """\
.subckt npn13G2 c b e bn
.param Nx=1 dtemp=0
+Ny=1 le=0.96e-6 we=0.12e-6
+El=le*1e6
+selft=1
+sw_nqs=0
...
+ cje = '8.418E-15*(Nx*0.25)**0.975*vbic_cje'
+ cjep = '3.56E-15*(Nx*0.25)*vbic_cjc'
+ rth = '1*selft*3.26E+03*(4/Nx)**0.9'

kpex-extracted device card: (n/a)
""",
    ),
    (
        "1",
        5,
        "Post-layout adapter subcircuit",
        """\
* post-layout adapter: pam4drv_pam4_lay -> pam4drv_pam4 schematic ports
.subckt pam4drv_pam4 lsbp lsbn msbp msbn outp outn vcc vcasc vcmb blsb bmsb
Xlay sub msbn lsbp vcmb lsbn msbp tmsb0 tlsb0 tmsb1 vcasc outp outn vcc pam4drv_pam4_lay
Gtlsb0 tlsb0 0 blsb 0 1m
Gtmsb0 tmsb0 0 bmsb 0 1m
Gtmsb1 tmsb1 0 bmsb 0 1m
Vsub sub 0 DC 0
.ends pam4drv_pam4
.
""",
    ),
    ("7", 12, "Final cell", "signoff notebook complete\n"),
]

Row = tuple[str, list[object]]

# (section, execution count, title, column headers, rows); values as the notebook displayed them
TABLES: list[tuple[str, int, str, list[str], list[Row]]] = [
    (
        "2",
        6,
        "DC signoff: max swing and DAC levels",
        [
            "max swing [Vpp]",
            "DC level 0 [V]",
            "DC level 1 [V]",
            "DC level 2 [V]",
            "DC level 3 [V]",
        ],
        [
            ("schem-nominal", [2.368, -0.532, -0.176, 0.176, 0.532]),
            ("schem-retuned", [2.221, -0.497, -0.164, 0.164, 0.497]),
            ("post-layout", [2.209, -0.489, -0.161, 0.161, 0.489]),
        ],
    ),
    (
        "3",
        7,
        "Transient signoff: bias point",
        ["power [mW]", "V_CE Q1 (input) [V]", "V_CE Q3 (cascode) [V]", "tail node [V]"],
        [
            ("schem-nominal", [191.027, 1.348, 1.101, 0.934]),
            ("schem-retuned", [179.123, 1.445, 1.033, 0.938]),
            ("post-layout", [179.123, NAN, NAN, 0.938]),
        ],
    ),
    (
        "3",
        8,
        "Method cross-check: transient DFT vs .ac",
        ["S21@1G tran-DFT [dB]", "S21@1G .ac [dB]", "delta [dB]"],
        [
            ("schem-nominal", [9.071, "9.060", 0.011]),
            ("post-layout", [8.262, 8.249, 0.013]),
        ],
    ),
    (
        "4",
        9,
        "AC signoff: gain, bandwidth, matching",
        [
            "LSB gain [dB]",
            "MSB gain [dB]",
            "DAC weight [dB]",
            "BW LSB / MSB [GHz]",
            "S11 worst ≤32G [dB]",
            "S22 worst ≤50G [dB]",
        ],
        [
            ("schem-nominal", [3.09, 9.06, 5.97, "92.7 / 66.6", -10.96, -15.72]),
            ("schem-retuned", [2.42, 8.4, 5.98, "96.4 / 70.0", -11.38, -15.7]),
            ("post-layout", [2.27, 8.25, 5.98, "78.9 / 58.8", -10.03, -10.14]),
        ],
    ),
    (
        "5",
        10,
        "48 GBaud PAM-4 eye",
        ["vout_pp_v", "eye_openings_v", "rlm"],
        [
            ("schem-nominal", [0.888, "[0.264, 0.265, 0.267]", 0.975]),
            ("schem-retuned", [0.824, "[0.244, 0.246, 0.247]", 0.975]),
            ("post-layout", [0.81, "[0.244, 0.241, 0.247]", 0.974]),
        ],
    ),
    (
        "6",
        11,
        "Master spec table: paper vs EIC vs pre/post-layout",
        [
            "spec",
            "paper (meas.)",
            "EIC golden (schem)",
            "ours schem-nominal",
            "ours schem-retuned",
            "ours post-layout",
        ],
        [
            ("LSB gain [dB]", [">= 2.2", "3.2", "3.10 ✓", "3.09 ✓", "2.42 ✓", "2.27 ✓"]),
            ("MSB gain [dB]", [">= 8.2", "9.2", "9.07 ✓", "9.06 ✓", "8.40 ✓", "8.25 ✓"]),
            ("DAC weight [dB]", [">= 5", "6.0", "5.97 ✓", "5.97 ✓", "5.98 ✓", "5.98 ✓"]),
            ("BW [GHz]", [">= 50", "51–67 (meas.)", "68.50 ✓", "66.56 ✓", "70.01 ✓", "58.76 ✓"]),
            ("S11 [dB]", ["<= -10", "< −10", "-10.87 ✓", "-10.96 ✓", "-11.38 ✓", "-10.03 ✓"]),
            ("S22 [dB]", ["<= -10", "< −10", "-14.76 ✓", "-15.72 ✓", "-15.70 ✓", "-10.14 ✓"]),
            ("Swing [Vpp]", [">= 2.1", "2.1", "2.92 ✓", "2.37 ✓", "2.22 ✓", "2.21 ✓"]),
            ("Power [mW]", ["<= 192", "192", "191.03 ✓", "191.03 ✓", "179.12 ✓", "179.12 ✓"]),
            ("RLM", [NAN, "—", "0.975", "0.975", "0.975", "0.974"]),
            ("Area [mm²]", [NAN, "0.011 (core)", "—", "—", "—", "0.008"]),
        ],
    ),
]

# (section, execution count, file in report_figs/, SHA-256 of the PNG the run embedded)
FIGURES: list[tuple[str, int, str, str]] = [
    (
        "0",
        3,
        "pam4_layout_final.png",
        "903e01c918e96098174403439cd4388f467120d4d5da5dc4a791206bf62c37d4",
    ),
    (
        "2",
        6,
        "dc_transfer_dac_levels.png",
        "24ed9f5cb352f4ced1c14c1d675009313d5a5d4150635a0fb7e960f571100dec",
    ),
    (
        "3",
        7,
        "bias_ramp_transient.png",
        "2b54db6acda67aa3ee2fffea433524b2b8341b76efa043559a0eeb8cc6e71f7d",
    ),
    (
        "4",
        9,
        "sparams_s21_s11_s22.png",
        "55132c425fe6d3423dabda70f0da0c501e9ec97aa4c46373cd0bf4f763d1e6d5",
    ),
    (
        "5",
        10,
        "eye_48gbd_pam4.png",
        "eecf1200a1385bd13bd07f002a4a489388a022ef4276f9495dfe655e3eee463f",
    ),
]


def _cell(value: object) -> str:
    """Format one table value the way pandas displayed it (NaN as ``NaN``)."""
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    return str(value)


def format_table(headers: list[str], rows: list[Row]) -> str:
    """Render a table as aligned plain text, index column first."""
    grid = [["", *headers]] + [[name, *(_cell(v) for v in values)] for name, values in rows]
    widths = [max(len(line[i]) for line in grid) for i in range(len(grid[0]))]
    lines = [
        "  ".join(
            c.ljust(w) if i == 0 else c.rjust(w)
            for i, (c, w) in enumerate(zip(line, widths, strict=True))
        )
        for line in grid
    ]
    return "\n".join(lines)


def check_figures() -> list[str]:
    """Return one problem line per figure that is missing or differs from the recorded PNG."""
    problems = []
    for _section, _count, name, digest in FIGURES:
        path = FIG_DIR / name
        if not path.is_file():
            problems.append(f"missing: {path}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            problems.append(f"differs from the recorded figure: {path}")
    return problems


def show_figures() -> None:
    """Display the recorded figures with matplotlib, one window per figure."""
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    for section, count, name, _digest in FIGURES:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(mpimg.imread(FIG_DIR / name))
        ax.set_axis_off()
        ax.set_title(f"§{section}, In [{count}]: {name}")
        fig.tight_layout()
    plt.show()


def main(argv: list[str] | None = None) -> int:
    """Print every recorded output in notebook order; exit 1 when a figure does not match."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--show", action="store_true", help="display the figures with matplotlib")
    args = parser.parse_args(argv)

    blocks: list[tuple[int, str]] = []
    for section, count, title, text in TEXT_OUTPUTS:
        blocks.append((count, f"§{section}, In [{count}]: {title}\n{text}"))
    for section, count, title, headers, rows in TABLES:
        blocks.append(
            (count, f"§{section}, In [{count}]: {title}\n{format_table(headers, rows)}\n")
        )
    for section, count, name, _digest in FIGURES:
        blocks.append((count, f"§{section}, In [{count}]: figure report_figs/{name}\n"))
    for _count, block in sorted(blocks, key=lambda b: b[0]):
        print(block)

    problems = check_figures()
    for line in problems:
        print(line, file=sys.stderr)
    if args.show:
        show_figures()
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
