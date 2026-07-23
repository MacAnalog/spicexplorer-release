# Measurement pitfalls: when a bench measures the wrong thing

A recurring failure mode in this database is a bench that returns a *plausible number* for a
circuit that is not doing the thing being measured. Two were found and fixed on 2026-07-20/21, and
they share one root cause, so they are documented together — the pattern is what generalises.

## The pattern

> A **level test alone cannot establish that a circuit is operating.** Rails, dead loops and cut-off
> devices all produce output voltages, and those voltages routinely land inside the window a
> threshold-based metric is checking.

Every bench that asks "is the output where I expect?" also needs to ask **"is the circuit actually
active?"** — an *activity criterion*. In both cases below the activity test is a **slope**:

| quantity | level test | activity test | why slope works |
|---|---|---|---|
| amplifier ICMR | `\|vout - vin\| <= VTRACK` | `\|dvout/dvin - 1\| <= SLOPE_TOL` | a tracking follower has slope 1; a railed output has slope 0 |
| LDO dropout | `\|vout - VOUT_NOM\| <= VREG_TOL` | `\|dvout/dvin\| <= REG_SLOPE_MAX` | a regulating output is flat vs vin; a railed one follows it with slope 1 |

Slope is preferable to a "keep N mV off the rail" margin because it stays correct for rail-to-rail
parts: an RRIO buffer genuinely tracking at 50 mV has slope 1 and survives a slope test, but a
fixed rail-exclusion margin would wrongly reject it.

## Case 1 — amplifier ICMR measured rail coincidence

`_shared/classes/amplifier/testbench-templates/linearity*.spice` tested only
`|vout - vin| <= VTRACK` over a buffer-connected DC sweep. Below the input pair's turn-on the
output is pinned at a rail — but if `vin` is near that same rail, `|vout - vin|` is small **by
coincidence**, and the dead region scores as tracking. Those points are *contiguous* with the real
band, so a widest-contiguous-run scan cannot reject them either.

Measured on `amp_033_ti_ldo_ref_selfbias` (gf180mcu, 3.3 V, VTRACK 50 mV): for vin = 0..0.05 V the
NMOS pair is off and vout sits at ~0, yet `verr = vin <= 50 mV`, so the scan reported a **3.23 V
ICMR on a 3.3 V supply** — physically impossible. `amp_032` showed the same artifact at the top
rail (output railed high while vin walked up to VDD).

The in-deck implementation was *also* wrong independently: `meas dc ... WHEN verr=VTRACK CROSS=1`
finds the band **exit** on a DUT that already tracks at vin=0, so the CROSS pair returned the
complement of the real band — it read `amp_022_fer_two_stage` as 0.105 V against a true 1.400 V.

Fixed in three places so both lanes agree: `spicexplorer_core.measurements.waveforms.icmr_band`
(gains `slope_tol`, default 0.1; `None` restores legacy), the `dc` recipe kind in `registry.py`,
and both `linearity` templates (an in-deck contiguous-run scan mirroring the registry).

## Case 2 — LDO dropout rewarded a dead pass device

`_shared/classes/ldo/testbench-templates/dropout.spice` did:

```
meas dc vin_at WHEN v(vout)=${VOUT_THRESH} RISE=1
let v_dropout = vin_at - ${VOUT_THRESH}
```

"when does vout first rise past a threshold" — which cannot distinguish regulation from a pass
device stuck fully on. When the loop is dead, `vout` simply follows `vin`, crosses `VOUT_THRESH` at
`vin ~ VOUT_THRESH`, and the bench reports a dropout of **~0**. A completely broken regulator scores
a perfect number, and it fails *optimistically* — the dangerous direction.

This green-lit a real candidate. A resistor-biased variant of `ldo_005_buffered_ref` reported
dropout **0.090 V** (against 0.490 V for the working design) while actually railing below ~3.1 V —
`vout` was 2.59 V at `vin` 2.6 V. Only `line_reg` (1.185 V) caught it. Post-fix the ranking inverts
correctly: working design 0.550 V, railed variant 1.417 V.

New bindings `VOUT_NOM` / `VREG_TOL` / `REG_SLOPE_MAX`; `VOUT_NOM` resolves from the datasheet's
`default_conditions.vout`, the other two have defaults in `assemble.py`, so no per-circuit edits
were needed. The legacy `VOUT_THRESH` binding is unused — a threshold alone is what was wrong.
The bench now returns **NaN** when the sweep never reaches regulation, rather than fabricating a
number from a circuit that never worked.

## Cross-lane consistency

A second, independent defect surfaced alongside case 1 and is worth stating separately, because it
is a *plumbing* bug rather than a physics one.

`analog-db run` / `verify --tier 3,4` / `scoreboard` resolve a datasheet `extract: {meas: X}` by
treating `X` as a **string key into ngspice stdout scalars** (`ppa.metric_values` ->
`runner.parse_measures`). They never call the platform measurement registry — nothing under
`spicexplorer_analog_db/` imports `spicexplorer_core.measurements`. Sibling extract keys such as
`vin:` / `vtrack:` are silently dropped. The optimizer lane
(`spicexplorer.backends.analog_db.TestbenchRun.evaluate`) *does* build a real recipe.

So the two lanes could report **different numbers for the same deck**. Until `ppa.metric_values` is
routed through the registry (which additionally requires `run_circuit` to retain the `.raw` it
currently discards), any metric whose definition lives in the registry must have an equivalent
in-deck implementation, and the two must be kept in step. Both fixes above were done that way and
cross-checked numerically:

- ICMR: ngspice scan vs Python registry agree exactly (amp_033 3.000 V, amp_032 0.000 V), and the
  in-deck contiguous scan was validated against a Python reference on amp_001_5t (0.9200),
  amp_022 (1.4000) and amp_033 (3.2300).
- A `vecmin`/`vecmax` mask over the in-track set is **not** an acceptable shortcut: it silently
  merges disjoint bands (amp_022 -> 1.500 V vs a true 1.400 V). A run-length scan is required.

## Checklist for a new bench

1. What does this number mean if the circuit is **dead**? If that value is inside the passing
   window, the bench is unsafe.
2. Is there an activity signal (slope, current, an operating region) that distinguishes working
   from not-working? Prefer it over a rail-exclusion margin.
3. Degrade to **NaN**, never to a plausible-looking default.
4. If the metric also exists in the platform registry, implement both and check they agree
   numerically on at least one real circuit — see "Cross-lane consistency".
