import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ferrosim reference corpus — tour

    The DB registers **imported third-party circuits** in the same `circuits/` registry as its
    verifiable circuits, marked **`kind: reference`** (plan D-9). Most come from the **ferrosim**
    corpus ([`Arcadia-1/ferrosim`](https://github.com/Arcadia-1/ferrosim), author **Token Zhang**,
    MIT): Spectre decks written for a proprietary 28/65 nm foundry PDK.

    They are **not lowered to an open PDK and not simulated here** — the harness runs a
    reference-only Tier-0 (schema + provenance + deck-exists) and skips T1–T4. This notebook
    browses them from the manifest. It is fully **PDK-free** and needs no simulator.

    Provenance: [`../corpora/ferrosim/PROVENANCE.md`](../corpora/ferrosim/PROVENANCE.md). Of the 30
    imported ferrosim families, 9 were promoted to verifiable accessions, 8 moved to
    `corpora/ferrosim/reference-only/`, and `ferrosim_amp5t` was folded into `amp_001_5t`; the table
    below lists what stays registered.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The reference circuits

    `catalog.json` is the manifest. Every reference circuit carries a `references` list of
    foreign bindings, each indexing its `.scs` decks classified `dut` / `tb` / `runs` / `other`.
    """)
    return


@app.cell
def _():
    import pandas as pd

    from spicexplorer_analog_db import catalog, model, paths

    cat = catalog.build_catalog()
    refs = [c for c in cat['circuits'] if c.get('kind') == 'reference']


    def _deck_paths(c):
        return [p for b in c.get('references', []) for role in ('dut', 'tb', 'runs', 'other')
                for p in b.get(role, [])]


    df = pd.DataFrame([{
        'id': c['id'],
        'class': c['class'],
        'nodes': ', '.join(sorted({(b.get('node') or 'va') for b in c['references']})),
        'decks': len(_deck_paths(c)),
    } for c in refs]).set_index('id')
    print(f"{len(df)} reference circuits | {df['decks'].sum()} decks | "
          f"{df['class'].nunique()} classes")
    df
    return model, paths, refs


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One reference circuit, up close

    `ferrosim_inbuf` is a cascode input buffer with differential inputs and outputs, characterized
    upstream only by PSS runs from 0.1 to 8 GHz (its `README.md` says why it stays a reference). Its
    binding preserves the upstream `dut/` + `tb/` + `runs/` layout verbatim, so a testbench and its
    DUT travel together. The former `ferrosim_amp5t` is the same topology as `amp_001_5t`; its decks
    are now an extra `references` binding of that circuit.
    """)
    return


@app.cell
def _(model, refs):
    ckt = model.load_circuit('ferrosim_inbuf')
    print('kind:', ckt.kind, '| class:', ckt.klass, '| status:', ckt.status)
    print('reference-only (skips T1-4):', ckt.is_reference_only)
    print('provenance:', {k: ckt.manifest['provenance'][k] for k in ('source', 'designer', 'license')})

    entry = next(c for c in refs if c['id'] == 'ferrosim_inbuf')
    binding = entry['references'][0]
    print('\nbinding:', binding['dir'], '| tool:', binding['tool'], '| node:', binding['node'])
    for role in ('dut', 'tb', 'runs'):
        for p in binding.get(role, []):
            print(f'  {role:5s} {p}')
    return (binding,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Read a deck

    The decks are plain Spectre text (proprietary-PDK includes stubbed as `${PDK_ROOT}`
    placeholders). Catalog paths are db-root-relative — resolve them through `paths.db_root()`. The cell prints the DUT's `subckt` line and counts its
    instances by element type.
    """)
    return


@app.cell
def _(binding, paths):
    import re
    from collections import Counter

    dut_rel = binding['dut'][0]
    lines = (paths.db_root() / dut_rel).read_text().splitlines()
    print(dut_rel, f'({len(lines)} lines)\n')
    print(next(ln for ln in lines if ln.startswith('subckt')))
    instances = Counter(m[1] for ln in lines if (m := re.match(r'\s+([A-Z])\w* \(', ln)))
    print('instances by element:', dict(sorted(instances.items())))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why they're reference-only

    These decks target a proprietary foundry PDK we don't vendor — they can't be lowered to the
    open PDKs or simulated here. The verify harness reflects that: a reference circuit passes a
    reference-only Tier-0 and **skips** T1–T4.
    """)
    return


@app.cell
def _():
    from spicexplorer_analog_db import verify

    results = verify.run([0, 1, 2], circuit_ids=['ferrosim_inbuf'])
    for r in results:
        print(f'  [{r.status:4s}] T{r.tier} {r.check}'
              + (f'  — {r.reason}' if r.reason else ''))
    print('\nderived status:', verify.derive_status('ferrosim_inbuf', results))
    return


if __name__ == "__main__":
    app.run()
