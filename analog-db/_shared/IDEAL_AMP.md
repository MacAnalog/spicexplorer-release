# Baseline parameters for the ideal amplifier macromodel (owner decision, PR #37)

The behavioral fully-differential amplifier (`amp_028_ideal_fully_diff`; drawn
as `ideal-amp-fully-diff`: `Gm` VCCS + `Rout`/`Cout` + `Rin`/`Cin`) is the
standard **ideal-OTA leaf** for top-down composition (CMFB servos, RRL output
stages, early system models). Its five knobs get one of two BASELINE sets —
pick per role, override per-instance in the consuming entry's `sizing.yaml`:

| Knob | `ideal-ota` baseline | `servo-grade` baseline | meaning |
|---|---|---|---|
| `gm_val`   | `100u` S  | `100u` S | transconductance |
| `rout_val` | `10Meg`   | `100k`   | output resistance -> DC gain = gm*rout |
| `cout_val` | `1p`      | `100f`   | output cap -> dominant pole / UGF |
| `rin_val`  | `1e12`    | `1e12`   | differential input resistance (no `T` suffix — parse_value has none) |
| `cin_val`  | `10f`     | `10f`    | differential input cap |

- **`ideal-ota`** (gain 1000 = 60 dB, UGF ≈ gm/(2π·cout) ≈ 15.9 MHz): the
  default for signal-path modeling; amp_028's committed sizing defaults.
  Verified live: 60.0 dB / 15.5 MHz into the 50 fF bench load.
- **`servo-grade`** (gain 10 = 20 dB, pole ≈ 1/(2π·rout·cout) ≈ 16 MHz): for
  auxiliary loops (CMFB, RRL). Rationale — the CCIA landing showed an
  unclamped gain-1000 macromodel in a CM servo winds up to ±10s of volts on a
  50 mV error and can limit-cycle (~490 kHz observed); bounded low gain keeps
  the servo authority inside the rails and the loop dynamics benign
  (`drawings/DRAWING_REVIEW.md` §3). Used by `ia_001` (tuned to gain 5: rout_val 50k) and
  recommended for `cmfb_001_ideal_rsense_servo`-style servos.

**The macromodel is an ideal *OTA*, not an ideal op-amp** (finite `rout_val`,
current-source output — see the OTA/op-amp distinction in
`drawings/README.md`). An ideal *op-amp* leaf (buffered E-source output,
Rout ≈ 100 ohm) is not in the catalogue yet; add it as its own drawn block if
needed rather than abusing `rout_val` here.

Sign convention: `Gm voutn voutp vinp vinn {gm_val}` — current is pulled from
`voutn` into `voutp` for `v(vinp) > v(vinn)`, i.e. `voutp` follows `vinp`
(non-inverting mapping), matching a transistor diff pair + load.
