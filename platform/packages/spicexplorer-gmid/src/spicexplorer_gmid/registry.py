"""LUTRegistry — enumerate and load committed gm/ID LUTs from a root directory.

The registry reads the ``<device>__<corner>[__<T>C][__wf<W>u].manifest.json`` sidecars directly.
It never imports ``spicexplorer_analog_db`` — the tool is data-driven and decoupled from the DB —
so the filename convention the extractor writes is mirrored here (and only here).
"""

from __future__ import annotations

import math
from pathlib import Path

from .contract import LUTManifest
from .errors import GmidError
from .tables import DeviceTable

# The extractor tags a LUT filename only when it is OFF the historic nominal, so the original
# `<device>__<corner>` names keep working: 27 °C carries no `__<T>C`, a 5 µm finger no `__wf<W>u`.
NOMINAL_TEMP_C = 27.0
NOMINAL_WF_UM = 5.0
_TEMP_TOL_C = 0.5  # the tag appears once |T − 27 °C| exceeds this
_TEMP_MATCH_TOL_C = 1.0  # manifests record kelvin (300.0 K = 26.85 °C), so match loosely


def _temp_suffix(temp_c: float | None) -> str:
    """``__<T>C`` for a non-nominal temperature; empty at 27 °C (the historic filename)."""
    if temp_c is None or abs(float(temp_c) - NOMINAL_TEMP_C) < _TEMP_TOL_C:
        return ""
    return f"__{int(round(float(temp_c)))}C"


def _wf_suffix(wf_um: float | None) -> str:
    """``__wf<W>u`` for a non-nominal finger width; empty at 5 µm (the default single-W LUT).

    ``.`` is not filename-safe here (it would confuse the extension split) so it is written ``p``:
    0.5 µm → ``__wf0p5u``, 1 µm → ``__wf1u``.
    """
    if wf_um is None or abs(float(wf_um) - NOMINAL_WF_UM) < 1e-9:
        return ""
    return "__wf" + f"{float(wf_um):g}".replace(".", "p") + "u"


def lut_stem(
    device: str, corner: str = "tt", temp_c: float | None = None, wf_um: float | None = None
) -> str:
    """``<device>__<corner>[__<T>C][__wf<W>u]`` — the optional segments appear only off-nominal."""
    return f"{device}__{corner}{_temp_suffix(temp_c)}{_wf_suffix(wf_um)}"


class LUTRegistry:
    """Index of committed gm/ID LUTs under a root directory.

    Each LUT is a ``<pdk>/<stem>.pkl`` data file paired with a ``<pdk>/<stem>.manifest.json``
    sidecar that records the complete run dimensions (VGS/VDS/VSB/L grids, W/nfing/temp), corner,
    exact model-card lines, stored parameter names, and extraction provenance. The stem is
    ``<device>__<corner>[__<T>C][__wf<W>u]`` (see :func:`lut_stem`): a LUT extracted off the
    nominal 27 °C / 5 µm finger carries the corresponding tag, addressed with the ``temp_c`` /
    ``wf_um`` selectors of :meth:`find` and :meth:`load`.

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

        # a tagged variant: the -40 °C table characterised on a 1 µm finger
        cold = reg.load("sky130", "sky130_fd_pr__nfet_01v8", temp_c=-40, wf_um=1.0)
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

    def find(
        self,
        pdk: str,
        device: str,
        corner: str = "tt",
        *,
        temp_c: float | None = None,
        wf_um: float | None = None,
    ) -> LUTManifest:
        """The manifest for one (pdk, device, corner[, temperature, finger width]).

        ``temp_c`` (°C) and ``wf_um`` (µm) address the tagged variants the extractor writes
        (``__<T>C`` / ``__wf<W>u``); omit them — or pass the nominal 27 °C / 5 µm — for the
        untagged file. Raises :class:`KeyError` if that variant is absent, and
        :class:`~spicexplorer_gmid.GmidError` if the sidecar found under the addressed name
        describes a *different* temperature or finger width (a mis-tagged file must never be
        served as the requested variant).
        """
        stem = lut_stem(device, corner, temp_c, wf_um)
        p = self.root / pdk / f"{stem}.manifest.json"
        if not p.is_file():
            pdk_dir = self.root / pdk
            have = (
                sorted(q.name[: -len(".manifest.json")] for q in pdk_dir.glob("*.manifest.json"))
                if pdk_dir.is_dir()
                else []
            )
            raise KeyError(
                f"no manifest for {pdk}/{stem} under {self.root}. "
                f"Committed: {', '.join(have) or 'none'}."
            )
        man = LUTManifest.from_path(p)
        self._require_variant_matches(man, p, temp_c=temp_c, wf_um=wf_um)
        return man

    @staticmethod
    def _require_variant_matches(
        man: LUTManifest, path: Path, *, temp_c: float | None, wf_um: float | None
    ) -> None:
        """Cross-check an explicitly addressed variant against the conditions the sidecar records."""
        if temp_c is not None:
            got_c = man.conditions.temp_k - 273.15
            if abs(got_c - float(temp_c)) > _TEMP_MATCH_TOL_C:
                raise GmidError(
                    f"{path.name} is named for {temp_c:g} °C but records temp_k="
                    f"{man.conditions.temp_k:g} K ({got_c:.4g} °C) — refusing to serve it as the "
                    f"{temp_c:g} °C variant."
                )
        if wf_um is not None and not math.isclose(man.conditions.width_um, float(wf_um), rel_tol=1e-6):
            raise GmidError(
                f"{path.name} is named for a {wf_um:g} µm finger but records width_um="
                f"{man.conditions.width_um:g} µm — refusing to serve it as the {wf_um:g} µm variant."
            )

    def load(
        self,
        pdk: str,
        device: str,
        corner: str = "tt",
        *,
        temp_c: float | None = None,
        wf_um: float | None = None,
    ) -> DeviceTable:
        """Load a LUT as a :class:`~spicexplorer_gmid.DeviceTable` with its manifest attached.

        Same selectors as :meth:`find`. Raises :class:`KeyError` if the manifest is absent and
        :class:`FileNotFoundError` if its ``.pkl`` is not next to it.

        The ``.pkl`` is resolved from the **addressed** stem, not from the manifest's ``lut_file``
        field: the extractor writes that field un-suffixed for every tagged variant, so trusting it
        would hand back the 27 °C / 5 µm table under an ``__85C`` / ``__wf1u`` manifest — a silent
        wrong answer. A missing file is reported instead.
        """
        man = self.find(pdk, device, corner, temp_c=temp_c, wf_um=wf_um)
        stem = lut_stem(device, corner, temp_c, wf_um)
        pkl = self.root / pdk / f"{stem}.pkl"
        if not pkl.is_file():
            raise FileNotFoundError(
                f"the manifest for {pdk}/{stem} is present but its data file is not: expected "
                f"{pkl}. (The manifest's lut_file field says {man.lut_file!r}; that field is "
                f"written un-suffixed for tagged variants and is not used to select one.)"
            )
        # DeviceTable.load() auto-discovers the sidecar → manifest is attached
        return DeviceTable.load(pkl)
