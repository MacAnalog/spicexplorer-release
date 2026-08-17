"""build → DRC → LVS → PEX in one call, for a caller-supplied builder.

The builder is any ``Callable[[params], Path]`` that writes a GDS and returns its path
(e.g. ``spicexplorer_layout.gen.GdsBuilder`` bound to a generator module) — this package
never imports the generator side, so the same function serves an agent iteration and an
optimizer trial. Stops at the first failing gate unless ``continue_on_fail``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from .drc import run_drc
from .lvs import run_lvs
from .pex import run_pex
from .results import DrcResult, LvsResult, PexResult


@dataclass
class FlowResult:
    gds: str | None
    drc: DrcResult | None
    lvs: LvsResult | None
    pex: PexResult | None
    stage_failed: str | None = None  # "build" | "drc" | "lvs" | "pex" | None
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.stage_failed is None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["ok"] = self.ok
        return d


def run_flow(
    build: Callable[[Any], str | Path],
    params: Any,
    *,
    netlist: str | Path,
    cell: str,
    run_dir: str | Path,
    pdk: str = "ihp-sg13g2",
    pex_mode: str = "CC",
    do_pex: bool = True,
    continue_on_fail: bool = False,
) -> FlowResult:
    run_dir = Path(run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    try:
        gds = Path(build(params)).resolve()
    except Exception as e:  # builder bugs are a verdict, not a crash of the loop
        return FlowResult(None, None, None, None, "build", f"{type(e).__name__}: {e}")
    drc = run_drc(gds, cell, run_dir / "drc", pdk=pdk)
    if not drc.passed and not continue_on_fail:
        return FlowResult(str(gds), drc, None, None, "drc", drc.reason)
    lvs = run_lvs(gds, netlist, cell, run_dir / "lvs", pdk=pdk)
    if not lvs.passed and not continue_on_fail:
        return FlowResult(str(gds), drc, lvs, None, "lvs", lvs.reason)
    pex = None
    if do_pex:
        pex = run_pex(gds, cell, netlist, run_dir / "pex", mode=pex_mode, pdk=pdk)
        if not pex.ok:
            return FlowResult(str(gds), drc, lvs, pex, "pex", pex.reason)
    failed = None
    if not drc.passed:
        failed = "drc"
    elif not lvs.passed:
        failed = "lvs"
    return FlowResult(str(gds), drc, lvs, pex, failed)
