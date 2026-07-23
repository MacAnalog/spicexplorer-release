"""LIVE (slow): the engine-neutral Protocol path on a REAL PDK circuit.

Runs an `examples/analog-db` reference circuit (amp_001_5t, IHP sg13g2, DC op)
through the exact seams the optimizer now uses — `build_simulator` (the factory) →
`apply_corner` (PDK anchoring via `model_lib_root`) → `run()` → `SimResult.scalar`
— against real ngspice + the real IHP models. The offline RC tests in core prove the
plumbing; this proves it on PDK devices.

Gated on ngspice + the IHP PDK (`probe_pdk`, e.g. ``PDK_ROOT=~/local/pdks`` natively
or the api container) + the analog-db submodule being initialized.

Two analog-db-vs-platform impedance notes this test bridges (both engine truths, not
test conveniences):

* The analog-db raw decks resolve their corner lib by BARE name
  (`.lib cornerMOSlv.lib mos_tt`), expecting a sourcepath-configured image. Natively,
  `apply_corner` with an absolute `model_lib_root` replaces that include with a
  fully-resolved one — exactly the corner seam a real PVT run drives.
* The raw decks run their analysis from a `.control` block whose bare ``write``
  (destined for spicelib's ``-r`` rawfile) produces NO file under this ngspice-45
  build — the sim "succeeds" with no RAW (observed live 2026-07-05: the log prints
  ``ASCII raw file "..."`` twice yet nothing lands; an explicit ``write <file>``
  works). The platform's own testbenches are card-style (plain ``.ac``/``.op``
  cards, batch auto-write), which is reliable — so the test lowers the deck to a
  card-style ``.op``, preserving the identical operating point (the card run's
  ``|i(vdd)|`` equals the control block's printed ``i_supply`` to all digits).
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest
from _spicexplorer_fixtures import REPO_ROOT, requires_ngspice, requires_pdk, slow
from spicexplorer.core.domains import Corner
from spicexplorer.optimization.simulator_factory import build_simulator
from spicexplorer_core import env
from spicexplorer_core.pvt import ModelInclude

ANALOG_DB = REPO_ROOT / "examples/analog-db"
DECK = ANALOG_DB / "raw/amp_001_5t/ihp-sg13g2/dc_op.spice"

VDD = 1.5  # the deck's .param VDD


def _ihp_models_dir() -> Path | None:
    """The directory holding the IHP ngspice corner libs, wherever the PDK lives
    (native ``PDK_ROOT`` or the container's ``/opt/pdk``)."""
    pdk_root = env.probe_pdk().get("pdk_root")
    if not pdk_root:
        return None
    root = Path(pdk_root)
    for candidate in (root, root / "ihp-sg13g2"):
        hits = list(candidate.glob("**/ngspice/models/cornerMOSlv.lib"))
        if hits:
            return hits[0].parent
    return None


def _card_style_deck(tmp_path: Path) -> Path:
    """The analog-db deck with its `.control` block lowered to a card-style `.op`
    (see the module docstring for why). Everything else — testbench, bound sizing
    params, the lowered PDK DUT subckt — is byte-identical."""
    text = DECK.read_text()
    lowered = re.sub(r"(?ms)^\.control.*?^\.endc\s*$", ".op", text)
    assert lowered != text, "expected to find a .control block to lower"
    out = tmp_path / "amp001_dcop_card.spice"
    out.write_text(lowered)
    return out


@slow
@requires_ngspice
@requires_pdk
@pytest.mark.skipif(not DECK.exists(), reason="analog-db submodule not initialized")
def test_protocol_path_runs_a_pdk_circuit_live(tmp_path):
    models_dir = _ihp_models_dir()
    assert models_dir is not None, "probe_pdk said ok but no ngspice models dir found"

    # P4: construct through the factory, exactly as the orchestrator does.
    sim = build_simulator(
        "ngspice",
        netlist_filename=_card_style_deck(tmp_path),
        testbench_name="amp001_dcop",
        output_folder=tmp_path / "runs",
    )

    # PDK anchoring: replace the deck's bare-name `.lib` with the resolved one —
    # the same corner seam a PVT run drives (protocol v1.1 `model_lib_root`).
    tt = Corner(
        name="tt",
        model_includes=[ModelInclude(lib_file="cornerMOSlv.lib", section="mos_tt")],
        temp=27.0,
    )
    sim.apply_corner(tt, model_lib_root=str(models_dir))

    # Blocking Protocol run → engine-neutral scalar reads at the DC operating point.
    result = sim.run(label="amp001_dcop_tt")

    v_out = result.scalar("v(vout)", "op")
    assert np.isfinite(v_out), "output node voltage must extract from the op plot"
    assert 0.0 < v_out < VDD, f"5T-OTA output must sit inside the rails, got {v_out!r} V"

    i_supply = abs(result.scalar("i(vdd)", "op"))
    assert np.isfinite(i_supply)
    # A biased 5T-OTA draws real current: µA-scale, far from both 0 and mA-scale.
    assert 1e-9 < i_supply < 1e-2, f"implausible supply current {i_supply!r} A"

    # A missing metric degrades to NaN (never an exception) — the scorer's contract.
    assert np.isnan(result.scalar("v(no_such_node)", "op"))

    # The run's log landed and is harvestable through the duck-typed extension.
    assert getattr(result, "log_path", None) is not None
