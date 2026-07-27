"""In-library integration of analog-db circuits — one router over open (ngspice) + closed (Spectre).

Reads a circuit's committed, NDA-clean binding YAMLs (``pdk/<pdk>/{sizing,corners}.yaml``,
``analyses/<id>.yaml``, ``datasheet.yaml``, and the shared ``_shared/pdk/<pdk>.yaml``
registry) and resolves them into ready-to-run pieces: the design-var sizing defaults, the
PDK core-rail supply, the PVT :class:`~spicexplorer_core.pvt.Corner`, the raw deck, the
analysis params, and the datasheet metric targets (recipe + spec band). This **de-bespokes**
what were hand-transcribed Python dicts in the amp_022 live tests — the same numbers now flow
from the repo's own binding data.

Two layers:

* **Loaders** (Layer A) — ``load_sizing``/``pdk_supply``/``resolve_corner``/``raw_deck_path``/
  ``load_analysis``/``load_datasheet_metrics`` turn the bindings into pieces.
* **Router** (Layer B) — :func:`run_circuit` runs an analog-db circuit through its *native*
  engine, chosen by the committed ``sim_engine`` marker in ``_shared/pdk/<pdk>.yaml``: open
  PDKs (ihp-sg13g2/sky130/gf180mcu → ``ngspice``) run their self-contained raw deck; the
  closed PDK (tsmc-n65 → ``spectre``) runs native Spectre via the virtuoso-bridge. Both yield
  an engine-neutral SimResult, so :meth:`CircuitRun.evaluate` scores the datasheet metrics off
  either through the *same* measurement registry. :func:`probe_engine` reports which engine a
  (circuit, pdk) routes to and whether it can run here — degrading like ``/api/library``.

NDA posture: only **generic** corner labels (``tt``/``ss``/``ff``) + a **neutral** wrapper
filename ever appear here or in git; the kit-section indirection lives in the
operator's out-of-repo ``model_lib_root`` wrapper (see analog-db ``_shared/pdk/<pdk>.yaml``).
Core ``pvt`` stays PDK-agnostic; this module reads analog-db **data** (it never imports the
analog-db package) and raises :class:`AnalogDbUnavailable` when the submodule/binding is
absent — the caller degrades exactly as the ``/api/library`` surface does.
"""

from __future__ import annotations

import logging
import math
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml
from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride

from .params import CircuitParams, load_params_file

_LOG = logging.getLogger(__name__)

__all__ = [
    "AnalogDbUnavailable",
    "EngineUnavailable",
    "EngineCapability",
    "MetricTarget",
    "MetricEval",
    "CircuitRun",
    "analog_db_root",
    "load_circuit_params",
    "load_sizing",
    "pdk_supply",
    "resolve_corner",
    "raw_deck_path",
    "load_analysis",
    "load_datasheet_metrics",
    "effective_supply",
    "circuit_class",
    "bench_ocean_measurements",
    "pdk_sim_engine",
    "list_circuits",
    "circuit_pdks",
    "circuit_analyses",
    "probe_engine",
    "build_ngspice_run",
    "build_spectre_run",
    "run_circuit",
]

_NGSPICE, _SPECTRE = "ngspice", "spectre"

#: analog-db testbench/analysis id → the engine-neutral analysis kind its metrics key off.
#: The unity-buffer disturbance benches (`cmrr_vcm`/`psrr_vdd`) and the closed-loop bench
#: are AC sweeps like `ac_open_loop` — only the deck stimulus differs; `linearity` is the
#: buffer-connected DC sweep (ICMR).
_TB_ANALYSIS: dict[str, str] = {
    "ac_open_loop": "ac",
    "ac_closed_loop": "ac",
    "cmrr_vcm": "ac",
    "psrr_vdd": "ac",
    "dc_op": "op",
    "noise": "noise",
    "tran_step": "tran",
    # thd/iip3 are engine-split: the ngspice lane runs the deck's tran (registry FFT
    # recipes, kind "tran"); the Spectre lane composes a native pss instead and
    # `CircuitRun.evaluate` swaps the recipes to their `*_pss` twins.
    "thd": "tran",
    "iip3": "tran",
    "linearity": "dc",
    "dc_sweep": "dc",
    # loop-gain probe: Spectre-lane payload only (ngspice runs the deck's closed-loop AC;
    # the stb.stb loopGain wave feeds {meas: pm_loop|gain_margin_db|loopgain_db})
    "stb": "stb",
    # golden chopper benches: Spectre-lane payloads only — a PSS+PAC gain / Z_in
    # and a PSS+pnoise chopped-noise read on the RUNNING-clock configuration (ngspice has
    # no PSS; its lane keeps the transient-domain approximations tran_chopper_ripple /
    # tran_zin_chopped). Figures ride the registry route ({meas: gain_cl|zin_mag,
    # analysis: pac} / {meas: onoise_pnoise_total}), not datasheet conformance.
    "pac_gain": "pac",
    "pac_zin": "pac",
    "pnoise_chopped": "pnoise",
}

# analog-db analysis-id → engine-neutral analysis kind the measurement registry keys off
# (same vocabulary as the testbench map — datasheet `analysis:` ids ARE testbench ids).
_ANALYSIS_KIND: dict[str, str] = _TB_ANALYSIS


class AnalogDbUnavailable(RuntimeError):
    """The analog-db submodule, or a required binding file, is not checked out."""


@dataclass(frozen=True)
class MetricTarget:
    """One datasheet metric: the registry recipe + its engine-neutral analysis + spec band."""

    name: str
    recipe: dict[str, Any]  # ``{meas, out, …}`` — fed straight to ``registry.measure``
    analysis: str  # engine-neutral analysis KIND: ``ac``/``op``/``noise``/``tran``/``dc``
    spec_min: float | None = None
    spec_max: float | None = None
    #: the datasheet's own ``analysis:`` id (a testbench id, e.g. ``cmrr_vcm``). Evaluation
    #: matches on THIS, not the kind — `ac_open_loop`, `cmrr_vcm` and `ac_closed_loop` are
    #: all kind ``ac`` but score different decks (dcgain off the CMRR residual is not a gain).
    analysis_id: str = ""

    def satisfied(self, value: float) -> bool:
        """True iff ``value`` is finite and inside ``[spec_min, spec_max]`` (either bound optional)."""
        if not math.isfinite(value):
            return False
        if self.spec_min is not None and value < self.spec_min:
            return False
        if self.spec_max is not None and value > self.spec_max:
            return False
        return True


def analog_db_root(explicit: str | os.PathLike[str] | None = None) -> Path:
    """The analog-db checkout root.

    Resolution order: ``explicit`` → ``$SPICEXPLORER_ANALOG_DB`` → ``<project_root>/examples/
    analog-db`` (the same order the live tests use, so a worktree with an empty submodule can
    point at a populated shared checkout).
    """
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("SPICEXPLORER_ANALOG_DB")
    if env:
        return Path(env).expanduser()
    from spicexplorer_core import project_root

    return project_root() / "examples/analog-db"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AnalogDbUnavailable(f"analog-db binding not found: {path}")
    with path.open() as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise AnalogDbUnavailable(f"malformed analog-db binding (not a mapping): {path}")
    return data


def _circuit_dir(circuit: str, root: str | os.PathLike[str] | None) -> Path:
    return analog_db_root(root) / "circuits" / circuit


def load_sizing(circuit: str, pdk: str, *, root: str | os.PathLike[str] | None = None) -> dict[str, str]:
    """``{var: default}`` design-var defaults from ``pdk/<pdk>/sizing.yaml`` (eng-strings kept verbatim)."""
    data = _load_yaml(_circuit_dir(circuit, root) / "pdk" / pdk / "sizing.yaml")
    return {
        str(v["name"]): str(v["default"])
        for v in data.get("variables", [])
        if "name" in v and "default" in v
    }


def load_circuit_params(
    circuit: str, *, root: str | os.PathLike[str] | None = None
) -> CircuitParams | None:
    """The circuit's ``abstract/params.yaml`` (``spicexplorer/params@1``), or ``None``.

    Layer-A loader for the DUT-parameterization contract: the atomic
    per-instance inventory plus the shipped
    default tying (``groups:``/``ratios:``). Adoption is per circuit — an **absent** file
    returns ``None`` (no behavior change anywhere); a *malformed* file raises
    ``spicexplorer.backends.params.ParamsError`` loudly. Group/atomic knob resolution and
    the ``ungroup:`` shadowing semantics live in :mod:`spicexplorer.backends.params`; the
    optimizer-projection wiring (``params_file:`` + ``ungroup:`` YAML keys) in
    ``Project_Setup.from_yaml``. Note the in-library runners (:func:`run_circuit` /
    :func:`build_ngspice_run` / :func:`build_spectre_run`) run the committed decks at
    their defaults, where a dissolved tie is numerically identical to the shipped one —
    ``ungroup:`` only matters where symbols are *swept*, i.e. in a projection.
    """
    path = _circuit_dir(circuit, root) / "abstract" / "params.yaml"
    if not path.is_file():
        return None
    return load_params_file(path)


def pdk_supply(pdk: str, *, root: str | os.PathLike[str] | None = None) -> float:
    """Nominal core-rail supply (V) from ``_shared/pdk/<pdk>.yaml`` (``supply.default``/``typical``)."""
    data = _load_yaml(analog_db_root(root) / "_shared/pdk" / f"{pdk}.yaml")
    supply = data.get("supply") or {}
    value = supply.get("default", supply.get("typical"))
    if value is None:
        raise AnalogDbUnavailable(f"{pdk} registry has no supply.default/.typical")
    return float(value)


def resolve_corner(
    circuit: str,
    pdk: str,
    label: str = "tt",
    *,
    root: str | os.PathLike[str] | None = None,
    temp: float = 27.0,
    supply_node: str = "VDD",
) -> Corner:
    """**Layer A — the generic→kit corner shim.**

    Reads the circuit's ``pdk/<pdk>/corners.yaml`` (a generic label → neutral
    ``[{lib_file, section}]`` list) + the PDK supply, and builds a core :class:`Corner`. The
    ``lib_file``/``section`` stay **generic + neutral** (e.g. ``tt`` on
    ``tsmc_n65_models.scs``); the operator's ``model_lib_root`` wrapper does the kit-section
    indirection at run time, and ``apply_corner`` prepends ``model_lib_root``
    to the ``lib_file``. Raises :class:`AnalogDbUnavailable` for a missing binding and
    ``KeyError`` for an unknown corner label.
    """
    data = _load_yaml(_circuit_dir(circuit, root) / "pdk" / pdk / "corners.yaml")
    corners = data.get("corners") or {}
    if label not in corners:
        raise KeyError(
            f"corner {label!r} not in the {pdk} binding for {circuit}; have {sorted(corners)}"
        )
    includes = [
        ModelInclude(lib_file=str(inc["lib_file"]), section=str(inc["section"]))
        for inc in corners[label]
    ]
    return Corner(
        name=f"{pdk}_{label}",
        model_includes=includes,
        temp=float(temp),
        supplies=[SupplyOverride(node=supply_node, value=pdk_supply(pdk, root=root))],
    )


def raw_deck_path(
    circuit: str, pdk: str, testbench: str, *, root: str | os.PathLike[str] | None = None
) -> Path:
    """The ngspice raw deck for a testbench: ``raw/<circuit>/<pdk>/<testbench>.spice``."""
    path = analog_db_root(root) / "raw" / circuit / pdk / f"{testbench}.spice"
    if not path.is_file():
        raise AnalogDbUnavailable(f"analog-db raw deck not found: {path}")
    return path


def load_analysis(
    circuit: str, analysis_id: str, *, root: str | os.PathLike[str] | None = None
) -> dict[str, Any]:
    """The analysis descriptor (``analyses/<id>.yaml``) — ``params``/``produces``/``template``."""
    return _load_yaml(_circuit_dir(circuit, root) / "analyses" / f"{analysis_id}.yaml")


def circuit_class(circuit: str, *, root: str | os.PathLike[str] | None = None) -> str:
    """The circuit's class id (``circuit.yaml class:``) — the key the per-class engine
    configs (testbench templates, ``spectre-benches.yaml``) are filed under."""
    return str(_load_yaml(_circuit_dir(circuit, root) / "circuit.yaml").get("class", "amplifier"))


def differential_output(
    circuit: str, *, root: str | os.PathLike[str] | None = None
) -> tuple[str, str] | None:
    """``(voutp, voutn)`` if the DUT has a DIFFERENTIAL output pair and no single-ended
    ``vout``, else ``None`` — read from the canonical ``circuit.yaml ports:`` manifest.

    A fully-differential amp exposes ``voutp``/``voutn`` (no ``vout``); its gain/UGF/PM must
    be read on the DIFFERENCE ``v(voutp)-v(voutn)`` and its noise output taken across the pair,
    not the non-existent single-ended ``v(vout)``. This is the pipeline-level source of truth
    the Spectre analysis composition + calculator route consult (the campaign generator's
    per-deck detection, promoted here so every consumer — /api/library, notebooks — is FD-aware)."""
    ports = _load_yaml(_circuit_dir(circuit, root) / "circuit.yaml").get("ports") or []
    lows = {str(p).lower() for p in ports}
    if "voutp" in lows and "voutn" in lows and "vout" not in lows:
        return ("voutp", "voutn")
    return None


def load_datasheet_metrics(
    circuit: str,
    *,
    root: str | os.PathLike[str] | None = None,
    out: str = "vout",
    only: Iterable[str] | None = None,
) -> list[MetricTarget]:
    """Datasheet metric targets (``datasheet.yaml``) as registry recipes + spec bands.

    Each metric's ``extract: {meas: …}`` becomes a ``{meas, out}`` recipe (``out`` is the
    output port, ``vout`` by amplifier convention); its ``spec: {min?, max?}`` becomes the
    pass band. ``only`` restricts to named metrics (e.g. the AC trio). Metrics without an
    ``extract.meas`` (or op-point/noise metrics that need a different signal key) are skipped
    unless selected — pass an explicit ``out`` and ``only`` for those.
    """
    data = _load_yaml(_circuit_dir(circuit, root) / "datasheet.yaml")
    want = set(only) if only is not None else None
    targets: list[MetricTarget] = []
    for name, meta in (data.get("metrics") or {}).items():
        if want is not None and name not in want:
            continue
        extract = meta.get("extract") or {}
        meas = extract.get("meas")
        if not meas:
            continue
        recipe: dict[str, Any] = {"meas": str(meas), "out": out}
        recipe.update({k: v for k, v in extract.items() if k != "meas"})
        spec = meta.get("spec") or {}
        targets.append(
            MetricTarget(
                name=str(name),
                recipe=recipe,
                analysis=_ANALYSIS_KIND.get(str(meta.get("analysis", "")), "ac"),
                spec_min=_maybe_float(spec.get("min")),
                spec_max=_maybe_float(spec.get("max")),
                analysis_id=str(meta.get("analysis", "")),
            )
        )
    return targets


def _maybe_float(value: Any) -> float | None:
    """Parse a datasheet spec bound to a float, or ``None`` when there is no numeric bound.

    Datasheets spell an *unbounded* side as ``any`` (e.g. ``vn_in: {max: any}`` — noise is
    reported, not gated); an empty/``none`` string means the same. Treat all of these as "no
    bound" rather than crashing ``float('any')`` (which took down every metric on 23 circuits'
    ``evaluate()`` path). A genuinely malformed numeric still raises."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in ("", "any", "none", "n/a", "-"):
        return None
    return float(value)


def effective_supply(
    circuit: str, pdk: str, testbench: str = "ac_open_loop", *, root: str | os.PathLike[str] | None = None
) -> dict[str, float | None]:
    """**The supply source-of-truth pin** — ``{"pdk_rail", "deck_vdd", "open_lane", "closed_lane"}``.

    Two supplies exist and they answer different questions:

    * ``deck_vdd`` — the analyses binding's ``VDD`` param (``analyses/<tb>.yaml``): the
      circuit's *authored operating point*, one value per circuit across ALL its PDKs,
      baked into the committed raw decks at render time.
    * ``pdk_rail`` — the per-PDK registry rail (``_shared/pdk/<pdk>.yaml supply.default``):
      the *process* core-rail limit.

    Lane precedence (what actually runs): the **open (ngspice) lane executes the deck as
    committed** — ``deck_vdd`` — at every corner (a corner swap changes process section +
    temperature, never the operating point). The **closed (Spectre) lane always injects
    ``pdk_rail``** (``build_spectre_run``'s parameter override + the resolved Corner), because
    the closed PDK's devices are rated for *its* rail — e.g. amp_022's analyses bake 1.5 V
    while tsmc-n65 runs 1.2 V. When the two differ, that divergence is by design; surface it
    (this helper exists so notebooks/UI can) rather than "fixing" either number.
    """
    params = load_analysis(circuit, testbench, root=root).get("params", {})
    rail = pdk_supply(pdk, root=root)
    deck_vdd = params.get("VDD")
    if deck_vdd is not None:
        from spicexplorer_core.eng import parse_value

        deck_vdd = float(parse_value(str(deck_vdd)))
    return {
        "pdk_rail": rail,
        "deck_vdd": deck_vdd,
        "open_lane": deck_vdd if deck_vdd is not None else rail,
        "closed_lane": rail,
    }


# ===========================================================================
# Layer B — engine-capability probe + in-library run builders behind ONE router
# ===========================================================================
# The platform reads analog-db as *data* and routes a (circuit, pdk) to its native engine
# via the committed ``sim_engine`` marker — never importing the analog-db package. Open PDKs
# run their self-contained ngspice raw deck; the closed PDK runs native Spectre via the bridge.


class EngineUnavailable(RuntimeError):
    """The routed simulation engine for a (circuit, pdk) cannot run in this environment."""


@dataclass(frozen=True)
class EngineCapability:
    """The router verdict: which engine a (circuit, pdk) routes to, and whether it runs here."""

    circuit: str
    pdk: str
    engine: str | None  # ``ngspice`` | ``spectre`` | None (no marker / no binding)
    available: bool
    reason: str

    def __bool__(self) -> bool:  # ``if probe_engine(...):``
        return self.available


def _pdk_registry(pdk: str, root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """The ``_shared/pdk/<pdk>.yaml`` registry dict (raises :class:`AnalogDbUnavailable`)."""
    return _load_yaml(analog_db_root(root) / "_shared/pdk" / f"{pdk}.yaml")


def pdk_sim_engine(pdk: str, *, root: str | os.PathLike[str] | None = None) -> str | None:
    """The committed native ``sim_engine`` marker for a PDK (``ngspice``/``spectre``), or None.

    The router's source of truth — a *data* marker in ``_shared/pdk/<pdk>.yaml``, so the
    platform learns a PDK's engine without importing the analog-db package.
    """
    return _pdk_registry(pdk, root).get("sim_engine")


def list_circuits(*, root: str | os.PathLike[str] | None = None) -> list[str]:
    """Sorted circuit ids in the analog-db ``circuits/`` tree (those with a ``circuit.yaml``)."""
    base = analog_db_root(root) / "circuits"
    if not base.is_dir():
        raise AnalogDbUnavailable(f"analog-db circuits/ not found: {base}")
    return sorted(p.name for p in base.iterdir() if (p / "circuit.yaml").is_file())


def circuit_pdks(circuit: str, *, root: str | os.PathLike[str] | None = None) -> list[str]:
    """Sorted PDKs a circuit is bound for (``circuits/<id>/pdk/<pdk>/``)."""
    base = _circuit_dir(circuit, root) / "pdk"
    if not base.is_dir():
        raise AnalogDbUnavailable(f"{circuit} has no pdk/ bindings: {base}")
    return sorted(p.name for p in base.iterdir() if p.is_dir())


def circuit_analyses(circuit: str, *, root: str | os.PathLike[str] | None = None) -> list[str]:
    """Sorted analysis ids a circuit defines (``circuits/<id>/analyses/<id>.yaml``)."""
    base = _circuit_dir(circuit, root) / "analyses"
    return sorted(p.stem for p in base.glob("*.yaml")) if base.is_dir() else []


def probe_engine(
    circuit: str,
    pdk: str,
    *,
    root: str | os.PathLike[str] | None = None,
    model_lib_root: str | os.PathLike[str] | None = None,
) -> EngineCapability:
    """Route a (circuit, pdk) to an engine and report whether it can run **here**.

    Reads the committed ``sim_engine`` marker, confirms the circuit carries that PDK binding,
    then checks the environment for the routed engine: ngspice on PATH (open lane), or a
    virtuoso-bridge + Cadence env + the operator's neutral corner wrapper at ``model_lib_root``
    (closed lane; the wrapper filename comes from the registry's ``corners.lib_file``). Never
    raises for a *missing* capability — it returns ``available=False`` + a human ``reason`` so a
    caller degrades exactly like the ``/api/library`` surface.
    """

    def cap(engine: str | None, ok: bool, reason: str) -> EngineCapability:
        return EngineCapability(circuit=circuit, pdk=pdk, engine=engine, available=ok, reason=reason)

    try:
        registry = _pdk_registry(pdk, root)
    except AnalogDbUnavailable as exc:
        return cap(None, False, str(exc))
    engine = registry.get("sim_engine")
    if engine is None:
        return cap(None, False, f"{pdk} registry has no sim_engine marker")
    if not (_circuit_dir(circuit, root) / "pdk" / pdk).is_dir():
        return cap(engine, False, f"{circuit} has no {pdk} binding")

    if engine == _NGSPICE:
        from spicexplorer_core.env import probe_ngspice

        ng = probe_ngspice()
        if not ng["ngspice_ok"]:
            return cap(engine, False, "ngspice not on PATH")
        return cap(
            engine,
            True,
            f"ngspice at {ng['ngspice_path']} (open-PDK models resolved on the sourcepath at run time)",
        )

    if engine == _SPECTRE:
        reasons: list[str] = []
        try:
            import virtuoso_bridge  # noqa: F401
        except Exception:
            reasons.append("virtuoso-bridge not installed")
        from spicexplorer_core.env import probe_cadence

        # The bridge's cadence env is usually carried by the vb_env_file profile (loaded at run
        # time with override=True), so treat a present SPICEXPLORER_VB_ENV_FILE as a configured
        # bridge even when the cadence vars aren't in this process's os.environ.
        vb_env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE")
        bridge_env_ok = probe_cadence()["cadence_ok"] or bool(
            vb_env_file and Path(vb_env_file).expanduser().is_file()
        )
        if not bridge_env_ok:
            reasons.append("no Cadence/virtuoso-bridge env (set SPICEXPLORER_VB_ENV_FILE or a Cadence env var)")
        wrapper = (registry.get("corners") or {}).get("lib_file")
        mlr = model_lib_root or os.environ.get("SPICEXPLORER_TSMC65_MODEL_ROOT")
        mlr_path = Path(mlr).expanduser() if mlr else None
        if not (wrapper and mlr_path and (mlr_path / str(wrapper)).is_file()):
            reasons.append("no operator corner wrapper at model_lib_root")
        if reasons:
            return cap(engine, False, "; ".join(reasons))
        return cap(engine, True, "spectre via virtuoso-bridge + operator corner wrapper")

    return cap(engine, False, f"unknown sim_engine {engine!r}")


@dataclass(frozen=True)
class MetricEval:
    """One datasheet metric measured off a run: the value + whether it meets the spec band."""

    name: str
    value: float
    satisfied: bool
    spec_min: float | None
    spec_max: float | None


@dataclass
class CircuitRun:
    """One in-library run of an analog-db circuit + its datasheet-metric evaluation.

    ``result`` is the engine-neutral SimResult (ngspice or Spectre); :meth:`evaluate` reads each
    datasheet metric off it through the *same* measurement registry, translating only the output
    signal name to the engine's convention (``vout`` for Spectre, ``v(vout)`` for ngspice).
    """

    circuit: str
    pdk: str
    engine: str
    testbench: str
    corner: str
    result: Any
    metrics: list[MetricTarget]
    #: the testbench's ``analyses/<tb>.yaml`` params — evaluation defaults (VTOL → the
    #: settling tolerance, TSTART → the step instant) come from here so the datasheet
    #: ``extract`` stays minimal.
    params: dict[str, Any] = field(default_factory=dict)
    #: analog-db root + bridge env file — the Spectre lane's ``evaluate`` needs them to render
    #: the class OCEAN calculator and open an ``OceanMetricsSession`` on the run's raw dir.
    root: str | os.PathLike[str] | None = None
    vb_env_file: str | os.PathLike[str] | None = None

    @property
    def analysis(self) -> str:
        return _TB_ANALYSIS.get(self.testbench, "ac")

    def artifact_path(self) -> Path | None:
        """The run's raw result artifact, engine-neutrally: the Spectre psfascii raw
        DIR (persisted under ``work_dir``) or the ngspice ``.raw`` FILE.

        This is the visual-verification seam: hand it to
        ``spicexplorer_waveview.snapshot(run.artifact_path(), out_dir)`` to store the
        key traces (compressed npz) and auto-export per-analysis PNGs — waveview is a
        peer tool, so the composition stays caller-side (path in, artifacts out).
        ``None`` when the run left no artifact (e.g. a failed sim).
        """
        raw_dir = getattr(self.result, "raw_dir", None)  # SpectreSimResult
        if raw_dir:
            p = Path(raw_dir)
            return p if p.exists() else None
        # NgspiceSimResult: the wrapper records the parsed raw's path (spicelib's
        # RawRead does NOT retain its filename — reading it off `raw` fails)
        raw_path = getattr(self.result, "raw_path", None)
        if raw_path:
            p = Path(raw_path)
            return p if p.exists() else None
        raw = getattr(self.result, "raw", None)  # legacy: RawReads that kept the name
        fname = getattr(raw, "raw_filename", None) if raw is not None else None
        if fname:
            p = Path(fname)
            return p if p.exists() else None
        return None

    def _out(self, node: str) -> str:
        return f"v({node})" if self.engine == _NGSPICE else node

    def _spectre_calc_values(self) -> dict[str, float]:
        """Evaluate THIS testbench's class OCEAN **calculator** rows on the run's raw dir →
        ``{meas_name: value}``. This is the Spectre metric path: Cadence's own calculator
        (dB20/phaseMargin/cross/getData-integ) reads the PSF, NOT the Tier-1 Python registry
        (whose Spectre PSF reads mis-resolve signal
        names on the noise/AC results). Empty on no calculator rows / no raw
        dir / an OCEAN or template failure, so those metrics fall back to the Tier-1 path
        (op-point ``i_supply``, ``t_settle``/``icmr`` — which have no calculator expression)."""
        raw_dir = getattr(self.result, "raw_dir", None)
        if not raw_dir:
            return {}
        try:
            measurements = bench_ocean_measurements(
                self.circuit, self.testbench, pdk=self.pdk, root=self.root
            )
        except (AnalogDbUnavailable, KeyError):
            return {}
        if not measurements:
            return {}
        from .ocean_metrics import OceanMetricsError, OceanMetricsSession

        try:
            with OceanMetricsSession.from_vb_env(env_file=self.vb_env_file) as sess:
                return sess.measure(
                    raw_dir, measurements, label=f"{self.circuit}_{self.testbench}"
                )
        except OceanMetricsError as exc:  # session couldn't spawn / timed out → Tier-1 fallback
            _LOG.warning("OCEAN calculator unavailable for %s/%s (%s); Tier-1 fallback",
                         self.circuit, self.testbench, exc)
            return {}

    def evaluate(self, *, only: Iterable[str] | None = None) -> dict[str, MetricEval]:
        """Measure each datasheet metric bound to THIS testbench and check its spec band.

        Metrics match on the datasheet's ``analysis:`` id (== the testbench id) so
        same-kind benches don't cross-score (a ``gain_cl`` never reads a CMRR residual);
        a legacy target without an id falls back to kind matching.

        **Engine-driven metric route:** on the Spectre lane every metric
        the circuit's class defines an OCEAN *calculator* expression for is read through that
        calculator (:meth:`_spectre_calc_values`) — the Tier-1 density/AC PSF reads
        mis-resolve signal names on Spectre results. The Tier-1 registry
        stays the **ngspice** path and the Spectre fallback only for op-point/derived metrics
        with no calculator row (``i_supply``, ``t_settle``, ``icmr``). Metrics are matched to a
        calculator row by their extract ``meas`` (the datasheet metric *name* — e.g. ``vn_in`` —
        can differ from the calculator/``meas`` name — ``inoise_total``)."""
        from spicexplorer_core.measurements import measure

        want = set(only) if only is not None else None
        calc_values = self._spectre_calc_values() if self.engine == _SPECTRE else {}
        evals: dict[str, MetricEval] = {}
        for m in self.metrics:
            if want is not None and m.name not in want:
                continue
            if m.analysis_id:
                if m.analysis_id != self.testbench:
                    continue
            elif m.analysis != self.analysis:
                continue
            calc_key = str(m.recipe.get("meas", ""))
            if calc_key and calc_key in calc_values:  # Spectre calculator route (preferred)
                value = float(calc_values[calc_key])
                evals[m.name] = MetricEval(m.name, value, m.satisfied(value), m.spec_min, m.spec_max)
                continue
            recipe = {**m.recipe, "out": self._out(str(m.recipe.get("out", "vout")))}
            if "ref" in recipe:  # differential tran read (out - ref), e.g. voutp/voutn
                recipe["ref"] = self._out(str(recipe["ref"]))
            if "vin" in recipe:  # the DC-sweep (ICMR) recipes read the swept input net too
                recipe["vin"] = self._out(str(recipe["vin"]))
            if self.engine == _SPECTRE and self.testbench in ("thd", "iip3"):
                # the closed lane ran a NATIVE pss instead of the deck's tran (ngspice has
                # no PSS) — swap the FFT recipes for their harmonic-phasor twins
                meas0 = str(recipe.get("meas", ""))
                if meas0 in ("thd", "thd_pct", "thd_db"):
                    recipe["meas"] = meas0.replace("thd", "thd_pss", 1)
                    recipe.pop("f0", None)  # the pss fundamental already encodes it
                elif meas0 in ("iip3", "iip3_dbv", "im3_dbc"):
                    from spicexplorer_core.measurements import two_tone_indices

                    _f0, n1, n2 = two_tone_indices(
                        float(recipe.pop("f1")), float(recipe.pop("f2"))
                    )
                    recipe["meas"] = {
                        "iip3": "iip3_pss",
                        "iip3_dbv": "iip3_pss_dbv",
                        "im3_dbc": "im3_pss_dbc",
                    }[meas0]
                    recipe["n1"], recipe["n2"] = n1, n2
            if recipe.get("meas") == "i_supply" and "probe" not in recipe:
                # the dc_op template contract: the ngspice deck's own `let i_supply =
                # abs(i(Vdd))` current vector (written as `i(i_supply)`); the translated
                # Spectre deck reports the supply source current
                recipe["probe"] = "i(i_supply)" if self.engine == _NGSPICE else "VDD:p"
            if m.analysis == "noise" and m.recipe.get("out", "vout") == "vout":
                if self.engine == _NGSPICE:
                    # the ngspice noise template already integrates in-deck (`inoise_total`/
                    # `onoise_total` land in the Integrated Noise plot) — a scalar read, not
                    # a density integration
                    inp = recipe.get("meas") == "inoise_total"
                    value = float(
                        self.result.scalar("v(inoise_total)" if inp else "v(onoise_total)", "noise")
                    )
                    evals[m.name] = MetricEval(m.name, value, m.satisfied(value), m.spec_min, m.spec_max)
                    continue
                # Spectre lands density spectra in the noise.noise PSF as `in`/`out` —
                # the registry recipe integrates them over the swept band
                recipe["out"] = "in" if recipe.get("meas") == "inoise_total" else "out"
            if recipe.get("meas") == "t_settle" and "tol" not in recipe and "tol_frac" not in recipe:
                # the tran_step binding's own tolerance/step-instant (VTOL/TSTART params)
                from spicexplorer_core.eng import parse_value

                vtol = self.params.get("VTOL")
                recipe["tol"] = float(parse_value(str(vtol))) if vtol is not None else None
                if recipe["tol"] is None:
                    recipe.pop("tol")
                    recipe["tol_frac"] = 0.01
                if "t_start" not in recipe and self.params.get("TSTART") is not None:
                    recipe["t_start"] = float(parse_value(str(self.params["TSTART"])))
            value = float(measure(self.result, recipe, default_analysis=m.analysis))
            evals[m.name] = MetricEval(m.name, value, m.satisfied(value), m.spec_min, m.spec_max)
        return evals


def _apply_sizing_overrides(wrapper: Any, overrides: Mapping[str, Any]) -> None:
    """Override committed ``.param`` knobs on the fixed raw deck before the run.

    The sizing-experiment seam (the playground notebook rides it). Undeclared names are
    SKIPPED with a loud warning rather than applied: spicelib's ``set_parameter``
    silently inserts a dangling ``.param`` for an unknown name (BUG-B12), so a typo'd
    knob would otherwise no-op while looking applied.
    """
    ed = getattr(wrapper, "editor", None)
    if ed is None:
        raise RuntimeError("the ngspice wrapper exposes no netlist editor; cannot apply sizing_overrides")
    try:
        declared = {str(n).upper() for n in ed.get_all_parameter_names()}
    except Exception:
        declared = None  # introspection unavailable → apply blind (still explicit below)
    for key, value in overrides.items():
        if declared is not None and str(key).upper() not in declared:
            _LOG.warning(
                "sizing_overrides: %r is not a declared .param in this deck — skipped "
                "(keeping the committed value). Declared knobs: %s",
                key, sorted(declared),
            )
            continue
        ed.set_parameter(str(key), str(value))


def build_ngspice_run(
    circuit: str,
    pdk: str,
    testbench: str = "ac_open_loop",
    *,
    corner: str = "tt",
    root: str | os.PathLike[str] | None = None,
    output_dir: str | os.PathLike[str] | None = None,
    sizing_overrides: Mapping[str, Any] | None = None,
    label: str | None = None,
) -> Any:
    """Run the circuit's committed **ngspice** raw deck (open lane) → an ``NgspiceSimResult``.

    The raw deck (``raw/<circuit>/<pdk>/<testbench>.spice``) is self-contained (baked ``tt``
    corner + sizing + its own analysis), so this is a fixed-deck run through the same
    ``NGSpice_Wrapper`` the optimizer uses. A non-``tt`` ``corner`` swaps the process
    section + temperature via the circuit's own ``corners.yaml`` binding
    (``resolve_corner`` → ``apply_corner``: strips the deck's
    hardcoded ``.lib``, injects the corner's include, sets ``.options temp=``). The deck's
    authored operating point (its ``VDD`` param) is **preserved** at every corner — see
    :func:`effective_supply` for the supply source-of-truth pin.

    ``sizing_overrides`` maps committed ``.param`` knob names (see :func:`load_sizing`)
    to replacement values ("4.7u" eng strings or numbers) — the manual sizing-experiment
    seam. Unknown names warn and keep the committed value.
    """
    from spicexplorer_core.spice_engine import NGSpice_Wrapper

    deck = raw_deck_path(circuit, pdk, testbench, root=root)
    out = Path(output_dir).expanduser() if output_dir else Path(tempfile.mkdtemp(prefix="adb_ngspice_"))
    wrapper = NGSpice_Wrapper(
        netlist_filename=deck,
        output_folder=out,
        testbench_name=label or f"{circuit}_{pdk}_{testbench}",
    )
    if sizing_overrides:
        _apply_sizing_overrides(wrapper, sizing_overrides)
    if corner != "tt":
        corner_obj = resolve_corner(circuit, pdk, corner, root=root)
        # corner-swap changes process + temp only: drop the SupplyOverride so the deck's
        # authored `.param VDD` (the open lane's operating point of record) stays put
        wrapper.apply_corner(
            Corner(
                name=corner_obj.name,
                model_includes=corner_obj.model_includes,
                temp=corner_obj.temp,
                supplies=[],
            )
        )
    return wrapper.run()


def _spectre_context(
    testbench: str,
    params: dict[str, Any],
    *,
    supply: float | None = None,
    differential: tuple[str, str] | None = None,
) -> dict[str, Any]:
    """The render context for the Spectre template DB (bench params + computed extras).

    Bench params (``analyses/<tb>.yaml``, UPPERCASE) are parsed to numerics where they
    parse (eng strings like ``20u`` included); the extras are the values the class bench
    map (``spectre-benches.yaml``) documents: ``RAIL`` (the closed-lane supply — the PDK
    registry rail when given, else the authored ``VDD``) and the two-tone PSS plan
    (``IIP3_FUND``/``IIP3_HARMS``/``IIP3_N1``/``IIP3_N2``/``IIP3_NIM3A``/``IIP3_NIM3B``
    — both tones on a common fundamental so the IM3 products are plain harmonics).
    """
    from spicexplorer_core.eng import parse_value

    ctx: dict[str, Any] = {}
    for key, value in params.items():
        try:
            ctx[str(key)] = float(parse_value(str(value)))
        except (ValueError, TypeError):
            ctx[str(key)] = value
    if supply is not None:
        ctx["RAIL"] = float(supply)
    elif isinstance(ctx.get("VDD"), float):
        ctx["RAIL"] = ctx["VDD"]
    # noise-analysis output nodes. The `noise` analysis template probes ``( {OUT} {OUTN} )``:
    # OUTN is the reference node — ``0`` single-ended, ``voutn`` for a fully-differential DUT —
    # supplied here so EVERY class's noise bench renders (they keep ``OUT: vout``). NOISE_OUT is
    # the hot node the amplifier bench references as ``$NOISE_OUT`` (``vout`` single, ``voutp``
    # differential) — one template serves both output conventions.
    hot, ref = differential if differential else ("vout", "0")
    ctx["NOISE_OUT"], ctx["OUTN"] = hot, ref
    f1, f2 = ctx.get("F1"), ctx.get("F2")
    if isinstance(f1, float) and isinstance(f2, float):
        from spicexplorer_core.measurements import two_tone_indices

        fund, n1, n2 = two_tone_indices(f1, f2)
        ctx.setdefault("IIP3_FUND", fund)
        ctx.setdefault("IIP3_HARMS", 2 * n2 + 1)
        ctx.setdefault("IIP3_N1", n1)
        ctx.setdefault("IIP3_N2", n2)
        ctx.setdefault("IIP3_NIM3A", abs(2 * n1 - n2))
        ctx.setdefault("IIP3_NIM3B", 2 * n2 - n1)
    return ctx


def _spectre_analyses(
    testbench: str,
    params: dict[str, Any],
    *,
    supply: float | None = None,
    root: str | os.PathLike[str] | None = None,
    circuit_class: str = "amplifier",
    differential: tuple[str, str] | None = None,
) -> tuple[Any, ...]:
    """The Spectre analysis-statement tuple for a testbench (per the PSF-key contract).

    The deck *stimulus* (AC magnitudes on the input / feedback / supply sources, the
    tran-step pulse) rides in from the translated raw deck; only the analysis statements
    are composed here, off the same ``analyses/<tb>.yaml`` params the ngspice render used.
    ``supply`` (the PDK rail) bounds the linearity ICMR sweep — the closed lane sweeps the
    *actual* rail, not the deck's authored ``VDD`` (see :func:`effective_supply`).

    **Data-driven first**: when the analog-db checkout carries the engine template DB
    (``_shared/engines/spectre/analyses.yaml`` + the class ``spectre-benches.yaml``), the
    statements render from it (`spectre_templates.bench_analyses`) — an analysis config
    is a YAML edit there. The built-in composition below is the fallback for checkouts
    without the DB (and stays the parity reference the template tests pin against). A
    real template config error (`SpectreTemplateError`) always surfaces — only a missing
    DB/bench entry falls back.
    """
    context = _spectre_context(testbench, params, supply=supply, differential=differential)
    try:
        from .spectre_templates import bench_analyses

        return bench_analyses(testbench, context, circuit_class=circuit_class, root=root)
    except (AnalogDbUnavailable, KeyError):
        pass  # no template DB (or no bench entry) in this checkout — built-in composition

    from spicexplorer_core.eng import parse_value

    from .spectre_deck import (
        ac_analysis,
        dc_oppoint_analysis,
        dc_sweep_analysis,
        noise_analysis,
        pss_analysis,
        stb_analysis,
        transient_analysis,
    )

    def _num(key: str) -> float:
        return float(parse_value(str(params[key])))

    if testbench in ("ac_open_loop", "ac_closed_loop", "cmrr_vcm", "psrr_vdd"):
        # all four are one AC sweep; the bench identity lives in the deck stimulus
        # (mag=1 on the input, on both buffer inputs, or on the supply)
        return (
            dc_oppoint_analysis(),
            ac_analysis(_num("FSTART"), _num("FSTOP"), int(params["PPD"])),
        )
    if testbench == "dc_op":
        return (dc_oppoint_analysis(),)
    if testbench == "noise":
        # the translated input source is the VINP vsource carrying mag=1 → iprobe gives
        # the input-referred spectrum alongside the output density
        return (
            dc_oppoint_analysis(),
            noise_analysis(
                "vout", iprobe="VINP", start=_num("FSTART"), stop=_num("FSTOP"), dec=int(params["PPD"])
            ),
        )
    if testbench == "tran_step":
        return (
            dc_oppoint_analysis(),
            transient_analysis(_num("TSTOP"), step=_num("TSTEP") if "TSTEP" in params else None),
        )
    if testbench == "thd":
        # ngspice has no PSS — its lane runs the deck's tran; here the native pss at F0
        # replaces it (the fd-PSF harmonics feed {meas: thd_pss_*} — evaluate() swaps them in)
        return (pss_analysis(_num("F0"), harms=int(params.get("HARMS", 7))),)
    if testbench == "iip3":
        from spicexplorer_core.measurements import two_tone_indices

        # both tones share a fundamental (the template contract), so one pss at f0 resolves
        # the tones AND the IM3 products as plain harmonics; cover up to 2·n2 with margin
        f0, _n1, n2 = two_tone_indices(_num("F1"), _num("F2"))
        return (pss_analysis(f0, harms=2 * n2 + 1),)
    if testbench == "linearity":
        stop = supply if supply is not None else _num("VDD")
        # sweep-only on purpose: the op-point analysis would leave a sibling `dcOp.dc`
        # PSF beside the sweep's `dc.dc` (see read_swept_psf's exact-name preference)
        return (dc_sweep_analysis("VINP", 0.0, float(stop), _num("VSWEEP_STEP")),)
    if testbench == "stb":
        # the class template's VIPRB loop-probe marker (a 0 V source in the feedback
        # path) translates to an `iprobe` instance — stb's probe= target
        return (
            dc_oppoint_analysis(),
            stb_analysis("VIPRB", _num("FSTART"), _num("FSTOP"), int(params["PPD"])),
        )
    raise NotImplementedError(
        f"Spectre analysis composition for testbench {testbench!r} is not wired yet "
        f"(have: ac_open_loop/ac_closed_loop/cmrr_vcm/psrr_vdd/dc_op/noise/tran_step/"
        f"linearity/thd/iip3/stb). Add a bench entry to the class spectre-benches.yaml "
        f"(preferred) or a branch in _spectre_analyses."
    )


def bench_ocean_measurements(
    circuit: str,
    testbench: str,
    *,
    pdk: str | None = None,
    root: str | os.PathLike[str] | None = None,
) -> list[Any]:
    """The **PSS+SKILL (OCEAN Tier-2) route** for a bench: its calculator set, rendered.

    Returns the ``OceanMeasurement`` list the template DB configures for this testbench
    (the class ``spectre-benches.yaml`` rows over the engine ``calculator.yaml`` table),
    rendered against the circuit's own ``analyses/<tb>.yaml`` params — Cadence's own
    calculator functions (``thd``/``harmonic``/``phaseMargin``/``getData`` …) evaluated
    headlessly on the run's persisted raw dir::

        run = run_circuit(circuit, "tsmc-n65", testbench="thd", …)
        with OceanMetricsSession.from_vb_env() as s:
            skill = s.measure(run.result.raw_dir, bench_ocean_measurements(circuit, "thd"))

    ``[]`` when the bench configures no calculator rows; ``AnalogDbUnavailable`` when the
    checkout has no template DB. **This IS the Spectre metric path** — ``CircuitRun.evaluate``
    consumes it for every metric the class defines a calculator row for (Tier-1 stays the
    ngspice path + the op-point/derived Spectre fallback). AC exprs are rewritten to the
    differential output for a fully-differential DUT (``differential_output``)."""
    params = load_analysis(circuit, testbench, root=root).get("params", {})
    supply = pdk_supply(pdk, root=root) if pdk else None
    diff = differential_output(circuit, root=root)
    context = _spectre_context(testbench, params, supply=supply, differential=diff)
    from .ocean_metrics import OceanMeasurement
    from .spectre_templates import bench_measurements

    measurements = bench_measurements(
        testbench, context, circuit_class=circuit_class(circuit, root=root), root=root
    )
    if diff:
        # fully-differential DUT: read the AC metrics on the DIFFERENCE v(voutp)-v(voutn) —
        # the class calculator's single-ended v("vout") does not exist on this DUT. (The noise
        # row rides getData("in"), iprobe-based, so it is already FD-agnostic.)
        p, n = diff
        repl = f'(v("{p}")-v("{n}"))'
        measurements = [
            m if (m.result != "ac" or 'v("vout")' not in m.expr)
            else OceanMeasurement(name=m.name, result=m.result,
                                  expr=m.expr.replace('v("vout")', repl))
            for m in measurements
        ]
    return measurements


def build_spectre_run(
    circuit: str,
    pdk: str,
    testbench: str = "ac_open_loop",
    *,
    corner: str = "tt",
    model_lib_root: str | os.PathLike[str],
    deck_dir: str | os.PathLike[str],
    work_dir: str | os.PathLike[str],
    root: str | os.PathLike[str] | None = None,
    vb_env_file: str | os.PathLike[str] | None = None,
    sizing_overrides: Mapping[str, Any] | None = None,
    label: str | None = None,
) -> Any:
    """Run the circuit's committed raw deck through native **Spectre** (closed lane).

    Promotes the config-driven recipe: translate the raw deck body (``deck_spec_from_ngspice``),
    inject sizing + the PDK core-rail supply, compose the analyses, and apply the GENERIC corner
    resolved against the operator's out-of-repo neutral wrapper at ``model_lib_root`` (the
    generic→kit shim). Returns a ``SpectreSimResult``. Requires the virtuoso-bridge + the wrapper.
    """
    from .spectre import create_spectre_simulator
    from .spectre_deck import deck_spec_from_ngspice

    deck = raw_deck_path(circuit, pdk, testbench, root=root)
    sizing = load_sizing(circuit, pdk, root=root)
    supply = pdk_supply(pdk, root=root)
    if vb_env_file is None:
        # honor the same env var probe_engine treats as evidence of a configured bridge —
        # otherwise the bridge falls back to its own (possibly remote) default profile
        vb_env_file = os.environ.get("SPICEXPLORER_VB_ENV_FILE") or None
    corner_obj = resolve_corner(circuit, pdk, corner, root=root)
    params = load_analysis(circuit, testbench, root=root).get("params", {})
    spec = deck_spec_from_ngspice(
        deck,
        pdk=pdk,
        source_pdk=pdk,
        analyses=_spectre_analyses(
            testbench, params, supply=supply, root=root,
            circuit_class=circuit_class(circuit, root=root),
            differential=differential_output(circuit, root=root),
        ),
        # sizing defaults + PDK core-rail supply + caller sizing experiments (last wins)
        parameters={
            **sizing,
            "vdd": supply,
            **{str(k): str(v) for k, v in (sizing_overrides or {}).items()},
        },
    )
    sim = create_spectre_simulator(
        deck_spec=spec,
        deck_dir=Path(deck_dir),
        vb_env_file=Path(vb_env_file).expanduser() if vb_env_file else None,
        work_dir=str(work_dir),
    )
    # the generic→kit shim: a GENERIC corner resolved against the operator's neutral wrapper
    sim.apply_corner(corner_obj, model_lib_root=str(Path(model_lib_root).expanduser()))
    return sim.run(label=label or f"{circuit}_{pdk}_{testbench}")


def run_circuit(
    circuit: str,
    pdk: str,
    *,
    testbench: str = "ac_open_loop",
    corner: str = "tt",
    root: str | os.PathLike[str] | None = None,
    output_dir: str | os.PathLike[str] | None = None,
    model_lib_root: str | os.PathLike[str] | None = None,
    deck_dir: str | os.PathLike[str] | None = None,
    work_dir: str | os.PathLike[str] | None = None,
    vb_env_file: str | os.PathLike[str] | None = None,
    sizing_overrides: Mapping[str, Any] | None = None,
    label: str | None = None,
) -> CircuitRun:
    """**The in-library router.** Run an analog-db circuit through its native engine.

    ``sizing_overrides`` maps committed sizing-knob names (:func:`load_sizing`) to
    replacement values — the manual sizing-experiment seam, honored on BOTH lanes
    (ngspice: ``.param`` edit before the run; Spectre: parameter injection over the
    committed sizing). Unknown knob names warn and keep the committed value.

    Probes the committed ``sim_engine`` marker + the environment, then dispatches: open PDKs run
    their ngspice raw deck; the closed (Spectre-only) PDK runs native Spectre via the bridge
    (needs ``deck_dir`` + ``work_dir`` + ``model_lib_root``/``$SPICEXPLORER_TSMC65_MODEL_ROOT``).
    Raises :class:`EngineUnavailable` (with the probe's reason) when the routed engine can't run
    here. Returns a :class:`CircuitRun` whose ``evaluate()`` scores the datasheet metrics off the
    result, engine-neutrally.
    """
    cap = probe_engine(circuit, pdk, root=root, model_lib_root=model_lib_root)
    if not cap.available:
        raise EngineUnavailable(f"{circuit}/{pdk}: {cap.reason}")

    if cap.engine == _NGSPICE:
        result = build_ngspice_run(
            circuit, pdk, testbench, corner=corner, root=root, output_dir=output_dir,
            sizing_overrides=sizing_overrides, label=label,
        )
    elif cap.engine == _SPECTRE:
        if deck_dir is None or work_dir is None:
            raise ValueError(
                "the Spectre lane needs deck_dir + work_dir (per-candidate decks + the persisted PSF raw dir)"
            )
        mlr = model_lib_root or os.environ.get("SPICEXPLORER_TSMC65_MODEL_ROOT")
        if mlr is None:
            raise ValueError(
                "the Spectre lane needs model_lib_root (or $SPICEXPLORER_TSMC65_MODEL_ROOT) — the operator's neutral corner wrapper dir"
            )
        result = build_spectre_run(
            circuit, pdk, testbench, corner=corner, model_lib_root=mlr, deck_dir=deck_dir,
            work_dir=work_dir, root=root, vb_env_file=vb_env_file,
            sizing_overrides=sizing_overrides, label=label,
        )
    else:  # pragma: no cover - probe only reports available for a known engine
        raise EngineUnavailable(f"{circuit}/{pdk}: unroutable engine {cap.engine!r}")

    metrics = load_datasheet_metrics(circuit, root=root)
    try:
        params = load_analysis(circuit, testbench, root=root).get("params", {})
    except AnalogDbUnavailable:
        params = {}
    return CircuitRun(
        circuit=circuit, pdk=pdk, engine=cap.engine, testbench=testbench, corner=corner,
        result=result, metrics=metrics, params=params, root=root, vb_env_file=vb_env_file,
    )
