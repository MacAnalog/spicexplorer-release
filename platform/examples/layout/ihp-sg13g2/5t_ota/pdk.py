"""Shared IHP sg13g2 PyCell bootstrap + layer constants.

The foundry PyCells (``sg13g2_pycell_lib``) use ``from __future__ import annotations``,
which the KLayout GUI's *embedded* CPython 3.6 rejects — but they import and instantiate
cleanly under an external Python 3.11 that has the pip ``klayout`` module. We therefore
drive layout generation from Python, not from inside KLayout.

Set ``PDK_ROOT`` (default ``~/local/pdks``) so ``$PDK_ROOT/ihp-sg13g2`` resolves.
"""
from __future__ import annotations

import os
import sys
from types import ModuleType

PDK_ROOT: str = os.environ.get("PDK_ROOT", os.path.expanduser("~/local/pdks"))
PDK: str = os.path.join(PDK_ROOT, "ihp-sg13g2")
KL: str = os.path.join(PDK, "libs.tech/klayout")

# GDS (layer, datatype) tuples used by the generator.
L_ACTIV, L_POLY, L_CONT = (1, 0), (5, 0), (6, 0)
L_M1, L_VIA1, L_M2 = (8, 0), (19, 0), (10, 0)
L_NWELL, L_PSD, L_TEXT = (31, 0), (14, 0), (63, 0)
L_M1_TXT, L_M2_TXT = (8, 25), (10, 25)  # net-label layers the IHP LVS reads


def bootstrap() -> ModuleType:
    """Put the IHP PyCell libraries on ``sys.path`` and register ``SG13_dev``.

    Returns the ``pya`` module. Raises a clear error if the PDK / klayout module
    is missing.
    """
    os.environ.setdefault("PYTHONPYCACHEPREFIX", "/tmp/pyc_ihp")
    if not os.path.isdir(KL):
        raise FileNotFoundError(
            f"IHP klayout tech not found at {KL}. Set PDK_ROOT to the dir containing ihp-sg13g2."
        )
    api = os.path.join(KL, "python/pycell4klayout-api/source/python")
    for p in (os.path.join(KL, "python"), api):
        if p not in sys.path:
            sys.path.insert(0, p)
    # ihp-gdsfactory (>=0.2.7) vendors an incompatible copy of `cni` into
    # site-packages as a REGULAR package (has __init__.py); the PDK's
    # pycell4klayout-api `cni` is a NAMESPACE package, and regular packages win
    # regardless of sys.path order. Its `cni.dlo` lacks `List` and breaks the
    # sg13g2_pycell_lib import — so bind `cni` to the PDK's directory explicitly.
    import importlib.util
    spec = importlib.util.find_spec("cni")
    if spec is not None and spec.origin and api not in spec.origin:
        import types
        pkg = types.ModuleType("cni")
        pkg.__path__ = [os.path.join(api, "cni")]  # namespace-style submodule search
        sys.modules["cni"] = pkg
    try:
        import pya  # noqa: F401  (pip `klayout` module)
    except ImportError as e:
        raise ImportError("The pip `klayout` module is required (pip install klayout).") from e
    import sg13g2_pycell_lib  # noqa: F401  — registers the SG13_dev library
    import pya
    if pya.Library.library_by_name("SG13_dev") is None:
        raise RuntimeError("SG13_dev library did not register — check the PyCell import.")
    return pya
