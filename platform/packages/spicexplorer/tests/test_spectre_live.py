"""LIVE Spectre through the platform adapter (opt-in; needs Cadence + a TSMC deck).

Real `spectre` (local mode or
over the bridge's SSH tunnel), a real foundry-PDK `.scs`, and the adapter's full result
path — bridge PSF parse + our info-file op-point post-parse + the prefix-chain lookup.

Opt-in gating (all three, or the test skips):

* ``virtuoso_bridge`` importable in this venv (``uv pip install -e external/virtuoso-bridge-lite``)
* ``SPICEXPLORER_SPECTRE_DECK`` — path to an op+ac testbench `.scs` smoke deck
  (analyses named ``dcOp`` / ``ac``, an ``info what=oppoint`` dump, a DUT
  subckt ``X0`` with ``M0``, output node ``VOUT``). The deck references the NDA PDK by
  path, so it is never committed.
* ``SPICEXPLORER_VB_ENV_FILE`` (optional) — bridge profile to pin, e.g.
  ``~/.virtuoso-bridge/local.env`` on a Cadence host. Without it the bridge's own
  `.env` discovery decides local-vs-SSH.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_DECK = os.environ.get("SPICEXPLORER_SPECTRE_DECK", "")


@pytest.mark.skipif(
    not (_DECK and Path(_DECK).expanduser().is_file()),
    reason="set SPICEXPLORER_SPECTRE_DECK to a live Spectre testbench .scs",
)
def test_live_spectre_op_and_ac_through_the_adapter() -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    from spicexplorer.backends.spectre import create_spectre_simulator

    env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
    sim = create_spectre_simulator(
        Path(_DECK).expanduser(),
        vb_env_file=Path(env_file).expanduser() if env_file else None,
    )

    result = sim.run(label="live_p0")

    # op-point node voltage (dcOp.dc → dc_ key, reached through the "op" chain): in-rails
    vout = result.scalar("VOUT", "op")
    assert 0.0 < vout < 1.32, f"VOUT op-point out of rails: {vout}"

    # per-MOS op scalars — the bridge parser drops these; only our post-parse supplies them
    gm = result.scalar("X0.M0:gm", "op")
    assert np.isfinite(gm) and gm > 0.0, f"X0.M0:gm not a positive scalar: {gm}"
    region = result.scalar("X0.M0:region", "op")
    assert region in (0.0, 1.0, 2.0, 3.0, 4.0), f"X0.M0:region not a BSIM4 region code: {region}"

    # ac wave (analysis named `ac` → ac_ keys), complex-valued, non-empty
    ac_vout = result.wave("VOUT", "ac")
    assert ac_vout.size > 0
    assert np.iscomplexobj(ac_vout)

    # a missing scalar degrades to NaN (never crashes the scorer)
    assert np.isnan(result.scalar("no_such_signal", "op"))
