"""DRC through the PDK's own KLayout rule deck (``run_drc.py``), parsed to a :class:`DrcResult`.

The PDK runner ``chdir``s into its own deck directory, so every path is made absolute
first — a relative ``run_dir`` silently lands the report inside the PDK tree. The
report is KLayout's ``.lyrdb`` XML; :func:`parse_lyrdb` turns its ``<items>`` into
per-rule counts + a few sample locations, which is what an agent/optimizer needs to
*act* on a failure (rule name → generator knob), not just to know it failed.
"""

from __future__ import annotations

import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from .pdk import PdkPaths, for_pdk, klayout_exe, runner_python
from .results import DrcResult, DrcViolation, tail

_COORD = re.compile(r"\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)")


def parse_lyrdb(path: str | Path, max_locations: int = 5) -> list[DrcViolation]:
    """Per-rule violation counts (+ up to ``max_locations`` sample points, µm) from a .lyrdb."""
    root = ET.parse(str(path)).getroot()
    items = root.find("items")
    per: dict[str, DrcViolation] = {}
    if items is None:
        return []
    for it in items.findall("item"):
        cat = (it.findtext("category") or "").strip().strip("'")
        v = per.setdefault(cat, DrcViolation(rule=cat, count=0))
        v.count += 1
        if len(v.locations) < max_locations:
            for val in it.findall("./values/value"):
                m = _COORD.search(val.text or "")
                if m:
                    v.locations.append((float(m.group(1)), float(m.group(2))))
                    break
    return sorted(per.values(), key=lambda x: -x.count)


def run_drc(
    gds: str | Path,
    topcell: str,
    run_dir: str | Path,
    *,
    pdk: str | PdkPaths = "ihp-sg13g2",
    no_density: bool = True,
    extra_args: list[str] | None = None,
    timeout_s: int = 1800,
    max_locations: int = 50,
) -> DrcResult:
    """Run the PDK DRC deck on ``gds``/``topcell``; results under ``run_dir``.

    Returns ``available=False`` (never raises) when the deck or a klayout executable is
    missing, so callers can log a structured verdict either way.
    """
    p = for_pdk(pdk) if isinstance(pdk, str) else pdk
    gds, run_dir = Path(gds).resolve(), Path(run_dir).resolve()
    kl = klayout_exe()
    if not p.drc_runner.is_file():
        return DrcResult(False, False, reason=f"DRC deck not found: {p.drc_runner}")
    if not kl:
        return DrcResult(False, False, reason="no klayout executable (SIGNOFF_KLAYOUT / PATH)")
    if not gds.is_file():
        return DrcResult(False, True, reason=f"GDS not found: {gds}")
    run_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        runner_python(),
        str(p.drc_runner),
        f"--path={gds}",
        f"--topcell={topcell}",
        f"--run_dir={run_dir}",
    ]
    if no_density:
        cmd.append("--no_density")
    cmd += extra_args or []
    env = dict(os.environ)
    env["PATH"] = str(Path(kl).parent) + os.pathsep + env.get("PATH", "")
    try:
        r = subprocess.run(
            cmd, cwd=p.drc_runner.parent, capture_output=True, text=True, env=env, timeout=timeout_s
        )
    except subprocess.TimeoutExpired:
        return DrcResult(False, True, reason=f"DRC timed out after {timeout_s}s")
    out = r.stdout + r.stderr
    passed = "DRC Check Passed" in out
    reports = sorted(run_dir.glob("*_full.lyrdb")) or sorted(run_dir.glob("*.lyrdb"))
    viol: list[DrcViolation] = []
    if reports:
        try:
            viol = parse_lyrdb(reports[-1], max_locations=max_locations)
        except ET.ParseError:
            viol = []
    n = sum(v.count for v in viol)
    if not passed and n == 0 and r.returncode != 0:
        return DrcResult(
            False,
            True,
            report_path=str(reports[-1]) if reports else None,
            log=tail(out),
            reason="DRC runner exited non-zero without a parsable report",
        )
    return DrcResult(
        passed=passed and n == 0,
        available=True,
        n_violations=n,
        violations=viol,
        report_path=str(reports[-1]) if reports else None,
        log=tail(out),
    )
