# Sizing recipes

Worked flows, ordered from primitive to composite. All assume tables loaded as
`nch` / `pch` via `from pygmid import Lookup; nch = Lookup(pkl)`; `look_up` /
`look_upVGS` are **instance methods** on that object (`nch.look_up(...)`). For
typed, fail-loud sizing use the platform wrapper `spicexplorer_gmid.DeviceTable`
instead, which exposes the same `.look_up` / `.at` / `.sweep` over the same `.pkl`.

## 1. Intrinsic gain stage (IGS), the template for everything

Single common-source device, current-source load, load cap CL. Spec: unity-gain
frequency fu. This is also the half-circuit of an actively loaded diff pair, so
master it first.

```python
gm  = 2*np.pi*fu*CL
ID  = gm / gm_id                          # gm_id chosen (step 3 of core flow)
JD  = nch.look_up('ID_W', GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L)
W   = ID / JD
VGS = nch.look_upVGS(GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L)
Av0 = nch.look_up('GM_GDS', GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L)
fT  = nch.look_up('GM_CGG', GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L)/(2*np.pi)
```

Checks: fan-out fT/fu >= 10; VDS > ~2/gm_id + margin; report Av0 vs gain spec.

## 2. Constraint-driven choice of L and gm/ID

When one of the two knobs is fixed by a constraint, sweep the other:

- gm/ID fixed by linearity or swing (e.g. VDsat budget 150 mV implies
  gm/ID = 2/VDsat ~ 13.3 S/A): sweep L over the table's L vector, collect
  Av0(L), fT(L), W(L), pick the shortest L meeting the gain spec.
  Note ID is invariant in this sweep (gm and gm/ID both fixed).
- L fixed by gain or matching: sweep gm/ID 5..28, collect ID, W, fT, swing,
  pick the highest gm/ID that still satisfies fT/fu >= 10 (minimum power) or
  the value that maximizes a composite figure of merit.

Vectorized lookups make each sweep one call; never loop a scalar lookup over a
grid when a vector call works.

## 3. Current-density (JD) flow for weak inversion

gm/ID saturates in weak inversion, so it stops resolving designs. Choose JD
directly, derive gm/ID from it, then de-normalize as usual:

```python
gm_id = nch.look_up('GM_ID', ID_W=JD, VDS=VDS, VSB=VSB, L=L)   # mode 3
ID    = gm / gm_id
W     = ID / JD
```

Use when: subthreshold/ultra-low-power blocks, or full inversion-range
exploration. JD and gm/ID map one-to-one for fixed (L, VDS, VSB), so the two
flows are interchangeable; gm/ID is just the more intuitive knob in moderate
and strong inversion.

## 4. Iterative sizing under self-loading

When the device's own Cdd is not negligible against CL:

```python
JD    = nch.look_up('ID_W',  GM_ID=gm_id, L=L)
CDD_W = nch.look_up('CDD_W', GM_ID=gm_id, L=L)
Cdd = 0.0
for _ in range(5):
    gm  = 2*np.pi*GBW*(CL + Cdd)
    ID  = gm/gm_id
    W   = ID/JD
    Cdd = W*CDD_W
```
JD and CDD_W are invariant across iterations (inversion level fixed), so hoist
them out of the loop. Convergence is geometric; 3-5 iterations suffice. The
same pattern generalizes: whenever a parasitic scales with W, wrap the basic
flow in this fixed-point loop.

## 5. Noise-driven sizing entry point

Tables store drain-current noise PSDs: STH (thermal) and SFL (flicker).
- Thermal: input-referred PSD ~ STH/gm^2. For a noise spec, derive the
  required gm first (it replaces the bandwidth-derived gm in step 1), then
  proceed with the core flow.
- Flicker: SFL scales ~1/(W*L); compare SFL/STH at the corner frequency of
  interest. If flicker dominates, area (W*L) becomes the knob; increase L and
  re-run the flow rather than only increasing W.

## 6. Distortion-driven entry point

Linearity caps gm/ID (HD3 of a diff pair improves at lower gm/ID for a given
input amplitude). Recipe: from the HD3 spec and input amplitude, determine the
admissible gm/ID, then size with that gm/ID via the core flow. Validate the
extreme points in SPICE; the prediction degrades at the lowest gm/ID values
where drain-swing effects appear.

## 7. Mismatch / matching entry point

Matching improves with area. When offset or current-mirror accuracy is the
binding constraint, fix L (long), fix gm/ID (low for mirrors, typically
5-10 S/A so VDsat is large and VT-mismatch-to-current gain is small), then
de-normalize. Verify the resulting VGS-VT overdrive against the swing budget.

## 8. Multi-device circuits (OTAs, mirrors, cascodes)

Decompose: each device gets a (gm/ID, L) pair from its role:
- input pair: gm from GBW/noise; moderate-to-weak inversion.
- mirrors/loads: strong inversion (low gm/ID) for matching and headroom usage.
- cascodes: gm/ID mostly free; size for headroom, use look_upVGS mode 2
  (VDB/VGB) for stacked devices whose source floats.
- tail source: like a mirror; check saturation under worst-case common mode.

Compute branch currents from the topology, then run the per-device flow. Keep a
single dict of {device: (type, gm_id, L, ID, VDS, VSB)} as the design state;
emit W per device; hand the whole dict to the verification step.

## 9. Current-mirror / current-source topology ladder

For a current source/mirror, one spec (output current ID, compliance budget vsat)
picks the topology by the output resistance you need. Size the diode leg with low
gm/ID (3-5, large VDsat for matching) and LONG L (gain), then read gds off the
table and assemble rout. Split the compliance voltage across stacked devices via
the VDS argument of each lookup. (Adapted from the iic-jku sizing notebooks; the
high-swing cascoded mirror with its VBIAS stack is in biasing-and-pvt.md.)

- basic: gm/ID 3-5, max L, evaluate gds at VDS = vsat. rout = 1/gds.
- cascode: add a device, evaluate each at VDS = vsat/2.
  gds_tot = gds*gds/(gds + gm + gds)  (~ gds^2/(2gds+gm)); rout ~ (gm/gds)x higher.
- resistive degeneration: R_deg = (vsat/2)/ID; gds_tot = gds*(1/R)/(gds + gm + 1/R).
- regulated (gain-boosted): bottom device at VDS = vsat*3/4, top at vsat/4, plus a
  small aux amp (gm/ID ~ 25, min L): rout = 1/gds + 1/gds_top
  + gm*(1 + gm_aux/gds_aux)/(gds_top*gds). Highest rout, most headroom-cheap.

Scale mirror COPIES by the current ratio: W_copy = W_diode * (ID_copy / ID_diode).

## 10. Practical sizing idioms (from the worked notebooks)

Patterns the repo `gmid_sizing_demo.ipynb` and the iic-jku notebooks use; they make
the per-device flow concrete and PVT-aware. Numbers in parentheses are sg13/sky130
design choices (anchors), NOT universal constants.

- gm from a closed-loop -3 dB bandwidth (unity-gain buffer): gm = f_bw*(2*2*pi)*CL
  with a margin factor (~3x for PVT + parasitics). The 4*pi = 2*(2*pi) folds the
  diff-pair's factor-of-2 into the load pole. Then ID = gm/(gm/ID), round to a
  current grid (e.g. 0.5 uA).
- Parasitic self-load from gm-NORMALIZED caps (cleaner than building C from W):
  C_par = |gm/GM_CGS| + |gm/GM_CDD| (+ next stage |gm/GM_CGG|); then recompute the
  bandwidth with gm/(2*pi*(CL + C_par)). This is the self-loading loop (section 4)
  expressed via look_up ratios.
- Load-/match-driven gm: when a resistive load or back-termination sets gm
  (gm = Av/(RL/2), or 1/gm = RS for an input match), size at the REAL operating VDS
  (= VDD - Vout_dc), not the table default. Input cap = gm * dev.look_up('CGG_GM', ...).
- Cascode bookkeeping in look_up args: encode stack height as VSB = n*headroom, and
  get cascoded output conductance by DIVIDING by the cascode's gain:
  gds_casc = gds / dev.look_up('GM_GDS', cascode_bias).
- Closed-form perf one-liners (report these alongside each size):
  gain error = a0/(1+a0) - 1; kTC output noise = sqrt(kT/C * (2*g_in + 2*g_load*
  gm_load/gm_in)) with g = gamma; slew = C*dV/I; 5-tau settle = 5/(2*pi*f_bw);
  thermal gamma = dev.look_up('STH_GM',...)*gm / (4*kB*T*gm); flicker corner =
  dev.look_up('SFL_GM',...) / dev.look_up('STH_GM',...).
- W rounding: small devices to a 0.5 um grid (round(W*2)/2, floored at W_min);
  large RF/driver devices to a 10 um grid (round(W/10)*10).
- Body bias matters: pass VSB explicitly (stacked cascodes, a bandgap core NMOS at
  VSB ~ 0.8 V) — it shifts VT/VGS and therefore W materially.
