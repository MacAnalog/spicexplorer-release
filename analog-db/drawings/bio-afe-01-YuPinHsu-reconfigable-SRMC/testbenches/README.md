# bio-afe-01 testbenches (xschem)

Per-block bottom-up xschem benches for the **bio-afe-01** family (Hsu reconfigurable
SRMC biosignal AFE). Same golden placement as ccia-02/ccia-01 (`devices/code.sym` grid +
graphs + launchers). Generator: `scratchpad/gen_bio01_tb.py`.

> All benched blocks here are **continuous** (no `clk_*`/`phi*` ports), so AC is valid and
> the clocked-circuit guard does not fire. The *switched* SRMC filter itself is a separate
> case (see "Deferred" below).

| dir | DUT `.sch` | circuit | benches |
|---|---|---|---|
| [`SRMC-core-amp-w-cmfb/`](SRMC-core-amp-w-cmfb/) | `SRMC-core-amp-w-cmfb.sch` | `amp_031_srmc_core_cmfb` | ac_open_loop, dc_op, tran_cm_kick |
| [`PGA-ideal/`](PGA-ideal/) | `PGA-ideal.sch` | `ia_005_hsu_pga_ideal` | ac_closed_loop, dc_op |

Live-verified numbers (native IHP sg13g2, 2026-07-22):

- **SRMC-core-amp-w-cmfb** (the SRMC filter's core OTA + ideal-CMFB servo, biases internal):
  `ac_open_loop` **41.0 dB**, `dc_op` vocm **0.501 V** / i_supply **6.6 µA**, `tran_cm_kick`
  CMFB holds vocm at 0.501 V. This drawing is **optimizer-sized** (real numbers, not the
  min-size floor).
- **PGA-ideal** (ia_005, 3-bit binary-capbank programmable-gain amp): driven at gain code
  **111** (max), `ac_closed_loop` **18.0 dB**. It is an *ideal-amp macromodel* core
  (`ideal-amp-fully-diff`), so `dc_op` reports ~0 supply current and no CMFB-set output CM —
  that is the ideal cell's nature, not a bench fault. `ia_005` declares no analyses, so this
  bench set (closed-loop gain at a fixed code + operating point) was chosen.

## Global params the drawings need

Defined in each bench's `PARAMS_BENCH` (values = the entries' `sizing.yaml` defaults):

- ideal-CMFB macromodel: `gm_val=100u rout_val=10Meg rin_val=1T cin_val=10f cout_val=100f
  Rm=1Meg` (must be **global** `.param`s — attaching them to the hyphenated ideal subckt
  *instance* is what ngspice-45 refuses).
- caps: `Cc/Rz` (Miller), `Cin/Cf` (feedback), `Cu=1p` (capbank unit).
- capbank transmission-gate geometry: `tg_n_w/tg_p_w=0.18u tg_n_l/tg_p_l=0.13u` (PDK floor,
  deliberately not sized).

## Deferred (not benched here)

- **SRMC-core-amp-w-cmfb-5t** — the real sized-5T-CMFB variant has **no `.sym`** (top-level
  `.sch` only), so it can't be instantiated as a sub-DUT; and it's not accessioned yet
  (amp_032 candidate).
- **SRMC-ideal / SRMC** — the *switched* SRMC filter (series input switch duty-cycled at FS).
  It's a switched circuit, so AC is invalid; the right bench is transient. It has no landed
  circuit / declared analyses yet ("await the filter-class decision") — deferred until then.
- **ccia-ideal / afe-ideal** — blocked on the P4 composition composer.

## Running one

```bash
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
cd drawings
xschem -n -s -q --rcfile "$PWD/xschemrc" -o <outdir> \
  bio-afe-01-YuPinHsu-reconfigable-SRMC/testbenches/<dir>/<bench>.sch
cd <outdir> && ngspice -b <bench>.spice
```
