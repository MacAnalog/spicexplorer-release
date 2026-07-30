"""Engine sniffing + the one-call entry point: a path → :class:`WaveDataset`.

``load_result`` accepts an ngspice ``.raw`` file OR a Spectre psfascii raw directory,
figures out which engine produced it (or trusts an explicit ``engine=``), loads it, and
attaches the discovered simulator log when one sits next to the artifact.
"""

from __future__ import annotations

from pathlib import Path

from .dataset import WaveDataset
from .logs import discover_log
from .ngspice_loader import load_ngspice_raw
from .spectre_loader import SWEEP_EXT_TO_ANALYSIS, load_spectre_raw_dir

__all__ = ["load_result", "sniff_engine"]


def sniff_engine(path: str | Path) -> str | None:
    """Guess which engine produced an artifact: ``"ngspice"`` | ``"spectre"`` | None.

    A file is ngspice when it looks like a raw file (``.raw`` suffix, or a
    ``Title:``/binary raw header). A directory is Spectre when it contains at least one
    recognised psfascii PSF (``*.ac`` / ``*.tran`` / ``*.fd.pss`` / …, any depth).
    """
    p = Path(path)
    if p.is_file():
        if p.suffix.lower() == ".raw":
            return "ngspice"
        try:
            head = p.open("rb").read(64)
        except OSError:
            return None
        if head.startswith(b"Title:") or head.startswith(b"\xff\xfeT\x00i\x00"):  # ascii / utf-16 raw
            return "ngspice"
        return None
    if p.is_dir():
        for f in p.rglob("*"):
            if not f.is_file() or f.name.endswith(".cache"):
                continue
            lowered = f.name.lower()
            if any(lowered.endswith(ext) for ext in SWEEP_EXT_TO_ANALYSIS):
                return "spectre"
        return None
    return None


def load_result(
    path: str | Path, engine: str | None = None, log_path: str | Path | None = None
) -> WaveDataset:
    """Load any simulation result artifact into a :class:`WaveDataset`.

    :param path: an ngspice ``.raw`` file or a Spectre psfascii raw directory.
    :param engine: force ``"ngspice"``/``"spectre"``; default sniffs from the artifact.
    :param log_path: attach this simulator log; default discovers one beside the artifact.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"result artifact not found: {p}")
    resolved = engine or sniff_engine(p)
    if resolved == "ngspice":
        ds = load_ngspice_raw(p)
    elif resolved == "spectre":
        ds = load_spectre_raw_dir(p)
    else:
        raise ValueError(
            f"could not determine the engine for {p} — pass engine='ngspice' (a .raw file) "
            f"or engine='spectre' (a psfascii raw directory)."
        )
    ds.log_path = str(log_path) if log_path else discover_log(p, ds.engine)
    return ds
