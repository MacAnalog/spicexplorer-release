# cmp_002_strongarm — StrongARM latched comparator (clocked)

**Promoted** from the `ferrosim_comparator` reference entry (Arcadia-1/ferrosim, MIT), plain
core. Class `comparator` (new). Ports `vdd voutp voutn vinp vinn clk vss`; the upstream LM/LP
latch nodes are internalized, and the output naming is normalized so **voutp decides HIGH for
vinp > vinn** (upstream wiring vinn→sense_p / vinp→sense_n is kept, hence voutp = inverter(lm)).

Clocked tail + NMOS input pair into the sense nodes, cross-coupled NMOS/PMOS latch, 4 clk-gated
PMOS precharges, CMOS inverter per output. The upstream **offset-trim variant and the spectre
MC-offset / PSS-PNOISE characterization runs stay as references** (ngspice has no PSS).

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V, VCM 0.75, VOD 50 mV).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `tran_decision` (10 MHz clock, measured on the settled 2nd edge): t_prop
  (clk→voutp), decided levels mid-evaluation, period-average i_supply.
- **Structure:** `find_subcircuits` → `dp.nmos.simple` (XMINN/XMINP) + 2× `inv.cmos.stack`
  (no static mirrors exist in a clocked latch — expected).

## Measured (tt, native ngspice-45, 1.5 V, VOD 50 mV, 10 MHz)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| t_prop (clk → voutp) | 163 ps | 395 ps |
| decided levels (voutp/voutn) | 1.5 / ~0 V | 1.5 / ~0 V |
| i_supply (period average) | 1.8 µA | 0.6 µA |

Regenerate: `analog-db generate --circuit cmp_002_strongarm`.
