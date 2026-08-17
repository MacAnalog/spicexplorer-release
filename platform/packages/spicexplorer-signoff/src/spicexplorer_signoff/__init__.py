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
- :mod:`postlayout` — ``prep_pex_subckt``, ``splice_subckt``, ``deltas``.
- :mod:`sensitivity` — ``inject_caps``, ``inject_resistor``, ``scale_param``, ``sweep``.
"""

from .drc import run_drc
from .flow import FlowResult, run_flow
from .lvs import run_lvs
from .pdk import PdkPaths, ToolProbe, probe
from .pex import run_pex
from .results import DrcResult, DrcViolation, LvsResult, PexResult

__all__ = [
    "DrcResult",
    "DrcViolation",
    "FlowResult",
    "LvsResult",
    "PdkPaths",
    "PexResult",
    "ToolProbe",
    "probe",
    "run_drc",
    "run_flow",
    "run_lvs",
    "run_pex",
]
