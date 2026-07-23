#!/usr/bin/env python
"""One-shot P4 catalog migration to the atomic params layer.

For each verifiable circuit this helper mechanically:

1. reads the committed ``abstract/topology.cgraph.json`` (the cgraph records every card's
   parameter values) and maps device-field → legacy symbol / literal / ``base*N`` expression;
2. re-authors ``abstract/netlist.spice`` atomically (``x_dut_<inst>_<field>`` on every
   MOS geometry field and on SHARED passive values; numeric literals like ``m=1`` are
   symbolized; UNIQUE passive knobs and V/I bias-source values — ``i_tail``, ``vref_val``,
   ``'c_comp'`` — are already atomic first-class knobs and stay untouched);
3. derives ``groups:`` FROM today's sharing — devices sharing one legacy symbol for a field
   become one group tying that field (member sets sharing several fields merge into one
   multi-field group); ``kind`` is the structural detector's match when one covers exactly the
   member set (``matched_pair`` / ``mirror_length`` via ``params.py``), else
   ``shared_geometry`` (the vocabulary's legacy-global-tie case). AnalogGym ``base*N``
   m-arithmetic lowers to frozen ``ratios:`` entries against a multiplier-1 anchor;
4. re-keys every ``pdk/<pdk>/sizing.yaml`` legacy→atomic (values/bounds/descriptions
   unchanged; anchors with a non-1 multiplier get their default scaled — reported), appends
   frozen rows for the newly-symbolized literals, and re-keys recorded
   ``scoreboard/<pdk>/*.json`` sizing params;
5. regenerates the committed artifacts (cgraph, pdk netlists, ``raw/`` decks) and asserts
   NUMERIC PARITY of every ``raw/<cid>/<pdk>/_dut.spice`` against the pre-migration snapshot
   ``tests/data/premigration_dut_geometry.json`` (also the committed parity-test fixture),
   plus the Tier-1 D-6 params checks.

Usage (from the analog-db root, platform venv on PYTHONPATH=src):

    python tools/migrate_params.py <circuit_id> [<circuit_id> …] [--dry-run]
    python tools/migrate_params.py --all-remaining [--dry-run]

Deliberately a dev tool, not a CLI subcommand: it edits AUTHORED artifacts and exists for the
one-time P4 sweep; keep it for archaeology, don't wire it into the package.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

from spicexplorer_analog_db import export, generate, model, params, ppa, verify

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tests" / "data" / "premigration_dut_geometry.json"

_MULT = re.compile(r"^(?:([A-Za-z_]\w*)\*(\d+)|(\d+)\*([A-Za-z_]\w*))$")
_FIELD_ORDER = {"w": 0, "l": 1, "m": 2, "ng": 3, "Value": 4}


def parse_value(v):
    """Graph param value → ('lit', num) | ('sym', base, mult) | ('expr', raw)."""
    if isinstance(v, (int, float)):
        return ("lit", v)
    s = str(v).strip()
    if len(s) >= 2 and s.startswith("'") and s.endswith("'"):
        s = s[1:-1].strip()
    if params._SYMBOL_RE.match(s):
        return ("sym", s, 1)
    m = _MULT.match(s)
    if m:
        return ("sym", m.group(1) or m.group(4), int(m.group(2) or m.group(3)))
    return ("expr", str(v))


def _scale_token(tok: str, scale: int) -> str:
    """Scale a sizing eng-token (``1u`` → ``2u``, ``1`` → ``4``) by an integer factor."""
    s = str(tok).strip().strip("'\"")
    m = re.match(r"^([-+0-9.eE]+)([A-Za-z]*)$", s)
    val = float(m.group(1)) * scale
    return f"{val:g}{m.group(2)}"


def _field_sort(fields):
    return sorted(set(fields), key=lambda f: (_FIELD_ORDER.get(f, 9), f))


def plan_migration(c, graph):
    """Everything derivable before touching a file. Returns a dict plan or raises."""
    comps = {cm["id"]: cm for cm in graph["components"]}
    lines = (c.dir / "abstract" / "netlist.spice").read_text().splitlines()

    order, line_of = [], {}
    for i, ln in enumerate(lines):
        stripped = ln.strip()
        if not stripped or stripped.startswith("*") or stripped.startswith("."):
            continue
        inst = stripped.split()[0].upper()
        if inst in comps and inst not in line_of:
            line_of[inst] = i
            order.append(inst)
    missing = set(comps) - set(order)
    if missing:
        raise RuntimeError(f"{c.id}: cards not found in netlist for {sorted(missing)}")
    pos = {inst: k for k, inst in enumerate(order)}

    shared: dict[tuple, list] = {}   # (field, base) -> [(inst, mult)] in netlist order
    mos_renames: dict[str, dict] = {}
    frozen: list[tuple] = []         # (inst, field, int_literal)
    notes: list[str] = []

    for inst in order:
        comp = comps[inst]
        if comp.get("device_type") != "MOS":
            continue
        for field in sorted(comp.get("params") or {}):
            v = comp["params"][field]
            kind = parse_value(v)
            mos_renames.setdefault(inst, {})[field] = params.atomic_symbol(inst, field)
            if kind[0] == "lit":
                if float(kind[1]) != int(kind[1]):
                    raise RuntimeError(f"{c.id}: non-integer literal {inst}.{field}={v}")
                frozen.append((inst, field, int(kind[1])))
            elif kind[0] == "sym":
                shared.setdefault((field, kind[1]), []).append((inst, kind[2]))
            else:
                raise RuntimeError(f"{c.id}: unmigratable expression {inst}.{field}={v!r}")

    # ---- passives: atomize only SHARED value symbols; sources (V/I) always untouched ----
    passive_users: dict[str, list] = {}
    for inst in order:
        comp = comps[inst]
        if comp.get("device_type") in ("MOS", "VSOURCE", "ISOURCE"):
            continue
        for field in sorted(comp.get("params") or {}):
            k = params.knob_symbol(comp["params"][field])
            if k:
                passive_users.setdefault(k, []).append((inst, field))
    passive_renames: dict[str, dict] = {}
    passive_groups: list[dict] = []
    siz_rename: dict[str, tuple] = {}  # legacy -> (new, scale)
    for base, users in passive_users.items():
        if len(users) < 2:
            continue
        fields = {f for _, f in users}
        if len(fields) != 1:
            raise RuntimeError(f"{c.id}: passive base {base} spans fields {fields}")
        field = next(iter(fields))
        members = [i for i, _ in users]
        for inst in members:
            passive_renames.setdefault(inst, {})[field] = params.atomic_symbol(inst, field)
        siz_rename[base] = (params.atomic_symbol(members[0], field), 1)
        passive_groups.append(
            {
                "name": f"shared_{members[0].lower()}_{field.lower()}",
                "kind": "shared_geometry",
                "members": members,
                "tie": [field],
                "description": f"Mechanically derived from today's sharing (P4 sweep) - "
                f"legacy symbol(s): {base} ({field}).",
            }
        )

    # ---- MOS sharing -> groups / ratios / renamed sizing keys ----
    tie_entries: dict[tuple, dict] = {}
    ratios: list[dict] = []
    for (field, base), users in shared.items():
        users = sorted(users, key=lambda u: pos[u[0]])
        if len(users) == 1 and users[0][1] == 1:
            siz_rename[base] = (params.atomic_symbol(users[0][0], field), 1)
            continue
        if all(m == 1 for _, m in users):
            members = tuple(i for i, _ in users)
            e = tie_entries.setdefault(members, {"fields": [], "legacy": []})
            e["fields"].append(field)
            e["legacy"].append((base, field))
            continue
        anchors = [i for i, m in users if m == 1]
        anchor = anchors[0] if anchors else users[0][0]
        amult = 1 if anchors else users[0][1]
        for inst, mult in users:
            if inst == anchor:
                continue
            fr = Fraction(mult, amult)
            ratios.append(
                {
                    "param": field,
                    "ref": inst,
                    "of": anchor,
                    "ratio": int(fr) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}",
                    "description": f"Legacy {base}*{mult} vs anchor {anchor} (*{amult}), frozen (P4 sweep).",
                }
            )
        siz_rename[base] = (params.atomic_symbol(anchor, field), amult)
        if amult != 1:
            notes.append(
                f"SCALED ANCHOR: {base} -> {params.atomic_symbol(anchor, field)} "
                f"(no multiplier-1 member; sizing default x{amult})"
            )

    pairs = {frozenset((p.a, p.b)) for p in params.detect_matched_pairs(graph)}
    mirrors = {frozenset((m.ref, *m.outputs)): m.ref for m in params.detect_mirrors(graph)}
    groups: list[dict] = []
    for members, e in sorted(tie_entries.items(), key=lambda kv: pos[kv[0][0]]):
        mset = frozenset(members)
        fields = _field_sort(e["fields"])
        members = list(members)
        if mset in mirrors and "l" in fields:
            ref = mirrors[mset]
            members = [ref] + [m for m in members if m != ref]
            kind, name = "mirror_length", f"mirror_{ref.lower()}_{'_'.join(fields)}"
        elif mset in pairs and len(members) == 2:
            kind, name = "matched_pair", f"pair_{members[0].lower()}_{members[1].lower()}"
        else:
            kind, name = "shared_geometry", f"shared_{members[0].lower()}_{'_'.join(fields)}"
        legacy = ", ".join(f"{b} ({f})" for b, f in sorted(e["legacy"], key=lambda t: _FIELD_ORDER.get(t[1], 9)))
        groups.append(
            {
                "name": name,
                "kind": kind,
                "members": members,
                "tie": fields,
                "description": f"Mechanically derived from today's sharing (P4 sweep) - "
                f"legacy symbol(s): {legacy}.",
            }
        )
        for base, field in e["legacy"]:
            siz_rename[base] = (params.atomic_symbol(members[0], field), 1)

    ratios.sort(key=lambda r: (r["param"], pos[r["of"]], pos[r["ref"]]))
    return {
        "lines": lines,
        "comps": comps,
        "order": order,
        "line_of": line_of,
        "mos_renames": mos_renames,
        "passive_renames": passive_renames,
        "frozen": frozen,
        "groups": groups + passive_groups,
        "ratios": ratios,
        "siz_rename": siz_rename,
        "notes": notes,
    }


def rewrite_netlist(c, plan) -> None:
    lines = list(plan["lines"])
    for inst, fmap in {**plan["mos_renames"]}.items():
        i = plan["line_of"][inst]
        ln = lines[i]
        for field, newsym in fmap.items():
            pat = re.compile(rf"(?i)\b{field}\s*=\s*('[^']*'|\{{[^}}]*\}}|[^\s]+)")
            ln, n = pat.subn(f"{field}={newsym}", ln, count=1)
            if n != 1:
                raise RuntimeError(f"{c.id}: could not rewrite {inst}.{field} on line: {lines[i]}")
        lines[i] = ln
    for inst, fmap in plan["passive_renames"].items():
        i = plan["line_of"][inst]
        ln = lines[i]
        for field, newsym in fmap.items():
            old = str(plan["comps"][inst]["params"][field])
            if old.startswith("'"):
                new_ln = ln.replace(old, f"'{newsym}'", 1)
            else:
                new_ln = re.sub(rf"(?<![\w'.]){re.escape(old)}(?![\w'])", newsym, ln, count=1)
            if new_ln == ln:
                raise RuntimeError(f"{c.id}: could not rewrite {inst}.{field} on line: {ln}")
            ln = new_ln
        lines[i] = ln
    (c.dir / "abstract" / "netlist.spice").write_text("\n".join(lines) + "\n")


_FROZEN_HEADER = (
    "{ind}# Frozen per-device literals (P4 atomic sweep): defaults reproduce the authored\n"
    "{ind}# netlist literals exactly; freeze keeps them out of the search space.\n"
)


def rewrite_sizing(c, plan) -> list[str]:
    """Re-key legacy symbols + append frozen literal rows in every pdk sizing.yaml."""
    warnings: list[str] = []
    for pdk in c.pdks:
        p = c.dir / "pdk" / pdk / "sizing.yaml"
        text = p.read_text()
        for old, (new, scale) in plan["siz_rename"].items():
            text, n = re.subn(rf"(?<![\w-]){re.escape(old)}(?![\w])", new, text)
            if n == 0:
                warnings.append(f"{pdk}: legacy symbol {old} not found in sizing.yaml")
            if scale != 1:
                block = re.search(rf"- name: {re.escape(new)}\n((?:\s+\w+:[^\n]*\n)*)", text)
                if not block:
                    raise RuntimeError(f"{c.id}@{pdk}: cannot locate row {new} to scale x{scale}")
                row = block.group(0)
                drow = re.sub(
                    r"(default:\s*)([^\s#]+)",
                    lambda m: m.group(1) + _scale_token(m.group(2), scale),
                    row,
                    count=1,
                )
                text = text.replace(row, drow, 1)
                warnings.append(f"{pdk}: {new} default scaled x{scale} (anchor multiplier)")
        if plan["frozen"]:
            item = re.search(r"(?m)^([ \t]*)- ", text.split("variables:", 1)[1])
            ind = item.group(1) if item else ""
            rows = _FROZEN_HEADER.format(ind=ind)
            for inst, field, lit in plan["frozen"]:
                name = params.atomic_symbol(inst, field)
                mx = max(16, lit)
                rows += (
                    f'{ind}- {{name: {name}, description: "{inst} {field} (frozen literal)", '
                    f"default: {lit}, min: 1, max: {mx}, freeze: true, is_integer: true}}\n"
                )
            lines = text.splitlines(keepends=True)
            at = len(lines)
            for i, ln in enumerate(lines):
                if re.match(r"^analysis_params:", ln):
                    at = i
                    while at > 0 and lines[at - 1].lstrip().startswith("#"):
                        at -= 1
                    break
            lines.insert(at, rows)
            text = "".join(lines)
        p.write_text(text)
    return warnings


def rewrite_scoreboards(c, plan) -> None:
    for p in sorted((c.dir / "scoreboard").glob("*/*.json")):
        text = p.read_text()
        for old, (new, scale) in plan["siz_rename"].items():
            if scale != 1:
                # recorded design point: the anchor knob's value is the legacy value x scale
                def _rekey(m, _new=new, _scale=scale):
                    q, val = m.group(1), m.group(2)
                    num = ppa.parse_eng(val)
                    return f'"{_new}": {q}{num * _scale:g}{q}'

                text = re.sub(rf'"{re.escape(old)}":\s*("?)([^",\n]+)\1', _rekey, text)
            else:
                text = text.replace(f'"{old}"', f'"{new}"')
        p.write_text(text)


def check_parity(c, snapshot) -> list[str]:
    errs: list[str] = []
    for pdk, old in snapshot.get(c.id, {}).items():
        new = ppa.resolve_deck_geometry(export.dut_path(c, pdk).read_text())
        if set(new) != set(old):
            errs.append(f"{pdk}: device set changed {sorted(set(new) ^ set(old))}")
            continue
        for dev, fields in old.items():
            if set(new[dev]) != set(fields):
                errs.append(f"{pdk}:{dev}: field set {sorted(set(new[dev]) ^ set(fields))}")
                continue
            for f, v in fields.items():
                nv = new[dev][f]
                if abs(nv - v) > abs(v) * 1e-9:
                    errs.append(f"{pdk}:{dev}.{f}: {v} -> {nv}")
    return errs


def migrate(cid: str, snapshot, dry_run: bool = False) -> bool:
    c = model.load_circuit(cid)
    if c.is_reference_only:
        print(f"  skip  {cid} — kind: reference")
        return True
    if (c.dir / "abstract" / "params.yaml").is_file():
        print(f"  skip  {cid} — already adopted params.yaml")
        return True
    graph = params.load_graph(c.dir / "abstract" / "topology.cgraph.json")
    plan = plan_migration(c, graph)
    print(f"== {cid}: {len(plan['groups'])} group(s), {len(plan['ratios'])} ratio(s), "
          f"{len(plan['frozen'])} frozen literal(s), {len(plan['siz_rename'])} sizing re-key(s)")
    for g in plan["groups"]:
        print(f"   group {g['name']:32s} {g['kind']:16s} tie={g['tie']} members={g['members']}")
    for n in plan["notes"]:
        print(f"   NOTE  {n}")
    if dry_run:
        return True

    rewrite_netlist(c, plan)
    warnings = rewrite_sizing(c, plan)
    rewrite_scoreboards(c, plan)
    generate.write_generated(c)

    c = model.load_circuit(cid)  # reload: sizing/netlist changed
    newgraph = params.load_graph(c.dir / "abstract" / "topology.cgraph.json")
    authored = {}
    if plan["groups"]:
        authored["groups"] = plan["groups"]
    if plan["ratios"]:
        authored["ratios"] = plan["ratios"]
    doc = params.refresh_params_doc(authored, newgraph)
    (c.dir / "abstract" / "params.yaml").write_text(params.render_params_yaml(doc, cid))

    ok = True
    free = params.free_symbols(doc)
    for pdk in c.pdks:
        names = {v["name"] for v in c.sizing(pdk).get("variables", [])}
        if names != free:
            ok = False
            print(f"   FAIL {pdk}: sizing != free knobs: only-sizing={sorted(names - free)} "
                  f"only-free={sorted(free - names)}")
    export.write_all([cid])
    for err in check_parity(c, snapshot):
        ok = False
        print(f"   PARITY FAIL {err}")
    for r in verify._tier1_params_checks(c):
        if r.status == "fail":
            ok = False
            print(f"   T1 FAIL {r.check}: {r.reason}")
        elif r.status == "skip":
            print(f"   T1 warn {r.check}: {r.reason}")
    for w in warnings:
        print(f"   WARN {w}")
    print(f"   {'OK' if ok else 'FAILED'}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("circuits", nargs="*")
    ap.add_argument("--all-remaining", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    snapshot = json.loads(SNAPSHOT.read_text())
    ids = args.circuits or (model.list_circuit_ids() if args.all_remaining else [])
    if not ids:
        ap.error("give circuit ids or --all-remaining")
    ok = True
    for cid in ids:
        ok = migrate(cid, snapshot, dry_run=args.dry_run) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
