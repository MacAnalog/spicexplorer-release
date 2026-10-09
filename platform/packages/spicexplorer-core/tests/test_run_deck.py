"""`run_deck`: per-deck run dirs, `.spiceinit` in the cwd, busy marker, rc/fatal rules.

The offline tests drive a FAKE `ngspice` (a shell script that echoes what a real ngspice-45
batch run prints and drops a rawfile), so the directory/marker/parse rules are pinned without a
simulator; the `slow` tests run the real binary when it is on PATH.
"""

from __future__ import annotations

import os
import shutil
import socket
import stat
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from spicexplorer_core.spice_engine import DeckRunError, RunResult, deck_digest, run_deck

needs_ngspice = pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice not on PATH")

PROBE = textwrap.dedent(
    """\
    * lane probe: one resistor
    v1 a 0 1
    r1 a 0 1k
    .control
    op
    let i_ma = -i(v1)*1e3
    print i_ma
    write sim.raw
    quit
    .endc
    .end
    """
)


@pytest.fixture
def fake_ngspice(tmp_path):
    """A stand-in binary: prints the deck's `* log:` lines (with `\\n` expanded) on stdout and
    its `* err:` lines on stderr, writes `sim.raw` unless the deck says `* noraw`, exits with
    the deck's `* rc: N`."""
    exe = tmp_path / "bin" / "ngspice"
    exe.parent.mkdir()
    exe.write_text(
        textwrap.dedent(
            """\
            #!/bin/sh
            deck="$2"
            grep '^\\* log:' "$deck" | sed 's/^\\* log: //' | while IFS= read -r l; do printf '%b\\n' "$l"; done
            grep '^\\* err:' "$deck" | sed 's/^\\* err: //' | while IFS= read -r l; do printf '%b\\n' "$l" >&2; done
            grep -q '^\\* noraw' "$deck" || echo "fake raw" > sim.raw
            [ -f .spiceinit ] && echo "INIT_SEEN $(cat .spiceinit | head -1)"
            rc=$(grep '^\\* rc:' "$deck" | sed 's/^\\* rc: //')
            exit ${rc:-0}
            """
        )
    )
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    return str(exe)


def _deck(*log: str, rc: int = 0, noraw: bool = False, err: tuple[str, ...] = ()) -> str:
    lines = ["* fake deck"] + [f"* log: {ln}" for ln in log] + [f"* err: {ln}" for ln in err]
    lines.append(f"* rc: {rc}")
    if noraw:
        lines.append("* noraw")
    return "\n".join(lines) + "\n.end\n"


def test_run_dir_spiceinit_and_scalars(tmp_path, fake_ngspice):
    deck = _deck("i_ma = 1.000000e+00", "ugf = 1.2e6 at=  3.2")
    r = run_deck(
        deck,
        label="probe",
        workdir=tmp_path / "w",
        ngspice=fake_ngspice,
        spiceinit="set ngbehavior=hsa\n",
        extra_files={"inc.sp": "* inc\n"},
    )
    assert isinstance(r, RunResult) and r.ok and r.rc == 0
    assert r.dir == tmp_path / "w" / f"probe-{deck_digest(deck)}"
    assert (r.dir / ".spiceinit").read_text() == "set ngbehavior=hsa\n"
    assert (r.dir / "inc.sp").exists() and r.deck.read_text() == deck
    assert r.measures == {"i_ma": 1.0, "ugf": 1.2e6} and r.failed == [] and r.fatal == []
    assert r.raw is not None and r.raw.name == "sim.raw" and r.raws == [r.raw]
    assert "INIT_SEEN set ngbehavior=hsa" in r.text(), "ngspice ran with the run dir as cwd"
    assert str(r) == os.fspath(r) == str(r.dir) and Path(r) / "x" == r.dir / "x"
    assert float((r.dir / "wall.txt").read_text()) == pytest.approx(r.wall, abs=1e-3)
    assert not (r.dir / ".busy").exists()


def test_no_spiceinit_leaves_none(tmp_path, fake_ngspice):
    r = run_deck(_deck("x = 1"), label="p", workdir=tmp_path, ngspice=fake_ngspice)
    assert not (r.dir / ".spiceinit").exists() and "INIT_SEEN" not in r.text()


def test_different_decks_same_label_get_different_dirs(tmp_path, fake_ngspice):
    a = run_deck(_deck("x = 1"), label="same", workdir=tmp_path, ngspice=fake_ngspice)
    b = run_deck(_deck("x = 2"), label="same", workdir=tmp_path, ngspice=fake_ngspice)
    assert a.dir != b.dir and a.measures["x"] == 1 and b.measures["x"] == 2


def test_label_rules(tmp_path, fake_ngspice):
    with pytest.raises(ValueError):
        run_deck(_deck(), label="  ", workdir=tmp_path, ngspice=fake_ngspice)
    r = run_deck(_deck("x = 1"), label="a b/c", workdir=tmp_path, ngspice=fake_ngspice)
    assert r.dir.name.startswith("a_b_c-")


def test_failed_meas_is_not_fatal(tmp_path, fake_ngspice):
    r = run_deck(
        _deck(
            "Error: measure  bad  when(WHEN) : out of interval",
            " meas tran bad when v(a)=5 failed!",
            "good                =  1.500000e-09",
        ),
        label="fm",
        workdir=tmp_path,
        ngspice=fake_ngspice,
    )
    assert r.failed == ["bad"] and r.measures == {"good": 1.5e-9} and r.fatal == []


def test_fatal_line_raises_with_result_and_no_absolute_path(tmp_path, fake_ngspice):
    with pytest.raises(DeckRunError, match="RHS") as ei:
        run_deck(
            _deck('Error: RHS "v(nowhere)*2" invalid'),
            label="bad_let",
            workdir=tmp_path,
            ngspice=fake_ngspice,
        )
    assert ei.value.result is not None and ei.value.result.fatal
    assert str(tmp_path) not in str(ei.value), "error text names the run, never the work path"
    with pytest.raises(DeckRunError, match="ignored"):  # the silent-zero class
        run_deck(
            _deck(
                "Warning: 'r1 a 0' is not a valid resistor instance line, ignored!",
                "i_ma = -0.000000e+00",
            ),
            label="inv",
            workdir=tmp_path,
            ngspice=fake_ngspice,
        )


def test_nonzero_rc_raises(tmp_path, fake_ngspice):
    with pytest.raises(DeckRunError, match="rc=3") as ei:
        run_deck(_deck("x = 1", rc=3), label="rc3", workdir=tmp_path, ngspice=fake_ngspice)
    assert ei.value.result is not None and ei.value.result.rc == 3


def test_stale_raw_is_removed(tmp_path, fake_ngspice):
    deck = _deck("x = 1", noraw=True)
    rd = tmp_path / f"p-{deck_digest(deck)}"
    rd.mkdir()
    (rd / "old.raw").write_text("stale")
    r = run_deck(deck, label="p", workdir=tmp_path, ngspice=fake_ngspice)
    assert r.raws == [] and r.raw is None


def test_busy_marker_live_vs_stale(tmp_path, fake_ngspice):
    deck = _deck("x = 1")
    rd = tmp_path / f"p-{deck_digest(deck)}"
    rd.mkdir()
    (rd / ".busy").write_text(str(os.getpid()))  # a live owner: refuse
    with pytest.raises(DeckRunError, match="busy"):
        run_deck(deck, label="p", workdir=tmp_path, ngspice=fake_ngspice)
    (rd / ".busy").write_text(str(2**22 - 1))  # a dead owner (killed session): reclaim
    assert run_deck(deck, label="p", workdir=tmp_path, ngspice=fake_ngspice).measures["x"] == 1
    assert not (rd / ".busy").exists()


def test_missing_binary(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_deck(_deck(), label="p", workdir=tmp_path, ngspice=str(tmp_path / "nope"))


def test_timeout(tmp_path):
    exe = tmp_path / "slow"
    exe.write_text("#!/bin/sh\nsleep 5\n")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    with pytest.raises(DeckRunError, match="timed out"):
        run_deck(_deck(), label="p", workdir=tmp_path / "w", ngspice=str(exe), timeout=0.3)
    assert not list((tmp_path / "w").rglob(".busy")), "the marker is released on a timeout"


def test_extra_files_are_basenames_only(tmp_path, fake_ngspice):
    """A key with a path separator would land outside the run dir; the lane's own file names are
    reserved. Both are rejected before anything is created."""
    for bad in ("../ESCAPED.txt", "sub/inc.sp", "/abs.sp", "deck.sp", ".busy", "", "."):
        with pytest.raises(ValueError, match="extra_files"):
            run_deck(
                _deck("x = 1"),
                label="p",
                workdir=tmp_path / "w",
                ngspice=fake_ngspice,
                extra_files={bad: "* x\n"},
            )
    assert not (tmp_path / "ESCAPED.txt").exists() and not (tmp_path / "w").exists()


def test_body_meas_failure_is_reported_from_stderr(tmp_path, fake_ngspice):
    """A `.meas` in the deck body (batch mode, no `.control`) reports its failure on STDERR —
    ngspice-45 prints `Error: measure …` and ` .meas tran bad … failed!` there — so the parse
    must read the whole log, not stdout alone."""
    r = run_deck(
        _deck(
            "trise               =   1.50000e-09",
            err=(
                "Error: measure  bad  when(WHEN) : out of interval",
                " .meas tran bad when v(a)=5 failed!",
            ),
        ),
        label="body",
        workdir=tmp_path,
        ngspice=fake_ngspice,
    )
    assert r.failed == ["bad"] and r.measures == {"trise": 1.5e-9} and r.fatal == []


@pytest.mark.parametrize(
    "marker,age_s,busy",
    [
        ("", 0, False),  # empty marker: unparsable = stale, never `kill(0, …)`
        ("garbage", 0, False),  # unparsable = stale
        ("-5", 0, False),  # a non-positive pid is never a process to signal
        ("1", 0, True),  # pid 1 is alive; `kill` says PermissionError (or nothing as root)
        (f"{2**22 - 1} {socket.gethostname()}", 0, False),  # dead pid on this host: reclaim
        ("12345 some-other-host", 0, True),  # a foreign host's marker: alive while fresh …
        ("12345 some-other-host", 7200, False),  # … stale once older than the run timeout
    ],
)
def test_busy_marker_rules(tmp_path, fake_ngspice, marker, age_s, busy):
    deck = _deck("x = 1")
    rd = tmp_path / f"p-{deck_digest(deck)}"
    rd.mkdir()
    (rd / ".busy").write_text(marker)
    if age_s:
        old = time.time() - age_s
        os.utime(rd / ".busy", (old, old))
    if busy:
        with pytest.raises(DeckRunError, match="busy"):
            run_deck(deck, label="p", workdir=tmp_path, ngspice=fake_ngspice, timeout=3600)
        assert (rd / ".busy").read_text() == marker, "a live marker is left alone"
    else:
        r = run_deck(deck, label="p", workdir=tmp_path, ngspice=fake_ngspice, timeout=3600)
        assert r.measures["x"] == 1 and not (rd / ".busy").exists()


def test_own_marker_records_pid_and_host(tmp_path):
    exe = tmp_path / "peek"
    exe.write_text("#!/bin/sh\ncat .busy\necho\n")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    r = run_deck(_deck(), label="p", workdir=tmp_path / "w", ngspice=str(exe))
    assert r.text().split("\n")[0] == f"{os.getpid()} {socket.gethostname()}"


def test_timeout_keeps_partial_log(tmp_path):
    exe = tmp_path / "slow"
    exe.write_text("#!/bin/sh\necho PARTIAL_STDOUT\necho PARTIAL_STDERR >&2\nsleep 5\n")
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    with pytest.raises(DeckRunError, match="timed out"):
        run_deck(_deck(), label="p", workdir=tmp_path / "w", ngspice=str(exe), timeout=0.5)
    logs = list((tmp_path / "w").rglob("ngspice.out"))
    assert len(logs) == 1, "what ngspice printed before the timeout is kept"
    assert "PARTIAL_STDOUT" in logs[0].read_text() and "PARTIAL_STDERR" in logs[0].read_text()


# ------------------------------------------------------------------ live ----------------


@pytest.mark.slow
@needs_ngspice
def test_live_probe(tmp_path, monkeypatch):
    monkeypatch.delenv("SPICE_USERINIT_DIR", raising=False)
    r = run_deck(
        PROBE, label="probe", workdir=tmp_path, spiceinit="echo LANE_INIT_OK\n", timeout=120
    )
    assert r.measures["i_ma"] == pytest.approx(1.0, abs=1e-6) and r.raw is not None
    assert "LANE_INIT_OK" in r.text(), "the per-run .spiceinit was read"
    assert r.rc == 0 and r.wall > 0


@pytest.mark.slow
@needs_ngspice
def test_live_errors(tmp_path, monkeypatch):
    monkeypatch.delenv("SPICE_USERINIT_DIR", raising=False)
    bad = PROBE.replace("let i_ma = -i(v1)*1e3\nprint i_ma", "let x = v(nowhere)*2\nprint x")
    with pytest.raises(DeckRunError, match="RHS"):
        run_deck(bad, label="bad_let", workdir=tmp_path, timeout=120)
    with pytest.raises(DeckRunError, match="ignored"):
        run_deck(PROBE.replace("r1 a 0 1k", "r1 a 0"), label="inv", workdir=tmp_path, timeout=120)
    with pytest.raises(DeckRunError, match="rc=3"):
        run_deck(PROBE.replace("quit\n", "quit 3\n"), label="rc3", workdir=tmp_path, timeout=120)
    r = run_deck(
        "* p\nv1 a 0 pulse(0 1 1n 1n 1n 5n 10n)\nr1 a 0 1k\n.control\ntran 0.1n 20n\n"
        "meas tran bad when v(a)=5\nmeas tran good when v(a)=0.5 rise=1\nwrite sim.raw\nquit\n"
        ".endc\n.end\n",
        label="failmeas",
        workdir=tmp_path,
        timeout=120,
    )
    assert r.failed == ["bad"] and r.measures["good"] == pytest.approx(1.5e-9, rel=1e-3)


@pytest.mark.slow
@needs_ngspice
def test_live_concurrent_same_label(tmp_path, monkeypatch):
    monkeypatch.delenv("SPICE_USERINIT_DIR", raising=False)

    def go(rval):
        return run_deck(
            PROBE.replace("1k", rval), label="same", workdir=tmp_path, timeout=120
        ).measures["i_ma"]

    with ThreadPoolExecutor(2) as pool:
        got = list(pool.map(go, ["1k", "2k"]))
    assert got[0] == pytest.approx(1.0) and got[1] == pytest.approx(0.5)


@pytest.mark.slow
@needs_ngspice
def test_live_body_meas_on_stderr(tmp_path, monkeypatch):
    monkeypatch.delenv("SPICE_USERINIT_DIR", raising=False)
    r = run_deck(
        "* body .meas, batch mode\nv1 a 0 pulse(0 1 1n 1n 1n 5n 10n)\nr1 a 0 1k\n"
        ".tran 0.1n 20n\n.meas tran trise when v(a)=0.5 rise=1\n.meas tran bad when v(a)=5\n"
        ".meas tran dly trig v(a) val=0.2 rise=1 targ v(a) val=0.8 rise=1\n.end\n",
        label="body",
        workdir=tmp_path,
        timeout=120,
    )
    assert r.failed == ["bad"] and r.fatal == []
    assert r.measures["trise"] == pytest.approx(1.5e-9, rel=1e-3)
    assert r.measures["dly"] == pytest.approx(0.6e-9, rel=1e-2)
