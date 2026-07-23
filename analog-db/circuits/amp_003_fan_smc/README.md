# amp_003_fan_smc — 3-stage OTA, SMC compensation

Imported from CODA-Team/AnalogGym `Amplifier/.../Fan_SMC_Pin_3` (BSD-3-Clause) by `analog-db import-analoggym`. Compensation scheme + source: Fan, Mishra, Sanchez-Sinencio, IEEE JSSC 40(3):584-592, 2005.

- `abstract/netlist.spice` — PDK-neutral (sky130→nmos/pmos), canonical ports, role-encoded
  design-variable symbols preserved.
- `pdk/sky130/sizing.yaml` — the AnalogGym design variables (W/L/M + compensation passives).
- `datasheet.yaml` — extract-only benchmark specs (skill §6); per-topology CLoad from the
  AnalogGym design_variables. Lowers to all three PDKs (`ihp-sg13g2`/`sky130`/`gf180mcu`) and
  runs an **AC-only unoptimized baseline** (`results/<pdk>__tt.json`: only `ac_open_loop`;
  `dc_op`/`noise`/`tran_step` are disabled, and some DC gains are still negative/unoptimized).
  Matrix + caveats in `_shared/PDK_SIM.md`.

## FOUNDRY-n65 binding (Spectre; gm/ID re-sized 2026-07-22)

The `pdk/FOUNDRY-n65` binding carries the **gm/ID re-sizing** from the PPA campaign's hand-design
pass (`campaigns/ppa_FOUNDRY65/hand_design`, tag `gmid_v5`; the pre-campaign committed sizing
measured 59.8 dB @ 1894 µW on the campaign benches). LUT-derived, role-driven bias plan at the
15 µA bias floor — the m-ratio welds lock every branch current, so the design freedom is per-role
inversion level + L. Campaign-bench numbers (1.8 V, tt): **dcgain 74.7 dB · pm 77.9° · ugf
4.1 MHz · cmrr 78.5 dB · psrr 70.2 dB · 422 µW — all specs pass** (score −0.64, within 0.02 of
the best hand point with +1.5 dB/+4° more margin). Power below ~420 µW needs an m/ratio change,
not sizing (the 15 µA knob floor scales every welded branch).
