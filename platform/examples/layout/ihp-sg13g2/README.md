# IHP sg13g2 layout generation — the 5T OTA reference generator

Programmatic **layout generation + physical signoff + parasitic extraction** for IHP
`sg13g2`, driven from Python through the platform packages **`spicexplorer-layout`**
(generator contract, `GdsBuilder`, patterns, headless render) and **`spicexplorer-signoff`**
(DRC/LVS/PEX runners with structured verdicts, `run_flow`, post-layout splice, sensitivity
injection). The worked example is a rough **5T OTA** (`amp_001_5t` from the `analog-db`
submodule) generated with `gdsfactory` + [`ihp-gdsfactory`](https://github.com/gdsfactory/ihp):
[`5t_ota_gf/gen_5t_ota_gf.py`](5t_ota_gf/gen_5t_ota_gf.py) follows the generator contract
(`build(params, sizing=None)`, `CELL`, `BOUNDS`) and is the reference generator;
`run_flow(GdsBuilder(...), {})` gives DRC 0 / LVS match / a kpex-CC extraction end to end.

| Dir | What |
|---|---|
| [`5t_ota_gf/`](5t_ota_gf/) | the generator (computed rows + mirrored pairs, port-driven routing), its flat LVS reference, a KLayout GUI launcher |
| [`5t_ota_gf/opt/`](5t_ota_gf/opt/) | the layout knobs searched **through the platform optimizer** (`sim_engine: layout`): DRC/LVS/PEX gates + the post-layout AC bench as target specs |
| [`5t_ota_gf/coopt/`](5t_ota_gf/coopt/) | layout ↔ schematic **co-optimization** (device widths and layout knobs in one project), walked through by the guide notebook `packages/spicexplorer/notebooks/layout_schematic_cooptimization.py` |

The compact, symmetric floorplan keeps the post-layout UGF penalty at **−0.72 MHz** (the strip
layout of an earlier foundry-PyCell prototype lost 4.45 MHz), and the in-loop layout search took
the core from 232.1 to **205.9 µm²** (−11.3 %) with the error term also improved; see
[`5t_ota_gf/README.md`](5t_ota_gf/README.md) for the comparison.

**Retired in the 2026-09 close-out** (still in git history): the July prototype scripts (a kpex
wrapper, a pre/post-layout AC compare, KLayout and Magic+netgen signoff wrappers, a stand-alone
nevergrad layout loop and its walkthrough notebook) and the foundry-PyCell lane. Their jobs are
done by `spicexplorer-signoff` (DRC / LVS / PEX), the optimizer's layout backend
(`spicexplorer.backends.layout`: the layout loop, and the pre-layout reference run of the same
bench through `LayoutSimulator.run_prelayout_reference`) and the gdsfactory generator.

## Tools

DRC/LVS run through the PDK's own decks via a working `klayout` executable (`spicexplorer-signoff`
finds the decks under `PDK_ROOT` and runs `run_drc.py` / `run_lvs.py`, or a `.lydrc` deck when the
PDK ships no `run_drc.py`). On the research server that executable is the no-root
`~/local/klayout-runtime` shim; [`INSTALL.md`](INSTALL.md) records how the toolchain was set up
there. The generator needs `gdsfactory` + `ihp-gdsfactory` (the layout package's `gds` extra, or
the `ai_env` conda env on the research server).

## Parasitic extraction (PEX) — klayout-pex

Open-source PEX for sg13g2 works via **[klayout-pex](https://github.com/iic-jku/klayout-pex)**
(`kpex`), the KLayout-integrated extractor with first-class IHP support (the PDK even ships
the process stack as `libs.tech/parasitics/itf/sg13g2_typ.itf`). It runs KLayout LVS
internally for connectivity, then extracts coupling/ground **C** and wire **R** (modes
`CC`/`RC`/`R`; engines: built-in 2.5D — used here — plus optional FasterCap/magic).
`spicexplorer_signoff.run_pex` (CLI `spicexplorer-signoff pex`) drives it; the commands are in
[`5t_ota_gf/README.md`](5t_ota_gf/README.md) ("Run it").

The PEX netlist keeps the six `sg13_lv_*` devices (with layout-accurate `AS/AD/PS/PD`) and
adds the parasitic network; `spicexplorer_signoff.postlayout.prep_pex_subckt` rewrites the `M`
cards to `XM` cards (ngspice's sg13 devices are subcircuits), and the layout backend's
`postlayout:` stage runs the amp_001_5t `ac_open_loop` bench on the extracted subckt.

PEX notes / gotchas:

- kpex drives the **KLayout executable's** Ruby LVS engine, and its deck needs **Ruby ≥ 2.6**
  — the rpm-shim batch klayout (Ruby 2.5) fails with a syntax error. Point
  `KPEX_KLAYOUT_EXE` at a KLayout with Ruby ≥ 2.6; unset, `spicexplorer-signoff` falls back to
  `~/local/klayout-py311/klayout-batch.sh` (the research server's py3.11 source build, Ruby 2.7).
- **Magic-native RC extraction stays a dead end** here: magic reads the GDS (DRC works)
  but extracts no `fet` devices from the generated geometry, and the PDK's
  `ihp-sg13g2-extract.tech` has no `cifinput` section (it's for magic-native databases).
  kpex sidesteps magic entirely.
- FasterCap (3D field-solver accuracy) is a drop-in engine upgrade later.

## Docs and files in this folder

- [`INSTALL.md`](INSTALL.md) — how the full toolchain (KLayout ×2, magic, netgen, PDK, python
  env) was set up on the EDA server, with reproduction steps and verification.
- [`KLAYOUT_CHEATSHEET.md`](KLAYOUT_CHEATSHEET.md) — KLayout GUI shortcuts + the PyCell-editing
  workflow.
- [`em_sim.yaml`](em_sim.yaml) — an annotated EM solver setup for
  `spicexplorer_layout.em.EmSim.from_yaml()`.

## What "passing DRC" means here

`run_drc` runs DRC with `no_density=True` by default: the layout is **geometrically clean** (0
spacing/width/enclosure/latch-up violations). The full deck additionally flags metal/active/poly
**fill** and **min-density** rules (`M*Fil.h`, `AFil.g`, `GFil.g`, `M*.j`, `TM*.c`) — these are
satisfied by chip-level fill insertion at full-chip assembly, not on a standalone block, so
they are deferred (standard practice).

## Design notes / gotchas (hard-won)

- **LU.b latch-up:** every nmos must be within 20 µm of a p-substrate tie — the generator
  rides the taps on the vss rails next to every nmos row.
- **LVS net labels** must be `Text` on **Metal2.text (10/25)** (or 8/25 for M1), and only the
  6 real ports should be labelled (labelling an internal net promotes it to a pin).
- **LVS reference** must use primitive `M` cards, not the `XM* … sg13_lv_nmos` subckt-instance
  form of the analog-db lowered netlist (that reads as a call to an undefined subcircuit).
- **Foundry PyCells** (from the retired PyCell prototype): the `pmos` PyCell returns 4 Metal1
  boxes (two stacked per finger); the `ptap1`/`ntap1` PyCells extract as *resistor devices* and
  pollute LVS, so bulk ties there were raw diffusion taps (Activ + pSD + Cont + Metal1). The
  PyCells need Python ≥ 3.11, which the stock KLayout GUI does not embed (see the cheatsheet).

## Status

The flow runs **netlist → layout → DRC/LVS → PEX → post-layout sim → optimizer** through the
platform packages: `spicexplorer-signoff`, `spicexplorer-layout` and the optimizer's layout
backend (`opt/`, `coopt/`). The placement engine and channel router the prototype listed as next
steps are not planned (`spicexplorer-layout`'s `patterns.*` are helpers). Still open: the
FasterCap engine for kpex, magic-native extraction, and upstreaming the `ihp-gdsfactory` Via1 bug
report (see the gotchas in [`5t_ota_gf/README.md`](5t_ota_gf/README.md)).
