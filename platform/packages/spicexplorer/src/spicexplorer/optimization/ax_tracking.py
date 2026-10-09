"""Ax tracking metrics from a trial's ``fit_summary``, with no dependency on the optional ``ax`` extra.

The Ax backend (:mod:`spicexplorer.optimization.stochastic.bayesian_ax`) reports every target
spec to its ``Client`` as a *tracking* metric beside the ``score`` objective (diagnostics, not
the objective). Folding a trial's ``fit_summary`` into that ``raw_data`` dict is plain Python, so
it lives here: importing this module never imports ``ax`` or ``torch``, and its tests run in the
fast suite without ``uv sync --extra ax``.
"""

import logging
from collections.abc import Iterable, Mapping
from typing import Any

import numpy as np

logger = logging.getLogger("spicexplorer.optimization.ax_tracking")


def extract_tracking_metrics(
    fit_summary: Mapping[str, Any],
    target_names: Iterable[str],
    save_in_dict: dict[str, Any],
) -> dict[str, Any]:
    """Fold a trial's per-spec values into the Ax ``raw_data`` dict as tracking metrics.

    ``fit_summary`` has bare spec keys in single mode, but ``"<corner>::<spec>"`` keys in
    multi-corner mode (Phase 2), so match on the BARE spec name (``key.split("::")[-1]``) and
    average a spec's value across corners for a single diagnostic scalar (B4: the old bare-name
    match reported zero metrics in multi mode). Non-dict entries (e.g. per-corner totals) are
    skipped, and missing or non-finite values are omitted (the Ax client rejects NaN tracking
    metrics); a spec with no finite value at any corner is left out. Mutates and returns
    ``save_in_dict``."""
    logger.debug("Extracting the tracking metrics from the metadata.")
    targets = set(target_names)
    by_spec: dict[str, list[float]] = {}
    for metric_key, content in fit_summary.items():
        if not isinstance(content, dict):  # tolerate non-dict metadata (per-corner totals)
            continue
        bare = str(metric_key).split("::")[-1]
        if bare not in targets:
            continue
        val = content.get("curr_val")
        if val is None or not np.isfinite(val):  # Ax rejects NaN tracking metrics
            logger.debug(f"skipping {metric_key} (missing/non-finite)")
            continue
        by_spec.setdefault(bare, []).append(float(val))
    for bare, vals in by_spec.items():
        save_in_dict[bare] = float(np.mean(vals))  # mean across corners (diagnostic only)
        logger.debug(f"\tadded tracking metric {bare} = {save_in_dict[bare]}")
    logger.debug("Completed extracting the tracking metrics.")
    return save_in_dict
