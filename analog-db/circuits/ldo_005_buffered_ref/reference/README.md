# Original design sources — ldo_005_buffered_ref

Verbatim copy of the xschem design tree this circuit was imported from
(`spicexplorer-workspace` meta-repo, `external/conceptual_LDO_design/ti-ldo/`,
first-party MacAnalog material; GF180MCU-native, TI application-note
architecture). Kept for reference/provenance — nothing here is consumed by the
harness; the DB's runnable realization lives in `../abstract/netlist.spice` +
`../analyses/`.

- `ldo/ldo.sch` + `ldo.sym` — the top-level LDO (`ref_amp` -> `lpf_rc` ->
  `error_amp` -> PMOS pass device); **the imported source of truth**.
  `ldo/ldo_two_r.sch` is the same topology with fixed instead of parameterized
  sizing (not imported separately).
- `ref_amp/` — the reference-buffer 5T OTA (+ `ref_amp_real_current_source`
  variant) and its symbol.
- `error_amp/` — the error amplifier (12+ transistor cascoded-mirror
  implementation, "Error Amplifier Implementation - TI LDO Paper") + its own
  per-block testbenches (`error_amp_tb*.sch`: ac / loopgain / noise / tran) and
  a diode-connected variant; `foldded_cascode_pmos_input` is an alternative
  amp under evaluation in the source project (also in `gen_amps/`).
- `lpf/` — the reference RC low-pass filter + its AC testbench.
- `testbench/dc_trans_tb.sch` — the top-level DC + transient testbench.
- `pictures/TI_LDO_system_architecture.png` — the source project's own
  architecture diagram.
- `xschemrc` — the source project's xschem configuration (gf180mcu paths).

Excluded on purpose: the source tree's `simulation/` output caches (`.raw`
waveforms and pre-baked `.spice` flattens — one of which, `ldo/simulation/
ldo.sch/ldo.spice`, was found to be **stale** relative to the current `.sch`
sources during import; see "Provenance" in `../README.md`) and editor
`.metadata/`.

Note the DB realization intentionally reuses a proven 5T shape for both amp
stages rather than byte-cloning the larger cascoded internals here — it matches
this design's *architecture* (buffered+filtered reference), not its transistor
count. The full 12T error amplifier **is** imported standalone as
[`amp_019_ti_ldo_error`](../../amp_019_ti_ldo_error/) (amplifier class), decoded from
`error_amp/error_amp.sch` in this tree.
