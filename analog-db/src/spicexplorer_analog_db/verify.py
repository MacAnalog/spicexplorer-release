"""The tiered verification harness.

T0 schema      — metadata well-formed + cross-resolvable (LIVE).
T1 generation  — all netlists generate; committed == regenerated; lowered re-parses (LIVE).
T2 assembly    — every (circuit × analysis × pdk × corner) assembles runnable (LIVE).
T3 sim smoke   — every design runs in every applicable testbench (IMPLEMENTED; opt-in via
                 ``--sim``, PDK-gated — off by default so the fast gate stays PDK-free).
T4 conformance — measured vs datasheet spec + symbolic cross-check (IMPLEMENTED; opt-in via
                 ``--sim``, parallel to T3, PDK-gated — reuses the T3 measures).

The matrix report is ``list[CheckResult]``: each row is one (circuit, tier, check) → status.
``circuit.status`` is DERIVED from the highest tier a circuit clears.
"""

from __future__ import annotations

import concurrent.futures
import json
import math
import os
import re
from dataclasses import asdict, dataclass
from typing import Literal

import yaml

from . import catalog, export, generate, model, paths, pdks, schema, yamlio
from .extends import ExtendsError, resolve_extends

Status = Literal["pass", "fail", "skip"]
TIERS = (0, 1, 2, 3, 4)
_TIER_LANDS = {3: "Phase 7 (PDK-gated)", 4: "Phase 7 (PDK-gated)"}

# status precedence for the DERIVED circuit status
_TIER_STATUS = {0: "generated", 1: "generated", 2: "generated", 3: "simulated", 4: "validated"}


@dataclass(frozen=True)
class CheckResult:
    circuit: str  # "" for DB-level checks
    tier: int
    check: str
    status: Status
    reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _ok(circuit: str, tier: int, check: str, reason: str = "") -> CheckResult:
    return CheckResult(circuit, tier, check, "pass", reason)


def _fail(circuit: str, tier: int, check: str, reason: str) -> CheckResult:
    return CheckResult(circuit, tier, check, "fail", reason)


def _skip(circuit: str, tier: int, check: str, reason: str) -> CheckResult:
    return CheckResult(circuit, tier, check, "skip", reason)


# --------------------------------------------------------------------------- Tier 0


def _tier0_db_level() -> list[CheckResult]:
    results: list[CheckResult] = []
    # accession numbers are unique per class code (append-only, never reused)
    seen: dict[tuple[str, int], list[str]] = {}
    for cid in model.list_circuit_ids():
        acc = model.parse_accession(cid)
        if acc:
            seen.setdefault((acc[0], acc[1]), []).append(cid)
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    results.append(
        _ok("", 0, "id:accession_unique")
        if not dups
        else _fail(
            "",
            0,
            "id:accession_unique",
            "duplicate accession number(s): "
            + "; ".join(f"{code}_{num:03d} → {ids}" for (code, num), ids in sorted(dups.items())),
        )
    )
    # every class library validates against the class schema
    for cid in model.list_class_ids():
        errs = schema.validation_errors(model.load_class(cid), "class")
        results.append(
            _ok("", 0, f"schema:class:{cid}")
            if not errs
            else _fail("", 0, f"schema:class:{cid}", "; ".join(errs))
        )
    # catalog determinism: committed == freshly built
    cpath = paths.catalog_path()
    if not cpath.is_file():
        results.append(
            _skip(
                "",
                0,
                "catalog:determinism",
                "no committed catalog.json (run `analog-db catalog --write`)",
            )
        )
    else:
        results.append(
            _ok("", 0, "catalog:determinism")
            if cpath.read_text() == catalog.catalog_json()
            else _fail(
                "",
                0,
                "catalog:determinism",
                "committed catalog.json is stale; run `analog-db catalog --write`",
            )
        )
    # scoreboard.json determinism: committed == freshly built from the per-circuit entries
    from . import scoreboard as sb

    spath = sb.index_path()
    if not spath.is_file():
        results.append(
            _skip(
                "",
                0,
                "scoreboard:determinism",
                "no committed scoreboard.json (run `analog-db scoreboard --write`)",
            )
        )
    else:
        results.append(
            _ok("", 0, "scoreboard:determinism")
            if spath.read_text() == sb.index_json()
            else _fail(
                "",
                0,
                "scoreboard:determinism",
                "committed scoreboard.json is stale; run `analog-db scoreboard --write`",
            )
        )
    results.extend(_tier0_raw_catalog())
    return results


def _tier0_raw_catalog() -> list[CheckResult]:
    """``raw/`` tree ⇄ committed catalog index: no dangling pointers, no unindexed decks.

    Cheap (reads the committed catalog + lists ``raw/``; no assembly) — the byte-identical drift of
    the deck *contents* is the Tier-1 ``raw:drift`` guard."""
    cpath = paths.catalog_path()
    if not cpath.is_file():
        return [_skip("", 0, "raw:catalog_xref", "no committed catalog.json")]
    rd = export.raw_root()
    # Top-level ``raw/_*`` dirs hold hand-curated research/demo artifacts (e.g. the placement-strategy
    # gallery), not catalog decks, so they're excluded from the index cross-check.
    on_disk = (
        {
            str(p.relative_to(paths.db_root()))
            for p in rd.rglob("*.spice")
            if not p.relative_to(rd).parts[0].startswith("_")
        }
        if rd.is_dir()
        else set()
    )
    in_catalog: set[str] = set()
    for entry in json.loads(cpath.read_text()).get("circuits", []):
        for tbs in (entry.get("raw") or {}).values():
            in_catalog.update(tbs.values())
    dangling = sorted(in_catalog - on_disk)
    orphan = sorted(on_disk - in_catalog)
    if not dangling and not orphan:
        return [_ok("", 0, "raw:catalog_xref")]
    reason = []
    if dangling:
        reason.append(f"catalog → {len(dangling)} missing file(s) e.g. {dangling[:2]}")
    if orphan:
        reason.append(f"{len(orphan)} unindexed deck(s) e.g. {orphan[:2]}")
    return [
        _fail("", 0, "raw:catalog_xref", "; ".join(reason) + " — run `analog-db generate --all`")
    ]


def _tier0_reference_circuit(c: model.Circuit) -> list[CheckResult]:
    """Reference-only T0 subset: a kind: reference circuit carries foreign/proprietary decks
    that are never lowered or simulated here, so it is exempt from the class-library / abstract-netlist
    / open-PDK checks. It must instead: validate against the circuit schema, credit its source, and
    have every declared reference binding present on disk with at least one DUT deck."""
    r: list[CheckResult] = []

    errs = schema.validation_errors(c.manifest, "circuit")
    r.append(
        _ok(c.id, 0, "schema:circuit")
        if not errs
        else _fail(c.id, 0, "schema:circuit", "; ".join(errs))
    )

    # corpus-scoped id: reference circuits keep <corpus>_<name> ids.
    r.append(
        _ok(c.id, 0, "id:format")
        if model.REFERENCE_ID_RE.match(c.id)
        else _fail(c.id, 0, "id:format", "reference id must be lowercase [a-z0-9_]")
    )

    # provenance is mandatory for reference circuits — they are imported third-party work.
    prov = c.manifest.get("provenance") or {}
    missing = [k for k in ("source", "license") if not prov.get(k)]
    r.append(
        _ok(c.id, 0, "ref:provenance")
        if not missing
        else _fail(c.id, 0, "ref:provenance", f"provenance missing {missing} (source + license required)")
    )

    # every declared reference binding is either an upstream POINTER (URL — nothing on disk to
    # check; no third-party or foundry-bound decks are redistributed here) or a legacy on-disk
    # dir with at least one deck (searched recursively: dut/tb/runs, netlists/, variants/, D-9).
    for entry in c.references:
        if entry.get("upstream") and not entry.get("dir"):
            r.append(_ok(c.id, 0, f"ref:pointer:{entry['upstream']}"))
            continue
        label = str(entry.get("dir") or entry)
        bdir = c.reference_dir(entry)
        if not bdir.is_dir():
            r.append(_fail(c.id, 0, f"ref:binding:{label}", f"references dir {label!r} missing"))
            continue
        decks = next(bdir.rglob("*.scs"), None)
        r.append(
            _ok(c.id, 0, f"ref:binding:{label}")
            if decks is not None
            else _fail(c.id, 0, f"ref:binding:{label}", f"no .scs deck under {label}/")
        )

    r.extend(_tier0_reference_decks_parse(c))
    return r


def _tier0_reference_decks_parse(c: model.Circuit) -> list[CheckResult]:
    """Every reference deck parses through the dialect-aware ``NetlistView`` (``ref:parse:*``).

    Structural read only — Spectre ``.scs`` via auto-detection, HSPICE-family ``.sp`` via the
    explicit hspice reader (bare-subckt DUT fragments carry no strong dialect markers); includes
    are never resolved, and a deck with no devices (a runs/params deck) still counts as
    parsed. Skips gracefully when spicexplorer-core predates dialect support.
    """
    import importlib
    import logging

    # Feature-probe fully dynamically (importlib, no static import): a pre-dialect
    # spicexplorer-core has no NetlistDialect and no `dialect=` kwarg, and this repo's pyright
    # ratchet type-checks against whatever platform env CI provides — a static import here
    # would count as a new reportMissingImports until the dialect feature lands on platform main.
    try:
        spice_engine = importlib.import_module("spicexplorer_core.spice_engine")
    except ImportError:
        spice_engine = None
    if spice_engine is None or not hasattr(spice_engine, "NetlistDialect"):
        return [
            _skip(c.id, 0, "ref:parse", "dialect-aware NetlistView unavailable (pre-dialect spicexplorer-core)")
        ]
    netlist_view = spice_engine.NetlistView

    r: list[CheckResult] = []
    core_logger = logging.getLogger("spicexplorer_core")
    prev_level = core_logger.level
    core_logger.setLevel(logging.ERROR)  # reader warnings (black-box masters, …) are not verify output
    try:
        for entry in c.references:
            if not entry.get("dir"):
                continue  # upstream pointer entry — nothing on disk to parse
            bdir = c.reference_dir(entry)
            label = str(entry.get("dir") or entry)
            if not bdir.is_dir():
                continue  # ref:binding already failed above
            bad: list[str] = []
            checked = 0
            for deck in sorted(bdir.rglob("*.scs")) + sorted(bdir.rglob("*.sp")):
                checked += 1
                dialect = "auto" if deck.suffix.lower() == ".scs" else "hspice"
                try:
                    netlist_view.from_file(deck, dialect=dialect)
                except Exception as exc:  # noqa: BLE001 — any parse failure is the finding
                    bad.append(f"{deck.name}: {type(exc).__name__}: {exc}")
            if not checked:
                continue  # emptiness is ref:binding's finding, not a parse result
            if bad:
                extra = f" (+{len(bad) - 3} more)" if len(bad) > 3 else ""
                r.append(_fail(c.id, 0, f"ref:parse:{label}", "; ".join(bad[:3]) + extra))
            else:
                r.append(_ok(c.id, 0, f"ref:parse:{label}"))
    finally:
        core_logger.setLevel(prev_level)
    return r


def _tier0_params_yaml(c) -> list[CheckResult]:
    """Optional ``abstract/params.yaml`` (spicexplorer/params@1) schema check.

    Adoption is per circuit: absent is fine (no row); present must validate. Only ``c.dir`` /
    ``c.id`` are consumed, so this stays testable in isolation.
    """
    p = c.dir / "abstract" / "params.yaml"
    if not p.is_file():
        return []
    try:
        doc = yamlio.read_yaml(p)
    except yaml.YAMLError as exc:
        return [_fail(c.id, 0, "schema:params", f"unparseable YAML: {exc}")]
    errs = schema.validation_errors(doc if isinstance(doc, dict) else {}, "params")
    if errs:
        return [_fail(c.id, 0, "schema:params", "; ".join(errs))]
    return [_ok(c.id, 0, "schema:params")]


def _tier0_composition(c: model.Circuit) -> list[CheckResult]:
    """Composite manifests: ``composition.yaml`` schema + the composer's
    validators (interface, pins, taps/omit, acyclic DAG, PDK bindings). Absent = not a
    composite (no row)."""
    from . import compose

    if not compose.is_composite(c):
        return []
    r: list[CheckResult] = []
    try:
        doc = compose.load_composition(c)
    except (compose.ComposeError, yaml.YAMLError) as exc:
        return [_fail(c.id, 0, "schema:composition", f"unparseable: {exc}")]
    errs = schema.validation_errors(doc, "composition")
    r.append(
        _ok(c.id, 0, "schema:composition")
        if not errs
        else _fail(c.id, 0, "schema:composition", "; ".join(errs))
    )
    verrs = compose.validate(c)
    r.append(
        _ok(c.id, 0, "compose:valid")
        if not verrs
        else _fail(c.id, 0, "compose:valid", "; ".join(verrs))
    )
    return r


def _tier0_circuit(c: model.Circuit) -> list[CheckResult]:
    if c.is_reference_only:
        return _tier0_reference_circuit(c)

    r: list[CheckResult] = []

    # --- schema validation ---
    errs = schema.validation_errors(c.manifest, "circuit")
    r.append(
        _ok(c.id, 0, "schema:circuit")
        if not errs
        else _fail(c.id, 0, "schema:circuit", "; ".join(errs))
    )

    ds_path = c.dir / "datasheet.yaml"
    datasheet: dict = {}
    if ds_path.is_file():
        datasheet = c.datasheet()
        errs = schema.validation_errors(datasheet, "datasheet")
        r.append(
            _ok(c.id, 0, "schema:datasheet")
            if not errs
            else _fail(c.id, 0, "schema:datasheet", "; ".join(errs))
        )
    else:
        r.append(_fail(c.id, 0, "schema:datasheet", "datasheet.yaml missing"))

    for pdk in c.pdks:
        sz = c.dir / "pdk" / pdk / "sizing.yaml"
        if sz.is_file():
            errs = schema.validation_errors(c.sizing(pdk), "sizing")
            r.append(
                _ok(c.id, 0, f"schema:sizing:{pdk}")
                if not errs
                else _fail(c.id, 0, f"schema:sizing:{pdk}", "; ".join(errs))
            )
        else:
            r.append(_fail(c.id, 0, f"schema:sizing:{pdk}", f"pdk/{pdk}/sizing.yaml missing"))

    for aid, apath in c.analysis_files().items():
        errs = schema.validation_errors(c.analysis(aid), "analysis")
        r.append(
            _ok(c.id, 0, f"schema:analysis:{aid}")
            if not errs
            else _fail(c.id, 0, f"schema:analysis:{aid}", "; ".join(errs))
        )

    r.extend(_tier0_params_yaml(c))
    r.extend(_tier0_composition(c))

    # --- accession id ---
    acc = model.parse_accession(c.id)
    if acc is None:
        r.append(
            _fail(
                c.id,
                0,
                "id:format",
                "verifiable id must be <code>_<nnn>_<slug> (e.g. ldo_004_basic_pmos); "
                "allocate with `analog-db new-circuit`",
            )
        )
    else:
        code = model.class_id_code(c.klass)
        r.append(
            _ok(c.id, 0, "id:format")
            if code is None or acc[0] == code
            else _fail(
                c.id, 0, "id:format", f"id code {acc[0]!r} != class {c.klass!r} id_code {code!r}"
            )
        )

    # --- cross-reference resolution ---
    classes = set(model.list_class_ids())
    if c.klass in classes:
        r.append(_ok(c.id, 0, "xref:class_exists"))
        templates = set(model.class_templates(c.klass))
        canon = set(model.load_class(c.klass).get("canonical_metrics", []))

        bad = [a for a in c.analyses if a not in templates]
        r.append(
            _ok(c.id, 0, "xref:analyses_in_class")
            if not bad
            else _fail(c.id, 0, "xref:analyses_in_class", f"not in class templates: {bad}")
        )

        # A clocked (chopper / switched-cap) circuit must NOT declare a frozen-OP small-signal
        # analysis (.ac / .noise) — it freezes the switches, so the figure is physically wrong.
        # Author-time fail-fast (the PDK-free gate); assemble() also refuses it at run time.
        bad_ss = [
            a for a in c.analyses if c.is_clocked and model.is_frozen_smallsignal_analysis(a)
        ]
        r.append(
            _ok(c.id, 0, "xref:no_frozen_ss_on_clocked")
            if not bad_ss
            else _fail(
                c.id,
                0,
                "xref:no_frozen_ss_on_clocked",
                f"frozen-OP small-signal analyses on a clocked circuit "
                f"(use transient or PSS/PAC): {bad_ss}",
            )
        )

        for aid in c.analysis_files():
            adoc = c.analysis(aid)
            tmpl = adoc.get("template", aid)
            resolved = model.resolve_template(c.klass, tmpl)
            r.append(
                _ok(c.id, 0, f"xref:template:{aid}")
                if resolved
                else _fail(
                    c.id, 0, f"xref:template:{aid}", f"template {tmpl!r} resolves to no file"
                )
            )

        metrics = datasheet.get("metrics", {})
        bad_m = [m for m in metrics if m not in canon]
        r.append(
            _ok(c.id, 0, "xref:metrics_in_class")
            if not bad_m
            else _fail(c.id, 0, "xref:metrics_in_class", f"not in class canonical_metrics: {bad_m}")
        )

        bad_a = [
            m
            for m, spec in metrics.items()
            if spec.get("analysis") and spec["analysis"] not in c.analyses
        ]
        r.append(
            _ok(c.id, 0, "xref:metric_analysis_refs")
            if not bad_a
            else _fail(
                c.id,
                0,
                "xref:metric_analysis_refs",
                f"metrics reference analyses not in circuit.analyses: {bad_a}",
            )
        )
    else:
        r.append(
            _fail(
                c.id,
                0,
                "xref:class_exists",
                f"class {c.klass!r} has no library under _shared/classes/",
            )
        )

    registries = set(pdks.registry_ids())
    for pdk in c.pdks:
        present = (c.dir / "pdk" / pdk).is_dir()
        r.append(
            _ok(c.id, 0, f"xref:pdk_dir:{pdk}")
            if present
            else _fail(c.id, 0, f"xref:pdk_dir:{pdk}", f"pdk/{pdk}/ missing")
        )
        r.append(
            _ok(c.id, 0, f"xref:pdk_registry:{pdk}")
            if pdk in registries
            else _fail(c.id, 0, f"xref:pdk_registry:{pdk}", f"_shared/pdk/{pdk}.yaml missing")
        )

    abstract = c.dir / "abstract" / "netlist.spice"
    r.append(
        _ok(c.id, 0, "xref:abstract_netlist")
        if abstract.is_file()
        else _fail(c.id, 0, "xref:abstract_netlist", "abstract/netlist.spice missing")
    )

    # --- scoreboard integrity ---
    from . import scoreboard as sb

    entries = sb.load_entries(c)
    if entries:
        bad_e = []
        for e in entries:
            errs = schema.validation_errors(e, "scoreboard-entry")
            if errs:
                bad_e.append(f"{e.get('pdk')}/{e.get('design_id')}: {errs[0]}")
            elif e.get("circuit") != c.id:
                bad_e.append(f"{e.get('pdk')}/{e.get('design_id')}: circuit field {e.get('circuit')!r}")
        r.append(
            _ok(c.id, 0, "scoreboard:entries")
            if not bad_e
            else _fail(c.id, 0, "scoreboard:entries", "; ".join(bad_e[:3]))
        )
        dangling = [
            f"{pdk}→{did}"
            for pdk, did in sb.baselines(c).items()
            if not sb.entry_path(c, pdk, did).is_file()
        ]
        r.append(
            _ok(c.id, 0, "scoreboard:baselines")
            if not dangling
            else _fail(c.id, 0, "scoreboard:baselines", f"dangling baseline(s): {dangling}")
        )
    else:
        r.append(_skip(c.id, 0, "scoreboard:entries", "no recorded design points yet"))

    # --- optimizer projection extends resolution ---
    proj = c.dir / "optimizer" / "projection.yaml"
    if proj.is_file():
        try:
            resolve_extends(proj)
            r.append(_ok(c.id, 0, "extends:projection"))
        except ExtendsError as exc:
            r.append(_fail(c.id, 0, "extends:projection", str(exc)))
    else:
        r.append(_skip(c.id, 0, "extends:projection", "no optimizer/projection.yaml"))

    return r


def run_tier0(circuit_ids: list[str] | None = None) -> list[CheckResult]:
    # DB-level checks (id uniqueness, class schemas, catalog xref — a full-corpus render) only
    # run on an unfiltered sweep, same contract as run_tier1: a --circuit-filtered run is that
    # circuit's checks, not the whole registry's.
    results = _tier0_db_level() if circuit_ids is None else []
    ids = circuit_ids if circuit_ids is not None else model.list_circuit_ids()
    for cid in ids:
        results.extend(_tier0_circuit(model.load_circuit(cid)))
    return results


# --------------------------------------------------------------------------- Tier 1


def _params_group_incoherence(
    group: dict, comps: dict[str, dict]
) -> str | None:
    """Why this group's members are NOT electrically coherent with its claimed ``kind`` (plan
    D-6), or ``None`` when they are.

    Deliberately LOOSER than the structural detectors: a ``matched_pair`` needs exactly 2
    same-polarity MOS sharing SOURCE and BULK nets — no non-diode / non-supply-source demand
    (mirror-load halves like a diode-connected XM3 with its XM4 twin on vdd are a legitimate
    matched_pair; the kind vocabulary says so). ``mirror_length`` needs same polarity, shared
    GATE + SOURCE nets, and ≥1 diode-connected member. Authored kinds (``bias_chain``,
    ``shared_geometry``) carry no structural claim — members-exist is their whole contract."""
    kind = group.get("kind")
    if kind not in ("matched_pair", "mirror_length"):
        return None
    members = group.get("members") or []
    rows = []
    for m in members:
        comp = comps.get(m)
        if comp is None:
            return f"member {m!r} not in the topology graph"
        if comp.get("device_type") != "MOS":
            return f"member {m!r} is not a MOS device (kind {kind!r} is a MOS symmetry)"
        rows.append(comp)
    if len({r.get("polarity") for r in rows}) > 1:
        return f"mixed polarities {sorted({str(r.get('polarity')) for r in rows})}"

    def _net(row: dict, pin: str):
        return (row.get("connections") or {}).get(pin)

    if kind == "matched_pair":
        if len(members) != 2:
            return f"matched_pair needs exactly 2 members, has {len(members)}"
        if _net(rows[0], "SOURCE") != _net(rows[1], "SOURCE"):
            return "members do not share a SOURCE net"
        if _net(rows[0], "BULK") != _net(rows[1], "BULK"):
            return "members do not share a BULK net"
    else:  # mirror_length
        if len({_net(r, "GATE") for r in rows}) > 1:
            return "members do not share one GATE net"
        if len({_net(r, "SOURCE") for r in rows}) > 1:
            return "members do not share one SOURCE net"
        if not any(_net(r, "GATE") is not None and _net(r, "GATE") == _net(r, "DRAIN") for r in rows):
            return "no diode-connected member (gate==drain) to anchor the mirror"
    return None


def _tier1_params_checks(c: model.Circuit) -> list[CheckResult]:
    """Plan D-6 Tier-1 checks for the OPTIONAL ``abstract/params.yaml`` tying layer.

    Adoption is per circuit: no file → no rows. Present, the layer must be *referentially
    sound* (members/fields/ratio endpoints exist), *electrically coherent* with each group's
    claimed kind, and *symbol-closed* (netlist symbols ⊆ inventory; sizing.yaml keys on exactly
    the FREE symbols, so the lowered deck's ``.param`` header leaves nothing undefined).
    A detected-but-untied symmetry is a WARNING (skip row), never a failure."""
    from . import params as par

    if not (c.dir / "abstract" / "params.yaml").is_file():
        return []
    try:
        doc = par.load_params_doc(c.dir)
    except Exception as exc:  # noqa: BLE001 — unparseable YAML is the finding
        return [_fail(c.id, 1, "params:load", f"unparseable abstract/params.yaml: {exc}")]
    if not isinstance(doc, dict) or not isinstance(doc.get("devices"), dict):
        return [_fail(c.id, 1, "params:load", "no devices: mapping (schema shape is the Tier-0 gate)")]
    cg = c.dir / "abstract" / "topology.cgraph.json"
    if not cg.is_file():
        return [_fail(c.id, 1, "params:graph", "topology.cgraph.json missing (run `analog-db generate`)")]
    graph = par.load_graph(cg)
    comps = {cm["id"]: cm for cm in graph.get("components", [])}
    devices: dict = doc["devices"]
    r: list[CheckResult] = []

    # --- referential soundness: members exist, tie fields exist, ratio endpoints exist ---
    bad_refs: list[str] = []
    for g in doc.get("groups") or []:
        gname = g.get("name", "?")
        for m in g.get("members") or []:
            if m not in devices:
                bad_refs.append(f"group {gname}: member {m!r} not in devices:")
            else:
                for field in g.get("tie") or []:
                    if field not in devices[m]:
                        bad_refs.append(f"group {gname}: member {m!r} has no {field!r} field")
    for rt in doc.get("ratios") or []:
        label = f"ratio {rt.get('ref')}←{rt.get('of')}"
        for end in ("ref", "of"):
            inst = rt.get(end)
            if inst not in devices:
                bad_refs.append(f"{label}: {end} {inst!r} not in devices:")
            elif rt.get("param") not in devices[inst]:
                bad_refs.append(f"{label}: {end} {inst!r} has no {rt.get('param')!r} field")
    r.append(
        _ok(c.id, 1, "params:refs")
        if not bad_refs
        else _fail(c.id, 1, "params:refs", "; ".join(bad_refs[:4]))
    )

    # --- kind coherence (structural, from the committed graph) ---
    for g in doc.get("groups") or []:
        gname = g.get("name", "?")
        why = _params_group_incoherence(g, comps)
        r.append(
            _ok(c.id, 1, f"params:kind:{gname}")
            if why is None
            else _fail(c.id, 1, f"params:kind:{gname}", f"kind {g.get('kind')!r} incoherent: {why}")
        )

    # --- symbol closure: netlist symbols ⊆ inventory ---
    inventory_syms: set[str] = set()
    for fields in devices.values():
        if isinstance(fields, dict):
            for v in fields.values():
                inventory_syms |= par.value_symbols(v)
    missing_syms = sorted(par.netlist_symbols(graph) - inventory_syms)
    r.append(
        _ok(c.id, 1, "params:symbols")
        if not missing_syms
        else _fail(
            c.id,
            1,
            "params:symbols",
            f"netlist symbols not in the devices: inventory: {missing_syms[:6]} "
            "(run `analog-db gen-params --write` after re-authoring)",
        )
    )

    # --- sizing.yaml keys on exactly the FREE symbols, per PDK ---
    free = par.free_symbols(doc)
    tied = par.tied_symbols(doc)
    for pdk in c.pdks:
        if not (c.dir / "pdk" / pdk / "sizing.yaml").is_file():
            continue  # Tier-0 already fails the missing binding
        try:
            variables = c.sizing(pdk).get("variables", [])
        except Exception as exc:  # noqa: BLE001
            r.append(_fail(c.id, 1, f"params:sizing:{pdk}", f"sizing.yaml unreadable: {exc}"))
            continue
        names = {v["name"] for v in variables}
        # Knobs applied by the TESTBENCHES (bias-port DC sources / supply), not the
        # DUT ``.param`` header — flagged ``testbench: true`` in sizing.yaml. They
        # legitimately have no DUT inventory symbol, so they are exempt from the
        # closure below (e.g. a bias-port VCCS driver's tail/vcasc/vcm/vcc).
        testbench = {v["name"] for v in variables if v.get("testbench")}
        problems: list[str] = []
        undefined = sorted(free - names)
        if undefined:
            problems.append(
                f"free symbol(s) with no sizing row (the deck's .param would be undefined): {undefined[:6]}"
            )
        shadowing = sorted(names & tied)
        if shadowing:
            problems.append(f"sizing row(s) for TIED symbols (double definition): {shadowing[:6]}")
        mislabelled = sorted(testbench & (free | tied))
        if mislabelled:
            problems.append(
                f"sizing row(s) marked testbench: but defined in the DUT inventory: {mislabelled[:6]}"
            )
        unknown = sorted(names - free - tied - testbench)
        if unknown:
            problems.append(
                f"sizing row(s) for symbols neither in the inventory nor testbench-applied: {unknown[:6]}"
            )
        r.append(
            _ok(c.id, 1, f"params:sizing:{pdk}")
            if not problems
            else _fail(c.id, 1, f"params:sizing:{pdk}", "; ".join(problems))
        )
        # --- provenance inventory: an INFO row, per PDK (freeze flags are per-PDK, D-4) ---
        cls = par.classify_symbols(doc, c.sizing(pdk).get("variables", []))
        r.append(_ok(c.id, 1, f"params:inventory:{pdk}", par.counts_line(cls)))

    # --- detected-but-untied symmetry: WARNING, never a failure ---
    untied = par.untied_symmetries(graph, doc)
    r.append(
        _ok(c.id, 1, "params:untied_symmetry")
        if not untied
        else _skip(
            c.id,
            1,
            "params:untied_symmetry",
            "detected-but-untied (warning, not a gate): " + "; ".join(untied[:4]),
        )
    )
    return r


def _tier1_circuit(c: model.Circuit) -> list[CheckResult]:
    """Generation: committed GENERATED artifacts == freshly regenerated; lowered re-parses
    isomorphically; netlist2tf ingests. All PDK-free (the drift guard)."""
    from spicexplorer_circuitgraph import CircuitGraph
    from spicexplorer_core.spice_engine import NetlistView

    from . import compose

    r: list[CheckResult] = []

    abstract = c.dir / "abstract" / "netlist.spice"
    if not abstract.is_file():
        return [_fail(c.id, 1, "gen:abstract", "abstract/netlist.spice missing")]

    # composite drift: the flat netlist + per-PDK sizing are GENERATED from
    # composition.yaml — byte-identical drift guard, same contract as every generated artifact.
    if compose.is_composite(c):
        try:
            fresh_nl = compose.compose_netlist(c)
        except compose.ComposeError as exc:
            return [_fail(c.id, 1, "gen:compose", f"composer failed: {exc}")]
        r.append(
            _ok(c.id, 1, "gen:compose")
            if abstract.read_text() == fresh_nl
            else _fail(c.id, 1, "gen:compose", "stale abstract/netlist.spice; run `analog-db generate`")
        )
        for pdk in c.pdks:
            sz = c.dir / "pdk" / pdk / "sizing.yaml"
            if not sz.is_file():
                r.append(_fail(c.id, 1, f"gen:compose_sizing:{pdk}", "sizing.yaml not committed"))
                continue
            r.append(
                _ok(c.id, 1, f"gen:compose_sizing:{pdk}")
                if sz.read_text() == compose.compose_sizing(c, pdk, fresh_nl)
                else _fail(
                    c.id, 1, f"gen:compose_sizing:{pdk}", "stale; run `analog-db generate`"
                )
            )
    abstract_graph = CircuitGraph.from_netlist(NetlistView.from_file(str(abstract)), name=c.id)
    n_dev, n_net = abstract_graph.component_count, abstract_graph.net_count

    # cgraph.json drift
    cg = c.dir / "abstract" / "topology.cgraph.json"
    if not cg.is_file():
        r.append(
            _fail(
                c.id,
                1,
                "gen:cgraph",
                "topology.cgraph.json not committed (run `analog-db generate`)",
            )
        )
    else:
        r.append(
            _ok(c.id, 1, "gen:cgraph")
            if cg.read_text() == generate.cgraph_json(c)
            else _fail(c.id, 1, "gen:cgraph", "stale; run `analog-db generate`")
        )

    for pdk in c.pdks:
        lowered = c.dir / "pdk" / pdk / "netlist.spice"
        if not lowered.is_file():
            r.append(_fail(c.id, 1, f"gen:netlist:{pdk}", "lowered netlist not committed"))
            continue
        # drift
        try:
            fresh = generate.lowered_netlist(c, pdk)
        except Exception as exc:  # unknown PDK / map error
            r.append(_fail(c.id, 1, f"gen:netlist:{pdk}", f"generation failed: {exc}"))
            continue
        r.append(
            _ok(c.id, 1, f"gen:netlist:{pdk}")
            if lowered.read_text() == fresh
            else _fail(c.id, 1, f"gen:netlist:{pdk}", "stale; run `analog-db generate`")
        )
        # re-parse: lowered is isomorphic to the abstract (device/net counts preserved)
        try:
            lg = CircuitGraph.from_netlist(NetlistView.from_file(str(lowered)), name=c.id)
            ok = lg.component_count == n_dev and lg.net_count == n_net
            r.append(
                _ok(c.id, 1, f"reparse:{pdk}")
                if ok
                else _fail(
                    c.id,
                    1,
                    f"reparse:{pdk}",
                    f"counts {lg.component_count}/{lg.net_count} != abstract {n_dev}/{n_net}",
                )
            )
        except Exception as exc:
            r.append(_fail(c.id, 1, f"reparse:{pdk}", f"lowered netlist failed to re-parse: {exc}"))

    # optional params.yaml tying layer: referential + kind coherence + symbol closure
    r.extend(_tier1_params_checks(c))

    # generated project_setup.yaml drift (the optimizer projection)
    if (c.dir / "optimizer" / "projection.yaml").is_file():
        from .extends import ExtendsError as _EErr
        from .extends import generate_project_setup

        ps = c.dir / "project_setup.yaml"
        if not ps.is_file():
            r.append(
                _fail(c.id, 1, "gen:project_setup", "not committed (run `analog-db generate`)")
            )
        else:
            try:
                fresh_ps = generate_project_setup(c.dir)
                r.append(
                    _ok(c.id, 1, "gen:project_setup")
                    if ps.read_text() == fresh_ps
                    else _fail(c.id, 1, "gen:project_setup", "stale; run `analog-db generate`")
                )
            except _EErr as exc:
                r.append(_fail(c.id, 1, "gen:project_setup", str(exc)))

    # netlist2tf ingests the abstract (best-effort cross-check, not a generation gate):
    # only required for circuits that opt into the symbolic cross-check (a datasheet metric with
    # a `symbolic:` entry). For others (e.g. the 3-stage AnalogGym amps, whose param-arithmetic
    # netlist2tf ingest doesn't model yet — deferred) it's skipped, not failed.
    try:
        import spicexplorer_netlist2tf as n2tf
    except ImportError:
        r.append(
            _skip(
                c.id,
                1,
                "n2tf:ingest",
                "spicexplorer-netlist2tf not installed (the [symbolic] extra)",
            )
        )
        return r
    try:
        ds_metrics = (
            c.datasheet().get("metrics", {}) if (c.dir / "datasheet.yaml").is_file() else {}
        )
    except Exception:
        ds_metrics = {}
    uses_symbolic = any("symbolic" in spec for spec in ds_metrics.values())
    try:
        ir = n2tf.from_file(str(abstract), name=c.id)
        n_mos = sum(
            1 for d in abstract_graph.get_components() if type(d).__name__.endswith("MosfetNode")
        )
        r.append(
            _ok(c.id, 1, "n2tf:ingest")
            if len(ir.devices) >= n_mos
            else _fail(
                c.id, 1, "n2tf:ingest", f"ingested {len(ir.devices)} devices, expected >= {n_mos}"
            )
        )
    except Exception as exc:  # netlist2tf can't model this topology yet
        result = _fail if uses_symbolic else _skip
        r.append(
            result(
                c.id,
                1,
                "n2tf:ingest",
                f"netlist2tf ingest unsupported for this topology: {type(exc).__name__}",
            )
        )

    return r


def _tier1_db_level() -> list[CheckResult]:
    """``raw/`` decks: committed bytes == freshly rendered (byte-identical drift guard, same contract
    as the lowered netlists). Full-DB only; a circuit-scoped verify skips this global gate."""
    stale, missing, orphan = export.check_drift()
    if not (stale or missing or orphan):
        return [_ok("", 1, "raw:drift")]
    head = (stale + missing + orphan)[:3]
    return [
        _fail(
            "",
            1,
            "raw:drift",
            f"{len(stale)} stale / {len(missing)} missing / {len(orphan)} orphan deck(s) "
            f"e.g. {head}; run `analog-db generate --all`",
        )
    ]


def run_tier1(circuit_ids: list[str] | None = None) -> list[CheckResult]:
    ids = circuit_ids if circuit_ids is not None else model.list_circuit_ids()
    out: list[CheckResult] = []
    if circuit_ids is None:
        out.extend(_tier1_db_level())
    for cid in ids:
        c = model.load_circuit(cid)
        if c.is_reference_only:
            out.append(_skip(cid, 1, "gen:reference", "kind: reference — not lowered/generated here"))
            continue
        out.extend(_tier1_circuit(c))
    return out


# --------------------------------------------------------------------------- Tier 2


def _corner_names(c: model.Circuit, pdk: str) -> list[str]:
    path = c.dir / "pdk" / pdk / "corners.yaml"
    if not path.is_file():
        return []
    doc = yamlio.read_yaml(path) or {}
    return sorted((doc.get("corners") or {}).keys())


def _tier2_circuit(c: model.Circuit) -> list[CheckResult]:
    """Assembly: every (analysis × pdk × corner) renders a complete netlist — no unresolved
    placeholders, all sizing params bound — and the result re-parses. PDK-free."""
    from spicexplorer_core.spice_engine import NetlistView

    from .assemble import AssembleError, assemble

    r: list[CheckResult] = []
    bindings = c.analysis_files()
    for aid in c.analyses:
        if aid not in bindings:
            r.append(
                _fail(
                    c.id,
                    2,
                    f"asm:{aid}",
                    f"declared in circuit.analyses but analyses/{aid}.yaml missing",
                )
            )
            continue
        for pdk in c.pdks:
            corners = _corner_names(c, pdk)
            if not corners:
                r.append(
                    _fail(c.id, 2, f"asm:{aid}@{pdk}", f"pdk/{pdk}/corners.yaml missing or empty")
                )
                continue
            for corner in corners:
                check = f"asm:{aid}@{pdk}/{corner}"
                try:
                    netlist = assemble(c, aid, pdk, corner)
                    NetlistView.from_string(netlist)  # must re-parse
                    r.append(_ok(c.id, 2, check))
                except AssembleError as exc:
                    r.append(_fail(c.id, 2, check, str(exc)))
                except Exception as exc:
                    r.append(_fail(c.id, 2, check, f"assembled netlist failed to parse: {exc}"))
    return r


def run_tier2(circuit_ids: list[str] | None = None) -> list[CheckResult]:
    ids = circuit_ids if circuit_ids is not None else model.list_circuit_ids()
    out: list[CheckResult] = []
    for cid in ids:
        c = model.load_circuit(cid)
        if c.is_reference_only:
            out.append(_skip(cid, 2, "asm:reference", "kind: reference — not assembled/lowered here"))
            continue
        out.extend(_tier2_circuit(c))
    return out


# --------------------------------------------------------------------------- Tier 3 (sim smoke)
#
# Runs every verifiable (circuit × applicable analysis × pdk × tt corner) natively through ngspice
# and classifies each cell. PDK-gated + OPT-IN: T3/T4 report a skip unless ``sim=True``
# AND the host carries ngspice + the PDK under ``$PDK_ROOT`` — so the per-PR fast gate (and any host
# without a PDK) stays green in seconds, while the PDK-equipped host / nightly job runs the full
# matrix ("T0–T2 per-PR, T3 nightly").
#
# Two-level contract (the same one the slow-suite T3 sweep proved at 0 hard-fails):
#   FAIL  — the deck did NOT run: a PDK lib/model/subckt didn't resolve, or a syntax error. A real
#           artifact bug (must be fixed). Deliberately NARROW + unambiguous.
#   SKIP  — recorded FLOOR: ngspice loaded + ran the deck but the baseline sizing didn't bias into a
#           working circuit (no finite measure — no convergence, W out of the model bin, all measures
#           failed/NaN). The reason carries the failed measures + a diagnostic snippet for triage.
#   PASS  — the deck ran and produced ≥1 finite (non-NaN) measure with no load error.
# Genuinely malformed decks can't reach here: Tier-2 re-parses every assembly and the byte-drift guard
# pins committed == freshly rendered. Per-metric NaN on an otherwise-converged cell is surfaced by
# Tier-4 (the metric is omitted → conformance skip), not by this smoke gate.

# LOAD-time failure markers — the deck didn't run. A degenerate baseline (binning "could not find a
# valid modelname" → "incomplete or empty netlist", a singular matrix, no convergence) is NOT here —
# those are floors (ngspice still loaded the deck), classified by "no finite measure" below.
_T3_LOAD_FAIL = re.compile(
    r"(could not find library|unknown subckt|syntax error|can't open|cannot open)", re.IGNORECASE
)
# Diagnostic lines worth surfacing in a floor's reason (sizing degeneracy vs a testbench bug).
_T3_DIAG = re.compile(
    r"(valid modelname|singular matrix|no convergence|timestep too small|gmin|source stepping|"
    r"incomplete or empty netlist|no such (?:vector|parameter|node)|out of |doesn't exist|"
    r"measure(?:ment)?\s.*fail|fatal|timed out)",
    re.IGNORECASE,
)


# (status, reason, measures) — measures kept for Tier-4 to reuse without re-simulating.
CellResult = tuple[Status, str, dict[str, float]]


def _sim_workers() -> int:
    """Thread-pool width for the native sim sweep. ``$ANALOG_DB_SIM_WORKERS`` overrides; default is
    a modest fraction of the host so a shared research server isn't saturated."""
    env = os.environ.get("ANALOG_DB_SIM_WORKERS", "")
    if env.isdigit() and int(env) > 0:
        return int(env)
    return max(1, min(16, os.cpu_count() or 4))


def _sim_cell(c: model.Circuit, aid: str, pdk: str, spice) -> CellResult:
    """Run one (analysis, pdk, tt) cell natively and classify it. Never raises — an assemble or
    runner failure becomes a fail row so the sweep always completes."""
    from .assemble import AssembleError, assemble
    from .runner import parse_measures

    try:
        netlist = assemble(c, aid, pdk, "tt")
    except AssembleError as exc:
        return ("fail", f"assemble failed: {exc}", {})
    except Exception as exc:  # noqa: BLE001 — any assembly error is a real finding
        return ("fail", f"assemble error: {type(exc).__name__}: {exc}", {})
    try:
        output = spice(netlist)
    except Exception as exc:  # noqa: BLE001 — a runner/subprocess failure is a finding, not a crash
        return ("fail", f"ngspice runner error: {type(exc).__name__}: {exc}", {})

    load_errs = [ln.strip() for ln in output.splitlines() if _T3_LOAD_FAIL.search(ln)]
    if load_errs:
        return ("fail", "deck did not run (load/lib/syntax): " + "; ".join(load_errs[:2]), {})
    measures, failed = parse_measures(output)
    finite = {k: v for k, v in measures.items() if math.isfinite(v)}
    if finite:
        return ("pass", "", measures)
    diag = next((ln.strip() for ln in output.splitlines() if _T3_DIAG.search(ln)), "")
    reason = "ran but no finite measure (recorded floor — baseline sizing does not bias)"
    if failed:
        reason += f"; failed meas: {sorted(set(failed))[:6]}"
    if diag:
        reason += f"; diag: {diag[:110]}"
    return ("skip", reason, measures)


def simulate_matrix(
    circuit_ids: list[str] | None = None, *, max_workers: int | None = None
) -> dict[str, dict[tuple[str, str], CellResult]]:
    """Simulate every verifiable (circuit × enabled analysis × installed-pdk × tt) cell natively,
    concurrently. Returns ``{circuit_id: {(analysis, pdk): CellResult}}`` — consumed by BOTH Tier-3
    (smoke status) and Tier-4 (conformance measures), so the sweep runs once per verify."""
    from . import runner as runmod

    ids = circuit_ids if circuit_ids is not None else model.list_circuit_ids()
    circuits: dict[str, model.Circuit] = {}
    runners: dict[str, object] = {}
    jobs: list[tuple[str, str, str]] = []
    for cid in ids:
        c = model.load_circuit(cid)
        if c.is_reference_only:
            continue
        circuits[cid] = c
        for pdk in c.pdks:
            if not runmod.native_pdk_available(pdk):
                continue
            if pdk not in runners:
                runners[pdk] = runmod.native_pdk_runner(pdk)
            for aid in c.analyses:
                if c.analysis(aid).get("enabled", True):
                    jobs.append((cid, aid, pdk))

    cache: dict[str, dict[tuple[str, str], CellResult]] = {}
    if not jobs:
        return cache

    def _do(job: tuple[str, str, str]) -> tuple[tuple[str, str, str], CellResult]:
        cid, aid, pdk = job
        return job, _sim_cell(circuits[cid], aid, pdk, runners[pdk])

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers or _sim_workers()) as ex:
        for (cid, aid, pdk), result in ex.map(_do, jobs):
            cache.setdefault(cid, {})[(aid, pdk)] = result
    return cache


def run_tier3(
    circuit_ids: list[str] | None = None,
    *,
    sim: bool = False,
    cache: dict[str, dict[tuple[str, str], CellResult]] | None = None,
) -> list[CheckResult]:
    from . import runner as runmod

    ids = circuit_ids if circuit_ids is not None else model.list_circuit_ids()
    out: list[CheckResult] = []
    if not sim:
        for cid in ids:
            out.append(
                _skip(
                    cid,
                    3,
                    "sim",
                    "opt-in: pass --sim on a host with ngspice + $PDK_ROOT "
                    f"({_TIER_LANDS[3]}, nightly cadence)",
                )
            )
        return out
    if cache is None:
        cache = simulate_matrix(ids)
    for cid in ids:
        c = model.load_circuit(cid)
        if c.is_reference_only:
            out.append(_skip(cid, 3, "sim:reference", "kind: reference — not simulated here"))
            continue
        cell = cache.get(cid, {})
        analyses = [a for a in c.analyses if c.analysis(a).get("enabled", True)]
        for pdk in c.pdks:
            if not runmod.native_pdk_available(pdk):
                for aid in analyses:
                    out.append(
                        _skip(cid, 3, f"sim:{aid}@{pdk}", f"PDK {pdk} not installed under $PDK_ROOT")
                    )
                continue
            for aid in analyses:
                st, reason, _m = cell.get((aid, pdk), ("skip", "cell not simulated", {}))
                out.append(CheckResult(cid, 3, f"sim:{aid}@{pdk}/tt", st, reason))
    return out


# --------------------------------------------------------------------------- Tier 4 (conformance)
#
# measured (the Tier-3 sim measures) vs the datasheet ``spec`` band (min/typ/max) — the oracle.
# Reuses ``ppa.metric_values`` (the SAME spec verdict the scoreboard records)
# so the conformance matrix is consistent with baseline entries. An out-of-spec metric is reported
# as a SKIP, not a fail: today's baselines are "runs, not tuned" and must not break the DB-wide
# verify (todo_examples_db Phase-7 note — the status ladder stops at ``simulated`` for them). A
# circuit reaches ``validated`` (derive_status) only when EVERY spec-bounded conformance row passes.


def _numeric_bound(x) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _has_spec_bound(spec: dict | None) -> bool:
    if not spec:
        return False
    return _numeric_bound(spec.get("min")) is not None or _numeric_bound(spec.get("max")) is not None


def _spec_str(spec: dict) -> str:
    lo, hi = spec.get("min"), spec.get("max")
    unit = spec.get("unit", "")
    if lo is not None and hi is not None:
        return f"[{lo}, {hi}] {unit}".strip()
    if lo is not None:
        return f">= {lo} {unit}".strip()
    return f"<= {hi} {unit}".strip()


def run_tier4(
    circuit_ids: list[str] | None = None,
    *,
    sim: bool = False,
    cache: dict[str, dict[tuple[str, str], CellResult]] | None = None,
) -> list[CheckResult]:
    from . import ppa
    from . import runner as runmod

    ids = circuit_ids if circuit_ids is not None else model.list_circuit_ids()
    out: list[CheckResult] = []
    if not sim:
        for cid in ids:
            out.append(
                _skip(
                    cid,
                    4,
                    "conform",
                    "opt-in: pass --sim (reuses Tier-3 measures) — datasheet-spec oracle, "
                    f"{_TIER_LANDS[4]}, nightly/release cadence",
                )
            )
        return out
    if cache is None:
        cache = simulate_matrix(ids)
    for cid in ids:
        c = model.load_circuit(cid)
        if c.is_reference_only:
            out.append(
                _skip(cid, 4, "conform:reference", "kind: reference — no datasheet spec oracle")
            )
            continue
        metrics = (
            c.datasheet().get("metrics", {}) if (c.dir / "datasheet.yaml").is_file() else {}
        )
        bounded = {n: s for n, s in metrics.items() if _has_spec_bound((s or {}).get("spec"))}
        if not bounded:
            out.append(_skip(cid, 4, "conform", "no spec-bounded datasheet metric to check"))
            continue
        cell = cache.get(cid, {})
        avail = [p for p in c.pdks if runmod.native_pdk_available(p)]
        if not avail:
            out.append(_skip(cid, 4, "conform", "no installed PDK to simulate against"))
            continue
        for pdk in avail:
            ablock: dict[str, dict] = {}
            for (aid, ppdk), (st, _r, meas) in cell.items():
                if ppdk == pdk:
                    ablock[aid] = {"status": "ok" if st == "pass" else "sim_error", "measures": meas}
            values = ppa.metric_values(c, ablock)  # {metric: {value, spec verdict}}
            for name, mspec in bounded.items():
                spec = mspec.get("spec") or {}
                check = f"conform:{name}@{pdk}"
                if name not in values:
                    out.append(
                        _skip(
                            cid,
                            4,
                            check,
                            f"no clean measure (analysis {mspec.get('analysis')!r} did not extract "
                            f"{(mspec.get('extract') or {}).get('meas')!r})",
                        )
                    )
                    continue
                val, verdict = values[name]["value"], values[name]["spec"]
                if verdict == "pass":
                    out.append(_ok(cid, 4, check))
                else:  # out of spec — recorded, but NOT a gate (untuned baseline)
                    out.append(
                        _skip(
                            cid,
                            4,
                            check,
                            f"{name}={val:.4g} outside spec {_spec_str(spec)} "
                            "(untuned baseline — recorded, not a verify gate)",
                        )
                    )
    return out


# --------------------------------------------------------------------------- driver


def run(
    tiers: list[int] | None = None,
    circuit_ids: list[str] | None = None,
    *,
    sim: bool = False,
) -> list[CheckResult]:
    """Run the requested tiers (default: all). T3/T4 report skip unless ``sim=True`` on a host with
    ngspice + ``$PDK_ROOT``. When both sim tiers run, the native sweep executes
    once and both tiers read its measures."""
    selected = tiers if tiers is not None else list(TIERS)
    out: list[CheckResult] = []
    cache: dict[str, dict[tuple[str, str], CellResult]] | None = None
    if sim and any(t in (3, 4) for t in selected):
        cache = simulate_matrix(circuit_ids)
    for t in selected:
        if t == 0:
            out.extend(run_tier0(circuit_ids))
        elif t == 1:
            out.extend(run_tier1(circuit_ids))
        elif t == 2:
            out.extend(run_tier2(circuit_ids))
        elif t == 3:
            out.extend(run_tier3(circuit_ids, sim=sim, cache=cache))
        elif t == 4:
            out.extend(run_tier4(circuit_ids, sim=sim, cache=cache))
    return out


def derive_status(circuit_id: str, results: list[CheckResult]) -> str:
    """Highest tier a circuit fully clears → its derived status.

    A kind: reference circuit is terminal at ``reference`` once its T0 subset is clean —
    it is never lowered or simulated here, so the tier ladder does not apply."""
    try:
        if model.load_circuit(circuit_id).is_reference_only:
            t0 = [r for r in results if r.circuit == circuit_id and r.tier == 0]
            return "reference" if t0 and not any(r.status == "fail" for r in t0) else "incomplete"
    except KeyError:
        pass
    status = "draft"
    for t in (0, 1, 2, 3, 4):
        rows = [r for r in results if r.circuit == circuit_id and r.tier == t]
        if not rows or any(r.status == "fail" for r in rows):
            break
        if all(r.status == "skip" for r in rows):
            break
        if t == 4:
            # ``validated`` is a strong claim: every spec-bounded conformance row must PASS. An
            # out-of-spec metric is a skip (§ T4), so a mix of pass+skip (an untuned baseline that
            # happens to meet some specs) must NOT graduate to validated — it stops at simulated.
            conform = [r for r in rows if r.check.startswith("conform:") and "@" in r.check]
            if not conform or any(r.status != "pass" for r in conform):
                break
        status = _TIER_STATUS[t]
    return status


def summarize(results: list[CheckResult]) -> dict[str, int]:
    out = {"pass": 0, "fail": 0, "skip": 0}
    for r in results:
        out[r.status] += 1
    return out
