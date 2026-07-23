# ccia-01 testbenches (xschem)

Per-block bottom-up xschem benches for the **ccia-01** family (Hsu bandpass class-AB
CCIA). Same golden placement as ccia-02 (`devices/code.sym` code grid top-left, graph
boxes top-right, `COMMANDS` + launchers right, DUT centre). Generator:
`scratchpad/gen_ccia01_tb.py`.

> **ccia-01 is CONTINUOUS (no chopper), so AC benches are valid here** — unlike the
> ccia-02 chopper DUT (where `.ac` on the switched network is meaningless and is removed).
> `ia_001` / `amp_025` expose no `clk_*`/`phi*` ports, so the clocked-circuit guard
> (`assemble()` / verify Tier-0) does not fire.

| dir | DUT `.sch` | circuit | benches |
|---|---|---|---|
| [`two-stage-ota-core/`](two-stage-ota-core/) | `two-stage-ota-core.sch` | `amp_025_hsu_classab_ota` | ac_open_loop, dc_op, noise, tran_step, ac_cm_reg, tran_cm_kick |
| [`ccia-dut/`](ccia-dut/) | `ccia-dut.sch` | `ia_001_hsu_bandpass_classab` | ac_closed_loop, dc_op, noise, thd, ac_zin_diff |

`ccia-dut` is a self-contained cap-coupled CCIA (Cin/Cf ratio gain + pseudo-R DC servo +
internal biases); the bench just drives the differential input + rails + loads. The OTA
core exposes `Vb1/Vb2/Vb3` + `vcmfb_ref` ports, which the bench drives with DC.

## Global params the drawings need

The drawings reference these by bare name (`value=<name>`) rather than hardcoding, so the
bench `PARAMS_BENCH` block defines them (values = the entries' `sizing.yaml` defaults):

- `Cc=1p Rz=10k` — OTA Miller comp; `Cin=16p Cf=0.8p` — ia_001 cap-ratio feedback (gain 20).
- `gm_val=100u rout_val=10Meg rin_val=1T cin_val=10f cout_val=100f Rm=1Meg` — the shared
  **ideal-CMFB macromodel** knobs (`ideal-amp-fully-diff` + `vcm-detector-simple`, nested in
  `cmfb-output-ideal-amp-inv`). These must be **global** `.param`s — attaching them to the
  hyphenated ideal subckt *instance* is what ngspice-45 refuses; a global `.param` is fine.

## Sizing caveat — drawn at the PDK floor

The transistors are drawn at `w=0.15u l=0.13u` (min size), so these are **skeleton**
numbers, not spec (e.g. `ac_open_loop` ≈ −68 dB, `ac_closed_loop` ≈ −73 dB — mirrors
ccia-02's documented "−31.6 dB min-size" floor). The benches are the *harness*; they read
real once the drawing carries the entry sizing. Injecting sizing needs the drawing
parameterized first (the ccia-02 parameterization campaign) — a follow-up, not done here.

## Running one

```bash
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
cd drawings
xschem -n -s -q --rcfile "$PWD/xschemrc" -o <outdir> \
  ccia-01-YuPinHsu-bandpass-class-ab-output/testbenches/<dir>/<bench>.sch
cd <outdir> && ngspice -b <bench>.spice
```

All 11 netlist + simulate cleanly on native IHP sg13g2 (2026-07-22). `thd` uses ngspice's
`fourier` command (`four` is not available in this build).
