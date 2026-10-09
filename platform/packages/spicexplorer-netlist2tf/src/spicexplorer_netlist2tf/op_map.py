"""A simulator operating point → the symbols netlist2tf mints (``operating_point=`` / ``subs=``).

To check a hand-form at a design's bias, ``transfer_function(..., operating_point=...)`` (or
``build_system(..., subs=...)``) needs a value for every symbol the small-signal model minted:
``gm_m1``, ``ro_m1`` … and, for a device flattened out of a subckt instance, a name that carries
the instance (``XM1`` in ``xota`` mints ``gm_m1_xota``: the ``X`` of a wrapped device is
dropped). :func:`operating_point_from` fills those names from what a simulator reports — read
from the model's own symbol table, never rebuilt from the ref — so no design writes that mapping
by hand:

* an ngspice ``.op`` result keyed by device-parameter vectors, ``@m1[gm]``,
  ``@m.xota.m1[gds]``, or ``@n.xota.xm1.nsg13_lv_nmos[gm]`` for a PDK device wrapped in a subckt
  (the OSDI/PSP layout);
* a Spectre oppoint dict from :func:`spicexplorer_core.spice_engine.psfascii.read_oppoint_info`,
  keyed ``<instance path>:<param>`` (``xota.xm1:gm``, or ``xota.xm1.m0:gm`` through a wrapper).

Keys are matched case-insensitively. Any other key (a node voltage, a ``.meas`` result) is
ignored. Nothing is defaulted: a symbol with no value in the result is returned in ``unmapped``.

Checked against a live simulator: ngspice with the IHP PSP devices (the OD-8 acceptance). The
Spectre side is checked for its key shape only; a Spectre model that names a parameter
differently from the table below (its junction caps, say) leaves that role in ``unmapped``.

The device mapping (the hybrid-pi of :func:`.models.expand_mosfet`):

====== ==================================== ===========================================
symbol from the simulator                    note
====== ==================================== ===========================================
gm     ``gm``
ro     ``1/gds``                            a non-positive ``gds`` is left unmapped
gmb    ``gmb``, else ``gmbs``
cgs    ``cgs`` + ``cgsol`` (when reported)  PSP's ``cgs`` excludes the overlap
cgd    ``cgd`` + ``cgdol`` (when reported)  PSP's ``cgd`` excludes the overlap
cdb    ``cjd``, else ``capbd``              junction cap, never PSP's ``cdb``
csb    ``cjs``, else ``capbs``              junction cap, never PSP's ``csb``
====== ==================================== ===========================================

PSP's intrinsic ``cdb``/``csb`` are trans-capacitances (∂Q/∂Vb of the drain/source charge), not
drain-bulk/source-bulk branches: stamping them in place of the junctions over-counted the output
node of the IHP 5T OTA and moved its predicted −3 dB point 7.4 % low (0.3 % with this mapping,
the OD-8 acceptance in ``tests/test_n2tf_slow_sim.py``).
"""

from __future__ import annotations

import logging
import math
import re
from collections.abc import Mapping

import sympy as sp

from .model.ir import Circuit2TF, Fidelity
from .model.ssir import SmallSignalIR
from .models import small_signal_model

logger = logging.getLogger(__name__)

__all__ = ["operating_point_from"]

_NGSPICE_KEY = re.compile(r"^@(?P<path>[^\[\]]+)\[(?P<param>[^\[\]]+)\]$")
_SPECTRE_KEY = re.compile(r"^(?P<path>[^:@\s]+):(?P<param>[^:\s]+)$")


def _flat_names(tokens: list[str]) -> list[str]:
    """netlist2tf's flattened ref for an instance path, outer → inner (``[xota, xm1]`` →
    ``xm1_xota``), then the same without the last level: a PDK device is a subckt wrapper whose
    one inner device the simulator names (``[xota, xm1, nsg13_lv_nmos]`` → ``xm1_xota``)."""
    names = ["_".join(reversed(tokens))]
    if len(tokens) > 1:
        names.append("_".join(reversed(tokens[:-1])))
    return names


def _parse_key(key: str) -> tuple[list[str], str] | None:
    """``(candidate flat refs, parameter)`` for an ngspice or Spectre device key, else ``None``."""
    k = key.strip().lower()
    m = _NGSPICE_KEY.match(k)
    if m:
        tokens = m["path"].split(".")
        # ngspice spells a device inside a subckt with its type letter first: m.xota.m1
        if len(tokens) > 1 and len(tokens[0]) == 1:
            tokens = tokens[1:]
        return _flat_names(tokens), m["param"]
    m = _SPECTRE_KEY.match(k)
    if m:
        return _flat_names(m["path"].split(".")), m["param"]
    return None


def _number(raw: object) -> float | None:
    try:
        v = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _device_ops(result: Mapping[str, object], refs: set[str]) -> dict[str, dict[str, float]]:
    """``{ref (lower-case): {param: value}}`` for every device of ``refs`` the result reports.

    The exact flattened name wins over the wrapper-stripped one, so a key never lands on the
    wrapper when the path names the device itself."""
    exact: dict[str, dict[str, float]] = {}
    wrapped: dict[str, dict[str, float]] = {}
    for key, raw in result.items():
        parsed = _parse_key(str(key))
        value = _number(raw)
        if parsed is None or value is None:
            continue
        names, param = parsed
        for i, name in enumerate(names):
            if name in refs:
                (exact if i == 0 else wrapped).setdefault(name, {}).setdefault(param, value)
                break
    out = dict(wrapped)
    for name, params in exact.items():
        out[name] = {**out.get(name, {}), **params}
    return out


def _first(op: dict[str, float], *names: str) -> float | None:
    for n in names:
        if n in op:
            return op[n]
    return None


def _role_value(role: str, op: dict[str, float]) -> float | None:
    """One hybrid-pi role's value from a device's reported parameters, or ``None``."""
    if role == "gm":
        return _first(op, "gm")
    if role == "ro":
        gds = _first(op, "gds")
        return 1.0 / gds if gds is not None and gds > 0.0 else None
    if role == "gmb":
        return _first(op, "gmb", "gmbs")
    if role in ("cgs", "cgd"):
        base = _first(op, role)
        return None if base is None else base + op.get(f"{role}ol", 0.0)
    if role == "cdb":
        return _first(op, "cjd", "capbd")
    if role == "csb":
        return _first(op, "cjs", "capbs")
    return None


def _ssir_symbols(ssir: SmallSignalIR) -> set[str]:
    """Every symbol the primitives leave free (what ``build_system`` would keep symbolic)."""
    names: set[str] = set()
    for p in ssir.primitives:
        v = getattr(p, "value", None)
        if isinstance(v, sp.Expr):
            names.update(str(x) for x in v.free_symbols)
    return names


def operating_point_from(
    result: Mapping[str, object],
    circuit: Circuit2TF | SmallSignalIR,
    *,
    level: Fidelity = Fidelity.FULL,
    params: bool = True,
) -> tuple[dict[str, float], list[str]]:
    """Map a simulator's operating point onto netlist2tf's symbol names.

    ``result`` is an ngspice ``.op`` result (``{"@m.xota.m1[gm]": 1.2e-4, …}``) or a Spectre
    oppoint dict (``read_oppoint_info``: ``{"xota.xm1:gm": 1.2e-4, …}``). ``circuit`` is the
    ingested :class:`Circuit2TF`, modelled here at ``level`` (default ``FULL``, which mints every
    role the table in the module docstring fills), or a :class:`SmallSignalIR` you already built —
    pass that one when the result is for the model you will solve, so the names are the same
    objects' names.

    ``params`` (default on) also fills a symbol that is a numeric global ``.param`` of the deck
    (``CL`` in ``C1 out 0 {CL}`` with ``.param CL=1p``): the value the simulator ran with.

    Returns ``(values, unmapped)``: ``values`` maps every symbol name it could fill to a float,
    and ``unmapped`` lists, sorted, every free symbol of the model it could not. Nothing is
    defaulted — check ``unmapped`` (or pass ``values`` to ``subs=`` and let what is left stay
    symbolic).
    """
    ssir = (
        circuit if isinstance(circuit, SmallSignalIR) else small_signal_model(circuit, level=level)
    )
    targets = _ssir_symbols(ssir)
    values: dict[str, float] = {}

    ops = _device_ops(result, {ref.lower() for ref in ssir.symbols})
    for ref, syms in ssir.symbols.items():
        op = ops.get(ref.lower())
        if op is None:
            continue
        for role, sym in syms.items():
            v = _role_value(role, op)
            if v is not None:
                values[str(sym)] = v
            elif role == "ro" and "gds" in op:
                logger.warning(
                    "operating_point_from: %s has gds=%g; ro left unmapped", ref, op["gds"]
                )

    if params:
        for name, expr in ssir.params.items():
            if name in targets and name not in values and expr.is_number:
                v = _number(expr)
                if v is not None:
                    values[name] = v

    unmapped = sorted(targets - set(values))
    return values, unmapped
