import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    from spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE, Optimizer_Type_Enum
    from spicexplorer_core.logging.logger_setup import setup_loggers_with_spicelib_suppression as setup_loggers

    from pathlib        import Path
    from datetime       import datetime


    logger = setup_loggers()

    TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    BASE_SAVE_DIR = mo.notebook_dir() / f"save_{TIMESTAMP}"
    # BASE_SAVE_DIR = Path(f"./save")
    BASE_SAVE_DIR.mkdir(exist_ok=True)
    return (
        BASE_SAVE_DIR,
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
        Path,
        TIMESTAMP,
        logger,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Comparison to Manual Design of Cascode (Telescopic) OTA
    From JKU IIC github page. Available [here](https://github.com/iic-jku/analog-circuit-design).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ![image-2.png](public/cascode_ota_schematic.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Setup the Optimizer
    """)
    return


@app.cell
def _(Optimizer_Type_Enum, mo):
    path_to_project_setup = mo.notebook_dir() / "project_setup.yaml"
    optimizer_type = Optimizer_Type_Enum.NEVERGRAD_SINGLE
    return optimizer_type, path_to_project_setup


@app.cell
def _(
    Circuit_Optimizer_Orchestrator_with_SPICE,
    TIMESTAMP,
    logger,
    optimizer_type,
    path_to_project_setup,
):
    orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=path_to_project_setup,
        optimizer_type=optimizer_type,
        auto_load=False,
        verbose=True
    )

    # Update the temp path
    temp_dir = f"{orchestrator.project_setup.outdir}_{TIMESTAMP}"
    orchestrator.project_setup.outdir = f"{orchestrator.project_setup.outdir}_{TIMESTAMP}"
    logger.info(f"overwrote project_setup.outdir with {temp_dir}")

    orchestrator.initialize()


    optimizer = orchestrator.get_optimizer()
    optimizer.parameterize()
    # orchestrator.run_sanity_on_spicelib_wrapper()
    return optimizer, orchestrator


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Run the Optimization Loop
    """)
    return


@app.cell
def _(optimizer):
    optimizer.optimize(render_optimization_trace=True, keep_history=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Viewing the Optimization Results
    """)
    return


@app.cell
def _(optimizer):
    optimizer.setup_obj.optimizer_config.target_specs.list_target_names()
    return


@app.cell
def _(BASE_SAVE_DIR, Path, optimizer):
    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True, save_path=BASE_SAVE_DIR/Path("./ugf_dcgain.html"))

    optimizer.plot_optimization_trace(metric_y="ugf", metric_x="i(idd_total)", show=True, save_path=BASE_SAVE_DIR/Path("./ugf_idd_total.html"))
    optimizer.plot_optimization_trace(metric_y="dcgain", metric_x="i(idd_total)", show=True, save_path=BASE_SAVE_DIR/Path("./dcgain_idd_total.html"))

    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="v(inoise_total)", show=True, save_path=BASE_SAVE_DIR/Path("./ugf_inoise.html"))
    optimizer.plot_optimization_trace(metric_x="dcgain", metric_y="v(inoise_total)", show=True,  save_path=BASE_SAVE_DIR/Path("./dcgain_inoise.html"))

    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="pm", show=True,  save_path=BASE_SAVE_DIR/Path("./ugf_pm.html"))
    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="tsettle", show=True,  save_path=BASE_SAVE_DIR/Path("./ugf_tsettle.html"))
    optimizer.plot_optimization_trace(metric_x="dcgain", metric_y="tsettle", show=True,  save_path=BASE_SAVE_DIR/Path("./dcgain_tsettle.html"))
    optimizer.plot_optimization_trace(metric_x="pm", metric_y="tsettle", show=True,  save_path=BASE_SAVE_DIR/Path("./pm_tsettle.html"))
    return


@app.cell
def _(optimizer):
    optimizer.spicelib_wrappers['tb_ac'].get_dut_params()
    return


@app.cell
def _(optimizer):
    optimizer.plot_design_space_exploration(param_x="X_DUT_M1CM2C_L", param_y="X_DUT_M1CM2C_W", show=True)
    return


@app.cell
def _(optimizer):
    optimizer.get_best_params(verbose=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Saving the Results
    """)
    return


@app.cell
def _(BASE_SAVE_DIR, Path, optimizer, orchestrator):
    _save_path = BASE_SAVE_DIR/Path(f"{orchestrator.project_setup.optimizer_config.name}_{orchestrator.project_setup.optimizer_config.budget}_score.html")
    optimizer.plot_score(show=False, save_path=_save_path)
    return


@app.cell
def _(BASE_SAVE_DIR, Path, optimizer, orchestrator):
    _save_path = BASE_SAVE_DIR/Path(f"{orchestrator.project_setup.optimizer_config.name}_{orchestrator.project_setup.optimizer_config.budget}")
    optimizer.save_checkpoint(name=_save_path)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cleanup

    ```python
    # Uncomment the following line to clean up temporary files created during optimization
    # optimizer.clean_up()
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
