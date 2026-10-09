"""Render a generated ``.sch`` to an image with headless xschem.

Verified behaviour in the EDA container (``spicexplorer-spice-base:local``):

* ``xschem -x -q --svg --plotfile <out.svg> <in.sch>`` renders **headlessly** via cairo and exits 0.
  Symbol resolution needs the PDK xschem dir on ``XSCHEM_LIBRARY_PATH`` (the container default omits
  it). We judge success by "a non-empty SVG was written", not by the exit code, because a benign
  ``tkwait`` message can appear on stderr. With net colouring on (the default), we instead drive the
  export through ``--command 'xschem select_all; xschem hilight; xschem print svg <out>'`` so the
  per-net highlight palette is applied first (``--svg`` exports before ``--command`` runs).
* ``xschem --png`` requires a running X server (it rasters through Tk), which the headless image lacks.
  So PNG is produced by rasterizing the SVG with :mod:`cairosvg` — no X server, and faithful to
  xschem's own rendering. ``cairosvg`` is an optional dependency (the ``[render]`` extra); when it's
  absent we fall back to ``rsvg-convert`` and then to ImageMagick, and return the SVG with a note if
  none of the three is installed. ImageMagick's BUILT-IN renderer loses drawing (issue #225), so that
  fallback warns loudly and names itself in ``RenderResult.rasterizer``.
* The exported SVG is post-processed before anything reads it: :func:`fit_viewport` widens the
  viewport to the text at the sheet's edges, and :func:`stroke_safe_svg` copies the stylesheet onto
  the elements so a caller that rasterizes the SVG ITSELF does not silently lose wires.

When xschem isn't on ``PATH`` at all (e.g. a native macOS dev box), :func:`render` is a clean no-op:
it returns ``available=False`` with no image — the ``.sch`` itself is still valid and renders in the
UI's live viewer. PNG/SVG export is strictly additive.
"""

from __future__ import annotations

import html
import logging
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .sch_parser import SchText, parse_sch
from .sym_library import default_search_paths

__all__ = [
    "RenderResult",
    "render",
    "xschem_available",
    "drawn_elements",
    "fit_viewport",
    "stroke_safe_svg",
    "missing_sheet_text",
    "with_text_extents",
]

logger = logging.getLogger(__name__)

#: SVG tags xschem uses to draw a schematic. `rect` is excluded on purpose: the export always
#: contains exactly one, the background, and counting it would make an empty sheet look drawn.
_DRAWN = re.compile(r"<(path|line|polyline|polygon|circle|ellipse|text)\b")

_SVG_TAG = re.compile(r"<svg\b[^>]*>")
_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
#: Where an SVG element keeps its GEOMETRY. Only these are read — a class name like `l4` and a
#: `stroke-width` are numbers too, and sweeping every number in the tag put the viewport at
#: x=888816 on the first sheet it saw.
_GEOM_RUN = re.compile(r'\b(?:d|points)="([^"]*)"')
_GEOM_XY = re.compile(r'\b(x|y|x1|y1|x2|y2|cx|cy)="(-?[\d.eE+-]+)"')
#: A whole ``<text>`` element, attributes and content. Text is measured on its own (below) because
#: its position is a TRANSFORM, not an ``x``/``y`` pair, and because its extent depends on the
#: string it draws — neither of which the attribute scan above can see.
_TEXT_EL = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.DOTALL)
#: ``transform="translate(X, Y)"`` / ``translate(X Y)`` — how xschem places every string.
_TRANSLATE = re.compile(
    r'\btransform="[^"]*\btranslate\(\s*(-?[\d.eE+-]+)[\s,]+(-?[\d.eE+-]+)\s*\)'
)
_FONT_SIZE = re.compile(r'\bfont-size="(-?[\d.eE+-]+)"')
_TEXT_ANCHOR = re.compile(r'\btext-anchor="\s*(start|middle|end)\s*"')
#: ``&amp;``/``&#160;`` draw as ONE glyph; count them as one character, not as five.
_ENTITY = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")
#: Advance width of one character, in ems. 0.6 em is Courier's fixed advance and an upper bound for
#: the proportional sans xschem exports (which averages ~0.5 em), so the reserved room is never too
#: SHORT — and a viewport a few percent too wide clips nothing.
_CHAR_ADVANCE = 0.6
#: Used when an element carries no ``font-size``. xschem always writes one; a hand-made SVG may not.
_FALLBACK_FONT_SIZE = 10.0


def drawn_elements(svg: str) -> int:
    """How many drawing elements an exported SVG actually contains.

    A render is judged by its CONTENT, not by "a non-empty file appeared". xschem exits 0 and
    writes a perfectly valid ~3 kB SVG — ``<svg><style><rect/></svg>``, the background and nothing
    else — when it could not open the schematic at all. A sheet of record with no circuit on it is
    not evidence, and the size check reported it as success.
    """
    return len(_DRAWN.findall(svg))


def _text_box(attrs: str, content: str) -> tuple[list[float], list[float]]:
    """The box one ``<text>`` element draws into: its anchor plus the string's estimated extent.

    Two things make text different from every other element, and missing either is what left issue
    #159's edge label clipped anyway (issue #224):

    * **Position is a transform.** xschem writes ``transform="translate(120.7, 175.2)"`` and no
      ``x``/``y`` attributes at all, so an attribute scan contributes NOTHING for any string and a
      port name drawn left of x=0 never widens the viewport. Both forms are composed here
      (``translate`` offset plus any ``x``/``y``), so either spelling works.
    * **A string occupies width the SVG never states.** It is estimated from ``font-size`` times the
      character count (see :data:`_CHAR_ADVANCE`) and laid out in the direction the text runs —
      rightward from the anchor by default, leftward for ``text-anchor="end"``, split for
      ``middle``. Only ``translate`` is understood: a ``rotate``/``matrix`` transform (which xschem's
      export does not use) contributes its anchor alone.

    The vertical extent spans baseline−``font-size`` (cap top) to the baseline itself; descenders
    are inside the margin :func:`fit_viewport` adds.
    """
    tx = ty = 0.0
    if (m := _TRANSLATE.search(attrs)) is not None:
        tx, ty = float(m.group(1)), float(m.group(2))
    x = y = 0.0
    for key, val in _GEOM_XY.findall(attrs):
        try:
            num = float(val)
        except ValueError:  # pragma: no cover - malformed attribute
            continue
        if key == "x":
            x = num
        elif key == "y":
            y = num
    x, y = tx + x, ty + y
    size = _FALLBACK_FONT_SIZE
    if (fs := _FONT_SIZE.search(attrs)) is not None:
        try:
            size = abs(float(fs.group(1)))
        except ValueError:  # pragma: no cover - malformed attribute
            size = _FALLBACK_FONT_SIZE
    width = len(_ENTITY.sub("x", content).strip()) * size * _CHAR_ADVANCE
    anchor = m.group(1) if (m := _TEXT_ANCHOR.search(attrs)) else "start"
    if anchor == "end":
        xs = [x - width, x]
    elif anchor == "middle":
        xs = [x - width / 2.0, x + width / 2.0]
    else:
        xs = [x, x + width]
    return xs, [y - size, y]


def _extents(svg: str) -> tuple[list[float], list[float]]:
    """Every x and every y the drawing actually uses."""
    xs: list[float] = []
    ys: list[float] = []
    for element in re.findall(r"<(?:path|line|polyline|polygon|circle|ellipse)\b[^>]*>", svg):
        for run in _GEOM_RUN.findall(element):
            nums = [float(n) for n in _NUM.findall(run)]
            xs += nums[0::2]
            ys += nums[1::2]
        for key, val in _GEOM_XY.findall(element):
            try:
                (ys if key[0] == "y" or key == "cy" else xs).append(float(val))
            except ValueError:  # pragma: no cover - malformed attribute
                continue
    for attrs, content in _TEXT_EL.findall(svg):
        tx, ty = _text_box(attrs, content)
        xs += tx
        ys += ty
    return xs, ys


def fit_viewport(svg: str, *, margin: float = 8.0) -> str:
    """Widen the exported SVG's viewport to the geometry it actually contains.

    xschem sizes the export from the schematic's object bounding box, which does not account for
    the WIDTH of text drawn at the edge — so a port label on the left of the sheet is drawn at a
    negative x and falls outside the viewport, silently (issue #159). The label's box is measured by
    :func:`_text_box`, which reads xschem's ``transform="translate(..)"`` placement and estimates the
    string's drawn width; reading ``x``/``y`` alone made this function a no-op for exactly the case
    it was added for (issue #224). Adding a ``viewBox`` that
    covers the real extent brings it back without moving anything: the file already holds the
    geometry, only the window onto it was too small. An export that fits already is returned
    byte-identical.
    """
    tag = _SVG_TAG.search(svg)
    if tag is None or "viewBox" in tag.group(0):
        return svg
    w = re.search(r'\bwidth="([\d.]+)"', tag.group(0))
    h = re.search(r'\bheight="([\d.]+)"', tag.group(0))
    if not (w and h):
        return svg
    xs, ys = _extents(svg)
    if not xs or not ys:
        return svg
    width, height = float(w.group(1)), float(h.group(1))
    x0, y0 = min(min(xs), 0.0), min(min(ys), 0.0)
    x1, y1 = max(max(xs), width), max(max(ys), height)
    if (x0, y0, x1, y1) == (0.0, 0.0, width, height):
        return svg
    x0, y0, x1, y1 = x0 - margin, y0 - margin, x1 + margin, y1 + margin
    new_tag = re.sub(r'\bwidth="[\d.]+"', f'width="{x1 - x0:.0f}"', tag.group(0))
    new_tag = re.sub(r'\bheight="[\d.]+"', f'height="{y1 - y0:.0f}"', new_tag)
    new_tag = new_tag[:-1] + f' viewBox="{x0:.0f} {y0:.0f} {x1 - x0:.0f} {y1 - y0:.0f}">'
    return svg.replace(tag.group(0), new_tag, 1)


# ---------------------------------------------------------------------------
# A sheet's own text survives the export (issue #239)
# ---------------------------------------------------------------------------
#: xschem sizes the export from the bounding box of DRAWN objects, padded out to the export's
#: fixed aspect, and writes nothing that falls outside the resulting window — a title above the
#: topmost wire is not clipped, it is ABSENT from the file. Measured on xschem 3.4.4 with a
#: three-wire sheet: the title at ``y = -170`` exports, at ``y = -180`` it is gone; widen the same
#: sheet from 140 to 940 units and even ``y = -200`` exports. So "outside the object bbox" is NOT
#: the rule — the aspect padding is part of it — and a static pre-pass that rewrote every record
#: outside the bbox would rewrite every sheet this package generates (``emit`` places every title
#: at ``min_y - 200``, and those sheets render their titles today). The guard below therefore lets
#: xschem itself be the oracle: export, ask which records did not arrive, and re-export only those
#: sheets with an extent object that forces the window open.

#: One text line's height in schematic units at ``size_y = 1``. Measured off an export: a
#: ``size 0.4`` record draws at ``font-size`` 20.8 schematic units.
_SCH_LINE_HEIGHT = 52.0
#: Layer 0 is the BACKGROUND colour in both colour schemes (``#000000`` dark, ``#ffffff`` light),
#: so a line drawn on it enlarges xschem's bounding box and paints nothing a reader can see.
_EXTENT_LAYER = 0
#: A ``T`` record whose text xschem substitutes at draw time (``@name``, ``tcleval(...)``) draws
#: something other than what the file says, so "is this string in the SVG" cannot judge it.
_SUBSTITUTED = re.compile(r"@\w|tcleval\s*\(")
#: ``hide=true`` in a text record's property block — xschem draws nothing, and neither should the
#: guard expect anything.
_HIDDEN = re.compile(r"\bhide\s*=\s*(?:true|1)\b", re.IGNORECASE)


def _judgeable(t: SchText) -> bool:
    """Is this ``T`` record one whose presence in the SVG can be decided by reading the file?"""
    return bool(t.text.strip()) and not _HIDDEN.search(t.props) and not _SUBSTITUTED.search(t.text)


def _svg_text(svg: str) -> str:
    """Every ``<text>`` element's content, entity-decoded, joined — the haystack for the guard."""
    return "\n".join(html.unescape(content) for _, content in _TEXT_EL.findall(svg))


def missing_sheet_text(sch_text: str, svg: str) -> tuple[str, ...]:
    """Top-level ``T`` records of ``sch_text`` that did not make it into ``svg``.

    Counting ``<text>`` elements cannot see this: the reported sheet had 20 of them and no title
    (issue #239) — symbol text (every instance name, every parameter, every pin label) so outnumbers
    the sheet's own records that a count comparison is never even close. Each record's text is
    looked for instead, line by line, in the decoded content of the export's ``<text>`` elements.

    Records xschem substitutes at draw time (``@name``, ``tcleval(…)``) and hidden ones are not
    judged — see :data:`_SUBSTITUTED` / :data:`_HIDDEN`.
    """
    try:
        texts = parse_sch(sch_text).texts
    except Exception as exc:  # pragma: no cover - a sheet the parser chokes on
        # render() degrades gracefully by contract; a guard is not a new way for it to fail.
        logger.debug("text guard: could not parse the sheet (%r); nothing judged", exc)
        return ()
    drawn = _svg_text(svg)
    missing: list[str] = []
    for t in texts:
        if not _judgeable(t):
            continue
        lines = [ln.strip() for ln in t.text.splitlines() if ln.strip()]
        if any(ln not in drawn for ln in lines):
            missing.append(t.text)
    return tuple(missing)


def _extent_box(t: SchText) -> tuple[float, float, float, float]:
    """A box that covers what the ``T`` record draws, in schematic units.

    An unrotated record is anchored at its top-left and runs right and down, which is what every
    title this package writes looks like. A rotated or mirrored one is covered by a square of the
    larger dimension around the anchor rather than by working out the four orientations: the box
    is only ever used to prise the export window open, and over-reserving on a rare record costs a
    little margin, never a dropped string.
    """
    lines = t.text.splitlines() or [""]
    height = _SCH_LINE_HEIGHT * abs(t.size_y) * len(lines)
    width = max(len(ln) for ln in lines) * _SCH_LINE_HEIGHT * abs(t.size_x) * _CHAR_ADVANCE
    if t.rot == 0 and t.flip == 0:
        return t.x, t.y, t.x + width, t.y + height
    reach = max(width, height)
    return t.x - reach, t.y - reach, t.x + reach, t.y + reach


def with_text_extents(sch_text: str, texts: tuple[str, ...]) -> str:
    """``sch_text`` plus one invisible extent line per named ``T`` record.

    The record itself is left exactly where its author put it — a title above the sheet stays above
    the sheet. What is added is an ``L 0 …`` graphic line across the text's extent: layer 0 is the
    background colour in both schemes, so it enlarges the bounding box xschem exports from and
    draws nothing. Measured on xschem 3.4.4: the sheet from issue #239 exports its title with the
    line and without it does not; a ZERO-length line is not registered at all, which is why the
    line spans the text's box rather than marking its corner.

    Nudging the record inside the bbox instead (the issue's option (a)) was rejected: it moves a
    caption a generator placed deliberately, and the placement it would have to move to is
    ``emit``'s own "clear above every device, where it cannot collide with a top-row gate label".

    The caller writes the result to a RENDER-TIME COPY; the committed ``.sch`` is never touched.
    """
    wanted = set(texts)
    if not wanted:
        return sch_text
    extents: list[str] = []
    for t in parse_sch(sch_text).texts:
        if t.text in wanted:
            x0, y0, x1, y1 = _extent_box(t)
            extents.append(f"L {_EXTENT_LAYER} {x0:g} {y0:g} {x1:g} {y1:g} {{}}")
    if not extents:
        return sch_text
    body = sch_text if sch_text.endswith("\n") else sch_text + "\n"
    return body + "\n".join(extents) + "\n"


#: The ``<style>`` block xschem writes, and one ``.lN{...}`` rule inside it.
_STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.DOTALL)
_CSS_RULE = re.compile(r"\.([A-Za-z_][\w-]*)\s*\{([^}]*)\}")
_CSS_DECL = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;]+)")
#: The declarations read off a class rule. Presentation attributes are the only styling
#: ImageMagick's built-in (MSVG) parser reads; ``stroke-linecap``/``-linejoin`` are cosmetic and
#: left in the stylesheet.
_INLINED = ("stroke", "stroke-width", "fill", "fill-opacity")
#: ...and the subset actually WRITTEN onto the element. ``fill-opacity`` is read (a transparent fill
#: is part of what makes a path vanish) but never inlined: MSVG multiplies the STROKE by it too, so
#: copying xschem's ``fill-opacity: 0.5`` highlight would hand that renderer half-strength wires —
#: measured. A conformant renderer keeps taking all four from the stylesheet either way.
_WRITTEN = ("stroke", "stroke-width", "fill")
_STYLED_EL = re.compile(r"<(path|line|polyline|polygon|circle|ellipse|rect)\b([^>]*?)(/?)>")
_CLASS_ATTR = re.compile(r'\bclass="([^"]*)"')
_D_ATTR = re.compile(r'\bd="([^"]*)"')
#: A ``d`` that is one straight segment — a path enclosing ZERO area, which no conformant renderer
#: can fill. xschem draws every wire and every symbol line in this form.
_TWO_POINT_D = re.compile(
    r"^\s*[Mm]\s*(?:-?[\d.eE+-]+)[\s,]+(?:-?[\d.eE+-]+)\s*"
    r"[Ll]\s*(?:-?[\d.eE+-]+)[\s,]+(?:-?[\d.eE+-]+)\s*$"
)
_TRANSPARENT = {"0", "0.0", "0%", ".0"}


def _class_rules(svg: str) -> dict[str, dict[str, str]]:
    """``{class name: {property: value}}`` for the properties worth inlining."""
    rules: dict[str, dict[str, str]] = {}
    for block in _STYLE_BLOCK.findall(svg):
        for name, body in _CSS_RULE.findall(block):
            decls = rules.setdefault(name, {})
            for prop, val in _CSS_DECL.findall(body):
                prop = prop.strip().lower()
                if prop in _INLINED:
                    decls[prop] = val.strip()
    return rules


def stroke_safe_svg(svg: str) -> str:
    """Make an xschem export survive a renderer that reads only presentation attributes.

    The SVG xschem writes is correct and renders correctly in cairo, librsvg and every browser. It
    does NOT rasterise faithfully through ImageMagick's built-in (MSVG) parser, and the failure is
    silent: **wires disappear from the PNG while the SVG is right** (issue #225). A design repo that
    exports ``fmt="svg"`` and rasterises the sheet itself gets a clean-looking picture of a circuit
    that is missing nets — on the reported sheet, both supply rails.

    Two properties of the export cause it, and both are fixed here:

    * **Styling lives only in a CSS class.** xschem writes ``<path class="l19" d="…"/>`` with the
      colour and width in a ``<style>`` block. MSVG does not apply it, so the path is drawn with
      default styling or not at all. Each element's class declarations are copied onto it as
      ``stroke`` / ``stroke-width`` / ``fill`` attributes, written AFTER the ``class`` attribute
      (that parser applies attributes in source order, so anything written before ``class`` loses).
    * **A ``fill="none"`` path is not drawn AT ALL** — stroke included; ``fill-opacity="0"`` behaves
      the same way (both measured on ImageMagick 7.1.2). Which wires survive is then decided by the
      highlight palette, since xschem gives some layers a fill colour and others ``fill: none``. A
      path that encloses zero area — one straight ``M…L…`` segment, which is how every wire and
      symbol line is written — is therefore given a fill equal to its stroke.

    **Both rewrites are no-ops for a conformant renderer.** The ``<style>`` block is kept, and a
    class selector outranks a presentation attribute in CSS specificity, so cairo/librsvg/browsers
    go on using the stylesheet exactly as before; and filling a zero-area path paints nothing
    anywhere. Only a renderer that ignores the stylesheet sees any difference — which is the one
    that was losing the wires.

    Known residual: a MULTI-point ``fill: none`` path (an open outline) keeps ``fill="none"``,
    because giving it a fill would flood its interior in a correct renderer — such a path is still
    dropped by MSVG. :func:`render` warns when that renderer is the one in use.
    """
    rules = _class_rules(svg)

    def rewrite(m: re.Match[str]) -> str:
        tag, attrs, close = m.group(1), m.group(2), m.group(3)
        cls = _CLASS_ATTR.search(attrs)
        decls = rules.get(cls.group(1).split()[0], {}) if cls and cls.group(1).strip() else {}
        present = {p: a.group(1) for p in _INLINED if (a := re.search(rf'\b{p}="([^"]*)"', attrs))}
        # 1. carry the class's declarations onto the element (never overriding an explicit attribute)
        wanted = {p: decls[p] for p in _WRITTEN if p in decls and p not in present}
        # 2. a zero-area stroked path gets a fill equal to its stroke
        if tag == "path":
            effective = {**decls, **present}
            fill, stroke = effective.get("fill"), effective.get("stroke")
            # Only an EXPLICIT ``none``/transparent counts. A path with no fill stated at all
            # already defaults to opaque black and is drawn by every renderer; rewriting it would
            # be noise.
            invisible = fill == "none" or effective.get("fill-opacity") in _TRANSPARENT
            d = _D_ATTR.search(attrs)
            if invisible and stroke and stroke != "none" and d and _TWO_POINT_D.match(d.group(1)):
                wanted["fill"] = stroke
        if not wanted:
            return m.group(0)
        out, added = attrs, []
        for prop, val in wanted.items():
            if prop in present:
                out = re.sub(rf'\b{prop}="[^"]*"', f'{prop}="{val}"', out, count=1)
            else:
                added.append(f'{prop}="{val}"')
        # APPENDED, never prepended. ImageMagick's parser applies attributes in source order and
        # lets a later ``class`` overwrite what an earlier attribute set, so an inlined ``fill``
        # written before ``class="l21"`` is silently undone by the very rule it is there to beat
        # (measured: identical raster, rails still missing). After the class, it holds.
        joined = (" " + " ".join(added)) if added else ""
        return f"<{tag}{out.rstrip()}{joined}{close}>"

    return _STYLED_EL.sub(rewrite, svg)


def _svg_user_width(svg: str) -> float | None:
    """The export's width in user units (the ``viewBox``'s if it has one, else ``width``)."""
    tag = _SVG_TAG.search(svg)
    if tag is None:
        return None
    if (vb := re.search(r'\bviewBox="([^"]*)"', tag.group(0))) is not None:
        nums = [float(n) for n in _NUM.findall(vb.group(1))]
        if len(nums) == 4 and nums[2] > 0:
            return nums[2]
    if (w := re.search(r'\bwidth="([\d.]+)"', tag.group(0))) is not None:
        return float(w.group(1))
    return None


#: What :func:`_rasterize` says when it had to fall back to ImageMagick's built-in renderer.
_MSVG_WARNING = (
    "PNG rasterized with ImageMagick's BUILT-IN (MSVG) renderer — neither cairosvg nor "
    'rsvg-convert is available. That renderer ignores the stylesheet and drops fill="none" '
    "paths, so the PNG may be MISSING WIRES even though the SVG is correct (issue #225). The "
    "export is rewritten by stroke_safe_svg() to survive it, but an open (multi-point) unfilled "
    "outline is still lost. Install cairosvg (the [render] extra) or rsvg-convert for a faithful "
    "raster; the .svg beside it is always right."
)


def _rasterize(svg_path: Path, png_path: Path, png_width: int) -> tuple[str | None, str]:
    """Rasterize ``svg_path`` to ``png_path``; return ``(rasterizer name, note)``.

    Tried in order of fidelity: ``cairosvg`` (xschem's own rendering library), then
    ``rsvg-convert``, then ImageMagick. The last one is a fallback that LOSES DRAWING — it is taken
    only when nothing else is installed, and it says so loudly (issue #225).
    """
    try:
        import cairosvg  # type: ignore[import-not-found]  # optional [render] extra, imported lazily

        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path), output_width=png_width)
        return "cairosvg", ""
    except Exception as exc:  # cairosvg missing or rasterization failed
        note = f"cairosvg unavailable ({exc!r}); trying an external rasterizer."

    if (rsvg := shutil.which("rsvg-convert")) is not None:
        proc = subprocess.run(
            [rsvg, "-w", str(png_width), "-o", str(png_path), str(svg_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if png_path.is_file() and png_path.stat().st_size > 0:
            return "rsvg-convert", note
        note = f"{note}\nrsvg-convert failed: {proc.stderr.strip()}"

    magick = shutil.which("magick") or shutil.which("convert")
    if magick is not None:
        # Scale through -density, not -resize: MSVG rasterizes at the requested dpi, while a resize
        # would upsample a 96-dpi raster and blur every stroke.
        user_w = _svg_user_width(svg_path.read_text(errors="replace")) or float(png_width)
        density = max(1.0, 96.0 * png_width / user_w)
        proc = subprocess.run(
            [
                magick,
                "-density",
                f"{density:.4f}",
                "-background",
                "white",
                str(svg_path),
                str(png_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if png_path.is_file() and png_path.stat().st_size > 0:
            logger.warning("%s", _MSVG_WARNING)
            return "imagemagick", f"{note}\n{_MSVG_WARNING}"
        note = f"{note}\nImageMagick failed: {proc.stderr.strip()}"

    return None, f"{note}\nNo rasterizer available."


def _reexport_with_text_extents(
    sch_path: Path,
    sch_text: str,
    dropped: tuple[str, ...],
    svg_path: Path,
    library_path: str,
    *,
    color_nets: bool,
    dark: bool,
) -> tuple[str | None, str]:
    """Export again from a render-time COPY of the sheet that carries invisible extent objects.

    The copy and its own rcfile live in a scratch directory that is deleted afterwards, so the
    committed ``.sch`` is untouched and the ``xschemrc`` beside the image still says exactly what
    the first pass wrote. The sheet's own directory joins the search path, so a design-local
    ``C {block.sym}`` next to the original still resolves from the scratch dir.
    """
    scratch = Path(tempfile.mkdtemp(dir=str(svg_path.parent), prefix=".n2x-extent-"))
    try:
        copy = scratch / sch_path.name
        copy.write_text(with_text_extents(sch_text, dropped))
        lib = os.pathsep.join([str(sch_path.parent), library_path])
        tmp_svg = scratch / svg_path.name
        log = _export_svg(copy, tmp_svg, lib, color_nets=color_nets, dark=dark)
        if not (tmp_svg.is_file() and tmp_svg.stat().st_size > 0):
            return None, f"re-export with text extents produced no SVG; keeping the first:\n{log}"
        text = tmp_svg.read_text(errors="replace")
        svg_path.write_text(text)
        return text, (
            f"{len(dropped)} text record(s) were missing from the export; re-exported with an "
            f"invisible extent object per record (issue #239).\n{log}"
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


ImageFmt = Literal["svg", "png"]


@dataclass(frozen=True)
class RenderResult:
    """The outcome of a render attempt."""

    sch_path: Path
    image_path: Path | None  # None when no image was produced
    fmt: ImageFmt | None
    available: bool  # was xschem on PATH?
    log: str = ""
    #: Drawing elements counted in the exported SVG. Zero means xschem wrote a valid file
    #: holding nothing but the background — see :func:`drawn_elements`.
    strokes: int = 0
    #: Which rasterizer produced the PNG (``"cairosvg"`` / ``"rsvg-convert"`` / ``"imagemagick"``),
    #: or ``None`` when no PNG was made. ``"imagemagick"`` means the built-in MSVG renderer, whose
    #: PNG may be missing wires the SVG has — see :data:`_MSVG_WARNING` and issue #225.
    rasterizer: str | None = None
    #: The sheet's own ``T`` records whose text is NOT in the export — a rendering DEFECT, not a
    #: style question (issue #239). Empty on a healthy sheet and on one the extent re-export
    #: repaired; non-empty means the image is missing text the ``.sch`` carries, and :func:`render`
    #: has also logged a warning. See :func:`missing_sheet_text`.
    texts_dropped: tuple[str, ...] = ()
    #: ``<text>`` elements in the exported SVG. Reported for the record; it is NOT what decides
    #: :attr:`texts_dropped` — symbol text outnumbers a sheet's own records many times over.
    text_elements: int = 0


def xschem_available() -> bool:
    """True if the ``xschem`` binary is on ``PATH``."""
    return shutil.which("xschem") is not None


def _library_path(explicit: str | None, pdk: str | None = None) -> str:
    if explicit:
        return explicit
    return os.pathsep.join(str(p) for p in default_search_paths(pdk))


def _relative_entry(entry: str, base: str | Path | None) -> str:
    """``entry`` written relative to ``base`` when it is ``base`` itself or lies inside it.

    Everything else — the platform's own ``docker/xschem_library``, a PDK root, a sibling project —
    is returned unchanged, because a relative path out of the rc's directory would encode the same
    machine-specific layout the absolute one does.
    """
    if base is None or not entry:
        return entry
    try:
        here = Path(os.path.realpath(entry))
        root = Path(os.path.realpath(base))
    except OSError:  # pragma: no cover - realpath on a pathological name
        return entry
    if here == root:
        return "."
    try:
        return here.relative_to(root).as_posix()
    except ValueError:
        return entry


def _rcfile_text(
    library_path: str, *, dark: bool = False, relative_to: str | Path | None = None
) -> str:
    """An xschemrc that seeds the Tcl ``XSCHEM_LIBRARY_PATH`` from ``library_path``.

    xschem resolves symbols from the *Tcl* variable, which the stock system xschemrc leaves unset and
    which the ``XSCHEM_LIBRARY_PATH`` env var alone does not populate — and the seeding rc only loads
    from ``$HOME/.xschem`` (image- and HOME-dependent). Shipping our own rc and passing ``--rcfile``
    makes symbol resolution independent of the runtime image / HOME.

    ``relative_to`` is the directory the rc is written into. The **output directory's own entry** is
    then emitted as ``.`` (and an entry nested inside it relative to the rc), because this file is a
    build product designs COMMIT beside their sheets — it is what makes a later re-netlist resolve
    the design's own symbols — and an absolute entry records whichever checkout drew the sheet last.
    Three revisions of one design's rc named three different directories, the most recent a
    throwaway worktree that no longer exists, and every rebuild from a different clone rewrote the
    file plus the ``** sch_path:`` comments of every ``.spice`` beside it (issue #248). Entries
    OUTSIDE the directory stay absolute: they are not the rc's to relativize.

    Relative entries resolve against xschem's working directory, which every caller here sets to the
    rc's own directory (:func:`_export_svg`, ``endcheck.xschem_source_netlist``) and which the
    documented re-netlist recipe runs from.
    """
    lines = ["# auto-generated by spicexplorer-netlist2xschem", "set XSCHEM_LIBRARY_PATH {}"]
    for entry in library_path.split(os.pathsep):
        if entry:
            lines.append(
                "append XSCHEM_LIBRARY_PATH {:" + _relative_entry(entry, relative_to) + "}"
            )
    if not dark:
        # A sheet of record is read on paper and in a report, both of which are white. xschem's
        # own default is the dark scheme, whose strokes come out pale on a light page — the render
        # had to be post-processed by hand before it could be committed (issue #159). Layer 0 is
        # the background, and this is the switch that turns it from #000000 to #ffffff.
        lines.append("set dark_colorscheme 0")
    return "\n".join(lines) + "\n"


def write_xschemrc(directory: str | Path, library_path: str, *, dark: bool = False) -> Path:
    """Write an xschemrc seeding ``library_path`` into ``directory`` and return its path.

    ``directory``'s own entry is written as ``.`` — see :func:`_rcfile_text` — so two builds of the
    same sheet from two different checkouts produce a byte-identical file.
    """
    rc = Path(directory) / "xschemrc"
    rc.write_text(_rcfile_text(library_path, dark=dark, relative_to=directory))
    return rc


def _export_svg(
    sch_path: Path,
    svg_path: Path,
    library_path: str,
    color_nets: bool = True,
    dark: bool = False,
) -> str:
    rc = write_xschemrc(svg_path.parent, library_path, dark=dark)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = library_path  # belt-and-suspenders alongside the rcfile
    cmd = ["xschem", "--rcfile", str(rc), "-x", "-q"]
    if color_nets:
        # Give every net its own colour (xschem's incrementing highlight palette) so each net name and
        # its wires render in a matching colour — the same flag drawn twice is then obviously one node.
        # Done purely at render time (select-all → highlight → export), so the .sch stays unchanged.
        # ``print svg`` replaces the ``--svg``/``--plotfile`` flags, which export before --command runs.
        cmd += [
            "--command",
            f"set incr_hilight 1; xschem select_all; xschem hilight; xschem print svg {{{svg_path}}}",
        ]
    else:
        cmd += ["--svg", "--plotfile", str(svg_path)]
    # ABSOLUTE. xschem resolves a relative schematic argument against the PWD environment
    # variable, not against the process's working directory, so passing a relative path with only
    # `cwd=` set makes any caller that is not a real shell `cd` open `<caller's $PWD>/<name>` —
    # which does not exist, which xschem reports on stderr and then exits 0 anyway, having written
    # a valid but EMPTY svg. `PWD` is set to match for the same reason.
    cmd.append(str(sch_path.resolve()))
    env["PWD"] = str(svg_path.parent.resolve())
    try:
        proc = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=120, cwd=str(svg_path.parent)
        )
        # Success is judged by the artifact, not the exit code (benign tkwait noise on stderr).
        return (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        return "xschem --svg timed out after 120s"


def render(
    sch_path: str | Path,
    *,
    fmt: ImageFmt = "svg",
    outdir: str | Path | None = None,
    library_path: str | None = None,
    png_width: int = 1600,
    color_nets: bool = True,
    pdk: str | None = None,
    dark: bool = False,
) -> RenderResult:
    """Render ``sch_path`` to ``fmt`` (``"svg"`` or ``"png"``).

    Returns a :class:`RenderResult`. Degrades gracefully: no xschem → ``available=False`` (no image);
    PNG requested but no rasterizer → SVG returned with a note. The ``.sch`` is never modified.

    ``color_nets`` (default on) colour-codes the render: each net's name labels and wires share one
    colour from xschem's highlight palette, so the (often several) flags of one net read as one node.

    ``pdk`` scopes the symbol search path (and therefore the generated ``xschemrc``) to that kit, so
    a commercial-kit design is not handed the vendored open-PDK symbol library. ``dark`` restores
    xschem's own dark colour scheme; the default is light, because the render is committed into a
    report.

    **The sheet's own text is checked, and repaired** (issue #239). xschem writes nothing that falls
    outside the window it sizes from the DRAWN objects, so a title above the topmost wire is absent
    from the file rather than clipped — invisible until the day a port moves and every sheet loses
    its name at once. After the export, every judgeable ``T`` record is looked for in the SVG; if
    any is missing the sheet is exported once more from a render-time copy carrying an invisible
    extent object (:func:`with_text_extents`), and whatever is *still* missing is reported in
    :attr:`RenderResult.texts_dropped` and logged as a warning. A healthy sheet costs one extra
    parse and renders byte-identically to before.
    """
    sch_path = Path(sch_path).resolve()
    out = Path(outdir).resolve() if outdir is not None else sch_path.parent
    out.mkdir(parents=True, exist_ok=True)

    if not xschem_available():
        return RenderResult(
            sch_path,
            None,
            None,
            available=False,
            log="xschem not on PATH; the .sch is still valid for the UI's live viewer.",
        )

    svg_path = out / f"{sch_path.stem}.svg"
    lib_path = _library_path(library_path, pdk)
    log = _export_svg(sch_path, svg_path, lib_path, color_nets=color_nets, dark=dark)
    if not (svg_path.is_file() and svg_path.stat().st_size > 0):
        return RenderResult(
            sch_path, None, None, available=True, log=f"xschem produced no SVG:\n{log}"
        )
    svg_text = svg_path.read_text(errors="replace")
    strokes = drawn_elements(svg_text)

    # Did every ``T`` record the sheet carries actually arrive? xschem drops one that falls outside
    # the window it sizes from the drawn objects, silently (issue #239). It is the oracle for its
    # own rule, so ask it: only a sheet that really lost text is exported a second time, from a
    # copy carrying an invisible extent object. Skipped when the export holds NOTHING — every
    # record is "missing" from an empty file, and that diagnostic (below) is the one worth having.
    dropped: tuple[str, ...] = ()
    if strokes:
        sch_text = sch_path.read_text(errors="replace")
        dropped = missing_sheet_text(sch_text, svg_text)
        if dropped:
            retried, retry_log = _reexport_with_text_extents(
                sch_path, sch_text, dropped, svg_path, lib_path, color_nets=color_nets, dark=dark
            )
            log = f"{log}\n{retry_log}"
            if retried is not None:
                svg_text = retried
                strokes = drawn_elements(svg_text)
                dropped = missing_sheet_text(sch_text, svg_text)
        if dropped:
            logger.warning(
                "%s: xschem dropped %d text record(s) from the export and the extent re-export "
                "did not bring them back: %s",
                sch_path.name,
                len(dropped),
                ", ".join(repr(t) for t in dropped),
            )
    text_elements = len(_TEXT_EL.findall(svg_text))
    # Post-process the export in place: widen the viewport to the text at the edges (#159/#224) and
    # make the styling survive a renderer that reads only presentation attributes (#225).
    rewritten = stroke_safe_svg(fit_viewport(svg_text))
    if rewritten != svg_text:
        svg_path.write_text(rewritten)
    if strokes == 0:
        return RenderResult(
            sch_path,
            None,
            None,
            available=True,
            log=(
                f"xschem wrote {svg_path.name} but drew NOTHING into it — the export holds only "
                f"the background. The sheet was not read; check the log for an 'unable to open "
                f"file' line and the symbol search path.\n{log}"
            ),
        )

    if fmt == "svg":
        return RenderResult(
            sch_path,
            svg_path,
            "svg",
            available=True,
            log=log,
            strokes=strokes,
            texts_dropped=dropped,
            text_elements=text_elements,
        )

    # fmt == "png": rasterize the SVG (cairosvg, else rsvg-convert, else ImageMagick).
    png_path = out / f"{sch_path.stem}.png"
    rasterizer, note = _rasterize(svg_path, png_path, png_width)
    if rasterizer is None:
        return RenderResult(
            sch_path,
            svg_path,
            "svg",
            available=True,
            log=f"{log}\nPNG requested but rasterization unavailable; returning SVG instead.\n{note}",
            strokes=strokes,
            texts_dropped=dropped,
            text_elements=text_elements,
        )
    return RenderResult(
        sch_path,
        png_path,
        "png",
        available=True,
        log=f"{log}\n{note}".rstrip(),
        strokes=strokes,
        rasterizer=rasterizer,
        texts_dropped=dropped,
        text_elements=text_elements,
    )
