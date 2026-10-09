# spicexplorer-gmid

Deterministic transistor sizing with the **gm/ID lookup-table methodology** (Jespers & Murmann,
*Systematic Design of Analog CMOS Circuits Using Pre-Computed Lookup Tables*). Pick an inversion
level (gm/ID) and a channel length per device; read current density, V<sub>GS</sub>, intrinsic gain,
f<sub>T</sub>, and capacitances off a pre-characterized LUT; de-normalize to a width. No square-law
hand formulas, no SPICE tweaking loop — agreement with simulation to a few percent.

It is a **leaf tool**: it depends on `spicexplorer-core` + `pygmid` + `numpy` + `pydantic` only. It
never imports a peer tool (the optimizer, `netlist2tf`) or the data repo `spicexplorer-analog-db`.
The LUTs come from `analog-db gmid-extract` (open PDKs, ngspice; committed at
`_shared/gmid/<pdk>/<device>__<corner>.pkl`) or `analog-db gmid-extract-spectre` (a **licensed**
kit, through the Spectre lane; written out-of-repo to `~/.spicexplorer/gmid/<pdk>/`), and this
package takes a *path, an object, or just a name* — `load_lut(pdk, device)` finds whichever store
this installation has (see [Where the tables are](#where-the-tables-are-load_lut-no-root-to-hand-in)).
Reading the DB and re-simulating stays an orchestration concern, not part of the tool.

Import name: `spicexplorer_gmid` (distribution `spicexplorer-gmid`).

## Quickstart

```python
from math import pi
from spicexplorer_gmid import (
    DeviceTable,
    size_for_gm,
    size_for_current_density,
    size_resistor,
    size_capacitor,
)

# 1. load a committed pygmid LUT (sky130 1.8 V core NMOS, TT corner)
nch = DeviceTable.load(".../_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl")
# ...or by name, from wherever this installation keeps its tables (incl. a licensed kit's):
#   from spicexplorer_gmid import load_lut;  nch = load_lut("sky130", "sky130_fd_pr__nfet_01v8")

# 2. read an operating point off the table (everything but the 4 coordinates is interpolated)
op = nch.at(gm_id=15, L=0.5, vds=0.9)
print(op.jd, op.vgs, op.av0, op.ft)  # A/µm, V, gm/gds, Hz

# 3a. gm-first flow: size to a transconductance target (e.g. gm for a target GBW·CL)
dev = size_for_gm(nch, gm=2 * pi * 1e9 * 1e-12, gm_id=15, L=0.5, vds=0.9)
print(dev.W, dev.ID, dev.passed)  # width [µm], bias current [A], all sanity gates hold?

# 3b. current-first / JD flow: fix the bias current + inversion level
dev = size_for_current_density(nch, ID=50e-6, gm_id=12, L=1.0, vds=0.9)

# 4. explore the trade-off curves (the range must stay inside the reachable gm/ID band —
#    see "Reachability" below; sweeping past the weak-inversion peak raises OutOfGridError)
sw = nch.sweep(gm_id=(5, 25), L=0.5, vds=0.9)  # arrays: jd, ft, av0, vgs over gm/ID

# 5. passives from PDK constants
r = size_resistor(10e3, sheet_res=355, w_um=1.0)  # → 28.2 squares, l_um ≈ 28.2
# area_cap is F/µm², so a MIM plate is ~2e-15, NOT 2e-3 — the quickstart used to say 2e-3,
# which sizes a 1 pF cap as 5e-10 µm². Both constants come from the PDK, in these units.
c = size_capacitor(1e-12, area_cap=2.07e-15)  # → area_um2 ≈ 483
```

## Public API — by module

Everything is re-exported at the top level (`from spicexplorer_gmid import …`); the table groups by
source module.

| Module | Surface | What it's for |
|---|---|---|
| `tables` | `DeviceTable` (`.load`, `.at`, `.look_up`, `.gm_id_for_jd`, `.gm_id_band`, `.sweep`, `.w_char`, `.manifest`; grids `L_grid`/`VGS_grid`/`VDS_grid`/`VSB_grid`), `Sweep` | Typed, fail-loud wrapper over a pygmid `Lookup`. `at()` → `OperatingPoint`; `sweep()` → trade-off arrays; `gm_id_band()` → the reachable gm/ID interval of a bias slice; `look_up()` → the low-level raw scalar lookup (bias axes and a `GM_ID=` key gated like `at()`; an `ID_W=` key is not range-gated — use `gm_id_for_jd()`). |
| `fingerwidth` | `FingerWidthSet` (`.load`, `.at`, `.gm_id_for_jd`, `.table_at`, `.finger_widths`) | One `DeviceTable` per characterised **finger width**, linearly interpolated across it. |
| `sizing` | `size_for_gm`, `size_for_current_density` | The two de-normalisation flows (gm-first / current-first); either table type. |
| `passives` | `size_resistor`, `size_capacitor` | Closed-form passive sizing from PDK sheet-R / area-C constants. |
| `registry` | `LUTRegistry` (`.list_available`, `.find`, `.load`) | Enumerate + load committed LUTs under a root dir by `(pdk, device, corner[, temp_c, wf_um])`, attaching the manifest. |
| `registry` | `load_lut`, `finger_width_set`, `search_luts`, `default_roots` | Load one table, or one device's tables at every finger width, by name from the roots this installation searches (no root to pass in); list every table those roots hold. |
| `contract` | `OperatingPoint`, `SizedDevice`, `SizedPassive`, `SizingReport`, `SanityGate`, `GeometryBounds`, and the manifest models `LUTManifest`, `AxisSpec`, `LUTConditions`, `LUTModelRecord`, `LUTProvenance` | The single Pydantic-v2 I/O contract (one source of truth; feeds OpenAPI/TS/MCP later). |
| `errors` | `GmidError`, `OutOfGridError` | Fail-loud: off-grid / NaN / un-interpolable lookups, and a gm/ID off the slice's reachable band, raise with the characterized grid in the message — never a silent edge clamp, and never a bare `ValueError` out of scipy (a degenerate bias slice such as `VDS=0` is reported as `OutOfGridError` naming the offending axis). |

`gm_id_for_jd(jd, L, vds, vsb=0.0)` is the **weak-inversion entry point**: where gm/ID plateaus, JD
resolves better. It inverts the table to the gm/ID giving a target current density [A/µm], round-trips
the inversion (the read-back must land within 5 % *of the requested JD*), and raises `OutOfGridError`
if the target JD doesn't invert consistently —
`size_for_current_density(..., jd=…)` uses it under the hood.

### Reachability: the gm/ID band, not the VGS grid

gm/ID is **not monotonic in V<sub>GS</sub>** — it climbs towards weak inversion, peaks, then
collapses as the device turns off. pygmid inverts **only the falling branch** and pchip-*extrapolates*
past its ends, returning finite garbage (negative JD, kilovolt V<sub>GS</sub>, negative widths) with
nothing but a warning printed to stdout. So the reachability domain is that branch, not the
V<sub>GS</sub> grid:

```python
lo, hi, vgs_peak = nch.gm_id_band(L=0.13, vds=0.4)  # e.g. (1.02, 27.79, 0.25) on the IHP nmos
```

`at()`, `sweep()` and a `GM_ID=`-keyed `look_up()` all gate every requested gm/ID against `[lo, hi]`
— a **closed** interval, endpoints included — and raise `OutOfGridError`
naming the band when it falls outside (`look_up()` gates the slice pygmid actually reads, including
the L/VDS/VSB defaults pygmid fills in for an axis left out). On LUTs whose peak sits at an
**interior** V<sub>GS</sub> (most IHP `sg13g2` slices) an
above-peak request solves back to a V<sub>GS</sub> that *is* inside the grid, so a V<sub>GS</sub>-range
check alone silently passed it — that is the band the guard closes. `at()` additionally rejects a
non-positive current density, and the sizing flows reject a non-finite or non-positive `gm`, `ID`,
`jd` or `W`: **a negative width is never returned with `passed=True`**.

`gm_id_band()` is a public entry point, so it gates its own bias axes like the others (an off-grid
`L`/`VDS`/`VSB` raises rather than pchip-extrapolating into a confident-looking band), rejects a
slice that carries no current (VDS=0 degenerates, ID→0 — including the slices whose ID/W locus is a
single *denormal* sample), and never returns a non-positive lower bound. The solved-V<sub>GS</sub>
backstop inside `at()`/`sweep()` carries a float-noise tolerance of `1e-9·span`: on a LUT peaking at
the V<sub>GS</sub> grid edge the band maximum inverts to ≈`-4e-18 V`, and rejecting *that* would
contradict the closed interval above. Anything further out still raises.

### Finger width: `FingerWidthSet` and the `finger_width` gate

A LUT's normalised parameters (JD, gm/gds, C/W, the solved V<sub>GS</sub>) are invariant under
*adding identical fingers*, but they depend on the **finger width itself** — a 0.5 µm and a 5 µm
finger read a few-to-tens of % apart. So a single `DeviceTable` only describes fingers at its own
characterization width, `nch.w_char`.

```python
from spicexplorer_gmid import finger_width_set, size_for_gm

fs = finger_width_set("sky130", "sky130_fd_pr__nfet_01v8")  # every width the roots hold
fs.finger_widths  # [5.0] on the committed store, [0.5, 1.0, 5.0] once extracted
op = fs.at(gm_id=15, L=0.5, vds=0.9, wf=2.0)  # linearly interpolated across finger width
dev = size_for_gm(fs, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=2.0)  # wf is REQUIRED for a set
```

`finger_width_set(pdk, device, corner="tt", *, temp_c=None, widths=None, roots=None)` opens the
untagged 5 µm table and each `__wf<W>u` companion (`__wf0p5u` is 0.5 µm) through `load_lut`, so it
searches the same roots in the same order (see [Where the tables are](#where-the-tables-are-load_lut-no-root-to-hand-in)).

| argument | effect |
|---|---|
| `widths=None` | opens every finger width the searched roots hold for that device, corner and temperature |
| `widths=(0.5, 1, 5)` | opens exactly those widths [µm] |
| `temp_c=-40` | opens the `__-40C` tables instead of the 27 °C ones |

A requested width with no table raises **one** `KeyError` for the whole set. It lists the missing
widths and their file stems, the widths found, every root searched with what it holds, and the
extraction command. `FingerWidthSet.load({wf: path})` still takes explicit paths.

The committed open-PDK tables are the 5 µm ones only. The narrow companions are written by
`regen_gmid_luts.py --fingers` in analog-db, for the widths listed under `gmid.finger_widths` in
that PDK's registry entry.

Both sizing entry points take either table type. `wf` is passed through as the keyword-only argument
`FingerWidthSet` requires (omitting it on a set raises `GmidError`); on a plain `DeviceTable` `wf` is
the finger width you intend to *draw* — it picks the finger count when no `wf_max` is given. On a set,
an interior `wf` blends two per-table JD→gm/ID inversions, and the **blend** is held to the same 5 %
round-trip contract each table is (JD runs exponentially in gm/ID, so the straight line between two
consistent answers is not itself consistent — measured up to 7.59 % off on the production
{0.5, 1.0, 5.0} µm sky130 store). An interior `wf` that cannot honour it raises rather than returning
a `SizedDevice` that disagrees with its own operating point.

Every `SizedDevice` also carries a **`finger_width` gate** comparing the realised `W/nf` against the
width the operating point was characterized at, over the window
`[w_char/wf_ratio_max .. w_char·wf_ratio_max]` (default `wf_ratio_max` 2×). It is **three-state**:

| you passed | narrow side (`< w_char/2`) | wide side (`> 2·w_char`) |
|---|---|---|
| `wf=` | `fail` (vetoes `passed`) | `fail` (vetoes `passed`) |
| `wf_max=` only | `fail` (vetoes `passed`) | `unchecked` (advisory) |
| neither | `unchecked` (advisory) | `unchecked` (advisory) |

An `unchecked` gate reports `ok=False` and its measurement in `detail`, but **does not** flip
`SizedDevice.passed` — with no `wf`/`wf_max` and `nf=1`, `W/nf` is not a finger choice at all, it is
the total width the physics demanded, so the ledger is reporting LUT *coverage* rather than caller
geometry. (Gating it unconditionally turned every device under `w_char/2` red — below ~7.5 µA on the
5 µm sky130 LUT, i.e. the whole low-current half of the design space.) Note what the gate does **not**
police: `wf_max` fingering *wider* than `w_char` inside the 2× window stays green — `wf_max=10` on a
5 µm table realises a 7.46 µm finger, +49.1 %, `status="ok"`. Only gross narrowing is a hard fail, and
the 2× default is argued from narrow-width-effect physics, **not measured against a live PDK sweep**.

`wf_ratio_max` is a *widening* factor and must be ≥ 1 (below 1 the window inverts); NaN and anything
under 1 raise `GmidError` rather than silently reversing the gate. `math.inf` is accepted and means
"no opinion" — the window `[0 .. inf]`, i.e. the gate switched off.

## LUT registry & manifests

Each committed LUT is a `<pdk>/<stem>.pkl` data file paired with a `<pdk>/<stem>.manifest.json`
sidecar (the typed `LUTManifest`: the full run dimensions — `L`/`VGS`/`VDS`/`VSB` grids — plus
`conditions` (temp/W/nfing), `corner`, the model corner lines, stored params, and extraction
`provenance`). The stem is `<device>__<corner>[__<T>C][__wf<W>u]`: the extractor tags a LUT only when
it is *off* the historic nominal (27 °C, a 5 µm finger), so the original names keep working.
`DeviceTable.load()` auto-attaches the sidecar; `LUTRegistry` enumerates and loads by name:

### Where the tables are (`load_lut`, no root to hand in)

`load_lut` loads a table by PDK, device and corner from a fixed list of roots, so a design repo
does not pass a directory. A design repo's working directory is neither the platform checkout nor
the LUT store, so it has no root to hand `LUTRegistry` (#157).

```python
from spicexplorer_gmid import load_lut, search_luts, default_roots

nch = load_lut("generic-n65", "nmos_lvt")  # corner="tt"; manifest attached
search_luts()  # every table this installation can reach, one manifest
# per table file (__<T>C, __wf<W>u tables included)
default_roots()  # the search order, existing or not
```

Search order: the first root that holds a table serves it, so a table extracted locally is used in
place of a committed one of the same name, and `search_luts` lists that name once, from that root.

| # | root | what lives there |
|---|---|---|
| 1 | `$SPICEXPLORER_GMID_ROOTS` (`os.pathsep`-separated) | a store rows 2-4 do not cover: a mounted share, a per-project cache |
| 2 | `~/.spicexplorer/gmid` | the Spectre lane's own `out_root` — a **licensed** kit's tables, in no repo. Derived curves are not kit content, but committing them is an owner decision, so the default store is out-of-repo and per-user |
| 3 | `$SX_ROOT/spicexplorer-platform/examples/analog-db/_shared/gmid` | the committed open-PDK tables as the shared installation exposes them to a design |
| 4 | `<enclosing platform checkout>/examples/analog-db/_shared/gmid` | the same, when you *are* in a platform checkout |

`$SX_ROOT` deliberately precedes the enclosing checkout: a design should get the installation's
tables, not whichever checkout happens to sit above its cwd. A miss raises `KeyError` naming
**every root searched and what each holds** — an empty store and an absent PDK are different
problems with different fixes, and the extraction command for each lane is in the message.

`DeviceTable.from_lut_dict(data)` takes an **in-memory** pygmid table — what an extractor's
`assemble()` returns — so a table just characterized on the lane can be sized against without a
round trip through a file.

### `LUTRegistry`: one known root

```python
from spicexplorer_gmid import LUTRegistry

reg = LUTRegistry(".../_shared/gmid")  # root holding <pdk>/ sub-dirs
for m in reg.list_available("sky130"):  # omit the pdk arg for the whole catalog
    print(m.pdk, m.device, m.corner)

nch = reg.load("sky130", "sky130_fd_pr__nfet_01v8")  # corner="tt" default; manifest attached
nch.manifest.conditions  # the characterization conditions

cold = reg.load("sky130", "sky130_fd_pr__nfet_01v8", temp_c=-40, wf_um=1.0)  # a tagged variant
```

`reg.find(pdk, device, corner="tt", *, temp_c=None, wf_um=None)` returns just the `LUTManifest`
(raises `KeyError`, listing what *is* committed, when absent); `reg.load(...)` raises if the
addressed `.pkl` is missing. Two fail-loud details worth knowing: the `.pkl` is resolved from the
**addressed stem**, never from the manifest's `lut_file` field (the extractor writes that field
un-suffixed, so trusting it would serve the 27 °C/5 µm table under an `__85C`/`__wf1u` manifest); and
an explicitly addressed variant whose sidecar records a *different* temperature or width raises
`GmidError` rather than being served. A sidecar that exists but cannot be read (I/O error, bad JSON, a
schema field renamed) is never silent: `DeviceTable.load()` still loads the table with
`manifest=None`, and `list_available()` skips that LUT, each with a logged warning naming the file;
`find()`/`load()` raise its validation error. The registry **never imports the analog-db package** —
it reads the sidecars directly, so the tool stays decoupled from the DB.

## What the contract carries

| Model | Fields |
|---|---|
| `OperatingPoint` | `gm_id, L, vds, vsb, vgs, jd, av0, ft, cgg_w, cdd_w` (the LUT view at one bias) |
| `SizedDevice` | `W, L, nf, ID, gm, cgg, cdd, op, gates`; `.passed` (every **blocking** gate holds), `.wf` |
| `SizedPassive` | `kind, target, value` + geometry (`squares`/`area_um2`) |
| `SizingReport` | named `devices` + `passives` + `assumptions` ledger |
| `SanityGate` | `name, ok, detail, status` (`"ok"`/`"unchecked"`/`"fail"`), `.blocking` — saturation head-room, intrinsic-gain/fT finiteness, finger width vs `w_char`, geometry envelope. `"unchecked"` is an advisory: reported with `ok=False`, never a veto. An omitted `status` mirrors `ok`, so a two-state gate needs no change. |

Off-grid / NaN lookups raise `OutOfGridError` **with the characterized grid in the message** — never
a silent clamp to an edge value (a confidently-wrong size).

## CLI / Run

**Library-only — there is no console script.** `pyproject.toml` declares no `[project.scripts]`; the
tool is driven from Python (or a notebook). Composition that reads the DB, sizes a whole block, and
re-simulates is an *orchestration* concern, not part of this leaf tool.

## Notebooks

- [`notebooks/spicexplorer_gmid_quickstart.py`](notebooks/spicexplorer_gmid_quickstart.py) — the sizing flow (`load_lut` / `search_luts`, `DeviceTable.at`, `gm_id_band`, `sweep`, `size_for_gm`, `size_for_current_density`, the finger-width gate, `size_resistor` / `size_capacitor`) on the four committed tt tables (sky130 and IHP, NMOS and PMOS). A marimo notebook that imports `spicexplorer_gmid` only, never `spicexplorer_analog_db`; `tests/test_notebooks.py` runs it offline.

The worked references beside the LUT data and the consumer flow:

- [`gmid_tables_tour.py`](../../examples/analog-db/notebooks/gmid_tables_tour.py) — load a committed LUT, read operating points, sweep the gm/ID trade-offs.
- [`gmid_sizing_demo.py`](../../examples/analog-db/notebooks/gmid_sizing_demo.py) — the `size_for_gm` / `size_for_current_density` flows + sanity gates.
- [`gmid_cascode_resizing.py`](../../examples/notebooks/gmid_cascode_resizing.py) — consumer flow: role-by-role re-sizing of the folded-cascode OTA `amp_004_folded_cascode` into the sky130 envelope (the "P5" flow), written as a `sizing.yaml` fragment. A marimo notebook; `tests/test_notebooks.py` runs it offline and checks every emitted variable against the circuit's sky130 `sizing.yaml`.

## Tests

```bash
uv run pytest packages/spicexplorer-gmid/tests -v
```

Tests run **PDK-free** against copies of the committed sky130 and IHP NMOS LUTs in `tests/fixtures/`
(no DB import), plus two small **synthetic** PMOS tables built in memory
(`_gmid_fixtures.synthetic_pmos_lut`: a sky130-pfet-shaped and an IHP-pmos-shaped one) that follow the
pmos magnitude convention — `|ID|` and `|VSB|` stored positive — and check that a table breaking it is
refused (`test_gmid_pmos.py`). The PDK-gated `.op` back-annotation check (a table-predicted
operating point vs a real ngspice `.op`, 10 % gate) is `test_gmid_backannot.py` — a `slow` test that
runs inside the api container (`plan_gmid_sizing.md` **P4, done**):

```bash
uv run pytest packages/spicexplorer-gmid/tests -m slow   # PDK-gated .op back-annotation (in the api container)
```

> Cascode re-sizing is not code in this package — it is a *consumer* notebook
> (`examples/notebooks/gmid_cascode_resizing.py`) that drives the same `size_for_gm` /
> `size_for_current_density` API role-by-role; see `doc/archive/plan_gmid_sizing.md` P5.

See the meta-repo [`doc/archive/plan_gmid_sizing.md`](../../../doc/archive/plan_gmid_sizing.md) for the roadmap
(P1 scaffold … P5 cascode re-sizing) and the `gmid-sizing` / `gmid-lut-generation` Claude skills for
the methodology condensation the flows encode.
