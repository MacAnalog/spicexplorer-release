# PAM-4 driver — parameterized gdsfactory layout (IHP sg13g2)

Programmatic, **optimizer-ready** layouts for the three driver DUTs
(`../dut/dut_{lsb,msb,pam4}.spice`), built with **gdsfactory +
[ihp-gdsfactory]** on the pattern of the platform 5T-OTA lane
(`examples/layout/ihp-sg13g2/5t_ota_gf/`). First HBT layout in the
ecosystem.

| DUT | Cells | Devices | Size (default params) | DRC | LVS |
|---|---|---|---|---|---|
| `lsb` | 1 | 4 HBT + 5 R + 1 C | 43.8 x 60.1 um (2633 um2) | PASS | PASS |
| `msb` | 2 | 8 HBT + 8 R + 2 C | 77.6 x 60.1 um (4665 um2) | PASS | PASS |
| `pam4` | M0\|L0\|M1 | 12 HBT + 12 R + 3 C | 116.2 x 62.9 um (7311 um2) | PASS | PASS |

Signoff: KLayout DRC (`--no_density`, geometrically clean) + KLayout LVS
("Netlists match") through the PDK's own decks, per DUT.

## Files

```
gen_layout.py       LayoutParams (25 free constants) -> GDS + netlists
signoff.py          DRC + LVS wrapper (per DUT)      -> out/signoff/
pex_sim.py          kpex 2.5D PEX + pre/post ngspice .op/.ac comparison
optimize_layout.py  nevergrad loop: gen -> DRC/LVS gate -> PEX -> sim
render.py           GDS -> PNG (IHP layer colors)
out/                dut_<d>.gds/.png, dut_<d>_{lvs,kpex,sim}.spice,
                    signoff/, pex/, pex_report.yaml
```

Run (conda `ai_env`; kpex from the `pex` env is invoked directly):

```sh
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
python gen_layout.py --dut all          # generate GDS + netlists
python signoff.py                       # DRC + LVS (all PASS)
python pex_sim.py --dut all             # PEX + pre/post metrics
python optimize_layout.py --dut lsb --budget 20
```

## Floorplan (one gain cell)

Mirror-symmetric about the cell axis; signal flows bottom -> top:

```
vcc rail (TopMetal2) ── RCp/RCn (rsil) ── outp/outn buses (TopMetal1)
        cascode row:   Q3 ──────── Q4     (vcasc strap on the B bars)
        c1/c2 nodes:   wide short Metal2 plates (input C bar -> casc E plate)
        input row:     Q1 ── Cdeg (cmim, center) ── Q2
        emitters:      Metal2 straps -> RE (rsil) -> tail bus (port)
        inputs:        B-bar drops (M1) -> input buses (Metal3) -> RB -> vcmb
        substrate:     p-sub guard ring (`sub`) + tap columns between cells
```

RF practices baked in: differential mirror symmetry; the Miller-critical
cascode nodes are <3 um long full-width M2 plates; outputs rise straight to
thick TopMetal1 buses and the 48 mA vcc rail is TopMetal2; via *arrays* on
every DC path; each pcell's substrate is ringed and tapped (isolation +
well-defined `sub` reference). All spacings/widths are `LayoutParams`
fields — the optimizer's search space.

Tails are **ports** (`tail`, `tail0/1`, `tlsb0/tmsb0/tmsb1`): the ideal
VCCS tail current source stays in the testbench, exactly like the schematic
DUTs, so layout and schematic characterizations stay comparable.

## Devices (all foundry-recognized, LVS-extracted)

- **npn13G2 Nx=3** via the ihp-gdsfactory *PyCell* wrapper
  (`cells2.npn13G2`) — pass `emitter_width=0.07` (the wrapper's 0.7 um
  default draws an unrecognizable emitter). Two thin Metal1 patch overlays
  per device fix the PyCell's CntB.h1 (M1 enclosure of ContBar) violations.
- **rsil** for RE/RC/RB. Sizing accounts for the **contact-head resistance
  (~4.5 ohm*um per end)**: `l = (R*w - 9)/7`. That forces `re_w >= 4.4 um`
  for the 2.5-ohm RE (default 5.0 -> exactly 2.5 ohm total). Lengths snap
  to 0.01 um (the cell halves them internally; 0.005 offgrid otherwise).
- **cmim** Cdeg: drawn 2.87 um -> extracted/effective w = drawn + 0.72
  (MIM layer) -> 19.9 fF on the cap_cmim model. Bottom plate (Metal5) on
  e1, top plate (TopMetal1) on e2 — single-cap asymmetry noted; both e
  nodes are low-impedance degeneration points.
- Guard ring is hand-drawn (Activ+pSD+Cont+M1); the ihp-gdsfactory
  `guard_ring` cell violates Cnt.b at its corners.

## Generated netlists (device records == drawn geometry, by construction)

- `dut_<d>_lvs.spice` — KLayout-LVS reference: primitive `Q/R/C` cards
  (`Q.. npn13G2 AE=0.063p PE=1.94u M=3`, 2-node `R.. rsil w= l=`,
  `C.. cap_cmim W= L=`).
- `dut_<d>_kpex.spice` — same, but 3-node rsil (kpex's deck models poly
  resistors as 3-terminal).
- `dut_<d>_sim.spice` — ngspice subckt on the PDK models (X-cards).
  Requires `.spiceinit` with `osdi .../r3_cmc.osdi` (rsil is an OSDI
  device) — `driver_lib.spiceinit_lines()` now adds it automatically.

## PEX + post-layout results (defaults, typ corner, kpex 2.5D mode CC)

`pex_sim.py` compares three tiers: the *schematic* golden numbers live in
`../results/`; here **pre** = same devices on PDK R/C models, no wiring;
**post** = + extracted parasitics:

| DUT:path | S21 LF (dB) | f3dB pre -> post (GHz) | S11 worst pre -> post (dB) | P (mW) |
|---|---|---|---|---|
| lsb:in    | 2.94 | >100 -> 96.3 | -16.5 -> -15.2 | 63.6 |
| msb:in    | 8.92 | 69.4 -> 58.4 | -11.0 -> **-9.5** | 127.3 |
| pam4:lsb  | 2.95 | 92.6 -> 66.1 | -16.5 -> -13.8 | 191.0 |
| pam4:msb  | 8.92 | 66.8 -> 51.1 | -11.0 -> **-8.9** | 191.0 |

Takeaways (the case-study motivation): with the *nominal* schematic sizing,
layout parasitics alone push the MSB/PAM4 input reflection **below the
-10 dB spec** and cost the MSB path ~16 GHz of bandwidth — the layout
constants and the electrical sizing have to be co-optimized, which is what
`optimize_layout.py` provides: DRC/LVS hard-gated, real kpex+ngspice in the
loop, objective

    score = w_area*area/area0 + bw_loss/loss0
            + w_s11*max(0, S11_post - spec)      # hinge, dB over -10 dB

with the resistor *widths* (`re_w`/`rc_w`/`rb_w`) in the search space —
their lengths always re-derive from the PDK rsil model (R = 7*l/w + 9/w,
contact heads included), so every candidate holds the resistance target
while trading resistor area and parasitics. The real rsil/cmim models also
shave ~0.16 dB of LF gain vs the ideal-R schematic (silicided-poly heads,
cap tolerance) — visible in the `pre` column vs `../results/`.

## Known workarounds / tool gaps

- **kpex cannot extract the MIM cap** (its ihp tech tables have
  `cmim_top = <TODO>` -> KeyError). `pex_sim.py` strips the MIM/Vmim/MemCap
  layers from a GDS copy (plates keep coupling as plain metal), removes the
  C cards from the kpex schematic, and re-inserts the intentional
  `cap_cmim` devices into the converted netlist (cell-wise, via the RE
  resistor terminals). Validated for mode CC.
- kpex needs `KPEX_KLAYOUT_EXE` with Ruby >= 2.6
  (`~/local/klayout-py311/klayout-batch.sh`, as in the OTA lane).
- ihp-gdsfactory bugs found here: `cells.npn13G2` duplicate ports for
  Nx>1; `cells2` PyCell rsil crashes (KeyError 'EXTBlock');
  `emitter_width` default 0.7 should be 0.07; `guard_ring` corner Cnt.b.
- EM note: via arrays are sized for DRC, not signoff-grade EM; the RC
  path (24 mA) gets stack_w=2.0 arrays — widen `stack_w`/`rc_w` for a
  tapeout-grade rail budget.

[ihp-gdsfactory]: https://github.com/gdsfactory/ihp

## 2026-08-09 (v2): full-spec resize + RF layout fixes — ALL 8 SPECS PASS

The first signoff (notebook 03) caught the v1 optimum (nx=2, R_C=70)
failing **S22** (−8.3 dB) and **max swing** (2.07 Vpp) — both absent from
the v1 objective. An expert RF layout review (routing / placement / metals /
process variation / symmetry / reflection) plus a directed probe ladder
produced the v2 configuration, now baked in as `gen_layout.FINAL_LAYOUT` +
`FINAL_BIASES`:

* **Electrical (back to the paper's nominal topology):** nx=3,
  tail 15 mA/cell, R_C=50 Ω, R_B=48 Ω, R_E=3.2 Ω (w=4.5), C_deg=16 fF,
  V_casc=3.35 V. R_E↑ is the S11 closer: series feedback shrinks the
  effective input C (the model card scales with Nx only — see notebook 03
  §0b for why `emitter_width=0.07` is exactly the modeled device).
* **Input network:** `input_feed="center"` (H-tree: R_B columns on the
  centreline, symmetric branches — halves the input line per branch,
  zeroes M0/M1 skew), `in_bus_layer="Metal4"`, `in_bus_gap=3.0`,
  `in_off=2.2`, `drop_layer="Metal2"` (base drops descend on M2 with the
  M1→M2 via below the bar). msb S11 at nx=3: −8.8 → −10.03 dB.
* **Output network:** `out_gap=8.0` (differential sidewall C counts double),
  `out_w=1.64` (TM1 min), `w_out=1.5`, `rc_sep=4.0`, `stack_w=1.7`
  (stack() now clamps pads per-via, e.g. TopVia2 → 1.9), bus overhang
  ±1.5 µm, row compaction `gap_x=6.0` / `cell_gap=5.0`.
  S22 at R_C=50: −8.4 → −10.14 dB. kpex C-budget: the summing-bus network
  carried ~14 fF/side (kpex charges TM1 37.4 aF/µm of *edge* to substrate
  unconditionally, so length is what matters) + ~14 fF/side of cascode
  junction C that no layout removes.
* **Extraction cross-check:** kpex RC mode (2134 R cards) reproduces every
  CC metric to 0.01 dB (needs `.options rshunt=1e10` — the split nets
  leave floating R-islands).
* **Signoff:** DRC + LVS PASS on all 3 DUTs; pam4 99.6 × 75.8 µm
  (7552 µm²). Post-layout (kpex CC, wrapped driver_lib benches):
  LSB/MSB gain 2.27/8.25 dB, weight 5.98 dB, BW 58.8 GHz, S11 −10.03 dB,
  S22 −10.14 dB, swing 2.21 Vpp, power 179 mW — all specs met.

**Pre-tapeout flags from the layout review (open):** vcasc rail bypass
(≥1 pF/cell cmim) + 20–50 Ω odd-mode series R per cell (six cascodes share
a thin M1 rail — stability); EM/current-density pass on via stacks and the
TM1 bus (single TopVia2 on 20+ mA paths); ground cage (via-stacked ring
≥3 µm, tap fence ≤5 µm pitch, stitched sub rail); HBT/rsil/cmim dummies at
row ends (interdigitation is not available for the fixed HBT PyCells —
translation-symmetric placement is kept deliberately); R_E is ~2/3
contact-head resistance at w=4.5 (split into parallel units for matching);
group-delay variation + extracted-rail stability (K-factor, odd-mode)
before tapeout; 2-row floorplan held in reserve (halves the summing bus →
~+1.5 dB more S22 margin) if larger margins are required.

Before/after figure of the v2 optimization: `before_after.png`
(regenerate with `compare_layouts.py`).
