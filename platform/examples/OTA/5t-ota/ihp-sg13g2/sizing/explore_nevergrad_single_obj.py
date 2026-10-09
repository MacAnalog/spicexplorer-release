import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE, Optimizer_Type_Enum
    from spicexplorer_core.logging.logger_setup import setup_loggers, setup_loggers_with_spicelib_suppression

    logger = setup_loggers_with_spicelib_suppression()
    # logger = setup_loggers()
    return Circuit_Optimizer_Orchestrator_with_SPICE, Optimizer_Type_Enum


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Comparison to Manual Design of 5t OTA
    From JKU IIC github page. Available [here](https://github.com/iic-jku/analog-circuit-design).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Target to beat: Noise
    ![image.png](public/nevergrad_single_obj_target_noise.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Target to beat: AC openloop
    ![image.png](public/nevergrad_single_obj_target_ac_openloop.png)

    ## Target to beat: AC Unity Gain Feedback Mode
    ![image-2.png](public/nevergrad_single_obj_target_ac_unity_gain.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Target to beat: Transient
    ![image.png](public/nevergrad_single_obj_target_transient.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Start of Optimization Code
    """)
    return


@app.cell
def _(Optimizer_Type_Enum, mo):
    path_to_project_setup = mo.notebook_dir() / "project_setup.yaml"
    optimizer_type = Optimizer_Type_Enum.NEVERGRAD_CONSTRAINT
    return optimizer_type, path_to_project_setup


@app.cell
def _(
    Circuit_Optimizer_Orchestrator_with_SPICE,
    optimizer_type,
    path_to_project_setup,
):
    orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=path_to_project_setup,
        optimizer_type=optimizer_type,
        verbose=True
    )
    return (orchestrator,)


@app.cell
def _(orchestrator):
    optimizer = orchestrator.get_optimizer()
    # orchestrator.run_sanity_on_spicelib_wrapper()
    return (optimizer,)


@app.cell
def _(optimizer):
    optimizer.parameterize()
    return


@app.cell
def _(optimizer):
    optimizer.optimize()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Viewing the Optimization Results
    """)
    return


@app.cell
def _(optimizer):
    optimizer.plot_score(show=True)
    return


@app.cell
def _(mo, optimizer):
    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True, save_path=mo.notebook_dir() / "ugf_dcgain.html")
    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="v(inoise_total)", show=True, save_path=mo.notebook_dir() / "ugf_inoise.html")
    optimizer.plot_optimization_trace(metric_x="dcgain", metric_y="v(inoise_total)", show=True,  save_path=mo.notebook_dir() / "dcgain_inoise.html")
    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="pm", show=True,  save_path=mo.notebook_dir() / "ugf_pm.html")
    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="tsettle", show=True,  save_path=mo.notebook_dir() / "ugf_tsettle.html")
    optimizer.plot_optimization_trace(metric_x="dcgain", metric_y="tsettle", show=True,  save_path=mo.notebook_dir() / "dcgain_tsettle.html")
    optimizer.plot_optimization_trace(metric_x="pm", metric_y="tsettle", show=True,  save_path=mo.notebook_dir() / "pm_tsettle.html")
    return


@app.cell
def _(optimizer):
    optimizer.plot_design_space_exploration(param_x="x_dut_nfet_input_w", param_y="x_dut_nfet_input_l", show=True)
    return


@app.cell
def _(mo, optimizer, orchestrator):
    optimizer.save_checkpoint(name=mo.notebook_dir() / f"{orchestrator.project_setup.optimizer_config.name}_{orchestrator.project_setup.optimizer_config.budget}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cleanup
    """)
    return


@app.cell
def _():
    # Uncomment the following line to clean up temporary files created during optimization
    # optimizer.clean_up()

    import nevergrad as ng

    for item in ng.optimizers.registry:
        print(item)
    return


if __name__ == "__main__":
    app.run()
