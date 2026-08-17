# Running with Docker

A local stack — the **API** (`:8000`) and the **Studio UI** (`:4000`) — built
from the sources in this repo. Nothing to install but Docker (with the Compose
plugin). For the native route, see [getting-started.md](getting-started.md).

Two lanes: `make up` is lightweight and has no simulator; **`make up-live` adds
ngspice and three open PDKs so live SPICE works with nothing installed on the
host** — see [Live SPICE in the container](#live-spice-in-the-container).

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
| `spice-base` | `spicexplorer-spice-base:release` | — | [`Dockerfile.spice-base`](../Dockerfile.spice-base). `live` profile: built only by `make up-live`, never started — the `api` `FROM`s it |

Wiring: the UI is built with `BACKEND_URL=http://api:8000`, so the browser talks
only to `:4000` and the UI proxies `/api/*` to the `api` service over the compose
network. Change host ports without editing files:

```bash
BACKEND_PORT=8010 FRONTEND_PORT=4010 docker compose up --build
LOG_LEVEL=DEBUG docker compose up --build      # api log level (default INFO)
```

## Live SPICE in the container

`make up` is deliberately lightweight: the `api` image carries **no ngspice and
no PDK**, so the app runs in **replay / cached mode**
(`GET http://localhost:8000/api/env` → `pdk_ok:false`, `live_runs_enabled:false`).
Everything that doesn't need a simulator works — the Studio UI, the reference
library, score shaping, compare/explore over cached checkpoints — but live
simulation and the single-sim endpoints are disabled.

To simulate, build the **EDA base image** and bring the stack up on top of it:

```bash
make up-live            # == make spice-base, then rebuild the api FROM it
```

Now `GET http://localhost:8000/api/env` reports `pdk_ok:true` and
`live_runs_enabled:true`, and you can start live optimizer runs from the UI —
**with nothing installed on the host**: no ngspice, no PDK download, no
`PDK_ROOT` to point at.

### What the base image contains

[`Dockerfile.spice-base`](../Dockerfile.spice-base) builds
`spicexplorer-spice-base:release`:

| | |
|---|---|
| **ngspice 45** | compiled from source, headless — OSDI + XSPICE codemodels, OpenMP, no X |
| **IHP sg13g2** | primary PDK — device models, `.spiceinit`, OSDI compact models, xschem symbols |
| **SkyWater sky130** | ngspice corner libs + `sky130_fd_pr` device models (BSIM4) |
| **GF gf180mcu** | ngspice model libs (BSIM4) |
| **xschem** | headless, for batch SPICE netlisting from `.sch` |

All three PDKs are **Apache-2.0** and vendored under
[`platform/docker/pdk/`](../platform/docker/pdk/) (see its `README.md`). They all
sit on the ngspice sourcepath, so a netlist selects one with its own `.lib` and
bare-name resolution works for each.

### Architecture and `OSDI_MODE`

The IHP models are Verilog-A compiled to OSDI, which is architecture-specific:

```bash
make up-live                      # OSDI_MODE=vendor (default) — reuse the
                                  # committed prebuilt x86-64 .osdi. Fast.
make up-live OSDI_MODE=compile    # build openvaf (Rust + LLVM-18) and compile
                                  # the Verilog-A for THIS arch. Slow, but the
                                  # native route on arm64 (Apple silicon).
```

`vendor` on arm64 works only under emulation. Everything else in the image —
ngspice itself, sky130, gf180mcu — is built natively for the build arch either
way.

> The first `make up-live` compiles ngspice from source and takes several
> minutes (much longer with `OSDI_MODE=compile`, which also builds a Rust/LLVM
> toolchain). It is cached afterwards, and `make up` never pays for it.

### Ordering

The `api` image `FROM`s the base **by tag**, and compose does not order a build
against an image tag — so the base must exist first. `make up-live` does the two
steps in order; by hand it is:

```bash
docker compose --profile live build spice-base
SPICE_BASE=spicexplorer-spice-base:release docker compose up --build api ui
```

A bare `docker compose --profile live up --build` races the two and can pick up a
stale (or missing) base.

### Or run natively

You can also get live SPICE outside Docker with a host ngspice + open PDK — see
[getting-started.md](getting-started.md#live-spice-optional).

## Rebuild / clean

```bash
docker compose build --no-cache api     # force a clean API rebuild
docker compose down -v                  # stop and drop volumes
```

> Heads-up: these images are for **local evaluation**, not a hardened production
> deployment. The UI image already runs as a non-root user (see
> `ui/Dockerfile.prod`); review resource limits, secrets, and TLS termination
> before exposing anything beyond localhost.
