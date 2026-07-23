# vref_001_vgs — WIP cross-PDK bindings (authored, not yet live-validated)

These sky130 + gf180mcu bindings for the ΔVth reference **lower correctly** (the multi-flavor
`devices.map` + circuitgraph flavor-aware lowering emit two distinct NMOS models per DUT), but each
hit a **per-PDK device-model** issue during live native sim — NOT the sim infrastructure (which was
fixed this round: `runner.py::_prepare_native_deck` gives gf180 its absolute `.include` resolution
and sky130 the slim-lib swap; both validated on known-good circuits). They are parked here (out of
the circuit's active `pdks:`) until the model issues are resolved, then move back under `pdk/`.

- **sky130** (`nfet_01v8` source + `nfet_g5v0d10v5` diode): slim-swap works (sim ~5 s, not ~60 s),
  but the 5 V IO device fails to instantiate at the sub-Vt bias. Try an all-1.8 V pairing instead —
  `nfet_01v8_lvt` (source) + `nfet_01v8` (diode) — same oxide → cleaner ΔVth; needs the slim lib
  regenerated with the `nfet_01v8_lvt` family (`tools/make_sky130_slim_lib.py --families …`).
- **gf180mcu** (`nfet_03v3` + a second flavor): single-flavor gf180 now sims natively (the
  `.include design.ngspice` fix). The second flavor (6 V / native) needs its `_tox`/stat params,
  which gf180 keeps in the `sm141064.ngspice` preamble (not loaded by a section-scoped `.lib`) —
  wire that param section before the device's corner section.
