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
    **Runs today, but does not reproduce its saved outputs.** `project_setup.yaml` in this folder has changed since the saved run: it now names SamplingSearch with a budget of 5 trials, each simulated at two PVT corners, and a run takes about 4 s with ngspice and the IHP SG13G2 PDK. The saved outputs are a one-off LHSSearch run of 5,000 trials (random seed 48, 1 h 09 min of optimization) and are kept in `explore_nevergrad_single_obj.recorded-outputs.html` beside this file.
    """)
    return


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
    ## Comparison to CORA.OpAmp
    Paper available [here](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=11270673)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Circuit Schematic: Folded-cascode
    ![image.png](public/cora_opamp_folded_cascode_schematic.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Desgin Space Exploration Limits
    ![image.png](public/cora_opamp_action_space.png)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Target Specs to Beat
    ![image-2.png](public/cora_opamp_target_requirements.png)
    ![image.png](public/cora_opamp_performance_summary.png)
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
    optimizer.plot_optimization_trace(metric_x="ugf", metric_y="pm", show=True, save_path=mo.notebook_dir() / "ugf_pm.html")
    return


@app.cell
def _(mo, optimizer, orchestrator):
    optimizer.save_checkpoint(name=mo.notebook_dir() / f"{orchestrator.project_setup.optimizer_config.name}_{orchestrator.project_setup.optimizer_config.budget}")
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
