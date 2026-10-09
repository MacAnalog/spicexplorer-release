"""The analog-db ``meas`` names that the Tier-1 registry does not define — MEASURED, not guessed.

``CircuitRun.evaluate()`` degrades an unmeasurable metric to ``NaN`` + a WARNING instead of
aborting the bench (O-2b). The commit that landed that guard described the fallout as two
circuits and one metric name (``amp_023_fer_fd2s`` / ``amp_020`` declare ``vos``) and framed
the sweep as an FD-only follow-up. Re-measuring the whole corpus put the real scope roughly
two orders of magnitude higher, and mostly on SINGLE-ENDED circuits — a hand-off note that
says "add one registry entry" sends the next agent down the wrong path.

This test re-derives every number in ``doc/TODO.md`` §21 from the corpus itself, so the
tracker cannot silently rot:

* it FAILS if the retracted framing is ever restored (the assertions below are all
  incompatible with "2 circuits / 1 name / FD-only");
* it never switches itself off: at the analog-db commit the numbers were measured at, every
  figure must match exactly; at any OTHER commit (a re-pin, or git unable to say) the figures
  may move (that is a §21 doc edit, not a code failure), but the gap may not GROW past the
  committed ``non_registry_metrics``. A commit mismatch used to be a skip, so every re-pin
  turned the guard off unnoticed (it sat skipped from ``ed4d7c48`` to ``8ca247de`` while the
  gap grew from 224 to 342);
* it SKIPS only when ``examples/analog-db`` is not checked out at all.

Nothing here modifies analog-db: it is a nested submodule with its own review.
"""

from __future__ import annotations

import collections
import dataclasses
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml
from spicexplorer_core.measurements.registry import _EXTENSIONS, _MEAS_TABLE


@dataclass(frozen=True)
class _Scope:
    """The measured snapshot of the registry gap over one analog-db checkout."""

    registry_names: int = 0
    circuits: int = 0
    non_registry_metrics: int = 0
    circuits_affected: int = 0
    distinct_names: int = 0
    single_ended_metrics: int = 0
    differential_metrics: int = 0
    fd_circuits: int = 0
    fd_circuits_affected: int = 0
    names: collections.Counter[str] = field(default_factory=collections.Counter)

    def figures(self) -> dict[str, int]:
        """Just the counts quoted in the docs (the `names` histogram is context, not a figure)."""
        return {k: v for k, v in vars(self).items() if k != "names"}


#: The analog-db commit ``doc/TODO.md`` §21's table was measured at.
MEASURED_AT = "def1e3dc"

#: The measured snapshot — every figure quoted in ``doc/TODO.md`` §21 and in
#: ``CircuitRun.evaluate()``'s docstring. ``non_registry_metrics`` is also the gap's
#: ceiling at every other analog-db commit.
EXPECTED = {
    "registry_names": 62,
    "circuits": 85,
    "non_registry_metrics": 342,
    "circuits_affected": 68,
    "distinct_names": 89,
    "single_ended_metrics": 264,
    "differential_metrics": 78,
    "fd_circuits": 19,
    "fd_circuits_affected": 16,
}

_ADB = Path(__file__).resolve().parents[3] / "examples" / "analog-db"


def _corpus_root() -> Path:
    circuits = _ADB / "circuits"
    if not circuits.is_dir():
        pytest.skip("examples/analog-db submodule not checked out")
    return circuits


def _corpus_head() -> str | None:
    """The analog-db commit (8-char short sha), or None when git cannot resolve it.

    An export (``git archive``, as ``make ci-local`` ships it) has no ``.git``: it gives None too,
    even when it sits inside another repo's work tree, where ``git -C`` would otherwise walk up
    and answer with that repo's commit."""
    if not (_ADB / ".git").exists():
        return None
    try:
        return subprocess.run(
            ["git", "-C", str(_ADB), "rev-parse", "--short=8", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _is_differential(circuit_dir: Path) -> bool:
    """Mirror ``analog_db.differential_output``: a ``voutp``/``voutn`` pair and no ``vout``."""
    manifest = circuit_dir / "circuit.yaml"
    if not manifest.is_file():
        return False
    ports = (yaml.safe_load(manifest.read_text()) or {}).get("ports") or []
    lows = {str(p).lower() for p in ports}
    return "voutp" in lows and "voutn" in lows and "vout" not in lows


def _core_names() -> set[str]:
    """The Tier-1 registry that §21 refers to: the built-in names only.

    A downstream family (the waveview eye) joins ``_MEAS_TABLE`` when its module is imported, and
    ``CircuitRun.evaluate`` never imports it — so counting the live table would make the figures
    depend on which test ran first in the same worker."""
    return {name for name, (kind, _required) in _MEAS_TABLE.items() if kind not in _EXTENSIONS}


def _measure(root: Path | None = None) -> _Scope:
    root = root if root is not None else _corpus_root()
    canonical = _core_names()
    circuits = sorted(p for p in root.iterdir() if p.is_dir())

    names: collections.Counter[str] = collections.Counter()
    affected: set[str] = set()
    fd_all: set[str] = set()
    fd_affected: set[str] = set()
    single_ended = differential = 0

    for circuit in circuits:
        datasheet = circuit / "datasheet.yaml"
        if not datasheet.is_file():
            continue
        diff = _is_differential(circuit)
        if diff:
            fd_all.add(circuit.name)
        metrics = (yaml.safe_load(datasheet.read_text()) or {}).get("metrics") or {}
        for metric in metrics.values():
            meas = ((metric or {}).get("extract") or {}).get("meas")
            if meas is None or meas in canonical:
                continue
            names[meas] += 1
            affected.add(circuit.name)
            if diff:
                differential += 1
                fd_affected.add(circuit.name)
            else:
                single_ended += 1

    return _Scope(
        registry_names=len(canonical),
        circuits=len(circuits),
        non_registry_metrics=sum(names.values()),
        circuits_affected=len(affected),
        distinct_names=len(names),
        single_ended_metrics=single_ended,
        differential_metrics=differential,
        fd_circuits=len(fd_all),
        fd_circuits_affected=len(fd_affected),
        names=names,
    )


def _assert_on_record(scope: _Scope, head: str | None) -> None:
    """The guard: every §21 figure at ``MEASURED_AT``, the gap's ceiling everywhere else."""
    if head == MEASURED_AT:
        actual = scope.figures()
        assert actual == EXPECTED, (
            "doc/TODO.md §21 no longer matches the corpus — re-measure and update the table "
            f"(and CircuitRun.evaluate's docstring). Measured: {actual}"
        )
        return
    ceiling = EXPECTED["non_registry_metrics"]
    assert scope.non_registry_metrics <= ceiling, (
        f"analog-db at {head or 'an unresolvable commit'} has {scope.non_registry_metrics} "
        f"datasheet metrics naming a non-registry meas — over the ceiling of {ceiling} "
        f"measured at {MEASURED_AT}: the gap GREW. Register the new names or fix the "
        "datasheets; a deliberate rise is a reviewed edit of MEASURED_AT/EXPECTED and §21. "
        f"Measured: {scope.figures()}"
    )


_THIS = sys.modules[__name__]

#: A syntactically valid analog-db commit that is NOT the measured one.
_OTHER_PIN = "0123abcd"

#: A scope equal to EXPECTED; the synthetic probes below move one figure at a time.
_ON_RECORD = dataclasses.replace(_Scope(), **EXPECTED)


def _outcome(fn, *args) -> BaseException | None:
    """Call ``fn`` and hand back whatever it raised, or None.

    A ``Skipped`` is a ``BaseException``: ``pytest.raises(AssertionError)`` lets it through and
    the test reports SKIPPED, not FAILED — which is exactly the regression this module fixes (a
    re-pin switching the guard off). Catching everything and checking the TYPE closes that."""
    try:
        fn(*args)
    except BaseException as exc:  # a Skipped here IS the failure under test
        return exc
    return None


def _assert_guard_fails(scope: _Scope, head: str | None, needle: str) -> None:
    exc = _outcome(_assert_on_record, scope, head)
    assert type(exc) is AssertionError, f"at {head!r} the guard gave {exc!r}, not a failure"
    assert needle in str(exc), f"at {head!r} the guard failed on the wrong branch: {exc}"


def _assert_guard_passes(scope: _Scope, head: str | None) -> None:
    exc = _outcome(_assert_on_record, scope, head)
    assert exc is None, f"at {head!r} the guard gave {exc!r} for {scope.figures()}"


def test_documented_scope_matches_the_corpus() -> None:
    """Every figure in doc/TODO.md §21 is re-derived here — and a re-pin cannot switch it off."""
    _assert_on_record(_measure(), _corpus_head())


def _copy_datasheets(src: Path, dst: Path) -> Path:
    """The two files ``_measure`` reads, per circuit, copied into a scratch corpus."""
    for circuit in (p for p in src.iterdir() if p.is_dir()):
        (dst / circuit.name).mkdir(parents=True)
        for name in ("circuit.yaml", "datasheet.yaml"):
            if (circuit / name).is_file():
                shutil.copyfile(circuit / name, dst / circuit.name / name)
    return dst


def test_the_ratchet_trips_when_the_gap_grows(tmp_path: Path) -> None:
    """One datasheet metric past the ceiling fails the guard — at the measured pin AND at any
    other one (the other-pin branch is the one that used to skip)."""
    real = _corpus_root()
    base = _measure(real)
    corpus = _copy_datasheets(real, tmp_path / "circuits")
    assert _measure(corpus).figures() == base.figures()  # the copy is faithful

    unknown = "not_a_registry_meas"
    assert unknown not in _MEAS_TABLE
    # enough new readings to land exactly one past the committed ceiling, whatever the pin
    extra = EXPECTED["non_registry_metrics"] - base.non_registry_metrics + 1
    datasheet = sorted(corpus.glob("*/datasheet.yaml"))[0]
    doc = yaml.safe_load(datasheet.read_text()) or {}
    metrics = doc.get("metrics") or {}
    for i in range(extra):
        metrics[f"gap_probe_{i}"] = {"extract": {"meas": unknown}}
    doc["metrics"] = metrics
    datasheet.write_text(yaml.safe_dump(doc, sort_keys=False))

    grown = _measure(corpus)
    assert grown.non_registry_metrics == EXPECTED["non_registry_metrics"] + 1
    # each pin fails on ITS branch: the snapshot at MEASURED_AT, the ceiling everywhere else
    _assert_guard_fails(grown, MEASURED_AT, "no longer matches")
    _assert_guard_fails(grown, _OTHER_PIN, "the gap GREW")
    _assert_guard_fails(grown, None, "an unresolvable commit")
    # and the untouched corpus stays within the record at any pin
    _assert_guard_passes(base, _OTHER_PIN)
    _assert_guard_passes(base, None)


def test_the_gap_is_corpus_wide_and_not_fd_only() -> None:
    """The retracted framing, stated as assertions so it cannot come back.

    "amp_023 / amp_020 declare `vos`, then sweep the 17 FD datasheets" implies ~2 circuits,
    1 name, and an FD-only footprint. All three are false.
    """
    m = _measure()
    assert m.circuits_affected > 2  # claimed 2, measured 68
    assert m.distinct_names > 1  # claimed 1 (`vos`), measured 89
    # and the majority sits OUTSIDE the fully-differential set the fix targeted
    assert m.single_ended_metrics > m.differential_metrics
    assert m.single_ended_metrics > 0.5 * m.non_registry_metrics


def test_no_single_name_is_the_whole_story() -> None:
    """`vos` was real, but only 16 of 224 readings at ``ed4d7c48``. It has since joined the
    registry (0 readings left) and the gap is 342 readings wide; the most-used name
    (`ugf_loop`, 42) is still well under a quarter of it."""
    names = _measure().names
    total = sum(names.values())
    assert names["vos"] < 0.25 * total
    assert max(names.values()) < 0.25 * total
    # a single-ended circuit's own non-registry name, live-confirmed as NaN/satisfied=False
    # on buf_001_super_follower/ihp-sg13g2/dc_op while the deck's scalar reads -0.405 V
    assert names["v_offset"] > 0


def test_the_figures_do_not_depend_on_which_plug_in_families_are_imported() -> None:
    """Importing the waveview eye family registers extra names in the live table; the §21 scope
    must not move (it did under xdist whenever an eye test shared the worker)."""
    before = _measure().figures()
    import spicexplorer_waveview.eye  # noqa: F401 — registers the eye family on import

    assert set(_MEAS_TABLE) - _core_names(), "the eye family should now be registered"
    assert _measure().figures() == before


# --- the guard's two branches (exact match / ceiling), on synthetic scopes (no corpus needed) ---


@pytest.mark.parametrize("head", [MEASURED_AT, _OTHER_PIN, "", None])
def test_the_record_itself_passes_at_every_pin(head: str | None) -> None:
    assert _OTHER_PIN != MEASURED_AT
    _assert_guard_passes(_ON_RECORD, head)


@pytest.mark.parametrize("key", sorted(EXPECTED))
@pytest.mark.parametrize("delta", [-1, +1])
def test_at_the_measured_pin_every_figure_is_a_snapshot(key: str, delta: int) -> None:
    """At ``MEASURED_AT`` all nine figures must match — a SHRINK there is §21 drift too, and so is
    a figure other than the count moving (the ceiling alone would let both through)."""
    moved = dataclasses.replace(_ON_RECORD, **{key: EXPECTED[key] + delta})
    _assert_guard_fails(moved, MEASURED_AT, "no longer matches")


@pytest.mark.parametrize("head", [_OTHER_PIN, "", None])
def test_at_any_other_pin_only_a_growing_gap_fails(head: str | None) -> None:
    """Off the measured pin the figures may move (a re-pin is a §21 doc edit) and the gap may
    shrink; one reading past the committed ceiling fails, the ceiling itself does not."""
    ceiling = EXPECTED["non_registry_metrics"]
    for allowed in (ceiling, ceiling - 1, 0):
        _assert_guard_passes(dataclasses.replace(_ON_RECORD, non_registry_metrics=allowed), head)
    repinned = dataclasses.replace(
        _ON_RECORD, circuits=EXPECTED["circuits"] + 7, distinct_names=1, fd_circuits=0
    )
    _assert_guard_passes(repinned, head)
    over = dataclasses.replace(_ON_RECORD, non_registry_metrics=ceiling + 1)
    _assert_guard_fails(over, head, "the gap GREW")
    _assert_guard_fails(over, head, f"analog-db at {head or 'an unresolvable commit'} has")


@pytest.mark.parametrize("head", [_OTHER_PIN, None])
def test_a_repin_runs_the_guard_instead_of_skipping(
    monkeypatch: pytest.MonkeyPatch, head: str | None
) -> None:
    """The module's own guard test at a pin other than ``MEASURED_AT`` must RUN — pass within the
    ceiling, fail past it — and never skip (the old behaviour, which hid 224 -> 342)."""
    ceiling = EXPECTED["non_registry_metrics"]
    monkeypatch.setattr(_THIS, "_corpus_head", lambda: head)

    within = dataclasses.replace(_ON_RECORD, non_registry_metrics=ceiling - 3)
    monkeypatch.setattr(_THIS, "_measure", lambda root=None: within)
    assert _outcome(test_documented_scope_matches_the_corpus) is None

    over = dataclasses.replace(_ON_RECORD, non_registry_metrics=ceiling + 1)
    monkeypatch.setattr(_THIS, "_measure", lambda root=None: over)
    exc = _outcome(test_documented_scope_matches_the_corpus)
    assert type(exc) is AssertionError and "the gap GREW" in str(exc), repr(exc)


# --- _corpus_head: the pin it reports decides the branch ----------------------------------------


def test_corpus_head_reads_the_checkouts_commit() -> None:
    _corpus_root()  # skips when the submodule is absent
    if shutil.which("git") is None:
        pytest.skip("git unavailable")
    if not (
        _ADB / ".git"
    ).exists():  # a `git archive` export (as ci-local ships): no commit to read
        pytest.skip("analog-db is an export, not a git checkout")
    head = _corpus_head()
    assert head is not None and re.fullmatch(r"[0-9a-f]{8,}", head), head
    full = subprocess.run(
        ["git", "-C", str(_ADB), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert full.startswith(head)


def test_corpus_head_is_none_outside_a_git_checkout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    if shutil.which("git") is None:
        pytest.skip("git unavailable")
    monkeypatch.delenv("GIT_DIR", raising=False)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    monkeypatch.setattr(_THIS, "_ADB", tmp_path)
    assert _corpus_head() is None


def test_corpus_head_is_none_for_an_export_inside_another_work_tree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    if shutil.which("git") is None:
        pytest.skip("git unavailable")
    monkeypatch.delenv("GIT_DIR", raising=False)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    outer = tmp_path / "outer"
    export = outer / "examples" / "analog-db"
    export.mkdir(parents=True)
    (export / "README.md").write_text("an exported corpus\n")
    git = [
        "git",
        "-C",
        str(outer),
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@t",
        "-c",
        "commit.gpgsign=false",
    ]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "outer"], check=True)
    monkeypatch.setattr(_THIS, "_ADB", export)
    assert _corpus_head() is None


@pytest.mark.parametrize(
    "failure",
    [
        FileNotFoundError("git"),
        subprocess.TimeoutExpired("git", 30),
        subprocess.CalledProcessError(128, "git"),
    ],
    ids=["no-git", "timeout", "not-a-repo"],
)
def test_corpus_head_is_none_when_git_cannot_answer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, failure: Exception
) -> None:
    (tmp_path / ".git").mkdir()  # looks like a checkout, so the call reaches git
    monkeypatch.setattr(_THIS, "_ADB", tmp_path)
    called: list[object] = []

    def boom(*args: object, **_kwargs: object) -> None:
        called.append(args)
        raise failure

    monkeypatch.setattr(subprocess, "run", boom)
    assert _corpus_head() is None
    assert called, "git was never asked"


# --- _measure / _is_differential on a synthetic corpus -----------------------------------------


def _put(path: Path, doc: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("" if doc is None else yaml.safe_dump(doc))


def _synthetic_corpus(root: Path) -> Path:
    """Seven circuits covering every branch of the count, plus a stray file at the corpus root."""
    known = sorted(_core_names())[0]

    def m(meas: object) -> dict:
        return {"extract": {"meas": meas}}

    c = root / "circuits"
    _put(c / "se_a/circuit.yaml", {"class": "amplifier", "ports": ["vin", "VOUT"]})
    _put(
        c / "se_a/datasheet.yaml",
        {
            "metrics": {
                "known": m(known),
                "a": m("unk_a"),
                "b": m("unk_b"),
                "null_metric": None,
                "no_extract": {},
                "null_extract": {"extract": None},
                "null_meas": m(None),
            }
        },
    )
    _put(c / "fd_b/circuit.yaml", {"ports": ["VOUTP", "voutn", "vinp"]})  # case-insensitive pair
    _put(c / "fd_b/datasheet.yaml", {"metrics": {"a": m("unk_a")}})
    _put(c / "fd_c/circuit.yaml", {"ports": ["voutp", "voutn"]})  # FD, registry-only
    _put(c / "fd_c/datasheet.yaml", {"metrics": {"known": m(known)}})
    _put(c / "mixed_d/circuit.yaml", {"ports": ["voutp", "voutn", "vout"]})  # has a vout: not FD
    _put(c / "mixed_d/datasheet.yaml", {"metrics": {"c": m("unk_c")}})
    _put(c / "no_datasheet_e/circuit.yaml", {"ports": ["voutp", "voutn"]})
    _put(c / "empty_f/datasheet.yaml", None)  # empty file, and no manifest at all
    _put(c / "nulls_g/circuit.yaml", {"ports": None})
    _put(c / "nulls_g/datasheet.yaml", {"metrics": None})
    (c / "README.md").write_text("a stray file is not a circuit\n")
    return c


def test_measure_counts_exactly_the_non_registry_readings(tmp_path: Path) -> None:
    scope = _measure(_synthetic_corpus(tmp_path))
    assert scope.figures() == {
        "registry_names": len(_core_names()),
        "circuits": 7,  # every directory, with or without a datasheet; not the stray file
        "non_registry_metrics": 4,  # unk_a x2, unk_b, unk_c — nulls and registry names skipped
        "circuits_affected": 3,  # se_a, fd_b, mixed_d
        "distinct_names": 3,
        "single_ended_metrics": 3,  # se_a (2) + mixed_d (1: a vout makes it single-ended)
        "differential_metrics": 1,  # fd_b
        "fd_circuits": 2,  # fd_b, fd_c (a circuit without a datasheet is not counted)
        "fd_circuits_affected": 1,
    }
    assert scope.names == collections.Counter({"unk_a": 2, "unk_b": 1, "unk_c": 1})
    assert _measure(tmp_path / "circuits").figures() == scope.figures()  # same on a second pass


def test_the_differential_mirror_agrees_with_production(tmp_path: Path) -> None:
    """``_is_differential`` duplicates ``analog_db.differential_output``; check the two agree on
    the synthetic edge cases and on every real circuit, so the FD split cannot drift."""
    from spicexplorer.backends.analog_db import differential_output

    synthetic = _synthetic_corpus(tmp_path)
    for d in sorted(p for p in synthetic.iterdir() if (p / "circuit.yaml").is_file()):
        assert _is_differential(d) == (differential_output(d.name, root=tmp_path) is not None), (
            d.name
        )
    assert [d.name for d in sorted(synthetic.iterdir()) if _is_differential(d)] == [
        "fd_b",
        "fd_c",
        "no_datasheet_e",
    ]

    real = _corpus_root()
    dirs = sorted(p for p in real.iterdir() if (p / "circuit.yaml").is_file())
    assert dirs
    for d in dirs:
        assert _is_differential(d) == (differential_output(d.name, root=_ADB) is not None), d.name


# --- the doc half of the acceptance: §21 and the evaluate docstring quote the record -----------

_DOC = Path(__file__).resolve().parents[3] / "doc" / "TODO.md"

#: §21's table rows -> the EXPECTED key each quotes (and, for "N of M", the denominator's key).
_TABLE_21 = {
    "registry canonical `meas` names": ("registry_names", None),
    "circuits in the corpus": ("circuits", None),
    "datasheet metrics naming a non-registry `meas`": ("non_registry_metrics", None),
    "circuits affected": ("circuits_affected", "circuits"),
    "distinct non-registry `meas` names": ("distinct_names", None),
    "…on SINGLE-ENDED circuits": ("single_ended_metrics", None),
    "…on fully-differential circuits": ("differential_metrics", None),
    "FD circuits affected": ("fd_circuits_affected", "fd_circuits"),
}


def _section_21() -> str:
    if not _DOC.is_file():
        pytest.skip("doc/TODO.md is not in this checkout")
    found = re.search(r"^## 21\. .*?(?=^## 22\. )", _DOC.read_text(), re.S | re.M)
    assert found, "doc/TODO.md has no §21 followed by §22 — the tracker moved; update this test"
    return found.group(0)


def _table_rows(section: str) -> dict[str, str]:
    rows = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().replace("**", "") for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0] != "measure" and set(cells[0]) - {"-"}:
            rows[cells[0]] = cells[1]
    return rows


def test_section_21_quotes_the_recorded_figures() -> None:
    """§21's table and prose carry ``EXPECTED``/``MEASURED_AT`` — the "§21 numbers match the
    test" half of the acceptance. A figure edited on one side only fails here, at any pin."""
    assert {k for pair in _TABLE_21.values() for k in pair if k} == set(EXPECTED)
    section = _section_21()
    rows = _table_rows(section)
    assert set(rows) == set(_TABLE_21), f"§21's table rows changed: {sorted(rows)}"
    for label, (key, of) in _TABLE_21.items():
        quoted = re.match(r"(\d+)(?: of (\d+))?", rows[label])
        assert quoted, f"§21 {label!r} quotes no figure: {rows[label]!r}"
        assert int(quoted.group(1)) == EXPECTED[key], (
            f"§21 {label!r} = {rows[label]!r}, {key} = {EXPECTED[key]}"
        )
        if of is not None:
            assert quoted.group(2) is not None and int(quoted.group(2)) == EXPECTED[of], (
                f"§21 {label!r} = {rows[label]!r}, {of} = {EXPECTED[of]}"
            )

    e = EXPECTED
    prose = " ".join(section.split())
    share = round(100 * e["single_ended_metrics"] / e["non_registry_metrics"])
    for phrase in (
        f"**analog-db `{MEASURED_AT}`**",
        f"grows past **{e['non_registry_metrics']}**",
        f"({share} % of the affected metrics are on single-ended circuits",
        f"it is **{e['distinct_names']}**",
        f"{e['distinct_names']} names is too many",
        f"many of the {e['non_registry_metrics']} —",
    ):
        assert phrase in prose, f"§21 no longer says {phrase!r}"
    if "has since joined the registry" in prose:
        assert "vos" in _core_names(), "§21 says `vos` joined the registry; it is not in it"


def test_section_21_histogram_claims_match_the_corpus() -> None:
    """The claims §21 derives from the name histogram — the used-once count and the most-used
    list (truthful counts, and nothing as common as its last entry left out) — re-derived at
    the pin they were measured at. Elsewhere only the ceiling is checked and this prose may move."""
    section = _section_21()
    _corpus_root()
    head = _corpus_head()
    if head != MEASURED_AT:
        pytest.skip(f"§21's histogram prose is measured at {MEASURED_AT}; analog-db is at {head}")
    names = _measure().names
    prose = " ".join(section.split())

    once = sum(1 for n in names.values() if n == 1)
    assert f"({once} of them used exactly once)" in prose, f"{once} names are used exactly once"

    most = re.search(r"Most-used: (.*?)\.", prose)
    assert most, "§21 has no Most-used list"
    listed = {name: int(n) for name, n in re.findall(r"`(\w+)` \((\d+)\)", most.group(1))}
    tail = re.search(r"then (\d+) each for (.*)$", most.group(1))
    if tail:
        listed.update({name: int(tail.group(1)) for name in re.findall(r"`(\w+)`", tail.group(2))})
    assert listed, "§21's Most-used list parsed empty"
    assert listed == {name: names[name] for name in listed}, "§21's Most-used counts are stale"
    floor = min(listed.values())
    assert set(listed) == {n for n, c in names.items() if c >= floor}, (
        "§21's Most-used list leaves out a name at least as common as its last entry"
    )


def test_evaluate_docstring_quotes_the_recorded_figures() -> None:
    from spicexplorer.backends.analog_db import CircuitRun

    doc = " ".join((CircuitRun.evaluate.__doc__ or "").split())
    if not doc:
        pytest.skip("docstrings stripped (python -OO)")
    e = EXPECTED
    for phrase in (
        f"At analog-db ``{MEASURED_AT}``, **{e['non_registry_metrics']}** datasheet metrics "
        f"across **{e['circuits_affected']} of {e['circuits']}** circuits",
        f"(**{e['distinct_names']}** distinct names; **{e['single_ended_metrics']}** of them on "
        "SINGLE-ended circuits",
        f"{e['fd_circuits_affected']} of the {e['fd_circuits']} FD circuits are affected",
    ):
        assert phrase in doc, f"CircuitRun.evaluate's docstring no longer says {phrase!r}"
