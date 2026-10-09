# Layout review — `ldo_ihp_capless`, as ported

What an independent reviewer said about this drawing, and what a later independent sign-off did
with it. Two passes, both in the source design repo (@ `40cad45`), both by
someone other than the designer:

| pass | artefact | verdict |
|---|---|---|
| **review-004** — layout review, 27 findings | `layout/ldo_ihp_capless/REVIEW.{md,yaml,png}` | **PASS with majors** |
| **the sign-off pass** — five claims | `layout/ldo_ihp_capless/SIGNOFF.md` | **SIGNED — 8/8 spec lines at tt / 27 °C** |

(The source repo numbers that sign-off inconsistently — `SIGNOFF.md`'s own title says round 5,
`REPORT.md`'s round table calls it round 6. It is one pass either way; this file calls it "the
sign-off".)

The two do not simply agree, and the order matters: review-004 graded the drawing, then the
sign-off re-measured it on a fixed extraction and moved the row of record from the CC extraction
to the stitched RC one. Several review-004 findings are answered by that later run. This file
says which, so a reader of `REVIEW.yaml`'s `verdict: open` column does not carry a closed item
forward — and so nothing that is still open gets quietly dropped either.

## Reproduced here, before anything was believed

Every claim below was re-run in THIS entry (`analog-db layout run`, 2026-09-05), not copied:

| | source repo (the signed run) | this entry |
|---|---|---|
| GDS rebuilt from the committed generator | `sha256 e638b89e…` | **`e638b89e…` — byte-identical** |
| bbox / area | (−73.50, −135.50)–(137.64, 74.15), 44 266 µm² | **identical** |
| current density | 30/30 checked, 0 violations, worst 0.836× | **identical** |
| DRC (`sg13g2_maximal`, `--no_density`) | 0 violations | **0, `violations_per_rule {}`** |
| LVS (`--combine_devices`, reference from `netlist_ref.py`) | matched | **matched, `unmatched {}`** |
| LVS reference netlist | `sha256 f573b653…` | `117c9f7c…` — the same device lines, differing in **one header comment**, which names `netlist_ref.py`'s new home |

The generator here reads this entry's own `../netlist.spice` and `../sizing.yaml` instead of the
source repo's. That the GDS comes out byte-identical is the proof the port did not move a device:
the lowered netlist emits its cards in a different (sorted) ORDER, and the drawing does not care,
because every device is looked up by name.

## Findings still open after both passes

**1 — the pooled dropout budget is missed (from sign-off §3.4; supersedes review-004 F1's ruling
without closing F1's own concern).** `brief.json`'s `dropout_pool` prices the two supply nets at a
quarter of S4's margin:

> `10.34 × R(vdd) + 8.65 × R(vout) ≤ 23.83 mV`

Scored on the record row the layout spends **29.99 mV — 1.26× the pool**, i.e. 3.00 Ω pooled at
the 10 mA dropout point. Each net's INDIVIDUAL budget is met (1.57 Ω against 2.31 Ω on `vdd`,
1.52 Ω against 2.76 Ω on `vout`); the shared pool they both draw on is not. What is over is
exactly what does not divide by the 39 pass-array columns: the common **TopMetal1 strap**
(0.59 Ω) and the **Via2–TopVia1** stack (0.75 Ω). Widening the strap and multiplying the via array
is the designer's action, and the knobs are already in `layout.yaml` (`pwr_w`, `pwr_stitch`,
`pwr_riser_vias`).

**This is a discipline guard-band, not a spec.** S4 measures **134.66 mV against a 200 mV
bound — 65.3 mV, 33 % of margin** — and all eight spec lines pass at the record row.

**F1 (major, `pex`) — the extracted series-R VALUES, as distinct from the mesh topology.** The
reviewer solved the stitched mesh as a nodal network and read ~41 Ω of common element in front of
the pass array on a path whose drawn TopMetal1 is 0.59 Ω, i.e. terminal/via values 70–140× the
metal. The topology half of the finding is closed (see below); the values half is not, and it is
upstream of this cell — the same defect `rail_solve.py` exists to work around, by solving the
drawn copper instead of reading the extractor. Read it alongside sign-off §3.4, which measures the
pooled 3.00 Ω **through the benches** rather than out of the mesh: the two numbers are an order
apart, and only the bench-measured one carries a verdict here.

**F3 + F16 (major, `objective`) — the margin is measured, its distribution is not.** F3 measured,
in the assembled cell, that S7's sensitivity to `gate` to-rail capacitance is a smooth 0.44 mV/fF with no
step, crossing the 150 mV line at about +45 fF against 34.45 fF drawn — so the drawn value sits at
~43 % of what the net can carry, and the brief's "12 fF budget with a step" is a gate-only
artefact. F16 is why that is not yet a closure: whether those 22.4 mV of margin survive ss/−40 and
mismatch is unmeasured. Sign-off §5 records the corner rows that DO exist and are decisive —
**S5 fails at ff/125 (58.37 µA vs 50)** and **S7 fails at ss/125 (171.09 mV) and, pre-extraction,
at sf/−40 (301.81 mV)** — and separates them honestly: `i_q` is a dc quantity, so ff/125 is purely
schematic (pre and post agree to five figures); ss/125 is a schematic failure that extraction
worsens by 18.3 mV; sf/−40 is one that extraction *repairs*, 301.81 → 106.12 mV. The post-layout
corner sweep and the mismatch Monte Carlo are the last measurements this cell needs.

**Since review-004 the corner half has moved, and this entry does not carry it.** The source
repo's `experiments/007-post-layout-corners` now runs the EXTRACTED netlist over the five MOS
corner bundles × −40 / 27 / 125 °C with the schematic row beside it as a control, so "post-layout
is tt / 27 only" is no longer true *of the cell* — it is true of **everything catalogued here**,
which is one tt / 27 row per scorecard. What is still not run anywhere is a **Monte Carlo over the
PDK's own mismatch distributions** (selecting the `*_mismatch.lib` sections would mean editing the
certified `corners.yaml`, a schematic-lane change), and **corners × mismatch jointly** — nobody has
run a class's mismatch offset *at* a failing corner such as ss/−40 or ff/125, which is exactly
where the two could compound.

**F13 (minor, `reproduce`) — pin labelling is not one-per-declared-edge.** `fb` was fixed and sits
on the left edge at (−62.600, 12.830). `vref` is still labelled at (8.810, 13.530), **71 µm inside
the cell**, where PLAN A1 declares a left-edge pin. And `vdd` now carries **two** labels — Metal1
(8/25) at (−65.500, 43.830) and TopMetal1 (126/25) at (−65.500, 69.550) — which is the same
ambiguity that was raised for `vss` and closed there (exactly one label, at (−70.000, −134.000)):
which label is the pin decides what the series resistance to it is. Either drop the Metal1 one and
move `vref` to the edge, or amend the plan to call `vref` an internal probe.

**F15 (note, `pex`) — the MIM plate swap, agreed and deferred.** Swapping `XCFF`/`XCC` plate order
takes a few fF off `fb`, worth about +0.3° of phase margin by hand model. It is a certified-netlist
edit plus a re-freeze; the re-certification would have been the cheap moment and was not taken.
Costs nothing to include at the next re-freeze.

**F18 (minor, `drc`) — the waiver list is itemised, `--density` is still not run.** All twelve
waived rules are named (`AFil.g`, `AFil.g2`, `GFil.g`, `M1.j`–`M4.j`, `M1Fil.h`–`M4Fil.h`,
`TM2.c`); fill is met at chip assembly and is out of scope by plan. What is unverified is whether
the waived SET grew with a floorplan 4.8 % larger carrying two new wide straps. The reviewer's own
run was `--no_density` too, and says so. `signoff.py --density` runs it.

**F26 (minor, `pex`) — the record is kept, the gate is only half built.** `_pex_record()` now
carries `mesh_connected` and the whole `mesh` dict, and `pex_gate()` refuses an RC row whose mesh
is open — that half is done and is what the table below credits. F26's fix note asked for a second
condition as well: refuse a row where a **stub net carries a series-R budget**. `pex_gate()` never
reads `mesh["n_stub_nets"]`; the count is printed to the stage log and stored in the record, but
nothing refuses on it. On this cell 19 nets are stubs (the 18 divider nets and `lp_brk`) — a mesh
with nothing measured through it — and none of them carries a scored metric, so no number here is
affected. The gate is what would catch it if one ever did.

**Mismatch (sign-off §4) — recorded, not closed.** `brief.json` prices `ea_nmos_load` at 1.0 mV of
tolerated ΔV_T against a PDK 1σ of 1.6468 mV (√2 · A_VT/√(W·L), A_VT = 2.0 mV·µm from
`sg13g2_moslv_mismatch.lib`, W·L = 2.95 × 1.0 µm on the whole device), and its own out-of-box ΔV_T
at 2.0 mV — so P(ΔV_T > 2.0 mV on the dangerous XM3 side) ≈ **11 % of dies**, one-sided, from one
class alone and before any parasitic. `bias_p_group` is ≈ **9 %**. The sign-off ruled the
designer's numbers are the ones that describe the cell as built. The two sub-σ classes are priced
by single-class injection, not by a distribution: this is the Monte Carlo half of F16, and it is
open.

## Findings the later run closed

| # | review-004 said | what closed it |
|---|---|---|
| **F25** | kpex emits no `[Pin]` markers although the labels are drawn | sign-off §3.1 on the platform fix @ `6c07a02`: **15/15 named ports anchored on a `[Pin]` node**; the 18 proxies are anonymous `$nn` nets |
| **F26** (record kept, gate only half built — see the open findings above) | the sign-off record drops `mesh_connected` / `mesh` | `_pex_record()` carries both, and `pex_gate()` refuses an RC row whose mesh is open. Recorded on the signed run (`out/pex/rc_netlist.sha256`'s header): 3096 mesh nodes, 3101 zero-ohm edges contracted, `n_zero_r_cards 0`, 220/243 device pins on the mesh, 0 open nets |
| **F27** | the stitched netlist is not the one the benches pick up | `select_pex_netlist()` — vendored here in `pex_sim.py` — reads the PEX stage's own record, prefers `*_stitched.spice`, prints which file it measured, and REFUSES two unrelated netlists instead of choosing one silently. `test_builder.py` carries seven cases for it |
| **F1 (topology half)** | the RC mesh is an electrical island | mesh stitched and verified connected; the values half stays open above |
| **F9** | the `vss_active` budget is written on the wrong quantity | re-solved: the COMMON series element pin → riser top is **≈ 4.7–4.8 Ω** (0.29× of the 16.48 Ω budget), not the 20.88 Ω worst-active-device figure the budget was scored on — two independent solves, the reviewer's Laplace flood-fill at 4.84 Ω and `rail_solve.py`'s at 4.743 Ω, agreeing to ~2%. Sign-off §2 measures what it costs, on its own 4.74 Ω: PSRR 70.09 → **67.33 dB** — still 27.3 dB clear of the 40 dB line. `rail_solve.py` is vendored here so that solve is repeatable |
| **F19** | — | **FIXED before the port**: the certified deck IS the drawn device set (XMP with `ng` fingers, common-centroid halves, resistor chains), verified by re-measurement. It is why `netlist_ref.py` can derive the LVS reference from the netlist instead of a table of its own |

Eleven further findings (**F2, F4–F8, F10–F12, F17**) were fixed in the source repo before this
port and are listed as `fixed` in `REVIEW.yaml`: 40/40 documented knob endpoints build clean and
off-grid sizing is refused; the current-density table describes the drawn vias and contacts; all
seven common-centroid pairs XOR to 0.000 µm² with equal via counts; the `fb` track shortened
107.15 → 79.57 µm and the measured phase margin moved with it; `lp_brk` is escaped and labelled at
the output-pin edge; every net is listed under one accounting convention; the dead knob is deleted
and the hidden one promoted; dummies are sized to their own neighbour; the obstacle map is
layer-aware and its regression fails without it.

## Not ported

**F14, F20, F21, F22, F23, F24** are findings about the source repo's own documents and workflow —
an empty `sizing` block in its `design.json`, a tolerance printed as 6 mV where the brief says 5.0,
a README row describing the opposite of the code, iteration snapshots that are not self-contained,
RC bench counts in its REPORT that do not reproduce, and a `signoff.json` overwritten by a partial
re-run (fixed: `_write_record` merges). They have no counterpart in this entry, which carries no
`iterations/`, no REPORT and no ledger. F24's fix travelled with the vendored `signoff.py`.

## At a glance, from the reviewer's own reading of the rebuilt GDS

`ea_in_pair` is dummy/XM1a/XM2a/XM2b/XM1b/dummy at x = 0.29–22.19 — ABBA, both centroids at
x = 11.24. `ea_nmos_load` is ABBA with both centroids at x = 27.94. `bias_n_group` is ABC·CBA with
all three centroids at x = 85.96. All seven matching classes XOR to 0.000 µm² at device bbox +
1.2 µm with equal Via1 counts. Dummies sit at both ends of every device row, each sized to its own
neighbour. All five well/substrate tap regions merge to ONE polygon WITH A HOLE — the rings
actually close. Resistors are on one 2.0 µm pitch throughout with tied dummies at each end. Straps
run at 0.836× J_max, 0.9835× worst over the 40-endpoint walk. Two blemishes, both findings above:
`XCOUT` has no MIM dummy ring (a declared, recorded plan deviation) and the pin labelling is F13's.
