> **[TODO]** — Test repoint worklist. Parent plan: `doc/plan_examples_db.md` §3c. Unit-fixture moves (circuitgraph, netlist2tf, core) are **DONE** — verified by `tests/fixtures/` presence. Integration repoints (api, optimizer) and runtime repoints (Phase 8) remain open.

# Platform coupling to `examples/OTA/…` — the repoint worklist

> Plan `doc/plan_examples_db.md` §3c. The migration (Phase 3) and the submodule extraction
> (Phase 4) change every example path, and the platform suite hard-codes `examples/OTA/…`
> across **five packages**. This is the enumerated worklist so the repoint happens in lock-step.
> Generated at Phase 0 from a tree-wide grep; line numbers are point-in-time.

## The fix (two parts — plan §3c)

1. **Single path indirection.** `spicexplorer_analog_db.paths.db_root()` is the one
   env-overridable seam (`$SPICEXPLORER_ANALOG_DB`) that resolves in-tree vs the
   `examples/analog-db/` submodule. **Seeded in Phase 0.** The extraction (Phase 4) flips one
   place, not ~30. Tests should import circuit fixtures through this, not via raw
   `project_root()/"examples"/"OTA"/…`.
2. **Move genuine unit-test fixtures into each package's `tests/fixtures/`.** Leaf-tool unit
   tests (circuitgraph / netlist2tf / core) depend on the example DB only because the small
   netlists happen to live there — the DB is for *integration*, not unit fixtures. Moving them
   lets those tests run without the DB (de-risks the shallow-clone "submodule absent" case,
   mirroring the PDK-absence contract). Only the optimizer/api integration + `slow` sim tests
   then consume the DB through the indirection.

## Coupled TEST files (the §3c worklist)

### `spicexplorer-api` — through the indirection (integration; keep DB-backed)
- `tests/conftest.py` (EXAMPLE_YAML / _DUT_NETLIST / _TB_NETLIST — cascode)
- `tests/test_ws_root_contract.py`, `tests/test_pvt_wizard_roundtrip.py` (cascode + folded),
  `tests/test_ui_phase_completion.py`, `tests/test_ui_restructure_2026_06.py`,
  `tests/test_audit_r3_tier4_backend.py`

### `spicexplorer` (optimizer) — through the indirection (integration; keep DB-backed)
- `tests/conftest.py` (cascode `project_setup.yaml` + netlists)
- `tests/test_pvt_corner.py` (cascode + folded), `tests/test_smoke_optimization.py`
  (5t-ota + cascode + folded), `tests/test_audit_fixes.py`, `tests/test_audit_r3_newcas.py`,
  `tests/test_newcas_demo_runner.py`

### `spicexplorer-circuitgraph` — **move to `tests/fixtures/`** (unit) ✅ DONE
- `tests/test_graph_build.py`, `test_roundtrip.py`, `test_emit.py`, `test_review_fixes.py`,
  `test_scaffold.py`, `test_serialization.py`, `test_subckt.py`, `test_views.py`
  (cascode `ota-improved.spice`, folded `cora_testbench_ac.spice`)
  — verified: `packages/spicexplorer-circuitgraph/tests/fixtures/` exists with the netlists.

### `spicexplorer-netlist2tf` — **move to `tests/fixtures/`** (unit) ✅ DONE
- `tests/test_n2tf_{scaffold,ingest,models,mna,flatten,pipeline}.py` (cascode DUT, 5T subckt,
  AC testbench via `project_root()`)
  — verified: `packages/spicexplorer-netlist2tf/tests/fixtures/` exists with the netlists.

### `spicexplorer-core` — **move to `tests/fixtures/`** (unit) ✅ DONE
- `tests/test_netlist_view.py`
  — verified: `packages/spicexplorer-core/tests/fixtures/` exists.

## Coupled SOURCE files (runtime — repoint in Phase 8 with the API/UI)

These are NOT tests; they bind the *running platform* to `examples/`. They repoint when the
DB extracts + the API serves the catalog (Phase 8), via the same `db_root()` seam.
- `spicexplorer-api/src/.../routes/netlist.py:15` — serves `examples/spec_library.yaml`
  (relocated copy at `_shared/spec-library.yaml`; original kept until this repoints).
- `spicexplorer-api/src/.../routes/checkpoint.py`, `routes/projects.py`,
  `services/project_service.py` — example-relative project paths.
- `spicexplorer/src/spicexplorer/demo/newcas_demo_runner.py:25` — `examples/OTA/cascode` path.

## Note

The Phase-0 additions do **not** touch any of the above (the new `circuits/` tree coexists with
`examples/OTA/`; the only edit to a shared test harness is `conftest.py`, which now *skips*
super-DSL projections so the new thin `project_setup.yaml` files aren't mis-parsed as legacy
optimizer configs). Full repoint is Phase 3 (tests) + Phase 4 (flip the seam to the submodule).
