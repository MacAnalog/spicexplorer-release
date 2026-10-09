import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    # from    spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE, Optimizer_Type_Enum
    from   spicexplorer.core                import Project_Setup
    from   spicexplorer_core.spice_engine        import NGSpice_Wrapper, Ngspice_Plot_Type, Sim_Execution_Type

    from spicexplorer_core.logging.logger_setup import setup_loggers

    from pathlib import Path

    logger = setup_loggers()
    logger.info(f"current directory : {Path.cwd()}")
    return (
        NGSpice_Wrapper,
        Ngspice_Plot_Type,
        Path,
        Project_Setup,
        Sim_Execution_Type,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Testing the NGspice simulator wrapper
    """)
    return


@app.cell
def _(Project_Setup, mo):
    path_to_project_setup = mo.notebook_dir() / "project_setup.yaml"
    project_setup = Project_Setup.from_yaml(yaml_path=path_to_project_setup)

    project_setup.summary()
    return (project_setup,)


@app.cell
def _(NGSpice_Wrapper, Path, Sim_Execution_Type, project_setup):
    tb_1= project_setup.testbenches[0]

    tb_1_wrapper = NGSpice_Wrapper(
        netlist_filename    =   Path(project_setup.ws_root) / Path(tb_1.netlist),
        testbench_name      =   tb_1.name,
        traces_of_interest  =   [],
        output_folder       =   Path(project_setup.ws_root) / Path(project_setup.outdir),
        sim_execution_t     =   Sim_Execution_Type.RUN_AND_WAIT,
        path_to_simulator   =   Path(project_setup.simulator),
        verbose             =   True
    )
    return (tb_1_wrapper,)


@app.cell
def _(tb_1_wrapper):
    tb_1_wrapper.get_tb_params()
    return


@app.cell
def _(tb_1_wrapper):
    tb_1_wrapper.get_dut_params()
    return


@app.cell
def _(tb_1_wrapper):
    tb_1_wrapper.run_sanity_check()
    return


@app.cell
def _(tb_1_wrapper):
    raw_file, log_file, task_name = tb_1_wrapper.run_and_wait()
    return


@app.cell
def _(tb_1_wrapper):
    [plot.get_plot_name() for plot in tb_1_wrapper.curr_raw.plots]
    return


@app.cell
def _(tb_1_wrapper):
    [plot.get_trace_names() for plot in tb_1_wrapper.curr_raw.plots]
    return


@app.cell
def _(tb_1_wrapper):
    tb_1_wrapper.curr_raw
    return


@app.cell
def _(Ngspice_Plot_Type, tb_1_wrapper):
    tb_1_wrapper.extract_scalar_variable_from_raw("ugf", plot_type=Ngspice_Plot_Type.AC)
    return


@app.cell
def _(tb_1_wrapper):
    tb_1_wrapper.get_available_plots()
    return


@app.cell
def _(tb_1_wrapper):
    tb_1_wrapper.clean_up(keep_netlist=True, keep_logs=True)
    return


if __name__ == "__main__":
    app.run()
