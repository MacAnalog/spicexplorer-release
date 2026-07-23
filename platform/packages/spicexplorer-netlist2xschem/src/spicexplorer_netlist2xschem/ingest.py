"""Netlist → internal device model, read leaf-legally over ``NetlistView``.

This mirrors ``spicexplorer-circuitgraph``'s ``device_factory`` dispatch (by reference-designator
prefix) but produces a tiny, layout-oriented model rather than a graph — we depend on
``spicexplorer-core`` only and never import a peer tool. The model is just enough to place + wire:
each :class:`Device` carries its canonical pin → net map, its MOS polarity, and its raw ``k=v`` params.

All accessors are single-level (they do not descend into subcircuits). To draw the devices *inside* a
subckt, pass ``into=<instance>`` to :func:`from_file` / :func:`from_string`, which steps into that
instance via ``NetlistView.get_subcircuit`` before ingesting.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from spicexplorer_core.spice_engine import NetlistView

logger = logging.getLogger(__name__)

__all__ = [
    "DeviceKind",
    "MosPolarity",
    "Device",
    "N2XCircuit",
    "ingest",
    "from_file",
    "from_string",
    "MOS_PINS",
    "TWO_TERMINAL_PINS",
]

# Canonical pin orders (match circuitgraph's MOSFET / two-terminal pin enums and spicelib's node order).
MOS_PINS: tuple[str, ...] = ("DRAIN", "GATE", "SOURCE", "BULK")
TWO_TERMINAL_PINS: tuple[str, ...] = ("P", "N")


class DeviceKind(str, Enum):
    MOS = "mos"
    RES = "res"
    CAP = "cap"
    IND = "ind"
    VSOURCE = "vsource"
    ISOURCE = "isource"
    SUBCKT = "subckt"


class MosPolarity(str, Enum):
    NMOS = "nmos"
    PMOS = "pmos"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Device:
    """A single device, layout-ready: pins in canonical order + the net each is wired to."""

    ref: str
    kind: DeviceKind
    model: str | None
    polarity: MosPolarity
    pins: tuple[str, ...]
    nets: Mapping[str, str]  # canonical pin name -> net name
    params: Mapping[str, str | float]


@dataclass(frozen=True)
class N2XCircuit:
    """A flat, single-level circuit: the devices to draw plus a net inventory + supply hints."""

    name: str
    devices: tuple[Device, ...]
    nets: tuple[str, ...]
    supply: Mapping[str, str]  # net name -> "VDD" | "VSS" | "GND"
    ports: tuple[str, ...] = ()  # declared external ports (a descended subckt's formal-header nets)


_MOS_PREFIXES = ("M", "XM")
_RES_PREFIXES = ("R", "XR")
_CAP_PREFIXES = ("C", "XC")
_IND_PREFIXES = ("L", "XL")
_VSOURCE_PREFIXES = ("V",)
_ISOURCE_PREFIXES = ("I",)

_TWO_TERMINAL = {
    _RES_PREFIXES: DeviceKind.RES,
    _CAP_PREFIXES: DeviceKind.CAP,
    _IND_PREFIXES: DeviceKind.IND,
    _VSOURCE_PREFIXES: DeviceKind.VSOURCE,
    _ISOURCE_PREFIXES: DeviceKind.ISOURCE,
}


def _mos_polarity(model: str | None) -> MosPolarity:
    # Match the common device-model naming conventions across PDKs: ``nmos``/``pmos`` (IHP, generic)
    # and ``nfet``/``pfet`` (sky130 ``nfet_01v8``, gf180 ``nfet_03v3``, …).
    if model:
        lowered = model.lower()
        if "nmos" in lowered or "nfet" in lowered:
            return MosPolarity.NMOS
        if "pmos" in lowered or "pfet" in lowered:
            return MosPolarity.PMOS
    return MosPolarity.UNKNOWN


def _params(view: NetlistView, ref: str) -> dict[str, str | float]:
    # spicelib echoes the value/model token back as a 'Value' key — drop it (it lives in `model`).
    return {k: v for k, v in view.get_component_parameters(ref).items() if k != "Value"}


def _classify_supply(net: str) -> str | None:
    """Coarse rail classification by name (display/placement hint only; wiring is by-name)."""
    n = net.strip().lower().strip("!")
    if n in {"0", "gnd", "vgnd", "gnd_a", "vsubs"}:
        return "GND"
    if n.startswith(("vdd", "vcc", "vpwr", "vdda")):
        return "VDD"
    if n.startswith(("vss", "vee", "vssa", "vnw")):
        return "VSS"
    return None


def _make_device(ref: str, view: NetlistView) -> Device | None:
    """Type ``ref`` by prefix and capture its pin→net map, or ``None`` if it can't be modeled."""
    ref_u = ref.upper()
    nodes = view.get_component_nodes(ref)

    if ref_u.startswith(_MOS_PREFIXES):
        if len(nodes) != len(MOS_PINS):
            logger.warning(
                "skipping %s: %d nets but MOSFET expects %d", ref, len(nodes), len(MOS_PINS)
            )
            return None
        model = view.get_component_value(ref)
        return Device(
            ref=ref,
            kind=DeviceKind.MOS,
            model=model,
            polarity=_mos_polarity(model),
            pins=MOS_PINS,
            nets=dict(zip(MOS_PINS, nodes)),
            params=_params(view, ref),
        )

    for prefixes, kind in _TWO_TERMINAL.items():
        if ref_u.startswith(prefixes):
            if len(nodes) != len(TWO_TERMINAL_PINS):
                logger.warning("skipping %s: %d nets but %s expects 2", ref, len(nodes), kind.value)
                return None
            return Device(
                ref=ref,
                kind=kind,
                model=view.get_component_value(ref),
                polarity=MosPolarity.UNKNOWN,
                pins=TWO_TERMINAL_PINS,
                nets=dict(zip(TWO_TERMINAL_PINS, nodes)),
                params=_params(view, ref),
            )

    if ref_u.startswith("X"):
        if not nodes:
            logger.warning("skipping %s: subckt instance has no connected nets", ref)
            return None
        formal = view.get_subcircuit_ports(ref)
        if formal and len(formal) == len(nodes) and len(set(formal)) == len(formal):
            names = tuple(formal)
        else:
            names = tuple(str(i) for i in range(1, len(nodes) + 1))
        return Device(
            ref=ref,
            kind=DeviceKind.SUBCKT,
            model=view.get_component_value(ref),
            polarity=MosPolarity.UNKNOWN,
            pins=names,
            nets=dict(zip(names, nodes)),
            params=_params(view, ref),
        )

    logger.warning("skipping %s: unrecognized device prefix", ref)
    return None


def ingest(
    view: NetlistView, *, name: str = "circuit", ports: tuple[str, ...] = ()
) -> N2XCircuit:
    """Build an :class:`N2XCircuit` from the devices at ``view``'s current level.

    ``ports`` are the declared external port nets (a descended subckt's formal-header names), kept
    only where they actually appear on a device so they can be drawn as port pins.
    """
    devices = [
        d for d in (_make_device(ref, view) for ref in view.get_components()) if d is not None
    ]
    nets = sorted({net for d in devices for net in d.nets.values()})
    supply = {n: role for n in nets if (role := _classify_supply(n)) is not None}
    netset = set(nets)
    return N2XCircuit(
        name=name,
        devices=tuple(devices),
        nets=tuple(nets),
        supply=supply,
        ports=tuple(p for p in ports if p in netset),
    )


def _formal_ports(view: NetlistView, into: str | None) -> tuple[str, ...]:
    """Formal ``.subckt``-header port nets for the instance we descended into (``()`` if unknown)."""
    if not into:
        return ()
    try:
        return tuple(view.get_subcircuit_ports(into) or ())
    except Exception:  # pragma: no cover - defensive; missing/unresolved definition
        return ()


def from_file(path: str | Path, *, name: str | None = None, into: str | None = None) -> N2XCircuit:
    """Parse a netlist file and ingest it. ``into`` steps into a subckt *instance* first."""
    view = NetlistView.from_file(path)
    ports = _formal_ports(view, into)
    if into:
        view = view.get_subcircuit(into)
    return ingest(view, name=name or into or Path(str(path)).stem, ports=ports)


def _ensure_title(text: str) -> str:
    """SPICE treats the first line as an ignored title; spicelib requires it. Prepend a title when a
    pasted netlist starts straight with a device/dot card, so title-less input still parses."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        return text if stripped.startswith("*") else f"* netlist2xschem\n{text}"
    return f"* netlist2xschem\n{text}"


def from_string(text: str, *, name: str = "circuit", into: str | None = None) -> N2XCircuit:
    """Parse raw SPICE text and ingest it. ``into`` steps into a subckt *instance* first.

    A missing SPICE title line is tolerated (a placeholder title is prepended), so a pasted netlist
    that begins directly with a device card still parses.
    """
    view = NetlistView.from_string(_ensure_title(text))
    ports = _formal_ports(view, into)
    if into:
        view = view.get_subcircuit(into)
    return ingest(view, name=name, ports=ports)
