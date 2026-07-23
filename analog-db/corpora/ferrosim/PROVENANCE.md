# ferrosim — provenance (reference corpus)

> **[REFERENCE]** — provenance record for the `ferrosim` reference circuits (plan D-9).

## Source & license

- **Upstream:** [`Arcadia-1/ferrosim`](https://github.com/Arcadia-1/ferrosim)
- **Author / attribution:** **Token Zhang** (`L-Trump` / `Arcadia-1`)
- **License:** **MIT** (owner decision, 2026-06-30 — consistent with the author's MIT sibling repos `netlist-crawler` / `analog-agent-workflow` / `analog-design-cli`). MIT license text reproduced below.
- **Imported via:** `sandbox/netlist-crawler/examples/ferrosim/` (the netlist-crawler vendored copy), on **2026-06-30**.
- **Byte/SHA manifest of the vendored upstream:** see the copied upstream index at [`upstream-README.md`](upstream-README.md).

Some decks are noted upstream as **"ported from `circuit-bench`"** (the `ferrosim_*` circuits sourced from `decks/ported/`). If the `circuit-bench` chain carries a distinct upstream license, that applies to those ported decks; confirm when reachable.

> **Hygiene (non-blocking):** when `Arcadia-1/ferrosim` is reachable, confirm its actual `LICENSE`
> file + the exact copyright holder/year and the `circuit-bench` provenance; update this file and the
> repo `NOTICE` only if either differs from MIT / Token Zhang.

## How these entries were imported

- Each upstream family became a **`circuits/ferrosim_<name>/` reference circuit** (`kind: reference`, plan D-9) — **not** a verifiable open-PDK circuit. The harness runs a reference-only Tier-0 (schema + provenance + deck-exists) and **skips T1–T4** (no lowering, no simulation here).
- The upstream directory layout for each family is **preserved verbatim** under the binding dir (`spectre/<node>/…`) so relative `include` paths stay intact (`netlist/dut|tb|runs/`, `netlists/`, `variants/`, monolithic ported decks).
- **Proprietary foundry paths are stubbed** as `${PDK_ROOT}` / `${CADENCE_ROOT}` / `${PROJECT_VA_ROOT}` placeholders (as received from the netlist-crawler vendored copy). No PDK is vendored.
- **Node labels:** the structured families and the SPICE-model decks originate from a **TSMC 28 nm** project (`crn28ull` / `tcbn28…` includes, `*_mac` device cards) → `node: 28nm`; the `decks/ported/*_65.scs` variants → `node: 65nm`; the process-agnostic **Verilog-A primitive demos** (`va_demo`, `va_decl_init`) carry no node (`spectre/va`). Node is a best-effort label, not a foundry assertion.

## The 30 imported circuits (122 decks)

| Circuit id | Class | Node(s) | Decks |
|---|---|---|---|
| `ferrosim_amp5t` | amplifier | 28nm | 5 |
| `ferrosim_bandgap_core` | reference | 28nm, 65nm | 2 |
| `ferrosim_biquad` | filter | 28nm | 16 |
| `ferrosim_bjt_cal` | characterization | 28nm | 1 |
| `ferrosim_bsimbulk_iv` | characterization | 28nm | 3 |
| `ferrosim_cap_meas` | characterization | 28nm | 1 |
| `ferrosim_common_source` | amplifier | 28nm, 65nm | 2 |
| `ferrosim_comparator` | comparator | 28nm | 14 |
| `ferrosim_differential_pair` | amplifier | 28nm, 65nm | 2 |
| `ferrosim_hyst_comparator` | comparator | 28nm, 65nm | 2 |
| `ferrosim_inbuf` | buffer | 28nm | 7 |
| `ferrosim_ldo` | ldo | 28nm, 65nm | 2 |
| `ferrosim_ldo_sample` | ldo | 28nm | 1 |
| `ferrosim_lfsr8` | digital | 28nm | 1 |
| `ferrosim_opamp` | opamp | 28nm | 8 |
| `ferrosim_pga_16step` | amplifier | 28nm | 1 |
| `ferrosim_refbuf` | reference | 28nm | 3 |
| `ferrosim_restrim` | trim | 28nm | 3 |
| `ferrosim_ring5` | oscillator | 28nm | 1 |
| `ferrosim_sampling_bts` | sampler | 28nm | 7 |
| `ferrosim_sar` | adc | 28nm | 18 |
| `ferrosim_sc_counter` | digital | 28nm | 3 |
| `ferrosim_sc_integrator` | filter | 28nm | 1 |
| `ferrosim_sc_ring` | oscillator | 28nm | 2 |
| `ferrosim_sc_sample` | sampler | 28nm | 1 |
| `ferrosim_source_follower` | buffer | 28nm, 65nm | 2 |
| `ferrosim_transistor_char` | characterization | 28nm | 3 |
| `ferrosim_two_stage_opamp` | opamp | 28nm, 65nm | 2 |
| `ferrosim_va_decl_init` | demo | (va) | 1 |
| `ferrosim_va_demo` | demo | (va) | 7 |

The authoritative machine index of every deck (per circuit, per binding, classified dut/tb/runs) is the top-level [`catalog.json`](../../catalog.json) `references` field.

## Post-import dispositions (updated 2026-07-15)

The table above is the **as-imported** record. Curated triage has since moved several entries out of
the flat `circuits/ferrosim_*` namespace (in addition to the 9 topologies promoted to first-class
`amp_*/buf_*/cmp_*/dp_*/gs_*/ldo_*` accessions on the 2026-07-05 triage). Current homes:

**Folded into a topology-first accession**
- `ferrosim_amp5t` → its TSMC-28 nm decks now live under
  [`circuits/amp_001_5t/spectre/28nm/`](../../circuits/amp_001_5t/spectre/28nm) as an extra
  `references` binding. `AMP_5T_D2S` is the **same topology** as `amp_001_5t`, so a separate
  accession would duplicate a topology (the registry is topology-first). The standalone
  `ferrosim_amp5t` circuit is retired.

**Reclassed `reference` → `voltage_reference`** (a real curated class replaced the placeholder
`reference` label; all stay `kind: reference`)
- `ferrosim_bandgap_core`, `ferrosim_refbuf` (and the non-ferrosim `sfe_reference_core_library`).

**Moved to [`reference-only/`](reference-only/)** — de-registered from `catalog.json` (these are not
analog topologies, so no class library applies; kept as pure browsable corpus):
- digital: `ferrosim_lfsr8`, `ferrosim_sc_counter`
- device characterization: `ferrosim_bjt_cal`, `ferrosim_bsimbulk_iv`, `ferrosim_cap_meas`, `ferrosim_transistor_char`
- Verilog-A language demos: `ferrosim_va_demo`, `ferrosim_va_decl_init`

Every remaining `ferrosim_*` family stays a registered `kind: reference` circuit under `circuits/`,
each now resolving to a real class library (`adc`, `filter`, `oscillator`, `sampler`, `trim`,
`voltage_reference`, `amplifier`, `buffer`) rather than a dangling class label.

## MIT License

```
MIT License

Copyright (c) Token Zhang (Arcadia-1/ferrosim)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

*(Copyright holder/year is reproduced as attributed pending upstream `LICENSE` confirmation — see the hygiene note above.)*
