# Worked reference designs (book Ch 5 & Ch 6)

Concrete sized designs from Jespers & Murmann, "Practical Circuit Examples I" (Ch 5:
bias / LDO / LNA / charge amp / PVT) and "Practical Circuit Examples II" (Ch 6: OTAs,
switches). Use these as **anchors**: when you size one of these blocks, your gm/ID, ID,
W, and cap values should land in the same ballpark, and your SPICE deltas should match
the "verified" line. All in a **65 nm** process, VDD = 1.2 V unless noted; γ (thermal
noise factor) ≈ 0.7–0.8. Numbers are the book's; treat as ±a few % targets, not exact.

The book's flow-level methodology is in `ota-recipes.md` (Ch 6) and `biasing-and-pvt.md`
(Ch 5); this file is the numeric companion. Cite the example number (e.g. "Ex 6.6"), not
a page — the PDF filename page ranges are mislabeled.

---

## Ch 6 — OTAs in the SC gain stage

Shared config: sampling cap CS, feedback CF, load CL; closed-loop gain G = CS/CF, fan-out
FO = CL/CS, feedback factor β. βmax = 1/(1+G). Optimum β ≈ 0.75·βmax. fTi = gm/Cgs
(lookup `GM_CGS`), distinct from fT = gm/Cgg.

### Ex 6.2 — Basic OTA (NMOS pair, ideal loads), linear settling
- **Specs**: fu = 1 GHz, integrated output noise = 100 µV_rms, G = 2, FO = 1, L = 100 nm,
  εd < 0.1 %.
- **Sized**: gm/ID = 20.4 S/A (from the K-minimum, Table 6.1 FO=1 row), β = 0.825·βmax =
  0.275, CLtot = 2·(γ/β)·kT/vod² = 2.1 pF, gm = CLtot·ωu/β = 48.2 mS, ID = gm/(gm/ID) =
  2.36 mA, W = ID/JD = 783 µm. Caps: CFtot = 774 fF, CS = CL = 1.55 pF, CF = CFtot − Cgd =
  515 fF (Cgd = 259 fF). Static gain error εs ≈ −1/(β·gm/gds) = −15 % (gm/gds = 24.2).
  ts = τ·ln(1/εd) = 6.9·τ = 1.10 ns.
- **Verified (SPICE)**: DC gain 4.68 dB (calc 4.61), fc 1.05 GHz, settle-to-0.1 % ≈ 1.06 ns;
  integrated noise **90.4 µV (≈10 % LOW** — neglected Cdb ≈ 230 fF). Noise-scaling fix:
  S = (90.4/100)² = 0.81, multiply all C/W/ID by S (−19 % current), response unchanged.
- **Lesson**: a basic OTA at short L lands at εs ≈ −15 % — usually unusable; that pushes you
  to a longer L or a cascode/two-stage topology.

### Ex 6.3 — Basic OTA with slewing
- **Specs**: same as Ex 6.2 but large-signal, ts = 1.1 ns @ 0.1 %, design at vOD,final = 800 mV.
- **Sized** (2-D self-consistent β × gm/ID search): gm/ID = 19.55, β = 0.277, ID = 2.6 mA,
  W = 713.5 µm, CLtot = 2.09 pF, CFtot = 768 fF, CS = CL = 1.54 pF, CF = 532 fF,
  SR = 2.45×10⁹ V/s, t_slew = 176 ps (**≈16 % of ts**; ≈32 % at 1600 mV).
- **Verified**: ts ≈ 1.12 ns. Observed SR ~20 % below predicted: ~10 % extra junction cap +
  the diff pair never fully steers (~10 % current stays in the "off" device).

### Ex 6.6 — Folded-cascode OTA
- **Topology**: NMOS input pair M1; bottom NMOS mirror M2; NMOS cascode M3; PMOS cascode M4;
  PMOS source M5. W2 = 2·W3 ⇒ gm2 = 2·gm3.
- **Specs**: ts = 5 ns @ 0.1 %, integrated diff output noise = 400 µV_rms, G = 2, FO = 0.5.
- **Output branch** (Ex 6.4): 0.8 Vpp-diff swing → ~200 mV VDS/device → gm/ID ≥ 2/VDsat = 10;
  pick **gm/ID = 15** (all of M2–M5). L2=L3=L4=L5 = **0.4 µm** for L0 > 50. fp2 = 1.45 GHz,
  fp2/fu1 = 6.6 → PM ≈ 81° (justifies the first-order ts estimate).
- **Input pair** (Ex 6.5): gm/ID1 = 18.7, ID1 = 163 µA, **L1 = 200 nm** (≈2×Lmin sweet spot;
  rself ≈ 40 % of CLtot at L=0.4 µm forces the longer-L diminishing-returns choice),
  β/βmax = 0.728, CLtot = 508 fF, rself = 0.23. fTi1 ≈ 2.5 GHz ≈ 11×fu1.
- **Geometries** (W/L µm | gm/ID): M1 119/0.2 | 18.7 · M2 129/0.4 | 15 · M3 64.5/0.4 | 15 ·
  M4 142/0.4 | 15 · M5 142/0.4 | 15. Tail 2·ID1 = 326 µA. Caps CF = 224 fF, CS = 448 fF,
  CL = 224 fF.
- **Verified**: loop fu = 207.9 MHz (calc 220), PM = 81.1°, DC loop gain 38.9 dB (88) > 50,
  settle-0.1 % = 4.39 ns (~12 % faster than 5 ns spec — 2nd-pole speedup), integrated noise
  **396.8 µV (on target** — folded-cascode noise eqs have no large approximation).

### Ex 6.8 — Two-stage Miller OTA
- **Topology**: NMOS input pair (PMOS loads) → NMOS common-source 2nd stage (PMOS loads);
  Miller CC with RZ = 1/gm2 (kills the RHP zero); neutralization caps Cn at stage-1 input
  remove the input Miller term so β ≈ CF/(CF+CS+Cgg1).
- **Specs**: same as Ex 6.6 (ts = 5 ns, noise = 400 µV_rms, G = 2, FO = 0.5). L1=L4=150 nm,
  L2=L3=200 nm. gm3/gm1 = 1, gm4/gm2 = 0.5. fp2/fu1 = 6 (PM ~80°). Cgs2/CC = 0.3.
- **Sized**: gm/ID1 = 15.2, gm/ID2 = 20.6, ID1 = 157 µA, ID2 = 196 µA (total 353 µA),
  β/βmax = 0.81, CLtot/CC = 0.53, CC = 416 fF, CS = 198 fF, RZ = 247 Ω, rself1 = 0.40,
  rself2 = 0.28.
- **Geometries** (W/L µm | gm/ID): M1 48.4/0.15 | 15.2 · M3 32.3/0.2 | 15.2 ·
  M2b 120.3/0.2 | 20.6 · M4 22.1/0.15 | 10.3. Cn = 17 fF; explicit Miller add = 375 fF.
- **Verified**: loop fu = 203.4 MHz (calc 220), PM = 79.6°, DC loop gain 39.3 dB (93) > 50,
  settle-0.1 % = 4.24 ns (~15 % faster), integrated noise **436.8 µV (≈9 % HIGH** —
  approximate γ + ignored flicker; fix by scaling +9 % or bumping CC).
- **Topology call**: two-stage total current ≈ 706 µA vs folded-cascode ≈ 652 µA for the
  same specs (~8 % apart). Pick by **swing/CM-range, not power**: two-stage for large output
  swing (fewer stacked devices), folded-cascode for wider input common-mode range.

### Switch sizing (§6.5)
Transmission gate (NMOS ∥ PMOS), ron = ron,n ∥ ron,p, each ron = 1/gds at VDS = 0 (triode):
`lookup(dev, 'GDS', VGS=VDD−VIN, VSB=VIN, VDS=0)`. ron,n is lowest at VIN = 0, ron,p lowest
at VIN = VDD; total ron peaks near mid-supply. VIN sets VSB, so step VIN only on the VSB
grid and spline-interpolate. Size PMOS larger (k > 1) to flatten ron(VIN); L = Lmin.

---

## Ch 5 — Bias, regulators, RF, sensor front-ends

### Ex 5.1 — Constant-gm bias generator
- **Topology**: PMOS mirror M3–M4 (1:1) over NMOS pair M1–M2 (W1 > W2) with degeneration R
  under M1. M2 diode-connected, in its **own well (VSB2 = 0)**. Start-up circuit mandatory.
- **Specs**: ID = 50 µA, VDD = 1.2 V, VR = R·ID = 0.1 V, all L = 0.5 µm. Design point W2 = 15 µm.
- **Sized** (one current, three very different inversion levels — normal):
  M2 gm/ID = 13.29 (W2 = 15 µm), M1 gm/ID = 21.59 (W1 = 82.6 µm), M3 gm/ID = 6.86
  (W3 = 6.99 µm). R = 2 kΩ, VGS2 = 0.514 V, gm2 = 659 µS.
- **gm law**: weak inv gm2 = ln(W1/W2)/R; strong inv gm2 = (2/R)(1−√(W2/W1)).
- **Verified**: temperature only (−40…125 °C, Fig 5.5) → **gm2 within ~±1 %** while ID swings
  −20/+30 %. Full process corners (Ex 5.10, fast/cold & slow/hot) widen it: gm2 −4.0/+4.2 %,
  ID −22/+34 %, VGS2 ±16 mV — still far tighter on gm2 than on ID, which is the whole point;
  budget for the current swing. VDD ±: ID and gm both ~±10 % (DIBL/CLM in non-diode M1/M4 —
  fix by cascoding M1, M4 if it matters).

### High-swing cascoded current mirror
- **Topology**: core M1(diode)–M3(output), cascodes M2/M4 equalize VDS1=VDS3, diode stack
  M6–M7 sets VBIAS.
- **Specs**: Iin = Iout = 100 µA, gm/ID = 20, L = 500 nm. One knob: VX margin above VDsat.
- **VX trade** (VDS1 = 2/(gm/ID) + VX = 0.1 V + VX):

  | VX | VDS1 | core VEA | Rout @100µA | W |
  |---|---|---|---|---|
  | 0 mV | 100 mV | 0.556 V | 0.49 MΩ | 146 µm |
  | **50 mV** | **150 mV** | **1.729 V** | **1.23 MΩ** | 131 µm |
  | 100 mV | 200 mV | 2.285 V | 1.37 MΩ | 128 µm |

  **Use VX = 50 mV**: VX=0 puts gds at the cliff (VEA collapses 1.73→0.56 V); VX=100 mV buys
  little and costs compliance. Uncascoded core for comparison: VGS=0.438 V, W=121 µm,
  VEA=4.19 V, Rout only 20→80 kΩ over VOUT.
- **Verified**: with VX = 50 mV, Iout flat **< 0.2 %** for VOUT from ~0.3 V to VDD; if current
  droops early, the realized VDsat exceeds 2/(gm/ID) — re-check the inversion level.

### Ex 5.2 — Low-dropout regulator (LDO)
- **Topology**: series **common-source PMOS** pass device M1 (CD-NMOS would need ~VT of
  dropout — impractical < 0.4 V); diff-amp error stage; f = 1.
- **Specs**: 10 mA load, VOUT = 0.9 V, VDD = 1.2 V (dropout 0.3 V), maximize loop gain.
- **Sized**: series M1 L = 100 nm, **gm/ID1 = 10** (must be > 6.6 to keep VDsat < 0.3 V dropout)
  → A1 = 4.78, W1 = 890 µm, VGS1 = 0.637 V. Diff-amp L = 500 nm, gm/ID = 20 → Aa = 25.2,
  Wp = 20.4 µm, Wn = 127 µm, tail = **2·IDn = 0.2 mA (~2 % of load)**. Loop gain A1·Aa = 120.
- **Key**: PSR_OL = (YL+gds1)/gds1 ≈ 2–3× only (here 2.13) → feedback amp mandatory.
  Closed-loop PSR = PSR_OL + (gm/gds)1·Aa = 259; Rout ≈ 1/(gm1·Aa) = 0.4 Ω.
- **Load cap** (Ex 5.3): choose CL to cancel the regulation zero — poles go real at CL ≈ 140 nF,
  pole-on-zero (flat, no peaking) at CL ≈ 191 nF; resulting cutoff ≈ 9.6 MHz (calc) /
  8.67 MHz (SPICE), low-freq |vout/vdd| = −48 dB = 1/PSR.
- **Verified**: PSR 257 (calc 259), Rout 0.39 Ω (calc 0.40).

### Ex 5.4 — Noise-cancelling LNA (CG + CS active balun)
- **Topology**: CG stage M1 (load R1, source-degen RB) + CS stage M2 (load R2); single-ended
  in → differential out. Cancels M1 thermal noise + distortion when **A_v,CG = A_v,CS**.
- **Specs**: NF ≤ 2.5 dB, input match RS = 50 Ω, VDD = 1.2 V, VR1 = VR2 = 0.4 V, L = 100 nm,
  gm/ID2 = 14.
- **Sized**: input match **1/gms1 = RS** (gms = gm+gmb) fixes the CG current → ID1 = 1.5 mA,
  ID2 = 5.24 mA, W1 = 142.7 µm, W2 = 448.8 µm, R1 = 267 Ω, R2 = 76.2 Ω, RB = 337 Ω,
  fT1 = 22 GHz.
- **Verified**: NF 2.30 dB (≤ 2.5 dB over 10 MHz–2 GHz), gain 9.08, IDs within < 1 %.
- **HD2-min variant** (Ex 5.5): AC-couples so VR1 ≠ VR2; uses **VR2 = 0.3 V** (the "VR ≥ 0.5 V"
  figure is the *general* HD2-null constraint inherited from Ch 4, not a hard rule here),
  L = 80 nm, ID2/ID1 = 11. Cancellation only helps small signals (< ~−15 dBm); IIP2 ≈ 37.7 dBm
  in SPICE but large blockers still raise HD2.

### Ex 5.8 — Charge amplifier (capacitive sensor front-end)
- **Topology**: input device M1 (transducer CS + signal on gate), feedback CF, wideband
  unity-gain buffer, fixed bias ID.
- **Specs**: fc = 3 GHz, input noise 50 pA/√Hz @ fc, CS = 1 pF, CFtot/C1 = 3, L = 100 nm,
  γn = 0.7.
- **Sized**: CS+CF = 3.30 pF → CF = 2.30 pF, Cgg = 511 fF (Cgg/(CS+CF) from the noise+BW
  optimum, ≈ (CS+CF)/2 region but read numerically), gm = ωT·Cgg = 24 mS, gm/ID from the
  L=100 nm optimum → ID = 1.09 mA, JD = 2.2 µA/µm, W = 495 µm. Buffer CB = 658 fF.
- **Input-device optimum** (Ex 5.6/5.7): constant-ωT → Cgg = CS+CF; **constant-ID square-law
  → (CS+CF)/3 but the real 60 nm optimum ≈ 0.14·(CS+CF)** (the 1/3 rule oversizes ~2.4× and
  costs ~15 % noise — always locate it numerically); noise+BW-constrained → Cgg = (CS+CF)/2.
- **Verified**: gain −8.47 dB (calc −7.84, the gap is neglected rds of M1), fc 3.19 GHz,
  input noise 49 pA/√Hz; gm 23.6 mS (sim VDS 427 mV vs 600 assumed).
- **Re-size for area** (Ex 5.9): forcing gm/ID = 18 → W = 272 µm (−45 %) at the cost of
  ID = 1.33 mA (+22 %). The current-vs-area trade at the optimum is shallow and nearly free.

### Ex 5.11 — Corner-aware charge amp (spec pre-distortion in action)
- Constant-current bias ⇒ gm drops ~30 % slow/hot ⇒ **pre-distort: BW target = fc/0.7 =
  1.4× = 4.2 GHz**. Re-optimized: gm/ID = 20.5 (vs 21.9 nominal), ID = 1.17 mA (**only +10 %**
  vs the 1.09 mA nominal design despite +40 % bandwidth — over-bandwidth is cheap on the
  shallow current minimum), W = 395 µm.
- **Verified across corners**: fc = 3.19 / 4.37 / 5.74 GHz and noise = 46.8 / 35.4 / 27.7
  pA/√Hz at slow-hot / nominal / fast-cold — **meets spec at every corner**. Noise margin is
  slightly larger than bandwidth margin (kT adds temperature dependence beyond the gm swing).
