# 5T-OTA multi-corner PVT sizing — worked example / pipeline proof

Reproducible demonstration of the **Phase-2 multi-corner PVT flow** end-to-end on the
5-transistor OTA (ihp-sg13g2), including the **constraint-first corner aggregation
(AGG-1)**. Config: [`project_setup_multicorner.yaml`](project_setup_multicorner.yaml).

Every optimizer trial runs the `{tb_ac} × {5 corners}` cross-product, scores each corner
on its own AC results, and collapses the five per-corner scores into one objective with
`score_aggregation: mean` under the constraint-first rule. Live on ngspice-45 + the IHP
sg13g2 PDK; the corner axis fans out (`parallel_sim: true`).

## The five corners (process × voltage × temperature)

| corner | process (cornerMOSlv.lib) | temp | VDD |
|---|---|---|---|
| `tt_27C_1V50` | `mos_tt` | 27 °C | 1.50 V |
| `ss_125C_1V35` | `mos_ss` | 125 °C | 1.35 V (−10 %) |
| `ff_m40C_1V65` | `mos_ff` | −40 °C | 1.65 V (+10 %) |
| `sf_85C_1V50` | `mos_sf` | 85 °C | 1.50 V |
| `fs_0C_1V50` | `mos_fs` | 0 °C | 1.50 V |

All corners select only `cornerMOSlv.lib` and override the same supply node `VDD`
(the enabled corners are **symmetric**, as multi-mode load-time validation requires).
Each corner is verified applied at runtime: `.lib cornerMOSlv.lib <section>` +
`.options temp=<T>` + `.param VDD=<V>`.

## Result 1 — the pipeline runs; corners genuinely differ

NGOpt, budget 20 (⇒ 100 AC simulations). Best design (trial 11), per-corner AC metrics:

| corner | DC gain (dB) | UGF | PM (°) | corner score |
|---|---|---|---|---|
| `tt_27C_1V50` | 27.49 | 166 MHz | 95 | 0.000 (pass) |
| `ss_125C_1V35` | 26.69 | 98 MHz | 94 | 0.000 (pass) |
| `ff_m40C_1V65` | 28.21 | 249 MHz | 95 | 0.000 (pass) |
| `sf_85C_1V50` | 26.04 | 126 MHz | 94 | 0.000 (pass) |
| `fs_0C_1V50` | 28.38 | 193 MHz | 96 | 0.000 (pass) |

The corner spread is physically correct: the fast/cold/high-V corner (`ff`) has the
highest UGF (249 MHz) and gain (28.2 dB); the slow/hot/low-V corner (`ss`) the lowest
(98 MHz, 26.7 dB). UGF varies **2.5×** across corners — corner application is not a no-op.
The optimizer's score trajectory converges from PVT-failing to all-corner-passing:
`−0.21 → −0.25 → … → −0.027 → 0.0` (feasible from trial 11 on).

## Result 2 — constraint-first aggregation averts corner masking (AGG-1)

Re-scoring that **same** design at a demanding `dcgain` target of **27.5 dB** (which the
corner spread 26.0–28.4 dB straddles) with rewards enabled, so passing corners earn
large positive scores:

| corner | DC gain | corner score |
|---|---|---|
| `tt_27C_1V50` | 27.49 | +32.84 (pass) |
| `ss_125C_1V35` | 26.69 | +19.27 (pass) |
| `ff_m40C_1V65` | 28.21 | +49.48 (pass) |
| `sf_85C_1V50` | **26.04** | **−0.008 (FAIL)** |
| `fs_0C_1V50` | 28.38 | +38.17 (pass) |

- **Naive `mean(all 5)` = +27.95** — strongly positive. The four passing corners' rewards
  bury the one failing corner, so the optimizer would be told this is an *excellent* design
  and could converge to a part that **fails PVT sign-off**.
- **Constraint-first (AGG-1) = −0.008** — correctly negative. Because one corner fails,
  only the failing corners' penalties aggregate; passing corners' rewards are discarded.
  This is the value the optimizer actually consumes.

That +27.95 → −0.008 gap is exactly the masking AGG-1 eliminates while keeping `mean` the
default (range specs like phase margin are two-sided, so a blanket worst-corner
scalarization is the wrong optimization objective — see
[`doc/PVT_plan.md`](../../../../doc/PVT_plan.md) §"SPECIFIED FIX — constraint-first corner aggregation").

## Reproduce

```bash
# from spicexplorer-platform/ (needs live ngspice + ihp-sg13g2 PDK)
uv run python examples/OTA/5t-ota/ihp-sg13g2/sizing/run_multicorner_5t.py
```

(The runner script and this write-up were produced with the multi-corner sweep + the
AGG-1 masking demo; per-corner numbers above are the actual live ngspice results.)
