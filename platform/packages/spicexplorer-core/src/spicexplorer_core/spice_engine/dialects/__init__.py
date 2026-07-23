"""Netlist dialect support: detection + Spectre/HSPICE → canonical-SPICE readers.

Public surface (re-exported from ``spicexplorer_core.spice_engine``):

* :class:`NetlistDialect` / :func:`detect_dialect` — the dialect vocabulary and sniffer.
* :func:`get_reader` — the reader registry (``SPECTRE``/``HSPICE`` → a
  :class:`BaseDialectReader` producing a :class:`ParsedDeck`).
* :class:`DialectSpec` — per-dialect syntax facts, shared with the circuitgraph emitters.
"""

from __future__ import annotations

from .base import (
    BaseDialectReader,
    DialectSpec,
    DialectSyntaxError,
    Directive,
    NetlistDialect,
    ParsedDeck,
    detect_dialect,
)
from .hspice import HSPICE_SPEC, HspiceReader
from .spectre import SPECTRE_SPEC, SpectreReader

__all__ = [
    "BaseDialectReader",
    "DialectSpec",
    "DialectSyntaxError",
    "Directive",
    "NetlistDialect",
    "ParsedDeck",
    "detect_dialect",
    "get_reader",
    "SpectreReader",
    "HspiceReader",
    "SPECTRE_SPEC",
    "HSPICE_SPEC",
]

_READERS: dict[NetlistDialect, BaseDialectReader] = {
    NetlistDialect.SPECTRE: SpectreReader(),
    NetlistDialect.HSPICE: HspiceReader(),
}


def get_reader(dialect: NetlistDialect | str) -> BaseDialectReader:
    """The reader for a foreign dialect (``SPICE`` needs none — spicelib parses it natively)."""
    resolved = NetlistDialect.coerce(dialect)
    reader = _READERS.get(resolved)
    if reader is None:
        raise ValueError(f"no dialect reader for {resolved.value!r} (native spicelib dialect)")
    return reader
