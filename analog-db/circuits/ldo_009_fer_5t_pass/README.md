# ldo_009_fer_5t_pass — LDO: 5T OTA + PMOS pass, unity feedback, Miller-compensated

**Promoted** from the `ferrosim_ldo_sample` reference entry (Arcadia-1/ferrosim, MIT). Class
`ldo` (existing), self-contained 3-port convention (`vdd vout vss`).

5T OTA error amp (NMOS pair, PMOS mirror load, NMOS tail mirror) driving a PMOS pass device;
**unity feedback** (vout is the OTA's diode-side input directly — no divider), Miller cap from
vout to the pass gate, 50 pF on-board decap. **Internalized (promotion):** the upstream
Verilog-A behavioral bandgap (`va_vref`, vnom + 10 kΩ rout) becomes an ideal source + series
`x_rref` = 10 kΩ; the external 20 µA bias becomes an in-DUT source. **Normalization:** a
100 kΩ bleed (RBLD, ~9 µA) is added — with unity feedback and no divider the upstream DUT has
no no-load pull-down (its TB always drew ≥ 0.5 mA) and vout floats to vdd at Iload = 0;
standard LDO practice.

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (VDD 1.8 V, vout = vref = 0.9 V).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** the full 9-bench ldo set.
- **Reference bindings:** original proprietary-PDK 28 nm deck (incl. the va_vref module) under
  `spectre/28nm/`.
- **Structure:** `find_subcircuits` → `dp.nmos.simple` (XMIP/XMIN), `cm.nmos.simple`
  (XMNB→XMNT), `cm.pmos.simple` (XMLD→XMLM).

## Measured (tt, native ngspice-45, 1.8 V in, 0.9 V target)

| metric | ihp-sg13g2 |
|--------|-----------|
| v_out (no load) / i_q | 0.914 V / 73 µA |
| load reg (0→10 mA) / line reg | 39 mV / 0.7 mV |
| dropout (1 mA) | 149 mV |
| PSRR @ 1 kHz | 57 dB |
| load-step undershoot / recovery | 21 mV / 24.4 µs |

(sky130 column on the committed scoreboard.)

Regenerate: `analog-db generate --circuit ldo_009_fer_5t_pass`.
