"""What a schematic agent reads after netlist2xschem draws a sheet, as JSON-ready dictionaries.

netlist2xschem drafts sheets; the schematic agent places the components, draws the symbols and
the hierarchy, and decides what to keep. On a drawn sheet nobody can tell a net joined by a wire
from one joined only by its name labels, so these functions return the measurements the agent
acts on. They are built from documents already drawn and change no sheet.

- :func:`sheet_report`, one sheet: the router that drew it, the nets still carried by name and
  the number of drawn pieces their pins fall into, the port pins parked at the frame, the lanes
  reserved per channel, the nets the channel router did not route (issue #243), and the rails,
  spines, taps and refused wires of each supply net.
- :func:`check_report`, the flatten-versus-netlist check of a ``--collapse`` hierarchy.
- :func:`collapse_report`, a ``--collapse`` hierarchy (issue #264): every sheet's report, each
  group's slices and ports, and the check.

``netlist2xschem --report FILE.json`` (``-`` for standard output) writes the same data.
"""

from __future__ import annotations

from typing import Any

from .collapse import CollapseCheck, CollapsedResult
from .emit import SchDocument

__all__ = ["sheet_report", "check_report", "collapse_report"]


def sheet_report(doc: SchDocument) -> dict[str, Any]:
    """One sheet's measurements (see the module docstring); every key is always present.

    ``lanes`` keys read ``"v:<i>"`` for the vertical channel ``i`` (0 is left of the first block
    column) and ``"h:<j>"`` for the horizontal channel ``j`` (0 is above the first block row).
    """
    return {
        "router": doc.router,
        "devices": doc.device_count,
        "wires": doc.wire_count,
        "labels": doc.label_count,
        "ports": doc.port_count,
        "nets_by_name": list(doc.nets_by_name),
        "nets_by_name_count": len(doc.nets_by_name),
        "pieces": dict(sorted(doc.pieces.items())),
        "parked_ports": list(doc.parked_ports),
        "lanes": {f"{axis}:{i}": n for (axis, i), n in sorted(doc.lanes.items())},
        "unrouted": list(doc.unrouted),
        "supply": {net: dict(counts) for net, counts in sorted(doc.supply.items())},
        "warnings": list(doc.warnings),
    }


def check_report(check: CollapseCheck) -> dict[str, Any]:
    """The flattened sheets against the netlist: the counts, and every difference by kind."""
    return {
        "identical": check.identical,
        "terminals": check.terminals,
        "nets": check.nets,
        "split": list(check.split),
        "merged": [list(nets) for nets in check.merged],
        "missing": [list(t) for t in check.missing],
        "extra": [list(t) for t in check.extra],
        "port_mismatch": list(check.port_mismatch),
        "duplicate": list(check.duplicate),
    }


def collapse_report(result: CollapsedResult, check: CollapseCheck) -> dict[str, Any]:
    """A ``--collapse`` hierarchy: top-sheet instances before and after, each group, each sheet."""
    return {
        "top_sheet": {
            "instances_before": result.device_count,
            "instances_after": result.parent_instances,
        },
        "groups": {
            g: {
                "instance": result.group_instances[g],
                "slices": list(refs),
                "ports": list(result.block_pins[g]),
            }
            for g, refs in sorted(result.groups.items())
        },
        "sheets": {name: sheet_report(doc) for name, doc in result.sheets.items()},
        "check": check_report(check),
        "warnings": list(result.warnings),
    }
