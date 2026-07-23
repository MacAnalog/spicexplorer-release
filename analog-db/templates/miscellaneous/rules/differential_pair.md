# Differential Pair (`dp`) & Differential Stage (`DS`)

> **Family/class:** `differential_pair` · **Polarity:** nmos / pmos ·
> **Roles emitted:** `differential_pair` (and `tail_current_source` for the tail device)
> **Sources:** Massier 2008 (eqs. 33–36) · GENIE-ASI (`DiffPair`)

The differential pair converts a $v_{gs}$ difference into a drain-current difference — the
input device of almost every op-amp. This note covers the pair (Level 1), its
cascoded/folded recognition variants, and the differential stage (Level 3) that wraps it
with a current mirror. Layout follows [design-rules index](../../README.md).

## 1. Function

Transform a gate-source voltage difference into a drain-current difference. Both transistors
work as `vccs`; the current-mirror FE/FG rules (equal $v_{ds}$, equal length) hold
analogously, plus symmetry (equal $W$ and $L$).

## 2. Structure & recognition

- Two same-polarity MOSFETs whose **gates connect to the circuit input nets** (manifest port
  roles `in_p` / `in_n`) and whose **sources are tied together** at a common tail node (`CM_tail`).
- Detected as a **dependent template** anchored on the tail: admitted when the tail lands on
  a detected mirror's `out` net (filtered by the template's `tail_sources` allow-list); a
  fallback admits a pair whose tail is driven by any rail-sourced MOS on its own supply.
- The device whose **drain sits on the `CM_tail` net** is labeled `tail_current_source`.
- **GENIE-ASI `DiffPair`** expands to three structural variants: `DifferentialPair`,
  `CascodedDifferentialPair`, `FoldedCascodeDifferentialPair`.

## 3. Sizing rules

Both transistors act as `vccs` (saturation) — see
[device roles (vccs/vcres)](../../device_roles.md).
Pair rules (Massier eqs. 33–36):

| Rule | Constraint | Purpose |
|---|---|---|
| **FG1** | $l_1 = l_2$ | Symmetry (equal length) |
| **FG2** | $w_1 = w_2$ | Symmetry (equal width) |
| **FE** | $\lvert v_{ds_2} - v_{ds_1}\rvert \le \Delta V_{ds_{max}(dp)}$ | Equal $v_{ds}$ → suppress systematic offset |
| **RE** | $\lvert v_{gs_2} - v_{gs_1}\rvert \le \Delta V_{gs_{max}}$ | Keep the transfer approximately linear |

## 5. Design intuition & trade-offs

The pair is an inherently matched, symmetric structure — the equalities $w_1=w_2$, $l_1=l_2$
come straight from requiring the two halves to behave identically at balance. The
$\Delta V_{gs_{max}}$ inequality bounds the differential input swing over which the
transconductance stays roughly constant.

**Differential Stage (`DS`, Level 3):** an arbitrary current mirror (any `CM`, see
[current mirrors](../../current_mirror/rules/current_mirror.md)) plus a `dp` — the pair
with its active-load mirror. `DS` produces **no new sizing rules of its own**; recognizing
the enclosing stage simply resolves the pair's role (the pair need not be flagged
"uncertain").

## 6. Template mapping

- **Manifest:** `examples/analog-db/templates/miscellaneous/manifest.yaml`
  (`family: differential_pair`), a **dependent** template anchored via `CM_tail` /
  `tail_sources`.
- Role emitted: `differential_pair`; the tail device gets `tail_current_source`.
- Cascoded / folded-cascode variants exist in the GENIE-ASI taxonomy; confirm coverage
  against the manifest before relying on them.
