"""Optional, lazily-imported simulation backends behind the `Simulator` protocol.

Everything here is opt-in: importing `spicexplorer.backends` (or the `spectre` module)
pulls in **no** Cadence / virtuoso-bridge dependency. The bridge is imported lazily,
only when a Spectre simulator is actually constructed (see
`spicexplorer.backends.spectre.create_spectre_simulator`), so ngspice-only users — and
`spicexplorer-core`, and the open-PDK Docker lane — never touch it.
"""
