# gm/ID skills for spicexplorer agents

Two skills implementing the Jespers & Murmann lookup-table methodology
("Systematic Design of Analog CMOS Circuits Using Pre-Computed Lookup Tables").

**Provenance + review status:** a condensation of the textbook; the book itself
is not redistributed here. The two **Practical Circuit Examples** chapters
(Ch 5 bias/LDO/LNA/charge-amp/PVT, Ch 6 OTAs/switches) have had a full
review/extraction pass (2026-06-12): theory fact-checked against the source and
the worked designs distilled into `references/worked-examples.md`. Ch 4
(noise/distortion/mismatch derivations) and App 1/3 have not yet had that pass.
Keep the references book-faithful; API/tooling specifics live in the platform
docs.

## Platform integration (the implementation these skills steer)

- **LUT generation**: `analog-db gmid-extract` (analog-db repo, docs at
  `_shared/GMID.md`) — corner, LV/HV device variant, and the full
  VGS/VDS/VSB/L grid configurable via the PDK registry + CLI. This is the
  **only** LUT path; do not write ad-hoc sweep scripts.
- **LUT format + location**: pygmid-compatible `.pkl` (the Murmann LUT-dict
  convention) committed at `_shared/gmid/<pdk>/<device>__<corner>.pkl`. Five
  LUTs are committed @ tt: sky130 {nfet_01v8, pfet_01v8}, ihp-sg13g2
  {sg13_lv_nmos, sg13_lv_pmos}, gf180mcu {nfet_03v3} — i.e. NMOS+PMOS for
  sky130 and ihp; gf180 is NMOS-only so far.
- **Lookup**: `pygmid.Lookup` reads the committed `.pkl` directly. The
  platform's **`spicexplorer-gmid`** tool
  (`platform/packages/spicexplorer-gmid`) wraps it with a typed, fail-loud API (`DeviceTable` / `size_for_gm` / `size_for_current_density` /
  passives) — prefer it over raw pygmid for sizing.
- **Worked examples**: the analog-db `notebooks/` gm/ID notebooks (tables
  tour + sizing demo) exercise the committed LUTs end-to-end.

```
gmid-sizing/                      # the one agents use daily
├── SKILL.md                      # core flow, units, pitfalls (always loaded on trigger)
└── references/
    ├── lookup-api.md             # lookup/lookupVGS semantics (the book kit's API, as pygmid implements it)
    ├── sizing-recipes.md         # IGS, JD flow, self-loading, noise/distortion/mismatch
    ├── ota-recipes.md            # full OTA flows (basic, folded-cascode, two-stage Miller) + SC switches
    ├── biasing-and-pvt.md        # constant-gm bias, cascode mirrors, corner methodology
    ├── worked-examples.md        # concrete sized reference designs from Ch 5 & Ch 6 (numbers + SPICE deltas)
    ├── verification.md           # ngspice back-annotation + tolerance gates
    └── book-map.md               # topic → chapter map of the source textbook

gmid-lut-generation/              # one-time per PDK/corner/temp
└── SKILL.md                      # drives `analog-db gmid-extract`; output contract, acceptance checks
```

## Using them elsewhere

- Claude Code: these live in this repo's `.claude/skills/`, so a clone picks
  them up automatically. To use them in another repo, copy both folders into
  that repo's `.claude/skills/`. Skill metadata (name + description) is what
  triggers them; the bodies and references load on demand.
- Claude.ai project: upload as user skills; they will appear under
  `/mnt/skills/user/`.
- Other agent runtimes: point the skill loader at these directories; the
  implementation layer they invoke is `analog-db gmid-extract` +
  `spicexplorer-gmid` (which wraps `pygmid`).

## Adding resources (the part agents must respect)

1. New LUTs come from the pipeline, never dropped in by hand: `analog-db
   gmid-extract --pdk <pdk> [--device --corner ...]` writes them into the DB
   at `_shared/gmid/<pdk>/`; commit them there with the regen command in the
   message. The sizing skill verifies header `CORNER`/`TEMP` against the
   simulation settings — never recycle a nominal table for a corner check.
2. New PDK: add the registry `gmid:` block (+ a `_FAMILY` entry if the model
   family is new) per the gmid-lut-generation skill's debug-first rule.
3. New circuit recipes: append to `gmid-sizing/references/sizing-recipes.md`
   rather than growing SKILL.md; keep SKILL.md under ~150 lines so it stays
   cheap to load.
4. Worked examples: add notebooks to the analog-db `notebooks/` dir and
   reference them from sizing-recipes.md.

## Dependencies

pygmid (+ numpy). ngspice + PDK only for generation/verification, i.e. the
EDA base image / api container (`make up-live`).
