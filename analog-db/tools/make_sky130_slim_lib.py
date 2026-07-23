#!/usr/bin/env python3
"""Generate a SLIM sky130 ngspice corner library.

Native-ngspice sky130 simulations are dominated by *library-parse* time, not the
solve: `.lib sky130.lib.spice <corner>` pulls in the entire binned PDK model set
(~480k expanded lines: every MOS flavour + diodes + BJTs + caps + res + RF), and
ngspice rebuilds that model DB on every fresh process (~59 s, 99% CPU-bound). A
typical analog cell instances only a couple of device families, so almost all of
that parse work is wasted.

This tool writes `sky130_slim.lib.spice` next to the stock `corners/<corner>.spice`
files (same directory, so the per-device `.include` paths copied verbatim below resolve
relative to it). NOTE: that `corners/` dir is NOT on ngspice's sourcepath — only the
ngspice root (where the stock `sky130.lib.spice` lives) is — so a deck must reference this
slim lib by ABSOLUTE path, not a bare basename (a bare `.lib sky130_slim.lib.spice <c>`
fails with "Could not find library file"). The platform runner does this automatically.
Each corner section contains:
  * the shared preamble the models depend on, extracted from the stock `all.spice`
    (`.option scale`, the LOD-stress params `parameters/lod.spice`, and every
    `*_dlc_rotweak` param assignment), plus the mc switches set to nominal (0); and
  * ONLY the `.include` lines for the requested device families, copied VERBATIM
    from the stock `corners/<corner>.spice` (so whatever include form the PDK uses —
    `__<corner>.pm3.spice` for nfet_01v8, `__<corner>.corner.spice` for the rest —
    is reproduced exactly, guaranteeing numerically identical results).

Because mc_mm_switch / mc_pr_switch stay 0, no Monte-Carlo files are needed; the
slim lib is a nominal-corner drop-in and is byte-parity with the full lib for the
covered devices (validated: dc_op / ac metrics match to every printed digit).

Default families are the ones the analog-db corpus uses (1.8 V core + 5 V IO MOS);
override with --families. Result is ~90x faster for pure-core-MOS decks and ~50x
faster with the IO devices included.

Usage:
    make_sky130_slim_lib.py [--ngspice-dir DIR] [--families f1,f2,...]
                            [--pdk-root DIR] [--out NAME] [--check]

Exit status is non-zero if any referenced source file is missing.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

# The device families the analog-db sky130 decks instance (from _shared/pdk/sky130.yaml
# devices: nmos/pmos core+io). Exact device names; matched on a `__` word boundary so
# e.g. "nfet_01v8" never captures "nfet_01v8_lvt" or "esd_nfet_01v8".
DEFAULT_FAMILIES = [
    "nfet_01v8",
    "pfet_01v8",
    "nfet_g5v0d10v5",
    "pfet_g5v0d10v5",
]
CORNERS = ["tt", "ss", "ff", "sf", "fs"]
OUT_DEFAULT = "sky130_slim.lib.spice"


def resolve_ngspice_dir(ngspice_dir: str | None, pdk_root: str | None) -> str:
    """Locate the sky130 libs.tech/ngspice dir (holds corners/, all.spice, parameters/)."""
    if ngspice_dir:
        cand = os.path.abspath(ngspice_dir)
    else:
        root = pdk_root or os.environ.get("PDK_ROOT")
        if not root:
            sys.exit("error: pass --ngspice-dir or --pdk-root (or set $PDK_ROOT)")
        cand = os.path.join(os.path.abspath(root), "sky130A", "libs.tech", "ngspice")
    if not os.path.isdir(os.path.join(cand, "corners")):
        sys.exit(f"error: {cand} does not look like a sky130 ngspice dir (no corners/)")
    return cand


def read(path: str) -> str:
    with open(path, "r") as fh:
        return fh.read()


def family_include_lines(corner_text: str, families: list[str]) -> dict[str, list[str]]:
    """Return {family: [verbatim .include lines]} extracted from a stock corner file.

    Keeps both the model include (…__<corner>.pm3/corner.spice) and the mismatch
    include (…__mismatch.corner.spice) for each family, in file order.
    """
    got: dict[str, list[str]] = {f: [] for f in families}
    for line in corner_text.splitlines():
        s = line.strip()
        if not s.lower().startswith(".include"):
            continue
        for fam in families:
            # match sky130_fd_pr__<fam>__  exactly (double-underscore boundary)
            if re.search(rf"sky130_fd_pr__{re.escape(fam)}__", s):
                got[fam].append(s)
                break
    return got


def _dlc_assignments(all_text: str) -> list[tuple[str, str]]:
    """Every `<name>_dlc_rotweak = <value>` assignment in all.spice, normalized.

    all.spice mixes forms: a big `.param` continuation block (`+ name = value`) plus a
    few standalone `.param name=value` lines. Normalize both to (name, value) pairs,
    preserving file order (base defs precede the per-device aliases that reference them).
    """
    out: list[tuple[str, str]] = []
    for ln in all_text.splitlines():
        if "dlc_rotweak" not in ln:
            continue
        s = ln.strip()
        if s.startswith("+"):
            s = s[1:].strip()
        if s.lower().startswith(".param"):
            s = s[len(".param"):].strip()
        if "=" in s:
            name, val = s.split("=", 1)
            out.append((name.strip(), val.strip()))
    return out


def build_preamble(all_text: str, ngspice_dir: str, out_dir: str, families: list[str]) -> list[str]:
    """Shared per-section preamble lines, derived from the stock all.spice."""
    lines: list[str] = []

    # .option scale — decks give W/L in bare microns; missing this is a silent 1e6 error.
    m = re.search(r"^\s*\.option\s+scale\s*=\s*\S+", all_text, re.MULTILINE | re.IGNORECASE)
    lines.append(m.group(0).strip() if m else ".option scale=1.0u")

    # mc switches nominal (matches the stock .lib wrapper in sky130.lib.spice).
    lines.append(".param mc_mm_switch=0")
    lines.append(".param mc_pr_switch=0")

    # LOD-stress params (…__wlod_diff etc.) referenced by the pm3 model cards.
    lod = os.path.join(ngspice_dir, "parameters", "lod.spice")
    rel = os.path.relpath(lod, out_dir)
    lines.append(f'.include "{rel}"')

    # dlc_rotweak params: emit the base tokens (lv_/hv_/lvt_/… = value) plus the
    # per-target-family aliases (sky130_fd_pr__<fam>__dlc_rotweak = <base>). We keep
    # ALL base defs (a handful, cheap) and only the aliases for covered families, so
    # the referenced base is always present and no irrelevant device names leak in.
    assigns = _dlc_assignments(all_text)
    wanted = {f"sky130_fd_pr__{f}__dlc_rotweak" for f in families}
    emit: list[tuple[str, str]] = []
    for name, val in assigns:
        is_family = name.startswith("sky130_fd_pr__") or name.startswith("sky130_fd_bs_")
        if not is_family:
            emit.append((name, val))          # base def (lv_/hv_/lvt_/lvhvt_/sonos_…)
        elif name in wanted:
            emit.append((name, val))          # alias for a covered family
    if emit:
        lines.append(".param")
        for name, val in emit:
            lines.append(f"+ {name} = {val}")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate a slim sky130 ngspice corner lib.")
    ap.add_argument("--ngspice-dir", help="sky130A/libs.tech/ngspice (else derived from --pdk-root/$PDK_ROOT)")
    ap.add_argument("--pdk-root", help="PDK_ROOT (expects sky130A/ under it)")
    ap.add_argument("--families", help=f"comma list (default: {','.join(DEFAULT_FAMILIES)})")
    ap.add_argument("--out", default=OUT_DEFAULT, help=f"output filename in corners/ (default {OUT_DEFAULT})")
    ap.add_argument("--check", action="store_true", help="only verify source files exist; write nothing")
    args = ap.parse_args()

    ngspice_dir = resolve_ngspice_dir(args.ngspice_dir, args.pdk_root)
    corners_dir = os.path.join(ngspice_dir, "corners")
    out_path = os.path.join(corners_dir, args.out)
    families = [f.strip() for f in args.families.split(",")] if args.families else list(DEFAULT_FAMILIES)

    all_spice = os.path.join(ngspice_dir, "all.spice")
    if not os.path.isfile(all_spice):
        sys.exit(f"error: {all_spice} not found")
    all_text = read(all_spice)
    preamble = build_preamble(all_text, ngspice_dir, corners_dir, families)

    missing: list[str] = []
    out: list[str] = [
        "* SLIM sky130 corner library — GENERATED by make_sky130_slim_lib.py. DO NOT EDIT.",
        f"* Families: {', '.join(families)}.  Corners: {', '.join(CORNERS)}.",
        "* Drop-in for `.lib sky130.lib.spice <corner>` when a netlist uses only these",
        "* device families; cuts ngspice library-parse time from ~59 s to sub-second and",
        "* is numerically identical to the full lib for the covered devices. Re-run this",
        "* generator after a PDK update. Include forms are copied verbatim from the stock",
        "* corners/<corner>.spice, so parity holds across PDK versions.",
        "",
    ]

    for c in CORNERS:
        corner_file = os.path.join(corners_dir, f"{c}.spice")
        if not os.path.isfile(corner_file):
            sys.exit(f"error: stock corner file {corner_file} not found")
        inc = family_include_lines(read(corner_file), families)

        out.append(f".lib {c}")
        out.extend(preamble)
        for fam in families:
            if not inc[fam]:
                sys.exit(f"error: no include for family '{fam}' in {c}.spice "
                         f"(bad family name or unsupported PDK layout)")
            for line in inc[fam]:
                out.append(line)
                # validate the referenced file resolves relative to corners/
                mfile = re.search(r'"([^"]+)"', line)
                if mfile:
                    p = os.path.normpath(os.path.join(corners_dir, mfile.group(1)))
                    if not os.path.isfile(p):
                        missing.append(p)
        out.append(f".endl {c}")
        out.append("")

    if missing:
        for p in missing:
            print(f"MISSING source file: {p}", file=sys.stderr)
        return 2

    if args.check:
        print(f"OK: all sources present for families {families} across {CORNERS}")
        return 0

    with open(out_path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"wrote {out_path}  ({len(families)} families, {len(CORNERS)} corners)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
