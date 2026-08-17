# spicexplorer-layout

Parameterized layout generation as a **library**. A layout of record is *code*: a Python
module exposing a frozen `LayoutParams` dataclass (every field is a knob an optimizer may move,
with a default and optional `BOUNDS`) and `build(params, sizing=None) -> gdsfactory.Component`.
This package gives that contract a loader, a deterministic build step (GDS + bbox / area /
sha256), a `params → GDS` callable for `spicexplorer_signoff.run_flow` and optimizer trials,
matching-pattern helpers, and a headless render.

## Layering

Leaf tool: depends on `spicexplorer-core` only. `gdsfactory` + `ihp-gdsfactory` + `klayout`
are the **opt-in `gds` extra** (`uv sync --extra gds`; on the research server the `ai_env`
conda env already has them) — the contract, loader, pattern orders and offline tests import
without them. `GdsBuilder` runs the generator in a **subprocess** by default (gdsfactory
caches components by name+params and PDK activation is process-global — the classic ways to
rebuild yesterday's layout) and can point at another interpreter (`python=`) that has the
generation stack; this package's `src` is exposed to it via `PYTHONPATH`. Never imports a
peer tool (`spicexplorer_signoff` consumes the builder, not the other way round).

## Public API

| call | what |
|---|---|
| `load_generator(path_or_module)` → `Generator` | import `gen_<cell>.py`; checks `LayoutParams` (dataclass) + `build`; reads `CELL`, `BOUNDS` |
| `params_schema(gen)` / `params_from_json(gen, text)` | knob list `{name, default, lo, hi}` for optimizers/UIs; overrides → `LayoutParams` (unknown keys are an error) |
| `build_gds(gen, params, out, sizing=, cell=)` → `GdsBuild` | writes the GDS (no timestamps → same params, same bytes), reports `bbox_um`, `area_um2`, `sha256` |
| `GdsBuilder(gen_path, out_dir, cell=, sizing_json=, python=, inproc=False)` | callable `params → Path`; `.last` is the `GdsBuild` |
| `render_png(gds, png, pdk=)` | headless PNG with the PDK layer colours (`klayout.lay`) |
| `patterns.interdigitate_order(labels, n_each, style="ABBA")` | finger order for an offset-setting pair |
| `patterns.common_centroid_order(labels, rows, cols, n_each=)` | 2-D grid (ABBA/BAAB rows, cross-quad) for a ratio |
| `patterns.with_dummies(order, n)` / `mirror_pair(...)` / `place_row(...)` | dummies; gdsfactory placement helpers (lazy import) |
| `review.Review / Finding`, `load_review / dump_review / validate` | the **layout-review DSL** (`schema: layout-review/1`; **YAML canonical** — `REVIEW.yaml` — JSON accepted): findings with geometry anchors, severity, category, evidence, effect (metric/delta/model), fix (knob → value), re-review verdict |
| `iterations.snapshot(iter_dir, note=, detail=, gen_path=, gds=, params=, drc=, lvs=, pex=, scorecard=, area_um2=, keep_gds=)` → `IterationEntry` | **iteration audit trail**: `note` is a ONE-LINE headline *problem → fix → effect* (≤ 140 chars, warned above; it is what the diff picture and the table show — write it for an expert: `"TM1.b ×5 at xc12 seam: comb bars inset w/2 before end caps → DRC 0"`), `detail` the long form (numbers, reasoning; YAML only); `set_note(iter_dir, it, note)` tightens a headline after the fact (the old text moves to `detail`); copies the generator source + GDS + a PDK render into `iter_dir/it<NN>/`, records knob values, DRC per-rule counts **and hit locations**, LVS/PEX verdicts, shas and the designer's one-line *what changed / what it fixed* note in `iter_dir/iterations.yaml` (append-only) |
| `iterations.diff_png(iter_dir, "it02", "it03")` | **before \| after** picture: left = the before layout with its DRC hits; right = the after layout with the changed regions boxed (per-layer GDS XOR, clustered) and the before-hits marked **fixed** (blue) / **still** or **NEW** (red). A floorplan-wide change (shift/re-pitch) is reported as one note instead of a useless whole-cell box |
| `iterations.iterations_table_md(iter_dir)` | the Markdown table for a report's *Iterations* section (links to each `gen.py`, PNG and diff) |
| `measure_protocol.serve(fn)` / `read_request()` / `write_result(scalars)` / `parse_result(stdout)` | the **post-layout `measure` module protocol** the optimizer's layout backend (`spicexplorer.backends.layout`, `measure:` in a `layout-flow/1` spec) speaks with a block-specific bench: ONE JSON request on stdin (`{pex_subckt, pex_netlist, gds, work_dir, cell, params, corner, extra}`) → ONE marked JSON line on stdout (`{"scalars": {...}, "status": "ok"}`); pure stdlib, so it runs in ANY interpreter (the block's own harness venv — the backend puts this package's `src` on `PYTHONPATH`). Write `def measure(req) -> dict[str, float]` and point the spec at it; `serve(measure)` under `__main__` makes the module hand-runnable too |
| `review.annotate(gds, review, png, size=, pdk=, only=, frame=)` / `annotate_crops(gds, review, dir)` | PDK-coloured render with every finding drawn as a numbered, severity-coloured marker (box / crosshair / arrow / polyline / DRC hits, symmetry axis) + legend strip; one zoomed PNG per finding. Uses KLayout's `viewport_trans`, so markers land exactly. |

CLI: `spicexplorer-layout build GEN.py --out-dir D [--params JSON] [--sizing design.json] [--cell C] [--png] [--json]`,
`spicexplorer-layout knobs GEN.py`, `spicexplorer-layout render GDS PNG`,
`spicexplorer-layout annotate GDS REVIEW.yaml PNG [--crops DIR]`, `spicexplorer-layout validate-review REVIEW`,
`spicexplorer-layout snapshot ITER_DIR --note "…" --gen GEN.py [--gds G] [--params J] [--drc drc.json] [--lvs …] [--pex …] [--scorecard …] [--area A] [--no-gds]`,
`spicexplorer-layout diff ITER_DIR it01 it02 [--out PNG]`, `spicexplorer-layout iterations-md ITER_DIR [--rel-prefix P]`, `spicexplorer-layout set-note ITER_DIR it05 "headline" [--detail …]`.

### Iteration audit trail (`iterations`)

A layout goes through many *edit → build → DRC/LVS/PEX* rounds; a reader auditing the work wants
to see **what changed and what it fixed**, per round, with pictures — not a paragraph written
from memory at the end. So after **every** verification round the designer calls `snapshot()`
(or the CLI) with a one-line note, and `diff_png()` for the round before → after:

```
layout/<cell>/iterations/
  iterations.yaml            # append-only log: id, note, shas, knobs, drc{rules,hits}, lvs, pex, files
  it01/ gen.py layout.png    # generator source + PDK render at that round (layout.gds too, unless --no-gds)
  it02/ …
  diff_it01_it02.png         # before | after with changed regions boxed and DRC hits fixed/still/new
```

The report's *Iterations* section is then `iterations_table_md()` output — generated, not typed —
and every row links its picture. Failed builds are snapshots too (`gds=None`, note = the error).
GDS copies can be MBs: keep them if the block repo ignores `layout/**/iterations/*/layout.gds`,
otherwise `keep_gds=False` (sha only; the diff then needs the build dir GDS instead).

## Layout-review DSL (`layout-review/1`)

The reviewer's machine-readable output (YAML — human-readable first; `.json` also loads); every finding is *localizable*:

```yaml
schema: layout-review/1
cell: lpf_core
gds: build/lpf_core.gds            # the GDS the review was made on
gds_sha256: ...
generator: {path: layout/H12/gen_H12.py, params: {...}, sha256: ...}
verdict: PASS with majors           # PASS | PASS with majors | FAIL
reproduced: {build: match, drc: {passed: true, n: 0}, lvs: {passed: true, netlist_sha: ...}, pex: {mode: CC, n_c: 812}, scorecard: {fc_hz: {designer: 249.1, reviewer: 249.1}}}
units: um
axis: {x: 0.0}                      # symmetry axis (drawn)
findings:
  - id: F1
    severity: major                 # blocker | major | minor | note
    category: coupling              # reproduce|drc|lvs|pex|budget|coupling|matching|symmetry|routing|well|leakage|knob|objective|other
    title: net2 TopMetal1 spine runs 40 um parallel to voutp
    where:                          # anchors, µm, GDS coordinates — any number, any mix
      - {kind: box, layer: TopMetal1drawing, x0: -12.0, y0: 210.0, x1: -8.0, y1: 250.0}
      - {kind: pair, a: {x: -10, y: 230}, b: {x: -30, y: 230}}      # arrow: aggressor ↔ victim
      - {kind: point, x: -10.0, y: 250.0}
      - {kind: line, points: [[-10, 210], [-10, 250], [-30, 250]]}
      - {kind: device, name: xm2, x0: -20, y0: 100, x1: -4, y1: 118}
      - {kind: rule, name: NW.b1, locations: [[3.2, 41.0], [3.2, 55.5]]}
      - {kind: net, name: net2}                                     # legend-only
    evidence: "PEX coupling_ff net2|voutp = 0.41 fF vs brief budget 0.28"
    effect: {metric: ph_max_deg, delta: -0.9, unit: deg, model: what-if}
    fix: {knob: shield_w, to: 8.0, note: "or route the spine on Metal3 under the shield"}
    expected: "coupling < 0.1 fF, ph_max +0.7 deg"
    verdict: open                    # open | fixed | worse (re-review)
not_checked: ["RC extraction (kpex RC did not converge)"]
reviewer: layout-reviewer
```

`annotate()` draws it: box → filled outline, point → crosshair, pair → arrow-line, line →
polyline, rule → small squares at each hit, device → box; each tagged with the finding number
in the severity colour (blocker red, major orange, minor yellow, note blue), legend strip
below the render; `annotate_crops()` zooms each finding.

## Generator contract (what a `gen_<cell>.py` must look like)

```python
import dataclasses, gdsfactory as gf
from ihp import PDK, cells as C

PDK.activate()

CELL = "lpf_core_H12pc"
BOUNDS = {"gap_x": (0.8, 2.0), "n_dummy": (0, 2)}


@dataclasses.dataclass(frozen=True)
class LayoutParams:  # the optimizer knobs — never W/L/m (those come from `sizing`)
    gap_x: float = 1.2
    n_dummy: int = 1


def build(params: LayoutParams, sizing: dict | None = None) -> gf.Component:
    c = gf.Component(CELL)
    ...  # sizes from `sizing`, placement/routing from `params`
    return c
```

Optional: `write_lvs_reference(params, sizing=None, out=None) -> str` — the flat `M`/`C`-card
netlist the KLayout LVS deck compares against, regenerated per candidate when it depends on
the knobs (dummies, split arrays) or on the sizing (co-optimization); the optimizer's layout
backend calls it as `lvs: {writer: write_lvs_reference}` and passes `sizing=` when the
signature accepts it.

Reference implementation: `examples/layout/ihp-sg13g2/5t_ota_gf/gen_5t_ota_gf.py` (the
prototype 5T OTA, adapted to the contract; DRC/LVS-clean, kpex-extracted, optimized in-loop).
**Optimizing the knobs through the platform optimizer** (`sim_engine: layout`, the flow spec
`layout-flow/1`, DRC/LVS/PEX gates + post-layout benches as target specs) is
`spicexplorer.backends.layout` — see `examples/layout/ihp-sg13g2/5t_ota_gf/opt/`.

## Tests

`packages/spicexplorer-layout/tests/test_layout_offline.py` — loader/schema/build determinism
with a stub generator, subprocess builder, pattern orders. No gdsfactory needed.

## Status / next

T0 of `doc/plan_layout_automation.md` (meta-repo). Next: T1 placement engine (row/mirror-pair
placer from the prototype behind a grouping spec), T2 pattern geometry (interdigitation /
common-centroid instantiation + dummies as gdsfactory helpers), live-PCell spike.
