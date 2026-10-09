"""ngspice value-token semantics — re-exported from ``core``.

The table itself moved to :mod:`spicexplorer_core.spice_eng` on 2026-09-10: while it was private to
this package, ``spicexplorer-netlist2tf`` read netlist values through the DSL parser instead and
answered ``1M`` as *mega* where this package answers *milli* — a 10⁹ disagreement on one token
between two tools in one workspace (Codex review, items TF-01 and CG-01). Peer tools may not import
each other, so the shared table lives in ``core`` and both read from it.

This module stays as the import path this package's own call sites already use
(``_signatures.norm_value``, ``emit``) and as the name its docstrings reference.
"""

from __future__ import annotations

from spicexplorer_core.spice_eng import format_number, spice_number

__all__ = ["spice_number", "format_number"]
