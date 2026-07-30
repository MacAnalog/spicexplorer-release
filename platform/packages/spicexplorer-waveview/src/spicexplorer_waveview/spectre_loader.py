"""Spectre psfascii raw dir → :class:`~spicexplorer_waveview.dataset.WaveDataset`.

Reads a persisted Spectre ``-raw`` output directory: every swept psfascii PSF
(``ac.ac`` / ``dc.dc`` / ``tran.tran`` / ``noise.noise`` / ``pnoise.pnoise`` /
``<n>.fd.pss`` / ``stb.stb``), the non-swept op-point PSF (``dcOp.dc`` node values),
and the per-device ``*.info`` op-point STRUCTs (``inst:param`` scalars like ``M0:gm``).

This is a deliberate SIBLING of ``spicexplorer.backends.spectre.read_swept_psf`` /
``parse_psfascii_oppoint`` — waveview is a leaf tool that must not import the optimizer
package (peer tools never import each other), so the analysis→file contract is restated
here and pinned to the backend's by tests, not imports. File-name → analysis mapping,
contract-file preference, and abscissa aliasing all match the backend's semantics so a
recipe measured through ``DatasetResult`` reads the same wave ``SpectreSimResult`` would.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from .dataset import WaveAnalysis, WaveDataset, WaveSignal

__all__ = ["load_spectre_raw_dir", "SWEEP_EXT_TO_ANALYSIS"]

# PSF file extension → engine-neutral analysis key (mirror of the backend's _SWEEP_EXT,
# inverted). Ordered longest-suffix-first so `.fd.pss` wins over a plain suffix match.
SWEEP_EXT_TO_ANALYSIS: dict[str, str] = {
    ".fd.pss": "pss",
    ".td.pss": "pss_td",  # time-domain steady state — viewer-only (no registry recipes)
    # periodic AC: one PSF per output sideband (pac.<k>.pac). Harmonic 0 is the
    # signal-band (chopper/SC) transfer, so `.0.pac` claims the canonical `pac` key
    # (the backend reader's rule); other sidebands land under `pac_sb` (viewer-only).
    # The suffix can't false-match `pac.10.pac` (its last 6 chars are `10.pac`). The
    # metadata-only `pac.pac` parent index is skipped explicitly in the load loop.
    ".0.pac": "pac",
    ".pac": "pac_sb",
    ".pnoise": "pnoise",
    ".noise": "noise",
    ".tran": "tran",
    ".stb": "stb",
    ".ac": "ac",
    ".dc": "dc",
}

# The canonical abscissa aliases per analysis (mirror of the backend's _SWEEP_ABSCISSA):
# the sweep vector is exported under its native PSF name AND these, so recipes needn't
# know Spectre spells frequency `freq`.
_SWEEP_ABSCISSA: dict[str, tuple[str, ...]] = {
    "ac": ("frequency", "freq"),
    "dc": ("dc", "sweep"),
    "tran": ("time",),
    "noise": ("frequency", "freq"),
    "pnoise": ("frequency", "freq"),
    "pss": ("frequency", "freq"),
    "pss_td": ("time",),
    "pac": ("frequency", "freq"),
    "pac_sb": ("frequency", "freq"),
    "stb": ("frequency", "freq"),
}

# Spectre dataset alias map: the registry's noise-family analysis strings all resolve to
# the one swept density PSF, exactly like the backend's `_ANALYSIS_PREFIXES` chains.
_SPECTRE_ALIASES: dict[str, str] = {
    "noise_spectrum": "noise",
    "noise_spectral": "noise",
}

# ADE-standard `info` dumps that are NOT operating-point data. Skipping them keeps the
# dataset lean — and, for `modelParameter` (`info what=models`), keeps NDA foundry
# model-card values from ever entering viewer data. (Same set as the Spectre backend.)
_INFO_SKIP_STEMS: frozenset[str] = frozenset(
    {"modelParameter", "designParamVals", "outputParameter", "primitives", "subckts", "element"}
)

_STRUCT_DEF_RE = re.compile(r'^"([^"]+)"\s+STRUCT\(')
_STRUCT_MEMBER_RE = re.compile(r'^"([^"]+)"\s+(?:FLOAT|INT|DOUBLE|BYTE)\b')
_STRUCT_VALUE_OPEN_RE = re.compile(r'^"([^"]+)"\s+"([^"]+)"\s+\(\s*$')


def parse_info_structs(text: str) -> dict[str, float]:
    """``inst:param`` scalars from one psfascii ``info`` file's STRUCT data.

    Reimplements the Spectre backend's ``_parse_info_structs`` (see module docstring on
    why it can't be imported): the TYPE section declares per-model STRUCT member names in
    order; each VALUE entry ``"X0.M0" "bsim4" (`` is followed by one number per member.
    """
    lines = text.splitlines()

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


def _match_ext(name: str) -> tuple[str, str] | None:
    """Longest matching known PSF extension for a file name → (ext, analysis key)."""
    lowered = name.lower()
    for ext, analysis in SWEEP_EXT_TO_ANALYSIS.items():  # dict order = longest first
        if lowered.endswith(ext):
            return ext, analysis
    return None


def _unique_key(base: str, taken: set[str]) -> str:
    if base not in taken:
        return base
    n = 2
    while f"{base}:{n}" in taken:
        n += 1
    return f"{base}:{n}"


def _read_psf_analysis(path: Path, key: str, ds: WaveDataset) -> WaveAnalysis | None:
    """One psfascii PSF file → a :class:`WaveAnalysis` (None + warning on parse failure)."""
    try:
        from psf_utils import PSF
    except ImportError as exc:  # pragma: no cover — declared dependency
        raise ImportError(
            "reading Spectre psfascii PSFs needs 'psf-utils' "
            "(a declared dependency of spicexplorer-waveview; `uv sync` installs it)."
        ) from exc
    try:
        psf = PSF(str(path))
    except Exception as exc:  # noqa: BLE001 — binary PSF / malformed file: keep loading the rest
        ds.warnings.append(f"could not parse PSF {path.name!r}: {exc}")
        return None

    an = WaveAnalysis(analysis=key, native_name=path.name)
    try:
        sweep = psf.get_sweep()
    except Exception:  # noqa: BLE001 — psf_utils raises on multi-sweep corner cases
        sweep = None
    if sweep is not None:
        absc = np.asarray(sweep.abscissa)
        sweep_name = str(sweep.name)
        sweep_units = str(getattr(sweep, "units", "") or "") or None
        an.sweep = sweep_name
        an.signals[sweep_name] = WaveSignal(name=sweep_name, data=absc, units=sweep_units)
        base_key = key.split(":", 1)[0]
        for alias in _SWEEP_ABSCISSA.get(base_key, ()):
            if alias not in an.signals:
                an.signals[alias] = WaveSignal(name=alias, data=absc, units=sweep_units)

    skipped_text: list[str] = []
    for sig in psf.all_signals():
        name = str(sig.name)
        # NO skip on collision: a REAL trace that shares an abscissa-alias name
        # ("frequency"/"time") must WIN over the alias — read_swept_psf overwrites the
        # same way, and parity with the backend is the contract here.
        data = np.asarray(sig.ordinate)
        if data.dtype.kind not in "fciub":  # STRING/object signals (e.g. the stb margin
            skipped_text.append(name)  # PSF's stability verdict text) — arrays only here
            continue
        units = str(getattr(sig, "units", "") or "") or None
        an.signals[name] = WaveSignal(name=name, data=data, units=units)
        if an.sweep is None and data.size == 1:  # non-swept PSF (dcOp): point values
            an.scalars[name] = float(np.real(data.reshape(-1)[0]))
    if skipped_text:
        ds.warnings.append(f"{path.name}: skipped non-numeric signal(s) {skipped_text}")
    return an


def load_spectre_raw_dir(path: str | Path) -> WaveDataset:
    """Load a Spectre psfascii raw directory into a :class:`WaveDataset`.

    Analysis keys follow the backend contract: the contract-named file (``ac.ac``,
    ``tran.tran``, …) claims the canonical key when siblings share an extension (e.g.
    a ``dc`` sweep next to a ``dcOp`` op-point both end ``.dc``); others get
    ``<key>:<stem>``. ``dcOp.dc`` maps to ``op``. ``*.info`` STRUCT op-points merge
    into the ``op`` analysis as ``inst:param`` scalars. ``*.cache`` siblings and the
    ADE model/parameter dumps are skipped.
    """
    root = Path(path)
    if not root.is_dir():
        raise FileNotFoundError(f"Spectre raw directory not found: {root}")

    ds = WaveDataset(source=str(root), engine="spectre", aliases=dict(_SPECTRE_ALIASES))

    candidates = sorted(p for p in root.rglob("*") if p.is_file())
    psf_files: list[tuple[Path, str, str]] = []  # (file, ext, analysis)
    info_files: list[Path] = []
    for f in candidates:
        if f.name.endswith(".cache"):
            continue
        if f.name == "pac.pac":
            continue  # the metadata-only pac parent index (types, no node data)
        if f.suffix == ".info":
            if f.stem not in _INFO_SKIP_STEMS:
                info_files.append(f)
            continue
        m = _match_ext(f.name)
        if m is not None:
            psf_files.append((f, m[0], m[1]))

    # Contract-named file first per analysis key (matches read_swept_psf's sort), so it
    # claims the canonical key; siblings keep their stem as a suffix.
    taken: set[str] = set()
    for f, ext, base in sorted(psf_files, key=lambda t: (t[2], t[0].name != f"{t[2]}{t[1]}", str(t[0]))):
        stem = f.name[: -len(ext)]
        if ext == ".dc" and stem == "dcOp":
            base = "op"
        key = base if base not in taken else _unique_key(f"{base}:{stem}", taken)
        an = _read_psf_analysis(f, key, ds)
        if an is None:
            continue
        taken.add(key)
        ds.analyses[key] = an

    if info_files:
        op = ds.analyses.get("op")
        if op is None:
            op = WaveAnalysis(analysis="op", native_name="*.info op-point")
            ds.analyses["op"] = op
        for f in info_files:
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                ds.warnings.append(f"could not read info file {f.name!r}: {exc}")
                continue
            op.scalars.update(parse_info_structs(text))

    if not ds.analyses:
        ds.warnings.append(f"no recognised psfascii PSF files under {root}")
    return ds
