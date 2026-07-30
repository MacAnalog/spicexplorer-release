# spicexplorer-gmid

Deterministic transistor sizing with the **gm/ID lookup-table methodology** (Jespers & Murmann,
*Systematic Design of Analog CMOS Circuits Using Pre-Computed Lookup Tables*). Pick an inversion
level (gm/ID) and a channel length per device; read current density, V<sub>GS</sub>, intrinsic gain,
f<sub>T</sub>, and capacitances off a pre-characterized LUT; de-normalize to a width. No square-law
hand formulas, no SPICE tweaking loop — agreement with simulation to a few percent.

It is a **leaf tool**: it depends on `spicexplorer-core` + `pygmid` + `numpy` + `pydantic` only. It
never imports a peer tool (the optimizer, `netlist2tf`) or the data repo `spicexplorer-analog-db`.
The LUTs come from `analog-db gmid-extract` (committed at `_shared/gmid/<pdk>/<device>__<corner>.pkl`),
but this package takes a *path or object*, so reading the DB and re-simulating is an orchestration
concern, not part of the tool.

Import name: `spicexplorer_gmid` (distribution `spicexplorer-gmid`).

## Quickstart

```python
from math import pi
from spicexplorer_gmid import (DeviceTable, size_for_gm, size_for_current_density,
                               size_resistor, size_capacitor)

# 1. load a committed pygmid LUT (sky130 1.8 V core NMOS, TT corner)
nch = DeviceTable.load(".../_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl")

# 2. read an operating point off the table (everything but the 4 coordinates is interpolated)
op = nch.at(gm_id=15, L=0.5, vds=0.9)
print(op.jd, op.vgs, op.av0, op.ft)        # A/µm, V, gm/gds, Hz

# 3a. gm-first flow: size to a transconductance target (e.g. gm for a target GBW·CL)
dev = size_for_gm(nch, gm=2 * pi * 1e9 * 1e-12, gm_id=15, L=0.5, vds=0.9)
print(dev.W, dev.ID, dev.passed)           # width [µm], bias current [A], all sanity gates hold?

# 3b. current-first / JD flow: fix the bias current + inversion level
dev = size_for_current_density(nch, ID=50e-6, gm_id=12, L=1.0, vds=0.9)

# 4. explore the trade-off curves
sw = nch.sweep(gm_id=(5, 25), L=0.5, vds=0.9)   # arrays: jd, ft, av0, vgs over gm/ID

# 5. passives from PDK constants
r = size_resistor(10e3, sheet_res=355, w_um=1.0)   # → squares, drawn length
c = size_capacitor(1e-12, area_cap=2e-3)           # → plate area [µm²] from F/µm²
```

## Public API — by module

Everything is re-exported at the top level (`from spicexplorer_gmid import …`); the table groups by
source module.

| Module | Surface | What it's for |
|---|---|---|
| `tables` | `DeviceTable` (`.load`, `.at`, `.look_up`, `.gm_id_for_jd`, `.sweep`, `.manifest`; grids `L_grid`/`VGS_grid`/`VDS_grid`/`VSB_grid`), `Sweep` | Typed, fail-loud wrapper over a pygmid `Lookup`. `at()` → `OperatingPoint`; `sweep()` → trade-off arrays. |
| `sizing` | `size_for_gm`, `size_for_current_density` | The two de-normalisation flows (gm-first / current-first). |
| `passives` | `size_resistor`, `size_capacitor` | Closed-form passive sizing from PDK sheet-R / area-C constants. |
| `registry` | `LUTRegistry` (`.list_available`, `.find`, `.load`) | Enumerate + load committed LUTs under a root dir by `(pdk, device, corner)`, attaching the manifest. |
| `contract` | `OperatingPoint`, `SizedDevice`, `SizedPassive`, `SizingReport`, `SanityGate`, `GeometryBounds`, and the manifest models `LUTManifest`, `AxisSpec`, `LUTConditions`, `LUTModelRecord`, `LUTProvenance` | The single Pydantic-v2 I/O contract (one source of truth; feeds OpenAPI/TS/MCP later). |
| `errors` | `GmidError`, `OutOfGridError` | Fail-loud: off-grid / NaN lookups raise with the characterized grid in the message — never a silent edge clamp. |

`gm_id_for_jd(jd, L, vds, vsb=0.0)` is the **weak-inversion entry point**: where gm/ID plateaus, JD
resolves better. It inverts the table to the gm/ID giving a target current density [A/µm], round-trips
the inversion (5 % tol), and raises `OutOfGridError` if the target JD doesn't invert consistently —
`size_for_current_density(..., jd=…)` uses it under the hood.

## LUT registry & manifests

Each committed LUT is a `<pdk>/<device>__<corner>.pkl` data file paired with a
`<pdk>/<device>__<corner>.manifest.json` sidecar (the typed `LUTManifest`: the full run dimensions —
`L`/`VGS`/`VDS`/`VSB` grids — plus `conditions` (temp/W/nfing), `corner`, the model corner lines,
stored params, and extraction `provenance`). `DeviceTable.load()` auto-attaches the sidecar;
`LUTRegistry` enumerates and loads by name:

```python
from spicexplorer_gmid import LUTRegistry

reg = LUTRegistry(".../_shared/gmid")            # root holding <pdk>/ sub-dirs
for m in reg.list_available("sky130"):           # omit the pdk arg for the whole catalog
    print(m.pdk, m.device, m.corner)

nch = reg.load("sky130", "sky130_fd_pr__nfet_01v8")   # corner="tt" default; manifest attached
nch.manifest.conditions                          # the characterization conditions
```

`reg.find(pdk, device, corner="tt")` returns just the `LUTManifest` (raises `KeyError`, listing what
*is* committed, when absent); `reg.load(...)` raises if the manifest's `.pkl` is missing. The registry
**never imports the analog-db package** — it reads the sidecars directly, so the tool stays decoupled
from the DB.

## What the contract carries

| Model | Fields |
|---|---|
| `OperatingPoint` | `gm_id, L, vds, vsb, vgs, jd, av0, ft, cgg_w, cdd_w` (the LUT view at one bias) |
| `SizedDevice` | `W, L, nf, ID, gm, cgg, cdd, op, gates`; `.passed`, `.wf` |
| `SizedPassive` | `kind, target, value` + geometry (`squares`/`area_um2`) |
| `SizingReport` | named `devices` + `passives` + `assumptions` ledger |
| `SanityGate` | `name, ok, detail` — saturation head-room, intrinsic-gain/fT finiteness, geometry envelope |

Off-grid / NaN lookups raise `OutOfGridError` **with the characterized grid in the message** — never
a silent clamp to an edge value (a confidently-wrong size).

## CLI / Run

**Library-only — there is no console script.** `pyproject.toml` declares no `[project.scripts]`; the
tool is driven from Python (or a notebook). Composition that reads the DB, sizes a whole block, and
re-simulates is an *orchestration* concern, not part of this leaf tool.

## Notebooks

This package has no in-package `notebooks/` dir. The worked references live with the LUT data and the
consumer flow:

- [`gmid_tables_tour.ipynb`](../../examples/analog-db/notebooks/gmid_tables_tour.ipynb) — load a committed LUT, read operating points, sweep the gm/ID trade-offs.
- [`gmid_sizing_demo.ipynb`](../../examples/analog-db/notebooks/gmid_sizing_demo.ipynb) — the `size_for_gm` / `size_for_current_density` flows + sanity gates.
- [`gmid_cascode_resizing.ipynb`](../../examples/notebooks/gmid_cascode_resizing.ipynb) — consumer flow: role-by-role re-sizing of a folded-cascode OTA into the sky130 envelope (the "P5" flow).

## Tests

```bash
uv run pytest packages/spicexplorer-gmid/tests -v
```

Tests run **PDK-free** against a copy of the committed sky130 NMOS LUT in `tests/fixtures/`
(no DB import). The PDK-gated `.op` back-annotation check (a table-predicted operating point vs a
real ngspice `.op`, 10 % gate) is `test_gmid_backannot.py` — a `slow` test that runs inside the api
container (`plan_gmid_sizing.md` **P4, done**):

```bash
uv run pytest packages/spicexplorer-gmid/tests -m slow   # PDK-gated .op back-annotation (in the api container)
```

> Cascode re-sizing is not code in this package — it is a *consumer* notebook
> (`examples/notebooks/gmid_cascode_resizing.ipynb`) that drives the same `size_for_gm` /
> `size_for_current_density` API role-by-role; see `doc/plan_gmid_sizing.md` P5.

See the meta-repo [`doc/plan_gmid_sizing.md`](../../../doc/plan_gmid_sizing.md) for the roadmap
(P1 scaffold … P5 cascode re-sizing) and the `gmid-sizing` / `gmid-lut-generation` Claude skills for
the methodology condensation the flows encode.
