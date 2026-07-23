import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
import yaml
from dacite import Config, from_dict
from dacite.exceptions import DaciteError, MissingValueError, UnexpectedDataError, WrongTypeError

# Re-exported from the shared kernel so existing call sites doing
# `from spicexplorer.core.domains import parse_value / Corner / PVTConfig / ...`
# keep working after these moved into spicexplorer_core (eng + pvt).
# The noqa'd names are pure re-exports (unused here by design — do not remove).
from spicexplorer_core.eng import MULTIPLIERS, parse_value, resolve_reference  # noqa: F401
from spicexplorer_core.pvt import (  # noqa: F401
    Corner,
    ModelInclude,
    PVTConfig,
    SupplyOverride,
    _normalize_pvt_block,
)
from spicexplorer_core.spice_engine import Ngspice_Plot_Type

# ------------------ Module Logger ------------------

logger = logging.getLogger("spicexplorer.designer_tools.domains")

# ------------------ Enums ------------------

class SimType(str, Enum):
    DC = "dc"
    AC = "ac"
    OP = "op"
    TRAN = "tran"
    NOISE = "noise"
    NOISE_SPECTRUM = "noise_spectrum"

class SpiceSimulatorType(Enum):
    SPECTRE = "spectre"
    HSPICE  = "hspice"
    NGSPICE = "ngspice"

class OptimizationGoalType(str, Enum):
    EXACT    = "exact"
    EXCEED   = "exceed"
    MINIMIZE = "minimize"

class OptimizerType(str, Enum):
    NEVERGRAD = "nevergrad"
    BAYESIAN_AX = "bayesian_ax"
    RL = "reinforcement_learning"

class Error_Types(str, Enum):
    ABSOLUTE = "absolute"
    SQUARED  = "squared"
    EXPONENTIAL = "exponential"
    RELATIVE_ABSOLUTE = "relative-absolute"
    RELATIVE_SQUARED  = "relative-squared"
    RELATIVE_EXPONENTIAL = "relative-exponential"
    RELATIVE_SIGMOID = "relative-sigmoid"

    def is_relative(self) -> bool:
        return "relative" in self.value

class Reward_Types(str, Enum):
    NO_REWARD = "none"
    RELATIVE_ABSOLUTE = "relative-absolute"
    RELATIVE_LOG = "relative-log"
    LOG = "log"
    # Below types are not recommended
    ABSOLUTE = "absolute"
    RELATIVE_SIGMOID = "relative-sigmoid"

    def is_relative(self) -> bool:
        return "relative" in self.value

class NoiseType(str, Enum):
    GAUSSIAN = "gaussian"
    OU = "ou"  # Ornstein-Uhlenbeck

class AgentType(str, Enum):
    "RL Agent Types Supported by SpiceExplorer"
    # Standard SB3 Agents
    PPO = "ppo"
    SAC = "sac"
    DDPG = "ddpg"
    TD3 = "td3"
    # Placeholder for user-defined
    CUSTOM_DDPG = "custom-ddpg"
    CUSTOM_SAC = "custom-sac"

# ------------------ Constants ------------------


SIMTYPE_TO_NGSPICE_PLOTTYPE : Dict[SimType, Ngspice_Plot_Type] = {
    SimType.AC: Ngspice_Plot_Type.AC,
    SimType.DC: Ngspice_Plot_Type.DC,
    SimType.TRAN: Ngspice_Plot_Type.TRAN,
    SimType.NOISE: Ngspice_Plot_Type.NOISE_1,
    SimType.NOISE_SPECTRUM: Ngspice_Plot_Type.NOISE_2,
    SimType.OP: Ngspice_Plot_Type.OP,
}

# ------------------ Helpers ------------------




def safe_from_dict(cls, data: dict, logger: logging.Logger, config: Config = Config(cast=[Enum])):
    try:
        return from_dict(data_class=cls, data=data, config=config)
    except MissingValueError as e:
        logger.critical(f"❌ Missing required field in {cls.__name__}: {e}")
        raise
    except WrongTypeError as e:
        logger.critical(f"❌ Wrong type while parsing {cls.__name__}: {e}")
        raise
    except UnexpectedDataError as e:
        logger.critical(f"❌ Unexpected field while parsing {cls.__name__}: {e}")
        raise

def list_target_spec_hook(data: list) -> 'ListTargetSpec':
    return ListTargetSpec([TargetSpec(**item) for item in data])

# ---------- Core Dataclasses ----------

@dataclass
class TechSpec:
    """Process technology (PDK) specification with constraints on device parameters."""
    name: str
    constraints: Dict[str, np.float64 | float | str] = field(default_factory=dict)

    def __post_init__(self):
        for key, val in self.constraints.items():
            if isinstance(val, str):
                self.constraints[key] = parse_value(val)
                logger.debug(f"Parsed constraint '{key}': '{val}' to {self.constraints[key]}")

# ---------- PVT Corner System ----------
# These dataclasses make process/voltage/temperature corners first-class so they
# actually drive the SPICE simulation. They are deliberately PDK-AGNOSTIC: core
# never interprets `lib_file`/`section` strings — the spice engine emits them verbatim.





@dataclass
class Param:
    name: str
    min_val: Optional[Union[float, np.float64, str]]
    max_val: Optional[Union[float, np.float64, str]]
    val: Optional[Union[float, np.float64, str]]
    init: Optional[Union[float, np.float64, str]]
    description: Optional[str]
    log_scale: bool = False
    is_integer: bool = False
    # Default False so an omitted `freeze` key means "optimize this param" — this
    # matches the wizard/parse-to-form default and the historical behavior where
    # every dut_param was swept. Set `freeze: true` to exclude a param from the
    # search space (its `val`/`init`, if given, is injected; otherwise the
    # netlist's own .param default is used).
    freeze: bool = False

    def needs_resolution(self) -> bool:
        return isinstance(self.min_val, str) or isinstance(self.max_val, str) or (self.init is not None and isinstance(self.init, str)) or (self.val is not None and isinstance(self.val, str))

    def resolve_min_max(self, constraints: Dict[str, np.float64]) -> None:
        if self.min_val is None or self.max_val is None:
            raise ValueError(f"Param {self.name} missing min or max value for resolution")
        self.min_val = resolve_reference(self.min_val, constraints)
        self.max_val = resolve_reference(self.max_val, constraints)
        if self.init is not None:
            self.init = resolve_reference(self.init, constraints)
        if self.min_val >= self.max_val:
            raise ValueError(f"Param {self.name} has min_val >= max_val ({self.min_val} >= {self.max_val})")

    def ressolve_val(self, constraints: Dict[str, np.float64]) -> None:
        if self.val is not None:
            self.val = resolve_reference(self.val, constraints)

    def compute_lin_normalization(self, denorm_val: np.float64) -> np.float64:
        if self.needs_resolution():
            raise ValueError(f"Param {self.name} min/max not resolved before normalization")
        if self.max_val is None or self.min_val is None:
            raise ValueError(f"No min/max defined for parameter {self.name}")
        return denorm_val * (self.max_val - self.min_val) + self.min_val

    def compute_log_normalization(self, denorm_val: np.float64) -> np.float64:
        if self.needs_resolution():
            raise ValueError(f"Param {self.name} min/max not resolved before normalization")
        if self.max_val is None or self.min_val is None:
            raise ValueError(f"No min/max defined for log-normalization of {self.name}")
        # Use base-10 to match the active Nevergrad denorm path (utils.log_denormalize uses
        # log10/10**); the prior base-e here meant the RL and Nevergrad backends mapped the same
        # log-scale param to different physical values (BUG-B24).
        log_min, log_max = np.log10(self.min_val), np.log10(self.max_val)
        return np.power(10.0, denorm_val * (log_max - log_min) + log_min)

    def get_val(self) -> float:
        if self.val is None:
            raise ValueError(f"dut_param {self.name!r}: val is not set")
        return float(self.val)

    def has_val(self) -> bool:
        return self.val is not None


@dataclass
class TestbenchParams:
    name: str
    params: List[Param]
    netlist: str
    enable: bool = True
    description: Optional[str] = None

@dataclass
class TargetSpec:
    name:       str
    testbench:  str
    target:     float | np.float64
    goal:       Union[OptimizationGoalType, str]
    sim_type:   Union[str, SimType, Ngspice_Plot_Type]
    # Optional fields with defaults
    log_scale:  bool = False
    enable:     bool = True
    range:      Union[np.float64, float, str | None] = None
    error_type: Union[Error_Types, str] = Error_Types.RELATIVE_ABSOLUTE
    reward_type: Union[Reward_Types, str] = Reward_Types.NO_REWARD
    weight:     Optional[float | np.float64] = 1.0
    tolerance:  Optional[float | np.float64] = None  # if not given use 5% of target
    description: Optional[str] = None
    # Optional declarative measurement recipe. Three authoring styles, all validated at
    # load and merged back under this spec's `name` so `scalar(name, analysis)` returns the
    # value (scorer unchanged):
    #  * Tier-1, engine-neutral Python — {meas: <name>, ...args} (e.g. meas: pm, out: vout;
    #    meas: i_supply, probe: 'i(vvdd)'). Computed from the result's own waves by
    #    spicexplorer_core.measurements.registry via optimization/measure_integration.py;
    #    works for BOTH ngspice and Spectre.
    #  * Tier-2, raw OCEAN — {result, expr} (e.g. result: ac, expr: 'gainBwProd(v("v_out"))').
    #  * Tier-2, builder OCEAN — {builder, ...args} (e.g. builder: device_op_param,
    #    instance: XM1, param: gm). Spectre/OCEAN backend only; built by
    #    optimization/ocean_integration.py.
    measurement: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        # Prepare human-friendly lists for error messages
        valid_goals = [g.value for g in OptimizationGoalType]
        valid_sim_types = [s.value for s in SimType]

        # --- Validate / convert goal ---
        if isinstance(self.goal, str):
            try:
                self.goal = OptimizationGoalType(self.goal.lower())
            except ValueError:
                logger.critical(
                    f"Invalid goal '{self.goal}' for target '{self.name}'. "
                    f"Must be one of {valid_goals}."
                )
                raise ValueError(f"Invalid goal '{self.goal}'. Must be one of {valid_goals}.")
        elif not isinstance(self.goal, OptimizationGoalType):
            logger.critical(
                f"Invalid goal type '{type(self.goal)}' for target '{self.name}'. "
                f"Must be one of {valid_goals}."
            )
            raise ValueError(f"Invalid goal '{self.goal}'. Must be one of {valid_goals}.")

        # --- Validate / convert sim_type ---
        if isinstance(self.sim_type, str):
            try:
                self.sim_type = SIMTYPE_TO_NGSPICE_PLOTTYPE[SimType(self.sim_type.lower())] # FIXME: hacked for NGspice simulators
            except ValueError:
                logger.critical(
                    f"Invalid sim_type '{self.sim_type}' for target '{self.name}'. "
                    f"Must be one of {valid_sim_types}."
                    f"Mapping: {SIMTYPE_TO_NGSPICE_PLOTTYPE}"
                )
                raise ValueError(f"Invalid sim_type '{self.sim_type}'. Must be one of {valid_sim_types}.")
        elif isinstance(self.sim_type, SimType):
            self.sim_type = SIMTYPE_TO_NGSPICE_PLOTTYPE[self.sim_type] # FIXME: hacked for NGspice simulators
            logger.critical(
                f"Must be in the mapping: {SIMTYPE_TO_NGSPICE_PLOTTYPE}"
            )
            raise ValueError(f"Invalid sim_type '{self.sim_type}'. Must be one of {valid_sim_types}.")
        elif not isinstance(self.sim_type, Ngspice_Plot_Type):
            logger.critical(
                f"Invalid sim_type type '{type(self.sim_type)}' for target '{self.name}'. "
                f"Must be one of {valid_sim_types}."
            )
            raise ValueError(f"Invalid sim_type '{self.sim_type}'. Must be one of {valid_sim_types}.")

        # --- Validate / convert error_type ---
        if isinstance(self.error_type, str):
            try:
                self.error_type = Error_Types(self.error_type.lower())
            except ValueError:
                valid_errors = [e.value for e in Error_Types]
                logger.critical(
                    f"Invalid error_type '{self.error_type}' for target '{self.name}'. "
                    f"Must be one of {valid_errors}."
                )
                raise ValueError(f"Invalid error_type '{self.error_type}'. Must be one of {valid_errors}.")

        # --- Coerce target (BUG-B7) ---
        # YAML 1.1 leaves dot-less / unsigned-exponent scientific literals like `200e6`,
        # `25e-6` as STRINGS, and the list_target_spec_hook path bypasses dacite casting, so
        # `target` can arrive as a str. Parse it (engineering suffixes + plain floats) before
        # any arithmetic, else `abs(0.05 * self.target)` and `value - self.target` raise.
        if isinstance(self.target, str):
            self.target = parse_value(self.target)

        # --- Coerce weight (BUG-B9) ---
        # The 1.0 default applies only to an OMITTED key; an explicit `weight:` / `weight: null`
        # yields None, and `np.float64(None)` is NaN — which poisons every weighted penalty for
        # the whole run (Nevergrad can't rank NaN). Normalize None / non-finite to 1.0.
        if isinstance(self.weight, str):
            self.weight = parse_value(self.weight)
        if self.weight is None or not np.isfinite(np.float64(self.weight)):
            self.weight = np.float64(1.0)

        # --- Validate / convert range ---
        if isinstance(self.range, str):
            self.range = parse_value(self.range)
        self.range = np.float64(self.range)
        # An omitted/blank range yields np.float64(None) == NaN, which silently
        # poisons every relative penalty/reward (the `<= 0` guards in utils do not
        # catch NaN). Fall back to a sane normalizer, matching score_service.
        if not np.isfinite(self.range) or self.range <= 0:
            fallback = np.float64(max(abs(float(self.target)), 1.0))
            logger.warning(
                f"Target '{self.name}' has no valid 'range' (got {self.range}); "
                f"falling back to {fallback} for metric normalization."
            )
            self.range = fallback

        # --- Tolerance fallback ---
        if isinstance(self.tolerance, str):
            self.tolerance = parse_value(self.tolerance)

        if self.tolerance is None or not(self.tolerance > 0):
            self.tolerance = abs(0.05 * self.target)
            if not (self.tolerance > 0):
                # target == 0 (or ~0): the 5%-of-target rule degenerates to 0, which would violate
                # the `tolerance > 0` invariant this block exists to enforce (and leave a zero-width
                # band). Floor to a small, scale-aware positive derived from the (already-validated,
                # >0) normalizing `range` (BUG-B17).
                self.tolerance = np.float64(self.range) * 1e-6
            logger.warning(
                f"No valid tolerance specified for target '{self.name}'. "
                f"Using default tolerance: {self.tolerance}"
            )

        # --- Validate the optional OCEAN measurement recipe (Spectre path) ---
        # `list_target_spec_hook` builds TargetSpec via `TargetSpec(**item)`, bypassing
        # dacite, so a nested `measurement:` mapping arrives here as a raw dict and its
        # SHAPE is validated at load (loudly). The recipe is otherwise opaque to core —
        # optimization/ocean_integration.py owns building the OceanMeasurement (keeping
        # this module free of any ocean_metrics / virtuoso_bridge import).
        if self.measurement is not None:
            self.measurement = self._validate_measurement(self.name, self.measurement)

        # --- Initialization log ---
        logger.debug(
            f"Initialized TargetSpec: {self.name}, target={self.target}, "
            f"tolerance={self.tolerance}, goal={self.goal}, sim_type={self.sim_type}, enable={self.enable}"
        )

    @staticmethod
    def _measurement_tier(m: Dict[str, Any]) -> str:
        """Which measurement tier a (shape-valid) recipe selects: `derived` (param-derived,
        `{derived: …}` — computed from the candidate sizing, no sim), `python` (Tier-1,
        engine-neutral `{meas: …}`), or `ocean` (Tier-2, `{result, expr}` / `{builder, …}`)."""
        keys = {str(k) for k in m}
        if "derived" in keys:
            return "derived"
        return "python" if "meas" in keys else "ocean"

    @staticmethod
    def _validate_measurement(spec_name: str, m: Any) -> Dict[str, Any]:
        """Validate a target's measurement recipe shape; return a normalized dict.

        Three authoring styles, all validated at load (before any simulation runs):

        * Tier-1 (engine-neutral Python) — ``{meas: str, ...args}``; the canonical name and
          its required args are validated later by ``spicexplorer_core.measurements.registry``
          (which owns the metric table), this just checks ``meas`` is a non-empty string.
        * Tier-2 raw OCEAN — ``{result: str, expr: str}``.
        * Tier-2 builder OCEAN — ``{builder: str, ...args}``; the builder name/args are
          validated later by ``optimization/ocean_integration`` (which owns the table).

        Keeping the name/arg tables in their owning modules leaves core decoupled from both
        the measurement registry and the OCEAN backend. Raises ValueError on a bad shape.
        """
        if not isinstance(m, dict):
            raise ValueError(
                f"target '{spec_name}': `measurement` must be a mapping, got {type(m).__name__}."
            )
        keys = {str(k) for k in m}
        if "derived" in keys:
            if not isinstance(m.get("derived"), str) or not str(m["derived"]).strip():
                raise ValueError(
                    f"target '{spec_name}': `measurement.derived` must be a non-empty string."
                )
        elif "meas" in keys:
            if not isinstance(m.get("meas"), str) or not str(m["meas"]).strip():
                raise ValueError(
                    f"target '{spec_name}': `measurement.meas` must be a non-empty string."
                )
        elif "builder" in keys:
            if not isinstance(m.get("builder"), str) or not str(m["builder"]).strip():
                raise ValueError(
                    f"target '{spec_name}': `measurement.builder` must be a non-empty string."
                )
        elif "expr" in keys or "result" in keys:
            if not (isinstance(m.get("result"), str) and isinstance(m.get("expr"), str)):
                raise ValueError(
                    f"target '{spec_name}': raw `measurement` needs both `result` and `expr` "
                    f"as strings (got {sorted(keys)})."
                )
        else:
            raise ValueError(
                f"target '{spec_name}': `measurement` needs one of {{derived, …}} (param-derived, "
                f"no sim), {{meas, …}} (Tier-1 Python), {{result, expr}} (raw OCEAN), or "
                f"{{builder, …args}} (a named ocean_metrics constructor); got {sorted(keys)}."
            )
        return dict(m)

    def measurement_tier(self) -> Optional[str]:
        """`python` (Tier-1), `ocean` (Tier-2), or None if this spec carries no recipe."""
        if self.measurement is None:
            return None
        return self._measurement_tier(self.measurement)

    def has_ocean_measurement(self) -> bool:
        """True when this spec carries a Spectre/OCEAN (Tier-2) measurement recipe."""
        return self.measurement_tier() == "ocean"

    def has_python_measurement(self) -> bool:
        """True when this spec carries a Tier-1 engine-neutral `{meas: …}` recipe."""
        return self.measurement_tier() == "python"

    def has_derived_measurement(self) -> bool:
        """True when this spec carries a param-derived `{derived: …}` recipe (scored from the
        candidate sizing, with no simulation — e.g. active area)."""
        return self.measurement_tier() == "derived"

    def get_simple_penalty(self, value: np.float64) -> np.float64:
        """Compute a simple penalty based on the goal and tolerance. Will allow reward in the form of negative penalty."""
        if not self.enable:
            return np.float64(0.0)

        if self.tolerance is None:
            logger.error(f"Something went wrong and tolerance is None for target '{self.name}'")
            raise RuntimeError("Tolerance should never be None here... check the log.")

        if self.goal == OptimizationGoalType.EXACT:
            if np.abs(value - self.target) <= self.tolerance:
                return np.float64(0.0)
            else:
                return np.abs(value - self.target) - self.tolerance

        elif self.goal == OptimizationGoalType.EXCEED:
            if value >= self.target - self.tolerance:
                return np.float64(0.0)
            else:
                return np.float64(self.target - self.tolerance - value)

        elif self.goal == OptimizationGoalType.MINIMIZE:
            if value <= self.target + self.tolerance:
                return np.float64(0.0)
            else:
                return np.float64(value - (self.target + self.tolerance))

        else:
            logger.error(f"Unknown goal type '{self.goal}' for target '{self.name}'")
            raise ValueError(f"Unknown goal type '{self.goal}'")

    def meets_spec(self, value: np.float64) -> bool:
        """Check if the given value meets the specification."""
        penalty = self.get_simple_penalty(value)
        return not (penalty > np.float64(0.0))

    def get_analysis(self) -> str:
        """The engine-neutral analysis string for this spec (`"ac"`, `"op"`, …).

        `__post_init__` eagerly coerces `sim_type` to an `Ngspice_Plot_Type` (its own
        FIXME notes the ngspice hack), so the neutral vocabulary the `SimResult`
        protocol speaks has to be recovered by reverse-mapping
        `SIMTYPE_TO_NGSPICE_PLOTTYPE`. Every backend resolves these strings itself
        (ngspice → plot type, Spectre → PSF-key prefix); the reverse map is pinned
        against the forward one by a unit test. A plot type with no `SimType` alias
        falls back to its display value, which the ngspice resolver also accepts."""
        if isinstance(self.sim_type, str):
            return self.sim_type.strip().lower()
        if isinstance(self.sim_type, SimType):
            return self.sim_type.value
        for st, pt in SIMTYPE_TO_NGSPICE_PLOTTYPE.items():
            if pt == self.sim_type:
                return st.value
        return self.sim_type.value

    def get_equivalent_ngspice_plot_type(self) -> Ngspice_Plot_Type:
        if isinstance(self.sim_type, Ngspice_Plot_Type):
            return self.sim_type
        elif isinstance(self.sim_type, SimType) and self.sim_type in SIMTYPE_TO_NGSPICE_PLOTTYPE:
            return SIMTYPE_TO_NGSPICE_PLOTTYPE[self.sim_type]
        elif isinstance(self.sim_type, str):
            try:
                return SIMTYPE_TO_NGSPICE_PLOTTYPE[SimType(self.sim_type.lower())]
            except ValueError:
                logger.critical(f"Cannot map sim_type '{self.sim_type}' to Ngspice_Plot_Type for target '{self.name}'")
                raise ValueError(f"Cannot map sim_type '{self.sim_type}' to Ngspice_Plot_Type")
        else:
            logger.critical(f"Cannot map sim_type '{self.sim_type}' to Ngspice_Plot_Type for target '{self.name}'")
            raise ValueError(f"Cannot map sim_type '{self.sim_type}' to Ngspice_Plot_Type")

    def __str__(self) -> str:
        return (
            f"TargetSpec(name={self.name}, target={self.target}, range={self.range:.2e} "
            f"tolerance={self.tolerance}, goal={self.goal.value}, sim_type={self.sim_type.value}, enable={self.enable}, "
            f"error_type={self.error_type.value}, weight={self.weight}, enable={self.enable}, description={self.description})"
        )

@dataclass
class ListTargetSpec:
    targets: List[TargetSpec] = field(default_factory=list)

    def __post_init__(self):
        # Reject duplicate spec names (mirrors the dut_param and PVT-corner uniqueness checks). The
        # performance map / fit_summary are keyed by spec name, so two specs sharing a name would
        # silently overwrite each other and mis-score the run (BUG-B29).
        seen: set[str] = set()
        dups = [t.name for t in self.targets if t.name in seen or seen.add(t.name)]
        if dups:
            raise ValueError(f"duplicate target_spec name(s): {sorted(set(dups))}")

    def add_target(self, target: TargetSpec) -> None:
        logger.info(f"Adding target '{target.name}' to ListTargetSpec")
        self.targets.append(target)

    def get_target_by_name(self, name: str) -> Optional[TargetSpec]:
        for t in self.targets:
            if t.name == name:
                return t
        return None

    def list_target_names(self) -> List[str]:
        return [t.name for t in self.targets]

    def enabled_targets(self) -> List[TargetSpec]:
        return [t for t in self.targets if t.enable]

@dataclass
class LossFunctionConfig:
    max_loss: Union[np.float64, str]
    loss_norm_method: Optional[str]
    loss_type: Optional[str]
    rescale_mag: Optional[bool] = False
    include_phase_loss : Optional[bool] = False
    include_mag_loss : Optional[bool] = False

@dataclass
class VariableBoundConfig:
    min: float
    max: float

    def get_range(self) -> float:
        return self.max - self.min

    def get_min_max(self) -> Tuple[float, float]:
        return (self.min, self.max)

# ------------------ RL Configuration Objects ------------------

@dataclass
class NoiseConfig:
    type: str = NoiseType.GAUSSIAN.value
    sigma_initial: float = 0.2
    sigma_min: float = 0.01
    sigma_decay: float = 0.995

@dataclass
class ReplayBufferConfig:
    buffer_size: int = 100000
    batch_size: int = 64

@dataclass
class RLTrainingConfig:
    """Contains training loop settings and environment wrapper settings."""
    gamma: float = 0.99
    tau: float = 0.005
    update_every: int = 1
    initial_random_steps: int = 1000
    policy_update_freq: int = 2
    # Moved from EnvHyperparameters
    max_episode_steps: int = 1000
    normalize_observations: bool = True
    normalize_actions: bool = True

@dataclass
class NetworkConfig:
    """Generic config for Actor or Critic networks."""
    lr: float = 0.001
    hidden_units: Tuple[int, ...] = (256, 128)
    weight_decay: float = 0.0
    grad_clip: float = 1.0

# --- Specific Agent Configs ---

@dataclass
class SACAlphaConfig:
    learn_alpha: bool = True
    alpha_init: float = 0.2
    lr_alpha: float = 0.0003

@dataclass
class AgentConfig:
    """Base interface for agent settings."""
    pass

@dataclass
class DDPGConfig(AgentConfig):
    actor: NetworkConfig = field(default_factory=NetworkConfig)
    critic: NetworkConfig = field(default_factory=NetworkConfig)
    noise: NoiseConfig = field(default_factory=NoiseConfig)
    memory: ReplayBufferConfig = field(default_factory=ReplayBufferConfig)
    training: RLTrainingConfig = field(default_factory=RLTrainingConfig)

@dataclass
class SACConfig(AgentConfig):
    actor: NetworkConfig = field(default_factory=NetworkConfig)
    critic: NetworkConfig = field(default_factory=NetworkConfig)
    alpha: SACAlphaConfig = field(default_factory=SACAlphaConfig)
    memory: ReplayBufferConfig = field(default_factory=ReplayBufferConfig)
    training: RLTrainingConfig = field(default_factory=RLTrainingConfig)

@dataclass
class OptimizerConfig:
    name: str # Optimization algorithm name
    type: str # Optimizer family type
    budget: int
    optimizer_kwargs: Optional[Dict[str, Any]]

    target_specs: ListTargetSpec
    lin_variable_bounds: Optional[VariableBoundConfig]
    log_variable_bounds: Optional[VariableBoundConfig]
    loss_function_config: Optional[LossFunctionConfig]
    random_seed: Optional[int]

    def __post_init__(self):
        # Mandatory checks
        if not self.name or not self.type or self.budget is None:
            logger.critical("OptimizerConfig is missing a mandatory field (name, type, or budget).")
            raise ValueError("OptimizerConfig requires name, type, and budget.")

        # -------------------------
        # General
        # -------------------------
        logger.info(
            f"Initialized OptimizerConfig: {self.name}, "
            f"type={self.type}, budget={self.budget}, random_seed={self.random_seed}"
        )

        if self.optimizer_kwargs is None:
            self.optimizer_kwargs = {}
        else:
            logger.debug("optimizer_kwargs provided:")
            for k, v in self.optimizer_kwargs.items():
                logger.debug(f"\t{k}: {v}")

        # -------------------------
        # Bounds
        # -------------------------
        if self.lin_variable_bounds is None:
            logger.warning("No lin_variable_bounds provided; using default [0.0, 1.0].")
            self.lin_variable_bounds = VariableBoundConfig(min=0.0, max=1.0)
        else:
            logger.debug(
                f"\tLinear bounds: min={self.lin_variable_bounds.min}, max={self.lin_variable_bounds.max}"
            )
        if self.log_variable_bounds is None:
            logger.warning("No log_variable_bounds provided; using default [0.0, 1.0].")
            self.log_variable_bounds = VariableBoundConfig(min=1, max=100.0)
        else:
            logger.debug(
                f"\tLog bounds: min={self.log_variable_bounds.min}, max={self.log_variable_bounds.max}"
            )

        # -------------------------
        # Loss function config
        # -------------------------
        if self.loss_function_config is None:
            logger.warning("No loss_function_config provided; using default values.")
        else:
            logger.debug(
                f"\tLoss function: max_loss={self.loss_function_config.max_loss}, "
                f"norm_method={self.loss_function_config.loss_norm_method}, "
                f"type={self.loss_function_config.loss_type}, rescale_mag={self.loss_function_config.rescale_mag}, "
                f"include_phase_loss={self.loss_function_config.include_phase_loss}, "
                f"include_mag_loss={self.loss_function_config.include_mag_loss}"
            )

        # -------------------------
        # Target Specs
        # -------------------------
        logger.debug(f"\tNumber of target specs: {len(self.target_specs.targets)}")
        for t in self.target_specs.targets:
            logger.debug(f"\t\t- {t}")

    def get_lin_variable_range(self) -> np.float64:
        if self.lin_variable_bounds is None:
            raise ValueError("Linear variable bounds are not set")
        return np.float64(self.lin_variable_bounds.get_range())

    def get_log_variable_range(self) -> np.float64:
        if self.log_variable_bounds is None:
            raise ValueError("Log variable bounds are not set")
        return np.float64(self.log_variable_bounds.get_range())

    def get_lin_min_max(self) -> Tuple[float, float]:
        if self.lin_variable_bounds is None:
            raise ValueError("Linear variable bounds are not set")
        return self.lin_variable_bounds.get_min_max()

    def get_log_min_max(self) -> Tuple[float, float]:
        if self.log_variable_bounds is None:
            raise ValueError("Linear variable bounds are not set")
        return self.log_variable_bounds.get_min_max()

# ---------- Interface Dataclass ----------

@dataclass
class Project_Setup:
    # General Info
    name: str
    description: str
    simulator:  str
    ws_root :   Path | str
    netlist:    Path | str
    outdir :    Path | str

    # Custom Data types
    tech_spec: TechSpec
    dut_params: List[Param]
    testbenches: List[TestbenchParams]
    optimizer_config: OptimizerConfig

    save_sim:  bool = False
    parallel_sim: bool = True
    # Optional pointer to the design's xschem schematic, relative to `ws_root`.
    # Consumed by the UI's Schematic viewer to pre-select the main `.sch`.
    schematic: Path | str | None = None

    # Optional simulation-backend selector. Default
    # `ngspice` preserves every existing project verbatim; `spectre`/`hspice` are valid
    # engine names the factory dispatches on (only `ngspice` is loop-wired today). This
    # is *distinct* from `simulator`, which is a path to the ngspice executable — the
    # backend factory keys off `sim_engine`, the wrapper still uses `simulator`.
    sim_engine: str = "ngspice"

    # PVT corner system. When present, the optimizer applies `pvt.get_active()`
    # to every enabled testbench's netlist once, before the optimization loop — so the
    # chosen corner's `.lib`/temp/supply actually drive the simulation. `None` preserves
    # the legacy behavior (the corner is whatever the testbench `.spice` hardcodes).
    pvt: Optional[PVTConfig] = None

    # DUT-parameterization projection.
    # `params_file` points at the circuit's `abstract/params.yaml` (spicexplorer/params@1 —
    # atomic inventory + shipped tying); a relative path resolves against `ws_root`, like
    # `netlist`. With it set, a dut_param name may be `<group>.<field>` (resolved to the
    # group's FIRST member's atomic symbol — the free knob under the tie lowering) and the
    # optional `ungroup:` selector list ("<group>" | "kind:<kind>" | "ratio:<ref>") dissolves
    # shipped ties by appending FROZEN shadow dut_params (one explicit `.param
    # <member_symbol> = <current deck default>` per dissolved non-first member-field —
    # untying = shadowing), making those symbols independently addressable as their own
    # dut_params. The frozen shadows ride the optimizer's existing verbatim `.param` rewrite
    # (NevergradMixin injects frozen vals) — zero optimizer-core changes, both engine lanes.
    # Both keys absent → exactly the legacy behavior. See backends/params.py.
    params_file: Path | str | None = None
    ungroup: Optional[List[str]] = None

    def __post_init__(self):
        # correct path types
        if isinstance(self.ws_root, str):
            self.ws_root = Path(self.ws_root)
        if isinstance(self.netlist, str):
            self.netlist = Path(self.netlist)
        if isinstance(self.outdir, str):
            self.outdir = Path(self.outdir)
        if isinstance(self.schematic, str):
            self.schematic = Path(self.schematic)
        # Validate dut_param name uniqueness: a duplicate name silently collapses
        # to a single search dimension in the optimizer (parameters[name] = ...
        # overwrites), masking a data error. Fail loudly instead.
        _dut_names = [p.name for p in self.dut_params]
        _dupes = sorted({n for n in _dut_names if _dut_names.count(n) > 1})
        if _dupes:
            raise ValueError(
                f"Duplicate dut_param name(s) {_dupes} in project '{self.name}'. "
                "Each DUT parameter must have a unique name."
            )
        # Normalise + validate the optional simulation-backend selector. Fail loudly on a
        # typo at load rather than deep in the factory. (An unwired-but-valid engine like
        # 'spectre' passes here; the orchestrator decides what is actually runnable.)
        if isinstance(self.sim_engine, str):
            self.sim_engine = self.sim_engine.strip().lower()
        try:
            SpiceSimulatorType(self.sim_engine)
        except ValueError as exc:
            raise ValueError(
                f"Unknown sim_engine {self.sim_engine!r} in project '{self.name}'; "
                f"valid: {[e.value for e in SpiceSimulatorType]}."
            ) from exc
        # Log basic info
        logger.info(f"Project '{self.name}' initialized with simulator '{self.simulator}'")
        logger.info(f"\tWorkspace root: {self.ws_root}")
        logger.info(f"\tNetlist path: {self.netlist}")
        logger.info(f"\tOutput directory: {self.outdir}")
        if self.schematic is not None:
            logger.info(f"\tSchematic path: {self.schematic}")

    # ------------------ Class Methods ------------------

    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> "Project_Setup":
        """Load a Project object from a YAML file with variable resolution."""

        try:
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)
            logger.debug(f"YAML content successfully loaded: {list(data.keys())}")

            # Resolve `ws_root` so committed example projects are portable across
            # machines (see CLAUDE.md "ws_root in YAML"):
            #   • absolute path             → used as-is (e.g. an out-of-repo workspace)
            #   • relative path (e.g. "..") → resolved against THIS YAML file's directory
            #   • omitted / empty           → defaults to the YAML file's own directory
            # A leading "~" is expanded. The examples ship `ws_root: ..`, which works on
            # any fresh clone without per-user path editing because the netlists are
            # committed inside the repo alongside the YAML.
            proj = data['project']
            yaml_dir = Path(yaml_path).resolve().parent
            ws = Path(str(proj.get('ws_root') or '.')).expanduser()
            if not ws.is_absolute():
                ws = yaml_dir / ws
            proj['ws_root'] = str(ws.resolve())
            logger.debug(f"Resolved ws_root → {proj['ws_root']}")

            # Desugar the optional `pvt:` block (expand process bundles, widen
            # singular `supply`, coerce numerics) before dacite maps it to PVTConfig.
            _normalize_pvt_block(proj)

            project = safe_from_dict(cls, proj, logger, config=DECITE_CONFIG)

            # P3 group/atomic knob resolution + `ungroup:` shadowing (no-op without
            # `params_file:`) — runs BEFORE range resolution so appended frozen shadow
            # params get their vals resolved by the existing machinery.
            project.resolve_param_projection()

            # Resolve constraints in tech_spec
            project.resolve_all_parameter_ranges()

            logger.info("✅ Project setup successfully created")
            return project

        except FileNotFoundError:
            logger.critical(f"YAML file not found: {yaml_path}")
            raise
        except yaml.YAMLError as e:
            logger.critical(f"Failed to parse YAML {yaml_path}: {e}")
            raise
        except DaciteError as e:
            logger.critical(f"Failed to map YAML → Project_Setup: {e}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected error while loading {yaml_path}: {e}")
            raise

    # ------------------ Getters & Helpers ------------------
    def resolve_param_projection(self) -> None:
        """Group/atomic knob resolution + ``ungroup:``.

        No-op without ``params_file`` — exactly the legacy behavior. Otherwise:

        1. Each dut_param name is resolved against the circuit's params.yaml contract:
           ``<group>.<field>`` → the group's FIRST member's atomic symbol (the free knob
           under the tie lowering); an atomic/free symbol passes through unchanged.
        2. Each ``ungroup:`` selector (``"<group>"`` | ``"kind:<kind>"`` | ``"ratio:<ref>"``)
           dissolves a shipped tie by appending a FROZEN shadow dut_param per non-first
           member-field, valued at the tie target's current default read from this
           project's ``netlist`` deck header (untying = shadowing: the frozen param's
           explicit ``.param`` rewrite overrides the deck's tie line). A shadowed symbol
           the projection already lists as its own dut_param is left free — the sweep
           itself shadows the tie.

        Called by ``from_yaml`` before ``resolve_all_parameter_ranges`` (so shadow vals
        resolve through the existing machinery); call it manually after a programmatic
        construction that sets ``params_file``.
        """
        if self.params_file is None:
            if self.ungroup:
                raise ValueError(
                    f"Project '{self.name}': `ungroup:` requires `params_file:` "
                    "(the circuit's abstract/params.yaml — the tie definitions to dissolve)."
                )
            return
        from spicexplorer.backends.params import (
            load_params_file,
            netlist_param_defaults,
            resolve_knob,
            shadow_params,
        )

        ppath = Path(self.params_file).expanduser()
        if not ppath.is_absolute():
            ppath = Path(self.ws_root) / ppath
        contract = load_params_file(ppath)

        for p in self.dut_params:
            resolved = resolve_knob(contract, p.name)
            if resolved != p.name:
                logger.info(f"🔗 dut_param '{p.name}' → atomic symbol '{resolved}' (group first member)")
                p.name = resolved
        # Re-check uniqueness post-resolution: `<group>.<field>` and its first member's
        # atomic symbol are the SAME knob (the __post_init__ check ran on the raw names).
        names = [p.name for p in self.dut_params]
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise ValueError(
                f"Project '{self.name}': dut_params collapse to duplicate atomic symbol(s) "
                f"{dupes} after group resolution — a `<group>.<field>` knob and its first "
                "member's atomic symbol are the same search dimension."
            )

        if self.ungroup:
            deck = Path(self.netlist)
            if not deck.is_absolute():
                deck = Path(self.ws_root) / deck
            shadows = shadow_params(contract, self.ungroup, netlist_param_defaults(deck))
            for sym, val in shadows.items():
                if sym in names:
                    continue  # already a free knob here — the sweep itself shadows the tie
                self.dut_params.append(
                    Param(
                        name=sym,
                        min_val=None,
                        max_val=None,
                        val=val,
                        init=None,
                        description="ungroup shadow — dissolved tie",
                        freeze=True,
                    )
                )
                logger.info(f"🧩 ungroup: frozen shadow .param {sym} = {val}")

    def resolve_all_parameter_ranges(self) -> None:
        """Resolve all parameter min/max/default values based on tech_spec constraints."""
        logger.info("resolving DUT parameters...")
        for param in self.dut_params:
            if param.freeze:
                # Frozen params are INJECTED, not searched, so min/max are optional. Resolve the
                # injected operating point `val` and the `init` fallback (eng-strings / constraint
                # refs); validate bounds only when BOTH are present. A frozen eng-string constant
                # with no min/max must not crash the load (BUG-B10) — `resolve_min_max` would raise
                # "missing min or max" because a string `val`/`init` makes needs_resolution() true.
                param.ressolve_val(self.tech_spec.constraints)
                if param.min_val is not None and param.max_val is not None:
                    param.resolve_min_max(self.tech_spec.constraints)  # resolves init + checks min<max
                elif isinstance(param.init, str):
                    param.init = resolve_reference(param.init, self.tech_spec.constraints)
                continue
            # Non-frozen params are search DIMENSIONS: bounds are required, and ALWAYS validated
            # (incl. the min_val >= max_val check) even when given as plain numbers — previously the
            # check ran only for string bounds via needs_resolution(), so numeric `min: 5, max: 1`
            # silently inverted the search range (BUG-B8). `resolve_min_max` also resolves init.
            logger.debug(f"Resolving ranges for param '{param.name}'")
            param.resolve_min_max(self.tech_spec.constraints)
            logger.debug(f"Resolved param '{param.name}': min={param.min_val}, max={param.max_val}, default={param.init}")
            # Resolve the operating-point `val` too (eng-string / constraint ref), so the Schematic
            # inspector nominal and the project summary don't fall back to the range midpoint
            # (SCH-2 / BUG-A4). Mirrors the testbench-param loop below.
            param.ressolve_val(self.tech_spec.constraints)

        logger.info("resolving TESTBENCH parameters...")
        for tb in self.testbenches:
            for param in tb.params:
                param.ressolve_val(self.tech_spec.constraints)
                logger.debug(f"Resolved value for tb '{tb.name}' param '{param.name}' is {param.val}")
        logger.info("")


    def get_constraint_by_name(self, name: str) -> Optional[np.float64]:
        value = self.tech_spec.constraints.get(name)
        logger.debug(f"Constraint '{name}': {value}")
        return value

    def list_constraints(self) -> Dict[str, np.float64]:
        logger.debug(f"Listing all constraints: {self.tech_spec.constraints}")
        return self.tech_spec.constraints

    def get_param_by_name(self, name: str) -> Optional[Param]:
        for p in self.dut_params:
            if p.name == name:
                # logger.debug(f"Found DUT param: {p}")
                return p
        logger.warning(f"DUT param '{name}' not found")
        return None

    def list_params(self) -> List[str]:
        param_names = [p.name for p in self.dut_params]
        logger.debug(f"DUT param names: {param_names}")
        return param_names

    def get_log_scaled_params(self) -> List[Param]:
        log_params = [p for p in self.dut_params if p.log_scale]
        logger.debug(f"Log-scaled params: {[p.name for p in log_params]}")
        return log_params

    def filter_params_by_range(self, min_value: float, max_value: float) -> List[Param]:
        filtered = [p for p in self.dut_params if p.init is not None and min_value <= p.init <= max_value]
        logger.debug(f"Params in range {min_value}-{max_value}: {[p.name for p in filtered]}")
        return filtered

    def summary(self) -> None:
        logger.info("========== Project Setup Summary ==========")
        logger.info(f"📂 Project: {self.name}")
        logger.info(f"📝 Description: {self.description}")
        logger.info(f"🧠 Simulator: {self.simulator}")
        logger.info(f"📜 DUT Netlist: {self.netlist}")
        logger.info(f"🧪 Testbenches: {len(self.testbenches)} count")
        for i,tb in enumerate(self.testbenches):
            logger.info(f"\t({i+1}) {tb.name} @ {tb.netlist}")
            if tb.description:
                logger.info(f"\t- Description: {tb.description}")
        if self.pvt is not None:
            active = self.pvt.get_active() if self.pvt.get(self.pvt.active_corner) else None
            logger.info(
                f"🌡️  PVT (active): '{self.pvt.active_corner}' "
                f"({len(self.pvt.corners)} defined, {len(self.pvt.enabled_corners())} enabled)"
            )
            if active is not None:
                _libs = ", ".join(f"{m.lib_file}:{m.section}" for m in active.model_includes)
                _sup = ", ".join(f"{s.node}={s.value}V" for s in active.supplies)
                logger.info(f"\t→ temp={active.temp}°C  supplies=[{_sup}]  includes=[{_libs}]")
        logger.info(f"🔧 Tech Spec: {len(self.tech_spec.constraints)} constraints")
        for k, v in self.tech_spec.constraints.items():
            logger.info(f"\t• {k}: {v:.2e}")
        logger.info(f"🎛 DUT Params: {len(self.dut_params)} params -> {[p.name for p in self.dut_params]}")

        logger.info(f"🔍 target specs ({len(self.optimizer_config.target_specs.targets)}): {[(p.name, p.target, p.goal.value) for p in self.optimizer_config.target_specs.targets]}")
        logger.info("===========================================")

# ------------------ Dacite Config ------------------
DECITE_CONFIG = Config(
    type_hooks={
        ListTargetSpec: list_target_spec_hook
    }
)

# ------------------ Optimizer Objects ------------------
@dataclass
class OptimizationPoint:
    """Represents the simplest point in the optimization trace."""
    params: Dict[str, float | np.float64]
    score: float | np.float64
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict) # to add any other information

@dataclass
class OptimizationLogEntry:
    """Represents a single entry in the optimization log."""
    point: 'OptimizationPoint'
    fit_summary: Optional[Dict[str, Dict[str, float | np.floating]]] = field(default_factory=dict)   # Depends on your optimizer output (could refine type)
    log_file: Optional[Dict[str, str | Path]] = None                                  # Any log/debug info

    def get_score(self) -> float | np.floating:
        return self.point.score

    def get_params(self) -> Dict[str, float | np.floating]:
        return self.point.params

    def get_metadata(self) -> Dict[str, Any] | None:
        return self.point.metadata

    def get_param_val(self, param_name: str) -> float | np.floating | None:
        if param_name not in self.point.params.keys():
            logger.debug(f"{param_name} was not found in the OptimizationLogEntry object - should be one of {self.point.params.keys()}")
            return None
        return self.point.params[param_name]

    def get_fit_summary(self) -> Dict[str, Any]:
        if self.fit_summary is None:
            logger.error("tried accessing the fit_summary but this was never created")
            raise ValueError("tried accessing the fit_summary but this was never created")
        return self.fit_summary

    def get_performance_params(self) -> Dict[str, float]:
        if self.fit_summary is None: raise ValueError("fit_summary field is missing!")

        output = {}
        for key, val in self.fit_summary.items():
            output[key] = float(val["curr_val"])

        return output




class OptimizationLog:
    """Acts like a list of OptimizationLogEntry objects."""
    def __init__(self, initial_logs: Optional[List[OptimizationLogEntry]] = None):
        # Copy (and never share the default) so two default-constructed logs do
        # not alias the same list — the classic mutable-default trap that leaked
        # trials across runs/sanity-checks in one backend process.
        self.log: List[OptimizationLogEntry] = list(initial_logs) if initial_logs is not None else []

    def __iter__(self) -> Iterator[OptimizationLogEntry]:
        """Allow iteration over log entries."""
        return iter(self.log)

    def __len__(self) -> int:
        """Return the number of log entries."""
        return len(self.log)

    def __getitem__(self, index: int) -> OptimizationLogEntry:
        """Support indexing like a list."""
        return self.log[index]

    def __setitem__(self, index: int, value: OptimizationLogEntry) -> None:
        """Support assignment by index."""
        self.log[index] = value

    def __delitem__(self, index: int) -> None:
        """Support deletion by index."""
        del self.log[index]

    def append(self, entry: OptimizationLogEntry) -> None:
        """Append a new entry to the log."""
        self.log.append(entry)

    def extend(self, entries: List[OptimizationLogEntry]) -> None:
        """Extend log with multiple entries."""
        self.log.extend(entries)

    def __repr__(self) -> str:
        """Readable representation."""
        return f"OptimizationLog({self.log!r})"

    def get_score(self, index: int) -> float | np.floating:
        return self.log[index].get_score()

    def get_params(self, index: int) -> Dict[str, float | np.floating]:
        return self.log[index].get_params()

    def get_all_loss(self) -> List[np.floating]:
        return np.array([entry.get_score() for entry in self.log])

    def get_metadata(self, index: int) -> Dict[str, Any]:
        return self.log[index].get_metadata()

    def has_param(self, param_name: str) -> bool:
        if len(self.log) == 0:
            logger.debug("no log file in the object")
            return False
        if param_name not in self.log[0].get_params():
            logger.debug(f"param '{param_name}' not found in optimization trace")
            return False
        return True

    def is_empty(self):
        if len(self.log) == 0:
            logger.debug("no log file in the object")
            return True
        return False

    def list_available_params(self) -> List[str]:
        if self.is_empty(): return []
        return list(self.log[0].get_params().keys())

    def list_available_metrics(self) -> List[str]:
        if self.is_empty(): return []
        return list(self.log[0].get_fit_summary().keys())


    def update_entry(self, index: int, new_entry: OptimizationLogEntry) -> None:
        """Update an existing log entry at the specified index."""
        if index < 0 or index >= len(self.log):
            logger.error(f"Index {index} out of range for OptimizationLog of size {len(self.log)}")
            raise IndexError("Index out of range")
        self.log[index] = new_entry

    def update_entry_fit_summary(self, index: int, fit_summary: Dict[str, Dict[str, float | np.floating]]) -> None:
        """Update the fit_summary of an existing log entry at the specified index."""
        if index < 0 or index >= len(self.log):
            logger.error(f"Index {index} out of range for OptimizationLog of size {len(self.log)}")
            raise IndexError("Index out of range")
        self.log[index].fit_summary = fit_summary



