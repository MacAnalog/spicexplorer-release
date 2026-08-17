# PAM-4 driver (2-bit current-mode DAC, SiGe HBT) — ported netlists + testbenches

Port of the **EIC-designer `lumped-broadband-driver` verified reference** —
a block-level replication of *Inac, Peczek, Gerfers, Malignaggi, "Inductorless
96 Gb/s PAM-4 Optical Modulators Driver in SiGe:C BiCMOS", EuMIC 2022* —
into the spicexplorer analog-db staging area. **First bipolar (HBT) circuit in
the ecosystem.** PDK: IHP SG13G2 (`npn13G2` VBIC HBT, `cornerHBT.lib`), no
OSDI needed.

Provenance: `~/code/EIC-designer/projects/lumped-broadband-driver/` (16/16
requirements verified, dual sign-off). The port reproduces the EIC golden
reference **bit-exact to the reported precision — zero delta on all 8
system metrics** (see `results/pam4_results.yaml` → `vs_eic_golden`).

## Three DUTs

The driver is factored into three standalone DUT subcircuits (`dut/`),
mirroring the paper's figures:

| DUT | Subckt | Contents | Paper figure |
|---|---|---|---|
| `lsb` | `pam4drv_lsb` | 1 differential-cascode gain cell + R_C + R_B | Fig. 2(a) |
| `msb` | `pam4drv_msb` | 2 identical gain cells in parallel + shared R_C/R_B | Fig. 2(b) |
| `pam4` | `pam4drv_pam4` | 1 LSB + 2 MSB cells current-summing into shared R_C | Fig. 1 |

Nominal (EIC-verified): `npn13G2 Nx=3`, 16 mA tail per cell (8 mA/device,
peak-f_T), R_E = 2.5 Ω/side, C_deg = 20 fF, R_C = R_B = 50 Ω/side,
V_casc = 3.25 V, V_CM = 1.9 V, VCC = 4 V.

DUT port convention: `... vcc vcasc vcmb bias` (single-input DUTs:
`inp inn outp outn ...`; pam4: `lsbp lsbn msbp msbn outp outn ... blsb bmsb`).
Tail currents are **VCCS-driven, 1 mA/V** from the `bias`/`blsb`/`bmsb`
ports, so the same DUT netlist serves the ramped-transient testbenches
(PWL 0→16 V) and the DC/AC testbenches (DC 16). Tail sources and input
terminations are ideal — block-level fidelity as in the EIC reference (no
bias mirrors, no pad parasitics; simulated BW is optimistic vs measurement,
as disclosed there).

## Layout

```
dut/            dut_{lsb,msb,pam4}.spice     DUT subcircuits
netlists/       tb_*.spice + .spiceinit      static, directly runnable decks
testbenches/    driver_lib.py                builders + runners + extractors
                run_verify.py                full characterization (tran + ac)
                run_eye.py                   48 GBaud PAM-4 eye + metrics
                dump_netlists.py             regenerates dut/ + netlists/
results/        <dut>_results.yaml, *.png    metrics + plots (committed)
schematics/     dut_*.sch/svg/png            xschem schematics (see below)
layout/         gen_layout.py + signoff/PEX  parameterized gdsfactory GDS
                                             (DRC+LVS PASS, kpex+sim loop —
                                             see layout/README.md)
notebooks/      01_schematic_sizing          executed case-study notebooks
                02_layout_in_the_loop        (jupytext .py sources + .ipynb):
                03_signoff                   sizing, layout/electrical co-opt
                                             with DRC/LVS/PEX/spice in the
                                             loop, and full pre/post-layout
                                             signoff (DC/tran/AC/eye) vs the
                                             paper + EIC specs
```

## Running

Static decks (from `netlists/`, where the `.spiceinit` lives):

```sh
export PDK_ROOT=$HOME/local/pdks PDK=ihp-sg13g2
cd netlists && ngspice -b tb_pam4_sparam_msb_1ghz.spice
```

Full characterization (needs numpy/matplotlib/pyyaml on the python path):

```sh
cd testbenches
python run_verify.py all      # or: lsb | msb | pam4
python run_eye.py
```

**`.spiceinit` is mandatory**: it sets the model `sourcepath` and
`set ngbehavior=hsa`. Without `hsa` the IHP models parse but the HBT
conducts **0 A silently**. The python runners write their own `.spiceinit`
into each run's temp dir (PDK resolved from `$PDK_ROOT/$PDK`, falling back
to `~/local/pdks/ihp-sg13g2`, then the platform-vendored
`docker/pdk/ihp-sg13g2`).

## Measurement methods — and the JPP-361 update

Every metric is computed by **two independent methods** and cross-checked:

1. **`tran` (golden, EIC-validated):** ramp-everything-from-0 (`tran … uic`
   with PWL supplies), single-tone sine probe, single-bin DFT (least-squares
   cos/sin projection) of the steady window. S21 as differential power-wave
   gain `2·Vout/Vsrc` into 50 Ω/side references (the paper's VNA convention);
   S11/S22 via `Z = V/I` at the port.
2. **`ac`:** plain `.op` + `.ac` with the same in-deck power-wave math
   (`tb_*_op_ac*.spice`), full sweep in one run (~30× cheaper).

**EIC finding JPP-361 ("the self-heating VBIC HBT does not converge in
ngspice `.op`/`.ac`/`.dc`") reproduces on ngspice-44 but NOT on ngspice-45:**
on ngspice-45 (KLU), single-device and full-driver `.op`, `.dc`, and `.ac`
all converge with self-heating enabled, and agree with the transient-DFT
golden numbers to ≤ 0.011 dB (LF gain), ≤ 0.01 dB (S11/S22 spot points) and
≤ 0.1 % (bias). Consequence for the optimizer case study: on ngspice-45 the
cheap `.ac` path is usable per-candidate, with the transient probes retained
as the method-independent check; on ngspice-44 use the transient probes only.

## Results (nominal, typical corner)

`pam4` (combined system) vs the EIC golden reference — all deltas 0.000:

| Metric | Value | Paper spec |
|---|---|---|
| LSB / MSB LF gain | 3.10 / 9.07 dB | 3.2 / 9.2 dB measured |
| 3-dB BW (LSB / MSB) | 70.0 / 68.5 GHz | ≥ 50 GHz (block model optimistic) |
| S11 (worst ≤ 32 GHz) | −10.87 dB | < −10 dB |
| S22 (worst ≤ 50 GHz) | −14.76 dB | < −10 dB |
| Power | 191.03 mW @ 4 V | ≤ 192 mW |
| Max diff swing | 2.92 Vpp | ≥ 2.1 Vpp |
| 48 GBd PAM-4 eye | RLM 0.975, ~265 mV eye openings | Fig. 5 |

Standalone cells (`lsb`/`msb` DUTs, new characterization): LSB 3.1 dB /
63.7 mW / S11 ≤ −16.4 dB to 32 GHz; MSB 9.07 dB / 127.3 mW / S11 ≤ −10.87 dB
— consistent with the paper's observation that LSB input reflection is lower
(half the input capacitance) and MSB dominates the S11 budget.

## Schematics (`schematics/`)

Generated with `spicexplorer-netlist2xschem` from the DUT netlists, then
hand-edited to follow the paper's figures: `dut_lsb.sch` (Fig. 2a),
`dut_msb.sch` (Fig. 2b), `dut_pam4.sch` (Fig. 1 top view with amp-block
symbols; presentation sheet — the flat connectivity-true sheet is
`dut_pam4_flat.sch`, and the authoritative netlist is always
`../dut/dut_pam4.spice`). Open with `xschem` from that directory (the local
`xschemrc` resolves the IHP `npn13G2` symbols via `$PDK_ROOT`); rendered
`.svg`/`.png` are committed alongside.

Tooling note: `netlist2xschem` gained an HBT symbol mapping for this port
(`npn13G2[l|v]` subckt primitives → `sg13g2_pr/*.sym`, in
`packages/spicexplorer-netlist2xschem/.../mapping.py`). The VCCS tail
(`G…`) is not ingested by the tool (no `G` prefix support yet) and was
drawn by hand with `devices/vccs.sym` in the edited sheets.

## Toward the TCAS-2026 case study

This port is step 1 (runnable netlists + validated metric extraction) of
the plan in `spicexplorer-tcas-2026/doc/pam4_driver_case_study_feasibility.md`.
Next: land as an analog-db circuit entry (`drv_001_pam4_sige_dac/`) with
`circuit.yaml`/`datasheet.yaml`, the §3 spec tier for the optimizer
(8 design knobs: Nx integer 1–10 with `I_C < 3·Nx mA` validity, tail 4–24 mA
log, R_E/C_deg log, R_C/R_B linear 25–100 Ω, V_casc, V_CM), and the HBT
device entry in the IHP PDK registry. The `bias`-port VCCS convention makes
the tail current a plain `.param` knob for the optimizer.
