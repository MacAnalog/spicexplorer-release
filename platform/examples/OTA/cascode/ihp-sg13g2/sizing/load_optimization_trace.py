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
    **Does not run today, and has no saved outputs.** It reads the run folders `auto_save/CASCODE-OTA_<optimizer>_<date>_<time>/` beside it, which are git-ignored and in no repository, so `python` on this file stops at the Option 2 cell (KeyError: 'CASCODE-OTA'). The CSV files it wrote for four of the runs it names, the selected `CASCODE-OTA_LHSSearch_2026-02-07_10-53-21` among them, are in `../../NEWCAS_SUBMISSION_APPENDIX/`.
    """)
    return


@app.cell
def _():
    from spicexplorer.optimization      import Circuit_Optimizer_Orchestrator_with_SPICE
    from spicexplorer.viz               import Optimization_Log_Visualizer
    from spicexplorer.core.domains      import OptimizationLog, OptimizationLogEntry
    from spicexplorer_core.logging.logger_setup               import setup_loggers_with_spicelib_suppression as setup_loggers

    from pathlib import Path
    from typing import List, Dict, Tuple, Any

    import os
    import re

    logger = setup_loggers()
    logger.info("Plotting Notebool imports completed.")
    return (
        Dict,
        List,
        OptimizationLog,
        Optimization_Log_Visualizer,
        Path,
        logger,
        os,
        re,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Helper Functions
    """)
    return


@app.cell
def _(Dict, List, Path, logger, os, re):
    def find_project_folders(path: str | Path) -> List[Path]:  # pyright: ignore[reportInvalidTypeForm]
        # Matches: project_optimizer_YYYY-MM-DD_HH-MM-SS
        pattern = re.compile(r'^[^_]+_[^_]+_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$')
    
        matches: List[Path] = []  # pyright: ignore[reportInvalidTypeForm]
        if not os.path.exists(path):
            return matches

        for entry in os.scandir(path):
            if entry.is_dir() and pattern.match(entry.name):
                matches.append(Path(entry.path))
            
        return matches

    def find_project_folders_nested(base_path: str | Path) -> Dict[str, Dict[str, Dict[str, Path]]]:  # pyright: ignore[reportInvalidTypeForm]
        """
        Returns a nested dictionary: {project_name: {optimizer: [(timestamp: path)]}}
        """
        # Pattern: project_optimizer_YYYY-MM-DD_HH-MM-SS
        pattern = re.compile(r'^([^_]+)_([^_]+)_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})$')
    
        path_obj = Path(base_path)
        nested_results: Dict[str, Dict[str, Dict[str, Path]]] = {}  # pyright: ignore[reportInvalidTypeForm]

        if not path_obj.exists():
            return nested_results

        # Use iterdir() for Path-based iteration
        for folder in path_obj.iterdir():
            if folder.is_dir():
                match = pattern.match(folder.name)
                if match:
                    # Capture groups from the regex
                    project, optimizer, timestamp = match.groups()
                
                    # Initialize nested levels if they don't exist
                    if project not in nested_results:
                        nested_results[project] = {}
                    if optimizer not in nested_results[project]:
                        nested_results[project][optimizer] = {}
                
                    # Assign the Path object
                    nested_results[project][optimizer][timestamp] = folder
                
        return nested_results

    def extract_json_data(target_dirs: List[Path]) -> Dict[str, List[Path]]:  # pyright: ignore[reportInvalidTypeForm]
        combined_data: Dict[str, List[Path]] = {}  # pyright: ignore[reportInvalidTypeForm]
        for dir_path in target_dirs:
            if not isinstance(dir_path, Path): dir_path = Path(dir_path)
            combined_data[dir_path.name] = [Path(file.path )for file in os.scandir(dir_path) if (file.is_file() and file.name.endswith('.json'))]
            logger.info(f"directory {dir_path.name} has {len(combined_data[dir_path.name])} json files")
            
        return combined_data

    return extract_json_data, find_project_folders_nested


@app.cell
def _(List, Path, find_project_folders_nested):
    def get_runs(project: str, optimizer: str, base_path: str | Path) -> List[Path]:  # pyright: ignore[reportInvalidTypeForm]
        nested_results = find_project_folders_nested(base_path=base_path)
        return list(nested_results[project][optimizer].values())

    return (get_runs,)


@app.cell
def _(OptimizationLog, Optimization_Log_Visualizer, logger):
    def load_from_json_list(json_path_list) -> Optimization_Log_Visualizer:  # pyright: ignore[reportInvalidTypeForm]
        viz = Optimization_Log_Visualizer(optimization_log=OptimizationLog(initial_logs=[]))
        logger.info(f"initial viz size: {len(viz.optimization_log.log)}")
        for path_to_checkpoint in json_path_list:
            loaded_ckpt = Optimization_Log_Visualizer.load_checkpoint(path_to_checkpoint=path_to_checkpoint)
            logger.info(f"initial loaded size: {len(loaded_ckpt.optimization_log.log)}")
            for entry in loaded_ckpt.optimization_log.log:
                viz.optimization_log.append(entry=entry)

            logger.info(f"current loaded size: {len(viz.optimization_log.log)}")
        logger.info(f"final viz size: {len(viz.optimization_log.log)}")

        return viz

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Loading Results
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Option 1

    ```python
    # Option (1) to load
    # --------------------------------

    # target_dirs: List[Path] = find_project_folders(mo.notebook_dir() / 'auto_save')
    # print(target_dirs)
    # results = extract_json_data(target_dirs=target_dirs)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Option 2
    """)
    return


@app.cell
def _(extract_json_data, get_runs, mo):
    # Option (2) to load
    # -------------------------------- 

    targets_for_optimizer = get_runs(project="CASCODE-OTA", optimizer="LHSSearch", base_path=mo.notebook_dir() / 'auto_save')
    # targets_for_optimizer = get_runs(project="CASCODE-OTA", optimizer="LogMultiBFGSPlus", base_path=mo.notebook_dir() / 'auto_save')
    # targets_for_optimizer = get_runs(project="CASCODE-OTA", optimizer="LogBFGSCMAPlus", base_path=mo.notebook_dir() / 'auto_save')
    # targets_for_optimizer = get_runs(project="CASCODE-OTA", optimizer="LhsDE", base_path=mo.notebook_dir() / 'auto_save')
    # targets_for_optimizer = get_runs(project="CASCODE-OTA", optimizer="TinyCMA", base_path=mo.notebook_dir() / 'auto_save')

    results_for_optimizer = extract_json_data(target_dirs=targets_for_optimizer)
    results_for_optimizer
    return (results_for_optimizer,)


@app.cell
def _(logger, results_for_optimizer):
    idx = "CASCODE-OTA_LHSSearch_2026-02-07_10-53-21"

    # idx = "CASCODE-OTA_LhsDE_2026-02-07_10-54-54"
    # idx = "CASCODE-OTA_LhsDE_2026-02-07_14-53-23"

    # idx = "CASCODE-OTA_TinyCMA_2026-02-07_10-51-36"

    # idx = "CASCODE-OTA_LogMultiBFGSPlus_2026-02-07_10-58-00"
    # idx = "CASCODE-OTA_LogBFGSCMAPlus_2026-02-08_00-01-55"


    # json_path_list  = results[idx]
    json_path_list  = results_for_optimizer[idx]
    json_path       = json_path_list[-1]

    logger.info(f"selected run = {idx}")
    logger.info(f"selected path:  {json_path}")
    logger.info(f"list (len {len(json_path_list)}) : {json_path_list}")
    return idx, json_path


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Constructing the Optimization_Log_Visualizer object
    """)
    return


@app.cell
def _(Optimization_Log_Visualizer, json_path, logger):
    viz = Optimization_Log_Visualizer.load_checkpoint(path_to_checkpoint=json_path)
    logger.info(f"loaded count {len(viz.optimization_log)}")

    # viz = load_from_json_list(json_path_list=json_path_list)
    return (viz,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Exporting to CSV and Pandas Dataframe
    """)
    return


@app.cell
def _(viz):
    score_df = viz.extract_best_score_evolution(include_metrics=True, running_avg_n=10)
    return (score_df,)


@app.cell
def _(idx, logger, mo, score_df):
    # description = "relAbs-loss"
    description = "blind-search_sigmoid-loss"
    # description = "sigmoid-loss"
    # description = "BFGS_relativeAbs-loss"

    # top_n       = 100
    # viz.filter_top_n(n=top_n)
    # csv_filename = f"{idx}_{description}_top{top_n}.csv"

    csv_filename = f"{idx}_{description}.csv"
    logger.info(f"will write to {csv_filename}")
    score_df.to_csv(mo.notebook_dir() / f"scores_{csv_filename}")
    return (csv_filename,)


@app.cell
def _(csv_filename, mo, viz):
    viz_df = viz.to_df()
    viz_df.to_csv(mo.notebook_dir() / csv_filename)

    viz_df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Plotting Scores
    """)
    return


@app.cell
def _(viz):
    _ = viz.plot_loss_breakdown(show=True, log_y=False)
    return


@app.cell
def _(viz):
    _ = viz.plot_best_score_evolution(show=True)
    return


@app.cell
def _(viz):
    _ = viz.plot_best_score_evolution(show=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Visualize
    """)
    return


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
    viz.plot_design_space_exploration(param_x="X_DUT_M1CM2C_W", param_y="X_DUT_M1CM2C_L", show=True)
    return


@app.cell
def _(viz):
    viz.plot_design_space_exploration(param_x="X_DUT_V_BIAS_1", param_y="X_DUT_V_BIAS_2", show=True)
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
    viz.plot_optimization_trace(metric_x="ugf", metric_y="pm", show=True, log_x=True, log_y=False)
    return


@app.cell
def _(viz):
    viz.plot_optimization_trace(metric_x="v(inoise_total)", metric_y="dcgain", show=True, log_x=True, log_y=False)
    return


@app.cell
def _(viz):
    viz.plot_optimization_trace(metric_x="dcgain", metric_y="i(idd_total)", show=True, log_x=False, log_y=True)
    viz.plot_optimization_trace(metric_x="ugf", metric_y="i(idd_total)", show=True, log_x=True, log_y=True)
    viz.plot_optimization_trace(metric_x="tsettle", metric_y="dcgain", show=True, log_x=True, log_y=False)
    return


if __name__ == "__main__":
    app.run()
