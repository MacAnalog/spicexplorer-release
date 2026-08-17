# amp_023_fer_fd2s — fully-differential 2-stage (folded cascode + CS, RC-CMFB)

**Promoted** from the `ferrosim_opamp` reference entry (Arcadia-1/ferrosim, MIT). Class
`amplifier` (existing), **differential self-biased convention** (`vinp vinn voutp voutn vdd
vss`, the `_diff` templates).

Stage 1: NMOS-input folded cascode (Sooch-style bias ladder off one reference). Stage 2: NMOS
common-source with PMOS current-source loads. Miller + nulling-R per side. CMFB: RC sense of
voutp/voutn → 5T error amp → current forced into an NMOS diode → the stage-1 bottom sinks
(vcmfb is an NMOS Vgs by construction). The upstream **IBIAS and VCMR ports are internalized**
as ideal sources (frozen sizing knobs `x_ibias_val` = 20 µA, `x_vcmr_val` = 0.75 V) so the
6-port class convention applies; the upstream deck drove both from its testbench.

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V, input CM 0.9).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `ac_open_loop` (ac_open_loop_diff), `dc_op` (dc_op_diff: i_supply + vos),
  `noise` (noise_diff), `tran_step` (tran_step_diff).
- **Reference bindings:** original proprietary-PDK 28 nm deck + spectre run set under `spectre/`.
- **Structure:** `find_subcircuits` → `dp.nmos.simple` (XMI1/XMI2) + the full mirror bank
  (XMBD→XMB1/XMB2/XMT nmos; XMPD1→XMSA/XMSB/XMLA/XMLB/XMPM1 pmos).

## Measured (tt, native ngspice-45, 1.5 V, CM 0.9, 500 fF/side)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| dc_gain (differential) | 65.9 dB | 81.3 dB |
| UGF / PM | 151 MHz / 72° | 135 MHz / 69° |
| vos (CMFB residual) / vocm | ~0 V / 0.777 V | ~0 V / 0.712 V |
| i_supply | 550 µA | 371 µA |
| t_settle (0.2 V diff, 2 mV band) | 10.5 ns | 12.0 ns |

Regenerate: `analog-db generate --circuit amp_023_fer_fd2s`.
