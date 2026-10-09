"""One bad measure must fail ONE metric — never wipe its siblings, never break strict JSON.

The wider `sim_log` parser reads what the retired analog-db regexes dropped: ngspice's
`meas … failed!` report, and literal `inf`/`nan` from an overflowing `let`. That is more honest,
but it put three things in reach at once, all fixed together and pinned here:

* **F2** `run_text` raised `SimError` on the FIRST NaN. `run_circuit` turns that into
  `status: sim_error`, and `ppa.metric_values` skips a non-`ok` analysis outright — so every
  sibling metric of that analysis vanished from the scorecard. Absence scores more leniently than
  failure (the same defect family as `_shared/MEASUREMENT_PITFALLS.md` cases 1-3), so a dead
  metric could *improve* a cell's apparent record.
* **F7** `verify._sim_cell` never applied the `failed → NaN` substitution, so Tier-3/4 kept
  ngspice's `-999` sentinel as a real measure (`isfinite(-999)` is True) and scored it against the
  datasheet, while the scoreboard lane recorded NaN for the very same deck.
* **F3** `json.dumps` defaults to `allow_nan=True` and writes bare `NaN`/`Infinity`, which is not
  valid JSON — a strict reader cannot load the entry at all.
"""

from __future__ import annotations

import json
import math

import pytest

from spicexplorer_analog_db import runner, scoreboard, verify


def _log(*lines: str) -> str:
    return "".join(ln + "\n" for ln in lines)


# ───────────────────────────── F2: run_text keeps the siblings ─────────────────────────────


def test_one_nan_measure_does_not_wipe_its_siblings() -> None:
    """The review's own probe: `let bad = ln(0) - ln(0)` beside a good measure."""
    log = _log("good = 2.5", "bad = -nan")
    out = runner.run_text("deck", "<t>", runner=lambda _n: log)
    assert out["good"] == 2.5, "the good measure must survive a NaN sibling"
    assert math.isnan(out["bad"]), "the bad measure is kept as NaN so metric_values fails it"


def test_failed_meas_sentinel_becomes_nan_not_a_real_value() -> None:
    """ngspice prints BOTH `-999` and `… failed!`; the sentinel must not score as a measurement."""
    log = _log("gm = -9.99000e+02", "meas ac gm find ngdb when ph=0 cross=1 failed!", "pm = 61.4")
    out = runner.run_text("deck", "<t>", runner=lambda _n: log)
    assert math.isnan(out["gm"]) and out["pm"] == 61.4


def test_run_text_raises_only_when_nothing_finite_survives() -> None:
    log = _log("a = nan", "b = -nan", "meas tran c when v(x)=1 failed!")
    with pytest.raises(runner.SimError, match="no finite measure"):
        runner.run_text("deck", "<t>", runner=lambda _n: log)


def test_run_text_still_raises_with_no_parseable_measure() -> None:
    with pytest.raises(runner.SimError, match="no measures parsed"):
        runner.run_text("deck", "<t>", runner=lambda _n: _log("ngspice chatter", "nothing here"))


# ───────────────────────────── F7: both lanes agree on one deck ─────────────────────────────


def test_sim_cell_and_run_text_agree_on_a_failed_meas(monkeypatch: pytest.MonkeyPatch) -> None:
    """The SAME failing deck must not be a `-999` pass in Tier-3/4 and a NaN in the scoreboard."""
    log = _log("gm = -9.99000e+02", "meas ac gm find ngdb when ph=0 cross=1 failed!", "pm = 61.4")

    monkeypatch.setattr(verify, "_T3_LOAD_FAIL", __import__("re").compile(r"(?!x)x"))
    from spicexplorer_analog_db import model

    circuit = model.load_circuit("amp_001_5t")
    monkeypatch.setattr(verify, "assemble", lambda *a, **k: "deck", raising=False)
    status, _reason, meas = verify._sim_cell(circuit, "ac_open_loop", "ihp-sg13g2", lambda _n: log)

    assert status == "pass" and meas["pm"] == 61.4
    assert math.isnan(meas["gm"]), "Tier-3/4 must not keep -999 as a real measure (lane parity)"
    assert math.isnan(runner.run_text("deck", "<t>", runner=lambda _n: log)["gm"])


# ───────────────────────────── F3: entries stay strict JSON ─────────────────────────────


def test_recorded_analyses_are_strict_json() -> None:
    """Non-finite measures are stored as ``null`` — which `metric_values` already scores `fail`."""
    analyses = {
        "ac": {"status": "ok", "measures": {"good": 2.5, "bad": float("nan"), "big": float("inf")}},
        "op": {"status": "ok", "measures": {"vout": 1.2}},
    }
    safe = scoreboard._json_safe_analyses(analyses)
    assert safe["ac"]["measures"] == {"good": 2.5, "bad": None, "big": None}
    assert safe["op"]["measures"] == {"vout": 1.2}
    # the point of the exercise: strict JSON, no bare NaN/Infinity tokens
    json.dumps(safe, allow_nan=False)
    assert analyses["ac"]["measures"]["bad"] != analyses["ac"]["measures"]["bad"], "input untouched"


# ───────────────────────────── T4 crash site ─────────────────────────────


# The sim=True branch needs no PDK: one installed PDK is stubbed and the Tier-3 sweep is passed in
# as a synthetic `cache` ({circuit: {(analysis, pdk): (status, reason, measures)}}). With
# `sim=False` both tiers return their opt-in skip before any of the code below runs.
_PDK = "ihp-sg13g2"


def _one_pdk_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "native_pdk_available", lambda pdk: pdk == _PDK)


def _clean_cells(cid: str, measures: dict[str, float]) -> dict:
    from spicexplorer_analog_db import model

    c = model.load_circuit(cid)
    enabled = [a for a in c.analyses if c.analysis(a).get("enabled", True)]
    return {cid: {(aid, _PDK): ("pass", "", dict(measures)) for aid in enabled}}


def _inside(spec: dict) -> float:
    """A value strictly inside a datasheet spec band."""
    lo, hi = verify._numeric_bound(spec.get("min")), verify._numeric_bound(spec.get("max"))
    if lo is not None and hi is not None:
        return (lo + hi) / 2
    if lo is not None:
        return lo + abs(lo) + 1.0
    assert hi is not None, spec
    return hi / 2


def test_tier4_renders_a_missing_value_instead_of_crashing(monkeypatch: pytest.MonkeyPatch) -> None:
    """`ppa.metric_values` returns `{value: None, spec: fail}` for a clean run with no measure;
    Tier-4's skip-reason used to `f"{val:.4g}"` that None and die with a TypeError mid-sweep.

    PRE-EXISTING (identical on `main` for `amp_031_srmc_core_cmfb` and `cmfb_002_5t_pmos_input`),
    not introduced by the parser swap — but it aborts the whole corpus sweep, so it is fixed here.
    Driven through the sim=True branch (audit DATA-D10: a sim=False call never reached it).
    """
    cid = "amp_031_srmc_core_cmfb"
    _one_pdk_installed(monkeypatch)
    results = verify.run_tier4([cid], sim=True, cache=_clean_cells(cid, {}))
    rows = {r.check: r for r in results}
    row = rows[f"conform:dc_gain_db@{_PDK}"]
    assert row.status == "skip" and row.reason.startswith("dc_gain_db=n/a outside spec >= 50 dB")
    assert all(r.check.endswith(f"@{_PDK}") for r in results), "only the installed PDK is scored"


def test_tier3_and_tier4_sim_branch_reach_validated_only_when_every_row_passes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The ladder's top rungs from the sim=True path: every spec-bounded metric in spec →
    ``validated``; ONE metric out of spec is a Tier-4 skip, so the circuit stops at ``simulated``."""
    from spicexplorer_analog_db import model

    cid = "amp_001_5t"
    _one_pdk_installed(monkeypatch)
    metrics = model.load_circuit(cid).datasheet()["metrics"]
    bounded = {n: s for n, s in metrics.items() if verify._has_spec_bound(s.get("spec"))}
    good = {s["extract"]["meas"]: _inside(s["spec"]) for s in bounded.values()}
    pdk_free = verify.run([0, 1, 2], [cid])
    assert verify.derive_status(cid, pdk_free) == "generated"

    cache = _clean_cells(cid, good)
    t3 = verify.run_tier3([cid], sim=True, cache=cache)
    assert {r.status for r in t3 if r.check.endswith(f"@{_PDK}/tt")} == {"pass"}
    assert {r.status for r in t3 if f"@{_PDK}" not in r.check} == {"skip"}  # PDK not installed
    t4 = verify.run_tier4([cid], sim=True, cache=cache)
    assert len(t4) == len(bounded) and {r.status for r in t4} == {"pass"}
    assert verify.derive_status(cid, pdk_free + t3 + t4) == "validated"

    for cell in cache[cid].values():
        cell[2]["pm"] = 10.0  # pm_deg: [60, 90] deg
    t4 = verify.run_tier4([cid], sim=True, cache=cache)
    skipped = [r for r in t4 if r.status == "skip"]
    assert [r.check for r in skipped] == [f"conform:pm_deg@{_PDK}"]
    assert "pm_deg=10 outside spec [60.0, 90] deg" in skipped[0].reason
    assert verify.derive_status(cid, pdk_free + t3 + t4) == "simulated"


# The sim=True branch's other exits (audit DATA-D10: none was reached by any test). PDK-free rows
# for T0-T2 are synthetic: `derive_status` reads only the rows it is handed.


def _pdk_free(cid: str) -> list[verify.CheckResult]:
    return [verify.CheckResult(cid, t, f"synthetic:t{t}", "pass") for t in (0, 1, 2)]


def test_sim_branch_with_no_installed_pdk_skips_every_row_and_stops_at_generated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from spicexplorer_analog_db import model

    cid = "amp_001_5t"
    c = model.load_circuit(cid)
    monkeypatch.setattr(runner, "native_pdk_available", lambda pdk: False)
    t3 = verify.run_tier3([cid], sim=True, cache={})
    assert t3 and {r.check.rsplit("@", 1)[1] for r in t3} == set(c.pdks)
    for r in t3:
        pdk = r.check.rsplit("@", 1)[1]
        assert (r.status, r.reason) == ("skip", f"PDK {pdk} not installed under $PDK_ROOT"), r
    t4 = verify.run_tier4([cid], sim=True, cache={})
    assert [(r.check, r.status, r.reason) for r in t4] == [
        ("conform", "skip", "no installed PDK to simulate against")
    ]
    assert verify.derive_status(cid, _pdk_free(cid) + t3 + t4) == "generated"


def test_sim_branch_with_no_cell_for_the_circuit_skips_and_stops_at_generated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The installed PDK was never simulated (the circuit is absent from the cache)."""
    cid = "amp_001_5t"
    _one_pdk_installed(monkeypatch)
    t3 = verify.run_tier3([cid], sim=True, cache={})
    mine = [r for r in t3 if r.check.endswith(f"@{_PDK}/tt")]
    assert mine and {(r.status, r.reason) for r in mine} == {("skip", "cell not simulated")}
    t4 = verify.run_tier4([cid], sim=True, cache={})
    assert t4 and all(r.status == "skip" and r.reason.startswith("no clean measure") for r in t4)
    assert verify.derive_status(cid, _pdk_free(cid) + t3 + t4) == "generated"


def test_a_failed_sim_cell_is_a_tier3_fail_and_no_tier4_measure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Tier-3 ``fail`` is a ``sim_error`` analysis to Tier-4: its measures are not scored, even
    ones that would sit inside the spec band."""
    from spicexplorer_analog_db import model

    cid = "amp_001_5t"
    _one_pdk_installed(monkeypatch)
    metrics = model.load_circuit(cid).datasheet()["metrics"]
    bounded = {n: s for n, s in metrics.items() if verify._has_spec_bound(s.get("spec"))}
    good = {s["extract"]["meas"]: _inside(s["spec"]) for s in bounded.values()}
    cache = _clean_cells(cid, good)
    cache[cid] = {key: ("fail", "ngspice aborted", m) for key, (_st, _r, m) in cache[cid].items()}
    t3 = verify.run_tier3([cid], sim=True, cache=cache)
    mine = [r for r in t3 if r.check.endswith(f"@{_PDK}/tt")]
    assert mine and {(r.status, r.reason) for r in mine} == {("fail", "ngspice aborted")}
    t4 = verify.run_tier4([cid], sim=True, cache=cache)
    assert len(t4) == len(bounded)
    assert all(r.status == "skip" and r.reason.startswith("no clean measure") for r in t4)
    assert verify.derive_status(cid, _pdk_free(cid) + t3 + t4) == "generated"


def test_sim_branch_skips_a_reference_circuit_and_a_circuit_with_no_spec_bound(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _one_pdk_installed(monkeypatch)
    ref = "ferrosim_biquad"
    assert [(r.check, r.status) for r in verify.run_tier3([ref], sim=True, cache={})] == [
        ("sim:reference", "skip")
    ]
    assert [(r.check, r.status) for r in verify.run_tier4([ref], sim=True, cache={})] == [
        ("conform:reference", "skip")
    ]
    assert (
        verify.derive_status(ref, [verify.CheckResult(ref, 0, "synthetic:t0", "pass")])
        == "reference"
    )

    unbounded = "sup_003_rrl_sc_integrator"  # its datasheet sets no numeric min/max
    assert [
        (r.check, r.status, r.reason) for r in verify.run_tier4([unbounded], sim=True, cache={})
    ] == [("conform", "skip", "no spec-bounded datasheet metric to check")]


_UNKNOWN = "zz_not_a_circuit"  # not in the registry: derive_status reads the rows alone
_T012 = [(0, "a", "pass"), (1, "b", "pass"), (2, "c", "pass")]
_T3 = [(3, f"sim:ac@{_PDK}/tt", "pass"), (3, "sim:ac@sky130", "skip")]


@pytest.mark.parametrize(
    ("rows", "status"),
    [
        pytest.param([], "draft", id="no-rows"),
        pytest.param([(0, "a", "fail")], "draft", id="t0-fail"),
        # generated = T0, T1 and T2 all cleared (plan §6); a run missing one backs no rung
        pytest.param(_T012[:1], "draft", id="t0-only"),
        pytest.param(_T012[:2], "draft", id="no-t2-rows"),
        pytest.param([_T012[0], (1, "b", "fail"), _T012[2]], "draft", id="t1-fail"),
        pytest.param([*_T012[:2], (2, "c", "skip")], "draft", id="t2-all-skip"),
        pytest.param(_T012, "generated", id="t0-t2-clear"),
        pytest.param([*_T012, (3, "sim", "skip")], "generated", id="t3-opt-in-skip"),
        pytest.param([*_T012, (3, "x", "pass"), (3, "y", "fail")], "generated", id="t3-one-fail"),
        pytest.param([*_T012, *_T3], "simulated", id="no-t4-rows"),
        pytest.param(
            [*_T012, *_T3, (4, "conform:a@p", "pass"), (4, "conform:b@p", "pass")],
            "validated",
            id="every-conform-row-passes",
        ),
        pytest.param(
            [*_T012, *_T3, (4, "conform:a@p", "pass"), (4, "conform:b@p", "skip")],
            "simulated",
            id="one-conform-row-out-of-spec",
        ),
        pytest.param(
            [*_T012, *_T3, (4, "conform:a@p", "pass"), (4, "conform:b@p", "fail")],
            "simulated",
            id="one-conform-row-fails",
        ),
        pytest.param(
            [*_T012, *_T3, (4, "conform", "skip")], "simulated", id="t4-circuit-level-skip"
        ),
        pytest.param(
            [*_T012, *_T3, (4, "conform", "pass")], "simulated", id="t4-pass-without-a-pdk-row"
        ),
    ],
)
def test_derive_status_is_validated_only_when_every_per_pdk_conform_row_passes(
    rows, status
) -> None:
    results = [verify.CheckResult(_UNKNOWN, t, check, st) for t, check, st in rows]
    # another circuit's rows never move this one's rung
    results.append(verify.CheckResult("other", 4, "conform:a@p", "skip"))
    assert verify.derive_status(_UNKNOWN, results) == status
