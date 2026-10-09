"""Every optimizer config under ``raw_optimize/`` names decks that exist (FU-IA004-TB).

``raw_optimize/ia_004_fan_chopper_rrl.yaml`` pointed at
``raw/ia_004_fan_chopper_rrl/ihp-sg13g2/ac_closed_loop.spice``, a deck that has not existed since
the 2026-07-22 refusal of a frozen-operating-point ``.ac`` on a clocked (chopper) circuit; no test
read the config. ``generated/amp_020_two_stage_miller_cmfb.yaml`` stayed after its
circuit (retired in #59) the same way.

A config names a deck in ``project.netlist`` and in each ``testbenches[].netlist``, and may name
the circuit's params file in ``project.params_file``; each resolves against ``ws_root``, which
resolves against the config's own directory. One prefix is the exception, and it is checked, not
skipped: ``raw_optimize/_abs/<accession>/<deck>`` names a machine-local copy of a committed deck
with absolute ``.include`` paths (``.gitignore`` says why it is never committed), so its committed
twin ``raw/<accession>_*/<tech_spec.name>/<deck>`` must exist.

Every config's ``optimizer_config.type`` must also be an engine the platform runs (B-ADB-1).
``Project_Setup.from_yaml`` loads an unknown engine without error; the orchestrator refuses it
at construction, so ``type: ax`` in three ``generated/*_ax.yaml`` files failed only when a run
started. The check calls the platform's own resolver, ``optimizer_type_from_config``, so the
accepted names are the platform's (``OptimizerType``), not a list kept here. That import needs
the ``spicexplorer`` kernel, which analog-db does not declare; it is in the platform venv these
tests run from (TESTING.md).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from spicexplorer_analog_db import paths

optimizer_type_from_config = pytest.importorskip(
    "spicexplorer.optimization.orchestrator"
).optimizer_type_from_config

ABS_PREFIX = "raw_optimize/_abs/"


def _configs() -> list[Path]:
    return sorted((paths.db_root() / "raw_optimize").rglob("*.yaml"))


def _named_files(doc: dict) -> list[str]:
    project = doc.get("project") or {}
    named = [project.get("netlist"), project.get("params_file")]
    named += [tb.get("netlist") for tb in project.get("testbenches") or []]
    return [n for n in named if n]


def _abs_twin(ref: str, pdk: str, db: Path) -> list[Path]:
    """The committed decks a ``raw_optimize/_abs/<accession>/<deck>`` copy stands for."""
    accession, deck = Path(ref).relative_to(ABS_PREFIX).parts
    return sorted(db.glob(f"raw/{accession}_*/{pdk}/{deck}"))


def missing_files(config: Path) -> list[str]:
    """The files ``config`` names that do not exist (``_abs/`` copies: whose committed twin does not)."""
    doc = yaml.safe_load(config.read_text()) or {}
    project = doc.get("project") or {}
    ws_root = (config.parent / project.get("ws_root", ".")).resolve()
    pdk = (project.get("tech_spec") or {}).get("name", "")
    missing = []
    for ref in _named_files(doc):
        if ref.startswith(ABS_PREFIX):
            if len(_abs_twin(ref, pdk, ws_root)) != 1:
                missing.append(f"{ref} (no single committed twin raw/<accession>_*/{pdk}/…)")
        elif not (ws_root / ref).is_file():
            missing.append(ref)
    return missing


@pytest.mark.parametrize("config", _configs(), ids=lambda p: str(p.relative_to(paths.db_root())))
def test_every_raw_optimize_config_names_files_that_exist(config):
    assert missing_files(config) == []


@pytest.mark.parametrize("config", _configs(), ids=lambda p: str(p.relative_to(paths.db_root())))
def test_every_raw_optimize_config_names_an_engine_the_platform_runs(config):
    """``optimizer_config.type`` resolves through the platform's engine selector (B-ADB-1)."""
    doc = yaml.safe_load(config.read_text()) or {}
    engine = ((doc.get("project") or {}).get("optimizer_config") or {}).get("type", "")
    optimizer_type_from_config(SimpleNamespace(optimizer_config=SimpleNamespace(type=engine)))


def test_the_engine_check_refuses_ax():
    """The resolver the check above calls refuses ``ax``, the name the three ``_ax`` files had."""
    with pytest.raises(ValueError, match="not a known engine"):
        optimizer_type_from_config(SimpleNamespace(optimizer_config=SimpleNamespace(type="ax")))


def test_the_scan_covers_the_authored_and_the_generated_configs():
    rel = {str(p.relative_to(paths.db_root())) for p in _configs()}
    assert "raw_optimize/amp_001_5t.yaml" in rel
    assert "raw_optimize/generated/amp_001_5t.yaml" in rel
    assert any(r.startswith("raw_optimize/generated/amp_032_ax") for r in rel)


def test_the_abs_prefix_is_the_gitignored_local_copy_dir():
    """The ``_abs/`` rule depends on the ``.gitignore`` entry; this test fails if it is removed."""
    ignored = (paths.db_root() / ".gitignore").read_text().splitlines()
    assert ABS_PREFIX in ignored


def test_retired_configs_stay_retired():
    root = paths.db_root() / "raw_optimize"
    assert not (root / "ia_004_fan_chopper_rrl.yaml").exists()
    assert not (root / "generated" / "amp_020_two_stage_miller_cmfb.yaml").exists()


# ---------------------------------------------------------------- the check itself, on tmp configs


def _write(tmp_path: Path, project: dict) -> Path:
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(yaml.safe_dump({"project": project}))
    return cfg


def test_a_missing_testbench_deck_is_reported(tmp_path):
    db = paths.db_root()
    cfg = _write(
        tmp_path,
        {
            "ws_root": str(db),
            "netlist": "raw/amp_001_5t/ihp-sg13g2/dc_op.spice",
            "testbenches": [
                {"netlist": "raw/amp_001_5t/ihp-sg13g2/dc_op.spice"},
                {"netlist": "raw/ia_004_fan_chopper_rrl/ihp-sg13g2/ac_closed_loop.spice"},
            ],
        },
    )
    assert missing_files(cfg) == ["raw/ia_004_fan_chopper_rrl/ihp-sg13g2/ac_closed_loop.spice"]


def test_a_missing_top_level_netlist_and_params_file_are_reported(tmp_path):
    cfg = _write(
        tmp_path,
        {
            "ws_root": str(paths.db_root()),
            "netlist": "raw/no_such_circuit/ihp-sg13g2/dc_op.spice",
            "params_file": "circuits/no_such_circuit/abstract/params.yaml",
        },
    )
    assert missing_files(cfg) == [
        "raw/no_such_circuit/ihp-sg13g2/dc_op.spice",
        "circuits/no_such_circuit/abstract/params.yaml",
    ]


def test_ws_root_resolves_against_the_config_directory(tmp_path):
    (tmp_path / "decks").mkdir()
    (tmp_path / "decks" / "tb.spice").write_text("* tb\n")
    sub = tmp_path / "configs"
    sub.mkdir()
    cfg = sub / "cfg.yaml"
    cfg.write_text(yaml.safe_dump({"project": {"ws_root": "..", "netlist": "decks/tb.spice"}}))
    assert missing_files(cfg) == []
    cfg.write_text(yaml.safe_dump({"project": {"ws_root": ".", "netlist": "decks/tb.spice"}}))
    assert missing_files(cfg) == ["decks/tb.spice"]


@pytest.mark.parametrize(
    ("ref", "pdk", "reported"),
    [
        pytest.param("raw_optimize/_abs/amp_032/dc_op.spice", "gf180mcu", False, id="twin-exists"),
        pytest.param(
            "raw_optimize/_abs/amp_032/no_such_bench.spice", "gf180mcu", True, id="no-deck"
        ),
        pytest.param("raw_optimize/_abs/amp_032/dc_op.spice", "no-such-pdk", True, id="no-pdk"),
        pytest.param("raw_optimize/_abs/amp_999/dc_op.spice", "gf180mcu", True, id="no-accession"),
    ],
)
def test_an_abs_copy_needs_its_committed_twin(tmp_path, ref, pdk, reported):
    cfg = _write(
        tmp_path,
        {
            "ws_root": str(paths.db_root()),
            "tech_spec": {"name": pdk},
            "testbenches": [{"netlist": ref}],
        },
    )
    assert bool(missing_files(cfg)) is reported
