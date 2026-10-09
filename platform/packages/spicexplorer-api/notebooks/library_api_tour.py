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
    # Reference Library API — a server-free tour

    The `/api/library/*` routes serve the **analog-db catalog** to the Studio's `/library` browser.
    This notebook walks the browser's **read surface** — `status`, `catalog`, per-circuit datasheet,
    bulk `results`, the class registry, `templates`, and the schematic SVGs — **in-process** via
    FastAPI's `TestClient` (no `uvicorn`, no network). It runs top-to-bottom on the borrowed platform venv.

    > Two routes aren't run live here to keep the tour read-only and side-effect-free: the template
    > **PNG** render `GET /api/library/templates/{id}/image` (a binary sibling of the schematic SVGs) and
    > the **write** path `POST /api/library/circuits` (the Register wizard's draft scaffold, which creates
    > a `circuits/<id>/` dir). Both are covered end-to-end in `tests/test_library_routes.py` and the guide.

    > The `analog-db` submodule is an **optional** dependency (not a `uv` workspace member). When it
    > isn't installed the routes degrade gracefully (see the last cell); install it into the env with
    > `uv pip install --no-deps -e examples/analog-db && uv pip install jsonschema`.

    See also: the end-to-end guide `doc/guide_library_catalog.md`, and the Python data layer in
    analog-db's `notebooks/analog_db_tour.py`.
    """)
    return


@app.cell
def _():
    from fastapi.testclient import TestClient
    from spicexplorer_api.main import app

    client = TestClient(app)

    # The availability probe always answers — it gates the UI and every cell below.
    status = client.get("/api/library/status").json()
    AVAILABLE = status["available"]
    status
    return AVAILABLE, client, status


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Catalog — the class-grouped browse list
    """)
    return


@app.cell
def _(AVAILABLE, client, status):
    if AVAILABLE:
        cat = client.get("/api/library/catalog").json()
        print("schema :", cat["schema"])
        print("classes:", {k: len(v) for k, v in cat["classes"].items()})
        print("circuits:", len(cat["circuits"]))
        ex = next(c for c in cat["circuits"] if c["id"] == "amp_001_5t")
        print(
            "\n5t_ota:",
            {k: ex[k] for k in ("id", "class", "compensation", "stages", "status", "pdks")},
        )
        print("provenance:", ex["provenance"])
    else:
        print("analog-db unavailable —", status["reason"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Circuit detail — datasheet + recorded results + schematic modes
    """)
    return


@app.cell
def _(AVAILABLE, client):
    if AVAILABLE:
        d = client.get("/api/library/circuits/amp_001_5t").json()
        print("ports        :", d["ports"])
        print("datasheet    :", list(d["datasheet"])[:6], "...")
        print("result PDKs  :", list(d["results"]))
        sky = d["results"]["sky130"]["measures"]
        print("sky130 dcgain:", sky.get("dcgain"), "dB · ugf:", sky.get("ugf"), "Hz")
        print("schematics   :", list(d["schematics"]))
    else:
        print("skipped (analog-db unavailable)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Bulk results, class registry, and the template library
    """)
    return


@app.cell
def _(AVAILABLE, client):
    if AVAILABLE:
        results = client.get("/api/library/results").json()["results"]
        print("circuits with recorded results:", len(results))

        classes = client.get("/api/library/classes").json()["classes"]
        for c in classes:
            print(
                f"  class {c['class']:10s} · {len(c['canonical_metrics'])} metrics · {len(c['templates'])} analyses"
            )

        tpl = client.get("/api/library/templates").json()
        print("template families:", tpl["families"], "· total:", len(tpl["templates"]))
        print(
            "first template   :",
            tpl["templates"][0]["id"],
            "—",
            tpl["templates"][0]["display_name"],
        )
    else:
        print("skipped (analog-db unavailable)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Schematics — block-aware / hierarchical / pure

    Each circuit's schematic renders in three views. The bytes stream from
    `GET /api/library/circuits/{id}/schematic?mode=`; the datasheet UI offers a toggle over the modes
    the detail's `schematics` map reports.
    """)
    return


@app.cell
def _(AVAILABLE, client):
    from IPython.display import SVG, display

    if AVAILABLE:
        for mode in ("block_aware", "hierarchical", "pure"):
            r = client.get(f"/api/library/circuits/amp_001_5t/schematic?mode={mode}")
            print(
                f"{mode:12s} -> {r.status_code} {r.headers['content-type']} ({len(r.content)} bytes)"
            )
        # render the block-aware view inline
        svg = client.get("/api/library/circuits/amp_001_5t/schematic?mode=block_aware").content
        display(SVG(data=svg))
    else:
        print("skipped (analog-db unavailable)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Graceful degradation

    The data routes never 500 when analog-db is absent — they 503, and `status` reports why. Here we
    stub the reader absent to show the contract the UI relies on.
    """)
    return


@app.cell
def _(client):
    from spicexplorer_api.services import library_db

    _orig = library_db._modules
    library_db._modules = lambda: None  # simulate the submodule not being installed
    try:
        print("status  :", client.get("/api/library/status").json())
        print("catalog :", client.get("/api/library/catalog").status_code, "(503 = graceful)")
    finally:
        library_db._modules = _orig  # restore
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. The webapp's own data — the derived `index.db`

    The tour above browsed the analog-db **catalog**. The webapp's *own* state — **projects** and
    their **runs** under `WORK_ROOT` — is served from a derived SQLite index, `index.db` (project-fs
    P2). It is a **rebuildable cache of the filesystem**: the FS is canonical, `GET /projects` reads
    the index but falls back to an FS scan on any DB error, and `rebuild()` re-derives the whole index
    from disk. Point it at a throwaway `WORK_ROOT`, create a project, and rebuild:
    """)
    return


@app.cell
def _():
    import os
    import tempfile

    from spicexplorer_api.services import index_db, project_service

    # index.db is per-WORK_ROOT; use a throwaway one so this cell is self-contained.
    os.environ["WORK_ROOT"] = tempfile.mkdtemp(prefix="idx_tour_")
    pid = project_service.create_project("Index Tour Demo")  # a real WORK_ROOT v2 project

    print("index.db path :", index_db.db_path())
    print("rebuild       :", index_db.rebuild())  # FS truth -> index: {projects, runs}
    print("projects      :", [p["id"] for p in index_db.list_projects()])
    print("runs(project) :", index_db.list_runs(pid))  # none yet
    # The CLI runs the same rebuild:  python -m spicexplorer_api.services.index_db --work-root <dir>
    return


if __name__ == "__main__":
    app.run()
