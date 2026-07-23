# Original design sources — ldo_004_basic_pmos

Verbatim copy of the LTspice sources this circuit was imported from
(`spicexplorer-workspace` meta-repo, `external/conceptual_LDO_design/ltspice/`,
first-party MacAnalog material). Kept for reference/provenance — nothing here is
consumed by the harness; the DB's runnable realization lives in
`../abstract/netlist.spice` + `../analyses/`.

- `LDO_basic.asc` / `LDO_basic.asy` — the design itself: an ideal behavioral
  op-amp (LTspice `UniversalOpAmp`, `Avol=400000 GBW=10Meg Vos=0`) driving a
  PMOS pass device through a resistive feedback divider. The DB circuit is the
  minimal *real-transistor* equivalent of this (circuitgraph has no VCVS/`E`
  support — see `../README.md`).
- `Noise_6p38..6p42.asc` — output-noise benches (`.noise v(vout)` + integrated
  output noise), stepping Vin / Iout / Cout.
- `PSRR_6p33..6p36.asc` — supply-rejection AC benches, stepping Iout / Vin / Cout.
- `Line Transient_6p27..6p28.asc` — time-domain Vin-step benches (peak-to-peak
  Vout deviation), at heavy/light load.
- `Load Transient_6p29..6p30.asc` — time-domain load-step benches.

The `6pNN` suffixes are figure numbers from the accompanying LDO literature the
conceptual study followed (see the study's `doc/` folder in the meta-repo:
TI "LDO Technical Review" / TI slyt194 / ADI PM LDO design note / Toshiba LDO
basics — third-party PDFs cited here rather than vendored).

These benches motivated two additions to the shared LDO class
(`_shared/classes/ldo/`): the `noise` template (integrated output noise) and the
`tran_line_step` template (time-domain line transient) — the class's DC
`line_regulation`, `psrr`, and `tran_load_step` templates already covered the
rest of this suite's methodology.
