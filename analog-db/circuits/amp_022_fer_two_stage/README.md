# amp_022_fer_two_stage — classic Miller two-stage opamp (PMOS input)

**Promoted** from the `ferrosim_two_stage_opamp` reference entry (Arcadia-1/ferrosim, MIT).
Class `amplifier` (existing), **ibias-port convention** (`vdd vout vinp vinn ibias vss`, as
amp_001/amp_018).

PMOS input pair + NMOS mirror load, PMOS tail and second-stage current-source load off one
PMOS bias diode, NMOS common-source second stage, 2 pF Miller cap. The upstream deck bias-
references the PMOS diode with an external ideal *sink*; the promotion adds an NMOS
diode+mirror front-end (XMBD/XMBS, +2 devices) so the class's vdd→ibias convention drives it —
documented normalization, same trick as dp_001's mirror tail. Upstream m-ratios (3:3:17
bias:tail:load, 2:24 mirror:CS) are preserved so the current split matches the source design.

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V, IBIAS 20 µA, VCM 0.6 — PMOS input).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `ac_open_loop` (via **ac_open_loop_biaswrap_ibias** — a fixed-VCM open loop
  rails a two-stage's output), `dc_op`, `noise`, `tran_step` (universal templates).
- **Reference bindings:** original proprietary-PDK 28 nm + 65 nm ferrosim decks under `spectre/`.
- **Structure:** `find_subcircuits` → `dp.pmos.simple` (XM0/XM1), `cm.nmos.simple` (XM3→XM4 +
  XMBD→XMBS), `cm.pmos.simple` (XM7→XM5, XM7→XM6).

## Measured (tt, native ngspice-45, 1.5 V / 20 µA / 500 fF)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| dc_gain (bias-wrapped) | 51.5 dB | 65.7 dB |
| UGF / PM | 20.9 MHz / 81° | 3.5 MHz / 87° |
| i_supply | 246 µA | 85 µA |
| t_settle (0.2 V, 2 mV band) | 38 ns | 2.6 µs |

**Bench-validation pass (2026-07-09, tt, in-library `run_circuit`; pre-campaign sizing)** — the full amplifier bench
suite. ihp-sg13g2 (ngspice): CMRR 64.3 dB, PSRR+ 76.4 dB, ICMR 1.37 V,
THD 0.023 % (100 mV @ 1 MHz), IIP3 +23.6 dBV. The THD/IIP3 pair is internally coherent
(lower distortion ↔ higher intercept).

Regenerate: `analog-db generate --circuit amp_022_fer_two_stage`.
