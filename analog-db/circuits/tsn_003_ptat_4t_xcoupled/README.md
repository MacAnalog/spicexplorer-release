# tsn_003_ptat_4t_xcoupled — resistorless 4T PTAT cell

**Promoted** from the `sfe_ptat_65_classic` reference entry (AnalogGym "Sensing Front End",
BSD-3-Clause). Class `temp_sensor`. Ports `vdd vout vss`.

Cross-coupled NMOS/PMOS pairs: NMOS diode (XM1) + gate-coupled NMOS (XM0) against a PMOS
diode at vout (XM3) + gate-coupled PMOS (XM4). The loop self-biases in sub-threshold with no
resistor — the third PTAT flavor in the class (tsn_001 = 2T, tsn_002 = classic R-degenerated).
The upstream 65 nm cell is 4 × 200n/60n (1:1); on the open PDKs a 4:1 NMOS W-skew (as in
tsn_002) plus long channels (3 µm) set a non-degenerate ~50 µA operating point.

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V shared).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** temp_sensor set — `dc_op`, `temp_sweep` (−20..120 °C), `line_sweep`
  (1.3–1.7 V), `psrr`.
- **Reference binding:** the original FOUNDRY **65 nm** spectre deck under `spectre/65nm/`
  (parse-only here — never simulated, no FOUNDRY models in-repo).
- **Structure:** `find_subcircuits` → no mirror/pair templates match (both "mirrors" are
  gate-cross-coupled, not diode-anchored) — expected for this cell; the loop is validated by
  the temp/line sweeps instead.

## Measured (tt, native ngspice-45, 1.5 V)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| v_out (27 °C) | 88.7 mV | 40.0 mV |
| sens (dVout/dT) | +0.21 mV/°C | +0.19 mV/°C |
| line sensitivity (1.3→1.7 V) | 34 % | 75 % |
| PSR @ 1 kHz | −22.4 dB | −22.5 dB |
| i_supply | 54 µA | 9.4 µA |

Line sensitivity is the cell's known weakness: uncascoded, every leg's Vds tracks the supply
(worse on sky130, where the higher vth pushes the loop deeper sub-Vt). Cascoding fixes it but
would depart from the 65 nm original.

Regenerate: `analog-db generate --circuit tsn_003_ptat_4t_xcoupled`.
