# amp_001_5t — 5-transistor OTA (single-stage)

The canonical single-stage OTA: NMOS input pair, PMOS current-mirror load, NMOS tail
biased by an NMOS mirror reference. The **Phase-0 proof circuit** for the analog-DB schema
(plan `doc/plan_examples_db.md`).

## Layout
- `circuit.yaml` — the super-DSL manifest (identity, class, ports, pdks, analyses, optimize).
- `datasheet.yaml` — spec/metric sheet (cace_format 5.2 superset).
- `abstract/netlist.spice` — **AUTHORED** PDK-neutral source of truth (`nmos`/`pmos` tokens).
- `abstract/topology.cgraph.json` — **GENERATED** by circuitgraph (`analog-db generate`).
- `abstract/schematic.svg` — canonical visual (from analog-circuit-design `ota-5t.svg`).
- `pdk/ihp-sg13g2/` — a PDK binding (also `pdk/sky130/`, `pdk/gf180mcu/`, and the licensed
  `pdk/FOUNDRY-n65/` — NDA-clean `add-binding` transfer, Spectre-only, added with the
  bench-validation pass 2026-07-09): `devices.map.yaml`, `sizing.yaml`, `corners.yaml`,
  `netlist.spice` (**GENERATED** lowered), `schematic/` (xschem provenance; ihp only).
  The FOUNDRY-n65 `sizing.yaml` carries `analysis_params` (VDD 1.2 / VCM 0.45) — the live 1.2 V
  input tracking band is [0.20, 0.67] V, so the cross-PDK VCM 0.8 would kill every AC bench.
- `analyses/*.yaml` — the full amplifier bench suite: `ac_open_loop`, `ac_closed_loop`,
  `dc_op`, `noise`, `tran_step`, `psrr_vdd`, `cmrr_vcm`, `linearity` (ICMR), `thd`, `iip3`, `stb`.
- `project_setup.yaml` — optimizer projection (`extends: circuit.yaml`).

## Provenance
Derived from IIC-JKU / Pretl `analog-circuit-design` (`cace/voltage-buffer-ota.yaml`,
`xschem/ota-5t.*`), Apache-2.0. The abstract netlist is the clean 5T core; the IHP
implementation's enable/power-down network is intentionally **not** part of the abstract
topology (it is a PDK-implementation detail; see `doc/_shared/MIGRATION.md`).

## Measured (bench-validation pass 2026-07-09, tt)
Through the platform's in-library router (`run_circuit`, engine per the `sim_engine` marker):
ihp-sg13g2 (ngspice) — gain 29.8 dB / UGF 30 MHz / PM 61°, CMRR 29.7 dB, PSRR+ 29.7 dB,
ICMR 0.88 V, THD 1.62 % (100 mV @ 1 MHz), IIP3 −1.5 dBV; FOUNDRY-n65 (native Spectre, 1.2 V) —
gain 26.1 dB / UGF 32 MHz / PM 78°, CMRR 33.9 dB, PSRR+ 28.1 dB, ICMR 0.47 V, THD 1.30 %,
IIP3 +5.9 dBV (the ~26 dB is the LVT single-stage intrinsic-gain ceiling). stb bench (2026-07-10): loop PM 88.9° (≈ single-pole), gain margin honestly NaN on both the registry and Spectre's native stb-margin routes (the loop phase never reaches −180° in-band).

## Regenerate
```
analog-db generate --circuit amp_001_5t     # rewrites abstract/topology.cgraph.json + pdk/*/netlist.spice
analog-db verify --circuit amp_001_5t       # Tier 0 (schema + cross-ref + catalog determinism)
```
