# AnalogGym LDO corpus — provenance

Source material for the three **verifiable** `analoggym_*` LDO circuits (unlike the
`ferrosim_*` corpus these are fully lowered + simulated, so each circuit keeps its
own upstream files under `circuits/<id>/reference/`; this file records the
corpus-level story and licenses).

## Upstream repositories

1. **CODA-Team/AnalogGym** (`https://github.com/CODA-Team/AnalogGym`), BSD-3-Clause
   (see [LICENSE.AnalogGym](LICENSE.AnalogGym)). The "Low Dropout Regulator"
   category ships the `Basic_LDO` netlist (`spice_netlist/LDO_netlist.txt`), per-design
   testbenches, design-variable lists, and the `perf_extraction_LDO.py` methodology.
   A local snapshot lives in the meta-repo at `external/AnalogGym-remainder/`.
2. **ChrisZonghaoLi/sky130_ldo_rl** (`https://github.com/ChrisZonghaoLi/sky130_ldo_rl`),
   Apache-2.0 (see [LICENSE.sky130_ldo_rl](LICENSE.sky130_ldo_rl)) — the repo the
   AnalogGym RGNN_RL example is built on. Its committed testbench flattens carry the
   actual `ldo` (= AnalogGym's *ldo_simple*) and `ldo_folded_cascode` subcircuits.

## Imported circuits

| DB circuit | Upstream design | Netlist source |
|---|---|---|
| `ldo_001_analoggym_basic` | `Basic_LDO` (aliases `LDO_1`) | AnalogGym `spice_netlist/LDO_netlist.txt` |
| `ldo_003_analoggym_simple` | `ldo_simple` / `ldo` | sky130_ldo_rl `python/simulations/ldo_tb.spice` |
| `ldo_002_analoggym_folded_cascode` | `ldo_folded_cascode` | sky130_ldo_rl `python/simulations/ldo_folded_cascode_tb.spice` |

## The missing designs: `ldo_1` and `ldo_2`

AnalogGym's LDO category *names* four variant designs (`ldo_simple`, `ldo_1`,
`ldo_2`, `ldo_folded_cascode`) via testbenches, design-variable lists and op-point
extraction scripts — but **their circuit netlists were never published**: every
`ldo_*_acdc.cir` testbench does `.include ../simulations/ldo_<name>.txt`, a
directory that exists in no revision of the repository (verified against the full
git history on 2026-07-03: the only netlist files ever committed under
`spice_netlist/` are `LDO_1.txt` and `LDO_netlist.txt`, both revisions of
`Basic_LDO`). `ldo_simple` and `ldo_folded_cascode` were recovered from
sky130_ldo_rl (above); `ldo_1` (9 FETs, current-biased) and `ldo_2` (~21 FETs)
exist nowhere we could find and are **not** imported — reconstructing them from
their variable names alone would be guesswork, not an import.

## Import conventions

Upstream designs are sky130-native. Each DB circuit folds the upstream external
pins (Vref / Vfb / bias voltages or currents) into internal ideal sources to meet
the LDO class's 3-port `[vdd, vout, vss]` DUT convention; the transistor topology,
role-encoded design-variable names, and m-multiplier arithmetic are preserved
verbatim. sky130 bindings carry the upstream default sizing and native device
flavors (`01v8` for Basic_LDO; 5 V `g5v0d10v5` for the two sky130_ldo_rl designs);
ihp-sg13g2 / gf180mcu bindings are `add-binding` transfers with per-PDK bias/
reference retuning documented in each circuit's README.
