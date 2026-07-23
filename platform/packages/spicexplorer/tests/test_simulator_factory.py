"""Backend factory dispatch + orchestrator routing + the optional YAML selector.

Proves: `resolve_engine` normalises every engine spelling; `build_simulator` dispatches
ngspice → `NGSpice_Wrapper` and non-ngspice → the right (failing-offline) branch; the
optional `Project_Setup.sim_engine` field defaults to ngspice and rejects typos; and the
orchestrator routes construction through the factory and hands ANY protocol-conformant
backend to the (engine-neutral) optimizer loop. The spectre builder's own guards — a
non-.scs netlist (no translated deck) and the missing optional bridge — are
asserted offline.
"""

from __future__ import annotations

import dataclasses
import importlib.util
from pathlib import Path

import pytest
from _spicexplorer_fixtures import REPO_ROOT, requires_ngspice
from spicexplorer.backends.spectre import SpectreSimResult  # noqa: F401  (import-graph sanity)
from spicexplorer.core.domains import Project_Setup, SpiceSimulatorType
from spicexplorer.optimization import orchestrator as orch_mod
from spicexplorer.optimization.orchestrator import (
    Circuit_Optimizer_Orchestrator_with_SPICE,
    Optimizer_Type_Enum,
)
from spicexplorer.optimization.simulator_factory import (
    SIMULATOR_BUILDERS,
    build_simulator,
    resolve_engine,
)
from spicexplorer_core.spice_engine import NGSpice_Wrapper, Sim_Engines_Type

EXAMPLE_YAML = REPO_ROOT / "examples/OTA/cascode/ihp-sg13g2/sizing/project_setup.yaml"

RC_DECK = """* RC low-pass
V1 in 0 dc 0 ac 1
R1 in out 1k
C1 out 0 100p
.ac dec 5 1k 1Meg
.end
"""


class _FakeSimulator:
    """A structural Simulator that is NOT an NGSpice_Wrapper (for the routing test)."""

    def update_params(self, params: dict[str, float]) -> bool:  # noqa: D401
        return True

    def apply_corner(self, corner: object, *, model_lib_root: str | None = None) -> None: ...

    def run(self, *, label: str | None = None) -> object:  # pragma: no cover - not called here
        return object()

    def submit(self, *, label: str | None = None) -> object:  # pragma: no cover
        return object()


# ---------------------------------------------------------------------------
# resolve_engine
# ---------------------------------------------------------------------------
def test_resolve_engine_accepts_every_spelling() -> None:
    assert resolve_engine(None) is SpiceSimulatorType.NGSPICE
    assert resolve_engine("ngspice") is SpiceSimulatorType.NGSPICE
    assert resolve_engine("  NGSPICE ") is SpiceSimulatorType.NGSPICE
    assert resolve_engine("spectre") is SpiceSimulatorType.SPECTRE
    assert resolve_engine(SpiceSimulatorType.HSPICE) is SpiceSimulatorType.HSPICE
    # core's Sim_Engines_Type.NGSPICE maps by value
    assert resolve_engine(Sim_Engines_Type.NGSPICE) is SpiceSimulatorType.NGSPICE


def test_resolve_engine_rejects_unknown_and_non_overlapping() -> None:
    with pytest.raises(ValueError, match="Unknown sim_engine"):
        resolve_engine("verilog-a")
    # ltspice exists in Sim_Engines_Type but has no SpiceSimulatorType equivalent
    with pytest.raises(ValueError, match="no SpiceSimulatorType equivalent"):
        resolve_engine(Sim_Engines_Type.LTSPICE)


def test_every_enum_member_has_a_builder() -> None:
    assert set(SIMULATOR_BUILDERS) == set(SpiceSimulatorType)


# ---------------------------------------------------------------------------
# build_simulator dispatch
# ---------------------------------------------------------------------------
@requires_ngspice
def test_build_simulator_ngspice_returns_wrapper(tmp_path: Path) -> None:
    deck = tmp_path / "rc.cir"
    deck.write_text(RC_DECK)
    sim = build_simulator(
        "ngspice",
        netlist_filename=deck,
        testbench_name="rc",
        output_folder=tmp_path / "runs",
    )
    assert isinstance(sim, NGSpice_Wrapper)


@pytest.mark.skipif(
    importlib.util.find_spec("virtuoso_bridge") is not None,
    reason="tests the ImportError guard; needs a venv without virtuoso-bridge",
)
def test_build_simulator_spectre_offline_reaches_the_lazy_adapter(tmp_path: Path) -> None:
    # virtuoso-bridge is not installed in the ngspice-only venv, so dispatch reaching the
    # spectre builder surfaces as an actionable ImportError (never a silent ngspice fallback).
    with pytest.raises(ImportError, match="virtuoso-bridge"):
        build_simulator("spectre", netlist_filename=tmp_path / "tb.scs")


def test_build_simulator_spectre_rejects_non_scs_netlist(tmp_path: Path) -> None:
    # Until the P2 ngspice→.scs translator lands, only a hand-written Spectre deck can
    # flow. An ngspice deck must fail BEFORE the lazy bridge import, with the pointer
    # at P2 — not a misleading "bridge not installed".
    with pytest.raises(NotImplementedError, match=r"\.scs"):
        build_simulator("spectre", netlist_filename=tmp_path / "tb.cir")


def test_build_simulator_hspice_is_registered_but_unimplemented(tmp_path: Path) -> None:
    with pytest.raises(NotImplementedError, match="HSPICE"):
        build_simulator("hspice", netlist_filename=tmp_path / "tb.sp")


# ---------------------------------------------------------------------------
# Project_Setup.sim_engine field
# ---------------------------------------------------------------------------
def test_sim_engine_defaults_to_ngspice_and_is_backward_compatible() -> None:
    # the committed example never mentions sim_engine → the default applies
    p = Project_Setup.from_yaml(EXAMPLE_YAML)
    assert p.sim_engine == "ngspice"


def test_sim_engine_normalised_and_typos_rejected() -> None:
    p = Project_Setup.from_yaml(EXAMPLE_YAML)
    # case-insensitive normalisation via a re-construction through __post_init__
    normalised = dataclasses.replace(p, sim_engine="SPECTRE")
    assert normalised.sim_engine == "spectre"
    with pytest.raises(ValueError, match="Unknown sim_engine"):
        dataclasses.replace(p, sim_engine="totally-bogus")


# ---------------------------------------------------------------------------
# Engine-neutral analysis vocabulary
# ---------------------------------------------------------------------------
def test_target_spec_analysis_string_round_trips_every_simtype() -> None:
    """`TargetSpec.get_analysis()` (the reverse map the engine-neutral scoring path
    uses) must land on the SAME ngspice plot the legacy
    `get_equivalent_ngspice_plot_type()` selected — for the specs the example YAML
    actually carries AND for the full SimType vocabulary."""
    from spicexplorer.core.domains import SIMTYPE_TO_NGSPICE_PLOTTYPE
    from spicexplorer_core.spice_engine import resolve_ngspice_plot_type

    p = Project_Setup.from_yaml(EXAMPLE_YAML)
    for spec in p.optimizer_config.target_specs.targets:
        analysis = spec.get_analysis()
        assert resolve_ngspice_plot_type(analysis) is spec.get_equivalent_ngspice_plot_type(), spec.name

    for st, pt in SIMTYPE_TO_NGSPICE_PLOTTYPE.items():
        assert resolve_ngspice_plot_type(st.value) is pt, st


# ---------------------------------------------------------------------------
# Orchestrator routing
# ---------------------------------------------------------------------------
@requires_ngspice
def test_orchestrator_routes_ngspice_through_factory(tmp_path: Path) -> None:
    orch = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=EXAMPLE_YAML,
        optimizer_type=Optimizer_Type_Enum.NEVERGRAD_CONSTRAINT,
    )
    wrappers = orch.get_spicelib_wrapper()
    assert wrappers
    assert all(isinstance(w, NGSpice_Wrapper) for w in wrappers.values())


def test_orchestrator_hands_any_protocol_backend_to_the_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    # auto_load=False: build wrappers manually with build_simulator stubbed to return a
    # non-ngspice (but protocol-conformant) backend. The loop is engine-neutral now, so
    # the orchestrator hands it through instead of raising (the old NGSpice-only guard).
    from spicexplorer_core.spice_engine import Simulator

    orch = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=EXAMPLE_YAML,
        optimizer_type=Optimizer_Type_Enum.NEVERGRAD_CONSTRAINT,
        auto_load=False,
    )
    orch.project_setup.sim_engine = "spectre"
    monkeypatch.setattr(orch_mod, "build_simulator", lambda *a, **k: _FakeSimulator())
    wrappers = orch.create_spicelib_wrappers()
    assert wrappers, "expected one wrapper per enabled testbench"
    assert all(isinstance(w, _FakeSimulator) for w in wrappers.values())
    assert all(isinstance(w, Simulator) for w in wrappers.values())  # runtime protocol check
