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
    **Does not run today, and has no saved outputs.** It reads `checkpoints/LHSSearch_2000.json`, which is in no repository, so `python` on this file stops at the checkpoint-load cell (FileNotFoundError). Its code is the 5T OTA folder's `../../../5t-ota/ihp-sg13g2/sizing/explore_load_optimization_trace.py`, cell for cell, with that circuit's parameter names (`x_dut_nfet_input_w`, `x_dut_nfet_mirror_w`); the saved outputs of that notebook's run are recorded beside it.
    """)
    return


@app.cell
def _():
    from spicexplorer.optimization      import Circuit_Optimizer_Orchestrator_with_SPICE
    from spicexplorer.viz               import Optimization_Log_Visualizer
    from spicexplorer_core.logging.logger_setup               import setup_loggers_with_spicelib_suppression as setup_loggers

    logger = setup_loggers()
    logger.info("Spicelib_Wrapper imported successfully.")
    return (Optimization_Log_Visualizer,)


@app.cell
def _(Optimization_Log_Visualizer, mo):
    path_to_checkpoint = mo.notebook_dir() / "checkpoints/LHSSearch_2000.json"
    viz = Optimization_Log_Visualizer.load_checkpoint(path_to_checkpoint=path_to_checkpoint)
    return (viz,)


@app.cell
def _(viz):
    viz.list_available_params()
    return


@app.cell
def _(viz):
    viz.list_available_metrics()
    return


@app.cell
def _(viz):
    viz.plot_design_space_exploration(param_x="x_dut_nfet_input_w", param_y="x_dut_nfet_mirror_w", show=True)
    return


@app.cell
def _(viz):
    viz.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True)
    viz.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True, log_x=True, log_y=False)
    viz.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True, log_x=False, log_y=True)
    viz.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=True, log_x=True, log_y=True)
    return


@app.cell
def _(viz):
    viz.plot_optimization_trace(metric_x="v(inoise_total)", metric_y="dcgain", show=True, log_x=True, log_y=False)
    return


@app.cell
def _(viz):
    viz.plot_optimization_trace(metric_x="tsettle", metric_y="dcgain", show=True, log_x=True, log_y=False)
    return


if __name__ == "__main__":
    app.run()
