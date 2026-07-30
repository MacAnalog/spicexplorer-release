"""Derived SQLite index over WORK_ROOT (plan_project_filesystem P2 — §3.7/D-1).

The filesystem stays canonical; ``index.db`` is a rebuildable cache that makes
the registry listers O(1 query) instead of O(read-every-json). Contract:

- **Single writer**: only the API process writes the DB (this module). The
  storage kernel (``spicexplorer_core.workspace``) and orchestration agents
  write the filesystem only and never link sqlite.
- **Reads degrade, never 500**: any sqlite/OS error falls back to the FS scan
  (``project_service``); a broken/missing/corrupt index costs latency, not
  correctness.
- **Self-heal**: every read runs a cheap existence probe (one scandir) against
  the FS — an out-of-band project/run created or deleted by an agent/CLI is
  re-scanned on the next read. *Content* freshness (rename, run status flips)
  comes from write-through at the API's own mutation points plus the full
  rebuild at startup; an out-of-band content edit surfaces at the next rebuild
  (documented P2 limitation — P3's run envelope closes it).
- ``journal_mode=DELETE`` (not WAL): WAL's ``-shm`` mmap coherence is not
  guaranteed when the Docker and native lanes share the ``/work`` bind mount.

Rebuild CLI: ``python -m spicexplorer_api.services.index_db [--work-root PATH]``.
Schema: ``projects`` + ``runs`` are populated in P2; ``metrics`` + ``artifacts``
are reserved (DDL only) for the P3 run envelope.
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

logger = logging.getLogger(__name__)

INDEX_DB_ENV = "SPICEXPLORER_INDEX_DB"
_UNSCOPED = ""  # project_id key for WORK_ROOT/runs (runs not owned by a project)

_DDL = """
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS projects(
    id TEXT PRIMARY KEY,
    name TEXT, updated TEXT, run_count INTEGER, best_score REAL,
    source_kind TEXT, pdk TEXT, rev INTEGER
);
CREATE TABLE IF NOT EXISTS runs(
    project_id TEXT NOT NULL,          -- '' = unscoped (WORK_ROOT/runs)
    dir_name TEXT NOT NULL,            -- the run directory name (FS identity today;
                                       -- == run_id once P3 unifies them, D-4)
    run_id TEXT, kind TEXT, status TEXT, started TEXT, ended TEXT,
    best_score REAL,
    raw TEXT NOT NULL,                 -- the full run.json — listers return it
                                       -- verbatim so no key is ever dropped
    PRIMARY KEY (project_id, dir_name)
);
CREATE INDEX IF NOT EXISTS runs_by_project ON runs(project_id, dir_name DESC);
-- P3 run-envelope metrics (a run.json's flat metrics: {name: value} map).
CREATE TABLE IF NOT EXISTS metrics(
    run_id TEXT NOT NULL, name TEXT NOT NULL, value REAL, corner TEXT
);
CREATE INDEX IF NOT EXISTS metrics_by_run ON metrics(run_id);
-- Reserved for the P3 artifacts registry (created now so the schema file is stable):
CREATE TABLE IF NOT EXISTS artifacts(
    run_id TEXT NOT NULL, rel_path TEXT NOT NULL, kind TEXT, bytes INTEGER, sha TEXT
);
"""


def db_path() -> Path:
    """``$SPICEXPLORER_INDEX_DB`` else ``WORK_ROOT/index.db``."""
    env = os.environ.get(INDEX_DB_ENV)
    if env:
        return Path(env).expanduser()
    from spicexplorer_api.app_config import work_root
    return work_root() / "index.db"


@contextmanager
def _db() -> Iterator[sqlite3.Connection]:
    """A short-lived connection (per call — trivially thread-safe) with the
    bind-mount-safe pragmas and the schema ensured. Always closed."""
    with closing(sqlite3.connect(db_path(), timeout=5.0)) as con:
        con.execute("PRAGMA journal_mode=DELETE")
        con.execute("PRAGMA busy_timeout=5000")
        con.executescript(_DDL)
        yield con
        con.commit()


# ---------- FS truth → rows (the scanner) ----------

def _fs_project_ids() -> list[str]:
    """The registry's project ids straight off the FS (the existence probe)."""
    from spicexplorer_api.app_config import projects_root
    from spicexplorer_api.services import project_service as ps
    return sorted(
        pd.name for pd in projects_root().iterdir()
        if pd.is_dir() and ps.project_exists(pd.name)
    )


def _fs_run_dir_names(project_id: str | None) -> set[str]:
    """Run dir names (those carrying a run.json) for the probe — one scandir."""
    from spicexplorer_api.services import project_service as ps
    return {
        rd.name for rd in ps.runs_dir(project_id or None).iterdir()
        if rd.is_dir() and (rd / "run.json").exists()
    }


def _scope_rows(project_id: str | None) -> tuple[list[tuple[Any, ...]], list[tuple[Any, ...]]]:
    """``(run_rows, metric_rows)`` for one scope, read from the FS in a SINGLE
    pass — each run.json is parsed once and its flat ``metrics: {name: value}``
    map is flattened to metric rows off the same dict (no second re-parse)."""
    from spicexplorer_api.services import project_service as ps
    run_rows: list[tuple[Any, ...]] = []
    metric_rows: list[tuple[Any, ...]] = []
    for rd in sorted(ps.runs_dir(project_id or None).glob("*")):
        rj = rd / "run.json"
        if not rj.exists():
            continue
        try:
            d = json.loads(rj.read_text())
        except Exception:
            continue
        bs = d.get("best_score")
        run_rows.append((
            project_id or _UNSCOPED, rd.name,
            d.get("run_id"), d.get("kind"), d.get("status"),
            d.get("started"), d.get("ended"),
            float(bs) if isinstance(bs, (int, float)) else None,
            json.dumps(d),
        ))
        rid, metrics = d.get("run_id"), d.get("metrics")
        if rid and isinstance(metrics, dict):
            metric_rows.extend(
                (rid, name, float(val), None) for name, val in metrics.items()
                if isinstance(val, (int, float))
            )
    return run_rows, metric_rows


def _project_row(project_id: str, run_rows: list[tuple[Any, ...]]) -> tuple[Any, ...]:
    """One projects-table row, derived from the manifest + this scope's run rows
    (same rollup rule as ``project_service.list_projects``: max best_score)."""
    from spicexplorer_api.services import project_service as ps
    man = ps.read_manifest(project_id)
    scores = [r[7] for r in run_rows if r[7] is not None]
    return (
        project_id,
        man.get("name", project_id),
        man.get("updated") or man.get("created"),
        len(run_rows),
        max(scores) if scores else None,
        (man.get("source") or {}).get("kind", "unknown"),
        man.get("default_pdk"),
        man.get("rev"),
    )


def _replace_scope(con: sqlite3.Connection, scope: str,
                   run_rows: list[tuple[Any, ...]], metric_rows: list[tuple[Any, ...]]) -> None:
    """Replace one scope's runs + metrics rows in a single batched pass. Metrics
    are deleted BEFORE the runs rows (the old run set identifies the stale
    metrics) and re-inserted with one executemany, not one per run."""
    con.execute(
        "DELETE FROM metrics WHERE run_id IN (SELECT run_id FROM runs WHERE project_id=?)",
        (scope,),
    )
    con.execute("DELETE FROM runs WHERE project_id=?", (scope,))
    con.executemany("INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?)", run_rows)
    if metric_rows:
        con.executemany("INSERT INTO metrics VALUES (?,?,?,?)", metric_rows)


def _write_project(con: sqlite3.Connection, project_id: str) -> None:
    """Upsert one project + replace its run/metrics rows (the write-through unit)."""
    run_rows, metric_rows = _scope_rows(project_id)
    _replace_scope(con, project_id, run_rows, metric_rows)
    con.execute(
        "INSERT OR REPLACE INTO projects VALUES (?,?,?,?,?,?,?,?)",
        _project_row(project_id, run_rows),
    )


def _write_unscoped_runs(con: sqlite3.Connection) -> None:
    run_rows, metric_rows = _scope_rows(None)
    _replace_scope(con, _UNSCOPED, run_rows, metric_rows)


# ---------- rebuild ----------

def rebuild() -> dict[str, int]:
    """Full rescan: FS truth → index, one transaction. Cheap at registry scale
    (it reads exactly what the FS listers read); called at API startup and by
    the self-heal probes. Returns counts for logging."""
    pids = _fs_project_ids()
    with _db() as con:
        con.execute("DELETE FROM projects")
        con.execute("DELETE FROM runs")
        con.execute("DELETE FROM metrics")
        for pid in pids:
            _write_project(con, pid)
        _write_unscoped_runs(con)
        n_runs = con.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        con.execute(
            "INSERT OR REPLACE INTO meta VALUES ('last_rebuild', ?)",
            (datetime.now().isoformat(timespec="seconds"),),
        )
    return {"projects": len(pids), "runs": n_runs}


# ---------- write-through (API-process mutations only) ----------

def notify_project_changed(project_id: str) -> None:
    """Best-effort upsert after an API mutation (create/rename/touch/restore/
    run edit). Never raises — the FS write already succeeded and is canonical."""
    try:
        with _db() as con:
            _write_project(con, project_id)
    except Exception:
        logger.debug("index write-through failed for %r", project_id, exc_info=True)


def notify_project_deleted(project_id: str) -> None:
    try:
        with _db() as con:
            con.execute(
                "DELETE FROM metrics WHERE run_id IN"
                " (SELECT run_id FROM runs WHERE project_id=?)", (project_id,))
            con.execute("DELETE FROM projects WHERE id=?", (project_id,))
            con.execute("DELETE FROM runs WHERE project_id=?", (project_id,))
    except Exception:
        logger.debug("index delete failed for %r", project_id, exc_info=True)


def notify_runs_changed(project_id: str | None) -> None:
    """Refresh one scope's run rows (a run.json was written/renamed/deleted)."""
    try:
        with _db() as con:
            if project_id:
                _write_project(con, project_id)
            else:
                _write_unscoped_runs(con)
    except Exception:
        logger.debug("index run write-through failed for %r", project_id, exc_info=True)


# ---------- indexed reads (probe → self-heal → query; FS fallback) ----------

def list_projects() -> list[dict[str, Any]]:
    """Indexed twin of ``project_service.list_projects`` (same shape + order).
    Existence-probes the registry first so out-of-band creates/deletes self-heal."""
    from spicexplorer_api.services import project_service as ps
    try:
        fs_ids = _fs_project_ids()
        with _db() as con:
            idx_ids = sorted(r[0] for r in con.execute("SELECT id FROM projects"))
            if idx_ids != fs_ids:
                logger.info("index stale (projects %d≠%d) — rebuilding", len(idx_ids), len(fs_ids))
                con.execute("DELETE FROM projects")
                con.execute("DELETE FROM runs WHERE project_id != ?", (_UNSCOPED,))
                for pid in fs_ids:
                    _write_project(con, pid)
                # Prune metrics orphaned by the runs delete above (an out-of-band
                # project removal), so the metrics table can't outlive its runs.
                con.execute(
                    "DELETE FROM metrics WHERE run_id NOT IN"
                    " (SELECT run_id FROM runs WHERE run_id IS NOT NULL)")
            rows = con.execute(
                "SELECT id, name, updated, run_count, best_score, source_kind FROM projects"
            ).fetchall()
        out = [
            {"id": r[0], "name": r[1], "updated": r[2], "run_count": r[3],
             "best_score": r[4], "source": r[5]}
            for r in rows
        ]
        out.sort(key=lambda p: p.get("updated") or "", reverse=True)
        return out
    except Exception:
        logger.warning("index read failed — serving the FS scan", exc_info=True)
        return ps.list_projects()


def list_runs(project_id: str | None) -> list[dict[str, Any]]:
    """Indexed twin of ``project_service.list_runs`` (verbatim run.json dicts,
    newest-first by RECORDED start time, dir-name tiebreak — the P3 ordering).
    Probes the run dir set for self-heal."""
    from spicexplorer_api.services import project_service as ps
    try:
        scope = project_id or _UNSCOPED
        fs_names = _fs_run_dir_names(project_id)
        with _db() as con:
            idx_names = {
                r[0] for r in con.execute(
                    "SELECT dir_name FROM runs WHERE project_id=?", (scope,))
            }
            if idx_names != fs_names:
                logger.info("index stale (runs of %r) — rescanning", scope)
                if project_id:
                    _write_project(con, project_id)
                else:
                    _write_unscoped_runs(con)
            rows = con.execute(
                "SELECT raw FROM runs WHERE project_id=?"
                " ORDER BY COALESCE(started, '') DESC, dir_name DESC", (scope,)
            ).fetchall()
        return [json.loads(r[0]) for r in rows]
    except Exception:
        logger.warning("index read failed — serving the FS scan", exc_info=True)
        return ps.list_runs(project_id)


# ---------- CLI: python -m spicexplorer_api.services.index_db ----------

def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        prog="python -m spicexplorer_api.services.index_db",
        description="Rebuild the derived WORK_ROOT index (FS is canonical).",
    )
    ap.add_argument("--work-root", type=Path, default=None,
                    help="WORK_ROOT to index (default: $WORK_ROOT, else <repo>/work)")
    args = ap.parse_args(argv)
    if args.work_root:
        os.environ["WORK_ROOT"] = str(args.work_root)
    print(json.dumps({"db": str(db_path()), **rebuild()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
