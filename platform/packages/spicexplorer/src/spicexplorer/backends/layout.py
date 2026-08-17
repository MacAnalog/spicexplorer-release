"""Layout-flow simulation backend — optimize a parameterized layout "the platform way".

A generator-produced layout (``spicexplorer_layout``: a ``gen_<cell>.py`` whose
``LayoutParams`` are the knobs) is exposed to the optimizer as a **testbench** whose
"simulation" is the physical flow

    build (gdsfactory, foreign interpreter) → DRC → LVS → PEX → post-layout measure

and whose "scalars" are the flow's verdicts and numbers (``area_um2``, ``drc_pass``,
``lvs_match``, per-net parasitic C, plus whatever the block's own benches report). The
YAML DSL stays untouched: ``dut_params`` are the layout knobs, a testbench's ``netlist:``
points at a ``layout-flow/1`` spec (this module's :class:`LayoutFlowSpec`) instead of a
SPICE deck, target specs use ``sim_type: layout``, and ``sim_engine: layout`` selects the
backend in the factory. The optimizer loop consumes only the ``Simulator`` protocol, so
Nevergrad / checkpoints / reports work unchanged.

Layering: this is the optimizer package; the leaf tools ``spicexplorer_layout`` (build)
and ``spicexplorer_signoff`` (DRC / LVS / PEX runners) are imported **lazily** inside
:class:`LayoutSimulator` (install the ``layout`` extra), exactly like ``backends/spectre.py``
lazily imports the bridge. Leaf tools never import this package.

Failure semantics (mirrors the SPICE backends' "a failed sim reads NaN"): a stage that
FAILS never raises out of ``run()`` — it is recorded in the run's ``summary.json`` and the
stages it gates are skipped, so their scalars read NaN and the optimizer's MAX_PENALTY
applies to those specs while the ones that DID compute (e.g. ``area_um2`` after a DRC
failure) still score. Spec / config errors (bad YAML, missing generator, unknown knob) DO
raise, at load or at ``update_params`` — loudly, once, not per trial.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, Optional

import numpy as np
import yaml

if TYPE_CHECKING:
    from spicexplorer_core.pvt import Corner

logger = logging.getLogger("spicexplorer.backends.layout")

SCHEMA = "layout-flow/1"
_GROUND_NETS = frozenset({"0", "gnd", "vss", "vsubs"})
_MISSING_EXTRA_MSG = (
    "The layout backend needs the leaf tools spicexplorer_layout + spicexplorer_signoff "
    "(and the `klayout` wheel). Install the optional extra: `uv sync --extra layout` "
    "(workspace) or `pip install 'spicexplorer[layout]'`."
)


def _import_leaf_tools():
    """Lazy import of the leaf tools (optional extra) with an actionable error."""
    try:
        from spicexplorer_layout import GdsBuilder
        from spicexplorer_signoff import run_drc, run_lvs, run_pex
        from spicexplorer_signoff.pex import strip_cards, strip_mim_for_pex
        from spicexplorer_signoff.postlayout import prep_pex_subckt
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise ImportError(f"{_MISSING_EXTRA_MSG} ({exc})") from exc
    return GdsBuilder, run_drc, run_lvs, run_pex, strip_cards, strip_mim_for_pex, prep_pex_subckt


def _leaf_src_paths() -> list[str]:
    """The leaf tools' ``src`` dirs, for foreign interpreters (they are pure stdlib on the
    generator/measure side, so PYTHONPATH beats requiring an install there)."""
    out: list[str] = []
    for mod in ("spicexplorer_layout", "spicexplorer_signoff", "spicexplorer_core"):
        try:
            m = __import__(mod)
        except ImportError:
            continue
        f = getattr(m, "__file__", None)
        if f:
            out.append(str(Path(f).resolve().parents[1]))
    return out


def _expand(value: str, base: Path) -> Path:
    """``~`` + ``$VAR`` expansion; a relative path resolves against ``base`` (the spec dir).
    Normalised WITHOUT resolving symlinks: a venv's ``bin/python`` is a symlink to the base
    interpreter, and resolving it would silently drop the venv (its site-packages)."""
    p = Path(os.path.expandvars(os.path.expanduser(str(value))))
    return Path(os.path.normpath(p if p.is_absolute() else base / p))


def _expand_env(env: Mapping[str, Any] | None) -> dict[str, str]:
    return {str(k): os.path.expandvars(os.path.expanduser(str(v))) for k, v in (env or {}).items()}


# ---------------------------------------------------------------------------
# Spec
# ---------------------------------------------------------------------------
@dataclass
class DrcSpec:
    enabled: bool = True
    no_density: bool = True
    timeout_s: int = 1800


@dataclass
class LvsSpec:
    #: a fixed reference netlist (the LVS "schematic")…
    reference: Optional[Path] = None
    #: …OR a callable in the generator module, ``writer(LayoutParams, out=path) -> path``, run
    #: in `gds_python` per trial (the reference may depend on the knobs: dummies, splits).
    writer: Optional[str] = None
    timeout_s: int = 1800


@dataclass
class PexSpec:
    mode: str = "CC"  # CC | RC | R
    #: strip the MIM device layers from the GDS (and the C cards from the LVS reference)
    #: before extraction — the IHP kpex recipe; the schematic cap cards are re-inserted below.
    strip_mim: bool = False
    #: schematic file whose ``xc*`` (default) cards are re-inserted into the prepared subckt
    schematic_cards_from: Optional[Path] = None
    schematic_card_prefixes: tuple[str, ...] = ("xc",)
    #: rewrite the extracted header to ``.subckt <cell> <ports>`` (+ VSS/VSUBS→0, drop 0-0
    #: elements) — the block's benches instantiate the cell with this exact port order.
    ports: Optional[str] = None
    #: an explicit schematic for kpex when there is no LVS stage (else the LVS reference)
    schematic: Optional[Path] = None
    #: nets that are AC ground for the block's benches; when given, ``c_<net>_ff`` is the
    #: C from <net> to {ground ∪ ac_gnd_nets} (the number a bench sees), and the plain
    #: Σ-to-anything sum is ``ctot_<net>_ff``. Without it, ``c_<net>_ff`` = Σ-to-anything.
    ac_gnd_nets: tuple[str, ...] = ()
    timeout_s: int = 3600


@dataclass
class MeasureSpec:
    module: Path
    callable: str = "measure"
    python: Optional[str] = None  # interpreter for the bench (default: this one)
    cwd: Optional[Path] = None
    pythonpath: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)
    timeout_s: int = 1800


@dataclass
class PostlayoutSpec:
    """Post-layout simulation through the PLATFORM's own testbenches (ngspice) + measurement
    registry — the alternative to the block-specific `measure` hook.

    After PEX the backend writes ``dut_postlayout.spice`` = the extracted subckt renamed to
    ``subckt`` with the schematic DUT's exact ``.subckt`` header (pin ORDER; kpex reorders
    pins), then runs every listed testbench with its DUT reference swapped to that file —
    an ``.include``/``.inc`` of ``dut`` becomes ``.include <pex file>``; an inline
    ``.subckt <subckt> … .ends`` block is replaced by that include. ``params`` are the fixed
    DUT sizing values the pre-layout run would have injected (``NGSpice_Wrapper.update_params``,
    so a deck carrying ``.param W1=…`` keeps working; the PEX subckt itself is already sized).
    """

    dut: Path
    testbenches: list[tuple[str, Path]]
    subckt: str = ""
    engine: str = "ngspice"
    params: dict[str, Any] = field(default_factory=dict)
    #: kpex globals (e.g. VSUBS) to tie to node 0 inside the post-layout subckt; ports are
    #: never rewritten. Default: none (a floating substrate node — the `sim_pex_compare` convention).
    ground_nets: tuple[str, ...] = ()
    #: the schematic DUT's pin list (from its .subckt line), filled at load
    dut_ports: list[str] = field(default_factory=list)


@dataclass
class GateSpec:
    """Which stage failures skip the downstream stages (skipped stages read NaN)."""

    drc: bool = True  # DRC fail → skip LVS/PEX/measure
    lvs: bool = True  # LVS mismatch → skip PEX/measure
    pex: bool = True  # PEX fail → skip measure


@dataclass
class LayoutFlowSpec:
    """A ``layout-flow/1`` YAML, block-agnostic. Paths are relative to the spec file."""

    path: Path
    generator: Path
    cell: str
    sizing: Optional[Path] = None
    gds_python: str = ""
    pdk: str = "ihp-sg13g2"
    fixed_params: dict[str, Any] = field(default_factory=dict)
    #: co-optimization (sizing + layout knobs in ONE Project_Setup): dut_param name → key of
    #: the generator's `sizing` dict. Those candidates are NOT layout knobs — they overlay the
    #: `sizing` JSON handed to build(params, sizing) (a per-run sizing.json) AND are injected
    #: into the `postlayout` decks' `.param`s (NGSpice_Wrapper.update_params). A list means
    #: name == key.
    sizing_params: dict[str, str] = field(default_factory=dict)
    #: grid the float knobs snap to (µm); 0/None = no rounding
    param_grid: Optional[float] = 0.01
    #: grid the `sizing_params` candidates snap to, in the SIZING dict's own units;
    #: None (default) = pass the optimizer's raw float through untouched. Set it whenever the
    #: sizing draws geometry — see `LayoutFlowSpec.snap_sizing`.
    sizing_grid: Optional[float] = None
    env: dict[str, str] = field(default_factory=dict)
    drc: DrcSpec = field(default_factory=DrcSpec)
    lvs: Optional[LvsSpec] = None
    pex: Optional[PexSpec] = None
    measure: Optional[MeasureSpec] = None
    postlayout: Optional[PostlayoutSpec] = None
    gates: GateSpec = field(default_factory=GateSpec)
    max_workers: int = 1
    #: ``all`` keeps every trial dir; ``summary`` deletes the heavy artifacts (drc/lvs/pex
    #: dirs, GDS) after the summary is written; ``none`` removes the run dir (log_path is
    #: then a per-run summary kept under ``<output>/summaries/``).
    retain: str = "all"
    #: knob name → default value, introspected (ast) from the generator's ``LayoutParams``;
    #: drives int/bool/str casting of candidates and unknown-knob validation. Empty when
    #: the generator has no literal-default dataclass (casting then falls back to types).
    param_defaults: dict[str, Any] = field(default_factory=dict)
    bounds: dict[str, tuple[Any, Any]] = field(default_factory=dict)

    # -- loading -----------------------------------------------------------------
    @classmethod
    def from_yaml(cls, path: str | Path) -> "LayoutFlowSpec":
        path = Path(os.path.normpath(Path(path).expanduser().absolute()))
        if path.suffix.lower() not in (".yaml", ".yml"):
            raise ValueError(
                f"sim_engine='layout' needs the testbench `netlist:` to be a layout-flow YAML "
                f"spec (schema {SCHEMA}), got {path.name!r}."
            )
        if not path.is_file():
            raise FileNotFoundError(f"layout-flow spec not found: {path}")
        raw = yaml.safe_load(path.read_text()) or {}
        if not isinstance(raw, dict):
            raise ValueError(f"{path}: layout-flow spec must be a mapping")
        return cls.from_dict(raw, base=path.parent, path=path)

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any], *, base: Path, path: Path | None = None) -> "LayoutFlowSpec":
        schema = raw.get("schema")
        if schema != SCHEMA:
            raise ValueError(f"{path or '<dict>'}: expected `schema: {SCHEMA}`, got {schema!r}")
        for key in ("generator", "cell"):
            if not raw.get(key):
                raise ValueError(f"{path or '<dict>'}: layout-flow spec needs `{key}`")
        gen = _expand(raw["generator"], base)
        if not gen.is_file():
            raise FileNotFoundError(f"{path}: generator not found: {gen}")
        sizing = _expand(raw["sizing"], base) if raw.get("sizing") else None
        if sizing is not None and not sizing.is_file():
            raise FileNotFoundError(f"{path}: sizing JSON not found: {sizing}")
        # interpreter for the gdsfactory stack: env GDS_PYTHON overrides the spec (so a
        # committed spec is portable across hosts), else the spec's `gds_python`, else this one.
        gds_python = str(os.environ.get("GDS_PYTHON") or raw.get("gds_python") or sys.executable)
        gds_python = os.path.expandvars(os.path.expanduser(gds_python))

        drc_raw = raw.get("drc")
        drc = DrcSpec()
        if isinstance(drc_raw, dict):
            drc = DrcSpec(
                enabled=bool(drc_raw.get("enabled", True)),
                no_density=bool(drc_raw.get("no_density", True)),
                timeout_s=int(drc_raw.get("timeout_s", 1800)),
            )
        elif drc_raw is False:
            drc = DrcSpec(enabled=False)

        lvs: Optional[LvsSpec] = None
        lvs_raw = raw.get("lvs")
        if isinstance(lvs_raw, dict) and lvs_raw.get("enabled", True):
            ref = _expand(lvs_raw["reference"], base) if lvs_raw.get("reference") else None
            writer = lvs_raw.get("writer")
            if (ref is None) == (writer is None):
                raise ValueError(f"{path}: `lvs` needs exactly one of `reference` / `writer`")
            if ref is not None and not ref.is_file():
                raise FileNotFoundError(f"{path}: LVS reference not found: {ref}")
            lvs = LvsSpec(reference=ref, writer=writer, timeout_s=int(lvs_raw.get("timeout_s", 1800)))

        pex: Optional[PexSpec] = None
        pex_raw = raw.get("pex")
        if isinstance(pex_raw, dict) and pex_raw.get("enabled", True):
            mode = str(pex_raw.get("mode", "CC")).upper()
            if mode not in ("CC", "RC", "R"):
                raise ValueError(f"{path}: pex.mode must be CC|RC|R, got {mode!r}")
            cards = _expand(pex_raw["schematic_cards_from"], base) if pex_raw.get("schematic_cards_from") else None
            if cards is not None and not cards.is_file():
                raise FileNotFoundError(f"{path}: pex.schematic_cards_from not found: {cards}")
            sch = _expand(pex_raw["schematic"], base) if pex_raw.get("schematic") else None
            if sch is None and lvs is None:
                raise ValueError(f"{path}: `pex` needs an `lvs` stage (its reference is kpex's schematic) or `pex.schematic`")
            prefixes = pex_raw.get("schematic_card_prefixes", ["xc"])
            ports = pex_raw.get("ports")
            pex = PexSpec(
                mode=mode,
                strip_mim=bool(pex_raw.get("strip_mim", False)),
                schematic_cards_from=cards,
                schematic_card_prefixes=tuple(str(p).lower() for p in (prefixes if isinstance(prefixes, list) else [prefixes])),
                ports=" ".join(ports) if isinstance(ports, list) else (str(ports) if ports else None),
                schematic=sch,
                ac_gnd_nets=tuple(str(n) for n in (pex_raw.get("ac_gnd_nets") or [])),
                timeout_s=int(pex_raw.get("timeout_s", 3600)),
            )

        measure: Optional[MeasureSpec] = None
        m_raw = raw.get("measure")
        if isinstance(m_raw, dict) and m_raw.get("enabled", True):
            if not m_raw.get("module"):
                raise ValueError(f"{path}: `measure` needs `module` (a .py file)")
            module = _expand(m_raw["module"], base)
            if not module.is_file():
                raise FileNotFoundError(f"{path}: measure module not found: {module}")
            if pex is None:
                raise ValueError(f"{path}: `measure` needs a `pex` stage (it receives the extracted subckt)")
            py = m_raw.get("python")
            if py and ("/" in str(py) or str(py).startswith("~")):
                py = str(_expand(py, base))  # a path (relative to the spec) — else a command name
            measure = MeasureSpec(
                module=module,
                callable=str(m_raw.get("callable", "measure")),
                python=str(py) if py else None,
                cwd=_expand(m_raw["cwd"], base) if m_raw.get("cwd") else None,
                pythonpath=tuple(str(_expand(p, base)) for p in (m_raw.get("pythonpath") or [])),
                env=_expand_env(m_raw.get("env")),
                extra=dict(m_raw.get("extra") or {}),
                timeout_s=int(m_raw.get("timeout_s", 1800)),
            )

        postlayout: Optional[PostlayoutSpec] = None
        pl_raw = raw.get("postlayout")
        if isinstance(pl_raw, dict) and pl_raw.get("enabled", True):
            if pex is None:
                raise ValueError(f"{path}: `postlayout` needs a `pex` stage (it simulates the extracted subckt)")
            if not pl_raw.get("dut"):
                raise ValueError(f"{path}: `postlayout` needs `dut` (the pre-layout DUT netlist the testbenches include)")
            dut = _expand(pl_raw["dut"], base)
            if not dut.is_file():
                raise FileNotFoundError(f"{path}: postlayout.dut not found: {dut}")
            engine = str(pl_raw.get("engine", "ngspice")).lower()
            if engine != "ngspice":
                raise NotImplementedError(f"{path}: postlayout.engine={engine!r} — only 'ngspice' is wired today")
            subckt = str(pl_raw.get("subckt") or raw["cell"])
            tbs_raw = pl_raw.get("testbenches") or []
            if not isinstance(tbs_raw, list) or not tbs_raw:
                raise ValueError(f"{path}: `postlayout.testbenches` must be a non-empty list of {{name, netlist}}")
            tbs: list[tuple[str, Path]] = []
            for i, t in enumerate(tbs_raw):
                if not isinstance(t, dict) or not t.get("name") or not t.get("netlist"):
                    raise ValueError(f"{path}: postlayout.testbenches[{i}] needs `name` and `netlist`")
                deck = _expand(t["netlist"], base)
                if not deck.is_file():
                    raise FileNotFoundError(f"{path}: postlayout testbench {t['name']!r} deck not found: {deck}")
                tbs.append((str(t["name"]), deck))
            if len({n for n, _ in tbs}) != len(tbs):
                raise ValueError(f"{path}: duplicate postlayout testbench names")
            from spicexplorer_signoff.postlayout import extract_subckt

            try:
                _, dut_ports = extract_subckt(dut, subckt)
            except KeyError as exc:
                raise ValueError(f"{path}: postlayout.dut {dut} has no `.subckt {subckt}`") from exc
            # every deck must reference the DUT one of the two supported ways (checked here so
            # a mis-pointed deck fails at load, not on trial 0)
            for name, deck in tbs:
                how = detect_dut_reference(deck.read_text(errors="replace"), dut_path=dut, subckt=subckt, base_dirs=(deck.parent, base))
                if how is None:
                    raise ValueError(
                        f"{path}: postlayout testbench {name!r} ({deck}) neither `.include`s {dut.name} nor "
                        f"carries an inline `.subckt {subckt}` — the backend cannot swap the DUT."
                    )
            # the LVS reference must have the same pin SET as the DUT (kpex names pins after it)
            if lvs is not None and lvs.reference is not None:
                try:
                    _, ref_ports = extract_subckt(lvs.reference, raw["cell"])
                except KeyError:
                    ref_ports = []
                if ref_ports and {p.lower() for p in ref_ports} != {p.lower() for p in dut_ports}:
                    raise ValueError(
                        f"{path}: pin set of lvs.reference `.subckt {raw['cell']}` {ref_ports} differs from "
                        f"postlayout.dut `.subckt {subckt}` {dut_ports} — the extracted subckt could not "
                        f"replace the DUT."
                    )
            postlayout = PostlayoutSpec(
                dut=dut,
                testbenches=tbs,
                subckt=subckt,
                engine=engine,
                params=dict(pl_raw.get("params") or {}),
                ground_nets=tuple(str(n) for n in (pl_raw.get("ground_nets") or [])),
                dut_ports=list(dut_ports),
            )

        g_raw = raw.get("gates") or {}
        gates = GateSpec(
            drc=bool(g_raw.get("drc", True)), lvs=bool(g_raw.get("lvs", True)), pex=bool(g_raw.get("pex", True))
        )
        retain = str(raw.get("retain", "all")).lower()
        if retain not in ("all", "summary", "none"):
            raise ValueError(f"{path}: retain must be all|summary|none, got {retain!r}")
        grid = raw.get("param_grid", 0.01)
        s_grid = raw.get("sizing_grid")
        defaults, bounds = introspect_generator(gen)
        fixed = dict(raw.get("fixed_params") or {})
        if defaults:
            unknown = sorted(set(fixed) - set(defaults))
            if unknown:
                raise ValueError(f"{path}: fixed_params not in {gen.name}'s LayoutParams: {unknown}")
        sp_raw = raw.get("sizing_params") or {}
        if isinstance(sp_raw, list):
            sizing_params = {str(n): str(n) for n in sp_raw}
        elif isinstance(sp_raw, dict):
            sizing_params = {str(k): str(v) for k, v in sp_raw.items()}
        else:
            raise ValueError(f"{path}: sizing_params must be a list of names or a {{dut_param: sizing_key}} map")
        clash = sorted(set(sizing_params) & set(defaults))
        if clash:
            raise ValueError(f"{path}: sizing_params {clash} are also LayoutParams knobs — a name must be one or the other")
        return cls(
            path=path or base / "<dict>",
            generator=gen,
            cell=str(raw["cell"]),
            sizing=sizing,
            gds_python=gds_python,
            pdk=str(raw.get("pdk", "ihp-sg13g2")),
            fixed_params=fixed,
            sizing_params=sizing_params,
            param_grid=float(grid) if grid else None,
            sizing_grid=float(s_grid) if s_grid else None,
            env=_expand_env(raw.get("env")),
            drc=drc,
            lvs=lvs,
            pex=pex,
            measure=measure,
            postlayout=postlayout,
            gates=gates,
            max_workers=int(raw.get("max_workers", 1)),
            retain=retain,
            param_defaults=defaults,
            bounds=bounds,
        )

    # -- knobs -------------------------------------------------------------------
    def cast_params(self, params: Mapping[str, Any]) -> dict[str, Any]:
        """Cast one candidate to the generator's knob types: bool/str knobs kept as-is, int
        knobs rounded to int, float knobs snapped to ``param_grid``. Unknown knobs raise
        (a config error) when the generator's `LayoutParams` could be introspected."""
        out: dict[str, Any] = {}
        known = self.param_defaults
        for name, val in params.items():
            if known and name not in known:
                raise KeyError(
                    f"{name!r} is not a knob of {self.generator.name}'s LayoutParams "
                    f"(known: {sorted(known)}). Fix the dut_param / fixed_params name."
                )
            default = known.get(name)
            if isinstance(val, (bool, str)) or isinstance(default, (bool, str)):
                out[name] = val if not isinstance(default, bool) else bool(val)
            elif isinstance(default, int) or (default is None and isinstance(val, (int, np.integer)) and not isinstance(val, bool)):
                out[name] = int(round(float(val)))
            else:
                out[name] = snap_to_grid(val, self.param_grid)
        return out

    def snap_sizing(self, value: Any) -> float:
        """Round one ``sizing_params`` candidate onto ``sizing_grid``.

        Separate from the knobs' ``param_grid`` because the two live in different unit
        systems: ``param_grid`` is a layout grid in the generator's drawing units, while a
        sizing dict's units are whatever that generator's ``build(params, sizing)`` expects
        (µm for the 5T OTA, but a generator is free to use metres). So this is **opt-in**:
        with no ``sizing_grid:`` the value is passed through unchanged, exactly as before.

        Set it when the sizing feeds drawn geometry. A raw optimizer float like
        ``0.5052731805394455`` µm reaches the generator as a device width and lands the
        drawn geometry OFF the manufacturing grid; KLayout then reports a wall of
        ``OffGrid.*`` violations and the candidate is thrown away for a reason that has
        nothing to do with the design. Snapping sizing the way the knobs are already
        snapped is what makes a co-optimization search space actually reachable.
        """
        return snap_to_grid(value, self.sizing_grid)


def snap_to_grid(value: Any, grid: Optional[float]) -> float:
    """Round ``value`` onto ``grid``; a falsy grid passes the value through unchanged."""
    f = float(value)
    if not grid:
        return f
    return round(round(f / grid) * grid, 10)


def introspect_generator(gen_path: Path) -> tuple[dict[str, Any], dict[str, tuple[Any, Any]]]:
    """(LayoutParams literal defaults, BOUNDS) read via ``ast`` — never imports the generator
    (it imports gdsfactory + a node PDK, which live in another interpreter)."""
    defaults: dict[str, Any] = {}
    bounds: dict[str, tuple[Any, Any]] = {}
    try:
        tree = ast.parse(Path(gen_path).read_text())
    except (OSError, SyntaxError) as exc:
        logger.warning(f"could not introspect generator {gen_path}: {exc}")
        return defaults, bounds
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "LayoutParams":
            for st in node.body:
                if isinstance(st, ast.AnnAssign) and st.value is not None and isinstance(st.target, ast.Name):
                    try:
                        defaults[st.target.id] = ast.literal_eval(st.value)
                    except (ValueError, TypeError):
                        pass  # a computed default: unknown type, casting falls back to the value's own
        elif isinstance(node, (ast.AnnAssign, ast.Assign)):
            target = node.target if isinstance(node, ast.AnnAssign) else (node.targets[0] if node.targets else None)
            if isinstance(target, ast.Name) and target.id == "BOUNDS" and node.value is not None:
                try:
                    b = ast.literal_eval(node.value)
                    if isinstance(b, dict):
                        bounds = {str(k): (v[0], v[1]) for k, v in b.items()}
                except (ValueError, TypeError):
                    pass
    return defaults, bounds


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
class LayoutSimResult:
    """The `SimResult` of one layout-flow run.

    Its OWN scalar table holds the flow's numbers (``area_um2``, ``drc_pass``, per-net C,
    the `measure` hook's keys, …; NaN when absent) and has no waveforms. When the flow ran
    `postlayout` testbenches, their engine results are attached as ``inner`` (name → the
    ngspice `SimResult`) and both ``scalar`` and ``wave`` DELEGATE to them for any name not
    in the own table — the analysis string (``"ac"``/``"op"``/…) is passed straight through,
    so a Tier-1 ``{meas: pm, out: vout}`` recipe (measure_integration → registry →
    ``result.wave("vout", "ac")``) scores post-layout phase margin with no new scorer code.

    Qualification rule: ``"<tb>:<name>"`` pins the read to one inner testbench (the prefix
    must be an inner testbench name — a bare colon inside a name is left alone); an
    unqualified name is looked up in the inner testbenches IN THEIR SPEC ORDER and the first
    finite scalar / first available wave wins. Merged scalars (``merge_scalars``, the Tier-1
    path) are authoritative and win every collision.
    """

    def __init__(
        self,
        scalars: Mapping[str, Any],
        *,
        summary: Mapping[str, Any],
        log_path: Path | None,
        inner: Mapping[str, Any] | None = None,
    ):
        self._scalars: dict[str, float] = {}
        for k, v in scalars.items():
            try:
                f = float(v) if v is not None else math.nan
            except (TypeError, ValueError):
                f = math.nan
            self._scalars[str(k)] = f
        self._merged: dict[str, float] = {}
        self.summary: dict[str, Any] = dict(summary)
        self._log_path = log_path
        self.inner: dict[str, Any] = dict(inner or {})

    def _split(self, name: str) -> tuple[Any | None, str]:
        """(inner result, bare name) for a `<tb>:<name>` qualified read; (None, name) otherwise."""
        if ":" in name:
            tb, _, rest = name.partition(":")
            if tb in self.inner and rest:
                return self.inner[tb], rest
        return None, name

    def merge_scalars(self, scalars: Mapping[str, float]) -> None:
        """Fold post-sim canonical scalars (Tier-1 measurements keyed by target-spec name) in;
        consulted first in `scalar` so a merged metric wins any collision."""
        for k, v in scalars.items():
            self._merged[str(k)] = float(v)

    def scalar(self, name: str, analysis: str) -> float:
        if name in self._merged:
            return self._merged[name]
        if name in self._scalars:
            return self._scalars[name]
        target, bare = self._split(name)
        if target is not None:
            try:
                return float(target.scalar(bare, analysis))
            except Exception:
                return math.nan
        for res in self.inner.values():
            try:
                v = float(res.scalar(bare, analysis))
            except Exception:
                continue
            if not math.isnan(v):
                return v
        return math.nan

    def wave(self, name: str, analysis: str) -> np.ndarray:
        if not self.inner:
            raise NotImplementedError(
                "a layout-flow result has no waveforms of its own — add `postlayout` testbenches "
                "to the flow spec to read post-layout waves through the layout testbench"
            )
        target, bare = self._split(name)
        if target is not None:
            return target.wave(bare, analysis)
        last_exc: Exception | None = None
        for res in self.inner.values():
            try:
                return res.wave(bare, analysis)
            except Exception as exc:  # try the next inner testbench
                last_exc = exc
        raise KeyError(f"wave {name!r} ({analysis}) not found in post-layout testbenches {list(self.inner)}: {last_exc}")

    @property
    def log_path(self) -> Path | None:
        return self._log_path

    @property
    def scalars(self) -> dict[str, float]:
        return {**self._scalars, **self._merged}

    @property
    def status(self) -> str:
        return str(self.summary.get("status", "unknown"))

    def __repr__(self) -> str:
        return (f"LayoutSimResult(status={self.status!r}, n_scalars={len(self._scalars)}, "
                f"inner={list(self.inner)}, log={self._log_path})")


class LayoutSimHandle:
    """`SimHandle` over a `Future[LayoutSimResult]`."""

    def __init__(self, future: "Future[LayoutSimResult]"):
        self._future = future

    def is_done(self) -> bool:
        return self._future.done()

    def result(self) -> LayoutSimResult:
        return self._future.result()


# ---------------------------------------------------------------------------
# Simulator
# ---------------------------------------------------------------------------
class LayoutSimulator:
    """A `Simulator` whose run is build → DRC → LVS → PEX → measure for one candidate."""

    def __init__(
        self,
        spec: LayoutFlowSpec,
        *,
        output_folder: str | Path,
        testbench_name: str = "layout",
        verbose: bool = False,
        path_to_simulator: str | Path | None = None,
    ):
        self.spec = spec
        self.testbench_name = testbench_name
        self.output_folder = Path(output_folder).expanduser().resolve()
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        #: the ngspice executable for `postlayout` testbenches (the project's `simulator:`)
        self.path_to_simulator = Path(path_to_simulator) if path_to_simulator else None
        self._params: dict[str, Any] = dict(spec.fixed_params)
        #: extra (non-knob) params forwarded to the post-layout decks (a testbench's `params:`)
        self._deck_params: dict[str, Any] = {}
        #: sizing overrides (spec.sizing_params candidates), keyed by the sizing-dict key
        self._sizing: dict[str, Any] = {}
        self._corner: dict[str, Any] | None = None
        self._corner_obj: Any = None
        self._model_lib_root: str | None = None
        self._n = 0
        self._lock = threading.Lock()
        self._pool: ThreadPoolExecutor | None = None
        # `env:` from the spec are DEFAULTS for the tool discovery (the signoff runners read
        # os.environ at call time) — an already-set variable wins.
        for k, v in spec.env.items():
            os.environ.setdefault(k, v)
        # fail early on a missing extra rather than on trial 0
        _import_leaf_tools()

    # -- protocol ----------------------------------------------------------------
    def update_params(self, params: Mapping[str, Any], /) -> bool:
        """Overlay a candidate onto the stored knobs (`fixed_params` + earlier calls). Cast to
        the generator's types (ints, 0.01 µm grid); an unknown knob raises."""
        if not params:
            return True
        known = self.spec.param_defaults
        sizing = {k: v for k, v in params.items() if k in self.spec.sizing_params}
        rest = {k: v for k, v in params.items() if k not in sizing}
        knobs = {k: v for k, v in rest.items() if not known or k in known}
        extra = {k: v for k, v in rest.items() if known and k not in known}
        if extra and self.spec.postlayout is None:
            raise KeyError(
                f"{sorted(extra)} are not knobs of {self.spec.generator.name}'s LayoutParams "
                f"(known: {sorted(known)}) and this flow has no `postlayout` testbenches to forward "
                f"them to. Fix the dut_param / testbench params name."
            )
        cast = self.spec.cast_params(knobs)
        with self._lock:
            self._params.update(cast)
            self._params.update(self.spec.fixed_params)  # pinned modes always win
            self._deck_params.update(extra)  # → NGSpice_Wrapper.update_params of the post-layout decks
            for name, val in sizing.items():
                # snapped onto the flow's `sizing_grid` (opt-in) — an un-snapped device
                # width draws off-grid geometry and every candidate dies on `OffGrid.*`
                snapped = self.spec.snap_sizing(val)
                self._sizing[self.spec.sizing_params[name]] = snapped
                self._deck_params[name] = snapped  # the deck's `.param <name>` too (co-optimization)
        return True

    def apply_corner(self, corner: "Corner", /, *, model_lib_root: str | None = None) -> None:
        """Layout is corner-independent; the corner is stored and forwarded to `measure`
        (the block's benches may honour it: temp, supplies, cap corner…)."""
        self._corner_obj = corner
        self._model_lib_root = model_lib_root
        if corner is None:
            self._corner = None
            return
        d: dict[str, Any]
        if dataclasses.is_dataclass(corner) and not isinstance(corner, type):
            d = dataclasses.asdict(corner)
        else:
            d = {k: getattr(corner, k) for k in ("name", "temp", "supplies", "params", "options") if hasattr(corner, k)}
        if model_lib_root is not None:
            d["model_lib_root"] = model_lib_root
        self._corner = json.loads(json.dumps(d, default=str))

    def run(self, *, label: str | None = None) -> LayoutSimResult:
        run_dir, params, corner = self._next_run(label)
        return self._execute(run_dir, params, corner)

    def submit(self, *, label: str | None = None) -> LayoutSimHandle:
        run_dir, params, corner = self._next_run(label)
        if self._pool is None:
            self._pool = ThreadPoolExecutor(max_workers=max(1, self.spec.max_workers), thread_name_prefix="layout-flow")
        return LayoutSimHandle(self._pool.submit(self._execute, run_dir, params, corner))

    def collect(self, handle: LayoutSimHandle) -> LayoutSimResult:
        return handle.result()

    def close(self) -> None:
        if self._pool is not None:
            self._pool.shutdown(wait=True)
            self._pool = None

    # -- internals ---------------------------------------------------------------
    def _next_run(self, label: str | None) -> tuple[Path, dict[str, Any], dict[str, Any] | None]:
        with self._lock:
            self._n += 1
            n = self._n
            params = dict(self._params)
            corner = dict(self._corner) if self._corner else None
            if self._sizing:
                params["__sizing__"] = dict(self._sizing)  # popped by _execute (not a knob)
        tag = label or self.testbench_name
        run_dir = self.output_folder / f"run_{n}_{tag}"
        return run_dir, params, corner

    def _execute(self, run_dir: Path, params: dict[str, Any], corner: dict[str, Any] | None) -> LayoutSimResult:
        (GdsBuilder, run_drc, run_lvs, run_pex, strip_cards, strip_mim_for_pex, prep_pex_subckt) = _import_leaf_tools()
        spec = self.spec
        run_dir.mkdir(parents=True, exist_ok=True)
        t_start = time.time()
        sizing_over: dict[str, Any] = params.pop("__sizing__", {}) if isinstance(params.get("__sizing__"), dict) else {}
        sizing_json: Path | None = spec.sizing
        if sizing_over:
            base_sizing = json.loads(spec.sizing.read_text()) if spec.sizing is not None else {}
            sizing_json = run_dir / "sizing.json"
            sizing_json.write_text(json.dumps({**base_sizing, **sizing_over}, indent=1))
        scalars: dict[str, Any] = {}
        stages: dict[str, Any] = {}
        summary: dict[str, Any] = {
            "schema": "layout-flow-run/1",
            "cell": spec.cell,
            "run_dir": str(run_dir),
            "params": params,
            "sizing": sizing_over or None,
            "corner": corner,
            "status": "ok",
            "error": None,
            "stages": stages,
            "scalars": scalars,
        }
        status = "ok"
        error: str | None = None

        def _fail(stage: str, msg: str) -> None:
            nonlocal status, error
            if status == "ok":
                status, error = f"{stage}_fail", msg
            stages.setdefault(stage, {})["error"] = msg[-2000:]
            logger.warning(f"[{run_dir.name}] {stage} failed: {msg[-300:]}")

        # 1) build -------------------------------------------------------------
        t0 = time.time()
        gds: Path | None = None
        try:
            builder = GdsBuilder(spec.generator, run_dir, cell=spec.cell, sizing_json=sizing_json, python=spec.gds_python)
            gds = builder(params)
            b = builder.last
            assert b is not None
            scalars["area_um2"] = float(b.area_um2)
            left, bottom, right, top = b.bbox_um
            scalars["width_um"] = float(right - left)
            scalars["height_um"] = float(top - bottom)
            stages["build"] = {"ok": True, "gds": str(gds), "sha256": b.sha256, "bbox_um": list(b.bbox_um)}
        except Exception as exc:  # build-time assertions (symmetry / keep-apart / validate)
            stages["build"] = {"ok": False}
            _fail("build", str(exc))
        scalars["build_secs"] = time.time() - t0
        stages.setdefault("build", {})["secs"] = scalars["build_secs"]

        # 2) DRC ---------------------------------------------------------------
        build_ok = gds is not None
        drc_ok: bool | None = None  # None = not run / unavailable / runner error
        if build_ok and spec.drc.enabled:
            t0 = time.time()
            try:
                drc = run_drc(gds, spec.cell, run_dir / "drc", pdk=spec.pdk, no_density=spec.drc.no_density, timeout_s=spec.drc.timeout_s)
                stages["drc"] = {**{k: v for k, v in drc.to_dict().items() if k != "log"}, "secs": time.time() - t0}
                if not drc.available:
                    _fail("drc", f"DRC unavailable: {drc.reason}")
                else:
                    drc_ok = bool(drc.passed)
                    scalars["drc_violations"] = float(drc.n_violations)
                    scalars["drc_pass"] = 1.0 if drc_ok else 0.0
                    if not drc_ok:
                        rules = sorted({v.rule for v in drc.violations})[:8]
                        _fail("drc", f"{drc.n_violations} DRC violation(s): {rules}")
            except Exception as exc:
                stages["drc"] = {"ok": False, "secs": time.time() - t0}
                _fail("drc", f"DRC runner error: {exc}")
        # a gate "passes" when the stage is off, or passed, or is configured not to block
        drc_gate = (not spec.drc.enabled) or drc_ok is True or (not spec.gates.drc)

        # 3) LVS ---------------------------------------------------------------
        lvs_ok: bool | None = None
        lvs_ref: Path | None = None
        if build_ok and spec.lvs is not None and drc_gate:
            t0 = time.time()
            try:
                lvs_ref = self._lvs_reference(params, run_dir, sizing_json)
                lvs = run_lvs(gds, lvs_ref, spec.cell, run_dir / "lvs", pdk=spec.pdk, timeout_s=spec.lvs.timeout_s)
                stages["lvs"] = {**{k: v for k, v in lvs.to_dict().items() if k != "log"}, "secs": time.time() - t0}
                if not lvs.available:
                    _fail("lvs", f"LVS unavailable: {lvs.reason}")
                else:
                    lvs_ok = bool(lvs.matched)
                    scalars["lvs_match"] = 1.0 if lvs_ok else 0.0
                    if not lvs_ok:
                        _fail("lvs", f"LVS mismatch: {lvs.unmatched or lvs.reason}")
            except Exception as exc:
                stages["lvs"] = {"ok": False, "secs": time.time() - t0}
                _fail("lvs", f"LVS error: {exc}")
        lvs_gate = (spec.lvs is None) or lvs_ok is True or (not spec.gates.lvs)

        # 4) PEX ---------------------------------------------------------------
        pex_ok: bool | None = None
        pex_subckt: Path | None = None
        if build_ok and spec.pex is not None and drc_gate and lvs_gate:
            t0 = time.time()
            try:
                px_spec = spec.pex
                schematic = px_spec.schematic or lvs_ref
                if schematic is None:  # the lvs writer failed but its gate is off
                    raise RuntimeError("no schematic for kpex (LVS reference missing)")
                pex_gds: Path = gds  # type: ignore[assignment]  (build_ok ⇒ gds is a Path)
                if px_spec.strip_mim:
                    pex_gds = strip_mim_for_pex(pex_gds, run_dir / f"{spec.cell}_nomim.gds")
                    nomim_sch = run_dir / f"{Path(schematic).stem}_nomim.sp"
                    nomim_sch.write_text(strip_cards(Path(schematic).read_text()))
                    schematic = nomim_sch
                px = run_pex(pex_gds, spec.cell, schematic, run_dir / "pex", mode=px_spec.mode, pdk=spec.pdk, timeout_s=px_spec.timeout_s)
                stages["pex"] = {
                    **{k: v for k, v in px.to_dict().items() if k not in ("log", "per_net_c_ff", "coupling_ff")},
                    "secs": time.time() - t0,
                }
                if not px.available:
                    _fail("pex", f"PEX unavailable: {px.reason}")
                else:
                    pex_ok = bool(px.ok)
                    scalars["pex_ok"] = 1.0 if pex_ok else 0.0
                    if pex_ok:
                        scalars["pex_n_c"] = float(px.n_c)
                        scalars["pex_n_r"] = float(px.n_r)
                        scalars.update(parasitic_scalars(px.per_net_c_ff, px.coupling_ff, ac_gnd_nets=px_spec.ac_gnd_nets))
                        assert px.netlist_path
                        raw_txt = Path(px.netlist_path).read_text()
                        pex_subckt = run_dir / f"{spec.cell}_pex_{px_spec.mode.lower()}.sp"
                        pex_subckt.write_text(prepare_pex_subckt(raw_txt, spec.cell, prep_pex_subckt, ports=px_spec.ports, cards_from=px_spec.schematic_cards_from, card_prefixes=px_spec.schematic_card_prefixes))
                        stages["pex"]["subckt"] = str(pex_subckt)
                    else:
                        _fail("pex", f"PEX failed: {px.reason}")
            except Exception as exc:
                stages["pex"] = {"ok": False, "secs": time.time() - t0}
                _fail("pex", f"PEX error: {exc}")
        # measure needs the prepared subckt, so a failed PEX always skips it (gates.pex only
        # matters for a PEX that ran but reported not-ok yet still wrote a netlist — kpex
        # never does, so the flag is kept for symmetry / future extractors).

        # 5) postlayout: the platform's own testbenches on the extracted subckt --------
        inner: dict[str, Any] = {}
        if spec.postlayout is not None and pex_subckt is not None and (pex_ok is True or not spec.gates.pex):
            t0 = time.time()
            try:
                inner = self._postlayout(run_dir, params, stages, prep_pex_subckt)
                pl = stages.setdefault("postlayout", {})
                pl["secs"] = time.time() - t0
                n_ok = sum(1 for tb in inner if getattr(inner[tb], "raw", None) is not None)
                scalars["postlayout_ok"] = 1.0 if (inner and n_ok == len(spec.postlayout.testbenches)) else 0.0
                if not inner or n_ok != len(spec.postlayout.testbenches):
                    _fail("postlayout", f"{len(spec.postlayout.testbenches) - n_ok} post-layout testbench(es) produced no RAW")
            except Exception as exc:
                stages.setdefault("postlayout", {})["secs"] = time.time() - t0
                scalars["postlayout_ok"] = 0.0
                _fail("postlayout", f"postlayout error: {exc}")

        # 6) measure -----------------------------------------------------------
        if spec.measure is not None and pex_subckt is not None and (pex_ok is True or not spec.gates.pex):
            t0 = time.time()
            try:
                reply = self._measure(pex_subckt, run_dir, params, corner, stages)
                stages["measure"] = {**{k: v for k, v in reply.items() if k != "scalars"}, "secs": time.time() - t0}
                if reply.get("status", "ok") != "ok":
                    _fail("measure", str(reply.get("error") or "measure reported an error"))
                for k, v in (reply.get("scalars") or {}).items():
                    scalars[k] = math.nan if v is None else float(v)
            except Exception as exc:
                stages["measure"] = {"ok": False, "secs": time.time() - t0}
                _fail("measure", f"measure error: {exc}")

        scalars["total_secs"] = time.time() - t_start
        summary["status"], summary["error"] = status, error
        summary["scalars"] = {k: (None if isinstance(v, float) and not math.isfinite(v) else v) for k, v in scalars.items()}
        log_path = self._write_summary(run_dir, summary)
        if self.verbose:
            logger.info(f"[{run_dir.name}] {status} area={scalars.get('area_um2')} ({scalars['total_secs']:.1f}s)")
        return LayoutSimResult(scalars, summary=summary, log_path=log_path, inner=inner)

    def _write_summary(self, run_dir: Path, summary: dict[str, Any]) -> Path:
        text = json.dumps(summary, indent=1, default=str)
        path = run_dir / "summary.json"
        path.write_text(text)
        if self.spec.retain == "summary":
            for sub in ("drc", "lvs", "pex"):
                shutil.rmtree(run_dir / sub, ignore_errors=True)
            for f in run_dir.glob("*.gds"):
                f.unlink(missing_ok=True)
        elif self.spec.retain == "none":
            keep = self.output_folder / "summaries"
            keep.mkdir(parents=True, exist_ok=True)
            path = keep / f"{run_dir.name}.json"
            path.write_text(text)
            shutil.rmtree(run_dir, ignore_errors=True)
        return path

    def _postlayout(self, run_dir: Path, params: dict[str, Any], stages: dict[str, Any], prep_pex_subckt) -> dict[str, Any]:
        """Write ``dut_postlayout.spice`` and run every `postlayout` testbench on it through the
        ngspice backend (built via the factory so the project's simulator path flows through).
        Returns {tb name: NgspiceSimResult}. Raises on a config-level problem (port mismatch,
        DUT reference not found); a deck that fails to simulate yields a NaN-backed result."""
        pl = self.spec.postlayout
        assert pl is not None
        px = stages.get("pex", {})
        raw = Path(px["netlist_path"]).read_text()
        pex_dut = build_postlayout_dut(raw, self.spec.cell, pl.subckt, pl.dut_ports, prep_pex_subckt, ground_nets=pl.ground_nets)
        dut_path = run_dir / "dut_postlayout.spice"
        dut_path.write_text(pex_dut)
        stages.setdefault("postlayout", {})["dut"] = str(dut_path)
        return self._run_decks(run_dir / "postlayout", dut_path, stages["postlayout"])

    def run_prelayout_reference(self, out_dir: str | Path) -> dict[str, Any]:
        """Run the `postlayout` testbenches on the PRE-layout schematic DUT (the reference the
        post-layout numbers are compared against) — the same decks, same params/corner, only
        the DUT include untouched. Not part of the trial loop; for baselines / reports / tests.
        Returns {tb name: NgspiceSimResult}."""
        if self.spec.postlayout is None:
            raise ValueError("this flow has no `postlayout` testbenches")
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        info: dict[str, Any] = {}
        return self._run_decks(out, self.spec.postlayout.dut, info)

    def _run_decks(self, deck_dir: Path, dut_file: Path, info: dict[str, Any]) -> dict[str, Any]:
        from spicexplorer.optimization.simulator_factory import build_simulator

        pl = self.spec.postlayout
        assert pl is not None
        deck_dir.mkdir(parents=True, exist_ok=True)
        inner: dict[str, Any] = {}
        for tb_name, deck in pl.testbenches:
            t0 = time.time()
            text = deck.read_text(errors="replace")
            swapped, how = swap_dut_reference(text, dut_path=pl.dut, subckt=pl.subckt, pex_path=dut_file, base_dirs=(deck.parent, self.spec.path.parent))
            tb_deck = deck_dir / f"{tb_name}.spice"
            tb_deck.write_text(swapped)
            sim = build_simulator(
                "ngspice",
                netlist_filename=tb_deck,
                testbench_name=tb_name,
                output_folder=deck_dir / f"{tb_name}_out",
                path_to_simulator=self.path_to_simulator,
                verbose=self.verbose,
            )
            if self._corner_obj is not None:
                sim.apply_corner(self._corner_obj, model_lib_root=self._model_lib_root)
            sim.update_params({**pl.params, **self._deck_params})
            res = sim.run(label=tb_name)
            inner[tb_name] = res
            info[tb_name] = {
                "deck": str(tb_deck),
                "dut_swap": how,
                "ok": getattr(res, "raw", None) is not None,
                "log_path": str(getattr(res, "log_path", None)),
                "raw_path": str(getattr(res, "raw_path", None)),
                "secs": time.time() - t0,
            }
        return inner

    def _lvs_reference(self, params: dict[str, Any], run_dir: Path, sizing_json: Path | None = None) -> Path:
        """The LVS reference for this candidate: the fixed `lvs.reference`, or the generator's
        `lvs.writer` run in `gds_python` — called as ``writer(LayoutParams, out=…)``, plus
        ``sizing=<dict>`` when the writer's signature accepts it (co-optimization: the
        reference must follow the candidate's sizing)."""
        assert self.spec.lvs is not None
        if self.spec.lvs.reference is not None:
            return self.spec.lvs.reference
        out = run_dir / f"{self.spec.cell}_lvs.sp"
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(_leaf_src_paths() + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        code = (
            "import importlib.util, inspect, json, sys\n"
            f"spec = importlib.util.spec_from_file_location('gen_mod', {str(self.spec.generator)!r})\n"
            "m = importlib.util.module_from_spec(spec); sys.modules['gen_mod'] = m; spec.loader.exec_module(m)\n"
            f"p = m.LayoutParams(**json.loads({json.dumps(params)!r}))\n"
            f"fn = getattr(m, {self.spec.lvs.writer!r})\n"
            f"sizing = json.loads(open({str(sizing_json)!r}).read()) if {sizing_json is not None!r} else None\n"
            "kw = {'sizing': sizing} if (sizing is not None and 'sizing' in inspect.signature(fn).parameters) else {}\n"
            f"print(fn(p, out={str(out)!r}, **kw))\n"
        )
        r = subprocess.run([self.spec.gds_python, "-c", code], env=env, capture_output=True, text=True, timeout=self.spec.lvs.timeout_s, cwd=str(self.spec.generator.parent))
        if r.returncode != 0 or not out.is_file():
            raise RuntimeError(f"lvs writer {self.spec.lvs.writer!r} failed ({r.returncode}): {(r.stderr or r.stdout)[-1500:]}")
        return out

    def _measure(self, pex_subckt: Path, run_dir: Path, params: dict[str, Any], corner: dict[str, Any] | None, stages: dict[str, Any]) -> dict[str, Any]:
        from spicexplorer_layout.measure_protocol import parse_result

        m = self.spec.measure
        assert m is not None
        python = m.python or sys.executable
        env = dict(os.environ)
        env.update(m.env)
        env["PYTHONPATH"] = os.pathsep.join(list(m.pythonpath) + _leaf_src_paths() + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else []))
        request = {
            "pex_subckt": str(pex_subckt),
            "pex_netlist": stages.get("pex", {}).get("netlist_path"),
            "gds": stages.get("build", {}).get("gds"),
            "work_dir": str(run_dir),
            "cell": self.spec.cell,
            "params": params,
            "corner": corner,
            "extra": m.extra,
        }
        code = (
            "import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('layout_measure_mod', {str(m.module)!r})\n"
            "mod = importlib.util.module_from_spec(spec); sys.modules['layout_measure_mod'] = mod; spec.loader.exec_module(mod)\n"
            "from spicexplorer_layout.measure_protocol import serve\n"
            f"sys.exit(serve(getattr(mod, {m.callable!r})))\n"
        )
        r = subprocess.run(
            [python, "-c", code],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            env=env,
            cwd=str(m.cwd or m.module.parent),
            timeout=m.timeout_s,
        )
        (run_dir / "measure.log").write_text((r.stdout or "") + "\n--- stderr ---\n" + (r.stderr or ""))
        reply = parse_result(r.stdout or "")
        if reply is None:
            raise RuntimeError(f"measure produced no result line (exit {r.returncode}): {(r.stderr or r.stdout)[-1500:]}")
        return reply


# ---------------------------------------------------------------------------
# Helpers (pure functions, unit-testable offline)
# ---------------------------------------------------------------------------
def parasitic_scalars(
    per_net_c_ff: Mapping[str, float],
    coupling_ff: Mapping[str, float],
    *,
    ac_gnd_nets: tuple[str, ...] | list[str] = (),
) -> dict[str, float]:
    """`PexResult` per-net / coupling sums → optimizer scalars.

    * ``ctot_<net>_ff`` — Σ C touching <net> (kpex's per-net sum, to anything).
    * ``c_<a>__<b>_ff`` — the coupling C between two nets (``coupling_ff`` "a|b").
    * ``c_<net>_ff`` — with ``ac_gnd_nets``: C from <net> to {0/gnd/vss/vsubs ∪ ac_gnd_nets},
      i.e. what a bench that AC-grounds those nets sees (the layout-brief budget number);
      without: the same as ``ctot_<net>_ff``.
    """
    out: dict[str, float] = {}
    acg = {n.lower() for n in ac_gnd_nets} | _GROUND_NETS
    for net, c in per_net_c_ff.items():
        out[f"ctot_{net}_ff"] = float(c)
    for pair, c in coupling_ff.items():
        a, b = pair.split("|", 1)
        out[f"c_{a}__{b}_ff"] = float(c)
    for net, c in per_net_c_ff.items():
        if net.lower() in _GROUND_NETS:
            continue
        if not ac_gnd_nets:
            out[f"c_{net}_ff"] = float(c)
            continue
        to_others = 0.0
        to_acg = 0.0
        for pair, cc in coupling_ff.items():
            a, b = pair.split("|", 1)
            if net not in (a, b):
                continue
            other = b if a == net else a
            to_others += cc
            if other.lower() in acg:
                to_acg += cc
        c_to_0 = float(c) - to_others  # what remains is C to node 0 (excluded from coupling)
        out[f"c_{net}_ff"] = c_to_0 + to_acg
    return out


def prepare_pex_subckt(
    raw: str,
    cell: str,
    prep_pex_subckt,
    *,
    ports: str | None = None,
    cards_from: Path | None = None,
    card_prefixes: tuple[str, ...] = ("xc",),
) -> str:
    """kpex netlist → the ``.subckt`` a bench splices in.

    Always ``M``→``XM`` (``spicexplorer_signoff.postlayout.prep_pex_subckt``). With ``ports``
    the header is rewritten to ``.subckt <cell> <ports>`` (dropping kpex's continuation
    lines), ``VSS``/``VSUBS`` become node ``0`` and 0-0 elements are dropped; with
    ``cards_from`` the schematic's ``xc*`` cards (the MIM devices stripped for PEX) are
    re-inserted before ``.ends`` — the recipe from the H12 layout report §4, generalised.
    """
    text = prep_pex_subckt(raw, cell)
    if ports is None and cards_from is None:
        return text
    lines: list[str] = []
    skip_cont = False
    for ln in text.splitlines():
        if ports is not None and ln.lower().startswith(".subckt"):
            lines.append(f".subckt {cell} {ports}")
            skip_cont = True
            continue
        if skip_cont and ln.startswith("+"):
            continue
        skip_cont = False
        if ports is not None:
            toks = [("0" if w.upper() in ("VSS", "VSUBS") else w) for w in ln.split()]
            if toks and toks[0][:1].lower() in "cr" and len(toks) >= 4 and toks[1] == "0" and toks[2] == "0":
                continue
            ln = " ".join(toks)
        lines.append(ln)
    if cards_from is not None:
        prefixes = tuple(p.lower() for p in card_prefixes)
        cards = [ln.strip() for ln in Path(cards_from).read_text().splitlines() if ln.strip().lower().startswith(prefixes)]
        ends = [k for k, ln in enumerate(lines) if ln.strip().lower().startswith(".ends")]
        i = ends[0] if ends else len(lines)
        lines = lines[:i] + cards + lines[i:]
    return "\n".join(lines) + "\n"


_DUT_INCLUDE_RE = re.compile(r"^\s*\.(?:include|inc)\s+[\"']?([^\"'\s]+)[\"']?", re.IGNORECASE)
_LIB_RE = re.compile(r"^(\s*\.lib\s+)[\"']?([^\"'\s]+)[\"']?(.*)$", re.IGNORECASE)


def _same_file(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except OSError:
        return False


def _resolve_ref(target: str, base_dirs: tuple[Path, ...]) -> Path | None:
    p = Path(os.path.expandvars(os.path.expanduser(target)))
    if p.is_absolute():
        return p if p.exists() else None
    for base in base_dirs:
        cand = base / p
        if cand.exists():
            return cand
    return None


def detect_dut_reference(tb_text: str, *, dut_path: Path, subckt: str, base_dirs: tuple[Path, ...]) -> str | None:
    """How a testbench deck references the DUT: ``"include"`` (an ``.include``/``.inc`` that
    resolves to ``dut_path`` — or names its basename), ``"inline"`` (a ``.subckt <subckt>``
    block in the deck), or ``None``."""
    for line in tb_text.splitlines():
        m = _DUT_INCLUDE_RE.match(line)
        if not m:
            continue
        target = m.group(1)
        resolved = _resolve_ref(target, base_dirs)
        if (resolved is not None and _same_file(resolved, dut_path)) or Path(target).name == dut_path.name:
            return "include"
    if re.search(rf"(?im)^\s*\.subckt\s+{re.escape(subckt)}\b", tb_text):
        return "inline"
    return None


def swap_dut_reference(
    tb_text: str,
    *,
    dut_path: Path,
    subckt: str,
    pex_path: Path,
    base_dirs: tuple[Path, ...],
) -> tuple[str, str]:
    """Return (deck text with the DUT swapped to ``.include <pex_path>``, how).

    * ``.include``/``.inc`` of the DUT (resolved against ``base_dirs`` or by basename) →
      ``.include <pex_path>``;
    * else an inline ``.subckt <subckt> … .ends`` block → replaced by that include;
    * every OTHER relative ``.include``/``.inc``/``.lib`` path that resolves against
      ``base_dirs`` is made absolute (the swapped deck is written elsewhere).
    Raises ``ValueError`` when the deck references the DUT neither way (a config error).
    """
    lines = tb_text.splitlines()
    out: list[str] = []
    swapped = False
    for line in lines:
        m = _DUT_INCLUDE_RE.match(line)
        if m:
            target = m.group(1)
            resolved = _resolve_ref(target, base_dirs)
            if not swapped and ((resolved is not None and _same_file(resolved, dut_path)) or Path(target).name == dut_path.name):
                out.append(f".include {pex_path}")
                swapped = True
                continue
            if resolved is not None and not Path(target).is_absolute():
                out.append(f".include {resolved.resolve()}")
                continue
            out.append(line)
            continue
        ml = _LIB_RE.match(line)
        if ml:
            target = ml.group(2)
            resolved = _resolve_ref(target, base_dirs)
            if resolved is not None and not Path(target).is_absolute():
                out.append(f"{ml.group(1)}{resolved.resolve()}{ml.group(3)}")
                continue
        out.append(line)
    text = "\n".join(out) + ("\n" if tb_text.endswith("\n") else "")
    if swapped:
        return text, "include"
    # inline block → the include line (nesting-aware: the first .ends at depth 0 closes it)
    hdr = re.compile(rf"^\s*\.subckt\s+{re.escape(subckt)}\b", re.IGNORECASE)
    start = next((i for i, ln in enumerate(out) if hdr.match(ln)), None)
    if start is None:
        raise ValueError(f"testbench deck references neither `.include {dut_path.name}` nor an inline `.subckt {subckt}`")
    depth = 0
    end = None
    for i in range(start, len(out)):
        s_ = out[i].strip().lower()
        if s_.startswith(".subckt"):
            depth += 1
        elif s_.startswith(".ends"):
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        raise ValueError(f"inline `.subckt {subckt}` has no matching .ends")
    new_lines = out[:start] + [f".include {pex_path}"] + out[end + 1:]
    return "\n".join(new_lines) + ("\n" if tb_text.endswith("\n") else ""), "inline"


def build_postlayout_dut(
    raw: str,
    cell: str,
    subckt: str,
    dut_ports: list[str],
    prep_pex_subckt,
    *,
    ground_nets: tuple[str, ...] | list[str] = (),
) -> str:
    """kpex netlist → ``.subckt <subckt> <dut ports…>`` with the schematic DUT's exact pin
    order (kpex reorders pins), ``M``→``XM`` cards, and ``ground_nets`` (e.g. VSUBS) tied to
    node 0. Raises ``ValueError`` when the extracted pin SET differs from the DUT's."""
    from spicexplorer_signoff.postlayout import extract_subckt

    text = prep_pex_subckt(raw, cell, rename=subckt)
    _, pex_ports = extract_subckt(text, subckt)
    if {p.lower() for p in pex_ports} != {p.lower() for p in dut_ports}:
        raise ValueError(
            f"post-layout pin set {sorted(pex_ports)} != schematic DUT `.subckt {subckt}` pins "
            f"{sorted(dut_ports)} — the extracted subckt cannot replace the DUT (check the LVS "
            f"reference / postlayout.dut)."
        )
    gnd = {n.lower() for n in ground_nets} - {p.lower() for p in dut_ports}
    lines: list[str] = []
    skip_cont = False
    for ln in text.splitlines():
        if ln.lower().lstrip().startswith(".subckt"):
            lines.append(f".subckt {subckt} {' '.join(dut_ports)}")
            skip_cont = True
            continue
        if skip_cont and ln.lstrip().startswith("+"):
            continue
        skip_cont = False
        if gnd and not ln.lstrip().startswith(("*", ".")):
            toks = ln.split()
            ln = " ".join("0" if (i > 0 and t.lower() in gnd) else t for i, t in enumerate(toks))
        lines.append(ln)
    return "\n".join(lines) + "\n"


def create_layout_simulator(
    spec_path: str | Path,
    *,
    output_folder: str | Path,
    testbench_name: str = "layout",
    verbose: bool = False,
    path_to_simulator: str | Path | None = None,
) -> LayoutSimulator:
    """Factory entry: load the ``layout-flow/1`` spec and build the simulator."""
    spec = LayoutFlowSpec.from_yaml(spec_path)
    return LayoutSimulator(spec, output_folder=output_folder, testbench_name=testbench_name, verbose=verbose,
                           path_to_simulator=path_to_simulator)


__all__ = [
    "SCHEMA",
    "LayoutFlowSpec",
    "DrcSpec",
    "LvsSpec",
    "PexSpec",
    "MeasureSpec",
    "PostlayoutSpec",
    "GateSpec",
    "LayoutSimResult",
    "LayoutSimHandle",
    "LayoutSimulator",
    "create_layout_simulator",
    "introspect_generator",
    "parasitic_scalars",
    "prepare_pex_subckt",
    "detect_dut_reference",
    "swap_dut_reference",
    "build_postlayout_dut",
]
