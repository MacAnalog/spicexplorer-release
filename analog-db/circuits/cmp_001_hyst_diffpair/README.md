# cmp_001_hyst_diffpair — continuous-time hysteretic comparator

**Promoted** from the `ferrosim_hyst_comparator` reference entry (Arcadia-1/ferrosim, MIT).
Class `comparator` (new). Ports `vdd vout vinp vinn vss` — fully self-contained (the pair is
biased by its **resistor tail**, a deliberate upstream choice kept here; consequently the
diff-pair detector has no mirror-anchored tail to flag, and only the load mirror is reported).

NMOS input pair with PMOS mirror load; output-fed trip-shifters (small MOS + series R from
the decision node) move the threshold with the output state — the hysteresis; a 3-stage
inverter chain (m = 1/2/4) squares the decision to rail-to-rail. The upstream 3 MΩ shifter
resistors gave sub-mV (unmeasurable) hysteresis on the open PDKs; the default is retuned to
300 kΩ so the defining feature is visible (~7-23 mV).

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V, VCM 0.75).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `dc_op` (decided-high v_out + static i_supply), `dc_hysteresis` (up/down
  sweeps → vth_rise/vth_fall/v_hyst).
- **Reference bindings:** original FOUNDRY 28 nm + 65 nm ferrosim decks under `spectre/`.
- **Structure:** `find_subcircuits` → `cm.pmos.simple` (XMPLD→XMPLM) + 3× `inv.cmos.stack`.

## Measured (tt, native ngspice-45, 1.5 V, VCM 0.75)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| vth_rise / vth_fall | 0.7745 / 0.7675 V | 0.7575 / 0.7345 V |
| v_hyst | 7 mV | 23 mV |
| v_out (decided high) | 1.50 V | 1.50 V |
| i_supply (static) | 78 µA | 20 µA |

Regenerate: `analog-db generate --circuit cmp_001_hyst_diffpair`.
