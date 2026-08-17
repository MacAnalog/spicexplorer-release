"""LVS through the PDK's KLayout deck (``run_lvs.py``), parsed to an :class:`LvsResult`.

The reference netlist is the *certified schematic netlist of record*; its path and
sha are recorded in the verdict so a reviewer can prove which netlist was compared
(the most common false pass is a clean LVS against the wrong file).
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path

from .pdk import PdkPaths, for_pdk, klayout_exe, runner_python
from .results import LvsResult, tail

_UNMATCHED = re.compile(r"(\d+)\s+(?:un)?matched\s+(net|device|pin|circuit)s?", re.I)


def sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_lvs(
    gds: str | Path,
    netlist: str | Path,
    topcell: str,
    run_dir: str | Path,
    *,
    pdk: str | PdkPaths = "ihp-sg13g2",
    extra_args: list[str] | None = None,
    timeout_s: int = 1800,
) -> LvsResult:
    p = for_pdk(pdk) if isinstance(pdk, str) else pdk
    gds, netlist, run_dir = Path(gds).resolve(), Path(netlist).resolve(), Path(run_dir).resolve()
    kl = klayout_exe()
    if not p.lvs_runner.is_file():
        return LvsResult(False, False, reason=f"LVS deck not found: {p.lvs_runner}")
    if not kl:
        return LvsResult(False, False, reason="no klayout executable (SIGNOFF_KLAYOUT / PATH)")
    for f in (gds, netlist):
        if not f.is_file():
            return LvsResult(False, True, reason=f"input not found: {f}")
    run_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        runner_python(),
        str(p.lvs_runner),
        f"--layout={gds}",
        f"--netlist={netlist}",
        f"--topcell={topcell}",
        f"--run_dir={run_dir}",
    ] + (extra_args or [])
    env = dict(os.environ)
    env["PATH"] = str(Path(kl).parent) + os.pathsep + env.get("PATH", "")
    try:
        r = subprocess.run(
            cmd, cwd=p.lvs_runner.parent, capture_output=True, text=True, env=env, timeout=timeout_s
        )
    except subprocess.TimeoutExpired:
        return LvsResult(
            False,
            True,
            reason=f"LVS timed out after {timeout_s}s",
            netlist_path=str(netlist),
            netlist_sha=sha256(netlist),
        )
    out = r.stdout + r.stderr
    logs = sorted(run_dir.glob(f"{topcell}.log")) or sorted(run_dir.glob("*.log"))
    if logs:
        out += "\n" + logs[-1].read_text(errors="replace")[-20000:]
    matched = "Netlists match" in out
    unmatched: dict[str, int] = {}
    if not matched:
        for m in _UNMATCHED.finditer(out):
            unmatched[m.group(2).lower()] = unmatched.get(m.group(2).lower(), 0) + int(m.group(1))
    return LvsResult(
        passed=matched,
        available=True,
        matched=matched,
        unmatched=unmatched,
        report_path=str(logs[-1]) if logs else None,
        netlist_path=str(netlist),
        netlist_sha=sha256(netlist),
        log=tail(out),
    )
