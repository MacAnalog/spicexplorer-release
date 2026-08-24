# Drawings sizing & validation report — ngspice/ihp lane

> **[REVIEW]** — results record for the 2026-07-18 drawings campaign: (1) CMFB-polarity
> closure (B5), (2) full-drawings IHP bench sweep, (3) optimizer sizing of the unsized
> blocks, (4) xvport port of every drawing to Virtuoso. (Closed-lane simulator
> results are not published in this repository.) Forward checklist stays in
> [`TODO_bio_afe_port.md`](TODO_bio_afe_port.md); drawing-bug history in
> [`DRAWING_REVIEW.md`](DRAWING_REVIEW.md) (§8 = the per-block IHP sweep table).
> Created 2026-07-18. Sections marked *(pending)* fill in as the campaign lands.
> **All sizes/biases/specs are consolidated machine-readably in
> [`sizing-and-specs.yaml`](sizing-and-specs.yaml)** — including the FULL-PRECISION
> optimizer winners (amp_025's is bistable: rounded knobs land in the wrong basin).

## 1. Strategy

Two engines, one truth per block:

- **Open lane (ngspice, ihp-sg13g2, native)**: decks assembled from the committed
  `simulation/` xschem exports; benches per block (dc op, CMFB plant-sign, closed-loop
  CM + kick, diff AC, IA cap-ratio gain, static-phase filter corner). This lane found
  the polarities, the actuator fix, and all §8 metrics.
- **Sizing**: nothing in `drawings/` is deliberately sized (seed = min-size). Strategy:
  (a) adopt the landed `circuits/` sizing where a block already has one (amp_020/025/
  026/027/029, ia_002/003, sup_003 — validated against their scoreboards in §8);
  (b) for the genuinely unsized `SRMC-core-amp`, optimizer-drive the sizing with the
  SpiceXplorer YAML DSL (`raw_optimize/` lane, Nevergrad) against explicit targets
  (dcgain ≥ 55 dB, UGF ≥ 2 MHz @ 50 fF, PM ≥ 60°, I ≤ 100 µA, CM errors ≤ 20 mV,
  servos in-rail); (c) fine-tune the weak landed amp_025 sizing (35.8 dB vs its 60 dB
  datasheet target) the same way.
- **Closed lane (Spectre, virtuoso-bridge, kit-unbound)**: every drawing ported to
  real Virtuoso cellviews with `xvport` (device map sg13_lv_* → the target kit's
  low-Vt devices, per-finger w, simM; R/C/V/VCCS → analogLib), proven per block by
  xvport's three oracles (verify = terminal bindings; netcheck = circuitgraph
  isomorphism vs Virtuoso's own netlist; simcheck = Spectre DC op with the user's
  own NDA-neutral model wrapper). Closed-lane bench numbers are not published here.
- **NDA**: no kit model bytes, device names, corner names, or results keyed to a
  licensed kit are committed; decks reference only the user's local model wrapper.

## 2. CMFB polarity closure (B5) — done, sim-proven

Full detail in `TODO_bio_afe_port.md` §B5-resolution. Summary: SRMC's two per-stage
plants are inverting → canonical `cmfb-output-ideal-amp` on both loops (as drawn);
ccia-01's plant is non-inverting → `cmfb-output-ideal-amp-inv` (as drawn). Wrong
pairing winds the unclamped ideal servo out of rail. Source fixes landed: XM8
0.15u→0.5u + VB2 0.5→0.7 V (loop-1 actuator authority); stale `ccia-dut.spice`
re-exported. Method landed as the amplifier-class template `dc_cmfb_plant_sign`.

## 3. IHP (ngspice) validation — every block benched

The per-block table lives in `DRAWING_REVIEW.md` §8 (21 blocks, all OK / expected-fail
with reasons). Headline numbers:

| Block | IHP headline |
|---|---|
| SRMC-core-amp-w-cmfb | CM 0.500±0.001 both loops; diff 41.0 dB, GBW 6.8 MHz (not unity-gain stable — feedthrough shelf) |
| SRMC filter (transistor) | corner == ideal within 0.1 % at duty-scaled R_eff (150 kHz proxy) |
| ccia-ideal / PGA-ideal / afe-ideal | ×1.0 / 1–4× per code (thermometer) / +11.7 dB chain |
| ccia-01 two-stage-ota-core (amp_025 sizing) | IA dut 24.5 dB (ideal 26), CM 0.599, servo in-rail |
| ccia-02 two-stage-opamp-core (amp_026 sizing) | 61.7 dB / 20.8 MHz / 64.3° |
| ccia-02 integrator-switchcap-opamp (amp_027 sizing) | 46.6 dB / 47.6° (= scoreboard); functional single-sided CM loop |
| ia_002 / ia_003 duts (sized) | 25.72 dB (ideal 26.02); PF benign static |
| OTA amp_020 / amp_029 | 24.8 dB / 22 MHz / 90.2° ; no-interior-CM-point reproduced |

## 4. Optimizer sizing (IHP) — DONE (winners verified; honest misses recorded)

### 4.1 `SRMC-core-amp` — sized: seed was UNSTABLE, winner meets specs (gain −0.33 dB shy)

Campaign: the YAML-DSL runs plateaued in the wound-servo region; a seeded scripted
Nevergrad run (400 budget, checkpointed) found the basin, and a 100-loop banded refine
seeded at its best produced the winner.

| Device group | Seed (drawn) | **Winner W / L** |
|---|---|---|
| XM3/XM4 NMOS input pair | 0.15µ/0.13µ | **1.93 µ / 0.717 µ** |
| XM6/XM7 PMOS input pair | 0.15µ/0.13µ | **4.33 µ / 0.554 µ** |
| XM5 NMOS tail | 0.15µ/0.13µ | **2.65 µ / 0.486 µ** |
| XM8 PMOS tail | 0.5µ/0.13µ | **2.86 µ / 0.444 µ** |
| XM1/XM9 output NMOS | 0.15µ/0.13µ | **2.02 µ / 0.428 µ** |
| XM2/XM10 output PMOS | 0.15µ/0.13µ | **1.59 µ / 0.576 µ** |
| Cc / Rz / VB2 | 1p / 1k / 0.7 | **0.583 pF / 2.10 kΩ / 0.700 V** |

Before → after (IHP tt, 1.2 V, VCM 0.5, refs 0.5, 50 f): dcgain 39.9 → **54.67 dB**
(target 55 — honest −0.33 dB miss), UGF 34.7 M → **76.2 MHz**, PM **−17.8°
(seed compensation UNSTABLE) → 60.2°**, i_supply 4.05 µ → **96.9 µA**, CM errors
**0.21/0.31 mV**, servos **0.214/0.309 V in-rail**. Standalone verification: op/AC
reproduce; **loop-2 CM kick PASS** (zero residual); **loop-1 CM kick FAILS** — a
100 nA kick escapes the interior basin (servo winds out of rail): loop 1 is only
*locally* stable with the unclamped ideal servo. Follow-up: rail-clamped CMFB
macromodel variant, or a loop-1 kick spec inside the next campaign.

### 4.2 `amp_025` fine-tune — gain is a TOPOLOGY limit, not a sizing miss

Three campaigns (250 full-bounds / 250 banded / 300 gain-weighted): best
**38.83 dB** vs the 55–60 dB target — full-bounds collapsed, banded won, gain-weighted
traded current for nothing. Within this two-stage class-AB topology at 1.2 V the DC
gain plateaus at ~38–39 dB (seed 35.8); reaching 55+ needs cascoding/longer-L second
stage — a topology change (consistent with the LVT single-stage gm/gds ceiling).
Wins kept: PM 73.9 → **84.1°**, i_supply 173.6 → **105.5 µA**, UGF 10.5 MHz (≥3 M ✓),
vocm 0.5994 ✓, vcmfb 0.648 in-rail ✓, CM-kick PASS. Winner knob table in the session
artifacts (`opt/t2/winner_params.json`). **Robustness flag:** the DC solution is
bistable — rounding knobs to 6 significant digits flips verification into the
wound-servo basin; the winner verifies only at full precision. Any adoption into
`circuits/amp_025` sizing.yaml must carry full-precision defaults.

### 4.3 Clocked SRMC corner (FS = 5 kHz, duty 0.5 / 0.1) — clocked CM healthy;
corner scaling unobservable at seed component values

Quiet clocked runs: vocm 0.5007 at both duties, vodm ≈ 0 — **the CM loops hold under
real clocking** (the former gating concern, resolved). In-band clocked gains
(100–2500 Hz): −5.2…−5.4 dB (d=0.5), −5.0…−5.6 dB (d=0.1) vs static −4.67 dB. The
R_eff = R/d corner prediction lands 4 decades ABOVE the FS/2 = 2.5 kHz observable band
at the drawn placeholder values (Rf=1 kΩ, Cf=1 pF → static corner ~159 MHz), so
corner-vs-duty cannot be resolved by any 5 kHz-clock tran; observing the paper's
40–320 Hz axis needs Rf·Cf scaled ~10⁴× — **owner decision on the filter component
values** (the drawn 1 k/1 p are placeholders).

## 5. Virtuoso port — DONE, all oracles green (24 cells in `xvport_dev`)

**Every drawing ported and proven**: verify (terminal bindings) + netcheck
(circuitgraph isomorphism vs Virtuoso's own netlist) + simcheck (Spectre DC op with
the operator wrapper) pass for all 24 cells — including the full `afe-ideal` chain,
both ccia-02 duts, and (with `--no-simcheck`, by design) the unbiasable
`two-stage-skeleton`. No `--prefix` collisions; `--with-symbols` walks re-use
already-ported deps cleanly.

**Port gotchas + two real xvport bugs found (candidates for platform issues):**
- *G1* — a cell instantiating local masters must be ported `--with-symbols`, else the
  `.il` load fails (`dbOpenCellViewByType(… "symbol")` on a never-ported dep).
- *G2* — netcheck of depth-2 sources (`shared/ideal/*`) needs
  `XSCHEM_LIBRARY_PATH=<drawings root>` (endcheck's rcfile adds only source dir+parent).
- *G3 (xvport bug)* — **labels-mode stub labels fail to bind on odd-rotation kit MOS
  pins** (ccia-dut M1–M4 at MXR90/R90/MYR90/R270: `verify FAILED — M1.B: expected
  'net3' got 'net6'`). Same drawing ports all-green with `--mode wires`.
- *G4 (xvport bug)* — **xvport trusts stale stored wire `lab=` attrs** (netex.py wire
  union): in `two-stage-miller-comp-common-mode-control.sch` a stale `lab=B` on the
  mirror-reference island merges disjoint B/REF islands into a real short in the
  cellview — caught by the netcheck oracle (`net count differs: 15 vs 14`); xschem
  itself re-derives labels and netlists them separately. Ported green from a
  wire-attr-stripped scratch copy; every other block's netcheck passed, so no other
  port is affected.
- Also: the daemon `load()`s the `.il` from Virtuoso's own cwd → pass `-o` with an
  ABSOLUTE path; the target library must already exist (`xvport_dev`).

## 7. Open items after this campaign

**Owner decisions:**
- ~~capbank thermometer-vs-binary weighting~~ — **DECIDED binary, landed 2026-07-19**:
  value=Cu (TB-supplied unit) with structural m=1/2/4 weighting → C_eff=(1+code)·Cu;
  live-validated exact 1–8 pF + PGA gains (1+code) within 0.08 dB (DRAWING_REVIEW §8
  finding 1). Closed-lane follow-up: re-port capbank with an m-aware capa map rule
  when the daemon returns (xvport currently drops cap m).
- SRMC filter component values: the drawn Rf=1 k/Cf=1 p placeholders put the clocked
  corner 4 decades above FS/2 — scale Rf·Cf ~10⁴× to realize the paper's 40–320 Hz
  axis (§4.3).

**Engineering follow-ups:**
- Rail-clamped ideal-CMFB macromodel variant (`shared/ideal/`): the unclamped servo
  hides rail-outs (§6.1) and creates escapable latch basins (§4.1 loop-1 kick FAIL).
  **Superseded for the SRMC consumer 2026-07-20**: the REAL 5T CMFB (§8) is
  rail-clamped by construction and both kicks recover with zero residual; the
  macromodel variant remains open only for consumers that stay on ideal servos.
- ~~Adopt the §4.1 SRMC sizing~~ — **DONE 2026-07-19: landed as
  `circuits/amp_031_srmc_core_cmfb`** (full-precision sized binding; T3 3/3 + T4
  primary PASS; CM-kick tails recorded-indicative). Also landed:
  `sw_003_binary_capbank` + `ia_005_hsu_pga_ideal` (documented-only benches — the
  code-pin-aware bench template is the follow-up) and the `afe` class scaffold.
- amp_025 sizing adoption is NOT recommended as-is: +3 dB gain for a bistable
  knife-edge DC solution (§4.2) — the cascode topology change is the real fix.
- Two xvport bugs to file upstream (§5 G3 labels-mode rotation binding, G4 stale
  wire-lab attrs; workarounds known).
- Clocked benches beyond the SRMC corner (notch/aliasing FFT, chain e2e, TRNOISE /
  pss+pnoise clocked noise) — `TODO_bio_afe_port.md` bench-gaps list; ccia-02 clocked
  operation remains architecture-blocked (CM bistability, P4-4b core-CM closure).

## 8. Real 5T-amp CMFB (addendum 2026-07-20) — sized, validated, consumer landed

The owner drew transistor-level CMFB error amps to replace the ideal servos
(`drawings/shared/`): `amp-single-ended-5t-{nmos,pmos}-input` (5T OTA + on-cell
2-diode bias string — no external bias pin) wrapped as
`cmfb-output-amp-5t-{nmos,pmos}-input` (detector R-pair + amp). The wrapper pin
footprint is **identical to the ideal pair**, so swapping a consumer between ideal
and real CMFB is a pure symbol-path change — the design intent. This pass added the
`-inv` swapped-input variants (for non-inverting plants, B5 rule), sized both
flavors, and landed the SRMC consumer variant.

**Polarity + baseline (drawn min sizes, vref 0.5).** Standalone dc sweeps: canonical
slopes +14.0 (nmos-in) / +9.4 (pmos-in); `-inv` mirrors −14.4 / −9.5. In-loop
(sized amp_031 core): the loops close and are stable even at min size, but the low
servo gain costs ~35 mV static CM error, which starves the output-stage drivers and
drags diff PM to 43–47° (vs 60.2° ideal-servo baseline) — the sizing target in one
sentence: buy servo gain to shrink CM error and recover PM.

**Sizing (per-flavor Nevergrad TwoPointsDE, ~400 evals, 8 workers).** One eval = one
ngspice run (diff AC + 20 µs dual-kick tran, op read from pre-kick samples); score =
CM errors + PM/gain/UGF floors + kick residual/ring + supply-current budget.
Full-precision winners + rounded 3-sigfig values in `sizing-and-specs.yaml
shared.real_5t_cmfb`; **rounded values reproduce the winner metrics exactly** (the
loop is not bistable) and are committed in the `.sch` files.

| flavor | CM err loop1/loop2 | dcgain | UGF | PM | I_supply | kick resid |
|---|---|---|---|---|---|---|
| **pmos-input (chosen)** | 3.6 / 2.1 mV | 54.72 dB | 76.9 MHz | 58.9° | 116.4 µA | 0.000 mV both |
| nmos-input (secondary) | 3.8 / 4.8 mV | 54.72 dB | 76.9 MHz | 58.9° | 112.9 µA | 0.000 mV both |

The pmos flavor wins on CM accuracy (its natural output 0.502 V sits closest to the
0.215/0.318 V the actuator gates need) and its input pair is comfortable at the
0.5 V sensed CM. Diff metrics match the ideal-servo binding to within ~1° PM.

**Consumer landed.** `SRMC-core-amp-w-cmfb-5t.sch` (bio-afe-01) = the ideal
consumer with both servo symbols swapped to `shared/cmfb-output-amp-5t-pmos-input`.
End-to-end from its committed export (sized core overlay): CM err 2.1 mV,
54.72 dB / 76.9 MHz / PM 58.9°, 116.4 µA, kick residual 0.000. Both ideal and real
consumers stay available side by side.

**Findings / gotchas:**
- **Rail-clamped by construction**: both CM kicks recover with zero residual —
  closes §4.1's loop-1 basin-escape and supersedes the rail-clamped-macromodel
  follow-up for this consumer.
- **Real-servo static CM error** ≈ (needed actuator gate − amp natural output) /
  A_servo: pick the flavor whose natural output sits near the plant's balance gates.
- **xschem CLI port-order footgun**: `--netlist` orders top-level ports by pin
  *object order in the .sch file*, not by type — a fresh consumer .sch netlisted
  with VDD/VSS first while the (GUI-exported) ideal consumer has vinp-first. Fixed
  by reordering the pin objects in the new .sch to match; check `**.subckt` order
  whenever creating a consumer variant by copy.
- ngspice MAX/MIN `meas` lines append ` at= <x>`; an end-anchored parse regex
  silently drops them (harness bug found + fixed this pass).
- nevergrad `NGOpt` crashes in its metamodel step on this numpy (0-dim scalar
  TypeError) at ~eval 112 — use `TwoPointsDE` for scripted lanes.

**Follow-ups:** ccia consumer with the `-inv` real wrapper (needs its own sizing —
different plant, different balance gates); closed-lane port of the six new cells when the
CIW daemon returns; the ideal-macromodel rail-clamp item stays open for
ideal-servo consumers only. **Accessioned 2026-07-20 (same day):** the dedicated
`cmfb` class now exists — `cmfb_001_ideal_rsense_servo` (re-classed sup_002),
`cmfb_002_5t_pmos_input` (this section's chosen winner), `cmfb_003_5t_nmos_input`
(secondary); rigorous block-level suite (dc_cmfb_transfer / ac_servo /
tran_cmfb_step) live on all three, all specs pass.
