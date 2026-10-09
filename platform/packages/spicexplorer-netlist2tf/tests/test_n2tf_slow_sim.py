"""P6 — ``slow`` validation against a real simulator (gated; auto-skips without ngspice/PDK).

These cross-check netlist2tf against an actual ngspice ``.ac`` run:

* the RC cross-check is **PDK-free** (only needs ngspice) and runs on any host with ngspice;
* the OTA acceptance (decision OD-8) is **PDK-gated**: the committed IHP sg13g2 5T OTA
  testbench (``fixtures/ota-5t_tb-ac.spice``), opened into an open-loop bench, is flattened and
  solved by netlist2tf at the bias ngspice measures (``.op`` + the PSP device's own small-signal
  parameters), and its DC gain / dominant pole / unity-gain frequency are compared with the
  simulator's ``.ac`` sweep. It runs wherever ngspice and the IHP PDK are installed (``PDK_ROOT``,
  or the lab/container install under ``/opt/pdk``) and skips, naming what is missing, elsewhere.

Run with ``uv run pytest -m slow``.
"""

from __future__ import annotations

import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pytest
from spicexplorer_core.measurements.waveforms import (
    bandwidth_3db,
    dc_gain_db,
    unity_gain_freq,
)
from spicexplorer_netlist2tf import (
    Fidelity,
    PoleZeroResult,
    build_system,
    from_string,
    operating_point_from,
    poles_zeros,
    small_signal_model,
    transfer_function,
)

pytestmark = pytest.mark.slow

_NGSPICE = shutil.which("ngspice")

_RC_NETLIST = """* rc lowpass
V1 in 0 dc 0 ac 1
R1 in out 1k
C1 out 0 159.155n
.control
ac dec 50 1 1Meg
meas ac f3db when vdb(out)=-3.0103
print f3db
.endc
.end
"""


@pytest.mark.skipif(_NGSPICE is None, reason="ngspice not on PATH")
def test_rc_pole_matches_ngspice_ac():
    """netlist2tf's predicted −3 dB frequency matches a real ngspice ``.ac`` sweep (PDK-free)."""
    assert _NGSPICE is not None  # guaranteed by skipif; narrows the type for the call below
    # ngspice reference
    with tempfile.TemporaryDirectory() as d:
        cir = Path(d) / "rc.cir"
        cir.write_text(_RC_NETLIST)
        proc = subprocess.run(
            [_NGSPICE, "-b", str(cir)], capture_output=True, text=True, timeout=60
        )
    m = re.search(r"f3db\s*=\s*([0-9.eE+-]+)", proc.stdout)
    if not m:  # ngspice ran (the skipif saw it) but produced no measurement: a real failure
        pytest.fail(
            f"could not parse f3db from ngspice output:\n{proc.stdout[-500:]}\n{proc.stderr[-500:]}"
        )
    f3db_sim = float(m.group(1))

    # netlist2tf prediction for the same RC (R=1k, C=159.155n → f3dB ≈ 1 kHz)
    res = transfer_function(
        "* rc\nR1 in out R\nC1 out 0 C\n.end",
        ("out", "0"),
        ("in", "0"),
        operating_point={"r": 1e3, "c": 159.155e-9},
    )
    assert res.poles, "expected one pole"
    f3db_pred = res.poles[0].frequency_hz
    assert f3db_pred is not None
    assert f3db_pred == pytest.approx(f3db_sim, rel=0.05)


# ------------------------------------------------------------------ OTA acceptance (OD-8)
_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ota-5t_tb-ac.spice"
_IHP = "ihp-sg13g2"
#: the lab workstation / container install, searched after $PDK_ROOT / $PDK / $IHP_PDK_ROOT
_DEFAULT_PDK_ROOT = Path("/opt/pdk")

#: The fixture drives the OTA as a unity-gain buffer. An open-loop OTA has no defined DC output
#: on its own, so the simulator's bench keeps the unity DC feedback through a 1 TH inductor while
#: a 1 TF capacitor grounds the inverting input for AC: from ~1e-12 Hz up, the loop is open.
_BUFFER = "xota v_dd v_out v_in v_out net1 v_ena v_ss ota-5t"
_OPEN_LOOP_SIM = (
    "xota v_dd v_out v_in v_fb net1 v_ena v_ss ota-5t\nLfb v_out v_fb 1T\nCfb v_fb v_ss 1T"
)
#: The same bench in small-signal terms: v_fb is an AC ground, and a DC source is an AC short.
#: (The pencil solver refuses inductors — 1/sL is not affine in s — and the L/C pair contributes
#: nothing at any swept frequency, so netlist2tf is handed the AC-equivalent.)
_OPEN_LOOP_N2TF = "xota v_dd v_out v_in v_fb net1 v_ena v_ss ota-5t\nVfb v_fb v_ss dc 0"

#: PSP operating-point outputs read per MOSFET — :func:`spicexplorer_netlist2tf.operating_point_from`
#: maps them onto the FULL-fidelity hybrid-pi (its module docstring has the table).
_PSP_OP = ("gm", "gds", "gmb", "cgs", "cgsol", "cgd", "cgdol", "cjd", "cjs")
_VALUE = re.compile(r"^\s*(\S+)\s*=\s*([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)\s*$", re.M)


def _ihp_tree() -> tuple[Path | None, str]:
    """The IHP sg13g2 install ngspice can load (model lib + PSP OSDI), or ``(None, why)``."""
    from spicexplorer_core.env import probe_pdk

    pdk = probe_pdk(extra_roots=[("default install", _DEFAULT_PDK_ROOT)])
    if not pdk["pdk_ok"]:  # probe_pdk's key — the stub this replaces read a non-existent "ok"
        return None, str(pdk["pdk_detail"])
    root = Path(str(pdk["pdk_root"]))
    for tree in (root / _IHP, root):
        lib = tree / "libs.tech/ngspice/models/cornerMOSlv.lib"
        osdi = tree / "libs.tech/ngspice/osdi/psp103_nqs.osdi"
        if lib.is_file() and osdi.is_file():
            return tree, ""
    return None, f"IHP models found under {root} but not the ngspice model lib + PSP OSDI layout"


def _bench(feedback: str, control: str = "") -> str:
    """The fixture with its buffer connection replaced by ``feedback`` and its ``.control``
    block replaced by ``control`` (the DUT subckt, the bias and the .params are untouched)."""
    text = _FIXTURE.read_text()
    assert _BUFFER in text, "fixture's buffer connection changed — update _BUFFER"
    start, end = text.index(".control"), text.index(".endc") + len(".endc")
    return (text[:start] + control + text[end:]).replace(_BUFFER, feedback)


def _ngspice_path(ref: str) -> str:
    """``XM1_XOTA`` (netlist2tf's flattened ref) → ``xota.xm1`` (ngspice's instance path)."""
    inst, _, parent = ref.lower().partition("_")
    assert parent and "_" not in parent, f"expected one flatten level, got {ref}"
    return f"{parent}.{inst}"


def _response(pz: PoleZeroResult, freq: np.ndarray) -> np.ndarray:
    """H(j2πf) rebuilt from the pencil's ZPK (roots are listed with their conjugates)."""
    assert pz.dc_gain is not None
    s = 2j * np.pi * freq
    h = np.full(freq.shape, complex(pz.dc_gain))
    for z in pz.zeros:
        h *= (1.0 - s / complex(z.value_real or 0.0, z.value_imag or 0.0)) ** z.multiplicity
    for p in pz.poles:
        h /= (1.0 - s / complex(p.value_real or 0.0, p.value_imag or 0.0)) ** p.multiplicity
    return h


@pytest.mark.skipif(_NGSPICE is None, reason="ngspice not on PATH")
def test_ihp_ota_open_loop_matches_ngspice_ac(tmp_path: Path):
    """Corpus acceptance (OD-8): netlist2tf's DC gain, dominant pole and UGF of the committed IHP
    5T OTA agree with ngspice's ``.ac`` sweep of the same bench at the bias ngspice solved.

    Two independent paths to one number: ngspice linearizes the PSP devices itself; netlist2tf
    flattens the SAME netlist into its FULL hybrid-pi, fills each device from the PSP operating
    point (:func:`operating_point_from`, the package's own mapping) and reads the poles/zeros
    off the MNA pencil. Tolerances, per measured quantity (measured values from 2026-09-25 in brackets):

    * DC gain, 0.02 dB [6e-5 dB]: at DC every capacitor is open, so both sides linearize the same
      conductance network (gm, gmb, gds are the device's own derivatives); what netlist2tf omits
      is leakage — junction conductances ≤ 5e-14 S and gate-tunnelling currents ≤ 3e-11 A on the
      signal-path devices, against their gds ≥ 2.8e-8 S.
    * −3 dB frequency, 2 % [0.3 %]: set by CL plus the output node's overlap and junction caps.
      Tight enough to reject a wrong cap mapping (PSP's intrinsic cdb/csb as branches: 7.4 %).
    * UGF, 5 % [1.8 %]: it sits near the mirror pole, so it also carries the gate-node caps of
      the load mirror, where a four-branch-cap hybrid-pi has no place for PSP's non-reciprocal
      transcapacitances (cdg ≠ cgd) — the most plausible source of the residual.
    """
    tree, why = _ihp_tree()
    if tree is None:
        pytest.skip(f"IHP sg13g2 PDK not installed: {why}")
    assert _NGSPICE is not None

    ir = from_string(_bench(_OPEN_LOOP_N2TF), name="ota_5t_open_loop")
    mos = [d for d in ir.devices if d.kind.value in ("nmos", "pmos")]
    assert len(mos) == 13, [d.ref for d in ir.devices]  # the 5T core + bias/enable devices

    # ---- ngspice: the operating point, then the open-loop AC sweep of the same bench
    probes = [
        f"print @n.{_ngspice_path(d.ref)}.n{str(d.model).lower()}[{p}]"
        for d in mos
        for p in _PSP_OP
    ]
    osdi = tree / "libs.tech/ngspice/osdi/psp103_nqs.osdi"
    control = "\n".join(
        [
            ".control",
            f"pre_osdi {osdi}",  # the IHP devices are PSP via OSDI; no reliance on a .spiceinit
            "op",
            *probes,
            "ac dec 100 1 10G",
            "meas ac a0 find vdb(v_out) at=1",
            "let a3db = vdb(v_out)[0] - 3",  # DC − 3 dB: the definition bandwidth_3db applies
            "meas ac f3db when vdb(v_out)=a3db fall=1",
            "meas ac ugf when vdb(v_out)=0 fall=1",
            "quit",
            ".endc",
        ]
    )
    model_lib = tree / "libs.tech/ngspice/models/cornerMOSlv.lib"
    deck = _bench(_OPEN_LOOP_SIM, control).replace(
        ".lib cornerMOSlv.lib mos_tt",
        f".lib {model_lib} mos_tt",  # no reliance on sourcepath
    )
    (tmp_path / "ota_5t_open_loop.spice").write_text(deck)
    proc = subprocess.run(
        [_NGSPICE, "-b", "ota_5t_open_loop.spice"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=300,
    )
    sim = {k.lower(): float(v) for k, v in _VALUE.findall(proc.stdout)}
    missing = [k for k in ("a0", "f3db", "ugf") if k not in sim]
    if missing:
        pytest.fail(f"ngspice produced no {missing}:\n{proc.stdout[-1500:]}\n{proc.stderr[-1500:]}")

    # ---- netlist2tf: the flattened bench at that operating point, FULL fidelity
    ssir = small_signal_model(ir, level=Fidelity.FULL)
    assert not ssir.unmodelled
    # the package maps the ngspice OP (and the bench's .params, CL) onto the minted symbols
    subs, unmapped = operating_point_from(sim, ssir)
    assert not unmapped, f"symbols the OP did not fill: {unmapped}"
    pz = poles_zeros(
        build_system(ssir, subs=subs), ("v_out", "0"), ("v_in", "0"), numeric_subs=subs
    )

    freq = np.logspace(0, 10, 20001)  # 2000/dec: interpolation error far below the tolerances
    h = _response(pz, freq)
    pred = {
        "a0": dc_gain_db(freq, h),
        "f3db": bandwidth_3db(freq, h),
        "ugf": unity_gain_freq(freq, h),
    }
    report = {k: (pred[k], sim[k]) for k in pred}

    # the dominant-pole structure this bench is about: one output pole > a decade below the rest
    p1, p2 = (p.frequency_hz or 0.0 for p in pz.poles[:2])
    assert p2 / p1 > 10.0, f"no dominant pole: p1={p1:.4g} Hz, p2={p2:.4g} Hz"
    assert pred["a0"] == pytest.approx(sim["a0"], abs=0.02), report
    assert pred["f3db"] == pytest.approx(sim["f3db"], rel=0.02), report
    assert p1 == pytest.approx(sim["f3db"], rel=0.02), report  # −3 dB ≈ p1 when p2/p1 > 10
    assert pred["ugf"] == pytest.approx(sim["ugf"], rel=0.05), report
    assert math.isfinite(pred["ugf"]) and pred["a0"] > 20.0, report
