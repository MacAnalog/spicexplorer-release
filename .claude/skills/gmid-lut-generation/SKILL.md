---
name: gmid-lut-generation
description: >
  Generate the pre-computed MOSFET lookup tables (LUTs) that the gmid-sizing
  skill consumes, by sweeping device characterization testbenches in ngspice
  over (L, VGS, VDS, VSB). Use this skill whenever lookup tables are missing,
  stale, or needed for a new PDK / device flavor / corner / temperature, or
  when the user mentions "characterize the devices", "technology sweep",
  "generate gm/ID tables", "device characterization", or asks why a
  sizing-table file (.pkl) for a device does not exist. Requires live
  ngspice + PDK (the EDA base image / api container, or any host with both
  installed).
---

<!-- Managed by the private release infra (scripts/release/repo/.claude/) —
     edit there, not here; the next release port overwrites this file. -->

# gm/ID Lookup Table Generation

One-time (per PDK / corner / temperature / device flavor) characterization that
produces the 4-D tables consumed by `gmid-sizing`. The methodology is the
book's techsweep flow; **the implementation is the analog-db pipeline** —
do not write ad-hoc sweep scripts.

## The pipeline (the only LUT path)

```bash
analog-db gmid-extract --pdk <ihp-sg13g2|sky130|gf180mcu> \
    [--device DEV] [--corner tt] [--vgs a,s,b] [--vds a,s,b] [--vsb a,s,b] \
    [--length l1,l2,...] [--width W_um] [--temp K] [--docker-image IMG]
```

- Implementation: `spicexplorer_analog_db.gmid` (analog-db repo). Full docs:
  the DB's `_shared/GMID.md`.
- Output: **pygmid-compatible `.pkl`** (the Murmann LUT-dict convention) in the
  **out-of-repo store** `~/.spicexplorer/gmid/<pdk>/<device>__<corner>[__<T>C].pkl`
  (`gmid.out_root`; the LUTs are NOT committed — regenerable). Rebuild the whole
  store with `python tools/regen_gmid_luts.py`; extract one device/corner ad-hoc
  with the CLI. Corners `tt/ss/ff/sf/fs`, W = 5 µm, 27 °C by default.
- **The Spectre lane** (`analog-db gmid-extract-spectre`) is the same flow
  against a Spectre-routed kit; it adds `--flavor lvt|svt|hvt|all` keyed to
  `devices.{nmos,pmos}[flavor]`, both polarities per pass. No such kit is bound
  in this repo — the open PDKs above are.
- Defaults (grid, W, fingers, temp, default device) live in the PDK registry
  `_shared/pdk/<pdk>.yaml` → `gmid:` block; every knob is CLI-overridable.
- **Device flavors:** LV/HV/IO variants are just `--device <model>`; a variant
  whose models live in a different corner lib or section resolves through the
  registry `gmid.variants` override (regex on the device name). Verified:
  sky130 HV, ihp HV nmos+pmos (incl. non-tt corners). Known limitation: gf180
  6V IO devices do not characterize in the vendored open model subset (their
  statistical-mismatch wrapper aborts a bare sweep) — documented in GMID.md;
  use the 3.3 V core devices.
- **pmos** is auto-detected from the device name; biases are mirrored and the
  stored axes are magnitudes.
- The ngspice parameter-handle maps are **already verified and encoded** for
  both model families (BSIM4: sky130/gf180; PSP/OSDI: ihp) in `gmid.py`'s
  `_FAMILY` table — probe instance names, port order, id/ids, gmbs/gmb, nf/ng,
  capacitance names, and the noise method (1-Hz `.noise`+CCVS vs direct
  sid/sfl at `.op`).

## Output contract (what gmid-sizing and pygmid read)

One `.pkl` per device+corner, a flat dict:

- Axis vectors: `L` (um), `VGS`, `VDS`, `VSB` (V), monotonic increasing
  (`VSB` stored as magnitude).
- 4-D arrays indexed `[L, VGS, VDS, VSB]`: `ID VT GM GMB GDS CGG CGS CGD CGB
  CDD CSS STH SFL`.
- Header: `INFO` (free text: PDK, model), `CORNER`, `TEMP` (K), `W`
  (characterization width, um), `NFING` (fingers).
- Units: W/L in um; everything else unscaled SI. `STH`/`SFL` are drain-current
  noise PSDs (A^2/Hz); `SFL` at the 1 Hz convention so flicker rescales as SFL/f.

## Grid guidance (book defaults, encoded in the registries)

- VGS: 0 to VDD in 25 mV steps (max-fidelity default). VDS: **25 mV too** —
  first-order gm/ID sizing needs few VDS points, but gds/av0/ro and headroom
  checks need the saturation knee resolved; a 200 mV grid was measured to cost
  up to 40 % av0 error at low VDS, so the registries now default to 25 mV.
- VSB: **~11 body-bias points 0 to VDD/2** (a 2-point grid interpolates fine but
  goes off-grid — fail-loud — above 0.4 V, which any stacked/body-biased device
  hits).
- L: dense near Lmin, sparse beyond (each registry carries a sensible set).
- Fixed W ~5–10 um in a representative finger configuration; `W`/`NFING` are
  recorded. Sizing assumes ID scales with W at constant finger width.

## Extending to a NEW PDK (debug-first rule, mandatory)

Adding a PDK means adding a registry (`_shared/pdk/<pdk>.yaml` with a `gmid:`
block) and, if its model family differs from BSIM4/PSP, a `_FAMILY` entry.
Before trusting a full sweep, run a single-point deck for one (L, VGS, VDS,
VSB) and print every device parameter you intend to harvest — saveable
parameter handles differ across model families and OSDI builds (`@m.x...[gm]`
style names must be confirmed against `display` output). A configuration error
caught here saves a multi-hour silent failure, the same reason the book ships
a one-shot debug variant of its sweep script. Derived quantities (CDD = intrinsic
+ junction + overlap, sign conventions per family) stay an explicit table in
`gmid.py`, never inline arithmetic scattered through a parser.

## Acceptance checks (before publishing any new table)

- gm/ID vs VGS at Lmin is smooth, peaks ~25–30 S/A in weak inversion,
  decreases monotonically after its maximum.
- ID monotonic in VGS and in VDS (saturation flattening allowed).
- Round-trip: pick 3 random grid-off points, compare pygmid interpolation
  against a direct ngspice `.op` at that bias; require <2% on ID and gm.
- `pygmid.Lookup` loads the file and `look_upVGS` returns a sane mid-VGS at
  gm/ID = 10.
- Record provenance (PDK version, model section, ngspice version) in `INFO`.

## New corner / temperature

Re-run with only the flags changed: `--corner ss`, `--temp 358`. Files are
named `<device>__<corner>.pkl` by the pipeline. The sizing skill verifies the
header `CORNER`/`TEMP` against the simulation settings, so never recycle a
nominal table for a corner check. LUTs are regenerable artifacts and are not
committed: they live in the out-of-repo store, not in the database.
