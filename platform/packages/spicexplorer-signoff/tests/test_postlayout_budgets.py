"""Per-net extracted C against the layout brief's three capacitance budgets.

The brief states, per net, a balanced budget (C to AC ground), a one-sided budget (the
difference between the two halves of a pair) and a differential budget (C drawn directly between
the halves). ``score_c_budgets`` splits an extracted netlist the same way; the sums are checked
here against :func:`summarize_parasitics` on the same netlist, so the table a reviewer writes and
the per-net C a PEX verdict carries cannot drift apart.
"""

from __future__ import annotations

import json

import pytest
from spicexplorer_signoff.pex import summarize_parasitics
from spicexplorer_signoff.postlayout import c_budget_table, score_c_budgets

PEX = r"""* synthetic extracted netlist
.subckt amp inp inn outp outn tail vdd vss vb
M1 outp inp tail vss nmos w=1u l=0.1u
M2 outn inn tail vss nmos w=1u l=0.1u
Cext_1 inp vss 10f
Cext_2 inp inn 2f
Cext_3 inp outp 1.5f
Cext_4 inn vss 7f
Cext_5 inn \$12 500a
Cext_6 outp vsubs 3f
Cext_7 outn vsubs 3.4f
Cext_8 outp outn 0.25f
Cext_9 tail 0 20f
Cext_10 vss vss 5f
Cext_11 inp inp 4f
Cext_12 vdd vss 30f
Cext_13 vb vss 2f
CDESIGN_1 outp outn 50f
Rext_1 outp outn 1meg
.ends amp
"""

BRIEF = {
    "cell": "amp",
    "nets": [
        {
            "name": "inp",
            "twin": "inn",
            "budget_c_ff": 15.0,
            "budget_c_asym_ff": 2.0,
            "budget_c_diff_ff": 1.0,
        },
        # no `twin` key: the pair comes from structure.mirror_pairs (the agent-doc schema)
        {"name": "outp", "budget_c_ff": 3.5, "budget_c_asym_ff": 1.2, "budget_c_diff_ff": 1.0},
        {"name": "tail", "twin": None, "budget_c_ff": 50.0},
        {"name": "vdd", "budget_c_ff": 1.0},  # over, but a don't-care: shown, never scored
        {"name": "vb"},  # no budget at all
        {"name": "ghost", "budget_c_ff": 5.0},  # renamed / absent from the extraction
    ],
    "structure": {"mirror_pairs": [["outp", "outn"]]},
    "dont_care": {"capacitance": ["vdd"], "leakage": "every node"},
}


def _rows(**kw):
    return {r["net"]: r for r in score_c_budgets(PEX, BRIEF, **kw)}


def test_balanced_one_sided_and_differential_columns():
    r = _rows(exclude=r"cdesign")["inp"]
    # balanced: every partner but the twin (ground 10 fF + the 1.5 fF to outp); self-loop skipped
    assert r["twin"] == "inn"
    assert r["bal_ff"] == pytest.approx(11.5)
    assert r["bal_twin_ff"] == pytest.approx(7.5)  # 7 fF to ground + 0.5 fF to an internal net
    assert r["asym_ff"] == pytest.approx(4.0)
    assert r["diff_ff"] == pytest.approx(2.0)
    assert (r["bal_ok"], r["asym_ok"], r["diff_ok"]) == (True, False, False)
    assert r["found"] and not r["dont_care"]


def test_twin_from_mirror_pairs_and_the_design_capacitor_exclusion():
    """The 50 fF bridging capacitor between the halves is a DESIGN device, not a parasitic: the
    caller names it by card-name pattern (any case), and it leaves the differential column."""
    kept = _rows()["outp"]
    assert kept["twin"] == "outn"
    assert kept["diff_ff"] == pytest.approx(50.25) and kept["diff_ok"] is False
    r = _rows(exclude=[r"cdesign_\d+"])["outp"]
    assert r["diff_ff"] == pytest.approx(0.25) and r["diff_ok"] is True
    assert r["bal_ff"] == pytest.approx(4.5) and r["bal_ok"] is False
    assert r["asym_ff"] == pytest.approx(1.1) and r["asym_ok"] is True


def test_a_net_without_a_twin_has_no_one_sided_or_differential_value():
    r = _rows()["tail"]
    assert r["bal_ff"] == pytest.approx(20.0) and r["bal_ok"] is True
    assert r["twin"] is None
    assert r["asym_ff"] is None and r["diff_ff"] is None and r["bal_twin_ff"] is None
    assert r["asym_ok"] is None and r["diff_ok"] is None


def test_dont_care_and_unbudgeted_nets_are_shown_not_scored():
    rows = _rows()
    vdd, vb = rows["vdd"], rows["vb"]
    assert vdd["dont_care"] and vdd["bal_ff"] == pytest.approx(30.0)
    # over its number, and still no verdict
    assert vdd["budget_bal_ff"] == 1.0 and vdd["bal_ok"] is None
    assert not vb["dont_care"] and vb["bal_ff"] == pytest.approx(2.0)
    assert vb["budget_bal_ff"] is None and vb["bal_ok"] is None


def test_dont_care_as_a_plain_list():
    """The agent-doc schema writes `dont_care` as a list of names."""
    brief = {**BRIEF, "dont_care": ["tail"]}
    rows = {r["net"]: r for r in score_c_budgets(PEX, brief)}
    assert rows["tail"]["dont_care"] and rows["tail"]["bal_ok"] is None
    assert not rows["vdd"]["dont_care"] and rows["vdd"]["bal_ok"] is False


def test_a_budgeted_net_missing_from_the_extraction_is_not_a_pass():
    """A renamed net would otherwise sum to 0 fF and pass every budget it has."""
    r = _rows()["ghost"]
    assert not r["found"]
    assert r["bal_ff"] is None and r["bal_ok"] is None


def test_sums_reconcile_with_summarize_parasitics(tmp_path):
    f = tmp_path / "amp_pex.spice"
    f.write_text(PEX)
    _, _, per_net, coupling = summarize_parasitics(f)
    rows = score_c_budgets(f, BRIEF)  # a path works as well as the text
    checked = 0
    for r in rows:
        if not r["found"]:
            assert r["net"] not in per_net
            continue
        assert r["bal_ff"] + (r["diff_ff"] or 0.0) == pytest.approx(per_net[r["net"]])
        if r["twin"]:
            key = "|".join(sorted((r["net"], r["twin"])))
            assert r["diff_ff"] == pytest.approx(coupling[key])
            assert r["bal_twin_ff"] + r["diff_ff"] == pytest.approx(per_net[r["twin"]])
        checked += 1
    assert checked == 5


def test_brief_from_a_file(tmp_path):
    f = tmp_path / "brief.json"
    f.write_text(json.dumps(BRIEF))
    assert score_c_budgets(PEX, f) == score_c_budgets(PEX, BRIEF)


def test_table_names_every_verdict():
    md = c_budget_table(score_c_budgets(PEX, BRIEF, exclude=r"cdesign"))
    lines = md.splitlines()
    assert lines[0].startswith("| net | twin | balanced C")
    assert len(lines) == 2 + len(BRIEF["nets"])
    by = {ln.split("|")[1].strip(" `"): ln for ln in lines[2:]}
    assert "OVER" in by["inp"] and "ok" in by["inp"]
    assert "don't care" in by["vdd"] and "OVER" not in by["vdd"]
    assert "no bound" in by["vb"]
    assert "not in extraction" in by["ghost"] and " ok" not in by["ghost"]
    assert "11.50" in by["inp"] and "4.00" in by["inp"]
