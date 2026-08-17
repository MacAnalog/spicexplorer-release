"""The tiny stdin/stdout protocol a post-layout **measure** module speaks.

A layout-flow "testbench" (``spicexplorer.backends.layout``) can end with a block-specific
bench step: after build → DRC → LVS → PEX it launches ``measure.python`` (any interpreter —
typically the block's own venv, which has *its* benches and their SPICE wrappers) and hands
it ONE JSON request on stdin::

    {"pex_subckt": "<path to the prepared .subckt file>",
     "work_dir":   "<this trial's run dir>",
     "params":     {<the candidate layout knobs>},
     "corner":     {<the active PVT corner as a dict, or null>},
     "extra":      {<measure.extra from the flow spec, or {}>}}

and expects exactly ONE JSON line back on stdout (anything else on stdout is ignored,
stderr is captured for the log)::

    {"scalars": {"ugf_mhz": 29.4, "pm_deg": 61.9, ...}, "status": "ok"}

Every key of ``scalars`` becomes a metric the optimizer's ``TargetSpec.name`` can score.
A non-finite / missing scalar reads NaN downstream (→ the optimizer's MAX_PENALTY).

This module is pure stdlib so it imports in ANY interpreter (the backend puts this
package's ``src`` on ``PYTHONPATH`` for the subprocess). Two ways to use it:

* write ``def measure(req: dict) -> dict[str, float]`` in your module and point the flow
  spec at it (``measure: {module: measure_post.py, callable: measure, python: …}``) — the
  backend runs it through :func:`serve`;
* or make the module a script: ``if __name__ == "__main__": serve(measure)`` — then it can
  also be exercised by hand: ``echo '{"pex_subckt": …}' | python measure_post.py``.
"""

from __future__ import annotations

import json
import math
import sys
import traceback
from typing import Any, Callable, Mapping

RESULT_MARK = "@@layout-measure@@"


def read_request(stream=None) -> dict[str, Any]:
    """Parse the JSON request from ``stream`` (default stdin)."""
    text = (stream or sys.stdin).read()
    req = json.loads(text) if text.strip() else {}
    if not isinstance(req, dict):
        raise ValueError("measure request must be a JSON object")
    return req


def _clean(scalars: Mapping[str, Any]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for k, v in scalars.items():
        try:
            f = float(v)
        except (TypeError, ValueError):
            out[str(k)] = None
            continue
        out[str(k)] = f if math.isfinite(f) else None  # NaN is not JSON; None → NaN downstream
    return out


def write_result(
    scalars: Mapping[str, Any] | None,
    *,
    status: str = "ok",
    error: str | None = None,
    stream=None,
) -> None:
    """Emit the one-line JSON reply (marked so it is unambiguous amid other stdout noise)."""
    payload: dict[str, Any] = {"scalars": _clean(scalars or {}), "status": status}
    if error:
        payload["error"] = error
    out = stream or sys.stdout
    out.write(RESULT_MARK + json.dumps(payload) + "\n")
    out.flush()


def parse_result(stdout: str) -> dict[str, Any] | None:
    """The backend side: find the marked reply line in a subprocess' stdout (last one wins)."""
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith(RESULT_MARK):
            return json.loads(line[len(RESULT_MARK):])
    # tolerate an unmarked bare-JSON last line (hand-written scripts)
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(d, dict) and "scalars" in d:
                return d
    return None


def serve(fn: Callable[[dict[str, Any]], Mapping[str, Any]]) -> int:
    """Run ``fn(request) -> scalars`` over stdin/stdout; never raises (errors are reported
    in the reply as ``status: error`` with an empty scalar set). Returns the exit code."""
    try:
        req = read_request()
    except Exception as exc:  # malformed request: still answer in-protocol
        write_result({}, status="error", error=f"bad request: {exc}")
        return 2
    try:
        scalars = fn(req)
    except Exception:
        write_result({}, status="error", error=traceback.format_exc()[-4000:])
        return 1
    write_result(scalars)
    return 0


__all__ = ["RESULT_MARK", "read_request", "write_result", "parse_result", "serve"]
