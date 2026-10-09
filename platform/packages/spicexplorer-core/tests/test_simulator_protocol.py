"""`Simulator` / `SimResult` / `SimHandle` protocol seam.

Two tiers:

* Pure-Python (run everywhere, no ngspice): structural conformance, the analysis-string
  resolver, and the `None`-backed result degradation.
* `needs_ngspice` (run a real RC AC sweep — no PDK required): the blocking `run()` and
  non-blocking `submit()` paths, plus **scalar/wave parity** proving the new `SimResult`
  reads the numbers `extract_scalar_variable_from_raw` / `extract_wave` read, except for the
  scalar of a complex AC trace, which is |H| rather than the legacy Re(H) (OPT-12).
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path

import numpy as np
import pytest
from spicexplorer_core.spice_engine import (
    Ngspice_Plot_Type,
    NGSpice_Wrapper,
    NgspiceSimHandle,
    NgspiceSimResult,
    SimHandle,
    SimResult,
    Simulator,
    resolve_ngspice_plot_type,
)

needs_ngspice = pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice not on PATH")

# A self-contained RC low-pass — no PDK models, so this runs on any ngspice host
# (Mac included). spicelib requires the leading `*` title line.
RC_DECK = """* RC low-pass for the Simulator-protocol tests
V1 in 0 dc 0 ac 1
R1 in out 1k
C1 out 0 100p
.ac dec 5 1k 1Meg
.end
"""


@pytest.fixture
def rc_wrapper(tmp_path: Path) -> NGSpice_Wrapper:
    deck = tmp_path / "rc.cir"
    deck.write_text(RC_DECK)
    out = tmp_path / "runs"
    return NGSpice_Wrapper(netlist_filename=deck, output_folder=out, testbench_name="rc")


# ---------------------------------------------------------------------------
# Pure-Python: structural conformance + resolver + degradation
# ---------------------------------------------------------------------------
def test_ngspice_wrapper_satisfies_simulator_protocol_structurally() -> None:
    # runtime_checkable Protocols (method-only) support issubclass: this pins that the
    # wrapper exposes update_params / apply_corner / run / submit — no inheritance needed.
    assert issubclass(NGSpice_Wrapper, Simulator)
    assert issubclass(NgspiceSimResult, SimResult)
    assert issubclass(NgspiceSimHandle, SimHandle)


def test_resolve_ngspice_plot_type_vocabulary() -> None:
    assert resolve_ngspice_plot_type("ac") is Ngspice_Plot_Type.AC
    assert resolve_ngspice_plot_type("OP") is Ngspice_Plot_Type.OP
    assert resolve_ngspice_plot_type("op") is Ngspice_Plot_Type.OP
    assert resolve_ngspice_plot_type("tran") is Ngspice_Plot_Type.TRAN
    assert resolve_ngspice_plot_type("noise") is Ngspice_Plot_Type.NOISE_1
    assert resolve_ngspice_plot_type("noise_spectrum") is Ngspice_Plot_Type.NOISE_2
    assert resolve_ngspice_plot_type("dc") is Ngspice_Plot_Type.DC
    # enum members pass through, and the enum's display value resolves too
    assert resolve_ngspice_plot_type(Ngspice_Plot_Type.DC) is Ngspice_Plot_Type.DC
    assert resolve_ngspice_plot_type("AC Analysis") is Ngspice_Plot_Type.AC
    # the DC plot type carries ngspice's ACTUAL sweep title, so a RawRead plot lookup matches
    # (ngspice names a dc sweep "DC transfer characteristic", not "DC Analysis").
    assert Ngspice_Plot_Type.DC.value == "DC transfer characteristic"
    assert resolve_ngspice_plot_type("DC transfer characteristic") is Ngspice_Plot_Type.DC
    with pytest.raises(ValueError, match="Unknown analysis"):
        resolve_ngspice_plot_type("not-an-analysis")


def test_none_backed_result_degrades_like_the_wrapper() -> None:
    # A failed/diverged sim leaves no RAW → NaN scalars (never crashes the scorer),
    # while a wave request is a hard ask and raises.
    res = NgspiceSimResult(None)
    assert math.isnan(res.scalar("v(out)", "op"))
    with pytest.raises(RuntimeError):
        res.wave("v(out)", "op")


class _FakePlot:
    """The two methods of a spicelib plot the pure extraction helpers call."""

    def __init__(self, name: str, waves: dict[str, np.ndarray]) -> None:
        self._name = name
        self._waves = waves

    def get_plot_name(self) -> str:
        return self._name

    def get_wave(self, name: str) -> np.ndarray:
        if name not in self._waves:
            raise IndexError(name)
        return self._waves[name]


class _FakeRaw:
    def __init__(self, *plots: _FakePlot) -> None:
        self.plots = list(plots)


def test_ac_scalar_of_a_phasor_is_its_magnitude_and_a_real_vector_keeps_its_sign() -> None:
    """OPT-12. ngspice writes every AC-plot vector as complex. A node phasor's scalar is |H| (it
    used to be Re(H)); a `.meas`/`let` result shares the plot as a real value padded with 0j,
    and it must keep its sign — a -20 degree phase margin is not a +20 degree one."""
    res = NgspiceSimResult(
        _FakeRaw(
            _FakePlot(
                "AC Analysis",
                {  # type: ignore[arg-type]
                    "v(out)": np.array([0.6 - 0.8j, 0.3 - 0.4j]),
                    "v(in)": np.array([1.0 + 0j, 1.0 + 0j]),
                    "pm": np.array([-20.0 + 0j, 0j]),
                    "dcgain": np.array([-6.0 + 0j, 0j]),
                },
            )
        )
    )
    assert res.scalar("v(out)", "ac") == pytest.approx(1.0)  # |0.6-0.8j|, not 0.6
    assert res.scalar("v(in)", "ac") == 1.0
    assert res.scalar("pm", "ac") == -20.0
    assert res.scalar("dcgain", "ac") == -6.0
    assert math.isnan(res.scalar("v(missing)", "ac"))


def test_ac_scalar_is_a_magnitude_when_any_sweep_point_is_complex() -> None:
    """OPT-12. A phasor is told from a real-valued vector by its whole sweep, not its first
    point: an inverting stage's trace can be real at the first point (-2+0j at DC) and complex
    after it. Its scalar is still |H| at the first point (2.0), never the signed real part."""
    res = NgspiceSimResult(
        _FakeRaw(
            _FakePlot(
                "AC Analysis",
                {  # type: ignore[arg-type]
                    "v(inv)": np.array([-2.0 + 0j, 0.5 - 0.5j, 0.1 - 0.2j]),
                    "v(late)": np.array([3.0 + 0j, 3.0 + 0j, 0.0 - 1.0j]),
                },
            )
        )
    )
    assert res.scalar("v(inv)", "ac") == 2.0
    assert res.scalar("v(late)", "ac") == 3.0


def test_ac_scalar_of_a_single_point_sweep() -> None:
    res = NgspiceSimResult(
        _FakeRaw(
            _FakePlot(
                "AC Analysis",
                {  # type: ignore[arg-type]
                    "v(out)": np.array([-0.6 - 0.8j]),
                    "gm_db": np.array([-3.0 + 0j]),
                },
            )
        )
    )
    assert res.scalar("v(out)", "ac") == pytest.approx(1.0)
    assert res.scalar("gm_db", "ac") == -3.0


def test_non_ac_scalars_keep_their_sign() -> None:
    """The magnitude rule is for complex plots only: a real transient/op vector reads as is."""
    res = NgspiceSimResult(
        _FakeRaw(  # type: ignore[arg-type]
            _FakePlot("Transient Analysis", {"v(out)": np.array([-0.5, 1.0])}),
            _FakePlot("Operating Point", {"i(v1)": np.array([-1e-3])}),
        )
    )
    assert res.scalar("v(out)", "tran") == -0.5
    assert res.scalar("i(v1)", "op") == -1e-3


def test_spice_engine_ships_no_dead_storage_module() -> None:
    """OPT-18: `spice_engine.storage` (Spice_Simulation_Database) had no importer anywhere."""
    import importlib.util

    assert importlib.util.find_spec("spicexplorer_core.spice_engine.storage") is None


# ---------------------------------------------------------------------------
# Live ngspice: run/submit through the protocol + parity vs the legacy extractors
# ---------------------------------------------------------------------------
@needs_ngspice
def test_run_blocking_returns_conformant_simresult(rc_wrapper: NGSpice_Wrapper) -> None:
    # instance-level conformance (attributes present on the live object)
    assert isinstance(rc_wrapper, Simulator)

    res = rc_wrapper.run()
    assert isinstance(res, SimResult)

    # v(out) of an RC low-pass at 1 kHz is ~unity → a finite, non-NaN scalar
    gain = res.scalar("v(out)", "ac")
    assert not math.isnan(gain)
    assert abs(gain) > 0.0

    wave = res.wave("v(out)", "ac")
    freqs = res.wave("frequency", "ac", is_real=True)
    assert wave.shape == freqs.shape
    assert wave.size > 1
    assert np.iscomplexobj(wave)  # AC → complex trace


@needs_ngspice
def test_scalar_and_wave_parity_with_legacy_extractors(rc_wrapper: NGSpice_Wrapper) -> None:
    res = rc_wrapper.run()  # populates curr_raw; res wraps that same RawRead

    for var in ("v(out)", "v(in)"):
        proto_scalar = res.scalar(var, "ac")
        legacy_wave0 = rc_wrapper.extract_wave(var, plot_type=Ngspice_Plot_Type.AC)[0]
        # exact: the protocol's AC scalar of a phasor is |H| at the first point (OPT-12). The
        # legacy `extract_scalar_variable_from_raw` still reads Re(H), so it is no longer the
        # reference for a complex trace; v(in) (1+0j) is real-valued and reads the same either way.
        assert proto_scalar == float(np.abs(legacy_wave0))

        proto_wave = res.wave(var, "ac")
        legacy_wave = rc_wrapper.extract_wave(var, plot_type=Ngspice_Plot_Type.AC)
        np.testing.assert_array_equal(proto_wave, legacy_wave)

        proto_real = res.wave(var, "ac", is_real=True)
        legacy_real = rc_wrapper.extract_wave(var, plot_type=Ngspice_Plot_Type.AC, is_real=True)
        np.testing.assert_array_equal(proto_real, legacy_real)


@needs_ngspice
def test_submit_nonblocking_returns_conformant_handle(rc_wrapper: NGSpice_Wrapper) -> None:
    handle = rc_wrapper.submit()
    assert isinstance(handle, SimHandle)
    assert isinstance(handle.is_done(), bool)

    res = handle.result()  # blocks until the task finishes
    assert isinstance(res, SimResult)
    assert handle.is_done()  # done once result() returned

    gain = res.scalar("v(out)", "ac")
    assert not math.isnan(gain)
    assert abs(gain) > 0.0

    # calling result() again returns the cached SimResult (no re-read)
    assert handle.result() is res


# `.meas` results and `let` vectors land in the AC plot next to the node phasors, written as
# complex with a zero imaginary part (a `.meas` scalar padded to the sweep length with 0j).
# The control block follows the analog-db decks' form (`set filetype=ascii` … `write` / `quit`).
MEAS_DECK = """* RC low-pass with AC .meas results
V1 in 0 dc 0 ac 1
R1 in out 1k
C1 out 0 100p
.control
set filetype=ascii
ac dec 5 1k 1Meg
let ph = cph(v(out))*180/3.14159265
meas ac ph100k FIND ph AT=100k
write
quit
.endc
.end
"""


@needs_ngspice
def test_ac_scalar_live_magnitude_for_phasors_sign_for_meas(tmp_path: Path) -> None:
    """OPT-12 against real ngspice output: the node phasor reads |H|, the `.meas` phase keeps
    its (negative) sign."""
    deck = tmp_path / "rc_meas.cir"
    deck.write_text(MEAS_DECK)
    res = NGSpice_Wrapper(
        netlist_filename=deck, output_folder=tmp_path / "runs", testbench_name="rc_meas"
    ).run()
    first = res.wave("v(out)", "ac")[0]
    assert first.imag != 0.0  # a genuine phasor at 1 kHz
    assert res.scalar("v(out)", "ac") == float(np.abs(first))
    ph100k = res.scalar("ph100k", "ac")
    rc_lag = math.degrees(math.atan(2 * math.pi * 1e5 * 1e3 * 100e-12))  # ≈ 3.6° at 100 kHz
    assert ph100k == pytest.approx(-rc_lag, rel=1e-3)
