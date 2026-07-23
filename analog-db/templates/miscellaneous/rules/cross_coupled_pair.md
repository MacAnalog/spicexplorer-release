# Cross-Coupled Pair (`cc`)

> **Family/class:** `cross_coupled` · **Polarity:** nmos / pmos ·
> **Roles emitted:** currently `differential_pair` (**WIP** — no dedicated role yet)
> **Sources:** Massier 2008 (eqs. 37–38) · GENIE-ASI (cross-coupling cue)

A Level-1 building block that acts as a **negative resistor** (e.g. a VCO tank) or forms a
simple two-transistor latch/memory. Its defining property is symmetry between two identical,
mutually coupled transistors. Layout follows [design-rules index](../../README.md).

## 1. Function

Present a negative resistance (VCO) or bistable latch. Function depends purely on the two
halves being identical, not on holding any particular operating region.

## 2. Structure & recognition

- Two same-polarity MOSFETs with **each gate connected to the other's drain** (the cross
  coupling) — a symmetric two-cycle in the graph.
- GENIE-ASI treats cross-coupling as a diode-configuration-like cue when identifying **load
  parts** (grouped with diode-connected devices in its generated instructions).
- **WIP caveat:** the matcher currently assigns cross-coupled pairs the `differential_pair`
  structural role (no dedicated `cross_coupled` role exists yet) — a known follow-up noted
  in the miscellaneous manifest.

## 3. Sizing rules

Symmetry only — **no electrical (bias-region) rules of its own** (Massier eqs. 37–38):

| Rule | Constraint | Purpose |
|---|---|---|
| **FG1** | $l_1 = l_2$ | Symmetry (equal length) |
| **FG2** | $w_1 = w_2$ | Symmetry (equal width) |

## 5. Design intuition & trade-offs

The pair carries only geometric symmetry rules because its function (a symmetric negative
resistance / latch) depends entirely on the two halves being identical, not on keeping a
particular operating region — contrast the differential pair, which adds electrical
constraints ($v_{ds}$, $v_{gs}$ limits) to preserve a linear transfer.

## 6. Template mapping

- **Manifest:** `examples/analog-db/templates/miscellaneous/manifest.yaml` — the file's
  top-level `family` is `differential_pair`; the two `xc.*` entries carry per-entry
  `family: cross_coupled`.
- **WIP:** dedicated `cross_coupled` structural role not yet emitted — devices currently
  labeled `differential_pair`. Adding the role is the tracked follow-up.
