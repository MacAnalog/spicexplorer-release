# amp_004_folded_cascode — Folded-cascode OTA (CORA benchmark design)

> ⚠️ Sizing under active revision (2026-06-13); sky130/gf180 figures below may be stale — see
> the committed `results/*.json` for current values. As committed: `ihp-sg13g2__tt.json` runs
> clean, but both `sky130__tt.json` and `gf180mcu__tt.json` still show a negative DC gain
> (mis-biased at the IHP-tuned geometry).

The CORA folded-cascode (legacy `examples/OTA/folded_cascode/`, alias `FOLDED-CASCODE-OTA`).
PMOS input pair folded into an NMOS mirror with NMOS+PMOS cascodes; ideal cascode bias
sources (`x_dut_vb1/2`). The CORA `opamp` subckt has **no enable network** — the abstract IS
the verbatim core with nets renamed to canonical names (see abstract/netlist.spice header).

- `pdk/ihp-sg13g2/testbenches.legacy/` — the three CORA benches **verbatim**
  (`cora_testbench{,_ac,_noise}.spice`; the legacy project_setup also referenced
  `_tran`/`_op` benches that were never committed — they remain absent, disabled).
- Port order is the CORA one: `vinn vinp vout vdd ibias vss` (vin-/vin+/out/vdd/ib/GND).
- NG_* fingers were frozen testbench params in the legacy setup — carried as
  `freeze: true` sizing variables.
- `optimizer/projection.yaml` → GENERATED `project_setup.yaml`.
- `pdk/sky130/`, `pdk/gf180mcu/` — retarget bindings (committed lowering-ready). Like the telescopic
  cascode, the IHP-tuned large-W cascode geometry doesn't yet yield a meaningful sky130/gf180
  baseline (sky130 hits invalid binned-model params; gf180 runs but mis-biases) — needs gm/ID
  re-sizing (Phase 6). See `_shared/PDK_SIM.md`.

## Migration verification (CORA → abstract): sim-confirmed equivalent

The abstract netlist was checked against the verbatim CORA bench by running the **same CORA AC
testbench harness** twice (ngspice-45 + IHP PSP103 OSDI), swapping only the subckt body:
A = CORA `opamp` (old `net*` names, PMOS listed **source-first**), B = the migrated canonical
netlist (`tail`/`foldp`/…, terminals reordered to true `d g s b`). Result:

- **DC operating point is bit-identical**: `v(out) = 1.248155 V` in both; every transistor's
  `gm`/`gds` matches to 6–7 significant figures (only 7th-digit solver round-off). Same topology,
  same bias — provably the same circuit.
- **AC metrics agree to <0.13 dB / <1.2%**: DC gain 44.12 → 44.23 dB (+0.11 dB), GBW 3.590 →
  3.592 MHz, 3-dB BW 46.4 → 45.9 kHz, phase margin unchanged (~105°).

The small residual is **not** a net-naming bug. It is the PMOS `s g d b` → `d g s b`
canonicalization (abstract/netlist.spice header): with all `gm`/`gds` equal, the only
direction-sensitive small-signal term left is the **body effect** (the cascode `R_out` boost is
`(gm + gmbs)·ro`, and `gmbs` is referenced to whichever terminal the model calls *source*). CORA's
source-first listing labelled the physical **drain** as "source" on the even-finger devices
(XM1/XM2/XM7/XM8, ng=8); the migrated netlist labels them physically correctly (PMOS source at the
higher-potential node, e.g. XM1 source = `tail`). **So the abstract netlist is the *more*
physically faithful of the two** — it is the same direction error netlist2tf's symbolic check
caught, now confirmed in SPICE.

> ⚠️ **Why this matters beyond a 0.1 dB curiosity.** PSP103 here is nearly d/s-symmetric, so the
> reversal cost only ~0.1 dB. That tolerance is **not** something to rely on. In shrinking nodes
> the body effect (and DIBL / drain-referenced output conductance) grows and is increasingly
> asymmetric, so a swapped source/drain can shift gain, `g_mb`, and `r_out` materially — and any
> direction-sensitive consumer (netlist2tf, hand hybrid-pi, gm/ID extraction) will be wrong, not
> just imprecise. **Authoring rule: keep transistor terminals in true `d g s b` with the source on
> the physically-correct (source) node, and only sign off against PDK models that model the body
> effect.** Don't treat "the simulator didn't care" as a guarantee — it won't hold at smaller
> geometries.
