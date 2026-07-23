# ccia-02 testbenches — bottom-up (per-block) bring-up

xschem testbenches for the Fan CCIA (ccia-02) family, one directory per DUT so each
leaf can be brought up **from the ground** before the full system:

| dir | DUT drawing | analog-db circuit | class | benches |
|---|---|---|---|---|
| [`ccia-dut/`](ccia-dut/) | `ccia-dut-chopper-w-positive-feedback-rrl.sch` | `ia_004_fan_chopper_rrl` | ia | full-system (chopper + PF + RRL); see its own README + CMFB_PLAN.md |
| [`ccia-core-opamp/`](ccia-core-opamp/) | `two-stage-opamp-core.sch` | `amp_026_fan_chopper_ota` | amplifier | ac_open_loop, dc_op, noise, tran_step |
| [`rrl-integrator-opamp/`](rrl-integrator-opamp/) | `integrator-switchcap-opamp.sch` | `amp_027_fan_rrl_ota` | amplifier | ac_open_loop, dc_op, noise, tran_step, ac_cm_reg, tran_cm_kick |
| [`rrl-dut/`](rrl-dut/) | `rrl-switched-capa-integrator.sch` | `sup_003_rrl_sc_integrator` | support | tran_rrl_sense |

Each bench's stimulus + measures are lifted from the class template its circuit's
`analyses/<id>.yaml` binds (`_shared/classes/{amplifier,support}/testbench-templates/`)
and adapted to the **drawing** symbol. The drawing exposes `Vb1..Vb4` as external
ports (the analog-db circuit entry pulls them inside as knob-driven sources), so the
block benches drive them with DC sources at the block's own `sizing.yaml` bias levels.

## Layout convention (golden template)

Placement follows [`ccia-dut/tran_zin_chopped.sch`](ccia-dut/tran_zin_chopped.sch):
`devices/code.sym` (not `code_shown`) code blocks in a top-left grid; graph boxes
top-right; `COMMANDS` + launchers on the right; DUT centre at `(1015,-725)`; sources
roughly placed (connection is by **net name** — the wires are visual aids, tweak freely).

## Running a bench

Both native ngspice and xschem resolve here (PDK present). Headless netlist + sim:

```bash
cd examples/analog-db
xschem --rcfile drawings/xschemrc -n -s -q -x -o /tmp/out \
  drawings/ccia-02-QinwenFan-chopper-ripple-reduction/testbenches/<dir>/<bench>.sch
( cd /tmp/out && ngspice -b <bench>.spice )      # prints the measures; writes <bench>.raw + *.svg
```

Interactively in xschem: open the `.sch`, hit the **"Simulate + load waves"** launcher
(bottom-right). Waveforms render three ways: the on-canvas graph boxes (auto-populated),
`hardcopy *.svg` (batch-safe), and `plot` (interactive only — it is *refused* under
`ngspice -b`, which is harmless).

## Recorded baselines (live tt, ngspice-45, IHP sg13g2, block's own sizing.yaml)

**ccia-core-opamp** — amp_026, two-stage Miller OTA, statically-transparent output
chopper (`vctl`→vdd, `vctl_not`→vss), **no CMFB** (vocm is ratio-set):

| bench | result |
|---|---|
| ac_open_loop | dc_gain **61.72 dB**, ugf **20.07 MHz**, pm **64.42°** |
| dc_op | i_supply **173.3 µA**, vos ≈0, vocm **0.5991 V** (centred at VCM with no CMFB) |
| noise | inoise_total **107.9 µV**, onoise_total 72.37 mV (1 Hz–10 MHz) |
| tran_step | t_settle **233 ns** |

The core opamp is **healthy standalone** (61.7 dB / 64° PM / centred vocm) — the
CCIA's clocked-transient railing (see `ccia-dut/CMFB_PLAN.md`) is a composition /
clocking phenomenon, not a core-opamp DC problem. This bench isolates that.

**rrl-integrator-opamp** — amp_027, telescopic OTA with an internal DDA-CMFB whose
reference is **`vb4` = pin `V_cmfb_ref`**:

| bench | result |
|---|---|
| ac_open_loop | dc_gain **46.61 dB**, ugf 444.4 MHz, pm 47.60° |
| dc_op | i_supply 64.23 µA, vos ≈0, vocm **0.474 V** (CMFB targets vb4=0.6 → ~126 mV static CM error: weak servo) |
| noise | inoise_total 81.12 µV, onoise_total 13.09 mV |
| **ac_cm_reg** | zcm_lf **3253.244 Ω**, zcm_peak **23216.63 Ω**, cm_peaking **17.070 dB** — matches amp_027's recorded datasheet baseline **to 6 sig figs** (FAIL vs 6 dB max: underdamped CM loop) |
| tran_cm_kick | cm_kick −16.6 mV, cm_resid **0** (no latch-up), t_cm_settle 25.3 ns |
| tran_step | t_settle 44.3 ns |

**rrl-dut** — sup_003, ripple-sensing demodulating SC integrator (biases internal;
drives only the ripple + clocks):

| bench | result |
|---|---|
| tran_rrl_sense | ripple_gain **−1.015e6 V/s/V** (PDK-floor 0.18u switches); **−4.37678e5 @ 2u switches** = sup_003's recorded live baseline (−4.377e5) exactly |

The negative sign is the RRL demodulation polarity. The committed bench uses PDK-floor
switches (per the owner's TG directive); the datasheet documents that narrower switches
*raise* ripple_gain, so floor reads ~2.3× the 2u number — set `tg_n_w=tg_p_w=2u` in
`PARAMS_SWITCH` to reproduce the recorded −4.377e5. A handful of `singular matrix: check
node voutn` warnings are SC start-up only (the ramp is clean; the 2u reproduction confirms it).

Two benches reproduce their analog-db recorded numbers **exactly** (amp_027 ac_cm_reg;
sup_003 tran_rrl_sense @ 2u) — an end-to-end check that the drawing → netlist → param
injection → sim path is correct across all three blocks.

## Design note — where the CMFB goes (Vb4 / V_cmfb_ref)

`integrator-switchcap-opamp` (amp_027) exposes pin **`V_cmfb_ref`** exactly where
`two-stage-opamp-core` (amp_026) exposes **`Vb4`**. In amp_027, `vb4` is documented as
*"Output common-mode reference into the DDA-CMFB"*; in amp_026, `vb4` is the tail + fold
+ output PMOS current-source gate. So **the CMFB injection node for the core opamp is
`Vb4`, not `Vb1`** — an external CM servo on the core should drive `Vb4` (mirroring how
amp_027 self-regulates onto its `V_cmfb_ref`). This supersedes the `vb1`-injection attempt
recorded in `ccia-dut/CMFB_PLAN.md`.
