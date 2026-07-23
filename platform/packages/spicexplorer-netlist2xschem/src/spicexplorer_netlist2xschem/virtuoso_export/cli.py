"""``xvport`` — port xschem schematics/symbols to Virtuoso cellviews (and back, later).

Subcommands (forward direction):

* ``xvport sch2cv design.sch --lib MYLIB [--with-symbols] [-o out.il] [--run --verify]``
* ``xvport sym2cv symbol.sym --lib MYLIB [-o out.il] [--run --verify]``
* ``xvport dump-map`` — print the built-in device map YAML as a starting point.

Everything up to ``-o`` is offline; ``--run`` loads the artifact through virtuoso-bridge-lite
(``--port`` for a local daemon, else the bridge's env resolution) and ``--verify`` reads the
built cellview(s) back and diffs them against the emitter's expectation tables.

After a ``--run``, two independent end-to-end checks execute by default (see
:mod:`.endcheck`): **netcheck** — xschem-netlist the source and Virtuoso-netlist every built
schematic, then prove graph equivalence with circuitgraph; **simcheck** — wrap the top
cellview's netlist in a smoke deck (``--sim-models``/``--sim-section`` or
``XVPORT_SIM_MODELS``/``XVPORT_SIM_SECTION``) and solve a DC op through Spectre. Disable
with ``--no-netcheck``/``--no-simcheck``; a check that cannot run (missing xschem/bridge/
circuitgraph/model config) reports SKIPPED without failing the port.

``--with-symbols`` walks the schematic's unmapped symbol references depth-first and ports
each dependency — the ``.sym`` drawing, and its same-stem ``.sch`` when one sits next to it —
into the target library before the top schematic, so hierarchical designs port in one call.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from ..sch_parser import Schematic, parse_sch
from .devmap import DEFAULT_MAP_YAML, DeviceMap, load_device_map
from .emit_il import EmitResult, emit_schematic_il
from .symbols import SymbolEmitResult, emit_symbol_il_from_text
from .symlib import symlib_for_source
from .xform import DEFAULT_SCALE

__all__ = ["main"]


def _cellname(stem: str, prefix: str = "") -> str:
    from .emit_il import _sanitize

    return _sanitize(f"{prefix}{stem}", prefix="cell")


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("source", type=Path, help="the xschem source file")
    p.add_argument("--lib", required=True, help="target Virtuoso library")
    p.add_argument("--cell", default=None, help="target cell name (default: source stem)")
    p.add_argument(
        "--prefix",
        default="",
        help="prefix for every locally-created cell name (escape hatch when an xschem "
        "basename collides with a kit cell)",
    )
    p.add_argument("--map", dest="map_file", type=Path, default=None, help="device map YAML")
    p.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="user units per xschem unit")
    p.add_argument(
        "--mode",
        choices=("labels", "wires"),
        default="labels",
        help="connectivity: net-label stubs (default) or drawn wires + pin patching",
    )
    p.add_argument("-o", "--output", type=Path, default=None, help=".il output path")
    p.add_argument("--run", action="store_true", help="load the emitted .il via the bridge")
    p.add_argument("--verify", action="store_true", help="after --run, read back and diff")
    p.add_argument("--host", default="127.0.0.1", help="bridge daemon host (with --port)")
    p.add_argument("--port", type=int, default=None, help="local daemon port (skips SSH env)")


def _collect_dependencies(
    source: Path,
    devmap: DeviceMap,
    scale: float,
    lib: str,
    seen: set[str],
    warnings: list[str],
    mode: str = "labels",
    prefix: str = "",
) -> tuple[list[tuple[str, str, object, Path]], Schematic]:
    """Depth-first dependency builds for ``source``: ``(kind, cell, emit-result, source-path)``
    leaves first."""
    sch = parse_sch(source.read_text(encoding="utf-8", errors="replace"))
    symlib = symlib_for_source(source)
    builds: list[tuple[str, str, object, Path]] = []
    for comp in sch.components:
        if not comp.is_device or comp.is_port:
            continue
        sym = symlib.load(comp.symref)
        if sym is None or sym.type == "label" or devmap.lookup(comp.symref) is not None:
            continue
        sym_path = symlib.resolve(comp.symref)
        if sym_path is None:
            continue
        cell = _cellname(sym_path.stem, prefix)
        if cell in seen:
            continue
        seen.add(cell)
        sub_sch = sym_path.with_suffix(".sch")
        if sub_sch.is_file():
            deeper, sub = _collect_dependencies(
                sub_sch, devmap, scale, lib, seen, warnings, mode, prefix
            )
            builds.extend(deeper)
            sub_result = emit_schematic_il(
                sub,
                lib=lib,
                cell=cell,
                devmap=devmap,
                symlib=symlib_for_source(sub_sch),
                scale=scale,
                source_name=sub_sch.name,
                local_cells=seen,
                mode=mode,
                local_prefix=prefix,
            )
            warnings.extend(f"{sub_sch.name}: {w}" for w in sub_result.warnings)
            builds.append(("sch", cell, sub_result, sub_sch))
        sym_result = emit_symbol_il_from_text(
            sym_path.read_text(encoding="utf-8", errors="replace"),
            lib=lib,
            cell=cell,
            scale=scale,
            source_name=sym_path.name,
        )
        warnings.extend(f"{sym_path.name}: {w}" for w in sym_result.warnings)
        builds.append(("sym", cell, sym_result, sym_path))
    return builds, sch


def _cmd_sch2cv(args: argparse.Namespace) -> int:
    devmap = load_device_map(args.map_file)
    cell = args.cell or _cellname(args.source.stem, args.prefix)
    warnings: list[str] = []
    builds: list[tuple[str, str, object, Path]] = []
    seen: set[str] = {cell}

    if args.with_symbols:
        builds, sch = _collect_dependencies(
            args.source, devmap, args.scale, args.lib, seen, warnings, args.mode, args.prefix
        )
    else:
        sch = parse_sch(args.source.read_text(encoding="utf-8", errors="replace"))

    top = emit_schematic_il(
        sch,
        lib=args.lib,
        cell=cell,
        devmap=devmap,
        symlib=symlib_for_source(args.source),
        scale=args.scale,
        source_name=args.source.name,
        local_cells=seen if args.with_symbols else None,
        mode=args.mode,
        local_prefix=args.prefix,
    )
    warnings.extend(top.warnings)
    builds.append(("sch", cell, top, args.source))

    out_path = args.output or args.source.with_suffix(".il")
    out_path.write_text("".join(b[2].il for b in builds), encoding="utf-8")  # type: ignore[attr-defined]
    kinds = ", ".join(f"{k}:{c}" for k, c, *_ in builds)
    print(f"xvport: wrote {out_path} ({kinds})")
    for w in warnings:
        print(f"xvport: WARNING {w}", file=sys.stderr)

    if not args.run:
        return 0
    from .runner import connect, load_il, verify_schematic, verify_symbol

    client = connect(host=args.host, port=args.port)
    load_il(client, out_path)
    print(f"xvport: loaded {len(builds)} cellview build(s) into {args.lib}")
    rc = 0
    if args.verify:
        for kind, built_cell, result, _src in builds:
            if kind == "sch":
                assert isinstance(result, EmitResult)
                report = verify_schematic(client, args.lib, built_cell, result)
            else:
                assert isinstance(result, SymbolEmitResult)
                report = verify_symbol(client, args.lib, built_cell, result)
            print(f"xvport: {kind} {args.lib}/{built_cell}: {report.summary()}")
            rc = rc or (0 if report.ok else 2)

    # --- end-to-end checks (on by default; independent oracles, see endcheck.py) -----
    if not (args.netcheck or args.simcheck):
        return rc
    from .endcheck import netcheck, simcheck

    check_dir = args.check_dir or out_path.with_suffix(".checks")
    if args.netcheck:
        for kind, built_cell, _result, src in builds:
            if kind != "sch":
                continue
            report_n = netcheck(client, args.lib, built_cell, src, check_dir / built_cell)
            print(f"xvport: netcheck {args.lib}/{built_cell}: {report_n.summary()}")
            rc = rc or (0 if report_n.ok else 2)
    if args.simcheck:
        cv_netlist = check_dir / cell / "cellview" / "input.scs"
        sim_params = dict(p.split("=", 1) for p in args.sim_param or () if "=" in p)
        report_s = simcheck(
            client,
            args.lib,
            cell,
            top.expected_ports,
            check_dir / cell,
            models=args.sim_models,
            section=args.sim_section,
            env_file=args.sim_env,
            params=sim_params or None,
            netlist_file=cv_netlist,
        )
        print(f"xvport: simcheck {args.lib}/{cell}: {report_s.summary()}")
        rc = rc or (0 if report_s.ok else 2)
    return rc


def _cmd_sym2cv(args: argparse.Namespace) -> int:
    text = args.source.read_text(encoding="utf-8", errors="replace")
    cell = args.cell or _cellname(args.source.stem, args.prefix)
    result = emit_symbol_il_from_text(
        text, lib=args.lib, cell=cell, scale=args.scale, source_name=args.source.name
    )
    out_path = args.output or args.source.with_suffix(".il")
    out_path.write_text(result.il, encoding="utf-8")
    print(f"xvport: wrote {out_path} ({len(result.terms)} terminals)")
    for w in result.warnings:
        print(f"xvport: WARNING {w}", file=sys.stderr)

    if not args.run:
        return 0
    from .runner import connect, load_il, verify_symbol

    client = connect(host=args.host, port=args.port)
    load_il(client, out_path)
    print(f"xvport: loaded into {args.lib}/{cell}")
    if args.verify:
        report = verify_symbol(client, args.lib, cell, result)
        print(f"xvport: {report.summary()}")
        return 0 if report.ok else 2
    return 0


def _cmd_dump_map(_args: argparse.Namespace) -> int:
    print(DEFAULT_MAP_YAML, end="")
    return 0


def _add_reverse_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("lib", help="Virtuoso library of the cellview to reverse-port")
    p.add_argument("cell", help="cell name to reverse-port")
    p.add_argument("--map", dest="map_file", type=Path, default=None, help="device map YAML")
    p.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="user units per xschem unit")
    p.add_argument("-o", "--output", type=Path, default=None, help="output file path")
    p.add_argument("--host", default="127.0.0.1", help="bridge daemon host (with --port)")
    p.add_argument("--port", type=int, default=None, help="local daemon port (skips SSH env)")


def _cmd_cv2sch(args: argparse.Namespace) -> int:
    devmap = load_device_map(args.map_file)
    from .reverse import XvportNDAError, cv2sch
    from .runner import connect

    client = connect(host=args.host, port=args.port)
    try:
        text, warnings = cv2sch(client, args.lib, args.cell, devmap, scale=args.scale)
    except XvportNDAError as exc:
        print(f"xvport: REFUSED — {exc}", file=sys.stderr)
        return 3
    out_path = args.output or Path(f"{args.cell}.sch")
    out_path.write_text(text, encoding="utf-8")
    print(f"xvport: wrote {out_path}")
    for w in warnings:
        print(f"xvport: WARNING {w}", file=sys.stderr)
    if not args.verify:
        return 0
    # reverse verify: xschem-netlist the EMITTED .sch and prove graph equivalence against
    # Virtuoso's own netlist of the source cellview (the same oracles as --netcheck).
    from .endcheck import (
        CheckUnavailable,
        fetch_cellview_netlist,
        netlists_graph_equivalent,
        xschem_source_netlist,
    )

    check_dir = out_path.parent / f"{out_path.stem}.rev-checks"
    try:
        src_net = xschem_source_netlist(out_path, check_dir / "sch")
        cv_net = fetch_cellview_netlist(client, args.lib, args.cell, check_dir / "cellview")
        cmp = netlists_graph_equivalent(src_net, cv_net)
    except CheckUnavailable as exc:
        print(f"xvport: reverse verify SKIPPED — {exc}")
        return 0
    state = "OK" if cmp.equivalent else "FAILED"
    print(f"xvport: reverse verify {state}: {cmp.reason}")
    return 0 if cmp.equivalent else 2


def _cmd_cv2sym(args: argparse.Namespace) -> int:
    devmap = load_device_map(args.map_file)
    from .reverse import XvportNDAError, cv2sym
    from .runner import connect

    client = connect(host=args.host, port=args.port)
    try:
        text, warnings = cv2sym(client, args.lib, args.cell, devmap, scale=args.scale)
    except XvportNDAError as exc:
        print(f"xvport: REFUSED — {exc}", file=sys.stderr)
        return 3
    out_path = args.output or Path(f"{args.cell}.sym")
    out_path.write_text(text, encoding="utf-8")
    print(f"xvport: wrote {out_path}")
    for w in warnings:
        print(f"xvport: WARNING {w}", file=sys.stderr)
    if args.verify:
        # light self-check: the emitted .sym must carry pin boxes; geometric fidelity is
        # the round-trip's job (re-port it forward with sym2cv)
        pins = text.count("B 5 ")
        print(f"xvport: emitted .sym has {pins} pin boxes")
        return 0 if pins > 0 else 2
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xvport", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_sch = sub.add_parser("sch2cv", help="port an xschem .sch to a Virtuoso schematic")
    _add_common(p_sch)
    p_sch.add_argument(
        "--with-symbols",
        action="store_true",
        help="also port unmapped .sym dependencies (and their .sch) depth-first",
    )
    p_sch.add_argument(
        "--netcheck",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="after --run: xschem-netlist the source + Virtuoso-netlist each built "
        "schematic and prove circuitgraph graph equivalence (default: on)",
    )
    p_sch.add_argument(
        "--simcheck",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="after --run: solve a DC op of the top cellview's netlist through Spectre "
        "with --sim-models/--sim-section (default: on; SKIPs when unconfigured)",
    )
    p_sch.add_argument(
        "--sim-models",
        default=os.environ.get("XVPORT_SIM_MODELS"),
        help="model file for --simcheck (default: $XVPORT_SIM_MODELS); a PATH handed "
        "to Spectre — never committed, never read",
    )
    p_sch.add_argument(
        "--sim-section",
        default=os.environ.get("XVPORT_SIM_SECTION"),
        help="model-file section for --simcheck (default: $XVPORT_SIM_SECTION)",
    )
    p_sch.add_argument(
        "--sim-env",
        default=os.environ.get("XVPORT_VB_ENV") or os.environ.get("SPICEXPLORER_VB_ENV_FILE"),
        help="bridge env file pinning the Spectre profile for --simcheck (default: "
        "$XVPORT_VB_ENV, else $SPICEXPLORER_VB_ENV_FILE, else bridge discovery — "
        "which can silently pick a remote-SSH profile)",
    )
    p_sch.add_argument(
        "--sim-param",
        action="append",
        default=None,
        metavar="NAME=VALUE",
        help="value for a symbolic drawing parameter in --simcheck (repeatable); lands "
        "as a spectre `parameters` line in the smoke deck",
    )
    p_sch.add_argument(
        "--check-dir",
        type=Path,
        default=None,
        help="artifact dir for the checks (default: <output>.checks/)",
    )
    p_sch.set_defaults(func=_cmd_sch2cv)

    p_sym = sub.add_parser("sym2cv", help="port an xschem .sym to a Virtuoso symbol view")
    _add_common(p_sym)
    p_sym.set_defaults(func=_cmd_sym2cv)

    p_map = sub.add_parser("dump-map", help="print the built-in device map YAML")
    p_map.set_defaults(func=_cmd_dump_map)

    p_cvs = sub.add_parser("cv2sch", help="reverse-port a Virtuoso schematic to xschem .sch")
    _add_reverse_common(p_cvs)
    p_cvs.add_argument(
        "--verify",
        action="store_true",
        help="xschem-netlist the emitted .sch and prove circuitgraph graph equivalence "
        "against Virtuoso's own netlist of the cellview",
    )
    p_cvs.set_defaults(func=_cmd_cv2sch)

    p_cvy = sub.add_parser("cv2sym", help="reverse-port a Virtuoso symbol to xschem .sym")
    _add_reverse_common(p_cvy)
    p_cvy.add_argument(
        "--verify", action="store_true", help="light structural self-check of the .sym"
    )
    p_cvy.set_defaults(func=_cmd_cv2sym)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
