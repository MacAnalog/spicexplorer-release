# layout-001-inductorless-cascode

**First layout entry in the analog-db corpus** — and the template for the
versioned, per-circuit-per-PDK physical-design convention:

```
circuits/<circuit>/pdk/<pdk>/layout-<NNN>-<slug>/
```

`<NNN>` is a monotonic layout revision, `<slug>` names the physical approach. A
circuit-PDK pair may carry several `layout-*` revisions side by side (a future
inductor-peaked floorplan would land as `layout-002-…`). The self-describing
[`layout.yaml`](layout.yaml) manifest is the machine-readable contract; this
README is the human guide. See the circuit-level
[`../../../README.md`](../../../README.md) for the block itself.

This entry is the parametric **gdsfactory** layout of the inductorless 96 Gb/s
PAM-4 SiGe:C-HBT driver (`drv_001_pam4_sige_dac`) on IHP SG13G2 — the *first
physical design* of the block (the EIC reference had none). Ported from the
standalone repo `github.com/JPPhotonics/agentic-design-pam4-driver-ihp130`
(`layout/` + `testbenches/driver_lib.py`, vendored here) and re-validated live.

## How the harness sees it

The analog-db verify tiers (T0–T2) validate only named YAML by path, so they do
**not** walk this subtree — nothing here is schema-checked or byte-drift-guarded.
It is discovered and driven through the additive harness surface:

```
analog-db layout list [--circuit ID]
analog-db layout show --circuit drv_001_pam4_sige_dac
analog-db layout run  --circuit drv_001_pam4_sige_dac --step {generate|signoff|pex|cosize} -- <args>
```

(backed by `Circuit.layouts()/layout_dir()/layout_manifest()` in `model.py`).
The `run` step inherits your environment — set the tools up first (below).

## Files

| file | role |
|---|---|
| `layout.yaml` | **manifest** — convention, toolchain, `knob_map`, signed-off point |
| `gen_layout.py` | parametric generator: `LayoutParams → dut_<d>.gds` + LVS/kpex/sim netlists (from one device model, so layout & netlist can't drift) |
| `signoff.py` + `pdk_runner/` | KLayout **DRC + LVS** via the PDK's own decks (vendored, engine-agnostic) |
| `pex_sim.py` | **kpex** 2.5D extraction + pre/post-layout ngspice `.op/.ac` |
| `driver_lib.py` | vendored bench engine (power-wave S21/S11/S22; writes the mandatory `.spiceinit`) |
| `optimize_layout.py` | floorplan-only nevergrad loop at fixed sizing (upstream) |
| **`optimize_cosize.py`** | **the showcase** — JOINT schematic + floorplan co-opt (below) |
| `render.py` | GDS → PNG with the IHP layer props |
| `LAYOUT_REVIEW.md` | pre-tapeout flags (open items) |
| `out/` | generated: text netlists + `pex_report.yaml` + PNGs are tracked; `*.gds`, `signoff/`, `pex/*/` rebuild (gitignored) |

Three DUTs: `lsb` (1 gain cell), `msb` (2 cells), `pam4` (the catalogued 2-bit
DAC, `pam4drv_pam4_lay`).

## EDA tool setup (important)

The flow needs **two** KLayout builds:

- the pip **`klayout` module** (gen / DRC / our-LVS / render), plus
  `gdsfactory>=9`, `ihp-gdsfactory==0.2.7`, `nevergrad`;
- **`kpex>=0.3.12`** (klayout-pex) for 2.5D extraction, which drives a **KLayout
  *executable* built with Ruby ≥ 2.6** for its internal LVS deck (`model[1..]`
  endless-range) — an rpm-shim KLayout with Ruby 2.5 fails with a syntax error.

Wire them via environment (all PDK paths resolve from `$PDK_ROOT`):

```sh
export PDK_ROOT=/path/to/pdks PDK=ihp-sg13g2            # dir containing ihp-sg13g2
export KPEX=/path/to/kpex                                # else resolved from PATH
export KPEX_KLAYOUT_EXE=/path/to/ruby2.7-klayout         # the LVS-capable KLayout
```

ngspice-45+ is required (`ngbehavior=hsa` is mandatory — the HBT silently
conducts 0 A otherwise; `driver_lib` writes the `.spiceinit`). See
`layout.yaml → requires`.

## Run it

```sh
# one DUT: layout -> DRC/LVS -> kpex -> pre/post AC
python gen_layout.py --dut pam4 --out-dir out
python signoff.py    --dut pam4
python pex_sim.py    --dut pam4 --mode CC        # -> out/pex_report.yaml

# the layout-aware sizing loop (joint schematic + floorplan co-opt)
python optimize_cosize.py --dut pam4 --budget 12 --out-dir cosize_out
```

## The layout-aware sizing loop (`optimize_cosize.py`)

This is the TCAS-2026 showcase. Unlike `optimize_layout.py` (floorplan only, at
fixed sizing), `optimize_cosize.py` searches the **schematic sizing knobs** and
the **layout floorplan knobs** *together*, scoring every candidate on its
**post-extraction** metrics — so schematic and physical design are co-optimized
against the same kpex netlist:

```
 schematic sizing knobs         floorplan knobs
 (../sizing.yaml, SHARED)       (this entry)
            \                    /
             nevergrad joint search
                     |
   gen_layout -> DRC + LVS (HARD GATE) -> kpex 2.5D -> ngspice .op/.ac
                     |
   score = Σ w_spec·hinge(post-layout spec)  +  w_area·area/area_ref
```

The electrical knobs and their bounds come from the circuit's
`pdk/ihp-sg13g2/sizing.yaml` (the single source of truth — see
`layout.yaml → knob_map`): `x_dut_{nx,re,rc,rb,cdeg_ff}` re-derive LayoutParams
geometry; `x_dut_{itail_ma,vcasc,vcm_in}` set the bench operating point. Every
candidate is DRC/LVS-gated, so the optimizer only ever trades *legal* layouts.
The score is a heterogeneous, mixed-unit hinge sum (dB gain, dB return loss with
a ≤ goal, GHz bandwidth, mW power) — the regime where the score-shaping study
lives.

**Live finding (recorded in `cosize_out/`).** Seeded from the golden *schematic*
sizing, the loop immediately surfaces what the schematic hides: post-extraction
msb **S11 = −9.66 dB fails the ≤ −10 dB spec** (every other spec passes). The
feasible region is *narrow and straddles two competing specs* — raising R_E lowers
S11 but also drops the gain (a recorded trial reached S11 −11.69 dB with the gain
collapsed to 4.9 dB), so the feasible band sits at R_E ≈ 3.2 Ω: the manual-review
needle in `layout.yaml → signed_off_point` (S11 −10.03, gain 8.25, each within
~0.05 dB of spec), which this flow reproduces. Naive weights at a modest live
budget did **not** converge onto that needle — a tight S11 ↔ gain feasible region,
gated by DRC, is exactly the landscape whose penalty→reward *shape* the
score-shaping study addresses. Full write-up: `layout.yaml → co_opt_study`.

## Validation (2026-08-10, live)

All three DUTs generate DRC/LVS-clean and reproduce the source-repo signoff to
the last digit. The catalogued **pam4** DUT at the signed-off point
(`gen_layout.FINAL_LAYOUT`/`FINAL_BIASES`, kpex-CC, tt):

| metric | post-layout | spec |
|---|---|---|
| MSB gain | 8.25 dB | ≥ 8.2 |
| LSB gain | 2.27 dB | ≥ 2.2 |
| DAC weight | 5.98 dB | ≈ 6.0 |
| MSB f₃dB | 58.8 GHz | (≥ 50) |
| S11 (worst) | −10.03 dB | ≤ −10 |
| power | 179 mW | ≤ 192 |
| area | 7552 µm² | — |
| DRC / LVS | pass / pass | — |

S22 (−10.14 dB) and swing (2.21 Vpp) are the notebook-03 `driver_lib` benches
(out of the fast co-opt loop). `status: signed-off` in `layout.yaml`; the entry
stays a *design* record — the harness has no bipolar layout conformance lane yet.
`LAYOUT_REVIEW.md` lists the open pre-tapeout items.
