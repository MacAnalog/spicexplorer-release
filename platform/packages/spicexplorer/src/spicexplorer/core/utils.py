from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

import numpy as np

# torch / control / sympy are OPTIONAL. They are needed ONLY by the Bode / AC
# transfer-function-fitting helpers in this module; the common numpy scoring path
# (compute_error / compute_reward / compute_relative_*) used by the constraint and
# single-objective optimizers never touches them. Keeping the import lazy lets the
# api's score path import this module without the heavy torch wheel. Install the
# Bode/RL features with:  pip install 'spicexplorer[torch]'.
try:
    import torch
except ModuleNotFoundError:
    torch = None
try:
    import control as ctrl
except ModuleNotFoundError:
    ctrl = None
try:
    import sympy as sp
except ModuleNotFoundError:
    sp = None

import logging

# Plotting Tools
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from spicexplorer.core.domains import Error_Types, OptimizationGoalType, Reward_Types

logger = logging.getLogger("spicexplorer.designer_tools.utils")

UNIT_DICT: Dict[str, float] ={
    'p' : 1e-12,
    'n' : 1e-9,
    'u' : 1e-6,
    'k' : 1e3
}

# Preserve the original global torch config when torch is available (no-op without it).
if torch is not None:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dtype  = torch.double
    torch.set_default_dtype(dtype)
    torch.set_default_device(device)
else:
    device = None
    dtype  = None

# ----------------------------
# Loss Functions Helpers
# ----------------------------
def weighted_mse_loss(
    response: torch.Tensor,
    target_response: torch.Tensor,
    weights: torch.Tensor,
    normalize_method: str = None,
    epsilon: float = 1e-10
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:

    """Computes the weighted mean squared error loss between the response and the target response."""

    norm_params = {}

    if normalize_method is None:
        norm_params = None
        loss = torch.mean(weights * (response - target_response) ** 2)

    elif normalize_method == "z-score":
        mean = torch.mean(target_response)
        std = torch.std(target_response)

        # Avoid division by zero
        std = torch.clamp(std, min=epsilon)

        target_response_norm = (target_response - mean) / std
        response_norm = (response - mean) / std

        norm_params = {"mean": mean, "std": std}
        loss = torch.mean(weights * (response_norm - target_response_norm) ** 2)

    elif normalize_method == "min-max":
        min_val = torch.min(target_response)
        max_val = torch.max(target_response)

        norm_params = {"min": min_val, "max": max_val}

        loss = torch.mean(weights * (response - target_response) ** 2 / ((max_val-min_val)** 0.5))

    else:
        raise ValueError("Invalid normalization method. Choose 'z-score' or 'min-max' or None.")

    return loss, norm_params

def weighted_mae_loss(
    response: torch.Tensor,
    target_response: torch.Tensor,
    weights: torch.Tensor,
    normalize_method: str = None,
    epsilon: float = 1e-10
) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:

    """Computes the weighted absolute error loss between the response and the target response."""

    norm_params = {}

    if normalize_method is None:
        return torch.mean(weights * torch.abs(response - target_response)), norm_params

    elif normalize_method == "z-score":
        mean = torch.mean(target_response)
        std = torch.std(target_response)

        # Avoid division by zero
        std = torch.clamp(std, min=epsilon)

        target_response_norm = (target_response - mean) / std
        response_norm = (response - mean) / std

        norm_params = {"mean": mean, "std": std}
        loss = torch.mean(weights * torch.abs(response_norm - target_response_norm))

    elif normalize_method == "min-max":
        min_val = torch.min(target_response)
        max_val = torch.max(target_response)

        norm_params = {"min": min_val, "max": max_val}
        loss = torch.mean(weights * torch.abs(response - target_response)/ ((max_val-min_val)** 0.5))

    else:
        raise ValueError("Invalid normalization method. Choose 'z-score' or 'min-max' or None.")

    return loss, norm_params

def get_bode_fitness_loss( current_complex_response: torch.Tensor, target_complex_response: torch.Tensor, freq_weights: torch.Tensor | None = None, loss_type: str = 'mae',norm_method: str = "min-max", rescale:bool = True, epsilon: float = 1e-10) -> Dict[str, torch.Tensor]:
    # Ensure inputs are tensors
    if not isinstance(current_complex_response, torch.Tensor):
        current_complex_response = torch.tensor(current_complex_response, dtype=torch.cfloat)
    if not isinstance(target_complex_response, torch.Tensor):
        target_complex_response = torch.tensor(target_complex_response, dtype=torch.cfloat)

    # Set freq_weights to an array of ones if not provided, matching the dtype of current_complex_response
    if freq_weights is None:
        freq_weights = torch.ones_like(current_complex_response, dtype=torch.float64)

    helper = Transfer_Func_Helper()

    # Extract magnitude and phase
    curr_mag, curr_phase     = helper.get_mag_phase_from_complex_response(current_complex_response)
    target_mag, target_phase = helper.get_mag_phase_from_complex_response(target_complex_response)

    fit_summary = {}


    # --- Compute gain ---
    curr_max_mag    = torch.max(curr_mag)
    target_max_mag  = torch.max(target_mag)
    # log in the summary
    fit_summary['curr_max_mag'] = curr_max_mag
    fit_summary['target_max_mag'] = target_max_mag
    if rescale:  # mag is in dB so we normalize to
        curr_mag   -= curr_max_mag
        target_mag -= target_max_mag

    # --- Compute 3dB cutoff ---
    # TODO


    # Compute losses
    if loss_type == 'mae':
        mag_loss, _   = weighted_mae_loss(curr_mag, target_mag, freq_weights, norm_method, epsilon=epsilon)
        phase_loss, _ = weighted_mae_loss(curr_phase, target_phase, freq_weights, norm_method, epsilon=epsilon)
    elif loss_type == 'mse':
        mag_loss, _   = weighted_mse_loss(curr_mag, target_mag, freq_weights, norm_method, epsilon=epsilon)
        phase_loss, _ = weighted_mse_loss(curr_phase, target_phase, freq_weights, norm_method, epsilon=epsilon)
    else:
        raise KeyError(f"{loss_type} is a loss type option... choose from: ['mae', 'mse']")

    fit_summary['mag_loss']   = mag_loss
    fit_summary['phase_loss'] = phase_loss

    return fit_summary

def convert_linear_to_log(val: np.ndarray | float | np.float64) -> np.ndarray | np.float64:
    """Converts a value from linear scale to (log10)."""
    return np.log10(val)

def convert_log_to_linear(val: np.ndarray | float | np.float64) -> np.ndarray | np.float64:
    """Converts a value from (log10) to linear scale."""
    return np.power(10, val)

# ----------------------------
# Decade-space transforms for `log_scale` specs (SHARED — one implementation)
# ----------------------------
# Used by BOTH the optimizer's per-spec scorer (`Base_Optimizer.compute_*_for_spec`) and the API
# Score-Shaping preview (`score_service`). Keeping them here — next to `compute_error` — means the
# "what-if" preview and the real run transform GBW-type log-scale specs into decades identically,
# instead of the API reimplementing (and diverging from) the scorer.
_LOG_BAND_FLOOR = np.float64(1e-12)  # floor a (target - tol) that would go <= 0 before log10


def log_space_band(curr_val, target_val, tolerance):
    """Map (value, target, LINEAR tolerance) into log10 space for a ``log_scale`` spec.

    ``tolerance`` is a band HALF-WIDTH, not a point on the axis, so ``log10(tolerance)`` is wrong —
    it produced an absurd / negative band that inverted pass/fail (BUG-B19). Instead derive the
    half-width in DECADES from the transformed bounds ``log10(target ± tol)``. Returns
    ``(log_curr, log_target, log_tol_halfwidth)``."""
    lc = np.float64(convert_linear_to_log(curr_val))
    lt = np.float64(convert_linear_to_log(target_val))
    lo = np.float64(convert_linear_to_log(max(target_val - tolerance, _LOG_BAND_FLOOR)))
    hi = np.float64(convert_linear_to_log(target_val + tolerance))
    half = np.float64(max(abs(hi - lt), abs(lt - lo)))
    return lc, lt, half


def log_space_range_coeff(target_val, range_val):
    """Decade-space error normalizer for a ``log_scale`` spec.

    A log-scale spec's error is measured in DECADES (via :func:`log_space_band`), so it must be
    normalized by a DECADE-space range — the number of decades the LINEAR ``range`` spans above the
    target, ``log10(target + range) - log10(target)``. Normalizing the decade-space error by the raw
    LINEAR ``range`` (e.g. dividing a ~1-decade miss by 1e8) collapses the penalty to ~0 and silently
    disables GBW-type log-scale constraints. Always finite and > 0 for
    ``target > 0`` and ``range > 0`` (the latter guaranteed by ``TargetSpec.__post_init__``)."""
    lt = np.float64(convert_linear_to_log(target_val))
    hi = np.float64(convert_linear_to_log(target_val + range_val))
    return np.float64(abs(hi - lt))

# ----------------------------
# Constraints function
# ----------------------------
# Numerical guards for the error/reward kernels (opt-in error/reward types — the shipped
# examples use relative-sigmoid/relative-absolute, but these must not produce inf/nan):
_EXP_ARG_CAP = np.float64(50.0)       # cap exp() argument so a large error can't overflow to inf
_LOG_REWARD_EPS = np.float64(1e-12)   # floor for log-reward operands so an exact match isn't -inf

# A - Normalized Error Functions
def compute_relative_absolute_error(curr_val: np.float64, target_val: np.float64, normalizing_coeff: np.float64) -> np.float64:
    return np.float64(np.abs(curr_val - target_val) / normalizing_coeff)
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_relative_squared_error(curr_val: np.float64, target_val: np.float64, normalizing_coeff: np.float64) -> np.float64:
    return np.float64(((curr_val - target_val) / normalizing_coeff) ** 2)
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_relative_exponential_error(curr_val: np.float64, target_val: np.float64, normalizing_coeff: np.float64) -> np.float64:
    # Clamp the exponent so a large (e.g. raw-SI-magnitude) error doesn't overflow to inf
    # and flatten the optimizer's gradient to a saturated penalty (BUG-B22).
    arg = np.minimum(np.abs(curr_val - target_val) / normalizing_coeff, _EXP_ARG_CAP)
    return np.float64(np.exp(arg) - 1)
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_relative_sigmoid_error(curr_val: np.float64, target_val: np.float64, normalizing_coeff: np.float64) -> np.float64:
    diff = abs(curr_val - target_val) / normalizing_coeff
    return 2.0 / (1.0 + np.exp(-diff)) - 1.0
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_log_cosh_error(curr, target, normalizing_coeff=1.0):
    """Log-Cosh loss, smooth and robust"""
    diff = (curr - target) / normalizing_coeff
    return np.log(np.cosh(diff))
# -----------------------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------------------
# B - Unnormalized Error Functions
def compute_absolute_error(curr_val: np.float64, target_val: np.float64) -> np.float64:
    return np.float64(np.abs(curr_val - target_val))
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_squared_error(curr_val: np.float64, target_val: np.float64) -> np.float64:
    return np.float64((curr_val - target_val) ** 2)
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_exponential_error(curr_val: np.float64, target_val: np.float64) -> np.float64:
    arg = np.minimum(np.abs(curr_val - target_val), _EXP_ARG_CAP)  # avoid inf overflow (BUG-B22)
    return np.float64(np.exp(arg) - 1)
# -----------------------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------------------
# C - Normalized Reward Functions
def compute_relative_absolute_reward(curr_val: np.float64, target_val: np.float64, normalizing_coeff : np.float64) -> np.float64:
    return np.float64(np.abs(curr_val - target_val) /  normalizing_coeff)
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_relative_log_reward(curr_val: np.float64, target_val: np.float64, normalizing_coeff : np.float64) -> np.float64:
    # Floor the difference so an exact match (curr == target) doesn't take log10(0) = -inf (BUG-B21).
    diff = np.maximum(np.abs(curr_val - target_val), _LOG_REWARD_EPS)
    return np.abs(np.log10(diff / normalizing_coeff))
# -----------------------------------------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------------------------------------
# D - Unnormalized Reward Functions
def compute_log_reward(curr_val: np.float64, target_val: np.float64) -> np.float64:
    # Floor both operands so a zero/negative metric or target doesn't yield -inf/nan (BUG-B21).
    num = np.maximum(np.abs(curr_val), _LOG_REWARD_EPS)
    den = np.maximum(np.abs(target_val), _LOG_REWARD_EPS)
    return np.abs(np.log10(num / den))
# -----------------------------------------------------------------------------------------------------------------------------------------------


# Dictionary to map error types to functions
ERROR_COMPUTE_FUNCTIONS : Dict[Error_Types, Callable]= {
    # Unnormalized Errors
    Error_Types.ABSOLUTE:     compute_absolute_error,
    Error_Types.SQUARED:      compute_squared_error,
    Error_Types.EXPONENTIAL:  compute_exponential_error,
    # Relative Errors
    Error_Types.RELATIVE_ABSOLUTE:      compute_relative_absolute_error,
    Error_Types.RELATIVE_SQUARED:       compute_relative_squared_error,
    Error_Types.RELATIVE_EXPONENTIAL:   compute_relative_exponential_error,
    Error_Types.RELATIVE_SIGMOID :      compute_relative_sigmoid_error
}


# Dictionary to map error types to functions
REWARD_COMPUTE_FUNCTIONS : Dict[Reward_Types, Callable]= {
    Reward_Types.RELATIVE_ABSOLUTE:  compute_relative_absolute_reward,
    Reward_Types.RELATIVE_LOG:       compute_relative_log_reward,
    Reward_Types.LOG:       compute_log_reward,
}

# -----------------------------------------------------------------------------------------------------------------------------------------------
# [Endpint] - Compute Error
def compute_error(curr_val: np.float64, target_val: np.float64, error_type: Error_Types | str, normalizing_coeff: np.float64 | None = None) -> np.float64:
    """Computes the error between curr_val and target_val based on the specified error_type."""
    if isinstance(error_type, str):
        error_type = Error_Types(error_type)

    if "relative" in error_type.value:
        if normalizing_coeff is None or not np.isfinite(normalizing_coeff) or normalizing_coeff <= 0:
            logger.error(f"Normalizing coefficient must be provided, finite and > 0 for relative error types. Got: {normalizing_coeff}")
            raise ValueError(f"Normalizing coefficient must be provided, finite and > 0 for relative error types. Got: {normalizing_coeff}")
        return ERROR_COMPUTE_FUNCTIONS[error_type](curr_val, target_val, normalizing_coeff)
    return ERROR_COMPUTE_FUNCTIONS[error_type](curr_val, target_val)

# [Endpint] - Compute Reward
def compute_reward(curr_val: np.float64, target_val: np.float64, reward_type: Reward_Types | str, normalizing_coeff: np.float64 | None = None, goal: OptimizationGoalType = OptimizationGoalType.EXCEED) -> np.float64:
    """Computes the reward for the spec"""
    if isinstance(reward_type, str):
        reward_type = Reward_Types(reward_type)

    if reward_type == Reward_Types.NO_REWARD:
        return np.float64(0)

    if "relative" in reward_type.value:
        if normalizing_coeff is None or not np.isfinite(normalizing_coeff) or normalizing_coeff <= 0:
            logger.error(f"Normalizing coefficient must be provided, finite and > 0 for relative reward types. Got: {normalizing_coeff}")
            raise ValueError(f"Normalizing coefficient must be provided, finite and > 0 for relative reward types. Got: {normalizing_coeff}")
        return REWARD_COMPUTE_FUNCTIONS[reward_type](curr_val, target_val, normalizing_coeff)
    return REWARD_COMPUTE_FUNCTIONS[reward_type](curr_val, target_val)


# [Endpint] - Aggregate per-corner scores (multi-corner PVT, Phase 2)
# Keyed by the CANONICAL strategy names validated at YAML-load time by
# spicexplorer_core.pvt.normalize_score_aggregation ("add"→sum, "average"→mean,
# "worst_case"→min), so this registry never needs to know the aliases.
CORNER_SCORE_AGGREGATORS: Dict[str, Any] = {
    "sum":  np.sum,   # add per-corner scores  — average-case bias, can mask one bad corner
    "mean": np.mean,  # average them           — magnitude comparable to a single-corner run
    "min":  np.min,   # worst case             — classic PVT sign-off; any failing corner dominates
}


def aggregate_corner_scores(corner_scores: Dict[str, np.float64], strategy: str) -> np.float64:
    """Collapse per-corner total scores {corner_name: score} into one scalar objective.

    **Constraint-first.** A per-corner total ``< 0`` means that corner *fails* a
    constraint (its score is a penalty sum); ``>= 0`` means it *passes* (a reward sum) —
    the exact lexicographic rule ``compute_fitness`` applies per spec
    (``total = reward if penalty > -EPS else penalty``), lifted to the corner axis. So:

    - **If ANY corner fails**, aggregate ONLY the failing corners' penalties. A
      comfortably-passing corner's large positive reward can then never numerically
      out-vote a failing corner's penalty under ``mean``/``sum`` (the masking bug).
    - **Only when EVERY corner passes** do we aggregate the (positive) rewards.

    ``min`` is unaffected (it already picks the worst corner); this makes ``mean``/``sum``
    masking-safe while keeping the all-pass reward landscape intact. ``mean`` stays the
    default: range specs (e.g. phase margin) are two-sided, so a blanket worst-corner
    scalarization is the right *sign-off* lens but a poor *optimization* objective.
    """
    if not corner_scores:
        raise ValueError("aggregate_corner_scores needs at least one corner score.")
    aggregator = CORNER_SCORE_AGGREGATORS.get(strategy)
    if aggregator is None:
        raise ValueError(
            f"Unknown corner score_aggregation '{strategy}'. "
            f"Canonical strategies: {sorted(CORNER_SCORE_AGGREGATORS)}."
        )
    # Partition on sign: failing corners (penalty) take precedence over passing ones (reward).
    penalties = {c: s for c, s in corner_scores.items() if s < 0}
    subset = penalties if penalties else corner_scores
    return np.float64(aggregator(list(subset.values())))


# ----------------------------
# norm/denorm function
# ----------------------------
def log_normalize(p, pmin, pmax) -> float:
    """
    Log-normalize parameter p to [0, 1] range.
    p, pmin, pmax must be > 0.
    Always returns a float.
    """
    p = np.asarray(p, dtype=np.float64)
    pmin = np.asarray(pmin, dtype=np.float64)
    pmax = np.asarray(pmax, dtype=np.float64)

    log_p = np.log10(p)
    log_min = np.log10(pmin)
    log_max = np.log10(pmax)
    result = (log_p - log_min) / (log_max - log_min)
    return float(np.asarray(result, dtype=np.float64))

def log_denormalize(x, pmin, pmax) -> float:
    """
    Map normalized x in [0, 1] back to physical parameter using log scaling.
    Always returns a float.
    """
    x = np.asarray(x, dtype=np.float64)
    pmin = np.asarray(pmin, dtype=np.float64)
    pmax = np.asarray(pmax, dtype=np.float64)

    log_min = np.log10(pmin)
    log_max = np.log10(pmax)
    log_p = x * (log_max - log_min) + log_min
    result = 10.0 ** log_p
    return float(np.asarray(result, dtype=np.float64))

def linear_normalize(p, pmin, pmax) -> float:
    """
    Linearly normalize parameter p to [0, 1] range.
    Always returns a float.
    """
    p = np.asarray(p, dtype=np.float64)
    pmin = np.asarray(pmin, dtype=np.float64)
    pmax = np.asarray(pmax, dtype=np.float64)

    result = (p - pmin) / (pmax - pmin)
    return float(np.asarray(result, dtype=np.float64))

def linear_denormalize(x, pmin, pmax) -> float:
    """
    Map normalized x in [0, 1] back to physical parameter linearly.
    Always returns a float.
    """
    x = np.asarray(x, dtype=np.float64)
    pmin = np.asarray(pmin, dtype=np.float64)
    pmax = np.asarray(pmax, dtype=np.float64)

    result = pmin + x * (pmax - pmin)
    return float(np.asarray(result, dtype=np.float64))

# ----------------------------
# Plotting
# ----------------------------
def plot_ac_response(frequencies: torch.Tensor, mag_list: list, phase_list: list, labels: list = None, title: str = "Frequency Response"):
    """(Deprecated) Plots multiple AC responses on the same plot using Plotly for interactivity.

    Args:
        frequencies: A PyTorch tensor of frequencies (shared by all responses).
        H_f_list: A list of PyTorch tensors, each representing the complex frequency response (H_f) of a circuit.
        phase_list: A list of PyTorch tensors, each representing the phase response of a circuit.
        labels: A list of strings, each representing the label for a circuit's response.
        title: The title of the plot.
    """

    if labels is None:
        labels = [f"Series {i}" for i in range(len(mag_list))]

    fig = make_subplots(rows=2, cols=1, subplot_titles=("Gain (dB)", "Phase (deg)"))
    helper = Transfer_Func_Helper()
    for H_f, phase, label in zip(mag_list, phase_list, labels):
        fig.add_trace(go.Scatter(x=frequencies.tolist(), y=helper.convert_to_dB(H_f).tolist(), mode='lines', name=f"{label}-mag"), row=1, col=1)  # Gain
        fig.add_trace(go.Scatter(x=frequencies.tolist(), y=phase.tolist(), mode='lines', name=f"{label}-phase"), row=2, col=1)  # Phase

    fig.update_layout(
        title=title,
        xaxis_type="log",  # Logarithmic frequency axis
        xaxis_title="Frequency (Hz)",
        yaxis_title="Gain (dB)",
        xaxis2_type="log", # Logarithmic frequency axis for phase plot
        xaxis2_title="Frequency (Hz)",
        yaxis2_title="Phase (deg)",
        height=800,  # Set the height (in pixels) - Increase this value
        width=1000   # Set the width (in pixels)
    )

    fig.show()

def plot_complex_response(frequencies: torch.Tensor, complex_response_list: list, labels: list = None, title: str = "Frequency Response"):
    """Plots multiple AC responses on the same plot using Plotly for interactivity.

    Args:
        frequencies: A PyTorch tensor of frequencies (shared by all responses).
        complex_response_list: A list of PyTorch tensors, each representing the complex frequency response (H_f) of a circuit.
        labels: A list of strings, each representing the label for a circuit's response.
        title: The title of the plot.
    """

    if labels is None:
        labels = [f"Series {i}" for i in range(len(complex_response_list))]

    fig = make_subplots(rows=2, cols=1, subplot_titles=("Gain (dB)", "Phase (deg)"))

    helper = Transfer_Func_Helper()

    for complex_response, label in zip(complex_response_list, labels):

        magnitude_dB, phase_deg = helper.get_mag_phase_from_complex_response(complex_response)

        # Plot magnitude response
        fig.add_trace(go.Scatter(
            x=frequencies.tolist(),
            y=magnitude_dB.tolist(),
            mode='lines',
            name=f"{label}-mag"
        ), row=1, col=1)

        # Plot phase response
        fig.add_trace(go.Scatter(
            x=frequencies.tolist(),
            y=phase_deg.tolist(),
            mode='lines',
            name=f"{label}-phase"
        ), row=2, col=1)

    fig.update_layout(
        title=title,
        xaxis_type="log",  # Logarithmic frequency axis
        xaxis_title="Frequency (Hz)",
        yaxis_title="Gain (dB)",
        xaxis2_type="log",  # Logarithmic frequency axis for phase plot
        xaxis2_title="Frequency (Hz)",
        yaxis2_title="Phase (deg)",
        height=800,  # Set the height (in pixels)
        width=1000   # Set the width (in pixels)
    )

    fig.show()

# Helper Functions
def _linear_interpolate(x1, y1, x2, y2, target_y):
        """Interpolates x for a given target_y using two known points (x1, y1) and (x2, y2)."""
        if y1 == y2:  # Avoid division by zero
            return x1
        return x1 + (x2 - x1) * ((target_y - y1) / (y2 - y1))

# ----------------------------
# Classes
# ----------------------------
class Transfer_Func_Helper:
    def __init__(self):
        pass

    def convert_from_dB(self, val: torch.Tensor) -> torch.Tensor:
        return torch.pow(10, val / 20)

    def convert_to_dB(self, val: torch.Tensor) -> torch.Tensor:
        return 20 * torch.log10(val)

    def convert_to_omega(self, f: torch.Tensor) -> torch.Tensor:
        return 2 * torch.pi * f

    def convert_to_f(self, omega: torch.Tensor) -> torch.Tensor:
        return omega / (2 * torch.pi)

    def eval_tf(self, tf: sp.Expr, f_val: torch.Tensor) -> torch.Tensor:
        s = sp.symbols("s")

        # Convert torch tensor to NumPy before passing to lambdify
        H_f = sp.lambdify(s, tf, "numpy")
        f_numpy = f_val.cpu().numpy()  # Ensure f_val is a NumPy array

        # Evaluate transfer function
        H_result = H_f(f_numpy * 2 * np.pi * 1j)  # Keep NumPy operations

        # Convert back to PyTorch tensor using torch.from_numpy
        return torch.from_numpy(np.asarray(H_result, dtype=np.complex64)).to(f_val.device)

    def get_mag_phase_from_complex_response(self, complex_response_array: torch.Tensor, epsilon: float = 1e-12) -> Tuple[torch.Tensor, torch.Tensor]:
        mag   = 20 * torch.log10(torch.clamp(torch.abs(complex_response_array), min=epsilon))
        phase = torch.tensor(np.unwrap(torch.angle(complex_response_array)) * 180.0 / np.pi)
        return mag, phase

    def get_ac_response_from_symbolic(self, tf: sp.Expr, frequencies: torch.Tensor, epsilon: float = 1e-12) -> Tuple[torch.Tensor, torch.Tensor]:
        complex_response_array = self.eval_tf(tf, frequencies)
        mag, phase  = self.get_mag_phase_from_complex_response(complex_response_array=complex_response_array, epsilon=epsilon)
        return mag, phase

    def control_tf_to_sympy(self, tf_sys):
        """
        Converts a control.TransferFunction to a sympy symbolic transfer function.

        Parameters:
        tf_sys (control.TransferFunction): The transfer function from the control module.

        Returns:
        sympy.Expr: The symbolic transfer function H(s).
        """
        s = sp.symbols('s')  # Define the Laplace variable

        # Extract numerator and denominator coefficients
        num_coeffs = tf_sys.num[0][0]  # Extract numerator coefficients
        den_coeffs = tf_sys.den[0][0]  # Extract denominator coefficients

        # Construct symbolic numerator and denominator polynomials
        num_expr = sum(c * s**i for i, c in enumerate(reversed(num_coeffs)))
        den_expr = sum(c * s**i for i, c in enumerate(reversed(den_coeffs)))

        # Construct and return the symbolic transfer function
        return num_expr / den_expr

    def sympy_tf_to_control(self, H_s):
        """
        Converts a sympy symbolic transfer function to a control.TransferFunction.

        Parameters:
        H_s (sympy.Expr): The symbolic transfer function.
        s (sympy.Symbol): The Laplace variable.

        Returns:
        control.TransferFunction: Equivalent transfer function in the control module.
        """
        s = sp.symbols("s")

        # Get numerator and denominator
        num_expr, den_expr = sp.fraction(H_s)  # Extract numerator and denominator

        # Convert to polynomials
        num_poly = sp.Poly(num_expr, s)
        den_poly = sp.Poly(den_expr, s)

        # Get coefficients in order of decreasing powers
        num_coeffs = [float(c) for c in num_poly.all_coeffs()]
        den_coeffs = [float(c) for c in den_poly.all_coeffs()]

        # Create control.TransferFunction
        return ctrl.TransferFunction(num_coeffs, den_coeffs)

    def compute_cutoff(self, freq: torch.Tensor, mag_db: torch.Tensor, drop_by: float = 3.0) -> Tuple[Tuple[torch.Tensor], int]:
        """
        Computes the 3dB (can be changed) cutoff frequencies for a Low-Pass or Band-Pass filter.

        Args:
            freq (torch.Tensor): Frequency vector (1D tensor).
            mag_db (torch.Tensor): Magnitude response (1D tensor in dB).
            drop_by (float): The dB drop defining the cutoff.
        """
        # Find max gain and cutoff level
        curr_max_mag = torch.max(mag_db)
        cutoff_level = curr_max_mag - drop_by

        # Find transitions where mag_db crosses the cutoff level
        crossings = []
        for i in range(1, len(mag_db)):
            if (mag_db[i-1] > cutoff_level and mag_db[i] <= cutoff_level) or \
            (mag_db[i-1] < cutoff_level and mag_db[i] >= cutoff_level):
                # Interpolate for more accurate cutoff frequency
                f_c = _linear_interpolate(freq[i-1].item(), mag_db[i-1].item(),
                                        freq[i].item(), mag_db[i].item(),
                                        cutoff_level)
                crossings.append(f_c)

        if len(crossings) == 0:
            return None, 0  # No valid cutoff found

        elif len(crossings) == 1:
            # Single cutoff -> LPF or HPF
            return (crossings[0],), 1

        elif len(crossings) >= 2:
            # Two cutoffs -> BPF
            return (crossings[0], crossings[-1]), 2

        return None, 0  # Fallback case

class Frequency_Weight:
    def __init__(self, lower: float, upper: float, frequency_array: torch.Tensor = None, bias: float = 10):
        """
        Initializes the Frequency_Weight object.

        Args:
            lower (float): The lower bound of the frequency range to get the bias.
            upper (float): The upper bound of the frequency range to get the bias.
            frequency_array (torch.Tensor): The input tensor of frequencies.
            bias (float, optional): The weight assigned to frequencies within the bounds. Default is 10.
        """
        self.lower = lower
        self.upper = upper
        self.bias  = bias
        self.parent_frequency_array = frequency_array
        if frequency_array is not None:
            self.weights = torch.where((frequency_array >= lower) & (frequency_array <= upper), bias, torch.tensor(1.0))
        else:
            self.weights = None

    def compute_weights(self) -> torch.Tensor:
        if self.parent_frequency_array is not None:
            self.weights = torch.where((self.parent_frequency_array >= self.lower) & (self.parent_frequency_array <= self.upper), self.bias, torch.tensor(1.0))
            return self.weights
        return None

    def __add__(self, other):
        """
        Takes the element-wise maximum of the weight tensors of two Frequency_Weight objects.

        Args:
            other (Frequency_Weight): Another Frequency_Weight object.

        Returns:
            Frequency_Weight: A new object with the maximum weights at each index.
        """
        if not isinstance(other, Frequency_Weight):
            raise TypeError("Can only add Frequency_Weight objects.")

        if self.parent_frequency_array is None:
            return other

        new_obj = Frequency_Weight(frequency_array=self.parent_frequency_array, lower=-1, upper=-1)  # Dummy instance
        new_obj.weights = torch.maximum(self.weights, other.weights)
        return new_obj

    def __repr__(self):
        return f"Frequency_Weight(weights={self.weights})"
