"""Live 5-corner PVT sizing of the 5T OTA (Phase-2 multi-corner flow proof).

Runs the {tb_ac x 5 corners} cross-product per trial, scores each corner, and
collapses the per-corner scores into one objective with constraint-first
aggregation (AGG-1). Prints the per-corner spread at the best design and shows,
on a fixed design, how constraint-first aggregation averts corner masking that a
naive mean would allow. See multicorner_results.md for a captured run.

Requires live ngspice + the ihp-sg13g2 PDK. Run from anywhere:
    uv run python examples/OTA/5t-ota/ihp-sg13g2/sizing/run_multicorner_5t.py
"""
from pathlib import Path
import numpy as np

from spicexplorer.optimization.orchestrator import (
    Circuit_Optimizer_Orchestrator_with_SPICE, Optimizer_Type_Enum,
)
from spicexplorer.core.utils import aggregate_corner_scores
from spicexplorer_core.logging.logger_setup import (
    setup_loggers_with_spicelib_suppression as setup_loggers,
)

HERE = Path(__file__).resolve().parent
YAML = HERE / "project_setup_multicorner.yaml"
setup_loggers()


def _build(reward: bool = False, dcgain_target: float | None = None):
    orch = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=YAML, optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE,
        auto_load=False, verbose=False,
    )
    p = orch.project_setup
    if reward or dcgain_target is not None:
        for t in p.optimizer_config.target_specs.targets:
            if reward:
                t.reward_type = "relative-absolute"
            if dcgain_target is not None and t.name == "dcgain":
                t.target = dcgain_target
    orch.initialize()
    opt = orch.get_optimizer()
    opt.parameterize()
    return p, opt


def _metric(fs, c, s):
    return float(fs.get(f"{c}::{s}", {}).get("curr_val", float("nan")))


# ── (1) the sweep ───────────────────────────────────────────────────────────
p, opt = _build()
opt.optimize(render_optimization_trace=False, keep_history=False)
log = opt.optimization_log
scores = [float(e.point.score) for e in log]
best_i = int(np.argmax(scores))
best = log[best_i]
meta = best.point.metadata or {}
corner_scores = {k: float(v) for k, v in meta.get("corner_scores", {}).items()}
fs = best.fit_summary or {}
corners = list(corner_scores)
best_params = {k: float(v) for k, v in best.point.params.items()}

print("=" * 72)
print(f"5T-OTA MULTI-CORNER PVT SWEEP  ({len(corners)} corners x tb_ac, "
      f"NGOpt budget={p.optimizer_config.budget})")
print("=" * 72)
print(f"best trial #{best_i}  aggregated score = {scores[best_i]:+.4f}")
print("corner".ljust(15) + "dcgain".rjust(10) + "ugf".rjust(14) + "pm".rjust(6)
      + "score".rjust(10) + "  verdict")
for c in corners:
    sc = corner_scores[c]
    print(c.ljust(15) + f"{_metric(fs,c,'dcgain'):10.3f}" + f"{_metric(fs,c,'ugf'):14.4g}"
          + f"{_metric(fs,c,'pm'):6.0f}" + f"{sc:10.3f}"
          + ("  PASS" if sc >= 0 else "  FAIL"))
ugfs = [_metric(fs, c, "ugf") for c in corners]
print(f"UGF spread across corners: {min(ugfs):.4g} .. {max(ugfs):.4g} "
      f"({max(ugfs)/min(ugfs):.2f}x) — corner application is not a no-op")

# ── (2) masking-averted demo on that fixed design ───────────────────────────
DEMANDING = 27.5
_, opt2 = _build(reward=True, dcgain_target=DEMANDING)
score2, fs2 = opt2.evaluate(best_params, append_to_log=True)
cs2 = {k: float(v) for k, v in (opt2.optimization_log[-1].point.metadata or {})["corner_scores"].items()}
naive = float(np.mean(list(cs2.values())))
cf = float(aggregate_corner_scores({k: np.float64(v) for k, v in cs2.items()}, "mean"))
fails = [c for c in cs2 if cs2[c] < 0]

print("\n" + "=" * 72)
print(f"AGG-1 MASKING-AVERTED DEMO  (same design, dcgain target = {DEMANDING} dB)")
print("=" * 72)
for c in cs2:
    print(c.ljust(15) + f"dcgain={_metric(fs2,c,'dcgain'):7.3f}"
          + f"   corner_score={cs2[c]:+9.3f}" + ("  PASS" if cs2[c] >= 0 else "  FAIL"))
print(f"failing corners           : {fails or 'none'}")
print(f"naive mean(all corners)   = {naive:+.4f}   (masks the failing corner)")
print(f"constraint-first (AGG-1)  = {cf:+.4f}   (== optimizer score: {abs(cf-score2)<1e-6})")
print("=" * 72)
