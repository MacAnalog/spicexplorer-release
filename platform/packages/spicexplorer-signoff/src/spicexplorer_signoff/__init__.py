"""spicexplorer-signoff — physical signoff as a library.

Engine-agnostic **DRC / LVS / PEX** runners that return structured verdicts
(GDS in → verdict out), plus the two netlist-side helpers a post-layout flow
needs: splicing an extracted subckt into an existing bench deck
(:mod:`postlayout`) and injecting parasitics / mismatch into a subckt to
measure layout sensitivity (:mod:`sensitivity`).

Public surface (stable):

- :func:`probe` — which tools/decks are available on this machine.
- :func:`run_drc` / :func:`run_lvs` / :func:`run_pex` — the runners.
- :func:`run_flow` — build → drc → lvs → pex for a caller-supplied builder.
- :mod:`postlayout` — ``prep_pex_subckt``, ``splice_subckt``, ``deltas``,
  ``select_pex_netlist`` (WHICH extracted netlist a scorecard measured, as a
  ``MeasuredNetlist`` provenance record), ``score_c_budgets`` / ``c_budget_table``
  (per-net extracted C against the layout brief's balanced / one-sided / differential budgets).
- :mod:`sensitivity` — ``inject_caps``, ``inject_resistor``, ``scale_param``, ``sweep``;
  on an EXTRACTED block ``find_mos_cards`` (a device class by connectivity, since the
  extraction has no design-device names), ``inject_threshold_offset``, ``filter_caps``
  and ``insert_series_return``.
- :func:`check_current_density` — the electromigration budget no rule deck checks;
  :func:`budgets_from_brief` builds its rows from the layout brief's ``currents`` block.
- :func:`check_mesh_connectivity` / :func:`stitch_rc_netlist` — RC/R extraction only:
  kpex leaves the resistor mesh unattached to the devices; these join it and prove it.
"""

from .current_density import (
    Budget,
    CurrentDensityResult,
    CurrentDensityViolation,
    budgets_from_brief,
    check_current_density,
)
from .drc import run_drc
from .flow import FlowResult, run_flow
from .lvs import run_lvs
from .pdk import PdkPaths, ToolProbe, probe
from .pex import check_mesh_connectivity, run_pex, stitch_rc_netlist
from .postlayout import MeasuredNetlist, select_pex_netlist
from .results import DrcResult, DrcViolation, LvsResult, PexResult

__all__ = [
    "Budget",
    "CurrentDensityResult",
    "CurrentDensityViolation",
    "DrcResult",
    "MeasuredNetlist",
    "DrcViolation",
    "FlowResult",
    "LvsResult",
    "PdkPaths",
    "PexResult",
    "ToolProbe",
    "budgets_from_brief",
    "check_current_density",
    "check_mesh_connectivity",
    "probe",
    "run_drc",
    "run_flow",
    "run_lvs",
    "run_pex",
    "select_pex_netlist",
    "stitch_rc_netlist",
]
