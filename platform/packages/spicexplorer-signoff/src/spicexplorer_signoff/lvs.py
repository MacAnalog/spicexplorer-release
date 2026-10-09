"""LVS through the PDK's KLayout deck (``run_lvs.py``), parsed to an :class:`LvsResult`.

The reference netlist is the *certified schematic netlist of record*; its path and
sha are recorded in the verdict so a reviewer can prove which netlist was compared
(the most common false pass is a clean LVS against the wrong file).

The verdict is read from the runner's output and the log it wrote during this run:

- **match**: ``Netlists match`` (IHP SG13G2: ``INFO : Congratulations! Netlists match.``);
- **mismatch**: ``Netlists don't match`` (IHP SG13G2: ``ERROR : Netlists don't match``), or
  unmatched counts such as ``2 unmatched nets`` from a deck that prints them;
- **no verdict**: neither of the above, or a nonzero exit: a runner that did not finish.

The IHP ``run_lvs.py`` imports ``docopt``; it runs under ``SIGNOFF_PYTHON`` (default: this
interpreter), so ``docopt`` is a dependency of this package.
"""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path

from .pdk import PdkPaths, for_pdk, klayout_exe, runner_python
from .results import LvsResult, proc_output, snapshot, tail, written_since

_UNMATCHED = re.compile(r"(\d+)\s+(?:un)?matched\s+(net|device|pin|circuit)s?", re.I)
#: a deck's own mismatch verdict; IHP SG13G2 prints "ERROR : Netlists don't match". It does not
#: contain the substring "Netlists match", so the match test alone reads it as no verdict at all.
_MISMATCH = re.compile(r"Netlists (?:don't|do not) match", re.I)


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
    try:
        p = for_pdk(pdk) if isinstance(pdk, str) else pdk
    except ValueError as exc:  # an unsupported PDK is a verdict, not a crash of `run_flow`
        return LvsResult(False, False, reason=str(exc))
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
    # `run_dir` is only mkdir-ed, never cleared, so the ordinary fix-and-retry loop leaves an
    # earlier successful log next to a crashed runner. Snapshot before the run and read the verdict
    # ONLY out of files this run wrote.
    # cwd = the RUN DIR, not the deck's own directory. The IHP LVS runset falls back to
    # `Pathname.new(RBA::CellView.active.filename).parent` for its extracted netlist when
    # `target_netlist` is unset, and an empty filename makes that `..` — i.e. the parent of the
    # process cwd. `run_lvs.py` does set `target_netlist`, and it resolves its rule deck through
    # `__file__`, so nothing here depends on the old cwd; running from `run_dir` only means a
    # deck that ever does fall through writes next to this run instead of into the shared PDK tree.
    before = snapshot(run_dir.glob("*.log"))
    try:
        r = subprocess.run(
            cmd, cwd=run_dir, capture_output=True, text=True, env=env, timeout=timeout_s
        )
    except subprocess.TimeoutExpired as exc:
        partial = proc_output(exc.stdout) + proc_output(exc.stderr)
        return LvsResult(
            False,
            True,
            reason=(
                f"LVS timed out after {timeout_s}s: "
                f"{tail(partial.strip() or '(no output before the timeout)', 2000)}"
            ),
            netlist_path=str(netlist),
            netlist_sha=sha256(netlist),
            log=tail(partial),
        )
    out = r.stdout + r.stderr
    logs = sorted(written_since(run_dir.glob(f"{topcell}.log"), before)) or sorted(
        written_since(run_dir.glob("*.log"), before)
    )
    if logs:
        out += "\n" + logs[-1].read_text(errors="replace")[-20000:]
    mismatch = _MISMATCH.search(out)
    matched = "Netlists match" in out and mismatch is None
    unmatched: dict[str, int] = {}
    if not matched:
        for m in _UNMATCHED.finditer(out):
            unmatched[m.group(2).lower()] = unmatched.get(m.group(2).lower(), 0) + int(m.group(1))
    # A crashed runner is not a mismatch. Before this check the caller got matched=False and an
    # EMPTY reason while the cause (e.g. the PDK deck's `import docopt` failing under
    # SIGNOFF_PYTHON) was in stderr. A runner that exits 0 without printing any verdict did not
    # finish either, so it also fails with a reason.
    reason = ""
    if r.returncode != 0 or not logs or not (matched or unmatched or mismatch):
        if not logs:
            why = f"wrote no {topcell}.log during this run"
        elif not (matched or unmatched or mismatch):
            why = "produced a log carrying neither a 'Netlists match' verdict nor unmatched counts"
        else:
            why = "failed"
        reason = (
            f"LVS runner exited {r.returncode} and {why}: "
            f"{tail(r.stderr.strip() or r.stdout.strip() or '(no output)', 2000)}"
        )
    elif mismatch is not None:
        # A finished comparison that found a difference (#278). It used to fall into the
        # no-verdict branch above and read like a crashed runner. The reason is never empty: the
        # layout backend reports `LVS mismatch: {unmatched or reason}`.
        reason = (
            f"the layout does not match the reference netlist {netlist.name}: the deck printed "
            f"{mismatch.group(0)!r}; the comparison per net and per device is in the .lvsdb "
            f"file in {run_dir}"
        )
    return LvsResult(
        # `matched` is necessary but not sufficient. `reason` was already set on a dirty exit while
        # `passed` stayed True, so the record contradicted itself: passed=True next to "LVS runner
        # exited 7 and wrote no cell.log". The exit status is still not trusted ALONE (a verdict-free
        # exit 0 is a failure too, above) — it is an ADDED condition (Codex review, item SIGN-01).
        # `reason` is exactly the set of cases that must not pass, so it is the condition.
        passed=matched and not reason,
        available=True,
        matched=matched,
        unmatched=unmatched,
        report_path=str(logs[-1]) if logs else None,
        netlist_path=str(netlist),
        netlist_sha=sha256(netlist),
        log=tail(out),
        reason=reason,
    )
