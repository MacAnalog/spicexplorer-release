# amp_020_two_stage_miller_cmfb — Two-stage Miller OTA with resistive CMFB

A fully-differential, two-stage, Miller-compensated OTA: an NMOS input pair with
PMOS current-source loads (stage 1), driving two independent common-source
amplifiers (stage 2, one per side). Stage 1's load-gate bias is servoed by a
**passive resistive common-mode averager** instead of a diode connection — the
"common mode control" the source schematic is named for. The bias reference
current is generated **internally** (no external `ibias` port, unlike `amp_001_5t`).

## Layout
- `circuit.yaml` — the super-DSL manifest (identity, class, ports, pdks, analyses).
- `datasheet.yaml` — spec/metric sheet (cace_format 5.2 superset).
- `abstract/netlist.spice` — **AUTHORED** PDK-neutral source of truth (`nmos`/`pmos`
  tokens, `x_dut_*`/passive sizing symbols), parameterized from the source schematic.
- `abstract/topology.cgraph.json` — **GENERATED** by circuitgraph (`analog-db generate`).
- `pdk/ihp-sg13g2/` (native) + `pdk/sky130/`, `pdk/gf180mcu/` (via `add-binding`): each has
  `devices.map.yaml`, `sizing.yaml`, `corners.yaml`, `netlist.spice` (**GENERATED** lowered).
- `pdk/ihp-sg13g2/schematic/` — the original xschem source (`amp_020_two_stage_miller_cmfb.sch`,
  copied verbatim from `templates/OTA-Two-Stage/two-stage-miller-comp-common-mode-control.sch`)
  + its headless-xschem-rendered `.svg`, matching `amp_001_5t`'s schematic-provenance layout.
- `analyses/{ac_open_loop,dc_op,noise,tran_step}.yaml` — bind the amplifier class's new
  **`*_diff` templates** (see below), not the single-ended universal ones.
- `results/<pdk>__tt.json` — recorded `analog-db run` baselines for all three PDKs.

## Provenance
Netlisted headlessly from `templates/OTA-Two-Stage/two-stage-miller-comp-common-mode-control.sch`
(xschem, Stefan Schippers) against the vendored IHP sg13g2 PDK symbol library:
```
docker run --rm -i spicexplorer-spice-base:local bash -lc \
  'XSCHEM_LIBRARY_PATH=/opt/pdk/ihp-sg13g2/libs.tech/xschem:/opt/xschem_library:/opt/xschem_library/devices:. \
   xschem -x -q -n -s -o . two-stage-miller-comp-common-mode-control.sch'
```
The resulting flat netlist (13 devices, ports `vinp vinn voutp voutn VDD VSS`) was then
**parameterized** into `abstract/netlist.spice`: every device/passive that the source
schematic sized identically (min-size placeholders) got its own `x_dut_*`/passive sizing
symbol, grouped by functional role (input pair, stage-1 load, stage-2 pull-up/pull-down,
bias reference, Miller R-C, CM-servo R-C) rather than by instance.

## Why this needed new class templates
Every existing amplifier-class SPICE template (`ac_open_loop`, `dc_op`, `noise`,
`tran_step`) assumes a single-ended `vout` port, and most assume an external `ibias`
pin. This circuit has neither: it's genuinely differential-output (`voutp`/`voutn`) with
an internally self-generated bias reference. Four new class templates were added —
`ac_open_loop_diff`, `dc_op_diff`, `noise_diff`, `tran_step_diff` (registered in
`_shared/classes/amplifier/metrics.yaml`) — following the exact precedent set by
`ac_open_loop_biaswrap` (a distinct template file wired in via each `analyses/<id>.yaml`'s
`template:` field, while the analysis `id` stays the canonical one). They're reusable by
any future differential-output, self-biased circuit.

`ac_open_loop_diff`/`noise_diff`/`dc_op_diff` drive the DUT **directly** (matched
`vinp=vinn=VCM` DC inputs, true ±half differential AC drive) — no AnalogGym-style
Lfb/Cin bias-wrap. That trick exists because a single-ended amp with *no* internal
output feedback has an output DC point that's undefined by open-loop gain alone; here
the topology is genuinely symmetric, so matched inputs give a well-matched output
**offset** (`vos` measures ~0, essentially SPICE floating-point noise) regardless of
gain — there's no asymmetry for the gain to amplify into a rail. `tran_step_diff` closes
one feedback path (`vinn <- voutp`) deliberately, to measure real closed-loop settling.

## A known limitation: output common-mode centering
Stage 1's internal nodes are CM-servoed by the resistive network (R3-R6), but **stage 2
has no CMFB of its own** — `voutp`/`voutn`'s common-mode level is a knife-edge balance
between the (fixed-current) NMOS pull-down mirror and the PMOS pull-up's drive strength.
A device-width sweep on `dc_op` (`vocm = (v(voutp)+v(voutn))/2`) was used to hand-pick
`x_dut_pfet_out_w` per PDK so the *nominal typical-corner* bias sits near mid-supply
(~0.75 V of 1.5 V) on all three PDKs — but this is inherently **not robust to real device
mismatch** (a production design would need genuine output CMFB, or careful trimming).
Treat the current sizing as an unsized-but-functional floor, same spirit as the other
circuits' unoptimized starting points — a future gm/ID sizing pass is the real fix.

## Regenerate
```
analog-db generate --circuit amp_020_two_stage_miller_cmfb --all   # netlists/cgraph/raw/ decks/catalog
analog-db verify --circuit amp_020_two_stage_miller_cmfb --tier 2  # Tier 0-2 (schema/xref/generation/assembly)
analog-db run --circuit amp_020_two_stage_miller_cmfb --pdk ihp-sg13g2 --docker-image --write
```
