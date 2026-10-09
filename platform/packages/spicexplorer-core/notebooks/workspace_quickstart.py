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
    # WORK_ROOT v2 — the storage kernel tour

    `spicexplorer_core.workspace` is the single home for *what lives where under `WORK_ROOT`* — the storage contract the FastAPI `project_service` **and** the orchestration/MCP agents both build on, so every process speaks one data model (meta-repo [`doc/archive/plan_project_filesystem.md`](../../../doc/archive/plan_project_filesystem.md), §3 layout + §5 decisions D-1…D-11).

    This quickstart tours the four primitives the kernel exposes, all pure-Python (no ngspice, no PDK — it runs in the fast lane on a fresh `uv sync`):

    1. **Layout** — scaffold a self-contained v2 project directory.
    2. **Identity** — `manifest.json` (schema v2) with a monotonic `rev`.
    3. **Migration** — the *additive, idempotent* v1→v2 upgrade.
    4. **Runs** — the generalized run envelope: `dir == run_id`, owner-liveness, and content-addressed input provenance.

    > Everything below writes to a throwaway `WORK_ROOT` in a temp dir, so this notebook never touches your real `work/`.
    """)
    return


@app.cell
def _():
    import json
    import os
    import shutil
    import tempfile
    import time
    from datetime import datetime
    from pathlib import Path

    # Hermetic: point WORK_ROOT at a throwaway dir BEFORE importing the kernel's
    # resolver, so the tour is repo-location-independent and self-cleaning.
    WORK = Path(tempfile.mkdtemp(prefix="wsv2_tour_"))
    os.environ["WORK_ROOT"] = str(WORK)

    from spicexplorer_core import workspace as ws

    print("WORK_ROOT for this tour :", WORK)
    print("manifest schema version:", ws.SCHEMA_VERSION)
    print("run envelope version   :", ws.ENVELOPE_VERSION)
    return WORK, datetime, json, os, shutil, time, ws


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Layout — scaffold a project

    A project directory is **self-contained and portable** (D-7): trash/fork/copy move the whole dir. `scaffold_project` is *create-missing-only* — running it on an existing project touches nothing, which is exactly what makes the v1→v2 migration additive (§3). The v1 dirs (`spice/`, `xschem/`, `scratch/`) are deliberately part of the schema so the root `project.yaml`'s netlists keep resolving.
    """)
    return


@app.cell
def _(ws):
    root = ws.work_root()  # resolves $WORK_ROOT (our temp dir)
    proj = root / "projects" / "my_ota-0a1b2c3d"
    created = ws.scaffold_project(proj)  # idempotent: create-missing-only

    print("scaffold created", len(created), "entries; e.g.:", created[:6])
    print("re-scaffold created:", ws.scaffold_project(proj), "(idempotent)")
    print()
    print("project dirs on disk:", sorted(p.name for p in proj.iterdir()))
    return proj, root


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Identity — `manifest.json` (schema v2)

    v2 makes the **manifest** the project identity, not the optimizer YAML (D-2): a project that only annotates or analyzes a netlist is still a project. Every write is atomic and bumps a monotonic `rev` — the optimistic-concurrency seam (§3.8) that lets a multi-process world detect lost updates. `project.yaml` **stays at the root** (moving it would silently re-anchor its relative `ws_root` — the D-2 hazard).
    """)
    return


@app.cell
def _(datetime, proj, ws):
    man = ws.new_manifest(
        "my_ota-0a1b2c3d", "My OTA", source={"kind": "scratch"}, now=datetime.now().isoformat()
    )
    man = ws.write_manifest(proj, man)  # atomic; stamps schema_version, bumps rev
    print("after create :  rev =", man["rev"], " schema_version =", man["schema_version"])

    man["name"] = "My OTA (renamed)"
    man = ws.write_manifest(proj, man)  # every mutation bumps rev
    print("after rename :  rev =", man["rev"])
    print(
        "read back    : ",
        ws.read_manifest(proj)["name"],
        "| default_job =",
        ws.read_manifest(proj)["default_job"],
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Migration — additive, idempotent v1→v2

    The migrator **only creates missing structure and fills missing manifest fields** — it never moves, renames, or deletes (D-11). That is what makes it safe to run against a live `WORK_ROOT`: every existing endpoint, run dir, and checkpoint path keeps resolving, and re-running reports zero changes.
    """)
    return


@app.cell
def _(json, root, ws):
    # A pre-v2 project on disk: a project.yaml + a v1 manifest (schema_version 1, no rev).
    v1 = root / "projects" / "legacy_amp-99887766"
    v1.mkdir(parents=True)
    (v1 / "project.yaml").write_text("ws_root: .\n")  # stays at root (D-2)
    (v1 / "manifest.json").write_text(
        json.dumps({"id": "legacy_amp-99887766", "name": "Legacy Amp", "schema_version": 1})
    )

    rep = ws.migrate_project(v1)  # scaffold + upgrade manifest
    print(
        "migrate #1:",
        {k: rep[k] for k in ("manifest_upgraded", "changed")},
        "| created",
        len(rep["created"]),
        "dirs",
    )
    print(
        "manifest now:",
        {k: ws.read_manifest(v1)[k] for k in ("schema_version", "rev", "default_job")},
    )

    rep2 = ws.migrate_project(v1)  # idempotent — nothing to do
    print(
        "migrate #2:",
        {k: rep2[k] for k in ("manifest_upgraded", "changed")},
        "| created",
        len(rep2["created"]),
        "dirs",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Runs — the generalized envelope

    A *run* is one user/agent-level action of any kind (optimize, simulate, sweep, annotate, layout, …). The envelope (§3.3 / D-4) gives every writer one shape:

    - **`dir == run_id`** — a sortable, checkpoint-safe id `{ts}_{kind}_{hex8}` that *is* the directory name (kills the old O(N) run-dir scan).
    - **owner-liveness** — an `owner` block + a `.heartbeat`, so a startup reconciler flips `running → error` *only* for a provably-dead writer (an agent's long job survives an API restart).
    - **provenance** — every input blob content-addressed into the project's `.objects/` store, so a run record's hashes dereference forever.

    The FastAPI adapter wraps these as `project_service.begin_run` / `finalize_run`; here we drive the kernel primitives directly.
    """)
    return


@app.cell
def _(datetime, proj, ws):
    runs_base = proj / "runs"
    id1, dir1 = ws.mint_run_dir(runs_base, "simulate")  # dir NAME == run_id
    id2, dir2 = ws.mint_run_dir(runs_base, "optimize")
    print("run 1:", id1, "-> kind", id1.split("_")[1])
    print("run 2:", id2, "-> kind", id2.split("_")[1])
    print("dir name IS the run_id :", dir1.name == id1)
    print("sortable ts prefix     :", id1.split("_")[0], "|", id2.split("_")[0])

    record = {
        "run_id": id1,
        "project_id": proj.name,
        "status": "running",
        "started": datetime.now().isoformat(timespec="seconds"),
        **ws.envelope_fields("simulate", retention="metrics_only"),
    }
    ws.write_run_record(dir1, record)  # atomic run.json
    ws.touch_heartbeat(dir1)  # cheap liveness ping (no run.json rewrite)

    back = ws.read_run_record(dir1)
    print()
    print("envelope fields:", {k: back[k] for k in ("envelope", "kind", "retention")})
    print("owner          :", back["owner"])
    return dir1, record, runs_base


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4b. Owner-liveness — the reconcile gate

    `owner_is_dead` is what a startup reconciler consults before flipping a stuck `running` run to `error`. It distinguishes a **live out-of-process writer** (leave it alone) from a **crashed** one (flip it) — and is careful about a *recycled pid* on the same host after a restart (a `/proc` start-token guard, Linux).
    """)
    return


@app.cell
def _(dir1, os, record, runs_base, time, ws):
    # (a) a LIVE run owned by THIS process — the reconciler must NOT touch it.
    print("live run dead? ", ws.owner_is_dead(record, dir1))  # -> False

    # (b) a LEGACY record (no owner block) — old behavior: a restart flips it.
    print("legacy dead?   ", ws.owner_is_dead({"status": "running"}, dir1))  # -> True

    # (c) a run owned by a FOREIGN host whose heartbeat has gone stale (> 3600 s).
    foreign = runs_base / "foreign"
    foreign.mkdir()
    ws.write_run_record(
        foreign,
        {"owner": {"hostname": "some-other-host", "pid": 4242, "started": "2020-01-01T00:00:00"}},
    )
    old = time.time() - 10_000  # backdate run.json past the stale window
    os.utime(foreign / "run.json", (old, old))
    print("foreign stale? ", ws.owner_is_dead(ws.read_run_record(foreign), foreign))  # -> True
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4c. Input provenance — the `.objects/` content store

    `snapshot_inputs` sha256's every input blob and copies it into the owning project's `.objects/<sha>` store (D-7), so the hashes recorded on an immutable run *dereference forever*. It is content-addressed — re-snapshotting identical bytes reuses the same object — and best-effort (an unreadable input records an error entry instead of failing the run).
    """)
    return


@app.cell
def _(proj, ws):
    # Author a design input, then content-address the run's inputs.
    cell_dir = proj / "design" / "cells" / "ota"
    cell_dir.mkdir(parents=True, exist_ok=True)
    netlist = cell_dir / "netlist.spice"
    netlist.write_text("* my ota\nM1 vout vin 0 0 nch W=10u L=0.18u\n")

    objects = ws.project_objects_dir(proj)  # <project>/.objects
    inputs = ws.snapshot_inputs(
        objects, files={"netlist": netlist}, values={"params": {"W": "10u", "L": "0.18u"}}
    )
    print("inputs recorded on the run:")
    for name, meta in inputs.items():
        print(f"  {name:8} sha256={meta['sha256'][:16]}...")

    sha = inputs["netlist"]["sha256"]
    print()
    print(
        ".objects/<sha> round-trips to the exact bytes:",
        (objects / sha).read_bytes() == netlist.read_bytes(),
    )

    before = len(list(objects.iterdir()))
    ws.snapshot_inputs(objects, files={"netlist": netlist})  # identical bytes
    print("object count stable across re-snapshot:", before == len(list(objects.iterdir())))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    | Concept | Kernel symbol(s) |
    |---|---|
    | resolve the mutable root | `work_root()`, `shared_root()` |
    | scaffold a v2 project | `scaffold_project()`, `PROJECT_DIRS_V2` |
    | project identity + CAS | `new_manifest()`, `write_manifest()`, `read_manifest()` |
    | additive v1→v2 upgrade | `migrate_project()`, `migrate_workspace()`, `upgrade_manifest()` |
    | mint a run (`dir == run_id`) | `new_run_id()`, `mint_run_dir()` |
    | envelope + record + heartbeat | `envelope_fields()`, `write_run_record()`, `read_run_record()`, `touch_heartbeat()` |
    | reconcile gate | `owner_is_dead()` |
    | input provenance | `snapshot_inputs()`, `project_objects_dir()` |

    In the FastAPI adapter these are wrapped by `project_service.begin_run` / `finalize_run` (one seam for every run kind); the derived SQLite index (`services/index_db.py`) is a rebuildable, API-single-writer cache *over* this filesystem — the filesystem stays canonical. See [`doc/archive/plan_project_filesystem.md`](../../../doc/archive/plan_project_filesystem.md).
    """)
    return


@app.cell
def _(WORK, shutil):
    shutil.rmtree(WORK, ignore_errors=True)
    print("removed the temp WORK_ROOT — tour complete")
    return


if __name__ == "__main__":
    app.run()
