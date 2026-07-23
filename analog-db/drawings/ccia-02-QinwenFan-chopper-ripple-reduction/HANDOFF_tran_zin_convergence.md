# Handoff — ia_004 CCIA `tran_zin_chopped` convergence fix

**Date:** 2026-07-21 · **Status:** FIXED + live-verified (native ngspice + IHP PDK, srv-elamien) ·
**Circuit:** `ia_004_fan_chopper_rrl` (Qinwen-Fan chopper CCIA + ripple-reduction loop) ·
**Drawing:** `examples/analog-db/drawings/ccia-02-QinwenFan-chopper-ripple-reduction`

## TL;DR

The `tran_zin_chopped` transient aborted with `Timestep too small … trouble with node
"xdut.x_ccia_opamp.net1"` at t≈0.843 ms. **Root cause was a clocking bug, not numerics:** the
RRL switched-cap integrator (`clk_phi_1`/`clk_phi_2`) was clocked at **1× fchop** instead of
**2×**. Fixed by halving the phi period (`TCHOP → TCHOP/2`). Deck now runs the full 1 ms on the
default trapezoidal integrator; `zin_chop_ohm = 9.17 MΩ`.

## The error (as originally reported)

```
Initial Transient Solution … OK (DC op-point + dynamic gmin stepping both succeeded)
doAnalyses: TRAN:  Timestep too small; time = 0.000842784, timestep = 2.5e-19:
                   trouble with node "xdut.x_ccia_opamp.net1"
tran simulation(s) aborted
```
(A separate, unrelated `Can't open viewport for graphics.` at the end is just the headless
no-X11 ngspice build refusing the `plot` command — see "Leftover / unrelated" below.)

## Diagnosis

- Abort is at t≈0.843 ms (near the 1 ms tstop), **not** t=0. DC op-point and gmin stepping
  succeeded, and the timestep cruised at ~2.6 µs steps, then collapsed **mid-phase** (42 µs
  *after* the 0.8 ms chopper edge). Signature = a **growing/limit-cycle instability**, not a
  startup-convergence or switch-edge glitch.
- Trouble node `xdut.x_ccia_opamp.net1` = the core two-stage OTA's **PMOS tail** node
  (XM1 drain / input-pair source).
- The deck's own comment (sizing block, `.param gm_val=…` region) already flagged the RRL
  ideal-Gm loop as a divergence source under the registry 5 kHz default.

## Root cause

The RRL is a switched-cap integrator that must sample the chopper ripple in **both** chopper
phases, so its clocks run at **2× the chopping frequency**. The testbench authored `Vphi1`/`Vphi2`
at `TCHOP` (= 1× fchop = 5 kHz). At 1× the integrator mis-samples the ripple → the discrete-time
ripple-reduction loop builds a growing limit cycle → timestep collapses. The **phase** was already
correct (phi_1 starts low = in phase with the main chopper clock `clk_chin`; phi_2 starts high =
in phase with `clk_chin_not`); only the **frequency** was wrong.

Also confirmed (no change needed): all four chopper clocks (`clk_chin/chfb/chout/chpf`) share
identical `pulse(… TCHOP)` params, and the TB ties `clk_CHrrl ← clk_chout` (RRL chopper = output
chopper). The chop network is coherent; only the SC integrator clock was off.

## The fix (applied)

Change phi period `TCHOP → TCHOP/2`, i.e. `pulse(… {TCHOP/2-TEDGE} {TCHOP})` →
`pulse(… {TCHOP/4-TEDGE} {TCHOP/2})`, phase preserved. Applied in **both** the source schematic
and the generated deck:

| File | Where | What |
|---|---|---|
| `testbenches/ccia-dut/tran_zin_chopped.sch` | lines 138 (`Vphi1`), 141 (`Vphi2`) | **source of truth** — xschem vsource props; edit here so a re-netlist keeps the fix |
| `testbenches/ccia-dut/simulation/tran_zin_chopped.spice` | `Vphi1`/`Vphi2` lines (~25–27) | generated deck; verified running |

> ⚠ The `.spice` is generated from the `.sch`. If you regenerate/re-netlist, the `.sch` is what
> matters — it's fixed. If they ever diverge, re-run the netlister from the `.sch`.

## Verification (empirical, native ngspice + IHP PDK on srv-elamien)

To reproduce: `ngspice -b tran_zin_chopped.spice` from the `simulation/` dir (the `.lib
cornerMOSlv.lib` resolves via the sourcepath in `~/.spiceinit`; runs cwd-independent).

| Variant | Result | zin |
|---|---|---|
| baseline (1× clk, default trap) | **abort** @ 0.843 ms | — |
| 1× clk + `.options method=gear maxord=2` | completes | 11.1 MΩ |
| 1× clk + gear + `cshunt=1e-15` | abort @ 0.880 ms | — |
| **2× clk, default trap (THE FIX)** ✅ | **completes 1 ms** | **9.17 MΩ** |
| 2× clk + gear | abort @ 0.2 ms | — |

Baseline is deterministic (identical abort time on repeat). Recorded sibling baselines for sanity:
ia_002 = 11.79 MΩ, ia_003 = 23.7 MΩ (ia_004 has none). 9.17 MΩ is in the right ballpark and is the
number to trust (correct clocking).

**Note on `method=gear`:** it was a *false lead*. Gear rescued the *buggy* 1× deck by damping the
growth, but it *breaks* the correct 2× deck (aborts at 0.2 ms). With the clocking fixed you keep
the **default trapezoidal** integrator — no `gear`, no `cshunt`, no tolerance loosening. Reach for
`method=gear maxord=2` only for a genuinely stiff chopper/SC deck; it is **not** needed here.

## Open follow-ups (for the next agent)

1. **Re-examine `gm_val=10u`** (sizing block, `.param gm_val rout_val cout_val`). That override
   was the *1×-era* mitigation for the loop-gain-> 1 divergence. Now that the clock is correct, the
   loop may tolerate the real `sup_003` Gm (100 µu). Re-test raising `gm_val` toward 100u and check
   the transient still converges and `zin` stabilizes. **Untested — do not assume.**
2. **`zin_chop_ohm = 9.17 MΩ`** — decide whether this becomes the ia_004 recorded baseline
   (`analyses/` binding / datasheet), and whether it meets the intended Zin spec.
3. **Sibling testbenches / benches** — only `tran_zin_chopped` exercises the phi integrator clock
   in this drawing (checked). But the same 2×-vs-1× logic applies to any other RRL transient bench
   authored later; keep the 2× convention.
4. **Headless plotting (unrelated to convergence):** the deck's `.control` still ends in
   `plot voutp`, which fails on this box because ngspice at `~/local/bin/ngspice` is
   built **without X11** (`Can't open viewport for graphics.`). For a headless figure, replace with
   `set hcopydevtype=svg` + `hardcopy zin.svg v(voutp) v(voutn)` and convert with
   `rsvg-convert zin.svg -o zin.png` (both `rsvg-convert` and `cairosvg` are in the `ai_env`).
   ngspice has no native PNG device; matplotlib is NOT installed in `ai_env`.

## UPDATE — 2nd non-convergence after clock consolidation (PF chopper phase bug)

After the above fix, the DUT schematic was edited to **consolidate all chopper clocks onto
one `clk_chop`/`clk_chop_not` pair** (previously separate-but-identical `clk_chin/chfb/chout/chpf`
sources). The regenerated deck then aborted **much earlier — t≈2.7 µs** (startup), same node
`xdut.x_ccia_opamp.net1`.

**Root cause: the consolidation flipped the positive-feedback (PF) chopper's phase.** The PF
chopper (`x_CH_pf`, DUT subckt pins 1–2 `clk_CHpf`/`clk_CHpf_not`) must be wired **anti-phase** —
in the original deck `clk_CHpf ← clk_chpf_not`. Naively tying every chopper's "main" pin to
`clk_chop` gave `clk_CHpf ← clk_chop` (in-phase). An in-phase PF chopper turns the impedance-boost
path into real destabilizing positive feedback → the **core OTA tail diverges within ~3 µs at
startup** (RRL-independent — confirmed: lowering `gm_val`, `cshunt` 1e-15…1e-13, `itl4`/`reltol`
relax, and `method=gear` ALL still died at that node; only fixing the phase worked).

> **"Same clock pair" ≠ "same phase."** The PF chopper shares the one `clk_chop` pair but taps it
> **inverted**. This is the diagnostic tell: a phase/wiring bug, not numerics — no `.options` knob
> rescued it, and an electrically-*equivalent* earlier deck (v3) converged, so the difference had
> to be a real connectivity change.

**Fix applied (both files):**
- `testbenches/ccia-dut/tran_zin_chopped.sch` — swapped the PF chopper's two clock labels
  `l9`/`l10` (lines ~102–103): `l9 → clk_chop_not`, `l10 → clk_chop`. (Mapped label→pin by symbol
  x-offset: `clk_CHpf`@230→l9, `clk_CHpf_not`@250→l10.) **This is the source of truth.**
- `.../simulation/tran_zin_chopped.spice` — swapped the first two `XDUT` clock args
  `clk_chop clk_chop_not → clk_chop_not clk_chop`, with an explanatory comment.

**Verified:** full 1 ms, no abort, `zin_chop_ohm = 9.174524e6` — bit-identical to the pre-
consolidation good run, confirming the consolidation is now electrically equivalent + correctly
phased. The `gm_val`/gear/cshunt lessons from the first fix all still hold (numerics were never
the lever here either).

## CORRECTION — the PF direction matters: stable ≠ correct (impedance-boost fix)

The "fix" in the section above (make the PF chopper **anti-phase** to stop the divergence) is
**superseded** — it stabilizes the sim but puts the positive-feedback loop in the WRONG direction.
Measured, phase-controlled, at nominal Rb=10M (transient bench — **no AC**, invalid for a switched
circuit):

| PF config | Cpf | chopped Zin | note |
|---|---|---|---|
| PF off (baseline) | 0 | **14.5 MΩ** | un-boosted switched-cap floor |
| anti-phase (prev "fix") | 0.8p | 9.2 MΩ ↓ | stable but **subtracts** — wrong for a boost |
| in-phase (boosting), as-drawn | 0.8p | — | **diverges** (boost over-driven) |
| **in-phase (boosting), reduced** | **0.3p** | **17.2 MΩ ↑** | **stable + boosting — the correct fix** |

**Root understanding:** a PF *impedance boost* needs the in-phase (boosting) direction, whose
whole job is to push Zin up toward the cap-reactance ceiling. Pushed too hard it drives the input
resistance negative → the transient diverges (this is the `0.8p in-phase` case, and the original
"non-convergence"). The anti-phase tap avoids the divergence only by making the loop *reduce* Zin.
So the earlier convergence fix and design-correctness were in tension; the right lever is **Cpf**,
not the phase.

**Proper fix applied (both files):**
- PF chopper restored to **in-phase** (boosting): `.sch` labels `l9=clk_chop`, `l10=clk_chop_not`
  (lines ~102-103); deck `XDUT` first two clk args back to `clk_chop clk_chop_not`.
- **Cpf 0.8p → 0.3p**: `tran_zin_chopped.sch:168` `.param` (source of truth) + deck `.param
  x_dut_cpf1_main_value`. ia_003 authored 0.8p, but THIS composite adds the RRL, which changes the
  loop and needs a smaller Cpf.

**Verified:** full 1 ms, `zin_chop_ohm = 1.722e7` (17.2 MΩ), boosting above the 14.5 MΩ baseline.

**Caveats / open items for the next agent:**
- The loop is **marginally stable**: the in-phase Cpf sweep shows isolated divergences at 0.35p and
  ≥0.7p amid a stable 0.4–0.6p island and stable 0.2–0.3p region. 0.3p was chosen for a strong
  boost with margin below the 0.8p ceiling, but this bench tips easily — re-verify after any sizing,
  corner, or temperature change. A proper stability margin / Cpf-tuning pass is warranted.
- **In-operation gain is low**: output ≈ 43 mV for a 10 mV input → effective gain ≈ 4.3, far below
  the cap ratio Cin/Cfb = 20. This weakens the PF (its injected charge ∝ Vout). Suspected: Rb=10M is
  small vs the Cfb reactance (~40 MΩ) at fchop=5k, shunting the feedback. Could NOT be confirmed in
  the tran bench (higher-Rb runs need >1 ms to settle), and **AC is not applicable** — needs a
  transient study (e.g. longer settle, or fchop/Rb co-design), not an AC gain bench.
- Sibling ia_003 (pf) recorded 23.7 MΩ; the corrected ia_004 (~17.2 MΩ) is now in-family (the
  previous 9.2 MΩ anti-phase value was the outlier).

## Design reference (for context)

Fan CCIA + RRL: the chopper up-modulates the offset/1/f to fchop, producing an output **ripple at
fchop**. The RRL is a switched-cap integrator that senses that ripple and feeds back a nulling
current. It is clocked at **2× fchop** with a defined phase to the chopper (phi_1 ∥ main chop
clock, phi_2 ∥ chop-not) so it samples both chopper half-periods. Getting this clock wrong is the
classic way to make the RRL loop oscillate/diverge in transient — which is what happened here.
