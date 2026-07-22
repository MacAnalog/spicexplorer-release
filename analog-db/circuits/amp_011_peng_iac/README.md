# amp_011_peng_iac — 3-stage OTA, IAC compensation

Imported from CODA-Team/AnalogGym `Amplifier/.../Peng_IAC_Pin_3` (BSD-3-Clause) by `analog-db import-analoggym`. Compensation scheme + source: Peng, Sansen, Hou, Wang, Wu, IEEE JSSC 46(2):445-451, 2011.

- `abstract/netlist.spice` — PDK-neutral (sky130→nmos/pmos), canonical ports, role-encoded
  design-variable symbols preserved.
- `pdk/sky130/sizing.yaml` — the AnalogGym design variables (W/L/M + compensation passives).
- `datasheet.yaml` — extract-only benchmark specs (skill §6); per-topology CLoad from the
  AnalogGym design_variables. Lowers to all three PDKs (`ihp-sg13g2`/`sky130`/`gf180mcu`) and
  runs an **AC-only unoptimized baseline** (`results/<pdk>__tt.json`: only `ac_open_loop`;
  `dc_op`/`noise`/`tran_step` are disabled, and some DC gains are still negative/unoptimized).
  Matrix + caveats in `_shared/PDK_SIM.md`.
