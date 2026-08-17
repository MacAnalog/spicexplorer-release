"""Structured verdicts. Every runner returns one of these; nothing is a bare bool.

They serialize with :meth:`to_dict` (JSON-safe) so an optimizer trial, an agent
or a CLI can log the same object. ``log`` holds the tool's raw stdout+stderr
(tail-truncated by the runner) — enough to debug, small enough to store.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DrcViolation:
    rule: str
    count: int
    locations: list[tuple[float, float]] = field(default_factory=list)  # µm, ≤ N per rule


@dataclass
class DrcResult:
    passed: bool
    available: bool  # False = tool/deck missing → passed is meaningless
    n_violations: int = 0
    violations: list[DrcViolation] = field(default_factory=list)
    report_path: str | None = None  # KLayout .lyrdb (XML) or tool report
    log: str = ""
    reason: str = ""  # why unavailable / why failed to run

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LvsResult:
    passed: bool
    available: bool
    matched: bool | None = None  # tool's own verdict; None if it did not run
    unmatched: dict[str, int] = field(default_factory=dict)  # e.g. {"nets": 2, "devices": 0}
    report_path: str | None = None
    netlist_path: str | None = None  # the reference netlist compared against
    netlist_sha: str | None = None
    log: str = ""
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PexResult:
    ok: bool
    available: bool
    mode: str = "CC"  # CC | RC | R
    netlist_path: str | None = None  # extracted subckt (devices + parasitics)
    n_c: int = 0
    n_r: int = 0
    per_net_c_ff: dict[str, float] = field(default_factory=dict)  # Σ C to anything, per net
    coupling_ff: dict[str, float] = field(default_factory=dict)  # "a|b" -> C between nets
    log: str = ""
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def tail(text: str, n: int = 4000) -> str:
    return text if len(text) <= n else text[-n:]
