# amp_015_sau_cfcc — 3-stage OTA, CFCC compensation

Imported from CODA-Team/AnalogGym `Amplifier/.../Sau_CFCC_Pin_3` (BSD-3-Clause) by `analog-db import-analoggym`. Compensation scheme + source: S.S. Chong & P.K. Chan, IEEE JSSC 47(9):2227-2234, 2012.

- `abstract/netlist.spice` — PDK-neutral (sky130→nmos/pmos), canonical ports, role-encoded
  design-variable symbols preserved.
- `pdk/sky130/sizing.yaml` — the AnalogGym design variables (W/L/M + compensation passives).
- `datasheet.yaml` — extract-only benchmark specs (skill §6); per-topology CLoad from the
  AnalogGym design_variables. Lowers to all three PDKs (`ihp-sg13g2`/`sky130`/`gf180mcu`) and
  simulates; baselines are unoptimized floors in `results/<pdk>__tt.json` (matrix + caveats in
  `_shared/PDK_SIM.md`).
