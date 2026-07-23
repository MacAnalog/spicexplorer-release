# The PPA scoreboard — usage guide

> REFERENCE for `analog-db scoreboard` / `run --write` / `new-circuit` and the on-disk
> scoreboard contract. Design + decisions: meta-repo `doc/plan_scoreboard.md` (D-1…D-10).

## What it is

A per-circuit, per-PDK log of **design points**: each entry records one full sizing vector,
the measured analyses at every corner it has been run at, the datasheet-mapped canonical
metrics with spec verdicts, and a Power / Performance / Area rollup. It replaces the old
one-snapshot `results/<pdk>__<corner>.json` (absorbed 2026-07; the old snapshots became each
circuit's first entries).

```
circuits/<id>/scoreboard/
├─ baselines.yaml              # AUTHORED {pdk: design_id} — the named baseline per PDK
└─ <pdk>/<design_id>.json      # RECORDED entry, one per design point
scoreboard.json                # GENERATED global index (drift-guarded, Tier 0)
```

`design_id` = first 10 hex of sha256 over the canonical (circuit, pdk, sizing vector), with
values normalized numerically (`0.5u` ≡ `5e-07`) so formatting never forks identity. Same
design re-run at a new corner ⇒ the entry gains that corner. Different numbers (even a
rounding pass) ⇒ a different design point — see the telescopic cascode's two ihp points
(committed defaults vs the NEWCAS-2026 optimizer best).

## Recording

```bash
# run every declared analysis on a PDK and record the design point (host: use --docker-image)
analog-db run --circuit ldo_004_basic_pmos --pdk sky130 --docker-image --write

# another corner of the SAME design upserts into the same entry
analog-db run --circuit ldo_004_basic_pmos --pdk sky130 --corner ss --docker-image --write
```

The first recorded design point per (circuit, pdk) is auto-named the **baseline**. Re-point it:

```bash
analog-db scoreboard set-baseline --circuit amp_018_telescopic_cascode \
    --pdk ihp-sg13g2 --design d35babe5f9
analog-db generate --all        # refresh catalog.json + scoreboard.json afterwards
```

Programmatic recording (optimizer / RL campaigns) goes through the same seam:

```python
from spicexplorer_analog_db import model, runner, scoreboard
c = model.load_circuit("ldo_004_basic_pmos")
results = runner.run_circuit(c, "sky130", "tt", runner.base_image_runner())
scoreboard.record(c, results)                          # today's sizing.yaml defaults
scoreboard.record(c, results, sizing_override=params)  # a candidate the optimizer proposed
```

**Pruning policy (D-9):** commit baselines + Pareto members + hand-kept entries only. A bulk
campaign must not commit thousands of JSONs — record into a scratch checkout / keep candidates
out of git, and promote winners by recording them here.

## Reading

- `scoreboard.json` — the global `class × pdk × circuit × design-point` view. Each row carries
  the entry's PPA rollup, its spec pass/fail counts, `baseline: true|false`, and
  `pareto: true|false` (the non-dominated set over power ↓, active area ↓, and the class's
  directed headline metrics — deliberately **no scalar rank**, it's a tradeoff surface).
- `catalog.json` — each verifiable circuit carries `scoreboard.<pdk>` = its baseline's
  `{design_id, ppa, spec}`; enough for "smallest LDO on sky130 that passes its specs" without
  touching the entries.
- Entry `metrics.<corner>.<name>.spec` (`pass`/`fail`/`none`) is the datasheet-conformance
  data path (a future live Tier-4 reads exactly this).

## PPA definitions (D-7)

Declared per class in `_shared/classes/<class>/metrics.yaml`:

```yaml
ppa:
  power: {metric: i_q, times_vdd: true}      # power_w = worst-corner i_q × typical supply
  performance:
    - {metric: load_reg, better: min}        # each reported at its WORST recorded corner
    - {metric: psrr_vdd_db, better: max}
```

Area is `active_gate_area_um2` = Σ (w · l · m) over the lowered netlist's MOS devices, with
geometry expressions resolved against `sizing.yaml` (sky130 = bare µm under `.option scale=1u`;
ihp/gf180 = SI suffixes). It is an honest **gate-area proxy** — no spacing, routing or wells —
and the entry also records ΣC / ΣR so passive area can be costed later (in several circuits the
mim caps and dividers dominate real silicon).

## Accession ids (D-1/D-2)

Verifiable circuits: `<class-code>_<nnn>_<slug>` (`amp_001_5t`, `ldo_004_basic_pmos`) —
append-only numbers, never renumbered/reused; allocate with

```bash
analog-db new-circuit --class ldo --slug my_regulator --ports vdd,vout,vss --pdks sky130
```

Tier 0 enforces the format, the code ↔ class binding (`id_code` in the class's metrics.yaml)
and accession uniqueness. Reference circuits keep corpus-scoped ids (`ferrosim_*`).
Pre-migration names (`5t_ota`, `pmos_ldo`, `*_pin_3`) live in `provenance.aliases`.
