# spicexplorer-signoff

Physical signoff as a **library**: engine-agnostic **DRC / LVS / PEX** runners that return
structured verdicts (GDS in → verdict out), plus the two netlist-side helpers a post-layout
flow needs — splicing an extracted subckt into an existing bench deck, and injecting
parasitics / mismatch into a subckt to measure layout sensitivity (the primitive behind the
layout *brief*). One call — `run_flow(build, params, …)` — chains build → DRC → LVS → PEX for
any caller-supplied builder, which is exactly what an agent iteration or an optimizer trial
needs.

## Layering

Leaf tool: depends on `spicexplorer-core` (+ the `klayout` python wheel, which the PDK's own
`run_drc.py` / `run_lvs.py` import). The heavy tools — a `klayout` executable, `kpex`, the PDK
decks, ngspice — are **discovered at run time, never imported**; every runner degrades to an
`available=False` verdict, so the package imports and its offline tests pass on a machine with
none of them. Never imports a peer tool: the generator side hands in a build *callable*
(`spicexplorer_layout.GdsBuilder`), the benches stay in the block repo / analog-db.

Tools & PDK: `PDK_ROOT` (default `~/local/pdks`), `SIGNOFF_KLAYOUT` (default `klayout` on PATH),
`SIGNOFF_PYTHON` (interpreter for the PDK runners; default this one), `SIGNOFF_KPEX` /
`KPEX_KLAYOUT_EXE` (kpex + the Ruby ≥ 2.6 KLayout it drives). `probe()` tells you what is there.

## Public API

| call | returns | notes |
|---|---|---|
| `probe(pdk="ihp-sg13g2")` | `ToolProbe` (`drc_ok/lvs_ok/pex_ok`, tool paths) | cheap, launches nothing |
| `run_drc(gds, topcell, run_dir, no_density=True)` | `DrcResult` (`passed`, `n_violations`, `violations=[{rule,count,locations}]`, `report_path` .lyrdb) | PDK KLayout deck; paths made absolute (the runner `chdir`s) |
| `run_lvs(gds, netlist, topcell, run_dir)` | `LvsResult` (`matched`, `unmatched`, `netlist_sha`) | compares against the **certified** schematic netlist; the sha is in the verdict so a reviewer can prove which file |
| `run_pex(gds, cell, schematic, out_dir, mode="CC", halo_um=None)` | `PexResult` (`netlist_path`, `n_c/n_r`, `per_net_c_ff`, `coupling_ff`) | kpex 2.5D; `CC` in loops (RC's R-mesh can dangle gate pins), `RC` for the final report; `halo_um` overrides the tech sidewall halo (kpex `--halo`) — couplings beyond the halo (IHP: 8 µm) are DROPPED, so raise it when a spacing sweep crosses it |
| `pex.strip_mim_for_pex(gds_in, gds_out, layers=, topmetal_margin_um=)` / `pex.strip_cards(text)` | Path / text | **kpex has no `cap_cmim` support** (its IHP tech marks the MIM layer `<TODO>` and crashes): extract a MIM-stripped copy (default MIM + Vmim cleared, top plates cut back by 0.2 µm; `layers=` adds e.g. MemCap `(69,0)`, `topmetal_margin_um=None` keeps the plates as plain metal so their coupling still extracts) against a schematic without the `C` cards, then add the schematic MIM cards back for the benches |
| `run_flow(build, params, netlist=, cell=, run_dir=, pex_mode=)` | `FlowResult` (`gds, drc, lvs, pex, stage_failed`) | stops at the first failing gate; a builder exception is a `stage_failed="build"` verdict |
| `postlayout.prep_pex_subckt(pex, cell, rename=)` | text | `M`→`XM` cards (ngspice IHP devices are subckts), optional rename |
| `postlayout.extract_subckt / splice_subckt(deck, replacement, name)` | text | drop the extracted block into the block's own bench deck; pin lists must agree |
| `postlayout.to_lvs_reference(subckt, name, cell=)` | text | ngspice-style `X` subckt calls → the flat `M`/`C` cards the KLayout LVS deck reads (`w·m` combined, `ng` dropped, MIM `w/l/m` kept) |
| `postlayout.deltas(pre, post)` | `{key: {pre, post, delta, rel}}` | scorecard diff |
| `sensitivity.inject_caps / inject_resistor / scale_param / inject_vsource / inject_isource` | text | perturb a subckt (C net→ref, pair, one-sided, balanced; series R; ×/+ a device param; series V on a device pin = ΔV_T; dc current into a node = leakage) |
| `sensitivity.sweep(subckt, name, measure, nets=, pairs=, c_ff=(1,10), r_nets=, params=, i_nets=, v_pins=)` | `(baseline, [SensRow])` | `measure(text) -> {metric: value}` is the campaign's harness; rows carry `delta` and `per_unit` |

CLI: `spicexplorer-signoff probe | drc GDS --cell C --run-dir D | lvs GDS --cell C --netlist N --run-dir D | pex GDS --cell C --netlist N --out-dir D --mode CC` — JSON verdict on stdout, exit 0/1.

## Usage

```python
from spicexplorer_layout import GdsBuilder
from spicexplorer_signoff import run_flow, probe

assert probe().drc_ok
build = GdsBuilder(
    "layout/H12/gen_H12.py",
    "build/",
    cell="lpf_core_H12pc",
    sizing_json="signoff/post-pvt/H12-pdk-cap/design.json",
    python="~/miniconda3/envs/ai_env/bin/python",
)  # where gdsfactory lives
res = run_flow(
    build,
    {"gap_x": 1.2},
    netlist="signoff/post-pvt/H12-pdk-cap/asbuilt/core.sp",
    cell="lpf_core_H12pc",
    run_dir="build/signoff",
    pex_mode="CC",
)
print(res.ok, res.pex.per_net_c_ff if res.pex else None)
```

Live check on the prototype 5T OTA (research server): DRC 0 violations in ~25 s, LVS match in
~4 s, kpex CC in ~7 s, `vinp` 1.23 fF — `pytest -m slow packages/spicexplorer-signoff`.

## Tests

`packages/spicexplorer-signoff/tests/test_signoff_offline.py` (parsers, splice, injection,
flow verdicts — no tools) and `test_signoff_live.py` (`slow`; each test skips with the
missing capability as reason).

## Status / next

T0 of `doc/plan_layout_automation.md` (meta-repo). Not yet: Magic-DRC / netgen-LVS second
opinion as runners (the prototype scripts still do it), FasterCap engine, density/antenna
runs, a `postlayout.measure` that drives analog-db benches (composition → orchestration).
