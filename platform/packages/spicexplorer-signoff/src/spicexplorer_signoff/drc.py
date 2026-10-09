"""DRC through the PDK's KLayout rule deck, parsed to a :class:`DrcResult`.

Two deck forms run, chosen by :meth:`~spicexplorer_signoff.pdk.PdkPaths.drc_deck`:

- **the PDK's ``run_drc.py``**, run as ``<python> run_drc.py --path=… --topcell=… --run_dir=…``;
  a clean cell prints ``DRC Check Passed``.
- **a KLayout ``.lydrc`` rule deck**, used when the checkout ships no ``run_drc.py``, run as
  ``klayout -b -r <deck> -rd in_gds=… -rd cell=… -rd report_file=…``; after its last rule it
  prints ``Number of DRC errors: <N>``, and a clean cell prints ``N = 0``.

Every path is made absolute first. The ``run_drc.py`` runner changes into its own deck directory,
so a relative ``run_dir`` puts the report inside the PDK tree; a ``.lydrc`` deck writes its report
beside the input GDS unless ``report_file`` names another place. The report is KLayout's
``.lyrdb`` XML; :func:`parse_lyrdb` turns its ``<items>`` into a count per rule and a few sample
locations, so the caller learns which rule failed and where, not only that DRC failed.
"""

from __future__ import annotations

import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from .pdk import PdkPaths, for_pdk, klayout_exe, runner_python
from .results import DrcResult, DrcViolation, proc_output, snapshot, tail, written_since

_COORD = re.compile(r"\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)")
#: the line a `.lydrc` deck prints after its last rule: the error count summed over every rule
_LYDRC_COUNT = re.compile(r"^Number of DRC errors:\s*(\d+)\s*$", re.M)


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
    deck: str | Path | None = None,
) -> DrcResult:
    """Run the PDK DRC deck on ``gds``/``topcell``; results under ``run_dir``.

    The deck is ``deck`` when given (a ``run_drc.py`` runner or a ``.lydrc`` file), else
    :meth:`PdkPaths.drc_deck`: the PDK's ``run_drc.py``, or its first ``.lydrc`` deck when the
    checkout has no runner. ``no_density`` skips the chip-level density rules, which a single cell
    cannot meet: ``--no_density`` for ``run_drc.py``, ``-rd densityRules=false`` for a ``.lydrc``
    deck. ``extra_args`` go on the end of the command line unchanged (``run_drc.py`` options, or
    ``-rd name=value`` pairs for a ``.lydrc`` deck). ``DrcResult.deck`` names the deck that ran.

    Returns ``available=False`` (never raises) when :func:`for_pdk` has no entry for the PDK, or
    no deck or no klayout executable is found, so the caller always gets a DrcResult to record.
    """
    try:
        p = for_pdk(pdk) if isinstance(pdk, str) else pdk
    except ValueError as exc:  # an unsupported PDK is a verdict, not a crash of `run_flow`
        return DrcResult(False, False, reason=str(exc), no_density=no_density)
    gds, run_dir = Path(gds).resolve(), Path(run_dir).resolve()
    kl = klayout_exe()
    chosen = Path(deck).expanduser().absolute() if deck is not None else p.drc_deck()
    if chosen is None or not chosen.is_file():
        looked = [chosen] if chosen is not None else [p.drc_runner, *p.drc_decks]
        return DrcResult(
            False,
            False,
            reason=f"DRC deck not found: {', '.join(str(x) for x in looked)}",
            no_density=no_density,
        )
    used = str(chosen)
    if not kl:
        return DrcResult(
            False,
            False,
            reason="no klayout executable (SIGNOFF_KLAYOUT / PATH)",
            deck=used,
            no_density=no_density,
        )
    if not gds.is_file():
        return DrcResult(
            False, True, reason=f"GDS not found: {gds}", deck=used, no_density=no_density
        )
    run_dir.mkdir(parents=True, exist_ok=True)
    lydrc = chosen.suffix.lower() == ".lydrc"
    report = run_dir / f"{topcell}_{chosen.stem}.lyrdb"  # where a `.lydrc` deck is told to write
    if lydrc:
        cmd = [kl, "-b", "-r", used, "-rd", f"in_gds={gds}", "-rd", f"cell={topcell}"]
        cmd += ["-rd", f"report_file={report}"]
        if no_density:
            cmd += ["-rd", "densityRules=false"]
        clean = "Number of DRC errors: 0"
    else:
        cmd = [runner_python(), used, f"--path={gds}", f"--topcell={topcell}"]
        cmd.append(f"--run_dir={run_dir}")
        if no_density:
            cmd.append("--no_density")
        clean = "DRC Check Passed"
    cmd += extra_args or []
    env = dict(os.environ)
    env["PATH"] = str(Path(kl).parent) + os.pathsep + env.get("PATH", "")
    # `run_dir` is never cleared between attempts, so an earlier run's .lyrdb would otherwise be
    # parsed as this run's violations. Snapshot first; only count reports this run wrote.
    # cwd = the run dir (same reason as LVS): the PDK runner resolves its rule deck through
    # `__file__`, so any cwd-relative artefact a deck writes lands with this run, not in the PDK.
    before = snapshot(run_dir.glob("*.lyrdb"))
    try:
        r = subprocess.run(
            cmd, cwd=run_dir, capture_output=True, text=True, env=env, timeout=timeout_s
        )
    except subprocess.TimeoutExpired as exc:
        partial = proc_output(exc.stdout) + proc_output(exc.stderr)
        return DrcResult(
            False,
            True,
            log=tail(partial),
            reason=(
                f"DRC timed out after {timeout_s}s: "
                f"{tail(partial.strip() or '(no output before the timeout)', 2000)}"
            ),
            deck=used,
            no_density=no_density,
        )
    out = r.stdout + r.stderr
    if lydrc:
        # Read the number, not only whether the line is there: "Number of DRC errors: 12" is a
        # finished run with 12 violations. The last count printed is the deck's total.
        counts = _LYDRC_COUNT.findall(out)
        passed = bool(counts) and int(counts[-1]) == 0
        reports = written_since([report], before)
    else:
        passed = "DRC Check Passed" in out
        reports = sorted(written_since(run_dir.glob("*_full.lyrdb"), before)) or sorted(
            written_since(run_dir.glob("*.lyrdb"), before)
        )
    viol: list[DrcViolation] = []
    unparseable = ""
    if reports:
        try:
            viol = parse_lyrdb(reports[-1], max_locations=max_locations)
        except ET.ParseError as exc:
            # Swallowing this into `viol = []` made a corrupt report indistinguishable from a clean
            # cell — and a truncated report is exactly when a clean verdict must not be believed.
            unparseable = f"{reports[-1].name} could not be parsed: {exc}"
    n = sum(v.count for v in viol)
    report_path = str(reports[-1]) if reports else None
    # A clean cell says so on stdout. Anything else — no verdict line and no violations — is a
    # runner that did not do the job, whatever its exit status: a deck that dies early still exits
    # 0 often enough that trusting the status reported a silent PASS. Only a POSITIVE verdict
    # passes. A missing report fails a `.lydrc` run only (below): `run_drc.py` may write no .lyrdb
    # for a clean cell.
    if unparseable:
        return DrcResult(
            False,
            True,
            report_path=report_path,
            log=tail(out),
            reason=(
                f"DRC wrote a report this run that is not readable, so its verdict cannot be "
                f"trusted: {unparseable}"
            ),
            deck=used,
            no_density=no_density,
        )
    # A POSITIVE verdict is necessary but not sufficient. The exit status is still never trusted on
    # its own — a deck that dies early exits 0 often enough that doing so reported a silent PASS,
    # which is why the verdict marker is required above — but a runner that printed the verdict and
    # then died did not finish the job either, and used to pass (Codex review, item SIGN-01). So the
    # conditions are ADDED, not swapped: marker AND clean exit AND a report that parsed.
    if passed and r.returncode != 0:
        return DrcResult(
            False,
            True,
            n_violations=n,
            violations=viol,
            report_path=report_path,
            log=tail(out),
            reason=(
                f"DRC printed {clean!r} but the runner then exited {r.returncode}; a "
                f"verdict from a run that did not finish is not a clean cell: "
                f"{tail(r.stderr.strip() or r.stdout.strip() or '(no output)', 2000)}"
            ),
            deck=used,
            no_density=no_density,
        )
    # A `.lydrc` deck names its report (`report(…, report_file)`) before its first rule, but
    # KLayout writes the .lyrdb only when the run ends, after the deck has printed its count. A
    # save that fails there still exits 0 (KLayout 0.30.5, report_file in a missing directory:
    # "Unable to open file … in ReportDatabase::save in Executable::cleanup"), so a clean count
    # with no report from this run is not a pass.
    if passed and lydrc and not reports:
        return DrcResult(
            False,
            True,
            log=tail(out),
            reason=(
                f"DRC printed {clean!r} but wrote no {report.name} during this run, so the "
                f"count has no report behind it"
            ),
            deck=used,
            no_density=no_density,
        )
    if not passed and n == 0:
        return DrcResult(
            False,
            True,
            report_path=report_path,
            log=tail(out),
            reason=(
                f"DRC runner exited {r.returncode} without a {clean!r} verdict and "
                f"without violations from a report written by this run: "
                f"{tail(r.stderr.strip() or r.stdout.strip() or '(no output)', 2000)}"
            ),
            deck=used,
            no_density=no_density,
        )
    return DrcResult(
        passed=passed and n == 0,
        available=True,
        n_violations=n,
        violations=viol,
        report_path=report_path,
        log=tail(out),
        deck=used,
        no_density=no_density,
    )
