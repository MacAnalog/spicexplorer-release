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
"""

from __future__ import annotations

import itertools
import os
import re
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from .spectre_deck import SpectreDeckSpec, render_native_scs, render_spectre_deck

if TYPE_CHECKING:  # keep this module import-cheap and Cadence-free
    from concurrent.futures import Future

    from spicexplorer_core.pvt import Corner


# analysis (engine-neutral string) → ordered PSF-key prefix chain, live-validated
# against real licensed-kit psfascii (2026-07-05). Per-MOS op scalars (`M0:gm`) are merged in
# bare by our own info-file post-parse below; op-point NODE voltages come from `dcOp.dc`
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


# ADE-standard `info` dumps that are NOT operating-point data. Skipping them keeps the
# result dict lean — and, for `modelParameter` (`info what=models`), keeps NDA foundry
# model-card values from ever entering result data. Never emit those in a deck anyway.
_INFO_SKIP_STEMS: frozenset[str] = frozenset(
    {"modelParameter", "designParamVals", "outputParameter", "primitives", "subckts", "element"}
)

_STRUCT_DEF_RE = re.compile(r'^"([^"]+)"\s+STRUCT\(')
_STRUCT_MEMBER_RE = re.compile(r'^"([^"]+)"\s+(?:FLOAT|INT|DOUBLE|BYTE)\b')
_STRUCT_VALUE_OPEN_RE = re.compile(r'^"([^"]+)"\s+"([^"]+)"\s+\(\s*$')


def _parse_info_structs(text: str) -> dict[str, float]:
    """Extract `<inst>:<param>` scalars from one psfascii `info` file's STRUCT data.

    psfascii op-point files define per-model STRUCTs in the TYPE section (member names in
    order, e.g. bsim4's `ids`/`vgs`/…/`gm`/`region`) and emit, per instance, a VALUE entry
    `"X0.M0" "bsim4" (` followed by one number per member. The bridge's parser drops these
    (it only handles `"name" value` lines) — this fills the gap on our side of the seam.
    """
    lines = text.splitlines()

    # TYPE section: struct member names, in declaration order, per struct type.
    structs: dict[str, list[str]] = {}
    section = ""
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped in ("HEADER", "TYPE", "SWEEP", "TRACE", "VALUE", "END"):
            section = stripped
            i += 1
            continue
        if section == "TYPE":
            m_def = _STRUCT_DEF_RE.match(stripped)
            if m_def:
                members: list[str] = []
                depth = stripped.count("(") - stripped.count(")")
                i += 1
                while i < len(lines) and depth > 0:
                    inner = lines[i].strip()
                    if depth == 1:
                        m_member = _STRUCT_MEMBER_RE.match(inner)
                        if m_member:
                            members.append(m_member.group(1))
                    depth += inner.count("(") - inner.count(")")
                    i += 1
                structs[m_def.group(1)] = members
                continue
        elif section == "VALUE":
            break
        i += 1

    # VALUE section: zip each instance's number block with its struct's member names.
    out: dict[str, float] = {}
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == "END":
            break
        m_open = _STRUCT_VALUE_OPEN_RE.match(stripped)
        if m_open:
            inst, type_name = m_open.group(1), m_open.group(2)
            values: list[float | None] = []
            i += 1
            while i < len(lines):
                inner = lines[i].strip()
                # the numeric block ends at ")" — or ") PROP(" when the instance carries
                # a trailing PROP annotation (real kit output: `"model" "nmos_lvt.10"`)
                if inner.startswith(")"):
                    break
                try:
                    values.append(float(inner))
                except ValueError:
                    values.append(None)
                i += 1
            members = structs.get(type_name, [])
            if members and len(members) == len(values):
                for member, value in zip(members, values):
                    if value is not None:
                        out[f"{inst}:{member}"] = value
        i += 1
    return out


def parse_psfascii_oppoint(output_dir: Path | str) -> dict[str, float]:
    """Per-instance op-point scalars (`X0.M0:gm`, …) from a run's psfascii `*.info` files.

    Complements the bridge's own directory parser (which drops STRUCT values). Skips the
    ADE model/parameter dumps in `_INFO_SKIP_STEMS`; unreadable or malformed files degrade
    to "no keys", never an exception — a missing op-point scalar then scores as NaN.
    """
    out: dict[str, float] = {}
    root = Path(output_dir)
    if not root.is_dir():
        return out
    for info_file in sorted(root.rglob("*.info")):
        if info_file.stem in _INFO_SKIP_STEMS:
            continue
        try:
            text = info_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out.update(_parse_info_structs(text))
    return out


# Swept analyses (AC / tran / noise) land in their OWN psfascii PSF file (`ac.ac`,
# `tran.tran`, `noise.noise`) — NOT in the bridge's flat scalar dict, which carries only
# op-point / dc node values (so an op-point run looks fine while the AC sweep is silently
# absent). `SpectreSimResult` reads them lazily from the persisted `-raw` dir (mirroring the
# op-point `*.info` post-parse) so the engine-neutral measurement registry can pull an AC
# transfer / transient / noise-spectrum wave uniformly for ngspice AND Spectre.
_SWEEP_EXT: dict[str, str] = {
    "ac": ".ac",
    # a DC *sweep* (`dc dc dev=… start=… stop=… step=…`, e.g. the linearity/ICMR transfer).
    # The op-point analysis (`dcOp dc`) also writes a `.dc` PSF — `read_swept_psf` prefers
    # the exact `dc.dc` file so the sweep wins when both are present.
    "dc": ".dc",
    "tran": ".tran",
    "transient": ".tran",
    "noise": ".noise",
    "noise_spectrum": ".noise",
    "noise_spectral": ".noise",
    # PSS harmonics: the frequency-domain fd-PSF (`<name>.fd.pss`) IS a swept PSF — sweep
    # `freq` = harmonic frequencies [0, f0, 2·f0, …], each signal a COMPLEX per-harmonic
    # phasor array. (The sibling `<name>.td.pss` is the time-domain steady state; not read here.)
    "pss": ".fd.pss",
    # periodic noise riding a PSS solution (`pnoise ( out ref ) pnoise …`): a plain swept
    # PSF `pnoise.pnoise` — sweep `freq` (the noise offset band), top-level `out`/`in`
    # V/√Hz densities + `gain`, plus per-device `INST:src` V²/Hz contributions (discovered
    # live on the closed lane, 2026-07-11). Spectre also leaves a `pnoise.pnoise.cache` sibling,
    # which the `*{ext}` glob correctly ignores (it ends `.cache`). NOTE `*.noise` does
    # NOT match `pnoise.pnoise` (the char before `noise` is `p`, not `.`), so a deck with
    # both analyses keeps them cleanly separate.
    "pnoise": ".pnoise",
    # periodic AC riding a PSS solution (`pac pac …`): Spectre writes ONE PSF per sideband
    # — `pac.<k>.pac` is harmonic k (the response observed at sideband k of the input's
    # small signal), plus a metadata-only `pac.pac` "pac parent" index (types Tau/Alpha/…,
    # no node data). The signal-band transfer of a chopper/SC circuit is the BASEBAND
    # response, harmonic 0, so `pac` pins to `.0.pac` (the `*.0.pac` glob matches only
    # `pac.0.pac`, never `pac.10.pac`/`pac.pac`) — the same "pick the meaningful sibling"
    # rule that pins `pss` to `.fd.pss`. Higher sidebands stay reachable by reading
    # `pac.<k>.pac` directly. Live-validated on an ideal chopper, 2026-07-17.
    "pac": ".0.pac",
    # loop-gain (stability) sweep: the `loopGain` complex-vs-freq wave the pm_loop /
    # gain-margin recipes read (the stb bench's payload).
    "stb": ".stb",
}
# Sideband selection: the analysis spelling `pac.<k>` reads the k-th sideband PSF
# (`pac.<k>.pac`) instead of the baseband — conversion-gain / ripple analysis
# (`wave("out", "pac.1")`). `pac` alone stays the baseband (`pac.0.pac`).
_PAC_SIDEBAND_RE = re.compile(r"pac\.(-?\d+)")
# The canonical abscissa name the registry looks up per analysis kind (recipe defaults:
# `frequency` for ac/noise, `time` for tran), aliased onto the PSF sweep vector so a recipe
# needn't know Spectre spells it `freq`.
_SWEEP_ABSCISSA: dict[str, tuple[str, ...]] = {
    "ac": ("frequency", "freq"),
    "dc": ("dc", "sweep"),  # the swept-source value; recipes usually read the input NET trace
    "tran": ("time",),
    "transient": ("time",),
    "noise": ("frequency", "freq"),
    "noise_spectrum": ("frequency", "freq"),
    "noise_spectral": ("frequency", "freq"),
    "pnoise": ("frequency", "freq"),
    "pss": ("frequency", "freq"),  # harmonic frequencies as the abscissa (index k → k·f0)
    "pac": ("frequency", "freq"),  # the baseband small-signal sweep of the periodic OP
    "stb": ("frequency", "freq"),
}


def read_swept_psf(output_dir: Path | str | None, analysis: str) -> dict[str, np.ndarray]:
    """Signals from a run's swept psfascii PSF (`ac.ac`/`tran.tran`/`noise.noise`) as arrays.

    Returns ``{signal_name: ndarray}`` — every trace plus the sweep vector, the latter also
    aliased to the registry's canonical abscissa name (`frequency`/`time`). Empty when the
    analysis is not swept, no matching PSF exists, or ``output_dir`` is unset — a missing wave
    then raises in :meth:`SpectreSimResult.wave` exactly as a missing flat signal does.

    The analysis spelling ``pac.<k>`` selects the k-th sideband of a periodic-AC run
    (the ``pac.<k>.pac`` PSF) instead of the baseband — the conversion-gain / ripple
    read; plain ``pac`` stays harmonic 0.
    """
    key = str(analysis).strip().lower()
    sideband = _PAC_SIDEBAND_RE.fullmatch(key)
    if sideband:
        key, ext = "pac", f".{sideband.group(1)}.pac"
    else:
        ext = _SWEEP_EXT.get(key)
    root = Path(output_dir) if output_dir else None
    if ext is None or root is None or not root.is_dir():
        return {}
    files = sorted(p for p in root.rglob(f"*{ext}") if p.is_file())
    if not files:
        return {}
    # Prefer the contract-named PSF when siblings share the extension (e.g. a deck with both
    # a `dc` sweep and a `dcOp` op-point leaves `dc.dc` AND `dcOp.dc`; alphabetical order is
    # luck, not a contract — same reasoning that pins `pss` to `.fd.pss` over `.td.pss`).
    files.sort(key=lambda p: (p.name != f"{key}{ext}", str(p)))
    try:
        from psf_utils import PSF
    except ImportError as exc:  # pragma: no cover - psf_utils is a declared dependency
        raise ImportError(
            "reading a Spectre swept PSF (AC/tran/noise) needs 'psf_utils' "
            "(a declared dependency of spicexplorer; `uv sync` installs it)."
        ) from exc

    psf = PSF(str(files[0]))
    out: dict[str, np.ndarray] = {}
    sweep = psf.get_sweep()
    if sweep is not None:
        absc = np.asarray(sweep.abscissa)
        out[str(sweep.name)] = absc
        for alias in _SWEEP_ABSCISSA.get(key, ()):
            out.setdefault(alias, absc)
    for sig in psf.all_signals():
        out[str(sig.name)] = np.asarray(sig.ordinate)
    return out


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


class SpectreSimResult:
    """`SimResult` over the bridge's flat PSF numeric dict.

    Lookup tries the analysis-prefixed key first (`ac_out`), then the bare name (`out`,
    and per-MOS op-point keys like `M0:gm` which carry no prefix). A missing scalar
    degrades to NaN — mirroring the ngspice result — so one absent metric never crashes
    the scorer; a missing wave raises (a wave is a hard request).
    """

    def __init__(self, data: dict[str, Any] | None, *, raw_dir: str | None = None) -> None:
        self._data: dict[str, Any] = dict(data or {})
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
    "ids", "id", "gm", "gds", "gmbs", "vgs", "vds", "vbs", "vsb",
    "vth", "vdsat", "cgg", "cgs", "cgd", "cdd", "region",
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

    def __init__(self, future: "Future[Any]") -> None:
        self._future = future
        self._result: SpectreSimResult | None = None

    def is_done(self) -> bool:
        return self._future.done()

    def result(self) -> SpectreSimResult:
        if self._result is None:
            sim_result = self._future.result()
            self._result = SpectreSimResult(
                _data_of(sim_result), raw_dir=_raw_dir_of(sim_result)
            )
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
                deck_dir
                if deck_dir is not None
                else tempfile.mkdtemp(prefix="spicexplorer-scs-")
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

    def apply_corner(self, corner: "Corner", *, model_lib_root: str | None = None) -> None:
        """Emit the Spectre corner selection (`include "<file>" section=<sec>`) + rails.

        The ngspice seam strips `.lib`/injects `.lib …`/sets `.options temp=`; the Spectre
        equivalent is `include "<lib_file>" section=<section>` per model include, plus
        supply `parameters` and `temp`. Idempotent: re-applying replaces, never accumulates.
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

        self._params["corner_includes"] = [
            f'include "{_resolve(inc.lib_file)}" section={inc.section}'
            for inc in corner.model_includes
        ]
        self._params["temp"] = corner.temp
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
                source=self._native_scs,  # names the deck if the injection is ambiguous
            )
        else:
            assert self._deck_spec is not None
            text = render_spectre_deck(
                self._deck_spec,
                parameters=injected,
                corner_includes=self._params.get("corner_includes"),
                temp=self._params.get("temp"),
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
        return SpectreSimResult(_data_of(sim_result), raw_dir=_raw_dir_of(sim_result))

    def submit(self, *, label: str | None = None) -> SpectreSimHandle:
        """Non-blocking submit → `SimHandle` (bridge `submit` → `Future`)."""
        future = self._bridge.submit(self._netlist_for_run(label), self._params_for(label))
        return SpectreSimHandle(future)

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
