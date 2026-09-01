"""PEX via **kpex** (klayout-pex, 2.5D engine) → :class:`PexResult` with per-net C sums.

kpex runs the KLayout LVS deck internally for connectivity, then extracts coupling /
ground C (``CC``), + wire R (``RC``), or R only. It writes
``<out_dir>/<gds-stem>__<cell>/<cell>_k25d_pex_netlist.spice``. Gotchas pinned by the
prototype: kpex needs a KLayout executable with Ruby ≥ 2.6 (``KPEX_KLAYOUT_EXE``), an
**absolute** ``--out_dir``, and in an optimizer loop use ``CC`` — ``RC``'s R-mesh can
leave gate-net pin nodes dangling and make the ngspice matrix singular.

**kpex does not support IHP MIM caps (``cap_cmim``)**: its tech (``klayout_pex_protobuf/
ihp-sg13g2_tech.pb.json``) defines the MIM top layer ``cmim_top`` (GDS 36) with
``original_layer_name: "<TODO>"`` and the 2.5D sidewall/fringe extractor dies with
``KeyError: '<TODO>' in EdgeNeighborhoodVisitor.on_edge`` on any cell containing one.
Workaround (validated on the LPF H12 cell): extract a copy of the GDS with layers 36/0 (MIM)
and 129/0 (Vmim) cleared and TopMetal1 (126/0) minus the MIM regions (top plates removed,
stubs kept), against a schematic with the ``C`` cards removed; then add the schematic MIM
cards back into the extracted subckt for the benches — bottom-plate (Metal5) parasitics are
extracted, top-plate-to-neighbour C is lost. See :func:`strip_mim_for_pex`.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Sequence

from .pdk import kpex_exe, kpex_klayout_exe, pdk_root
from .results import PexResult, tail

_ELEM = re.compile(r"^([CR])\S*\s+(\S+)\s+(\S+)\s+(\S+)", re.I)
_SI = {
    "a": 1e-18,
    "f": 1e-15,
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "meg": 1e6,
    "g": 1e9,
    "t": 1e12,
}


def _num(tok: str) -> float | None:
    """SPICE number with optional SI suffix (kpex writes ``62.1879a`` = 62.19 aF)."""
    m = re.match(r"^([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(meg|[afpnumkgt])?", tok, re.I)
    if not m:
        return None
    return float(m.group(1)) * _SI.get((m.group(2) or "").lower(), 1.0)


def _net(tok: str) -> str:
    return tok.replace("\\", "")  # kpex escapes internal nets as \$17


def summarize_parasitics(
    netlist: str | Path,
) -> tuple[int, int, dict[str, float], dict[str, float]]:
    """(n_C, n_R, per-net ΣC [fF], coupling C between net pairs [fF]) from a PEX netlist."""
    n_c = n_r = 0
    per: dict[str, float] = {}
    coup: dict[str, float] = {}
    for line in Path(netlist).read_text(errors="replace").splitlines():
        m = _ELEM.match(line.strip())
        if not m:
            continue
        kind, a, b, val = m.group(1).upper(), _net(m.group(2)), _net(m.group(3)), _num(m.group(4))
        if kind == "R":
            n_r += 1
            continue
        if val is None:
            continue
        n_c += 1
        ff = val * 1e15
        for n in (a, b):
            if n not in ("0", "gnd", "GND", "vss", "VSS"):
                per[n] = per.get(n, 0.0) + ff
        if a not in ("0",) and b not in ("0",):
            key = "|".join(sorted((a, b)))
            coup[key] = coup.get(key, 0.0) + ff
    return n_c, n_r, per, coup


def strip_mim_for_pex(
    gds_in: str | Path,
    gds_out: str | Path,
    *,
    mim: tuple[int, int] = (36, 0),
    vmim: tuple[int, int] = (129, 0),
    topmetal1: tuple[int, int] = (126, 0),
    margin_um: float | None = 0.2,
    layers: Sequence[tuple[int, int]] | None = None,
    topmetal_margin_um: float | None = None,
) -> Path:
    """Write a PEX-only copy of ``gds_in`` with the IHP MIM device layers removed (see the
    module docstring). Flattens the top cell. Needs the ``klayout`` python module.

    ``layers`` (default ``(mim, vmim)``) are the (layer, datatype) pairs cleared — an HBT/BiCMOS
    block also drops ``MemCap`` (69, 0). ``topmetal_margin_um`` (alias of ``margin_um``, wins when
    given) is how far TopMetal1 is cut back over the MIM plates; ``None`` keeps TopMetal1 intact so
    the plates stay as plain metal and their coupling to the neighbourhood is still extracted."""
    import klayout.db as db

    if topmetal_margin_um is not None:
        margin_um = topmetal_margin_um
    strip = tuple(layers) if layers is not None else (mim, vmim)
    ly = db.Layout()
    ly.read(str(gds_in))
    top = ly.top_cell()
    lmim = ly.layer(*mim)
    region = db.Region(top.begin_shapes_rec(lmim)).merged()
    top.flatten(True)
    for lay in strip:
        top.shapes(ly.layer(*lay)).clear()
    if margin_um is not None:
        ltm = ly.layer(*topmetal1)
        tm = db.Region(top.begin_shapes_rec(ltm)).merged()
        top.shapes(ltm).clear()
        top.shapes(ltm).insert(tm - region.sized(int(round(margin_um / ly.dbu))))
    ly.write(str(gds_out))
    return Path(gds_out)


def strip_cards(netlist_text: str, prefixes: tuple[str, ...] = ("C",)) -> str:
    """Drop element cards starting with ``prefixes`` (default the ``C`` cards) — the schematic
    kpex compares against when the MIM devices were stripped from the GDS."""
    return (
        "\n".join(ln for ln in netlist_text.splitlines() if ln.lstrip()[:1].upper() not in prefixes)
        + "\n"
    )


def run_pex(
    gds: str | Path,
    cell: str,
    schematic: str | Path,
    out_dir: str | Path,
    *,
    mode: str = "CC",
    pdk: str = "ihp-sg13g2",
    engine: str = "--2.5D",
    timeout_s: int = 3600,
    halo_um: float | None = None,
) -> PexResult:
    """Run kpex on ``cell`` of ``gds`` against ``schematic``.

    ``halo_um`` overrides the tech file's sidewall halo (kpex ``--halo``): couplings between
    shapes farther apart than the halo are DROPPED, so a knob that sweeps a spacing across
    the tech default (IHP: 8 um) sees a fake step in C — raise the halo (e.g. 20) when an
    optimizer explores spacings around it."""
    gds, schematic, out_dir = (
        Path(gds).resolve(),
        Path(schematic).resolve(),
        Path(out_dir).resolve(),
    )
    kp, kl = kpex_exe(), kpex_klayout_exe()
    if not kp:
        return PexResult(
            False, False, mode, reason="kpex not found (SIGNOFF_KPEX / PATH / pex env)"
        )
    if not kl:
        return PexResult(
            False, False, mode, reason="no Ruby≥2.6 klayout for kpex (KPEX_KLAYOUT_EXE)"
        )
    for f in (gds, schematic):
        if not f.is_file():
            return PexResult(False, True, mode, reason=f"input not found: {f}")
    out_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["KPEX_KLAYOUT_EXE"] = kl
    env.setdefault("PDK_ROOT", str(pdk_root()))
    cmd = [
        kp,
        "--pdk",
        pdk,
        "--gds",
        str(gds),
        "--cell",
        cell,
        "--schematic",
        str(schematic),
        engine,
        "--mode",
        mode,
        "--out_dir",
        str(out_dir),
    ]
    if halo_um is not None:
        cmd += ["--halo", str(halo_um)]
    try:
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return PexResult(False, True, mode, reason=f"kpex timed out after {timeout_s}s")
    out = r.stdout + r.stderr
    spice = out_dir / f"{gds.stem}__{cell}" / f"{cell}_k25d_pex_netlist.spice"
    if r.returncode != 0 or not spice.is_file():
        return PexResult(
            False,
            True,
            mode,
            log=tail(out, 6000),
            reason=f"kpex exited {r.returncode}; netlist {'found' if spice.is_file() else 'missing'}",
        )
    n_c, n_r, per, coup = summarize_parasitics(spice)
    return PexResult(
        True,
        True,
        mode,
        netlist_path=str(spice),
        n_c=n_c,
        n_r=n_r,
        per_net_c_ff=per,
        coupling_ff=coup,
        log=tail(out),
    )
