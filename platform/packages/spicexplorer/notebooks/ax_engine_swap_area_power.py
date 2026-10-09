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
    # Ax engine swap + area/power + batched trials — 3-stage NMCF op-amp

    This guide extends [`optimizer_quickstart.py`](optimizer_quickstart.py) with the
    **Ax (Bayesian) backend** and two features that ride the shared scoring loop:

    1. **Engine swap** — the *same* `project_setup.yaml` runs under Nevergrad or Ax, chosen by
       `optimizer_config.type` (`nevergrad` | `bayesian_ax`). Nothing else changes.
    2. **Area + power as first-class metrics** — `power` (a Tier-1 op-point `|I_supply|·VDD`) and
       `active_area` (a **param-derived** `Σ W·L·m`, *no simulation*) are scored, normalized and
       aggregated **exactly like** gain/UGF/PM.
    3. **Batched Ax** — `optimizer_kwargs.batch_size` asks Ax for several candidates per generation
       call (`1` = exact serial parity).

    Vehicle: the unsized three-stage nested-Miller (NMCF) op-amp `amp_008_leung_nmcf`
    (`ihp-sg13g2`, 15 free knobs — a wider search than the two-stage amp_020).

    > **Requirements** (`tests/test_notebooks.py` MANIFEST): `live_ngspice` + `analog_db`. The live
    > Ax cells are additionally guarded on the optional `[ax]` extra (Python ≥ 3.11) and skip with a
    > note when it is absent, so the lane never hard-fails.
    """)
    return


@app.cell
def _():
    import logging
    import os
    import warnings

    # Keep this guide's output readable: quiet the engine/ax INFO logs, the tqdm progress bar, and
    # the ax tracking-metric deprecation notices. (None of this affects the optimization itself.)
    os.environ.setdefault("TQDM_DISABLE", "1")
    warnings.filterwarnings("ignore")
    for _n in ("ax", "spicexplorer", "spicexplorer_core"):
        logging.getLogger(_n).setLevel(logging.ERROR)

    from spicexplorer_core.paths import project_root

    # Resolve inputs from the workspace root so the notebook runs from any cwd (the lane sets the
    # kernel cwd to this notebook's dir). ws_root inside each YAML is resolved against the YAML file.
    ROOT = project_root()
    BASELINE = ROOT / "examples/ax_area_power/amp_008_baseline.yaml"  # noqa: F841 -- the baseline YAML, named for the reader; no cell reads it
    AREA_POWER = ROOT / "examples/ax_area_power/amp_008_area_power.yaml"
    print("workspace root:", ROOT)
    return AREA_POWER, logging, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1 · The project — area & power as first-class metrics

    `amp_008_area_power.yaml` is the baseline (gain/UGF/PM) plus two extra `target_specs`. Note the
    `measurement:` recipes — `power` is a Tier-1 op-point read, `active_area` is param-derived.
    """)
    return


@app.cell
def _(AREA_POWER):
    from spicexplorer.core.domains import Project_Setup

    ps = Project_Setup.from_yaml(str(AREA_POWER))
    searched = [p.name for p in ps.dut_params if not p.freeze]
    frozen = [p.name for p in ps.dut_params if p.freeze]
    print(ps.name)
    print(f"  searched knobs : {len(searched)}   frozen : {len(frozen)}")
    print("  target specs (name · goal · target · measurement):")
    for t in ps.optimizer_config.target_specs.targets:
        recipe = t.measurement if getattr(t, "measurement", None) else "(bare .meas read)"
        print(f"    {t.name:12s} {str(t.goal):>8}  target={t.target!s:>10}   {recipe}")
    return (ps,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `power` and `active_area` carry `goal: minimize` targets below the default design's values, so
    the optimizer feels steady downward pressure on silicon cost while it meets gain/UGF/PM. They
    are scored through the **same** per-spec `range` normalization + reward/penalty aggregation as
    every other spec — there is no bespoke multi-objective machinery.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2 · Engine swap — `optimizer_config.type`

    One YAML, two engines. `optimizer_type_from_config` maps `type:` to a backend; the orchestrator
    resolves through it when no explicit `optimizer_type` is passed. This cell needs **no SPICE**.
    """)
    return


@app.cell
def _(ps):
    from spicexplorer.optimization.orchestrator import (
        Optimizer_Type_Enum,
        optimizer_type_from_config,
    )

    for engine in ("nevergrad", "bayesian_ax"):
        ps.optimizer_config.type = engine
        resolved = optimizer_type_from_config(ps)
        print(f"  optimizer_config.type={engine!r:14} -> {resolved.value}")
    ps.optimizer_config.type = "nevergrad"  # restore
    return (Optimizer_Type_Enum,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3 · Size it LIVE under Ax (Bayesian)

    A short Ax run over the committed raw decks. Guarded on the `[ax]` extra — where it is absent
    the cell prints a skip note instead of raising. (Blocking sims + a `/tmp` scratch dir keep a
    bind-mounted `examples/` tree clean; see `examples/ax_area_power/run_demo.py` for the full sweep.)
    """)
    return


@app.cell
def _(AREA_POWER, Optimizer_Type_Enum, logging, os):
    import importlib.util
    import tempfile

    HAVE_AX = importlib.util.find_spec("ax") is not None

    def size_live(engine, budget=6, batch_size=1):
        """Run one engine to completion; return (score, {metric: value})."""
        if engine == "ax":
            import ax  # noqa: F401 — trigger ax's own logging setup, then quiet its child logger  # pyright: ignore[reportMissingImports] -- the optional [ax] extra; HAVE_AX guards every call

            logging.getLogger("ax.api.client").setLevel(logging.ERROR)
        from spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE

        engines = {
            "nevergrad": Optimizer_Type_Enum.NEVERGRAD_SINGLE,
            "ax": Optimizer_Type_Enum.AX_SINGLE,
        }
        orch = Circuit_Optimizer_Orchestrator_with_SPICE(
            project_setup_path=str(AREA_POWER),
            optimizer_type=engines[engine],
            auto_load=False,
            verbose=False,
        )
        orch.project_setup.outdir = os.environ.get(
            "SX_NB_OUTDIR", os.path.join(tempfile.gettempdir(), "sxsim")
        )
        orch.project_setup.parallel_sim = False  # blocking run() — container-safe
        oc = orch.project_setup.optimizer_config
        oc.budget = budget
        oc.optimizer_kwargs = {**(oc.optimizer_kwargs or {}), "batch_size": batch_size}
        orch.initialize()
        opt = orch.get_optimizer()
        opt.disable_autosave = True
        opt.parameterize()
        opt.optimize()
        best = max(opt.optimization_log, key=lambda e: float(e.point.score))
        metrics = {
            s: float(i["curr_val"])
            for s, i in best.fit_summary.items()  # pyright: ignore[reportOptionalMemberAccess] -- a scored trial's entry always carries its fit_summary
            if isinstance(i, dict) and "curr_val" in i
        }
        opt.close()
        return float(best.point.score), metrics

    if HAVE_AX:
        _score, _metrics = size_live("ax", budget=6)
        print(f"Ax best score = {_score:.4f}")
        for k, v in _metrics.items():
            print(f"    {k:12s} = {v:.4g}")
    else:
        print(
            "[skipped] the optional `ax` extra is not installed "
            "(pip install 'spicexplorer[ax]', Python >= 3.11)."
        )
    return HAVE_AX, size_live


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The Ax run trades some gain/UGF for a **compensated** design (positive phase margin) at lower
    power and area — the score picks up the `power`/`active_area` penalties automatically. On this
    3-stage search, Ax's surrogate typically reaches a stable design in far fewer trials than the
    evolutionary sampler; `run_demo.py --circuit amp_008` sweeps both engines side by side.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4 · Batched Ax — `optimizer_kwargs.batch_size`

    `batch_size = N` (default `1`) asks Ax for `N` candidates per generation call; the loop drains
    one per step, so **budget still counts individual trials** and best-tracking is unchanged.
    Nevergrad ignores the knob (a YAML shared across backends can carry it safely).
    """)
    return


@app.cell
def _(HAVE_AX, size_live):
    if HAVE_AX:
        _score, _metrics = size_live("ax", budget=8, batch_size=4)
        print(
            f"Ax (batch_size=4) best score = {_score:.4f}  (Center+Sobol, then MBM/BoTorch batches of 4)"
        )
    else:
        print("[skipped] needs the `ax` extra.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > Per-candidate *parallel* evaluation would need per-candidate wrappers (the shared testbench
    > wrappers are stateful) — a further follow-up. Today batching buys joint (space-filling)
    > proposals + fewer generation calls.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5 · Scoring you get for free

    Both engines optimize the same landscape, sharpened by three fixes on the shared scorer:

    - **Reward through the feasible band** — a satisfied MINIMIZE/EXCEED spec earns a smooth,
      monotone reward measured from the tolerance-adjusted boundary, instead of a flat dead-zone in
      the grace band. Keeps a gradient toward better area/power once the constraints are met.
    - **Decade-space log specs** — a `log_scale` spec (e.g. a GBW target) normalizes its error in
      *decades*, and the `/api/score` preview scores through the **same** kernel, so the what-if
      penalty matches what the optimizer actually minimizes.
    - **Bounded sim waits** — a hung/stuck ngspice child fails only *that trial* (its metrics score
      as a failure) instead of stalling the whole run (`SPICEXPLORER_SIM_WAIT_TIMEOUT_S`).

    See `doc/archive/plan_ax_sprint.md` for the details.
    """)
    return


if __name__ == "__main__":
    app.run()
