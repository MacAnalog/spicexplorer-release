> **[REFERENCE]** — CACE field-mapping spike + adapter contract. Parent plan: `doc/plan_examples_db.md` O-1/D-12. The bidirectional CACE adapter described in §O-1 below was **not built in Phase 2** and remains **deferred** — `runner.py` slots the adapter in as a future pluggable backend (see its docstring). Do not rely on a working CACE adapter; use the native runner.

# CACE `cace_format` 5.2 ↔ super-DSL datasheet — field overlap (resolves O-1)

> Plan `doc/plan_examples_db.md` O-1 + follow-up #2 / D-12. The spike: `pip install cace`
> (v**2.9.0**), confirm the **Python API**, load the analog-circuit-design `5t` 5.2 datasheet,
> and map its fields onto our `datasheet.yaml` super-DSL → decide **verbatim-reuse vs rename**.

## CACE Python API (confirmed, v2.9.0)

The documented, modern entry point is the **`ParameterManager`** class — not the legacy
`cace.common.cace_read.cace_read()`, which is the *old flat text format* reader and errors
("Undefined syntax") on a 5.x YAML.

```python
from cace.parameter.parameter_manager import ParameterManager
pm = ParameterManager()
pm.load_datasheet("voltage-buffer-ota.yaml")   # parses cace_format 5.2 YAML  → True
ds = pm.get_datasheet()                          # dict: name, PDK, cace_format, pins,
                                                 #       default_conditions, parameters, paths
pm.get_all_pnames()           # ['ac_params','ac_mc_params','noise_params','tran_params']
pm.run_parameters(...)        # drives ngspice/xschem/magic/netgen  (PDK-gated → container)
pm.save_datasheet(path)       # writes the characterized datasheet back
```

Confirmed loading the a-c-d `5t` datasheet: `cace_format: 5.2`, spec shape
`{display, description, unit, minimum:{value}, typical:{value}, maximum:{value}}`.
**`load_datasheet` + `get_datasheet` are PDK-free** (ran on this host); `run_parameters` needs
ngspice + the IHP PDK → it runs in the `api` container (see `verify-live-spice-in-docker`).

## Structural diff

| Aspect | CACE 5.2 | super-DSL `datasheet.yaml` |
|---|---|---|
| metric container | nested under **parameter groups**: `parameters.<group>.spec.<metric>` | **flat**: `metrics.<id>` |
| per-group baggage | each group carries its own `tool` / `plot` / `conditions` | analysis binding lives in `analyses/*.yaml`; plots are a UI concern |
| spec bounds | `minimum/typical/maximum: {value: <num>|any}` | `spec: {min/typ/max[, unit]}` (`any` → omit) |
| sim hookup | `tool.ngspice: {template, variables, format, suffix, script}` | `extract: {meas|fn}` |
| symbolic | — (none) | `symbolic: {tool: netlist2tf, call, args}` ← **our differentiator (D-5)** |
| conditions | `default_conditions` + per-group `conditions` (corner enumerate / min-typ-max sweeps) | `default_conditions` (PVT lives in `pdk/*/corners.yaml`) |
| pins | `pins.<p>: {type, direction, Vmin, Vmax}` | `circuit.yaml.ports` (order) + role inference |

## Field map (total, mechanical — the adapter contract)

| CACE 5.2 | super-DSL |
|---|---|
| `name` | `circuit.yaml.id` / `display_name` |
| `PDK` | `circuit.yaml.pdks[*]` |
| `cace_format` | `datasheet.cace_format` (kept for round-trip) |
| `default_conditions.<v>.{unit,typical}` | `datasheet.default_conditions.<v>.{unit,typical}` (1:1) |
| `parameters.<g>.spec.<m>.{display,description,unit}` | `metrics.<m>.{display,description,unit}` |
| `parameters.<g>.spec.<m>.minimum.value` | `metrics.<m>.spec.min` (`any`→omit) |
| `parameters.<g>.spec.<m>.typical.value` | `metrics.<m>.spec.typ` |
| `parameters.<g>.spec.<m>.maximum.value` | `metrics.<m>.spec.max` |
| `parameters.<g>.tool.ngspice.template` | `analyses/<id>.yaml.template` + `metrics.<m>.analysis` |
| `parameters.<g>.tool.ngspice.variables[*]` | `metrics.<m>.extract.meas` |
| `parameters.<g>.tool.ngspice.script` | `extract.fn` (ported into `_shared/extract/`) |
| `parameters.<g>.conditions` | `pdk/*/corners.yaml` + analysis `params` |
| `pins.<p>` | `circuit.yaml.ports` (+ future role/limits block) |
| — | `metrics.<m>.symbolic` (super-DSL only; dropped when emitting cace) |

## O-1 resolution — **superset-rename, with a total bidirectional adapter**

**Decision:** the super-DSL is a **renamed superset**, *not* a verbatim cace embedding.
- **Why not verbatim:** cace's group-nesting (`parameters.<group>.spec`) and per-group
  `tool/plot/conditions` fight the flat, agent-queryable metric vocabulary the class layer
  validates (D-7/D-8), and bake ngspice/xschem/CLI-centricity into the canonical sheet.
  The super-DSL also adds first-class `symbolic` (the netlist2tf cross-check, D-5), which has
  no cace equivalent.
- **Why still compatible (D-12):** the map above is **total and mechanical**, so a Phase-2
  adapter can (a) **emit** a cace-shaped datasheet from `datasheet.yaml` and drive a real CACE
  run via `ParameterManager`, and (b) **ingest** the characterized result back into
  `results/`. CACE stays an *optional pluggable backend behind an adapter*, never a core dep.

**Plan deltas:** O-1 → **RESOLVED (superset-rename + adapter map)**. The field map above is complete
and serves as the adapter contract. The bidirectional adapter (emit cace-shaped datasheet / ingest
characterized result) is **deferred beyond Phase 2** — `runner.py` (lines 12–14) reserves the slot
for a future CACE-backend pluggable behind the same `run_cell` interface.
