"""``xvport`` — port xschem schematics/symbols to Virtuoso cellviews (and back, later).

Subcommands (forward direction):

* ``xvport sch2cv design.sch --lib MYLIB [--with-symbols] [-o out.il] [--run --verify]``
* ``xvport sym2cv symbol.sym --lib MYLIB [-o out.il] [--run --verify]``
* ``xvport dump-map`` — print the built-in device map YAML as a starting point.

Everything up to ``-o`` is offline; ``--run`` loads the artifact through virtuoso-bridge-lite
(``--port`` for a local daemon, else the bridge's env resolution) and ``--verify`` reads the
built cellview(s) back and diffs them against the emitter's expectation tables.

A sheet's ``code``/``code_shown`` directive block is not a cellview object, so it is never
built as circuitry. It is written verbatim to ``<output stem>.<cell>.directives.txt``, named
in the summary, WARNED about on stderr, and — unless ``--no-directives-note`` — drawn into
the cellview as schematic note labels below the circuit, so a human opening it can read the
measurement setup that did not come across (#250).

After a ``--run``, two independent end-to-end checks execute by default (see
:mod:`.endcheck`): **netcheck** — xschem-netlist the source and Virtuoso-netlist every built
schematic, then prove graph equivalence with circuitgraph; **simcheck** — wrap the top
cellview's netlist in a smoke deck (``--sim-models``/``--sim-section`` or
``XVPORT_SIM_MODELS``/``XVPORT_SIM_SECTION``) and solve a DC op through Spectre. Disable
``--strict-netcheck`` adds model names and declared parameters to netcheck's comparison (for
a same-kit port; a cross-kit topology port changes both on purpose). Disable the checks
with ``--no-netcheck``/``--no-simcheck``; a check that cannot run (missing xschem/bridge/
circuitgraph/model config) reports SKIPPED without failing the port.

The checks are ISOLATED from one another: one that raises prints ``NOT RUN (<reason>)`` on
stderr and fails the run, but never stops the checks after it, and a requested check that
printed no verdict line at all fails the run too — silence must not read as a pass (#240).

Connectivity is ported in ``--mode wires`` by DEFAULT (#267): the drawing's wires are drawn
as wires, so the cellview a human opens looks like the sheet. ``--mode labels`` still ports
placement and connectivity — each terminal gets a labelled stub, and the cellview netlists
correctly — but it draws NO wiring, which every gate here calls equivalent and only a person
opening the cellview can see; it says so once per run on stderr. ``--mode`` applies to every
cellview a call builds, dependencies included.

``--with-symbols`` walks the schematic's unmapped symbol references depth-first and ports
each dependency — the ``.sym`` drawing, and its same-stem ``.sch`` when one sits next to it —
into the target library before the top schematic, so hierarchical designs port in one call.
Each build gets its OWN ``<output stem>.<kind>.<cell>.il`` (children first), because a
``load`` failure names a line number and nothing else: one file per cellview is what makes
the failing build identifiable, and ``--run`` stops at it saying which one it was (#236).
"""

from __future__ import annotations

import argparse
import os
import sys
from functools import partial
from pathlib import Path
from typing import Any

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


def _netcheck(*args: Any, **kwargs: Any) -> Any:
    """:func:`.endcheck.netcheck`, imported at CALL time — an environment that cannot even
    import the oracle then reports ``NOT RUN`` like any other failure, instead of aborting
    the command before the checks that still work (#240)."""
    from .endcheck import netcheck

    return netcheck(*args, **kwargs)


def _simcheck(*args: Any, **kwargs: Any) -> Any:
    """:func:`.endcheck.simcheck`, imported at call time (see :func:`_netcheck`)."""
    from .endcheck import simcheck

    return simcheck(*args, **kwargs)


def _missing_verdicts(requested: set[str], emitted: set[str]) -> list[str]:
    """The requested checks that printed no verdict line at all.

    Silence is not a pass: a caller that records "the netcheck line, if any" cannot tell a
    check that emitted nothing from one that emitted OK, so the run must fail instead (#240).
    """
    return sorted(requested - emitted)


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
    p.add_argument(
        "--map",
        dest="map_file",
        type=Path,
        default=None,
        help="device map YAML — EXTENDS the built-in analogLib rules "
        "(your rules win; see --map-replace)",
    )
    p.add_argument(
        "--map-replace",
        action="store_true",
        help="--map replaces the built-in rules instead of extending them "
        "(the pre-#205 behaviour; drops every analogLib primitive)",
    )
    p.add_argument(
        "--allow-dense",
        action="store_true",
        help="accept a --scale whose instance pitch is under the safe minimum "
        "(masters do not scale: stubs can land on a neighbour's pin)",
    )
    p.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="user units per xschem unit")
    p.add_argument(
        "--mode",
        choices=("labels", "wires"),
        default="wires",
        help="connectivity: drawn wires + pin patching (default: wires — the port "
        "translates the sheet's placement AND its wiring), or net-label stubs. A "
        "`labels` cellview netlists correctly and shows no wires, so it is opt-in",
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
    errors: list[str],
    mode: str = "wires",
    prefix: str = "",
    symbolic: bool = False,
    dense: bool = False,
    directives_note: bool = True,
    allow_collinear: bool = False,
) -> tuple[list[tuple[str, str, object, Path]], Schematic]:
    """Depth-first dependency builds for ``source``: ``(kind, cell, emit-result, source-path)``
    leaves first.

    ``mode`` is the CALL's connectivity mode and reaches every build the walk makes, at every
    depth — a hierarchy ported in one call is ported one way, not `wires` at the top over
    children wired some other way (#267)."""
    sch = parse_sch(source.read_text(encoding="utf-8", errors="replace"))
    symlib = symlib_for_source(source)
    builds: list[tuple[str, str, object, Path]] = []
    for comp in sch.components:
        if not comp.is_device or comp.is_port:
            continue
        sym = symlib.load(comp.symref)
        if sym is None or sym.type == "label" or devmap.lookup(comp.symref, comp.attrs) is not None:
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
                sub_sch,
                devmap,
                scale,
                lib,
                seen,
                warnings,
                errors,
                mode,
                prefix,
                symbolic,
                dense,
                directives_note,
                allow_collinear,
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
                symbolic=symbolic,
                allow_dense=dense,
                allow_collinear=allow_collinear,
                directives_note=directives_note,
            )
            warnings.extend(f"{sub_sch.name}: {w}" for w in sub_result.warnings)
            errors.extend(f"{sub_sch.name}: {e}" for e in sub_result.errors)
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


def _write_directives(builds: list[tuple[str, str, object, Path]], out_path: Path) -> list[Path]:
    """Write each build's directive block beside its ``.il`` and say it was NOT ported.

    A ``code``/``code_shown`` block is not a cellview object (#215), so the port cannot
    build it — but it carries the analyses, the ``include``s and the ``save``s, and dropping
    it in silence is how a ported testbench arrives with the stimulus, the DUT and no
    measurement setup. Neither ``--strict-netcheck`` nor a component round trip can see the
    loss: the directives are absent from both sides of every comparison (#250).
    """
    written: list[Path] = []
    for kind, built_cell, result, _src in builds:
        directives = getattr(result, "directives", None)
        if kind != "sch" or not directives:
            continue
        text = "\n".join(block for _name, block in directives)
        side = out_path.with_name(f"{out_path.stem}.{built_cell}.directives.txt")
        side.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
        written.append(side)
        n = sum(1 for line in text.splitlines() if line.strip())
        blocks = ", ".join(name for name, _block in directives)
        print(f"xvport: wrote {side} ({n} directive line(s) from {blocks})")
        print(
            f"xvport: WARNING {n} directive line(s) not ported as circuit objects "
            f"(code_shown is not a cellview object) — see {side}",
            file=sys.stderr,
        )
    return written


#: Said ONCE per run, whatever a call builds: a `labels` cellview is placement + connectivity
#: with no wiring, and no gate in this tool can see that — netcheck, the read-back and a
#: re-simulation all pass on it. Only a person opening the cellview can (#267).
_LABELS_NO_WIRES = (
    "xvport: WARNING --mode labels ports NO wires: terminals are joined by labelled "
    "stubs; the cellview netlists correctly and shows no wiring"
)


def _cmd_sch2cv(args: argparse.Namespace) -> int:
    devmap = load_device_map(args.map_file, extend=not getattr(args, "map_replace", False))
    if args.mode == "labels":
        print(_LABELS_NO_WIRES, file=sys.stderr)
    cell = args.cell or _cellname(args.source.stem, args.prefix)
    warnings: list[str] = []
    errors: list[str] = []
    builds: list[tuple[str, str, object, Path]] = []
    seen: set[str] = {cell}

    if args.with_symbols:
        builds, sch = _collect_dependencies(
            args.source,
            devmap,
            args.scale,
            args.lib,
            seen,
            warnings,
            errors,
            args.mode,
            args.prefix,
            args.allow_symbolic,
            args.allow_dense,
            getattr(args, "directives_note", True),
            getattr(args, "allow_collinear_labels", False),
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
        symbolic=args.allow_symbolic,
        allow_dense=args.allow_dense,
        allow_collinear=getattr(args, "allow_collinear_labels", False),
        directives_note=getattr(args, "directives_note", True),
    )
    warnings.extend(top.warnings)
    errors.extend(top.errors)
    builds.append(("sch", cell, top, args.source))

    out_path = args.output or args.source.with_suffix(".il")
    # ONE `.il` PER CELLVIEW BUILD. A hierarchy walk used to concatenate every build into
    # `out_path`, and Virtuoso's `load` reports a failure as one line number in the whole
    # file ("error while loading file ... at line 3463") — with 43 builds in it, nothing is
    # loaded and nothing says which cellview broke (#236). Separate files make the failing
    # build its own artifact, and they are loaded children-first, in `builds` order. No
    # combined file is written in that case: nothing downstream reads it (the checks dir is
    # derived from the PATH), and loading it is the failure mode this replaces.
    parts: list[tuple[str, str, Path]] = []
    if len(builds) > 1:
        for kind, built_cell, result, _src in builds:
            part = out_path.with_name(f"{out_path.stem}.{kind}.{built_cell}.il")
            part.write_text(result.il, encoding="utf-8")  # type: ignore[attr-defined]
            parts.append((kind, built_cell, part))
        listed = ", ".join(part.name for _k, _c, part in parts)
        print(
            f"xvport: wrote {len(parts)} per-cellview .il in {out_path.parent} "
            f"(children first): {listed}"
        )
    else:
        out_path.write_text(builds[0][2].il, encoding="utf-8")  # type: ignore[attr-defined]
        kinds = ", ".join(f"{k}:{c}" for k, c, *_ in builds)
        print(f"xvport: wrote {out_path} ({kinds})")
    _write_directives(builds, out_path)
    # Per-cell parameter provenance: what the cellview STATES versus what it would inherit from
    # a CDF default. A caller records this beside the check verdicts instead of a bare IDENTICAL
    # over a size nothing wrote (#241).
    for kind, built_cell, result, _src in builds:
        if kind == "sch":
            assert isinstance(result, EmitResult)
            print(f"xvport: params {args.lib}/{built_cell}: {result.param_summary()}")
    for w in warnings:
        print(f"xvport: WARNING {w}", file=sys.stderr)
    # A port that changed the circuit must not be loaded, however complete the .il looks.
    # The file is still written — it is what localises the problem — but nothing runs.
    for e in errors:
        print(f"xvport: ERROR {e}", file=sys.stderr)
    if errors:
        print(
            f"xvport: {len(errors)} error(s) — nothing loaded. Fix the sheet or the map "
            "(--allow-symbolic accepts non-numeric values verbatim).",
            file=sys.stderr,
        )
        return 2

    if not args.run:
        return 0
    from .runner import connect, load_il, verify_schematic, verify_symbol

    client = connect(host=args.host, port=args.port)
    for kind, built_cell, part in parts or [("sch", cell, out_path)]:
        try:
            load_il(client, part)
        except RuntimeError as exc:
            print(
                f"xvport: ERROR the {kind} build of {args.lib}/{built_cell} failed to load "
                f"({part}): {exc}. Nothing after it was loaded.",
                file=sys.stderr,
            )
            return 2
    print(f"xvport: loaded {len(builds)} cellview build(s) into {args.lib}")

    # Every requested check is an INDEPENDENT oracle and must be run and reported as one:
    # `--verify` raising (the bridge's un-packaged CDF filter used to do exactly that, see
    # doc/bridge_limits.md §8) aborted the command before `--netcheck`, so the check that
    # actually proves the cellview emitted NO LINE and a caller recording "the netcheck line,
    # if any" wrote down silence for a port nothing had checked (#240).
    rc = 0
    requested: set[str] = set()
    emitted: set[str] = set()
    if args.verify:
        requested.add("verify")
    if args.netcheck:
        requested.add("netcheck")
    if args.simcheck:
        requested.add("simcheck")

    def run_check(key: str, label: str, fn: Any, *, verdict_label: str | None = None) -> int:
        """Run one check; whatever it does, the checks after it still run and still report."""
        try:
            report = fn()
        except Exception as exc:  # noqa: BLE001 — an oracle's failure is not the run's
            print(f"xvport: {label}: NOT RUN ({type(exc).__name__}: {exc})", file=sys.stderr)
            emitted.add(key)
            return 2
        print(f"xvport: {verdict_label or label}: {report.summary()}")
        emitted.add(key)
        return 0 if report.ok else 2

    if args.verify:
        for kind, built_cell, result, _src in builds:
            if kind == "sch":
                assert isinstance(result, EmitResult)
                fn = partial(verify_schematic, client, args.lib, built_cell, result)
            else:
                assert isinstance(result, SymbolEmitResult)
                fn = partial(verify_symbol, client, args.lib, built_cell, result)
            failed = run_check(
                "verify",
                f"verify {args.lib}/{built_cell}",
                fn,
                verdict_label=f"{kind} {args.lib}/{built_cell}",
            )
            rc = rc or failed

    # --- end-to-end checks (on by default; independent oracles, see endcheck.py) -----
    check_dir = args.check_dir or out_path.with_suffix(".checks")
    if args.netcheck:
        for kind, built_cell, result, src in builds:
            if kind != "sch":
                continue
            assert isinstance(result, EmitResult)
            failed = run_check(
                "netcheck",
                f"netcheck {args.lib}/{built_cell}",
                partial(
                    _netcheck,
                    client,
                    args.lib,
                    built_cell,
                    src,
                    check_dir / built_cell,
                    strict=args.strict_netcheck,
                    # instances this build dropped: invisible to both netlisters (#226)
                    dropped=result.dropped,
                ),
            )
            rc = rc or failed
    if args.simcheck:
        sim_params = dict(p.split("=", 1) for p in args.sim_param or () if "=" in p)
        failed = run_check(
            "simcheck",
            f"simcheck {args.lib}/{cell}",
            partial(
                _simcheck,
                client,
                args.lib,
                cell,
                top.expected_ports,
                check_dir / cell,
                models=args.sim_models,
                section=args.sim_section,
                env_file=args.sim_env,
                params=sim_params or None,
                netlist_file=check_dir / cell / "cellview" / "input.scs",
            ),
        )
        rc = rc or failed

    # A requested check that printed nothing is indistinguishable from one that passed, for
    # every consumer downstream — so it fails the run instead (#240).
    for missing in _missing_verdicts(requested, emitted):
        print(
            f"xvport: {missing}: NO VERDICT LINE — the check was requested and reported "
            "nothing; treat the port as unchecked",
            file=sys.stderr,
        )
        rc = rc or 2
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
    p.add_argument(
        "--map",
        dest="map_file",
        type=Path,
        default=None,
        help="device map YAML — EXTENDS the built-in analogLib rules "
        "(your rules win; see --map-replace)",
    )
    p.add_argument(
        "--map-replace",
        action="store_true",
        help="--map replaces the built-in rules instead of extending them "
        "(the pre-#205 behaviour; drops every analogLib primitive)",
    )
    p.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="user units per xschem unit")
    p.add_argument("-o", "--output", type=Path, default=None, help="output file path")
    p.add_argument("--host", default="127.0.0.1", help="bridge daemon host (with --port)")
    p.add_argument("--port", type=int, default=None, help="local daemon port (skips SSH env)")


def _cmd_cv2sch(args: argparse.Namespace) -> int:
    devmap = load_device_map(args.map_file, extend=not getattr(args, "map_replace", False))
    from .reverse import XvportNDAError, cv2sch, cv2sch_hierarchy
    from .runner import connect

    client = connect(host=args.host, port=args.port)
    top = f"{args.cell}.sch"
    try:
        if getattr(args, "with_symbols", False):
            files, warnings = cv2sch_hierarchy(
                client, args.lib, args.cell, devmap, scale=args.scale
            )
        else:
            text, warnings = cv2sch(client, args.lib, args.cell, devmap, scale=args.scale)
            files = {top: text}
    except XvportNDAError as exc:
        print(f"xvport: REFUSED — {exc}", file=sys.stderr)
        return 3
    out_path = args.output or Path(top)
    # sub-cell files go in the top sheet's directory: it references them as `{<sub>.sym}`
    paths = {n: out_path if n == top else out_path.parent / n for n in files}
    if any(n != top and p == out_path for n, p in paths.items()):
        print(
            f"xvport: ERROR -o {out_path} is the name of a sub-cell's sheet in this "
            "hierarchy — choose another output name",
            file=sys.stderr,
        )
        return 2
    for name, text in files.items():
        paths[name].write_text(text, encoding="utf-8")
        print(f"xvport: wrote {paths[name]}")
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
    devmap = load_device_map(args.map_file, extend=not getattr(args, "map_replace", False))
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
        "--allow-symbolic",
        action="store_true",
        help="accept parameter and stimulus values that are not numbers (a design variable, "
        "an expression) and write them to the CDF verbatim, as warnings. Off by default: "
        "Cadence turns an unresolved word into a design variable, so the ported device or "
        "source is then sized by whatever that variable holds",
    )
    p_sch.add_argument(
        "--directives-note",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="draw the sheet's code/code_shown directive text into the cellview as "
        "schematic NOTE labels below the circuit (default: on). They are annotation, "
        "never circuit objects — the text is written to <output>.<cell>.directives.txt "
        "and warned about either way",
    )
    p_sch.add_argument(
        "--allow-collinear-labels",
        action="store_true",
        help="accept a --mode labels instance whose stubs still run along one line after "
        "the fan-out (drain, source and bulk on one straight run), as warnings. Off by "
        "default: on the Cadence master those labels can land on one point, one wins, and "
        "the terminals reach the database on an auto-named net that netcheck, the "
        "read-back and a re-simulation all call correct",
    )
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
        "--strict-netcheck",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="make --netcheck also require equal model names and declared parameters "
        "(default: off). Use it for a SAME-KIT port, where a wrong threshold flavour or "
        "an undivided total width is otherwise invisible; leave it off for a cross-kit "
        "topology port, where both change on purpose",
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
    p_cvs.add_argument(
        "--with-symbols",
        action="store_true",
        help="also reverse-port every user cell under it, depth-first: each sub-cell's .sym "
        "and .sch, written beside the output. Masters the device table maps are not "
        "descended into, and a kit_libs master is never dumped",
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
