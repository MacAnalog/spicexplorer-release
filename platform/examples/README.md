# examples/

- **`analog-db/`** — the **analog circuit database** ([`spicexplorer-analog-db`](https://github.com/MacAnalog/spicexplorer-analog-db) submodule):
  the canonical topology/circuit registry (super-DSL + datasheets + class libraries) and the
  tiered `verify` harness. Init with `git submodule update --init examples/analog-db`. Develop it
  from this checkout by borrowing the platform venv (see `examples/analog-db/README.md`):
  `uv pip install --no-deps -e examples/analog-db && uv pip install jsonschema`.
- **`OTA/`** — the original per-PDK OTA examples (`cascode`, `5t-ota`, `folded_cascode`). These are
  the **pre-migration** sources; their content now lives, normalized, in the analog-db submodule
  (`telescopic_cascode_ota`, `5t_ota`, `folded_cascode_ota`). Kept here until consumers (the
  optimizer/api integration tests, the UI) repoint through `analog_db.paths.db_root()` (plan Phase 8);
  see `examples/analog-db/_shared/{MIGRATION,TEST_COUPLING}.md`.
- **`notebooks/`** ([`notebooks/README.md`](notebooks/README.md)) — orchestration-style guide notebooks
  that **compose** platform tools over the analog-db corpus (multi-corner PVT sweep, in-library run,
  bench validation, …), as opposed to the per-package quickstarts under `packages/<pkg>/notebooks/`.
- **`layout/`** ([`layout/ihp-sg13g2/README.md`](layout/ihp-sg13g2/README.md)) — prototype programmatic
  **layout generation + physical signoff + PEX** for IHP `sg13g2` (a 5T OTA via two independent
  generator lanes); scripts + a notebook, not yet a platform package.
- `spec_library.yaml`, `nevergrad_reference_*.yaml`, `coding_style.xml` — root reusable assets
  (a canonical copy of the first two also lives under the submodule's `_shared/`).
