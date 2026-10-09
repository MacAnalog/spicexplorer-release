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
    from    spicexplorer.core.domains    import Project_Setup

    from spicexplorer_core.logging.logger_setup import setup_loggers

    from pathlib import Path

    logger = setup_loggers()
    logger.info(f"current directory : {Path.cwd()}")
    return (Project_Setup,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Testing the Project Setup Loader
    """)
    return


@app.cell
def _(Project_Setup, mo):
    path_to_project_setup = mo.notebook_dir() / "project_setup.yaml"
    project_setup = Project_Setup.from_yaml(yaml_path=path_to_project_setup)
    return (project_setup,)


@app.cell
def _(project_setup):
    project_setup.testbenches
    return


@app.cell
def _(project_setup):
    project_setup.list_constraints()
    return


@app.cell
def _(project_setup):
    project_setup.list_params()
    return


@app.cell
def _(project_setup):
    project_setup.summary()
    return


if __name__ == "__main__":
    app.run()
