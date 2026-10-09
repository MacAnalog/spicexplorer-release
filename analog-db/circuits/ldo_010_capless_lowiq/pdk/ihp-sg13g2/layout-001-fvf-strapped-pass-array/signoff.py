"""005 — layout sign-off driver: guards -> GDS -> current density -> DRC -> LVS -> PEX.

Every stage is the platform's own runner (`spicexplorer_signoff`, `spicexplorer_layout`); this
file only sequences them and writes the verdicts a reviewer reads. Two interpreters are
involved and the split is not cosmetic:

* ``gen_layout.build`` needs **gdsfactory + ihp-gdsfactory** -> `$LDO_GF_PYTHON`
  (default ``~/miniconda3/envs/ai_env/bin/python``); it is run as a subprocess.
* DRC / LVS / PEX are KLayout runsets + kpex, driven from THIS interpreter through
  `spicexplorer_signoff` (which finds its own klayout/kpex executables via `$PDK_ROOT`).

  ``SIGNOFF_PYTHON``, if set, must name an interpreter that can import **both ``docopt``**
  (the PDK's ``run_lvs.py`` imports it) **and the layout API**. Leaving it unset resolves
  `pdk.runner_python()` to this checkout's venv, which has both. An interpreter missing
  ``docopt`` gives ``matched=False``, an empty run directory and an empty ``reason`` -- the
  ``ModuleNotFoundError`` traceback IS in the returned log, but `run_lvs` does not promote a
  non-zero exit into ``reason``, so a caller that records only ``matched``/``reason`` (this
  file did) reports a mismatch with no cause. Platform follow-up:
  doc/journal/run-lvs-swallows-its-own-traceback.md (review-002 m7).

The engine of record is therefore **KLayout** (IHP SG13G2 runsets) for DRC/LVS and **kpex**
(2.5D) for extraction -- not magic/netgen.

Two PDK-runset quirks are handled here, both journalled:

1. **kpex cannot read a 2-node ``rhigh``.** The standalone IHP LVS deck extracts the poly
   resistor as a 2-terminal device, but kpex's bundled copy
   (``rule_decks/custom_reader.lvs``: ``'Poly resistor should have 3 nodes'``) extracts it as
   3-terminal (two ports + substrate, connected to pwell). The LVS schematic and the PEX
   schematic therefore differ by that third node -- :func:`pex_schematic` adds it.
2. **kpex cannot extract IHP MIM caps** -- ``strip_mim_for_pex`` removes the MIM device layers
   and the C cards; the schematic MIM capacitors are spliced back for the benches.

Two stages exist because `review-002` said "silence from a check that did not run is not
evidence":

* **guards** — `test_builder.py`, the case M8 asked for: a Metal1 stub collision that only
  the obstacle map prevents.  It runs first and blocks, so the guard is exercised every round.
* **current density** — `spicexplorer_signoff.current_density` over the budget list the
  GENERATOR emits from its own drawn geometry (`gen_layout.power_budgets`), never a retyped table.
  Electromigration is not a rule-deck check and not a connectivity check, so without this stage a
  cell can pass DRC, LVS, PEX and every bench at 12-28x over the metal limit — which the cell of
  record did (B1, `doc/journal/metal-current-density-is-nobodys-check.md`).

    analog-db layout run --circuit ldo_010_capless_lowiq --step signoff -- --out <work dir>

**Vendored** from an agent-first design repo @ ``40cad45`` (``layout/signoff.py``). Three
changes, all of them the seam between the source repo and this entry: the working root is
``$SX_SCRATCH/ldo-adb/layout`` instead of the source repo's ``ldo.config.WORK``; the iteration
snapshot stage is dropped (it wrote into that repo's ``layout/ldo_ihp_capless/iterations/``,
which has no counterpart here); and ``--pex-mode`` defaults to **RC**, the mode of the
post-layout row of record, rather than to the CC comparison row.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CELL = "ldo_ihp_capless"
GEN = Path(__file__).resolve().parent / "gen_layout.py"
GF_PYTHON = os.environ.get("LDO_GF_PYTHON", str(Path.home() / "miniconda3/envs/ai_env/bin/python"))
#: Default working root. Everything this driver writes -- GDS, DRC/LVS/PEX run dirs, signoff.json
#: -- is regenerable output, so it goes to scratch, never into the repo. `out/` here holds only
#: the small text artefacts a reviewer reads.
WORK = Path(os.environ.get("SX_SCRATCH", str(Path.home() / "sx-scratch"))) / "ldo-adb" / "layout"


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print("  $", " ".join(str(c) for c in cmd)[:160], flush=True)
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)


# ---------------------------------------------------------------- build ----

def guards() -> dict:
    """The generator's own regression case (review-002 M8).  A blocker: a router guard that no
    case exercises rots, and this one is the difference between a shorted netlist and a clean
    one."""
    r = _run([sys.executable, str(Path(__file__).resolve().parent / "test_builder.py")])
    ok = r.returncode == 0
    print(" ", (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else "")
    return {"passed": ok, "log": (r.stdout + r.stderr)[-2000:]}


def current_density(power_json: Path) -> dict:
    """Score every current-carrying segment the generator drew against the PDK's own limits."""
    from spicexplorer_signoff.current_density import Budget, check_current_density, limit_for

    rows = json.loads(power_json.read_text())
    r = check_current_density([Budget(**d) for d in rows], pdk="ihp-sg13g2")
    table = []
    for d in rows:
        lim = limit_for(d["layer"], width_um=d["width_um"], n_vias=d["n_vias"])
        table.append({**d, "limit_a": lim[0] if lim else None, "rule": lim[1] if lim else None,
                      "over": round(d["current_a"] / lim[0], 4) if lim else None})
    worst = max((t["over"] for t in table if t["over"] is not None), default=None)
    print(f"  current density: passed={r.passed} checked={r.n_checked} worst={worst}")
    return {"passed": bool(r.passed), "n_checked": int(r.n_checked),
            "n_violations": int(r.n_violations), "worst_over": worst,
            "reason": r.reason, "segments": table,
            "violations": [v.__dict__ for v in r.violations]}


def build(out: Path, sizing: Path | None = None, params: dict | None = None) -> dict:
    """GDS + LVS reference + power-path budget at the sizing of record (or `sizing`)."""
    out.mkdir(parents=True, exist_ok=True)
    gds, lvs = out / f"{CELL}.gds", out / f"{CELL}_lvs.spice"
    cmd = [GF_PYTHON, GEN, "-o", gds, "--lvs", lvs, "--power", out / "power_path.json"]
    if sizing:
        cmd += ["--sizing", str(sizing)]
    if params:
        cmd += ["--params", json.dumps(params)]
    r = _run(cmd)
    if r.returncode != 0 or not gds.is_file():
        raise SystemExit(f"generator failed:\n{r.stdout}\n{r.stderr}")
    m = re.search(r"area um2: (\d+)", r.stdout)
    print(" ", r.stdout.strip().splitlines()[0])
    return {"gds": str(gds), "lvs_netlist": str(lvs), "power_path": str(out / "power_path.json"),
            "area_um2": int(m.group(1)) if m else None, "sizing": str(sizing) if sizing else None,
            "stdout": r.stdout.strip()}


def knob_space() -> dict:
    """`LayoutParams` defaults + `BOUNDS`, read from the generator (which needs gdsfactory)."""
    r = _run([GF_PYTHON, "-c",
              "import sys, json, dataclasses;"
              f"sys.path.insert(0, {str(GEN.parent)!r});"
              "import gen_layout as G;"
              "print(json.dumps({'bounds': G.BOUNDS,"
              " 'defaults': dataclasses.asdict(G.LayoutParams())}))"])
    if r.returncode != 0:
        raise SystemExit(f"cannot read the knob space:\n{r.stdout}\n{r.stderr}")
    return json.loads(r.stdout.strip().splitlines()[-1])


def bounds(out: Path, jobs: int = 2, only: str = "") -> dict:
    """Build + DRC + LVS at BOTH ends of every documented knob range (review-003 **F2**).

    "5 of 10 tested in-range values give a cell that is not the certified circuit" — the ranges
    were written as a search space and never walked.  This stage is what makes `BOUNDS` a claim
    instead of a comment; the run is capped at 2 concurrent KLayout jobs, which is the documented
    ceiling for this host (eight gave seven spurious DRC failures with empty violation lists).
    """
    from concurrent.futures import ThreadPoolExecutor

    space = knob_space()
    todo = []
    for k, (lo, hi) in sorted(space["bounds"].items()):
        if only and k not in only.split(","):
            continue
        for tag, v in (("lo", lo), ("hi", hi)):
            d = space["defaults"][k]
            todo.append((k, tag, int(v) if isinstance(d, int) else float(v)))

    def one(job):
        k, tag, v = job
        d = out / "bounds" / f"{k}_{tag}"
        rec: dict = {"knob": k, "end": tag, "value": v}
        try:
            b = build(d, params={k: v})
            rec["area_um2"] = b["area_um2"]
        except SystemExit as exc:
            rec.update(built=False, reason=str(exc)[-400:])
            return rec
        rec["built"] = True
        try:
            cd = current_density(d / "power_path.json")
            rec["cd_ok"], rec["cd_worst"] = cd["passed"], cd["worst_over"]
            rc = drc(d / f"{CELL}.gds", d / "drc")
            rec["drc_ok"], rec["drc_n"] = rc["passed"], rc["n_violations"]
            rec["drc_rules"] = rc["violations_per_rule"]
            lv = lvs(d / f"{CELL}.gds", d / f"{CELL}_lvs.spice", d / "lvs")
            rec["lvs_ok"] = lv["matched"]
        except Exception as exc:            # noqa: BLE001
            rec["reason"] = f"{type(exc).__name__}: {exc}"
        rec["ok"] = bool(rec.get("built") and rec.get("drc_ok") and rec.get("lvs_ok")
                         and rec.get("cd_ok"))
        return rec

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        rows = list(ex.map(one, todo))
    bad = [r for r in rows if not r.get("ok")]
    for r in rows:
        print(f"  {r['knob']:16s} {r['end']:2s} {str(r['value']):>6s}  "
              f"built={r.get('built')} drc={r.get('drc_n')} lvs={r.get('lvs_ok')} "
              f"cd={r.get('cd_worst')}  {'OK' if r.get('ok') else 'FAIL'}")
    print(f"  bounds: {len(rows) - len(bad)}/{len(rows)} endpoints clean")
    return {"passed": not bad, "n": len(rows), "n_bad": len(bad), "rows": rows}


def render(gds: Path, png: Path) -> bool:
    r = _run([sys.executable, "-m", "spicexplorer_layout.cli", "render", str(gds), str(png)])
    ok = png.is_file()
    if not ok:
        print("  render failed:", (r.stdout + r.stderr)[-500:])
    return ok


# ------------------------------------------------------------- sign-off ----

def drc(gds: Path, out: Path, no_density: bool = True) -> dict:
    """Rule check. `no_density` skips the density/fill tables, which a standalone cell cannot
    satisfy on its own -- they are met by fill at chip assembly. The README states the flag and
    lists what those tables report when enabled (review-002 m1); pass `--density` to see them."""
    from spicexplorer_signoff.drc import run_drc
    r = run_drc(str(gds), CELL, str(out), no_density=no_density)
    print(f"  DRC: passed={r.passed} violations={r.n_violations}")
    # `DrcViolation` is not JSON-serialisable, and this line only ever runs when the list is
    # non-empty -- so a clean cell hid the bug until the first real violation (review-002 B1
    # attempt). Count per rule instead: which rules fired is what a reviewer reads.
    per_rule: dict[str, int] = {}
    hits: dict[str, list] = {}
    for v in r.violations:
        k = str(getattr(v, "rule", "?"))
        per_rule[k] = per_rule.get(k, 0) + int(getattr(v, "count", 1))
        hits[k] = [[float(x), float(y)] for x, y in (getattr(v, "locations", None) or [])][:60]
    for k, n in sorted(per_rule.items(), key=lambda kv: -kv[1]):
        print(f"    {k:18s} {n:4d}  e.g. {hits.get(k, [])[:3]}")
    return {"passed": bool(r.passed), "available": bool(r.available), "no_density": bool(no_density),
            "n_violations": int(r.n_violations), "violations_per_rule": per_rule, "hits": hits,
            "report": r.report_path, "reason": r.reason}


def lvs(gds: Path, netlist: Path, out: Path) -> dict:
    from spicexplorer_signoff.lvs import run_lvs
    r = run_lvs(str(gds), str(netlist), CELL, str(out), extra_args=["--combine_devices"])
    # The wrapper's pass flag is the runset's own verdict line; keep the raw evidence beside it.
    matched = bool(r.matched) or "Congratulations! Netlists match" in (r.log or "")
    print(f"  LVS: matched={matched}")
    return {"passed": bool(r.passed), "matched": matched, "available": bool(r.available),
            "unmatched": dict(r.unmatched or {}), "report": r.report_path,
            "netlist_sha": r.netlist_sha, "reason": r.reason}


_R_CARD = re.compile(r"^(R\S*)\s+(\S+)\s+(\S+)\s+(rhigh|rppd|rsil)\b(.*)$", re.I)


def pex_schematic(lvs_text: str, sub: str = "vss") -> str:
    """The LVS netlist as kpex's reader wants it: no C cards (MIM is stripped from the GDS too)
    and every poly resistor given its third, substrate node."""
    from spicexplorer_signoff.pex import strip_cards

    out = []
    for ln in strip_cards(lvs_text).splitlines():
        m = _R_CARD.match(ln.strip())
        out.append(f"{m.group(1)} {m.group(2)} {m.group(3)} {sub} {m.group(4)}{m.group(5)}" if m else ln)
    return "\n".join(out) + "\n"


def pex(gds: Path, lvs_netlist: Path, out: Path, mode: str = "CC") -> dict:
    from spicexplorer_signoff.pex import run_pex, strip_mim_for_pex

    pex_gds = gds.with_name(f"{CELL}_pex.gds")
    strip_mim_for_pex(gds, pex_gds)
    sch = gds.with_name(f"{CELL}_pex_schematic.spice")
    sch.write_text(pex_schematic(lvs_netlist.read_text()))
    # kpex drives its own KLayout LVS pass and does NOT pass `-rd target_netlist=` to the runset
    # (`klayout_pex/klayout/lvs_runner.py:49-69`), so `sg13g2.lvs:232-236` falls into its else
    # branch: `Pathname.new(RBA::CellView.active.filename).parent.realpath`.  That has TWO
    # destinations — the input GDS's own directory when a layout is loaded, and the PARENT of the
    # process cwd when the active cellview filename is empty (`Pathname.new("").parent` is `..`,
    # not `.`), which is how one landed a level above this repo.  The platform contains it at
    # `97cc0be`, so the chdir below is belt-and-braces for the second branch only.
    out.mkdir(parents=True, exist_ok=True)
    cwd0 = Path.cwd()
    try:
        os.chdir(out)
        r = run_pex(pex_gds, CELL, sch, out, mode=mode)
    finally:
        os.chdir(cwd0)
    rec = _pex_record(r)
    print(f"  PEX: ok={r.ok} n_C={rec['n_c']} n_R={rec['n_r']}"
          + ("" if rec["mesh_connected"] is None else
             f" mesh_connected={rec['mesh_connected']} "
             f"pins_on_mesh={rec['mesh'].get('device_pins_on_mesh')}/"
             f"{rec['mesh'].get('device_pins')} open_nets={rec['mesh'].get('n_open_nets')} "
             f"stub_nets={rec['mesh'].get('n_stub_nets')}"))
    return rec


def _pex_record(r) -> dict:
    """The JSON row for one PEX run — pure, so a constructed `PexResult` can test it.

    review-004 **F26**: this used to drop `PexResult.mesh_connected`, `.mesh` and
    `.raw_netlist_path`, which are the fields that separate "RC ran" from "RC measured
    something": kpex writes the resistor mesh as an electrical island, so `n_r > 0` is not
    evidence that any resistance is in the circuit.  With them dropped, an RC row and a
    stitched-but-open RC row are the same three numbers in the record.
    """
    # EVERY net, not the top twelve (review-003 **F10**): `x1` and `y` read "< 17.7" in the last
    # report only because the twelfth net was 17.7 fF — they are 11.28 and 11.50, i.e. a quarter
    # of their budgets, and a table that truncates cannot say that.
    rows = sorted(((v, k) for k, v in (r.per_net_c_ff or {}).items()), reverse=True)
    return {"ok": bool(r.ok), "available": bool(r.available), "mode": r.mode,
            "netlist": r.netlist_path, "raw_netlist": getattr(r, "raw_netlist_path", None),
            "n_c": int(r.n_c), "n_r": int(r.n_r),
            "mesh_connected": getattr(r, "mesh_connected", None),
            "mesh": dict(getattr(r, "mesh", None) or {}),
            "per_net_c_ff": {k: round(v, 3) for v, k in rows}, "reason": r.reason,
            "log_tail": (r.log or "")[-1500:] if not r.ok else ""}


def pex_gate(rec: dict) -> str:
    """`""` if this PEX row may be scored, else why it may not (review-004 **F26**).

    CC carries no mesh, so `mesh_connected is None` is "not applicable" and passes.  An RC/R row
    whose mesh is open measures the CC numbers with a floating resistor island attached — the
    one failure mode that looks like success in every other field.
    """
    if not rec.get("ok"):
        return f"PEX did not run: {rec.get('reason') or 'no reason given'}"
    if rec.get("mesh_connected") is False:
        m = rec.get("mesh") or {}
        return ("RC/R mesh is not connected to the devices — "
                f"{m.get('device_pins_on_mesh')}/{m.get('device_pins')} device pins on the mesh, "
                f"{m.get('n_open_nets')} open net(s); the netlist would measure the CC numbers")
    return ""


def _write_record(out: Path, rec: dict) -> None:
    """Merge this invocation's stages into `signoff.json` instead of replacing the file.

    review-004 **F24**: `rec` holds only the stages THIS invocation ran, and it was written
    whole — so the documented two-step flow (a CC round, then `--stages pex --pex-mode RC`)
    left the file containing nothing but the RC row, and the build / current-density / DRC / LVS
    verdicts of the same round survived only in the console log.
    """
    f = out / "signoff.json"
    old: dict = {}
    if f.is_file():
        try:
            old = json.loads(f.read_text())
        except json.JSONDecodeError:
            old = {}
    old.update(rec)
    f.write_text(json.dumps(old, indent=1) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(WORK))
    # PEX is NOT in the default chain. The record row was extracted once; re-extracting is a
    # third KLayout job for a netlist the entry already names, so a reproduction run stops after
    # LVS and hands the recorded netlist to pex_sim.py. Add `pex` to --stages to re-extract.
    ap.add_argument("--stages", default="guards,build,render,cd,drc,lvs")
    ap.add_argument("--sizing", default=None, help="JSON sizing overrides (a second sizing point)")
    ap.add_argument("--pex-mode", default="RC", choices=["CC", "RC", "R"],
                    help="PEX policy: RC (+ mesh stitching) is the row of record; CC is the "
                         "ideal-metal comparison row")
    ap.add_argument("--density", action="store_true",
                    help="run the density/fill rule tables too (review-002 m1)")
    ap.add_argument("--jobs", type=int, default=2,
                    help="concurrent KLayout jobs for the `bounds` stage (2 is the host ceiling)")
    ap.add_argument("--only", default="", help="restrict `bounds` to these knobs (comma list)")
    ap.add_argument("--no-gate", action="store_true",
                    help="report DRC/LVS instead of stopping on them (diagnosis only — a run "
                         "with this flag is not a sign-off)")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    stages = a.stages.split(",")
    rec: dict = {}
    gds, netlist = out / f"{CELL}.gds", out / f"{CELL}_lvs.spice"

    if "guards" in stages:
        print("guards:")
        rec["guards"] = guards()
        if not rec["guards"]["passed"]:
            _write_record(out, rec)
            raise SystemExit("router guards failed — see test_builder.py")
    if "build" in stages:
        print("build:"); rec["build"] = build(out, Path(a.sizing) if a.sizing else None)
    if "render" in stages:
        print("render:"); rec["render"] = render(gds, out / f"{CELL}.png")
    if "cd" in stages:
        print("current density:")
        rec["current_density"] = current_density(out / "power_path.json")
        if not rec["current_density"]["passed"]:
            _write_record(out, rec)
            raise SystemExit("current-density stage failed — a segment is over the process limit")
    # review-003 **F2**: only `guards` and `current_density` used to stop the run, so a build
    # whose LVS did not match still produced a PEX netlist and a scorecard.  A cell that is not
    # the certified circuit has no scorecard — DRC and LVS are gates, not report lines.
    if "drc" in stages:
        print("drc:"); rec["drc"] = drc(gds, out / "drc", no_density=not a.density)
        if not rec["drc"]["passed"] and not a.no_gate:
            _write_record(out, rec)
            raise SystemExit(f"DRC failed — {rec['drc']['n_violations']} violation(s): "
                             f"{rec['drc']['violations_per_rule']}")
    if "lvs" in stages:
        print("lvs:"); rec["lvs"] = lvs(gds, netlist, out / "lvs")
        if not rec["lvs"]["matched"] and not a.no_gate:
            _write_record(out, rec)
            raise SystemExit("LVS did not match — the drawn cell is not the certified circuit")
    if "bounds" in stages:
        print("bounds:")
        rec["bounds"] = bounds(out, jobs=a.jobs, only=a.only)
        _write_record(out, rec)
        if not rec["bounds"]["passed"] and not a.no_gate:
            raise SystemExit(f"{rec['bounds']['n_bad']} documented knob endpoint(s) do not build, "
                             f"do not pass DRC or do not match LVS")
    if "pex" in stages:
        print("pex:"); rec["pex"] = pex(gds, netlist, out / f"pex_{a.pex_mode.lower()}"
                                        if a.pex_mode != "CC" else out / "pex", mode=a.pex_mode)
        why = pex_gate(rec["pex"])
        if why and not a.no_gate:
            _write_record(out, rec)
            raise SystemExit(f"PEX stage failed — {why}")

    _write_record(out, rec)
    print("\nwrote", out / "signoff.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
