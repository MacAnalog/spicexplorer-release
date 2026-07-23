# ldo_004_basic_pmos — Basic PMOS LDO (minimal 4T error amp, uncompensated)

The minimal closed-loop LDO in the DB: a bare 4-transistor error amp (NMOS input
pair + PMOS mirror load, ideal tail current sink, **no** explicit bias-mirror
transistor, **no** compensation network) driving a PMOS pass device directly.
The pass gate's own parasitic capacitance is the loop's only pole-splitting —
a deliberately "basic/conceptual" complement to the Miller-compensated
`ldo_007_pmos` and the richer 2-stage `ldo_005_buffered_ref`.

## Layout
- `circuit.yaml` — the super-DSL manifest (identity, class, ports, pdks, analyses).
- `datasheet.yaml` — spec/metric sheet, characterized on ihp-sg13g2.
- `abstract/netlist.spice` — **AUTHORED** PDK-neutral source of truth (`nmos`/`pmos`
  tokens, descriptive sizing symbols matching the LDO class's existing naming style).
- `abstract/topology.cgraph.json` — **GENERATED** by circuitgraph (`analog-db generate`).
- `pdk/ihp-sg13g2/` (native) + `pdk/sky130/`, `pdk/gf180mcu/` (via `add-binding`): each has
  `devices.map.yaml`, `sizing.yaml`, `corners.yaml`, `netlist.spice` (**GENERATED** lowered).
- `analyses/{dc_op,load_regulation,line_regulation,psrr,dropout,tran_load_step,
  loop_stability,noise,tran_line_step}.yaml` — the full LDO class analysis set.
  `noise` (integrated output noise) and `tran_line_step` (supply-step transient)
  are class templates added from this circuit's own source bench suite (below).
- `reference/ltspice/` — the original LTspice design **and its full testbench
  suite** (noise / PSRR / line- and load-transient benches), vendored verbatim;
  see `reference/README.md` for the file-by-file map.
- `results/<pdk>__tt.json` — recorded `analog-db run` baselines for all three PDKs.

## Provenance
Imported/inspired by `external/conceptual_LDO_design/ltspice/LDO_basic.asc` — a
textbook LTspice reference design: an ideal behavioral op-amp (`UniversalOpAmp`,
`Avol=400000 GBW=10Meg Vos=0`) driving a PMOS pass device through a resistive
feedback divider.

## Why not a literal behavioral op-amp
circuitgraph's `DeviceFactory` only types `M`/`R`/`C`/`L`/`V`/`I`/`X` SPICE
primitives (see `device_factory.py`) — there is no VCVS/`E`-source support. A first
attempt at this circuit used an `E`+`R`+`C` single-pole macromodel (`Ea aint 0 vref
fb {avol}` + an `Rp`/`Cp` dominant pole) to mirror the source design's ideal op-amp
literally; `analog-db generate` silently dropped the `E` element (`skipping
unsupported or malformed device 'EA'`), leaving a broken, disconnected amplifier in
every lowered netlist. This circuit is the minimal **real-transistor** equivalent
instead — the simplest working amp the ldo class's existing templates can drive,
matching the source design's spirit ("basic/conceptual") rather than its exact
implementation technique.

## Loop polarity and behavior
`vout^ -> fb^ -> egate v -> Vsg(pass)=vdd-egate ^ -> Ipass ^ -> vout v` — standard
negative feedback via the vout->fb->vss divider (same polarity convention as
`ldo_007_pmos`, matching its established "M1=mirrored/in+, M2=direct-drain/in-" 5T
pattern). Because there's no second gain stage, the loop's DC error is real and
visible: on ihp-sg13g2 (default sizing) it regulates to ~1.307 V against an ideal
target of `vref_val*(r_top+r_bot)/r_bot` = 1.2 V, a ~9% error from the amp's finite
open-loop gain — documented as a floor in `datasheet.yaml`, not something to
"fix" for what is intentionally the DB's simplest LDO.

## PDK notes
All three PDK bindings simulate cleanly (all 7 analyses `status: ok`, no sim
errors) with only minor per-circuit adjustments to the `dropout` analysis: the
class-default `dropout.yaml` (copied from `ldo_007_pmos`) sweeps at a 10 mA load,
which this circuit's much smaller default pass device (`x_dut_xmp_w=10u, x_dut_xmp_m=20`)
cannot regulate through at all — a probe DC sweep showed `vout` capping out well
below the ldo_007_pmos-era `VOUT_THRESH` across the entire `VDD_START..VDD_STOP`
range. Lowered to a 1 mA sweep + a threshold re-derived from an empirical probe
(see the comment in `analyses/dropout.yaml`).
