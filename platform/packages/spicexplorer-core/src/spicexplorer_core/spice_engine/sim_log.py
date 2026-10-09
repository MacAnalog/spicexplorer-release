"""Simulator-log text rules: severity per line, ngspice ``.meas``/``print`` scalars, fatal lines.

The one place that knows what a simulator log line *means*. Two consumers sit on it:

* :func:`run_deck` (this package) — a deck-string run reads its own ``ngspice.out`` back through
  :func:`parse_measures` (``RunResult.measures``/``failed``) and :func:`fatal_lines`
  (``RunResult.fatal``), because ngspice exits 0 after a failed operating point, an ignored
  device line or a failed ``.meas`` and the log is the only witness.
* ``spicexplorer_waveview.logs`` — the viewer's log panel re-exports :func:`classify_line`,
  :func:`parse_measures` and :func:`fatal_lines` unchanged (core cannot import the viewer, so
  the rules live here and the viewer borrows them).

Both engines' dialects classify: ngspice run logs (``Error:``/``Warning:``/``Note:`` prefixes)
and Spectre output (``ERROR (…)``/``WARNING (…)``/``Notice (…)``), plus a generic fallback.
"""

from __future__ import annotations

import re

__all__ = ["classify_line", "parse_measures", "fatal_lines", "LEVELS"]

LEVELS = ("info", "note", "warning", "error")

# Ordered: first match wins. Case-sensitive where the engines are (Spectre shouts).
_LEVEL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # hard failures. `fatal` is matched case-INSENSITIVELY but stays LINE-ANCHORED: a runner may
    # inject its own marker in any case (analog-db's `fatal: ngspice timed out after 30s`), while
    # the anchor is what keeps "warnings are never fatal" true — `Warning: … fatal …` mentions the
    # word mid-line and is classified by the warning pattern below.
    ("error", re.compile(r"^\s*(?:\*\*\s*)?fatal\b", re.IGNORECASE)),
    ("error", re.compile(r"(?:^|\W)(?:Error|ERROR)\s*[:(]")),
    ("error", re.compile(r"^\s*%?ERROR\b")),
    ("error", re.compile(r"^\s*Error on line\b")),  # `Error on line 12 : xm1 … Unknown model type`
    ("error", re.compile(r"analysis\s+(?:\S+\s+)?(?:failed|aborted)", re.IGNORECASE)),
    ("error", re.compile(r"doAnalyses:.*(?:failed|error)", re.IGNORECASE)),
    ("error", re.compile(r"no\s+convergence|non-?convergen", re.IGNORECASE)),
    # the silent-zero class: a `Warning:` that dropped a device line — the run continues on a
    # wrong circuit and leaves a rawfile full of zeros, so it outranks its prefix
    ("error", re.compile(r"is not a valid\b.*\bignored!?", re.IGNORECASE)),
    # warnings
    ("warning", re.compile(r"(?:^|\W)(?:Warning|WARNING)\s*[:(]")),
    ("warning", re.compile(r"^\s*%?WARNING\b")),
    # informational notes
    ("note", re.compile(r"(?:^|\W)(?:Note|Notice|NOTE)\s*[:(]")),
    # bare lines ngspice prints for failures it does not exit non-zero on (no `Error:` prefix).
    # They sit AFTER the warning/note patterns on purpose: `Warning: singular matrix` during gmin
    # stepping is recoverable and stays a warning; the bare form is the analysis giving up.
    ("error", re.compile(r"doAnalyses:\s*iteration limit reached", re.IGNORECASE)),
    ("error", re.compile(r"Transient solution failed", re.IGNORECASE)),
    ("error", re.compile(r"timestep too small", re.IGNORECASE)),
    ("error", re.compile(r"singular matrix", re.IGNORECASE)),
    ("error", re.compile(r"Unknown model type", re.IGNORECASE)),
    ("error", re.compile(r"could not find a valid modelname", re.IGNORECASE)),
    ("error", re.compile(r"simulation interrupted", re.IGNORECASE)),
    # A missing include/model file: ngspice prints it bare, and the run then continues on a
    # circuit with no models at all. Both spellings; deliberately down here so a `Warning: cannot
    # open …` (recoverable, e.g. an optional .ic file) is still just a warning.
    ("error", re.compile(r"can(?:no|')t open", re.IGNORECASE)),
    ("error", re.compile(r"fatal error", re.IGNORECASE)),
)

# A failed `.meas` is reported by name (`parse_measures`), never fatal: ngspice-45 prints
# `Error: measure  bad  when(WHEN) : out of interval` and then ` meas tran bad … failed!`.
_MEAS_ERROR = re.compile(r"Error:\s+measure\b", re.IGNORECASE)

# ngspice meas/print output: `name              =  2.977862e+01`. Measures may append their
# location(s) — `at=  4.34e-06` (min/max/pp), `from= … to= …` (avg/integ/pp), `targ= … trig= …`
# (a trig/targ delay) — any `<word>= …` tail is accepted. Names may be dotted (`m.dot`). The
# value may be `inf`/`-inf`/`nan`/`-nan` (an overflowing or indeterminate `let`): a scalar that
# did not fail, kept as a non-finite float for the caller's `isfinite` gate. The `print`
# contract is a NAMED vector — `let x = …` then `print x` — because `print <expression>`
# echoes the expression as the name (`-i(v1) = …`, `i_ma*2 = …`, `v(out)[3] = …`) and those
# are deliberately not parsed. A wider form than analog-db's runner copy (which reads its
# own decks and never sees the delay/dotted/non-finite cases).
_MEASURE = re.compile(
    r"^\s*([A-Za-z_][\w.]*)\s*=\s*"
    r"([-+]?(?:[0-9.]+(?:[eE][-+]?[0-9]+)?|inf|nan))"
    r"(?:\s+\w+\s*=.*)?\s*$",
    re.IGNORECASE,
)
# Both failed-measure forms: ngspice-45's ` meas tran bad when v(a)=5 failed!` (a body `.meas`
# in batch mode prints ` .meas tran bad … failed!`, on stderr) and the older `bad = failed` line.
_FAILED_MEAS = re.compile(
    r"^\s*\.?meas(?:ure)?\s+\w+\s+([A-Za-z_][\w.]*)\b.*\bfailed!?\s*$", re.IGNORECASE
)
_FAILED_EQ = re.compile(r"^\s*([A-Za-z_][\w.]*)\s*=\s*failed", re.IGNORECASE)


def classify_line(text: str) -> str:
    """Severity of one log line: ``"error" | "warning" | "note" | "info"``."""
    for level, pattern in _LEVEL_PATTERNS:
        if pattern.search(text):
            return level
    return "info"


def parse_measures(log_text: str) -> tuple[dict[str, float], list[str]]:
    """``(measures, failed)`` from an ngspice batch log (stdout and stderr — a body ``.meas``
    reports on stderr): every ``.meas`` scalar and every ``print`` of a *named* vector
    (``let x = …; print x``) by lower-cased name, ``inf``/``nan`` included as non-finite floats;
    and the names of the ``.meas`` statements ngspice reported as failed."""
    measures: dict[str, float] = {}
    failed: list[str] = []
    for line in log_text.splitlines():
        m = _MEASURE.match(line)
        if m:
            measures[m.group(1).lower()] = float(m.group(2))
            continue
        f = _FAILED_MEAS.match(line) or _FAILED_EQ.match(line)
        if f:
            name = f.group(1).lower()
            if name not in failed:
                failed.append(name)
    return measures, failed


def fatal_lines(log_text: str) -> list[str]:
    """The lines that make a run a failure whatever the rawfile or exit code says: every
    ``error``-level line (:func:`classify_line`) except a failed ``.meas`` report, which is a
    per-metric NaN, not a dead run. Warnings never qualify — the silent-zero
    ``… is not a valid … ignored!`` line is classified as an error for that reason.

    Covers a runner's own injected marker (``fatal:`` in any case, at the start of a line) and a
    missing include/model file (``cannot open``/``can't open``), so this is a superset of the
    ad-hoc lowercase substring scans it replaces."""
    out: list[str] = []
    for line in log_text.splitlines():
        if classify_line(line) == "error" and not _MEAS_ERROR.search(line):
            out.append(line)
    return out
