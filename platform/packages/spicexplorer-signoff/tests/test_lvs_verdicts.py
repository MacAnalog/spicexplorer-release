"""LVS verdicts from the IHP SG13G2 deck (MacAnalog/spicexplorer-platform#278).

On a mismatch the IHP deck logs ``ERROR : Netlists don't match`` and no unmatched counts, and
``run_lvs.py`` exits 0. The base looked for ``Netlists match`` and the counts only, so a finished
comparison that found a difference came back with the reason for a crashed runner: "exited 0 and
produced a log carrying neither a 'Netlists match' verdict nor unmatched counts".

``fixtures/ihp_lvs_mismatch.log`` is the log of that run, trimmed to its first lines and its
verdict block, with the run directory written as ``run/``. The reference had one gate net swapped
(an NMOS mirror, ``M2 iout iout vss vss`` instead of ``M2 iout iref vss vss``).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from spicexplorer_signoff.lvs import run_lvs
from spicexplorer_signoff.pdk import PdkPaths

FIX = Path(__file__).parent / "fixtures"
_MISMATCH_LOG = (FIX / "ihp_lvs_mismatch.log").read_text()
_MATCH_LOG = _MISMATCH_LOG.replace(
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "=========================================="
).replace("ERROR : Netlists don't match", "INFO : Congratulations! Netlists match.")
# what run_lvs.py itself printed on stdout during the recorded run (Python logging)
_STDOUT = (
    "25-Sep-2026 00:21:06 | INFO    | Your Klayout version is: KLayout 0.30.5\n"
    "25-Sep-2026 00:21:06 | INFO    | Running SG13G2 LVS checks on design run/cell.gds on cell cell\n"
)


@pytest.fixture
def lvs_runner(tmp_path, monkeypatch):
    """A PdkPaths whose run_lvs.py writes the given log to ``<run_dir>/cell.log`` and exits."""
    monkeypatch.delenv("SIGNOFF_PYTHON", raising=False)
    monkeypatch.setattr("spicexplorer_signoff.lvs.klayout_exe", lambda: str(tmp_path / "klayout"))
    (tmp_path / "cell.gds").write_bytes(b"")
    (tmp_path / "cell.sp").write_text(".subckt cell a\n.ends\n")
    runner = tmp_path / "run_lvs.py"
    pdk = PdkPaths(
        name="fake",
        root=tmp_path,
        klayout_tech=tmp_path,
        drc_runner=tmp_path / "run_drc.py",
        lvs_runner=runner,
        lyp=tmp_path / "fake.lyp",
        ngspice_models=tmp_path,
    )

    def install(log: str, rc: int = 0) -> PdkPaths:
        runner.write_text(
            "import sys, pathlib\n"
            "rd = [a.split('=', 1)[1] for a in sys.argv if a.startswith('--run_dir=')][0]\n"
            f"pathlib.Path(rd, 'cell.log').write_text({log!r})\n"
            f"sys.stdout.write({_STDOUT!r})\n"
            f"sys.exit({rc})\n"
        )
        return pdk

    return install


def _run(tmp_path: Path, pdk: PdkPaths):
    return run_lvs(tmp_path / "cell.gds", tmp_path / "cell.sp", "cell", tmp_path / "run", pdk=pdk)


def test_the_ihp_mismatch_line_is_a_mismatch_verdict(tmp_path, lvs_runner):
    """The #278 reproduction, on the recorded IHP log."""
    r = _run(tmp_path, lvs_runner(_MISMATCH_LOG))
    assert r.available and not r.passed and r.matched is False and r.unmatched == {}
    assert "neither" not in r.reason, "a finished comparison was reported as a runner failure"
    assert "does not match the reference netlist cell.sp" in r.reason
    assert "Netlists don't match" in r.reason and ".lvsdb" in r.reason
    assert r.report_path and r.report_path.endswith("cell.log")


def test_the_ihp_match_line_still_passes(tmp_path, lvs_runner):
    r = _run(tmp_path, lvs_runner(_MATCH_LOG))
    assert r.passed and r.matched and not r.reason


def test_a_mismatch_line_with_a_nonzero_exit_reports_the_exit(tmp_path, lvs_runner):
    """The runner-failure reason still wins when the runner did not exit cleanly."""
    r = _run(tmp_path, lvs_runner(_MISMATCH_LOG, rc=2))
    assert not r.passed and r.matched is False
    assert r.reason.startswith("LVS runner exited 2 and failed")


@pytest.mark.parametrize(
    "line",
    ["Netlists do not match", "INFO : Netlists match.\nERROR : Netlists don't match"],
    ids=["spelled-out", "both-lines"],
)
def test_any_mismatch_line_means_not_matched(tmp_path, lvs_runner, line):
    """ "do not" is read like "don't", and a log carrying both lines is not a match."""
    r = _run(tmp_path, lvs_runner(f"Starting SG13G2 LVS Comparison\n{line}\n"))
    assert not r.passed and r.matched is False and "does not match" in r.reason


def test_a_log_with_no_verdict_at_all_is_still_a_runner_failure(tmp_path, lvs_runner):
    """The negative case: a log that stops before the comparison keeps the no-verdict reason."""
    head = _MISMATCH_LOG.split("Starting SG13G2 LVS Comparison")[0]
    r = _run(tmp_path, lvs_runner(head))
    assert not r.passed and r.matched is False
    assert "neither a 'Netlists match' verdict nor unmatched counts" in r.reason


def test_unmatched_counts_without_a_mismatch_line_keep_their_shape(tmp_path, lvs_runner):
    """A deck that prints counts and no verdict line: counts recorded, no reason added."""
    r = _run(tmp_path, lvs_runner("2 unmatched nets\n1 unmatched device\n"))
    assert not r.passed and r.unmatched == {"net": 2, "device": 1} and r.reason == ""


def test_docopt_is_a_declared_dependency():
    """The IHP run_lvs.py starts with `from docopt import docopt` and runs under this interpreter
    by default; docopt reached the venv only through another package's dependency.

    The declaration is read from this package's `pyproject.toml`, not from the installed metadata:
    `uv sync` writes that metadata, so a venv synced on another branch would decide the result.
    """
    tomllib = pytest.importorskip("tomllib")  # Python 3.11+; the package supports 3.10
    meta = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8"))
    deps = meta["project"]["dependencies"]
    names = [re.split(r"[^A-Za-z0-9._-]", d.strip(), maxsplit=1)[0].lower() for d in deps]
    assert "docopt" in names, deps
