"""In-library router — OPEN lane LIVE: amp_022 ihp-sg13g2 AC via `run_circuit` (opt-in).

The mirror of the closed FOUNDRY-n65 proof, on the OPEN (ngspice) lane: the committed `sim_engine`
marker routes ihp-sg13g2 to ngspice, `run_circuit` runs the circuit's self-contained raw deck
through `NGSpice_Wrapper`, and the SAME datasheet metrics are scored off the result through the
engine-neutral registry (only the output signal name differs — `v(vout)` vs Spectre's `vout`).
No kit, no bridge — just ngspice + the open PDK on the sourcepath.

Opt-in: ngspice on PATH + the ihp-sg13g2 models resolvable + the analog-db binding (with the
`sim_engine` marker) present. Skips otherwise.
"""

from __future__ import annotations

import shutil

import pytest
from spicexplorer.backends.analog_db import (
    AnalogDbUnavailable,
    pdk_sim_engine,
    probe_engine,
    run_circuit,
)

pytestmark = pytest.mark.slow

_CIRCUIT, _PDK, _TB = "amp_022_fer_two_stage", "ihp-sg13g2", "ac_open_loop"


def _marker_present() -> bool:
    try:
        return pdk_sim_engine(_PDK) == "ngspice"
    except Exception:
        return False


@pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice not on PATH")
@pytest.mark.skipif(not _marker_present(), reason="analog-db ihp sim_engine marker not present")
def test_run_circuit_open_lane_amp022_ihp_ac() -> None:
    cap = probe_engine(_CIRCUIT, _PDK)
    assert cap.engine == "ngspice", cap
    if not cap.available:
        pytest.skip(f"open lane unavailable: {cap.reason}")

    try:
        run = run_circuit(_CIRCUIT, _PDK, testbench=_TB)
    except AnalogDbUnavailable as exc:
        pytest.skip(f"analog-db open lane unavailable: {exc}")

    assert run.engine == "ngspice"
    evals = run.evaluate(only={"dc_gain_db", "ugf_hz", "pm_deg"})
    assert set(evals) == {"dc_gain_db", "ugf_hz", "pm_deg"}, evals
    for name, m in evals.items():
        assert m.satisfied, f"{name}={m.value} fails datasheet spec [{m.spec_min}, {m.spec_max}]"
    # healthy two-stage amplifier operating point on the open PDK
    assert 40.0 < evals["dc_gain_db"].value < 65.0, evals
    assert 1.0e6 < evals["ugf_hz"].value < 100.0e6, evals
    assert 45.0 < evals["pm_deg"].value < 90.0, evals
