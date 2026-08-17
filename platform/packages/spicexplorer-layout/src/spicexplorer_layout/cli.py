"""``spicexplorer-layout`` CLI — build a generator to GDS (JSON summary), list its knobs, render."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .gen import build_gds, load_generator, params_from_json, params_schema, render_png


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="spicexplorer-layout")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build a generator module to GDS")
    b.add_argument("generator", help="path to gen_<cell>.py or a dotted module")
    b.add_argument("--out-dir", required=True)
    b.add_argument("--params", default=None, help="JSON overrides for LayoutParams")
    b.add_argument("--sizing", default=None, help="sizing JSON (design.json) passed to build()")
    b.add_argument("--cell", default=None)
    b.add_argument("--png", action="store_true", help="also render <cell>.png")
    b.add_argument("--json", action="store_true", help="print the GdsBuild as one JSON line")
    k = sub.add_parser("knobs", help="print LayoutParams schema (name/default/bounds)")
    k.add_argument("generator")
    r = sub.add_parser("render", help="render a GDS to PNG with PDK colours")
    r.add_argument("gds")
    r.add_argument("png")
    r.add_argument("--pdk", default="ihp-sg13g2")
    an = sub.add_parser("annotate", help="draw a layout-review/1 REVIEW.yaml over the PDK render")
    an.add_argument("gds")
    an.add_argument("review")
    an.add_argument("png")
    an.add_argument("--crops", default=None, help="also write one zoomed PNG per finding here")
    an.add_argument("--pdk", default="ihp-sg13g2")
    vr = sub.add_parser("validate-review", help="validate a REVIEW.yaml/.json against layout-review/1")
    vr.add_argument("review")
    sn = sub.add_parser("snapshot", help="record one layout iteration (gen.py + gds + png + verdicts)")
    sn.add_argument("iter_dir")
    sn.add_argument("--note", required=True, help="ONE-LINE headline: problem -> fix -> effect (<=140 chars)")
    sn.add_argument("--detail", default="", help="long form (numbers, reasoning); kept in the YAML only")
    sn.add_argument("--gen", required=True, help="generator source to copy")
    sn.add_argument("--gds", default=None)
    sn.add_argument("--params", default=None, help="knob values JSON (file or inline)")
    sn.add_argument("--drc", default=None, help="DrcResult JSON (file)")
    sn.add_argument("--lvs", default=None, help="LvsResult JSON (file)")
    sn.add_argument("--pex", default=None, help="PexResult JSON (file)")
    sn.add_argument("--scorecard", default=None, help="post-layout scorecard JSON (file)")
    sn.add_argument("--area", type=float, default=None)
    sn.add_argument("--no-gds", action="store_true", help="record the GDS sha only, do not copy it")
    sn.add_argument("--pdk", default="ihp-sg13g2")
    nt = sub.add_parser("set-note", help="tighten an iteration's headline after the fact (old note -> detail)")
    nt.add_argument("iter_dir")
    nt.add_argument("it")
    nt.add_argument("note")
    nt.add_argument("--detail", default=None)
    df = sub.add_parser("diff", help="before|after PNG for two iteration ids (it01 it02)")
    df.add_argument("iter_dir")
    df.add_argument("before")
    df.add_argument("after")
    df.add_argument("--out", default=None)
    df.add_argument("--pdk", default="ihp-sg13g2")
    im = sub.add_parser("iterations-md", help="Markdown table of iterations.yaml for the report")
    im.add_argument("iter_dir")
    im.add_argument("--rel-prefix", default="", help="path prefix for the file links")
    a = ap.parse_args(argv)
    if a.cmd == "annotate":
        from .review import annotate, annotate_crops, load_review

        rv = load_review(a.review)
        print(annotate(a.gds, rv, a.png, pdk=a.pdk))
        if a.crops:
            for pth in annotate_crops(a.gds, rv, a.crops, pdk=a.pdk):
                print(pth)
        return 0
    if a.cmd == "validate-review":
        import yaml

        from .review import load_review, validate

        errs = validate(yaml.safe_load(Path(a.review).read_text()))
        for e in errs:
            print("ERR", e)
        if not errs:
            print(f"ok: {load_review(a.review).schema}")
        return 1 if errs else 0
    if a.cmd in ("snapshot", "diff", "iterations-md", "set-note"):
        from . import iterations as it

        def _j(x: str | None):
            if not x:
                return None
            pth = Path(x)
            return json.loads(pth.read_text() if pth.is_file() else x)

        if a.cmd == "snapshot":
            e = it.snapshot(a.iter_dir, note=a.note, gen_path=a.gen, gds=a.gds, params=_j(a.params),
                            drc=_j(a.drc), lvs=_j(a.lvs), pex=_j(a.pex), scorecard=_j(a.scorecard),
                            area_um2=a.area, keep_gds=not a.no_gds, pdk=a.pdk, detail=a.detail)
            print(json.dumps(e.to_dict()))
        elif a.cmd == "set-note":
            it.set_note(a.iter_dir, a.it, a.note, detail=a.detail)
            print(f"{a.it}: {a.note}")
        elif a.cmd == "diff":
            print(it.diff_png(a.iter_dir, a.before, a.after, a.out, pdk=a.pdk))
        else:
            print(it.iterations_table_md(a.iter_dir, rel_prefix=a.rel_prefix), end="")
        return 0
    if a.cmd == "knobs":
        gen = load_generator(a.generator)
        json.dump(params_schema(gen), sys.stdout, indent=1)
        print()
        return 0
    if a.cmd == "render":
        render_png(a.gds, a.png, pdk=a.pdk)
        print(a.png)
        return 0
    gen = load_generator(a.generator)
    params = params_from_json(gen, a.params)
    sizing = json.loads(Path(a.sizing).read_text()) if a.sizing else None
    out = Path(a.out_dir) / f"{a.cell or gen.name}.gds"
    res = build_gds(gen, params, out, sizing=sizing, cell=a.cell)
    if a.png:
        render_png(res.gds, out.with_suffix(".png"))
    if a.json:
        print(json.dumps(res.to_dict()))
    else:
        print(
            f"wrote {res.gds}  bbox {res.bbox_um}  area {res.area_um2:.1f} um2  sha {res.sha256[:12]}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
