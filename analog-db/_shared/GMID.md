# gm/ID lookup tables (tri-PDK characterization — Phase 6)

The gm/ID design method sizes a transistor from a small set of **bias-independent** efficiency
curves (gm/ID vs ID/W, fT, intrinsic gain gm/gds, …) read off a pre-characterized device. This
subsystem **generates** those curves for any device in any of our three PDKs with an automated
ngspice sweep and stores them as a **pygmid-compatible** `.pkl` LUT, so `pygmid.Lookup` (and the
sizing notebooks built on it) read them directly.

```
analog-db gmid-extract --pdk sky130            # → _shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl
```

| | |
|---|---|
| **Module** | `spicexplorer_analog_db.gmid` |
| **CLI** | `analog-db gmid-extract` |
| **Config** | `_shared/pdk/<pdk>.yaml` → `gmid:` block (every knob overridable on the CLI) |
| **Output** | `~/.spicexplorer/gmid/<pdk>/<device>__<corner>[__<T>C].pkl` (**out-of-repo store**, not committed) |
| **Reader** | `pygmid.Lookup` (the `gmid` extra: `pip install -e '.[gmid]'`) |
| **Runtime** | dev-time tool only — the LUTs regenerate from the registries; nothing on a request path reads this module |

## Storage & regeneration (the LUTs are NOT committed)

The gm/ID LUTs are **regenerable artifacts, not source** — the max-fidelity open-PDK tables are
large (tens of MB each) and the FOUNDRY-n65 tables come from a licensed kit (NDA). So the whole store
lives **out-of-repo** and is rebuilt on demand:

- **Canonical store:** `gmid.out_root` in `_shared/pdk/<pdk>.yaml` (default `~/.spicexplorer/gmid`),
  laid out `…/<pdk>/<device>__<corner>[__<T>C].pkl` + `.manifest.json`. Every PDK — open and
  licensed — uses this one store.
- **Reader resolution:** `gmid.find_lut_path()` / `gmid.lut()` / `LUTRegistry` search the
  out-of-repo store **first**, then fall back to the legacy in-repo `_shared/gmid/<pdk>/` (so an
  older checkout still reads). `gmid.store_root(pdk)` is the write location.
- **Regenerate everything** (one command; open lane = native ngspice+`$PDK_ROOT`, FOUNDRY = Spectre):

  ```bash
  python tools/regen_gmid_luts.py                 # the whole store the environment can build
  python tools/regen_gmid_luts.py --pdk sky130    # one PDK, all devices × corners
  python tools/regen_gmid_luts.py --open-only     # skip the licensed Spectre lane
  ```

- **Grids (max fidelity, 2026-07-30):** VGS **25 mV**, VDS **25 mV** (was 200 mV — a 200 mV grid
  cost up to **40 % av0 error** at low VDS near the saturation knee), VSB **11 pts to VDD/2** (was
  2 pts, off-grid above 0.4 V), W = **5 µm**. All 5 corners `tt/ss/ff/sf/fs` per PDK.
- **Temperature:** recorded in the manifest (`conditions.temp_k`) and, off-nominal, in the filename
  (`__85C`); 27 °C tables carry no suffix. So multi-temp tables never collide.
- **Vt flavours (FOUNDRY-n65):** `gmid.flavors` + `--flavor lvt|svt|hvt|all` keys into
  `devices.{nmos,pmos}[flavor]` (`lvt`→`nch_lvt`, `svt`→`nch`, `hvt`→`nch_hvt`). **Note:** SVT/HVT
  require the operator's model wrapper to include those kit sections — the shipped wrapper maps only
  the `*_lvt` sections, so only LVT extracts until the wrapper is extended.
- **Finger width (OPT-IN, off by default):** gm/ID is invariant under scaling by *identical fingers*
  (add `m` fingers → same gm/ID, JD, fT; only ID scales — so **any W/L is reached from the one
  5 µm-finger LUT**, no W axis needed). It is NOT invariant under changing the *finger width*
  (narrow-width effects). For designs forced to sub-5 µm fingers (matching/minimum devices), the
  registry `gmid.finger_widths: [0.5, 1, 5]` + `regen_gmid_luts.py --fingers` generate narrow
  companions (`__wf0p5u`/`__wf1u` tagged) for the core devices; `gmid.finger_width_set(pdk, device,
  corner).at(gm_id, L, vds, vsb, wf=…)` (leaf tool `FingerWidthSet`) interpolates across them.
  **Default sizing uses the 5 µm table only** — interpolation happens solely when you call
  `finger_width_set`.

## Why we generate the decks (and not pygmid's sweeper)

[`pygmid`](https://github.com/dreoilin/pygmid) is the open-source port of Boris Murmann's gm/ID
starter kit: a `Lookup` reader + a `sweep` driver. **Its sweeper emits a Spectre `.scs` and is
Spectre-only** — useless for our open ngspice/OSDI flow. So `gmid.py` *generates the ngspice
characterization deck itself* (cloned from Murmann's
[`starter_files_open_source_tools`](https://github.com/bmurmann/Book-on-gm-ID-design), which target
exactly our three PDKs) and writes the LUT in pygmid's own `.pkl` schema. pygmid is then used purely
as the **reader** — its `Lookup` loads our `.pkl` unchanged.

## What is configurable (the registry `gmid:` block)

Everything the user asked for is a knob. Defaults live in `_shared/pdk/<pdk>.yaml`; any can be
overridden per-run on the CLI:

| Knob | Registry key | CLI | Notes |
|---|---|---|---|
| **Exact device / LV-HV variant** | `device` | `--device` | the model name from the library — picks LV vs HV and n vs p (below) |
| **Corner(s)** (tt/ss/ff/…) | `corners` | `--corner tt` / `tt,ss,ff` / `all` | one, a comma list, or `all` = the registry `gmid.corners` set; **each writes its own `<device>__<corner>.pkl`**. Resolves the same `.lib`/`.include` lines as a normal binding (`corners.yaml`). |
| **VGS range** | `sweep.vgs` | `--vgs a,s,b` | `(start, step, stop)` in V |
| **VDS range** | `sweep.vds` | `--vds a,s,b` | coarse by default (the method needs few VDS) |
| **VSB range** (body bias) | `sweep.vsb` | `--vsb a,s,b` | the deck sweeps the bulk **negative**; stored as `|VSB|` ≥ 0 |

**Sign convention (pmos):** a pmos deck sweeps every bias negative, but the LUT stores all axes
(`VGS`, `VDS`, `VSB`) and the currents as **positive magnitudes** — the Murmann/pygmid convention,
so one positive-gm/ID sizing flow serves both n- and p-channel. (You look up a pmos with positive
`VDS`/`gm/ID`, exactly like an nmos.)
| **Channel lengths** | `sweep.length_um` | `--length l1,l2,…` | µm; the L axis (no float drift — composed `values`) |
| **Width / fingers / temp** | `width_um`, `nfing`, `temp_k` | `--width`, (`nfing` registry), `--temp` | W in µm, T in K |

**Picking the variant** is just the device name. The default is each PDK's core-rail nmos; pass
`--device` for any other model the library defines. A device matching `pfet|pmos` is auto-detected
as p-type → the deck mirrors **all** biases to the opposite sign (VGS/VDS/VSB swept negative), and
the stored axes are the magnitudes.

**HV/LV is more than a name** — a non-core variant may keep its models in a *different corner lib or
section*. The `gmid.variants` block (a regex `match` on the device name → a `corners` override that
shallow-merges over the PDK default) handles this so `--device` "just works":

| PDK | default (LV/core nmos) | other variants (`--device`) | how the variant resolves |
|---|---|---|---|
| `sky130` | `sky130_fd_pr__nfet_01v8` ✅ | `…__pfet_01v8` ✅, `…__nfet_g5v0d10v5` (HV) ✅ | same `sky130.lib.spice <corner>` — no override needed |
| `ihp-sg13g2` | `sg13_lv_nmos` ✅ | `sg13_lv_pmos` ✅, `sg13_hv_nmos`/`sg13_hv_pmos` (HV) ✅ | HV → `variants` swaps the corner lib to **`cornerMOShv.lib`** |
| `gf180mcu` | `nfet_03v3` ✅ | `pfet_03v3` ✅; `nfet_06v0`/`pfet_06v0` (6 V IO) ⚠️ | IO → `variants` swaps to the `typical`+`*_06v0_t` sections |

✅ = extracts + verified physical. **⚠️ gf180 6 V IO known limitation:** the `variants` plumbing
selects the right sections, but this vendored open-source gf180 ngspice subset does **not**
characterize the 6 V device cleanly — its `_dss` mismatch wrapper (`agauss`/`var_vth`) plus a
`$`-comment in the `typical` master corner abort the bare op/noise sweep. A fuller gf180 model
vendoring unblocks it; use the 3.3 V core devices for gm/ID sizing. (Every other PDK×variant×corner
combination above — incl. HV at `ss` and HV pmos — extracts.)

## Two model families (the only per-PDK branch)

The deck differs in exactly two places, keyed by `family`: how the operating-point quantities are
named, and how the noise PSD is obtained. Everything else is generated identically.

| | **BSIM4** (`sky130`, `gf180mcu`) | **PSP/OSDI** (`ihp-sg13g2`) |
|---|---|---|
| `family` | `bsim4` | `psp` |
| Inner op-probe | `@m.xm1.m<model>[…]` (sky130) / `@m.xm1.m0[…]` (gf180) | `@n.xm1.n<model>[…]` |
| XM1 port order | `d g 0 b` | `0 g d b` |
| drain current | `id` | `ids` |
| body transcond. | `gmbs` | `gmb` |
| finger param | `nf` | `ng` |
| overlap / junction caps | `cgdo`,`cgso` / `capbd`,`capbs` | `cgdol`,`cgsol` / `cjd`,`cjs` |
| **noise** | 1-Hz `.noise` + a CCVS (`Hn`) mirrors Id; PSD = `onoise.id`²,`onoise.1overf`² | `.op` exposes `sid`/`sfl` directly |
| intrinsic cgd/cgs sign | negative (so `CGD = −cgd + cgdo`) | positive |

The deck sweeps with ngspice `compose`/`foreach`/`alter` (one `run` per bias point, `wrdata`
appended), reads the columns back **positionally** (the BSIM4 `.noise` deck emits a duplicate
`frequency` column that name-keying would collide on), reshapes to `(L, VGS, VDS, VSB)` order, and
applies the Murmann cap reductions (intrinsic + overlap/junction).

## LUT format (the pygmid contract)

A flat `dict` pickled to `.pkl`. Each electrical quantity is a 4-D array indexed
`[iL, iVGS, iVDS, iVSB]`; the four axis vectors give the grid:

```
INFO CORNER TEMP NFING W        # scalars / metadata
L VGS VDS VSB                   # 1-D axis grids (L in µm, VSB stored ≥ 0)
ID VT GM GMB GDS                # DC operating point
CGG CGB CGD CGS CDD CSS         # capacitances (intrinsic + overlap/junction reduced)
STH SFL                         # thermal + flicker noise PSD (V²/Hz referred)
```

This is exactly what `pygmid.Lookup` expects, so the sizing API works out of the box:

```python
from pygmid import Lookup
NCH = Lookup("_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl")
vgs   = NCH.look_upVGS(GM_ID=10, VDS=0.9, VSB=0, L=0.15)   # bias for a target efficiency
id_w  = NCH.look_up('ID_W',   GM_ID=10, VDS=0.9, VSB=0, L=0.15)   # current density → sizes W
ft    = NCH.look_up('GM_CGG', GM_ID=10, VDS=0.9,         L=0.15) / 6.2832   # transit freq
```

**One-step load (the common case):** `gmid.lut(pdk, device=None, corner="tt")` resolves the path
from the registry (device defaults to `gmid.device`) and returns a `Lookup` — no `GmidConfig`/path
surgery. It raises a **clear** `FileNotFoundError` (listing what *is* committed + the exact
`gmid-extract` command) when a (device × corner) isn't committed. The low-level
`gmid.load_lut(path)` (by path) is still there; both return the raw dict without pygmid.

```python
from spicexplorer_analog_db import gmid
nch = gmid.lut("sky130")                              # core nmos @ tt (registry default device)
pch = gmid.lut("sky130", "sky130_fd_pr__pfet_01v8")   # the pmos
```

## The generated LUT set (out-of-repo)

`tools/regen_gmid_luts.py` builds the full store: every PDK's n+p cores (plus ihp LV **and** HV) at
all 5 corners, on the max-fidelity 25 mV grid, into `~/.spicexplorer/gmid/<pdk>/`. Historic table
sizes above (0.35–1.5 MB) were the old coarse grids; the 25 mV / 11-VSB grids are tens of MB each —
which is exactly why they are no longer committed. Extend a single device/corner ad-hoc with
`gmid-extract`; rebuild the whole set with the regen script.

**Ground-truth validation.** `tests/test_gmid_ground_truth.py` cross-checks the committed IHP nmos
**and** pmos LUTs against the independently-characterized iic-jku `analog-circuit-design/gmid`
`sg13_lv_*.mat` tables (same PSP models): JD / intrinsic-gain / fT agree to **< 2 %** and VGS to
**< 1 mV** across ~96 bias points each — confirming the extraction pipeline and the pmos
positive-magnitude convention. (Skips when the iic-jku reference isn't checked out.)

Regenerate (needs the EDA base image — ngspice + all three PDKs):

```bash
docker compose --profile base build spice-base      # in spicexplorer-platform, once
analog-db gmid-extract --pdk sky130                  # → re-writes the committed .pkl
analog-db gmid-extract --pdk gf180mcu --device pfet_03v3   # add the pmos
analog-db gmid-extract --pdk ihp-sg13g2 --corner ss --vds 0,0.05,1.5   # fine VDS, slow corner
```

The slow test `test_L1_gmid_extract_is_physical_and_pygmid_loads` extracts a tiny grid on the base
image, asserts a physical weak-inversion gm/ID peak (~15–45 S/A) and that `pygmid.Lookup` loads it;
it skips cleanly when the base image isn't built (same guard as the other slow sim tiers).

## Manifest registration

Every committed LUT ships with a `<device>__<corner>.manifest.json` sidecar — the **typed registration
record** that makes the file self-describing.  It captures everything you need to know: run dimensions
(VGS/VDS/VSB/L grids, W/nfing/temp), the corner, the **exact `.lib`/`.include` lines** that pulled
the model card (so you can reproduce the run), stored parameter names, and extraction provenance.

**Typed access** (from `spicexplorer_gmid`):

```python
from spicexplorer_gmid import LUTManifest, LUTRegistry, DeviceTable

# 1. Registry — enumerate + load by pdk/device/corner
reg = LUTRegistry("_shared/gmid")
for m in reg.list_available("sky130"):
    print(m.device, m.corner)
    print("  L grid:", m.dimensions["L_um"].values)     # AxisSpec.values (non-uniform)
    print("  VGS step:", m.dimensions["VGS_V"].step)    # AxisSpec.step (uniform)
    print("  model lines:", m.model.corner_lines)       # exact .lib lines
    print("  temp:", m.conditions.temp_k, "K")

nch = reg.load("sky130", "sky130_fd_pr__nfet_01v8")     # DeviceTable with manifest attached
print(nch.manifest.pdk, nch.manifest.model_family)      # "sky130", "bsim4"

# 2. DeviceTable.load() auto-discovers the sidecar if present next to the .pkl
nch = DeviceTable.load("_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl")
assert nch.manifest is not None                         # auto-loaded from the sidecar
```

**JSON schema** (`spicexplorer/gmid-lut@1`):

| Field | Content |
|---|---|
| `pdk` / `device` / `corner` | identity keys |
| `model_family` | `"bsim4"` (sky130/gf180) or `"psp"` (ihp) |
| `polarity` | `"n"` or `"p"` |
| `model.corner_lines` | the **exact** `.lib`/`.include` lines used |
| `model.info` | human-readable description from the LUT header |
| `conditions` | `temp_k`, `width_um`, `nfing` — fixed across the sweep |
| `dimensions` | `L_um`, `VGS_V`, `VDS_V`, `VSB_V` — each an `AxisSpec` (n/min/max/step or values); `VSB_V.stored="magnitude"` |
| `params` | stored parameter names: `ID VT GM GMB GDS CGG CGB CGD CGS CDD CSS STH SFL` |
| `provenance` | `tool`, `ngspice` version, `extracted_at` ISO timestamp |

## Replicate / verify

**Regenerate** one LUT (needs the EDA base image — ngspice + all PDKs):

```bash
docker compose --profile base build spice-base              # once, if image is stale
analog-db gmid-extract --pdk sky130                         # nmos @ tt (registry defaults)
analog-db gmid-extract --pdk sky130 --device sky130_fd_pr__pfet_01v8   # pmos
analog-db gmid-extract --pdk ihp-sg13g2 --corner ss         # slow corner
analog-db gmid-extract --pdk gf180mcu --device nfet_03v3    # gf180 nmos
```

Each run writes `<device>__<corner>.pkl` + `<device>__<corner>.manifest.json` to `_shared/gmid/<pdk>/`.

**Back-annotate a sizing against SPICE** (the P4 slow test):

The `spicexplorer-gmid` package includes a PDK-gated back-annotation test that:

1. Loads the committed IHP nmos LUT from `packages/spicexplorer-gmid/tests/fixtures/`.
2. Calls `DeviceTable.at(gm_id=15, L=0.5, vds=0.9)` to resolve `VGS` from the table.
3. Biases a real `sg13_lv_nmos` instance at that `VGS` in an ngspice `.op` deck.
4. Compares the SPICE-returned `gm/ID` against the target (10% tolerance).

```bash
# Run inside the api container (ngspice + IHP PDK in PATH):
docker compose up --build
docker compose exec api pytest packages/spicexplorer-gmid/tests/test_gmid_backannot.py -v

# OR using the pre-built api image directly:
docker run --rm --entrypoint pytest spicexplorer-api:local \
  packages/spicexplorer-gmid/tests/test_gmid_backannot.py -v
```

Auto-skips on hosts without ngspice or the IHP PDK (`/opt/pdk/ihp-sg13g2/libs.tech/ngspice/models/`).
The CI `live-spice` job runs `pytest -m slow` inside the api container, so this test is gated there.

**Ground-truth cross-check** (IHP vs iic-jku reference tables):

```bash
# Requires the iic-jku analog-circuit-design repo.
# The platform submodule was removed in Dev #12; point at an external checkout:
IIC_JKU_GMID_DIR=/path/to/analog-circuit-design/gmid \
  pytest examples/analog-db/tests/test_gmid_ground_truth.py -v
# The test also auto-discovers the repo at <platform>/submodules/analog-circuit-design/gmid
# if that directory exists.
```

Checks JD / intrinsic-gain / fT to < 2% and VGS to < 1 mV across ~96 bias points.

## The Spectre lane — licensed-kit PDKs (`gmid-extract-spectre`)

A `sim_engine: spectre` PDK (FOUNDRY-n65) can't use the ngspice flow above — its models only exist
behind the licensed kit. The **Spectre lane** (`spicexplorer_analog_db.gmid_spectre`,
`analog-db gmid-extract-spectre`) characterizes it with **plain headless Spectre** — no
Virtuoso/OCEAN session — using the same registry-`gmid:`-block config style:

```bash
analog-db gmid-extract-spectre --pdk FOUNDRY-n65              # tt → ~/.spicexplorer/gmid/FOUNDRY-n65/
analog-db gmid-extract-spectre --pdk FOUNDRY-n65 --corner all --workers 16
analog-db gmid-extract-spectre --pdk FOUNDRY-n65 --smoke      # 2 L × 1 VSB validation pass
analog-db gmid-extract-spectre --pdk FOUNDRY-n65 --dry-run    # print the deck, run nothing
```

Differences from the open lane, and why:

- **Both polarities in ONE pass.** The deck instantiates the registry's `devices.nmos.core` +
  `devices.pmos.core` side by side with mirrored biases (`vbsn dc=-sb` / `vbsp dc=sb`), so one
  extraction writes both `<nmos>__<corner>.pkl` and `<pmos>__<corner>.pkl`.
- **Speed comes from the nested sweep, parallelism from YAML.** One Spectre process per
  (L, VSB) pair only; inside it a nested `sweepvds sweep { sweepvgs dc }` solves the whole
  VGS×VDS plane with warm-started DC solves (per-process overhead × nL·nVSB, **not** × every
  bias point — the difference between ~10 minutes and ~8 hours for a 1.7 M-point grid). The
  fan-out width is the registry's **`gmid.simulator`** block:

  ```yaml
  gmid:
    simulator:            # optional; CLI --workers/--timeout override
      workers: 12         # parallel Spectre jobs
      timeout_s: 1200     # per-job wall clock
  ```
- **NDA posture.** The deck's only include is the operator's *neutral* wrapper
  (`$SPICEXPLORER_<PDK>_MODEL_ROOT/<corners.lib_file>` + a **generic** section name — the same
  indirection the sim bindings use); the Spectre binary/env come from the virtuoso-bridge
  `local.env` (`VB_SPECTRE_BIN`/`VB_CADENCE_CSHRC`); Spectre logs stay in the scratch dir and
  are never echoed. LUTs land **out-of-repo** by default (`gmid.out_root`, mirroring the
  committed `_shared/gmid/<pdk>/` layout) — committing licensed-kit tables is an owner call.
- **Gate current is stored honestly.** bsim4 splits gate tunneling: `igd`/`igs` are the
  overlap/edge components only; the **channel** components `igcd`/`igcs` are ~100× larger at
  65 nm. The stored `IGD`/`IGS` are the folded totals, so a node-loading leak budget
  (`g_leak ≈ ∂(IGD+IGS)/∂VGS` by finite difference) reads true. A pygmid-convention LUT with
  bare `igd`/`igs` under-reads 65 nm gate leak two orders of magnitude.
- **No noise columns.** `STH`/`SFL` are omitted (not zeroed) until a pnoise-based lane exists —
  an absent key fails loud in `pygmid.Lookup`; silent zeros would lie.

**Accuracy, validated against live amplifier op dumps** (every MOS of two working designs,
looked up at its exact measured bias): 25 mV VGS/VDS grids give ≤0.3 % gm/ID and ≤5 % JD
interpolation error. The real accuracy axis is **finger width**, not the grid — the LUT is
per-unit-width at `width_um` (5 µm) fingers, and narrow fingers deviate (0.5 µm pch measured
2.2× off on gm/gds). Apply sizings with ~2–10 µm fingers and scale total W via `m`.

## Runners & parallelism (open lane)

The open-PDK lane has the same `simulator:` registry block, plus a **runner choice** — the
docker base image is no longer required when the host has ngspice + `$PDK_ROOT`:

```yaml
gmid:
  simulator:            # optional; CLI --runner/--workers/--timeout override
    runner: auto        # auto = host ngspice+$PDK_ROOT when available, else docker
    workers: 8          # parallel ngspice jobs, ONE PER L VALUE
    timeout_s: 3600
```

- **`native` runner** (`gmid.native_deck_runner`) reuses the Phase-7 native-sim machinery
  (`runner._NATIVE_PDK`): a per-PDK `.spiceinit` (sourcepath + IHP OSDI) in each job's scratch
  dir + the native deck fixes (slim-corner-lib swap, absolute includes). `docker` remains the
  containerized fallback; `auto` probes `runner.native_pdk_available()`.
- **Per-L fan-out** (`gmid.extract_parallel`): the characterization deck loops L outermost, so
  splitting on L is exact — each job runs the full VGS×VDS×VSB sweep for one length and the
  slices concatenate along axis 0. This is what amortizes sky130's ~60 s model-library parse
  (one per ngspice process): 8 lengths in parallel ≈ one parse-time, not eight.
- **Verified bit-identical**: a native re-extraction of all three PDKs reproduces the committed
  LUTs exactly (max relative error 0.0 across ID/GM/GDS/VT/CGG/STH, axes equal) — same
  ngspice-45 + models, deterministic solver; the per-L merge is exact.

## References

- **pygmid** — the LUT reader (and a Spectre sweeper we don't use): https://github.com/dreoilin/pygmid
- **Book on gm/ID design** (Murmann) — the method, the TB conventions, and the open-tool starter
  decks we cloned: https://github.com/bmurmann/Book-on-gm-ID-design
- **iic-jku/analog-circuit-design** — Jupyter notebooks applying the gm/ID strategy end-to-end:
  https://github.com/iic-jku/analog-circuit-design

## Where this plugs in next

The committed LUTs are the device characterization the **cascode re-sizing** (`PDK_SIM.md`, the
`amp_004_folded_cascode`/`amp_018_telescopic_cascode` sky130/gf180 no-run cluster) needs: pick gm/ID and L
per device, read ID/W + fT off the LUT, and emit a binned-model-legal sizing. The sizing API lives
in `packages/spicexplorer-gmid` in the platform repo (`DeviceTable`, `LUTRegistry`); the cascode
re-sizing notebooks consume it. For the **passive** side of
sizing — turning a target R into squares or a target C into MIM area — the measured sheet-res /
cap-density constants live in the registry `passives.models` block (see `PDK_SIM.md`).
