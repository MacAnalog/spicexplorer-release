"""Layout annotation — a labelled figure of a layout, from a declarative ``labels.yaml``.

A layout render is evidence only if a reader can *name* what they are looking at. Three
stages of the physical lane need the same picture with a different overlay:

* the **designer** ships the render of record and wants the floorplan named — matched
  groups, guard rings, straps, the pin frame, the current path;
* the **reviewer** ships the same render with numbered, severity-coloured findings;
* a **paper/report** figure wants role-only labels, math subscripts and a scale bar,
  on a white ground.

This module is that one method. The inputs are the **GDS** (never a hand-measured
coordinate) and a **``labels.yaml``**; the outputs are ``<prefix>_labelled.{png,pdf}``,
``<prefix>_labelled_scale.{png,pdf}`` (the scale bar is a *separate* file — a figure
placed in a paper often already carries the scale in its caption), ``<prefix>_review.*``
plus ``<prefix>_crops/F<n>.png`` when the spec carries ``findings``. **Nothing here ever
overwrites the plain render**: every output carries a suffix of its own.

    from spicexplorer_signoff.annotate import annotate, instances, regions
    annotate("cell.gds", "labels.yaml", "figs/cell")

    python -m spicexplorer_signoff.annotate cell.gds labels.yaml figs/cell

Reading positions out of the GDS
--------------------------------
:func:`instances` returns ``{name: Instance(name, cell, bbox_um)}`` for the top cell's
instances, in placement order. Generator stacks (gdsfactory) usually leave instances
**unnamed** — you get ``Unnamed_1…N`` or an ordinal — so ``match:`` accepts an ordinal
range as well as a name/cell regex, and a label may always carry an explicit ``bbox``.
:func:`regions` returns merged polygon boxes for a **PDK layer name** (``NWell``,
``TopMetal1``, ``pSD``…), optionally only those with holes — which is how you find a
closed guard ring without eyeballing it.

Layering note
-------------
``spicexplorer-signoff`` is a leaf tool: it must not import a peer (``spicexplorer_layout``).
The KLayout render is therefore duplicated here rather than reused from
``spicexplorer_layout.gen.render_png``, and the PDK layer properties come from this
package's own :mod:`spicexplorer_signoff.pdk` (``for_pdk(...).lyp``). Note also that
``spicexplorer_layout.review.annotate`` already draws a *findings-only* overlay (PIL) for
the ``layout-review/1`` DSL; this module is the superset (labels + groups + paths +
findings + scale bar, matplotlib/STIX). Merging the three render paths into one is a
deliberate follow-up, not an accident.

Everything that does not need KLayout or matplotlib (schema load/validate, the frame
transform, the collision stacker, the palette) imports and tests on a bare machine.

Packaging
---------
Landing this module needs a new optional extra in the package's ``pyproject.toml`` —
``[project.optional-dependencies] annotate = ["matplotlib", "pillow", "pyyaml"]``,
modelled on ``spicexplorer-layout``'s ``gds`` extra. Today signoff declares only
``spicexplorer-core`` and ``klayout``; the three drawing dependencies are imported
lazily so the rest of the module still works without the extra installed.
"""

from __future__ import annotations

import json
import math
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = "layout-annotation/1"

#: Okabe–Ito — the eight-colour qualitative palette that survives every common form of
#: colour-vision deficiency and greyscale printing. Groups cycle through it in order.
PALETTE = [
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#009E73",  # bluish green
    "#CC79A7",  # reddish purple
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#F0E442",  # yellow
    "#000000",  # black
]

#: Findings keep the reviewer's severity order but use Okabe–Ito hues so the review
#: overlay and the group outlines are legible under the same colour-vision constraints.
#: (``spicexplorer_layout.review.COLORS`` still uses red/orange/yellow/blue — see the
#: "refine" list in the workspace method doc.)
SEVERITY_COLOR = {
    "blocker": "#D55E00",
    "major": "#E69F00",
    "minor": "#0072B2",
    "note": "#009E73",
}
SEVERITIES = tuple(SEVERITY_COLOR)
ANCHORS = ("center", "above", "below", "left", "right")
GROUNDS = ("dark", "white")


# ---------------------------------------------------------------------- schema --


@dataclass
class RenderSpec:
    px_per_um: float = 6.0
    margin_frac: float = 0.02
    ground: str = "dark"
    oversampling: int = 3
    dpi: int = 600
    pdk: str = "ihp-sg13g2"
    max_hier_levels: int = 30


@dataclass
class Label:
    text: str
    role: str = ""
    match: dict[str, Any] = field(default_factory=dict)
    bbox: list[float] | None = None
    point: list[float] | None = None
    anchor: str = "center"
    style: dict[str, Any] = field(default_factory=dict)


@dataclass
class Group:
    name: str
    members: list[str] = field(default_factory=list)  # label texts
    bbox: list[float] | None = None
    color: str = ""
    note: str = ""
    bracket: str = "left"  # left | none


@dataclass
class PathSpec:
    """A polyline drawn as an arrow chain — the current path, a signal route."""

    name: str
    points_um: list[list[float]] = field(default_factory=list)
    color: str = "#D55E00"
    label: str = ""
    width: float = 2.0


@dataclass
class Finding:
    id: str
    severity: str
    text: str
    bbox: list[float] | None = None
    point: list[float] | None = None


@dataclass
class ScaleBar:
    length_um: float = 50.0
    separate_output: bool = True


@dataclass
class Spec:
    cell: str = ""
    gds: str = ""
    render: RenderSpec = field(default_factory=RenderSpec)
    labels: list[Label] = field(default_factory=list)
    groups: list[Group] = field(default_factory=list)
    paths: list[PathSpec] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    scale_bar: ScaleBar = field(default_factory=ScaleBar)
    legend: bool = True
    title: str = ""
    schema: str = SCHEMA


def load_spec(src: str | Path | dict[str, Any]) -> Spec:
    """Read a ``labels.yaml`` (or an already-parsed mapping) into a :class:`Spec`.

    JSON is accepted too — a ``.json`` file, or any file when PyYAML is missing.
    """
    if isinstance(src, dict):
        d = src
    else:
        text = Path(src).read_text()
        try:
            import yaml  # optional; JSON is a valid YAML subset anyway

            d = yaml.safe_load(text)
        except ImportError:  # pragma: no cover - environment dependent
            d = json.loads(text)
    if not isinstance(d, dict):
        raise ValueError("labels spec must be a mapping")
    errs = validate_spec(d)
    if errs:
        raise ValueError("invalid labels spec:\n  " + "\n  ".join(errs))
    return Spec(
        cell=d.get("cell", ""),
        gds=d.get("gds", ""),
        title=d.get("title", ""),
        legend=bool(d.get("legend", True)),
        schema=d.get("schema", SCHEMA),
        render=RenderSpec(**(d.get("render") or {})),
        labels=[Label(**x) for x in d.get("labels") or []],
        groups=[Group(**x) for x in d.get("groups") or []],
        paths=[PathSpec(**x) for x in d.get("paths") or []],
        findings=[Finding(**x) for x in d.get("findings") or []],
        scale_bar=ScaleBar(**(d.get("scale_bar") or {})),
    )


def validate_spec(d: dict[str, Any]) -> list[str]:
    """Readable schema errors (empty list = valid). Never raises on a bad shape."""
    errs: list[str] = []
    if d.get("schema", SCHEMA) != SCHEMA:
        errs.append(f"schema must be {SCHEMA!r}")
    r = d.get("render") or {}
    if not isinstance(r, dict):
        errs.append("render must be a mapping")
    else:
        if r.get("ground", "dark") not in GROUNDS:
            errs.append(f"render.ground must be one of {GROUNDS}")
        if float(r.get("px_per_um", 6.0)) <= 0:
            errs.append("render.px_per_um must be > 0")
        for k in r:
            if k not in RenderSpec.__dataclass_fields__:
                errs.append(f"render.{k}: unknown key")
    for i, x in enumerate(d.get("labels") or []):
        tag = f"labels[{i}]"
        if not isinstance(x, dict) or not x.get("text"):
            errs.append(f"{tag}: needs a non-empty 'text'")
            continue
        if not (x.get("match") or x.get("bbox") or x.get("point")):
            errs.append(f"{tag}: needs one of 'match', 'bbox', 'point'")
        if x.get("anchor", "center") not in ANCHORS:
            errs.append(f"{tag}.anchor must be one of {ANCHORS}")
        for k in x:
            if k not in Label.__dataclass_fields__:
                errs.append(f"{tag}.{k}: unknown key")
    names = {x.get("text") for x in d.get("labels") or []}
    for i, g in enumerate(d.get("groups") or []):
        tag = f"groups[{i}]"
        if not isinstance(g, dict) or not g.get("name"):
            errs.append(f"{tag}: needs a 'name'")
            continue
        if not (g.get("members") or g.get("bbox")):
            errs.append(f"{tag}: needs 'members' or 'bbox'")
        for m in g.get("members") or []:
            if m not in names:
                errs.append(f"{tag}: member {m!r} is not a label text")
    seen: set[Any] = set()
    for i, f in enumerate(d.get("findings") or []):
        tag = f"findings[{i}]"
        fid = (f or {}).get("id")
        if not fid or fid in seen:
            errs.append(f"{tag}: needs a unique 'id'")
        seen.add(fid)
        if f.get("severity") not in SEVERITIES:
            errs.append(f"{tag}.severity must be one of {SEVERITIES}")
        if not (f.get("bbox") or f.get("point")):
            errs.append(f"{tag}: needs 'bbox' or 'point'")
    return errs


# ------------------------------------------------------------------- geometry --


@dataclass(frozen=True)
class Instance:
    """One top-level instance: its name (or ordinal placeholder), cell, and µm bbox."""

    name: str
    cell: str
    bbox: tuple[float, float, float, float]
    index: int = 0

    @property
    def center(self) -> tuple[float, float]:
        x0, y0, x1, y1 = self.bbox
        return ((x0 + x1) / 2, (y0 + y1) / 2)


def instances(gds: str | Path, topcell: str | None = None) -> dict[str, Instance]:
    """``{name: Instance}`` for the top cell's instances, **in placement order**.

    A gdsfactory/kfactory stack rarely names its instances, so the key falls back to the
    instance's ``name`` property, then to the child cell name, then to ``<cell>#<n>``;
    ``index`` is always the placement ordinal, which is the stable handle for a generator
    that places a row of devices in a known order.
    """
    import klayout.db as kdb  # optional dep (a hard dependency of this package)

    ly = kdb.Layout()
    ly.read(str(gds))
    top = ly.cell(topcell) if topcell else ly.top_cell()
    if top is None:
        raise ValueError(f"no cell {topcell!r} in {gds}")
    out: dict[str, Instance] = {}
    for i, inst in enumerate(top.each_inst()):
        b = inst.dcplx_trans * inst.cell.dbbox()
        prop = inst.property("name")
        base = str(prop) if prop else f"{inst.cell.name}#{i}"
        name = base if base not in out else f"{base}@{i}"
        out[name] = Instance(name, inst.cell.name, (b.left, b.bottom, b.right, b.top), i)
    return out


def pdk_lyp(pdk: str = "ihp-sg13g2") -> Path | None:
    """The PDK's KLayout layer-properties file.

    Asks :mod:`spicexplorer_signoff.pdk` first (the package's single source of PDK paths),
    and falls back to the ``$PDK_ROOT`` glob when this file is executed **standalone** —
    which is how the workspace runner loads it before the module lands in the platform.
    Returns ``None`` when there is none; every caller then degrades to layer numbers.
    """
    try:
        from . import pdk as _pdk

        p = _pdk.for_pdk(pdk).lyp
        if Path(p).is_file():
            return Path(p)
    except (ImportError, ValueError):
        pass
    import os

    root = Path(os.environ.get("PDK_ROOT", os.path.expanduser("~/local/pdks"))).expanduser()
    hits = sorted((root / pdk / "libs.tech" / "klayout" / "tech").glob("*.lyp"))
    return hits[0] if hits else None


def layer_names(
    pdk: str = "ihp-sg13g2", lyp: str | Path | None = None
) -> dict[tuple[int, int], str]:
    """``{(layer, datatype): "NWell"}`` parsed from the PDK's own KLayout ``.lyp``.

    Reusing the PDK's names is the point: a spec that says ``layer: TopMetal1`` stays
    readable and survives a layer-number change in the kit.
    """
    out: dict[tuple[int, int], str] = {}
    if lyp is None:
        lyp = pdk_lyp(pdk)
    if lyp is None or not Path(lyp).is_file():
        return out  # no layer table — raw "layer/datatype" names still work
    for prop in ET.parse(str(lyp)).getroot().iter("properties"):
        src = (prop.findtext("source") or "").split("@")[0].strip()
        nm = (prop.findtext("name") or "").strip()
        m = re.match(r"^(\d+)/(\d+)$", src)
        if m and nm:
            out.setdefault((int(m.group(1)), int(m.group(2))), nm.split(".")[0].strip())
    return out


def regions(
    gds: str | Path,
    layer: str,
    *,
    topcell: str | None = None,
    pdk: str = "ihp-sg13g2",
    lyp: str | Path | None = None,
    datatype: int = 0,
    holes_only: bool = False,
    min_area_um2: float = 0.0,
) -> list[tuple[float, float, float, float]]:
    """Merged polygon bboxes (µm) on a **named** PDK layer, largest first.

    ``layer`` is the PDK's own name (``NWell``) or a raw ``"31/0"`` — the raw form is the
    escape hatch for a layer the ``.lyp`` does not name, and for a PDK with no layer table.
    ``holes_only=True`` keeps only polygons that enclose a hole — which is exactly what a
    *closed* guard ring is, and what a row of point taps on a pitch is not.
    """
    import klayout.db as kdb

    ly = kdb.Layout()
    ly.read(str(gds))
    top = ly.cell(topcell) if topcell else ly.top_cell()
    names = layer_names(pdk, lyp)
    raw = re.match(r"^(\d+)/(\d+)$", layer)
    want_num = (int(raw.group(1)), int(raw.group(2))) if raw else None
    out: list[tuple[float, float, float, float]] = []
    for li in ly.layer_indexes():
        info = ly.get_info(li)
        if want_num is not None:
            if (info.layer, info.datatype) != want_num:
                continue
        else:
            if names.get((info.layer, info.datatype)) != layer or info.datatype != datatype:
                continue
        reg = kdb.Region(top.begin_shapes_rec(li))
        reg.merge()
        for poly in reg.each():
            if holes_only and poly.holes() == 0:
                continue
            b = poly.bbox().to_dtype(ly.dbu)
            if b.width() * b.height() < min_area_um2:
                continue
            out.append((b.left, b.bottom, b.right, b.top))
    return sorted(out, key=lambda b: -((b[2] - b[0]) * (b[3] - b[1])))


def cell_bbox(gds: str | Path, topcell: str | None = None) -> tuple[float, float, float, float]:
    import klayout.db as kdb

    ly = kdb.Layout()
    ly.read(str(gds))
    top = ly.cell(topcell) if topcell else ly.top_cell()
    b = top.dbbox()
    return (b.left, b.bottom, b.right, b.top)


# --------------------------------------------------------------------- frame ---


@dataclass(frozen=True)
class Frame:
    """The rendered viewport: µm box → pixel coordinates of the raster.

    The renderer is asked for exactly this box at exactly this scale, so the transform is
    analytic (no viewport round-trip) and unit-testable without KLayout.
    """

    x0: float
    y0: float
    x1: float
    y1: float
    px_per_um: float

    @classmethod
    def around(cls, bbox: Sequence[float], px_per_um: float, margin_frac: float) -> Frame:
        x0, y0, x1, y1 = bbox
        m = margin_frac * max(x1 - x0, y1 - y0)
        return cls(x0 - m, y0 - m, x1 + m, y1 + m, px_per_um)

    @property
    def size_px(self) -> tuple[int, int]:
        return (
            round((self.x1 - self.x0) * self.px_per_um),
            round((self.y1 - self.y0) * self.px_per_um),
        )

    def to_px(self, x: float, y: float) -> tuple[float, float]:
        """µm → pixels (y flipped: raster row 0 is the top of the frame)."""
        return ((x - self.x0) * self.px_per_um, (self.y1 - y) * self.px_per_um)

    def box_px(self, bbox: Sequence[float]) -> tuple[float, float, float, float]:
        """µm bbox → (left, top, width, height) in pixels."""
        (px0, py0), (px1, py1) = self.to_px(bbox[0], bbox[3]), self.to_px(bbox[2], bbox[1])
        return (min(px0, px1), min(py0, py1), abs(px1 - px0), abs(py1 - py0))


# --------------------------------------------------------- collision stacking --


@dataclass
class Placed:
    """A label after collision resolution: where it is drawn and whether it moved."""

    key: str
    anchor_px: tuple[float, float]
    pos_px: tuple[float, float]
    size_px: tuple[float, float]
    moved: bool = False

    @property
    def rect(self) -> tuple[float, float, float, float]:
        (x, y), (w, h) = self.pos_px, self.size_px
        return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


_DIR = {
    "center": (0.0, 0.0),
    "above": (0.0, -1.0),
    "below": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
}


def _overlap(a: Sequence[float], b: Sequence[float], pad: float) -> bool:
    return not (
        a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1]
    )


def stack_labels(
    items: Iterable[tuple[str, tuple[float, float], tuple[float, float], str]],
    *,
    pad: float = 6.0,
    max_steps: int = 40,
    bounds: tuple[float, float, float, float] | None = None,
) -> list[Placed]:
    """Greedy de-collision, the LPF figure's axis stacking generalised to two axes.

    ``items`` are ``(key, anchor_px, size_px, anchor_kind)``. Each label starts on its
    anchor (offset half its own height/width in the anchor direction) and, while it
    overlaps an already-placed label, is pushed one step further **along its own anchor
    direction** — vertical anchors stack vertically, horizontal ones horizontally, and a
    ``center`` label falls back to stacking downwards. A label displaced by more than one
    of its own heights is marked ``moved`` so the caller can draw a leader line.

    ``bounds`` (``x0, y0, x1, y1`` in pixels) keeps every label inside the drawable area.
    It is applied **inside** the loop, never afterwards: clamping a finished layout is what
    reintroduces the very collisions the stacker just removed. A label the frame pins
    against an edge switches to stacking downwards instead of pushing into the wall.

    Deterministic: placement order is the input order, so a figure regenerates identically.
    """
    placed: list[Placed] = []
    for key, anchor, size, kind in items:
        ax, ay = anchor
        w, h = size
        dx, dy = _DIR.get(kind, (0.0, 0.0))
        if (dx, dy) == (0.0, 0.0):
            step = (0.0, h + pad)
            x, y = ax, ay
        else:
            x = ax + dx * (w / 2 + pad)
            y = ay + dy * (h / 2 + pad)
            step = (dx * (w + pad) if dx else 0.0, dy * (h + pad) if dy else 0.0)
            if step == (0.0, 0.0):
                step = (0.0, h + pad)

        def clamp(px: float, py: float, w: float = w, h: float = h) -> tuple[float, float]:
            if bounds is None:
                return px, py
            bx0, by0, bx1, by1 = bounds
            return (
                min(max(px, bx0 + w / 2), max(bx1 - w / 2, bx0 + w / 2)),
                min(max(py, by0 + h / 2), max(by1 - h / 2, by0 + h / 2)),
            )

        x, y = clamp(x, y)
        for _ in range(max_steps):
            cand = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if not any(_overlap(cand, p.rect, pad) for p in placed):
                break
            nx, ny = clamp(x + step[0], y + step[1])
            if abs(nx - x) < 1e-6 and abs(ny - y) < 1e-6:  # pinned against the frame
                step = (0.0, h + pad)
                nx, ny = clamp(x, y + step[1])
                if abs(ny - y) < 1e-6:  # nowhere left to go — take the overlap
                    break
            x, y = nx, ny
        dist = math.hypot(x - ax, y - ay)
        placed.append(Placed(key, (ax, ay), (x, y), (w, h), moved=dist > max(h, 1.0) * 1.2))
    return placed


# -------------------------------------------------------------------- render ---


def render_base(
    gds: str | Path,
    out_png: str | Path,
    *,
    frame: Frame,
    pdk: str = "ihp-sg13g2",
    lyp: str | Path | None = None,
    oversampling: int = 3,
    max_hier_levels: int = 30,
) -> Path:
    """Headless KLayout raster of exactly ``frame``, in the PDK's own layer colours.

    Text and grid are turned off: the viewer's automatic device labels overlap, clip at
    the frame and are the *viewer's* names, not the design's — this module supplies the
    names instead.
    """
    import klayout.db as kdb
    import klayout.lay as klay  # optional dep

    if lyp is None:
        lyp = pdk_lyp(pdk)
    w, h = frame.size_px
    lv = klay.LayoutView()
    lv.load_layout(str(gds), 0)  # type: ignore[call-overload]
    if lyp and Path(lyp).is_file():
        lv.load_layer_props(str(lyp))
    lv.max_hier_levels = max_hier_levels
    lv.set_config("grid-visible", "false")
    lv.set_config("text-visible", "false")
    lv.zoom_fit()
    box = kdb.DBox(frame.x0, frame.y0, frame.x1, frame.y1)
    # width, height, linewidth=0, oversampling, resolution=0, target box, monochrome=False
    lv.save_image_with_options(str(out_png), w, h, 0, oversampling, 0, box, False)
    return Path(out_png)


# ------------------------------------------------------------------- resolve ---


def resolve_label(
    lb: Label, insts: dict[str, Instance], gds: str | Path | None, pdk: str
) -> tuple[float, float, float, float]:
    """A label's µm bbox, from an explicit ``bbox``/``point`` or from a ``match``.

    ``match`` keys (all optional, ANDed): ``name`` / ``cell`` (regex), ``index``
    (``[lo, hi]`` inclusive ordinal range, or a single int), ``layer`` (+ ``holes_only``,
    ``nth``). Several matched instances are merged into their common bounding box —
    which is what makes a *group* label ("EA input pair") one label rather than four.
    """
    if lb.bbox:
        x0, y0, x1, y1 = lb.bbox
        return (float(x0), float(y0), float(x1), float(y1))
    if lb.point:
        x, y = lb.point
        return (float(x), float(y), float(x), float(y))
    m = dict(lb.match)
    if "layer" in m:
        if gds is None:
            raise ValueError(f"label {lb.text!r} matches a layer but no GDS was given")
        boxes = regions(
            gds,
            m["layer"],
            pdk=pdk,
            holes_only=bool(m.get("holes_only")),
            datatype=int(m.get("datatype", 0)),
        )
        if not boxes:
            raise ValueError(f"label {lb.text!r}: no {m['layer']} region found")
        return boxes[int(m.get("nth", 0))]
    hits = list(insts.values())
    if "name" in m:
        rx = re.compile(m["name"])
        hits = [i for i in hits if rx.search(i.name)]
    if "cell" in m:
        rx = re.compile(m["cell"])
        hits = [i for i in hits if rx.search(i.cell)]
    if "index" in m:
        idx = m["index"]
        lo, hi = (idx, idx) if isinstance(idx, int) else (idx[0], idx[1])
        hits = [i for i in hits if lo <= i.index <= hi]
    if not hits:
        raise ValueError(f"label {lb.text!r}: match {m} selected no instance")
    return (
        min(i.bbox[0] for i in hits),
        min(i.bbox[1] for i in hits),
        max(i.bbox[2] for i in hits),
        max(i.bbox[3] for i in hits),
    )


def _anchor_point(bbox: Sequence[float], kind: str) -> tuple[float, float]:
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return {
        "center": (cx, cy),
        "above": (cx, y1),
        "below": (cx, y0),
        "left": (x0, cy),
        "right": (x1, cy),
    }[kind]


# --------------------------------------------------------------------- draw ----


def _setup_mpl():
    import matplotlib

    matplotlib.use("Agg")
    matplotlib.rcParams.update(
        {"font.family": "STIXGeneral", "mathtext.fontset": "stix", "pdf.fonttype": 42}
    )
    return matplotlib


def annotate(
    source: str | Path,
    labels_yaml: str | Path | dict[str, Any] | Spec,
    out_prefix: str | Path,
    *,
    gds: str | Path | None = None,
    topcell: str | None = None,
    base_png: str | Path | None = None,
    variant: str = "",
    quantize: int = 0,
    formats: Sequence[str] = ("png", "pdf"),
) -> list[Path]:
    """Render ``source`` (a GDS, or an already-rendered PNG) and draw ``labels_yaml`` on it.

    Returns every file written. Outputs, all suffixed so the plain render is never touched
    (``<v>`` is ``variant`` — e.g. ``_white`` — which keeps a dark and a white rendering of
    the same spec under one name stem):

    ================================  ==============================================
    ``<prefix>_labelled<v>.{png,pdf}``  labels + group outlines + paths + legend
    ``<prefix>_labelled<v>_scale.*``    the same, plus a scale bar in a bottom strip
    ``<prefix>_review<v>.*``            the findings overlay (only when ``findings`` exist)
    ``<prefix>_crops/F<n>.png``         one zoom per finding
    ``<prefix>_base.png``               the raster the overlays sit on (regenerable)
    ================================  ==============================================
    """
    spec = load_spec(labels_yaml) if not isinstance(labels_yaml, Spec) else labels_yaml
    src = Path(source)
    gds_path = (
        Path(gds) if gds else (src if src.suffix.lower() in (".gds", ".gds2", ".oas") else None)
    )
    out_prefix = Path(out_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    r = spec.render

    if gds_path is not None:
        bbox = cell_bbox(gds_path, topcell)
        frame = Frame.around(bbox, r.px_per_um, r.margin_frac)
        base = Path(base_png) if base_png else out_prefix.with_name(out_prefix.name + "_base.png")
        render_base(
            gds_path,
            base,
            frame=frame,
            pdk=r.pdk,
            oversampling=r.oversampling,
            max_hier_levels=r.max_hier_levels,
        )
        insts = instances(gds_path, topcell)
    else:
        # A pre-rendered PNG: the caller must have produced it with the same frame, so the
        # spec has to carry the cell bbox explicitly on every label (no GDS to query).
        base = src
        if not spec.labels or any(not (lb.bbox or lb.point) for lb in spec.labels):
            raise ValueError(
                "rendering from a PNG needs every label to carry an explicit bbox/point"
            )
        xs = [v for lb in spec.labels for v in ((lb.bbox or []) + (lb.point or []))[:4]]
        frame = Frame.around(
            (min(xs[::2]), min(xs[1::2]), max(xs[::2]), max(xs[1::2])), r.px_per_um, r.margin_frac
        )
        insts = {}

    _setup_mpl()
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    img = mpimg.imread(str(base))[:, :, :3]
    if r.ground == "white":
        img = 1.0 - img
    fg = "#111111" if r.ground == "white" else "#f5f5f5"

    resolved = {lb.text: resolve_label(lb, insts, gds_path, r.pdk) for lb in spec.labels}

    written: list[Path] = []
    written += _draw(
        spec,
        img,
        frame,
        resolved,
        out_prefix,
        f"labelled{variant}",
        fg,
        formats,
        scale_bar=False,
        findings=False,
        quantize=quantize,
    )
    if spec.scale_bar and spec.scale_bar.length_um > 0:
        written += _draw(
            spec,
            img,
            frame,
            resolved,
            out_prefix,
            f"labelled{variant}_scale",
            fg,
            formats,
            scale_bar=True,
            findings=False,
            quantize=quantize,
        )
    if spec.findings:
        written += _draw(
            spec,
            img,
            frame,
            resolved,
            out_prefix,
            f"review{variant}",
            fg,
            formats,
            scale_bar=False,
            findings=True,
            quantize=quantize,
        )
        written += _crops(spec, img, frame, out_prefix, fg)
    plt.close("all")
    return written


def _draw(
    spec,
    img,
    frame,
    resolved,
    out_prefix,
    stem_suffix,
    fg,
    formats,
    *,
    scale_bar,
    findings,
    quantize=0,
):
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import numpy as np

    r = spec.render
    h, w = img.shape[:2]
    # Every hard-coded offset below is in POINTS scaled to pixels by `S`. matplotlib sizes
    # text in points at `dpi`, and the figure is `px/dpi` inches, so a bare pixel constant
    # silently means something different at 300 dpi than at 600 — which is exactly how the
    # first LDO render came out with 70 px labels stacked on top of each other.
    S = r.dpi / 72.0
    pad_l = int(54 * S) if (spec.groups and any(g.bracket == "left" for g in spec.groups)) else 0
    pad_b = int(25 * S) if scale_bar else 0
    pad_t = int(22 * S) if (spec.legend and (findings or spec.groups or spec.paths)) else 0
    ground = 1.0 if r.ground == "white" else 0.08
    canvas = np.full((h + pad_b + pad_t, w + pad_l, 3), ground, dtype=float)
    canvas[pad_t : pad_t + h, pad_l:, :] = np.clip(img, 0.0, 1.0)

    fig = plt.figure(figsize=((w + pad_l) / r.dpi, (h + pad_b + pad_t) / r.dpi), dpi=r.dpi)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.imshow(canvas, interpolation="none")
    ax.set_xlim(0, w + pad_l)
    ax.set_ylim(h + pad_b + pad_t, 0)
    ax.axis("off")

    def P(x, y):
        px, py = frame.to_px(x, y)
        return px + pad_l, py + pad_t

    # --- group outlines + left bracket column -------------------------------
    colors = {}
    for gi, g in enumerate(spec.groups):
        col = g.color or PALETTE[gi % len(PALETTE)]
        colors[g.name] = col
        if g.bbox:
            gb = tuple(float(v) for v in g.bbox)
        else:
            bs = [resolved[m] for m in g.members]
            gb = (
                min(b[0] for b in bs),
                min(b[1] for b in bs),
                max(b[2] for b in bs),
                max(b[3] for b in bs),
            )
        (x0, y0), (x1, y1) = P(gb[0], gb[3]), P(gb[2], gb[1])
        ax.add_patch(
            mpatches.Rectangle(
                (x0, y0), x1 - x0, y1 - y0, fill=False, ec=col, lw=1.4, ls=(0, (6, 3)), zorder=4
            )
        )
        if pad_l and g.bracket == "left":
            xb = pad_l * 0.66
            ax.plot([xb, xb], [y0, y1], color=col, lw=1.2, zorder=4)
            for yy in (y0, y1):
                ax.plot([xb, xb + pad_l * 0.12], [yy, yy], color=col, lw=1.2, zorder=4)
            # a rotated bracket label must fit the bracket it names, or it runs into the
            # neighbouring group's label — shrink it to the bracket's own length.
            span = abs(y1 - y0)
            for txt, base, xf, asp in ((g.name, 10.5, 0.42, 0.75), (g.note, 6.5, 0.20, 0.62)):
                if not txt:
                    continue
                # 0.9 safety: bold STIX runs wider than the plain-glyph estimate, and a
                # bracket label clipped mid-word ("Pass devi…") reads as a bug.
                fs = min(base, 0.9 * span / max(len(txt) * asp, 1.0) * 72.0 / r.dpi)
                if fs < 5.0:
                    continue  # illegible at this bracket length — the legend carries it
                ax.text(
                    pad_l * xf,
                    (y0 + y1) / 2,
                    txt,
                    rotation=90,
                    ha="center",
                    va="center",
                    fontsize=fs,
                    fontweight="bold" if txt is g.name else "normal",
                    color=col,
                )

    # --- paths (arrow chains) -----------------------------------------------
    for ps in spec.paths:
        pts = [P(x, y) for x, y in ps.points_um]
        for a, b in zip(pts, pts[1:]):
            ax.annotate(
                "",
                xy=b,
                xytext=a,
                zorder=5,
                arrowprops=dict(
                    arrowstyle="-|>", color=ps.color, lw=ps.width, shrinkA=0, shrinkB=0, alpha=0.9
                ),
            )
        if ps.label and pts:
            ax.text(
                pts[0][0],
                pts[0][1] - 6 * S,
                ps.label,
                color=ps.color,
                fontsize=7.0,
                fontweight="bold",
                ha="left",
                va="bottom",
                zorder=6,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=ps.color, lw=0.6, alpha=0.9),
            )

    # --- labels, de-collided -------------------------------------------------
    if not findings:
        items, texts = [], []
        for lb in spec.labels:
            bb = resolved[lb.text]
            ax_pt, ay_pt = _anchor_point(bb, lb.anchor)
            fs = float(lb.style.get("fontsize", 7.0))
            body = lb.text if not lb.role else f"{lb.text}\n{lb.role}"
            nlines = body.count("\n") + 1
            # matplotlib points -> pixels at this dpi; a 0.62 aspect is a safe glyph estimate
            # (mathtext markup is stripped first, or `$XM_{BP}$` measures 8 chars wide)
            plain = [re.sub(r"[$\\{}]|_(?=.)", "", s) for s in body.split("\n")]
            wpx = max(len(s) for s in plain) * fs * 0.62 * S
            hpx = nlines * fs * 1.35 * S
            items.append((lb.text, P(ax_pt, ay_pt), (wpx, hpx), lb.anchor))
            texts.append((lb, body, fs))
        # The drawable area excludes the bracket column (left), the legend strip (top) and
        # the scale-bar strip (bottom): a label parked on any of those hides what is there.
        bounds = (pad_l + 2 * S, pad_t + 2 * S, w + pad_l - 2 * S, pad_t + h - 2 * S)
        for pl, (lb, body, fs) in zip(stack_labels(items, pad=3.0 * S, bounds=bounds), texts):
            col = lb.style.get("color", "#111111")
            ax.text(
                pl.pos_px[0],
                pl.pos_px[1],
                body,
                ha="center",
                va="center",
                fontsize=fs,
                color=col,
                zorder=7,
                linespacing=1.25,
                bbox=dict(
                    boxstyle="round,pad=0.3,rounding_size=0.6",
                    fc="white",
                    ec=lb.style.get("edgecolor", "#555555"),
                    lw=0.6,
                    alpha=0.94,
                ),
            )
            if pl.moved:
                ax.plot(
                    [pl.anchor_px[0], pl.pos_px[0]],
                    [pl.anchor_px[1], pl.pos_px[1]],
                    color="#555555",
                    lw=0.7,
                    ls=(0, (2, 2)),
                    zorder=6,
                )
                ax.plot(*pl.anchor_px, marker="o", ms=2.0, color="#555555", zorder=6)

    # --- findings ------------------------------------------------------------
    if findings:
        for f in spec.findings:
            col = SEVERITY_COLOR[f.severity]
            if f.bbox:
                (x0, y0), (x1, y1) = P(f.bbox[0], f.bbox[3]), P(f.bbox[2], f.bbox[1])
                ax.add_patch(
                    mpatches.Rectangle(
                        (x0, y0),
                        x1 - x0,
                        y1 - y0,
                        fill=True,
                        fc=col,
                        alpha=0.16,
                        ec=col,
                        lw=2.2,
                        zorder=5,
                    )
                )
                tx, ty = x1, y0
            else:
                tx, ty = P(f.point[0], f.point[1])
                ax.plot(tx, ty, marker="+", ms=14, mew=2.2, color=col, zorder=5)
            n = f.id.lstrip("Ff") or f.id
            ax.plot(tx, ty, marker="o", ms=15, color=col, mec="black", mew=0.8, zorder=6)
            ax.text(
                tx,
                ty,
                n,
                ha="center",
                va="center",
                fontsize=7.5,
                color="white",
                fontweight="bold",
                zorder=7,
            )

    # --- legend strip --------------------------------------------------------
    if pad_t:
        entries = (
            [(SEVERITY_COLOR[f.severity], f"{f.id}  {f.text}") for f in spec.findings]
            if findings
            else [
                (colors[g.name], g.name + (f" — {g.note}" if g.note else "")) for g in spec.groups
            ]
            + [(p.color, p.label or p.name) for p in spec.paths]
        )
        fsl, sw = 6.5, 6.0 * S
        x, y = pad_l + 4 * S, pad_t * 0.34
        for col, txt in entries[:12]:
            plain = re.sub(r"[$\\{}]|_(?=.)", "", txt)
            adv = sw * 1.8 + len(plain) * fsl * 0.60 * S
            if x + adv > w + pad_l:
                x, y = pad_l + 4 * S, y + fsl * 1.9 * S
            ax.add_patch(mpatches.Rectangle((x, y - sw / 2), sw, sw, fc=col, ec="none", zorder=8))
            ax.text(x + sw * 1.5, y, txt, fontsize=fsl, color=fg, ha="left", va="center", zorder=8)
            x += adv

    # --- scale bar (its own output file) -------------------------------------
    if scale_bar:
        L = spec.scale_bar.length_um * frame.px_per_um
        xs, ys = pad_l + 0.02 * w, h + pad_t + pad_b * 0.45
        ax.plot([xs, xs + L], [ys, ys], color=fg, lw=2.2, solid_capstyle="butt", zorder=8)
        for xx in (xs, xs + L):
            ax.plot([xx, xx], [ys - pad_b * 0.10, ys + pad_b * 0.10], color=fg, lw=1.2, zorder=8)
        ax.text(
            xs + L / 2,
            ys - pad_b * 0.16,
            f"{spec.scale_bar.length_um:g} µm",
            ha="center",
            va="bottom",
            fontsize=9,
            color=fg,
            zorder=8,
        )

    out: list[Path] = []
    for ext in formats:
        p = out_prefix.with_name(f"{out_prefix.name}_{stem_suffix}.{ext}")
        fig.savefig(
            p, dpi=r.dpi, pad_inches=0, metadata={"CreationDate": None} if ext == "pdf" else None
        )
        if ext == "png" and quantize:
            _quantize_png(p, quantize)
        out.append(p)
    plt.close(fig)
    return out


def _quantize_png(png: Path, colors: int) -> None:
    """Palette-reduce a PNG in place — a layer render is flat colour plus hatching, so 256
    colours is ~3x smaller with no visible loss, and these figures are committed."""
    from PIL import Image

    im = Image.open(png).convert("RGB")
    # MEDIANCUT/FLOYDSTEINBERG are re-exported at module level for back-compat but the
    # installed Pillow stubs only type them under the Quantize/Dither enums.
    im.quantize(
        colors=colors,
        method=Image.MEDIANCUT,  # type: ignore[attr-defined]
        dither=Image.FLOYDSTEINBERG,  # type: ignore[attr-defined]
    ).save(png, optimize=True)


def _crops(spec, img, frame, out_prefix, fg, *, pad_um: float = 8.0):
    """One zoom per finding, named for its id — the reviewer's "where exactly"."""
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt

    d = out_prefix.with_name(out_prefix.name + "_crops")
    d.mkdir(parents=True, exist_ok=True)
    h, w = img.shape[:2]
    out: list[Path] = []
    for f in spec.findings:
        bb = f.bbox if f.bbox else [f.point[0], f.point[1], f.point[0], f.point[1]]
        left, t, bw, bh = frame.box_px(
            [bb[0] - pad_um, bb[1] - pad_um, bb[2] + pad_um, bb[3] + pad_um]
        )
        x0, y0 = int(max(0, left)), int(max(0, t))
        x1, y1 = int(min(w, left + bw)), int(min(h, t + bh))
        if x1 - x0 < 4 or y1 - y0 < 4:
            continue
        sub = img[y0:y1, x0:x1]
        fig = plt.figure(figsize=((x1 - x0) / 200, (y1 - y0) / 200), dpi=200)
        ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
        ax.imshow(sub, interpolation="none")
        ax.axis("off")
        col = SEVERITY_COLOR[f.severity]
        if f.bbox:
            bl, bt, bwp, bhp = frame.box_px(f.bbox)
            ax.add_patch(
                mpatches.Rectangle((bl - x0, bt - y0), bwp, bhp, fill=False, ec=col, lw=2.5)
            )
        ax.text(
            6,
            6,
            f"{f.id}  {f.text}",
            fontsize=7,
            color="white",
            ha="left",
            va="top",
            bbox=dict(boxstyle="round,pad=0.3", fc=col, ec="none", alpha=0.95),
        )
        p = d / f"{f.id}.png"
        fig.savefig(p, dpi=200, pad_inches=0)
        plt.close(fig)
        out.append(p)
    return out


# ----------------------------------------------------------------------- cli ---


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m spicexplorer_signoff.annotate",
        description="Draw a labels.yaml (labels / groups / paths / findings / scale bar) over a "
        "PDK-coloured layout render.",
    )
    ap.add_argument("source", help="GDS (or a pre-rendered PNG)")
    ap.add_argument("labels", help="labels.yaml")
    ap.add_argument("out_prefix", help="output prefix; every file gets a suffix of its own")
    ap.add_argument("--topcell", default=None)
    ap.add_argument("--gds", default=None, help="GDS to query when `source` is a PNG")
    ap.add_argument("--ground", default=None, choices=GROUNDS, help="override render.ground")
    ap.add_argument("--px-per-um", type=float, default=None)
    ap.add_argument(
        "--variant",
        default="",
        help="name suffix for this rendering (e.g. _white), so a dark and a white "
        "pass of one spec share a name stem",
    )
    ap.add_argument(
        "--base",
        default=None,
        help="where to put the plain raster the overlays sit on "
        "(default: <out_prefix>_base.png; point it at scratch to keep it "
        "out of the repo)",
    )
    ap.add_argument(
        "--quantize",
        type=int,
        default=0,
        metavar="N",
        help="palette-reduce every PNG output to N colours (256 is ~3x smaller with\n no visible loss on a layer render; 0 = off)",
    )
    ap.add_argument("--formats", default="png,pdf")
    ap.add_argument(
        "--dump-instances",
        action="store_true",
        help="print the top cell's instances (name, cell, bbox) and exit",
    )
    a = ap.parse_args(argv)

    if a.dump_instances:
        for i in instances(a.source, a.topcell).values():
            print(
                f"{i.index:4d}  {i.name:28s} {i.cell:44s} "
                f"({i.bbox[0]:8.2f},{i.bbox[1]:8.2f})-({i.bbox[2]:8.2f},{i.bbox[3]:8.2f})"
            )
        return 0

    spec = load_spec(a.labels)
    if a.ground:
        spec.render.ground = a.ground
    if a.px_per_um:
        spec.render.px_per_um = a.px_per_um
    for p in annotate(
        a.source,
        spec,
        a.out_prefix,
        gds=a.gds,
        topcell=a.topcell,
        base_png=a.base,
        variant=a.variant,
        quantize=a.quantize,
        formats=tuple(a.formats.split(",")),
    ):
        print(p)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
