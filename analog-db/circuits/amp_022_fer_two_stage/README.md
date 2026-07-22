# amp_022_fer_two_stage — classic Miller two-stage opamp (PMOS input)

**Promoted** from the `ferrosim_two_stage_opamp` reference entry (Arcadia-1/ferrosim, MIT).
Class `amplifier` (existing), **ibias-port convention** (`vdd vout vinp vinn ibias vss`, as
amp_001/amp_018).

PMOS input pair + NMOS mirror load, PMOS tail and second-stage current-source load off one
PMOS bias diode, NMOS common-source second stage, 2 pF Miller cap. The upstream deck bias-
references the PMOS diode with an external ideal *sink*; the promotion adds an NMOS
diode+mirror front-end (XMBD/XMBS, +2 devices) so the class's vdd→ibias convention drives it —
documented normalization, same trick as dp_001's mirror tail. Upstream m-ratios (3:3:17
bias:tail:load, 2:24 mirror:CS) are preserved so the current split matches the source design.

- **Open-PDK bindings:** `ihp-sg13g2`, `sky130` (1.5 V, IBIAS 20 µA, VCM 0.6 — PMOS input).
- `gf180mcu` binding added via `analog-db add-binding --from ihp-sg13g2` (untuned transfer; T3/T4 sim-smoke passes).
- **Licensed-PDK binding:** `tsmc-n65` (CRN65 low-Vt core: `nch_lvt`/`pch_lvt`). **NDA-clean** —
  the kit is *not* vendored; `pdk/tsmc-n65/corners.yaml` names only generic corner labels
  (`tt/ss/ff/sf/fs`) against a neutral wrapper `tsmc_n65_models.scs` that the operator supplies at
  simulation time (mapping `tt→tt_lvt`, …), resolved against `model_lib_root`. It runs through
  **Spectre via the virtuoso-bridge**, not open-PDK ngspice, so `analog-db run`/`verify --sim`
  skip it by design (no `_NATIVE_PDK` entry); Tier 0-2 offline verification still covers it.
- **Analyses:** `ac_open_loop` (via **ac_open_loop_biaswrap_ibias** — a fixed-VCM open loop
  rails a two-stage's output), `dc_op`, `noise`, `tran_step` (universal templates).
- **Reference bindings:** original TSMC 28 nm + 65 nm ferrosim decks under `spectre/`.
- **Structure:** `find_subcircuits` → `dp.pmos.simple` (XM0/XM1), `cm.nmos.simple` (XM3→XM4 +
  XMBD→XMBS), `cm.pmos.simple` (XM7→XM5, XM7→XM6).

## Measured (tt, native ngspice-45, 1.5 V / 20 µA / 500 fF)

| metric | ihp-sg13g2 | sky130 |
|--------|-----------|--------|
| dc_gain (bias-wrapped) | 51.5 dB | 65.7 dB |
| UGF / PM | 20.9 MHz / 81° | 3.5 MHz / 87° |
| i_supply | 246 µA | 85 µA |
| t_settle (0.2 V, 2 mV band) | 38 ns | 2.6 µs |

**Spectre (tsmc-n65, tt_lvt, 27 °C, 1.2 V / 20 µA / 500 fF)** — open-loop AC through the
platform's `SpectreSimulator` (virtuoso-bridge) + engine-neutral Tier-1 metrics: **dc_gain
47.4 dB · UGF 18.0 MHz · PM 61°** (`spicexplorer` `tests/test_amp022_tsmc65_ac_live.py`). Lower
than the open-PDK bindings by design — CRN65 low-Vt cores have lower intrinsic gain at the same
sizing. (Not an ngspice column: TSMC is Spectre-only, run at its 1.2 V core rail.)

Same node, **Spectre noise** analysis (1 kHz–100 MHz) through the same engine-neutral Tier-1
registry (`inoise_total`/`onoise_total`): **integrated output-referred ≈ 813 µV · input-referred
≈ 210 µV rms** (`spicexplorer` `tests/test_amp022_tsmc65_noise_live.py`). Wide-band figures — the
input-referred integral is dominated by the high-frequency tail where the gain has rolled off.

Same node, **Spectre transient THD** — wired as a unity-gain follower, driven by a 100 mV / 1 MHz
sine, through the same engine-neutral Tier-1 registry (`thd`, the coherent-FFT `thd_from_waveform`,
a SPICE `.four` analogue): **THD ≈ 0.077 % (−62 dB), HD2-dominated**, at a fundamental of 99.7 mV
(loop gain ≈ 1) (`spicexplorer` `tests/test_amp022_tsmc65_thd_live.py`). A closed-loop follower well
below the ~18 MHz UGF, so loop gain suppresses distortion.

**Bench-validation pass (2026-07-09, tt, in-library `run_circuit`)** — the full amplifier bench
suite on both lanes. ihp-sg13g2 (ngspice): CMRR 64.3 dB, PSRR+ 76.4 dB, ICMR 1.37 V,
THD 0.023 % (100 mV @ 1 MHz), IIP3 +23.6 dBV. tsmc-n65 (native Spectre, 1.2 V): CMRR 58.4 dB,
PSRR+ 96.6 dB, ICMR 1.07 V, THD 0.076 % (native PSS — matches the transient figure above),
IIP3 +17.9 dBV (two-tone 0.9/1.0 MHz on a 100 kHz-fundamental pss). Within each lane the
THD/IIP3 pair is internally coherent (lower distortion ↔ higher intercept).

**stb bench (2026-07-10, tsmc-n65 tt, native Spectre)** — the loop-gain probe (`stb` analysis
off the template's `VIPRB` marker): pm_loop 61.6°/60.8° (platform registry / Spectre's native
stb margin) vs the open-loop PM 60.9°, gain margin 8.06 dB on both routes, loop gain@DC
47.41 dB == the open-loop dcgain (β = 1). The bench's SKILL calculator set (the class
`spectre-benches.yaml` over `_shared/engines/spectre/calculator.yaml`) reproduced the THD/IIP3
figures exactly (0.0763 % / +17.93 dBV) — PSS+SKILL and Python-registry routes agree.

Regenerate: `analog-db generate --circuit amp_022_fer_two_stage`.
