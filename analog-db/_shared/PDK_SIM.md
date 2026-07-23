# Simulating the DB circuits (tri-PDK: ihp-sg13g2 + sky130 + gf180mcu)

The EDA base image (`spicexplorer-spice-base`, in spicexplorer-platform) vendors **three PDKs** so
ngspice can simulate any of them:

| PDK | Models | Vendored at | Corner lib (`corners.yaml`) | Geometry |
|---|---|---|---|---|
| `ihp-sg13g2` | PSP/OSDI compact models (compiled) | `/opt/pdk/ihp-sg13g2/libs.tech/ngspice/` | `cornerMOSlv.lib` + `cornerRES.lib` | meters (`u`) |
| `sky130` | BSIM4 (built into ngspice; no OSDI) | `/opt/pdk/sky130/libs.tech/ngspice/` | `sky130.lib.spice` | bare-µm (`.option scale=1u`) |
| `gf180mcu` | BSIM4 (built into ngspice; no OSDI) | `/opt/pdk/gf180mcu/libs.tech/ngspice/` | `sm141064.ngspice` + `design.ngspice` | meters (`u`) |

sky130 is unzipped from `docker/pdk/sky130_pdk.zip`; **gf180mcu from `docker/pdk/gf180_pdk.zip`**
(open_pdks `c6d73a35`, ngspice model subset only) by the base Dockerfile. The vendored zip was
fetched with `volare`, but **`ciel` is the maintained successor** (efabless → chipfoundry; iic-osic-tools
switched to it) — `ciel enable --pdk gf180mcu <open_pdks-hash>` produces the identical artifact, so
to refresh the zip use ciel: `ciel enable --pdk gf180mcu c6d73a35…` then re-zip `libs.tech/ngspice`.

## How the PDK "switch" works (env + data-driven)

`PDK_ROOT=/opt/pdk` is shared; each PDK lives at `$PDK_ROOT/<pdk>`. The base image's `.spiceinit`
puts **all three** PDK ngspice dirs on the ngspice `sourcepath`, so a netlist resolves its corner
lib by **bare name** — `cornerMOSlv.lib` (IHP), `sky130.lib.spice` (sky130), or `sm141064.ngspice`
(gf180). A circuit selects its PDK purely through `pdk/<pdk>/corners.yaml` (`lib_file` + `section`);
no per-run env change is needed, and all PDKs are always reachable. `PDK`/`PDK_ROOT` remain the env
hooks if a tool needs a single "active" PDK.

## Parameterization — how a circuit's knobs are named and shared

Every committed deck's sizing knobs come from one contract — the per-circuit
`abstract/params.yaml` (`spicexplorer/params@1`; full spec in [`PARAMS.md`](PARAMS.md)). It splits
*what CAN vary* (an exhaustive, mechanically-derived **atomic inventory**) from *what SHOULD vary
together* (shipped **default ties**), and both flow through lowering into the `.param` header of the
decks you pull from `raw/`. You never have to open `params.yaml` to run a deck, but reading its
banner tells you exactly how many independent knobs a circuit exposes and which devices track which.

**Atomic naming (`devices:`).** Every instance owns one mechanically-derived symbol per sizeable
field — `x_dut_<instance>_<field>`, lower-cased, collision-free, with **no design opinion**. For a
MOS device that's its geometry `{w, l, m}`; passives echo their value field. The inventory is
GENERATED from the topology (`analog-db gen-params --circuit <id> --write`) — it is a physical fact
of the netlist, not a curated list.

**Worked example — `amp_001_5t` (5T OTA).** Its `circuits/amp_001_5t/abstract/params.yaml` inventories
six transistors, one row each:

```yaml
devices:
  XM1: {l: x_dut_xm1_l, m: x_dut_xm1_m, w: x_dut_xm1_w}   # input pair (+)
  XM2: {l: x_dut_xm2_l, m: x_dut_xm2_m, w: x_dut_xm2_w}   # input pair (−)
  XM3: {l: x_dut_xm3_l, m: x_dut_xm3_m, w: x_dut_xm3_w}   # PMOS load (diode half)
  XM4: {l: x_dut_xm4_l, m: x_dut_xm4_m, w: x_dut_xm4_w}   # PMOS load (mirror half)
  XM5: {l: x_dut_xm5_l, m: x_dut_xm5_m, w: x_dut_xm5_w}   # tail device
  XM6: {l: x_dut_xm6_l, m: x_dut_xm6_m, w: x_dut_xm6_w}   # mirror reference
groups:
  - {name: input_pair, kind: matched_pair, members: [XM1, XM2], tie: [w, l, m]}
  - {name: load_pair,  kind: matched_pair, members: [XM3, XM4], tie: [w, l, m]}
```

Two `groups:` ship as **default ties**: the NMOS input pair `XM1/XM2` and the PMOS mirror-load
halves `XM3/XM4`, each a full-geometry `matched_pair`. The tail-mirror pair `XM5/XM6` is a real
current mirror but ships **UNtied** — a *detected-but-untied* symmetry (surfaced as a `params:untied_symmetry`
warning at verify, and carried in the catalog's `untied_symmetries` as `mirror XM6→XM5 (tie l)`),
left independent so the tail and its reference size separately.

**Lowering (the `.param` block).** Ties become `.param` lines in the committed deck that reference the
**first** group member's symbol — each tied symbol is defined exactly once. In
`raw/amp_001_5t/ihp-sg13g2/_dut.spice` the free defaults come first, then the generated tie block:

```spice
** params: 8 free + 4 frozen knobs (sizing.yaml) · 6 tied · 0 ratio-derived (abstract/params.yaml)
.param x_dut_xm1_w=0.5u
.param x_dut_xm1_l=5.0u
.param x_dut_xm3_w=1.5u
.param x_dut_xm3_l=5.0u
.param x_dut_xm5_w=2.0u
.param x_dut_xm5_l=5.0u
.param x_dut_xm6_w=2.0u
.param x_dut_xm6_l=5.0u
.param x_dut_xm1_m=1        # …plus xm3/xm5/xm6 m — frozen finger counts
* ---- GENERATED parameter ties (abstract/params.yaml groups/ratios) ----
.param x_dut_xm2_w = {x_dut_xm1_w}     # XM2 tracks XM1 (input pair)
.param x_dut_xm2_l = {x_dut_xm1_l}
.param x_dut_xm2_m = {x_dut_xm1_m}
.param x_dut_xm4_w = {x_dut_xm3_w}     # XM4 tracks XM3 (load pair)
.param x_dut_xm4_l = {x_dut_xm3_l}
.param x_dut_xm4_m = {x_dut_xm3_m}
```

`XM2`'s and `XM4`'s symbols are never given literal defaults — they resolve through the tie. Because
each tied symbol is defined exactly **once**, *untying = shadowing*: redefine the symbol upstream
(e.g. `x_dut_xm4_w`) and you break just that one tie, leaving every other sharing decision intact.

**`sizing.yaml` keys on the FREE symbols.** `pdk/<pdk>/sizing.yaml` carries one `variables:` row per
**free** symbol only — the first members plus untied atomics. For `amp_001_5t` that is exactly
`x_dut_xm1_{w,l}`, `x_dut_xm3_{w,l}`, `x_dut_xm5_{w,l}`, `x_dut_xm6_{w,l}` (the 8 geometry knobs) plus
the 4 `m` rows carried as `freeze: true` frozen literals. The tied members `XM2`/`XM4` get **no**
sizing row — their `.param` comes from the tie block above. (The row descriptions still note the
tracking, e.g. *"Input pair width (XM1; XM2 tied)"*.)

**Reading the `** params:` banner.** Every committed deck opens with a provenance banner counting the
knobs; on the DUT (`_dut.spice`) it reads:

```
** params: 8 free + 4 frozen knobs (sizing.yaml) · 6 tied · 0 ratio-derived (abstract/params.yaml)
```

and on a full testbench deck it gains one trailing term, e.g. `… · 4 testbench params`. Decode it as:
**free** = independent optimizer knobs (`sizing.yaml` rows, `freeze:false`); **frozen** = literals
pinned by `sizing.yaml` (`freeze:true` — here the four `m` finger counts); **tied** = symbols defined
by the generated tie block (the 6 = `XM2`/`XM4` × `{w,l,m}`); **ratio-derived** = symbols set by a
`ratios:` entry (`m(A) = m(B) × k`; none here); **testbench params** = knobs the testbench itself
injects. The same counts ride the catalog's per-circuit `params` block and are re-emitted as a
`params:inventory:<pdk>` info row by `analog-db verify --tier 1`.

**Untying upstream.** The DB ships the ties; an upstream optimizer *dissolves* them without touching
the deck via the `ungroup:` selector (`"<group>"` | `"kind:<kind>"` | `"ratio:<ref>"`) in a project's
`params_file:` projection — it appends frozen shadow `.param`s that redefine the non-first members,
so *untying = shadowing* end-to-end. Semantics live in the platform optimizer
(`packages/spicexplorer/README.md` → `backends/params.py`, guide `notebooks/optimizer_quickstart.ipynb`)
and there is a runnable demo over the committed `raw_optimize/` decks (`raw_optimize/README.md`) —
not duplicated here.

## sky130 native-ngspice performance — the SLIM corner lib (~50-90× faster)

sky130 sims are dominated by **library-parse time, not the solve.** `.lib sky130.lib.spice
<corner>` loads the *entire* binned PDK model set (~480k expanded lines: every MOS flavour +
diodes + BJTs + caps + res + RF), and ngspice rebuilds that model DB on **every fresh process**
— measured **~59 s, 99 % CPU-bound**, while the actual `.op`/AC/noise solve is <0.1 s. In an
optimizer sweep (a fresh `ngspice` per candidate × testbench) this ~59 s tax dominates wall-clock.
(IHP/gf180 don't hit this: IHP is compiled-OSDI PSP + a ~565-line corner lib → ~0.1 s; sky130's
cost is the sheer size of the BSIM4 binned set, not BSIM4 itself.)

**Fix — a slim corner lib.** `tools/make_sky130_slim_lib.py` writes a `sky130_slim.lib.spice`
next to the stock `corners/<corner>.spice` that includes **only the device families a deck uses**
(the corpus uses `nfet_01v8`, `pfet_01v8`, `nfet_g5v0d10v5`, `pfet_g5v0d10v5` — no PDK R/C) plus
the shared preamble those models need (`.option scale=1.0u`, `parameters/lod.spice`, the
`dlc_rotweak` params). It copies the per-device `.include` lines **verbatim** from the stock
corner files, so it is **numerically identical** to the full lib (verified: `dc_op`/`ac`/`noise`
match to every printed digit on `amp_001_5t` core-MOS and `amp_019` IO-MOS, and on the `ss`/`ff`
corner path) — just ~50-90× faster (dc_op 59 s → ~1 s; corpus smoke 182/182 runnable @ ~1.25 s).

```bash
# generate once per PDK install (writes into the sky130 corners/ dir; its verbatim includes resolve there):
python3 examples/analog-db/tools/make_sky130_slim_lib.py --ngspice-dir $PDK_ROOT/sky130A/libs.tech/ngspice
#   --pdk-root DIR   (derive the ngspice dir)      --families a,b,c  (override the device set)
#   --check          (verify sources exist only)   --out NAME        (default sky130_slim.lib.spice)
```

**How the runner uses it.** `NGSpice_Wrapper` swaps the deck's `.lib sky130.lib.spice <c>` for the
slim lib at run time (no deck edits, no re-export), referencing it by **absolute path** — the
`corners/` dir is off ngspice's sourcepath, so a bare basename wouldn't resolve. The swap is
**fail-safe**: it fires only when
the slim lib exists on `$PDK_ROOT`, covers every `sky130_fd_pr__*` device the deck instances (scanned
from the deck's `.subckt` text), and defines the selected corner section — otherwise it keeps the
full lib. It also strips any prior slim `.lib` line so multi-corner PVT (one editor re-used across
corners) doesn't accumulate sections. Controlled by **`$SPICEXPLORER_SKY130_SLIM_LIB`**: `auto`
(default) | `off`/`0` (never swap) | `<name-or-path>` (force a specific lib). Run the generator →
every native-sky130 run auto-speeds-up; skip it → unchanged behaviour.

## Noise analysis & the ngspice solver (KLU cannot do `.noise`)

ngspice's **KLU** direct solver **does not support `.noise`** — it errors (*"Noise simulation is
not (yet) supported with 'option KLU'. Use 'option sparse' instead."*) and returns an **empty**
`inoise_total`/`onoise_total`. Stock ngspice-45 defaults to **SPARSE 1.3** (so noise works out of
the box here), but any environment where KLU is the default (a build/config choice, or KLU enabled
for speed on large circuits) silently yields no noise result. As a guard, `NGSpice_Wrapper`
appends **`.option sparse`** to any deck that runs a noise analysis (harmless where sparse is
already the default; disable with `$SPICEXPLORER_NGSPICE_NOISE_SPARSE=0`). Do **not** globally force
sparse — KLU is fine (and faster on big matrices) for op/dc/ac/tran; only `.noise` needs sparse.

## PDK passives (R/C models)

All DB circuits today use **ideal** `R`/`C` elements (sizing params), but the registries and the
binding generator fully support PDK passive models: each `_shared/pdk/<pdk>.yaml` has a
**`passives`** block with (a) `libs` — the extra corner-lib lines an R/C model needs, which
`add-binding` appends to every generated corner bundle, and (b) `models` — measured tt constants
for sizing (sheet resistance in Ω/□, MIM-cap density in F/µm²; measured via ngspice on the base
image, provenance in the registry comments). How each PDK resolves them:

| PDK | extra corner-lib lines | registry models (tt, measured) |
|---|---|---|
| `sky130` | **none** — every MOS corner section already includes the typical R+C models | `res_high_po` 355 Ω/□ · `cap_mim_m3_1` 2.07 fF/µm² |
| `ihp-sg13g2` | `cornerRES.lib res_typ/wcs/bcs` + `cornerCAP.lib cap_typ/wcs/bcs` (ss→wcs, ff→bcs, sf/fs→typ) | `rhigh` 1515 · `rppd` 265 · `rsil` 7.8 Ω/□ · `cap_cmim` 1.52 fF/µm² |
| `gf180mcu` | `sm141064.ngspice res_*/mimcap_*` sections + the `cap_mim` subckt section (after the MOS bundle; sf/fs→typical) | `ppolyf_u` 381 · `nplus_u` 58 · `pplus_u` 207 Ω/□ · `cap_mim_2f0fF` 2.09 fF/µm² |

All three verified end-to-end: a MOS + PDK-resistor + PDK-cap deck simulates through each PDK's
*synthesized* tt bundle, with R/C measuring at the registry constants. Note the R subckts are
**3-terminal** (`sig sig bulk`) on every PDK; gf180 takes `r_width`/`r_length` (meters), sky130
bare-µm `w`/`l`, ihp `w`/`l` meters. Existing per-circuit `corners.yaml` files (AUTHORED) predate
this and omit the passive lines — add them (or regenerate the binding) when a circuit starts
instancing PDK passives.

## gf180mcu specifics (the third PDK — for cross-PDK benchmarking)

- **Device names** are short (no `gf180mcu_fd_pr__` prefix): `nfet_03v3` / `pfet_03v3` (3.3V core),
  `nfet_06v0`/`pfet_06v0` (IO). Geometry is explicit meters (NO `.option scale`, like IHP), but the
  BSIM4 device takes a **per-finger** width + `nf` (like sky130) → circuitgraph emits `nf=ng`,
  `w='(w)/(ng)'` on lowering (`GF180MCU.width_per_finger`).
- **Corners are split per device + composed in `corners.yaml`** (see `_shared/pdk/gf180mcu.yaml`
  `corners`): each corner = `.include design.ngspice` (global stat/`fnoicor` switches) →
  `.lib sm141064.ngspice noise_corner` (defines the `*_noia` params the model cards reference, so it
  must load FIRST) → the per-device model sections (`nfet_03v3_t` + `pfet_03v3_t`) →
  `.lib … fets_mm` (the device subckts). The assembler emits a sectionless bundle as `.include`.
- **Status:** the 3.3V transfer simulates for most amps (gains ~80–150 dB at default sizing:
  hoilee_affc, leung_*, peng_*, qu/ramos/sau/song/yan, tan_clia, amp_001_5t). A few don't bias at the
  unoptimized default (alfio_raffc, fan_smc → ~0/neg gain — recorded floors), and the in-repo
  cascodes (folded/telescopic) hit the same large-W/finger envelope limit as on sky130 (need
  re-sizing, Phase 6). Baselines: the gf180mcu scoreboard entries (`scoreboard/gf180mcu/`).
- **Rebuild note:** the gf180 vendoring is committed (Dockerfile + zip); the base image must be
  rebuilt (`docker compose --profile base build spice-base`) to bake it in. CI's `verify-slow.yml`
  does this with reliable network; a flaky local `docker.io/docker/dockerfile` frontend fetch can
  block a local rebuild (same class as the api-image flake) — the slow gf180 tier skips cleanly
  until the image carries gf180.

## Running sims

```bash
# from a spicexplorer-platform checkout (the EDA base image built):
analog-db run --circuit amp_003_fan_smc --pdk sky130 --docker-image --write   # via `docker run` base image
analog-db run --circuit amp_001_5t        --pdk ihp-sg13g2 --docker             # via a running api container
```

`--docker-image` pipes the assembled netlist into a fresh `docker run` of the base image — no
running service needed; it carries ngspice + all three PDKs (ihp-sg13g2 + sky130 + gf180mcu).
`--docker` uses a running compose service.

## Cross-PDK transfer — every circuit ready-to-run in both PDKs

`analog-db add-binding --circuit <id> --pdk <target> [--from <source>]` synthesizes the *other*
PDK binding from an existing one so a clone is ready-to-run in both (no post-processing):
`pdk/<target>/{devices.map,corners,sizing}.yaml` + the PDK added to `circuit.yaml`'s `pdks`.
Then `analog-db generate --circuit <id>` emits the lowered `pdk/<target>/netlist.spice`.

**Sizing conversion (the one real subtlety).** sky130 sizing W/L are bare microns (`.option
scale=1u`); IHP geometry is meters with a `u` suffix. The generator canonicalizes every geometry
value to microns, clamps defaults/min-bounds up to the target PDK's W/L bin floor (from the
`_shared/pdk/<pdk>.yaml` `geometry` block), and re-emits in the target notation. The `M`
multiplier, capacitances (F), bias currents (A), bias voltages (V), and integer finger counts are
PDK-independent and carried verbatim.

**Fingers (`ng` → `nf`).** The abstract netlists are authored IHP-style: `w` is the **total** device
width and `ng` the finger count. sky130/gf180 are **BSIM4 with `nf`**, which fingers a *given total*
`w` internally (it bins on the per-finger width `w/nf` itself). So circuitgraph emits `nf=ng` and
keeps `w` **total** (`Pdk.width_per_finger=False`). **Corrected 2026-06-12:** the emitter previously
divided here too (`w='(w)/(ng)'`) — double-dividing every `ng>1` device into a sub-µm width in a
defective model bin (`Dsub<0`/`Vsat<0`). That was the root cause of the multi-finger sky130/gf180
*no-run cluster*. `ng=1` devices are unaffected (so every AnalogGym baseline is byte-identical); only
the two cascodes (the only `ng>1` committed sizings) change. Verified at the sky130 subckt source +
by sim (`w=5,nf=1` ok; `w=5,nf=114` → tiny defective bin; `w=4.89,nf=1` ok). IHP (PSP) keeps `ng`.

**Status by direction:**
- **AnalogGym → ihp-sg13g2 (15 amps):** all simulate (open-loop AC, gains ~27–122 dB at default
  sizing). Baselines in each circuit's `scoreboard/ihp-sg13g2/` entry. Unoptimized floors, not spec-passing —
  several have low/negative PM at default sizing (compensation tuned for sky130). `amp_017_tan_clia`
  stays `incomplete` (a device below the sky130 W bin); it gets no IHP binding.
- **in-repo OTAs → sky130:** `amp_001_5t` simulates on both PDKs (small devices, no fingers). The
  **cascodes (`amp_004_folded_cascode`, `amp_018_telescopic_cascode`)** lower correctly and the gm/ID
  re-sizing (Phase 6 / `examples/notebooks/gmid_cascode_resizing.ipynb`) + the finger-convention fix
  (above) clear the two binning walls — but a clean sky130 sim has **two more vendored-model
  constraints** mapped 2026-06-12 (each a per-instance bin limit, not a sizing error):
  1. **NMOS `Dsub<0`** for per-finger width **> ~5µm** → size with `wf_max ≈ 5µm` (more `nf`).
  2. **Per-instance total W ≤ ~100µm** (the model `wmax`) → wide PMOS devices (the low-JD
     mirror/cascode at 200–660µm) need the **`m` parallel multiplier** (`m=ceil(W/100)`,
     per-instance `W/m`) to fit a bin, else ngspice aborts with *"incomplete or empty netlist"*.
  The re-sized `sizing.yaml` + the `m`-split are the remaining step to a positive-gain baseline; the
  bindings are committed lowering-ready. `ldo_006_stub` (a stub) simulates on sky130.

## Cross-PDK simulation test matrix

Every (circuit × PDK × analysis) cell **assembles + re-parses** (Tier 2, PDK-free — one of the
many thousands of assembly / re-parse checks in `verify`; see the live scoreboard for the current
count, which scales with the corpus); the table below is the *ngspice* outcome of `ac_open_loop` at the `tt` corner
(open-loop AC, default sizing). Legend: **pass** = loads + biases, finite positive gain (dB shown,
an unoptimized FLOOR, not a spec pass); **degen** = loads + the analysis runs but the design does
not bias at default sizing (≈0/negative gain — a recorded floor); **no-run** = ngspice aborts
(device geometry outside the binned-model envelope / invalid BSIM params); **—** = not bound.

| circuit | ihp-sg13g2 | sky130 | gf180mcu |
|---|---|---|---|
| amp_001_5t | pass 30 | pass 26 | pass 54 |
| amp_005_hoilee_affc | pass 75 | pass 86 | pass 85 |
| amp_006_leung_dfcfc1 | pass 92 | pass 122 | pass 136 |
| amp_007_leung_dfcfc2 | pass 91 | pass 102 | pass 105 |
| amp_008_leung_nmcf | pass 93 | pass 95 | pass 93 |
| amp_009_leung_nmcnr | pass 96 | pass 115 | pass 115 |
| amp_010_peng_acbc | pass 80 | pass 91 | pass 90 |
| amp_011_peng_iac | pass 92 | pass 112 | pass 109 |
| amp_012_peng_tcfc | pass 91 | pass 107 | pass 110 |
| amp_013_qu2017_azc | pass 80 | pass 94 | pass 105 |
| amp_014_ramos_pfc | pass 102 | pass 135 | pass 141 |
| amp_015_sau_cfcc | pass 74 | pass 100 | pass 111 |
| amp_016_song_dacfc | pass 72 | pass 84 | pass 81 |
| amp_021_yan_az | pass 122 | pass 150 | pass 151 |
| amp_003_fan_smc | pass 86 | pass 59 | degen −2 |
| amp_002_alfio_raffc | pass 28 | degen −14 | degen −20 |
| amp_017_tan_clia | — | no-run | pass 132 |
| amp_004_folded_cascode | pass 44 | no-run | degen −31 |
| amp_018_telescopic_cascode | pass 53 | no-run | no-run |
| ldo_006_stub † | stub | stub | stub |
| ldo_007_pmos ‡ | n/a | n/a | n/a |

`ac_open_loop` totals: **ihp-sg13g2 18/18 pass · sky130 15/19 pass · gf180mcu 15/19 pass.**

† `ldo_006_stub` is an LDO (no `ac_open_loop`); its `dc_op` + `load_regulation` assemble + simulate. It
is `status: incomplete` by design (the D-10 class-abstraction stub).

‡ `ldo_007_pmos` is the first real LDO (no `ac_open_loop`). It **lowers + assembles + re-parses (Tier
0–2)** on all three PDKs. Committed scoreboard baselines exist for all three PDKs (a `dc_op` run
succeeded; some analyses such as `dropout` still have pending measure extraction). The sizing is a
structurally-correct starting point and the circuit is `status: incomplete` — spec tuning continues
in the T3/T4 phase.

**The two failure clusters are both known + documented (not bugs in the lowering):**
1. **`amp_004_folded_cascode` + `amp_018_telescopic_cascode` on sky130/gf180** — their IHP-tuned cascode
   geometries fall outside the binned-model envelope: sky130's vendored BSIM4 subset returns invalid
   params (`Dsub<0`/`Vsat<0`/`Weff≤0`) across the L≈2–4.5µm region they use, and telescopic's L spans
   0.25–9.7µm (40×). Neither finger-subdivision (more `nf`) nor uniform W/L-ratio scaling fixes it:
   scaling gets folded *past* binning (k≤0.3) but the cascodes then mis-bias (negative gain), and
   telescopic can't be scaled into the window at all. → needs gm/ID **re-sizing** (Phase 6).
2. **`alfio_raffc`, `fan_smc` off their native PDK** — load + run but don't bias at the default
   (sky130-tuned) sizing on the 3.3V/IHP rail → degenerate floors until the optimizer sizes them.

These are recorded as floors; the slow tier asserts the *passing* representatives + parse, and the
known-limitation cells are documented here rather than masked.

## AnalogGym specifics
- The 3-stage amps are **self-biased** (internal `I0`; no `ibias` port) and need the
  **bias-wrap** open-loop AC testbench (`ac_open_loop_biaswrap`: a 1 TH `Lfb` DC-shorts the
  feedback to bias, a 1 TF `Cin` AC-opens it) — the direct-drive template won't bias them.
- `design_variables` (`MOSFET_*`/`CAPACITOR_*`/`CURRENT_*_BIAS`) are injected as `.param`s at
  assembly from `pdk/sky130/sizing.yaml`.
- the sky130 scoreboard entries hold the **default-sizing baselines** (unoptimized; not spec-passing —
  recorded so the optimizer has a floor to beat). `dc_op`/`noise`/`tran_step` are scaffolded but
  `enabled: false` (bias-aware variants deferred).
