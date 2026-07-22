# ldo_001_analoggym_basic — AnalogGym Basic LDO (2-stage, cascoded load, capless)

The flagship LDO of CODA-Team/AnalogGym (BSD-3-Clause) — the design its RGNN_RL
reinforcement-learning example optimizes. Verbatim transistor topology from
`spice_netlist/LDO_netlist.txt` (24 FETs): a PMOS bias-mirror rail (`xm0` diode + 6
mirrors), PMOS input pair into an **improved high-swing cascoded NMOS load** (the
self-biased vb3/vb4 rails — circuitgraph's structural detection identifies it as
`cm.nmos.improved_high_swing_cascode`), a pfet gm2 second stage riding the pass-gate
node, a large power PMOS (`m=928`), an internal 300k/100k divider (vout = 4·vref)
and a Miller cap. **Capless-class**: upstream runs only ~50 pF of output mim cap at
5–55 mA loads, so the transient/peaking numbers read very differently from the
1 uF-cap LDOs in this class — compare conditions, not just numbers.

## 3-port fold (import adaptation)
Upstream exposes `vinn/vinp/vfb/Ib` pins; the LDO class DUT is `[vdd, vout, vss]`.
Per the upstream testbench (`TB_LDO_ACDC.cir`): `vinn` -> internal ideal `Vref`
(0.4 V), `vinp` -> tied to the divider tap `vfb` (upstream ties them through a 1 TH
inductor), `Ib` -> internal ideal bias sink (`current_0_bias` = 1.5 uA). The mim
compensation cap (`XC0`, M_C0=34 units) becomes a plain 6.8 pF `c_comp`. The
upstream `pfet_01v8_lvt` flavor of the gm2 device lowers to the generic `pmos`
token (one flavor per polarity per binding — the only fidelity loss).

## Layout
- `abstract/netlist.spice` — AUTHORED, upstream instance names + m-multiplier
  arithmetic (`2*`, `4*`, `8*`) and role-encoded design-variable names preserved.
- `reference/analoggym/` — vendored upstream netlist, variables, both testbenches,
  and `perf_extraction_LDO.py`. Corpus provenance + licenses:
  [`corpora/analoggym-ldo/`](../../corpora/analoggym-ldo/PROVENANCE.md) — including
  the finding that AnalogGym's `ldo_1`/`ldo_2` variants were **never published**.
- `pdk/sky130/` (native: `01v8` devices, upstream default sizing verbatim) +
  `pdk/ihp-sg13g2/`, `pdk/gf180mcu/` via `add-binding`.
- `analyses/` — the full 9-analysis LDO class set at upstream conditions
  (VDD 1.8 V, 5 mA nominal / 55 mA heavy load, COUT 50 pF).

## Measured (tt, ILOAD 5 mA unless noted)
| | sky130 (native) | ihp-sg13g2 | gf180mcu |
|---|---|---|---|
| v_out | 1.595 | 1.596 | 1.596 |
| i_q | 19 uA | 20 uA | 19 uA |
| dropout | 0.218 | **0.006** | 0.072 |
| line_reg | 0.241 | **0.003** | **0.0008** |
| load_reg (0->55m) | 0.69 | **0.020** | 0.29 |
| psrr @1k | 8.9 dB | 39.6 dB | **53.5 dB** |

The datasheet is characterized on the upstream-native sky130 binding for
provenance fidelity — interestingly the transferred ihp-sg13g2 binding regulates
*much* harder (higher-gain devices at the same sizing). gf180mcu regulates at
nominal but is weak at the 55 mA heavy-load extreme (3.3 V-rated devices on a
1.8 V rail leave the amp little headroom) — runs everywhere, per-PDK optimization
is deliberately left as the optimizer's job (this is AnalogGym's optimization
benchmark, after all).
