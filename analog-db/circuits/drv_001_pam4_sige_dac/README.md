# drv_001_pam4_sige_dac — 2-bit PAM-4 current-mode DAC driver (SiGe HBT, IHP SG13G2)

Block-level replication of the inductorless 96 Gb/s PAM-4 optical-modulator driver of
**Inac, Peczek, Malignaggi, Gerfers et al., EuMIC 2022**, on the open **IHP SG13G2** SiGe:C
BiCMOS PDK. The **first bipolar and first RF/broadband circuit** in the corpus (new class
`drv`). Ported from the EIC-designer `lumped-broadband-driver` verified reference (16/16
requirements, dual sign-off) and reproduces the golden with **zero delta on all 8 system
metrics** (`reference/eic_golden_pam4_results.yaml`). Standalone repo with the full layout /
kpex / eye journey: `github.com/JPPhotonics/agentic-design-pam4-driver-ihp130`.

Landed from `drawings/pam4-driver-2-bit-dac-HBT/` (see that family's `landing.yaml`); the
authoritative editable drawing is `pdk/ihp-sg13g2/schematic/dut_pam4.sch`.

## Topology

Fully differential 2-bit binary-weighted current-mode DAC. **LSB** = 1 differential cascode
gain cell; **MSB** = 2 identical cells in parallel — the binary weight is realized by cell
*count*, not sizing. Each cell is a differential pair (`npn13G2`, `Nx` stripes) with
**capacitive emitter degeneration** (R_E bridged by C_deg) for inductorless bandwidth peaking,
driving a common-base cascode and current-summing into shared collector loads. Output CM is set
by the collector-load IR drop (open-loop, no CMFB).

The **bias-port VCCS convention** is the key optimizer affordance: each cell's tail is an ideal
`Gtail t 0 <bias> 0 1m` (1 mA/V), so the per-cell tail current in mA equals the `blsb`/`bmsb`
port voltage. The tail becomes a plain scalar knob (`x_dut_itail_ma`) a testbench sets with a DC
source, and one DUT netlist serves the transient, `.op` and `.ac` benches unchanged.

## The §3 optimizer spec tier

Eight searched knobs (`pdk/ihp-sg13g2/sizing.yaml`), defaults = the EIC golden:

| `.param` | type | bounds | note |
|---|---|---|---|
| `x_dut_nx` | integer | 1 … 10 | sole device-level knob; model validity `I_C < 3·Nx mA` |
| `x_dut_itail_ma` | log | 4 … 24 mA | per cell (bias-port VCCS); keep `tail ≤ 6·Nx` |
| `x_dut_re` | log | 0.5 … 20 Ω | |
| `x_dut_cdeg_ff` | log | 5 … 500 fF | peaking |
| `x_dut_rc` | linear | 25 … 100 Ω | golden 50; the paper-vs-thesis 100 Ω twist (see below) |
| `x_dut_rb` | linear | 25 … 100 Ω | |
| `x_dut_vcasc` | linear | 2.8 … 3.6 V | SOA-critical (V_CE vs BV_CEO ≈ 1.6 V) |
| `x_dut_vcm_in` | linear | 1.6 … 2.2 V | |

Frozen: `x_dut_vcc = 4.0 V`. Nine scored specs (`datasheet.yaml` → `project_setup.yaml`
`target_specs`): LSB/MSB LF gain (≥ 2.2 / 8.2 dB), the two 50 GHz relative-gain bandwidth
proxies (≥ −3 dB), S11 @ 32 GHz and S22 @ 50 GHz (≤ −10 dB), supply power (≤ 192 mW), swing
(≥ 2.1 Vpp), and an `ic_msb_ma` **liveness canary** (feasibility gap 4.3 — catches the silent
0 A HBT if `ngbehavior=hsa` is missing). Each spec is a single **bare scalar** the deck's own
`.control` block writes (via `meas ac … at=<f>`), read by name — no `.ac` grid / interpolation,
exactly like the OTA example's UGF/PM.

Eight testbenches collapse to six decks (`pdk/ihp-sg13g2/testbenches/`, `.op`+`.ac` on
ngspice-45): `tb_gain_lsb`, `tb_gain_msb` (each emits LF + 50 GHz-relative gain), `tb_s11`,
`tb_s22`, `tb_bias` (power + canary), `tb_swing` (large-signal transient). `dac_weight_db`
is derived (MSB − LSB) and the 48 GBaud PAM-4 eye (`rlm`, `eye_height_v`) is final-design
validation only, out of the sizing loop.

## Files

- `abstract/netlist.spice` — parameterized topology (authored, `npn13G2` direct — see above).
- `datasheet.yaml` — the 8 specs + derived weight + eye metrics, with `extract`/`spec`/`optimize`.
- `pdk/ihp-sg13g2/` — `netlist.spice` **(gen)** flat lowered topology, `devices.map.yaml` (empty),
  `sizing.yaml` (the 8 knobs), `corners.yaml` (cornerHBT.lib typ/wcs/bcs), `schematic/` (editable
  drawing), and `testbenches/`: the six `.op/.ac`/tran probe decks, `dut.spice` (the `.subckt` form
  they `.include`), and the mandatory `.spiceinit` (`ngbehavior=hsa`).
- `optimizer/projection.yaml` (thin) → `project_setup.yaml` **(gen)** — the optimizer-ready spec tier.
- `abstract/topology.cgraph.json`, `raw/` **(gen)** — cgraph + standalone DUT/schematic views.
- `reference/eic_golden_pam4_results.yaml` — the EIC-verified golden (provenance / `typ` source).

## What is authored vs. generated (and what the harness can/can't do here)

This is the corpus's first **bipolar/RF** circuit. The HBTs are `X`-prefixed subckt instances of
the `npn13G2` VBIC card, which `circuitgraph` treats as opaque `SUBCKT` black boxes (it has no BJT
device type). That is enough to clear the **PDK-free tiers T0–T2**: `analog-db generate` writes the
cgraph, the lowered `pdk/ihp-sg13g2/netlist.spice` (topology verbatim — nothing to model-retarget,
so `devices.map.yaml` is empty), the `raw/` standalone DUT + schematic views, and the merged
`project_setup.yaml` (dut_params from `sizing.yaml`, target_specs from the datasheet `optimize`
blocks). T0 schema + xrefs, T1 generation drift, and T2 assembly all pass.

What the CMOS-only harness still can't do (feasibility §4.4/4.5), and how it's handled:

- **No class-templated `analyses/*.yaml`.** The assembler renders MOS class benches; the RF/tran
  probes here don't fit it, so `circuit.analyses` is `[]` and the runnable path is the **optimizer
  projection over the static `testbenches/` decks** (the pattern `amp_004_folded_cascode` uses via
  `testbenches.legacy/`). The `drv` class `templates` declare the analysis vocabulary for when a
  bipolar assembler lands. Each deck `.include`s `testbenches/dut.spice` (the `.subckt` form of the
  DUT) and sets the `x_dut_*` knobs via its own `.param` block, which the optimizer rewrites.
- **No `{derived: active_area}` / gm-ID.** Those count MOS refs only; skip for a bipolar core
  (paper core area 0.011 mm², recorded in the standalone repo).
- **Sizing `log_scale`.** The §3 tail/R_E/C_deg knobs are intended log-scale, but the analog-db
  `sizing.yaml` schema carries no `log_scale` flag, so the generated `project_setup.yaml` dut_params
  are linear-bounded here (apply the log domain platform-side if wanted).

**Live-validated (2026-08-10).** All six decks run on ngspice-45 + the IHP PDK and reproduce the
EIC golden to the last digit — LSB/MSB gain 3.09/9.06 dB, S11 −10.88, S22 −14.75, power 190.96 mW,
swing 2.916 Vpp, canary I_C 7.96 mA. The golden nominal is recorded as the **baseline design point**
(`scoreboard/ihp-sg13g2/2a531e0f02.json`): **11/11 specs pass**, Pareto-marked, `power_w` 0.191 W.
Two deck fixes were needed and are in place: the degeneration cap is written `{x_dut_cdeg_ff*1f}`
(a plain `{…}f` unit suffix leaves a stray `f` token in ngspice; the femto-multiply form parses in
*both* ngspice and the area evaluator), and `swing_vpp_diff` is measured as 2×|fundamental phasor|
(the golden/`_dft_bin` convention, matching the S21 decks) rather than raw peak-to-peak, which
under-reads a compressing output. `status` stays `generated` until the harness gains a bipolar
**T3/T4 sim lane** (the recorded point is a design point, not a harness-run conformance pass).

## Physical design — layout-001-inductorless-cascode

The first *physical* design of this block lives at
[`pdk/ihp-sg13g2/layout-001-inductorless-cascode/`](pdk/ihp-sg13g2/layout-001-inductorless-cascode/)
— a parametric **gdsfactory** floorplan on the IHP HBT PCells with the full
signoff flow (KLayout **DRC + LVS**, **kpex** 2.5D extraction, pre/post-layout
ngspice AC). It establishes the analog-db per-circuit-per-PDK
`layout-<NNN>-<slug>/` convention (a self-describing `layout.yaml` manifest;
discover/drive it with `analog-db layout list|show|run`). All three DUTs are
DRC/LVS-clean and reproduce the source-repo signoff to the last digit; the
catalogued **pam4** DUT passes all 8 post-layout specs at the signed-off point
(MSB 8.25 dB, LSB 2.27 dB, S11 −10.03, S22 −10.14, swing 2.21 Vpp, 179 mW,
7552 µm²).

Its `optimize_cosize.py` is the **layout-aware sizing loop** — the co-optimization
showcase: it searches the shared electrical knobs (this circuit's `sizing.yaml`,
the single source of truth) and the layout floorplan knobs *jointly*, hard-gated
on DRC/LVS and scored on the **extracted** (post-kpex) design. It surfaces that
the golden *schematic* sizing is post-layout-infeasible on S11 (−9.66 dB after
extraction) until R_E↑ / C_deg↓ recover it — the same correction the manual RF
review found. See that entry's `README.md` / `layout.yaml`.

## Why this is a good score-shaping case study

Heterogeneous, simultaneously-tight constraints (dB gain, dB return loss with a ≤ goal, mW
power at 0.5 % margin, V swing) across mixed units — the regime where per-spec `error_type` /
`range` normalization and the penalty→reward landscape are measurable. And a **known-good answer
with a twist**: the published schematic labels R_C = R_B = 100 Ω while the thesis (and matching
the 50 Ω/side reference) says 50 Ω; a black-box search over the 25–100 Ω range should
*rediscover* 50 Ω from the S11/S22 specs alone.
