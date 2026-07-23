"""End-to-end schematic round-trip: every catalog schematic re-netlists to the *same circuit*.

For every committed full-circuit schematic under ``raw/`` this renders it back to a SPICE netlist with
xschem (``xschem -n``), then asserts the result is the same circuit as the source it was drawn from —
via :func:`circuitgraph.compare_netlists` (labeled bipartite-graph **isomorphism**). This is a
*structural* gate, not a name/text compare: it ignores instance/net names, model strings and sizing, and
matches on device type + MOS polarity + pin-level wiring with the supply rails anchored
(``compare_netlists`` defaults). So it catches any place where place→wire→map (or the block-annotation
overlay, or an alternative placement strategy) silently dropped, added or mis-wired a device — which the
byte-drift guard cannot see.

Covered, per circuit (all connectivity-equivalent to the source, only coordinates/overlay differ):
  * ``<id>.sch``                              — the plain DUT topology;
  * ``<id>_annotated.sch``                    — the detected blocks drawn as boxes over a block-aware
                                                placement (an overlay → must round-trip identically);
  * ``_block_placement_strategies/<id>/*.sch`` — the alternative placement strategies.
The hierarchical "block diagram" view (``hier/``) is **excluded**: its parent re-netlists to subckt
instances that must be flattened before comparison — that round-trip is covered for a sample in
``spicexplorer-netlist2xschem``'s ``test_hierarchy_round_trips_via_xschem``.

The schematics are drawn from the ``ihp-sg13g2`` lowered netlist (export ``_SCH_PDK``), so that lowered
netlist is the comparison source. xschem-gated (PDK-free otherwise): needs ``xschem`` (3.4.8+) on PATH
with the IHP xschem symbols resolvable — a host EDA setup or the platform base image — plus
``spicexplorer-netlist2xschem`` (for the symbol search path) and ``spicexplorer-circuitgraph``. Skips
cleanly when any is absent.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from spicexplorer_analog_db import export, model

# The PDK whose lowered netlist the schematics are drawn from (and thus the comparison source).
_SCH_PDK = export._SCH_PDK

_XSCHEM = shutil.which("xschem")
try:
    import spicexplorer_circuitgraph as cg
    from spicexplorer_netlist2xschem.render import write_xschemrc
    from spicexplorer_netlist2xschem.sym_library import default_search_paths

    _DEPS = True
except ImportError:  # netlist2xschem / circuitgraph not installed — the .sch were never generated either
    _DEPS = False

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(
        _XSCHEM is None or not _DEPS,
        reason="needs xschem on PATH + spicexplorer-netlist2xschem + circuitgraph (the EDA env)",
    ),
]


def _catalog_schematics() -> list[tuple[str, Path]]:
    """Every committed full-circuit schematic under ``raw/`` as ``(circuit_id, sch_path)``.

    The circuit id is always the schematic's parent directory name — true for the canonical
    ``raw/<class>/<id>/<id>.sch`` (+ ``_annotated``) *and* the ``raw/_block_placement_strategies/<id>/``
    variants. Excludes the hierarchical view (anything under a ``hier/`` directory) and keeps only
    schematics whose parent maps to a known circuit. Resolved at collection time (empty if the DB isn't
    checked out), so the suite simply collects nothing rather than erroring.
    """
    try:
        root = export.raw_root()
        known = {c.id for c in model.load_all_circuits()}
    except Exception:
        return []
    out: list[tuple[str, Path]] = []
    for sch in sorted(root.rglob("*.sch")):
        if "hier" in sch.relative_to(root).parts:
            continue
        cid = sch.parent.name
        if cid in known:
            out.append((cid, sch))
    return out


_SCHEMATICS = _catalog_schematics()
_IDS = [f"{cid}:{sch.name}" for cid, sch in _SCHEMATICS]


def _xschem_netlist(sch: Path, work: Path) -> str | None:
    """Re-netlist ``sch`` with headless ``xschem -n`` into ``work``; return the SPICE text (or None).

    The symbol search path is the vendored generic + IHP symbol dirs (which carry the clean ``*_np``
    twins the generated schematics use); seeded via our own rcfile so resolution is HOME-independent.
    """
    lib_path = os.pathsep.join(str(p) for p in default_search_paths())
    rc = write_xschemrc(work, lib_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = lib_path
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-x", "-q", "-n", "-s", "-o", str(work), str(sch.resolve())],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(work),
    )
    out = work / f"{sch.stem}.spice"
    return out.read_text() if out.is_file() else None


@pytest.mark.parametrize("cid,sch", _SCHEMATICS, ids=_IDS)
def test_catalog_schematic_round_trips_isomorphic(cid: str, sch: Path, tmp_path: Path) -> None:
    """The committed ``.sch`` → ``xschem -n`` → netlist is isomorphic to its ``_SCH_PDK`` source."""
    circuit = model.load_circuit(cid)
    lowered = circuit.dir / "pdk" / _SCH_PDK / "netlist.spice"
    if not lowered.is_file():
        pytest.skip(f"{cid}: no {_SCH_PDK} lowered netlist (schematics are drawn from {_SCH_PDK})")

    reparsed = _xschem_netlist(sch, tmp_path)
    assert reparsed, f"{cid}: xschem produced no netlist from {sch.name}"

    comparison = cg.compare_netlists(lowered.read_text(), reparsed)
    assert comparison, (
        f"{sch.name} ({cid}): the re-netlisted schematic is NOT the same circuit as the "
        f"{_SCH_PDK} source — {comparison.reason}"
    )
