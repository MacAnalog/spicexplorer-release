"""One xvport check may not silence the others (platform#240).

`--verify` used to raise `FileNotFoundError` on the CDF read filter the installed bridge does
not ship (doc/bridge_limits.md §8) and take the whole command down with it — so `--netcheck`,
the oracle that actually proves the cellview, printed NO LINE, and a caller recording "the
netcheck line, if any" wrote silence down as a looked-at check.

Offline throughout: the bridge client, the loader and every oracle are fakes. Nothing here
touches a live daemon (no Virtuoso is reachable from the test host).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from spicexplorer_netlist2xschem.virtuoso_export import cli as xvcli
from spicexplorer_netlist2xschem.virtuoso_export import endcheck, runner
from spicexplorer_netlist2xschem.virtuoso_export.cli import _missing_verdicts, main
from spicexplorer_netlist2xschem.virtuoso_export.runner import (
    FALLBACK_PARAM_FILTERS,
    VerifyReport,
    _filters_path,
)

FIXTURES = Path(__file__).parent / "fixtures" / "xvport"
SOURCE = FIXTURES / "transmission_gate_pair.sch"


@pytest.fixture
def ported(monkeypatch, tmp_path):
    """`xvport sch2cv --run` against a fake bridge; returns the argv builder."""
    monkeypatch.setattr(runner, "connect", lambda **kw: object())
    monkeypatch.setattr(runner, "load_il", lambda client, path, **kw: None)

    def argv(*extra: str) -> list[str]:
        return [
            "sch2cv",
            str(SOURCE),
            "--lib",
            "LIBX",
            "--cell",
            "tgate",
            "-o",
            str(tmp_path / "tgate.il"),
            "--run",
            *extra,
        ]

    return argv


def _ok_netcheck(*a, **k):
    return endcheck.CheckReport(name="netcheck", ok=True, detail="graph equivalent")


def test_a_verify_that_raises_still_leaves_the_netcheck_run_and_reported(
    ported, monkeypatch, capsys
):
    """#240: the bug, in one command. The missing CDF filter is the real reason it raised."""

    def boom(*a, **k):
        raise FileNotFoundError(2, "No such file or directory", "cdf_param_filters.yaml")

    monkeypatch.setattr(runner, "verify_schematic", boom)
    monkeypatch.setattr(endcheck, "netcheck", _ok_netcheck)

    rc = main(ported("--verify", "--netcheck", "--no-simcheck"))
    out = capsys.readouterr()

    assert "xvport: verify LIBX/tgate: NOT RUN (FileNotFoundError:" in out.err
    assert "xvport: netcheck LIBX/tgate: netcheck OK" in out.out
    assert rc == 2


def test_a_netcheck_that_raises_does_not_silence_the_checks_after_it(ported, monkeypatch, capsys):
    monkeypatch.setattr(
        runner, "verify_schematic", lambda *a, **k: VerifyReport(ok=True, checked_bindings=8)
    )

    def boom(*a, **k):
        raise RuntimeError("read_schematic SKILL error: no such cellview")

    monkeypatch.setattr(endcheck, "netcheck", boom)
    monkeypatch.setattr(
        endcheck,
        "simcheck",
        lambda *a, **k: endcheck.CheckReport(name="simcheck", ok=True, skipped=None),
    )

    rc = main(ported("--verify", "--netcheck", "--simcheck"))
    out = capsys.readouterr()

    assert "xvport: sch LIBX/tgate: verify OK" in out.out
    assert "xvport: netcheck LIBX/tgate: NOT RUN (RuntimeError:" in out.err
    assert "xvport: simcheck LIBX/tgate: simcheck OK" in out.out
    assert rc == 2


def test_a_failing_check_does_not_short_circuit_the_next_one(ported, monkeypatch, capsys):
    """Two failures in a row: the second must still RUN and still print its verdict."""
    monkeypatch.setattr(
        runner,
        "verify_schematic",
        lambda *a, **k: VerifyReport(ok=False, missing_instances=["M1"]),
    )
    monkeypatch.setattr(
        endcheck,
        "netcheck",
        lambda *a, **k: endcheck.CheckReport(name="netcheck", ok=False, detail="not equivalent"),
    )

    rc = main(ported("--verify", "--netcheck", "--no-simcheck"))
    out = capsys.readouterr()

    assert "verify FAILED" in out.out
    assert "xvport: netcheck LIBX/tgate: netcheck FAILED" in out.out
    assert rc == 2


def test_every_requested_check_reports_when_they_all_pass(ported, monkeypatch, capsys):
    monkeypatch.setattr(
        runner, "verify_schematic", lambda *a, **k: VerifyReport(ok=True, checked_bindings=8)
    )
    monkeypatch.setattr(endcheck, "netcheck", _ok_netcheck)

    rc = main(ported("--verify", "--netcheck", "--no-simcheck"))
    out = capsys.readouterr()

    assert "xvport: sch LIBX/tgate: verify OK" in out.out
    assert "xvport: netcheck LIBX/tgate: netcheck OK" in out.out
    assert "NOT RUN" not in out.err and "NO VERDICT LINE" not in out.err
    assert rc == 0


# --- "a requested check that printed no line is a failure" ----------------------------


def test_a_requested_check_that_printed_nothing_is_reported_missing():
    assert _missing_verdicts({"verify", "netcheck"}, {"netcheck"}) == ["verify"]
    assert _missing_verdicts({"verify", "netcheck", "simcheck"}, set()) == [
        "netcheck",
        "simcheck",
        "verify",
    ]
    assert _missing_verdicts({"netcheck"}, {"netcheck"}) == []
    assert _missing_verdicts(set(), {"netcheck"}) == []


def test_a_requested_check_whose_loop_never_ran_fails_the_run(ported, monkeypatch, capsys):
    """The audit's reason for existing: a check requested but never reached at all.

    Simulated by a `run_check` that reports nothing — what the pre-#240 code did whenever an
    earlier check aborted the command. The run must not come back green.
    """
    monkeypatch.setattr(
        runner, "verify_schematic", lambda *a, **k: VerifyReport(ok=True, checked_bindings=8)
    )
    monkeypatch.setattr(endcheck, "netcheck", _ok_netcheck)
    monkeypatch.setattr(xvcli, "_missing_verdicts", lambda requested, emitted: ["netcheck"])

    rc = main(ported("--verify", "--netcheck", "--no-simcheck"))
    out = capsys.readouterr()

    assert "xvport: netcheck: NO VERDICT LINE" in out.err
    assert rc == 2


# --- the CDF read filter the bridge does not package ----------------------------------


def test_the_bridges_own_filter_wins_when_it_is_installed(tmp_path):
    bridge = tmp_path / "bridge.yaml"
    bridge.write_text("fallback: all\n", encoding="utf-8")
    assert _filters_path(bridge) == bridge


def test_our_copy_is_used_when_the_bridge_wheel_left_its_own_behind(tmp_path):
    missing = tmp_path / "not-packaged.yaml"
    assert _filters_path(missing) == FALLBACK_PARAM_FILTERS


def test_no_filter_at_all_reads_everything_rather_than_raising(tmp_path):
    assert _filters_path(tmp_path / "a.yaml", tmp_path / "b.yaml") is None


def test_the_packaged_fallback_filter_is_loadable_and_kit_free():
    assert FALLBACK_PARAM_FILTERS.is_file(), "the fallback filter must ship beside runner.py"
    config = yaml.safe_load(FALLBACK_PARAM_FILTERS.read_text(encoding="utf-8"))
    assert config["fallback"] == "all"
    libs = {rule["match"]["lib"] for rule in config["filters"]}
    # Vendor-neutral by construction: no kit library (and so no kit device flavour) is named
    # in this repo. An unmatched kit device falls through to `fallback: all`.
    assert libs == {"analogLib", "basic"}
