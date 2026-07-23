# ferrosim_inbuf — Cascode input buffer (ferrosim)

**kind: reference** (plan D-9) — imported proprietary-PDK Spectre circuit. Indexed for reference/eval; **not lowered to an open PDK and not simulated here** (reference-only Tier-0, skips T1–T4).

- **Source:** [`Arcadia-1/ferrosim`](https://github.com/Arcadia-1/ferrosim), imported via `netlist-crawler`. Author: **Token Zhang**. License: **MIT** (see repo `NOTICE` + [`../../corpora/ferrosim/PROVENANCE.md`](../../corpora/ferrosim/PROVENANCE.md)).
- **Class:** `buffer` · **decks:** 7 `.scs` file(s), upstream layout preserved verbatim.

## Bindings

| Binding | Tool | Node |
|---|---|---|
| `spectre/28nm` | spectre | 28nm |

Proprietary-PDK includes are stubbed as `${PDK_ROOT}`/`${CADENCE_ROOT}` placeholders; open in a Spectre environment with the real PDK bound.

## Promotion status (2026-07-05 triage): stays reference — layout-extracted GHz buffer

The L1 cascode input buffer is a **28 nm layout-annotated deck** (per-device sa/sb/sd stress +
DFM parameters, `cfmom_2t` finger-caps, a VCM *bulk* rail) characterized upstream ONLY by
PSS/PNOISE runs at 0.1-8 GHz. ngspice has no PSS, the extracted geometry is meaningless on
130 nm open PDKs, and a DC/AC bench would not validate its actual (GHz) function — so an
open-PDK promotion would be dishonest. Kept as a reference topology + characterization corpus.
