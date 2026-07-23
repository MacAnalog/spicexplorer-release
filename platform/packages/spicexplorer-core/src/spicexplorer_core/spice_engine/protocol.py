"""The `Simulator` seam — `Simulator` / `SimResult` / `SimHandle` Protocols.

A Cadence-free structural seam over the existing `NGSpice_Wrapper` god-object that the
platform's standing refactor already wants. It captures *exactly* what the optimizer
already calls plus the symmetric async submit/handle path — nothing more.

Design rules (why this file is deliberately tiny and dependency-free):

* These are **`Protocol`s, not ABCs** — backends satisfy them *structurally*, so
  `NGSpice_Wrapper` (and, later, the optional Spectre adapter) need not inherit from
  anything here. `NGSpice_Wrapper` gains only two thin methods (`run` / `submit`)
  that wrap its existing `run_and_wait` / `run_and_pass`; there is **zero behaviour
  change** to any existing method.
* Backends may add extra *optional* parameters (e.g. ngspice's `run(exe_log=..., label=...)`);
  a Protocol call site only ever uses the required surface below, so this stays
  structurally compatible while the concrete wrappers keep their richer signatures.
* `core` imports **no** Cadence / bridge code. The Spectre adapter lives in an
  optional, lazily-imported package and is *never* imported from here (blast-radius rule).

The result surface is intentionally two methods:

* `scalar(name, analysis)` — one named number from an analysis (`M0:gm`, `v(out)@op`,
  a THD figure). This is what the scorer ultimately consumes.
* `wave(name, analysis)` — a full trace as a numpy array (complex for AC). The
  engine-neutral measurement library runs over these.

`analysis` is a plain string so it is engine-neutral: the ngspice `SimResult`
resolves it to an `Ngspice_Plot_Type`; the Spectre `SimResult` resolves it to a
`{"ac": "ac_", ...}` PSF-key prefix. Callers speak one vocabulary
(`"op"`/`"ac"`/`"dc"`/`"tran"`/`"noise"`), each backend maps it to its own plots.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

import numpy as np

if TYPE_CHECKING:
    # Type-checking only: keep this module import-cheap and free of any runtime
    # dependency on the PVT package. `Corner` lives in `spicexplorer_core.pvt`.
    from spicexplorer_core.pvt import Corner


@runtime_checkable
class SimResult(Protocol):
    """The read-back surface of one completed simulation.

    A backend's result object exposes named scalars and named waveforms keyed by an
    engine-neutral `analysis` string. Missing scalars degrade to NaN (mirroring
    `NGSpice_Wrapper.extract_scalar_variable_from_raw`) so a single absent metric can
    never crash the optimizer; missing waveforms raise (a wave is a hard request).
    """

    def scalar(self, name: str, analysis: str) -> float: ...

    def wave(self, name: str, analysis: str) -> np.ndarray: ...


@runtime_checkable
class SimHandle(Protocol):
    """A handle to an in-flight (non-blocking) simulation.

    Satisfied for free by both backends: spicelib's `RunTask`
    (`is_alive()` / `get_results()`) and `concurrent.futures.Future`
    (`done()` / `result()`) each wrap to this two-method surface.
    """

    def is_done(self) -> bool: ...

    def result(self) -> SimResult: ...


@runtime_checkable
class Simulator(Protocol):
    """A simulation backend the optimizer can drive without knowing which engine it is.

    The four methods are exactly the optimizer's current call surface (`update_params`,
    `apply_corner`) plus the run/submit pair that unifies ngspice's
    `run_and_wait` / `run_and_pass` with the bridge's `run_simulation` / `submit`.

    `update_params` / `apply_corner` take their first argument **positional-only** (the `/`)
    so a backend is free to name it whatever reads best in its own code — `NGSpice_Wrapper`
    already calls it `parameterization` — and still satisfy the protocol structurally under
    a static checker (which otherwise requires matching parameter names).

    `label`, when given, names this run's artifacts (ngspice: the `run_<n>_<label>`
    folder) — the optimizer passes `"<tb>__<corner>"` so one trial's per-corner runs
    never collide. `model_lib_root` is the root against which a corner's relative
    `lib_file` includes are resolved. Both are keyword-only so backends stay free to
    keep richer positional signatures.

    Two *optional* (non-protocol, duck-typed) extensions the optimizer uses when a
    backend offers them:

    * `SimResult.log_path` — where this run's simulator log landed (`None`/absent when
      the engine has no local log). Read via `getattr(result, "log_path", None)`.
    * `Simulator.collect(handle) -> SimResult` — read a submitted run's outputs back
      through the backend's own state (ngspice: `read_and_save_task_outputs`, which
      also refreshes `curr_raw`/`curr_log` for legacy readers). Callers fall back to
      `handle.result()` when absent.
    """

    def update_params(self, params: dict[str, float], /) -> bool: ...

    def apply_corner(self, corner: Corner, /, *, model_lib_root: str | None = None) -> None: ...

    def run(self, *, label: str | None = None) -> SimResult: ...  # blocking   (ngspice run_and_wait / Spectre run_simulation)

    def submit(self, *, label: str | None = None) -> SimHandle: ...  # non-blocking (ngspice run_and_pass / Spectre submit)


__all__ = ["SimResult", "SimHandle", "Simulator"]
