# gs_001_cascode_cs — cascode common-source stage (self-contained bias ladder)

**Promoted** from the `ferrosim_common_source` reference entry (Arcadia-1/ferrosim, MIT).
Class `gain_stage` (new). Ports `vdd vout vin ibias vss`; `ibias` is **sink-referenced**
(the bench pulls 20 µA out of the DUT's stacked PMOS diodes — the class convention).

NMOS common-source input (XMNIN) + NMOS cascode (XMNCA) against a cascoded PMOS
current-source load (XMPLD/XMPCA), biased by a self-contained ladder (stacked PMOS diodes for
the load/cascode gates, a 2-Vgs NMOS diode stack for the NMOS cascode gate). Since an
inverting stage's high-gain window is ~VDD/gain wide and PDK-dependent, `dc_op`/`ac_gain`
**bias-wrap** (1 TH inductor vout→vin) to self-bias at the trip point; `dc_transfer` sweeps
the full range.

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V, IBIAS 20 µA).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `dc_op` (v_trip + i_supply), `dc_transfer` (gain_dc + vin_pk), `ac_gain`
  (gain_ac_db + f3db into 200 fF).
- **Reference bindings:** original FOUNDRY 28 nm + 65 nm ferrosim decks under `spectre/`.
- **Structure:** `find_subcircuits` → `cm.pmos.simple` (XMPB1→XMPLD) **and** `cm.pmos.cascode`
  (XMPB1/XMPB2 → XMPLD/XMPCA).

## Measured (tt, native ngspice-45, 1.5 V / 20 µA)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| gain_dc (peak \|dVout/dVin\|) | 96.3 V/V @ 0.37 V | 83.7 V/V @ 0.71 V |
| v_trip (self-biased, = vin_pk ✓) | 0.373 V | 0.712 V |
| gain_ac_db / f3db (200 fF) | 32.0 dB / 3.8 MHz | 43.0 dB / 846 kHz |
| i_supply (self-biased) | 53 µA | 39 µA |

Regenerate: `analog-db generate --circuit gs_001_cascode_cs`.
