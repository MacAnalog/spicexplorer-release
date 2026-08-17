"""Layout-review DSL (``layout-review/1``) + annotated render.

Analog designers read pictures, not paragraphs. A review is therefore a **machine-readable
findings list whose every finding carries geometry anchors** (µm, in the GDS coordinate
system) and an **annotated PNG** where each finding is drawn as a numbered, severity-coloured
marker over the PDK-coloured render — next to the raw GDS and the plain PNG. The Markdown
review stays the narrative; this is what lets a reader *localize* a finding in one glance.

Schema (**YAML is the canonical, human-readable form** — ``REVIEW.yaml``; JSON is accepted
for tooling; ``schema: layout-review/1``):

    cell, gds, gds_sha256, generator {path, params, sha256}, verdict, reproduced {...},
    units: "um", axis {x|y: value} (optional symmetry axis), frame {x0,y0,x1,y1} (optional
    viewport), findings: [Finding], not_checked: [str], reviewer: str

    Finding: id ("F1"), severity (blocker|major|minor|note), category (reproduce|drc|lvs|
      pex|budget|coupling|matching|symmetry|routing|well|leakage|knob|objective|other),
      title, where: [Anchor], evidence, effect {metric, delta, unit, model}, fix {knob, to,
      note}, expected, verdict (open|fixed|worse — for re-reviews)

    Anchor: kind = box   {x0,y0,x1,y1, layer?}        rectangle
                   point {x,y}                        crosshair
                   pair  {a:{x,y}, b:{x,y}}           arrow between two spots (coupling, mismatch)
                   line  {points:[[x,y],...]}         polyline (routing asymmetry, a long run)
                   device{name, x0,y0,x1,y1?}          a device instance (box optional)
                   net   {name}                        a net by name only (legend-only, no geometry)
                   rule  {name, locations:[[x,y],...]} DRC rule hits

Public API: :func:`load_review`, :func:`dump_review`, :func:`annotate` (GDS + review → PNG),
:func:`validate` (schema check with a readable error list). The renderer uses KLayout's own
viewport transform (``LayoutView.viewport_trans``) so markers land exactly on the geometry.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA = "layout-review/1"
SEVERITIES = ("blocker", "major", "minor", "note")
CATEGORIES = (
    "reproduce",
    "drc",
    "lvs",
    "pex",
    "budget",
    "coupling",
    "matching",
    "symmetry",
    "routing",
    "well",
    "leakage",
    "knob",
    "objective",
    "other",
)
ANCHOR_KINDS = ("box", "point", "pair", "line", "device", "net", "rule")
COLORS = {
    "blocker": (220, 30, 30),
    "major": (255, 140, 0),
    "minor": (230, 200, 0),
    "note": (60, 140, 255),
}


@dataclass
class Finding:
    id: str
    severity: str
    category: str
    title: str
    where: list[dict[str, Any]] = field(default_factory=list)
    evidence: str = ""
    effect: dict[str, Any] = field(default_factory=dict)
    fix: dict[str, Any] = field(default_factory=dict)
    expected: str = ""
    verdict: str = "open"

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class Review:
    cell: str
    gds: str
    verdict: str
    findings: list[Finding] = field(default_factory=list)
    gds_sha256: str = ""
    generator: dict[str, Any] = field(default_factory=dict)
    reproduced: dict[str, Any] = field(default_factory=dict)
    units: str = "um"
    axis: dict[str, float] = field(default_factory=dict)
    frame: dict[str, float] | None = None
    not_checked: list[str] = field(default_factory=list)
    reviewer: str = ""
    schema: str = SCHEMA

    def to_dict(self) -> dict[str, Any]:
        d = {k: v for k, v in self.__dict__.items() if k != "findings"}
        d["findings"] = [f.to_dict() for f in self.findings]
        return d


def validate(d: dict[str, Any]) -> list[str]:
    """Readable schema errors (empty list = valid)."""
    errs: list[str] = []
    if d.get("schema") != SCHEMA:
        errs.append(f"schema must be {SCHEMA!r}")
    for k in ("cell", "gds", "verdict", "findings"):
        if k not in d:
            errs.append(f"missing top-level key {k!r}")
    seen: set[str] = set()
    for i, f in enumerate(d.get("findings", [])):
        tag = f"findings[{i}]"
        fid = f.get("id")
        if not fid or fid in seen:
            errs.append(f"{tag}: missing or duplicate id")
        seen.add(str(fid))
        if f.get("severity") not in SEVERITIES:
            errs.append(f"{tag}: severity must be one of {SEVERITIES}")
        if f.get("category") not in CATEGORIES:
            errs.append(f"{tag}: category must be one of {CATEGORIES}")
        if not f.get("title"):
            errs.append(f"{tag}: title required")
        for j, a in enumerate(f.get("where", [])):
            kind = a.get("kind")
            need = {
                "box": ("x0", "y0", "x1", "y1"),
                "point": ("x", "y"),
                "pair": ("a", "b"),
                "line": ("points",),
                "device": ("name",),
                "net": ("name",),
                "rule": ("name",),
            }
            if kind not in need:
                errs.append(f"{tag}.where[{j}]: kind must be one of {ANCHOR_KINDS}")
                continue
            for k in need[kind]:
                if k not in a:
                    errs.append(f"{tag}.where[{j}] ({kind}): missing {k!r}")
    return errs


def load_review(path: str | Path) -> Review:
    p = Path(path)
    text = p.read_text()
    if p.suffix.lower() == ".json":
        d = json.loads(text)
    else:
        import yaml  # workspace dep

        d = yaml.safe_load(text)
    errs = validate(d)
    if errs:
        raise ValueError("invalid review: " + "; ".join(errs))
    fs = [
        Finding(**{k: v for k, v in f.items() if k in Finding.__dataclass_fields__})
        for f in d["findings"]
    ]
    keys = {k for k in Review.__dataclass_fields__ if k != "findings"}
    return Review(findings=fs, **{k: v for k, v in d.items() if k in keys})


def dump_review(r: Review, path: str | Path) -> Path:
    """Write the review — YAML (default, human-readable; ``.yaml``/``.yml``) or JSON (``.json``)."""
    p = Path(path)
    d = r.to_dict()
    if p.suffix.lower() == ".json":
        p.write_text(json.dumps(d, indent=1))
    else:
        import yaml

        p.write_text(yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100))
    return p


# ------------------------------------------------------------------ annotated render --


def _pdk_lyp(pdk: str) -> Path | None:
    import os

    root = Path(os.environ.get("PDK_ROOT", os.path.expanduser("~/local/pdks")))
    cand = {
        "ihp-sg13g2": root / "ihp-sg13g2" / "libs.tech" / "klayout" / "tech" / "sg13g2.lyp"
    }.get(pdk)
    return cand if cand and cand.is_file() else None


def annotate(
    gds: str | Path,
    review: Review | str | Path,
    out_png: str | Path,
    *,
    size: tuple[int, int] = (2200, 1600),
    pdk: str = "ihp-sg13g2",
    lyp: str | Path | None = None,
    legend: bool = True,
    margin_um: float | None = None,
    only: list[str] | None = None,
    frame: dict[str, float] | None = None,
) -> Path:
    """Render ``gds`` with the PDK colours and draw every finding's anchors on top, numbered
    by finding id and coloured by severity; a legend lists id → title. Returns the PNG path.

    Needs the ``klayout`` python module and Pillow. ``review`` may be a Review or a path.
    """
    import klayout.db as db
    import klayout.lay as klay
    from PIL import Image, ImageDraw, ImageFont

    rv = review if isinstance(review, Review) else load_review(review)
    if only is not None:
        rv = Review(**{**rv.__dict__, "findings": [f for f in rv.findings if f.id in only]})
    if frame is not None:
        rv = Review(**{**rv.__dict__, "frame": frame})
    w, h = size
    lv = klay.LayoutView()
    lv.load_layout(str(gds), 0)  # type: ignore[call-overload]  (path, add_cellview)
    lyp = lyp or _pdk_lyp(pdk)
    if lyp:
        lv.load_layer_props(str(lyp))
    lv.max_hier_levels = 30
    lv.resize(w, h)
    cell = lv.cellview(0).cell
    bb = cell.dbbox()
    if rv.frame:
        box = db.DBox(rv.frame["x0"], rv.frame["y0"], rv.frame["x1"], rv.frame["y1"])
    else:
        m = margin_um if margin_um is not None else 0.04 * max(bb.width(), bb.height())
        box = bb.enlarged(m, m)
    lv.zoom_box(box)
    t = lv.viewport_trans()  # µm → pixels, y up
    tmp = Path(str(out_png) + ".base.png")
    lv.save_image(str(tmp), w, h)

    def px(x: float, y: float) -> tuple[float, float]:
        p = t.trans(db.DPoint(float(x), float(y)))
        return (p.x, h - p.y)

    img = Image.open(tmp).convert("RGBA")
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        fsm = ImageFont.truetype("DejaVuSans.ttf", 18)
    except OSError:
        font = fsm = ImageFont.load_default()

    def tag(x: float, y: float, text: str, col: tuple[int, int, int]) -> None:
        r = 16
        dr.ellipse([x - r, y - r, x + r, y + r], fill=col + (235,), outline=(0, 0, 0, 255), width=2)
        tw = dr.textlength(text, font=font)
        dr.text((x - tw / 2, y - 13), text, fill=(255, 255, 255, 255), font=font)

    # symmetry axis
    if rv.axis:
        if "x" in rv.axis:
            x0, _ = px(rv.axis["x"], box.bottom)
            dr.line([(x0, 0), (x0, h)], fill=(255, 255, 255, 140), width=2)
        if "y" in rv.axis:
            _, y0 = px(box.left, rv.axis["y"])
            dr.line([(0, y0), (w, y0)], fill=(255, 255, 255, 140), width=2)

    for f in rv.findings:
        col = COLORS.get(f.severity, (200, 200, 200))
        num = f.id.lstrip("Ff")
        for a in f.where:
            k = a.get("kind")
            if k in ("box", "device") and all(q in a for q in ("x0", "y0", "x1", "y1")):
                (X0, Y0), (X1, Y1) = px(a["x0"], a["y0"]), px(a["x1"], a["y1"])
                dr.rectangle(
                    [min(X0, X1), min(Y0, Y1), max(X0, X1), max(Y0, Y1)],
                    outline=col + (255,),
                    width=4,
                )
                dr.rectangle([min(X0, X1), min(Y0, Y1), max(X0, X1), max(Y0, Y1)], fill=col + (40,))
                tag(max(X0, X1), min(Y0, Y1), num, col)
            elif k == "point":
                X, Y = px(a["x"], a["y"])
                s = 14
                dr.line([(X - s, Y), (X + s, Y)], fill=col + (255,), width=3)
                dr.line([(X, Y - s), (X, Y + s)], fill=col + (255,), width=3)
                dr.ellipse([X - s, Y - s, X + s, Y + s], outline=col + (255,), width=3)
                tag(X + 22, Y - 22, num, col)
            elif k == "pair":
                A, B = px(a["a"]["x"], a["a"]["y"]), px(a["b"]["x"], a["b"]["y"])
                dr.line([A, B], fill=col + (255,), width=4)
                for P in (A, B):
                    dr.ellipse([P[0] - 8, P[1] - 8, P[0] + 8, P[1] + 8], fill=col + (255,))
                tag((A[0] + B[0]) / 2, (A[1] + B[1]) / 2 - 22, num, col)
            elif k == "line" and a.get("points"):
                pts = [px(x, y) for x, y in a["points"]]
                dr.line(pts, fill=col + (255,), width=4)
                tag(*pts[0], num, col)
            elif k == "rule":
                for x, y in a.get("locations", [])[:20]:
                    X, Y = px(x, y)
                    dr.rectangle([X - 10, Y - 10, X + 10, Y + 10], outline=col + (255,), width=3)
                if a.get("locations"):
                    X, Y = px(*a["locations"][0])
                    tag(X + 20, Y - 20, num, col)
            # net / device-without-box: legend only

    out = Image.alpha_composite(img, ov).convert("RGB")
    if legend:
        rows = [f"{f.id}  [{f.severity}] {f.title}" for f in rv.findings]
        rows += [f"verdict: {rv.verdict}    cell: {rv.cell}    gds sha {rv.gds_sha256[:12]}"]
        ncol = 2 if len(rows) > 8 else 1
        per = -(-len(rows) // ncol)
        lh = 26 * per + 24
        strip = Image.new("RGB", (w, lh), (250, 250, 250))
        d2 = ImageDraw.Draw(strip)
        colw = w // ncol
        for i, f in enumerate(rv.findings):
            cx, cy = 20 + (i // per) * colw, 12 + (i % per) * 26
            col = COLORS.get(f.severity, (200, 200, 200))
            d2.rectangle([cx, cy + 4, cx + 16, cy + 20], fill=col)
            d2.text((cx + 24, cy), rows[i], fill=(0, 0, 0), font=fsm)
        i = len(rv.findings)
        d2.text((20 + (i // per) * colw, 12 + (i % per) * 26), rows[-1], fill=(0, 0, 0), font=fsm)
        canvas = Image.new("RGB", (w, h + lh), (250, 250, 250))
        canvas.paste(out, (0, 0))
        canvas.paste(strip, (0, h))
        out = canvas
    out.save(str(out_png))
    tmp.unlink(missing_ok=True)
    return Path(out_png)


def anchor_bbox(f: Finding) -> tuple[float, float, float, float] | None:
    """Bounding box (µm) of all geometric anchors of a finding, or None if it has none."""
    xs: list[float] = []
    ys: list[float] = []
    for a in f.where:
        k = a.get("kind")
        if k in ("box", "device") and all(q in a for q in ("x0", "y0", "x1", "y1")):
            xs += [a["x0"], a["x1"]]
            ys += [a["y0"], a["y1"]]
        elif k == "point":
            xs.append(a["x"])
            ys.append(a["y"])
        elif k == "pair":
            xs += [a["a"]["x"], a["b"]["x"]]
            ys += [a["a"]["y"], a["b"]["y"]]
        elif k == "line":
            xs += [p[0] for p in a.get("points", [])]
            ys += [p[1] for p in a.get("points", [])]
        elif k == "rule":
            xs += [p[0] for p in a.get("locations", [])]
            ys += [p[1] for p in a.get("locations", [])]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def annotate_crops(
    gds: str | Path,
    review: Review | str | Path,
    out_dir: str | Path,
    *,
    pad_um: float = 5.0,
    size: tuple[int, int] = (1200, 900),
    **kw,
) -> list[Path]:
    """One zoomed PNG per finding that has geometry (``<out_dir>/<id>.png``), framed on its
    anchors + ``pad_um``. Returns the written paths."""
    rv = review if isinstance(review, Review) else load_review(review)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for f in rv.findings:
        bb = anchor_bbox(f)
        if bb is None:
            continue
        x0, y0, x1, y1 = bb
        # keep the image aspect: grow the shorter side
        wu, hu = max(x1 - x0, 1e-3) + 2 * pad_um, max(y1 - y0, 1e-3) + 2 * pad_um
        asp = size[0] / size[1]
        if wu / hu < asp:
            wu = hu * asp
        else:
            hu = wu / asp
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        frame = {"x0": cx - wu / 2, "y0": cy - hu / 2, "x1": cx + wu / 2, "y1": cy + hu / 2}
        written.append(
            annotate(
                gds,
                rv,
                out_dir / f"{f.id}.png",
                size=size,
                only=[f.id],
                frame=frame,
                legend=True,
                **kw,
            )
        )
    return written


def sha256_of(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
