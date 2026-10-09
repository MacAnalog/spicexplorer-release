"""Structured verdicts. Every runner returns one of these; nothing is a bare bool.

They serialize with :meth:`to_dict` (JSON-safe) so an optimizer trial, an agent
or a CLI can log the same object. ``log`` holds the tool's raw stdout+stderr
(tail-truncated by the runner) — enough to debug, small enough to store.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
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
    #: the rule deck that produced this verdict: the PDK's run_drc.py or a .lydrc file. The two
    #: IHP .lydrc decks check different rule sets, so a pass names the deck it passed.
    deck: str | None = None
    #: the density setting the deck ran with (run_drc's argument): True drops the chip-level
    #: density rules, so a clean verdict is conditional on density
    no_density: bool | None = None

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
    # RC / R only. kpex builds the resistor mesh as an ISLAND — its nodes touch no device pin —
    # so `n_r > 0` is not evidence that resistance is in the circuit. `mesh_connected` is the
    # verdict of the post-extraction connectivity check; `mesh` carries its counts.
    raw_netlist_path: str | None = None  # kpex's own output, before the mesh was stitched
    mesh_connected: bool | None = None  # None = not applicable (CC) / not checked
    mesh: dict[str, Any] = field(default_factory=dict)
    #: every node name treated as ground when per_net_c_ff / coupling_ff were summed, lower-cased:
    #: pex.GROUND_NETS plus the run's `ground_nets` (e.g. `sub` when the substrate is a pin)
    ground_nets: list[str] = field(default_factory=list)
    #: C cards with both terminals on one net (kpex writes e.g. `Cext_51 sub sub 23.0904f`); they
    #: store no charge, so they are left out of n_c and of every sum
    n_self: int = 0
    #: the sidewall halo [um] passed to kpex (`--halo`); None = the tech file's own halo. Couplings
    #: beyond it are dropped, so two extractions compare only at one halo
    halo_um: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def tail(text: str, n: int = 4000) -> str:
    return text if len(text) <= n else text[-n:]


def snapshot(paths: Iterable[Path]) -> dict[Path, float]:
    """`{path: mtime}` for the files a runner might overwrite, taken BEFORE it starts."""
    out: dict[Path, float] = {}
    for p in paths:
        try:
            out[Path(p)] = Path(p).stat().st_mtime
        except OSError:
            pass
    return out


def written_since(paths: Iterable[Path], before: dict[Path, float]) -> list[Path]:
    """The subset of ``paths`` this run actually produced: new, or with a changed mtime.

    A verdict must never be read out of a file the current run did not write. `run_dir` is only
    ``mkdir(exist_ok=True)``-ed and `run_flow` does not clear it, so the ordinary fix-and-retry
    loop leaves an earlier *successful* log sitting next to a crashed runner — and parsing it
    reported a PASS with a traceback in `reason`. Comparing against a pre-run snapshot rather than
    a wall-clock `t0` keeps this exact whatever the filesystem's timestamp granularity is; a runner
    that rewrites a file byte-identically inside one coarse tick is rejected, which is the safe
    direction.
    """
    out: list[Path] = []
    for p in paths:
        p = Path(p)
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if p not in before or before[p] != mtime:
            out.append(p)
    return out


def proc_output(value: object) -> str:
    """`TimeoutExpired.stdout`/`.stderr` as text.

    They are ``bytes`` (or ``None``) even when the call passed ``text=True`` — `run()` re-raises
    the exception without decoding the partial output it collected.
    """
    if value is None:
        return ""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value).decode(errors="replace")
    return str(value)
