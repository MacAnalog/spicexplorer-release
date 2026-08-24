# sfe_reference_core_library

> **[REFERENCE]** `kind: reference` — imported AnalogGym "Sensing Front End" decks. NOT lowered to an
> open PDK and NOT simulated by this DB (proprietary 180 nm). See the corpus
> [`PROVENANCE.md`](../../corpora/analoggym-sensing-fe/PROVENANCE.md).

A library of **26 self-biased sub-threshold voltage-reference / PTAT temperature-sensor cores**,
each a 2–7-transistor 3-terminal cell `(GND VDD VOUT)`. These are topology-exploration variants
(ZVT/HVT devices, substrate-tie tricks); the upstream design notes are in Chinese and preserved
verbatim in the deck.

## Decks

- `spectre/180nm/netlist/dut/topology.scs` — the master library (verbatim `topology.txt`), all cells:
  `front_end_{11_6T, 11_7T, 17_4T, 17_4T_b, 20_4T, 20_4T_body, 22, 22_2T, 22_3T, 24_2T, 24_6T, 25_6T,
  28_4T, 28_4T_VA, 31_3T, 33_3T, 33_4T, 41_2T_1, 41_2T_2, 41_2T_3, 42_1_2015_REF, 42_2_2015_REF,
  43_4T_1, 43_4T_2, 4_2pmos, 4_2pmos_b}`.
- `spectre/180nm/netlist/other/` — four standalone single-cell exports (`front_end_11_6T`, `25_6T`,
  `31_3T`, `42_2_2015_REF`) that are byte-identical to cells already in `topology.scs`, preserved
  verbatim per the "nothing left behind" import rule.

## Notes

- `topology.scs` defines `front_end_28_4T_schematic` **twice** — a genuine upstream name collision
  (the two differ only in one PMOS bulk connection: `M3` bulk tied to `VDD` vs. to `net12`). Both
  are kept verbatim; a consumer that flattens the whole file must disambiguate them.
- Format is **Spectre** (`subckt … ends`, parenthesised nodes) — not ngspice-native.

## Promotion status (2026-07-05 triage): stays reference — multi-topology survey corpus

This entry is a **library of four alternative sensing-front-end cores** (plus a topology index),
not one circuit: promoting it would need one accession id per core. The individually promoted
PTAT cores (tsn_001 2T, tsn_002 classic, tsn_003 4T cross-coupled) already cover the family's
promotable members; the remaining schematics stay here as a survey corpus until someone needs
one as a first-class entry.
