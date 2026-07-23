"""Command-line entry point: ``netlist2xschem``.

    netlist2xschem INPUT.spice [-o OUT.sch] [--pdk ihp-sg13g2] [--into XINST]
                   [--render none|svg|png] [--out-image PATH]

Generates an xschem ``.sch`` from a SPICE netlist; with ``--render`` it also exports an image via
headless xschem (SVG natively, PNG via the ``[render]`` extra). When xschem is unavailable the ``.sch``
is still written (it renders in the SpiceXplorer UI's viewer) and the image step is skipped with a note.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .annotate import annotate_sch
from .annotation import BlockAnnotationSet
from .emit import build_sch
from .hierarchy import build_hierarchical_sch, write_hierarchy
from .ingest import from_file
from .render import render, xschem_available

__all__ = ["main"]


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="netlist2xschem",
        description="Convert a SPICE netlist to an xschem schematic (.sch), optionally rendering an image.",
    )
    p.add_argument("netlist", help="Input SPICE netlist (.spice/.cir/.net/.sp)")
    p.add_argument(
        "-o", "--out", help="Output .sch path (default: <netlist stem>.sch beside the input)"
    )
    p.add_argument(
        "--pdk", default="ihp-sg13g2", help="Target PDK for MOSFET symbols (default: ihp-sg13g2)"
    )
    p.add_argument("--into", help="Descend into this subckt *instance* before generating")
    p.add_argument("--name", help="Schematic name / title (default: the netlist stem)")
    p.add_argument(
        "--annotations",
        help="JSON file of recognised functional blocks (spicexplorer/xschem-block-annotations@1) "
        "to outline as labelled boxes over the placement (e.g. from circuitgraph)",
    )
    p.add_argument(
        "--no-block-placement",
        dest="block_placement",
        action="store_false",
        help="With --annotations, draw the boxes over the default (block-agnostic) layout instead of "
        "clustering each block's devices into its own region (block-aware placement is on by default)",
    )
    p.add_argument(
        "--placement",
        choices=["block-aware", "template-stamp", "flat"],
        default=None,
        help="With --annotations, how blocks drive the flat layout: 'block-aware' (P5, default), "
        "'template-stamp' (lay each block at its hand-drawn symmetric template geometry), or 'flat' "
        "(block-agnostic). Supersedes --no-block-placement when given.",
    )
    p.add_argument(
        "--hierarchical",
        action="store_true",
        help="With --annotations, emit a TRUE xschem hierarchy instead of one flat .sch: each block "
        "becomes a child .sch + generated subcircuit symbol, and the parent .sch instantiates them. "
        "Writes the parent to -o (or <stem>.sch) plus a sibling blocks/ directory.",
    )
    p.add_argument(
        "--annotate-existing",
        action="store_true",
        help="Treat the INPUT as an existing xschem .sch (not a netlist) and just overlay the "
        "--annotations boxes on its current layout, moving nothing. Writes the annotated .sch to -o.",
    )
    p.add_argument(
        "--show-params",
        dest="show_device_params",
        action="store_true",
        help="Draw each device's parameter text (model, w/l, value). Off by default — the schematic "
        "uses clean 'no-params' symbols (the runnable values are still carried for netlisting).",
    )
    p.add_argument(
        "--render",
        choices=["none", "svg", "png"],
        default="none",
        help="Also render an image via headless xschem (default: none)",
    )
    p.add_argument("--out-image", help="Output image path (default: alongside the .sch)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    in_path = Path(args.netlist)
    if not in_path.is_file():
        print(f"error: input not found: {in_path}", file=sys.stderr)
        return 2

    # Annotate-an-existing-.sch: the input IS a schematic; just overlay the blocks on its layout.
    if args.annotate_existing:
        if not args.annotations:
            print("error: --annotate-existing needs --annotations (the blocks to draw)", file=sys.stderr)
            return 2
        try:
            annotations = BlockAnnotationSet.load(args.annotations)
        except Exception as exc:  # noqa: BLE001
            print(f"error: failed to read annotations {args.annotations}: {exc}", file=sys.stderr)
            return 1
        annotated, warnings = annotate_sch(in_path.read_text(), annotations)
        out_path = Path(args.out) if args.out else in_path.with_name(f"{in_path.stem}.annotated.sch")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(annotated)
        n_boxes = sum(1 for ln in annotated.splitlines() if ln.startswith("B "))
        print(f"wrote {out_path}  (overlaid {n_boxes} block boxes on the existing layout)")
        for w in warnings:
            print(f"  warning: {w}", file=sys.stderr)
        return _maybe_render(args, out_path)

    try:
        circuit = from_file(in_path, name=args.name, into=args.into)
    except Exception as exc:  # noqa: BLE001 — surface a clean CLI error
        print(f"error: failed to parse {in_path}: {exc}", file=sys.stderr)
        return 1

    annotations = None
    if args.annotations:
        try:
            annotations = BlockAnnotationSet.load(args.annotations)
        except Exception as exc:  # noqa: BLE001 — surface a clean CLI error
            print(f"error: failed to read annotations {args.annotations}: {exc}", file=sys.stderr)
            return 1

    if args.hierarchical and not annotations:
        print("error: --hierarchical needs --annotations (the blocks to lift into subcircuits)", file=sys.stderr)
        return 2

    out_path = Path(args.out) if args.out else in_path.with_suffix(".sch")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Strategy 1 — emit a true xschem hierarchy (parent .sch + blocks/ children & symbols).
    if args.hierarchical:
        result = build_hierarchical_sch(
            circuit, annotations, pdk=args.pdk, title=circuit.name,
            show_device_params=args.show_device_params,
        )
        write_hierarchy(result, out_path.parent, parent_name=out_path.stem)
        print(
            f"wrote {out_path}  ({result.block_count} block subcircuits + "
            f"{len(result.children)} child .sch in {out_path.parent / 'blocks'}/)"
        )
        for w in result.warnings:
            print(f"  warning: {w}", file=sys.stderr)
        return _maybe_render(args, out_path)

    # Strategies 2 / P5 — one flat .sch, blocks driving the layout per --placement.
    mode = args.placement or ("block-aware" if args.block_placement else "flat")
    doc = build_sch(
        circuit,
        pdk=args.pdk,
        title=circuit.name,
        annotations=annotations,
        placement_mode=mode if annotations else None,
        show_device_params=args.show_device_params,
    )
    out_path.write_text(doc.text)
    blocks = f", {doc.annotation_count} blocks" if annotations else ""
    print(f"wrote {out_path}  ({doc.device_count} devices, {doc.label_count} labels{blocks})")
    for w in doc.warnings:
        print(f"  warning: {w}", file=sys.stderr)

    return _maybe_render(args, out_path)


def _maybe_render(args: argparse.Namespace, out_path: Path) -> int:
    """Render the (parent) ``.sch`` to an image when ``--render`` was requested; always returns 0."""
    if args.render == "none":
        return 0
    if not xschem_available():
        print(
            "note: xschem not on PATH — skipped image render; the .sch renders in the UI viewer.",
            file=sys.stderr,
        )
        return 0
    out_image = Path(args.out_image) if args.out_image else None
    outdir = out_image.parent if out_image else out_path.parent
    result = render(out_path, fmt=args.render, outdir=outdir)
    if result.image_path is None:
        tail = result.log.strip().splitlines()[-1] if result.log.strip() else "unknown error"
        print(f"note: image not produced ({tail})", file=sys.stderr)
        return 0
    final = result.image_path
    if out_image is not None and result.image_path != out_image:
        result.image_path.replace(out_image)
        final = out_image
    print(f"rendered {final}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
