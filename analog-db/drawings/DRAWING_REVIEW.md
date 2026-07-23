# Drawing review — hand-drawn CCIA templates (ccia-01 Hsu / ccia-02 Fan)

> **[REVIEW]** — living tracker for the drawing bugs found while landing the
> `drawings/ccia-*` hierarchies as `circuits/` entries (2026-07-16, PR #37).
> Process for each item: fix the **source `.sch`** → headless re-export the
> `simulation/*.spice` → (at the end of the pass) re-flatten + re-verify the
> affected `circuits/` entries. The entries currently carry the fixes locally in
> their authored netlists (documented per-entry in the netlist header +
> `provenance.notes`); this review closes the loop back into the drawings.
> No PR merges until this list is clean and sims/sizing are re-run where needed.

## 1. `chopper-diff` was not a chopper — **FIXED 2026-07-16 (owner redraw + clock fix)**

**Was:** two straight-through transmission gates (VA_p→VB_p, VA_n→VB_n), both on
`Vctl` — a differential series switch. It cannot reverse polarity, so the CCIAs
gated the signal instead of chopping it (measured: clocked gain ≈1.6 V/V vs
19.3 static; output CM wandering rail-to-rail with no restoring path half of
every period).

**Now:** true 4-gate modulator. Signal topology (owner) + clock distribution
(fixed in this pass — the cross pair takes the *swapped* hookup; only the two
existing clock ports are used, so the subckt port order and every parent
instance are unchanged):

| Inst | Path                | vctl (top, NMOS gate) | vctl_not (bottom, PMOS gate) | Conducts when |
|------|---------------------|-----------------------|------------------------------|---------------|
| x1   | VA_p→VB_p straight  | Vctl                  | Vctl_not                     | Vctl **high** |
| x4   | VA_n→VB_n straight  | Vctl                  | Vctl_not                     | Vctl **high** |
| x2   | VA_p→VB_n cross     | **Vctl_not**          | **Vctl**                     | Vctl **low**  |
| x3   | VA_n→VB_p cross     | **Vctl_not**          | **Vctl**                     | Vctl **low**  |

The draft had all four gates on `Vctl` (both paths conducting together = VB_p
shorted to VB_n through the switches) and three PMOS gates floating.

**Design notes (chopper):**
- **Transparent state**: `Vctl` high / `Vctl_not` low = straight path on, cross
  path off — a clean pass-through, so the entries' clocks-held static benches
  (`dc_op_chopper_diff`, `ac_closed_loop_chopper_diff`) and amp_026's
  rails-tied output chopper remain valid unchanged.
- **Break-before-make**: complementary rail-driven clocks are fine at TG level;
  if non-overlap is added later, note both clock nets low turns each TG's PMOS
  **on** (gate low) — the same trap as the RRL PHI wiring (see §4).
- **Electrical proof** (ngspice, sg13 tt, min-size 0.15u/0.13u gates, 100 kHz):
  DC diff input +200 mV → output +163 mV / −163 mV / +163 mV across successive
  half-periods — polarity reversal confirmed. Attenuation is the resistive
  proof-bench load against the TG on-resistance, not a defect; sized 2u/0.13u
  TGs measure r_on ≈ 2.9 kΩ (measured live during the pass; spec bound max 20k in
  the sw_001 datasheet). The polarity proof is now a COMMITTED GATE:
  switch/tran_chop_polarity (chop_inversion ~ -1) bound on sw_002.
- **Measured downstream shift on entry resync (2026-07-16)**: the chopper itself
  now chops — the clocked bench's differential output transiently reaches the
  full cap-ratio gain (~19.6-20.9 V/V) — but the windowed clocked `gain_cl`
  only rose 1.6 -> ~2.0: the no-CMFB opamp core's output common mode is
  BISTABLE under clocking (a ~0.7 ms relaxation oscillation through the
  Cfb/Cin network flips vocm rail-to-rail and resets the differential
  build-up; Rb and output-branch retunes do not stabilize it).
  `v_ripple_pp` 8.4m -> ~50 mV is genuine chopping ripple + CM wander (in
  spec). Reaching the cap-ratio gain under clocking needs CM stabilization —
  a composed CMFB servo or the RRL itself — i.e. an architecture step for the
  P4 composition milestone, not a sizing fix. Recorded in the ia_002/003
  datasheets as the standing T4 `gain_cl` skip.

## 2. Fan `two-stage-opamp-core`: four floating source nets — **FIXED 2026-07-16 (owner)**

XM1 (input-pair tail), XM6/XM9 (PMOS current sources), XM15 (NMOS output
driver) each had their source on a single-connection stub net (net10–net13) —
the rail wires stopped one grid step short of the pins. Owner extended the
three VDD stubs and re-routed the VSS one in `two-stage-opamp-core.sch`.
**Verified**: connectivity scan of the re-exported subckt shows zero
single-connection internal nets; the fix propagates into the re-exported
`ccia-dut-chopper-simple` / `-w-positive-feedback` embeddings.
*Entries amp_026 / ia_002 / ia_003 carried the same fix locally — on resync
their netlist-header deviation notes for this item should be dropped (the
drawing now matches).*

## 3. Hsu CMFB servo: positive common-mode feedback — **FIXED 2026-07-16 (owner)**

As drawn, the CM detector fed the ideal amp's **+** input (vref on **−**) — an
even inversion count around the CM loop (verified by the railed OP and a
monotonically *increasing* open-loop `vocm(vcmfb)` sweep). Owner swapped the
routing in `cmfb-output-ideal-amp.sch`: vref now drives **+**, the detector
output drives **−**, i.e. `vcmfb = A·(vref − vcm_sensed)`.
**Verified live** (standalone subckt, gm 100u / rout 10Meg): sensed CM 50 mV
above vref → vcmfb slams negative; 50 mV below → positive — the servo now
opposes the CM error. The old wiring also had the vref path's wire cache
labelled VSS (latent short risk); the re-route cleared it.
*Residual (entry-level, not a drawing bug): the macromodel output still rests
at VSS; ia_001's entry rests it at `vcmfb_ref` with low gain (tuned to 5; servo-grade baseline is 10) for bounded
authority — keep that deviation note on resync, or move the Rout rest node in
`ideal-amp-fully-diff.sch` too (owner's call; it changes the macromodel for
all users).*

## 4. RRL SC integrator: AC-coupled by design; bench + phase wiring — **OPTION A IMPLEMENTED 2026-07-16; adversarial review demoted the spec (see below)**

**Post-chopper-fix reading (2026-07-16).** The signal chain is
`vinp/vinn → Cs1/Cs2 → x_CH_RRL (chopper) → PHI switch network → integrator`.
With §1's 4-gate chopper this is now a coherent **ripple-sensing demodulating
SC integrator** — the Fan RRL sense block: Cs AC-couples the main amplifier's
output ripple (DC is *supposed* to be blocked), x_CH_RRL synchronously
demodulates it at f_chop, and the SC core integrates the demodulated product
into the correction signal. The earlier "no input commutation" finding stands
only for **DC stimulus**: a DC differential input transfers zero net charge
per cycle (verified: VIN_DC = 0 and 10 mV give identical outputs) — which for
this block is a feature, not a bug.

**Resolution (owner chose option A — keep topology, re-scope the bench):**
`sup_003` now binds `tran_rrl_sense` (square ripple at f_chop + synchronous
CLK_CH_RRL + complementary PHI -> `ripple_gain`, V/s/V); the entry's chopper
carries the full 4-gate modulator at the DRAWN clock polarity, and the old
DC-ramp bench/metric is gone. Status `validated`. CAVEAT from the live bench:
at the placeholder sizing the measured ripple_gain (-8.4e7) is dominated by
the integration nodes' startup relaxation, not demodulation (a VR~0 control
reproduces it; the true demodulated response is bounded and below the
extraction floor) — so the S4.2 SIGN question stays OPEN until the composed
RRL loop test (or a startup-settled bench variant). All recorded verbatim in
sup_003's datasheet. **Adversarial review (2026-07-16, confirmed HIGH): the
original spec band was drawn around that startup artifact, letting a T4
conform row PASS on a number the datasheet itself disowns — the band is now
DROPPED (informative metric, entry returns to `simulated`), and the
superseded `tran_sc_integrate` template (bound by nothing; its
"transparent" hold actually selected the inverted path for the drawn
polarity) is deleted.**

**Original analysis (for the record):**
1. **The bench, not the topology.** `tran_sc_integrate` (DC input, chopper held
   transparent) measures the startup transient, and its expected-ramp formula
   (VIN_DC·Cs/Cint·FCLK) presumes an input-commutated integrator. Replace for
   this block with a ripple-sense bench: differential square/sine ripple ±Vr at
   f_chop on vinp/vinn, CLK_CH_RRL clocked **synchronously** at f_chop, PHI
   two-phase; metric = demodulated ramp rate per volt of ripple
   (`ripple_gain`, V/s/V). Entry resync: `sup_003` re-benches accordingly.
2. **Demodulation sign.** x_CH_RRL's `Vctl` is wired from `CLK_CH_RRL_not`
   (opposite phase). With a symmetric 4-gate chopper this flips the
   demodulation polarity — i.e. the SIGN of the RRL loop once composed. Wrong
   sign = ripple amplifier. Verify at composition time (or rename the two
   labels now); a one-label change either way.
3. **PHI complement wiring.** Each PHI switch uses the *other* phase as its
   `vctl_not`, so any non-overlap gap half-turns-on every PMOS. Benign with
   exact complements (the current bench convention); becomes a real leak if
   non-overlap is introduced. Consider dedicated complement nets if a
   non-overlap generator is ever added.

## 5. Minor normalizations — **FIXED IN SOURCE 2026-07-16 (this pass)**

| Item | Was | Now |
|---|---|---|
| `two-stage-ota-core.sch` R2 value | `RZ` (case-collides with R1's `Rz`) | `Rz` (one shared symbol) |
| `two-stage-ota-core` port name | `vcmbf_ref` (typo; .sym + .sch) | `vcmfb_ref` |
| `ideal-amp-fully-diff.sch` values | `GM/ROUT/RIN/COUT/CIN` (case-collide with instance names Gm/Rout/…) | `gm_val/rout_val/rin_val/cout_val/cin_val` (matches the circuits/ entries) |
| `two-stage-opamp-core.sch` Cm_1 | literal `1p` next to symbolic Cm_2=`Cm` (unedited xschem default) | `Cm` (matched pair, one symbol) |
| `ccia-dut-chopper-*.sch` Rb1/Rb2 | literal `1k` (HPF at ~MHz) | symbolic `Rb` (unsized-drawing convention, like Cc/Rz) |
| `simulation/ccia-chopper-simple.spice` | stale orphan export (ver-A core with dangling voutn; its .sch no longer exists) | **deleted** |
| `integrator-switchcap-opamp` XM6/XM8 | two identical parallel devices | **kept as drawn** (a legitimate ×2 reference half; entries tie them as a pair) — design note, not a bug |

All `simulation/*.spice` exports in both template dirs re-generated headlessly
after these edits (they also pick up the §1 chopper fix everywhere it embeds).

## Entry-resync checklist — **COMPLETE 2026-07-16**

- [x] `sw_002`, `amp_026`, `ia_002`, `ia_003` resynced (4-gate choppers in the
      netlists; §2 deviation notes retired). sw_002/amp_026 `validated`;
      ia_002/003 `simulated` with the CM-bistability finding above.
- [x] `amp_025`, `ia_001`, `sup_002` (§3/§5): notes retired; **correction** —
      (sup_002 = today's `cmfb_001_ideal_rsense_servo` — re-classed into the
      dedicated `cmfb` class 2026-07-20, full rigorous suite bound)
      sup_002's committed netlist had NOT carried the §3 polarity fix (only
      amp_025/ia_001 had); its G-card control pair was swapped to match the
      fixed drawing (bench is magnitude-only: 60.0 dB / 106 kHz unchanged,
      `validated`).
- [x] `sup_003` per §4 option A (`tran_rrl_sense`, `validated`).
- [x] `analog-db generate --all` + full `verify --sim` (see PR).

## 6. `bio-afe-01-YuPinHsu-reconfigable-SRMC` — **TRIAGED 2026-07-17 (port deferred per owner)**

New family (owner, 2026-07-16 evening): the Hsu/Liu/Hella TCAS-I 67(1) 2020 biosignal
acquisition system — an ideal-block AFE chain (`afe-ideal` = ccia-ideal → PGA-ideal →
SRMC-ideal) around the paper's innovation, the **SRMC (Switched-R-MOSFET-C) filter**: a
first-order active-RC LPF whose series input switch is duty-cycled at FS = 1 kHz so the
effective resistance scales as R/d — a 40–320 Hz corner from on-chip R (2/5 MΩ) and
C (80 pF). Paper headlines the benches must eventually reproduce: chain gain 43–55 dB
(3-bit PGA), THD −68 dB @ 6 mVpp/12 Hz, duty-controlled corner, 1 kHz clock notch.
See `bio-afe-01-.../landing.yaml` for the block → class/entry map.

**STATUS UPDATE 2026-07-18** (forward checklist now in [`TODO_bio_afe_port.md`](TODO_bio_afe_port.md)):
B1/B2 **DONE** (owner) via the TG realization — 0 S-elements / 0 `SWITCH1` in any export;
B3 **moot** on the TG path; B4 **DONE** (owner) — net-degree scan shows no floating pseudo-R
nodes; B5 **PARTIAL** — refs fixed (0.5 V); the block is now **canonical** `A·(sensed−vref)` (right
for SRMC), but §3 had adapted ccia-01 by flipping the *block*, so ccia-01/amp_025 now sees the
wrong sign — fix at **ccia-01's connection** + re-validate amp_025 (see TODO §B5); B6 **DONE** — all 8 `.sym` reordered to the
canonical `vinp vinn voutp voutn VDD VSS`+extras, capbank `Vinp`→`vinp`/`vinn`→`vout`(opin),
orphan `SRMC-ideal-switch-only.spice` deleted, exports refreshed (connectivity proven unchanged).

**Port BLOCKERS (fix in source before landing):**
- **B1. Switches can never close.** All three S-elements in SRMC-ideal /
  SRMC-ideal-switch-only (and the afe-ideal expansion) wire the CLOCK to the switch's
  NEGATIVE control pin and leave the POSITIVE control on a no-connect stub
  (`S1 net2 net3 net6 V_PHI SWITCH1` — ngspice S is `S n+ n- NC+ NC- model`, so the
  control voltage is v(float) − v(clock): inverted AND floating). The xschem
  `switch_ngspice.sym` netlists `@@P @@M @@CP @@CM` — the drawn wiring must land the
  clock on CP and VSS (or the complement) on CM.
- **B2. No `.model SWITCH1` card exists anywhere** — every SRMC deck hard-aborts
  (`can't find model 'switch1'`). Either add a `.model SWITCH1 SW(...)` fragment to the
  family or (preferred for landing) use the TG realization: `SRMC.sch` already
  instantiates `transmission_gate_pair` ×3 but has NO simulation/ export yet.
- **B3. Tooling: S-elements are unsupported end-to-end** — spicexplorer_circuitgraph's
  device factory silently DROPS them (no S prefix), and the P4 composer's `_NET_COUNTS`
  rejects them. Landing the behavioral-switch variants needs S support in both (or the
  TG variant per B2, which needs neither).
- **B4. Pseudo-resistor chains broken by 2.5-unit wire gaps** in ccia-ideal.sch and
  PGA-ideal.sch (both sides, e.g. PGA `#net3` ends x=1547.5 vs `#net4` starts x=1545):
  the diode-PMOS stacks' middle nodes float, so the amp summing nodes have NO DC bias
  path — the cap feedback loops are DC-open as drawn.
- **B5. CMFB polarity in `SRMC-core-amp-w-cmfb` is POSITIVE feedback as drawn**
  (the reused ccia-01 `cmfb-output-ideal-amp` block is wired vref→vinp, sensed
  CM→vinn, and the PMOS-load plant inverts once more — even inversion count; the §3
  fix pattern applies here too). Also its bias/CMFB references are 3 V placeholder
  sources on a 2 V (paper) system with sg13_lv devices.
  *RESOLVED 2026-07-18 — see `TODO_bio_afe_port.md` B5: decision A, two shared blocks
  (one per plant parity), both consumers sim-proven live. This diagnosis was correct for
  the block's then-§3 wiring; after the block went canonical (`sensed − vref`) the SRMC
  plants measure INVERTING → canonical is right for SRMC as now drawn, while ccia's plant
  is NON-inverting → it references the new `-inv` (§3) twin. Plus a stage-1 actuator
  bias/size fix (VB2 0.5→0.7 V, XM8 0.15u→0.5u) and a new class bench
  `dc_cmfb_plant_sign` capturing the method.*
- **B6. Port-order scramble traps:** SRMC-ideal vs SRMC-ideal-switch-only are
  net-identical twins whose subckt headers order ports two different ways; 5 of 8
  blocks netlist their .sym pin order differently from their .sch header order
  (positional-binding trap for any hand-written TB); `capbank` has the family's only
  capitalized pin (`Vinp`) and its output-side port is named `vinn` with dir=in.

**Bench gaps (new templates the port needs — plan §4.6 clocked family grows):**
- `pga_gain_code_step` — closed-loop gain per 3-bit code (drive V_D0..2 pairs + VCM).
- `srmc_corner_clocked_tran` — duty-cycled filter corner: non-overlap phi pair at FS,
  swept-tone long tran → f3dB vs duty d (the paper's 40–320 Hz axis).
- `srmc_clock_notch_aliasing` — FFT of tones near FS: clock-notch depth + imaging.
- `afe_chain_e2e` — whole-chain clocked bench (gain per code, BW per duty, THD at
  6 mVpp/12 Hz vs the −68 dB headline).
- `clocked_noise` — LTI `.noise` is INVALID with switches running: ngspice TRNOISE
  long-tran integrated noise (or Spectre pss+pnoise) — the long-standing chopped-noise
  gap now has a second customer.
- a shared **non-overlap two-phase clock fragment** (guaranteed dead time) — today
  every clocked bench hand-rolls complementary PULSE pairs (registry chopper default
  is now **FCHOP = 5 kHz**).

**Polarity notes (informational, not bugs):** every block wires the behavioral leaf's
`voutn` slot to the net named `voutp` — i.e. the blocks are INVERTING (gain
−Cin/Cf), which is what makes each cap-feedback loop negative; the drawn ideal-amp
leaf's port order (`... voutn voutp VSS VDD`) is the family convention and now also
the wrapper-symbol convention (see symbol-templates/README.md).

## 7. `rrl-switched-capa-integrator`: S1/S2 sense-ground phase asymmetry — **FIXED 2026-07-20 (owner redraw after Fan Fig. 6) + sim-proven; this was the RRL's real blocker**

**Was:** the sense-node ground switches used OPPOSITE phases — S1 grounds `sc_n` on
`phi_1` while S2 grounds `sc_p` on `phi_2` (drawing x_S_1/x_S_2). The 2026-07-17 audit
called this "half the sensing efficiency" and deferred it as unmeasurable until P4-4b.

**Now:** BOTH sense grounds on `phi_2` — symmetric, and on the SAME phase as the AZ
shorts S3/S4 (sample-and-auto-zero together; release-and-transfer on `phi_1`). Note
this is the OPPOSITE of the audit's guess ("same phase, *opposite* the AZ switches");
Fig. 6 settles it. The owner's same-pass edit also flipped the RRL chopper's `Vctl`
from `CLK_CH_RRL_not` to `CLK_CH_RRL` (the §4.2 hookup).

**The audit under-called this.** It is not a sizing nicety — it was what made the whole
block unmeasurable, and the deferral to P4-4b was wrong (§7 is an OPEN-LOOP property of
`sup_003`; only §4.2's *verdict* needs the composite). Live A/B, ihp tt, ngspice-45,
2026-07-20, `tran_rrl_sense` + per-side `int_p`/`int_n` observables:

| case | S1 | chopper | `ripple_gain` (VR=2m) | control (VR≈0) | `rate_p` / `rate_n` |
|---|---|---|---|---|---|
| A | phi_1 (old) | `_not` (old) | −6.465e7 | *tran aborted* | **−58.9 / +70.4** |
| B | phi_2 (new) | `_not` (old) | **+4.378e5** | +57.4 | +138.0 / +137.1 |
| C | phi_1 (old) | plain (new) | *tran aborted* | *tran aborted* | — |
| D | phi_2 (new) | plain (new) | **−4.377e5** | +58.4 | +137.1 / +138.0 |

Case A reproduces the committed baseline exactly (−6.465e7), so the harness is sound.
Reading:
- **The S1 fix is what ungated the metric.** With the asymmetry, the two integration
  sides ramp in OPPOSITE directions, so the startup common mode leaks into the
  differential and swamps it (signal/control ≈ 1). Symmetric, the startup ramp is pure
  common mode (+137 on both sides) and cancels: **signal/control ≈ 7.5e3**.
- **Convergence, too**: all 3 aborted transients are old-S1 cases; all 4 new-S1 runs
  converge. The asymmetric front end was numerically unstable, not merely inaccurate.
- **The chopper flip only sets the SIGN** — B vs D are equal magnitude, opposite sign,
  exactly as §4.2 predicted. So the demod sign is now *measurable* at `sup_003`;
  whether it makes the COMPOSED loop negative-feedback still needs P4-4b.

**Sizing done 2026-07-20** (numbers in the `sup_003` datasheet). First, the reference law:
the charge-transfer limit is the DIFFERENTIAL **2·(Cs/Cint)·FCHOP**·1000, not the
1× form the sup_003 datasheet used to claim — measured `ripple_gain` **exceeds** the 1×
law at 4p/4p (6.17e6 vs 5e6), 8p/4p and 4p/2p, so 1× is not a bound; 2× bounds all five
(Cs,Cint) points at 52–66 %. This matches §8's held-phase `2·Cs/Cint` result.

Efficiency is limited by a sense-node parasitic charge divider Cs/(Cs+Cpar), Cpar set by
switch **diffusion area** — so both levers run against intuition: **widening the TGs
strictly hurts** (at Cs=1p: 18.8 % @1u → 17.5 % @2u → 4.8 % @5u → 1.4 % @20u) and
**raising Cs helps** (24.2 % @1p → 61.7 % @4p at min-W). Ron is not the limiter at
FCHOP=5 kHz (min-W Ron ≈30 kΩ × 4p = 120 ns vs a 100 µs half-period), so "widen for
lower Ron" is actively wrong here — the owner's "TGs are min W/L in a tech node" rule
is the correct one. Caz is inert (1.0–1.2× over 16×).

**NOTHING LANDED — the sizing was tried and REVERTED.** Cs = Cint = 4p with minimum-W/L
switches reaches `ripple_gain` −6.172e6 V/s/V = **61.7 %** (a 14× block-local win over the
17.5 % placeholder), and efficiency keeps rising with cap area (8p/4p 64.3 %, 4p/8p 66.1 %).
But **both** block-local optima are SYSTEM regressions in the composed `ia_004`:

| change | block efficiency | `ia_004` `hpf_hz` (spec ≤ 1000 Hz) |
|---|---|---|
| committed baseline (2u TG, Cs=1p) | 17.5 % | 32.5 Hz ✅ |
| Cs 1p→4p | 61.7 % | 395 kHz ❌ |
| min-W/L switches | better | **776 kHz** ❌ |

Higher switch Ron reshapes the composite's feedback path; the Cs regression is independent
of it. `sup_003`'s binding is back at the committed defaults (`ia_004` re-verified at
`hpf_hz` 32.482 Hz, `validated`); only the characterization comments were kept.

**Conclusion: this block cannot be sized in isolation.** Size it composite-aware and
multi-objective (`ripple_gain` vs power vs **area** — 2×Cs + 2×Cint + 2×Caz dominate its
area, so a gain-only objective always spends area), and only AFTER the P4-4b CMFB closure
makes the composite exercisable. Note `ia_004`'s `composition.yaml` already detunes
`gm_val` 100u→10u to stop the composed RRL diverging at FCHOP = 5 kHz, so loop gain is a
composite-level knob regardless.

Related audit notes, recorded: the drawn TG gate pairing (NMOS on one phi, PMOS on the
other) structurally requires phi_1/phi_2 to be EXACT complements (the class benches
already drive them so — a true non-overlap pair would half-enable every TG in the dead
time); sup_003's `ripple_gain` SIGN at the committed placeholder sizing is dominated by
the startup/windup artifact. **The RRL DEMODULATION-SIGN question remains OPEN** (§4.2):
the composed ia_004 does NOT resolve it — the CM-uncontrolled Fan core rails within
~1-2 ms once the SC clocks actually run, so neither the cross nor the straight injection
hookup produces a valid (settled) output (an earlier claim that "cross nulls, straight
regenerates" was measured with the SC clocks accidentally undriven, i.e. the RRL inert —
a bench-template bug, since fixed). The demod sign is resolvable only after the core-CM
closure composite (plan P4-4b) lets the RRL actually operate.

## §8 — Full drawings sim sweep (2026-07-18): every block benched, native ihp tt

Follow-on to the B5 closure: every sim-able block in `drawings/` now has a native-ngspice
bench with measured metrics (decks assembled from the committed `simulation/` exports;
seed = devices as exported, sized = patched to the landed binding's `sizing.yaml`).
Session-scratchpad decks; the reusable methods are templated/tracked in
`_shared/classes/` (landed: `amplifier/dc_cmfb_plant_sign`; candidates:
`_shared/classes/TODO_new_class_testbenches.md` §sweep-2026-07-18).

| Block | Headline result | Verdict |
|---|---|---|
| shared/transmission_gate_pair | Ron 3.4–31 kΩ (hump at VCM=0.6, min-size), OFF ≈ 3.7–6.7 TΩ | OK |
| shared/chopper-diff | exact ±97.4 mV sign flip on ±50 mV diff in, CM preserved | OK |
| shared/capbank | ~~thermometer 1–4 pF~~ → **binary-parameterized 2026-07-19** (finding 1 resolved, owner decision): value=Cu with m=1/2/4 → C_eff = (1+code)·Cu, measured 1–8 pF exact @ Cu=1p, all 8 codes distinct | OK |
| shared/ideal/ideal-amp-fully-diff | 60.0 dB, f3dB 158.8 kHz, UGF 159 MHz (= gm·rout / cout params exactly) | OK |
| shared/ideal/vcm-detector-simple | exact average; Rout = Rm/2 = 500 kΩ (loading-sensitive) | OK |
| shared/ideal/cmfb-output-ideal-amp(/-inv) | slope +1000 / −1000 about vref — signs as named | OK |
| bio-afe SRMC-core-amp(-w-cmfb) | CM 0.500±0.001 both loops (post-B5 fix); diff 41.0 dB, GBW 6.8 MHz; **not unity-gain stable** (feedthrough shelf, PM −58° at 144 MHz crossing) | OK — reuse flag |
| bio-afe SRMC-ideal | unity-passband LPF; static corner TG-Ron-dominated (2.79 MHz stiff-gm); duty-scaled R_eff=1 MΩ → 150.4 kHz | OK |
| bio-afe SRMC | == ideal corner at duty-scaled R (150.2 kHz, Δ<0.1 %); **input CM must be 0.5** (committed refs), 0.6 rails the servos | OK |
| bio-afe ccia-ideal | midband ×0.998 (Cin/Cf=1), HP 2.18 Hz (pseudo-R ≈ 73 GΩ), LP 56 MHz; this export has NO input choppers | OK |
| bio-afe PGA-ideal | ~~1×/3×/4× thermometer~~ → **binary 2026-07-19**: gain = (1+code), measured 0→17.98 dB over codes 000–111 (ideal 18.06 @ Cf=1p, Cu=1p), monotonic, no degenerate codes | OK |
| bio-afe afe-ideal | chain +11.74 dB (stiff amps; = 1·4·0.97), HP 3.37 Hz, LP 2.41 MHz; no convergence blockers | OK |
| ccia-01 ccia-dut | 24.47 dB (ideal Cin/Cf=20 → 26 dB), HP 3.55 Hz, LP 586 kHz, vocm 0.599/servo in-rail — with the amp_025-flavor core bias (vb3 0.75); see finding 4 | OK |
| ccia-02 two-stage-opamp-core | sized: 61.7 dB / 20.8 MHz / 64.3°, vocm 0.599 (seed rails — knife-edge by design) | OK |
| ccia-02 integrator-switchcap-opamp | sized: 46.6 dB / 47.6° (= landed scoreboard); CM probes: zcm_lf 3.25 kΩ, peaking 17.1 dB; see finding 5 | OK |
| ccia-02 rrl-switched-capa-integrator | held-phase-1 transfer = cap-ratio law (2·Cs/Cint: 1.90/0.48 vs 2.0/0.5) | OK |
| ccia-02 ccia-dut-chopper-simple | sized: 25.72 dB (ideal 26.02), HP 31.9 Hz, LP 1.24 MHz, vocm 0.610 | OK |
| ccia-02 ccia-dut-chopper-w-positive-feedback | 25.72 dB; PF path benign in static phase — only LP 1.24→2.10 MHz | OK |
| OTA two-stage-miller-comp-common-mode-control | sized: 24.79 dB (= scoreboard) / 22.0 MHz / 90.2°, vocm 0.766 @ VDD 1.5 | OK |
| OTA two-stage-miller-comp | no interior DC point reproduced (cm_interior_pts=0; vocm snaps ~0↔1.1 across vbl 0.69→0.71) | expected-fail, documented |
| OTA two-stage-skeleton | unbiasable by design (no sources; floating gate nets; literal `xxx` ports) — N/A | N/A by design |

**Findings (owner attention):**
1. **capbank weighting — RESOLVED 2026-07-19 (owner: binary).** `shared/capbank.sch`
   re-parameterized: all caps value=**Cu** (unit, TB-supplied — benches must
   `.param Cu=1p`), binary weighting enforced structurally via m=1/1/2/4 on
   C1/C2(D0)/C3(D1)/C4(D2) → C_eff = (1+code)·Cu. Live-validated: C_eff exactly
   1–8 pF @ Cu=1p, PGA gains 0→17.98 dB = (1+code) within 0.08 dB. Full PGA validation
   (2026-07-19, all 8 codes): HP corner 2.17 Hz code-independent (pseudo-R/Cf), LP
   1.08–3.4 MHz (β·GBW, falls with gain), vocm 0.6000 every code; 10 mV step settles
   to 1 % in 0.52 µs at gain −3.96 (the family's inverting cap-feedback convention —
   sign expected); THD 0.0018 % (−94.9 dB) at code 111 / 476 mVpp out / 1 kHz (TG
   path adds nothing in-band). Exports re-netlisted
   (capbank + PGA-ideal + afe-ideal; the §8 afe-ideal chain-gain row predates this —
   code-111 chain gain is now +18 dB-class, not +11.7 dB). NOTE for the 65 nm lane:
   re-port capbank when the CIW daemon is next up — xvport's capa map rule carries only
   value→c, so the m=2/4 multipliers need a map extension (m→the analogLib cap
   multiplier CDF param, verify live) or they silently drop in the cellview.
2. **SRMC-core-amp is not unity-gain stable as compensated** (Miller feedthrough shelf
   crosses 0 dB at 144 MHz past −180°): fine inside the SRMC loop's β, a landmine for
   any unity-β reuse — recompensation (larger Rz / stage-2 gm) needed there.
3. **Bench rules for the bio-afe family**: input CM = 0.5 V (the committed refs), and the
   ideal-OTA default gm_val=100u cannot drive the SRMC 1k network — use a stiff-gm
   variant or duty-scaled R_eff to read design-intent numbers.
4. **ccia-01 drawing ↔ ia_001 servo-topology delta**: ia_001's landed biases (vb3 0.40)
   assume its rest-at-vref detuned servo (ROSRV to vcmfb_ref); the drawing's ideal-servo
   leaf rests at VSS, so with ia_001 biases the drawing has NO interior CM equilibrium.
   The drawing benches with the amp_025-flavor biases (vb1 0.55/vb2 0.45/vb3 0.75/ref 0.6).
5. **amp_027 "dangling CMFB" (2026-07-17 audit) refined**: sense-diode XM16 is dangling
   (gate/drain fan out nowhere), but the CM loop is functional single-sided via the shared
   tail — cost ≈ −126 mV static CM error + 17 dB CM peaking. The audit's one-net merge
   (cm_sense→cm_bias, drop XM16) stands as an improvement, not a bring-up blocker.

## §9 — ia_004 sizing attempt (2026-07-20): Ax/BO run, and the two defects it exposed

Follow-on to the §7 closure. Goal was a gain / power / area trade-off study on the composed
`ia_004` (IHP, ngspice lane). Config landed at
`raw_optimize/ia_004_fan_chopper_rrl.yaml`; nothing was sized, and no binding changed.

### 9.1 DEFECT — the S7 fix moved the closed-loop bandwidth 4.68x and NOTHING CAUGHT IT

Measured at the committed defaults vs `git show HEAD:` of the same raw deck (tt, ngspice-45):

| metric | pre-fix (HEAD) | post-S7-fix | scoreboard `ee77a983e2` |
|---|---|---|---|
| gain_cl_db | 25.71923 | 25.71322 | 25.71923 |
| hpf_hz | 32.48203 | 32.44218 | 32.48203 |
| **bw_cl_hz** | **385 609.8** | **1 802 165** | 385 609.8 |
| i_supply | — | 219.50 uA | 218.95 uA |

The pre-fix deck reproduces the scoreboard EXACTLY, so the attribution is unambiguous. Gain
vs frequency shows the 100 Hz - 10 kHz passband is untouched (25.276 / 25.661 / 25.700 /
25.713 dB before vs 25.281 / 25.669 / 25.709 / 25.713 after); the curves diverge only above
100 kHz, where the pre-fix version rolled off early (25.43 dB @100k, 18.70 @1M) and the fixed
one stays flat (25.70 @100k, 24.65 @1M).

Reading: the old roll-off was an ARTIFACT of the broken RRL loading the signal path, not
intentional band-limiting — and `ia_004` has no intentional band-limiting at all. For a
100-320 Hz front end, 1.8 MHz of closed-loop band is ~5600x the passband and buys only
integrated noise.

**Two follow-ups, both OPEN:**
- `scoreboard/ihp-sg13g2/ee77a983e2.json` is STALE (written 2026-07-17, pre-fix) and was never
  regenerated. Do not trust it.
- `bw_cl_hz`'s datasheet spec is ONE-SIDED (`min: 500`), which is why a 4.68x move passed
  `verify` silently. Make it two-sided BEFORE any optimizer run — a search will exploit a
  one-sided band far harder than a human will. Same critique applies to `hpf_hz` (`max: 1000`
  permits a corner above the passband).

### 9.2 DEFECT (FIXED) — `raw_optimize/run.py` silently overrode the DSL engine

`run.py` passed `optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE` explicitly, and the
orchestrator documents that an explicit `optimizer_type` BEATS the YAML — so a project setup
carrying `type: bayesian_ax` still ran under NGOpt with no warning. Fixed: the default is now
`None` (honor the YAML), with `--engine {nevergrad,bayesian_ax}` to override. Shipped configs
all carry `type: nevergrad`, so their behavior is unchanged.

### 9.3 RESULT — the seed is a local best, and the real levers are frozen behind CMFB

Method: `type: bayesian_ax`, 5 specs (gain_cl_db + power + active_area as objectives;
hpf_hz + bw_cl_hz carried as GUARDS so the search cannot repeat the §7 sizing regression).
A defaults-frozen CONTROL reproduces the deck exactly — gain 25.7132 / hpf 32.4422 /
bw 1.80216e6 / power 263.394 uW / active_area 96.8 um^2 (the last matching hand-computation
to the digit), so the config and both measurement paths (Tier-1 `power_uw`, param-derived
`active_area`) are verified correct.

Feasibility is the headline. Infeasible points all score an identical flat **-1e6**, which
gives the BO surrogate nothing to fit, so the feasible FRACTION decides whether Ax is doing
Bayesian optimization or random search:

| search | dims | feasible | note |
|---|---|---|---|
| devices + 4 gate biases, 0.3x-3x | 18 | **0 / 4** | free biases never yield a valid cascode op-point |
| devices only, 0.3x-3x | 14 | **1 / 15** | the one feasible point reached only 15.09 dB |
| devices only, **0.6x-1.7x** | 14 | **16 / 30** | BO finally learns; trials 27-29 converge toward the seed |

The 30-trial narrow run did NOT beat the hand-seeded default, which dominates on all three
objectives (seed score -0.909 vs best-found -1.281; gain 25.713 vs 25.611, power 263.4 vs
283.9 uW, area 96.8 vs 127.2 um^2). Ax never evaluates the seed — it starts from Sobol random
— and was still walking toward it when the budget ran out.

What the 16 feasible points reveal matters more than the winner:
- **`active_area` has almost no dynamic range** (96-132 um^2, seed at the BOTTOM). The searched
  transistors are not where the area is: 47.7 pF across 14 caps dwarfs 191 um^2 of gate area,
  and the derived recipe has no capacitor term at all. `active_area` here means "active DEVICE
  area of the searched core" and nothing more.
- **Power is dominated by the FROZEN parts** — total draw never drops below ~221 uW even for a
  0.87 dB design. The main-amp W/L can only swing ~220-330 uW; the rest is the frozen `rrl`
  instance plus the bias network.

CONCLUSION: the gain/power/area trade-off is NOT reachable through this parameterization. The
levers with authority over power are the bias currents and the RRL instance — and free biases
railed the circuit in 100% of trials. That is the same fragility P4-4b hit from the other
side: with no CM loop holding `vocm`, nearly any perturbation rails the output. **Sizing
ia_004 is not blocked by tooling; it is bottlenecked by a ~7-53% feasible rate whose cause is
the missing core CMFB.** Stop optimizing this configuration; close P4-4b first.

Open question for the next pass, not attempted: independent W/L may simply be the wrong
parameterization for a bias-critical topology. The gm/ID route (`spicexplorer-gmid` is in the
workspace) searches current densities and lets sizing follow, which structurally cannot
produce a railed stack the same way.
