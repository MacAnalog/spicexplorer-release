# 5T OTA — gdsfactory lane (`ihp-gdsfactory` PDK)

The `amp_001_5t` 5T-OTA generated with **gdsfactory + the
[ihp-gdsfactory](https://github.com/gdsfactory/ihp) PDK**: the reference generator of the
`spicexplorer-layout` contract. An earlier foundry-PyCell prototype of the same circuit, and the
stand-alone signoff / PEX / optimization scripts that drove both, were retired in the 2026-09
close-out (see [`../README.md`](../README.md)); `spicexplorer-signoff` and the optimizer's layout
backend do their jobs.

**Signoff:** KLayout DRC (no density rules) 0 violations and KLayout LVS "Netlists match"
through `spicexplorer-signoff`. In the July prototype a Magic DRC + netgen LVS second opinion
also passed on this GDS (Magic DRC 0, netgen "match uniquely").

## Why this lane exists (what gdsfactory buys you)

| | foundry-PyCell prototype (retired) | gdsfactory lane (this dir) |
|---|---|---|
| Device terminals | reverse-engineered (cluster Metal1 boxes by x) | **named `S`/`D`/`G` ports** on every device |
| Placement | hardcoded x-offsets on one long row | **computed**: 3 function rows, mirrored pairs about x=0, y from live bboxes |
| Matching | none (M1..M6 in a strip) | M1\|M2 and M3\|M4 are true geometric mirror pairs |
| Routing | hand-computed Metal2 trunks | port-driven; `gf.routing.route_single` for the manhattan nets |
| Area (core bbox) | ~50 x 14 um (~700 um2) | **205.9 um2** (232.1 hand-tuned, then optimized) |
| Wire parasitics (kpex RC) | 462 R segments | **152 R segments** |
| Post-layout UGF penalty | **-4.45 MHz** | **-0.72 MHz** (6x less) |

The UGF numbers were measured in July by the prototype's pre/post-layout compare (open-loop AC,
amp_001_5t `ac_open_loop` bench: VDD=1.5, VCM=0.8, IBIAS=20u, CL=50f, ngspice `mos_tt`); the same
bench is now [`opt/tb_ac.spice`](opt/tb_ac.spice), run pre- and post-layout by the layout backend
(parity table in [`opt/README.md`](opt/README.md)):

```
July 2026 record
pre-layout                 : dc_gain = 29.78 dB   ugf = 30.146 MHz   pm = 61.4 deg
gdsfactory lane            : dc_gain = 29.78 dB   ugf = 29.421 MHz   pm = 61.9 deg   (-0.73 MHz)
PyCell prototype (retired) : dc_gain = 29.78 dB   ugf = 25.693 MHz   pm = 64.0 deg   (-4.45 MHz)
```

Placement symmetry also shows up in the extracted parasitics:
`Cext(vinp->tail) = 34.6 aF` vs `Cext(vinn->tail) = 34.8 aF`.

## The committed `LayoutParams` (a July layout search)

Because the placement is fully parameterized (`LayoutParams`), the layout can be
*optimized against the real toolchain*: every candidate is generated, DRC+LVS **hard-gated**,
kpex-extracted and ngspice-simulated. In July a stand-alone nevergrad loop (now retired;
[`opt/`](opt/) below is the platform form of the same search) scored `area/area_0 +
ugf_loss/loss_0` over the 9 clearance/width constants.

The committed `LayoutParams` defaults ARE that search's winner (2x30 trials,
2026-07-09): **232.1 -> 205.9 um2 (-11.3%)** with the UGF penalty also slightly
improved (0.726 -> 0.717 MHz) — mostly by compacting the row channels (`ch_y`
1.8 -> 0.92) while *widening* `gap_x`/`vdd_off` to protect the error term.
In-loop PEX uses kpex `--mode CC` (validated identical UGF loss to RC on this
block): the 2.5D R-mesh occasionally leaves a pin node dangling on the tiny gate
nets, which makes ngspice's matrix singular — C-only extraction sidesteps that
entirely. Failed candidates (DRC `Cnt.g1`/`M1.a` at tight `edge_x`/`w_m1`) are
penalized, which is how the optimizer finds the legal boundary.

## Layout optimization THROUGH the platform optimizer (`opt/`)

The same search, expressed as an ordinary `spicexplorer` project (`sim_engine: layout`) instead
of the stand-alone script — see [`opt/README.md`](opt/README.md):

```bash
cd opt && uv run spicexplorer-optimize project_setup.yaml --budget 20
```

`opt/flow.yaml` (`layout-flow/1`) describes one trial — build → KLayout DRC → LVS → kpex CC →
**the platform's own `tb_ac.spice` on the extracted subckt** (`postlayout:`) — and
`opt/project_setup.yaml` scores `area_um2` (minimize) plus `ugf`/`pm`/`dcgain` measured by the
Tier-1 registry on the post-layout AC waves, gated by `drc_pass`/`lvs_match`/`pex_ok`. Trial 0 is
the committed `LayoutParams` (`seed_from_init`), so the run starts from the layout of record. The
`gen_5t_ota_gf.write_lvs_reference(p, sizing=, out=)` writer regenerates the LVS reference for a
sizing+layout co-optimization.

## Layout ↔ schematic **co-optimization** (`coopt/`)

[`opt/`](opt/) above tunes the layout around a *frozen* sizing. [`coopt/`](coopt/) is
the next step: **one** platform `Project_Setup` whose `dut_params` carry the device widths
**and** the `LayoutParams` knobs, searched together by the layout backend
(`sim_engine: layout`, `spicexplorer.backends.layout`).

| file | role |
|---|---|
| [`coopt/flow.yaml`](coopt/flow.yaml) | the `layout-flow/1` recipe: generator · DRC · LVS · kpex CC · post-layout AC. The co-optimization seam is `sizing: sizing.json` + `sizing_params: [in_w, pld_w, tail_w]`. |
| [`coopt/sizing.json`](coopt/sizing.json) | the FULL baseline sizing dict (µm) the candidates overlay — `build(params, sizing)` needs every key. |
| [`coopt/project_setup.yaml`](coopt/project_setup.yaml) | the project: 3 sizing params + 6 layout knobs, objective `area_um2`, constraints `ugf ≥ 32 MHz` / `dcgain ≥ 30 dB` / `pm ≥ 55°`, gates `drc_pass`/`lvs_match`/`pex_ok`/`postlayout_ok`. |
| [`coopt/ota_5t_gf_dut.spice`](coopt/ota_5t_gf_dut.spice) | the **parameterized** pre-layout DUT (`w={in_w*1e-6}` — the sizing dict is in µm, and `u` after a brace expression is not a multiplier in ngspice). |
| [`coopt/tb_ac.spice`](coopt/tb_ac.spice) | the open-loop AC bench, declaring the global `.param`s the backend rewrites per candidate. |
| [`coopt/coopt_helpers.py`](coopt/coopt_helpers.py) | notebook glue: capability probe, trial table from the crash-safe checkpoints, per-net C table, replay save/load. |
| `coopt/coopt_replay.json` | committed numbers so the guide notebook still renders where the toolchain is absent. |

Per candidate the backend overlays the sizing params onto `sizing.json` (a per-run
`sizing.json` → `build(params, sizing)`), hands the merged dict to
`gen_5t_ota_gf.write_lvs_reference` so the LVS reference follows the sizing — a fixed
reference would make every LVS verdict a lie once widths are searched — and injects them as
`.param <name>` into the post-layout deck.

```bash
cd coopt
GDS_PYTHON=~/miniconda3/envs/ai_env/bin/python \
  uv run spicexplorer-optimize project_setup.yaml --budget 12
```

The narrated walkthrough (pre-layout baseline → one post-layout evaluation with the per-net
C table → a live campaign → the area-vs-UGF trade and the winning layout) is the guide
notebook [`packages/spicexplorer/notebooks/layout_schematic_cooptimization.py`](../../../../packages/spicexplorer/notebooks/layout_schematic_cooptimization.py) (a marimo notebook).
Budget in wall time, not trials: one trial here is ~40 s, over half of it KLayout DRC.


## Floorplan

```
   vdd bar ──────────────────────────────
   [ntap]  M3 →|  |← M4   [ntap]     row P   (mirror load, shared NWell)
            ── outm strap / gates ──         channel
   [ptap]  M1 →|  |← M2   [ptap]     row N1  (input pair, S inward -> tail)
            ── vinp / vinn taps ──           channel
   [ptap]  M6 |    | M5   [ptap]     row N0  (bias ref + tail)
            ── ibias strap ──
   vss bar ──────────────────────────────    (+ vss rails at both edges)
```

Nets: intra-row on Metal1; `vout` (M4.D -> M2.D) on Metal2 so it crosses the `outm`
strap legally; `tail` drops through the kept-clear center channel. Taps ride the vss
rails next to every nmos row, so LU.b (20 um latch-up) holds by construction.

## Run it

```bash
python gen_5t_ota_gf.py                  # -> ota_5t_gf.gds (an interpreter with gdsfactory +
                                         #    ihp-gdsfactory: the `gds` extra, or ai_env)
uv run spicexplorer-signoff drc ota_5t_gf.gds --cell ota_5t_gf --run-dir signoff_out/drc
uv run spicexplorer-signoff lvs ota_5t_gf.gds --cell ota_5t_gf \
    --netlist ota_5t_gf_lvs.spice --run-dir signoff_out/lvs       # DRC 0 / LVS match
uv run spicexplorer-signoff pex ota_5t_gf.gds --cell ota_5t_gf \
    --netlist ota_5t_gf_lvs.spice --out-dir pex_out --mode CC     # kpex 2.5D, per-net C
./open_in_klayout.sh                     # view/tweak in the KLayout GUI (IHP colors)
```

Each `spicexplorer-signoff` command prints its verdict as JSON and exits 0 on a pass; it makes
the paths absolute itself (the PDK runners change directory). The pre- vs post-layout AC
comparison is one layout-flow trial: see [`opt/README.md`](opt/README.md).

## Files

| File | Role |
|---|---|
| `gen_5t_ota_gf.py` | Generator: row/mirror placement engine + port-driven routing; `write_lvs_reference` for co-optimization. |
| `ota_5t_gf_lvs.spice` | Flat LVS reference (primitive `M` cards; topcell `ota_5t_gf`). |
| `opt/` | The layout optimization **through the platform optimizer** (`sim_engine: layout`): `flow.yaml` (layout-flow/1), `project_setup.yaml`, `tb_ac.spice` + `ota_5t_gf_dut.spice` (the post-layout bench + schematic sim DUT), `README.md`. |
| `coopt/` | Sizing + layout co-optimization (see above). |
| `open_in_klayout.sh` | Open `ota_5t_gf.gds` in the KLayout GUI (edit mode + IHP colors). NOTE: no live PCells in this lane — the ihp-gdsfactory cells are baked geometry; for W/L/nf changes edit `SIZING` and regenerate. |

## Gotchas found in `ihp-gdsfactory` 0.2.7 (worth re-checking on upgrade)

- **`via_stack` Via1 is DRC-illegal**: its `VIA_RULES["Via1"]` size is 0.26 um but sg13g2
  V1.a requires exactly 0.19x0.19 — and for small `size=` values the via is *silently
  dropped* (a floating M1/M2 sandwich). The generator draws M1->M2 vias explicitly.
  GatPoly->Metal1 (`Cont`) via stacks are correct.
- **PyPI name is `ihp-gdsfactory`** (the PDK-vendored README says `ihp-gdfactory` — typo).
  Version 2.0.0 needs Python >= 3.12; **0.2.7 installs on py3.11** and is what `ai_env` has.
- Installing it downgrades `protobuf` (via `vlsir`); `pip install "protobuf>=6.32,<7"`
  afterwards restores langgraph/grpcio compatibility — only unused `vlsir` complains.
- Device ports sit on **pin layers** (`Metal1pin` 8/2); `gf.routing` wants drawing-layer
  ports — copy them onto `Metal1drawing`/`Metal2drawing` before routing (see `via12`/
  `route_single` usage in the generator).
- `ntap1`/`ptap1` have a **min width of 0.78 um**, and (unlike the foundry `ptap1`
  PyCell) extract as plain ties, not resistor devices — safe for LVS.
- Installing it **breaks the foundry PyCells** (`sg13g2_pycell_lib`) in the same interpreter
  unless handled: the wheel vendors an incompatible copy of `cni` into site-packages as a
  *regular* package, which shadows the PDK's *namespace*-package `pycell4klayout-api` on import
  (regular beats namespace at any sys.path position; its `cni.dlo` lacks `List`). A script that
  loads the PyCells must bind `cni` to the PDK's directory explicitly first (the retired PyCell
  prototype's bootstrap did). The vendored copy is unused by `ihp` itself.
