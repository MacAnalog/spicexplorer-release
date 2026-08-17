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
import warnings

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

        # Avoid division by zero (a FLAT target response has max == min) — the same clamp
        # the z-score branch applies to `std`; unclamped this returned inf/NaN and poisoned
        # the ranking of every candidate scored against that target.
        span = (max_val - min_val).clamp(min=epsilon)
        loss = torch.mean(weights * (response - target_response) ** 2 / (span ** 0.5))

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
        # Avoid division by zero (a FLAT target response has max == min) — see
        # `weighted_mse_loss`; unclamped this returned inf/NaN.
        span = (max_val - min_val).clamp(min=epsilon)
        loss = torch.mean(weights * torch.abs(response - target_response) / (span ** 0.5))

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
_LOG_BAND_FLOOR = np.float64(1e-12)  # floor any operand that would go <= 0 before log10


def log_space_band(curr_val, target_val, tolerance):
    """Map (value, target, LINEAR tolerance) into log10 space for a ``log_scale`` spec.

    ``tolerance`` is a band HALF-WIDTH, not a point on the axis, so ``log10(tolerance)`` is wrong —
    it produced an absurd / negative band that inverted pass/fail (BUG-B19). Instead derive the
    half-width in DECADES from the transformed bounds ``log10(target ± tol)``. Returns
    ``(log_curr, log_target, log_tol_halfwidth)``.

    A ``curr_val`` that is **not strictly positive** — ``0`` (``log10 -> -inf``), NEGATIVE
    (``log10 -> nan``) or ``nan`` — is replaced by ``_LOG_BAND_FLOOR``: the SAME
    ``value if value > 0 else floor`` guard the API Score-Shaping preview applies at its call
    site (``score_service._resolve_penalty_space``), so preview and run agree. Without it a
    bad sizing poisoned the transform: the ``nan`` made every band comparison ``False`` so the
    scorer recorded the constraint SATISFIED, and the ``-inf`` clipped to ``+MAX_REWARD`` — a
    degenerate candidate became a permanent global best.

    Scope of the guarantee (it is narrower than "total and finite", which an earlier revision
    of this docstring claimed and ``max()`` did not deliver — ``max(nan, floor)`` returns
    ``nan``):

    * the returned ``log_curr`` is **never nan** for any ``curr_val``, and is finite for every
      finite ``curr_val``;
    * a **strictly positive** ``curr_val`` is transformed AS READ, including below the floor —
      ``1e-13`` and ``1e-18`` are 5 decades apart and must score 5 decades apart. Clamping the
      current value UP to the floor (rather than only substituting for non-positives) flattened
      them onto one score;
    * ``+inf`` maps to ``+inf`` decades by design: admitting or rejecting a non-finite
      reading is :func:`is_scoreable_metric`'s job (it rejects every one of them), not this
      transform's. The scorer never reaches here with a non-finite ``curr_val``."""
    curr = np.float64(curr_val)
    lc = np.float64(convert_linear_to_log(curr if curr > 0 else _LOG_BAND_FLOOR))
    lt = np.float64(convert_linear_to_log(target_val))
    lo = np.float64(convert_linear_to_log(max(target_val - tolerance, _LOG_BAND_FLOOR)))
    hi = np.float64(convert_linear_to_log(target_val + tolerance))
    half = np.float64(max(abs(hi - lt), abs(lt - lo)))
    return lc, lt, half


def is_scoreable_metric(curr_val, *, log_scale: bool = False) -> bool:
    """Is ``curr_val`` a metric reading the scorer may actually score?

    Scoreable iff it is **finite** and — under ``log_scale`` — strictly positive. Anything
    else is a degenerate reading (a diverged/failed sim, a swept curve that collapsed) and
    must be scored as the maximal penalty, exactly like a missing/NaN metric, rather than fed
    to the error/reward kernels:

    * ``±inf`` is finite-looking to a bare ``isnan`` gate, and on a spec WITH a reward it
      produced an infinite reward that clipped to ``+MAX_REWARD`` — the best score the scorer
      can emit — so a degenerate candidate became a permanent global best (finding O-1).
    * ``<= 0`` under ``log_scale`` has no decade: the shipped ppa campaigns set ``log_scale: true``
      on ``power``/``active_area``/``v(inoise_total)``/``cap_area``, all of which a bad sizing can
      drive to ``0`` or negative. Floored to ``_LOG_BAND_FLOOR`` it would read as ``-12`` decades —
      i.e. *infinitely good* for a MINIMIZE spec — so rejecting it is the fail-loud reading.

    **The test is deliberately NOT goal-aware** (a goal-aware revision was written and
    reverted). The Tier-1 measurement library does emit ``+inf`` as a *perfect* sentinel
    (``sfdr_from_harmonics`` on a spur-free spectrum, ``iip3_from_harmonics`` on an
    unmeasurable IM3), so admitting a goal-ALIGNED infinity looks like the kinder reading —
    but the same ``+inf`` is also what a **diverged** solve produces, and the two are
    indistinguishable at this layer. 54 shipped campaign specs are EXCEED + linear + a
    relative-absolute reward, and every one of them is ``dcgain``
    (``20·log10|H|`` at the lowest AC point), where ``+inf`` means the AC solve blew up. On
    those, admitting the infinity re-opens exactly the ``+MAX_REWARD`` clip O-1 exists to
    close. Mistaking a divergence for perfection is unrecoverable — it poisons the whole
    run; mistaking perfection for a divergence costs one candidate. So every non-finite
    reading is rejected, whatever the goal.

    The underlying collision (the registry overloading ``inf`` for "perfect") is a
    cross-package API decision, recorded in ``doc/TODO.md`` §22 — not worked around here."""
    val = np.float64(curr_val)
    if not np.isfinite(val):
        return False
    return not (log_scale and val <= 0.0)


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

#: Feasibility threshold: a total penalty within one EPSILON of zero counts as FEASIBLE, so float
#: dust in a satisfied spec cannot suppress the reward landscape. Defined here (next to the
#: aggregation kernels that use it) and re-exported by `optimization.base` — one definition, so the
#: scorer and the aggregators can never drift apart on what "feasible" means.
EPSILON = np.float64(1e-12)

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
def compute_relative_sigmoid_error(curr_val: np.float64, target_val: np.float64, normalizing_coeff: np.float64, alpha: float = 1.0) -> np.float64:
    """Bounded [0,1) squashed penalty: 2 / (1 + exp(-alpha * d)) - 1, with d the normalized error.

    `alpha` is the SATURATION RATE: a larger alpha reaches the bound sooner, so the penalty
    behaves more like a hard constraint; a smaller alpha stays closer to linear over a wider
    range of misses. It defaults to 1.0, which is the value this kernel was previously hardcoded
    at, so every existing spec is unchanged.

    Analytically alpha is redundant with the normalizer (`sigmoid(alpha*p/S) == sigmoid(p/(S/alpha))`),
    but it is NOT redundant in practice: `range` is a per-spec fact authored alongside the target,
    while alpha is a property of the SHAPING being studied. Sweeping alpha with the spec set held
    fixed is what isolates the shaping effect; achieving the same by rewriting every spec's `range`
    would confound the two.
    """
    alpha = float(alpha)
    if not np.isfinite(alpha) or alpha <= 0:
        logger.error(f"relative-sigmoid requires a finite alpha > 0. Got: {alpha}")
        raise ValueError(f"relative-sigmoid requires a finite alpha > 0. Got: {alpha}")
    diff = abs(curr_val - target_val) / normalizing_coeff
    # Cap as in the other exp kernels; the argument is negated, so a large error underflows to
    # exp(-cap) ~ 0 and the penalty saturates at 1 instead of overflowing.
    arg = np.minimum(alpha * diff, _EXP_ARG_CAP)
    return 2.0 / (1.0 + np.exp(-arg)) - 1.0
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_relative_gaussian_error(curr_val: np.float64, target_val: np.float64, normalizing_coeff: np.float64, sigma: float = 1.0) -> np.float64:
    """Inverted-Gaussian penalty: 1 - exp(-d^2 / (2*sigma^2)), with d the normalized error.

    Bounded on [0, 1] like relative-sigmoid, so the two are directly comparable and one far-off
    metric cannot dominate the aggregate. They differ in the near-target region: the sigmoid's
    slope is MAXIMAL at d = 0, this one's VANISHES there and peaks near d = sigma. That makes
    this the controlled comparison for whether the benefit of relative-sigmoid comes from
    bounding the error or from smoothing it.

    `sigma` is the width in normalized-error units and is swept; it arrives from the spec's
    `error_params`. A smaller sigma saturates sooner, i.e. treats a near-miss more like a hard
    constraint.

    NOTE — where the landscape goes flat. In float64 this reaches EXACTLY 1.0 once
    d/sigma exceeds roughly 9 (1 - exp(-40) rounds to 1.0), so beyond that the optimizer sees
    no gradient at all. relative-sigmoid, decaying only exponentially in d rather than d^2,
    stays below 1.0 until d ~ 36. That is a real behavioural difference, not a rounding
    curiosity: with sigma = 1 a metric more than ~9 range-units off target is indistinguishable
    from one a million units off. Choose sigma with the expected miss magnitude in mind, and
    prefer a larger sigma when the search must climb out of a far-off region.
    """
    sigma = float(sigma)
    if not np.isfinite(sigma) or sigma <= 0:
        logger.error(f"relative-gaussian requires a finite sigma > 0. Got: {sigma}")
        raise ValueError(f"relative-gaussian requires a finite sigma > 0. Got: {sigma}")
    diff = (curr_val - target_val) / normalizing_coeff
    # Cap as in the exponential kernels. Here the argument is negated, so a large error
    # underflows to exp(-cap) ~ 0 and the penalty saturates at 1 instead of overflowing.
    arg = np.minimum((diff * diff) / (2.0 * sigma * sigma), _EXP_ARG_CAP)
    return np.float64(1.0 - np.exp(-arg))
# -----------------------------------------------------------------------------------------------------------------------------------------------
def compute_log_cosh_error(curr, target, normalizing_coeff=1.0):
    """Log-Cosh loss, smooth and robust"""
    diff = (curr - target) / normalizing_coeff
    return np.log(np.cosh(diff))
# -----------------------------------------------------------------------------------------------------------------------------------------------
#: Running-scale strategies `relative-adaptive` accepts.
ADAPTIVE_STRATEGIES: Tuple[str, ...] = ("running_mean", "ema", "running_max")

#: What the synthetic "past sample" that primes the statistic is derived from. Resolved to a
#: NUMBER by `TargetSpec` at load, because only the spec knows its target, range and `log_scale`
#: (a log-scale spec's samples are in DECADES, so the seed has to be too).
ADAPTIVE_SEED_BASES: Tuple[str, ...] = ("target", "range", "none")


class AdaptiveNormalizer:
    """Running per-spec error scale ``S_i`` for the ``relative-adaptive`` error type.

    Every other error type divides by a **fixed** normalizer — the spec's ``range``, authored by
    hand. That is what makes a mixed-unit spec set hard to balance: a 1e9 Hz bandwidth miss and a
    1e-6 A current miss are only commensurable if someone guessed both ranges well. Adaptive
    normalization replaces the guess with a statistic of the errors this spec has ACTUALLY produced
    so far, so each metric self-calibrates to its own observed scale.

    **Configuration.**

    * ``strategy`` — ``running_mean`` | ``ema`` | ``running_max``.
    * ``window`` — how many of the MOST RECENT samples the statistic covers (``running_mean`` and
      ``running_max``). ``None``/``0`` means every sample ever seen. A bounded window makes the
      scale forget early exploration, which matters because the errors seen in the first hundred
      random trials are not the errors seen near the feasible region — an all-time mean stays
      anchored to a regime the search has left. ``ema`` ignores it (its ``ema_beta`` already sets
      an effective memory of roughly ``1/(1-beta)`` samples).
    * ``seed`` / ``seed_weight`` — the synthetic "past sample" the history starts from, and how
      many copies of it. Without a seed the first real observation defines the scale by itself, so
      the very first violation always normalizes to exactly 1.0 whatever its size. Seeding from
      the target magnitude means "assume a 100 % miss until proven otherwise", which is a
      defensible prior and is what makes ``warmup: 0`` usable.
    * ``warmup`` — evaluations during which the scale stays pinned to the static fallback. Largely
      SUPERSEDED by ``seed``: seeding gives a sensible scale from evaluation one, where warmup
      just defers the question. Kept for the un-seeded style and for reproducing a fixed-scale
      run. Counted in REAL observations; seeded samples do not advance it.

    **This object is mutable and its scale depends on evaluation ORDER.** Consequences that are
    properties of the method, not defects, and that every consumer must know:

    * The objective is **non-stationary** — the same design point scores differently early and late
      in a run. That is inherent to adaptive normalization (Somani & Patra) and is precisely what
      the comparison against the fixed-scale types is meant to measure.
    * State is **per spec, per optimizer instance** — never a module-level singleton. Two runs in one
      process, or two corners of one trial, must not share a scale. (The corner axis deliberately
      DOES share it: corners are repeated observations of the same metric.)

    Only VIOLATING errors are ever observed, because the scorer calls the error kernel only outside
    the tolerance band. So ``S_i`` calibrates to the scale of this spec's *violations*, and a spec
    satisfied from the first trial never leaves its seed — both intended.
    """

    __slots__ = ("strategy", "ema_beta", "warmup", "window", "seed", "seed_weight",
                 "frozen", "n", "_samples", "_sum", "_max", "_ema")

    def __init__(self, strategy: str = "running_mean", ema_beta: float = 0.9, warmup: int = 0,
                 window: int | None = None, seed: float | None = None, seed_weight: int = 1):
        strategy = str(strategy).strip().lower()
        if strategy not in ADAPTIVE_STRATEGIES:
            raise ValueError(
                f"Unknown relative-adaptive strategy {strategy!r}. Valid: {list(ADAPTIVE_STRATEGIES)}."
            )
        beta = float(ema_beta)
        # A beta at either endpoint degenerates: 0 makes the EMA the last error alone (no memory,
        # so the scale rattles trial to trial), 1 freezes it at the first observation forever.
        if not np.isfinite(beta) or not (0.0 < beta < 1.0):
            raise ValueError(f"relative-adaptive ema_beta must be finite and in (0, 1). Got: {ema_beta!r}.")
        warm = int(warmup)
        if warm < 0:
            raise ValueError(f"relative-adaptive warmup must be >= 0. Got: {warmup!r}.")
        win = None if window is None else int(window)
        if win is not None and win < 0:
            raise ValueError(f"relative-adaptive window must be >= 0 (0/None = unbounded). Got: {window!r}.")
        if win == 0:
            win = None
        sw = int(seed_weight)
        if sw < 0:
            raise ValueError(f"relative-adaptive seed_weight must be >= 0. Got: {seed_weight!r}.")
        sd = None if seed is None else float(seed)
        if sd is not None and (not np.isfinite(sd) or sd <= 0):
            raise ValueError(f"relative-adaptive seed must be finite and > 0 (or None). Got: {seed!r}.")
        if sd is not None and win is not None and sw > win:
            # Otherwise the window is entirely seed and no real observation can ever influence it.
            raise ValueError(
                f"relative-adaptive seed_weight ({sw}) must not exceed window ({win}) — the "
                "window would hold nothing but the seed and the scale could never adapt.")
        self.strategy = strategy
        self.ema_beta = beta
        self.warmup = warm
        self.window = win
        self.seed = sd
        self.seed_weight = sw
        self.frozen = False
        self.reset()

    # ---- internals -------------------------------------------------------------------
    def _recompute_windowed(self) -> None:
        """Rebuild the O(1) accumulators from the retained window."""
        self._sum = np.float64(sum(self._samples)) if self._samples else np.float64(0.0)
        self._max = np.float64(max(self._samples)) if self._samples else np.float64(0.0)

    def reset(self) -> None:
        """Clear the statistic back to its seeded starting point.

        Use before re-scoring a logged run, so the replay starts where the original run did rather
        than inheriting whatever scale the live run ended on."""
        self.n = 0                                   # REAL observations only (drives `warmup`)
        self._samples: list[np.float64] = []
        self._ema: np.float64 | None = None
        if self.seed is not None and self.seed_weight > 0:
            seed = np.float64(self.seed)
            self._samples = [seed] * self.seed_weight
            self._ema = seed                         # the EMA starts AT the prior, not below it
        self._recompute_windowed()

    def observe(self, raw_error: np.float64 | float) -> None:
        """Fold one raw (un-normalized) error magnitude into the statistic.

        Non-finite readings are DROPPED rather than folded in: a single ``inf`` would pin
        ``running_max`` at ``inf`` for the rest of the run and drive every subsequent normalized
        error to 0, silently disabling the spec. (The scorer already rejects non-finite metrics
        upstream via :func:`is_scoreable_metric`; this is the second line of defence.) A ``frozen``
        normalizer ignores observations entirely — that is how a manual single sim or a post-hoc
        re-score reads the landscape without perturbing it."""
        if self.frozen:
            return
        err = np.float64(abs(np.float64(raw_error)))
        if not np.isfinite(err):
            logger.debug("relative-adaptive: dropping non-finite observation %r", raw_error)
            return
        self.n += 1
        self._samples.append(err)
        if self.window is not None and len(self._samples) > self.window:
            # Oldest-out. The seed occupies the oldest slots, so it is the FIRST thing evicted —
            # the prior fades exactly as real evidence accumulates, which is what a prior is for.
            del self._samples[:len(self._samples) - self.window]
        self._recompute_windowed()
        self._ema = err if self._ema is None else np.float64(
            self.ema_beta * self._ema + (1.0 - self.ema_beta) * err)

    def scale(self, fallback: np.float64 | float) -> np.float64:
        """The current ``S_i``, or ``fallback`` (the spec's static normalizer) during warmup.

        ``fallback`` is supplied per call rather than stored, so a ``log_scale`` spec — whose errors
        are in DECADES — automatically calibrates against the decade-space coefficient its caller
        already computed, with no special case here.

        Falls back whenever the statistic is not usable (no samples at all, or every retained
        sample was zero, or non-finite). Dividing by a zero scale would produce ``inf``/``nan`` and
        poison the whole run's ranking, so the fixed normalizer is always the safe floor."""
        fb = np.float64(fallback)
        if self.n < self.warmup:
            return fb
        if self.strategy == "running_mean":
            stat = (np.float64(self._sum / len(self._samples)) if self._samples
                    else np.float64(0.0))
        elif self.strategy == "running_max":
            stat = np.float64(self._max)
        else:  # "ema"
            stat = np.float64(self._ema) if self._ema is not None else np.float64(0.0)
        if not np.isfinite(stat) or stat <= 0.0:
            return fb
        return stat

    def describe(self) -> Dict[str, Any]:
        """Config + live state, for logging a run's shaping provenance."""
        return {"strategy": self.strategy, "ema_beta": self.ema_beta, "warmup": self.warmup,
                "window": self.window, "seed": self.seed, "seed_weight": self.seed_weight,
                "n_observed": self.n, "n_retained": len(self._samples), "frozen": self.frozen}

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return (f"AdaptiveNormalizer(strategy={self.strategy!r}, ema_beta={self.ema_beta}, "
                f"warmup={self.warmup}, window={self.window}, seed={self.seed}, "
                f"seed_weight={self.seed_weight}, n={self.n}, frozen={self.frozen})")


#: One-shot guard so an unwired `relative-adaptive` seam shouts once rather than per evaluation.
_WARNED_STATELESS_ADAPTIVE = False


#: Message for an unwired stateful seam. Module-level so tests can match it exactly rather than
#: on a fragment that a reword would silently break.
UNWIRED_ADAPTIVE_SEAM_MSG = (
    "UNWIRED SEAM: relative-adaptive was evaluated with NO AdaptiveNormalizer state. "
    "It is silently behaving as relative-absolute — i.e. as the LINEAR BASELINE this error type "
    "is supposed to be compared against. Any sweep in this state produces an adaptive arm that "
    "duplicates its own control while appearing to have run. "
    "Pass the owning spec's `TargetSpec.error_state` via `compute_error(..., error_state=)`. "
    "A stateless one-shot preview is the only legitimate case."
)


def compute_relative_adaptive_error(
    curr_val: np.float64,
    target_val: np.float64,
    normalizing_coeff: np.float64,
    strategy: str = "running_mean",
    ema_beta: float = 0.9,
    warmup: int = 0,
    window: int | None = None,
    seed: float | None = None,
    seed_weight: int = 1,
    state: "AdaptiveNormalizer | None" = None,
) -> np.float64:
    """Absolute error divided by an ADAPTIVE scale: ``|curr - target| / S_i``.

    Identical in shape to ``relative-absolute`` — the difference is entirely in the denominator.
    ``S_i`` is a running statistic of this spec's observed errors (see :class:`AdaptiveNormalizer`)
    instead of the authored ``range``, so specs spanning wildly different units become comparable
    without hand-tuned constants.

    ``state`` carries that statistic and is supplied by the caller (the scorer passes the spec's
    own, built and configured at load). The remaining keyword arguments mirror the configuration
    so the signature documents the vocabulary and a direct caller can build an equivalent state;
    they are NOT read here — ``state`` already carries its own configuration, and having this
    function silently re-configure a state it does not own would be a second source of truth.

    **Without ``state`` this degrades to exactly ``relative-absolute``** and shouts about it: see
    :data:`UNWIRED_ADAPTIVE_SEAM_MSG`. The degradation is silent in its numbers, which is the
    dangerous kind, so it is reported at ERROR level *and* raised as a `RuntimeWarning` (visible
    on stderr, and promotable to a hard failure with ``-W error::RuntimeWarning``). Emitted once
    per process — a 2000-evaluation run would otherwise bury the run log.
    """
    global _WARNED_STATELESS_ADAPTIVE
    diff = np.float64(abs(np.float64(curr_val) - np.float64(target_val)))
    if state is None:
        if not _WARNED_STATELESS_ADAPTIVE:
            _WARNED_STATELESS_ADAPTIVE = True
            logger.error(UNWIRED_ADAPTIVE_SEAM_MSG)
            warnings.warn(UNWIRED_ADAPTIVE_SEAM_MSG, RuntimeWarning, stacklevel=2)
        return np.float64(diff / normalizing_coeff)
    state.observe(diff)
    return np.float64(diff / state.scale(normalizing_coeff))
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
    Error_Types.RELATIVE_SIGMOID :      compute_relative_sigmoid_error,
    Error_Types.RELATIVE_GAUSSIAN:      compute_relative_gaussian_error,
    Error_Types.RELATIVE_ADAPTIVE:      compute_relative_adaptive_error,
}

#: Error types whose kernel carries mutable state across evaluations. The scorer must hand each of
#: these the owning spec's own state object (`TargetSpec.error_state`); every other error type is a
#: pure function of (curr, target, coeff) and ignores it.
STATEFUL_ERROR_TYPES: Tuple[Error_Types, ...] = (Error_Types.RELATIVE_ADAPTIVE,)

#: Shape parameters an error type accepts beyond (curr, target, coeff), and their defaults.
#: An error type absent here takes none, so `error_params` is ignored for it — which keeps every
#: existing error type byte-for-byte unchanged. Used to validate spec.error_params at LOAD time
#: rather than discovering a typo as a TypeError thousands of evaluations into a run.
ERROR_SHAPE_PARAMS: Dict[Error_Types, Dict[str, Any]] = {
    # The saturation rate. 1.0 is the value this kernel was hardcoded at before it became a
    # parameter, so an existing spec that names no `error_params:` is unchanged.
    Error_Types.RELATIVE_SIGMOID: {"alpha": 1.0},
    Error_Types.RELATIVE_GAUSSIAN: {"sigma": 1.0},
    # `strategy`/`ema_beta`/`warmup` configure the running scale; they are validated at LOAD by
    # constructing the spec's AdaptiveNormalizer there (TargetSpec.__post_init__), so a typo like
    # `strategy: runing_mean` fails immediately rather than mid-run.
    # `seed` is a BASIS name here ("target" | "range" | "none"), resolved to a number by
    # TargetSpec at load — only the spec knows its target/range and whether samples are in
    # decades. Defaults: seed from the target magnitude and adapt from evaluation one, which is
    # why `warmup` defaults to 0 (seeding supersedes burning in on the static range).
    Error_Types.RELATIVE_ADAPTIVE: {
        "strategy": "running_mean", "ema_beta": 0.9, "warmup": 0,
        "window": None, "seed": "target", "seed_weight": 1,
    },
}


# Dictionary to map error types to functions
REWARD_COMPUTE_FUNCTIONS : Dict[Reward_Types, Callable]= {
    Reward_Types.RELATIVE_ABSOLUTE:  compute_relative_absolute_reward,
    Reward_Types.RELATIVE_LOG:       compute_relative_log_reward,
    Reward_Types.LOG:       compute_log_reward,
}

# -----------------------------------------------------------------------------------------------------------------------------------------------
# [Endpint] - Compute Error
def resolve_error_params(error_type: Error_Types | str, error_params: Dict[str, Any] | None) -> Dict[str, Any]:
    """Merge a spec's `error_params` over the error type's defaults; reject unknown keys.

    Returns {} for error types that take no shape parameters, so the call path for every
    pre-existing error type is unchanged.
    """
    if isinstance(error_type, str):
        error_type = Error_Types(error_type)
    defaults = ERROR_SHAPE_PARAMS.get(error_type)
    if not defaults:
        if error_params:
            logger.warning(f"error_params {sorted(error_params)} ignored: error type '{error_type.value}' takes none.")
        return {}
    if not error_params:
        return dict(defaults)
    unknown = set(error_params) - set(defaults)
    if unknown:
        logger.error(f"Unknown error_params {sorted(unknown)} for '{error_type.value}'. Valid: {sorted(defaults)}.")
        raise ValueError(f"Unknown error_params {sorted(unknown)} for '{error_type.value}'. Valid: {sorted(defaults)}.")
    return {**defaults, **error_params}


# [Endpint] - Compute Error
def compute_error(curr_val: np.float64, target_val: np.float64, error_type: Error_Types | str, normalizing_coeff: np.float64 | None = None, error_params: Dict[str, Any] | None = None, error_state: "AdaptiveNormalizer | None" = None) -> np.float64:
    """Computes the error between curr_val and target_val based on the specified error_type.

    `error_params` carries shape parameters for error types that take them (relative-gaussian's
    `sigma`; relative-adaptive's `strategy`/`ema_beta`/`warmup`). It defaults to None, so every
    existing caller is unaffected.

    `error_state` carries the MUTABLE running scale for a stateful error type (see
    `STATEFUL_ERROR_TYPES`) and is passed by the scorer from the owning spec. It is ignored — not
    an error — for every stateless type, so a caller can pass it unconditionally.
    """
    if isinstance(error_type, str):
        error_type = Error_Types(error_type)

    shape = resolve_error_params(error_type, error_params)
    if error_type in STATEFUL_ERROR_TYPES:
        shape = {**shape, "state": error_state}
    if "relative" in error_type.value:
        if normalizing_coeff is None or not np.isfinite(normalizing_coeff) or normalizing_coeff <= 0:
            logger.error(f"Normalizing coefficient must be provided, finite and > 0 for relative error types. Got: {normalizing_coeff}")
            raise ValueError(f"Normalizing coefficient must be provided, finite and > 0 for relative error types. Got: {normalizing_coeff}")
        return ERROR_COMPUTE_FUNCTIONS[error_type](curr_val, target_val, normalizing_coeff, **shape)
    return ERROR_COMPUTE_FUNCTIONS[error_type](curr_val, target_val, **shape)

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
                      #   (always over the TOTAL corner count — see AGG-2 below)
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

    **Monotonicity (AGG-2).** ``mean`` divides by the TOTAL corner count, never by the
    size of the failing subset. Dividing by ``len(subset)`` made the reducer *non-monotone*
    — fixing a marginal corner shrinks the denominator, so e.g. ``{-10, -2}`` (mean −6)
    got WORSE, −10, when the −2 corner was improved to +1 — and gradient-free search reads
    that as "the improvement hurt". With the fixed denominator every strategy here is
    monotone non-decreasing in each corner's score.
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
    if strategy == "mean":  # see AGG-2: the denominator is the whole corner set
        return np.float64(np.sum(list(subset.values())) / len(corner_scores))
    return np.float64(aggregator(list(subset.values())))


# [Endpint] - Aggregate per-SPEC scores into one scalar objective
# ---------------------------------------------------------------------------------------------
# There are TWO aggregation axes and they are independent:
#   * the SPEC axis (here)   — {per-spec score} -> one scalar, chosen by
#                              `optimizer_config.spec_aggregation`
#   * the CORNER axis (above) — {per-corner total} -> one scalar, chosen by `pvt.score_aggregation`
# A multi-corner run applies this one first (once per corner), then `aggregate_corner_scores`.
#
# SIGN CONVENTION — everything here is "higher is better", the convention the whole optimizer uses:
# `compute_fitness_for_spec` returns a signed score (negative = constraint violation, positive =
# reward for a satisfied spec), and the Nevergrad/Ax backends negate the final scalar before
# `tell()` because their engines minimize. So each aggregator below returns a NEGATED cost.

#: Shape parameters an aggregation strategy accepts, and their defaults. A strategy absent here
#: takes none. Mirrors ERROR_SHAPE_PARAMS so both axes validate the same way at load.
AGGREGATION_SHAPE_PARAMS: Dict[str, Dict[str, Any]] = {
    "chebyshev": {"rho": 1.0e-3},
}

#: Canonical spec-axis strategies. `feasibility_reward` is the DEFAULT and reproduces the
#: historical hardcoded behaviour exactly, so an existing project that names none is unchanged.
SPEC_SCORE_AGGREGATORS: Tuple[str, ...] = ("feasibility_reward", "weighted_sum", "chebyshev")


def resolve_aggregation_params(strategy: str, params: Dict[str, Any] | None) -> Dict[str, Any]:
    """Merge `params` over a strategy's defaults; reject unknown keys. `{}` for strategies with none."""
    defaults = AGGREGATION_SHAPE_PARAMS.get(strategy)
    if not defaults:
        if params:
            logger.warning(f"aggregation_params {sorted(params)} ignored: strategy '{strategy}' takes none.")
        return {}
    if not params:
        return dict(defaults)
    unknown = set(params) - set(defaults)
    if unknown:
        raise ValueError(
            f"Unknown aggregation_params {sorted(unknown)} for '{strategy}'. Valid: {sorted(defaults)}."
        )
    return {**defaults, **params}


def aggregate_spec_scores(
    spec_scores: Dict[str, np.float64],
    strategy: str = "feasibility_reward",
    params: Dict[str, Any] | None = None,
) -> np.float64:
    """Collapse per-spec signed scores ``{spec_name: score}`` into one scalar objective.

    Each input is a spec's own fitness: ``< 0`` means it VIOLATES its constraint (the magnitude is
    its weighted, normalized penalty ``w_i·P_i``), ``> 0`` means it is satisfied and earning a
    reward ``w_i·R_i``. The two are mutually exclusive per spec — the reward kernels are gated on
    the constraint being met — so splitting on the sign recovers ``P_i`` and ``R_i`` exactly.

    Strategies (with ``P = {w_i·P_i : score_i < 0}``, ``R = Σ w_i·R_i`` over satisfied specs):

    * ``feasibility_reward`` — ``F = R`` if ``P`` is empty else ``F = -Σ P``. Lexicographic:
      while ANY spec is violated the score is the penalty sum alone and no amount of reward from
      satisfied specs can offset it; the reward landscape is only exposed once the design is
      feasible. This is the historical hardcoded behaviour and stays the default.
    * ``weighted_sum`` — ``F = -Σ P``, always, with no reward term. The plain scalarization: a
      one-unit improvement anywhere is worth the same. **Flat at 0 across the entire feasible
      region** (no reward gradient), which is the honest reading of "weighted sum of penalties" and
      is why it is a baseline rather than a recommendation.
    * ``chebyshev`` — ``F = -(max_i P_i + ρ·Σ P_i)``. Min-max: only the WORST-violated spec drives
      the score, with the ρ-weighted L1 term breaking ties so progress on the other specs is still
      visible (the standard *augmented* Chebyshev). Unlike a weighted sum it can reach non-convex
      parts of the Pareto front. Also flat at 0 once feasible.

    Every strategy is monotone non-decreasing in each spec's score, which gradient-free search
    relies on: improving one spec can never make the aggregate worse.

    An EMPTY input returns 0.0 rather than raising — a project whose specs are all `enable: false`
    is degenerate but not a crash, and `max()` over an empty penalty set would raise.
    """
    if strategy not in SPEC_SCORE_AGGREGATORS:
        raise ValueError(
            f"Unknown spec_aggregation '{strategy}'. Valid: {sorted(SPEC_SCORE_AGGREGATORS)}."
        )
    shape = resolve_aggregation_params(strategy, params)
    if not spec_scores:
        return np.float64(0.0)

    penalties = [-np.float64(s) for s in spec_scores.values() if s < 0]
    rewards = np.float64(sum(np.float64(s) for s in spec_scores.values() if s > 0))

    if strategy == "feasibility_reward":
        # `> -EPSILON` (not `>= 0`) mirrors the historical test: a penalty sum within one epsilon
        # of zero counts as feasible, so float dust in a satisfied spec cannot hide the rewards.
        total_penalty = -np.float64(sum(penalties))
        return rewards if total_penalty > -1 * EPSILON else total_penalty
    if strategy == "weighted_sum":
        return np.float64(-1 * sum(penalties))
    # chebyshev
    if not penalties:
        return np.float64(0.0)
    rho = np.float64(shape["rho"])
    return np.float64(-1 * (max(penalties) + rho * sum(penalties)))


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
