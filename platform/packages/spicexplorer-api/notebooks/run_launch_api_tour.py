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
    # Run-launch API tour — algorithms, the demo manifest, and the MC lane

    The Studio's **Run popover** and **Projects overlay** are driven by two small read
    endpoints this notebook walks **in-process** via FastAPI's `TestClient` (no `uvicorn`, no
    network — the `library_api_tour` convention):

    - `GET /api/optimize/algorithms` — the selectable optimizer algorithms, derived from the
      *installed* Nevergrad (the UI never hardcodes algorithm names).
    - `GET /api/examples` — the demo-project registry, curated by
      `examples/demos.yaml`.

    It closes with the launch-surface shape of the Monte Carlo lane
    (`POST /api/simulate/once {monte_carlo}` — the live half needs a PDK, see the core
    `monte_carlo_corners` notebook for the mechanism).
    """)
    return


@app.cell
def _():
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    client = TestClient(app)
    return (client,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. `GET /api/optimize/algorithms` — three tiers, one contract

    ```jsonc
    { "recommended": [...], "families": [...], "registry": [...] }
    ```

    - **`recommended`** — the curated known-good presets (the Run popover's primary group).
      Backend-owned and filtered against the installed Nevergrad at request time, so a version
      bump can never advertise a name that won't construct.
    - **`families`** — configurable optimizer **classes** (e.g. `SamplingSearch`,
      `ParametrizedBO`). These are the ONLY names that accept `optimizer_config.
      optimizer_kwargs` in a project YAML.
    - **`registry`** — every pre-configured Nevergrad **preset** (500+). Presets NEVER take
      kwargs — picking one in the Run popover while the YAML carries family kwargs used to
      crash the run at construction. Two guards now hold: the runner clears stale
      `optimizer_kwargs` when an override switches the algorithm, and the factory retries a
      preset WITHOUT kwargs (with a warning) if construction raises `TypeError`.
    """)
    return


@app.cell
def _(client):
    algos = client.get("/api/optimize/algorithms").json()
    print("recommended:", algos["recommended"])
    print("families   :", len(algos["families"]), "e.g.", algos["families"][:6])
    print("registry   :", len(algos["registry"]), "presets, e.g.", algos["registry"][:6])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. `GET /api/examples` — the curated demo registry

    **`examples/demos.yaml` is the single knob deciding what shows up as a demo and in what
    order.** Each entry is an `examples/`-relative `project_setup*.yaml` path; the list order
    is the display order. The rules (all server-side, `project_service`):

    - a listed-but-invalid entry is **skipped with a warning**, never fails the picker;
    - duplicates collapse (first occurrence wins);
    - **delete the file** (or empty its `demos:` list) → the registry falls back to an
      alphabetical scan of every `project_setup*.yaml` under `examples/`.

    Each row's display name/description come from the YAML's own `project.name` /
    `project.description` (path-derived fallback), so e.g. the analog-db demos read as
    "5T-OTA · analog-db amp_001" rather than N copies of "analog-db · circuits".
    """)
    return


@app.cell
def _(client):
    examples = client.get("/api/examples").json()["examples"]
    print(len(examples), "demos, in curated order:\n")
    for e in examples:
        print(f"  {e['name']:42s} {e['key']}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Loading a demo — and its schematics

    `POST /api/projects/from-example {example_key, name}` copies the demo into a fresh
    project. Demo YAMLs may carry a **top-level `assets:` block** (a sibling of `project:`,
    ignored by `Project_Setup.from_yaml`):

    ```yaml
    assets:
      xschem:            # circuit-dir-relative .sch/.sym files, validated + copied
        - reference/ti-ldo/error_amp.sch
    ```

    `copy_example` seeds those files into the new project's `xschem/` tree
    (structure-preserved), and the Schematic view scans it recursively — so a demo built from
    an analog-db circuit lands with its vendored reference schematics browsable. The analog-db
    `export-raw-project --demo` CLI emits this block automatically (every committed
    `.sch`/`.sym` under the circuit dir).

    *(Not executed here — creating projects is a side effect on `WORK_ROOT`; the seeding is
    covered by `tests/test_project_service.py`.)*

    ## 3. The Monte Carlo launch lane (shape only)

    ```jsonc
    POST /api/simulate/once
    {
      "project_id": "…",
      "params": { "w_dut_m1": "20u" },
      "monte_carlo": 8,        // 2..100 mismatch samples; requires a pvt block
      "mc_seed0": 1            // optional reproducibility pin
    }
    ```

    `active_corner` picks the **base** corner the `mc1..mcN` samples clone;
    `monte_carlo` is mutually exclusive with `sweep_corners`. Artifacts land as
    `run_<n>_<tb>__mc<i>` and light up the Analyze viewer's Monte Carlo mode. Mechanism +
    offline demo: `packages/spicexplorer-core/notebooks/monte_carlo_corners.py`; the live
    run needs a mismatch-shipping PDK (the Docker `api` container or the research server).
    """)
    return


if __name__ == "__main__":
    app.run()
