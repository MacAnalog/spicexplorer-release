<!-- Managed by the private release infra (scripts/release/repo/) — edit there,
     not here; the next port overwrites this file. -->
# SpiceXplorer

[![lint](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/lint.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/lint.yml)
[![analog-db](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/analog-db.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/analog-db.yml)
[![platform](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/platform.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/platform.yml)
[![ui](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/ui.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/ui.yml)

Open-source releases from the SpiceXplorer analog design-automation project,
developed by the MacAnalog research group at McMaster University. The project
is published incrementally; this monorepo grows one component at a time, each
as a curated snapshot.

## Components

| Directory | What it is | Status |
|---|---|---|
| [`analog-db/`](analog-db/) | Analog circuit database — the topology/circuit registry (netlists, datasheets, class libraries, testbench templates) and its tiered verification harness | released |
| [`platform/`](platform/) | SpiceXplorer platform packages: `spicexplorer-core` (foundation), `spicexplorer-circuitgraph` + `spicexplorer-netlist2xschem` (netlist tools), `spicexplorer-waveview` (result viewer), `spicexplorer` (optimization), `spicexplorer-api` (FastAPI adapter) | released |
| [`ui/`](ui/) | SpiceXplorer "Studio" — the Next.js front-end (HTTP/SSE) over the platform api | released |

Each component keeps its own `README.md`, `LICENSE`, and (for Python) `pyproject.toml`;
a `.release-provenance.json` in each records the snapshot it was cut from.

## Quickstart

Two ways to bring the app (API + Studio UI) up. **Full walkthroughs:**
[docs/getting-started.md](docs/getting-started.md) (native) and
[docs/docker.md](docs/docker.md) (Docker).

**Docker** — nothing to install but Docker:

```bash
make up            # build + run: API on :8000, Studio UI on :4000
# open http://localhost:4000        (make down to stop)
```

**Native** — [uv](https://docs.astral.sh/uv/) (Python) + Node 22+, two terminals:

```bash
make sync          # build the platform venv and borrow the analog-db corpus
make api           # terminal 1 — backend  → http://localhost:8000
make ui            # terminal 2 — frontend → http://localhost:4000
```

`make help` lists every target. Prefer raw commands? See the getting-started guide —
each `make` target is a one-line wrapper you can run by hand.

> **Live SPICE is optional and off by default.** The Docker image and a bare
> `uv sync` carry no simulator, so the app runs in replay/cached mode
> (`GET /api/env` → `pdk_ok:false`). To simulate, install a local **ngspice** and
> an open **PDK** (sky130 / gf180 / IHP sg13g2) and run the platform natively —
> see [docs/getting-started.md](docs/getting-started.md#live-spice-optional).

## Documentation

- [docs/getting-started.md](docs/getting-started.md) — install, run natively, run tests, enable live SPICE.
- [docs/docker.md](docs/docker.md) — the Docker stack, ports, environment, and its limits.
- Per-component detail: [`platform/README.md`](platform/README.md), [`ui/README.md`](ui/README.md), [`analog-db/README.md`](analog-db/README.md).

## Recommended tooling

- [uv](https://docs.astral.sh/uv/) for Python package management.
- Docker to run the containerized stack without a local Python/Node toolchain.
- Our forked schematic viewer for VS Code: [NooriDan/vscode-xschem-viewer-configurable](https://github.com/NooriDan/vscode-xschem-viewer-configurable).
