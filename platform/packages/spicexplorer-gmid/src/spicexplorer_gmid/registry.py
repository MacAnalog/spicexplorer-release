"""LUTRegistry — enumerate and load committed gm/ID LUTs from a root directory.

The registry reads the ``<device>__<corner>.manifest.json`` sidecars directly.  It never
imports ``spicexplorer_analog_db`` — the tool is data-driven and decoupled from the DB.
"""

from __future__ import annotations

from pathlib import Path

from .contract import LUTManifest
from .tables import DeviceTable


class LUTRegistry:
    """Index of committed gm/ID LUTs under a root directory.

    Each LUT is a ``<pdk>/<device>__<corner>.pkl`` data file paired with a
    ``<pdk>/<device>__<corner>.manifest.json`` sidecar that records the complete run
    dimensions (VGS/VDS/VSB/L grids, W/nfing/temp), corner, exact model-card lines,
    stored parameter names, and extraction provenance.

    Usage::

        from spicexplorer_gmid import LUTRegistry

        reg = LUTRegistry("/path/to/_shared/gmid")

        # enumerate everything (or pass pdk= to filter)
        for m in reg.list_available("sky130"):
            print(m.pdk, m.device, m.corner)
            print("  L grid:", m.dimensions["L_um"].values)
            print("  VGS:", m.dimensions["VGS_V"].n, "pts,", m.dimensions["VGS_V"].step, "V step")
            print("  model lines:", m.model.corner_lines)

        # load for sizing (manifest attached automatically)
        nch = reg.load("sky130", "sky130_fd_pr__nfet_01v8")
        assert nch.manifest is not None
        print(nch.manifest.conditions.temp_k)   # 300.0
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def list_available(self, pdk: str | None = None) -> list[LUTManifest]:
        """All committed LUT manifests under this registry root.

        Pass ``pdk`` to filter to one PDK; omit for the full catalog.  Corrupt or missing
        sidecars are skipped without raising — use :meth:`find` to surface errors for a
        specific (pdk, device, corner).
        """
        if pdk is not None:
            pdk_dirs = [self.root / pdk]
        elif self.root.is_dir():
            pdk_dirs = sorted(d for d in self.root.iterdir() if d.is_dir())
        else:
            pdk_dirs = []
        result: list[LUTManifest] = []
        for d in pdk_dirs:
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.manifest.json")):
                try:
                    result.append(LUTManifest.from_path(p))
                except Exception:
                    pass
        return result

    def find(self, pdk: str, device: str, corner: str = "tt") -> LUTManifest:
        """The manifest for one (pdk, device, corner) — raises :class:`KeyError` if absent."""
        p = self.root / pdk / f"{device}__{corner}.manifest.json"
        if not p.is_file():
            pdk_dir = self.root / pdk
            have = sorted(q.stem for q in pdk_dir.glob("*.manifest.json")) if pdk_dir.is_dir() else []
            raise KeyError(
                f"no manifest for {pdk}/{device}@{corner} under {self.root}. "
                f"Committed: {', '.join(have) or 'none'}."
            )
        return LUTManifest.from_path(p)

    def load(self, pdk: str, device: str, corner: str = "tt") -> DeviceTable:
        """Load a LUT as a :class:`~spicexplorer_gmid.DeviceTable` with its manifest attached.

        Raises :class:`KeyError` if the manifest is absent, :class:`FileNotFoundError` if
        the ``.pkl`` the manifest references is missing.
        """
        man = self.find(pdk, device, corner)
        pkl = self.root / pdk / man.lut_file
        if not pkl.is_file():
            raise FileNotFoundError(
                f"manifest for {pdk}/{device}@{corner} references '{man.lut_file}' "
                f"but it is not present at {pkl}."
            )
        # DeviceTable.load() auto-discovers the sidecar → manifest is attached
        return DeviceTable.load(pkl)
