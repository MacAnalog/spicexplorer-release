<!-- Managed by the private release infra (scripts/release/repo/) — edit there,
     not here; the next port overwrites this file. -->
# SpiceXplorer

[![lint](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/lint.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/lint.yml)
[![analog-db](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/analog-db.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/analog-db.yml)
[![platform](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/platform.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/platform.yml)
[![ui](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/ui.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/ui.yml)
[![docker](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/docker.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/docker.yml)

Open-source releases from the SpiceXplorer analog design-automation project,
developed by the MacAnalog research group at McMaster University. The whole
platform is public — every package, the Studio front-end, and the circuit
database — each published as a curated snapshot.

**Current release: v1.1.1.** It moves the reference circuits to upstream
pointers and refreshes the database (faster test tiers, publication-quality
schematics). v1.1 added the EDA base image, so `make up-live` gives
you a working simulator and three open PDKs with nothing installed on the host
(see [Live SPICE](#quickstart) below). v1.0 opened the platform: all ten
packages, the UI, and the database.

## Components

| Directory | What it is | Status |
|---|---|---|
| [`analog-db/`](analog-db/) | Analog circuit database — the topology/circuit registry (netlists, datasheets, class libraries, testbench templates) and its tiered verification harness | released |
| [`platform/`](platform/) | The Python workspace — kernel, leaf tools, optimizer and REST API (all ten packages below) | released |
| [`ui/`](ui/) | SpiceXplorer "Studio" — the Next.js front-end (HTTP/SSE) over the platform api | released |

### Platform packages

Dependencies flow **down** this table: the adapter builds on the optimizer, which
composes the leaf tools, which all rest on the kernel. Leaf tools never import each
other, so any one of them can be used on its own.

| Package | Layer | What it does |
|---|---|---|
| `spicexplorer-api` | adapter | FastAPI service over the optimizer and the library — thin, no business logic |
| `spicexplorer` | optimizer | The YAML design DSL, the scoring/optimization loop, and the simulation backends |
| `spicexplorer-circuitgraph` | leaf tool | Netlist → typed bipartite graph (nets ⟷ components), with round-trip and cross-PDK retargeting |
| `spicexplorer-netlist2xschem` | leaf tool | Netlist → xschem schematic, with headless SVG/PNG rendering |
| `spicexplorer-netlist2tf` | leaf tool | Netlist → exact symbolic transfer function, reduced to readable hand-form |
| `spicexplorer-gmid` | leaf tool | Deterministic gm/ID sizing from pre-computed lookup tables |
| `spicexplorer-waveview` | leaf tool | Universal result viewer — ngspice/Spectre artifacts → engine-neutral waveforms + plots |
| `spicexplorer-layout` | leaf tool | Parameterized layout generation (the generator contract + GDS build) |
| `spicexplorer-signoff` | leaf tool | Physical signoff — DRC / LVS / PEX runners with structured verdicts |
| `spicexplorer-core` | kernel | SPICE-engine wrappers, PVT corners, measurements, units, path anchoring |

Each component keeps its own `README.md`, `LICENSE`, and (for Python) `pyproject.toml`;
a `.release-provenance.json` in each records the snapshot it was cut from.

> **PDKs.** The database ships **open** PDK bindings only — IHP sg13g2, SkyWater
> sky130, and GlobalFoundries gf180mcu. The Spectre/commercial lane's machinery,
> templates and tests are here **kit-unbound**: no proprietary kit is bound, and
> no foundry-NDA-encumbered content — models, device or corner names, library
> identifiers, or data derived from a licensed kit — ships anywhere in this
> repository (CI enforces this: `nda-check`). You bind your own kit through the
> documented seam.

## Quickstart

Two ways to bring the app (API + Studio UI) up. **Full walkthroughs:**
[docs/getting-started.md](docs/getting-started.md) (native) and
[docs/docker.md](docs/docker.md) (Docker).

**Docker** — nothing to install but Docker:

```bash
make up            # build + run: API on :8000, Studio UI on :4000
# open http://localhost:4000        (make down to stop)

make up-live       # ...the same, but with live SPICE (see below)
```

**Native** — [uv](https://docs.astral.sh/uv/) (Python) + Node 22+, two terminals:

```bash
make sync          # build the platform venv and borrow the analog-db corpus
make api           # terminal 1 — backend  → http://localhost:8000
make ui            # terminal 2 — frontend → http://localhost:4000
```

`make help` lists every target. Prefer raw commands? See the getting-started guide —
each `make` target is a one-line wrapper you can run by hand.

> **Live SPICE is opt-in, and Docker makes it a one-liner.** `make up` and a bare
> `uv sync` carry no simulator, so the app starts in replay/cached mode
> (`GET /api/env` → `pdk_ok:false`) — the UI, the reference library, score
> shaping and compare/explore over cached checkpoints all work without one.
>
> **`make up-live`** builds the EDA base image
> ([`Dockerfile.spice-base`](Dockerfile.spice-base)) — **ngspice 45 compiled from
> source with OSDI, plus the IHP sg13g2, SkyWater sky130 and GF gf180mcu PDKs
> vendored** (all Apache-2.0) — and runs the stack on top of it. `pdk_ok:true`,
> with **nothing installed on the host**: no ngspice, no PDK download, no
> `PDK_ROOT`. It builds on both x86-64 and arm64 (Apple silicon) — the compact
> models are compiled from source there, which takes considerably longer the
> first time. See
> [docs/docker.md](docs/docker.md#live-spice-in-the-container).
>
> Prefer no containers? Install a local ngspice + an open PDK and run natively —
> see [docs/getting-started.md](docs/getting-started.md#live-spice-optional).

## Documentation

- [docs/getting-started.md](docs/getting-started.md) — install, run natively, run tests, enable live SPICE.
- [docs/docker.md](docs/docker.md) — the Docker stack, ports, environment, and its limits.
- Per-component detail: [`platform/README.md`](platform/README.md), [`ui/README.md`](ui/README.md), [`analog-db/README.md`](analog-db/README.md).

## Recommended tooling

- [uv](https://docs.astral.sh/uv/) for Python package management.
- Docker to run the containerized stack without a local Python/Node toolchain.
- Our forked schematic viewer for VS Code: [NooriDan/vscode-xschem-viewer-configurable](https://github.com/NooriDan/vscode-xschem-viewer-configurable).
