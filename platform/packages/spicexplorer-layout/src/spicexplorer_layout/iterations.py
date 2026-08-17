"""Iteration audit trail for a generator-produced layout — snapshots + before/after diffs.

A layout is iterated (generator edit → build → DRC/LVS/PEX → verdict) many times before it
is done; a reader auditing the work wants to see *what changed and what it fixed*, not a
paragraph. This module keeps that trail mechanically:

- :func:`snapshot` — after every round, copy the generator source and the GDS into
  ``<iter_dir>/it<NN>/`` (``gen.py``, ``layout.gds``, ``layout.png``), record the verdicts
  (DRC per-rule counts + hit locations, LVS, PEX, scorecard if any), the knob values, the
  designer's one-line *note* ("what changed / what it fixed") and shas, and append the entry
  to ``<iter_dir>/iterations.yaml``.
- :func:`diff_png` — a **before | after** picture for two snapshots: both renders side by
  side; on the *after* side the regions that changed (per-layer GDS XOR, boxed) and the
  *before* DRC hits marked as fixed (green) or remaining (red); on the *before* side the
  hits that were there. Uses the review renderer (:mod:`review`), so markers are exact.
- :func:`iterations_table_md` — the Markdown table for the report's *Iterations* section,
  generated from ``iterations.yaml`` (with the diff images linked).

Sizes: a GDS snapshot can be MBs; keep ``it*/layout.gds`` in the ignored build dir unless the
block repo says otherwise — ``iterations.yaml`` + the PNGs + ``gen.py`` copies are the small,
committable trail. ``snapshot(..., keep_gds=False)`` records the sha only.
"""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .review import Finding, Review, annotate


@dataclass
class IterationEntry:
    id: str                              # "it03"
    note: str                            # ONE terse line: problem -> fix -> effect (titles, tables)
    detail: str = ""                     # optional long form (numbers, reasoning); never drawn on pictures
    gen_sha256: str = ""
    gds_sha256: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    area_um2: float | None = None
    drc: dict[str, Any] = field(default_factory=dict)      # {passed, n, rules: {rule: count}}
    lvs: dict[str, Any] = field(default_factory=dict)      # {passed, matched, unmatched}
    pex: dict[str, Any] = field(default_factory=dict)      # {ok, mode, n_c, n_r}
    scorecard: dict[str, Any] = field(default_factory=dict)
    files: dict[str, str] = field(default_factory=dict)    # relative paths: gen, gds, png, diff
    drc_hits: dict[str, list[list[float]]] = field(default_factory=dict)  # rule -> [[x,y],...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha(p: str | Path | None) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if p and Path(p).is_file() else ""


def _load_log(iter_dir: Path) -> dict[str, Any]:
    f = iter_dir / "iterations.yaml"
    if f.is_file():
        import yaml

        return yaml.safe_load(f.read_text()) or {"iterations": []}
    return {"iterations": []}


def _save_log(iter_dir: Path, log: dict[str, Any]) -> None:
    import yaml

    (iter_dir / "iterations.yaml").write_text(
        yaml.safe_dump(log, sort_keys=False, allow_unicode=True, width=100)
    )


NOTE_MAX = 140   # a headline, not a paragraph — longer text belongs in ``detail``


def snapshot(iter_dir: str | Path, *, note: str, gen_path: str | Path, gds: str | Path | None,
             params: dict[str, Any] | None = None, drc: Any = None, lvs: Any = None, pex: Any = None,
             scorecard: dict[str, Any] | None = None, area_um2: float | None = None,
             keep_gds: bool = True, render: bool = True, pdk: str = "ihp-sg13g2",
             size: tuple[int, int] = (1600, 1200), detail: str = "") -> IterationEntry:
    """Record one iteration. ``drc/lvs/pex`` are the signoff verdict objects (or dicts); a
    verdict of ``None`` means the stage was not run this round.

    ``note`` is the ONE-LINE headline an expert reads on the diff picture and in the table:
    *problem -> fix -> effect*, e.g. ``"TM1.b x5 at xc12 seam: comb bars inset w/2 before end
    caps -> DRC 0"``. Anything longer than :data:`NOTE_MAX` chars is a warning; put numbers and
    reasoning in ``detail`` (kept in the YAML, never drawn)."""
    if len(note) > NOTE_MAX:
        import warnings

        warnings.warn(f"iteration note is {len(note)} chars (> {NOTE_MAX}); keep the note a headline "
                      f"and move the rest to detail=", stacklevel=2)
    iter_dir = Path(iter_dir)
    log = _load_log(iter_dir)
    n = len(log["iterations"]) + 1
    it = f"it{n:02d}"
    d = iter_dir / it
    d.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    gen_path = Path(gen_path)
    if gen_path.is_file():
        shutil.copy2(gen_path, d / "gen.py")
        files["gen"] = f"{it}/gen.py"
    if gds and Path(gds).is_file():
        if keep_gds:
            shutil.copy2(gds, d / "layout.gds")
            files["gds"] = f"{it}/layout.gds"
        if render:
            try:
                from .gen import render_png

                render_png(gds, d / "layout.png", pdk=pdk, size=size)
                files["png"] = f"{it}/layout.png"
            except Exception as e:  # rendering is best-effort
                files["png_error"] = f"{type(e).__name__}: {e}"

    def _d(x: Any) -> dict[str, Any]:
        if x is None:
            return {}
        return x.to_dict() if hasattr(x, "to_dict") else dict(x)

    dd, ld, pd_ = _d(drc), _d(lvs), _d(pex)
    hits: dict[str, list[list[float]]] = {}
    for v in dd.get("violations", []) or []:
        hits[v["rule"]] = [[float(x), float(y)] for x, y in v.get("locations", [])]
    entry = IterationEntry(
        id=it, note=note, detail=detail, gen_sha256=_sha(gen_path), gds_sha256=_sha(gds), params=dict(params or {}),
        area_um2=area_um2,
        drc={"passed": dd.get("passed"), "n": dd.get("n_violations"),
             "rules": {v["rule"]: v["count"] for v in dd.get("violations", []) or []}} if dd else {},
        lvs={"passed": ld.get("passed"), "matched": ld.get("matched"),
             "unmatched": ld.get("unmatched"), "netlist_sha": ld.get("netlist_sha")} if ld else {},
        pex={"ok": pd_.get("ok"), "mode": pd_.get("mode"), "n_c": pd_.get("n_c"),
             "n_r": pd_.get("n_r")} if pd_ else {},
        scorecard=dict(scorecard or {}), files=files, drc_hits=hits,
    )
    log["iterations"].append(entry.to_dict())
    _save_log(iter_dir, log)
    return entry


def _xor_boxes(gds_a: str | Path, gds_b: str | Path, *, min_area_um2: float = 0.05,
               merge_um: float = 2.0, max_boxes: int = 40) -> tuple[list[dict[str, Any]], float]:
    """Regions that differ between two GDS files: the per-layer XORs are unioned, clustered
    (``merge_um`` apart) and returned as boxes (µm, largest first) together with the changed
    fraction of the drawn area, summed over layers (0..1). Layers touched are listed per box."""
    import klayout.db as db

    la, lb = db.Layout(), db.Layout()
    la.read(str(gds_a))
    lb.read(str(gds_b))
    ta, tb = la.top_cell(), lb.top_cell()
    infos = {(li.layer, li.datatype) for li in la.layer_infos()} | {
        (li.layer, li.datatype) for li in lb.layer_infos()}
    dbu = la.dbu
    union = db.Region()
    per_layer: list[tuple[str, Any]] = []
    drawn = 0.0
    for lay, dt in sorted(infos):
        ia, ib = la.find_layer(lay, dt), lb.find_layer(lay, dt)
        ra = db.Region(ta.begin_shapes_rec(ia)) if ia is not None else db.Region()
        rb = db.Region(tb.begin_shapes_rec(ib)) if ib is not None else db.Region()
        drawn += (ra | rb).area()
        x = ra ^ rb
        if not x.is_empty():
            per_layer.append((f"{lay}/{dt}", x))
            union += x
    if union.is_empty():
        return [], 0.0
    # changed fraction of the drawn area (summed over layers): ~0 for a local edit, ~0.5+ for a shift
    frac = sum(x.area() for _, x in per_layer) / max(drawn, 1)
    clusters = union.sized(int(merge_um / 2 / dbu)).merged()
    full = (ta.bbox() + tb.bbox()).area()
    out: list[dict[str, Any]] = []
    for poly in clusters.each():
        b = poly.bbox()
        probe = db.Region(b)
        area = (union & probe).area() * dbu * dbu
        if area < min_area_um2:
            continue
        layers = [name for name, x in per_layer if not (x & probe).is_empty()]
        out.append({"layers": layers, "x0": b.left * dbu, "y0": b.bottom * dbu,
                    "x1": b.right * dbu, "y1": b.top * dbu, "area": area,
                    "bbox_frac": b.area() / max(full, 1)})
    out.sort(key=lambda r: -r["area"])
    return out[:max_boxes], frac


def diff_png(iter_dir: str | Path, before: str, after: str, out_png: str | Path | None = None, *,
             pdk: str = "ihp-sg13g2", size: tuple[int, int] = (1400, 1050),
             cell: str = "", global_change_frac: float = 0.4) -> Path:
    """Render **before | after** for two iteration ids (e.g. ``"it02"``, ``"it03"``).

    Left: the before layout with its DRC hits (red squares) and, as a note, its LVS state.
    Right: the after layout with the changed regions boxed (orange; per-layer GDS XOR, clustered)
    and the before-hits marked fixed (blue) or remaining/new (red). If more than
    ``global_change_frac`` of the drawn area differs, or one change cluster spans more than that
    fraction of the cell (a floorplan-wide shift/resize/re-pitch), the big boxes are replaced by
    one note — boxing everything hides the picture; small local clusters are still drawn. Needs
    both snapshots' ``layout.gds``.
    """
    from PIL import Image, ImageDraw, ImageFont

    iter_dir = Path(iter_dir)
    log = _load_log(iter_dir)
    ents = {e["id"]: e for e in log["iterations"]}
    ea, eb = ents[before], ents[after]
    ga, gb = iter_dir / ea["files"].get("gds", ""), iter_dir / eb["files"].get("gds", "")
    if not ga.is_file() or not gb.is_file():
        raise FileNotFoundError("both snapshots need layout.gds (snapshot(keep_gds=True))")
    out_png = Path(out_png) if out_png else iter_dir / f"diff_{before}_{after}.png"

    # --- before: its own DRC hits
    fa: list[Finding] = []
    for i, (rule, locs) in enumerate(ea.get("drc_hits", {}).items(), 1):
        fa.append(Finding(f"F{i}", "blocker", "drc", f"{rule} ×{ea['drc'].get('rules', {}).get(rule, len(locs))}",
                          where=[{"kind": "rule", "name": rule, "locations": locs}]))
    def _status(e: dict[str, Any]) -> str:
        d, lv, px_ = e.get("drc") or {}, e.get("lvs") or {}, e.get("pex") or {}
        parts = []
        if d:
            parts.append("DRC 0" if d.get("passed") else f"DRC {d.get('n')}")
        if lv:
            parts.append("LVS ok" if lv.get("passed") else "LVS MISMATCH")
        if px_ and px_.get("ok"):
            parts.append(f"PEX {px_.get('mode')} {px_.get('n_c')}C")
        if e.get("area_um2"):
            parts.append(f"{e['area_um2'] / 1e3:.1f}k µm²")
        return " · ".join(parts)

    ra = Review(cell=cell or before, gds=str(ga), verdict=_status(ea), findings=fa)
    pa = annotate(ga, ra, out_png.with_name(out_png.stem + "_a.png"), size=size, pdk=pdk, legend=True)

    # --- after: changed regions + before-hits fixed/remaining
    fb: list[Finding] = []
    boxes, frac = _xor_boxes(ga, gb)
    wide = [bx for bx in boxes if bx["bbox_frac"] > global_change_frac]
    if frac > global_change_frac or wide:
        # a floorplan-wide change (shift / resize / re-pitch): boxing "everything" hides the picture
        fb.append(Finding("F1", "major", "other",
                          f"floorplan-wide change ({frac:.0%} of drawn area) — large boxes suppressed"))
        boxes = [bx for bx in boxes if bx["bbox_frac"] <= global_change_frac and bx["bbox_frac"] < 0.1]
    # change boxes: ONE legend line for all of them (the boxes themselves localize; per-box
    # rows were noise), numbered markers still land on each box
    if boxes:
        tot = sum(bx["area"] for bx in boxes)
        lays = sorted({name for bx in boxes for name in bx["layers"]})
        fb.append(Finding(f"F{len(fb) + 1}", "major", "other",
                          f"{len(boxes)} changed region(s), {tot:.1f} µm² on {len(lays)} layer(s)"
                          + (f" [{','.join(lays[:4])}{'…' if len(lays) > 4 else ''}]"),
                          where=[{"kind": "box", "x0": bx["x0"], "y0": bx["y0"],
                                  "x1": bx["x1"], "y1": bx["y1"]} for bx in boxes]))
    after_hits = eb.get("drc_hits", {})
    k = len(fb)
    for rule, locs in ea.get("drc_hits", {}).items():
        remaining = after_hits.get(rule, [])
        rem_set = {(round(x, 2), round(y, 2)) for x, y in remaining}
        fixed = [p for p in locs if (round(p[0], 2), round(p[1], 2)) not in rem_set]
        if fixed:
            k += 1
            fb.append(Finding(f"F{k}", "note", "drc", f"{rule}: fixed ×{len(fixed)}",
                              where=[{"kind": "rule", "name": rule, "locations": fixed}]))
        if remaining:
            k += 1
            fb.append(Finding(f"F{k}", "blocker", "drc", f"{rule}: still ×{len(remaining)}",
                              where=[{"kind": "rule", "name": rule, "locations": remaining}]))
    for rule, locs in after_hits.items():
        if rule not in ea.get("drc_hits", {}) and locs:
            k += 1
            fb.append(Finding(f"F{k}", "blocker", "drc", f"{rule}: NEW ×{len(locs)}",
                              where=[{"kind": "rule", "name": rule, "locations": locs}]))
    rb = Review(cell=cell or after, gds=str(gb), verdict=_status(eb), findings=fb)
    pb = annotate(gb, rb, out_png.with_name(out_png.stem + "_b.png"), size=size, pdk=pdk, legend=True)

    # --- side by side: short title, then the headline note wrapped under it (never clipped)
    A, B = Image.open(pa), Image.open(pb)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        fnote = ImageFont.truetype("DejaVuSans.ttf", 19)
    except OSError:
        font = fnote = ImageFont.load_default()

    def _wrap(text: str, width_px: int, max_lines: int = 3) -> list[str]:
        words, lines, cur = text.split(), [], ""
        for w in words:
            cand = (cur + " " + w).strip()
            if fnote.getlength(cand) <= width_px:
                cur = cand
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = lines[-1][:-1] + "…"
        return lines

    la_, lb_ = _wrap(ea["note"], A.width - 20), _wrap(eb["note"], B.width - 20)
    band = 34 + 24 * max(len(la_), len(lb_)) + 8
    W, H = A.width + B.width + 30, max(A.height, B.height) + band
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(A, (0, band))
    canvas.paste(B, (A.width + 30, band))
    dr = ImageDraw.Draw(canvas)
    dr.text((10, 6), f"BEFORE — {before}", fill=(0, 0, 0), font=font)
    dr.text((A.width + 40, 6), f"AFTER — {after}", fill=(0, 0, 0), font=font)
    for i, ln in enumerate(la_):
        dr.text((10, 36 + 24 * i), ln, fill=(40, 40, 40), font=fnote)
    for i, ln in enumerate(lb_):
        dr.text((A.width + 40, 36 + 24 * i), ln, fill=(40, 40, 40), font=fnote)
    canvas.save(out_png)
    Path(pa).unlink(missing_ok=True)
    Path(pb).unlink(missing_ok=True)
    eb.setdefault("files", {})["diff_from_" + before] = out_png.name
    _save_log(iter_dir, log)
    return out_png


def iterations_table_md(iter_dir: str | Path, *, rel_prefix: str = "") -> str:
    """Markdown for the report's *Iterations* section, from ``iterations.yaml``."""
    iter_dir = Path(iter_dir)
    log = _load_log(iter_dir)
    rows = ["| it | what changed / what it fixed | DRC | LVS | PEX | area µm² | files |",
            "|---|---|---|---|---|---|---|"]
    for e in log["iterations"]:
        d = e.get("drc") or {}
        drc = "—" if not d else ("**0**" if d.get("passed") else
                                  f"{d.get('n')} (" + ", ".join(f"{r} ×{c}" for r, c in list((d.get('rules') or {}).items())[:4]) + ")")
        lv = e.get("lvs") or {}
        lvs = "—" if not lv else ("match" if lv.get("passed") else "MISMATCH")
        px = e.get("pex") or {}
        pex = "—" if not px else (f"{px.get('mode')} {px.get('n_c')}C/{px.get('n_r')}R" if px.get("ok") else "fail")
        f = e.get("files") or {}
        links = " ".join(f"[{k}]({rel_prefix}{v})" for k, v in f.items() if k in ("png", "gen") or k.startswith("diff_from_"))
        area = f"{e['area_um2']:.0f}" if e.get("area_um2") else ""
        rows.append(f"| {e['id']} | {e['note']} | {drc} | {lvs} | {pex} | {area} | {links} |")
    return "\n".join(rows) + "\n"


def set_note(iter_dir: str | Path, it: str, note: str, detail: str | None = None) -> None:
    """Rewrite an entry's headline (and optionally its detail) in ``iterations.yaml`` — for
    tightening notes after the fact; re-run :func:`diff_png` for the affected pairs afterwards."""
    iter_dir = Path(iter_dir)
    log = _load_log(iter_dir)
    for e in log["iterations"]:
        if e["id"] == it:
            if detail is None and len(e.get("note", "")) > len(note) and not e.get("detail"):
                e["detail"] = e["note"]          # keep the long form, don't lose information
            elif detail is not None:
                e["detail"] = detail
            e["note"] = note
            break
    else:
        raise KeyError(it)
    _save_log(iter_dir, log)


__all__ = ["IterationEntry", "NOTE_MAX", "snapshot", "diff_png", "iterations_table_md", "set_note"]
