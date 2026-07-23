# amp_024_smcnr — SMCNR two-stage, 100 nA sensing-front-end opamp

**Promoted** from the `sfe_smcnr_2stage_amp` reference entry (AnalogGym "Sensing Front End",
BSD-3-Clause). Class `amplifier` (existing), **AnalogGym 5-port self-biased convention**
(`vss vdd vinn vinp vout`, positional order required by `ac_open_loop_biaswrap` — as
amp_002..017).

PMOS bias-mirror bank off one diode (1:2:10 = diode:tail:stage-2 load), PMOS input pair with
NMOS mirror load, NMOS common-source second stage; single-Miller compensation with nulling
resistor (C0 2 pF + R0 100 kΩ). The upstream in-subckt **100 nA sink stays internal** (frozen
knob `x_ibias_val`) — the DUT is fully self-biased. The long upstream channels (L = 8-10 µm,
deep subthreshold at 100 nA) are kept: this is a micro-power sensing amp, not a GBW machine.

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V, VCM 0.5 — PMOS input).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Analyses:** `ac_open_loop` (biaswrap), `dc_op`, `noise`, `tran_step` (10 pF load; the
  100 nA slew makes settling hundreds of µs). The datasheet's `ibias` condition is 0 A —
  the universal templates' external Ibias line must inject nothing into a self-biased DUT.
- **Reference bindings:** original 180 nm spectre + HSPICE decks under `spectre/180nm/`.
- **Structure:** `find_subcircuits` → `dp.pmos.simple` (XM0/XM2), `cm.nmos.simple` (XM1→XM3),
  `cm.pmos.simple` (XM7→XM5, XM7→XM6).

## Measured (tt, native ngspice-45, 1.5 V, 10 pF)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| dc_gain (bias-wrapped) | 69.4 dB | 90.4 dB |
| UGF / PM | 152 kHz / 58° | 33 kHz / 84° |
| i_supply | 1.3 µA | 0.41 µA |
| t_settle (0.2 V, 2 mV band) | 8 µs | 210 µs |

Regenerate: `analog-db generate --circuit amp_024_smcnr`.
