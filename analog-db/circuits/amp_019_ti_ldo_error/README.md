# amp_019_ti_ldo_error — TI-LDO error amplifier (12T two-stage, level-shifted mirror load)

The full error amplifier from the TI-application-note LDO source design, imported
standalone as an amplifier-class circuit. `ldo_005_buffered_ref` deliberately abstracted
this amp down to a proven 5T shape when the LDO was imported; this circuit is the
faithful transistor-count import of the real thing.

## Topology
One external-bias mirror rail (`XMB0` diode + four NMOS sinks) biases everything.
NMOS input pair: `XM1` (g=VREF, **inverting**) / `XM2` (g=VFB, **non-inverting** —
its branch mirrors through the M7-diode onto the output). The first-stage load is a
**Vth-level-shifted PMOS mirror**: `XM4` runs at ~zero DC current as a source-follower
level shifter (its `nd` node has no DC path by design), so `XM3`/`XM5` mirror against
a level-shifted diode with extra Vds headroom — the TI paper's low-voltage mirror
trick. Second stage: `XM7` (diode, stacked on the first-stage node `nb`) drives the
`XM6` output PMOS against the `XMBO` sink; `Rz`+`Cc` compensate from `nb` to `vout`.

## Layout
- `abstract/netlist.spice` — AUTHORED PDK-neutral source of truth.
- `reference/README.md` — pointer to the vendored source `.sch` (kept with
  `ldo_005_buffered_ref`) + the full pin-geometry-resolved connectivity table.
- `pdk/gf180mcu/` (native — 6 V `nfet_06v0`/`pfet_06v0` at 3.3 V, umbrella corner
  sections) + `pdk/ihp-sg13g2/` (`sg13_hv_*`, `cornerMOShv.lib`) + `pdk/sky130/`
  (`g5v0d10v5`).
- `analyses/` — the amplifier-class set; `ac_open_loop` binds the
  **`ac_open_loop_biaswrap_ibias`** template (added to the class alongside this
  import): this amp has a *designed-in systematic offset* (see below), so an
  unwrapped open-loop op point rails.

## Import findings (the two real bring-up bugs)
1. **The source's 1x mirror ratios are degenerate.** The WIP `.sch` sizes every
   mirror sink identically. KCL at the first-stage node `nb` forces
   `i1 = i2 + I(mirror_e)`: with `I(mirror_e)` equal to the full tail current the
   input pair must split 1 mA/0 mA — no valid operating point (the amp railed,
   dcgain ~ -45 dB). Fixed by ratioing the `_e`/`_f` sinks to ~tail/4
   (`w_mirror_e`/`w_mirror_f` sizing symbols).
2. **Open-loop AC needs bias-wrap.** The ratioed sink is also a deliberate
   systematic offset, so the classic open-loop bench saturates. The new class
   template DC-shorts vout->vinn through 1 TH / AC-injects through 1 TF (same trick
   as the AnalogGym `biaswrap`, generalized to ibias-port DUTs).

## Measured (tt)
- gf180mcu (native, characterized): 40.3 dB, UGF 23.5 MHz, PM 49°, buffer gain
  0.979 @ 41 MHz BW, settle 63 ns, 2.32 mA from 3.3 V, 138 uVrms input noise.
- ihp-sg13g2: 53.8 dB, 42 MHz, **PM 25°** (needs per-PDK Rz/Cc retune — runs, not tuned).
- sky130: 45.1 dB, 28 MHz, PM 50°, buffer gain 0.78 (VCM=1.2 V is marginal for the
  5 V devices' Vth — runs, not tuned).
