# corpora/analoggym-sensing-fe — reference corpus (index)

> **[REFERENCE]** — the AnalogGym "Sensing Front End" reference corpus. Provenance + license:
> [`PROVENANCE.md`](PROVENANCE.md).

The **decks live under `circuits/sfe_*/`** as first-class `kind: reference` circuits (plan D-9),
each with its own `circuit.yaml` + `README.md`, indexed in the top-level
[`catalog.json`](../../catalog.json). This directory is the **corpus-level provenance home**, not a
second copy of the decks.

These circuits are **not lowered to an open PDK and not simulated** by this DB — they target
proprietary FOUNDRY 180 nm BCD-HV + 65 nm PDKs (`DEVICE`/`DEVICE`), in a mix of Spectre and HSPICE.
The harness runs a reference-only Tier-0 on them and skips T1–T4.

## The six circuits

| `sfe_reference_core_library` | 26 sub-Vt reference / PTAT cores (`topology.txt`) |
|---|---|
| `sfe_ptat_sensor_2t` | 2-transistor PTAT sensor core **+ its testbench** |
| `sfe_ptat_classic` | Classic mirror-biased PTAT reference |
| `sfe_ptat_65_classic` | Classic PTAT core, 65 nm |
| `sfe_ptat_sized_variants` | Sized PTAT variants `ptat_1..4` |
| `sfe_smcnr_2stage_amp` | Single-ended 2-stage OTA readout amp **+ AC/TRAN testbenches** |

## Browse

```python
import json
cat = json.load(open("catalog.json"))
sfe = [c for c in cat["circuits"] if c["id"].startswith("sfe_")]
for c in sfe:
    decks = [p for b in c["references"] for p in b.get("dut", [])]
    print(c["id"], c["class"], "→", len(decks), "dut deck(s)")
```

Each circuit's `references` entry lists its `.scs` DUT decks; the HSPICE `.sp` testbenches and the
verbatim `*.orig.sp` originals sit alongside on disk (not simulated by this DB). Or just browse
`circuits/sfe_*/`.

## Re-import

There is no dedicated importer yet — the corpus was authored directly from the meta-repo snapshot
`external/AnalogGym-remainder/Sensing Front End/`. See [`PROVENANCE.md`](PROVENANCE.md) for the
exact upstream→DB file mapping, dialect handling, and de-duplication.
