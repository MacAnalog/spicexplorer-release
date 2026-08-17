# 5T OTA layout optimization — through the platform optimizer

The gdsfactory-lane 5T OTA (`../gen_5t_ota_gf.py`) optimized "the platform way": an ordinary
`spicexplorer` project whose DUT parameters are the generator's 9 layout knobs and whose one
testbench is the **layout flow** — `sim_engine: layout` selects
`spicexplorer.backends.layout` in the backend factory; Nevergrad, checkpoints, reports and the
UI's replay are the standard path. This replaces the stand-alone `../optimize_layout.py` loop
for the platform lane (that script stays as the deterministic reference).

```bash
cd examples/layout/ihp-sg13g2/5t_ota_gf/opt
uv run spicexplorer-optimize project_setup.yaml --budget 20          # TwoPointsDE over the 9 knobs
uv run spicexplorer-optimize project_setup.yaml --budget 1 --outdir /tmp/ota_base   # budget 1 + seed_from_init = the layout of record
```

Requirements: a gdsfactory interpreter (`GDS_PYTHON`, default in `flow.yaml`:
`~/miniconda3/envs/ai_env/bin/python`), `klayout` + `kpex` (the signoff package's discovery /
fallbacks), `ngspice` on `PATH`, `PDK_ROOT` (default `~/local/pdks`). Install the optimizer's
`layout` extra: `uv sync --extra layout` (workspace) — it just pulls the two leaf tools.

## Files

| File | Role |
|---|---|
| `flow.yaml` | `layout-flow/1`: generator + cell, `gds_python`, DRC, LVS (fixed reference `../ota_5t_gf_lvs.spice`), kpex `CC` (`ac_gnd_nets` → `c_<net>_ff` = C to AC ground), **`postlayout:`** (the platform testbench below on the extracted subckt), gates. |
| `project_setup.yaml` | The project: 9 `dut_params` (= `BOUNDS`, `init` = the committed defaults), testbench `layout` (`netlist: flow.yaml`), target specs, `seed_from_init: true`. |
| `tb_ac.spice` | The post-layout bench: the amp_001_5t `ac_open_loop` conditions (VDD 1.5, VCM 0.8, IBIAS 20 µA, CL 50 fF, `mos_tt`), `.op` + `.ac`; `.include`s the schematic DUT. |
| `ota_5t_gf_dut.spice` | The schematic DUT for simulation (`XM` cards; same `.subckt ota_5t_gf` pins as the LVS reference). Per trial the flow swaps this include for `dut_postlayout.spice`. |

## What one trial does

```
build (gdsfactory, gds_python) → KLayout DRC → KLayout LVS → kpex 2.5D CC
  → dut_postlayout.spice (extracted subckt, header = the schematic DUT's `.subckt ota_5t_gf vdd vout vinp vinn ibias vss`)
  → tb_ac.spice with `.include ota_5t_gf_dut.spice` → `.include <run>/dut_postlayout.spice`, run by NGSpice_Wrapper
  → summary.json (= the trial's log_file) + scalars
```

Target specs (all through the `layout` testbench):

| spec | reads | goal |
|---|---|---|
| `area_um2` | the flow's own scalar (bbox area) | minimize, target 232.1, `reward_type: log` (monotonic below the target — `relative-log` rewards *proximity* to the target and would mis-rank a minimize objective) |
| `ugf` / `pm` / `dcgain` | Tier-1 registry recipes `{meas: ugf\|pm\|dcgain, out: v(vout)}` on the **post-layout** AC waves — `LayoutSimResult.wave` delegates to the inner `tb_ac` ngspice result | exceed 29 MHz / 55° / 29 dB |
| `drc_pass`, `lvs_match`, `pex_ok`, `postlayout_ok` | flow verdicts (1/0; NaN when the stage did not run) | exact 1 |

DSL spellings: `m >= T` → `goal: exceed`; `m <= T` → `goal: minimize` (with `reward_type: none`
it is a pure bound); `m == T` → `goal: exact, tolerance: 0`. A stage that fails (DRC hits, LVS
mismatch, kpex error) skips the downstream stages: their scalars read NaN → `MAX_PENALTY` on
those specs, while `area_um2` still scores. If several post-layout testbenches exist, a name may
be qualified `<tb>:<name>` (e.g. `tb_ac:i(vdd)`); unqualified names search them in spec order.

## Parity (defaults, this host, 2026-08-16)

| | dcgain | UGF | PM | area |
|---|---|---|---|---|
| pre-layout (schematic DUT, `LayoutSimulator.run_prelayout_reference`) | 29.77 dB | 30.145 MHz | 61.5° | — |
| post-layout (kpex CC, this flow) | 29.78 dB | 29.447 MHz | 61.9° | 205.9 µm² |

UGF loss 0.70 MHz — the figure `../sim_pex_compare.py` / `../optimize_layout.py` report for the
committed defaults. One trial ≈ 35–70 s (KLayout DRC dominates).

## Co-optimization (sizing + layout)

`flow.yaml` accepts `sizing_params: {<dut_param>: <sizing key>}`: those `dut_params` are routed
into `build(params, sizing)` (a per-run `sizing.json` overlay), the LVS writer
(`lvs: {writer: write_lvs_reference}` — `gen_5t_ota_gf.write_lvs_reference(p, sizing=, out=)`)
and the post-layout decks' `.param`s, so device W/L and layout knobs are searched together in one
project. A worked co-optimization project is the follow-on (`../coopt/`).
