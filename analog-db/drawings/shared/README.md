# drawings/shared/ — cross-family reusable blocks

Blocks used by **more than one** drawing family (and by landed `circuits/` entries)
live here instead of inside one family folder, so there is a single source of truth.

- **`shared/`** — reusable **structural / transistor-level** cells:
  - `transmission_gate_pair` — the TG switch primitive (basis of choppers, SC networks).
  - `chopper-diff` — 4-gate differential chopper/modulator.
  - `capbank` — TG-switched binary-weighted cap array (PGA cap-DAC); binary weighting
    is structural (`value=Cu`, `m=1/2/4`) since 2026-07-19.
  - `vcm-detector-simple` — resistive common-mode sense (moved out of `ideal/`
    2026-07-19: it is a structural R-pair, not a macromodel; consumers re-pointed).
  - `amp-single-ended-5t-{nmos,pmos}-input` — REAL 5T OTA error amps (diff pair +
    mirror load + tail, with an on-cell 2-diode bias string; no external bias pin).
  - `cmfb-output-amp-5t-{nmos,pmos}-input` (+ `-inv`) — REAL transistor-level CMFB:
    `vcm-detector-simple` + the 5T error amp. Same pin footprint and polarity
    convention as the ideal pair below (canonical `vcmfb = A·(sensed_CM − vref)`,
    `-inv` = `A·(vref − sensed_CM)`; pick by plant parity, B5 rule), so swapping a
    consumer between ideal and real CMFB is a pure symbol-path change.
- **`shared/ideal/`** — reusable **behavioral / ideal macromodels** (see
  [`../../_shared/IDEAL_AMP.md`](../../_shared/IDEAL_AMP.md)):
  - `ideal-amp-fully-diff` — Gm + finite-Rout fully-differential OTA macromodel.
  - `cmfb-output-ideal-amp` (+ `-inv`) — ideal CMFB error amp; canonical
    `vcmfb = A·(sensed_CM − vref)` / `-inv` = `A·(vref − sensed_CM)`; pick by plant
    parity (see `drawings/TODO_bio_afe_port.md` §B5).
- Each block keeps its headless netlist under `shared/simulation/` (or
  `shared/ideal/simulation/`).

## Referencing these from a schematic

Symbols resolve against `drawings/` on the xschem library path (added by
`drawings/xschemrc`, and by each landed entry's `pdk/<pdk>/schematic/xschemrc`), so
reference them with the `shared/`-relative path, e.g.:

```
C {shared/transmission_gate_pair.sym} ...
C {shared/ideal/ideal-amp-fully-diff.sym} ...
```

No family-dir prefix. Moving a block here therefore means rewriting its reference string
(`<family>/<block>` → `shared[/ideal]/<block>`) in **every** referencing `.sch`, including
landed `circuits/*/pdk/*/schematic/*.sch` — connectivity is unchanged (pure relocation).
