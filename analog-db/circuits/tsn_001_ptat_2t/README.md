# tsn_001_ptat_2t — 2-transistor sub-Vt PTAT temperature-sensor core

**Promoted** from the `sfe_ptat_sensor_2t` reference entry (AnalogGym "Sensing Front End",
BSD-3-Clause). Class `temp_sensor` (new). Ports `vdd vout vss`.

Two stacked NMOS: XM0 (gate tied to source → Vgs=0, sub-threshold conduction from the supply) over
XM1 (diode-connected to ground). The sense node `vout` settles at a temperature-proportional (PTAT)
voltage. A low-amplitude core (~10 nA bias) — a valid but small-signal PTAT.

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (device-generic abstract netlist lowered per PDK).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `dc_op` (power), `temp_sweep` (slope + box spread), `line_sweep` (line sensitivity),
  `psrr` (low-f supply rejection).
- **Reference binding:** original proprietary-PDK 180 nm AnalogGym decks kept verbatim under `spectre/180nm/`.
- **Structure:** no current mirror / diff pair (two stacked diodes) — `find_subcircuits` correctly
  reports none.

## Measured (tt, native ngspice-45)

| metric | ihp-sg13g2 @1.2V | sky130 @1.2V |
|--------|------------------|--------------|
| v_out (27 °C) | 30 mV | 53 mV |
| sens_v_per_c | +0.15 mV/°C | +0.48 mV/°C |
| i_supply | 9.9 nA | 17 pA |
| line_sens | 21 % | 34 % |
| psr_db | −40 dB | −30 dB |

Line sensitivity is high because the top device (Vgs=0) current tracks its Vds≈supply — inherent to
an un-cascoded 2-device core. Regenerate: `analog-db generate --circuit tsn_001_ptat_2t`.

## Absorbed: sized 180 nm variants (former `sfe_ptat_sized_variants`)

`spectre/180nm-sized-variants/` carries AnalogGym's `ptat_1..4` — **sized instances of this same
2T topology** (parallel diode + Vgs=0-top legs, extracted `multi`/geometry) from the
`spectre_test` library, plus `spectre_ptat6.scs` (a byte-identical upstream duplicate of
`ptat_2`, preserved per the "nothing left behind" rule). They are reference bindings of THIS
entry: same `(GND VDD VOUT)` topology, different sizing — not separate topologies, so they get
no accession id of their own. Spectre format, proprietary-PDK 180 nm — parse-only here.
