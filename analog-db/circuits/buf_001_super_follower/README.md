# buf_001_super_follower — feedback ("super") source follower

**Promoted** from the `ferrosim_source_follower` reference entry (Arcadia-1/ferrosim, MIT).
Class `buffer` (new). Ports `vdd vout vin ibias vss`; `ibias` is **source-referenced**
(bench pushes 10 µA into the DUT's NMOS diode — the class convention).

NMOS follower (XM1) whose drain node drives a shunt-feedback sink (XM2), lowering Zout and
stiffening the level shift; NMOS + PMOS mirrors distribute the bias, XMPB sources ~6x the
reference into the feedback node, CC compensates the local loop. Device widths stay
per-finger with `m=` multipliers (IHP PSP silently clips w > ~10 µm — the first lowering
attempt with 32-48 µm single fingers produced a dead bias point).

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V, IBIAS 10 µA). The follower's valid
  bias window (input device AND feedback sink saturated) is PDK-specific, so VCM is a
  **per-PDK `analysis_params` override** (ihp 0.66, sky130 1.05) — the schema-blocked
  `sizing.yaml analysis_params` mechanism was unblocked in this branch (see
  `_shared/schema/sizing.schema.json`).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `dc_op` (v_out, v_offset, i_supply), `dc_transfer` (gain_dc ~1), `ac_gain`.
- **Reference bindings:** original proprietary-PDK 28 nm + 65 nm ferrosim decks under `spectre/`.
- **Structure:** `find_subcircuits` → `cm.nmos.simple` (XMRN→XMNS) + `cm.pmos.simple`
  (XMPD→XMPB).

## Measured (tt, native ngspice-45, 1.5 V / 10 µA)

| metric | ihp-sg13g2 (VCM 0.66) | sky130 (VCM 1.05) |
|--------|----------------------|-------------------|
| gain_dc (peak dVout/dVin) | 0.836 | 0.827 |
| v_offset (vout − vin) | −0.405 V | −0.739 V |
| gain_ac_db / f3db (500 fF) | −2.3 dB / 985 MHz | −1.7 dB / 708 MHz |
| i_supply | 133 µA | 74 µA |

Regenerate: `analog-db generate --circuit buf_001_super_follower`.
