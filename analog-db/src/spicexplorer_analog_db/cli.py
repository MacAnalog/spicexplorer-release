"""``analog-db`` CLI — the verification + generation entry point (plan §6).

analog-db verify      [--tier N ...] [--circuit ID] [--pdk PDK] [--json]
analog-db generate    [--circuit ID] [--all]
analog-db gen-params  (--circuit ID | --all) [--write]
analog-db export-raw  [--circuit ID] [--pdk PDK] [--corner tt[,ss,…]] [--check] [--svg]
analog-db catalog     [--write]
analog-db run         --circuit ID --pdk PDK [--corner tt] [--docker [SERVICE]] [--write]
analog-db add-binding --circuit ID --pdk PDK [--from PDK]
analog-db gmid-extract --pdk PDK [--device DEV] [--corner tt|tt,ss,ff|all] [--vgs a,s,b] [--length l1,l2,…]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import catalog, generate, model, paths, verify


def _cmd_verify(args: argparse.Namespace) -> int:
    if not paths.db_present():
        print(
            f"analog-db: no database at {paths.db_root()} (set ${paths.ENV_VAR}?)", file=sys.stderr
        )
        return 2
    ids = [args.circuit] if args.circuit else None
    tiers = args.tier or None
    results = verify.run(tiers=tiers, circuit_ids=ids, sim=getattr(args, "sim", False))
    if args.pdk:
        results = [r for r in results if args.pdk in r.check or not r.circuit]

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        for r in results:
            mark = {"pass": "PASS", "fail": "FAIL", "skip": "skip"}[r.status]
            who = r.circuit or "(db)"
            line = f"  [{mark}] T{r.tier} {who} :: {r.check}"
            if r.reason:
                line += f"  — {r.reason}"
            print(line)
        s = verify.summarize(results)
        print(f"\n{s['pass']} passed, {s['fail']} failed, {s['skip']} skipped")
        for cid in ids or model.list_circuit_ids():
            print(f"  status[{cid}] = {verify.derive_status(cid, results)}")

    return 1 if verify.summarize(results)["fail"] else 0


def _cmd_generate(args: argparse.Namespace) -> int:
    ids = [args.circuit] if args.circuit else model.list_circuit_ids()
    for cid in ids:
        written = generate.write_generated(model.load_circuit(cid))
        for w in written:
            print(f"  wrote {cid}/{w}")
    if args.all:
        # the full-regen umbrella: netlists (above) → raw/ decks → catalog.json → scoreboard.json,
        # in dependency order.
        from . import export, scoreboard

        scope = [args.circuit] if args.circuit else None
        decks, skipped = export.write_all(scope)
        print(f"  exported {len(decks)} raw decks ({len(skipped)} skipped)")
        paths.catalog_path().write_text(catalog.catalog_json())
        print(f"  wrote {paths.catalog_path()}")
        scoreboard.index_path().write_text(scoreboard.index_json())
        print(f"  wrote {scoreboard.index_path()}")
    return 0


def _cmd_gen_params(args: argparse.Namespace) -> int:
    """``gen-params``: generate / refresh ``abstract/params.yaml`` (plan_parameterization P1).

    Generated-then-reviewed semantics: a fresh circuit gets the full structural proposal
    (inventory + detected groups/ratios); a circuit that already adopted the layer gets its
    ``devices:`` refreshed mechanically while the AUTHORED ``groups:``/``ratios:`` are preserved
    verbatim. Detected-but-untied symmetries are always reported (warnings, plan D-6). Without
    ``--write`` the proposal/diff goes to stdout; nothing is written."""
    import difflib

    from . import params as par

    if not args.circuit and not args.all:
        print("analog-db: gen-params needs --circuit ID or --all", file=sys.stderr)
        return 2
    ids = [args.circuit] if args.circuit else model.list_circuit_ids()
    rc = 0
    for cid in ids:
        c = model.load_circuit(cid)
        if c.is_reference_only:
            print(f"  skip  {cid} — kind: reference (no sizing contract, plan D-9)")
            continue
        cg = c.dir / "abstract" / "topology.cgraph.json"
        if not cg.is_file():
            print(
                f"  skip  {cid} — no topology.cgraph.json (run `analog-db generate --circuit {cid}`)",
                file=sys.stderr,
            )
            rc = 1
            continue
        graph = par.load_graph(cg)
        existing = par.load_params_doc(c.dir)
        if existing is None:
            doc = par.propose_params_doc(graph)
            action = "proposed (structural detection — review before committing)"
        else:
            doc = par.refresh_params_doc(existing, graph)
            action = "refreshed (devices: regenerated; authored groups:/ratios: preserved)"
        cls = par.classify_symbols(doc)  # PDK-neutral view: freeze flags live in sizing.yaml
        print(f"        {par.counts_line(cls)}")
        text = par.render_params_yaml(doc, cid)
        target = c.dir / "abstract" / "params.yaml"
        if args.write:
            target.write_text(text)
            print(f"  wrote {cid}/abstract/params.yaml — {action}")
        else:
            committed = target.read_text() if target.is_file() else ""
            if committed == text:
                print(f"  ok    {cid} — abstract/params.yaml up to date")
            else:
                sys.stdout.writelines(
                    difflib.unified_diff(
                        committed.splitlines(keepends=True),
                        text.splitlines(keepends=True),
                        fromfile=f"{cid}/abstract/params.yaml (committed)",
                        tofile=f"{cid}/abstract/params.yaml ({action})",
                    )
                )
        for u in par.untied_symmetries(graph, doc):
            print(f"  WARN  {cid}: detected-but-untied symmetry: {u} (warning, never a gate — plan D-6)")
    return rc


def _cmd_export_raw(args: argparse.Namespace) -> int:
    from . import export

    corners = tuple(c.strip() for c in args.corner.split(",") if c.strip())
    scope = [args.circuit] if args.circuit else None
    pdks = [args.pdk] if args.pdk else None

    if args.check:
        stale, missing, orphan = export.check_drift(scope, corners)
        for p in missing:
            print(f"  MISSING {p}")
        for p in stale:
            print(f"  STALE   {p}")
        for p in orphan:
            print(f"  ORPHAN  {p}")
        n = len(stale) + len(missing) + len(orphan)
        if n:
            print(f"\n{n} drift(s); run `analog-db export-raw` to refresh", file=sys.stderr)
            return 1
        print(f"  raw/ in sync ({len(export.generate_all(scope, corners)[0])} decks)")
        return 0

    written, skipped = export.write_all(scope, corners, pdks)
    for w in written:
        print(f"  wrote {w}")
    for cell, reason in skipped:
        print(f"  skip  {cell} — {reason}")
    print(f"\n{len(written)} decks written, {len(skipped)} skipped")
    if args.svg:
        rendered, available = export.render_svgs(scope)
        for r in rendered:
            print(f"  rendered {r}")
        if not available:
            print("  (xschem unavailable — .svg render skipped; run in the base image / container)")
        else:
            print(f"  {len(rendered)} .svg rendered")
    return 0


def _cmd_export_raw_project(args: argparse.Namespace) -> int:
    from . import raw_project

    out_dir = Path(args.out) if args.out else paths.db_root() / "raw_optimize" / "generated"
    ids = [args.circuit] if args.circuit else list(model.list_circuit_ids())
    written: list[Path] = []
    skipped: list[tuple[str, str]] = []
    for cid in ids:
        try:
            p = raw_project.write(cid, args.pdk, out_dir)
            written.append(p)
            print(f"  wrote {p.relative_to(paths.db_root())}")
        except Exception as exc:  # a circuit with no whitelisted metric / no binding → skip
            skipped.append((cid, f"{type(exc).__name__}: {exc}"))
            if args.circuit:  # explicit single-circuit request → surface the reason
                print(f"  skip  {cid} — {exc}", file=sys.stderr)
    print(f"\n{len(written)} project(s) written, {len(skipped)} skipped")
    return 0 if written or not args.circuit else 1


def _cmd_run(args: argparse.Namespace) -> int:
    from . import runner as runmod

    circuit = model.load_circuit(args.circuit)
    if args.docker_image:
        runner = runmod.base_image_runner(args.docker_image)
    elif args.docker:
        runner = runmod.docker_runner(args.docker)
    elif runmod.native_pdk_available(args.pdk):
        # per-PDK .spiceinit (sourcepath + OSDI) + native deck-prep (slim-swap, absolute includes) —
        # the multi-PDK native path (local_runner only resolves whatever $SPICE_USERINIT_DIR points at)
        runner = runmod.native_pdk_runner(args.pdk)
    else:
        runner = runmod.local_runner
    results = runmod.run_circuit(circuit, args.pdk, args.corner, runner)
    ok = all(a.get("status") in ("ok", "disabled") for a in results["analyses"].values())
    if args.crosscheck:
        from .symbolic import crosscheck

        report = crosscheck(circuit, args.pdk, args.corner, results["analyses"], runner)
        results["symbolic_crosscheck"] = report
        ok = ok and all(m.get("agrees", True) for m in report["metrics"].values())
    if args.write:
        path = runmod.write_results(circuit, results)
        print(f"  wrote {path}")
    else:
        print(json.dumps(results, indent=2, sort_keys=True))
    return 0 if ok else 1


def _cmd_import_analoggym(args: argparse.Namespace) -> int:
    from pathlib import Path

    from .importers import analoggym

    src = Path(args.src).expanduser().resolve()
    dest = paths.circuits_root()
    if args.circuit:
        cdir = analoggym.import_circuit(src, args.circuit, dest)
        print(f"  imported {cdir.name}")
        return 0
    imported, skipped = analoggym.import_all(src, dest)
    for cid in imported:
        print(f"  imported {cid}")
    for s in skipped:
        print(f"  SKIPPED {s}")
    print(f"\n{len(imported)} imported, {len(skipped)} skipped")
    return 0


def _cmd_import_ferrosim(args: argparse.Namespace) -> int:
    from pathlib import Path

    from .importers import ferrosim

    src = Path(args.src).expanduser().resolve()
    dest = paths.circuits_root()
    imported, skipped = ferrosim.import_all(src, dest)
    for cid in imported:
        print(f"  imported {cid}")
    for s in skipped:
        print(f"  SKIPPED {s}")
    # register the new circuits in the manifest (catalog.json) unless asked to skip it.
    if imported and not args.no_catalog:
        paths.catalog_path().write_text(catalog.catalog_json())
        print(f"  updated {paths.catalog_path().name}")
    print(f"\n{len(imported)} imported, {len(skipped)} skipped")
    return 0


def _cmd_scoreboard(args: argparse.Namespace) -> int:
    from . import scoreboard

    if args.action == "set-baseline":
        circuit = model.load_circuit(args.circuit)
        try:
            path = scoreboard.set_baseline(circuit, args.pdk, args.design)
        except FileNotFoundError as exc:
            print(f"analog-db: {exc}", file=sys.stderr)
            return 2
        print(f"  wrote {path}")
        print("  → run `analog-db generate --all` to refresh catalog.json + scoreboard.json")
        return 0
    text = scoreboard.index_json()
    if args.write:
        scoreboard.index_path().write_text(text)
        print(f"  wrote {scoreboard.index_path()}")
    else:
        sys.stdout.write(text)
    return 0


def _cmd_new_circuit(args: argparse.Namespace) -> int:
    from .authoring import ScaffoldError, allocate_id, scaffold_circuit

    try:
        cid = allocate_id(args.klass, args.slug)
        cdir = scaffold_circuit(
            {
                "id": cid,
                "class": args.klass,
                "display_name": args.display_name or args.slug.replace("_", " "),
                "ports": [p.strip() for p in args.ports.split(",") if p.strip()],
                "pdks": [p.strip() for p in args.pdks.split(",") if p.strip()],
            }
        )
    except (ScaffoldError, FileExistsError) as exc:
        print(f"analog-db: {exc}", file=sys.stderr)
        return 2
    print(f"  allocated {cid}")
    print(f"  scaffolded {cdir}")
    print(
        "  → author abstract/netlist.spice, datasheet.yaml, analyses/ and pdk/<pdk>/ bindings;"
        " `analog-db verify` fails until the circuit is complete"
    )
    return 0


def _cmd_add_binding(args: argparse.Namespace) -> int:
    from . import bindings

    circuit = model.load_circuit(args.circuit)
    try:
        written = bindings.add_binding(circuit, args.pdk, args.source)
    except bindings.BindingError as exc:
        print(f"analog-db: {exc}", file=sys.stderr)
        return 2
    for w in written:
        print(f"  wrote {args.circuit}/{w}")
    print(f"  → now run `analog-db generate --circuit {args.circuit}` to emit the lowered netlist")
    return 0


def _cmd_gmid_extract(args: argparse.Namespace) -> int:
    from . import gmid

    def _triple(s: str) -> tuple[float, float, float]:
        a, b, c = (float(x) for x in s.split(","))
        return (a, b, c)

    overrides: dict = {}
    if args.vgs:
        overrides["vgs"] = _triple(args.vgs)
    if args.vds:
        overrides["vds"] = _triple(args.vds)
    if args.vsb:
        overrides["vsb"] = _triple(args.vsb)
    if args.length:
        overrides["length_um"] = [float(x) for x in args.length.split(",")]
    if args.width is not None:
        overrides["width_um"] = args.width
    if args.temp is not None:
        overrides["temp_k"] = args.temp

    # --corner accepts one corner, a comma list (tt,ss,ff), or `all` = the registry gmid.corners set.
    if args.corner == "all":
        corners = gmid.registry_corners(args.pdk)
        print(f"  --corner all → registered corners for {args.pdk}: {', '.join(corners)}")
    else:
        corners = [c.strip() for c in args.corner.split(",") if c.strip()]

    runner = gmid.base_image_deck_runner(args.docker_image)
    ngspice = gmid.base_image_ngspice_version(
        args.docker_image
    )  # one cheap query, for the manifest
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    failures: list[str] = []
    for corner in corners:
        try:
            cfg = gmid.GmidConfig.from_registry(
                args.pdk, device=args.device, corner=corner, **overrides
            )
            n = (
                len(cfg.length_um)
                * len(gmid.axes(cfg)["VGS"])
                * len(gmid.axes(cfg)["VDS"])
                * len(gmid.axes(cfg)["VSB"])
            )
            print(
                f"  characterizing {cfg.pdk}/{cfg.device} @{cfg.corner} over ~{n} bias points "
                f"(L×VGS×VDS×VSB)…"
            )
            lut = gmid.extract(cfg, runner)
            path = gmid.write_lut(cfg, lut)
            man = gmid.write_manifest(cfg, lut, ngspice=ngspice, extracted_at=stamp)
            print(
                f"  wrote {path}  (L={list(lut['L'])}, VGS×VDS×VSB="
                f"{lut['GM'].shape[1]}×{lut['GM'].shape[2]}×{lut['GM'].shape[3]})"
            )
            print(f"  wrote {man}")
        except (ValueError, KeyError, RuntimeError) as exc:
            print(f"analog-db: {corner}: {exc}", file=sys.stderr)
            failures.append(corner)
    return 1 if failures else 0


def _cmd_catalog(args: argparse.Namespace) -> int:
    text = catalog.catalog_json()
    if args.write:
        paths.catalog_path().write_text(text)
        print(f"  wrote {paths.catalog_path()}")
    else:
        sys.stdout.write(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="analog-db", description="SpiceXplorer analog circuit database tools"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("verify", help="run the tiered verification harness")
    v.add_argument(
        "--tier",
        type=int,
        action="append",
        choices=verify.TIERS,
        help="tier(s) to run (default: all)",
    )
    v.add_argument("--circuit", help="limit to one circuit id")
    v.add_argument("--pdk", help="limit checks mentioning this PDK")
    v.add_argument("--json", action="store_true", help="emit the matrix report as JSON")
    v.add_argument(
        "--sim",
        action="store_true",
        help="run the Tier-3/4 native ngspice sweep (needs ngspice + $PDK_ROOT); off by default "
        "so the fast gate stays PDK-free (plan §6 cadence)",
    )
    v.set_defaults(func=_cmd_verify)

    g = sub.add_parser(
        "generate", help="(re)write generated artifacts (cgraph.json, lowered netlists)"
    )
    g.add_argument("--circuit", help="limit to one circuit id")
    g.add_argument(
        "--all",
        action="store_true",
        help="full regen: also export raw/ decks and rewrite catalog.json (netlists → raw → catalog)",
    )
    g.set_defaults(func=_cmd_generate)

    gp = sub.add_parser(
        "gen-params",
        help="generate/refresh abstract/params.yaml — atomic inventory + proposed default tying "
        "(generated-then-reviewed; preserves authored groups:/ratios: on refresh)",
    )
    gp.add_argument("--circuit", help="one circuit id")
    gp.add_argument("--all", action="store_true", help="every verifiable circuit")
    gp.add_argument(
        "--write",
        action="store_true",
        help="write abstract/params.yaml (default: print the proposal/diff to stdout)",
    )
    gp.set_defaults(func=_cmd_gen_params)

    er = sub.add_parser(
        "export-raw",
        help="materialize ready-to-run testbench decks + schematics (plain/annotated/hierarchical + "
        "structural.json) under raw/",
    )
    er.add_argument("--circuit", help="limit to one circuit id")
    er.add_argument("--pdk", help="limit to one PDK")
    er.add_argument(
        "--corner",
        default="tt",
        help="corner(s): tt (default) or a comma list (tt,ss,ff); non-tt decks get a __<corner> suffix",
    )
    er.add_argument(
        "--check",
        action="store_true",
        help="drift guard: report stale/missing/orphan decks vs a fresh render (exit 1 on drift); no writes",
    )
    er.add_argument(
        "--svg",
        action="store_true",
        help="also render each circuit's schematics (plain/annotated/hierarchical) to .svg via xschem "
        "(needs the base image / container, or a host with xschem 3.4.8+ for per-net colouring; a no-op "
        "where xschem is absent)",
    )
    er.set_defaults(func=_cmd_export_raw)

    erp = sub.add_parser(
        "export-raw-project",
        help="generate a raw-targeting project_setup.yaml (optimizer driven off the raw/ decks) "
        "into raw_optimize/generated/",
    )
    erp.add_argument("--circuit", help="one circuit id (default: every circuit with scorable decks)")
    erp.add_argument("--pdk", help="PDK binding to target (default: the circuit's first)")
    erp.add_argument("--out", help="output dir (default: <db>/raw_optimize/generated)")
    erp.set_defaults(func=_cmd_export_raw_project)

    r = sub.add_parser(
        "run", help="run analyses through ngspice (PDK-gated; use --docker from the host)"
    )
    r.add_argument("--circuit", required=True)
    r.add_argument("--pdk", required=True)
    r.add_argument("--corner", default="tt")
    r.add_argument(
        "--docker",
        nargs="?",
        const="api",
        default=None,
        help="execute ngspice inside this running compose service (default: api)",
    )
    r.add_argument(
        "--docker-image",
        nargs="?",
        const="spicexplorer-spice-base:local",
        default=None,
        help="execute ngspice via a fresh `docker run` of this EDA base image "
        "(has ngspice + both PDKs; no running service needed)",
    )
    r.add_argument(
        "--write",
        action="store_true",
        help="record on the scoreboard: scoreboard/<pdk>/<design_id>.json (upsert by corner)",
    )
    r.add_argument(
        "--crosscheck",
        action="store_true",
        help="netlist2tf symbolic-vs-sim cross-check (D-5; needs the [symbolic] extra)",
    )
    r.set_defaults(func=_cmd_run)

    ig = sub.add_parser("import-analoggym", help="import AnalogGym amplifier(s) into circuits/")
    ig.add_argument(
        "--src", required=True, help="path to AnalogGym .../Amplifier (has spice_netlist/)"
    )
    ig.add_argument("--circuit", help="one folder name (e.g. Fan_SMC_Pin_3); default: all")
    ig.set_defaults(func=_cmd_import_analoggym)

    fs = sub.add_parser(
        "import-ferrosim", help="import the ferrosim corpus as kind: reference circuits (D-9)"
    )
    fs.add_argument(
        "--src", required=True, help="path to the ferrosim tests/ dir (has decks/, va_demo/, sc_sample/)"
    )
    fs.add_argument(
        "--no-catalog", action="store_true", help="don't rebuild catalog.json after importing"
    )
    fs.set_defaults(func=_cmd_import_ferrosim)

    nc = sub.add_parser(
        "new-circuit",
        help="allocate the next accession id for a class and scaffold the draft circuit dir",
    )
    nc.add_argument("--class", dest="klass", required=True, help="circuit class (e.g. ldo)")
    nc.add_argument("--slug", required=True, help="descriptive id suffix (e.g. basic_pmos)")
    nc.add_argument("--display-name", help="human-readable name (default: the slug)")
    nc.add_argument("--ports", required=True, help="canonical port order, comma-separated")
    nc.add_argument("--pdks", default="sky130", help="target PDK id(s), comma-separated")
    nc.set_defaults(func=_cmd_new_circuit)

    ab = sub.add_parser(
        "add-binding", help="synthesize another PDK binding for a circuit (cross-PDK transfer)"
    )
    ab.add_argument("--circuit", required=True)
    ab.add_argument("--pdk", required=True, help="the target PDK to add a binding for")
    ab.add_argument(
        "--from",
        dest="source",
        help="source PDK to convert from (default: the circuit's first binding)",
    )
    ab.set_defaults(func=_cmd_add_binding)

    ge = sub.add_parser(
        "gmid-extract", help="characterize a PDK device into a pygmid-compatible gm/ID LUT"
    )
    ge.add_argument("--pdk", required=True)
    ge.add_argument(
        "--device", help="PDK model to characterize (default: the registry gmid.device)"
    )
    ge.add_argument(
        "--corner",
        default="tt",
        help="corner(s): one (tt), a comma list (tt,ss,ff), or 'all' = the registry "
        "gmid.corners set; each writes its own <device>__<corner>.pkl",
    )
    ge.add_argument("--vgs", help="VGS sweep 'start,step,stop' (V)")
    ge.add_argument("--vds", help="VDS sweep 'start,step,stop' (V)")
    ge.add_argument("--vsb", help="bulk sweep 'start,step,stop' (V; nmos negative)")
    ge.add_argument("--length", help="comma-separated L values in µm (e.g. 0.15,0.3,1,2)")
    ge.add_argument("--width", type=float, help="device width in µm (default: registry)")
    ge.add_argument("--temp", type=float, help="temperature in K (default: registry)")
    ge.add_argument(
        "--docker-image",
        default="spicexplorer-spice-base:local",
        help="EDA base image carrying ngspice + the PDK (default: spicexplorer-spice-base:local)",
    )
    ge.set_defaults(func=_cmd_gmid_extract)

    c = sub.add_parser("catalog", help="build the class-aware catalog.json")
    c.add_argument("--write", action="store_true", help="write to the db root instead of stdout")
    c.set_defaults(func=_cmd_catalog)

    sb = sub.add_parser(
        "scoreboard",
        help="build the generated scoreboard.json index (class × pdk × circuit × design point, "
        "Pareto-marked), or name a baseline",
    )
    sb.add_argument(
        "action",
        nargs="?",
        default="index",
        choices=["index", "set-baseline"],
        help="index (default): build the global index; set-baseline: name a design point",
    )
    sb.add_argument("--write", action="store_true", help="write to the db root instead of stdout")
    sb.add_argument("--circuit", help="(set-baseline) circuit id")
    sb.add_argument("--pdk", help="(set-baseline) PDK id")
    sb.add_argument("--design", help="(set-baseline) design_id of an existing entry")
    sb.set_defaults(func=_cmd_scoreboard)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
