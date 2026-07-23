# ldo_002_analoggym_folded_cascode — AnalogGym "ldo_folded_cascode" (9T folded-cascode OTA + PMOS pass)

The high-gain AnalogGym LDO: an NMOS input pair whose drain nodes are the *sources*
of a self-biased PMOS cascode pair (gates on the near-ground vb2 rail; the cascode's
mirror-side drain self-biases the top PMOS current sources), folded into NMOS sinks
(vb1), driving a PMOS pass device with Rz+Cc Miller compensation. Unity feedback
(vout = vref), 5 V sky130 devices at a 2.0 V rail, ~50 pF output cap (capless-class).

**Provenance nuance:** as with `ldo_003_analoggym_simple`, the netlist was never
published in CODA-Team/AnalogGym — source of truth is ChrisZonghaoLi/sky130_ldo_rl
(Apache-2.0), `reference/sky130_ldo_rl/ldo_folded_cascode_tb.spice`; AnalogGym's
`ldo_folded_cascode_vars.spice` supplies the default sizing (M1–M10 agree). See
[`corpora/analoggym-ldo/PROVENANCE.md`](../../corpora/analoggym-ldo/PROVENANCE.md).

## Import adaptations
Same pattern as `ldo_003_analoggym_simple`: 3-port fold (Vref/Vb1/Vb2 internal ideal
sources; upstream Vb2 = 25 mV — a deep near-ground PMOS cascode gate bias), unity
feedback, `R_bleed` 100k minimum-load bleed, and `l_tail` 0.5u -> 0.6u on gf180mcu
(6 V nfet bin floor). Note the self-biased cascode mirror is NOT detected by the
current template library (only the `dp.nmos.simple` input pair is) — a known
template-coverage gap, not an import defect.

## Bindings
sky130 native (upstream sizing verbatim); ihp-sg13g2 -> `sg13_hv_*`; gf180mcu ->
`nfet/pfet_06v0`. All 9 LDO-class analyses run on all three.

## Measured (tt, 10 mA nominal)
The gain of the folded cascode shows: vout 1.803 / 1.833 / 1.806 (sky130/ihp/gf180),
load_reg 3.6 mV / 32 mV / 5.7 mV, line_reg 0.3-1.5 mV everywhere, psrr 53 / 46 /
45 dB, dropout 58 / 45 / 81 mV. The cost is damping: zout peaking ~34-42 dB
(underdamped capless baseline — a good compensation-tuning benchmark) and ~0.7-0.8 V
undershoot on the 10 uA -> 10 mA step into 50 pF. i_q 269-624 uA.
