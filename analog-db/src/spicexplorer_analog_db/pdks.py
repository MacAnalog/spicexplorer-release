"""PDK resolution for lowering (plan D-1/D-2, Phase 1).

A circuit's ``pdk/<pdk>/devices.map.yaml`` is the per-topology override of circuitgraph's
built-in device table: it maps generic kinds (``nmos``/``pmos``/``res``/``cap``) to the PDK's
device names. ``load_pdk`` builds a circuitgraph ``Pdk`` from that map (so ``to_netlist(pdk=…)``
retargets correctly), falling back to the built-in (``get_pdk``) when no map is present.

The ``_shared/pdk/<pdk>.yaml`` registry carries PDK-level metadata (corner-lib catalog,
device-class map, nominal supply/geometry) consumed by analyses + sizing.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml
from spicexplorer_circuitgraph import Pdk, PdkDevice, get_pdk
from spicexplorer_circuitgraph.model.nodes import DeviceType, MosPolarityType

from . import paths
from .model import Circuit

# generic kind token -> (circuitgraph DeviceType, MOS polarity)
_KIND = {
    "nmos": (DeviceType.MOS, MosPolarityType.NMOS),
    "pmos": (DeviceType.MOS, MosPolarityType.PMOS),
    "res": (DeviceType.RES, MosPolarityType.UNKNOWN),
    "cap": (DeviceType.CAP, MosPolarityType.UNKNOWN),
    "ind": (DeviceType.IND, MosPolarityType.UNKNOWN),
}


def _split_kind(kind: str) -> tuple[str, str]:
    """A devices.map kind key -> (base kind, flavor). MOS keys may carry a threshold/voltage-class
    flavor as a suffix (``nmos_hv`` -> ``("nmos", "hv")``); everything else is flavorless
    (``nmos`` -> ``("nmos", "")``, ``res`` -> ``("res", "")``). The flavor lets ONE DUT bind two
    NMOS (or two PMOS) flavors — the abstract netlist uses the matching ``nmos``/``nmos_hv`` tokens,
    and circuitgraph's flavor-aware ``model_for`` retargets each instance to its own model."""
    for pol in ("nmos", "pmos"):
        if kind.startswith(pol + "_"):
            return pol, kind[len(pol) + 1 :]
    return kind, ""


def load_pdk(circuit: Circuit, pdk_name: str) -> Pdk:
    """The circuitgraph ``Pdk`` for lowering this circuit to ``pdk_name``.

    Per-topology ``devices.map.yaml`` wins; else the circuitgraph built-in. Raises if neither
    resolves (so an unknown PDK fails loudly rather than emitting un-retargeted models).
    """
    mp = circuit.dir / "pdk" / pdk_name / "devices.map.yaml"
    if mp.is_file():
        with mp.open() as fh:
            data = yaml.safe_load(fh) or {}
        devices: list[PdkDevice] = []
        for kind, spec in (data.get("devices") or {}).items():
            base, flavor = _split_kind(kind)
            if base not in _KIND:
                raise ValueError(f"{mp}: unknown device kind {kind!r} (known: {sorted(_KIND)})")
            model = spec["model"] if isinstance(spec, dict) else spec
            dt, pol = _KIND[base]
            devices.append(PdkDevice(model, dt, pol, flavor=flavor))
        if devices:
            # Inherit the built-in PDK's finger convention (per-finger width / `nf` for sky130) so a
            # devices.map override still lowers fingers correctly; default (IHP `ng`) otherwise.
            builtin = get_pdk(pdk_name)
            finger_param = builtin.finger_param if builtin else "ng"
            width_per_finger = builtin.width_per_finger if builtin else False
            return Pdk(
                name=pdk_name,
                devices=tuple(devices),
                finger_param=finger_param,
                width_per_finger=width_per_finger,
            )
    builtin = get_pdk(pdk_name)
    if builtin is None:
        raise ValueError(
            f"PDK {pdk_name!r}: no pdk/{pdk_name}/devices.map.yaml and no circuitgraph built-in"
        )
    return builtin


@lru_cache(maxsize=None)
def registry_ids() -> tuple[str, ...]:
    root = paths.shared_root() / "pdk"
    if not root.is_dir():
        return ()
    return tuple(sorted(p.stem for p in root.glob("*.yaml")))


def load_registry(pdk_name: str) -> dict[str, Any]:
    """The ``_shared/pdk/<pdk>.yaml`` PDK-level metadata."""
    path = paths.shared_root() / "pdk" / f"{pdk_name}.yaml"
    with path.open() as fh:
        return yaml.safe_load(fh) or {}
