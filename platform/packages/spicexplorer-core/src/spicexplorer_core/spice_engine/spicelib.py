from __future__ import annotations

import logging
import os
import re
import shutil
import threading
from enum import Enum
from pathlib import Path
from time import sleep

# For typing
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import numpy as np
from spicelib import AscEditor, RawRead, SimRunner, SpiceEditor
from spicelib.editor.base_editor import ComponentNotFoundError, ParameterNotFoundError
from spicelib.sim.run_task import RunTask as SpicelibRunTaskClass

# Import simulation runners
from spicelib.simulators.ngspice_simulator import NGspiceSimulator

if TYPE_CHECKING:
    # Type-checking only. `Corner` now lives in the core package alongside this
    # module (spicexplorer_core.pvt); kept under TYPE_CHECKING to avoid any
    # import-time cost.
    from spicexplorer_core.pvt import Corner

from spicexplorer_core.logging import setup_loggers
from spicexplorer_core.spice_engine.deck_prep import noise_needs_sparse, plan_slim_swap

logger = logging.getLogger("spicexplorer.spice_engine.spicelib")

# Output folders this *process* has already wiped-for-a-clean-start (resolved abs paths).
# A wrapper clears a STALE `output_folder` exactly once per process (so a lone wrapper still
# gets its documented fresh slate); sibling wrappers that legitimately SHARE that folder —
# e.g. the orchestrator builds one wrapper per testbench, all pointed at the project `outdir`
# — must NOT re-wipe it, because doing so destroys the earlier siblings' setup/run artifacts
# *mid-construction*. Tracking wiped folders here keeps single-wrapper behaviour intact while
# making N-wrapper construction safe. Guarded by a lock for the (rare) threaded-build case.
_WIPED_OUTPUT_FOLDERS: set[Path] = set()
_WIPED_OUTPUT_FOLDERS_LOCK = threading.Lock()


# ---------------------------------
# Enums Definition
# ---------------------------------
class Sim_Engines_Type(Enum):
    LTSPICE = "ltspice"
    NGSPICE = "ngspice"
    XYCE    = "xyce"

class Sim_Execution_Type(Enum):
    RUN_AND_WAIT        = "RUN_AND_WAIT"
    RUN_AND_PASS        = "RUN_AND_PASS"
    RUN_NOW             = "RUN_NOW"
    RUN_WITH_CALLBACK   = "RUN_WITH_CALLBACK"

class Ngspice_Plot_Type(Enum):
    AC = "AC Analysis"
    OP = "Operating Point"
    NOISE_1 = "Integrated Noise"
    NOISE_2 = "Noise Spectral Density Curves"
    TRAN = "Transient Analysis"
    # ngspice titles a `.dc`/`dc` sweep plot "DC transfer characteristic" (NOT "DC Analysis");
    # the RawRead plot lookup matches this enum's value against that title, so a `sim_type: dc`
    # target (e.g. an LDO load/line-regulation deck's `let load_reg`) reads its vector instead of
    # silently returning NaN against a name that never appears in the raw.
    DC = "DC transfer characteristic"

# ---------------------------------
# Analysis-string ↔ plot-type resolution (the `SimResult` analysis vocabulary)
# ---------------------------------
# The `SimResult` protocol keys results by an engine-neutral `analysis: str`. For ngspice
# that string resolves to an `Ngspice_Plot_Type`. Canonical keys mirror the optimizer's
# `SimType` values ("ac"/"dc"/"op"/"tran"/"noise"/"noise_spectrum") so callers speak one
# vocabulary across engines — but this map lives in `core` (which must not import the
# optimizer package), so it is defined here independently.
_ANALYSIS_TO_PLOT_TYPE: Dict[str, Ngspice_Plot_Type] = {
    "ac": Ngspice_Plot_Type.AC,
    "dc": Ngspice_Plot_Type.DC,
    "op": Ngspice_Plot_Type.OP,
    "oppoint": Ngspice_Plot_Type.OP,
    "tran": Ngspice_Plot_Type.TRAN,
    "transient": Ngspice_Plot_Type.TRAN,
    "noise": Ngspice_Plot_Type.NOISE_1,
    "noise_integrated": Ngspice_Plot_Type.NOISE_1,
    "noise_spectrum": Ngspice_Plot_Type.NOISE_2,
    "noise_spectral": Ngspice_Plot_Type.NOISE_2,
}


def resolve_ngspice_plot_type(analysis: "str | Ngspice_Plot_Type") -> Ngspice_Plot_Type:
    """Map an engine-neutral `analysis` string to an `Ngspice_Plot_Type`.

    Accepts (case-insensitively): a canonical short key (`"ac"`, `"op"`, `"noise_spectrum"`,
    …), an `Ngspice_Plot_Type` member (passed through), or the enum's own display value
    (`"AC Analysis"`). Raises `ValueError` on anything unrecognised so a typo surfaces
    loudly rather than silently reading the wrong plot.
    """
    if isinstance(analysis, Ngspice_Plot_Type):
        return analysis
    key = str(analysis).strip().lower()
    if key in _ANALYSIS_TO_PLOT_TYPE:
        return _ANALYSIS_TO_PLOT_TYPE[key]
    for pt in Ngspice_Plot_Type:
        if pt.value.lower() == key:
            return pt
    raise ValueError(
        f"Unknown analysis '{analysis}'. Use one of {sorted(_ANALYSIS_TO_PLOT_TYPE)} "
        f"or an Ngspice_Plot_Type value ({[p.value for p in Ngspice_Plot_Type]})."
    )


# ---------------------------------
# Pure RawRead extraction helpers (single source of truth for the SimResult adapter)
# ---------------------------------
# These replicate `NGSpice_Wrapper.extract_wave` / `extract_scalar_variable_from_raw`
# EXACTLY, operating on a standalone `RawRead` rather than `self.curr_raw`. The wrapper's
# own methods are left byte-for-byte untouched (zero behaviour change); `NgspiceSimResult`
# uses these so its numbers are, by construction, the same the optimizer reads today. The
# parity is pinned by unit tests.
def _extract_wave_from_raw(
    raw: RawRead, wave_name: str, plot_type: Ngspice_Plot_Type, is_real: bool = False
) -> np.ndarray:
    target_plot = None
    for p in raw.plots:
        if p.get_plot_name() == plot_type.value:
            target_plot = p
            break
    if target_plot is None:
        raise ValueError(f"Plot type '{plot_type.value}' not found.")
    wave = target_plot.get_wave(wave_name)  # IndexError if the trace is absent
    wave = np.asarray(wave)
    if is_real:
        # np.real(...) rather than `.real` — same values, but avoids a numpy-stub
        # false-positive pyright hits on `NDArray.real` (see extract_wave, untouched).
        return np.real(wave).astype(np.float64)
    return wave


def _extract_scalar_from_raw(
    raw: RawRead, var_name: str, plot_type: Ngspice_Plot_Type, is_real: bool = True
) -> np.float64:
    try:
        wave_data = _extract_wave_from_raw(raw, var_name, plot_type, is_real)
        val = np.asarray(wave_data)
        if val.size > 0:
            return np.float64(val.item(0) if val.ndim > 0 else val.item())
        return np.float64(np.nan)
    except (ValueError, IndexError, RuntimeError):
        return np.float64(np.nan)


# ---------------------------------
# ngspice `SimResult` / `SimHandle` adapters (satisfy spice_engine.protocol structurally)
# ---------------------------------
class NgspiceSimResult:
    """A `SimResult` over one ngspice `RawRead` snapshot.

    Holds its OWN reference to the run's `RawRead`, so it stays valid even after the
    wrapper runs again (the wrapper's `curr_raw` would move on). A `None` backing means
    the sim produced no raw (non-convergence/abort — the documented NaN-metrics
    degradation): `scalar` returns NaN, `wave` raises.

    `log_path` is the run's ngspice log file (or `None`) — the optional duck-typed
    extension the optimizer reads to key `OptimizationLogEntry.log_file`.
    `raw_path` is the parsed `.raw` file's path (or `None`) — spicelib's `RawRead`
    does not retain its filename, so the wrapper records it here; this is the
    artifact seam `CircuitRun.artifact_path()` (→ waveview snapshots) reads.
    """

    def __init__(
        self,
        raw: RawRead | None,
        log_path: str | Path | None = None,
        raw_path: str | Path | None = None,
    ) -> None:
        self._raw = raw
        self.log_path: str | Path | None = log_path
        self.raw_path: str | Path | None = raw_path
        # Post-sim canonical scalars (Tier-1 measurements keyed by target-spec name),
        # consulted FIRST in `scalar` so a merged metric wins over any RAW variable of the
        # same name — the engine-neutral twin of SpectreSimResult._merged, letting the
        # optimizer's measurement path (measure_integration) treat both engines uniformly.
        self._merged: dict[str, float] = {}

    @property
    def raw(self) -> RawRead | None:
        return self._raw

    def merge_scalars(self, scalars: dict[str, float]) -> None:
        """Fold post-sim canonical scalars (Tier-1 measurements keyed by target-spec name)
        in, so `scalar(name, analysis)` returns them. Authoritative: consulted before the
        RAW variables, so a canonical metric wins on a name collision."""
        for key, value in scalars.items():
            self._merged[str(key)] = float(value)

    def scalar(self, name: str, analysis: str, is_real: bool = True) -> float:
        if name in self._merged:  # merged canonical scalars are authoritative
            return self._merged[name]
        if self._raw is None:
            return float(np.nan)
        plot_type = resolve_ngspice_plot_type(analysis)
        return float(_extract_scalar_from_raw(self._raw, name, plot_type, is_real))

    def wave(self, name: str, analysis: str, is_real: bool = False) -> np.ndarray:
        if self._raw is None:
            raise RuntimeError(
                "No simulation data (raw is None — the run produced no RAW file)."
            )
        plot_type = resolve_ngspice_plot_type(analysis)
        return _extract_wave_from_raw(self._raw, name, plot_type, is_real)


class NgspiceSimHandle:
    """A `SimHandle` over a spicelib `RunTask` (the non-blocking `run_and_pass` path).

    `is_done()` maps to `not task.is_alive()`; `result()` blocks until the task finishes,
    then reads its `(raw, log)` into a fresh `NgspiceSimResult` — degrading to a `None`
    backing when the run left no RAW file, exactly like `NGSpice_Wrapper.load_task_outputs`.
    """

    def __init__(self, task: SpicelibRunTaskClass) -> None:
        self._task = task
        self._result: NgspiceSimResult | None = None

    @property
    def task(self) -> SpicelibRunTaskClass:
        """The underlying spicelib `RunTask` (used by `NGSpice_Wrapper.collect`)."""
        return self._task

    def is_done(self) -> bool:
        return not self._task.is_alive()

    def result(self) -> NgspiceSimResult:
        if self._result is not None:
            return self._result
        while self._task.is_alive():
            sleep(0.01)
        out = self._task.get_results()
        raw: RawRead | None = None
        log_file = None
        raw_path = None
        if isinstance(out, tuple) and len(out) == 2:
            raw_file, log_file = out
            if raw_file is not None and Path(raw_file).exists():
                raw = RawRead(raw_filename=raw_file)
                raw_path = raw_file
        self._result = NgspiceSimResult(raw, log_path=log_file, raw_path=raw_path)
        return self._result


# ---------------------------------
# Class Definitions
# ---------------------------------
class LTspice_Wrapper:
    def __init__(self, asc_filename: str, traces_of_interest: List[str] = [], dump_parent_folder: str = "runner", verbose: bool = False):
        """Reads and simulates the circuit defined in the given .asc file"""
        self.asc_filename: str = asc_filename
        self.netlist: AscEditor = AscEditor(asc_file=asc_filename)
        self.simengine: type[NGspiceSimulator] = NGspiceSimulator

        output_folder = f"{dump_parent_folder}/{self.simengine.__name__}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.runner: SimRunner = SimRunner(simulator=self.simengine, verbose=verbose, output_folder=output_folder)
        self.output_folder = output_folder
        self.verbose = verbose

        if not self.validate_runner():
            raise RuntimeError("Runner Cannot be validated --- check LTspice simulator is available to spicelib")


        # Storing Simulation Runs
        self.traces:     List[str]    = traces_of_interest
        self.curr_raw: RawRead  = None
        self.tasks: Dict[SpicelibRunTaskClass] = {}

    def validate_runner(self) -> bool:
        """Validation logic to check SPICE simulator is loaded correctly"""

        if len(self.runner.simulator.get_default_library_paths()) < 1:
            print(f"* default libs for {self.runner.simulator.__name__} cannot be ressolved")
            return False

        if len(self.runner.simulator.spice_exe) < 1:
            print(f"* spice_exe for {self.runner.simulator.__name__} cannot be ressolved")
            return False

        return True

    def update_params(self, parameterization: Dict[str, float]) -> bool:
        # Values arrive ALREADY in absolute SI (eng strings like "50f" resolve to floats
        # via parse_value upstream) and param names carry NO unit convention — set them
        # verbatim, exactly like NGSpice_Wrapper.update_params. The previous code
        # appended a unit by NAME PREFIX (C* → 'p', R* → 'k'), a dead convention that
        # silently corrupted any C*/R* param (CL 5e-14 became "5e-14p" = 5e-26 F).
        for key, value in parameterization.items():

            try: # Validate parameter already exists
                self.netlist.get_parameter(key)
            except ParameterNotFoundError:
                return False

            self.netlist.set_parameter(key, f"{value}")

        return True

    def update_component_values(self, parameterization: Dict[str, float]) -> bool:
        # Same verbatim-SI rule as update_params (the C*/R* unit-suffix convention is dead).
        for key, value in parameterization.items():

            try: # Validate parameter already exists
                self.netlist.get_parameter(key)
            except ParameterNotFoundError:
                return False

            self.netlist.set_component_value(key, f"{value}")

        return True

    def update_component_parameters(self, parameterization: Dict[str, Dict[str, float]]) -> bool:
        for component_name, component_parameters in parameterization.items():
            try:
                self.netlist.set_component_parameters(component_name, **component_parameters)
            except ComponentNotFoundError:
                return False

        return True

    @classmethod
    def callback(raw_file: str, log_file: str, traces_to_read: str):
        raw_read = RawRead(raw_filename=raw_file, traces_to_read=traces_to_read)
        return raw_read

    def run_and_wait(self, exe_log: bool = True) -> Tuple[RawRead, str]:

        task = self.runner.run(self.netlist, exe_log=exe_log)

        while task.is_alive():
            pass # wait so its done

        raw_file, log_file = task.get_results()
        self.tasks[task.name] = (raw_file, log_file)

        self.curr_raw = RawRead(raw_filename=raw_file)

        return self.curr_raw, task.name

    # def run_with_callback(self):
    #     pass

    def extract_wave(self, wave_name: str, is_real: bool = False) -> np.ndarray:

        if self.curr_raw is None:
            raise RuntimeError("Need to run the simulation at least once")

        wave = np.asarray(self.curr_raw.get_wave(wave_name))

        if is_real:
            return wave.real.astype(np.float64)

        return wave

class NGSpice_Wrapper:
    def __init__(self,
                 netlist_filename:      Path,
                 traces_of_interest:    List[str] = [],
                 testbench_name:        str = "DEFAULT",
                 output_folder:         Path = Path("./spicelib_runs"),
                 sim_execution_t:       Sim_Execution_Type = Sim_Execution_Type.RUN_AND_WAIT,
                 path_to_simulator:     None | Path = None,
                 verbose:               bool = False,
                 ):
        """Reads, modifies, and simulates the circuit defined in the given netlist_filename .spice file"""
        # self.logger = setup_loggers(parent_folder=output_folder.parent, out_logname=project_name)
        self.logger = logger

        self.netlist_filename   = netlist_filename
        self.traces_of_interest = traces_of_interest
        self.testbench_name     = testbench_name
        self.output_folder      = output_folder
        self.path_to_simulator  = path_to_simulator
        self.sim_execution_t    = sim_execution_t
        self.verbose            = verbose

        self._default_compatibility_mode: str   = "a"   # ngspice compatibility mode (refer to spicelib and ngspice docs for details)
        # DISPLAY-ONLY heuristic for get_dut_params/get_tb_params (matched
        # case-insensitively): many decks name their sizing knobs x_dut_*, but the
        # convention is NOT load-bearing — LDO decks size w_pass/i_tail, and the
        # optimizer's real DUT-param list is the project YAML's dut_params. Nothing in
        # the run path branches on a parameter's name.
        self._dut_parameter_prefix: str         = "X_DUT"

        self.runner: SimRunner | None       = None
        self.editor: None | SpiceEditor     = None
        self.tasks_outputs: Dict[str, Any]  = {}    # task name -> (raw, log) Tuple[Path, Path]
        self.curr_raw: RawRead | None       = None
        self.curr_log: str | None           = None
        # RawRead does not retain its filename — track the parsed raw's path alongside
        self.curr_raw_path: str | None      = None

        self._counter: int = 1

        self.__post_init__()
    # ----------------------------------------------------
    # [Private] Initialization and Validation
    # ----------------------------------------------------
    def __post_init__(self):
        # (1) Validate the settings
        if not self._validate():
            raise RuntimeError("Spicelib wrapper validation failed")

        # (2) Create the simulator
        simulator : type[NGspiceSimulator] = self._create_simulator()

        # (3) Create the runner
        self.runner = SimRunner(
            simulator=simulator,
            output_folder=self.output_folder,
            verbose=self.verbose
            )

        # (4) Create a SpiceEditor Instance
        self.editor = SpiceEditor(netlist_file=self.netlist_filename)

        # (5) print circuit info
        self.print_circuit_info()

    def _validate(self) -> bool:
        # The output folder is WIPED below — refuse to wipe a folder that contains the input
        # netlist itself (a mis-pointed output_folder must not destroy the user's netlist).
        netlist_abs = Path(self.netlist_filename).resolve()
        out_abs = Path(self.output_folder).resolve()
        if netlist_abs == out_abs or netlist_abs.is_relative_to(out_abs):
            raise ValueError(
                f"output_folder ({self.output_folder}) contains the input netlist "
                f"({self.netlist_filename}) and would be deleted — give the wrapper its own "
                f"disposable output directory"
            )
        # Prepare the output folder. The wipe-on-construction gives a lone wrapper a clean
        # slate, but is DESTRUCTIVE when sibling wrappers share one folder (the orchestrator
        # builds one wrapper per testbench, all pointed at the project `outdir`): the 2nd..Nth
        # wrapper's rmtree would delete the 1st's freshly-prepared folder mid-construction.
        # So wipe a given folder only ONCE per process; siblings that share it reuse it.
        out_resolved = out_abs  # already Path(self.output_folder).resolve() from the guard above
        with _WIPED_OUTPUT_FOLDERS_LOCK:
            already_wiped_this_process = out_resolved in _WIPED_OUTPUT_FOLDERS
            if os.path.exists(self.output_folder):
                if already_wiped_this_process:
                    self.logger.info(
                        f"📂 Reusing output directory already prepared this session "
                        f"(not re-wiping — a sibling wrapper may share it): {self.output_folder}"
                    )
                else:
                    self.logger.warning(f"⚠️ Output directory already exists, re-creating: {self.output_folder}")
                    shutil.rmtree(self.output_folder)
            else:
                self.logger.info(f"📂 Creating output directory for the first time: {self.output_folder}")

            # exist_ok=True: in the shared-folder reuse path we deliberately did NOT rmtree,
            # so the directory is still present and must not raise.
            os.makedirs(self.output_folder, exist_ok=True)
            _WIPED_OUTPUT_FOLDERS.add(out_resolved)

        # Check for netlist existence
        if not self.netlist_filename.exists():
            self.logger.critical(f"❌ Initial netlist not found: {self.netlist_filename}")
            self.logger.critical(f"Check the PWD: {Path.cwd()}")
            raise FileNotFoundError(f"Initial netlist not found: {self.netlist_filename}")

        # Log project info
        self.logger.info("--------------------------------------------------")
        self.logger.info("🚀 Spicelib_Wrapper initialized successfully!")
        self.logger.info(f"\t📝 Testbench: {self.testbench_name}")
        self.logger.info(f"\t📜 Schematic: {self.netlist_filename.stem}")
        self.logger.info(f"\t📂 Output Folder: {self.output_folder}")
        self.logger.info("--------------------------------------------------")
        return True

    def _create_simulator(self) -> type[NGspiceSimulator]:
        if self.path_to_simulator is not None:
            simulator = NGspiceSimulator.create_from(path_to_exe=self.path_to_simulator)
        else:
            simulator = NGspiceSimulator
        simulator.set_compatibility_mode(self._default_compatibility_mode)

        self.logger.info(f"Using ngspice from {simulator.spice_exe}")
        return simulator

    def _move_to_run_folder(self, label: str | None = "") -> Path:
        if self.runner is None or self.editor is None:
            raise RuntimeError("Runner or Editor not initialized")

        if isinstance(self.runner.output_folder, Path):
            self.runner.output_folder = self.runner.output_folder / f"run_{self._counter}_{label}"
            self.runner.output_folder.mkdir(parents=True, exist_ok=True)
            self._counter += 1
        else: raise RuntimeError("Runner output folder is not a Path instance")

        return self.runner.output_folder

    def _restore_parent_folder(self) -> None:
        if self.runner is None:
            raise RuntimeError("Runner not initialized")

        if isinstance(self.runner.output_folder, Path):
            self.runner.output_folder = self.runner.output_folder.parent
        else:
            raise RuntimeError("Runner output folder is not a Path instance")

    def _clear_loaded_sim_data(self) -> None:
        self.curr_raw = None
        self.curr_log = None
        self.curr_raw_path = None

    # ----------------------------------------------------
    # [Public] Simulation Running Methods
    # ----------------------------------------------------
    def update_params(self, parameterization: Dict[str, float]) -> bool:
        logger = self.logger
        logger.debug("Updating parameters...")
        if self.editor is None:
            raise RuntimeError("Editor not initialized")

        for key, value in parameterization.items():
            try:  # Validate parameter already exists
                self.editor.get_parameter(key)
            except ParameterNotFoundError:
                # A testbench whose netlist doesn't declare this param (e.g. a loopgain
                # tb that omits CL/VCM) must NOT abort the whole run — keep the netlist's
                # own default and move on. (Was: log ERROR + `return False`, which killed
                # the optimization the moment one testbench/netlist was inconsistent.)
                logger.warning(
                    f"⚠️ Parameter {key} is not declared in this testbench netlist — "
                    f"skipping it (keeping the netlist's own default)."
                )
                continue

            # Values arrive ALREADY in absolute SI: engineering YAML strings ("50f") are
            # resolved to floats (5e-14) by parse_value before they reach here. So set the
            # value directly. The previous code appended a unit by NAME PREFIX —
            # C* → 'p' (pico), R* → 'k' (kilo) — which DOUBLE-converted: e.g. CL 5e-14
            # became "5e-14p" = 5e-26 F (1e12× too small), silently corrupting capacitor
            # params (the only C*/R* param in the examples is CL).
            self.editor.set_parameter(key, f"{value}")
            logger.debug(f"... Parameter {key} set to {value:.3e}")
        logger.debug("✅  Parameters updated (any undeclared ones were skipped)")
        return True

    def _strip_matching_instructions(self, pattern: str) -> bool:
        """Remove every netlist line whose start matches `pattern` (case-insensitive).

        A thin wrapper over the editor's `remove_Xinstruction` that first checks for a
        match, so we avoid spicelib emitting a misleading ERROR log when there is
        nothing to strip (the common case on the first corner apply).
        """
        if self.editor is None:
            raise RuntimeError("Editor not initialized")
        regex = re.compile(pattern, re.IGNORECASE)
        if any(isinstance(ln, str) and regex.match(ln) for ln in self.editor.netlist):
            self.editor.remove_Xinstruction(pattern)
            return True
        return False

    def apply_corner(self, corner: "Corner", model_lib_root: str | None = None) -> None:
        """Apply a PVT `Corner` to this testbench's netlist editor (one-time setup).

        Concretely, for the chosen corner this:
          1. strips the netlist's hardcoded `.lib <file> <section>` selection for each
             library the corner references, then re-adds the corner's selection
             (ordered, cross-family) — so a `tt` netlist can be switched to `ss`/`ff`;
          2. sets the simulation temperature authoritatively via `.options temp=<val>`
             (a bare `.param temp` does NOT change ngspice's actual temperature);
          3. overrides supply rails and any extra per-corner `.param`s.

        This is the ONLY ngspice-specific corner-emission seam: a future simulator
        backend (e.g. Spectre `include`/`section`) overrides this method. It is
        idempotent — re-applying a corner replaces rather than accumulates directives.

        :param corner: the resolved `core.domains.Corner` to apply.
        :param model_lib_root: optional directory prepended to each `lib_file`, so a
            corner is portable across machines. `None` keeps the netlist's own `.lib`
            search path / PDK env (current behavior).
        """
        if self.editor is None:
            raise RuntimeError("Editor not initialized; cannot apply corner")
        ed = self.editor
        log = self.logger
        log.info(f"🌡️  Applying PVT corner '{corner.name}' to testbench '{self.testbench_name}'")

        # (1) process model includes — strip the netlist's prior `.lib <file> <section>` selection
        #     for each referenced library EXACTLY ONCE (path-agnostic: matches a bare basename or a
        #     full path), THEN add all corner includes. Stripping inside the per-include loop would
        #     delete a sibling section of the SAME lib_file that an earlier include just added,
        #     collapsing multiple sections of one `.lib` to only the last (BUG-B11). Re-apply stays
        #     idempotent: the upfront strip also removes any prior corner's includes for those libs.
        stripped_libs: set[str] = set()
        for inc in corner.model_includes:
            basename = Path(inc.lib_file).name
            if basename not in stripped_libs:
                self._strip_matching_instructions(rf"^\s*\.lib\s+\S*{re.escape(basename)}\s+\S+")
                stripped_libs.add(basename)
        for inc in corner.model_includes:
            path = inc.lib_file if not model_lib_root else str(Path(model_lib_root) / inc.lib_file)
            ed.add_instruction(f".lib {path} {inc.section}")
            log.info(f"\t🧩 .lib {path} {inc.section}")

        # (2) temperature — append an authoritative `.options temp=` (ngspice processes .options
        #     cumulatively, last temp wins). Strip only a prior STANDALONE injected temp line (for
        #     re-apply idempotency); do NOT strip a COMBINED line like `.options temp=27 gmin=1e-12`,
        #     which the old broad regex deleted whole — dropping the sibling options (BUG-B30).
        #     ALSO strip any `.temp <val>` card: ngspice gives `.temp` PRECEDENCE over
        #     `.options temp=`, so a netlist-hardcoded `.temp 27` silently pinned every corner
        #     to 27°C while the injected option looked correct in the netlist.
        self._strip_matching_instructions(r"^\s*\.temp\s+\S+")
        self._strip_matching_instructions(r"^\s*\.options?\s+temp\s*=\s*\S+\s*$")
        ed.add_instruction(f".options temp={corner.temp}")
        log.info(f"\t🌡️  .options temp={corner.temp}")

        # (2b) extra simulator options (e.g. a Monte Carlo sample's RNG seed —
        #      `.options seed=<n>` re-rolls the model library's agauss() draws per
        #      run). Same standalone-line strip discipline as temp for idempotency.
        for k, v in corner.options.items():
            self._strip_matching_instructions(rf"^\s*\.options?\s+{re.escape(str(k))}\s*=\s*\S+\s*$")
            ed.add_instruction(f".options {k}={v}")
            log.info(f"\t🎛️  .options {k}={v}")

        # (3) environment overrides — supplies then extra params (override `.param` defaults).
        #     A supply override is a `.param <node>=<value>`; spicelib's set_parameter SILENTLY
        #     INSERTS a dangling `.param` when <node> isn't already declared, so a mis-named rail
        #     (e.g. the source instance `Vdd` instead of the param `VDD`, or an undeclared `VSS`)
        #     would leave the sim at the netlist's DEFAULT supply with no error. Warn loudly when
        #     the node isn't a declared `.param` so this isn't silent (BUG-B12).
        try:
            declared = {str(n).upper() for n in ed.get_all_parameter_names()}
        except Exception:
            declared = None  # param introspection unavailable → skip the check, still apply
        for s in corner.supplies:
            if declared is not None and str(s.node).upper() not in declared:
                log.warning(
                    f"⚠️ PVT corner '{corner.name}': supply node '{s.node}' is NOT a declared "
                    f".param in testbench '{self.testbench_name}' — this override adds a dangling "
                    f".param and will NOT change the supply. 'node' must match a .param name "
                    f"(e.g. .param VDD=...). Declared params: {sorted(declared)}"
                )
            ed.set_parameter(s.node, s.value)
            log.info(f"\t🔌 .param {s.node}={s.value}")
        for k, v in corner.params.items():
            ed.set_parameter(k, v)
            log.info(f"\t⚙️  .param {k}={v}")

    def run_sanity_check(self, use_editor: bool = True, sim_execution_t: Sim_Execution_Type = Sim_Execution_Type.RUN_NOW, clean_up_after: bool = True) -> bool:
        logger = self.logger

        # (1) Pre-body
        if self.runner is None or self.editor is None:
            logger.critical("💥 Runner or Editor not initialized!")
            raise RuntimeError("Runner or Editor not initialized")

        # (1.1) Create a dedicated folder for sanity check
        if isinstance(self.runner.output_folder, Path):
            logger.info("📂 Creating dedicated sanity check folder...")
            self.runner.output_folder = self.runner.output_folder / "sanity_check"
            self.runner.output_folder.mkdir(parents=True, exist_ok=True)
            self._counter += 1
        else:
            logger.critical("❌ Runner output folder is not a Path instance!")
            raise RuntimeError("Runner output folder is not a Path instance")

        # (2) Run the simulation with the parameters already in the netlist
        logger.info("🧪 Running sanity check simulation...")

        netlist_used = self.editor if use_editor else self.netlist_filename
        run_filename = f"{self.testbench_name}_sanity.spice"
        raw, log = None, None

        # Allow running sanity check with different execution types
        if sim_execution_t == Sim_Execution_Type.RUN_NOW:
            logger.debug("⚡ Executing simulation immediately (RUN_NOW)")
            raw, log = self.runner.run_now(
                netlist=netlist_used,
                exe_log=True,
                run_filename=run_filename
            )
            logger.info(f"simulator log: {log}")
            logger.info(f"simulator RAW: {raw}")
        elif sim_execution_t == Sim_Execution_Type.RUN_AND_WAIT:
            logger.debug("⏳ Running simulation and waiting for completion...")
            self.run_and_wait(exe_log=True)
        elif sim_execution_t == Sim_Execution_Type.RUN_WITH_CALLBACK:
            logger.warning("🛑 RUN_WITH_CALLBACK not implemented yet 🚧")
            raise NotImplementedError("RUN_WITH_CALLBACK simulation execution type is not implemented yet :(")
        else:
            logger.critical("🚨 Invalid sim_execution_t provided!")
            raise RuntimeError("Invalid sim_execution_t")

        # (3) Check the simulation ran successfully
        logger.info("🔎 Verifying simulation results...")
        if log is None or log.suffix == ".fail":
            logger.error("❌ Sanity check failed: log is .fail")
            return False
        if raw is None:
            logger.error("❌ Sanity check failed: RAW is None")
            return False
        if not raw.exists():
            logger.error("❌ Sanity check failed: RAW returned but generation failed")
            return False
        if not log.exists():
            logger.error("❌ Sanity check failed: log returned but generation failed")
            return False

        logger.info("✅ Sanity check passed 🎉")

        # (4) Move out of the sanity check folder
        if isinstance(self.runner.output_folder, Path):
            logger.debug("📦 Restoring output folder to parent directory")
            self.runner.output_folder = self.runner.output_folder.parent

        # (5) Clean up if needed
        if clean_up_after: self.clean_up(delete_directories=True)

        return True

    def _prepare_ngspice_netlist(self) -> None:
        """Idempotent pre-run deck fixes on the editor (logic + the why live in ``deck_prep``).

        Runs right before EACH sim so it also catches a `.lib` re-injected by ``apply_corner``.
        Both fixes are no-ops once applied, so re-running is cheap:
          (A) swap a full PDK corner lib for its generated slim lib (parse-time speedup,
              identical results) when :func:`~spicexplorer_core.spice_engine.deck_prep.plan_slim_swap`
              allows it — data-driven per PDK, PDK-agnostic here;
          (B) force `.option sparse` on noise decks (ngspice KLU can't run `.noise`).
        """
        if self.editor is None:
            return

        # The raw deck TEXT — SpiceEditor stores a `.subckt` DUT body (and `.control` block)
        # opaquely, so device instances / the `noise` command are NOT in editor.netlist. Read
        # once; used for device coverage (A) and noise detection (B).
        deck_lines: list[str] = []
        try:
            deck_lines = Path(self.netlist_filename).read_text(errors="ignore").splitlines()
        except OSError:
            pass

        # (A) slim corner-lib swap — sections/`.include` from the editor (current corner),
        #     device coverage from the deck text (the .subckt body). The plan carries the
        #     strip patterns (full + prior-slim, the latter keeps multi-corner PVT from
        #     accumulating sections across a re-used editor).
        plan = plan_slim_swap(self.editor.netlist, device_scan_lines=deck_lines)
        if plan is not None:
            self._strip_matching_instructions(plan.full_lib_strip)
            self._strip_matching_instructions(plan.slim_lib_strip)
            for section in plan.sections:
                self.editor.add_instruction(f".lib {plan.slim_lib} {section}")
            self.logger.info(f"\t⚡ slim corner lib: .lib {plan.slim_lib} [{', '.join(plan.sections)}]")

        # (B) noise solver guard
        if noise_needs_sparse(self.editor.netlist, deck_lines, self.testbench_name):
            self.editor.add_instruction(".option sparse")
            self.logger.info("\t🧮 noise analysis → forcing '.option sparse' (KLU can't run .noise)")

    def run_and_wait(self, exe_log: bool = True, label: str | None = None) -> Tuple[RawRead | None, str | None, str]:
        """Runs the simulation and waits for it to complete, returning the RawRead instance (or None), the log filename (or None), and task name.

        ``label`` names this run's artifact subfolder (``run_<n>_<label>``); it
        defaults to the testbench name. Multi-corner callers pass
        ``"<tb>__<corner>"`` so per-corner artifacts of one trial don't collide."""
        # (1) Pre-body
        if self.runner is None or self.editor is None:
            raise RuntimeError("Runner or Editor not initialized")

        # (1.05) apply the native-ngspice pre-run deck fixes (slim lib + noise solver)
        self._prepare_ngspice_netlist()

        # (1.1) Create a dedicated folder for this run
        self._move_to_run_folder(label=label if label is not None else self.testbench_name)

        # (2) Run the simulation with the parameters already in the editor instance
        task = self.runner.run(
            netlist=self.editor,
            exe_log=exe_log)

        if task is None:
            raise RuntimeError("Failed to create a RunTask --- cannot proceed")

        # (3) Wait for the task to complete
        while task.is_alive():
            sleep(0.01)
            pass # wait so its done

        # (4) Get the results
        self.read_and_save_task_outputs(task)

        # Move out of the run folder
        self._restore_parent_folder()

        return self.curr_raw, self.curr_log, task.name

    def run_and_pass(self, exe_log: bool = True, label: str | None = None) -> SpicelibRunTaskClass:
        # (1) Pre-body
        if self.runner is None or self.editor is None:
            raise RuntimeError("Runner or Editor not initialized")

        # (1.05) apply the native-ngspice pre-run deck fixes (slim lib + noise solver)
        self._prepare_ngspice_netlist()

        # (1.1) Create a dedicated folder for this run (see run_and_wait on `label`)
        self._move_to_run_folder(label=label if label is not None else self.testbench_name)

        # (2) Run the simulation with the parameters already in the editor instance
        task = self.runner.run(
            netlist=self.editor,
            exe_log=exe_log)

        if task is None:
            raise RuntimeError("Failed to create a RunTask --- cannot proceed")

        self._restore_parent_folder()

        return task

    # ----------------------------------------------------
    # [Public] `Simulator` protocol surface (spice_engine.protocol)
    # ----------------------------------------------------
    # These two thin methods make `NGSpice_Wrapper` satisfy the `Simulator` Protocol
    # structurally. They add nothing new — `run` IS `run_and_wait` and `submit` IS
    # `run_and_pass`, just returning the engine-neutral `SimResult` / `SimHandle` shims
    # instead of raw spicelib objects. Existing callers keep using `run_and_wait` /
    # `run_and_pass` unchanged; new engine-agnostic code uses `run` / `submit`.
    def run(self, exe_log: bool = True, label: str | None = None) -> NgspiceSimResult:
        """Blocking run → `SimResult`. Thin wrapper over `run_and_wait` (no behaviour change)."""
        self.run_and_wait(exe_log=exe_log, label=label)
        return NgspiceSimResult(self.curr_raw, log_path=self.curr_log, raw_path=self.curr_raw_path)

    def submit(self, exe_log: bool = True, label: str | None = None) -> NgspiceSimHandle:
        """Non-blocking submit → `SimHandle`. Thin wrapper over `run_and_pass` (no behaviour change)."""
        task = self.run_and_pass(exe_log=exe_log, label=label)
        return NgspiceSimHandle(task)

    def collect(self, handle: NgspiceSimHandle) -> NgspiceSimResult:
        """Read a submitted run's outputs back through the wrapper — the legacy path.

        Equivalent to `read_and_save_task_outputs(handle.task)` (so `curr_raw`/`curr_log`
        are refreshed for legacy readers like `plot_solution`, and the RAW is parsed
        exactly once), then snapshots them as a `SimResult`. The optimizer prefers this
        over `handle.result()` when a backend offers it (see `spice_engine.protocol`)."""
        self.read_and_save_task_outputs(handle.task)
        return NgspiceSimResult(self.curr_raw, log_path=self.curr_log, raw_path=self.curr_raw_path)

    @classmethod
    def callback(cls, raw_file: str, log_file: str, traces_to_read: str):
        raw_read = RawRead(raw_filename=raw_file, traces_to_read=traces_to_read)
        return raw_read

    # ----------------------------------------------------
    # [Public] Simulation Results Extraction Methods
    # ----------------------------------------------------
    def read_and_save_task_outputs(self, task: SpicelibRunTaskClass) -> None:
        """Reads and saves the outputs of a previously run task."""
        if task.is_alive():
            logger.warning(f"⚠️ Task {task.name} is still running; cannot read outputs yet")
            self._clear_loaded_sim_data()
            return

        out = task.get_results()
        self.tasks_outputs[task.name] = out

        self.load_task_outputs(task.name)

    def load_task_outputs(self, task_name: str) -> None:
        """Loads the outputs of a previously run task by its name."""
        if task_name not in self.tasks_outputs:
            logger.warning(f"⚠️ Task outputs for {task_name} not found")
            self._clear_loaded_sim_data()
            return

        out = self.tasks_outputs[task_name]

        if isinstance(out, tuple) and len(out) == 2:
            raw_file, log_file = out
            # A hard ngspice failure (non-convergence, abort, timeout) leaves the
            # task's raw_file as None (or pointing at a file that was never
            # written) while still returning the (raw, log) tuple. Feeding that to
            # RawRead raised and KILLED the whole optimization run — the graceful
            # "curr_raw is None → NaN metrics → MAX_PENALTY" degradation the
            # optimizer documents (BUG-B28) was unreachable. Degrade here instead:
            # keep the log (it holds the failure reason) and clear the raw.
            if raw_file is None or not Path(raw_file).exists():
                logger.warning(
                    f"⚠️ Task {task_name} produced no RAW file (sim failed/diverged); "
                    f"its metrics will read as NaN. Log: {log_file}")
                self.curr_raw = None
                self.curr_log = log_file
                self.curr_raw_path = None
                return
            self.curr_raw = RawRead(raw_filename=raw_file)
            self.curr_log = log_file
            self.curr_raw_path = str(raw_file)
        else:
            logger.warning(f"⚠️ Not able to read the RAW or the LOG from task {task_name}")
            self._clear_loaded_sim_data()

    def load_raw(self, raw_file: Path | RawRead) -> None:
        """Loads a RawRead instance from the given raw_file path"""

        if isinstance(raw_file, RawRead):
            self.curr_raw = raw_file
            self.curr_raw_path = None  # RawRead does not retain its filename
            return

        if not raw_file.exists():
            raise FileNotFoundError(f"Raw file not found: {raw_file}")

        self.curr_raw = RawRead(raw_filename=raw_file)
        self.curr_raw_path = str(raw_file)

    def get_available_plots(self) -> List[str]:
        """Helper to see what plots are actually inside the current raw file."""
        if self.curr_raw is None:
            logger.warning("⚠️ No RAW file loaded; cannot get available plots")
            return []
        return self.curr_raw.get_plot_names()

    def extract_wave(self, wave_name: str,  plot_type: Ngspice_Plot_Type, is_real: bool = False) -> np.ndarray:
        """
        The endpiont to extract a waveform from the last simulation run
        Extracts a waveform from the simulation results based on the specific plot type.

        Args:
            wave_name: The name of the trace (e.g., 'v(n001)').
            plot_type: The enum indicating if this is AC, DC, TRAN, etc.
            is_real: If True, returns only the real part (or converts complex to real).
                     If False, returns complex data (if applicable).
        """
        if self.curr_raw is None:
            self.logger.error("❌ Attempted to extract wave but no simulation data is loaded.")
            raise RuntimeError("Need to run the simulation at least once")

        # 1. Search for the specific plot object
        target_plot = None
        for p in self.curr_raw.plots:
            if p.get_plot_name() == plot_type.value:
                target_plot = p
                break

        # 2. Handle case where plot type isn't found
        if target_plot is None:
            available = self.get_available_plots()
            self.logger.critical(f"❌ Plot type '{plot_type.value}' not found in raw file.")
            self.logger.critical(f"ℹ️ Available plots: {available}")
            raise ValueError(f"Plot type '{plot_type.value}' not found.")

        # 3. Extract the data from that specific plot
        try:
            wave = target_plot.get_wave(wave_name)
        except IndexError as e:
            self.logger.debug(f"❌ Waveform '{wave_name}' not found in plot '{plot_type.value}'.")
            raise e
        except Exception as e:
            self.logger.critical(f"❌ Unexpected error while extracting waveform '{wave_name}': {e.__class__.__name__}: {e}")
            raise e

        # 4. Return the waveform as a NumPy array. Core stays torch-free (so the MCP
        #    server, which depends on core only, imports without torch); the optimizer
        #    wraps this in a tensor at its Bode/AC call sites.
        wave = np.asarray(wave)
        if is_real:
            return wave.real.astype(np.float64)
        return wave

    def extract_scalar_variable_from_raw(self, var_name: str | List[str], plot_type: Ngspice_Plot_Type,is_real: bool = True) -> Dict[str, np.float64]:
        """
        Extracts the first point of a trace, useful for OP analysis or single-point measurements.
        """
        if not isinstance(var_name, list):
            var_name = [var_name]

        outputs: Dict[str, np.float64] = {}

        for var in var_name:
            try:
                # pass plot_type down to extract_wave
                wave_data = self.extract_wave(var, plot_type=plot_type, is_real=is_real)

                # We expect a scalar or an array where we want index 0
                val = np.asarray(wave_data)

                if val.size > 0:
                    outputs[var] = np.float64(val.item(0) if val.ndim > 0 else val.item())
                else:
                    outputs[var] = np.float64(np.nan)

            except (ValueError, IndexError, RuntimeError):
                self.logger.debug(f"❌ Scalar Variable {var} not found in the raw file for plot {plot_type.value}")
                outputs[var] = np.float64(np.nan)

        return outputs

    # ----------------------------------------------------
    # [Public] Helper Methods
    # ----------------------------------------------------

    def print_circuit_info(self) -> None:
        if self.logger is None or self.editor is None:
            raise RuntimeError("Logger or Editor not initialized")

        logger = self.logger
        editor = self.editor

        logger.info("📊 --- Circuit Information ---")

        # Nodes
        nodes = editor.get_all_nodes()
        if nodes:
            logger.info(f"🔗 Nodes in the netlist: {nodes}")
        else:
            logger.warning("⚠️ No nodes found in the netlist!")

        # Parameters
        tb_params = self.get_tb_params()
        dut_params = self.get_dut_params()

        if tb_params:
            logger.info(f"Testbench parameters: {tb_params}")
        else:
            logger.warning("⚠️ No testbench parameters found!")

        if dut_params:
            logger.info(f"DUT parameters: {dut_params}")
        else:
            logger.warning("⚠️ No DUT parameters found!")

        logger.info("✅ --- Circuit info printed successfully --- 🎉 ")

    def _is_dut_param(self, name: str) -> bool:
        """Display-only heuristic: does this deck param look like a DUT sizing knob?

        Case-insensitive match on ``_dut_parameter_prefix`` (analog-db raw decks write
        lowercase ``x_dut_*``). Informational classification for ``print_circuit_info``
        only — the optimizer's authoritative DUT-param set is the project YAML's
        ``dut_params`` list, and NO run-path code branches on a parameter's name.
        """
        return self._dut_parameter_prefix.upper() in name.upper()

    def get_dut_params(self) -> List[Tuple[str, Any]]:
        self.logger.debug("Getting DUT parameters")
        if self.editor is None:
            raise RuntimeError("Editor not initialized")
        editor = self.editor
        params = editor.get_all_parameter_names()
        return [(param, editor.get_parameter(param)) for param in params if self._is_dut_param(param)]

    def get_tb_params(self) -> List[Tuple[str, Any]]:
        self.logger.debug("Getting TB parameters")
        if self.editor is None:
            raise RuntimeError("Editor not initialized")
        editor = self.editor
        params = editor.get_all_parameter_names()
        return [(param, editor.get_parameter(param)) for param in params if not self._is_dut_param(param)]

    def clean_up(self, delete_directories: bool = False, keep_netlist: bool = False, keep_logs: bool = False, keep_raw: bool = False) -> None:
        """
        Cleans up the files generated during the simulation runs.

        Args:
            delete_directories (bool): If True, removes the entire 'run_X' subdirectories.
            keep_spice_netlist (bool): If True (and delete_directories is False), preserves .spice files.
            keep_logs (bool): If True (and delete_directories is False), preserves .log files.
            keep_raw (bool): If True (and delete_directories is False), preserves .raw files.
        """

        if delete_directories and (keep_netlist or keep_logs):
            self.logger.warning("⚠️ 'delete_directories' is True; 'keep_spice_netlist' and 'keep_logs' will be ignored.")
            keep_netlist = False
            keep_logs = False

        NETLIST_EXTENSIONS = {'.spice', '.net', '.cir'}
        LOG_EXTENSIONS = {'.log'}
        RAW_EXTENSIONS = {'.raw'}

        if self.runner is None:
            raise RuntimeError("Runner not initialized")

        if not self.output_folder.exists():
            self.logger.warning(f"⚠️ Output folder {self.output_folder} does not exist. Nothing to clean.")
            return

        self.logger.debug(f"🧹 Starting cleanup in: {self.output_folder}")

        for item in self.output_folder.iterdir():
            if item.is_dir():

                # --- Mode A: Delete entire directory ---
                if delete_directories:
                    try:
                        shutil.rmtree(item)
                        self.logger.debug(f"\t🗑️  Deleted directory: {item.name}")
                    except OSError as e:
                        self.logger.error(f"\t❌ Failed to delete {item.name}: {e}")
                    continue

                # --- Mode B: Selective File Deletion ---
                files_deleted = 0
                for file in item.iterdir():
                    if not file.is_file():
                        continue

                    should_delete = True
                    if keep_netlist   and file.suffix.lower() in NETLIST_EXTENSIONS:    should_delete = False
                    if keep_logs      and file.suffix.lower() in LOG_EXTENSIONS:        should_delete = False
                    if keep_raw       and file.suffix.lower() in RAW_EXTENSIONS:        should_delete = False

                    if should_delete:
                        try:
                            file.unlink()
                            files_deleted += 1
                        except OSError as e:
                            self.logger.warning(f"\t⚠️ Could not delete {file.name}: {e}")

                if files_deleted > 0:
                    self.logger.debug(f"\t✨ Cleaned {files_deleted} files in {item.name}")

        self.logger.debug("✅ Cleanup sequence finished")

    def get_logger(self) -> logging.Logger:
        if self.logger is None:
            raise RuntimeError("Logger not initialized")
        return self.logger

if __name__ == "__main__":
    logger = setup_loggers()
    logger.info("Spicelib_Wrapper module imported successfully")
