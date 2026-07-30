# Running with Docker

A lightweight local stack — the **API** (`:8000`) and the **Studio UI**
(`:4000`) — built from the sources in this repo. Nothing to install but Docker
(with the Compose plugin). For the native route, see
[getting-started.md](getting-started.md).

## Bring it up

```bash
make up                 # == docker compose up --build
```

Then open **http://localhost:4000**. First build compiles the UI and resolves
the Python workspace, so it takes a few minutes; later runs are cached.

```bash
make logs S=ui          # tail one service (== docker compose logs -f ui)
make down               # stop (== docker compose down)
```

## What runs

| Service | Image | Port | Built from |
|---|---|---|---|
| `api` | `spicexplorer-api:release` | `8000` | [`Dockerfile.api`](../Dockerfile.api) (context = repo root) |
| `ui`  | `spicexplorer-ui:release`  | `4000` | [`ui/Dockerfile.prod`](../ui/Dockerfile.prod) (Next.js standalone) |

Wiring: the UI is built with `BACKEND_URL=http://api:8000`, so the browser talks
only to `:4000` and the UI proxies `/api/*` to the `api` service over the compose
network. Change host ports without editing files:

```bash
BACKEND_PORT=8010 FRONTEND_PORT=4010 docker compose up --build
LOG_LEVEL=DEBUG docker compose up --build      # api log level (default INFO)
```

## No live SPICE in the container (by design)

The `api` image carries **no ngspice and no PDK**, keeping it small. The app runs
in **replay / cached mode**: `GET http://localhost:8000/api/env` reports
`pdk_ok:false` and `live_runs_enabled:false`. Everything that doesn't need a
simulator works — the Studio UI, the reference library, score shaping, and
compare/explore over cached checkpoints. Live simulation and single-sim
endpoints are disabled.

To **run live SPICE**, use the native path (a local ngspice + open PDK) in
[getting-started.md](getting-started.md#live-spice-optional). A full
simulation-in-container image (ngspice compiled from source + vendored PDKs) is
part of the project's private developer tooling and is not included in this
public release.

## Rebuild / clean

```bash
docker compose build --no-cache api     # force a clean API rebuild
docker compose down -v                  # stop and drop volumes
```

> Heads-up: these images are for **local evaluation**, not a hardened production
> deployment. The UI image already runs as a non-root user (see
> `ui/Dockerfile.prod`); review resource limits, secrets, and TLS termination
> before exposing anything beyond localhost.
