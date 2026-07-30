"""Errors for the gm/ID sizing tool.

The contract is *fail-loud*: a lookup that lands off the characterized grid, or that produces a
NaN, raises with the grid bounds in the message — it is **never** silently clamped to an edge
value (that ships a confidently-wrong size). This mirrors the gmid-skills pitfall list.
"""

from __future__ import annotations


class GmidError(Exception):
    """Base class for every error raised by ``spicexplorer_gmid``."""


class OutOfGridError(GmidError):
    """A bias point or target fell outside the characterized LUT grid (or interpolated to NaN).

    The message always states the offending axis/target and the characterized range so the caller
    can re-grid the LUT or move the operating point, rather than trust a clamped edge value.
    """
