"""A stand-in for `ocean -nograph` used by test_ocean_metrics.py (no Cadence needed).

Reads SKILL blocks emitted by `render_measure_block` from stdin, and on `close(...)`
writes the metrics file the real ocean would have produced: every fprintf'd metric name
as ``name=42.0`` plus the sentinel. Env knobs:

* ``SXQ_FAKE_DIE_AFTER=<n>`` — exit(1) abruptly after writing the n-th metrics file
  (exercises the session's dead-process respawn path).
* ``SXQ_FAKE_HANG=1`` — swallow input and never write a file (exercises the timeout path).
"""

import os
import re
import sys

OUTFILE_RE = re.compile(r'outfile\("([^"]+)"\)')
NAME_RE = re.compile(r'fprintf\(__sxq_port "([A-Za-z0-9_.:\-]+)=')
SENTINEL = "__spicexplorer_ocean_done__"

die_after = int(os.environ.get("SXQ_FAKE_DIE_AFTER", "0"))
hang = os.environ.get("SXQ_FAKE_HANG") == "1"

out_path = None
names: dict[str, None] = {}
written = 0

while True:
    line = sys.stdin.readline()
    if not line:
        sys.exit(0)
    line = line.strip()
    if line == "exit":
        sys.exit(0)
    if hang:
        continue
    m = OUTFILE_RE.search(line)
    if m:
        out_path = m.group(1)
        names = {}
        continue
    for name in NAME_RE.findall(line):
        if name != SENTINEL:
            names[name] = None
    if line.startswith("close(") and out_path is not None:
        with open(out_path, "w") as f:
            for name in names:
                f.write(f"{name}=42.0\n")
            f.write(f"{SENTINEL}=1\n")
        written += 1
        out_path = None
        if die_after and written >= die_after:
            os._exit(1)
