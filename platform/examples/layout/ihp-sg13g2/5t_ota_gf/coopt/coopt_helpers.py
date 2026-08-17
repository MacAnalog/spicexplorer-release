"""Helpers for the layout↔schematic co-optimization guide notebook.

Kept OUT of the notebook so the notebook stays a guide (prose + the few library calls that
carry the idea) rather than a wall of plumbing. Nothing here is co-optimization-specific
magic: it is the boring glue every layout-flow project needs —

* :func:`probe` — the capability check (gdsfactory interpreter, KLayout DRC/LVS decks, kpex,
  ngspice + PDK) behind the notebook's ``live_layout`` gate, returning the SAME reason string
  the test harness reports so a gated run explains itself;
* :func:`trials_table` — the optimizer's log (in memory and/or the crash-safe checkpoints on
  disk) flattened to one row per trial: denormalized params, every target's ``curr_val``, and
  the trial's own layout run dir;
* :func:`pex_net_table` / :func:`stage_times` — a run's ``summary.json`` read back as tables;
* :func:`replay_path` / :func:`save_replay` / :func:`load_replay` — the static fallback so the
  notebook's result cells still render where the toolchain is absent.

Import it from the notebook with the example dir on ``sys.path`` (the notebook does that).
Pure stdlib + pandas; it never imports gdsfactory.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

import pandas as pd

HERE = Path(__file__).resolve().parent
CELL_DIR = HERE.parent
FLOW_YAML = HERE / "flow.yaml"
PROJECT_YAML = HERE / "project_setup.yaml"
REPLAY_JSON = HERE / "coopt_replay.json"

#: the sizing dut_params of this project (flow.yaml `sizing_params`) — used only to split the
#: trial table into its two halves for display.
SIZING_PARAMS = ("in_w", "pld_w", "tail_w")


# ---------------------------------------------------------------------------
# capability probe (the `live_layout` gate)
# ---------------------------------------------------------------------------
def gds_python(flow_yaml: str | Path = FLOW_YAML) -> str | None:
    """The interpreter that owns the gdsfactory stack: ``$GDS_PYTHON`` wins, else the flow
    spec's ``gds_python:``. Returns None when it does not exist on this host."""
    cand = os.environ.get("GDS_PYTHON")
    if not cand:
        try:
            import yaml  # noqa: PLC0415 — optional at import time

            cand = (yaml.safe_load(Path(flow_yaml).read_text()) or {}).get("gds_python")
        except Exception:
            cand = None
    if not cand:
        return None
    cand = os.path.expandvars(os.path.expanduser(str(cand)))
    return cand if os.path.exists(cand) else None


def probe(flow_yaml: str | Path = FLOW_YAML, *, check_import: bool = False) -> dict[str, Any]:
    """``{ok, reason, tools}`` — everything one co-optimization trial needs.

    ``reason`` is None when ok, else the FIRST unmet capability phrased the way the notebook
    lane reports a skip. ``check_import=True`` additionally spends ~2-5 s proving the foreign
    interpreter can ``import gdsfactory`` (the gate itself stays cheap and does not).
    """
    tools: dict[str, Any] = {}
    reason: str | None = None

    py = gds_python(flow_yaml)
    tools["gds_python"] = py
    if py is None:
        reason = "no gdsfactory interpreter (set $GDS_PYTHON, or the flow spec's gds_python: path is missing)"

    try:
        from spicexplorer_signoff import probe as signoff_probe  # noqa: PLC0415

        p = signoff_probe()
        tools.update(p.to_dict())
        if reason is None and not p.drc_ok:
            reason = "KLayout DRC unavailable (klayout binary or the PDK's DRC deck missing)"
        if reason is None and not p.lvs_ok:
            reason = "KLayout LVS unavailable (klayout binary or the PDK's LVS deck missing)"
        if reason is None and not p.pex_ok:
            reason = "kpex unavailable (kpex / its KLayout wrapper / $PDK_ROOT missing)"
    except ImportError as exc:
        tools["spicexplorer_signoff"] = None
        if reason is None:
            reason = f"spicexplorer-signoff not installed — `uv sync --extra layout` ({exc})"

    try:
        from spicexplorer_core.env import probe_env  # noqa: PLC0415

        env = probe_env()
        tools["ngspice_ok"] = bool(env.get("ngspice_ok"))
        tools["pdk_ok"] = bool(env.get("pdk_ok"))
        if reason is None and not env.get("live_runs_enabled"):
            reason = "no live ngspice+PDK (probe_env.live_runs_enabled is false)"
    except Exception as exc:  # pragma: no cover — env probe should not throw
        if reason is None:
            reason = f"environment probe failed: {exc}"

    if reason is None and check_import and py is not None:
        r = subprocess.run([py, "-c", "import gdsfactory, ihp"], capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            reason = f"{py} cannot import gdsfactory+ihp: {(r.stderr or r.stdout).strip().splitlines()[-1][:160]}"

    return {"ok": reason is None, "reason": reason, "tools": tools}


def tool_table(pr: Mapping[str, Any]) -> pd.DataFrame:
    """The probe's `tools` dict as a two-column table (for display in the notebook)."""
    rows = [{"capability": k, "value": ("—" if v in (None, "") else v)} for k, v in pr["tools"].items()]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# reading a run back
# ---------------------------------------------------------------------------
def load_summary(run_dir: str | Path) -> dict[str, Any]:
    """A layout-flow run's ``summary.json`` (the trial's `log_file`)."""
    p = Path(run_dir)
    if p.is_dir():
        p = p / "summary.json"
    return json.loads(Path(p).read_text())


def stage_times(summary: Mapping[str, Any]) -> pd.DataFrame:
    """build / DRC / LVS / PEX / postlayout wall time + verdict for one run."""
    rows = []
    for stage, d in (summary.get("stages") or {}).items():
        if not isinstance(d, dict):
            continue
        verdict = "error" if d.get("error") else ("ok" if d.get("ok", True) else "fail")
        rows.append({"stage": stage, "secs": round(float(d.get("secs", float("nan"))), 1), "verdict": verdict})
    return pd.DataFrame(rows)


def pex_net_table(summary: Mapping[str, Any], *, top: int = 12) -> pd.DataFrame:
    """Per-net extracted capacitance from a run's scalars.

    The backend lands two families (see ``parasitic_scalars``): ``c_<net>_ff`` is C from the
    net to {ground ∪ the flow's ``ac_gnd_nets``} — what a bench that AC-grounds those rails
    actually sees — and ``ctot_<net>_ff`` is the Σ-to-anything sum. The gap between them is
    the net's coupling into other signal nets.
    """
    sc = summary.get("scalars") or {}
    nets: dict[str, dict[str, float]] = {}
    for key, val in sc.items():
        if val is None:
            continue
        if key.startswith("ctot_") and key.endswith("_ff"):
            nets.setdefault(key[5:-3], {})["c_total_fF"] = float(val)
        elif key.startswith("c_") and key.endswith("_ff") and "__" not in key:
            nets.setdefault(key[2:-3], {})["c_to_ac_gnd_fF"] = float(val)
    rows = [{"net": n, **v} for n, v in nets.items()]
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if "c_total_fF" in df:
        df = df.sort_values("c_total_fF", ascending=False)
    return df.head(top).reset_index(drop=True).round(4)


# ---------------------------------------------------------------------------
# the trial table
# ---------------------------------------------------------------------------
def _entries_from_checkpoints(ckpt_dir: str | Path) -> list[dict[str, Any]]:
    """Every entry from every checkpoint JSON in ``ckpt_dir``, in file order.

    The optimizer EMPTIES its in-memory log after each autosave, so with autosave on the
    complete trace lives in the checkpoint files, not on the object. Reading them back is
    also the crash-safe resume story: this is exactly what survives a killed process.
    """
    out: list[dict[str, Any]] = []
    for path in sorted(Path(ckpt_dir).glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:  # a torn file cannot happen (atomic writes) but be kind
            continue
        for e in data.get("optimization_log") or []:
            out.append(e)
    return out


def trials_table(optimizer: Any, *, checkpoint_dir: str | Path | None = None) -> pd.DataFrame:
    """One row per trial: ``trial, score``, every dut_param, every target spec's achieved
    ``curr_val``, and ``run_dir`` (the layout run that produced it).

    Entries come from the crash-safe checkpoints when ``checkpoint_dir`` is given (the
    complete trace across autosave resets) and otherwise from the optimizer's in-memory log;
    both are the same records.

    Parameter values: the log entry's ``point.params`` are already in PHYSICAL units (the
    optimizer denormalizes before evaluating and logs what it evaluated) — do **not** push
    them through ``denormalize_params`` again, or every value silently lands outside its own
    ``[min_val, max_val]``. Where a trial's layout run dir is reachable, its ``summary.json``
    wins: that file records the knobs and the per-run ``sizing`` the flow actually built with,
    grid-snapping included, which is the ground truth for reproducing a point.
    """
    raw: list[dict[str, Any]] = []
    if checkpoint_dir is not None and Path(checkpoint_dir).is_dir():
        raw = _entries_from_checkpoints(checkpoint_dir)
    if not raw:
        raw = [
            {
                "point": {"params": dict(e.point.params), "score": float(e.point.score)},
                "fit_summary": e.fit_summary or {},
                "log_file": e.log_file or {},
            }
            for e in getattr(optimizer, "optimization_log", [])
        ]

    rows: list[dict[str, Any]] = []
    for i, e in enumerate(raw):
        point = e.get("point") or {}
        values = {k: float(v) for k, v in (point.get("params") or {}).items()}

        log_file = e.get("log_file") or {}
        first = next(iter(log_file.values()), None) if isinstance(log_file, dict) else log_file
        run_dir = str(Path(str(first)).parent) if first else ""
        if run_dir:  # the flow's own record of what it built wins
            try:
                s = load_summary(run_dir)
                values.update({k: float(v) for k, v in (s.get("params") or {}).items() if k in values})
                values.update({k: float(v) for k, v in (s.get("sizing") or {}).items() if k in values})
            except (OSError, ValueError, TypeError):
                pass

        row: dict[str, Any] = {"trial": i, "score": float(point.get("score", float("nan")))}
        row.update({k: round(v, 4) for k, v in values.items()})
        for name, d in (e.get("fit_summary") or {}).items():
            row[name] = float(d["curr_val"]) if isinstance(d, dict) and "curr_val" in d else float("nan")
        row["run_dir"] = run_dir
        rows.append(row)
    return pd.DataFrame(rows)


def feasible_mask(df: pd.DataFrame, constraints: Mapping[str, float], *, gates: Iterable[str] = ()) -> pd.Series:
    """True where every ``metric >= threshold`` in ``constraints`` holds and every gate == 1."""
    def col(name: str, missing: float) -> pd.Series:
        s = df[name] if name in df.columns else pd.Series(missing, index=df.index)
        return s.astype(float).fillna(missing)

    ok = pd.Series(True, index=df.index)
    for name, lo in constraints.items():
        ok &= col(name, -math.inf) >= lo
    for g in gates:
        ok &= col(g, 0.0) >= 1.0
    return ok


def knob_delta(baseline: Mapping[str, float], best: Mapping[str, float], names: Iterable[str]) -> pd.DataFrame:
    """baseline → best per param, with the signed delta and % — the "what moved" table."""
    rows = []
    for n in names:
        b, x = float(baseline[n]), float(best[n])
        rows.append(
            {
                "param": n,
                "kind": "sizing" if n in SIZING_PARAMS else "layout knob",
                "baseline": round(b, 4),
                "best": round(x, 4),
                "delta": round(x - b, 4),
                "delta_%": round(100.0 * (x - b) / b, 1) if b else float("nan"),
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# the static replay fallback
# ---------------------------------------------------------------------------
def replay_path() -> Path:
    return REPLAY_JSON


def save_replay(payload: Mapping[str, Any], path: str | Path | None = None) -> Path:
    """Freeze the notebook's live numbers so a toolchain-less environment still renders §4-§6.

    Written by the notebook itself after a live run (and committed), never by the test lane.
    """
    p = Path(path or REPLAY_JSON)
    p.write_text(json.dumps(payload, indent=1, default=str))
    return p


def load_replay(path: str | Path | None = None) -> dict[str, Any] | None:
    p = Path(path or REPLAY_JSON)
    if not p.is_file():
        return None
    data = json.loads(p.read_text())
    if isinstance(data.get("trials"), list):
        data["trials"] = pd.DataFrame(data["trials"])
    return data


def png_or_note(png: str | Path) -> str:
    """A committed PNG path if it exists, else a one-line note — for the render cells."""
    p = Path(png)
    return str(p) if p.is_file() else f"(no render at {p}; klayout not available here)"


def which_report() -> pd.DataFrame:  # pragma: no cover — convenience for debugging a host
    rows = [{"tool": t, "path": shutil.which(t) or "—"} for t in ("ngspice", "klayout", "kpex", "magic", "netgen")]
    rows.append({"tool": "python (this kernel)", "path": sys.executable})
    return pd.DataFrame(rows)
