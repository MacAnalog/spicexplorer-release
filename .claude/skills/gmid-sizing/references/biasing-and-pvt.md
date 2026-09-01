# Biasing circuits and PVT-aware design

Distilled from Ch 5 of the source text (see book-map.md). Emphasis: the two
DC-bias workhorses (constant-gm generator, high-swing cascoded mirror) and the
process-corner methodology. Condensed entries for LDO, LNA, charge amplifier.

## Reusable lookup micro-patterns (used throughout this file)

- Diode-connected device (VDS = VGS, unknown a priori): two-pass inversion.
  First `look_upVGS` at the default VDS, then re-run with VDS set to the
  first estimate. One iteration suffices; VGS is a weak function of VDS.
- Stacked device with known source node (e.g. cascode on top of a mirror):
  find its VGS by equalizing current densities. Sweep a small offset S above
  the lower device's VGS, compute JD_upper(VGS+S, VDS=node, VSB=node), and
  1-D interpolate JD_upper/JD_lower = 1.
- Early voltage at a bias point: VEA = dev.look_up('ID_GDS', ...), i.e.
  JD/(gds/W). Rout = VEA/ID.

## 1. Constant-gm bias generator

Two cross-coupled self-biased mirrors (PMOS pair M3-M4 1:1, NMOS pair M1-M2
with W1 > W2 and degeneration resistor R under M1's source). Equilibrium sets
gm2 = F(W1/W2, inversion)/R: in weak inversion gm2 = ln(W1/W2)/R, in strong
inversion gm2 = 2(1 - sqrt(W2/W1))/R; F varies smoothly in between. gm2
therefore depends ONLY on R and a width ratio, not on mu, Cox, or VT.

Sizing recipe (specs: ID, VDD, voltage drop VR = R*ID, all L):
1. Choose (gm/ID)2 (sweep it; the choice trades W spread vs sensitivity).
2. Diode pattern: get VGS2 at VDS = VGS2 (two-pass). Then per device:
   JD2 at (VGS2, VDS=VGS2); JD1 at (VGS2 - VR, VDS=VGS2 - VR);
   JD3 (PMOS) at (VDD - VGS2, VDS=VDD - VGS2). Widths = ID/JD.
   Note the devices land in very different inversion levels for one current
   (worked case: M2 13.3, M1 21.6, M3 6.9 S/A); that is normal.
3. R = VR/ID.

Hard topology rules:
- M2 in its own well so VSB2 = 0 (the analysis assumes equal VT for M1, M2).
- Devices to be gm-stabilized (e.g. an amp input pair M6) must replicate M2's
  physics: same L as M2, similar inversion; the mirror device feeding them
  (M5) also same L as M2.
- Load resistors made of the same material as R cancel absolute resistor
  variation in the gain: gm6*RD tracks (RD/R)*ln(W1/W2).
- A start-up circuit is mandatory (the zero-current state is also stable).

Expected behavior (calibrates verification): over -40..125 C, gm2 holds
within about +-1% while ID swings roughly -20/+30%; that current swing is the
price, budget headroom for it. VDD sensitivity (~+-10% on ID and gm via
DIBL/CLM in the non-diode devices M1/M4) is the main residual weakness; fix
by cascoding M1 and M4 if it matters.

## 2. High-swing cascoded current mirror

Topology: mirror core M1 (diode) - M3 (output), cascode M4 on M3, M2 on M1 to
equalize VDS1 = VDS3 (kills systematic ratio error), diode stack M6-M7
generating VBIAS, with M6 a replica of M2 for tracking.

The whole design hangs on ONE choice: gm/ID of the core, plus a margin VX.
- VDS1 = VDsat + VX = 2/(gm/ID) + VX. Use VX = 50 mV. VX = 0 puts M3's gds at
  the cliff edge (worked case: core VEA collapses to 0.56 V vs 1.73 V at
  50 mV); VX = 100 mV buys little and costs compliance voltage.
- Compliance voltage (min usable VOUT) ~ VDS1 + VDsat4; gm/ID directly sets
  it: higher gm/ID = lower compliance = more swing downstream.

Recipe (specs: Iin, gm/ID, L, VX = 50 mV):
1. VDS1 = 2/(gm/ID) + VX; VGS1 = dev.look_upVGS(GM_ID=gm_id, VDS=VDS1, L=L).
2. JD1 at (VGS1, VDS1); W1 = W2 = W3 = W4 = Iin/JD1.
3. VGS2 by the JD-equalization pattern with VDS2 = VGS1 - VDS1, VSB2 = VDS1.
   VBIAS = VDS1 + VGS2.
4. W7 (triode bias device): JD7 = dev.look_up('ID_W', VGS=VBIAS, VDS=VDS1, L=L);
   W7 = Iin/JD7. M6 = copy of M2.
5. Predict Rout: VEA = VEA_core * A4, with A4 = (gm4 + gmb4 + gds4)/gds4
   evaluated by lookups; Rout = VEA/Iin.

Expected behavior: with VX = 50 mV, output current flat to <0.2% for VOUT
from ~0.3 V to VDD, and Rout ~ MOhm-class at 100 uA (two orders above the
uncascoded core). If simulation shows current drooping early, the realized
VDsat is bigger than 2/(gm/ID) predicted; re-check the inversion level.

## 3. Process corners and PVT methodology

Corner pairing for worst case: FAST/COLD and SLOW/HOT (pairs the parameter
set with the temperature that amplifies it). Analog bias circuits make VT
shifts mostly irrelevant; what matters is how the BIAS STRATEGY maps process
variation onto gm/ID, fT, gm/gds.

Two biasing extremes and their measured (65 nm, L = 100 nm) corner swings:

| Quantity        | Constant-ID bias | Constant-gm bias |
|-----------------|------------------|------------------|
| gm              | +-30%            | ~0 (by design)   |
| gm/ID           | +-30%            | +-50%            |
| ID              | 0 (by design)    | -50%..+100% (4x!) |
| fT              | +-25%            | small            |
| VDsat           | 10-30 mV drift   | up to +200 mV in slow/hot (strong inv.) |

Consequences agents must act on:
- Constant-gm gives PT-stable bandwidth (gm/CL) but the 4x current spread
  and VDsat growth can push devices into triode; dangerous in low-voltage
  and strong-inversion designs. Constant-ID gives stable current and VDsat
  but ~+-30% bandwidth swing.
- Most real designs sit deliberately between the extremes (a partially
  compensating bias generator), spreading variation across dimensions.
- Moderate inversion is the PVT-robust region: VDsat and gm/gds corner
  spreads are smallest at low-to-moderate inversion. Yet another reason the
  optima from the OTA flows (which land there anyway) are good designs.

Two corner-aware sizing flows:
1. Worst-case tables: size against the slow/hot LUT directly; other corners
   then pass by construction. Requires maintaining per-corner tables
   (naming: <device>__<corner>.pkl, see gmid-lut-generation).
2. RECOMMENDED, spec pre-distortion: size with the NOMINAL table but inflate
   the specs by the known corner factor, then verify corners in SPICE.
   Margin estimation is mechanical: identify which corner-varying quantity
   the spec rides on, read its swing from the table above. Example: a
   constant-ID design whose bandwidth and noise both ride on gm (-30% in
   slow/hot) gets a nominal bandwidth target of spec/0.7 = 1.4x. The worked
   charge-amp case met both specs at all corners this way, with under 10%
   extra current (over-bandwidth pushes the design off the shallow current
   minimum, which is cheap).
- Noise pre-distortion needs slightly more margin than bandwidth: kT adds
  temperature dependence beyond the gm swing.
- NON-NEGOTIABLE: pre-distortion replaces multi-corner SIZING, never
  multi-corner SPICE verification. All corners get simulated before sign-off.

## 4. Condensed: LDO regulator

- Pass device: common-source PMOS. Common-drain NMOS needs ~VT of dropout,
  impractical below ~0.4 V in modern CMOS. CS width is set by a direct
  ID_W lookup at (VGS = VDD - Vgate,max, VDS = dropout) and is remarkably
  flat vs dropout; gm/ID of the pass device 5-15 S/A is the knob, BUT it has a
  floor: (gm/ID)1 must keep VDsat ~ 2/(gm/ID) < dropout, e.g. > 6.6 S/A for a
  0.3 V dropout (worked Ex 5.2 picks gm/ID1 = 10).
- Open-loop PSR = (YL + gds1)/gds1, only ~2-3x: a feedback error amp is
  mandatory. Closed loop: PSR = PSR_OL + (gm/gds)1*Aa ~ (gm/gds)1*Aa and
  Rout ~ 1/(gm1*Aa), so the error-amp gain Aa buys both supply rejection and
  load regulation. Error-amp tail current rule of thumb: ~2% of the load current.
  Worked Ex 5.2: 10 mA / 0.9 V LDO -> loop gain 120, PSR 259, Rout 0.4 ohm.
- The frequency-domain PSR has a load-cap-dependent shape; an optimum CL
  exists for a given amp design; sweep CL in the small-signal model before
  committing.

## 5. Condensed: noise-cancelling LNA (CG + CS active balun)

- Balance condition Av_CG = Av_CS makes M1's thermal noise and distortion
  common mode (cancelled); the design then minimizes M2's noise.
- Input match fixes the CG stage: 1/gms1 = Rs (gms = gm + gmb), so gm1 is
  NOT free. (gm/ID)2 is the primary knob for noise figure.
- Resistor drops VR set headroom: VDS1 = VDD - VR - VGS2 must clear VDsat1.
  The general HD2-nulling constraint (from Ch 4) wants VR >= ~0.5 V, but it is
  NOT a hard rule: the worked distortion-min LNA (Ex 5.5) AC-couples so VR1 != VR2
  and deliberately uses VR2 = 0.3 V for a large output swing / 1-dB compression
  target. Per-device sizing is the standard pattern: GDS_ID, look_upVGS, ID_W,
  CGG_W at each device's ACTUAL VDS. Match condition for the input: 1/gms1 = Rs
  (gms = gm + gmb) fixes the CG current. Cancellation only helps SMALL signals
  (< ~-15 dBm); large blockers still raise HD2 despite a high IIP2.

## 6. Condensed: charge amplifier optima (continuous time)

Three constraint regimes give three different optimum input-device sizes
(Cgg relative to CS + CF):
- Constant wT imposed: Cgg = CS + CF (pure noise minimum at fixed speed).
- Constant ID, square-law: Cgg = (CS + CF)/3. DO NOT TRUST at short L: the
  real 60 nm optimum sits near 0.14, and using 1/3 costs ~15% noise and a
  2.4x oversized device. Locate numerically with the LUT, always.
- Noise + bandwidth constrained (minimum current): Cgg = (CS + CFtot)/2,
  the result reused for stage 2 of the two-stage OTA (ota-recipes.md).
All these optima are shallow; the area-vs-current trade at the minimum is
nearly free, same exploitation rule as the OTA flows. Worked numbers (Ex 5.6-5.9)
and the corner-aware re-design (Ex 5.11, spec pre-distortion in action) are in
worked-examples.md; the constant-gm and high-swing-mirror reference designs
(Ex 5.1, the VX sweep) are there too.
