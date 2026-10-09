import marimo

__generated_with = "0.25.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # `/api/waveview/*` — REST tour (the UI's contract)

    The viewer's REST surface end-to-end against a live `spicexplorer-api` server:
    **open** an artifact by path → **wave** (display-ready, downsampled JSON) → **measure**
    (any Tier-1 recipe) → **scalars** (op-point tables) → **log** (parsed) → **SSE live
    tail** → **browse**. Everything the Studio UI's viewer page will call.

    This tour is simulator-free: the artifacts are synthesized in real on-disk formats by
    `spicexplorer_waveview.testing` (the same generators the fast tests trust), so it runs
    anywhere. Swap the paths for any real `.raw`/`-raw` artifact and every call below works
    unchanged — see the two live notebooks.
    """)
    return


@app.cell
def _():
    # artifacts to serve: a single-pole ngspice AC .raw + a full synthetic Spectre raw dir
    import plotly.io as pio

    pio.renderers.default = "notebook_connected"

    from spicexplorer_core import project_root
    from spicexplorer_waveview.testing import synth_ac_raw, synth_spectre_raw_dir

    WORK = project_root() / "work" / "waveview_demo_api"
    WORK.mkdir(parents=True, exist_ok=True)
    truth = synth_ac_raw(WORK / "tb_ac.raw")
    (WORK / "tb_ac.log").write_text("Note: synthetic run\nWarning: demo warning\nall good\n")
    synth_spectre_raw_dir(WORK / "amp-raw")
    sorted(p.name for p in WORK.iterdir())
    return WORK, truth


@app.cell
def _(WORK):
    # start the API (dev-style) on :8011 — NEVER :8000 natively (the Docker stack owns it)
    import os
    import subprocess
    import sys
    import time

    import httpx

    env = {**os.environ, "SPICEXPLORER_WAVEVIEW_ROOTS": str(WORK)}
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "spicexplorer_api.main:app", "--port", "8011"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    BASE = "http://127.0.0.1:8011"
    for _ in range(60):
        try:
            if httpx.get(f"{BASE}/health", timeout=1).status_code == 200:
                break
        except httpx.TransportError:
            time.sleep(0.5)
    print("server up:", httpx.get(f"{BASE}/health").json(), "| docs at", BASE + "/docs")
    return BASE, httpx, server


@app.cell
def _(BASE, httpx):
    # GET /api/waveview/measurements — the recipe catalog (what the UI can offer)
    cat = httpx.get(f"{BASE}/api/waveview/measurements").json()["measurements"]
    print(len(cat), "measurements;  e.g.:")
    {k: cat[k] for k in ("dcgain", "ugf", "thd", "thd_pss", "pm_loop", "icmr_range")}
    return


@app.cell
def _(BASE, WORK, httpx):
    # POST /api/waveview/open — path in, dataset meta out (path-whitelisted; engine-sniffed)
    meta = httpx.post(f"{BASE}/api/waveview/open", json={"path": str(WORK / "tb_ac.raw")}).json()
    DS = meta["dataset_id"]
    print({k: meta[k] for k in ("dataset_id", "engine", "log_path")})
    [(a["analysis"], a["sweep"], [s["name"] for s in a["signals"]]) for a in meta["analyses"]]
    return (DS,)


@app.cell
def _(BASE, DS, httpx):
    # GET .../wave — display-ready arrays; the server downsamples (LTTB here: 901 -> ≤128)
    import plotly.graph_objects as go

    wave = httpx.get(
        f"{BASE}/api/waveview/datasets/{DS}/wave",
        params={
            "analysis": "ac",
            "signals": "v(vout)",
            "fmt": "mag_db",
            "max_points": 128,
            "method": "lttb",
        },
    ).json()
    sig = wave["signals"][0]
    print(
        f"n_total={sig['n_total']}  n_returned={sig['n_returned']}  downsampled={sig['downsampled']}"
    )
    fig = go.Figure(go.Scatter(x=sig["x"], y=sig["y"], mode="lines+markers", name=sig["name"]))
    fig.update_xaxes(type="log", title="frequency (Hz)")
    fig.update_layout(
        title="UI-side plot straight from the wave endpoint",
        yaxis_title="dB",
        template="plotly_white",
    )
    fig
    return


@app.cell
def _(BASE, DS, httpx, truth):
    # POST .../measure — the registry over REST (per-item degradation, JSON-safe values)
    resp = httpx.post(
        f"{BASE}/api/waveview/datasets/{DS}/measure",
        json={
            "items": [
                {"name": "dcgain", "recipe": {"meas": "dcgain", "out": "v(vout)"}},
                {"name": "ugf", "recipe": {"meas": "ugf", "out": "v(vout)"}},
                {"name": "pm", "recipe": {"meas": "pm", "out": "v(vout)"}},
                {"name": "broken", "recipe": {"meas": "dcgain", "out": "v(nope)"}},
            ]
        },
    ).json()
    print(f"analytic truth: dcgain={truth['dcgain_db']:.2f} dB, ugf={truth['ugf_hz']:.3g} Hz")
    resp["results"]
    return


@app.cell
def _(BASE, WORK, httpx):
    # the Spectre-format artifact serves identically — plus op-point scalars per device
    meta_sp = httpx.post(f"{BASE}/api/waveview/open", json={"path": str(WORK / "amp-raw")}).json()
    print("spectre analyses:", [a["analysis"] for a in meta_sp["analyses"]])
    httpx.get(
        f"{BASE}/api/waveview/datasets/{meta_sp['dataset_id']}/scalars", params={"prefix": "X0.M0:"}
    ).json()
    return


@app.cell
def _(BASE, DS, httpx):
    # GET .../log — the parsed, severity-classified simulator log
    log = httpx.get(f"{BASE}/api/waveview/datasets/{DS}/log").json()
    print("counts:", log["counts"])
    [(ln["no"], ln["level"], ln["text"]) for ln in log["lines"]]
    return


@app.cell
def _(BASE, WORK, httpx):
    # GET /api/waveview/log/stream — SSE tail. follow=false drains and closes; with
    # follow=true the same endpoint keeps tailing a log a live simulation is writing.
    import json

    events = []
    with httpx.stream(
        "GET",
        f"{BASE}/api/waveview/log/stream",
        params={"path": str(WORK / "tb_ac.log"), "follow": "false"},
    ) as _r:
        for _line in _r.iter_lines():
            if _line:
                events.append(_line)
    events
    return (json,)


@app.cell
def _(BASE, WORK, httpx, json):
    # ...and the LIVE tail: append lines while streaming — they arrive as they are written
    import threading
    import time as _t

    live_log = WORK / "live.log"
    live_log.write_text("run started\n")

    def writer():
        for i in range(3):
            _t.sleep(0.4)
            with live_log.open("a") as f:
                f.write(
                    f"iteration {i}: score improved\n"
                    if i < 2
                    else "Error: injected for the demo\n"
                )

    threading.Thread(target=writer).start()
    got = []
    with httpx.stream(
        "GET",
        f"{BASE}/api/waveview/log/stream",
        params={"path": str(live_log), "poll_s": 0.2},
        timeout=10,
    ) as _r:
        for _line in _r.iter_lines():
            if _line.startswith("data: "):
                got.append(json.loads(_line[6:]))
                if len(got) >= 4:
                    break
    got
    return


@app.cell
def _(BASE, WORK, httpx):
    # GET /api/waveview/browse — artifact discovery for a picker UI
    httpx.get(f"{BASE}/api/waveview/browse", params={"dir": str(WORK)}).json()["entries"]
    return


@app.cell
def _(BASE, DS, httpx, server):
    # lifecycle + teardown
    print(httpx.delete(f"{BASE}/api/waveview/datasets/{DS}").json())
    server.terminate()
    server.wait(timeout=10)
    print("server stopped")
    return


if __name__ == "__main__":
    app.run()
