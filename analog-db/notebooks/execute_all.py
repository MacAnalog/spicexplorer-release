"""Execute every notebook in this directory top-to-bottom (the CI notebook-smoke lane).

The notebooks are written to run PDK-free on a fresh clone — SPICE cells detect whether a simulator
and the PDK are present and skip when they are not — so a clean execution here is a real end-to-end
check of the library APIs they demonstrate (a gm/ID back-annotation bug was once caught only by a
notebook cell).

A notebook is in one of two formats while the notebooks move to marimo:

- a marimo notebook, a ``.py`` file that imports ``marimo`` and assigns ``app = marimo.App(...)``,
  runs as ``python <nb>.py`` in a subprocess: every cell runs in dependency order, and a cell that
  raises ends the run with exit code 1 and a traceback. A marimo notebook stores no outputs, so a
  clean run is also the proof that it reproduces them;
- a Jupyter ``.ipynb`` runs in memory under nbclient; the committed file is never rewritten.

A notebook present in both formats is an error: a converted notebook's ``.ipynb`` must be deleted.

Each notebook runs with its working directory set to this folder, and with this environment added
to the caller's:

- ``TMPDIR``, ``TMP``, ``TEMP``: a directory of its own, made under the caller's ``TMPDIR`` and
  deleted after the run, so the scratch directories a notebook and its simulator runs create cannot
  accumulate in the per-user ``/tmp`` quota;
- ``MPLBACKEND=Agg``: no plot window opens;
- ``PLOTLY_RENDERER=json``: in script mode plotly's default renderer is the browser one, which
  serves the figure once and then waits, without limit, for a browser to fetch it;
- ``TQDM_DISABLE=1``: no progress bars in the log;
- ``SPICEXPLORER_ANALOG_DB``, when unset: this checkout, so the platform backend that
  ``analog_db_sizing_playground`` calls reads the same circuits as ``spicexplorer_analog_db`` does.

Timeout: ``TIMEOUT_S`` caps each cell of an ``.ipynb`` and the whole run of a marimo notebook, which
has no per-cell timeout. On expiry the marimo notebook's process group is killed, simulator included.

Usage (borrowed platform venv: marimo from its dev group, plus nbformat + nbclient):
    $VENV/bin/python notebooks/execute_all.py
"""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TIMEOUT_S = 600  # per cell of an .ipynb; the whole run of a marimo notebook

_MARIMO_IMPORT = re.compile(r"^import marimo\s*$", re.M)
_MARIMO_APP = re.compile(r"^app = marimo\.App\(", re.M)


def is_marimo_notebook(path: Path) -> bool:
    """True for a ``.py`` file that imports marimo and assigns ``app = marimo.App(...)``."""
    if path.suffix != ".py" or not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return bool(_MARIMO_IMPORT.search(text) and _MARIMO_APP.search(text))


def notebook_files(folder: Path = HERE) -> list[Path]:
    """Every notebook in ``folder``: each ``.ipynb`` and each marimo ``.py``, sorted by name."""
    return sorted(p for p in folder.iterdir() if p.suffix == ".ipynb" or is_marimo_notebook(p))


def notebook_env(tmp: Path) -> dict[str, str]:
    """The caller's environment with the overrides listed in the module docstring."""
    env = dict(os.environ)
    env.update(
        TMPDIR=str(tmp),
        TMP=str(tmp),
        TEMP=str(tmp),
        MPLBACKEND="Agg",
        PLOTLY_RENDERER="json",
        TQDM_DISABLE="1",
    )
    env.setdefault("SPICEXPLORER_ANALOG_DB", str(HERE.parent))
    return env


def _tail(text: str, lines: int = 60) -> str:
    return "\n".join(text.rstrip().splitlines()[-lines:])


def run_marimo(path: Path, env: dict[str, str]) -> str | None:
    """Run a marimo notebook as ``python <nb>.py``; return None on success, else the reason."""
    proc = subprocess.Popen(
        [sys.executable, str(path)],
        cwd=HERE,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,  # its own process group, so a timeout also kills its children
    )
    try:
        out, err = proc.communicate(timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        out, err = proc.communicate()
        return (
            f"did not finish within {TIMEOUT_S} s (whole-run cap)\n"
            f"--- stdout (tail) ---\n{_tail(out)}\n--- stderr (tail) ---\n{_tail(err)}"
        )
    if proc.returncode != 0:
        return (
            f"exited {proc.returncode}: a cell raised\n"
            f"--- stderr (tail) ---\n{_tail(err)}\n--- stdout (tail) ---\n{_tail(out, 20)}"
        )
    return None


def run_ipynb(path: Path, env: dict[str, str]) -> str | None:
    """Execute a Jupyter notebook in memory with nbclient; return None on success, else the reason."""
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb, timeout=TIMEOUT_S, kernel_name="python3", resources={"metadata": {"path": str(HERE)}}
    )
    try:
        client.execute(env=env)
    except Exception as exc:  # nbclient raises CellExecutionError et al.
        return str(exc)
    return None


def main() -> int:
    notebooks = notebook_files()
    if not notebooks:
        print("no notebooks found", file=sys.stderr)
        return 1
    stems = [p.stem for p in notebooks]
    both = sorted({s for s in stems if stems.count(s) > 1})
    if both:
        print(
            f"in both formats (delete the converted notebook's .ipynb): {', '.join(both)}",
            file=sys.stderr,
        )
        return 1
    failed: list[str] = []
    for path in notebooks:
        print(f"== executing {path.name}", flush=True)
        tmp = Path(tempfile.mkdtemp(prefix=f"nb_{path.stem}_"))
        start = time.monotonic()
        try:
            run = run_ipynb if path.suffix == ".ipynb" else run_marimo
            reason = run(path, notebook_env(tmp))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        if reason is None:
            print(f"   ok ({time.monotonic() - start:.0f} s)", flush=True)
        else:
            print(f"!! {path.name} failed: {reason}", file=sys.stderr, flush=True)
            failed.append(path.name)
    if failed:
        print(f"FAILED: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"all {len(notebooks)} notebooks executed cleanly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
