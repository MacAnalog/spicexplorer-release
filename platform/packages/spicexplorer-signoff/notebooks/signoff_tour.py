import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # spicexplorer-signoff tour, offline

    `spicexplorer-signoff` runs DRC, LVS and PEX and returns each result as a structured verdict
    (`DrcResult`, `LvsResult`, `PexResult`) instead of a log to read. This notebook shows how those
    verdicts are read, on the package's committed fixtures in `tests/fixtures/`:

    | section | call | input |
    |---|---|---|
    | 1. DRC | `parse_lyrdb`, `run_drc` | `mini.lyrdb`, a recorded KLayout report |
    | 2. LVS | `run_lvs` | `ihp_lvs_mismatch.log`, a recorded IHP SG13G2 LVS log |
    | 3. PEX | `summarize_parasitics`, `scan_parasitics` | `mini_pex.spice`, `kpex_ground_aliases.spice` |
    | 4. current density | `check_current_density`, `budgets_from_brief` | budgets written in the cell |

    Nothing needs KLayout, kpex, a PDK or ngspice. Where a runner would start KLayout, a short
    Python script stands in for it and replays the recorded output; the runner then reads that
    output exactly as it reads a real run's. `probe()` reports which real tools this machine has.
    """)
    return


@app.cell
def _(mo):
    import os
    import shutil
    import sys
    import tempfile
    from pathlib import Path
    from unittest.mock import patch

    from spicexplorer_signoff import (
        Budget,
        budgets_from_brief,
        check_current_density,
        run_drc,
        run_lvs,
    )
    from spicexplorer_signoff.drc import parse_lyrdb
    from spicexplorer_signoff.pdk import PdkPaths
    from spicexplorer_signoff.pex import scan_parasitics, summarize_parasitics

    FIX = (mo.notebook_dir() / "../tests/fixtures").resolve()
    WORK = Path(tempfile.mkdtemp(prefix="signoff-tour-"))
    print("fixtures:", sorted(p.name for p in FIX.iterdir()))
    return (
        Budget,
        FIX,
        PdkPaths,
        WORK,
        budgets_from_brief,
        check_current_density,
        os,
        parse_lyrdb,
        patch,
        run_drc,
        run_lvs,
        scan_parasitics,
        shutil,
        summarize_parasitics,
        sys,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. DRC: the report and the verdict

    KLayout writes its DRC findings to a `.lyrdb` XML report. `parse_lyrdb` turns it into one
    `DrcViolation` per rule: the rule name, the count and up to `max_locations` sample points in µm.
    """)
    return


@app.cell
def _(FIX, parse_lyrdb):
    print(f"{'rule':6s} {'count':>5s}  first locations / um")
    for _v in parse_lyrdb(FIX / "mini.lyrdb"):
        print(f"{_v.rule:6s} {_v.count:5d}  {_v.locations}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `run_drc` decides pass or fail. With a KLayout `.lydrc` rule deck, a pass needs three things
    from the same run: the deck's closing line `Number of DRC errors: 0`, a report written during
    this run, and exit status 0. The cell builds a `PdkPaths` that points at an empty `.lydrc`
    file, and a stand-in `klayout` that copies the recorded report to the path the deck is told
    to write and prints the count. `SIGNOFF_KLAYOUT` names the executable, as it would name a real
    KLayout. The same stand-in then replays a clean run.
    """)
    return


@app.cell
def _(FIX, PdkPaths, WORK, os, patch, run_drc, sys):
    def stand_in_klayout(report_text: str, count: int):
        """A `klayout` that writes `report_text` to the deck's report_file and prints the count."""
        exe = WORK / "bin" / "klayout"
        exe.parent.mkdir(parents=True, exist_ok=True)
        exe.write_text(
            f"#!{sys.executable}\n"
            "import pathlib, sys\n"
            "a = sys.argv[1:]\n"
            "rd = dict(a[i + 1].split('=', 1) for i, x in enumerate(a) if x == '-rd')\n"
            f"pathlib.Path(rd['report_file']).write_text({report_text!r})\n"
            f"print('Number of DRC errors: {count}')\n"
        )
        exe.chmod(0o755)
        return exe

    PDK_DIR = WORK / "pdk"
    PDK_DIR.mkdir(exist_ok=True)
    (PDK_DIR / "recorded.lydrc").write_text("<klayout-macro/>\n")
    PDK = PdkPaths(
        name="recorded",
        root=PDK_DIR,
        klayout_tech=PDK_DIR,
        drc_runner=PDK_DIR / "run_drc.py",  # absent: run_drc falls back to the .lydrc deck
        lvs_runner=PDK_DIR / "run_lvs.py",
        lyp=PDK_DIR / "recorded.lyp",
        ngspice_models=PDK_DIR,
        drc_decks=(PDK_DIR / "recorded.lydrc",),
    )
    GDS = WORK / "t.gds"
    GDS.write_bytes(b"")  # the stand-ins never read it; the runners only check that it exists

    _recorded = (FIX / "mini.lyrdb").read_text()
    _empty = "<report-database><items></items></report-database>"
    for _label, _report, _count in (("recorded", _recorded, 3), ("clean", _empty, 0)):
        _exe = stand_in_klayout(_report, _count)
        with patch.dict(os.environ, SIGNOFF_KLAYOUT=str(_exe)):
            _r = run_drc(GDS, "t", WORK / f"drc-{_label}", pdk=PDK)
        print(
            f"{_label:8s} passed={_r.passed!s:5s} n_violations={_r.n_violations} "
            f"rules={[(v.rule, v.count) for v in _r.violations]} deck={_r.deck and os.path.basename(_r.deck)} "
            f"no_density={_r.no_density}"
        )
    return GDS, PDK, stand_in_klayout


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. LVS: a recorded mismatch

    The IHP SG13G2 LVS deck prints `ERROR : Netlists don't match` on a mismatch, with no counts,
    and exits 0. `run_lvs` reads the verdict from the `<topcell>.log` the deck writes during this
    run, and records the reference netlist's path and SHA-256 so a reviewer can tell which file
    the layout was compared against. The recorded log came from a mirror whose reference had one
    gate net swapped. The stand-in `run_lvs.py` below writes that log where the deck writes its
    own; the second run swaps in the deck's match line.
    """)
    return


@app.cell
def _(FIX, GDS, PDK, WORK, os, patch, run_lvs, stand_in_klayout, sys):
    _mismatch = (FIX / "ihp_lvs_mismatch.log").read_text()
    _match = _mismatch.replace(
        "ERROR : Netlists don't match", "INFO : Congratulations! Netlists match."
    )
    _klayout = stand_in_klayout("", 0)  # run_lvs only needs a klayout to put on PATH
    for _label, _log in (("recorded", _mismatch), ("match", _match)):
        PDK.lvs_runner.write_text(
            "import pathlib, sys\n"
            "rd = [a.split('=', 1)[1] for a in sys.argv if a.startswith('--run_dir=')][0]\n"
            f"pathlib.Path(rd, 'cell.log').write_text({_log!r})\n"
        )
        with patch.dict(os.environ, SIGNOFF_KLAYOUT=str(_klayout), SIGNOFF_PYTHON=sys.executable):
            _r = run_lvs(GDS, FIX / "core.sp", "cell", WORK / f"lvs-{_label}", pdk=PDK)
        print(
            f"{_label:8s} passed={_r.passed!s:5s} matched={_r.matched!s:5s} unmatched={_r.unmatched}"
        )
        print(
            f"         reference {os.path.basename(_r.netlist_path or '')} sha256 {(_r.netlist_sha or '')[:12]}..."
        )
        _reason = (_r.reason or "-").replace(str(WORK.resolve()), "<work>")
        print(f"         reason: {_reason.replace(str(WORK), '<work>')}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. PEX: summing the extracted capacitance

    `summarize_parasitics` reads a kpex netlist and returns `(n_C, n_R, per-net C [fF], coupling C
    between net pairs [fF])`. A C card to a ground node (`0`, `gnd`, `vss`, `vsubs`, any case)
    counts as that net's C to ground and forms no pair. Nets such as `\$17` are kpex's internal
    nodes. `run_pex` returns the same four numbers in its `PexResult`.
    """)
    return


@app.cell
def _(FIX, summarize_parasitics):
    n_c, n_r, per_net, coupling = summarize_parasitics(FIX / "mini_pex.spice")
    print(f"mini_pex.spice: {n_c} C cards, {n_r} R cards")
    print(f"{'net':8s} {'C / fF':>8s}")
    for _net, _ff in sorted(per_net.items()):
        print(f"{_net:8s} {_ff:8.4f}")
    print("coupling / fF:", {_k: round(_v, 4) for _k, _v in coupling.items()})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    When the substrate is a subckt pin (`sub` below), name it with `ground_nets` so its C counts as
    C to ground; `scan_parasitics` also returns the ground set applied and the number of self-loop
    cards skipped (a C with both terminals on one net, such as kpex's `Cext_51 sub sub 23.0904f`).
    `kpex_ground_aliases.spice` is shaped on a recorded kpex CC extraction.
    """)
    return


@app.cell
def _(FIX, scan_parasitics):
    for _gnd in ((), ("sub",)):
        _s = scan_parasitics(FIX / "kpex_ground_aliases.spice", ground_nets=_gnd)
        print(
            f"ground_nets={_gnd!s:8s} n_c={_s.n_c} self-loops={_s.n_self} "
            f"C(sub)={_s.per_net_c_ff.get('sub', 0.0):.2f} fF "
            f"C(outp|sub)={_s.coupling_ff.get('outp|sub', 0.0):.2f} fF ground={_s.ground_nets}"
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Current density: the electromigration budget

    No rule deck checks whether a wire is wide enough for its current. `check_current_density`
    does it with arithmetic, no GDS: per net, the current and the conductor it is drawn on, against
    the limits in `spicexplorer_core/techs/ihp-sg13g2.yaml` (`em_limits:`). A row whose limit
    cannot be resolved, such as a width below the qualified band, is reported in `reason` and
    fails the result; it is never a pass.
    """)
    return


@app.cell
def _(Budget, check_current_density):
    _budgets = [
        Budget("vdd", 10e-3, "Metal1", width_um=0.8, note="supply strap"),
        Budget("vdd", 10e-3, "Via1", n_vias=4, note="strap to Metal2"),
        Budget("vout", 1e-3, "Metal2", width_um=2.0),
        Budget("vbias", 50e-6, "Metal1", width_um=0.1),
    ]
    _res = check_current_density(_budgets, tech="ihp-sg13g2")
    print(
        f"passed={_res.passed} checked={_res.n_checked} of {len(_budgets)} violations={_res.n_violations}"
    )
    print(f"{'net':5s} {'layer':7s} {'I / mA':>7s} {'limit / mA':>10s} {'over':>6s}  rule")
    for _v in _res.violations:
        print(
            f"{_v.net:5s} {_v.layer:7s} {_v.current_a * 1e3:7.2f} {_v.limit_a * 1e3:10.2f} {_v.over_factor:5.1f}x  {_v.rule}"
        )
    print("reason:", _res.reason)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `budgets_from_brief` builds the rows from a layout brief's `currents` block (`net`, `i_ma`) and
    the conductors the layout drew. A brief net with no drawn conductor becomes a row on no layer,
    which `check_current_density` reports as not drawn.
    """)
    return


@app.cell
def _(budgets_from_brief, check_current_density):
    _brief = {
        "currents": [
            {"net": "vout", "i_ma": 10.0, "kind": "dc", "what": "load path"},
            {"net": "vdd", "i_ma": 10.5, "kind": "dc"},
            {"net": "vbias", "i_ma": 0.05, "kind": "dc"},
        ]
    }
    _drawn = {"vout": ("TopMetal1", 2.0), "vdd": [("TopMetal1", 4.0), ("TopVia1", 0.0, 8)]}
    _rows = budgets_from_brief(_brief, _drawn)
    for _b in _rows:
        print(
            f"{_b.net:5s} {_b.layer or '(none)':9s} {_b.current_a * 1e3:6.2f} mA  W={_b.width_um} um  cuts={_b.n_vias}"
        )
    _res = check_current_density(_rows, tech="ihp-sg13g2")
    print(f"passed={_res.passed} checked={_res.n_checked} violations={_res.n_violations}")
    print("reason:", _res.reason)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Where to go next

    - `run_flow(build, params, netlist=, cell=, run_dir=)` chains build → DRC → LVS → PEX for a
      layout generator and stops at the first failing stage.
    - The same checks from a shell: `spicexplorer-signoff probe | drc | lvs | pex | current-density`,
      a JSON verdict on stdout. The package README lists every call and its result fields.
    """)
    return


@app.cell
def _(WORK, shutil):
    shutil.rmtree(WORK, ignore_errors=True)
    print("removed", WORK.name)
    return


if __name__ == "__main__":
    app.run()
