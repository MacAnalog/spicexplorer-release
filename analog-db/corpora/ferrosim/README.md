# corpora/ferrosim — reference corpus (index)

> **[REFERENCE]** — the `ferrosim` reference corpus. Provenance + license: [`PROVENANCE.md`](PROVENANCE.md).

Most **decks live under `circuits/ferrosim_*/`** as first-class `kind: reference` circuits (plan D-9),
following the DB convention — each with its own `circuit.yaml` (topology metadata + `references`
bindings) and `README.md`, indexed in the top-level [`catalog.json`](../../catalog.json). This
directory is the **corpus-level provenance home**, not a second copy of the decks:

- [`PROVENANCE.md`](PROVENANCE.md) — source, MIT license text, import metadata, the full list of the 30 imported circuits (122 decks), and the **post-import dispositions** (fold / reclass / move).
- [`upstream-README.md`](upstream-README.md) — the vendored upstream index (per-file byte/SHA256 manifest) as received via `netlist-crawler`.
- [`reference-only/`](reference-only/) — imports that are **not analog topologies** (digital blocks, device-characterization benches, Verilog-A language demos) and so map to no class library. They are parked here as pure browsable corpus and **de-registered from `catalog.json`** (2026-07-15). See its [`README.md`](reference-only/README.md).

These circuits are **not lowered to an open PDK and not simulated** by this DB (they are proprietary
FOUNDRY 28/65 nm Spectre decks). The harness runs a reference-only Tier-0 on them and skips T1–T4.

## Use it

**(Re)import** (idempotent — never clobbers an existing circuit dir):

```bash
analog-db import-ferrosim --src <path-to>/ferrosim/tests   # authors circuits/ferrosim_* + rebuilds catalog.json
#                          [--no-catalog]                   # skip the catalog rebuild
```

`--src` is the ferrosim `tests/` directory (the one holding `decks/`, `va_demo/`, `sc_sample/`), e.g.
the `netlist-crawler` vendored copy. The importer is `importers/ferrosim.py`; the mapping (family →
circuit id / class / node bindings) lives in its spec tables.

**Browse** the corpus from the manifest (`catalog.json`):

```python
import json
cat = json.load(open("catalog.json"))
refs = [c for c in cat["circuits"] if c["kind"] == "reference"]           # registered kind:reference circuits (ferrosim_* still under circuits/, + sfe_*)
for c in refs:
    decks = [p for b in c["references"] for r in ("dut", "tb", "runs", "other") for p in b.get(r, [])]
    print(c["id"], c["class"], "→", len(decks), "decks")
```

Each circuit's `references` entry lists its `.scs` decks classified `dut` / `tb` / `runs` / `other`;
open any deck as text (they are **not** simulated by this DB). Or just browse `circuits/ferrosim_*/`.
