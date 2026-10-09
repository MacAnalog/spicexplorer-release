"""PDK + tool discovery. Everything is a path lookup with an env override; nothing is imported.

DRC deck: :func:`for_pdk` names the PDK's ``run_drc.py`` runner and, as a fallback, the KLayout
``.lydrc`` rule decks. Some IHP SG13G2 checkouts (CHANGELOG "Unreleased - 2024-10-14") ship only
``drc/sg13g2_maximal.lydrc`` and ``drc/sg13g2_minimal.lydrc``; :meth:`PdkPaths.drc_deck` returns
the deck :func:`~spicexplorer_signoff.drc.run_drc` will run on this checkout.

Env knobs (all optional):

- ``PDK_ROOT``            dir containing ``<pdk>/`` (default ``~/local/pdks``)
- ``SIGNOFF_KLAYOUT``     klayout executable for the PDK DRC/LVS decks (default: ``klayout`` on PATH)
- ``KPEX_KLAYOUT_EXE``    klayout executable kpex drives (needs Ruby ≥ 2.6; kpex's own env var)
- ``SIGNOFF_PYTHON``      interpreter for the PDK's python runners (default: this one; needs the
                          ``klayout`` module — a dependency of this package)
- ``SIGNOFF_KPEX``        kpex executable (default: ``kpex`` on PATH, then ``~/miniconda3/envs/pex/bin/kpex``)
"""

from __future__ import annotations

import os
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_PDK_ROOT = "~/local/pdks"
DEFAULT_KPEX_FALLBACK = "~/miniconda3/envs/pex/bin/kpex"
DEFAULT_KPEX_KLAYOUT_FALLBACK = "~/local/klayout-py311/klayout-batch.sh"


@dataclass(frozen=True)
class PdkPaths:
    """Where a PDK keeps the things signoff needs. Only ``ihp-sg13g2`` is filled in today;
    other nodes get the same shape (add a branch in :func:`for_pdk`)."""

    name: str
    root: Path  # $PDK_ROOT/<name>
    klayout_tech: Path  # .../libs.tech/klayout/tech
    drc_runner: Path  # run_drc.py
    lvs_runner: Path  # run_lvs.py
    lyp: Path  # layer properties (renders)
    ngspice_models: Path  # models dir (post-layout benches)
    #: KLayout rule decks (``.lydrc``) run directly by ``klayout -b -r`` when ``drc_runner`` is
    #: absent, in order of preference: the first one present is used.
    drc_decks: tuple[Path, ...] = ()

    def drc_deck(self) -> Path | None:
        """The DRC deck ``run_drc`` runs: ``drc_runner`` when the file exists, else the first
        existing ``drc_decks`` entry, else ``None`` (no DRC deck on this checkout)."""
        for deck in (self.drc_runner, *self.drc_decks):
            if deck.is_file():
                return deck
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            k: [str(x) for x in v] if isinstance(v, tuple) else str(v)
            for k, v in asdict(self).items()
        }


def pdk_root() -> Path:
    return Path(os.environ.get("PDK_ROOT", os.path.expanduser(DEFAULT_PDK_ROOT))).expanduser()


def for_pdk(name: str = "ihp-sg13g2", root: Path | None = None) -> PdkPaths:
    root = (root or pdk_root()) / name
    if name == "ihp-sg13g2":
        kl = root / "libs.tech" / "klayout" / "tech"
        return PdkPaths(
            name=name,
            root=root,
            klayout_tech=kl,
            drc_runner=kl / "drc" / "run_drc.py",
            lvs_runner=kl / "lvs" / "run_lvs.py",
            lyp=kl / "sg13g2.lyp",
            ngspice_models=root / "libs.tech" / "ngspice" / "models",
            # the full rule set first; the minimal deck checks a subset of the same rules
            drc_decks=(kl / "drc" / "sg13g2_maximal.lydrc", kl / "drc" / "sg13g2_minimal.lydrc"),
        )
    raise ValueError(f"unknown PDK {name!r} — add its paths in spicexplorer_signoff.pdk.for_pdk")


def runner_python() -> str:
    """Interpreter the PDK runner scripts execute under (must import ``klayout.db``)."""
    import sys

    return os.path.expanduser(os.environ.get("SIGNOFF_PYTHON", sys.executable))


def klayout_exe() -> str | None:
    return os.environ.get("SIGNOFF_KLAYOUT") or shutil.which("klayout")


def kpex_exe() -> str | None:
    cand = os.environ.get("SIGNOFF_KPEX") or shutil.which("kpex")
    if cand and os.path.exists(os.path.expanduser(cand)):
        return os.path.expanduser(cand)
    fb = os.path.expanduser(DEFAULT_KPEX_FALLBACK)
    return fb if os.path.exists(fb) else None


def kpex_klayout_exe() -> str | None:
    cand = os.environ.get("KPEX_KLAYOUT_EXE")
    if cand and os.path.exists(os.path.expanduser(cand)):
        return os.path.expanduser(cand)
    fb = os.path.expanduser(DEFAULT_KPEX_KLAYOUT_FALLBACK)
    return fb if os.path.exists(fb) else None


@dataclass
class ToolProbe:
    pdk: str
    pdk_ok: bool
    drc_deck_ok: bool  # run_drc.py or one of the .lydrc decks is present (PdkPaths.drc_deck)
    lvs_deck_ok: bool
    klayout: str | None
    kpex: str | None
    kpex_klayout: str | None
    ngspice: str | None
    magic: str | None
    netgen: str | None

    @property
    def drc_ok(self) -> bool:
        return self.drc_deck_ok and self.klayout is not None

    @property
    def lvs_ok(self) -> bool:
        return self.lvs_deck_ok and self.klayout is not None

    @property
    def pex_ok(self) -> bool:
        return self.pdk_ok and self.kpex is not None and self.kpex_klayout is not None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.update(drc_ok=self.drc_ok, lvs_ok=self.lvs_ok, pex_ok=self.pex_ok)
        return d


def probe(pdk: str = "ihp-sg13g2") -> ToolProbe:
    """Cheap availability check — no tool is launched."""
    try:
        p = for_pdk(pdk)
    except ValueError:
        return ToolProbe(
            pdk,
            False,
            False,
            False,
            klayout_exe(),
            kpex_exe(),
            kpex_klayout_exe(),
            shutil.which("ngspice"),
            shutil.which("magic"),
            shutil.which("netgen"),
        )
    return ToolProbe(
        pdk=pdk,
        pdk_ok=p.root.is_dir(),
        drc_deck_ok=p.drc_deck() is not None,
        lvs_deck_ok=p.lvs_runner.is_file(),
        klayout=klayout_exe(),
        kpex=kpex_exe(),
        kpex_klayout=kpex_klayout_exe(),
        ngspice=shutil.which("ngspice"),
        magic=shutil.which("magic"),
        netgen=shutil.which("netgen"),
    )
