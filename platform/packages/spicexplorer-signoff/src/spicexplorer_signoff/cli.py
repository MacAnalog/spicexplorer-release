"""``spicexplorer-signoff`` CLI — JSON verdicts for probe / drc / lvs / pex / current-density."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .current_density import Budget, check_current_density
from .drc import run_drc
from .lvs import run_lvs
from .pdk import probe
from .pex import run_pex

#: What each :class:`Budget` field must be in a ``--budgets`` file. JSON that parses but carries a
#: string current or a null width used to crash inside the check (exit 1, the violation code, with
#: no verdict), and a string ``n_vias`` rode through into the verdict — a malformed file is exit 2.
_BUDGET_TYPES: dict[str, tuple[type, ...]] = {
    "net": (str,),
    "current_a": (int, float),
    "layer": (str,),
    "width_um": (int, float),
    "n_vias": (int,),
    "note": (str,),
}


def _typed(b: Budget) -> Budget:
    for name, want in _BUDGET_TYPES.items():
        v = getattr(b, name)
        if isinstance(v, bool) or not isinstance(v, want):  # bool is an int, and never a current
            kinds = " or ".join(t.__name__ for t in want)
            raise TypeError(f"net {b.net!r}: {name} must be {kinds}, got {v!r}")
    return b


def _read_budgets(ap: argparse.ArgumentParser, path: str) -> list[Budget]:
    """``--budgets FILE``: a JSON list of :class:`Budget` rows, or ``{"budgets": [...]}``."""
    try:
        data = json.loads(Path(path).read_text())
        rows = data["budgets"] if isinstance(data, dict) else data
        budgets = [_typed(Budget(**row)) for row in rows]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        ap.error(f"--budgets {path}: {type(exc).__name__}: {exc}")
    if not budgets:
        ap.error(f"--budgets {path}: no budget rows (a check with nothing to check is not a pass)")
    return budgets


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="spicexplorer-signoff", description="physical signoff runners with JSON verdicts"
    )
    ap.add_argument("--pdk", default="ihp-sg13g2")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe", help="which tools/decks are available")
    d = sub.add_parser("drc")
    d.add_argument("gds")
    d.add_argument("--cell", required=True)
    d.add_argument("--run-dir", required=True)
    d.add_argument("--density", action="store_true")
    lv = sub.add_parser("lvs")
    lv.add_argument("gds")
    lv.add_argument("--cell", required=True)
    lv.add_argument("--netlist", required=True)
    lv.add_argument("--run-dir", required=True)
    px = sub.add_parser("pex")
    px.add_argument("gds")
    px.add_argument("--cell", required=True)
    px.add_argument("--netlist", required=True)
    px.add_argument("--out-dir", required=True)
    px.add_argument("--mode", default="CC", choices=["CC", "RC", "R"])
    px.add_argument(
        "--halo",
        type=float,
        metavar="UM",
        help="kpex sidewall halo in um (default: the tech file's); name it beside the numbers",
    )
    cd = sub.add_parser(
        "current-density", help="electromigration: each net's drawn metal/vias vs its current"
    )
    cd.add_argument(
        "--budgets",
        required=True,
        metavar="FILE",
        help='JSON list of {net, current_a, layer, width_um, n_vias, note} rows, or {"budgets": [...]}',
    )
    cd.add_argument("--tech", help="tech name or tech YAML path for the limits (default: --pdk)")
    a = ap.parse_args(argv)
    if a.cmd == "probe":
        res = probe(a.pdk).to_dict()
        ok = True
    elif a.cmd == "drc":
        r = run_drc(a.gds, a.cell, a.run_dir, pdk=a.pdk, no_density=not a.density)
        res, ok = r.to_dict(), r.passed
    elif a.cmd == "lvs":
        r = run_lvs(a.gds, a.netlist, a.cell, a.run_dir, pdk=a.pdk)
        res, ok = r.to_dict(), r.passed
    elif a.cmd == "current-density":
        r = check_current_density(_read_budgets(ap, a.budgets), tech=a.tech or a.pdk)
        res, ok = r.to_dict(), r.passed
    else:
        r = run_pex(a.gds, a.cell, a.netlist, a.out_dir, mode=a.mode, pdk=a.pdk, halo_um=a.halo)
        res, ok = r.to_dict(), r.ok
    if "log" in res:
        res["log"] = res["log"][-1500:]
    json.dump(res, sys.stdout, indent=1, default=str)
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
