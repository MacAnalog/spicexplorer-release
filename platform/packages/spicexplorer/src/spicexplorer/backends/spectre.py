"""Cadence Spectre backend — a `Simulator`-protocol adapter over virtuoso-bridge-lite.

This wraps the bridge's headless
`SpectreSimulator` (drives `spectre` over SSH on a flat `.scs`, parses PSF → a flat
numeric dict) behind the engine-neutral `Simulator` / `SimResult` / `SimHandle` protocol
defined in `spicexplorer_core.spice_engine.protocol`.

Non-negotiables it honours (blast-radius rule):

* **No top-level `virtuoso_bridge` import.** Importing this module is free of any Cadence
  dependency; the bridge is imported *inside* `create_spectre_simulator`, guarded, with a
  clear install hint. So `spicexplorer` (and the API that imports it) load fine without it.
* The lazy factory **pre-sets `VB_*` env before constructing the bridge**, so the bridge's
  `load_dotenv(override=True)` / cwd-upward `.env` discovery / package-logger mutation can't
  leak global state into an ngspice-only process.

Two run modes:

* **Fixed deck** — construct with a hand-written `.scs`; `update_params`/`apply_corner`
  only *stage* overrides (the file runs verbatim).
* **Composed deck** — construct with a `SpectreDeckSpec` (see `backends.spectre_deck`;
  build one from an ngspice deck via `deck_spec_from_ngspice`): every `run`/`submit`
  **materializes** the staged design params + corner into a fresh per-run `.scs` under
  `deck_dir` — that is the `parameters`-line injection (the bridge still executes a
  fixed file per run; *we* write it).

**PSF-naming contract (live-validated):** the
bridge's flat-dict prefixes come from the PSF *file names*, so the deck must name its
analyses `ac` / `dc` / `dcOp` for the `ac_` / `dc_` keys to appear (a deck-emitter
contract). Op-point *node voltages* land under `dc_` (a `dcOp dc` analysis writes
`dcOp.dc`), so the `op` lookup chain is bare-then-`dc_`. Per-MOS `.info` op-point scalars
(`M0:gm`, `M0:vth`, `M0:region`) are **not** extracted by the bridge's parser — psfascii
STRUCT values are dropped (each instance comes back as just its model-name string) — so
this module post-parses the run's `*.info` files from `metadata["output_dir"]` itself and
merges `<inst>:<param>` keys into the result, keeping the upstream submodule pristine.
`tran` signals merge bare (no prefix); a `noise` sweep's densities aren't in the bridge's
flat dict at all — they're read from the swept `noise.noise` PSF (`read_swept_psf`, below).

**The bridge's verdict decides whether there is a result at all** (`_result_of`). A run the
bridge reports as fatal or partial (`ok=False`), or whose process exited nonzero, still hands
back whatever PSF it managed to write; that is NOT data. Such a run becomes an empty
`SpectreSimResult` — scalars read NaN, waves raise — so the optimizer scores it MAX_PENALTY
exactly as it does an ngspice run that wrote no RAW (BUG-B28).
"""

from __future__ import annotations

import itertools
import logging
import os
import re
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
from spicexplorer_core.spice_engine import psfascii as _psf

from .spectre_deck import SpectreDeckSpec, render_native_scs, render_spectre_deck

if TYPE_CHECKING:  # keep this module import-cheap and Cadence-free
    from concurrent.futures import Future

    from spicexplorer_core.pvt import Corner

logger = logging.getLogger(__name__)


# analysis (engine-neutral string) → ordered PSF-key prefix chain, live-validated
# against real licensed-kit psfascii (2026-07-05). Per-MOS op scalars (`M0:gm`) are merged in
# bare by the core info-file post-parse (`psfascii.read_oppoint_info`); op-point NODE voltages come from `dcOp.dc`
# under `dc_`, hence op's two-step chain. `tran` merges bare in the bridge parser (no
# prefix); `noise_` is a flat-dict fallback, but a noise sweep's `out`/`in` densities come
# from the swept `noise.noise` PSF (`read_swept_psf`), not the bridge's flat dict.
_ANALYSIS_PREFIXES: dict[str, tuple[str, ...]] = {
    "op": ("", "dc_"),
    "oppoint": ("", "dc_"),
    "dc": ("dc_",),
    "ac": ("ac_",),
    "tran": ("",),
    "transient": ("",),
    "noise": ("noise_",),
    "noise_spectrum": ("noise_",),
    "noise_spectral": ("noise_",),
    "pnoise": ("pnoise_",),
}


def _resolve_prefixes(analysis: str) -> tuple[str, ...]:
    """Map an engine-neutral `analysis` string to its flat-PSF key-prefix chain."""
    return _ANALYSIS_PREFIXES.get(str(analysis).strip().lower(), ("",))


# The psfascii CONTRACT — per-instance `*.info` STRUCT op-points, the analysis → file table
# (`ac.ac`, `noise.noise`, `<n>.fd.pss`, `pac.<k>.pac`, `stb.stb`, …), the abscissa aliases and the
# swept-file reader — lives in core (`spicexplorer_core.spice_engine.psfascii`) since it is shared with
# the viewer (peer tools never import each other; core is what both import). The names below are the
# adapter's historical spellings, kept so callers and tests keep working.
_INFO_SKIP_STEMS = _psf.INFO_SKIP_STEMS
_STRUCT_DEF_RE = _psf.STRUCT_DEF_RE
_STRUCT_MEMBER_RE = _psf.STRUCT_MEMBER_RE
_STRUCT_VALUE_OPEN_RE = _psf.STRUCT_VALUE_OPEN_RE
_parse_info_structs = _psf.parse_info_structs
parse_psfascii_oppoint = _psf.read_oppoint_info
_SWEEP_EXT = _psf.SWEEP_EXT
_PAC_SIDEBAND_RE = _psf.PAC_SIDEBAND_RE
_SWEEP_ABSCISSA = _psf.SWEEP_ABSCISSA
read_swept_psf = _psf.read_swept_psf


def _data_of(sim_result: Any) -> dict[str, Any]:
    """Flat numeric dict from a bridge `SimulationResult` (duck-typed), op-point enriched.

    Starts from the bridge's own parsed `.data`, then merges our info-file post-parse
    (`<inst>:<param>` keys) from `metadata["output_dir"]` when the run left one — the
    bridge's keys win on (unexpected) collision.
    """
    data = dict(getattr(sim_result, "data", None) or {})
    output_dir = _raw_dir_of(sim_result)
    if output_dir:
        for key, value in parse_psfascii_oppoint(output_dir).items():
            data.setdefault(key, value)
    return data


def _raw_dir_of(sim_result: Any) -> str | None:
    """The run's persisted PSF `-raw` directory (`metadata["output_dir"]`), or None.

    The bridge only leaves this when constructed with `work_dir=` (composed-deck runs
    pass one so each candidate gets a distinct raw dir). It is the handle the OCEAN
    metrics runner (`backends.ocean_metrics`) reads to evaluate canonical measurements.
    """
    metadata = getattr(sim_result, "metadata", None)
    output_dir = metadata.get("output_dir") if isinstance(metadata, dict) else None
    return str(output_dir) if output_dir else None


def _verdict_of(sim_result: Any) -> tuple[bool, str, list[str], int | None]:
    """``(ok, status, errors, returncode)`` from a bridge `SimulationResult` (duck-typed).

    The rule is the one `spicexplorer_spectre.lane._finish` applies (Codex SPC-01): the
    returncode and the bridge's own verdict are EACH sufficient to fail a run. A nonzero exit
    fails it whatever `ok` says, and `ok=False` fails it even at rc 0 (the bridge flags a fatal
    or convergence error the exit status does not carry, and keeps the partial PSF). One
    difference: a result that carries NEITHER (a duck-typed stand-in with only `.data`) has no
    verdict to give and is read as before; the real bridge always sets `ok`.
    """
    verdict = getattr(sim_result, "ok", None)
    metadata = getattr(sim_result, "metadata", None)
    rc = metadata.get("returncode") if isinstance(metadata, dict) else None
    raw_status = getattr(sim_result, "status", None)
    status = str(getattr(raw_status, "value", raw_status) or "")
    errors = [str(e) for e in (getattr(sim_result, "errors", None) or [])]
    ok = verdict is not False and (rc is None or rc == 0)
    if not ok and status in ("", "success"):  # `_finish`'s wording for a run failed on rc alone
        status = f"failed (rc={rc})"
    return ok, status or "success", errors, rc


def _result_of(sim_result: Any, *, label: str | None = None) -> SpectreSimResult:
    """The adapter's `SimResult` for one bridge run — EMPTY when the bridge says it failed.

    A failed run keeps its verdict (`ok`/`status`/`errors`/`returncode`) but none of its PSF:
    no flat data and no `raw_dir`, so a scalar reads NaN, a wave raises, and nothing downstream
    (the OCEAN merge, a waveview snapshot) evaluates the partly-written results.
    """
    ok, status, errors, rc = _verdict_of(sim_result)
    if ok:
        return SpectreSimResult(
            _data_of(sim_result),
            raw_dir=_raw_dir_of(sim_result),
            ok=True,
            status=status,
            errors=errors,
            returncode=rc,
        )
    logger.warning(
        "Spectre run %s failed (status=%s, rc=%s): %s — its metrics score as failures; "
        "the partial results in %s are not read.",
        label or "",
        status,
        rc,
        "; ".join(errors)[:400] or "no error text",
        _raw_dir_of(sim_result) or "(no raw dir)",
    )
    return SpectreSimResult(None, ok=False, status=status, errors=errors, returncode=rc)


class SpectreSimResult:
    """`SimResult` over the bridge's flat PSF numeric dict.

    Lookup tries the analysis-prefixed key first (`ac_out`), then the bare name (`out`,
    and per-MOS op-point keys like `M0:gm` which carry no prefix). A missing scalar
    degrades to NaN — mirroring the ngspice result — so one absent metric never crashes
    the scorer; a missing wave raises (a wave is a hard request).

    `ok` / `status` / `errors` / `returncode` are the bridge's verdict on the run (see
    `_verdict_of`). A failed run is built with no data and no `raw_dir` (`_result_of`), so it
    reads like the ngspice no-RAW result: NaN scalars, raising waves.
    """

    def __init__(
        self,
        data: dict[str, Any] | None,
        *,
        raw_dir: str | None = None,
        ok: bool = True,
        status: str = "",
        errors: Iterable[str] = (),
        returncode: int | None = None,
    ) -> None:
        self._data: dict[str, Any] = dict(data or {})
        self.ok: bool = ok
        self.status: str = status
        self.errors: list[str] = list(errors)
        self.returncode: int | None = returncode
        # Post-sim canonical scalars (OCEAN measurements keyed by target-spec name), kept
        # SEPARATE from the raw PSF dict and consulted FIRST in `_lookup` so a canonical
        # metric wins even when its spec name collides with an analysis-prefixed PSF key
        # (e.g. a spec `gain` vs a PSF signal `ac_gain`).
        self._merged: dict[str, Any] = {}
        # The run's persisted PSF `-raw` dir (when work_dir= was set) — the OCEAN metrics
        # runner reads it; `None` for fixed-deck runs with no work_dir.
        self._raw_dir: str | None = raw_dir
        # Lazily-read swept PSF signals (AC/tran/noise) keyed by analysis — the bridge's flat
        # dict has only op-point/dc scalars, so a frequency/time-domain wave is read on demand
        # from `_raw_dir` (see `read_swept_psf`) and cached per analysis.
        self._swept: dict[str, dict[str, np.ndarray]] = {}
        # Optional duck-typed extension (see spice_engine.protocol): the bridge parses
        # PSF on the remote side and exposes no local simulator log file today; P5's
        # log/metrics plumbing may populate this.
        self.log_path: Path | str | None = None

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @property
    def raw_dir(self) -> str | None:
        """The persisted PSF `-raw` directory for this run (OCEAN measurement input)."""
        return self._raw_dir

    def merge_scalars(self, scalars: dict[str, float]) -> None:
        """Fold post-sim canonical scalars (OCEAN measurements keyed by target-spec name)
        in, so `scalar(name, analysis)` returns them. These are AUTHORITATIVE: `_lookup`
        consults them before any PSF key, so a canonical metric wins even when its name
        collides with an analysis-prefixed PSF signal (`gain` vs `ac_gain`)."""
        for key, value in scalars.items():
            self._merged[str(key)] = value

    def _lookup(self, name: str, analysis: str) -> Any | None:
        # Merged canonical scalars are authoritative — checked before the PSF keys.
        if name in self._merged:
            return self._merged[name]
        prefixes = _resolve_prefixes(analysis)
        for prefix in (*prefixes, ""):  # always end on the bare name
            key = f"{prefix}{name}"
            if key in self._data:
                return self._data[key]
        return None

    def scalar(self, name: str, analysis: str) -> float:
        value = self._lookup(name, analysis)
        if value is None:
            return float(np.nan)
        arr = np.asarray(value)
        if arr.size == 0:
            return float(np.nan)
        first = arr.reshape(-1)[0]
        return float(np.real(first))

    def _swept_signals(self, analysis: str) -> dict[str, np.ndarray]:
        """Swept PSF signals for `analysis` (AC/tran/noise), read once from `-raw` + cached."""
        key = str(analysis).strip().lower()
        if key not in self._swept:
            self._swept[key] = read_swept_psf(self._raw_dir, key)
        return self._swept[key]

    def wave(self, name: str, analysis: str) -> np.ndarray:
        value = self._lookup(name, analysis)
        if value is None:  # frequency/time-domain waves live in the swept PSF, not the flat dict
            value = self._swept_signals(analysis).get(name)
        if value is None:
            tried = [f"{p}{name}" for p in (*_resolve_prefixes(analysis), "")]
            raise KeyError(
                f"Spectre result has no signal {name!r} for analysis {analysis!r} "
                f"(looked up {tried}, then the swept PSF in the -raw dir)."
            )
        return np.asarray(value)


# ---------------------------------------------------------------------------
# gm/ID operating-point extractor — Spectre `.info` STRUCTs → consumer shape
# ---------------------------------------------------------------------------
# Canonical per-device op-point params read from Spectre's `info what=oppoint` STRUCTs
# (post-parsed as `<inst>:<param>` keys). A superset is tried — bsim4 spells drain current
# `ids` on some kits and `id` on others, and not every kit emits every capacitance — so
# missing members are simply skipped rather than forced to NaN in the result.
_OP_PARAM_NAMES: tuple[str, ...] = (
    "ids",
    "id",
    "gm",
    "gds",
    "gmbs",
    "vgs",
    "vds",
    "vbs",
    "vsb",
    "vth",
    "vdsat",
    "cgg",
    "cgs",
    "cgd",
    "cdd",
    "region",
)


def operating_point(
    result: Any,
    instance: str,
    *,
    params: tuple[str, ...] = _OP_PARAM_NAMES,
    analysis: str = "op",
) -> dict[str, float]:
    """One device's operating point in the gm/ID-consumer shape from an op-point result.

    Reads each present/finite ``<instance>:<param>`` scalar (the post-parsed `.info` STRUCT
    keys) and adds the derived gm/ID figures the sizing library speaks — ``gm_id`` (gm/ID
    efficiency, 1/V), ``gm_gds`` (intrinsic gain), ``ft`` (gm / 2π·cgg). Absent members are
    omitted, so this tolerates PDK-to-PDK op-param naming differences. Engine-neutral in
    principle (any `SimResult` carrying the ``inst:param`` op keys); Spectre in practice —
    that is where the `.info` post-parse produces them.
    """
    op: dict[str, float] = {}
    for p in params:
        value = float(result.scalar(f"{instance}:{p}", analysis))
        if not np.isnan(value):
            op[p] = value
    idrain = op.get("id", op.get("ids"))
    gm = op.get("gm")
    if gm is not None and idrain:
        op["gm_id"] = gm / abs(idrain)
    if gm is not None and op.get("gds"):
        op["gm_gds"] = gm / op["gds"]
    if gm is not None and op.get("cgg"):
        op["ft"] = gm / (2.0 * np.pi * op["cgg"])
    return op


def operating_points(
    result: Any, instances: Iterable[str], **kwargs: Any
) -> dict[str, dict[str, float]]:
    """`operating_point` for several instances → ``{instance: op-dict}``."""
    return {inst: operating_point(result, inst, **kwargs) for inst in instances}


class SpectreSimHandle:
    """`SimHandle` over the bridge's `concurrent.futures.Future[SimulationResult]`."""

    def __init__(self, future: Future[Any], *, label: str | None = None) -> None:
        self._future = future
        self._label = label
        self._result: SpectreSimResult | None = None

    def is_done(self) -> bool:
        return self._future.done()

    def result(self) -> SpectreSimResult:
        if self._result is None:
            self._result = _result_of(self._future.result(), label=self._label)
        return self._result


class SpectreSimulator:
    """`Simulator`-protocol adapter over a bridge Spectre simulator.

    `bridge` is duck-typed to the bridge's `SpectreSimulator`: it must expose
    `run_simulation(netlist, params) -> SimulationResult` and
    `submit(netlist, params) -> Future[SimulationResult]`. Tests inject a fake with that
    surface (no Cadence needed); production wires the real bridge via
    `create_spectre_simulator`.
    """

    def __init__(
        self,
        bridge: Any,
        netlist: Path | str | None = None,
        *,
        base_params: dict[str, Any] | None = None,
        deck_spec: SpectreDeckSpec | None = None,
        native_scs: Path | str | None = None,
        deck_dir: Path | str | None = None,
    ) -> None:
        if netlist is None and deck_spec is None and native_scs is None:
            raise ValueError(
                "SpectreSimulator needs a fixed .scs `netlist`, a `native_scs` file, or a `deck_spec`"
            )
        self._bridge = bridge
        self._netlist = Path(netlist) if netlist is not None else None
        # Three run modes (the bridge always executes a fixed file per run — *we* choose it):
        # * FIXED (`netlist`): run the `.scs` verbatim; overrides only staged.
        # * NATIVE FILE (`native_scs`): a hand-written `.scs` testbench (the YAML `netlist:`);
        #   every run rewrites its `parameters` line + corner includes IN PLACE via
        #   `render_native_scs` — the injection path for a native deck (the bridge drops
        #   params in local mode, so we do it).
        # * COMPOSED (`deck_spec`): materialise a deck assembled from parts.
        self._params: dict[str, Any] = dict(base_params or {})
        self._corner: Corner | None = None
        self._deck_spec = deck_spec
        self._native_scs = Path(native_scs) if native_scs is not None else None
        self._native_text = self._native_scs.read_text() if self._native_scs is not None else None
        # A rendered (native/composed) run needs a dir for the per-candidate `.scs`.
        if deck_spec is not None or native_scs is not None:
            self._deck_dir = Path(
                deck_dir if deck_dir is not None else tempfile.mkdtemp(prefix="spicexplorer-scs-")
            )
            self._deck_dir.mkdir(parents=True, exist_ok=True)
        else:
            self._deck_dir = Path(deck_dir) if deck_dir is not None else None
        self._run_seq = itertools.count(1)

    # -- protocol surface ---------------------------------------------------
    def update_params(self, params: dict[str, float]) -> bool:
        """Stage the optimizer's design-variable overrides (W/L, bias, …).

        Native-file / composed modes render these into each run's `parameters` line; fixed
        mode only records them (the bridge runs the file verbatim). Always returns True — an
        override on a param the deck doesn't declare is the emitter's concern, not a
        run-aborting error (matching the ngspice wrapper's lenient `update_params`).
        """
        design = self._params.setdefault("design_params", {})
        for key, value in params.items():
            design[key] = float(value)
        return True

    def apply_corner(self, corner: Corner, *, model_lib_root: str | None = None) -> None:
        """Emit the Spectre corner selection (`include "<file>" section=<sec>`) + rails.

        The ngspice seam strips `.lib`/injects `.lib …`/sets `.options temp=`; the Spectre
        equivalent is `include "<lib_file>" section=<section>` per model include, plus
        supply `parameters` and `temp` (with `tnom` beside it — `corner.options["tnom"]`, else
        the renderer's `DEFAULT_TNOM`). A second call replaces the last corner, never adds to it.
        A relative `lib_file` is resolved against `model_lib_root` (same contract as the
        ngspice wrapper's `apply_corner`); an absolute one is used as-is.
        """
        self._corner = corner
        self._params["corner"] = corner.name

        def _resolve(lib_file: str) -> str:
            p = Path(lib_file)
            if model_lib_root and not p.is_absolute():
                return str(Path(model_lib_root) / p)
            return str(p)

        # a sectionless include (section=None) is a library pulled in whole — no `section=`
        self._params["corner_includes"] = [
            f'include "{_resolve(inc.lib_file)}"'
            + (f" section={inc.section}" if inc.section else "")
            for inc in corner.model_includes
        ]
        self._params["temp"] = corner.temp
        # `tnom` comes from the corner's engine-neutral `options` (ngspice writes the same key as
        # `.options tnom=`); without it the renderer writes `DEFAULT_TNOM` next to `temp`.
        tnom = (corner.options or {}).get("tnom")
        if tnom is not None:
            self._params["tnom"] = float(tnom)
        else:
            self._params.pop("tnom", None)
        supplies: dict[str, float] = {s.node: float(s.value) for s in corner.supplies}
        supplies.update({k: float(v) for k, v in corner.params.items()})
        self._params["corner_params"] = supplies

    def _params_for(self, label: str | None) -> dict[str, Any]:
        """The staged params, plus this run's `run_label` when the caller names one.

        A labelled call forwards a *copy* so the label never sticks to the staged
        dict (one trial's `"<tb>__<corner>"` must not leak into the next)."""
        if label is None:
            return self._params
        params = dict(self._params)
        params["run_label"] = label
        return params

    def _netlist_for_run(self, label: str | None) -> Path:
        """Fixed mode → the configured `.scs`; native-file / composed mode → materialize
        the staged overrides (design params + corner) into a fresh per-run `.scs`."""
        if self._deck_spec is None and self._native_scs is None:
            assert self._netlist is not None  # guarded in __init__
            return self._netlist
        injected: dict[str, Any] = {}
        injected.update(self._params.get("design_params") or {})
        injected.update(self._params.get("corner_params") or {})
        if self._native_scs is not None:
            assert self._native_text is not None
            text = render_native_scs(
                self._native_text,
                parameters=injected,
                corner_includes=self._params.get("corner_includes"),
                temp=self._params.get("temp"),
                tnom=self._params.get("tnom"),
                source=self._native_scs,  # names the deck if the injection is ambiguous
            )
        else:
            assert self._deck_spec is not None
            text = render_spectre_deck(
                self._deck_spec,
                parameters=injected,
                corner_includes=self._params.get("corner_includes"),
                temp=self._params.get("temp"),
                tnom=self._params.get("tnom"),
            )
        assert self._deck_dir is not None  # set with deck_spec/native_scs in __init__
        safe_label = re.sub(r"[^A-Za-z0-9_.-]", "_", label) if label else "run"
        path = self._deck_dir / f"{next(self._run_seq):04d}_{safe_label}.scs"
        path.write_text(text)
        return path

    def run(self, *, label: str | None = None) -> SpectreSimResult:
        """Blocking run → `SimResult` (bridge `run_simulation`)."""
        netlist = self._netlist_for_run(label)
        sim_result = self._bridge.run_simulation(netlist, self._params_for(label))
        return _result_of(sim_result, label=label)

    def submit(self, *, label: str | None = None) -> SpectreSimHandle:
        """Non-blocking submit → `SimHandle` (bridge `submit` → `Future`)."""
        future = self._bridge.submit(self._netlist_for_run(label), self._params_for(label))
        return SpectreSimHandle(future, label=label)

    # -- inspection (used by tests / debugging) -----------------------------
    @property
    def staged_params(self) -> dict[str, Any]:
        """The params dict staged for the deck emitter / forwarded to the bridge."""
        return self._params


def create_spectre_simulator(
    netlist: Path | str | None = None,
    *,
    vb_env: dict[str, str] | None = None,
    vb_env_file: Path | str | None = None,
    base_params: dict[str, Any] | None = None,
    deck_spec: SpectreDeckSpec | None = None,
    native_scs: Path | str | None = None,
    deck_dir: Path | str | None = None,
    **bridge_kwargs: Any,
) -> SpectreSimulator:
    """Lazy factory: construct a Spectre `Simulator` backed by the real bridge.

    `virtuoso_bridge` is imported **here**, not at module load, so ngspice-only users never
    need it. `vb_env` is applied to `os.environ` (via `setdefault`, so it never clobbers an
    already-set value) **before** the bridge is constructed.

    **`vb_env_file` is the reliable profile pin**: the
    bridge's constructor calls `load_vb_env()` which discovers a `.env` (cwd-upward, then
    `~/.virtuoso-bridge/.env`) and `load_dotenv(..., override=True)`s it — clobbering both
    `vb_env` pre-sets and values sourced into the process env. On a host with a discoverable
    remote-profile `.env`, that silently flips a local-mode run to SSH. Passing
    `vb_env_file` registers the file via the bridge's `set_runtime_env_file`, which wins
    over discovery on every subsequent `load_vb_env()`.

    Raises `ImportError` with an actionable hint when the bridge isn't installed.
    """
    if vb_env:
        for key, value in vb_env.items():
            os.environ.setdefault(key, str(value))

    try:
        # Optional dependency, resolved only where the bridge is installed (the research
        # server); the guard below is the whole point, so a missing import is expected —
        # the bare `# type: ignore` keeps a bridge-less checkout pyright-clean.
        import virtuoso_bridge.spectre.runner as _vbr  # type: ignore

        _BridgeSpectre = _vbr.SpectreSimulator
    except ImportError as exc:  # pragma: no cover - exercised only without the bridge
        raise ImportError(
            "The Spectre backend requires the optional 'virtuoso-bridge' dependency, which "
            "is not installed. Install the bridge (external/virtuoso-bridge-lite) to use "
            "sim_engine='spectre'. ngspice-only users need nothing extra."
        ) from exc

    if vb_env_file is not None:
        from virtuoso_bridge.env import set_runtime_env_file  # type: ignore

        set_runtime_env_file(vb_env_file)

    bridge = _BridgeSpectre.from_env(**bridge_kwargs)
    return SpectreSimulator(
        bridge=bridge,
        netlist=netlist,
        base_params=base_params,
        deck_spec=deck_spec,
        native_scs=native_scs,
        deck_dir=deck_dir,
    )


__all__ = [
    "SpectreSimulator",
    "SpectreSimResult",
    "SpectreSimHandle",
    "SpectreDeckSpec",
    "create_spectre_simulator",
    "parse_psfascii_oppoint",
    "render_spectre_deck",
]
