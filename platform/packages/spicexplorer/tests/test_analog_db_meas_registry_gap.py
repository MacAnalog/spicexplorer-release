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
* it SKIPS, with "re-measure and update §21" as the reason, when ``examples/analog-db`` is
  absent or pinned to a different commit than the numbers were measured at — re-pinning the
  submodule is a legitimate reason for the figures to move, and that is a doc edit, not a
  code failure.

Nothing here modifies analog-db: it is a nested submodule with its own review.
"""

from __future__ import annotations

import collections
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml
from spicexplorer_core.measurements.registry import _MEAS_TABLE


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
    names: "collections.Counter[str]" = field(default_factory=collections.Counter)

    def figures(self) -> dict[str, int]:
        """Just the counts quoted in the docs (the `names` histogram is context, not a figure)."""
        return {k: v for k, v in vars(self).items() if k != "names"}


#: The analog-db commit ``doc/TODO.md`` §21's table was measured at.
MEASURED_AT = "ed4d7c48"

#: The measured snapshot — every figure quoted in ``doc/TODO.md`` §21 and in
#: ``CircuitRun.evaluate()``'s docstring.
EXPECTED = {
    "registry_names": 56,
    "circuits": 81,
    "non_registry_metrics": 224,
    "circuits_affected": 44,
    "distinct_names": 74,
    "single_ended_metrics": 173,
    "differential_metrics": 51,
    "fd_circuits": 17,
    "fd_circuits_affected": 16,
}

_ADB = Path(__file__).resolve().parents[3] / "examples" / "analog-db"


def _corpus_root() -> Path:
    circuits = _ADB / "circuits"
    if not circuits.is_dir():
        pytest.skip("examples/analog-db submodule not checked out")
    try:
        head = subprocess.run(
            ["git", "-C", str(_ADB), "rev-parse", "--short=8", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pytest.skip("cannot resolve the analog-db commit (git unavailable)")
    if head != MEASURED_AT:
        pytest.skip(
            f"analog-db is at {head}, doc/TODO.md §21 was measured at {MEASURED_AT} — "
            "re-run this module's measurement and update §21"
        )
    return circuits


def _is_differential(circuit_dir: Path) -> bool:
    """Mirror ``analog_db.differential_output``: a ``voutp``/``voutn`` pair and no ``vout``."""
    manifest = circuit_dir / "circuit.yaml"
    if not manifest.is_file():
        return False
    ports = (yaml.safe_load(manifest.read_text()) or {}).get("ports") or []
    lows = {str(p).lower() for p in ports}
    return "voutp" in lows and "voutn" in lows and "vout" not in lows


def _measure() -> _Scope:
    root = _corpus_root()
    canonical = set(_MEAS_TABLE)
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


def test_documented_scope_matches_the_corpus() -> None:
    """Every figure in doc/TODO.md §21 is re-derived here."""
    actual = _measure().figures()
    assert actual == EXPECTED, (
        "doc/TODO.md §21 no longer matches the corpus — re-measure and update the table "
        f"(and CircuitRun.evaluate's docstring). Measured: {actual}"
    )


def test_the_gap_is_corpus_wide_and_not_fd_only() -> None:
    """The retracted framing, stated as assertions so it cannot come back.

    "amp_023 / amp_020 declare `vos`, then sweep the 17 FD datasheets" implies ~2 circuits,
    1 name, and an FD-only footprint. All three are false.
    """
    m = _measure()
    assert m.circuits_affected > 2  # claimed 2, measured 44
    assert m.distinct_names > 1  # claimed 1 (`vos`), measured 74
    # and the majority sits OUTSIDE the fully-differential set the fix targeted
    assert m.single_ended_metrics > m.differential_metrics
    assert m.single_ended_metrics > 0.5 * m.non_registry_metrics


def test_vos_is_only_the_most_common_of_many_names() -> None:
    """`vos` is real — it is just 16 of 224 readings, not the whole story."""
    names = _measure().names
    assert names["vos"] > 0
    assert names["vos"] < 0.25 * sum(names.values())
    # a single-ended circuit's own non-registry name, live-confirmed as NaN/satisfied=False
    # on buf_001_super_follower/ihp-sg13g2/dc_op while the deck's scalar reads -0.405 V
    assert names["v_offset"] > 0
