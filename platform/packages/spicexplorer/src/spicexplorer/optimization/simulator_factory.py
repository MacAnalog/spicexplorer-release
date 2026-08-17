"""Backend factory — build a `Simulator` from an engine enum.

Replaces the hardcoded `NGSpice_Wrapper(...)` construction at the orchestrator call site
with a dispatch keyed off the platform's *existing* engine enums — the ones that were
dead-but-aspirational until now: `spicexplorer.core.domains.SpiceSimulatorType`
(`ngspice`/`spectre`/`hspice`) and `spicexplorer_core.spice_engine.Sim_Engines_Type`
(`ngspice`/`ltspice`/`xyce`). Everything downstream (`evaluate`/`compute_fitness`/
`optimize`/checkpoints/PVT) is engine-agnostic numpy and stays untouched.

`ngspice` is the default; the `spectre` builder constructs the optional, lazily-imported Spectre
adapter (so ngspice-only users pull in no Cadence dependency); `layout` builds the
layout-flow backend (`backends/layout.py`: build → DRC → LVS → PEX → measure over a
generator's knobs; leaf tools lazily imported — the `layout` extra); `hspice` is a
registered-but-unimplemented stub. The registry (`SIMULATOR_BUILDERS`) is the extension
point: a new backend is one entry.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict

from spicexplorer.core.domains import SpiceSimulatorType
from spicexplorer_core.spice_engine import (
    NGSpice_Wrapper,
    Sim_Engines_Type,
    Sim_Execution_Type,
)

if TYPE_CHECKING:
    from spicexplorer_core.spice_engine import Simulator


def resolve_engine(
    value: "SpiceSimulatorType | Sim_Engines_Type | str | None",
) -> SpiceSimulatorType:
    """Normalise any engine spelling to a `SpiceSimulatorType`.

    Accepts a `SpiceSimulatorType`, a core `Sim_Engines_Type` (mapped by value — only
    `ngspice` overlaps the two enums; `ltspice`/`xyce` have no `SpiceSimulatorType` and
    raise), a case-insensitive string, or `None` (→ ngspice default).
    """
    if value is None:
        return SpiceSimulatorType.NGSPICE
    if isinstance(value, SpiceSimulatorType):
        return value
    if isinstance(value, Sim_Engines_Type):
        try:
            return SpiceSimulatorType(value.value)
        except ValueError as exc:
            raise ValueError(
                f"Sim_Engines_Type.{value.name} has no SpiceSimulatorType equivalent "
                f"(only 'ngspice' overlaps). Valid: {[e.value for e in SpiceSimulatorType]}."
            ) from exc
    if isinstance(value, str):
        try:
            return SpiceSimulatorType(value.strip().lower())
        except ValueError as exc:
            raise ValueError(
                f"Unknown sim_engine {value!r}; valid: {[e.value for e in SpiceSimulatorType]}."
            ) from exc
    raise TypeError(f"Cannot resolve engine from {type(value).__name__}: {value!r}")


# ---------------------------------------------------------------------------
# Per-engine builders — each takes the normalised kwargs dict, returns a Simulator
# ---------------------------------------------------------------------------
def _build_ngspice(kw: Dict[str, Any]) -> "Simulator":
    return NGSpice_Wrapper(
        testbench_name=kw["testbench_name"],
        netlist_filename=kw["netlist_filename"],
        output_folder=kw["output_folder"],
        sim_execution_t=kw["sim_execution_t"],
        path_to_simulator=kw["path_to_simulator"],
        verbose=kw["verbose"],
    )


def _build_spectre(kw: Dict[str, Any]) -> "Simulator":
    # A testbench is a native Spectre `.scs` file (the YAML `netlist:` key, exactly like
    # an ngspice `.spice`). It runs in NATIVE-FILE mode: every candidate rewrites the
    # deck's `parameters` line (design vars) + corner includes in place — the injection
    # path, since the bridge runs a fixed file per run and in local mode drops its
    # `params` arg (verified 2026-07-06). `work_dir` persists the PSF raw dir the OCEAN
    # metric path reads; `deck_dir` holds the per-candidate `.scs`. Reject a non-`.scs`
    # BEFORE the lazy bridge import so the offline error is the actionable one.
    netlist = Path(kw["netlist_filename"])
    if netlist.suffix.lower() != ".scs":
        raise NotImplementedError(
            f"sim_engine='spectre' needs a native Spectre testbench netlist (.scs); got "
            f"{netlist.name!r}. Point the testbench `netlist:` at a hand-written Spectre "
            f"deck (its `parameters` line carries the design vars, injected per candidate). "
            f"To port an ngspice deck, translate it via "
            f"spicexplorer.backends.spectre_deck.deck_spec_from_ngspice(...) (opt-in "
            f"import path); or use sim_engine='ngspice'."
        )

    # Lazy: importing the adapter is Cadence-free, but constructing it pulls in the
    # optional virtuoso-bridge (raises a clear ImportError when absent — the ngspice-only
    # case). `vb_env` is pre-set inside the factory to suppress the bridge's `.env` leak.
    from spicexplorer.backends.spectre import create_spectre_simulator

    return create_spectre_simulator(
        native_scs=netlist,
        deck_dir=kw.get("deck_dir"),
        vb_env=kw.get("vb_env"),
        vb_env_file=kw.get("vb_env_file"),
        work_dir=kw.get("work_dir"),
    )


def _build_layout(kw: Dict[str, Any]) -> "Simulator":
    # A layout-flow "testbench": the YAML `netlist:` is a `layout-flow/1` YAML spec (the
    # generator + DRC/LVS/PEX/measure recipe), NOT a SPICE deck. Reject a non-YAML BEFORE the
    # lazy import so the offline error is the actionable one. Artifacts land per testbench
    # under `<outdir>/layout/<tb>/run_<n>_<label>/` (GDS, drc/, lvs/, pex/, summary.json).
    spec_path = Path(kw["netlist_filename"])
    if spec_path.suffix.lower() not in (".yaml", ".yml"):
        raise NotImplementedError(
            f"sim_engine='layout' needs the testbench `netlist:` to be a layout-flow YAML spec "
            f"(schema layout-flow/1: generator/cell/drc/lvs/pex/measure), got {spec_path.name!r}. "
            f"See spicexplorer.backends.layout.LayoutFlowSpec and examples/layout/ihp-sg13g2/"
            f"5t_ota_gf/opt/flow.yaml."
        )
    # Lazy: the backend module imports only stdlib+yaml, but constructing the simulator pulls
    # in the leaf tools spicexplorer_layout + spicexplorer_signoff (the optional `layout` extra —
    # actionable ImportError when absent).
    from spicexplorer.backends.layout import create_layout_simulator

    tb_name = str(kw.get("testbench_name") or "layout")
    out_dir = Path(kw["output_folder"]) / "layout" / tb_name
    return create_layout_simulator(
        spec_path,
        output_folder=out_dir,
        testbench_name=tb_name,
        verbose=bool(kw.get("verbose", False)),
        # the project's `simulator:` (ngspice exe) — used by the flow's `postlayout` testbenches
        path_to_simulator=kw.get("path_to_simulator"),
    )


def _build_hspice(kw: Dict[str, Any]) -> "Simulator":
    raise NotImplementedError(
        "The HSPICE backend is registered but not implemented yet "
        "(see doc/plan_spectre_hspice_integration.md). Use sim_engine='ngspice'."
    )


#: Engine → builder. The extension point: a new backend is one entry here.
SIMULATOR_BUILDERS: Dict[SpiceSimulatorType, Callable[[Dict[str, Any]], "Simulator"]] = {
    SpiceSimulatorType.NGSPICE: _build_ngspice,
    SpiceSimulatorType.SPECTRE: _build_spectre,
    SpiceSimulatorType.HSPICE: _build_hspice,
    SpiceSimulatorType.LAYOUT: _build_layout,
}


def build_simulator(
    engine: "SpiceSimulatorType | Sim_Engines_Type | str | None",
    *,
    netlist_filename: Path,
    testbench_name: str = "DEFAULT",
    output_folder: Path = Path("./spicelib_runs"),
    sim_execution_t: Sim_Execution_Type = Sim_Execution_Type.RUN_AND_WAIT,
    path_to_simulator: Path | None = None,
    verbose: bool = False,
    vb_env: Dict[str, str] | None = None,
    work_dir: Path | None = None,
    deck_dir: Path | None = None,
    vb_env_file: Path | str | None = None,
) -> "Simulator":
    """Construct the simulation backend for `engine`, returning a `Simulator`.

    The ngspice path returns a concrete `NGSpice_Wrapper` (identical to the previous
    hardcoded construction — zero behaviour change for existing runs; the Spectre-only
    kwargs below are ignored by `_build_ngspice`). Other engines dispatch through
    `SIMULATOR_BUILDERS`.

    Spectre-only kwargs (native-first wiring, `doc/plan_virtuoso_bridge.md`): the
    testbench `netlist:` is a native `.scs` run in native-file injection mode; `work_dir`
    persists the PSF raw dir (OCEAN input); `deck_dir` is where per-candidate `.scs` files
    land; `vb_env_file` pins the bridge/OCEAN profile.
    """
    resolved = resolve_engine(engine)
    try:
        builder = SIMULATOR_BUILDERS[resolved]
    except KeyError as exc:  # pragma: no cover - every enum member is registered
        raise NotImplementedError(
            f"No simulator builder registered for engine {resolved.value!r}."
        ) from exc

    return builder(
        {
            "netlist_filename": netlist_filename,
            "testbench_name": testbench_name,
            "output_folder": output_folder,
            "sim_execution_t": sim_execution_t,
            "path_to_simulator": path_to_simulator,
            "verbose": verbose,
            "vb_env": vb_env,
            "work_dir": work_dir,
            "deck_dir": deck_dir,
            "vb_env_file": vb_env_file,
        }
    )


__all__ = ["resolve_engine", "build_simulator", "SIMULATOR_BUILDERS"]
