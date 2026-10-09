"""DRC on a PDK checkout that ships only KLayout ``.lydrc`` decks (MacAnalog/spicexplorer-platform#277).

The lab workstation's IHP SG13G2 checkout (CHANGELOG "Unreleased - 2024-10-14") has
``drc/sg13g2_maximal.lydrc`` and ``drc/sg13g2_minimal.lydrc`` and no ``drc/run_drc.py``. Before the
fix ``run_drc`` looked for ``run_drc.py`` only and returned ``available=False``, and
``probe().drc_ok`` was False. Offline: a script named ``klayout`` stands in for
``klayout -b -r <deck> -rd name=value …``; it records its argument list in ``argv.json`` in its
working directory and prints the deck's closing count line.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
from spicexplorer_signoff import DrcResult, probe
from spicexplorer_signoff.drc import run_drc
from spicexplorer_signoff.pdk import PdkPaths, for_pdk

_HEAD = (
    "#!/usr/bin/env python3\n"
    "import json, pathlib, sys\n"
    "a = sys.argv[1:]\n"
    "pathlib.Path('argv.json').write_text(json.dumps(a))\n"
    "rd = dict(a[i + 1].split('=', 1) for i, x in enumerate(a) if x == '-rd')\n"
    "report = pathlib.Path(rd['report_file'])\n"
)
_EMPTY = "<report-database><items></items></report-database>"
_ONE_M1A = (
    "<report-database><items><item><category>'M1.a'</category><values>"
    "<value>edge-pair: (0,0;0,2)|(0.1,2;0.1,0)</value></values></item></items></report-database>"
)


def _pdk(
    tmp_path: Path, *, runner: bool = False, decks: tuple[str, ...] = ("max", "min")
) -> PdkPaths:
    """A PDK with no `run_drc.py` (unless ``runner``) and the named `.lydrc` decks present."""
    drc = tmp_path / "pdk" / "drc"
    drc.mkdir(parents=True)
    if runner:
        (drc / "run_drc.py").write_text("print('DRC Check Passed')\n")
    for name in decks:
        (drc / f"deck_{name}.lydrc").write_text("<klayout-macro/>\n")
    return PdkPaths(
        name="fake",
        root=tmp_path / "pdk",
        klayout_tech=tmp_path / "pdk",
        drc_runner=drc / "run_drc.py",
        lvs_runner=tmp_path / "pdk" / "run_lvs.py",
        lyp=tmp_path / "pdk" / "fake.lyp",
        ngspice_models=tmp_path / "pdk",
        drc_decks=(drc / "deck_max.lydrc", drc / "deck_min.lydrc"),
    )


@pytest.fixture
def fake_klayout(tmp_path, monkeypatch):
    """Install a `klayout` stand-in whose behaviour after `_HEAD` is the string passed in."""
    (tmp_path / "cell.gds").write_bytes(b"")

    def install(body: str) -> Path:
        exe = tmp_path / "bin" / "klayout"
        exe.parent.mkdir(exist_ok=True)
        exe.write_text(_HEAD + body)
        exe.chmod(0o755)
        monkeypatch.setattr("spicexplorer_signoff.drc.klayout_exe", lambda: str(exe))
        return exe

    return install


def _clean_run(report: str = _EMPTY, count: int = 0, rc: int = 0) -> str:
    return (
        f"report.write_text({report!r})\nprint('Number of DRC errors: {count}')\nsys.exit({rc})\n"
    )


def test_run_drc_falls_back_to_the_first_lydrc_deck(tmp_path, fake_klayout):
    """The #277 reproduction: no `run_drc.py`, a `.lydrc` deck present. The base returned
    `available=False, reason='DRC deck not found: …/run_drc.py'`."""
    pdk = _pdk(tmp_path)
    fake_klayout(_clean_run())
    run = tmp_path / "run"
    r = run_drc(tmp_path / "cell.gds", "cell", run, pdk=pdk)
    assert isinstance(r, DrcResult)
    assert r.available and r.passed and r.n_violations == 0 and not r.reason, r.reason
    assert r.deck == str(pdk.drc_decks[0])  # the maximal (first) deck, not the minimal one
    assert r.report_path == str(run.resolve() / "cell_deck_max.lyrdb")
    argv = json.loads((run / "argv.json").read_text())  # the deck ran with cwd = the run dir
    assert argv[:3] == ["-b", "-r", str(pdk.drc_decks[0])]
    assert f"in_gds={(tmp_path / 'cell.gds').resolve()}" in argv and "cell=cell" in argv
    assert f"report_file={run.resolve() / 'cell_deck_max.lyrdb'}" in argv
    assert argv[-2:] == ["-rd", "densityRules=false"]  # no_density=True is the default


def test_run_drc_on_an_ihp_checkout_that_ships_only_lydrc_decks(
    tmp_path, fake_klayout, monkeypatch
):
    """The same reproduction through the call every consumer makes, `pdk="ihp-sg13g2"`, on a
    checkout laid out like the lab's: `drc/` holds the two `.lydrc` decks and nothing else."""
    drc = tmp_path / "pdks" / "ihp-sg13g2" / "libs.tech" / "klayout" / "tech" / "drc"
    drc.mkdir(parents=True)
    for name in ("sg13g2_maximal.lydrc", "sg13g2_minimal.lydrc"):
        (drc / name).write_text("<klayout-macro/>\n")
    monkeypatch.setenv("PDK_ROOT", str(tmp_path / "pdks"))
    fake_klayout(_clean_run())
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run")
    assert r.available, r.reason
    assert r.passed and r.deck == str(drc / "sg13g2_maximal.lydrc")


def test_run_drc_lydrc_violations_come_from_the_report(tmp_path, fake_klayout):
    fake_klayout(_clean_run(_ONE_M1A, count=1))
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=_pdk(tmp_path))
    assert r.available and not r.passed and r.n_violations == 1
    assert [(v.rule, v.count, v.locations) for v in r.violations] == [("M1.a", 1, [(0.0, 0.0)])]


def test_run_drc_lydrc_density_rules_on_and_extra_args_appended(tmp_path, fake_klayout):
    fake_klayout(_clean_run())
    run = tmp_path / "run"
    r = run_drc(
        tmp_path / "cell.gds",
        "cell",
        run,
        pdk=_pdk(tmp_path),
        no_density=False,
        extra_args=["-rd", "threads=1"],
    )
    assert r.passed
    argv = json.loads((run / "argv.json").read_text())
    assert not any(a.startswith("densityRules") for a in argv)
    assert argv[-2:] == ["-rd", "threads=1"]


@pytest.mark.parametrize(
    ("body", "phrase"),
    [
        # exit 0, report written, no count line: the deck stopped before its last line
        (f"report.write_text({_EMPTY!r})\n", "without a 'Number of DRC errors: 0' verdict"),
        # a nonzero count with a report that lists nothing: the two disagree, so no pass
        (_clean_run(count=3), "without a 'Number of DRC errors: 0' verdict"),
        # a clean count and no report from this run
        ("print('Number of DRC errors: 0')\n", "wrote no cell_deck_max.lyrdb during this run"),
        # a clean count, a clean report, then a nonzero exit
        (_clean_run(rc=3), "then exited 3"),
    ],
    ids=["no-count-line", "count-disagrees", "no-report", "dirty-exit"],
)
def test_run_drc_lydrc_needs_count_zero_report_and_clean_exit(tmp_path, fake_klayout, body, phrase):
    fake_klayout(body)
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=_pdk(tmp_path))
    assert r.available and not r.passed, "a .lydrc run without all three conditions passed"
    assert phrase in r.reason, r.reason
    assert r.deck and r.deck.endswith("deck_max.lydrc")


def _old_report(run: Path, age_s: float = 100.0) -> Path:
    """A clean `cell_deck_max.lyrdb` left in `run` by an earlier run, dated ``age_s`` back."""
    run.mkdir(parents=True, exist_ok=True)
    old = run / "cell_deck_max.lyrdb"
    old.write_text(_EMPTY)
    t = time.time() - age_s
    os.utime(old, (t, t))
    return old


def test_run_drc_lydrc_ignores_a_clean_report_left_by_an_earlier_run(tmp_path, fake_klayout):
    """`run_dir` is reused between attempts. A clean report from an earlier run must not stand in
    for the report this run was told to write: the deck printed a zero count and wrote nothing."""
    run = tmp_path / "run"
    _old_report(run)
    fake_klayout("print('Number of DRC errors: 0')\n")
    r = run_drc(tmp_path / "cell.gds", "cell", run, pdk=_pdk(tmp_path))
    assert r.available and not r.passed, "an earlier run's report was read as this run's"
    assert "wrote no cell_deck_max.lyrdb during this run" in r.reason, r.reason
    assert r.report_path is None


def test_run_drc_lydrc_reads_a_report_this_run_rewrote(tmp_path, fake_klayout):
    """The same file name, rewritten by this run, is this run's report."""
    run = tmp_path / "run"
    old = _old_report(run)
    fake_klayout(_clean_run())
    r = run_drc(tmp_path / "cell.gds", "cell", run, pdk=_pdk(tmp_path))
    assert r.available and r.passed, r.reason
    assert r.report_path == str(old.resolve())


def test_run_drc_lydrc_timeout_names_the_deck(tmp_path, fake_klayout):
    fake_klayout("import time\nprint('M1.a: 0', flush=True)\ntime.sleep(30)\n")
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=_pdk(tmp_path), timeout_s=1)
    assert not r.passed and "timed out" in r.reason and "M1.a: 0" in r.log
    assert r.deck and r.deck.endswith("deck_max.lydrc")


def test_run_drc_prefers_run_drc_py_when_the_pdk_ships_it(tmp_path, fake_klayout, monkeypatch):
    """Nothing changes on a checkout that has the runner: it still runs, not the deck."""
    monkeypatch.delenv("SIGNOFF_PYTHON", raising=False)
    pdk = _pdk(tmp_path, runner=True)
    fake_klayout(_clean_run())
    run = tmp_path / "run"
    r = run_drc(tmp_path / "cell.gds", "cell", run, pdk=pdk)
    assert r.passed and r.deck == str(pdk.drc_runner)
    assert not (run / "argv.json").exists()  # klayout was not run directly


def test_run_drc_minimal_deck_when_only_it_is_present_and_explicit_deck(tmp_path, fake_klayout):
    pdk = _pdk(tmp_path, decks=("min",))
    fake_klayout(_clean_run())
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=pdk)
    assert r.passed and r.deck == str(pdk.drc_decks[1])
    # an explicit deck wins over the PDK's order; a missing one is named in the verdict
    both = _pdk(tmp_path / "b")
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run2", pdk=both, deck=both.drc_decks[1])
    assert r.passed and r.deck == str(both.drc_decks[1])
    r = run_drc(
        tmp_path / "cell.gds", "cell", tmp_path / "run3", pdk=both, deck=tmp_path / "x.lydrc"
    )
    assert not r.available and r.reason == f"DRC deck not found: {tmp_path / 'x.lydrc'}"


def test_run_drc_with_no_deck_at_all_names_every_place_it_looked(tmp_path):
    pdk = _pdk(tmp_path, decks=())
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=pdk)
    assert not r.available and not r.passed and r.deck is None
    for place in (pdk.drc_runner, *pdk.drc_decks):
        assert str(place) in r.reason


def test_run_drc_lydrc_without_klayout_or_gds_names_the_deck(tmp_path, monkeypatch):
    pdk = _pdk(tmp_path)
    monkeypatch.setattr("spicexplorer_signoff.drc.klayout_exe", lambda: None)
    r = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run", pdk=pdk)
    assert not r.available and "no klayout executable" in r.reason and r.deck
    monkeypatch.setattr("spicexplorer_signoff.drc.klayout_exe", lambda: "/bin/true")
    r = run_drc(tmp_path / "missing.gds", "cell", tmp_path / "run", pdk=pdk)
    assert r.available and not r.passed and "GDS not found" in r.reason and r.deck


def test_for_pdk_ihp_lists_the_lydrc_decks_and_probe_counts_them(tmp_path, monkeypatch):
    """probe().drc_deck_ok used to look at run_drc.py only, so drc_ok was False on this checkout."""
    drc = tmp_path / "ihp-sg13g2" / "libs.tech" / "klayout" / "tech" / "drc"
    drc.mkdir(parents=True)
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    p = for_pdk("ihp-sg13g2")
    assert [d.name for d in p.drc_decks] == ["sg13g2_maximal.lydrc", "sg13g2_minimal.lydrc"]
    assert p.drc_deck() is None and not probe("ihp-sg13g2").drc_deck_ok
    (drc / "sg13g2_minimal.lydrc").write_text("<klayout-macro/>\n")
    assert p.drc_deck() == drc / "sg13g2_minimal.lydrc" and probe("ihp-sg13g2").drc_deck_ok
    (drc / "run_drc.py").write_text("")
    assert p.drc_deck() == drc / "run_drc.py"
    d = p.to_dict()
    assert d["drc_decks"] == [str(x) for x in p.drc_decks] and d["drc_runner"] == str(
        drc / "run_drc.py"
    )
    json.dumps(d)  # JSON-safe, the tuple included


def test_the_verdict_records_the_density_setting_it_ran_with(tmp_path, fake_klayout):
    """A density-off clean DRC is conditional, so the verdict names the setting (L-PF-22)."""
    pdk = _pdk(tmp_path)
    fake_klayout(_clean_run())
    off = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run_off", pdk=pdk)
    on = run_drc(tmp_path / "cell.gds", "cell", tmp_path / "run_on", pdk=pdk, no_density=False)
    assert off.passed and on.passed
    assert (off.no_density, on.no_density) == (True, False)
    assert on.to_dict()["no_density"] is False
    assert run_drc(tmp_path / "cell.gds", "cell", tmp_path / "r", pdk="no-such-pdk").no_density
