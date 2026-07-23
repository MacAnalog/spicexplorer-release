from spicexplorer.optimization.orchestrator import Circuit_Optimizer_Orchestrator_with_SPICE, Optimizer_Type_Enum
from spicexplorer_core.logging.logger_setup import setup_loggers_with_spicelib_suppression as setup_loggers

from pathlib        import Path
from datetime       import datetime

logger = setup_loggers()
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

### (1) Configuration ###

path_to_project_setup = Path("./project_setup.yaml")
optimizer_type = Optimizer_Type_Enum.NEVERGRAD_SINGLE

### (2) Setup ###

orchestrator = Circuit_Optimizer_Orchestrator_with_SPICE(
    project_setup_path=path_to_project_setup,
    optimizer_type=optimizer_type,
    auto_load=False,
    verbose=True
)

# Add timestamp to the out_dir
temp_dir = f"{orchestrator.project_setup.outdir}_{TIMESTAMP}"
orchestrator.project_setup.outdir = f"{orchestrator.project_setup.outdir}_{TIMESTAMP}"
logger.info(f"overwrote project_setup.outdir with {temp_dir}")

orchestrator.initialize()

# Instantiate the optimizer

optimizer = orchestrator.get_optimizer()
optimizer.parameterize()
# orchestrator.run_sanity_on_spicelib_wrapper()

BASE_SAVE_DIR = optimizer.autosave_checkpoint_dir
logger.critical(f"Optimization Script - results will be saved to {BASE_SAVE_DIR.absolute()}")

# optimizer.autosave_checkpoint_freqeucny = 5
optimizer.optimize(render_optimization_trace=False, keep_history=False)


### (3) Saving ###
logger.info("plotting the results...")
optimizer.plot_optimization_trace(metric_x="ugf", metric_y="dcgain", show=False, save_path=BASE_SAVE_DIR/Path("./ugf_dcgain.html"))

optimizer.plot_optimization_trace(metric_y="ugf", metric_x="i(idd_total)", show=False, save_path=BASE_SAVE_DIR/Path("./ugf_idd_total.html"))
optimizer.plot_optimization_trace(metric_y="dcgain", metric_x="i(idd_total)", show=False, save_path=BASE_SAVE_DIR/Path("./dcgain_idd_total.html"))

optimizer.plot_optimization_trace(metric_x="ugf", metric_y="v(inoise_total)", show=False, save_path=BASE_SAVE_DIR/Path("./ugf_inoise.html"))
optimizer.plot_optimization_trace(metric_x="dcgain", metric_y="v(inoise_total)", show=False,  save_path=BASE_SAVE_DIR/Path("./dcgain_inoise.html"))

optimizer.plot_optimization_trace(metric_x="ugf", metric_y="pm", show=False,  save_path=BASE_SAVE_DIR/Path("./ugf_pm.html"))
optimizer.plot_optimization_trace(metric_x="ugf", metric_y="tsettle", show=False,  save_path=BASE_SAVE_DIR/Path("./ugf_tsettle.html"))
optimizer.plot_optimization_trace(metric_x="dcgain", metric_y="tsettle", show=False,  save_path=BASE_SAVE_DIR/Path("./dcgain_tsettle.html"))
optimizer.plot_optimization_trace(metric_x="pm", metric_y="tsettle", show=False,  save_path=BASE_SAVE_DIR/Path("./pm_tsettle.html"))
logger.info("END of plotting the results...")

logger.critical(f"Script - Saving the results...")
save_path = BASE_SAVE_DIR/Path(f"{orchestrator.project_setup.optimizer_config.name}_{orchestrator.project_setup.optimizer_config.budget}_score.html")
optimizer.plot_score(show=False, save_path=save_path)


### NO LONGER NEEDED SINCE THE OPTIMIZER AUTOSAVES

# save_path = BASE_SAVE_DIR/Path(f"{orchestrator.project_setup.optimizer_config.name}_{orchestrator.project_setup.optimizer_config.budget}")
# optimizer.save_checkpoint(name=save_path)