"""The OD-8 OTA acceptance's helper functions, checked offline (no ngspice, no PDK).

``test_n2tf_slow_sim`` is ``slow``: it only runs where ngspice and the IHP PDK are installed, and
for a long time it never ran at all — its PDK gate read ``probe_pdk()["ok"]`` (the key is
``pdk_ok``), so it skipped everywhere. These fast tests check that gate, the bench netlist edits,
the probe paths and when the test skips versus fails, on any host, and replay a
recorded ngspice run (``fixtures/ota-5t_open_loop_ngspice.txt``) through the WHOLE acceptance
so the netlist2tf half runs without a simulator.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import test_n2tf_slow_sim as slow
from spicexplorer_core.env import _PDK_ENV_VARS, probe_pdk
from spicexplorer_netlist2tf import (
    ComplexRoot,
    Fidelity,
    PoleZeroResult,
    build_system,
    from_string,
    operating_point_from,
    poles_zeros,
    small_signal_model,
)

_REPLAY = Path(__file__).resolve().parent / "fixtures" / "ota-5t_open_loop_ngspice.txt"
_OSDI = "libs.tech/ngspice/osdi/psp103_nqs.osdi"
_LIB = "libs.tech/ngspice/models/cornerMOSlv.lib"


def _fake_kit(root: Path, *, osdi: bool = True) -> Path:
    """An IHP sg13g2 install as ngspice needs it (model lib + PSP OSDI), under ``root``."""
    tree = root / "ihp-sg13g2"
    (tree / _LIB).parent.mkdir(parents=True)
    (tree / _LIB).write_text("* stand-in model lib\n")
    if osdi:
        (tree / _OSDI).parent.mkdir(parents=True)
        (tree / _OSDI).write_bytes(b"")
    return tree


@pytest.fixture
def no_kit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """No PDK anywhere: every PDK env var unset and the default install pointed at nothing (so
    the host's real ``/opt/pdk`` is never found). Returns that empty default location."""
    for var in _PDK_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    missing = tmp_path / "no-default-install"
    monkeypatch.setattr(slow, "_DEFAULT_PDK_ROOT", missing)
    return missing


def _outcome(call) -> BaseException:  # noqa: ANN001 — a zero-arg callable
    """Run ``call`` and return the pytest outcome it raised (skip OR fail), so a test can assert
    WHICH one — a propagated Skipped would otherwise skip the asserting test."""
    with pytest.raises((pytest.skip.Exception, pytest.fail.Exception)) as info:
        call()
    return info.value


# ------------------------------------------------------------------ the PDK gate (_ihp_tree)
def test_gate_finds_the_kit_under_pdk_root(no_kit, tmp_path, monkeypatch):
    """The reported defect: an installed kit was never found. PDK_ROOT is the kit's PARENT (the
    lab layout, ``/opt/pdk/ihp-sg13g2``), so the tree is ``root/ihp-sg13g2``."""
    tree = _fake_kit(tmp_path / "pdks")
    monkeypatch.setenv("PDK_ROOT", str(tmp_path / "pdks"))
    assert slow._ihp_tree() == (tree, "")


@pytest.mark.parametrize("var", ["PDK", "IHP_PDK_ROOT"])
def test_gate_accepts_the_kit_tree_itself(no_kit, tmp_path, monkeypatch, var):
    """A root that IS the kit tree (no ``ihp-sg13g2`` level below it) is used as-is."""
    tree = _fake_kit(tmp_path / "pdks")
    monkeypatch.setenv(var, str(tree))
    assert slow._ihp_tree() == (tree, "")


def test_gate_falls_back_to_the_default_install(no_kit, tmp_path, monkeypatch):
    """With every PDK variable unset, the lab/container install (``/opt/pdk``) is searched."""
    tree = _fake_kit(tmp_path / "opt-pdk")
    monkeypatch.setattr(slow, "_DEFAULT_PDK_ROOT", tmp_path / "opt-pdk")
    assert slow._ihp_tree() == (tree, "")


def test_gate_names_what_it_searched_when_nothing_is_installed(no_kit):
    tree, why = slow._ihp_tree()
    assert tree is None
    assert why == probe_pdk(extra_roots=[("default install", no_kit)])["pdk_detail"]
    assert "not found" in why and str(no_kit) in why


def test_gate_refuses_a_kit_without_the_psp_osdi(no_kit, tmp_path, monkeypatch):
    """The model lib alone satisfies ``probe_pdk``, but ngspice cannot load the PSP devices
    without the OSDI: the gate must say so rather than return an unusable tree."""
    _fake_kit(tmp_path / "pdks", osdi=False)
    monkeypatch.setenv("PDK_ROOT", str(tmp_path / "pdks"))
    tree, why = slow._ihp_tree()
    assert tree is None
    assert "PSP OSDI" in why and str(tmp_path / "pdks") in why


# ------------------------------------------------------------------ the bench netlist edits
def test_open_loop_bench_for_netlist2tf_has_no_control_and_an_ac_ground_feedback():
    text = slow._bench(slow._OPEN_LOOP_N2TF)
    fixture = slow._FIXTURE.read_text()
    assert ".control" not in text and ".endc" not in text
    assert slow._BUFFER not in text and slow._OPEN_LOOP_N2TF in text
    # everything outside the buffer line and the .control block is untouched
    for line in fixture.splitlines():
        if line.startswith((".param", ".subckt", ".lib", "XM", "C1 ", "Vin ", "I0 ")):
            assert line in text, line


def test_open_loop_bench_for_ngspice_carries_the_given_control_block():
    control = ".control\nop\nquit\n.endc"
    text = slow._bench(slow._OPEN_LOOP_SIM, control)
    assert text.count(".control") == 1 and text.count(".endc") == 1
    assert control in text
    assert "Lfb v_out v_fb 1T" in text and "Cfb v_fb v_ss 1T" in text
    assert "ac dec 101 1k 100MEG" not in text  # the fixture's own buffer sweep is gone


def test_bench_refuses_a_fixture_whose_buffer_line_moved(monkeypatch):
    monkeypatch.setattr(slow, "_BUFFER", "xota v_dd v_out v_in v_out net1 v_ena v_ss renamed")
    with pytest.raises(AssertionError, match="buffer"):
        slow._bench(slow._OPEN_LOOP_N2TF)


def test_flattened_bench_matches_the_probe_paths_and_the_full_hybrid_pi_roles():
    """What the live test indexes by must exist: 13 MOSFETs one flatten level down, each one's
    ngspice path, and every FULL role of each is filled by :func:`operating_point_from` from
    exactly the probed PSP outputs."""
    ir = from_string(slow._bench(slow._OPEN_LOOP_N2TF), name="ota_5t_open_loop")
    mos = [d for d in ir.devices if d.kind.value in ("nmos", "pmos")]
    assert {slow._ngspice_path(d.ref) for d in mos} == {f"xota.xm{i}" for i in range(1, 14)}
    ssir = small_signal_model(ir, level=Fidelity.FULL)
    op = {  # every probed value, nothing else
        f"@n.{slow._ngspice_path(d.ref)}.n{str(d.model).lower()}[{p}]": 1.0
        for d in mos
        for p in slow._PSP_OP
    }
    values, unmapped = operating_point_from(op, ssir)
    assert unmapped == []
    for d in mos:
        assert {str(sym) for sym in ssir.symbols[d.ref].values()} <= set(values), d.ref


# ------------------------------------------------------------------ naming + mapping
@pytest.mark.parametrize(("ref", "path"), [("XM1_XOTA", "xota.xm1"), ("xm13_xota", "xota.xm13")])
def test_ngspice_path_is_parent_dot_instance(ref, path):
    assert slow._ngspice_path(ref) == path


@pytest.mark.parametrize("ref", ["XM1", "XM1_XA_XB"])
def test_ngspice_path_refuses_anything_but_one_flatten_level(ref):
    with pytest.raises(AssertionError, match="one flatten level"):
        slow._ngspice_path(ref)


def test_value_regex_reads_every_name_value_line_and_nothing_else():
    stdout = (
        "Circuit: ** Example of simple 5-transistor OTA\n"
        "@n.xota.xm1.nsg13_lv_nmos[gm] = 1.234e-05\n"
        "@n.xota.xm1.nsg13_lv_nmos[cgdol] = -2.5E-16\n"
        "Doing analysis at TEMP = 27.000000 and TNOM = 27.000000\n"
        "a0                  =  3.264786e+01\n"
        "No. of Data Rows : 1001\n"
        "ugf                 =  1.975860e+07\n"
    )
    assert dict(slow._VALUE.findall(stdout)) == {
        "@n.xota.xm1.nsg13_lv_nmos[gm]": "1.234e-05",
        "@n.xota.xm1.nsg13_lv_nmos[cgdol]": "-2.5E-16",
        "a0": "3.264786e+01",
        "ugf": "1.975860e+07",
    }


# ------------------------------------------------------------------ the ZPK → H(jω) rebuild
def _pz(poles: list[complex], zeros: list[complex], dc: float) -> PoleZeroResult:
    def root(z: complex) -> ComplexRoot:
        return ComplexRoot(
            expr=str(z), value_real=z.real, value_imag=z.imag, frequency_hz=abs(z) / (2.0 * math.pi)
        )

    return PoleZeroResult(
        output="out",
        input="in",
        dc_gain=dc,
        poles=[root(p) for p in poles],
        zeros=[root(z) for z in zeros],
    )


def test_response_of_one_lhp_pole_lags_45_degrees_at_the_pole():
    w = 2.0 * math.pi * 1.0e3
    h = slow._response(_pz([-w], [], 10.0), np.array([0.0, 1.0e3]))
    assert h[0] == pytest.approx(10.0)
    assert abs(h[1]) == pytest.approx(10.0 / math.sqrt(2.0))
    assert np.degrees(np.angle(h[1])) == pytest.approx(-45.0)


def test_response_of_a_rhp_zero_lags_and_a_repeated_pole_squares():
    wz, wp = 2.0 * math.pi * 1.0e6, 2.0 * math.pi * 1.0e3
    pz = _pz([-wp], [wz], 1.0)
    pz.poles[0].multiplicity = 2
    f = 1.0e6
    h = slow._response(pz, np.array([f]))[0]
    expected = (1.0 - 1j * f / 1.0e6) / (1.0 + 1j * f / 1.0e3) ** 2
    assert h == pytest.approx(expected)
    assert np.degrees(np.angle(1.0 - 1j)) == pytest.approx(-45.0)  # the RHP zero's own lag


def test_response_matches_the_pencil_roots_of_an_rc():
    """End to end with netlist2tf's own sign convention: the pencil's LHP pole of R = 1 k,
    C = 1 n rebuilds H = 1/(1 + jωRC)."""
    ir = from_string("* rc\nV1 in 0 dc 0 ac 1\nR1 in out 1k\nC1 out 0 1n\n.end\n", name="rc")
    ssir = small_signal_model(ir)
    pz = poles_zeros(build_system(ssir), ("out", "0"), ("in", "0"))
    freq = np.logspace(3, 7, 9)
    expected = 1.0 / (1.0 + 2j * math.pi * freq * 1.0e3 * 1.0e-9)
    assert slow._response(pz, freq) == pytest.approx(expected, rel=1e-9)


def test_response_requires_a_dc_gain():
    with pytest.raises(AssertionError):
        slow._response(PoleZeroResult(output="out", input="in"), np.array([1.0]))


# ------------------------------------------------------------------ skip vs fail, and a replay
def _fake_ngspice(monkeypatch: pytest.MonkeyPatch, stdout: str) -> list[dict]:
    """Stand in for the ngspice process: record each call, answer with ``stdout``."""
    calls: list[dict] = []

    def run(args, **kwargs):  # noqa: ANN001, ANN202 — subprocess.run's shape
        calls.append({"args": list(args), **kwargs})
        return subprocess.CompletedProcess(args, 0, stdout=stdout, stderr="")

    monkeypatch.setattr(slow, "_NGSPICE", "ngspice")
    monkeypatch.setattr(slow, "subprocess", SimpleNamespace(run=run))
    return calls


def test_rc_check_fails_when_ngspice_runs_but_prints_no_measurement(monkeypatch):
    """ngspice ran (the skipif saw it) and printed no ``f3db``: a real failure, not a skip."""
    _fake_ngspice(monkeypatch, "ngspice banner only\n")
    outcome = _outcome(slow.test_rc_pole_matches_ngspice_ac)
    assert isinstance(outcome, pytest.fail.Exception), outcome
    assert "could not parse f3db" in str(outcome)


def test_rc_check_compares_the_parsed_measurement_with_the_prediction(monkeypatch):
    """The other side of the same parse: a printed ``f3db`` is read and checked against the
    netlist2tf pole (1 kHz for this RC), within 5 % and no looser."""
    _fake_ngspice(monkeypatch, "f3db                =  1.000000e+03\n")
    slow.test_rc_pole_matches_ngspice_ac()
    _fake_ngspice(monkeypatch, "f3db                =  1.060000e+03\n")
    with pytest.raises(AssertionError):
        slow.test_rc_pole_matches_ngspice_ac()


def test_ota_acceptance_skips_naming_what_is_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(slow, "_ihp_tree", lambda: (None, "no kit on this host"))
    outcome = _outcome(lambda: slow.test_ihp_ota_open_loop_matches_ngspice_ac(tmp_path))
    assert isinstance(outcome, pytest.skip.Exception), outcome
    assert "IHP sg13g2 PDK not installed: no kit on this host" in str(outcome)


@pytest.mark.parametrize(
    ("stdout", "missing"),
    [("", ["a0", "f3db", "ugf"]), ("a0 = 3.2e+01\nugf = 2.0e+07\n", ["f3db"])],
)
def test_ota_acceptance_fails_when_ngspice_prints_no_measurement(
    monkeypatch, tmp_path, stdout, missing
):
    """…and the deck it hands ngspice is self-contained: the PSP OSDI and the model lib by the
    kit's absolute path (no ``.spiceinit``/sourcepath), every device probed, the loop opened."""
    tree = _fake_kit(tmp_path / "pdks")
    monkeypatch.setattr(slow, "_ihp_tree", lambda: (tree, ""))
    calls = _fake_ngspice(monkeypatch, stdout)
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    outcome = _outcome(lambda: slow.test_ihp_ota_open_loop_matches_ngspice_ac(run_dir))
    assert isinstance(outcome, pytest.fail.Exception), outcome
    assert f"ngspice produced no {missing}" in str(outcome)

    (call,) = calls
    assert call["args"] == ["ngspice", "-b", "ota_5t_open_loop.spice"]
    assert Path(call["cwd"]) == run_dir
    deck = (run_dir / "ota_5t_open_loop.spice").read_text()
    assert f"pre_osdi {tree / _OSDI}" in deck
    assert f".lib {tree / _LIB} mos_tt" in deck and ".lib cornerMOSlv.lib" not in deck
    assert "Lfb v_out v_fb 1T" in deck and slow._BUFFER not in deck
    probes = [ln for ln in deck.splitlines() if ln.startswith("print @n.xota.xm")]
    assert len(probes) == 13 * len(slow._PSP_OP)


def test_ota_acceptance_replays_a_recorded_ngspice_run_offline(monkeypatch, tmp_path):
    """The whole acceptance — probe parsing, PSP → hybrid-pi, the FULL flattened solve, the ZPK
    response and every tolerance — against ngspice's recorded answer, with no simulator."""
    monkeypatch.setattr(slow, "_ihp_tree", lambda: (_fake_kit(tmp_path / "pdks"), ""))
    _fake_ngspice(monkeypatch, _REPLAY.read_text())
    slow.test_ihp_ota_open_loop_matches_ngspice_ac(tmp_path)
