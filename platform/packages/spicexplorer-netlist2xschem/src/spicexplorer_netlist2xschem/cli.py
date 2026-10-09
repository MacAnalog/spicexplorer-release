"""Command-line entry point: ``netlist2xschem``.

    netlist2xschem INPUT.spice [-o OUT.sch] [--pdk ihp-sg13g2] [--into XINST]
                   [--router per-route|channel] [--report FILE.json|-]
                   [--collapse CELL|GROUP=CELL[,CELL...]] [--cell-symbol CELL=PATH.sym]
                   [--render none|svg|png] [--out-image PATH]

Generates an xschem ``.sch`` from a SPICE netlist; with ``--render`` it also exports an image via
headless xschem (SVG natively, PNG via the ``[render]`` extra). When xschem is unavailable the ``.sch``
is still written (it renders in the SpiceXplorer UI's viewer) and the image step is skipped with a note.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import Any

from .annotate import annotate_sch
from .annotation import BlockAnnotationSet
from .collapse import CollapseGroup, build_collapsed_sch, check_collapsed, parse_collapse
from .emit import build_sch
from .hierarchy import build_hierarchical_sch, write_hierarchy
from .ingest import N2XCircuit, from_file
from .mapping import GENERIC_PDK_TOKENS, foreign_mos_models, vendored_pdks
from .placement import GridPlacer, PhasedPlacer, TopologyPlacer
from .render import render, xschem_available
from .report import collapse_report, sheet_report
from .symbols import analog_icons
from .title_block import TitleBlock, add_title_block, title_block_date

__all__ = ["main"]

#: The placers reachable from the command line. `PhasedPlacer` is the readable default, but it
#: bands by level, and a circuit whose devices all sit on one level lands in ONE row 5300 units
#: wide (measured on a 20-device commercial-kit OTA, issue #159). `TopologyPlacer` was already
#: implemented and simply had no way in — the CLI constructed the default and nothing else.
PLACERS = {
    "phased": PhasedPlacer,
    "topology": TopologyPlacer,
    "grid": GridPlacer,
}


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
        "--pdk",
        default="ihp-sg13g2",
        help="Target PDK for MOSFET symbols (default: ihp-sg13g2). A token with no vendored "
        "symbol library draws xschem's neutral generic symbols, which is the right lane "
        "for a commercial kit; pass `generic` to select that deliberately and quietly.",
    )
    p.add_argument(
        "--allow-foreign-symbols",
        action="store_true",
        help="draw the --pdk's symbols even when the netlist's MOS models are not that kit's",
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
        "--placer",
        choices=sorted(PLACERS),
        default=None,
        help="Device placement strategy: 'phased' (the default, level bands + vertical chains), "
        "'topology' (rows by VDD->VSS rank, symmetric legs straddling the diff pair — the one to "
        "reach for when 'phased' collapses a whole amp into one wide row), or 'grid' (a plain "
        "sorted grid). Independent of --placement, which only says how --annotations blocks "
        "influence whichever placer is chosen. With --collapse the default is a grid whose "
        "pitch clears the largest symbol on each sheet.",
    )
    p.add_argument(
        "--router",
        choices=["per-route", "channel"],
        default="per-route",
        help="How the wires are planned. 'per-route' (the default) draws every sheet as it always "
        "has. 'channel' is a helper for a top level of block symbols: on a sheet of two or more "
        "blocks and no MOSFET it moves the blocks apart until one lane per net fits in each gap "
        "and routes every net and supply in those lanes; any other sheet is still drawn "
        "per-route. Applies to the flat sheet and to every --collapse sheet.",
    )
    p.add_argument(
        "--report",
        metavar="FILE.json",
        help="Also write the measurements of what was drawn as JSON: per sheet the router that "
        "drew it, the nets still carried by name and into how many pieces, parked port pins, "
        "lanes per channel, nets the channel router did not route, and rails/spines/taps/"
        "refused per supply net; with --collapse also each group and the flatten-vs-netlist "
        "check. '-' writes it to standard output (the other messages then go to standard "
        "error). The .sch files are the same with or without it.",
    )
    p.add_argument(
        "--dark",
        action="store_true",
        help="Render on xschem's dark colour scheme. The default is light, because a sheet of "
        "record is read on a white page.",
    )
    p.add_argument(
        "--hierarchical",
        action="store_true",
        help="With --annotations, emit a TRUE xschem hierarchy instead of one flat .sch: each block "
        "becomes a child .sch + generated subcircuit symbol, and the parent .sch instantiates them. "
        "Writes the parent to -o (or <stem>.sch) plus a sibling blocks/ directory.",
    )
    p.add_argument(
        "--icon",
        action="append",
        default=[],
        metavar="SUBCKT=ICON",
        help="With --hierarchical, draw this block with a FUNCTIONAL ICON instead of a plain box: "
        "--icon sar_cmp=comparator (repeatable). SUBCKT matches the emitted cell name, the block "
        "id, the template id or the family; ICON is one of "
        f"{', '.join(analog_icons.icon_names())}, optionally scaled (comparator@1.7) when a small "
        "block has to hold its own beside a many-pin one. The icon changes the symbol's BODY only "
        "— pins, stubs and labels stay byte-identical, so the cell netlists exactly as before.",
    )
    p.add_argument(
        "--no-auto-icons",
        dest="auto_icons",
        action="store_false",
        help="With --hierarchical, do not map a recognised block type to its icon; draw only the "
        "blocks named by --icon. (The automatic mapping is deliberately narrow: a recognised type "
        "that does not map unambiguously to an icon is never guessed at.)",
    )
    p.add_argument(
        "--collapse",
        action="append",
        default=[],
        metavar="CELL|GROUP=CELL[,CELL...]",
        help="Move every instance of CELL one drawing level down, into a new cell (CELL_bank, or "
        "GROUP) whose sheet carries them; the top sheet carries one instance of it (repeatable). "
        "Its ports are computed: a net is a port when the netlist level declares it or anything "
        "outside the group touches it. Writes the group cells beside -o in blocks/, then "
        "flattens the finished sheets through both levels and exits 1 unless the connectivity "
        "is identical to the netlist's.",
    )
    p.add_argument(
        "--cell-symbol",
        action="append",
        default=[],
        metavar="CELL=PATH.sym",
        help="With --collapse, draw every instance of CELL with this .sym (copied to blocks/) "
        "(repeatable). A subcircuit with no symbol is not drawn.",
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
    g = p.add_argument_group(
        "title block",
        "Draw a title block (frame + cell/design/rev/date/author) clear of the drawing, instead of "
        "the loose title text. Its date is an INPUT, so the same sheet renders byte-identically "
        "tomorrow; xschem's own devices/title.sym takes its date from the file's mtime and cannot "
        "(issue #265) — it stays available for anyone who wants it.",
    )
    g.add_argument("--title-block", action="store_true", help="draw the title block")
    g.add_argument("--cell", help="cell/sheet name field (default: the schematic name)")
    g.add_argument("--design", default="", help="design field (e.g. the design repo's name)")
    g.add_argument("--rev", default="", help="revision field (e.g. a tag or short commit)")
    g.add_argument(
        "--date",
        default=None,
        help="date field, verbatim (default: SOURCE_DATE_EPOCH's UTC date if set, else today; "
        "the value used is printed)",
    )
    g.add_argument("--author", default="", help="author field")
    g.add_argument(
        "--title-block-corner",
        choices=["bottom-right", "bottom-left", "top-right", "top-left"],
        default="bottom-right",
        help="which corner of the drawing's extent the block is placed at (default: bottom-right)",
    )
    return p


def _title_block(args: argparse.Namespace, cell: str) -> TitleBlock | None:
    """The :class:`TitleBlock` ``--title-block`` asks for (printing the date used), or ``None``."""
    given = [f"--{n}" for n in ("design", "rev", "date", "author") if getattr(args, n, None)]
    if not args.title_block:
        if given:
            print(
                f"note: {', '.join(given)} ignored — pass --title-block to draw one",
                file=sys.stderr,
            )
        return None
    date = args.date if args.date is not None else title_block_date()
    print(f"title block: cell={args.cell or cell} date={date}")
    return TitleBlock(
        cell=args.cell or cell,
        design=args.design,
        rev=args.rev,
        date=date,
        author=args.author,
        corner=args.title_block_corner,
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    report: dict[str, Any] = {}
    if args.report == "-":
        out = sys.stdout
        with contextlib.redirect_stdout(sys.stderr):
            code = _main(args, report)
        if report:
            out.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
        return code
    code = _main(args, report)
    if args.report and report:
        Path(args.report).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    return code


def _main(args: argparse.Namespace, report: dict[str, Any]) -> int:
    """Everything after argument parsing; the flat and ``--collapse`` lanes fill ``report``."""
    in_path = Path(args.netlist)
    if not in_path.is_file():
        print(f"error: input not found: {in_path}", file=sys.stderr)
        return 2

    # --icon: parse and VALIDATE before anything is generated, so a typo'd icon name is a usage
    # error rather than a sheet that quietly came out as rectangles.
    icons: dict[str, str] = {}
    for entry in args.icon:
        key, sep, spec = entry.partition("=")
        if not sep or not key.strip() or not spec.strip():
            print(f"error: --icon expects SUBCKT=ICON, got {entry!r}", file=sys.stderr)
            return 2
        try:
            analog_icons.parse_spec(spec)
        except ValueError as exc:
            print(f"error: --icon {entry}: {exc}", file=sys.stderr)
            return 2
        icons[key.strip()] = spec.strip()
    if icons and not args.hierarchical:
        # The flat lane draws DEVICES; a block only becomes a symbol in the hierarchy lane. A design
        # that wants an icon on its own cells calls generate_icon_symbol directly (see the README).
        print(
            "error: --icon needs --hierarchical (only that lane draws a block as a symbol). "
            "For your own cells, call symbol_gen.generate_icon_symbol — see the README's "
            '"Functional icons" section.',
            file=sys.stderr,
        )
        return 2

    # --collapse / --cell-symbol: parsed and checked before anything is generated, as --icon is.
    try:
        groups = [parse_collapse(spec) for spec in args.collapse]
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    cell_symbols: dict[str, str] = {}
    for entry in args.cell_symbol:
        cell, sep, sym_path = entry.partition("=")
        if not sep or not cell.strip() or not sym_path.strip():
            print(f"error: --cell-symbol expects CELL=PATH.sym, got {entry!r}", file=sys.stderr)
            return 2
        if not Path(sym_path).is_file():
            print(f"error: --cell-symbol {entry}: no such file", file=sys.stderr)
            return 2
        cell_symbols[cell.strip()] = Path(sym_path).read_text()
    if cell_symbols and not groups:
        print("error: --cell-symbol needs --collapse", file=sys.stderr)
        return 2
    if (args.router != "per-route" or args.report) and (
        args.hierarchical or args.annotate_existing
    ):
        flag = f"--router {args.router}" if args.router != "per-route" else "--report"
        print(
            f"error: {flag} applies to the flat sheet or the --collapse sheets; it does not "
            "combine with --hierarchical or --annotate-existing",
            file=sys.stderr,
        )
        return 2
    if groups and (args.hierarchical or args.annotations or args.annotate_existing):
        print(
            "error: --collapse draws its hierarchy from the cell names; it does not combine "
            "with --hierarchical, --annotations or --annotate-existing",
            file=sys.stderr,
        )
        return 2

    # Annotate-an-existing-.sch: the input IS a schematic; just overlay the blocks on its layout.
    if args.annotate_existing:
        if not args.annotations:
            print(
                "error: --annotate-existing needs --annotations (the blocks to draw)",
                file=sys.stderr,
            )
            return 2
        try:
            annotations = BlockAnnotationSet.load(args.annotations)
        except Exception as exc:  # noqa: BLE001
            print(f"error: failed to read annotations {args.annotations}: {exc}", file=sys.stderr)
            return 1
        annotated, warnings = annotate_sch(in_path.read_text(), annotations)
        out_path = (
            Path(args.out) if args.out else in_path.with_name(f"{in_path.stem}.annotated.sch")
        )
        spec = _title_block(args, in_path.stem)
        if spec is not None:
            annotated = add_title_block(
                annotated,
                cell=spec.cell,
                design=spec.design,
                rev=spec.rev,
                date=spec.date,
                author=spec.author,
                corner=spec.corner,
                replaces_title=spec.cell,
            )
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
        print(
            "error: --hierarchical needs --annotations (the blocks to lift into subcircuits)",
            file=sys.stderr,
        )
        return 2

    # A sheet of record drawn with another foundry's symbols re-netlists correctly and passes
    # a netlist-identity gate — only the DRAWING is wrong, which is the one failure a generated
    # schematic is trusted not to have (#203). The default `--pdk` is a real kit, so omitting
    # the flag on a netlist from any other kit used to produce exactly that, silently.
    foreign = foreign_mos_models(circuit.devices, args.pdk)
    if foreign and not args.allow_foreign_symbols:
        print(
            f"error: --pdk {args.pdk} would draw its own symbols, but this netlist's MOSFETs "
            f"name models it does not have: {', '.join(foreign)}.\n"
            f"       Pass --pdk <your kit token> (any unmapped token draws neutral generic "
            f"symbols with the model on the instance, which is correct for a commercial kit), "
            f"or --allow-foreign-symbols to draw them anyway.",
            file=sys.stderr,
        )
        return 2
    if foreign:
        print(
            f"warning: drawing {args.pdk} symbols over foreign MOS models "
            f"({', '.join(foreign)}) — --allow-foreign-symbols",
            file=sys.stderr,
        )
    token = (args.pdk or "").strip().lower()
    if token not in vendored_pdks() and token not in GENERIC_PDK_TOKENS:
        # The generic fallback is the right behaviour; it just has to announce itself, because
        # a TYPO in a mapped token lands here and is otherwise indistinguishable from a hit.
        print(
            f"note: no vendored symbol library for --pdk {args.pdk}; drawing xschem's generic "
            f"symbols with the model on each instance. Vendored: "
            f"{', '.join(sorted(vendored_pdks()))}. Pass --pdk generic to silence this.",
            file=sys.stderr,
        )

    out_path = Path(args.out) if args.out else in_path.with_suffix(".sch")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if groups:
        return _collapse(args, circuit, groups, cell_symbols, out_path, report)

    # Strategy 1 — emit a true xschem hierarchy (parent .sch + blocks/ children & symbols).
    if args.hierarchical:
        result = build_hierarchical_sch(
            circuit,
            annotations,
            pdk=args.pdk,
            title=circuit.name,
            show_device_params=args.show_device_params,
            icons=icons,
            auto_icons=args.auto_icons,
        )
        write_hierarchy(result, out_path.parent, parent_name=out_path.stem)
        spec = _title_block(args, circuit.name)
        if spec is not None:
            # A post-pass on the parent sheet: `write_hierarchy` places the block symbols, so the
            # drawn extent the block has to keep clear of is only known once the file exists.
            out_path.write_text(
                add_title_block(
                    out_path.read_text(),
                    cell=spec.cell,
                    design=spec.design,
                    rev=spec.rev,
                    date=spec.date,
                    author=spec.author,
                    corner=spec.corner,
                    replaces_title=spec.cell,
                )
            )
        drawn = ", ".join(f"{cell}={icon}" for cell, icon in sorted(result.icons.items()))
        print(
            f"wrote {out_path}  ({result.block_count} block subcircuits + "
            f"{len(result.children)} child .sch in {out_path.parent / 'blocks'}/)"
        )
        # Say which blocks read as a function and which are still rectangles — the whole point of
        # the feature is what the reader sees, and that is not visible in a count of subcircuits.
        print(f"  icons: {drawn}" if drawn else "  icons: none (every block drawn as a plain box)")
        for w in result.warnings:
            print(f"  warning: {w}", file=sys.stderr)
        return _maybe_render(args, out_path)

    # Strategies 2 / P5 — one flat .sch, blocks driving the layout per --placement.
    mode = args.placement or ("block-aware" if args.block_placement else "flat")
    doc = build_sch(
        circuit,
        pdk=args.pdk,
        title=circuit.name,
        title_block=_title_block(args, circuit.name),
        annotations=annotations,
        placement_mode=mode if annotations else None,
        show_device_params=args.show_device_params,
        placer=PLACERS[args.placer or "phased"](),
        router=args.router,
    )
    out_path.write_text(doc.text)
    report.update(router_asked=args.router, sheets={circuit.name: sheet_report(doc)})
    blocks = f", {doc.annotation_count} blocks" if annotations else ""
    # Say how much of the sheet is still joined by NAME — a reader cannot see the difference.
    named = f", {len(doc.nets_by_name)} nets by name" if doc.nets_by_name else ""
    print(
        f"wrote {out_path}  ({doc.device_count} devices, {doc.label_count} labels, "
        f"{doc.wire_count} wires{blocks}{named})"
    )
    for w in doc.warnings:
        print(f"  warning: {w}", file=sys.stderr)

    return _maybe_render(args, out_path)


def _collapse(
    args: argparse.Namespace,
    circuit: N2XCircuit,
    groups: list[CollapseGroup],
    cell_symbols: dict[str, str],
    out_path: Path,
    report: dict[str, Any],
) -> int:
    """``--collapse``: draw, write, then flatten the finished sheets and compare (exit 1 if not equal)."""
    try:
        result = build_collapsed_sch(
            circuit,
            groups,
            pdk=args.pdk,
            cell_symbols=cell_symbols,
            placer=PLACERS[args.placer]() if args.placer else None,
            title=circuit.name,
            title_block=_title_block(args, circuit.name),
            show_device_params=args.show_device_params,
            router=args.router,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    write_hierarchy(result, out_path.parent, parent_name=out_path.stem)
    check = check_collapsed(result, circuit)
    report.update(router_asked=args.router, **collapse_report(result, check))
    print(
        f"wrote {out_path}  (top sheet: {result.device_count} -> {result.parent_instances} "
        f"instances; {result.block_count} group cells in {out_path.parent / 'blocks'}/)"
    )
    for sheet in (circuit.name, *result.groups):
        count = (
            f"{len(result.groups[sheet])} instances, {len(result.block_pins[sheet])} ports"
            if sheet in result.groups
            else f"{result.parent_instances} instances"
        )
        named = result.nets_by_name[sheet]
        print(
            f"  {sheet}: {count}, {result.routers[sheet]} router, {len(named)} nets by name"
            + (f" ({', '.join(named)})" if named else "")
        )
    verdict = "identical to the netlist" if check.identical else "NOT identical to the netlist"
    print(
        f"  flattened through both levels: {check.terminals} terminals on {check.nets} nets, "
        f"{verdict}"
    )
    for w in result.warnings:
        print(f"  warning: {w}", file=sys.stderr)
    if not check.identical:
        for label, items in (
            ("nets split", check.split),
            ("nets merged", check.merged),
            ("terminals missing", check.missing),
            ("terminals extra", check.extra),
            ("instances drawn more than once", check.duplicate),
            ("group ports", check.port_mismatch),
        ):
            if items:
                print(f"  {label}: {', '.join(map(str, items))}", file=sys.stderr)
        return 1
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
    result = render(
        out_path,
        fmt=args.render,
        outdir=outdir,
        pdk=getattr(args, "pdk", None),
        dark=getattr(args, "dark", False),
    )
    if result.image_path is None:
        tail = result.log.strip().splitlines()[-1] if result.log.strip() else "unknown error"
        print(f"note: image not produced ({tail})", file=sys.stderr)
        return 0
    final = result.image_path
    if out_image is not None and result.image_path != out_image:
        # Only adopt the caller's filename when the produced format actually matches it. `render()`
        # falls back to SVG when PNG rasterization is unavailable (cairosvg is an optional extra);
        # renaming those SVG bytes to `…png` hands back a file whose extension lies about its
        # content — image viewers reject it, and the caller is told "rendered <file>.png".
        if result.fmt is not None and out_image.suffix.lower() == f".{result.fmt}":
            result.image_path.replace(out_image)
            final = out_image
        else:
            target = out_image.with_suffix(f".{result.fmt}")
            result.image_path.replace(target)
            final = target
            print(
                f"note: {args.render} was requested but {result.fmt} was produced "
                f"(install the 'render' extra for PNG); wrote {final}, not {out_image}",
                file=sys.stderr,
            )
    print(f"rendered {final}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
