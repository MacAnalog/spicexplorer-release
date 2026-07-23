"""Agent context surface: append-only decisions → generated PROJECT.md.

Agents WRITE events — one ``O_APPEND`` line each to ``context/decisions.ndjson`` — and
never edit the rendered document. :func:`render_project_md` derives
``context/PROJECT.md`` from the decision log + the derived ``state.json``: the same
derived/rebuildable contract as ``index.db`` (regenerate to heal). One place an agent
reads to learn "where is this design at", instead of globbing a dozen racing files.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from spicexplorer_core.atomic_io import atomic_write_text
from spicexplorer_core.workspace.state import build_state

DECISIONS_REL = "context/decisions.ndjson"
PROJECT_MD_REL = "context/PROJECT.md"


def append_decision(
    project_dir: Path, event: dict[str, Any], *, now: datetime | None = None,
) -> dict[str, Any]:
    """Append ONE decision event to ``context/decisions.ndjson`` (O_APPEND — the
    contested-state-is-append-only rule). Stamps ``at`` if absent. Agents call
    this; they never edit ``PROJECT.md``."""
    ev = dict(event)
    ev.setdefault("at", (now or datetime.now()).isoformat(timespec="seconds"))
    p = project_dir / DECISIONS_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:  # O_APPEND: concurrent one-line writes don't tear
        f.write(json.dumps(ev, default=str) + "\n")
    return ev


def read_decisions(project_dir: Path) -> list[dict[str, Any]]:
    """Every decision event, in order. Tolerant of torn/blank lines."""
    p = project_dir / DECISIONS_REL
    out: list[dict[str, Any]] = []
    try:
        with p.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict):
                    out.append(row)
    except OSError:
        return []
    return out


def _pass_glyph(v: Any) -> str:
    return {True: "✅", False: "❌"}.get(v, "—")


def render_project_md(
    project_dir: Path, *, recent: int = 12, write: bool = True, now: datetime | None = None,
) -> str:
    """Derive ``context/PROJECT.md`` from ``state.json`` + the decision log and return the
    markdown. ``write=True`` (default) persists it atomically; pass ``write=False`` for a
    side-effect-free render (e.g. an idempotent HTTP GET, or a read-only project dir)."""
    state = build_state(project_dir, now=now)
    proj = state["project"]
    lines: list[str] = [
        f"# {proj.get('name') or proj.get('id')}",
        "",
        "> **GENERATED** from `context/decisions.ndjson` + `state.json` — do not hand-edit"
        " (append to `decisions.ndjson`; regenerate to heal).",
        "",
    ]

    summary = state["compliance_summary"]
    lines += ["## Compliance",
              f"- {summary['checked']} spec(s) checked, **{summary['passing']} passing**"
              f" (all pass: {summary['all_pass']})"]
    for sid, c in state["compliance"].items():
        tgt = f" (target {c['target']})" if c.get("target") else ""
        val = "—" if c["value"] is None else c["value"]
        lines.append(f"  - {_pass_glyph(c['pass'])} `{sid}` = {val}{tgt}"
                     f" [{c['aggregate']} over {c['n_points']} pt(s)]")
    lines.append("")

    best = state["best_runs"]["overall"]
    lines += ["## Best run",
              (f"- `{best['run_id']}` — best_score {best['best_score']} ({best['kind']})"
               if best else "- (none yet)"),
              f"  - election: {state['best_runs']['election_rule']}", ""]

    lines.append("## Cells")
    if state["cells"]:
        for cell in state["cells"]:
            binds = ", ".join(cell["bindings"]) or "none"
            lines.append(f"- `{cell['name']}` — {cell['maturity']} (bindings: {binds})")
    else:
        lines.append("- (none yet)")
    lines.append("")

    decisions = read_decisions(project_dir)
    lines.append(f"## Recent decisions ({min(recent, len(decisions))} of {len(decisions)})")
    for ev in decisions[-recent:][::-1]:
        who = f" _{ev['by']}_" if ev.get("by") else ""
        summary_txt = ev.get("summary") or ev.get("kind") or "decision"
        lines.append(f"- `{ev.get('at', '?')}`{who}: {summary_txt}")
    lines.append("")

    text = "\n".join(lines)
    if write:
        atomic_write_text(project_dir / PROJECT_MD_REL, text)
    return text
