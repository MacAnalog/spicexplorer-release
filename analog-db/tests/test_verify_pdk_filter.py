"""``analog-db verify --pdk`` is a DISPLAY filter — it must never change the VERDICT.

Regression for the defect where ``--pdk`` dropped every row whose ``check`` string does not
name a PDK. Circuit-WIDE checks (``schema:circuit``, ``xref:class_exists``, …) name none, so a
failing one was filtered away and the run exited **0** on exactly the result set that exits **1**
unfiltered. Reproduced on ldo_001_analoggym_basic with an illegal key in ``circuit.yaml``:
no ``--pdk`` → ``schema:circuit`` FAIL, exit 1; ``--pdk sky130`` → "3 passed, 0 failed", exit 0.
"""

from __future__ import annotations

import argparse
import json

import pytest

from spicexplorer_analog_db import cli, verify

# One circuit-wide failure (no PDK in the check name) + one PDK-scoped pass + one DB-level row.
_ROWS = [
    verify.CheckResult("ldo_synthetic", 0, "schema:circuit", "fail", "synthetic circuit-wide fail"),
    verify.CheckResult("ldo_synthetic", 0, "schema:sizing:sky130", "pass"),
    verify.CheckResult("", 0, "db:catalog", "pass"),
]

# The same set plus a failure scoped to ANOTHER PDK. That row survives `--pdk sky130` (a failure is
# never hidden), so every view has to say it is out of scope — otherwise a per-PDK matrix built from
# `verify --pdk sky130 --json` charges gf180mcu's failure to sky130.
_ROWS_OTHER_PDK = _ROWS + [
    verify.CheckResult("ldo_synthetic", 0, "schema:sizing:gf180mcu", "fail", "other-PDK fail"),
]


@pytest.fixture
def stub_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(verify, "run", lambda **_kw: list(_ROWS))


@pytest.fixture
def stub_run_other_pdk(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(verify, "run", lambda **_kw: list(_ROWS_OTHER_PDK))


def _args(pdk: str | None, as_json: bool = False) -> argparse.Namespace:
    return argparse.Namespace(circuit="ldo_synthetic", tier=[0], pdk=pdk, json=as_json, sim=False)


@pytest.mark.parametrize("pdk", [None, "sky130", "ihp-sg13g2"])
def test_pdk_filter_never_flips_the_exit_code(stub_run, pdk) -> None:
    """Same result set, three views: a circuit-wide FAIL always exits 1."""
    assert cli._cmd_verify(_args(pdk)) == 1


@pytest.mark.parametrize("pdk", [None, "sky130", "ihp-sg13g2"])
def test_failing_rows_are_never_hidden(stub_run, pdk, capsys) -> None:
    """A failure is never noise: every view lists it, so exit 1 is explainable."""
    cli._cmd_verify(_args(pdk))
    out = capsys.readouterr().out
    assert "schema:circuit" in out
    assert "0 failed" not in out


@pytest.mark.parametrize("pdk", [None, "sky130", "ihp-sg13g2"])
def test_json_view_carries_the_failure(stub_run, pdk, capsys) -> None:
    cli._cmd_verify(_args(pdk, as_json=True))
    rows = json.loads(capsys.readouterr().out)
    assert any(r["check"] == "schema:circuit" and r["status"] == "fail" for r in rows)


def test_derived_status_is_not_laundered_by_the_filter(stub_run, capsys) -> None:
    """``status[…]`` is derived from the rows; the filter must not raise it."""
    cli._cmd_verify(_args("sky130"))
    assert "status[ldo_synthetic] = draft" in capsys.readouterr().out


def test_pdk_filter_still_narrows_the_passing_view(stub_run, capsys) -> None:
    """The filter keeps doing its job: an out-of-scope PASS is still hidden."""
    cli._cmd_verify(_args("ihp-sg13g2"))
    assert "schema:sizing:sky130" not in capsys.readouterr().out


# --------------------------------------------------------------------------- scope marker
# `--pdk` narrows the listing but never hides a failure, so an out-of-scope FAIL is emitted under
# `--pdk X`. It must be MARKED as such, or a machine consumer silently absorbs it.

_SCOPE = {
    "schema:circuit": "any",  # circuit-wide — holds for every PDK
    "schema:sizing:sky130": "requested",  # the PDK asked for
    "db:catalog": "any",  # DB-level
    "schema:sizing:gf180mcu": "other",  # a DIFFERENT PDK
}


def test_json_rows_carry_the_pdk_scope_marker(stub_run_other_pdk, capsys) -> None:
    cli._cmd_verify(_args("sky130", as_json=True))
    rows = json.loads(capsys.readouterr().out)
    assert {r["check"]: r.get("pdk_scope") for r in rows} == _SCOPE


def test_out_of_scope_failure_is_not_charged_to_the_requested_pdk(
    stub_run_other_pdk, capsys
) -> None:
    """The marker is what lets a per-PDK matrix drop another PDK's failure."""
    cli._cmd_verify(_args("sky130", as_json=True))
    rows = json.loads(capsys.readouterr().out)
    in_scope = [r for r in rows if r.get("pdk_scope") != "other"]
    assert [r["check"] for r in in_scope] == [
        "schema:circuit",
        "schema:sizing:sky130",
        "db:catalog",
    ]
    assert [r["check"] for r in in_scope if r["status"] == "fail"] == ["schema:circuit"]


def test_json_without_pdk_carries_no_scope_key(stub_run_other_pdk, capsys) -> None:
    """No `--pdk`, no scope: nothing is out of scope, so the row schema is unchanged."""
    cli._cmd_verify(_args(None, as_json=True))
    rows = json.loads(capsys.readouterr().out)
    assert all("pdk_scope" not in r for r in rows)


def test_text_listing_marks_the_out_of_scope_failure(stub_run_other_pdk, capsys) -> None:
    cli._cmd_verify(_args("sky130"))
    lines = capsys.readouterr().out.splitlines()

    def row(check: str) -> str:
        return next(ln for ln in lines if f":: {check}" in ln)

    assert "(out of scope for --pdk sky130)" in row("schema:sizing:gf180mcu")
    assert "out of scope" not in row("schema:circuit")
