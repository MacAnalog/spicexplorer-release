"""Every testbench template a class ``metrics.yaml`` lists resolves, and the universal set holds no
dead template.

A class's ``templates:`` list is the analysis vocabulary its circuits may opt into
(``class.schema.json``). An id there resolves when the bench exists on one of the two lanes, the
same test the platform's library service (``spicexplorer_api.services.library_db._tb_profile``)
applies:

* **ngspice**: ``model.resolve_template`` finds a ``.spice`` file, class-scoped first, then the
  universal ``_shared/testbench-templates/`` set;
* **spectre**: the class's ``spectre-benches.yaml`` has a ``benches:`` entry for the id (the
  Spectre-only PSS/PAC benches, such as ia's ``pac_gain``, have no ``.spice`` template by design).

The second guard is for the universal set. A universal template that no circuit analysis resolves
is dead: every class that runs it shadows it with its own copy, or nobody binds it. The
supply-only universal ``dc_op.spice`` was such a file. ``support``, the only class that used it
(it has no copy of its own, so resolve_template returned the universal file), listed it without
any member binding it, so the listed id and the dead file each
made the other look in use. Both were retired together (RET-DCOP, 2026-09).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from spicexplorer_analog_db import model, paths

# Classes whose `templates:` list is analysis VOCABULARY only, with no bench on either lane yet.
# drv is the first bipolar/RF class: its circuits run self-contained probe decks through the
# optimizer projection, and the class templates wait for the bipolar assembler (drv_001's
# circuit.yaml: "analyses is []", feasibility gap 4.4). The self-check below fails as soon as an
# entry starts resolving or a drv circuit declares an analysis, so this list cannot go stale.
_VOCABULARY_ONLY: dict[str, frozenset[str]] = {
    "drv": frozenset(
        {"dc_bias", "ac_gain_lsb", "ac_gain_msb", "ac_s11", "ac_s22", "tran_swing", "tran_eye"}
    ),
}


def _class_ids() -> list[str]:
    # not model.list_class_ids(): it is lru_cached, and the synthetic trees below swap the root
    root = paths.classes_root()
    return sorted(p.parent.name for p in root.glob("*/metrics.yaml"))


def _spectre_benches(class_id: str) -> set[str]:
    f = paths.classes_root() / class_id / "spectre-benches.yaml"
    if not f.is_file():
        return set()
    return set(((yaml.safe_load(f.read_text()) or {}).get("benches") or {}))


def unresolved_class_templates() -> list[tuple[str, str]]:
    """``(class, template id)`` for every listed id that has no ngspice template and no Spectre
    bench entry."""
    gaps: list[tuple[str, str]] = []
    for klass in _class_ids():
        benches = _spectre_benches(klass)
        for tid in model.class_templates(klass):
            if model.resolve_template(klass, tid) is None and tid not in benches:
                gaps.append((klass, tid))
    return gaps


def dead_universal_templates(bindings: list[tuple[str, str]]) -> list[str]:
    """Universal templates that none of the ``(class, template id)`` bindings resolves to. A
    shadowed file counts as dead: the class copy is always found first."""
    used = {model.resolve_template(klass, tid) for klass, tid in bindings}
    return sorted(p.stem for p in paths.shared_templates_root().glob("*.spice") if p not in used)


def _corpus_bindings() -> list[tuple[str, str]]:
    # every analysis descriptor on disk (declared or not, enabled or not): anything that could
    # be bound keeps its template out of the dead list
    return [
        (c.klass, str((c.analysis(aid) or {}).get("template", aid)))
        for c in model.load_all_circuits()
        for aid in c.analysis_files()
    ]


# ─────────────────────────────── the corpus ───────────────────────────────


def test_every_class_template_resolves():
    gaps = [(k, t) for k, t in unresolved_class_templates() if t not in _VOCABULARY_ONLY.get(k, ())]
    assert not gaps, (
        "class metrics.yaml lists templates with no .spice template (class or universal) and no "
        f"spectre-benches.yaml row: {gaps}"
    )


def test_closed_lane_benches_resolve_through_the_spectre_map():
    # ia's PSS/PAC benches have no .spice file; they must still count as resolved
    assert model.resolve_template("ia", "pac_gain") is None
    assert "pac_gain" in _spectre_benches("ia")
    assert ("ia", "pac_gain") not in unresolved_class_templates()


@pytest.mark.corpus
def test_vocabulary_only_allowlist_is_still_needed():
    gaps = set(unresolved_class_templates())
    for klass, ids in _VOCABULARY_ONLY.items():
        assert klass in _class_ids(), f"{klass}: allowlisted class no longer exists"
        now_resolved = sorted(t for t in ids if (klass, t) not in gaps)
        assert not now_resolved, (
            f"{klass}: {now_resolved} resolve now; drop them from the allowlist"
        )
        not_listed = sorted(ids - set(model.class_templates(klass)))
        assert not not_listed, (
            f"{klass}: allowlist names ids the class no longer lists: {not_listed}"
        )
        binders = [c.id for c in model.load_all_circuits() if c.klass == klass and c.analyses]
        assert not binders, (
            f"{klass}: {binders} declare analyses, so the class vocabulary is no longer "
            "vocabulary-only; give those templates a bench instead of allowlisting them"
        )


@pytest.mark.corpus
def test_no_dead_universal_template():
    dead = dead_universal_templates(_corpus_bindings())
    assert not dead, (
        f"_shared/testbench-templates/ holds templates no circuit analysis resolves to: {dead} "
        "(shadowed by every class that runs them, or bound by nobody)"
    )


def test_support_class_lists_no_dc_op_and_no_universal_dc_op_exists():
    assert "dc_op" not in model.class_templates("support")
    assert not (paths.shared_templates_root() / "dc_op.spice").exists()


# ─────────────────────── the guards on synthetic trees ───────────────────────


def _put(root: Path, rel: str, text: str = "* template\n") -> None:
    f = root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text)


@pytest.fixture()
def db(tmp_path, monkeypatch) -> Path:
    monkeypatch.setenv(paths.ENV_VAR, str(tmp_path))
    (tmp_path / "circuits").mkdir()
    return tmp_path


def _metrics(klass: str, templates: list[str]) -> str:
    return yaml.safe_dump(
        {
            "schema": "spicexplorer/class@1",
            "class": klass,
            "canonical_metrics": ["i_supply"],
            "templates": templates,
        }
    )


def test_guard_names_only_the_unbacked_id(db):
    _put(
        db,
        "_shared/classes/foo/metrics.yaml",
        _metrics("foo", ["own", "shared", "closed", "missing"]),
    )
    _put(db, "_shared/classes/foo/testbench-templates/own.spice")
    _put(db, "_shared/testbench-templates/shared.spice")
    _put(
        db,
        "_shared/classes/foo/spectre-benches.yaml",
        yaml.safe_dump(
            {
                "schema": "spicexplorer/spectre-benches@1",
                "class": "foo",
                "benches": {"closed": {"analyses": [{"template": "pss"}]}},
            }
        ),
    )
    assert unresolved_class_templates() == [("foo", "missing")]


def test_guard_catches_a_listed_template_whose_universal_file_was_deleted(db):
    # the RET-DCOP half-done state: the universal file is gone, the class still lists the id
    _put(db, "_shared/classes/support/metrics.yaml", _metrics("support", ["dc_op", "dc_vcm_sense"]))
    _put(db, "_shared/classes/support/testbench-templates/dc_vcm_sense.spice")
    assert unresolved_class_templates() == [("support", "dc_op")]


def test_a_spectre_map_of_another_class_does_not_resolve_this_one(db):
    _put(db, "_shared/classes/foo/metrics.yaml", _metrics("foo", ["closed"]))
    _put(db, "_shared/classes/bar/metrics.yaml", _metrics("bar", ["closed"]))
    _put(
        db,
        "_shared/classes/bar/spectre-benches.yaml",
        yaml.safe_dump({"benches": {"closed": {"analyses": []}}}),
    )
    assert unresolved_class_templates() == [("foo", "closed")]


def test_dead_universal_guard_flags_a_shadowed_and_an_unbound_template(db):
    _put(db, "_shared/testbench-templates/used.spice")
    _put(db, "_shared/testbench-templates/shadowed.spice")  # every binder has its own copy
    _put(db, "_shared/testbench-templates/unbound.spice")  # nobody binds it
    _put(db, "_shared/classes/amp/testbench-templates/shadowed.spice")
    bindings = [("amp", "used"), ("amp", "shadowed"), ("ldo", "used")]
    assert dead_universal_templates(bindings) == ["shadowed", "unbound"]
    # a class WITHOUT its own copy keeps the universal file in use
    assert dead_universal_templates(bindings + [("ldo", "shadowed")]) == ["unbound"]
