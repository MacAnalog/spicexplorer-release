# ldo_007_pmos — PMOS-pass LDO with a 5T error amp

The first **real** regulator in the database (the `ldo_006_stub` is an NMOS source-follower that, by
construction, cannot achieve low dropout). `ldo_007_pmos` is the canonical low-dropout topology:

```
        Vin (vdd) ──┬───────────────[ MP pass PMOS ]───────┬──► Vout
                    │                     │gate(egate)      │
                    │                  ┌──┴──┐           [R1]
                 [error amp: 5T OTA]   │ Cc  │ Rz          ├── fb ──► (error-amp in+)
                 in+ = fb              └─────┘           [R2]
                 in- = vref ──(internal ideal ref)         │
                 out = egate                              Vss
```

* **Pass device** `MP`: PMOS common-source stage; dropout floor ≈ its `Vds,sat` (~hundreds of mV),
  not a full `Vt` as in the source-follower stub.
* **Error amp**: a 5-transistor OTA **hand-inlined as flat primitives** (`XM1..XM6`). It is *not*
  a black-box sub-circuit instance — see the note below.
* **Reference + tail bias** are **ideal internal sources** (`vref_val`, `i_tail`). This is a
  simulation reference, not a silicon bandgap; a clean `vref` (rather than a Vdd divider) is what
  makes line-regulation and PSRR physically meaningful.
* **Compensation**: a Miller cap `Cc` + nulling resistor `Rz` across the pass stage (pole split).
* **Regulation point**: the loop forces `fb = vref`, so `Vout = vref·(r_top+r_bot)/r_bot` ≈ 1.2 V
  for `vref = 0.6 V`, `r_top = r_bot`.

## Why hand-inlined, not composed from the catalog OTA

The original plan called for instantiating the catalog `amp_001_5t` as a black-box error-amp
sub-circuit ("the DB's first circuit composition"). A spike showed this **does not work today**:
`circuitgraph`'s `to_netlist` emits a foreign `.subckt` instance as an instance line *with no
definition body* (`emit.py`: "the `.subckt` definitions are not emitted"), and `assemble.py`'s
`dut_subckt` never injects a child definition — so the lowered/assembled deck would contain a
**dangling `ota_5t` reference** and fail to parse. True composition is a hierarchical-netlist
feature spanning `circuitgraph` + `core` + the circuit schema + `assemble`/`generate`/`verify`; it
is tracked as a separate tooling task. Hand-inlining is the runnable path now.

## Status

**sky130: SPICE-validated** (real ngspice 45, `results/sky130__tt.json`). Stable, low-dropout, and
regulating — the datasheet specs are characterized to these measurements:

| metric | sky130 measured | spec | |
|---|---|---|---|
| v_out | 1.205 V | 1.16–1.24 V | ✅ |
| i_q | 209 µA | ≤ 250 µA | ✅ |
| dropout @10 mA | **284 mV** | ≤ 300 mV | ✅ |
| load_reg (0→10 mA) | 15.6 mV | ≤ 20 mV | ✅ |
| line_reg | 1.1 mV | ≤ 20 mV | ✅ |
| PSRR @1 kHz | 59.2 dB | ≥ 30 dB | ✅ |
| Zout peaking | 7.0 dB (PM ≈ 42°) | ≤ 8 dB | ✅ |
| load-step undershoot | 28.9 mV | ≤ 100 mV | ✅ |
| recovery (1 µF Cout) | 22.2 µs | ≤ 30 µs | ✅ |

**Compensation story** (the tuning that got here): a Miller cap *fights* the dominant 1 µF output
pole, so it is disabled (`c_comp≈0`); stability comes from a fast error amp (`i_tail=200 µA`,
short EA devices) keeping the gate pole high, plus a **feedforward cap `c_ff`** across `r_top` that
adds a phase-lead zero near unity-gain. The residual ~7 dB peaking (PM ≈ 42°) is the limit of a
single-stage error amp driving a large pass-gate cap; a gate buffer stage would push it below 6 dB.

**ihp-sg13g2 / gf180mcu: lower + assemble + run in SPICE, but not yet retuned** (the committed
results show the sky130 sizing ported blindly — IHP has low loop gain / poor load-reg; gf180's
load-step is unstable). Per-PDK sizing is follow-up work. `status: incomplete` reflects this
(2 of 3 PDKs un-tuned). Tier 0–2 (schema / drift / assembly) pass on all three.

## Analyses

| analysis | template | metrics |
|---|---|---|
| `dc_op` | ldo/dc_op | `v_out`, `i_q` |
| `load_regulation` | ldo/load_regulation | `load_reg` |
| `line_regulation` | ldo/line_regulation | `line_reg` |
| `psrr` | ldo/psrr | `psrr_vdd_db` |
| `dropout` | ldo/dropout | `v_dropout` |
| `tran_load_step` | ldo/tran_load_step | `v_undershoot`, `t_transient` |
| `loop_stability` | ldo/loop_stability | `zout_peak_db` (Zout-peaking stability proxy) |
