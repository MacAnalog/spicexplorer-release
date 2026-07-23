# amp_017_tan_clia — 3-stage OTA, CLIA compensation

Imported from CODA-Team/AnalogGym `Amplifier/.../Tan_CLIA_Pin_3` (BSD-3-Clause) by `analog-db import-analoggym`. Compensation scheme + source: M. Tan & W.-H. Ki, IEEE JSSC 50(2):440-449, 2015.

- `abstract/netlist.spice` — PDK-neutral (sky130→nmos/pmos), canonical ports, role-encoded
  design-variable symbols preserved.
- `pdk/sky130/sizing.yaml` — the AnalogGym design variables (W/L/M + compensation passives).
- `datasheet.yaml` — extract-only benchmark specs (skill §6); per-topology CLoad from the
  AnalogGym design_variables. `status: incomplete` — no `ihp-sg13g2` binding (a device below the
  sky130 W bin); simulates on `gf180mcu` (baseline in `results/gf180mcu__tt.json`) and does not bias
  on `sky130` at default sizing. Matrix + caveats in `_shared/PDK_SIM.md`.
