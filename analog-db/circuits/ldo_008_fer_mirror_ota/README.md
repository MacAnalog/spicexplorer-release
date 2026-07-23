# ldo_008_fer_mirror_ota — LDO: mirror-loaded OTA + PMOS pass, RC-zero compensated

**Promoted** from the `ferrosim_ldo` reference entry (Arcadia-1/ferrosim, MIT). Class `ldo`
(existing), self-contained 3-port convention (`vdd vout vss`, as ldo_004/007).

NMOS diff pair (vref side / feedback side) with PMOS mirror load; the mirror-diode side is
the feedback leg so the mirror output drives the PMOS pass gate with the right loop polarity.
NMOS tail mirror off an internal 20 µA bias; R+C zero network from the pass gate to vout;
1:1 divider (vout = 2 × vref = 1.2 V). **Internalized (promotion):** the upstream external
VREF and bias sources are ideal in-DUT sources (frozen knobs `x_vref_val` 0.6 V,
`x_ibias_val` 20 µA); the upstream TB load and 10 pF output cap are dropped (class benches
provide Iload/COUT). The divider is 10× the upstream 900 Ω (67 µA instead of 667 µA burn).

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (VDD 1.8 V — ldo class convention).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** the full 9-bench ldo set (dc_op, load/line regulation, dropout, PSRR,
  loop_stability, tran load/line steps, output noise).
- **Reference bindings:** original FOUNDRY 28 nm + 65 nm ferrosim decks under `spectre/`.
- **Structure:** `find_subcircuits` → `dp.nmos.simple` (XMDR/XMDF), `cm.nmos.simple`
  (XMNB→XMNT), `cm.pmos.simple` (XMLD→XMLM).

## Measured (tt, native ngspice-45, 1.8 V in, 1.2 V target)

| metric | ihp-sg13g2 |
|--------|-----------|
| v_out (no load) / i_q | 1.209 V / 164 µA |
| load reg (0→10 mA) / line reg (1.4→2.0 V) | 28 mV / 2.0 mV |
| dropout (1 mA) | 12 mV |
| PSRR @ 1 kHz / Zout peaking | 49.5 dB / 3.8 dB |
| load-step undershoot / recovery | 41 mV / 24.5 µs |

(sky130 column on the committed scoreboard.)

Regenerate: `analog-db generate --circuit ldo_008_fer_mirror_ota`.
