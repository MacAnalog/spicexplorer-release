<!-- Managed by the private release infra (scripts/release/repo/) — edit there,
     not here; the next port overwrites this file. -->
# SpiceXplorer

[![lint](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/lint.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/lint.yml)
[![analog-db](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/analog-db.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/analog-db.yml)
[![platform](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/platform.yml/badge.svg)](https://github.com/MacAnalog/spicexplorer-release/actions/workflows/platform.yml)

Open-source releases from the SpiceXplorer analog design-automation project,
developed by the MacAnalog research group at McMaster University. The project
is published incrementally; this monorepo grows one component at a time, each
as a curated snapshot.

## Components

| Directory | What it is | Status |
|---|---|---|
| [`analog-db/`](analog-db/) | Analog circuit database — the topology/circuit registry (netlists, datasheets, class libraries, testbench templates) and its tiered verification harness | first release |
| [`platform/`](platform/) | SpiceXplorer platform packages: `spicexplorer-core` (foundation), `spicexplorer-circuitgraph` + `spicexplorer-netlist2xschem` (netlist tools), `spicexplorer` (optimization) | coming soon |

Each component keeps its own `README.md`, `LICENSE`, and `pyproject.toml`; a
`.release-provenance.json` in each records the snapshot it was cut from.

## Reproducibility

The `analog-db` test tier in CI runs the dependency-light checks today and
activates the full fast test suite automatically once the platform packages
join the monorepo.

## Recommended Installs

- [uv](https://docs.astral.sh/uv/) for package management.
- Docker for running the containerized environment without having to worry about installing open-source PDKs.
- Our forked schematic viewer for VS Code: [NooriDan/vscode-xschem-viewer-configurable](https://github.com/NooriDan/vscode-xschem-viewer-configurable).
