# ldo_003_analoggym_simple — AnalogGym "ldo_simple" (5T OTA + PMOS pass, unity feedback)

The smallest AnalogGym LDO: a 5T OTA (NMOS pair, PMOS mirror load, voltage-biased
tail) driving a PMOS pass device, Rz+Cc Miller from the pass gate to vout, **unity
feedback** (no divider — vout regulates to vref directly). Native design uses
sky130's 5 V (`g5v0d10v5`) devices at a 2.0 V rail with vref = 1.8 V and a ~50 pF
output mim cap (capless-class).

**Provenance nuance:** the netlist was *never published* in CODA-Team/AnalogGym
(only its testbench/variable shells — see
[`corpora/analoggym-ldo/PROVENANCE.md`](../../corpora/analoggym-ldo/PROVENANCE.md));
the subckt comes from the companion repo the AnalogGym RL example builds on,
ChrisZonghaoLi/sky130_ldo_rl (Apache-2.0), whose committed testbench flatten
(`reference/sky130_ldo_rl/ldo_tb.spice`) carries it. AnalogGym's own
`ldo_simple_vars.spice` supplies the default sizing — the two agree on every
device role (M1–M6 + Rfb/Cfb).

## Import adaptations
- 3-port fold: `Vfb` -> vout (unity), `Vref`/`Vb` -> internal ideal sources.
- `R_bleed` (100k) added: upstream never runs below ~10 uA load; with unity
  feedback there is NO internal DC path, so a true no-load dc_op rails vout to vdd.
- gf180mcu binding: `l_tail` bumped 0.5u -> 0.6u (`nfet_06v0` has no model bin
  below L=0.6 um — the deck errors with "could not find a valid modelname").
- Polarity check: XM1 (feedback) drains into the mirror-diode side = non-inverting,
  matching the class's proven 5T rule; confirmed by structural detection
  (`dp.nmos.simple` + `cm.pmos.simple`).

## Bindings
sky130 native (5 V devices, upstream sizing verbatim, incl. the huge `m_pass=360`);
ihp-sg13g2 -> `sg13_hv_*` (cornerMOShv.lib); gf180mcu -> `nfet/pfet_06v0`
(umbrella corner sections). All 9 LDO-class analyses run on all three.

## Measured (tt, 10 mA nominal)
vout 1.87 (sky130; +4% from finite 5T loop gain) / 1.82 (ihp) / 1.84 (gf180);
dropout 0.16 / 0.04 / 0.10; psrr 25.4 / 39.3 / 29.2 dB; load-step undershoot ~1 V
on the upstream 10 uA -> 10 mA step into 50 pF (capless-class); i_q ~110-170 uA.
