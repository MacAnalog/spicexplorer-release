# spicexplorer-signoff

Physical signoff as a **library**: engine-agnostic **DRC / LVS / PEX** runners that return
structured verdicts (GDS in → verdict out), plus the two netlist-side helpers a post-layout
flow needs — splicing an extracted subckt into an existing bench deck, and injecting
parasitics / mismatch into a subckt to measure layout sensitivity (the primitive behind the
layout *brief*). One call — `run_flow(build, params, …)` — chains build → DRC → LVS → PEX for
any caller-supplied builder, which is exactly what an agent iteration or an optimizer trial
needs.

## Layering

Leaf tool: depends on `spicexplorer-core`, the `klayout` python wheel (the PDK's own
`run_drc.py` / `run_lvs.py` import it) and `docopt` (the IHP `run_lvs.py` parses its command
line with it). Both runners execute under `SIGNOFF_PYTHON`, which defaults to this interpreter.

The heavy tools — a `klayout` executable, `kpex`, the PDK
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
| `probe(pdk="ihp-sg13g2")` | `ToolProbe` (`drc_ok/lvs_ok/pex_ok`, tool paths) | cheap, launches nothing; `drc_ok` counts a `.lydrc` deck as a DRC deck |
| `run_drc(gds, topcell, run_dir, no_density=True, deck=None)` | `DrcResult` (`passed`, `n_violations`, `violations=[{rule,count,locations}]`, `report_path` .lyrdb, `deck`, `no_density`) | **Which deck:** the PDK's `run_drc.py`; on a checkout without it (IHP SG13G2 snapshots that ship only `drc/sg13g2_maximal.lydrc` and `drc/sg13g2_minimal.lydrc`) the first `.lydrc` deck present, maximal first, run as `klayout -b -r <deck> -rd in_gds=… -rd cell=… -rd report_file=…`. `deck=` picks one explicitly; `DrcResult.deck` names the deck that ran. **Pass:** `run_drc.py` prints `DRC Check Passed`; a `.lydrc` run needs `Number of DRC errors: 0`, its report written during this run, and exit 0. `no_density` drops the chip-level density rules (`--no_density`, or `-rd densityRules=false`). Paths are made absolute because `run_drc.py` changes directory |
| `run_lvs(gds, netlist, topcell, run_dir)` | `LvsResult` (`matched`, `unmatched`, `netlist_sha`, `reason`) | compares against the **certified** schematic netlist; the sha is in the verdict so a reviewer can prove which file. A mismatch is read from `Netlists don't match` (the IHP deck's `ERROR : Netlists don't match`, printed with exit 0 and no counts) or from unmatched counts; the IHP line sets `reason` to "the layout does not match the reference netlist <file>" and points at the `.lvsdb` in the run directory. Only a POSITIVE verdict passes: a runner that exits non-zero, writes no `<topcell>.log`, or leaves a log with no verdict line and no unmatched counts sets `reason` from the last lines of stderr, so a deck that stopped with an error (for example, the PDK's `run_lvs.py` cannot `import docopt` under `SIGNOFF_PYTHON`) is never reported as a mismatch with an empty reason. All three runners read their verdict **only out of files the current run wrote** (`run_dir` is never cleared, so a fix-and-retry loop leaves the previous good log/`.lyrdb`/PEX netlist behind) and tail whatever the tool managed to say before a timeout |
| `run_pex(gds, cell, schematic, out_dir, mode="CC", halo_um=None, ground_nets=())` | `PexResult` (`netlist_path`, `n_c/n_r`, `per_net_c_ff`, `coupling_ff`, `ground_nets`, `n_self`, `halo_um`) | kpex 2.5D; `CC` in loops (RC's R-mesh can dangle gate pins), `RC` for the final report; `halo_um` overrides the tech sidewall halo (kpex `--halo`) — couplings beyond the halo (IHP: 8 µm) are DROPPED, so raise it when a spacing sweep crosses it. **Ground:** `0`/`gnd`/`vss`/`vsubs` (`pex.GROUND_NETS`, any case) plus `ground_nets` (e.g. `("sub",)` when the substrate is a subckt pin) get no `per_net_c_ff` entry and are in no `coupling_ff` pair; C between one of them and a signal net counts as that net's C to ground. `PexResult.ground_nets` records the set applied. **Self-loops:** a C card with both terminals on one net (kpex writes e.g. `Cext_51 sub sub 23.0904f`) is skipped and counted in `n_self`, not in `n_c` |
| `pex.strip_mim_for_pex(gds_in, gds_out, layers=, topmetal_margin_um=)` / `pex.strip_cards(text)` | Path / text | **kpex has no `cap_cmim` support** (its IHP tech marks the MIM layer `<TODO>` and crashes): extract a MIM-stripped copy (default MIM + Vmim cleared, top plates cut back by 0.2 µm; `layers=` adds e.g. MemCap `(69,0)`, `topmetal_margin_um=None` keeps the plates as plain metal so their coupling still extracts) against a schematic without the `C` cards, then add the schematic MIM cards back for the benches |
| `run_flow(build, params, netlist=, cell=, run_dir=, pex_mode=, no_density=True, halo_um=None)` | `FlowResult` (`gds, drc, lvs, pex, stage_failed`) | stops at the first failing gate; a builder exception is a `stage_failed="build"` verdict. `no_density` goes to `run_drc` (a density-off clean DRC is conditional), `halo_um` to `run_pex`; each verdict records its own (`DrcResult.no_density`, `PexResult.halo_um`, `None` = the tech file's halo), so report both beside the numbers |
| `postlayout.prep_pex_subckt(pex, cell, rename=)` | text | `M`→`XM` cards (ngspice IHP devices are subckts), optional rename |
| `postlayout.extract_subckt / splice_subckt(deck, replacement, name)` | text | drop the extracted block into the block's own bench deck; pin lists must agree |
| `postlayout.to_lvs_reference(subckt, name, cell=)` | text | ngspice-style `X` subckt calls → the flat `M`/`C` cards the KLayout LVS deck reads (`w·m` combined, `ng` dropped, MIM `w/l/m` kept) |
| `postlayout.deltas(pre, post)` | `{key: {pre, post, delta, rel}}` | scorecard diff |
| `postlayout.score_c_budgets(pex, brief, exclude=)` / `postlayout.c_budget_table(rows)` | one row per `brief["nets"]` entry / Markdown | per-net extracted C against the layout brief's three budgets: **balanced** (`budget_c_ff`: C to every partner but the twin), **one-sided** (`budget_c_asym_ff`: `\|bal(net) − bal(twin)\|`), **differential** (`budget_c_diff_ff`: C between the twins only); `bal + diff` is the net's `summarize_parasitics` sum. Twin from the net's `twin`, else `structure.mirror_pairs`. `exclude=` is the caller's card-name regex(es) for the design capacitors spliced back into the extraction. A don't-care net (`dont_care` list, or its `capacitance` list), a net without a budget, and a net named nowhere in the extraction get `*_ok = None`, never a pass |
| `postlayout.select_pex_netlist(pex_dir, explicit=, record=)` | `MeasuredNetlist(path, kind, how, note)` | **which extracted netlist a scorecard measured**, as a provenance record to log beside the numbers. An RC run leaves a matched PAIR (`…_pex_netlist.spice` + `…_pex_netlist_stitched.spice`) and a `*_pex_netlist.spice` glob does **not** match the stitched name — so the naive rule found "exactly one", reported no ambiguity and silently scored the netlist whose resistor mesh is not in the circuit. Order: `explicit` > the PEX stage's own `signoff.json` record **only when the file it names is under `pex_dir`** (one run dir with a CC *and* an RC stage has ONE record, naming whichever wrote last) > the directory, where a matched pair is answered in favour of the stitched one with a note and anything else raises |
| `check_current_density(budgets, pdk="ihp-sg13g2")` | `CurrentDensityResult` (`violations=[{net,layer,current_a,limit_a,over_factor,rule}]`, `worst_over_factor`, `reason`, `skipped`) | pure arithmetic, **no GDS**: per net, the current it carries + the conductor it is drawn on → the over-factor. Nothing else in the chain checks electromigration (DRC sees legal geometry, LVS sees the same net, PEX sees milliohms), so a DRC-0/LVS-matched cell can be 12–28x over its metal limit. `Budget(net, current_a, layer, width_um=, n_vias=, note=)`; IHP SG13G2 limits from `SG13G2_os_process_spec.pdf` §2.15 (M1 1 mA/µm >0.36 µm, 0.36 mA flat 0.16–0.36 µm; M2–M5 2 mA/µm >0.3 µm, 0.6 mA flat; TopMetal1 15 / TopMetal2 16 mA/µm; Via1–4 0.4 mA/via). §2.15 gives the top metals no width band, so their floor is the rule deck's own minimum width (TM1.a 1.64 µm, TM2.a 2.00 µm) — a scored width is a *drawable* width. An unknown layer, a sub-qualified width (including an omitted one) or a via count below 1 is a FAILURE with a reason, never a silent pass; an empty `budgets` list is `skipped=True`, `passed=False`, `n_checked=0` with a reason (nothing was checked: not a pass and not a violation); `over_factor` is always finite so `to_dict()` is JSON-safe |
| `budgets_from_brief(brief, drawn)` | `[Budget]` | the layout brief's `currents` block (`net`, `i_ma`) on the conductors drawn: `drawn={net: (layer, width_um, n_vias)}` or a list of them per net; `current_a = i_ma·1e-3`. A brief net with no `drawn` entry becomes an unchecked (failing) budget; a `drawn` net the brief has no current for raises `KeyError`; a brief with no `currents` rows raises `ValueError` (an empty check is not a pass) |
| `current_density.limit_for(layer, width_um=, n_vias=, tech=)` / `current_density.limits(tech)` | `(limit_A, rule)` or `None` / the `{layer: LayerLimit}` table | one conductor's limit. The numbers are **configuration**: they come from `spicexplorer_core/techs/<pdk>.yaml` (`em_limits:`), so a second process is a second YAML file, not a second copy of the arithmetic. `tech=` takes a `Tech`, a builtin PDK name or a path; `pdk=` is the same argument under its older name |
| `sensitivity.inject_caps / inject_resistor / scale_param / inject_vsource / inject_isource` | text | perturb a subckt (C net→ref, pair, one-sided, balanced; series R; ×/+ a device param; series V on a device pin = ΔV_T; dc current into a node = leakage) |
| `sensitivity.sweep(subckt, name, measure, nets=, pairs=, c_ff=(1,10), r_nets=, params=, i_nets=, v_pins=)` | `(baseline, [SensRow])` | `measure(text) -> {metric: value}` is the campaign's harness; rows carry `delta` and `per_unit` |
| `sensitivity.find_mos_cards(block, family=, drain=, gate=, source=, prefix=)` | `[card name]` | on an **extracted** block the design's device names are gone — every MOS is `XMn_<k>` — but the nets survive, because a generator names them after the certified netlist. Finds a device class by connectivity; `family` matches the model name's suffix, so the caller names the class, not one PDK's model string. A device drawn as several half-width cards returns several names: assert the count you expect |
| `sensitivity.inject_threshold_offset(subckt, name, cards, dvt_v, pin="g")` | text | `+dvt_v` of threshold voltage on every card of one device. `inject_vsource` makes the pin see `net + dv`, so a threshold INCREASE is a **negative** gate source — the sign lives here once rather than in each caller, because getting it backwards reports the safe direction as the dangerous one |
| `sensitivity.filter_caps(block, keep=, drop=, prefix="Cext")` | `(text, kept, dropped)` | the what-if that measures which extracted capacitance actually costs the metric. Nothing else in the block moves, so the difference between two runs is exactly the capacitance named. Re-inserted devices are `X` calls, so they always survive |
| `sensitivity.insert_series_return(block, net, ohm, kelvin=)` | `(text, cards_moved)` | a CC extraction carries no wire resistance at all, so every metric it produces assumes an IDEAL return. Renames `net` to `<net>_ret` inside the block (the header pin and the Kelvin-returned devices excepted) behind one resistor: `ohm` is the COMMON series element a return-path budget is written on |

CLI: `spicexplorer-signoff [--pdk P] probe | drc GDS --cell C --run-dir D [--density] | lvs GDS --cell C --netlist N --run-dir D | pex GDS --cell C --netlist N --out-dir D --mode CC [--halo UM] | current-density --budgets FILE [--tech T]` — JSON verdict on stdout, exit 0/1. `--budgets` is a JSON list of `Budget` rows (`net`, `current_a`, `layer`, `width_um`, `n_vias`, `note`) or `{"budgets": [...]}`; `--tech` defaults to `--pdk`; a malformed file (bad JSON, unknown or missing keys, a field of the wrong type) or an empty one exits 2.

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

## Notebook

[`notebooks/signoff_tour.py`](notebooks/signoff_tour.py) (marimo) reads each verdict on the committed
fixtures, offline: `parse_lyrdb` and `run_drc` on a recorded `.lyrdb` report, `run_lvs` on the recorded
IHP mismatch log, `summarize_parasitics` / `scan_parasitics` on the kpex-shaped netlists, and
`check_current_density` / `budgets_from_brief`. Short Python scripts stand in for KLayout and the LVS
runner and replay the recorded output. `tests/test_notebooks.py` runs it.

## Tests

| file | what it checks | tools |
|---|---|---|
| `tests/test_signoff_offline.py` | parsers, splice, injection, flow verdicts | none |
| `tests/test_drc_lydrc.py` | DRC with a `.lydrc` deck when the PDK has no `run_drc.py` (#277); a report left in `run_dir` by an earlier run is not read | none; a script stands in for `klayout` |
| `tests/test_lvs_verdicts.py` | the IHP LVS match and mismatch lines, on a recorded log (#278) | none |
| `tests/test_pex_ground_nets.py` | `run_pex(ground_nets=…)`, `PexResult.ground_nets` / `n_self` (#281); `sub` as ground on the recorded PAM-4 driver extractions | none; a script stands in for kpex; the PAM-4 test reads the analog-db submodule and skips without it |
| `tests/test_signoff_live.py` | the runners on real GDS files (`slow`) | klayout, the PDK, kpex; each test skips with the missing one as its reason |

## Status / next

T0 of `doc/archive/plan_layout_automation.md` (meta-repo). Not yet: Magic-DRC / netgen-LVS second
opinion as runners (the prototype script that did it was retired in the 2026-09 close-out),
FasterCap engine, density/antenna runs, a `postlayout.measure` that drives analog-db benches
(composition → orchestration).
