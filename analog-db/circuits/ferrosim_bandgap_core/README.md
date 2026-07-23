# ferrosim_bandgap_core — Bandgap core (ferrosim, ported from circuit-bench)

**kind: reference** (plan D-9) — imported proprietary-PDK Spectre circuit. Indexed for reference/eval; **not lowered to an open PDK and not simulated here** (reference-only Tier-0, skips T1–T4).

- **Source:** [`Arcadia-1/ferrosim`](https://github.com/Arcadia-1/ferrosim), imported via `netlist-crawler`. Author: **Token Zhang**. License: **MIT** (see repo `NOTICE` + [`../../corpora/ferrosim/PROVENANCE.md`](../../corpora/ferrosim/PROVENANCE.md)).
- **Class:** `voltage_reference` (reclassed 2026-07-15 from the placeholder `reference` label) · **decks:** 2 `.scs` file(s), upstream layout preserved verbatim.

## Bindings

| Binding | Tool | Node |
|---|---|---|
| `spectre/28nm` | spectre | 28nm |
| `spectre/65nm` | spectre | 65nm |

Proprietary-PDK includes are stubbed as `${PDK_ROOT}`/`${CADENCE_ROOT}` placeholders; open in a Spectre environment with the real PDK bound.

## Promotion status (2026-07-05 triage): stays reference — BJT not lowerable

The Brokaw-style core is built around **npn BJTs (Q0/Q1, 1:8)**, and circuitgraph's device
model has no BJT/diode `DeviceType` (MOS/RES/CAP/IND/V/I/SUBCKT only), so the abstract-netlist
-> `to_netlist(pdk=...)` lowering cannot represent it. Adding a BJT kind is a
spicexplorer-platform (circuitgraph) change, out of scope for the analog-db repo. Open-PDK
equivalents exist when that lands: sky130 `sky130_fd_pr__pnp_05v5` / ihp `npn13G2`.
