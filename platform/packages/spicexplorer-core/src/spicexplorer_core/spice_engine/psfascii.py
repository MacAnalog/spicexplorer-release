"""psfascii — the text result format a Spectre-class simulator writes (`-format psfascii -raw <dir>`),
read here without any vendor code.

One file per analysis (`ac.ac`, `tran.tran`, `noise.noise`, `dc.dc` / `dcOp.dc`, `<name>.fd.pss`,
`pac.<k>.pac`, `pnoise.pnoise`, `stb.stb`) plus per-instance operating-point STRUCTs in `*.info`.

**Why this lives in core.** Two peer tools read PSF — the optimizer's Spectre adapter
(`spicexplorer.backends.spectre`) and the viewer (`spicexplorer_waveview.spectre_loader`) — and peer
tools never import each other, so before this module each restated the file-name → analysis table,
the abscissa aliases and the STRUCT parser, pinned to each other by tests; design repos restated it
a third time (a licensed-kit LPF design's `lab/psf.py`). Core is the layer every tool imports. The blast-radius
rule in :mod:`.protocol` — "core imports no Cadence / bridge code; the Spectre adapter lives in an
optional, lazily-imported package" — is about the *adapter* and the *bridge*: this module imports
neither, it parses a text format, exactly as :mod:`.spicelib` reads ngspice rawfiles. The one
library the swept-file reader needs, `psf_utils` (small, pure Python), is imported lazily and
declared by the tools that read waves, not by core.

Public surface (the optimizer and the viewer re-export what they used to define):

* :func:`parse_info_structs` / :func:`read_oppoint_info` — `inst:param` op-point scalars.
* :data:`SWEEP_EXT` (analysis → file extension), :data:`EXT_TO_ANALYSIS` (the inverse, canonical
  keys, longest suffix first), :data:`SWEEP_ABSCISSA` (per-analysis abscissa aliases).
* :func:`find_swept_psf` (which file an analysis reads, contract-named sibling first),
  :func:`read_psf` (one file → `{signal: ndarray}`), :func:`read_swept_psf` (both).
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

__all__ = [
    "INFO_SKIP_STEMS",
    "STRUCT_DEF_RE",
    "STRUCT_MEMBER_RE",
    "STRUCT_VALUE_OPEN_RE",
    "parse_info_structs",
    "read_oppoint_info",
    "SWEEP_EXT",
    "EXT_TO_ANALYSIS",
    "SWEEP_ABSCISSA",
    "PAC_SIDEBAND_RE",
    "resolve_sweep_ext",
    "find_swept_psf",
    "read_psf",
    "read_swept_psf",
]


# ADE-standard `info` dumps that are NOT operating-point data. Skipping them keeps the
# result dict / viewer dataset lean — and, for `modelParameter` (`info what=models`), keeps NDA foundry
# model-card values from ever entering result data. Never emit those in a deck anyway.
INFO_SKIP_STEMS: frozenset[str] = frozenset(
    {"modelParameter", "designParamVals", "outputParameter", "primitives", "subckts", "element"}
)

STRUCT_DEF_RE = re.compile(r'^"([^"]+)"\s+STRUCT\(')
STRUCT_MEMBER_RE = re.compile(r'^"([^"]+)"\s+(?:FLOAT|INT|DOUBLE|BYTE)\b')
STRUCT_VALUE_OPEN_RE = re.compile(r'^"([^"]+)"\s+"([^"]+)"\s+\(\s*$')


def parse_info_structs(text: str) -> dict[str, float]:
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
            m_def = STRUCT_DEF_RE.match(stripped)
            if m_def:
                members: list[str] = []
                depth = stripped.count("(") - stripped.count(")")
                i += 1
                while i < len(lines) and depth > 0:
                    inner = lines[i].strip()
                    if depth == 1:
                        m_member = STRUCT_MEMBER_RE.match(inner)
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
        m_open = STRUCT_VALUE_OPEN_RE.match(stripped)
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


def read_oppoint_info(output_dir: Path | str) -> dict[str, float]:
    """Per-instance op-point scalars (`X0.M0:gm`, …) from a run's psfascii `*.info` files.

    Skips the
    ADE model/parameter dumps in `INFO_SKIP_STEMS`; unreadable or malformed files degrade
    to "no keys", never an exception — a missing op-point scalar then scores as NaN.
    """
    out: dict[str, float] = {}
    root = Path(output_dir)
    if not root.is_dir():
        return out
    for info_file in sorted(root.rglob("*.info")):
        if info_file.stem in INFO_SKIP_STEMS:
            continue
        try:
            text = info_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out.update(parse_info_structs(text))
    return out


# Swept analyses (AC / tran / noise) land in their OWN psfascii PSF file (`ac.ac`,
# `tran.tran`, `noise.noise`) — NOT in the bridge's flat scalar dict, which carries only
# op-point / dc node values (so an op-point run looks fine while the AC sweep is silently
# absent). `SpectreSimResult` reads them lazily from the persisted `-raw` dir (mirroring the
# op-point `*.info` post-parse) so the engine-neutral measurement registry can pull an AC
# transfer / transient / noise-spectrum wave uniformly for ngspice AND Spectre.
SWEEP_EXT: dict[str, str] = {
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
    # live on a licensed kit, 2026-07-11). Spectre also leaves a `pnoise.pnoise.cache` sibling,
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
PAC_SIDEBAND_RE = re.compile(r"pac\.(-?\d+)")
# The canonical abscissa name the registry looks up per analysis kind (recipe defaults:
# `frequency` for ac/noise, `time` for tran), aliased onto the PSF sweep vector so a recipe
# needn't know Spectre spells it `freq`.
SWEEP_ABSCISSA: dict[str, tuple[str, ...]] = {
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

# The inverse of SWEEP_EXT with CANONICAL keys, ordered longest-suffix-first so `.fd.pss` wins over
# a plain suffix match and `.0.pac` over `.pac`. The viewer extends it with its viewer-only keys
# (`.td.pss` → pss_td, other `.pac` sidebands → pac_sb).
EXT_TO_ANALYSIS: dict[str, str] = {
    ".fd.pss": "pss",
    ".0.pac": "pac",
    ".pnoise": "pnoise",
    ".noise": "noise",
    ".tran": "tran",
    ".stb": "stb",
    ".ac": "ac",
    ".dc": "dc",
}


def resolve_sweep_ext(analysis: str) -> tuple[str, str] | None:
    """`(canonical key, file extension)` for an analysis spelling, or None when it is not swept.

    `pac.<k>` selects the k-th sideband PSF (`pac.<k>.pac`); plain `pac` is the baseband `.0.pac`.
    """
    key = str(analysis).strip().lower()
    sideband = PAC_SIDEBAND_RE.fullmatch(key)
    if sideband:
        return "pac", f".{sideband.group(1)}.pac"
    ext = SWEEP_EXT.get(key)
    return (key, ext) if ext is not None else None


def find_swept_psf(output_dir: Path | str | None, analysis: str) -> Path | None:
    """The PSF file `analysis` reads under a `-raw` dir, or None (not swept / no dir / no file).

    Prefers the contract-named PSF when siblings share the extension (a deck with both a `dc`
    sweep and a `dcOp` op-point leaves `dc.dc` AND `dcOp.dc`; alphabetical order is luck, not a
    contract — the same reasoning that pins `pss` to `.fd.pss` over `.td.pss`).
    """
    resolved = resolve_sweep_ext(analysis)
    root = Path(output_dir) if output_dir else None
    if resolved is None or root is None or not root.is_dir():
        return None
    key, ext = resolved
    files = sorted(p for p in root.rglob(f"*{ext}") if p.is_file())
    if not files:
        return None
    files.sort(key=lambda p: (p.name != f"{key}{ext}", str(p)))
    return files[0]


def read_psf(path: Path | str, analysis: str | None = None) -> dict[str, np.ndarray]:
    """One psfascii PSF file → ``{signal_name: ndarray}``: every trace plus the sweep vector, the
    latter also aliased to the registry's canonical abscissa names (`frequency`/`time`) for
    `analysis` (inferred from the file name when not given). Needs `psf_utils`.
    """
    try:
        from psf_utils import PSF
    except ImportError as exc:  # pragma: no cover - the wave-reading tools declare psf_utils
        raise ImportError(
            "reading a Spectre swept PSF (AC/tran/noise) needs 'psf_utils' "
            "(declared by the tools that read waves — spicexplorer, spicexplorer-waveview — not by core)."
        ) from exc

    path = Path(path)
    key = None
    if analysis is not None:
        resolved = resolve_sweep_ext(analysis)
        key = resolved[0] if resolved else str(analysis).strip().lower()
    else:
        lowered = path.name.lower()
        for ext, k in EXT_TO_ANALYSIS.items():  # longest suffix first
            if lowered.endswith(ext):
                key = k
                break
    psf = PSF(str(path))
    out: dict[str, np.ndarray] = {}
    sweep = psf.get_sweep()
    if sweep is not None:
        absc = np.asarray(sweep.abscissa)
        out[str(sweep.name)] = absc
        for alias in SWEEP_ABSCISSA.get(key or "", ()):
            out.setdefault(alias, absc)
    for sig in psf.all_signals():
        out[str(sig.name)] = np.asarray(sig.ordinate)
    return out


def read_swept_psf(output_dir: Path | str | None, analysis: str) -> dict[str, np.ndarray]:
    """Signals from a run's swept psfascii PSF (`ac.ac`/`tran.tran`/`noise.noise`) as arrays.

    Returns ``{signal_name: ndarray}`` — every trace plus the sweep vector, the latter also
    aliased to the registry's canonical abscissa name (`frequency`/`time`). Empty when the
    analysis is not swept, no matching PSF exists, or ``output_dir`` is unset — a missing wave
    then raises in the adapter's `wave()` exactly as a missing flat signal does.

    The analysis spelling ``pac.<k>`` selects the k-th sideband of a periodic-AC run
    (the ``pac.<k>.pac`` PSF) instead of the baseband — the conversion-gain / ripple
    read; plain ``pac`` stays harmonic 0.
    """
    f = find_swept_psf(output_dir, analysis)
    if f is None:
        return {}
    return read_psf(f, analysis)
