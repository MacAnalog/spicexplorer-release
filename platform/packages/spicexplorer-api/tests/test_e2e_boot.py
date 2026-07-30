"""API boot E2E: launch the real uvicorn process (not an in-process TestClient) and hit a
handful of routes. Catches lifespan/startup/middleware/router-wiring failures that in-process
tests structurally cannot — the app module is imported by a fresh interpreter, the lifespan
hook actually runs, and requests cross a real socket. No SPICE, no DB required (the library
route degrades to 503 by contract when analog-db is not checked out).
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _get(url: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:  # >=400 still proves the route is wired
        return e.code, e.read()


@pytest.fixture(scope="module")
def server():
    port = _free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "spicexplorer_api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.time() + 30
        while True:
            if proc.poll() is not None:
                out = proc.stdout.read() if proc.stdout else ""
                pytest.fail(f"uvicorn exited during startup:\n{out}")
            try:
                if _get(f"{base}/health")[0] == 200:
                    break
            except Exception:
                pass
            if time.time() > deadline:
                proc.terminate()
                pytest.fail("server did not become ready within 30s")
            time.sleep(0.25)
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


def test_health(server: str) -> None:
    status, body = _get(f"{server}/health")
    assert status == 200
    assert json.loads(body) == {"status": "ok"}


def test_openapi_spec_serves(server: str) -> None:
    status, body = _get(f"{server}/openapi.json")
    assert status == 200
    spec = json.loads(body)
    assert spec["info"]["title"] == "SpiceXplorer API"
    assert len(spec["paths"]) > 20  # all routers mounted, not a partial app


def test_env_probe(server: str) -> None:
    status, body = _get(f"{server}/api/env")
    assert status == 200
    assert json.loads(body)  # parses; field set is EnvResponse's contract


def test_library_route_wired(server: str) -> None:
    # the availability probe answers 200 whether or not analog-db is checked out; the
    # catalog route answers 200 with it and 503 (by contract) without it — anything else
    # means the router or the requires_db seam broke.
    status, body = _get(f"{server}/api/library/status")
    assert status == 200
    assert json.loads(body)
    status, _ = _get(f"{server}/api/library/catalog")
    assert status in (200, 503)
