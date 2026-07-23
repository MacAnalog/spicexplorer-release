# ferrosim_refbuf — Push-pull reference buffer (ferrosim)

**kind: reference** (plan D-9) — imported proprietary-PDK Spectre circuit. Indexed for reference/eval; **not lowered to an open PDK and not simulated here** (reference-only Tier-0, skips T1–T4).

- **Source:** [`Arcadia-1/ferrosim`](https://github.com/Arcadia-1/ferrosim), imported via `netlist-crawler`. Author: **Token Zhang**. License: **MIT** (see repo `NOTICE` + [`../../corpora/ferrosim/PROVENANCE.md`](../../corpora/ferrosim/PROVENANCE.md)).
- **Class:** `voltage_reference` (reclassed 2026-07-15 from the placeholder `reference` label) · **decks:** 3 `.scs` file(s), upstream layout preserved verbatim.

## Bindings

| Binding | Tool | Node |
|---|---|---|
| `spectre/28nm` | spectre | 28nm |

Proprietary-PDK includes are stubbed as `${PDK_ROOT}`/`${CADENCE_ROOT}` placeholders; open in a Spectre environment with the real PDK bound.

## Promotion status (2026-07-05 triage): stays reference — multi-flavor device binding

The buffer mixes **three MOS flavors in one DUT** (`nch/pch_ulvt_mac` drive, `pch_18_mac`
thick-oxide bias) plus `cfmom_2t` finger-caps and geometric `rupolym` resistors. The lowering
pipeline binds ONE model per generic kind/polarity (`devices.map.yaml`), so ULVT-vs-1.8V
distinctions (which set the headroom design) cannot be expressed. Needs per-instance flavor
binding (a platform lowering feature) before an honest promotion is possible.
