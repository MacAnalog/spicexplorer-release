# ldo_005_buffered_ref — Buffered-reference LDO (ref-buffer + RC filter + error amp, Miller-compensated)

The richest LDO in the DB: **two** internal 5T OTA stages — a reference-buffer
amp and an error amp — plus a single-pole RC filter between them, driving a
Miller-compensated PMOS pass device. Distinguishes itself from `ldo_007_pmos` (one
error amp comparing `vout` directly against an ideal internal `Vref`) by
buffering+gaining the reference through its own closed-loop amp (with an outer
feedback divider) and RC-filtering it before the error amp ever sees it —
reducing the error amp's sensitivity to reference noise/ripple, at the cost of
an extra gain stage's own pole to compensate for.

## Layout
- `circuit.yaml` — the super-DSL manifest (identity, class, ports, pdks, analyses).
- `datasheet.yaml` — spec/metric sheet, characterized on ihp-sg13g2 (the best-behaved
  binding — see PDK notes below).
- `abstract/netlist.spice` — **AUTHORED** PDK-neutral source of truth (`nmos`/`pmos`
  tokens, descriptive sizing symbols grouped by stage: `*_ref_*` for the reference
  buffer, `*_err_*` for the error amp).
- `abstract/topology.cgraph.json` — **GENERATED** by circuitgraph (`analog-db generate`).
- `pdk/gf180mcu/` (native — matches the TI-paper source design's own device family) +
  `pdk/ihp-sg13g2/`, `pdk/sky130/` (via `add-binding`): each has `devices.map.yaml`,
  `sizing.yaml`, `corners.yaml`, `netlist.spice` (**GENERATED** lowered).
- `analyses/{dc_op,load_regulation,line_regulation,psrr,dropout,tran_load_step,
  loop_stability,noise,tran_line_step}.yaml` — the full LDO class analysis set
  (incl. the `noise` and `tran_line_step` templates added to the class alongside
  this import).
- `reference/ti-ldo/` — the original xschem design tree (all `.sch`/`.sym`
  sub-blocks, per-block testbenches, the TI architecture diagram, `xschemrc`),
  vendored verbatim; see `reference/README.md` for the file-by-file map.
- `results/<pdk>__tt.json` — recorded `analog-db run` baselines for all three PDKs.

## Provenance
Inspired by `external/conceptual_LDO_design/ti-ldo/ldo/ldo.sch` — a hierarchical,
GF180MCU-native LDO built from real xschem sub-blocks (`ref_amp`, `error_amp`,
`lpf_rc`, a PMOS pass device), following the TI application-note architecture
(see `error_amp.sch`'s own title text: "Error Amplifier Implementation - TI LDO
Paper"). A sibling file (`ldo_two_r.sch`) is the same topology with fixed instead
of parameterized sizing — not imported separately, since it adds nothing
structurally new.

Ground truth was established by headless-netlisting the source `.sch` files
natively (xschem 3.4.8 + a native gf180mcu PDK checkout with real xschem symbol
libraries, since the analog-db Docker image only vendors gf180mcu's `ngspice`
model files, not its `xschem` symbol library). A committed
`ldo/simulation/ldo.sch/ldo.spice` flatten in the source tree turned out to be
**stale** (missing the `ref_amp` bias-mirror transistors present in the current
`ref_amp.sch`, and showing a "floating" `vss` pin that a fresh netlist resolves
cleanly) — cross-checked against a fresh headless run plus direct `.sym`
pin-geometry math (pin `B`/`P`/`M` box coordinates transformed by each
instance's placement) for the handful of device symbols (`ppolyf_u_3k`,
`nfet_06v0`, `pfet_06v0`) that circuitgraph's real-PDK-model resolution
suppressed from the flatten output entirely.

The block-level topology: `ref_amp` = 5T OTA (folded NMOS input pair + PMOS
mirror load + explicit NMOS tail-bias mirror), non-inverting-buffer-configured
via an outer `R1`/`R2` divider around its own output. `lpf_rc` = a plain
series-R/shunt-C single-pole filter. `error_amp` compares `vout` against the
filtered reference and drives the PMOS pass gate through a Miller `Rz`/`Cc`
network. This abstraction reuses `ref_amp`'s and `error_amp`'s proven 5T
topology (matching `ldo_007_pmos`'s own error-amp shape) rather than replicating
every internal cascode/mirror transistor of the much larger source schematics
(`error_amp.sch` alone has 12+ transistors) — the goal was a genuine, correct,
testable realization of the TI-paper *architecture* (buffer + filter + error
amp + pass device), not a byte-exact transistor-count clone of a WIP academic
design.

## A polarity bug caught during bring-up
The first version of the reference-buffer stage had the "+"/"-" input roles
swapped: in a 5T OTA, the input whose current gets **mirrored** onto the output
(via the diode+mirror load pair) is the non-inverting input, and the input
whose drain **directly is** the output node is the inverting one. The initial
netlist put the external `vref` on the direct-drain/inverting side and the
`v_ref_fb` divider tap on the mirrored/non-inverting side — exactly backwards,
turning the outer feedback divider into **positive** feedback. Symptom: `dc_op`
converged to `vout ≈ 0 V` (or railed, depending on `vref_val`) instead of
regulating. Found by probing internal nodes (`v_ref_out`, `retail`, `rd1`, ...)
directly in a `.control op` deck and comparing against the already-validated
`ldo_007_pmos` error amp's own M1/M2 role assignment. Fixed in `abstract/netlist.spice`
(see the comment above `XM1`/`XM2`).

## PDK notes
All three PDK bindings simulate cleanly (all 7 analyses `status: ok`) but needed
per-PDK `vref_val` tuning beyond the class-default 0.6 V: gf180mcu's `nfet_03v3`
(3.3 V-rated) devices have high enough `Vth` that 0.6 V left the reference-buffer
input pair without enough headroom to turn on at all (`v_ref_out` collapsed to
~0 V) — bumped to 0.8 V. sky130 showed a milder version of the same effect —
bumped to 0.7 V. ihp-sg13g2 works fine at the class-default 0.6 V and regulates
almost exactly to the ideal `vref_val*(r_ref_top+r_ref_bot)/r_ref_bot` = 1.2 V
target, so it's the PDK `datasheet.yaml` is characterized against — gf180mcu and
sky130 run all analyses but aren't as tightly regulated (same "runs, not yet
per-PDK tuned" state `ldo_007_pmos` itself documents for its non-reference PDKs).
The `dropout` analysis also needed its `ILOAD` lowered from the class-default
10 mA to 1 mA on every PDK — a probe sweep showed `vout` going deeply negative/
nonlinear under 10 mA across most of the `VDD_START..VDD_STOP` range with this
circuit's default pass-device sizing.
