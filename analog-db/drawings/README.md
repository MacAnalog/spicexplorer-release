# drawings/ — hand-drawn schematic staging area

The home for **hand-drawn design families** (xschem `.sch`/`.sym` + their
`simulation/` exports): multi-block hierarchies sketched from papers or from
scratch, *before and independent of* their life as catalogue entries. Moved out
of `templates/` (which is the circuitgraph **matcher**-template library —
structural signatures, not designs) per the owner's PR #37 direction.

## Lifecycle: staging → landing → in-place ownership

1. **Stage.** Draw a family here: `drawings/<family>/` holds the blocks'
   `.sch`+`.sym` and headless/xschem netlist exports under `simulation/`.
   One family typically contains **several** circuit-worthy blocks.
2. **Land.** Each block worth cataloguing becomes a `circuits/<id>/` entry
   (accession via `analog-db new-circuit`), and the mapping is recorded in the
   family's **`landing.yaml`** manifest: drawn block → circuit id → class,
   plus any normalizations applied on the way in. The entry gets a **copy** of
   its own `.sch`/`.sym` under `circuits/<id>/pdk/<pdk>/schematic/` with an
   `xschemrc` that resolves child symbols from this directory.
3. **Own in place.** After landing, the `circuits/<id>/.../schematic/` copy is
   the **authoritative, editable** drawing for that circuit — edit it there,
   re-export, and regenerate the entry. The `drawings/` family remains the
   historical staging record plus the home of blocks not (yet) landed. This
   avoids repeated bulk porting from multi-circuit family folders: per-circuit
   evolution happens per-circuit.
   *(Exception: a fix that must reach several entries at once — e.g. a shared
   sub-block bug found during landing — may be applied here first and fanned
   out, as done for the chopper redraw; `DRAWING_REVIEW.md` tracks such
   passes.)*

Every verifiable `circuits/` entry is expected to carry a viewable/editable
schematic (`artifacts.schematic`); a landing is not complete without it.

## OTA vs. op-amp — do not mix them (owner decision, PR #37)

Both currently live under `class: amplifier` (until the plan's P1 class
split), distinguished by the **`subfamily`** facet and their symbols:

| | **OTA** (`subfamily: ota`) | **Op-amp** (`subfamily: opamp`) |
|---|---|---|
| Output | high-impedance current-source node (CS / cascode / single stage) | **buffered** low-impedance voltage output (follower / class-AB stage) |
| Gain | Gm·Rout, set by the load node | internal, load-insensitive |
| Load | capacitive / SC networks | resistive + capacitive |
| Compensation | often self-compensated at the load | internal (Miller/…) |

Corpus classification (note the drawn names don't always match the physics —
the *output stage* decides):

| Drawn block | Landed as | Actually is | Why |
|---|---|---|---|
| `two-stage-ota-core` (Hsu) | amp_025 | **op-amp** | class-AB push-pull *follower* output = buffered |
| `two-stage-opamp-core` (Fan) | amp_026 | **OTA** | common-source second stage = high-Zout |
| `integrator-switchcap-opamp` | amp_027 | **OTA** | telescopic single stage |
| `ideal-amp-fully-diff` | amp_028 | **ideal OTA** | Gm + finite Rout macromodel (see `_shared/IDEAL_AMP.md`) |

**Fixed symbol convention** for both: pins `vinp vinn voutp voutn vdd vss`, in
that order, lowercase — the class-bench contract, and as of 2026-07-20 the order
actually drawn in `symbol-templates/ota-fully-diff/`. **Single-ended** blocks use
`vdd vout vinp vinn vss` (`symbol-templates/ota-single-ended/`), the order the
landed single-ended entries already carry. Sanctioned extras — bias pins
(`vb1..vbN`, `ibias`, `vcmfb_ref`) and chopper / phase clock pins
(`vctl`/`vctl_not`, `clk_*`) — splice in **before the trailing supply pins**, not
after the core six. Distinct symbol *shapes* for OTA (open triangle, Gm
annotation) vs op-amp (closed triangle) are recommended for new drawings so the
two are never visually conflated.

## Files

- `<family>/landing.yaml` — the landing manifest (block → circuit id/class).
- `shared/` — cross-family reusable blocks (referenced by `shared/<block>.sym`);
  `shared/ideal/` holds the behavioral macromodels (ideal OTA, CMFB, VCM sense),
  `shared/` the structural cells (transmission gate, chopper, capbank). A block used
  by more than one family lives here, not inside one family folder — see
  [`shared/README.md`](shared/README.md).
- `DRAWING_REVIEW.md` — the drawing-debug tracker for the CCIA landing pass.
- `TODO_bio_afe_port.md` — the bio-afe landing checklist.
- `xschemrc` — opens any family's schematics with this directory on the
  library path (so both `<family>/…` and `shared/…` symbol refs resolve).

Follow-up (tracked, not yet built): a small `analog-db` check that every
`landing.yaml` target exists, carries `artifacts.schematic`, and that the
entry's schematic copy still opens against this library.
