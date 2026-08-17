# Expert RF layout review — PAM-4 driver (IHP SG13G2), 2026-08-09

Independent review of the generated pam4 driver layout by an RFIC layout
expert agent, covering routing, placement, metal selection, process
variation, symmetry, and reflection/RF performance. Constraint respected:
HBT interdigitation is NOT available (fixed foundry PyCells; the diff pair
stays as discrete mirror-placed devices).

Status annotations (2026-08-09 pm): items marked **[DONE]** were
implemented in the v2 resize (see `README.md` v2 section and
`gen_layout.FINAL_LAYOUT`); items marked **[OPEN]** are pre-tapeout work.

## Headline findings

1. **S22 was never in the v1 optimization objective** — the failing spec
   was structurally unopposed (R_C=70 bought gain with output mismatch,
   `out_gap` sat on its lower bound). **[DONE]** — notebook 02 v2 scores
   all eight specs on the pam4 DUT.
2. **Output C budget** (validated against extraction): ~28 fF/side
   layout-added (half of it outp↔outn sidewall coupling — TM1's 2 µm
   thickness at 1.8 µm gap — which counts DOUBLE differentially), on top of
   ~12-14 fF/side of cascode junction C. Model: R_C ∥ C_tot vs 50 Ω.
   **[DONE]** — out_gap 8 µm, min-width TM1, slim risers/stacks, compact
   row, R_C back to 50 Ω.
3. **Input feed was edge-fed** — the far MSB cell saw an ~80 µm stub
   (artificial line cutoff ~79 GHz, right where the BW loss was) and the
   channel boundary sat at the tightest bus gap (3.46 fF lsbn↔msbp
   crosstalk). **[DONE]** — center-fed H-tree R_B, MSB rows innermost,
   wide pair gap, Metal4 buses, Metal2 base drops. (The M3 inter-channel
   shield and M3+M4 stitching were tested and NOT adopted: with the short
   center-fed LSB buses they added more ground/perimeter C than they
   removed.)
4. **nx=2 was a symptom, not a solution** — "fix S11 geometrically and the
   S22 fix follows for free" (electrical point returns to the paper's
   nominal). **[DONE]** — final point nx=3, R_C=50, R_B=48, R_E=3.2.

## Open pre-tapeout items (prioritized)

1. **vcasc rail stability**: six cascode HBTs share a 0.24 µm M1 rail
   (~40 Ω, ~90 pH, 7.4 fF to sub, no bypass) — textbook common-base
   oscillation hazard, invisible to C-only extraction and ideal-source
   benches. Add ≥1 pF cmim bypass per cell + 20-50 Ω odd-mode series R per
   cell tap; widen/raise the rail. Same treatment (milder) for vcmb.
2. **EM/current density**: single TopVia1/TopVia2 on 20+ mA R_C/vcc paths
   (5-20× over typical limits); TM1 bus at ~4×10⁵ A/cm². DRC ran
   `--no_density` and KLayout checks no current. Distribute R_C per cell
   (3 × 150 Ω) and/or split `stack_w` into signal/power variants — but
   check the rsil J_max table first (a 50 Ω / 22 mA rsil realization may
   need serpentine area or an off-chip DC load via the modulator's
   back-termination, worth an explicit paragraph in the paper).
3. **Ground cage**: today one 1 µm M1 guard ring + 4 taps + a 0.8 µm sub
   hairline (which runs under the output buses). Widen ring ≥3 µm with a
   full via stack, tap fence ≤5 µm pitch, stitched M1+M2+M3 sub rail,
   cmim decoupling under the vcc rail.
4. **Matching/process variation**: HBT dummies at both row ends (same Nx,
   orientation, pitch; C/B/E tied off) — the outer M0/M1 devices set RLM
   and currently face different proximity than inner ones; rsil/cmim
   dummies likewise. R_E at w=4.5 is ~2/3 contact-head resistance (worse
   mismatch than sheet): split into N parallel wider units, or constrain
   `re_ohm*re_w ≥ 25` in the optimizer. Devices are translation-placed
   (never mirrored) — correct, keep.
5. **Extraction/verification depth**: kpex has no L (odd-mode bus
   Z0 ≈ 43 Ω, ~38 pH ignored → S22 numbers carry ~1-2 dB of artifact,
   pessimistic) and CC/RC agree here; add an EM solve (FastHenry/openEMS)
   of the output pair + return for tapeout-grade S22, plus group-delay
   variation (<2-3 ps budget at 48 GBd) and K-factor / odd-mode stability
   with extracted rails.
6. **Structural reserve**: 2-row floorplan halves the summing bus
   (~+1.5 dB S22) if more margin is ever needed.

## Symmetry notes

- Output buses: outp/outn substrate C differs ~5 % (different y) — a
  mid-span twist would fix; RLM currently 0.98 so deferred.
- L0 (center) runs 10-20 K hotter than M0/M1; the M0|L0|M1 ordering keeps
  the MSB pair thermally matched (this is what RLM cares about) — keep,
  and report LSB/MSB gain-ratio drift vs ΔT with the VBIC self-heating
  model as a robustness check.

---

*The review methodology used here (extraction-driven budgets, objective
audit, hypothesis-tested prescriptions) is distilled into a reusable
Claude Code agent definition at
[`.claude/agents/rf-layout-reviewer.md`](../.claude/agents/rf-layout-reviewer.md)
— launch it with the Agent tool on any layout + PEX netlist.*
