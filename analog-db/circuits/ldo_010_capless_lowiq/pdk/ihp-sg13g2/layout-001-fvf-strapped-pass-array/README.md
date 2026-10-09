# `layout-001-fvf-strapped-pass-array` — the drawn cell

The physical design of `ldo_010_capless_lowiq` on IHP SG13G2: one parametric gdsfactory cell,
**44 266 µm²**, DRC-clean, LVS-identical to the entry's own certified netlist, extracted, and
re-measured on the entry's own 13 benches. Ported from
an agent-first design repo @ `40cad45`,
where it was independently reviewed (review-004, *PASS with majors*) and then independently signed
off (*8/8 spec lines at tt / 27 °C*). What is still open is in
[`LAYOUT_REVIEW.md`](LAYOUT_REVIEW.md); the manifest a tool reads is
[`layout.yaml`](layout.yaml).

The drawn cell keeps the name `ldo_ihp_capless` — it is the GDS top cell, the LVS cell and the name
kpex writes into its `.subckt`, and every signed-off artefact refers to it. The rename to the
accession id happens once, on the extracted block, inside `pex_sim.py`.

## The floorplan

```
vdd TopMetal1 strap  (top edge)                                  <- vdd pin
XMP island: nwell + ntap ring, the certified card's `ng` fingers, Metal2 combs
vdd Metal1 rail
row B: [nwell island "quiet": bias_p_group | ea_in_pair]  [nwell island "fvf": XMC XMCP XMD]
channel: one Metal1 track per internal net, every vertical is Metal2
row A: [XM5] [ea_nmos_load] [fvf_fold_n] [bias_n_group]           (one ptap ring)
vss Metal1 rail
passive band: [XR1/XR2 common centroid + XRB]   [XCC XCFF]   [XCOUT 2x2 array]
vss Metal1 rail (bottom edge)                                    <- vss pin
vout TopMetal1 strap down the right edge                         <- vout pin
```

`out/ldo_ihp_capless_labelled_scale.png` is that sketch drawn on the real thing: matched groups
with the pattern each is drawn in, dummies, guard rings, power straps, the pin frame and the 10 mA
load path, with a 50 µm scale bar. Nothing in it is placed by hand — it is
`spicexplorer_signoff.annotate` over `labels.yaml`, whose ranges are the generator's own placement
ordinals, and the file says how to audit them. `render.py` also writes an un-scale-barred variant
and a light-ground `_white` pair; only the two figures above are committed, because the four are
near-duplicates of one 830 kB raster.

**Routing discipline.** Device straps, channel tracks and rails are Metal1 (horizontal); every
inter-row connection is a Metal2 vertical with a Via1 pad at each end, at an x unique to that
terminal, and no Metal1 stub may cross a foreign net's Metal1. Guard-ring metal is claimed in the
same obstacle map, so a stub cannot walk out through a ring. That map (`router.py`) exists because
two overlapping same-layer shapes merge into one legal polygon: **a stub that walks through a
neighbour's gate bar is a short DRC cannot see.** `test_builder.py` builds that collision by hand
and asserts the allocator refuses it — it runs first in the sign-off chain, and it blocks.

## Files

| file | what it is |
|---|---|
| `layout.yaml` | the manifest — provenance, toolchain, generator/signoff entry points, the knob space with its ranges, and the signed-off point with BOTH post-layout rows |
| `gen_layout.py` | the generator (vendored `gen_ldo.py`). `build_full(LayoutParams, sizing) -> (Component, Builder)`; also writes the LVS reference and the power-path budget |
| `netlist_ref.py` | the single source of device identity: parses `../netlist.spice` + `../sizing.yaml`. **The generator has no device table of its own** |
| `router.py` | the per-net Metal1 obstacle map and Metal2 column allocator (no gdsfactory, so it is testable) |
| `test_builder.py` | the router's regression case, plus seven cases for the extracted-netlist selection |
| `signoff.py` | guards → build → render → current density → DRC → LVS → (PEX). DRC and LVS are gates, not report lines |
| `pex_sim.py` | the post-layout scorecard: netlist surgery, then this entry's own benches (vendored `postlayout.py`) |
| `rail_solve.py` | sheet-resistance solve on a drawn metal net — how the `vss` return and the strap resistances are known, since the extractor's own terminal/via values are not usable (LAYOUT_REVIEW, F1) |
| `render.py` | the plain and the labelled figures |
| `labels.yaml` | the annotation spec behind the labelled figure |
| `out/` | what a reviewer reads: the PNGs, the two post-layout scorecards, the prepared CC block, and the digest of the RC netlist behind the record row |

The **GDS is not committed** — it is regenerable, and `circuits/*/pdk/*/layout-*/out/*.gds` is
gitignored. Neither is the extracted netlist: a ~5 500-card extractor output is a rawfile, so
`out/pex/rc_netlist.sha256` carries its digest, its card census and its path instead.

## Running it

```bash
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2 SX_SCRATCH=$HOME/sx-scratch
analog-db layout show --circuit ldo_010_capless_lowiq
analog-db layout run  --circuit ldo_010_capless_lowiq --step generate
analog-db layout run  --circuit ldo_010_capless_lowiq --step signoff   # guards, build, CD, DRC, LVS
analog-db layout run  --circuit ldo_010_capless_lowiq --step render
analog-db layout run  --circuit ldo_010_capless_lowiq --step pex       # the 13 benches, extracted
```

Everything regenerable lands in `$SX_SCRATCH/ldo-adb/layout`; only the small text and PNG
artefacts come back here.

### Environment

Two interpreters, and the split is not cosmetic:

* **drawing** — `gen_layout.py` needs `gdsfactory` + `ihp-gdsfactory`. It re-execs itself under
  **`$LDO_GF_PYTHON`** (default `~/miniconda3/envs/ai_env/bin/python`) when they are missing, so a
  caller does not have to know which python draws.
* **sign-off and benches** — DRC / LVS / PEX are KLayout runsets and kpex, driven through
  `spicexplorer_signoff`, and the benches need `spicexplorer_analog_db` + ngspice ≥ 45. Run the
  CLI itself with an interpreter that has all of those — this repo's own venv already does. To
  build one: `uv sync --extra gds` in the platform workspace (the extra belongs to
  `spicexplorer-layout`), or any venv carrying `spicexplorer-signoff`, `spicexplorer-layout`,
  `klayout>=0.30` and `docopt` (the PDK's own `run_lvs.py` imports it).

`--step pex` needs no KLayout job at all when the recorded extraction is on the machine: it reads
the path in `out/pex/rc_netlist.sha256`. Re-extracting is `--step signoff -- --stages pex
--pex-mode RC`, which wants `$KPEX` and a KLayout executable built with Ruby ≥ 2.6.

That recorded path — and the `pex_netlist` field inside `out/scorecard_post*.json`, copied verbatim
from the certified repo, and the same field in `out/pex/scorecard.json`, which `pex_sim.py` writes
the same way — is **provenance, not an input**: it is a path on the machine
the sign-off was measured on, under a scratch root that predates this entry's own
`$SX_SCRATCH/ldo-adb/layout` (the digest records it `$SX_SCRATCH`-relative; the two scorecard
fields still carry it absolute, with the account written `/home/<user>/`). On any other checkout the file is simply absent, and `--step pex`
says so and names the re-extraction rather than reading a stale netlist. The digest beside it is
what actually identifies the extraction.

## What the sign-off measured

All eight spec lines pass on the **stitched RC** row of record, at tt / 27 °C:

| # | spec | bound | pre (schematic) | CC (ideal metal) | **RC — record** | margin |
|---|---|---|---|---|---|---|
| S1 | `v_out` no load | 1.176–1.224 V | 1.199499 | 1.199499 | **1.199498** | 23.5 mV to the low edge |
| S2 | `load_reg` 0.1→10 mA | ≤ 5 mV | 0.026 | 0.026 | **0.027** | 185× |
| S3 | `line_reg` 1.4→1.65 V | ≤ 2 mV | 0.056 | 0.056 | **0.056** | 36× |
| S4 | `v_dropout` at 10 mA | ≤ 200 mV | 104.671 | 104.671 | **134.663** | 65.3 mV |
| S5 | `i_q` no load | ≤ 50 µA | 33.80539 | 33.80539 | **33.76923** | 16.2 µA |
| S6 | `psrr` at 1 kHz | ≥ 40 dB | 70.007 | 70.093 | **70.062** | 30.1 dB |
| S7 | `v_undershoot` 0.1→10 mA | ≤ 150 mV | 115.057 | 127.560 | **129.533** | 20.5 mV |
| S8 | `pm_loop` at 1 mA | ≥ 60° | 72.506 | 69.301 | **69.328** | 9.3° |

**Two extractions, and which is which is the point.** The **RC** row (`out/scorecard_post_rc.json`,
kpex 2.5D with the mesh stitched) is the row of record. The **CC** row (`out/scorecard_post.json`)
is the same layout with every wire resistance set to zero, so the difference between them IS the
drawn metal: the whole **+29.99 mV** of dropout is series resistance, 3.00 Ω pooled across `vdd`
and `vout` at the 10 mA point. Read CC against the record row, never instead of it.

That 29.99 mV is also the entry's one open budget miss — the brief allowed 23.83 mV — and what is
over is precisely what does not divide by the 39 pass-array columns: the shared TopMetal1 strap and
the Via2–TopVia1 stack. See `LAYOUT_REVIEW.md`.

**Two things this table does not say.** It is **tt / 27 °C**, and the corners are not kind:
`i_q` fails at ff/125 (58.37 µA — purely schematic, since pre and post agree to five figures) and
`v_undershoot` fails at ss/125 (171.09 mV). Extraction is not the cause; at sf/−40 it is the cure,
moving `v_undershoot` 301.81 → 106.12 mV. And it is **nominal**: the mismatch distances are
recorded, not sampled. The source repo has since run the post-layout corner sweep
(`experiments/007-post-layout-corners`); a Monte Carlo over the PDK's own mismatch distributions
is still not run anywhere, and neither is a corner and a mismatch offset applied together.
