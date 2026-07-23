# analog-db notebooks — the library's experimentation surface

Every feature of the DB is exposed for testing through these notebooks (the platform's
notebook-per-feature rule — meta-repo `doc/plan_notebooks_guides.md`). They run **top-to-bottom
PDK-free** on a fresh clone (borrowed platform venv, see `../README.md` → Development); cells that
need a real simulator are **PDK-gated** — they detect the EDA base image
(`docker compose --profile base build spice-base` in spicexplorer-platform) and skip with an
explanation when it's absent. All are committed **executed** so the outputs are reviewable.

| Notebook | What it exercises |
|---|---|
| [`analog_db_tour.ipynb`](analog_db_tour.ipynb) | The DB as a library: catalog → circuit → datasheet/sizing → abstract-vs-lowered netlists → **assemble** a runnable testbench → committed baselines → (gated) live run vs baseline. |
| [`gmid_tables_tour.ipynb`](gmid_tables_tour.ipynb) | The committed gm/ID LUTs (`_shared/gmid/`): pygmid loading, the canonical design curves (gm/ID vs VGS/JD, fT, intrinsic gain), **cross-PDK comparison**, passive constants, regen commands. |
| [`gmid_sizing_demo.ipynb`](gmid_sizing_demo.ipynb) | The gm/ID method on a real table: the 5-step flow, sanity gates, JD-first (weak-inversion) flow, self-loading iteration, design-space sweeps, R/C passive sizing, (gated) ngspice `.op` back-annotation. Seeds the `spicexplorer-gmid` tool API. |
| [`ferrosim_reference_tour.ipynb`](ferrosim_reference_tour.ipynb) | The **`kind: reference`** circuits (plan D-9): browse the 30 imported `ferrosim_*` Spectre circuits from the catalog manifest, inspect one circuit's `references` bindings + dut/tb/runs decks, read a deck, and see the reference-only Tier-0 (T1–T4 skipped). PDK-free — no simulator. |
| [`analog_db_sizing_playground.ipynb`](analog_db_sizing_playground.ipynb) | **The manual sizing loop** (live-gated): pick circuit/PDK/bench → committed-sizing baseline → edit a `sizing_overrides` dict → re-run → metric diff vs datasheet bands → baseline/modified waveform overlay + annotated snapshot plots → mini knob sweep. Rides `run_circuit(..., sizing_overrides=…)` (both lanes) + the waveview snapshot machinery. |

These notebooks are the *test surface* of record for the LUT layer — the L-sweep extraction bug
(identical L slices in the v1 committed tables) was caught by `gmid_sizing_demo`'s back-annotation
cell, not by the unit/slow tests. Keep them executing in any PR that touches the gm/ID pipeline.

**Coverage gap:** the `authoring.scaffold_circuit()` write path (the `analog-db new-circuit` CLI
backend) has no dedicated notebook yet — unit tests in `test_authoring.py` cover it, but the
notebook-per-feature rule calls for a tour notebook here once the feature stabilises.
