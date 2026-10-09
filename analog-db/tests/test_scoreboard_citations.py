"""No committed file cites a scoreboard design point that does not exist (FU-FF05).

amp_032's ``circuit.yaml`` and ldo_005's gf180mcu ``sizing.yaml`` both named ``ff05bbd572`` as
the scoreboard entry of the sizing they held. That design_id was never committed: it hashed the
pre-fix 13-device knob set, and ``baselines.yaml`` pointed at it until 5f579f2f re-pointed the
baseline to ``0d97ec7f42``. A reader who follows such a citation finds nothing.

A design_id is 10 lowercase hex digits. Every such token in a committed text file must be the file
name of a committed ``circuits/<id>/scoreboard/<pdk>/<design_id>.json`` entry, or sit on an
allowlisted line that says the point is gone. ``raw/`` (generated decks) and ``tests/`` (which name
retired points on purpose) are not scanned.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from spicexplorer_analog_db import paths

# At least one letter and one digit, and not part of a longer word or of a float's mantissa
# ("5.001304937e-06" contains "001304937e").
DESIGN_ID = re.compile(
    r"(?<![0-9A-Za-z_.])(?=[0-9a-f]{0,9}[a-f])(?=[0-9a-f]{0,9}[0-9])[0-9a-f]{10}(?![0-9A-Za-z_])"
)
TEXT_SUFFIXES = {
    ".md",
    ".yaml",
    ".yml",
    ".py",
    ".spice",
    ".txt",
    ".ipynb",
    ".toml",
    ".json",
    ".csv",
    ".sch",
    ".sp",
    ".cir",
    ".scs",
}
SKIP_TOP = {"raw", "tests", ".git", ".venv", "sandbox"}
SKIP_DIRS = {"__pycache__", ".ipynb_checkpoints"}

# (file, design_id) -> the phrase each line naming it must carry, and why the mention stays.
HISTORY = {
    ("circuits/amp_032_ti_ldo_error_selfbias/circuit.yaml", "ff05bbd572"): (
        "was dropped",
        "records why the pre-fix point is gone",
    ),
    ("circuits/ia_004_fan_chopper_rrl/analyses/dc_op.yaml", "ee77a983e2"): (
        "recorded then",
        "records the point retired 2026-09 (WP-77)",
    ),
    ("drawings/DRAWING_REVIEW.md", "ee77a983e2"): (
        "pre-fix",
        "section 9 is the dated 2026-07-20 review record",
    ),
}


def committed_design_ids(root: Path) -> set[str]:
    return {p.stem for p in root.glob("circuits/*/scoreboard/*/*.json")}


def cited_design_ids(root: Path) -> list[tuple[str, int, str, str]]:
    """``(file, line number, token, line)`` for every design_id-shaped token in a scanned file."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        if rel_dir.parts and rel_dir.parts[0] in SKIP_TOP:
            dirnames[:] = []
            continue
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix not in TEXT_SUFFIXES:
                continue
            rel = str(path.relative_to(root))
            for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
                for m in DESIGN_ID.finditer(line):
                    out.append((rel, n, m.group(0), line))
    return out


def dangling_citations(root: Path, history: dict) -> tuple[list[str], set]:
    """The citations of a design_id with no committed entry that ``history`` does not excuse, and
    the ``history`` keys that excused something."""
    known = committed_design_ids(root)
    bad, used = [], set()
    for rel, n, token, line in cited_design_ids(root):
        if token in known:
            continue
        phrase = history.get((rel, token), (None, ""))[0]
        if phrase is not None and phrase in line:
            used.add((rel, token))
            continue
        bad.append(f"{rel}:{n}: {token} is no committed scoreboard entry: {line.strip()}")
    return bad, used


@pytest.mark.corpus
def test_every_cited_design_point_exists_or_is_marked_as_history():
    root = paths.db_root()
    bad, used = dangling_citations(root, HISTORY)
    assert bad == []
    assert set(HISTORY) == used, f"allowlist entries that excuse nothing: {set(HISTORY) - used}"
    assert not committed_design_ids(root) & {token for _f, token in HISTORY}


def test_the_rewritten_citations_name_the_entry_their_values_match():
    """The drawing and the ldo_005 error-amp seeds carry 0d97ec7f42's knob values, the
    2026-07-21 amp_032 gf180mcu sizing (5f579f2f); sizing.yaml now holds baseline 08cfc9b9ba."""
    root = paths.db_root()
    amp = root / "circuits" / "amp_032_ti_ldo_error_selfbias"
    assert (amp / "scoreboard" / "gf180mcu" / "0d97ec7f42.json").is_file()
    assert "0d97ec7f42" in (amp / "circuit.yaml").read_text()
    ldo = (
        root / "circuits" / "ldo_005_buffered_ref" / "pdk" / "gf180mcu" / "sizing.yaml"
    ).read_text()
    assert "0d97ec7f42" in ldo and "~93 mV" not in ldo


# ---------------------------------------------------------------- the scan itself, on a tmp tree


def _tree(tmp_path: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    return tmp_path


def test_a_citation_of_a_missing_point_is_reported(tmp_path):
    root = _tree(
        tmp_path,
        {
            "circuits/x/scoreboard/ihp/0d97ec7f42.json": "{}",
            "circuits/x/circuit.yaml": "# landed at 0d97ec7f42\n# landed at ff05bbd572\n",
        },
    )
    bad, _ = dangling_citations(root, {})
    assert bad == [
        "circuits/x/circuit.yaml:2: ff05bbd572 is no committed scoreboard entry: "
        "# landed at ff05bbd572"
    ]


def test_a_history_line_needs_its_phrase(tmp_path):
    root = _tree(tmp_path, {"doc.md": "entry ff05bbd572 was dropped\nentry ff05bbd572 is live\n"})
    bad, used = dangling_citations(root, {("doc.md", "ff05bbd572"): ("was dropped", "")})
    assert bad == [
        "doc.md:2: ff05bbd572 is no committed scoreboard entry: entry ff05bbd572 is live"
    ]
    assert used == {("doc.md", "ff05bbd572")}


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("smin: 5.001304937e-06", id="float-mantissa"),
        pytest.param("n = 1234567890", id="all-digits"),
        pytest.param("xff05bbd572", id="longer-word-left"),
        pytest.param("ff05bbd5721", id="longer-word-right"),
        pytest.param("FF05BBD572", id="upper-case"),
        pytest.param("ff05bbd57", id="nine-digits"),
    ],
)
def test_tokens_that_are_not_design_ids_are_ignored(tmp_path, text):
    root = _tree(tmp_path, {"doc.md": text + "\n"})
    assert cited_design_ids(root) == []


def test_raw_tests_and_non_text_files_are_not_scanned(tmp_path):
    root = _tree(
        tmp_path,
        {
            "raw/x/deck.spice": "* ff05bbd572\n",
            "tests/test_x.py": "# ff05bbd572\n",
            "circuits/x/figure.svg": "<!-- ff05bbd572 -->\n",
            "circuits/x/__pycache__/m.py": "# ff05bbd572\n",
        },
    )
    assert cited_design_ids(root) == []
