# OTA design recipes (switched-capacitor context)

Distilled from Ch 6 of the source text (see book-map.md). Three topologies:
basic OTA, folded-cascode, two-stage Miller. All are designed inside the SC
feedback configuration: sampling cap CS, feedback cap CF, explicit load CL,
closed-loop gain G = CS/CF, fan-out FO = CL/CS. All flows minimize current for
given noise + settling specs by searching over (gm/ID, beta).

## 0. Shared SC settling framework (derive these before any sizing)

Specs in: settling time ts, dynamic settling error eps_d, static gain error
eps_s, total integrated differential output noise vod_rms, G, FO, output
swing vod_final, supply and common mode.

Derived:
- First-order bandwidth target: tau = ts / ln(1/eps_d), fu = 1/(2*pi*tau).
  This is conservative when a second pole at fp2/fu1 = 4..6 exists (real
  settling is up to ~33% faster at 0.1 percent accuracy); keep it as margin.
- beta_max = 1/(1+G). Loop gain need: L0 > 1/eps_s (often spec L0 > 50).
- Sampled noise: vod^2 = alpha*kB*T/(beta*CLtot), alpha = 2*gamma_n for the
  basic OTA, larger with excess-noise terms for cascode/two-stage (below).
  Noise sets CLtot, never the other way around.
- Bandwidth: wu = beta*gm/CLtot (basic; kappa factor for folded-cascode,
  exact two-pole expression for two-stage).
- Slewing parameter: X = vod_final*(beta/2)*(gm/ID). If X > 1 the circuit
  slews; required wu1 = (1/ts)*[X - 1 + ln(1/(eps_d*X))]. X <= 1 reduces to
  the linear case. Slewing pushes optima to slightly lower gm/ID.

Structural facts the cap/noise/bandwidth math depends on (get these right or the
numbers drift):
- fTi = gm/Cgs (lookup 'GM_CGS'), NOT fT = gm/Cgg ('GM_CGG'). The OTA optima use
  the intrinsic fTi (gate-source only); fTi is slightly above fT. Use GM_CGS for
  the wTi in these flows; GM_CGG only when you mean the full transit frequency.
- CFtot composition differs by topology: basic OTA CFtot = CF + Cgd1 (the input
  pair's Cgd is across CF), so CF = CFtot - Cgd1 for the netlist. Folded-cascode:
  Cgd1 is NOT across CF (CFtot -> CF); instead Cgd1 enters the input cap via the
  Miller term Cin = Cgg1 + Cgd1*(gm1/gm3). Two-stage: neutralization caps Cn = Cgd1
  cancel the input Miller, so beta = CF/(CF + CS + Cgg1).
- Self-loading has ONE term in the basic/folded OTA (rself at the output) but TWO
  in the two-stage: rself2 = (Cdb2+Cdd4)/(CL+(1-beta)CF) at the output AND
  rself1 = (Cdd1+Cdd3)/Cgs2 at the internal node; C1 = Cgs2*(1+rself1). Iterate both.

## 1. The master tradeoff (why an optimum gm/ID exists)

Minimizing ID at fixed noise and bandwidth reduces to minimizing
K = 1/(beta^2 * gm/ID). Raising gm/ID buys current efficiency but lowers
fTi = gm/Cgs, inflating Cgs, which sinks beta and demands more gm. The
optimum is in moderate inversion and is SHALLOW: being off by 2-3 S/A costs
only a few percent of current. Agents should exploit the shallowness: prefer
slightly lower gm/ID than optimal to cut W and area at near-zero power cost.

First-order optima (strong-inversion algebra; use as sanity anchors):
- beta_opt = 0.75*beta_max (holds within a few percent in every worked case)
- Basic OTA: Cgs_opt = (CS + CFtot)/3, wTi_opt = 3*(FO*G + 1)*wu.
  With self-loading and moderate inversion, the realized fTi/fu1 lands at
  ~7-11; treat wTi/wu >= ~6-10 as a technology feasibility gate.
- Charge amplifier (continuous-time, Ch 5): Cgs_opt = (CS + CFtot)/2.

## 2. Basic OTA (single diff pair + ideal loads), linear settling

1. Sweep gm/ID; get wTi = dev.look_up('GM_CGS', GM_ID=vec, L=L).
2. beta(gm/ID) = [1 - (1+FO*G)*wu/wTi] / [1 + G - wu/wTi]; K = 1/(beta^2*gm_id).
3. Pick the K minimum (or beta = 0.75*beta_max shortcut).
4. CLtot = alpha*kB*T/(beta*vod^2); gm = wu*CLtot/beta; ID = gm/gm_id.
5. W = ID / dev.look_up('ID_W', GM_ID=gm_id, L=L).
6. Caps: CLtot = CL + (1-beta)*CFtot with CL = FO*G*CFtot, so
   CFtot = CLtot/(FO*G + 1 - beta); CS = G*CFtot; CL = FO*CS.
   For simulation, CF = CFtot - Cgd, Cgd = W*dev.look_up('CGD_W',...).
7. Static gain error eps_s ~ 1/(beta*gm_gds); settle check ts = tau*ln(1/eps_d).

Noise scaling remedy (use after SPICE, costless elsewhere): if simulated noise
power deviates by factor S from spec, multiply ALL capacitances, widths, and
currents by S. Current densities, gm/ID, fT, and every gm/C ratio are
preserved, so the frequency response is untouched while noise scales as 1/C.

## 3. Slewing-aware optimization (basic OTA, also reused by the others)

beta and gm/ID are coupled through X, so closed-form optima vanish. Use the
self-consistent 2-D search:

for each beta_k in [0.25..1]*beta_max:
  over the gm/ID vector: CLtot from noise(beta_k); CFtot from cap relations;
  X = vod_final*beta_k/2*gm_id (clamp X < 1 to 1);
  ID = CLtot/(beta_k*gm_id*ts) * (X - 1 - ln(eps_d*X));
  gm = gm_id*ID; Cgs = gm/wTi; beta_actual = CFtot/(CFtot*(1+G) + Cgs);
  a physical design exists where beta_actual crosses beta_k; record it.
Pick the recorded point with minimum ID.

Typical outcome: slewing consumes ~16% of the transient at 0.8 V differential
swing (~32% at 1.6 V) and shifts the optimum a few S/A toward strong inversion.

## 4. Folded-cascode OTA

Divide and conquer: output branch first, input pair second, then assemble.

Phase A, output branch (M2 mirror NMOS, M3 NMOS cascodes, M4 PMOS cascodes,
M5 PMOS sources; W2 = 2*W3 so gm2 = 2*gm3):
1. Swing sets VDsat budget: e.g. 0.8 Vpp-diff around mid-supply leaves
   ~200 mV VDS per stacked device, forcing gm/ID >= 2/VDsat = 10; pick
   ~15 S/A for margin. Little freedom here; only margin can be traded.
2. Channel lengths from the loop-gain budget. Approximate
   1/L0 = 1/(beta*kappa) * [ (gds5/gm5)*(gds4/gm4) + (gds2/gm2 + gds1/gm1)*(gds3/gm3) ]
   evaluated with per-device dev.look_up('GM_GDS', GM_ID=15, VDS=actual, L=Lvec);
   sweep L and pick the shortest meeting L0 spec (worked case: L = 0.4 um for
   L0 > 50). Use kappa ~ 0.7 as the conservative current-division factor
   (kappa = 1/(1 + 2*gds1/gm3) exactly).
3. Non-dominant pole from the chosen branch:
   wp2 ~ gm3*(1+gmb3/gm3) / (Cdd2 + 2*Cdd3) via GM_CSS / GMB_GM / CDD_CSS
   lookups at the cascode bias. This wp2 CAPS the achievable speed because
   robust SC design requires wp2/wu1 >= 4 (Q = 0.5, critically damped,
   PM ~ 76 deg; never go below 4, overshoot is unmanageable; 5-6 is a good
   conservative first pass, PM ~ 79-81 deg).

Phase B, input pair: same self-consistent 2-D (beta x gm/ID) search as the
basic OTA with these substitutions:
- wu1 = beta*kappa*gm1/CLtot.
- CLtot = CL + CF*(1-beta) + Cself, rself = (Cdd3+Cdd4)/(CL + CF*(1-beta)).
- beta = CF/(CF + CS + Cin), Cin = Cgg1 + Cgd1*gm1/gm3 (Miller term).
- Excess noise alpha = 2*gamma1*(1 + gamma5/gamma1*(gm/ID)5/(gm/ID)1
  + 2*gamma2/gamma1*(gm/ID)2/(gm/ID)1) (book eq 6.54). NOTE the factor 2 on the
  M2 (bottom-mirror) term — it carries the full branch current (W2 = 2*W3).
  Cascode devices add ~10-20% more from high-frequency noise folding; budget it.
- Outer iteration on rself (start 0, feed back the realized value, converges
  ~4 iterations). Long input-pair L inflates rself badly (40% of CLtot at
  L = 0.4 um); input pair L ~ 2x Lmin is the typical sweet spot with
  diminishing returns beyond.

Phase C, assembly: ID1 fixed, all gm/ID fixed, so widths follow from ID_W
lookups at each device's actual VDS: W1 = ID1/JD1, W2 = 2*ID1/JD2, W3 = W2/2,
W5 = ID1/JD5, W4 = W5. Caps: CF = CLtot/((FO*G + 1 - beta)*(1 + rself)),
CS = G*CF, CL = FO*CS.

Slewing: SR = 2*kappa*ID1/CLtot; same X formalism with gm1, ID1.

## 5. Two-stage Miller OTA

Use when output swing is the binding constraint (fewer stacked devices);
expect total current within ~10% of the folded-cascode for equal specs, so
swing/common-mode range, not power, decides the topology.

Fixed-by-rule parameters (do not put in the optimizer):
- RZ = 1/gm2 kills the RHP zero; the third pole gm2/C1 then only shaves a few
  degrees of PM and is ignored in sizing.
- Channel lengths from L0 = beta*gm1*R1*gm2*R2 with roughly equal gain split.
- Load-to-signal gm ratios (gm3/gm1, gm4/gm2): pick ~1 and ~0.5; optima are
  shallow, do not optimize.
- Cgs2/CC = 0.5 (charge-amplifier optimum applied to stage 2; 1/3 in the
  conservative simplified flow).
- Neutralization caps Cn remove input Miller so beta = CF/(CF + CS + Cgg1).

Optimizer: 2-D sweep over beta and CLtot/CC (around unity). Every grid point
is feasible (no self-consistency search needed):
a. CC from the noise spec:
   vod^2 = 2*gamma1*kB*T/(beta^2)*(1/CC)*(1+gm3/gm1)... two-term form, stage 1
   referred through CC and stage 2 through CLtot; then all caps follow.
b. gm1 from wu1 using the EXACT two-pole expression; the textbook
   approximation wu1 = beta*gm1/CC errs by up to ~40% when gmR ~ 10. Keep the
   finite-gmR correction terms.
c. (gm/ID)1 from gm1 and Cgg1 (beta fixes Cgg1), hence ID1.
d. gm2 from the non-dominant pole target:
   wp2 = gm2/(C1 + CLtot*(1 + C1/CC)), C1 = Cgs2*(1+rself1).
e. (gm/ID)2 from gm2 and C1, hence ID2; total = ID1 + ID2.
Pick the (beta, CLtot/CC) minimizing total current; outer-iterate rself1,
rself2 as before.

Asymmetric slewing gate (MANDATORY for robustness): the up-going half slews at
min(ID1/CC, ID2/(CC+CLtot)); enforce ID2 > ID1*(1 + CLtot/CC) or the halves
slew at different rates, common mode drifts, and slow settling tails appear.
Mark and exclude the violating region of the (beta, CLtot/CC) grid; pushing
CLtot/CC above the unconstrained current minimum fixes it cheaply. With the
gate satisfied, differential SR = 2*ID1/CC and the standard X formalism holds.

## 6. Simplified deterministic flows (agent default for a first-pass design)

When a full 2-D optimization is overkill, the optima's shallowness justifies
fixed rules. Folded-cascode quick flow: design the cascode branch from swing +
L0 (Phase A above); budget ~30% of ts for slewing and derive wu1; assume
rself = 0.4, beta = 0.75*beta_max, kappa = 0.7, uniform gm/ID for the noise
factor alpha; CLtot from noise; gm1 from wu1; Cgg1 from beta and the caps;
fT1 -> (gm/ID)1 -> ID1; check X and realized ts, adjust slew budget; check
realized self-loading; consider trading down (gm/ID)1 for area; verify in
SPICE starting with small-signal sims. Two-stage quick flow: same skeleton
with Cgs2/CC = 1/3, CLtot = CC initially (this knob balances which stage works
harder; adjust if ID1 and ID2 come out wildly imbalanced), gm1 from wu1 with
gmR-corrected expression, gm2 from fp2/fu1 ~ 6.

## 7. Verification expectations (calibrate pass/fail)

Book-validated deviations to expect when the design is RIGHT (numbers from the
worked Ex 6.2 / 6.6 / 6.8 in worked-examples.md):
- fu and PM within ~5% / ~1 deg of prediction.
- Settling beats the first-order ts estimate; the speedup GROWS with accuracy
  (book Table 6.5, critically-damped fp2/fu1=4): ~15% at eps_d=1%, ~33% at
  eps_d=0.1%. So at the usual 0.1% target expect ~10-15% in the realized cases
  (folded 4.39 vs 5 ns, two-stage 4.24 vs 5 ns) — more at tighter accuracy.
- Integrated noise deviation is TOPOLOGY-DEPENDENT in sign, ~10% magnitude:
  the basic OTA reads ~10% LOW (neglected Cdb ~10% of CLtot), the folded-cascode
  lands on target (no large approximation), the two-stage reads ~9% HIGH
  (approximate gamma + ignored flicker). Fix with the noise-scaling step
  (multiply caps, W, ID by S = (sim/spec noise power)) or by nudging CC; never
  by re-running the whole optimization.
- Static gain follows G*(1 + eps_s); check eps_s is acceptable BEFORE sizing,
  a basic OTA at short L can land at eps_s ~ -15%, which is usually unusable
  and forces longer L or a cascode/two-stage topology.
Always simulate small-signal (AC loop gain, noise) before transient; debug
order matters.

Concrete sized reference designs (gm/ID, ID, W per device + the SPICE deltas) for
the basic / folded-cascode / two-stage OTAs are in `worked-examples.md` (Ex 6.2,
6.3, 6.6, 6.8). Anchor against them; your numbers should land in the same ballpark.

## 8. Switch sizing (transmission gates)

The same tables size SC switches. A transmission gate is NMOS || PMOS; its
on-resistance ron = ron_n || ron_p with each ron = 1/gds evaluated in the triode
region at VDS = 0:

```python
ron_n = 1 / nch.look_up('GDS', VGS=VDD - vin, VSB=vin, VDS=0.0)
ron_p = 1 / pch.look_up('GDS', VGS=vin,       VSB=VDD - vin, VDS=0.0)
```

- ron_n is lowest at vin = 0, ron_p lowest at vin = VDD; total ron peaks near
  mid-supply. Size the PMOS larger (k > 1, ~mobility ratio) to flatten ron(vin).
- vin sets each device's VSB, so you can only step vin on the table's VSB grid;
  spline-interpolate for a smooth ron-vs-vin curve.
- Switches use L = Lmin (speed, no gain/matching constraint). Size from the
  worst-case ron (mid-supply) given the settling-time RC budget.

## 9. Fully-differential / CMFB specifics (continuous-time variant)

The book's flows above are single-ended-equivalent SC OTAs. A fully-differential
continuous-time OTA (e.g. the iic-jku two-stage diff OTA) adds common-mode control
that the gm/ID flow must account for. Bias these CURRENT-FIRST (fix the branch
current, gm = (gm/ID)*ID/... per the topology) since the CM loop sets operating
points:
- CMFB-resistor load: the load resistor R that senses/sets output CM also loads the
  signal path. Stage gain A = gm_in / (1/R + sum of gds at that node), i.e.
  R_load = 1/(1/R + gds_load + gds_tail-or-mirror); do not forget the 1/R term.
- Output CM offset current: i_offset = (V_cm,target - VGS_output) / R sets the
  mirror ratio that pulls the output CM to its target.
- CM gain / CMRR estimate (size to a CMRR spec): for the diff pair on a tail source,
  A_cm ~ -gm_in * gds_tail / (gm_load * (gm_in + gds_tail)); second stage
  A_cm2 ~ -gm_out/gm_cs. CMRR ~ A_dm / A_cm; raise it by a higher-rout tail
  (cascode the tail, section 9 of sizing-recipes.md) which shrinks gds_tail.
- Dominant-pole/GBW check with the Miller/stabilization cap:
  f_dompole = 1/(2*pi*R_load*(C_par + C_stab)); GBW = |A1*A2|*f_dompole. Compare to
  the target; trade C_stab and the gm split to hit it.
