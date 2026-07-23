"""Console-script smoke: the installed ``netlist2xschem`` entry point (the workspace's only
``[project.scripts]``) must wire up end-to-end — catches entry-point/argparse/import breakage
that in-process tests bypass."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_console_script_help() -> None:
    exe = Path(sys.executable).with_name("netlist2xschem")
    assert exe.exists(), "netlist2xschem console script not installed (uv sync)"
    proc = subprocess.run([str(exe), "--help"], capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert "netlist" in proc.stdout.lower()
