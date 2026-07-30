"""Simulator-log parsing: raw text → structured, severity-classified lines.

Handles both engines' log dialects — ngspice run logs (spicelib's ``<netlist>.log``,
``Error:``/``Warning:``/``Note:`` prefixes) and Spectre output (``spectre.out`` /
bridge logs, ``ERROR (…)``/``WARNING (…)``/``Notice (…)`` markers) — plus a generic
fallback, so the viewer's log panel can colour any simulator log it is handed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["LogLine", "LogSummary", "parse_sim_log", "parse_log_text", "discover_log", "classify_line"]

# Ordered: first match wins. Case-sensitive where the engines are (Spectre shouts).
_LEVEL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # hard failures
    ("error", re.compile(r"^\s*(?:\*\*\s*)?(?:Fatal|FATAL)\b")),
    ("error", re.compile(r"(?:^|\W)(?:Error|ERROR)\s*[:(]")),
    ("error", re.compile(r"^\s*%?ERROR\b")),
    ("error", re.compile(r"analysis\s+(?:\S+\s+)?(?:failed|aborted)", re.IGNORECASE)),
    ("error", re.compile(r"doAnalyses:.*(?:failed|error)", re.IGNORECASE)),
    ("error", re.compile(r"no\s+convergence|non-?convergen", re.IGNORECASE)),
    # warnings
    ("warning", re.compile(r"(?:^|\W)(?:Warning|WARNING)\s*[:(]")),
    ("warning", re.compile(r"^\s*%?WARNING\b")),
    # informational notes
    ("note", re.compile(r"(?:^|\W)(?:Note|Notice|NOTE)\s*[:(]")),
)


@dataclass
class LogLine:
    """One classified log line (1-based ``no``)."""

    no: int
    level: str  # "error" | "warning" | "note" | "info"
    text: str


@dataclass
class LogSummary:
    """A parsed simulator log: structured lines + severity counts."""

    path: str | None
    lines: list[LogLine] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def n_lines(self) -> int:
        return len(self.lines)

    def filtered(self, min_level: str) -> list[LogLine]:
        """Lines at or above a severity ('note' < 'warning' < 'error')."""
        order = {"info": 0, "note": 1, "warning": 2, "error": 3}
        floor = order.get(min_level, 0)
        return [ln for ln in self.lines if order.get(ln.level, 0) >= floor]


def classify_line(text: str) -> str:
    for level, pattern in _LEVEL_PATTERNS:
        if pattern.search(text):
            return level
    return "info"


def parse_log_text(text: str, path: str | None = None) -> LogSummary:
    """Classify every line of a simulator log's text."""
    summary = LogSummary(path=path)
    counts = {"error": 0, "warning": 0, "note": 0, "info": 0}
    for i, raw_line in enumerate(text.splitlines(), start=1):
        level = classify_line(raw_line)
        counts[level] += 1
        summary.lines.append(LogLine(no=i, level=level, text=raw_line))
    summary.counts = counts
    return summary


def parse_sim_log(path: str | Path) -> LogSummary:
    """Read + classify a simulator log file (any encoding errors are replaced)."""
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    return parse_log_text(text, path=str(p))


def discover_log(source: str | Path, engine: str) -> str | None:
    """Best-effort log discovery next to a result artifact.

    ngspice: spicelib leaves ``<stem>.log`` beside ``<stem>.raw`` (same directory).
    Spectre: the bridge leaves ``spectre.out`` / ``*.log`` in the raw dir or its parent
    (a ``…-raw`` dir sits next to the deck's stdout capture).
    """
    src = Path(source)
    if engine == "ngspice":
        candidate = src.with_suffix(".log")
        if candidate.is_file():
            return str(candidate)
        logs = sorted(src.parent.glob("*.log"))
        return str(logs[0]) if len(logs) == 1 else None
    # spectre: raw dir → look inside, then in the parent
    for folder in (src, src.parent):
        if not folder.is_dir():
            continue
        for pattern in ("spectre.out", "*.out", "*.log"):
            hits = sorted(p for p in folder.glob(pattern) if p.is_file())
            if hits:
                return str(hits[0])
    return None
