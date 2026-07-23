# corpora/ferrosim/reference-only — de-registered corpus (not indexed)

> **[REFERENCE]** — ferrosim imports that are **not analog topologies**, parked out of the circuit
> registry. Provenance + license: [`../PROVENANCE.md`](../PROVENANCE.md).

These entries were imported from [`Arcadia-1/ferrosim`](https://github.com/Arcadia-1/ferrosim) (Token
Zhang, MIT) like the rest of the corpus, but they describe **no analog topology** — so no class
library (`amplifier`, `adc`, `filter`, …) applies to them. They were moved here on **2026-07-15** and
are **de-registered from [`catalog.json`](../../../catalog.json)**: the harness discovers circuits by
scanning `circuits/`, so nothing under this directory is loaded, verified, or indexed. Each still
keeps its original `circuit.yaml`, `README.md` and verbatim Spectre decks — this is a **park, not a
delete** — so any of them can be moved back under `circuits/` if a real use emerges.

| Circuit | Category | Why it has no class |
|---|---|---|
| `ferrosim_lfsr8` | digital | 8-bit LFSR — a digital state machine, outside the analog DB's remit. |
| `ferrosim_sc_counter` | digital | Programmable 4-bit counter — digital logic. |
| `ferrosim_bjt_cal` | characterization | A device calibration bench, not a circuit under test. |
| `ferrosim_bsimbulk_iv` | characterization | BSIM-Bulk NMOS/PMOS IV sweeps — model characterization. |
| `ferrosim_cap_meas` | characterization | A capacitance measurement bench. |
| `ferrosim_transistor_char` | characterization | gm/Id, DIBL, Ron device sweeps. |
| `ferrosim_va_demo` | demo | Verilog-A **language** primitive demos (diode/sqlaw/cswitch/…), not a circuit. |
| `ferrosim_va_decl_init` | demo | Verilog-A declaration/initialization language demo. |

To browse a deck, open it as text under `<circuit>/spectre/…` — none of these are simulated by the DB.
The registered `ferrosim_*` circuits that **do** carry a real class live under `circuits/ferrosim_*/`;
see the corpus index at [`../README.md`](../README.md) and the dispositions in
[`../PROVENANCE.md`](../PROVENANCE.md).
