# amp_002_alfio_raffc — 3-stage OTA, RAFFC compensation

Imported from CODA-Team/AnalogGym `Amplifier/.../Alfio_RAFFC_Pin_3` (BSD-3-Clause) by `analog-db import-analoggym`. Compensation scheme + source: Grasso, Palumbo, Pennisi, IEEE TCAS-I 54(7):1459-1470, 2007.

- `abstract/netlist.spice` — PDK-neutral (sky130→nmos/pmos), canonical ports, role-encoded
  design-variable symbols preserved.
- `pdk/sky130/sizing.yaml` — the AnalogGym design variables (W/L/M + compensation passives).
- `datasheet.yaml` — extract-only benchmark specs (skill §6); per-topology CLoad from the
  AnalogGym design_variables. Lowers to `ihp-sg13g2`/`gf180mcu` and runs an
  **AC-only unoptimized baseline** (`results/<pdk>__tt.json`: only `ac_open_loop`;
  `dc_op`/`noise`/`tran_step` are disabled, and the gf180 DC gain is still negative/unoptimized).
  **sky130 is not yet passing** — `circuit.yaml` status is `incomplete` (negative gain at the
  template dimensions), so no `results/sky130__tt.json` is committed. Matrix + caveats in
  `_shared/PDK_SIM.md`.
