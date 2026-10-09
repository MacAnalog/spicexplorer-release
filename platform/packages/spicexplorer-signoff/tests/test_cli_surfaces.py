"""The knobs an agent reaches through ``run_flow`` and the ``spicexplorer-signoff`` CLI.

DRC density and the kpex halo used to be settable only through the optimizer backend, so an agent
on these surfaces always ran density-off DRC at the tech-file halo; the electromigration check had
no CLI at all. Offline: every runner is monkeypatched where the caller binds it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from spicexplorer_signoff import (
    Budget,
    DrcResult,
    LvsResult,
    PexResult,
    budgets_from_brief,
    check_current_density,
    run_flow,
)
from spicexplorer_signoff.cli import main


def _budgets(tmp_path: Path, rows: Any) -> Path:
    f = tmp_path / "budgets.json"
    f.write_text(json.dumps(rows))
    return f


# --- current-density --budgets ------------------------------------------------------------------


def test_cli_current_density_exits_1_on_an_over_limit_budget(tmp_path, capsys):
    """10 mA on 0.5 um Metal1: the limit is 1 mA/um x 0.5 um = 0.5 mA, so 20x over."""
    f = _budgets(
        tmp_path,
        [{"net": "vout", "current_a": 10e-3, "layer": "Metal1", "width_um": 0.5, "note": "load"}],
    )
    rc = main(["--pdk", "ihp-sg13g2", "current-density", "--budgets", str(f)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["available"] and not out["passed"] and out["n_violations"] == 1
    v = out["violations"][0]
    assert v["net"] == "vout" and v["note"] == "load"
    assert v["over_factor"] == pytest.approx(20.0)
    assert v["limit_a"] == pytest.approx(0.5e-3)


def test_cli_current_density_exits_0_when_the_budget_fits(tmp_path, capsys):
    f = _budgets(
        tmp_path,
        [
            {"net": "vout", "current_a": 10e-3, "layer": "TopMetal1", "width_um": 2.0},
            {"net": "vout", "current_a": 10e-3, "layer": "Via1", "n_vias": 25},
        ],
    )
    rc = main(["--pdk", "ihp-sg13g2", "current-density", "--budgets", str(f)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["passed"] and out["n_checked"] == 2 and out["violations"] == []


def test_cli_current_density_tech_overrides_the_global_pdk(tmp_path, capsys):
    """`--tech` names the process the limits come from; without it the global `--pdk` does."""
    f = _budgets(tmp_path, [{"net": "vout", "current_a": 1e-3, "layer": "Metal1", "width_um": 2.0}])
    rc = main(["--pdk", "no-such-pdk", "current-density", "--budgets", str(f)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1 and not out["available"] and "no-such-pdk" in out["reason"]
    rc = main(
        ["--pdk", "no-such-pdk", "current-density", "--budgets", str(f), "--tech", "ihp-sg13g2"]
    )
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["passed"] and out["pdk"] == "ihp-sg13g2"


def test_cli_current_density_accepts_a_budgets_object(tmp_path, capsys):
    """`{"budgets": [...]}` is the same file as the bare list, so a report can carry other keys."""
    f = _budgets(
        tmp_path,
        {"budgets": [{"net": "vdd", "current_a": 1e-3, "layer": "Metal1", "width_um": 2.0}]},
    )
    assert main(["--pdk", "ihp-sg13g2", "current-density", "--budgets", str(f)]) == 0
    assert json.loads(capsys.readouterr().out)["n_checked"] == 1


@pytest.mark.parametrize(
    "rows",
    [
        [{"net": "vout", "current_a": 1e-3, "layer": "Metal1", "widht_um": 2.0}],  # typo'd key
        [{"net": "vout", "layer": "Metal1", "width_um": 2.0}],  # no current
        [],  # nothing to check is not a pass
        {"rows": []},
        # valid JSON, wrong types: each used to crash inside the check (exit 1, no JSON) or ride
        # through into the verdict unvalidated
        [{"net": "x", "current_a": "0.01", "layer": "Metal1", "width_um": 0.5}],
        [{"net": "x", "current_a": 0.01, "layer": "Metal1", "width_um": None}],
        [{"net": "x", "current_a": True, "layer": "Metal1", "width_um": 2.0}],
        [{"net": "x", "current_a": 0.01, "layer": "Via1", "n_vias": "4"}],
        [{"net": "x", "current_a": 0.01, "layer": "Via1", "n_vias": 2.5}],
        [{"net": "x", "current_a": 0.01, "layer": 5, "width_um": 0.5}],
        [{"net": None, "current_a": 0.01, "layer": "Metal1", "width_um": 2.0}],
    ],
)
def test_cli_current_density_rejects_a_malformed_budgets_file(tmp_path, capsys, rows):
    f = _budgets(tmp_path, rows)
    with pytest.raises(SystemExit) as exc:
        main(["--pdk", "ihp-sg13g2", "current-density", "--budgets", str(f)])
    assert exc.value.code == 2
    assert "--budgets" in capsys.readouterr().err


# --- pex --halo ---------------------------------------------------------------------------------


def _fake_run_pex(calls: list[dict[str, Any]]):
    def fake(gds, cell, schematic, out_dir, **kw):
        calls.append(kw)
        return PexResult(True, True, kw.get("mode", "CC"))

    return fake


def test_cli_pex_forwards_the_halo(tmp_path, monkeypatch, capsys):
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr("spicexplorer_signoff.cli.run_pex", _fake_run_pex(calls))
    args = ["pex", "top.gds", "--cell", "c", "--netlist", "c.sp", "--out-dir", str(tmp_path)]
    assert main([*args, "--halo", "20"]) == 0
    assert main(args) == 0
    capsys.readouterr()
    assert calls[0]["halo_um"] == pytest.approx(20.0)
    assert calls[1]["halo_um"] is None  # no flag = the tech file's own halo, as before


# --- run_flow ------------------------------------------------------------------------------------


@pytest.fixture
def flow_calls(tmp_path, monkeypatch) -> dict[str, list[dict[str, Any]]]:
    """DRC and LVS pass, PEX succeeds; every call's keyword arguments are recorded."""
    calls: dict[str, list[dict[str, Any]]] = {"drc": [], "lvs": [], "pex": []}

    def drc(gds, cell, run_dir, **kw):
        calls["drc"].append(kw)
        return DrcResult(True, True)

    def lvs(gds, netlist, cell, run_dir, **kw):
        calls["lvs"].append(kw)
        return LvsResult(True, True, matched=True)

    monkeypatch.setattr("spicexplorer_signoff.flow.run_drc", drc)
    monkeypatch.setattr("spicexplorer_signoff.flow.run_lvs", lvs)
    monkeypatch.setattr("spicexplorer_signoff.flow.run_pex", _fake_run_pex(calls["pex"]))
    return calls


def _flow(tmp_path: Path, **kw: Any):
    gds = tmp_path / "top.gds"
    gds.write_bytes(b"")
    return run_flow(lambda _p: gds, {}, netlist=tmp_path / "c.sp", cell="c", run_dir=tmp_path, **kw)


def test_run_flow_forwards_no_density(tmp_path, flow_calls):
    assert _flow(tmp_path, no_density=False).ok
    assert _flow(tmp_path).ok
    assert flow_calls["drc"][0]["no_density"] is False
    assert flow_calls["drc"][1]["no_density"] is True  # the default stays run_drc's own


def test_run_flow_forwards_the_halo(tmp_path, flow_calls):
    assert _flow(tmp_path, halo_um=20.0, pex_mode="RC").ok
    assert _flow(tmp_path).ok
    assert flow_calls["pex"][0]["halo_um"] == pytest.approx(20.0)
    assert flow_calls["pex"][0]["mode"] == "RC"
    assert flow_calls["pex"][1]["halo_um"] is None


# --- budgets_from_brief -------------------------------------------------------------------------

BRIEF = {
    "cell": "ldo",
    "currents": [
        {"net": "vout", "i_ma": 10.0, "i_rms_ma": 10.2, "kind": "dc", "what": "load path"},
        {"net": "vdd", "i_ma": 10.5, "kind": "dc"},
        {"net": "vbias", "i_ma": 0.05, "kind": "dc"},
    ],
}


def test_budgets_from_brief_maps_i_ma_to_current_a():
    rows = budgets_from_brief(
        BRIEF,
        {
            "vout": ("Metal1", 0.5, 1),
            "vdd": [("TopMetal1", 4.0, 1), ("TopVia1", 0.0, 8)],  # 1.4 mA/cut
            "vbias": ("Metal1", 0.2, 1),
        },
    )
    by = {(b.net, b.layer): b for b in rows}
    assert len(rows) == 4
    assert by[("vout", "Metal1")].current_a == pytest.approx(10e-3)
    assert by[("vout", "Metal1")].width_um == 0.5
    assert by[("vdd", "TopVia1")].n_vias == 8
    assert by[("vdd", "TopMetal1")].current_a == pytest.approx(10.5e-3)
    assert "load path" in by[("vout", "Metal1")].note
    res = check_current_density(rows, tech="ihp-sg13g2")
    assert not res.passed and [v.net for v in res.violations] == ["vout"]
    assert res.violations[0].over_factor == pytest.approx(20.0)


def test_budgets_from_brief_reads_a_brief_file_and_json_shaped_conductors(tmp_path):
    """`drawn` read from JSON has lists, not tuples; a 2-long conductor is one cut."""
    f = tmp_path / "brief.json"
    f.write_text(json.dumps(BRIEF))
    drawn = {"vout": ["Metal1", 12.0], "vdd": [["Metal2", 6.0, 1]], "vbias": ["Metal1", 0.2]}
    rows = budgets_from_brief(f, drawn)
    assert [(b.net, b.layer, b.width_um, b.n_vias) for b in rows] == [
        ("vout", "Metal1", 12.0, 1),
        ("vdd", "Metal2", 6.0, 1),
        ("vbias", "Metal1", 0.2, 1),
    ]
    assert all(isinstance(b, Budget) for b in rows)
    assert check_current_density(rows, tech="ihp-sg13g2").passed


def test_budgets_from_brief_a_net_with_no_drawn_conductor_fails_the_check():
    """A brief current nobody measured the metal for is a check that did not run, not a pass."""
    rows = budgets_from_brief(BRIEF, {"vout": ("TopMetal1", 2.0, 1), "vdd": ("TopMetal1", 2.0, 1)})
    res = check_current_density(rows, tech="ihp-sg13g2")
    assert not res.passed and res.n_violations == 0
    assert "vbias" in res.reason and "drawn" in res.reason


def test_a_budget_on_no_conductor_is_reported_as_not_drawn():
    """A brief net `drawn` leaves out becomes a Budget with layer=''. Its reason used to read
    "unknown layer '' for ihp-sg13g2 — not in the tech config's `em_limits:`", which sends the
    reader to the tech file instead of the layout (L-PF-23)."""
    rows = budgets_from_brief(BRIEF, {"vout": ("TopMetal1", 2.0, 1), "vdd": ("TopMetal1", 2.0, 1)})
    res = check_current_density(rows, tech="ihp-sg13g2")
    assert not res.passed and res.n_checked == 2
    assert "vbias: not drawn" in res.reason and "unknown layer" not in res.reason
    assert "not drawn" in check_current_density([Budget("x", 1e-3, " ")], tech="ihp-sg13g2").reason


def test_budgets_from_brief_rejects_a_drawn_net_the_brief_has_no_current_for():
    with pytest.raises(KeyError, match="vdd_typo"):
        budgets_from_brief(BRIEF, {"vdd_typo": ("Metal1", 1.0, 1)})


@pytest.mark.parametrize("brief", [{"cell": "ldo"}, {"currents": []}, {"currents": None}])
def test_budgets_from_brief_refuses_a_brief_with_no_currents(brief):
    """No `currents` block is a check with nothing to check, not the pass it would score as."""
    with pytest.raises(ValueError, match="currents"):
        budgets_from_brief(brief, {})


@pytest.mark.parametrize(
    "currents",
    [
        {"vdd": {"i_ma": 1.0}},  # keyed by net: list() would read only the keys
        {"net": "vdd", "i_ma": 1.0},  # one row, not wrapped in a list
        "vdd",
        ["vdd"],  # a list of net names, not rows
    ],
)
def test_budgets_from_brief_refuses_currents_that_are_not_a_list_of_rows(currents):
    """L-PF-21: a malformed `currents` block is a named TypeError, not an AttributeError."""
    with pytest.raises(TypeError, match="currents"):
        budgets_from_brief({"currents": currents}, {})


@pytest.mark.parametrize("i_ma", ["ten", "5", None, True, [1.0]])
def test_budgets_from_brief_refuses_an_i_ma_that_is_not_a_number(i_ma):
    """L-PF-21: `i_ma` must be a number (mA); the error names the net and the field."""
    with pytest.raises(TypeError, match=r"vdd.*i_ma"):
        budgets_from_brief({"currents": [{"net": "vdd", "i_ma": i_ma}]}, {})
