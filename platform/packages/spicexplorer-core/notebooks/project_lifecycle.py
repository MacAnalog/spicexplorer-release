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
    # Project lifecycle — retention, verification, promotion, reuse & agent context

    `workspace_quickstart.py` toured the storage kernel (scaffold / manifest / run
    envelope). This one tours what a **design effort** accumulates on top of runs — the
    P3.1/P4/P5 slices of [`doc/archive/plan_project_filesystem.md`](../../../doc/archive/plan_project_filesystem.md):

    1. **Retention / GC** — enforce a run's artifact tier (drop heavy waveforms, keep history).
    2. **Verification plan** — the spec × test × corner joining table.
    3. **`state.json`** — the derived compliance matrix + best-run pointers.
    4. **Promotion** — immutable design snapshots + an atomic `current` pointer.
    5. **Curated annotations** — a human correction survives regeneration.
    6. **Shared library** — publish-on-promote / copy-on-import.
    7. **Agent context** — append-only decisions → a generated `PROJECT.md`.

    > All pure-python in a throwaway `WORK_ROOT` — no ngspice, no PDK.
    """)
    return


@app.cell
def _():
    import os
    import shutil
    import tempfile
    from pathlib import Path

    WORK = Path(tempfile.mkdtemp(prefix="pf_lifecycle_"))
    os.environ["WORK_ROOT"] = str(WORK)

    from spicexplorer_core import workspace as ws

    # A design project to work in.
    proj = ws.work_root() / "projects" / "ota-0a1b2c3d"
    ws.scaffold_project(proj)
    ws.write_manifest(
        proj, {"id": "ota-0a1b2c3d", "name": "Folded-Cascode OTA", "default_pdk": "ihp-sg13g2"}
    )
    print("project:", proj.name)
    return Path, WORK, proj, shutil, ws


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Retention / GC — enforce a run's artifact tier

    Every run records a `retention` tier (`full` / `metrics_only` / `none`). The GC drops
    the heavy `sim/` waveforms at `metrics_only` while keeping the record + history — and
    per-trial candidates are already columnar rows in `events.ndjson` (not directories), so
    they survive. `prune_run` is idempotent and only ever touches a *terminal* run.
    """)
    return


@app.cell
def _(proj, ws):
    run = proj / "runs" / "20260715-100000_optimize_aaaa1111"
    (run / "sim" / "run_1_tb_ac__tt").mkdir(parents=True)
    (run / "sim" / "run_1_tb_ac__tt" / "out.raw").write_bytes(b"RAW" * 4096)  # the disk hog
    (run / "events.ndjson").write_text(
        '{"iter": 1, "score": 0.5, "metrics": {"dcgain": 41}}\n'
        '{"iter": 2, "score": 0.9, "metrics": {"dcgain": 44}}\n'
    )
    ws.write_run_record(
        run,
        {
            "run_id": run.name,
            "status": "done",
            "best_score": -0.4,
            "metrics": {"dcgain": 44.0},
            **ws.envelope_fields(
                "optimize", retention="metrics_only", coordinates={"corner": "tt"}
            ),
        },
    )

    print("candidates (rows, not dirs):", [c["iter"] for c in ws.iter_candidates(run)])
    rep = ws.prune_run(run)
    print("pruned tier:", rep["tier"], "| freed bytes:", rep["freed_bytes"])
    print("sim/ waveforms gone:", not (run / "sim").exists())
    print("history kept — candidates still readable:", [c["iter"] for c in ws.iter_candidates(run)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Verification plan — spec × test × corner

    `verify/plan.yaml` binds each spec to a Tier-1 measurement over a corner × temp matrix
    and how it collapses (`aggregate`). Target *values* stay canonical in `spec/targets.yaml`.
    """)
    return


@app.cell
def _(proj, ws):
    (proj / "verify").mkdir(exist_ok=True)
    (proj / "verify" / "plan.yaml").write_text("""
    specs:
      gain_db:
        measurement: dcgain
        corners: [tt, ss, ff]
        aggregate: min          # worst-case across corners
        target: ">= 40"
      power_w:
        measurement: itot
        corners: [tt]
        aggregate: max
        target: "<= 1m"
    """)
    plan = ws.load_verify_plan(proj)
    print("specs:", list(plan.specs))
    print("matrix points:", len(plan.matrix()))
    gain = plan.specs["gain_db"]
    print(
        "worst-case of [44, 41, 39] =",
        gain.aggregate_value([44, 41, 39]),
        "-> passes >= 40?",
        gain.passes([44, 41, 39]),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. `state.json` — the derived compliance matrix

    `build_state` joins the plan with run history (each run's `metrics` + `coordinates`) into
    a rebuildable rollup: the spec × corner compliance matrix, best-run pointers **with the
    election rule stated**, and the cell inventory. Derived — regenerate to heal.
    """)
    return


@app.cell
def _(proj, ws):
    # one run per corner, carrying its measured gain
    for corner, gain_val, score in [("tt", 44.0, -0.4), ("ss", 41.0, -0.6), ("ff", 39.0, -0.9)]:
        r = proj / "runs" / f"20260715-1005_optimize_{corner}00000"
        r.mkdir(parents=True, exist_ok=True)
        ws.write_run_record(
            r,
            {
                "run_id": r.name,
                "status": "done",
                "best_score": score,
                "metrics": {"dcgain": gain_val},
                **ws.envelope_fields("optimize", retention="full", coordinates={"corner": corner}),
            },
        )

    state = ws.rebuild_state(proj)
    comp = state["compliance"]["gain_db"]
    print(
        "gain_db  worst:", comp["value"], "| pass:", comp["pass"], "| by corner:", comp["by_corner"]
    )
    print("summary :", state["compliance_summary"])
    print("best run:", state["best_runs"]["overall"]["run_id"])
    print("  rule  :", state["best_runs"]["election_rule"])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Promotion — immutable snapshots + an atomic `current` pointer

    Accepting a design writes a sortable, immutable `design/history/<id>/` snapshot (netlist +
    sizing + annotations) and swaps `current` atomically, under a per-project lock. History is
    append-only: an old snapshot keeps the old sizing forever.
    """)
    return


@app.cell
def _(proj, ws):
    cell = proj / "design" / "cells" / "ota"
    cell.mkdir(parents=True, exist_ok=True)
    (cell / "netlist.spice").write_text("* ota\n")
    (cell / "sizing.yaml").write_text("W: 10u\n")
    v1 = ws.promote(proj, label="first gm/ID sizing")

    (cell / "sizing.yaml").write_text("W: 20u\n")  # iterate the live design
    v2 = ws.promote(proj, label="widened input pair")

    old = proj / "design" / "history" / v1["id"] / "cells" / "ota" / "sizing.yaml"
    print("v1 snapshot still holds:", old.read_text().strip(), "(immutable)")
    print("current points at v2   :", ws.current_promotion(proj)["label"])
    print("history (newest first) :", [p["label"] for p in ws.list_promotions(proj)])
    return (v2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Curated annotations — a human correction survives regeneration

    Curated annotations live in `design/cells/<cell>/annotations.yaml`, anchored to structural
    identities. Regeneration is a **merge proposal**, never a blind overwrite: `merge_curated`
    preserves every human-reviewed label (recording what the machine proposed).
    """)
    return


@app.cell
def _(ws):
    curated = {
        "M1": {"role": "input_pair", "reviewed_by": "human"},
        "M3": {"role": "tail", "reviewed_by": "agent"},
    }
    raw = {"M1": "input_diff", "M3": "tail_source", "M5": "mirror"}  # a fresh machine pass

    prop = ws.merge_proposal(curated, raw)
    print("proposal add    :", [a["id"] for a in prop["add"]])
    print("proposal conflict:", [(c["id"], c["protected"]) for c in prop["conflict"]])

    merged = ws.merge_curated(curated, raw)
    print("M1 (human) kept :", merged["M1"]["role"], "| records raw as", merged["M1"]["overrides"])
    print("M3 (agent) updated:", merged["M3"]["role"])
    print("M5 added         :", merged["M5"]["role"])
    return (merged,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Shared library — publish-on-promote / copy-on-import

    `shared/lib/<cell>/<version>/` is the cross-project reuse shelf: publish copies a cell's
    accepted files there (immutable versions); import **copies** them into another project with
    an `imported_from` provenance record — concrete files, not a live reference.
    """)
    return


@app.cell
def _(Path, merged, proj, v2, ws):
    ws.write_curated(proj, "ota", merged)  # attach the curated annotations
    rec = ws.publish_cell(proj, "ota", version="v1", source={"from_promotion": v2["id"]})
    print("published ota/v1 — captured:", rec["captured"])

    other = ws.work_root() / "projects" / "amp-0b2c3d4e"
    ws.scaffold_project(other)
    marker = ws.import_cell("ota", "v1", other, as_name="input_stage")
    imported = other / "design" / "cells" / "input_stage" / "sizing.yaml"
    print("imported into amp as input_stage:", imported.read_text().strip())
    print(
        "provenance marker:", marker["cell"], marker["version"], "->", Path(marker["source"]).name
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Agent context — decisions → a generated `PROJECT.md`

    Agents append decision *events* (one `O_APPEND` write each); they never edit the rendered
    document. `render_project_md` generates `context/PROJECT.md` from the decision log + the
    derived `state.json` — the one surface an agent reads to learn where a design is at.
    """)
    return


@app.cell
def _(proj, ws):
    ws.append_decision(
        proj, {"kind": "topology", "summary": "folded cascode for the gain wall", "by": "agent"}
    )
    ws.append_decision(
        proj, {"kind": "sizing", "summary": "accepted the 44 dB (tt) sizing", "by": "human"}
    )

    md_text = ws.render_project_md(proj)
    print(md_text)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Recap

    | Lifecycle concern | Kernel entry point |
    |---|---|
    | retention / GC | `prune_run`, `prune_workspace`, `iter_candidates` |
    | verification plan | `load_verify_plan` → `VerifyPlan`/`Spec` |
    | derived rollup | `build_state`, `rebuild_state`, `read_state` |
    | promotion | `promote`, `current_promotion`, `list_promotions` |
    | curated annotations | `merge_proposal`, `merge_curated`, `read/write_curated` |
    | shared library | `publish_cell`, `import_cell`, `list_library` |
    | agent context | `append_decision`, `read_decisions`, `render_project_md` |

    Over HTTP, the FastAPI adapter exposes the last two rows as
    `GET /projects/{id}/state`, `GET /projects/{id}/context`, and
    `POST /projects/{id}/decisions` — the surface an MCP server hands to agents.
    See [`doc/archive/plan_project_filesystem.md`](../../../doc/archive/plan_project_filesystem.md).
    """)
    return


@app.cell
def _(WORK, shutil):
    shutil.rmtree(WORK, ignore_errors=True)
    print("removed the temp WORK_ROOT — tour complete")
    return


if __name__ == "__main__":
    app.run()
