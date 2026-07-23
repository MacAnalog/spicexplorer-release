"""`Simulator` / `SimResult` / `SimHandle` protocol seam.

Two tiers:

* Pure-Python (run everywhere, no ngspice): structural conformance, the analysis-string
  resolver, and the `None`-backed result degradation.
* `needs_ngspice` (run a real RC AC sweep — no PDK required): the blocking `run()` and
  non-blocking `submit()` paths, plus **scalar/wave parity** proving the new `SimResult`
  reads exactly the numbers `extract_scalar_variable_from_raw` / `extract_wave` read today.
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

needs_ngspice = pytest.mark.skipif(
    shutil.which("ngspice") is None, reason="ngspice not on PATH"
)

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
        legacy_scalar = rc_wrapper.extract_scalar_variable_from_raw(
            var, plot_type=Ngspice_Plot_Type.AC
        )[var]
        # exact: both read the same RawRead through identical extraction logic
        assert np.float64(proto_scalar) == legacy_scalar or (
            math.isnan(proto_scalar) and math.isnan(float(legacy_scalar))
        )

        proto_wave = res.wave(var, "ac")
        legacy_wave = rc_wrapper.extract_wave(var, plot_type=Ngspice_Plot_Type.AC)
        np.testing.assert_array_equal(proto_wave, legacy_wave)

        proto_real = res.wave(var, "ac", is_real=True)
        legacy_real = rc_wrapper.extract_wave(
            var, plot_type=Ngspice_Plot_Type.AC, is_real=True
        )
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
