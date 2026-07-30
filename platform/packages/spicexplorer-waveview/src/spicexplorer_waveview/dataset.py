"""The engine-neutral ``WaveDataset`` model + its ``SimResult`` protocol adapter.

A ``WaveDataset`` is what both loaders (:mod:`.ngspice_loader`, :mod:`.spectre_loader`)
produce from a result artifact on disk: a mapping of **engine-neutral analysis keys**
(``"ac"`` / ``"dc"`` / ``"op"`` / ``"tran"`` / ``"noise"`` / ``"noise_spectrum"`` /
``"pss"`` / ``"pnoise"`` / ``"stb"`` …) to their signals (numpy arrays, complex for AC)
plus per-analysis scalars (e.g. Spectre per-device op-point ``inst:param`` values).

``DatasetResult`` wraps a dataset behind the two-method
:class:`~spicexplorer_core.spice_engine.protocol.SimResult` surface (``scalar`` /
``wave``), so the **entire Tier-1 measurement registry**
(:func:`spicexplorer_core.measurements.registry.measure`) runs against any loaded
artifact — the viewer computes ``dcgain``/``ugf``/``pm``/``thd``/… on a file someone
hands it, with the same math the optimizer uses on a live run.

Semantics mirror the engines' own result adapters (``NgspiceSimResult`` /
``SpectreSimResult``): a missing scalar degrades to NaN, a missing wave raises.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

import numpy as np

__all__ = ["WaveSignal", "WaveAnalysis", "WaveDataset", "DatasetResult", "merge_datasets"]


# Cross-engine analysis-string aliases (the registry's recipe vocabulary is wider than
# the loaders' canonical keys). Applied AFTER the dataset's own engine-specific aliases,
# so e.g. a Spectre dataset maps "noise_spectrum" → "noise" (its density sweep) while an
# ngspice dataset keeps "noise_spectrum" (its own density plot) distinct from "noise".
_COMMON_ALIASES: dict[str, str] = {
    "transient": "tran",
    "oppoint": "op",
    "noise_integrated": "noise",
    "noise_spectral": "noise_spectrum",
}


@dataclass
class WaveSignal:
    """One named trace of an analysis (a numpy array, complex for AC-family sweeps)."""

    name: str
    data: np.ndarray
    units: str | None = None  # engine-reported units ("V", "A", "s", "Hz") when known

    @property
    def is_complex(self) -> bool:
        return bool(np.iscomplexobj(self.data))

    @property
    def n_points(self) -> int:
        return int(np.asarray(self.data).size)


@dataclass
class WaveAnalysis:
    """All signals of one analysis, keyed by trace name, plus point-value scalars."""

    analysis: str  # engine-neutral key ("ac", "tran", "op", …)
    native_name: str  # ngspice plot title / Spectre PSF file name — for display
    signals: dict[str, WaveSignal] = field(default_factory=dict)
    sweep: str | None = None  # abscissa signal name ("frequency"/"time"/…), None for point data
    # Point scalars that are not traces: Spectre per-device op-point values ("M0:gm"),
    # non-swept PSF values (dcOp node voltages), ngspice op values also land as 1-pt signals.
    scalars: dict[str, float] = field(default_factory=dict)

    @property
    def n_points(self) -> int:
        if self.sweep and self.sweep in self.signals:
            return self.signals[self.sweep].n_points
        return max((s.n_points for s in self.signals.values()), default=0)


@dataclass
class WaveDataset:
    """One loaded result artifact: analyses + provenance + engine-specific alias map."""

    source: str  # the .raw file / PSF raw-dir path this was loaded from
    engine: str  # "ngspice" | "spectre"
    analyses: dict[str, WaveAnalysis] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)  # analysis alias → canonical key
    log_path: str | None = None  # discovered/linked simulator log, if any
    warnings: list[str] = field(default_factory=list)  # non-fatal load diagnostics

    def resolve_analysis(self, analysis: str) -> WaveAnalysis | None:
        """Map an engine-neutral analysis string (or alias) to its loaded analysis."""
        if analysis in self.analyses:  # exact key first — suffixed keys ("dc:dcOp2",
            return self.analyses[analysis]  # "stb:stb.margin") may carry file-stem case
        key = str(analysis).strip().lower()
        key = self.aliases.get(key, key)
        key = _COMMON_ALIASES.get(key, key)
        key = self.aliases.get(key, key)  # engine alias may target the common name too
        return self.analyses.get(key)

    def find_signal(self, analysis: str, name: str) -> WaveSignal | None:
        """Locate a signal with cross-engine name tolerance.

        Lookup order: exact → case-insensitive → ngspice-wrapped ``v(name)``/``i(name)``
        → unwrapped bare name (so a Spectre-style ``vout`` recipe finds ngspice's
        ``v(vout)`` and vice versa). Returns None when the analysis or signal is absent.
        """
        an = self.resolve_analysis(analysis)
        if an is None:
            return None
        sig = an.signals.get(name)
        if sig is not None:
            return sig
        lowered = {k.lower(): v for k, v in an.signals.items()}
        want = name.strip().lower()
        if want in lowered:
            return lowered[want]
        if "(" not in want:  # bare name → try the ngspice v()/i() spellings
            for wrapped in (f"v({want})", f"i({want})"):
                if wrapped in lowered:
                    return lowered[wrapped]
        elif want.startswith(("v(", "i(")) and want.endswith(")"):  # wrapped → try bare
            bare = want[2:-1]
            if bare in lowered:
                return lowered[bare]
        return None

    def iter_signals(self) -> Iterator[tuple[str, WaveSignal]]:
        for key, an in self.analyses.items():
            for sig in an.signals.values():
                yield key, sig


class DatasetResult:
    """A :class:`WaveDataset` behind the ``SimResult`` protocol (``scalar``/``wave``).

    This is the bridge that lets :func:`spicexplorer_core.measurements.registry.measure`
    evaluate any Tier-1 ``{meas: …}`` recipe against a loaded artifact. Behaviour mirrors
    the engines' own adapters: ``scalar`` degrades to NaN on a miss, ``wave`` raises.
    """

    def __init__(self, dataset: WaveDataset) -> None:
        self._ds = dataset

    @property
    def dataset(self) -> WaveDataset:
        return self._ds

    def scalar(self, name: str, analysis: str) -> float:
        an = self._ds.resolve_analysis(analysis)
        if an is not None and name in an.scalars:
            return float(an.scalars[name])
        sig = self._ds.find_signal(analysis, name)
        if sig is None:
            # op-point inst:param scalars ride the "op" analysis regardless of the
            # requested analysis string (mirrors SpectreSimResult's bare-name fallback).
            op = self._ds.resolve_analysis("op")
            if op is not None and name in op.scalars:
                return float(op.scalars[name])
            return float(np.nan)
        arr = np.asarray(sig.data)
        if arr.size == 0:
            return float(np.nan)
        return float(np.real(arr.reshape(-1)[0]))

    def wave(self, name: str, analysis: str) -> np.ndarray:
        sig = self._ds.find_signal(analysis, name)
        if sig is None:
            an = self._ds.resolve_analysis(analysis)
            have = sorted(an.signals) if an is not None else "<analysis not in dataset>"
            raise KeyError(
                f"dataset {self._ds.source!r} has no signal {name!r} for analysis "
                f"{analysis!r} (available: {have})."
            )
        return np.asarray(sig.data)


def merge_datasets(
    members: "list[tuple[str, WaveDataset]]",
    *,
    source: str,
    log_path: str | None = None,
) -> WaveDataset:
    """Combine several loaded artifacts into ONE multi-analysis dataset.

    The multi-testbench run case: a keep_raw optimizer/manual-sim run leaves one
    ``.raw`` per testbench (``run_1_tb_ac/…``, ``run_1_tb_tran/…``); merging them
    gives a single dataset whose analyses are the union — ``ac`` + ``tran`` +
    ``noise`` as tabs of one viewer entry, instead of N separate datasets.

    ``members`` are ``(label, dataset)`` pairs in priority order — the first
    holder of an analysis key keeps the bare key; later duplicates get a stable
    ``"<key>#2"``/``"#3"`` suffix (clients strip the ``#n`` for styling). Each
    suffixed analysis is a shallow ``dataclasses.replace`` so the underlying
    numpy arrays are shared, never copied. A non-empty ``label`` is appended to
    the analysis' ``native_name`` so provenance survives the merge. Signals are
    NEVER merged across members — same-named traces from different testbenches
    stay in their own analyses.
    """
    from dataclasses import replace

    if not members:
        raise ValueError("merge_datasets needs at least one member dataset")

    engines = []
    for _, ds in members:
        if ds.engine not in engines:
            engines.append(ds.engine)
    merged = WaveDataset(
        source=source,
        engine=engines[0] if len(engines) == 1 else "mixed",
        log_path=log_path if log_path is not None else members[0][1].log_path,
    )
    for label, ds in members:
        for alias, target in ds.aliases.items():
            merged.aliases.setdefault(alias, target)
        for w in ds.warnings:
            merged.warnings.append(f"{label}: {w}" if label else w)
        for key, an in ds.analyses.items():
            out_key = key
            n = 2
            while out_key in merged.analyses:
                out_key = f"{key}#{n}"
                n += 1
            native = f"{an.native_name} · {label}" if label else an.native_name
            merged.analyses[out_key] = replace(an, analysis=out_key, native_name=native)
    return merged
