"""Find and load gm/ID lookup tables (LUTs) by PDK, device, corner, temperature and finger width.

- **One known directory:** :class:`LUTRegistry` lists and loads the tables under a root you pass.
- **No directory to pass:** :func:`load_lut`, :func:`finger_width_set` and :func:`search_luts`
  search every root this installation may keep tables in (:func:`default_roots`), which is what
  a design repo calls.

Each table is a ``<pdk>/<stem>.pkl`` file with a ``<pdk>/<stem>.manifest.json`` beside it, and the
stem is ``<device>__<corner>[__<T>C][__wf<W>u]`` (:func:`lut_stem`). This package does not import
``spicexplorer_analog_db``, the package that writes these files, so the file-name rule is repeated
here, and only here.
"""

from __future__ import annotations

import logging
import math
import os
import re
from collections.abc import Iterable, Sequence
from pathlib import Path

from .contract import LUTManifest
from .errors import GmidError
from .fingerwidth import FingerWidthSet
from .tables import DeviceTable, _load_sidecar

logger = logging.getLogger(__name__)

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

        Pass ``pdk`` to filter to one PDK; omit for the full catalog.  A corrupt sidecar is
        skipped without raising, and logged as a warning naming the file — use :meth:`find` to
        raise its error for a specific (pdk, device, corner). Only a corrupt *file* is skipped;
        any other exception propagates.
        """
        return [man for _, man in self._sidecars(pdk)]

    def _sidecars(self, pdk: str | None) -> list[tuple[str, LUTManifest]]:
        """``(stem, manifest)`` for each readable sidecar, in :meth:`list_available` order.

        The stem is read from the sidecar's file name (``<stem>.manifest.json``), the name
        :meth:`find` addresses. The manifest's ``lut_file`` field is not used: the ngspice lane
        writes it as ``<device>__<corner>.pkl`` for a tagged table too.
        """
        if pdk is not None:
            pdk_dirs = [self.root / pdk]
        elif self.root.is_dir():
            pdk_dirs = sorted(d for d in self.root.iterdir() if d.is_dir())
        else:
            pdk_dirs = []
        result: list[tuple[str, LUTManifest]] = []
        for d in pdk_dirs:
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.manifest.json")):
                man = _load_sidecar(p)  # warns and yields None for a corrupt sidecar
                if man is not None:
                    result.append((p.name[: -len(".manifest.json")], man))
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
        if wf_um is not None and not math.isclose(
            man.conditions.width_um, float(wf_um), rel_tol=1e-6
        ):
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


# --------------------------------------------------------------- discovery ----
# Where the tables are (#157, skill-library #21). A design repo's working directory is neither
# the platform checkout nor the table store, so a design has no root to hand `LUTRegistry`. The
# functions below search a fixed list of roots instead, and they are the only code that decides
# where tables are looked for.

#: LUT roots separated by `os.pathsep` (`:` on Linux), searched before anything else: a store the
#: other roots do not cover, such as a mounted share or a per-project cache.
ROOTS_ENV = "SPICEXPLORER_GMID_ROOTS"
#: Where the Spectre lane writes by default (`gmid.out_root` in the analog-db registry). A
#: LICENSED kit's tables live here rather than in any repo: derived curves are not kit content,
#: but committing them is an owner decision, so the default store is out-of-repo and per-user.
USER_STORE = "~/.spicexplorer/gmid"
#: The committed open-PDK tables, relative to a platform checkout.
DB_RELATIVE = "examples/analog-db/_shared/gmid"


def default_roots() -> list[Path]:
    """Every LUT root this installation may hold, in search order, existing or not.

    Order is deliberate: an explicit `$SPICEXPLORER_GMID_ROOTS` first, then the per-user store
    the Spectre lane writes (a commercial kit's only lane), then the committed open-PDK tables —
    reached through `$SX_ROOT` (the shared read-only install a design repo sees) and through the
    enclosing platform checkout, in that order, because a design should get the installation's
    tables and not whatever checkout happens to be a parent of its cwd.

    Non-existent roots are kept so `load_lut` can say what it looked for.
    """
    roots: list[Path] = []

    def add(p: Path | str | None) -> None:
        if not p:
            return
        q = Path(p).expanduser()
        if q not in roots:
            roots.append(q)

    for part in (os.environ.get(ROOTS_ENV) or "").split(os.pathsep):
        add(part.strip() or None)
    add(USER_STORE)
    sx_root = os.environ.get("SX_ROOT")
    if sx_root:
        add(Path(sx_root) / "spicexplorer-platform" / DB_RELATIVE)
        add(Path(sx_root) / DB_RELATIVE)
    try:  # the enclosing platform checkout, when there is one
        from spicexplorer_core import project_root

        add(project_root() / DB_RELATIVE)
    except Exception as exc:  # pragma: no cover - no marker above cwd
        # Optional root: outside a platform checkout there is none; say why it was skipped.
        logger.debug("no enclosing platform checkout for LUT roots: %s", exc)
    return roots


def search_luts(
    pdk: str | None = None, *, roots: Sequence[Path | str] | None = None
) -> list[LUTManifest]:
    """The manifest of every LUT this installation can reach, one per table (optionally one PDK's).

    The listing is keyed on the PDK and the table's file stem,
    ``<device>__<corner>[__<T>C][__wf<W>u]``, read from the ``.manifest.json`` file name. A
    device's temperature tables (``__<T>C``) and finger-width tables (``__wf<W>u``) are therefore
    listed next to its untagged table: a root holding ``nch__tt``, ``nch__tt__-40C`` and
    ``nch__tt__wf1u`` lists three manifests.

    - **Order:** the roots in search order (``roots``, default :func:`default_roots`), then each
      root's PDK directories and manifests in file-name order.
    - **A stem present in two roots** is listed once, from the earlier root, the root
      :func:`load_lut` opens it from.
    - **To tell the tables apart**, read ``conditions.temp_k`` [K] and ``conditions.width_um``
      [µm]. For a table the analog-db ngspice lane extracted before analog-db #76, the ``lut_file``
      field reads ``<device>__<corner>.pkl`` for a tagged table too; the Spectre lane writes the
      tagged name.

    :func:`load_lut` with ``temp_c`` or ``wf_um`` opens one tagged table;
    :func:`finger_width_set` opens a device's finger-width tables as one set.
    """
    seen: set[tuple[str, str]] = set()
    out: list[LUTManifest] = []
    for root in roots or default_roots():
        for stem, man in LUTRegistry(Path(root).expanduser())._sidecars(pdk):
            key = (man.pdk, stem)
            if key in seen:
                continue
            seen.add(key)
            out.append(man)
    return out


#: The fix appended to every "no table" message: how each lane writes the missing table.
_EXTRACT_FIX = (
    f"FIX: extract it — an open PDK through `analog-db gmid-extract`, a LICENSED kit "
    f"through the Spectre lane (`analog-db gmid-extract-spectre`, which writes {USER_STORE}) "
    f"— or point ${ROOTS_ENV} at the store that already holds it."
)


def _describe_root(root: Path, pdk: str) -> str:
    """One line of a "no table" message: the root, and what it holds.

    A root that does not hold ``pdk`` lists the PDKs it does hold; a root that holds ``pdk``
    lists that PDK's table stems. The two cases need different fixes (extract the PDK, or
    extract one more device or width), so the message keeps them apart.
    """
    if not root.is_dir():
        return f"{root} (no such directory)"
    pdks = sorted(d.name for d in root.iterdir() if d.is_dir())
    if pdk not in pdks:
        return f"{root} (holds: {', '.join(pdks) or 'nothing'})"
    have = sorted(q.name[: -len(".manifest.json")] for q in (root / pdk).glob("*.manifest.json"))
    return f"{root}/{pdk} (holds: {', '.join(have) or 'nothing'})"


def _searched(pdk: str, roots: Sequence[Path]) -> str:
    return "Searched:\n  " + "\n  ".join(_describe_root(r, pdk) for r in roots)


def load_lut(
    pdk: str,
    device: str,
    corner: str = "tt",
    *,
    temp_c: float | None = None,
    wf_um: float | None = None,
    roots: Sequence[Path | str] | None = None,
) -> DeviceTable:
    """Load one LUT by PDK, device and corner from the first root that holds it.

    ``roots`` defaults to :func:`default_roots`. A miss raises `KeyError` naming every root
    searched and what each one holds, followed by the extraction command. An empty store and an
    absent PDK need different fixes, so the message tells them apart.
    """
    searched = [Path(r).expanduser() for r in roots or default_roots()]
    for r in searched:
        try:
            return LUTRegistry(r).load(pdk, device, corner, temp_c=temp_c, wf_um=wf_um)
        except KeyError:
            continue
    raise KeyError(
        f"no gm/ID LUT for {pdk}/{lut_stem(device, corner, temp_c, wf_um)}. "
        + _searched(pdk, searched)
        + "\n"
        + _EXTRACT_FIX
    )


# The suffix after `<device>__<corner>[__<T>C]` that marks a finger width: none for 5 µm,
# `__wf<W>u` otherwise, with `p` in place of the decimal point (`__wf0p5u` is 0.5 µm).
_WF_TAG = re.compile(r"(?:__wf(\d+(?:p\d+)?)u)?")


def _finger_widths_in(
    root: Path, pdk: str, device: str, corner: str, temp_c: float | None
) -> set[float]:
    """The finger widths [µm] one root holds tables for, read from the manifest file names.

    The file name decides the width, not the ``width_um`` the manifest records: :func:`load_lut`
    opens a table by name and refuses one whose manifest records a different width, so a
    mis-named file reaches the caller as that error. A tag that :func:`lut_stem` would not write
    for its own width (``__wf1p0u``, ``__wf5u``) is skipped, because no call could open it.
    """
    nominal = lut_stem(device, corner, temp_c)
    found: set[float] = set()
    for p in (root / pdk).glob("*.manifest.json"):
        stem = p.name[: -len(".manifest.json")]
        m = _WF_TAG.fullmatch(stem[len(nominal) :]) if stem.startswith(nominal) else None
        if m is None:
            continue
        wf = NOMINAL_WF_UM if m.group(1) is None else float(m.group(1).replace("p", "."))
        if lut_stem(device, corner, temp_c, wf) == stem:
            found.add(wf)
    return found


def _um(widths: Iterable[float]) -> str:
    return ", ".join(f"{w:g}" for w in widths) + " µm"


def finger_width_set(
    pdk: str,
    device: str,
    corner: str = "tt",
    *,
    temp_c: float | None = None,
    widths: Iterable[float] | None = None,
    roots: Sequence[Path | str] | None = None,
) -> FingerWidthSet:
    """Open one device's tables at several finger widths, by name, as a :class:`FingerWidthSet`.

    A table characterised on a 5 µm finger describes 5 µm fingers. A device drawn with narrower
    fingers (for matching, or at the minimum width) is sized from the companion tables
    ``<device>__<corner>[__<T>C]__wf<W>u``, which the set interpolates linearly in finger width.

    - **``widths=None``** opens every finger width the searched roots hold for this device,
      corner and temperature: the untagged 5 µm table plus each ``__wf<W>u`` companion, read from
      the ``.manifest.json`` file names.
    - **An explicit ``widths``** [µm] opens exactly those widths.
    - **Each width is opened by** :func:`load_lut` with the same ``roots`` (default
      :func:`default_roots`), so the first root that holds a width serves it, and two widths
      may come from two different roots.

    Raises:
        KeyError: once for the whole set, when a requested width has no table or ``widths=None``
            finds none. The message lists the missing widths with their file stems, the widths
            that were found, every root searched with what it holds, and the extraction command.
        ValueError: ``widths`` is empty, or holds a width that is not a finite number above 0.
        GmidError: a table's manifest records a finger width other than the one its name gives.
        FileNotFoundError: a manifest is present but its ``.pkl`` is not.

    Example::

        from spicexplorer_gmid import finger_width_set, size_for_gm

        fs = finger_width_set("sky130", "sky130_fd_pr__nfet_01v8")  # every width the roots hold
        fs.finger_widths  # [0.5, 1.0, 5.0] once the 0.5 and 1 µm tables are extracted
        dev = size_for_gm(fs, gm=1e-3, gm_id=15, L=0.5, vds=0.9, wf=2.0)

    The committed store holds the 5 µm tables only, so there the set is ``[5.0]`` and ``wf=2.0``
    raises :class:`OutOfGridError`: a finger width is interpolated between two tables, never
    extrapolated.
    """
    wanted: list[float] | None = None
    if widths is not None:
        given = [float(w) for w in widths]
        if not given or not all(math.isfinite(w) and w > 0 for w in given):
            raise ValueError(
                f"widths must be one or more finite finger widths above 0 µm; got {given}"
            )
        wanted = sorted(set(given))
    searched = [Path(r).expanduser() for r in roots or default_roots()]
    found = sorted(
        set().union(*(_finger_widths_in(r, pdk, device, corner, temp_c) for r in searched))
    )
    if wanted is None:
        wanted = found
    tables: dict[float, DeviceTable] = {}
    missing: list[float] = []
    for wf in wanted:
        try:
            tables[wf] = load_lut(pdk, device, corner, temp_c=temp_c, wf_um=wf, roots=searched)
        except KeyError:
            missing.append(wf)
    if missing or not tables:
        which = (
            f"at finger width {_um(missing)} "
            f"({', '.join(lut_stem(device, corner, temp_c, w) for w in missing)})"
            if missing
            else "at any finger width"
        )
        raise KeyError(
            f"no gm/ID LUT for {pdk}/{lut_stem(device, corner, temp_c)} {which}; "
            f"found: {_um(found) if found else 'none'}. "
            + _searched(pdk, searched)
            + "\n"
            + _EXTRACT_FIX
        )
    return FingerWidthSet(tables)
