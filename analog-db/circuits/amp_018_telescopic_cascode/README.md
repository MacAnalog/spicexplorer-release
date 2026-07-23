# amp_018_telescopic_cascode — Telescopic (cascode) OTA, the NEWCAS 2026 design

> ⚠️ Sizing under active revision (2026-06-13); sky130/gf180 figures below may be stale — see
> the committed `results/*.json` for current values. As committed: `ihp-sg13g2__tt.json` runs
> (ac/dc_op/noise/tran ok), `gf180mcu__tt.json` is all `sim_error`, and there is no
> `results/sky130__tt.json` yet.

The research design behind the NEWCAS 2026 submission (legacy `examples/OTA/cascode/`,
aliases `CASCODE-OTA` / `ota-improved`). NMOS input pair with NMOS cascodes, PMOS
mirror load with PMOS cascodes, NMOS tail + mirror reference, ideal cascode gate-bias
sources (`x_dut_v_bias_1/2` — themselves optimized knobs).

## Layout highlights
- `abstract/netlist.spice` — AUTHORED clean core (10 MOS + 2 bias V-sources). The legacy
  enable/power-down network, decoupling devices, and Vmeas ammeters live only in
  `pdk/ihp-sg13g2/netlist.legacy.spice` (the real, runnable artifact). The legacy DUT's
  `X_DUT_M3PCM4C_L` typo is normalized to `x_dut_m3cm4c_l` (what the testbenches simulate).
- `pdk/ihp-sg13g2/testbenches.legacy/` — the five NEWCAS testbenches **verbatim**
  (ac, loopgain, noise, tran, linearity; each embeds its own DUT copy and runs standalone).
- `artifacts/newcas2026/` — the paper's optimization traces, **preserved verbatim**
  (CSVs, draw notebooks, vector PDFs/SVGs).
- `results/newcas2026_best.json` — the best run (LhsDE, score 48.34: 49.3 dB, UGF 528 MHz,
  PM 69°) distilled; its sizing is the `sizing.yaml` defaults.
- `analyses/linearity.yaml` — the distilled ICMR sweep, scaffolded but `enabled: false`
  (Tier 2 assembles it; the runner skips it until thresholds are reviewed).
- `pdk/sky130/`, `pdk/gf180mcu/` — the retarget bindings (multi-PDK proof on a real design;
  defaults are the ihp point carried over, NOT re-optimized). These are committed lowering-ready
  but don't yet yield meaningful sky130/gf180 baselines at the IHP-tuned geometry — they need
  gm/ID re-sizing (Phase 6); see `_shared/PDK_SIM.md`.
- `optimizer/projection.yaml` → GENERATED `project_setup.yaml` (the optimizer view; must
  reproduce the committed NEWCAS baseline — the P3 regression gate).
