"""Construction-time side-effect taming.

The bridge's constructor path (`load_vb_env()`) discovers a `.env` cwd-upward and
`load_dotenv(override=True)`s it — the risk: a discoverable remote profile
silently flips a local-mode run to SSH, and the loader mutates the process env of a
LONG-LIVED host (the API server, an optimizer run). The adapter's answer is the
`vb_env_file` pin (registered via `set_runtime_env_file`, wins over discovery) plus
`vb_env` setdefault pre-sets.

This test discharges the question: constructing the adapter in a cwd holding a
DISCOVERABLE decoy `.env` must (a) honor the pinned profile, not the decoy, (b) leave
every non-``VB_*`` environment variable untouched, and (c) leave the root logging
config (handlers + level) unmutated. Offline — construction only, no license, no sim;
skips where the bridge isn't installed.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pytest


def test_bridge_construction_env_and_logging_isolation(tmp_path: Path, monkeypatch) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    from spicexplorer.backends.spectre import create_spectre_simulator
    from spicexplorer.backends.spectre_deck import deck_spec_from_native

    # a DISCOVERABLE decoy .env in cwd — without the pin, load_vb_env() would
    # load_dotenv(override=True) it into the process
    (tmp_path / ".env").write_text("VB_REMOTE_HOST=decoy.invalid\nHARMLESS_CANARY=decoy\n")
    monkeypatch.chdir(tmp_path)
    pinned = tmp_path / "pinned.env"
    pinned.write_text(
        "VB_REMOTE_HOST=localhost\nVB_SPECTRE_BIN=/bin/true\nVB_CADENCE_CSHRC=/dev/null\n"
    )
    monkeypatch.delenv("VB_REMOTE_HOST", raising=False)
    monkeypatch.delenv("HARMLESS_CANARY", raising=False)

    env_before = dict(os.environ)
    root = logging.getLogger()
    handlers_before = list(root.handlers)
    level_before = root.level

    try:
        sim = create_spectre_simulator(
            deck_spec=deck_spec_from_native("env isolation probe", "R1 (a 0) resistor r=1k"),
            deck_dir=tmp_path / "decks",
            vb_env_file=pinned,
            work_dir=str(tmp_path / "raw"),
        )
        assert sim is not None

        # (a) the pinned profile won; the discoverable decoy did not
        assert os.environ.get("VB_REMOTE_HOST") == "localhost"
        assert os.environ.get("HARMLESS_CANARY") != "decoy"
        # (b) no non-VB_* env key changed or appeared
        changed = {
            k for k in env_before
            if os.environ.get(k) != env_before[k] and not k.startswith("VB_")
        }
        grew = {k for k in os.environ if k not in env_before and not k.startswith("VB_")}
        assert not changed and not grew, f"bridge construction leaked env: {sorted(changed | grew)}"
        # (c) root logging config untouched
        assert list(root.handlers) == handlers_before
        assert root.level == level_before
    finally:
        # scrub the VB_* keys the pinned profile loaded, so later tests in this
        # process see their own environment, not this probe's
        for k in set(os.environ) - set(env_before):
            if k.startswith("VB_"):
                del os.environ[k]
        for k, v in env_before.items():
            if k.startswith("VB_") and os.environ.get(k) != v:
                os.environ[k] = v
