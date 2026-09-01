---
name: gmid-sizing
description: >
  Size and verify analog CMOS circuits with the gm/ID lookup-table methodology
  (Jespers & Murmann, "Systematic Design of Analog CMOS Circuits"). Use this
  skill whenever the task involves transistor sizing, choosing W/L or bias
  current, gm/ID, transconductance efficiency, inversion level, current density
  (ID/W, JD), intrinsic gain (gm/gds), transit frequency (fT, gm/Cgg), sizing an
  OTA / amplifier / current mirror / differential pair, or verifying a sized
  design against ngspice operating-point results. Trigger even if the user only
  says "size this circuit", "pick the bias current", "what gm/ID should I use",
  or "check my operating point" without mentioning gm/ID explicitly. Requires
  pre-computed device lookup tables (see the gmid-lut-generation skill if none
  exist for the target PDK).
---

<!-- Managed by the private release infra (scripts/release/repo/.claude/) —
     edit there, not here; the next release port overwrites this file. -->

# gm/ID Sizing and Verification

Systematic transistor sizing using pre-computed lookup tables (LUTs) instead of
square-law hand formulas or SPICE tweaking. The LUTs hold SPICE-accurate
small-signal parameters over a 4-D grid of (L, VGS, VDS, VSB), so calculations
agree with simulation to within a few percent without iteration.

## Prerequisites

1. Device LUTs from the analog-db pipeline, in the **out-of-repo store**
   `~/.spicexplorer/gmid/<pdk>/<device>__<corner>[__<T>C].pkl` (the LUTs are NOT
   committed — regenerable artifacts). Resolve one with
   `spicexplorer_analog_db.gmid.find_lut_path(pdk, device, corner)` /
   `gmid.lut(pdk, device, corner)` — the reader searches the out-of-repo store
   first, then the legacy in-repo `_shared/gmid/` fallback. If the store is
   empty, build it: `python tools/regen_gmid_luts.py` (open PDKs run native
   ngspice; a Spectre-routed kit, if one is bound, runs the Spectre lane).
   Coverage at max fidelity (25 mV, 5 corners
   tt/ss/ff/sf/fs, 27 °C): sky130 {nfet_01v8, pfet_01v8}, ihp-sg13g2 {sg13_lv,
   sg13_hv}×{n,p}, gf180mcu {nfet_03v3, pfet_03v3}. See the
   `gmid-lut-generation` skill and the DB's `_shared/GMID.md`.
2. The lookup layer. **Prefer the platform's `spicexplorer-gmid` tool**
   (`packages/spicexplorer-gmid`): `DeviceTable.load(pkl).at(gm_id, L, vds, vsb)`
   → typed `OperatingPoint`; `size_for_gm` / `size_for_current_density` →
   `SizedDevice` (W/ID/gm + sanity-gate ledger); `size_resistor`/`size_capacitor`
   for passives. It wraps `pygmid.Lookup` (the raw reader, same `lookup`/`lookupVGS`
   semantics as the book's MATLAB kit) but is **fail-loud** — off-grid/unreachable
   gm/ID raises `OutOfGridError` where raw pygmid returns finite GARBAGE with only a
   printed warning. Worked examples: the analog-db `notebooks/` gm/ID notebooks.
   A self-contained legacy numpy/scipy port of the book's `lookup.m`/`lookupVGS.m`
   for the older `.npz` table format is preserved at `scripts/lookup.py`
   (superseded by the above; offline reference only).
3. For verification only: ngspice + PDK available (in this repo that means
   inside the EDA base image / `api` container — `make up-live` — never a bare
   host without a PDK). Passive sizing constants (sheet resistance, MIM cap density)
   live in the analog-db registry `_shared/pdk/<pdk>.yaml` → `passives.models`.

## Units convention (critical, errors here silently corrupt results)

- W and L: microns. Everything else: unscaled SI (A, V, S, F, Ohm).
- `ID_W` (= JD) is therefore A/um. `STH`, `SFL` are drain-current noise PSDs.
- Tables are characterized at one fixed **finger width** (header field `W` = 5 µm,
  `NFING`). gm/ID, JD, fT, gm/gds are invariant under scaling by *identical fingers*
  (add `m` fingers → same gm/ID/JD, ID scales), so **any W/L is reached from the one
  5 µm LUT** via `W = ID/JD` + fingering — no W sweep. They are NOT invariant under
  changing the *finger width*, so keep the layout finger width ≈ 5 µm. For devices
  forced narrower (matching/minimum), the **opt-in** finger-width companions
  (`gmid.finger_width_set(pdk, device, corner).at(…, wf=…)`, leaf `FingerWidthSet`)
  interpolate across characterized finger widths {0.5, 1, 5} µm — default sizing uses
  5 µm only (see references/verification.md, layout dependence).

## Core sizing flow (the canonical 5 steps)

For circuits where the required gm is known from specs (most cases):

1. **gm from spec.** Example, unity-gain bandwidth: `gm = 2*pi*fu*CL`.
2. **Pick L.** Short L: speed, area. Long L: intrinsic gain, matching.
3. **Pick gm/ID.** High (20-30 S/A): low power, large swing, low fT.
   Low (5-10 S/A): speed, small area, more VDsat. Moderate inversion
   (~12-18 S/A) is the usual starting compromise.
4. **ID = gm / (gm/ID).**
5. **De-normalize to width:** `JD = lookup(dev, 'ID_W', GM_ID=gm_id, VDS=vds,
   VSB=vsb, L=L)` then `W = ID / JD`.

Everything else falls out of the same lookups at the chosen operating point:

```python
from pygmid import Lookup
nch = Lookup('…/analog-db/_shared/gmid/ihp-sg13g2/sg13_lv_nmos__tt.pkl')

gm_id, L, VDS, VSB = 15.0, 0.13, 0.75, 0.0
gm  = 2*np.pi*1e9*1e-12          # fu = 1 GHz, CL = 1 pF
ID  = gm / gm_id
W   = ID / nch.look_up('ID_W', GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L)
VGS = nch.look_upVGS(GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L)
Av0 = nch.look_up('GM_GDS', GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L)
fT  = nch.look_up('GM_CGG', GM_ID=gm_id, VDS=VDS, VSB=VSB, L=L) / (2*np.pi)
```

Sanity gates before accepting a size:
- Fan-out `fT / fu >= 10`, otherwise the quasi-static model is invalid at fu.
- Saturation margin: `VDS > VDsat ~ 2/(gm/ID)` with some margin.
- W within manufacturable bounds; if W is huge, lower gm/ID or revisit specs.

## When gm/ID is NOT the right knob

In weak inversion (gm/ID near its ~25-30 S/A plateau) many current densities
map to nearly the same gm/ID, so gm/ID no longer uniquely defines the design.
Switch to the current-density flow: choose `JD` first, look up the resulting
gm/ID, then proceed as usual. Use this when the circuit is known to operate in
weak inversion or when sweeping the whole inversion range during exploration.

## Self-loading & design-space sweeps (the two refinement moves)

- **Self-loading**: when `Cdd = W*CDD_W` is comparable to `CL`, size for `CL+Cdd`
  and iterate to convergence (< 5 rounds). Full recipe: sizing-recipes.md §4/§10.
- **Sweeps**: don't point-design when specs are intertwined (gain AND BW AND
  power) — `look_up`/`DeviceTable.sweep` vectorize over `gm_id`; loop `L`; build
  the ID/W/Av0/fT tradeoff arrays and pick the corner with margin.

Both are demonstrated end-to-end in the repo's `gmid_sizing_demo.ipynb`.

## Verification loop (always close the loop in SPICE)

After sizing, back-annotate W, L, ID into the netlist, run an ngspice `.op`,
and compare table predictions against simulated `gm`, `ID`, `gm/ID`, `VGS`,
`gds`. Expect agreement within a few percent; larger deviations mean wrong
table (corner/temp), wrong VDS/VSB assumption, device out of saturation, or
geometry outside the characterized grid. Full procedure, ngspice decks, and
tolerance table: read `references/verification.md`.

## Reference files (read on demand)

- `references/lookup-api.md`: full semantics of `lookup` / `lookup_vgs`
  (3 usage modes, defaults, non-monotonicity handling, failure modes).
  Read before doing anything beyond the basic flow above.
- `references/sizing-recipes.md`: device-level recipes (intrinsic gain stage,
  current-density flow, self-loading iteration, noise / distortion / mismatch
  entry points), the current-mirror/source topology ladder (basic → cascode →
  degenerated → regulated, with rout formulas), and practical idioms from the
  worked notebooks (gm-from-bandwidth margin, parasitic self-load via gm-normalized
  caps, load-match sizing, perf one-liners, W-rounding, body bias). Read when the
  circuit is more than one device.
- `references/ota-recipes.md`: full OTA design flows for switched-capacitor
  circuits (basic, folded-cascode, two-stage Miller): settling/noise spec
  translation, the K = 1/(beta^2 * gm/ID) optimization, slewing-aware
  self-consistent search, simplified deterministic flows, SC switch sizing
  (transmission-gate ron), and SPICE verification expectations. ALWAYS read this
  before sizing any OTA, amplifier, or SC gain stage.
- `references/worked-examples.md`: concrete sized reference designs from the
  book's Ch 5 & Ch 6 (per-device gm/ID, ID, W, caps + SPICE deltas). Read it to
  ANCHOR a new design — your numbers should land in the same ballpark.
- `references/biasing-and-pvt.md`: constant-gm bias generator, high-swing
  cascoded current mirror, process-corner methodology (corner swings of
  gm/ID, fT, gm/gds under constant-ID vs constant-gm bias; spec
  pre-distortion flow), plus condensed LDO, noise-cancelling LNA, and
  charge-amplifier optima. Read before designing any bias network, current
  mirror, or whenever PVT/corners are in scope.
- `references/book-map.md`: topic-to-chapter map of the source textbook;
  consult it when a distilled reference is insufficient.
- `references/verification.md`: SPICE back-annotation, .op parameter
  extraction, acceptance tolerances, layout-dependence cautions.

## Pitfalls checklist

- Defaults are silent: omitted `L` = min(L), `VDS` = max(VDS)/2, `VSB` = 0.
  Always pass the real operating point for final sizing.
- **Off-grid does NOT reliably return NaN.** An unreachable `GM_ID` (above the
  weak-inversion maximum) or an out-of-grid bias makes pygmid print a warning but
  return finite GARBAGE (negative caps, a VGS in the gigavolt range) — isfinite
  checks miss it. Guard by hand: verify the bias axes are within grid AND the
  solved VGS lands inside the characterized VGS range; reject otherwise. The
  `spicexplorer-gmid` `DeviceTable.at()` does exactly this (raises
  `OutOfGridError`) — use it instead of raw pygmid for sizing. Treat
  `OutOfGridError` as a hard stop: change the design point or fall back to
  analytical + SPICE, clearly labeled — never nudge the inputs until the error
  goes away, that is silent interpolation.
- Mode-3 cross-lookups against ratios other than GM_ID, GM_CGG, GM_CGS may hit
  multiple-intersection errors; restrict the VGS search range as the error
  message suggests.
- Tables are single corner/temperature (header fields `CORNER`, `TEMP`).
  PVT verification needs corner tables or direct SPICE corners.
- Never extrapolate: L, VGS, VDS, VSB requests must lie inside the table grid.
