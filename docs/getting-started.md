# Getting started (native, no Docker)

Run the SpiceXplorer **API** and **Studio UI** directly on your machine with
[uv](https://docs.astral.sh/uv/) (Python) and Node. For the container route
instead, see [docker.md](docker.md).

Every step below has a `make` shortcut (left) and the raw command it runs
(right) — use whichever you prefer. All paths are relative to the repo root.

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** — Python package/venv manager (installs its own Python).
- **Node 22+** and **npm** — for the Studio UI.
- *(optional)* **ngspice** + an open **PDK** (sky130 / gf180 / IHP sg13g2) — only if you want live SPICE simulation. See [Live SPICE](#live-spice-optional).

## Repository layout

```
.
├── platform/     # Python uv workspace: the 6 released packages (see platform/README.md)
│   ├── packages/spicexplorer-core, -circuitgraph, -netlist2xschem, -waveview,
│   │            spicexplorer (optimizer), spicexplorer-api (FastAPI)
│   ├── pyproject.toml          # the (virtual) workspace root
│   └── .spicexplorer-root      # workspace-root marker (do not remove)
├── ui/           # Next.js "Studio" front-end (see ui/README.md)
└── analog-db/    # circuit corpus the API's /api/library routes read
```

`platform/` is a **virtual uv workspace** (no root package): the packages under
`packages/*` are its members, wired together via `[tool.uv.sources]`. One
`uv sync` builds a single `.venv` with all of them.

## 1. Build the platform venv

```bash
make sync
```

which runs, from the repo root:

```bash
cd platform && uv sync                       # create platform/.venv with all 6 packages + deps
cd platform && uv pip install --no-deps -e ../analog-db
```

Notes specific to this repo:

- **Run `uv sync` inside `platform/`**, not at the repo root — the workspace and
  its `.venv` live there. (The repo root is a plain monorepo, not a uv workspace.)
- The second line **borrows the `analog-db` corpus editable** into the same venv.
  `analog-db` is its own component (not a workspace member), so `uv sync` does not
  pull it; the API's `/api/library` routes need it importable. `--no-deps` keeps
  it from dragging extra dependencies in.
- On Linux, `torch` (pulled by the optimizer's `[torch]` extra) resolves to the
  **CPU** wheel — the workspace pins the PyTorch CPU index, so no CUDA download.

## 2. Run the API

```bash
make api                                     # → http://localhost:8000  (docs at /docs)
```

which is:

```bash
cd platform && SPICEXPLORER_ANALOG_DB="$(pwd)/../analog-db" \
  uv run uvicorn spicexplorer_api.main:app --reload --port 8000
```

`SPICEXPLORER_ANALOG_DB` points the API at the corpus directory. Without a
simulator on `PATH` the API starts fine in **replay mode** — check with
`curl localhost:8000/api/env` (`pdk_ok:false`, `live_runs_enabled:false`).

## 3. Run the Studio UI

In a second terminal:

```bash
make ui                                      # → http://localhost:4000
```

which is:

```bash
cd ui && npm ci                              # first time only
cd ui && BACKEND_URL=http://127.0.0.1:8000 npm run dev -- -p 4000
```

The UI dev server proxies `/api/*` to `BACKEND_URL`, so open
**http://localhost:4000** and it talks to the API from step 2. Override ports
with `make api BACKEND_PORT=8010` / `make ui FRONTEND_PORT=4010`.

## Tests & checks

```bash
make test        # cd platform && uv run pytest -m 'not slow'   (fast, no SPICE)
make check       # lint (ruff + eslint) + UI typecheck + fast tests
```

`make build-ui` produces the production UI bundle; `make gen-types` regenerates
the UI's TypeScript types from the API's OpenAPI spec.

## Live SPICE (optional)

The released packages are simulator-agnostic; live simulation needs a simulator
and a PDK on the machine running the API:

1. Install **ngspice** (`apt install ngspice`, `brew install ngspice`, or from source).
2. Install an **open PDK** — sky130, gf180, or IHP sg13g2 — and point the toolchain at it (see `analog-db/README.md` for the per-PDK details).
3. Restart `make api`. `GET /api/env` should now report `pdk_ok:true` and
   `live_runs_enabled:true`, and live runs / single-sim endpoints become active.

The Docker image in [docker.md](docker.md) deliberately omits the simulator to
stay small, so live SPICE is a native-only path in this repo.
