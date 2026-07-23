"""SpiceXplorer shared kernel (``spicexplorer_core``).

The bottom layer of the workspace: low-level primitives that every package and
adapter (``spicexplorer``, ``spicexplorer_api``, …) depends on, with no upward
dependencies of its own. It carries:

- :mod:`~spicexplorer_core.paths` — the workspace-root anchor
  (:func:`project_root`), replacing the monolith's depth-sensitive parent walks;
- :mod:`~spicexplorer_core.spice_engine` — the NGSpice/LTspice + spicelib
  wrappers (``NGSpice_Wrapper``, ``NetlistView``, …);
- :mod:`~spicexplorer_core.eng` — engineering-string parsing (``parse_value``:
  ``"0.18u"`` → ``1.8e-7``);
- :mod:`~spicexplorer_core.pvt` — PVT primitives (``Corner``, ``PVTConfig``);
- :mod:`~spicexplorer_core.env` — runtime environment detection (``probe_env``:
  ngspice + PDK availability);
- :mod:`~spicexplorer_core.logging` — logger setup (``setup_loggers``).

Only the cheap, dependency-free root anchor is re-exported here for convenience;
import the heavier primitives from their submodules (e.g.
``from spicexplorer_core.pvt import Corner``) so this package stays light to
import.
"""

from spicexplorer_core.paths import ROOT_ENV_VAR, clear_cache, project_root

__all__ = ["project_root", "clear_cache", "ROOT_ENV_VAR"]
