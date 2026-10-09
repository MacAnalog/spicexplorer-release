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
import re
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
    "CONTROLLED_PINS",
]

# Canonical pin orders (match circuitgraph's MOSFET / two-terminal pin enums and spicelib's node order).
MOS_PINS: tuple[str, ...] = ("DRAIN", "GATE", "SOURCE", "BULK")
TWO_TERMINAL_PINS: tuple[str, ...] = ("P", "N")
#: A voltage-controlled source (``E``/``G``) senses across a second node pair.
CONTROLLED_PINS: tuple[str, ...] = ("P", "N", "CP", "CN")


class DeviceKind(str, Enum):
    MOS = "mos"
    RES = "res"
    CAP = "cap"
    IND = "ind"
    VSOURCE = "vsource"
    ISOURCE = "isource"
    #: A behavioural (``B``) or controlled (``E``/``G``/``F``/``H``) source. One kind, because
    #: what they have in common -- an output branch plus an expression or a controlling quantity
    #: -- is what placement and wiring need; the reference letter still picks the symbol.
    BSOURCE = "bsource"
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
#: Behavioural + controlled sources. `B` carries an expression on two nodes; `E`/`G` sense a
#: second node pair; `F`/`H` name a controlling source instead, so they stay two-terminal.
#: Dropping these (the old "unrecognized device prefix" path) draws a sheet with the source
#: MISSING -- a drawing that netlists to a different circuit, silently.
_BSOURCE_PREFIXES = ("B",)
_VCONTROLLED_PREFIXES = ("E", "G")
_CCONTROLLED_PREFIXES = ("F", "H")

_TWO_TERMINAL = {
    _RES_PREFIXES: DeviceKind.RES,
    _CAP_PREFIXES: DeviceKind.CAP,
    _IND_PREFIXES: DeviceKind.IND,
    _VSOURCE_PREFIXES: DeviceKind.VSOURCE,
    _ISOURCE_PREFIXES: DeviceKind.ISOURCE,
}


#: The ``nch``/``pch`` MOSFET naming convention, as commercial kits spell it: ``nch``, ``nch_25``,
#: ``pmos_lvt``, ``pch_18``, and library-prefixed forms like ``kit_nch``.
#:
#: ANCHORED to a word start or an underscore on purpose. ``"nch" in model`` would be true of any
#: model whose name merely contains those letters (``bench_r``), and mistyping a device's polarity
#: is worse than not typing it: the drawing would show an NMOS where the netlist has something
#: else. Requiring a boundary on both sides keeps the rule specific.
_NCH_RE = re.compile(r"(?:^|_)nch(?:[_0-9]|$)")
_PCH_RE = re.compile(r"(?:^|_)pch(?:[_0-9]|$)")


def _mos_polarity(model: str | None) -> MosPolarity:
    """The polarity of a MOSFET model, read off its name.

    Polarity is what selects the symbol, so a model whose convention is not recognised here is
    undrawable — it resolves to no symbol and the device is dropped from the sheet. Two families of
    convention are recognised:

    * ``nmos``/``pmos`` (IHP, generic) and ``nfet``/``pfet`` (sky130 ``nfet_01v8``, gf180
      ``nfet_03v3``) — the open PDKs, which are drawn with their own vendored symbols;
    * ``nch``/``pch`` — the convention commercial kits use (``nch_25``, ``pmos_lvt``). These are
      drawn on the GENERIC lane (``mapping._GENERIC_MOS_SYMREF``), because an NDA kit's symbol
      library cannot be vendored here.
    """
    if model:
        lowered = model.lower()
        if "nmos" in lowered or "nfet" in lowered:
            return MosPolarity.NMOS
        if "pmos" in lowered or "pfet" in lowered:
            return MosPolarity.PMOS
        if _NCH_RE.search(lowered):
            return MosPolarity.NMOS
        if _PCH_RE.search(lowered):
            return MosPolarity.PMOS
    return MosPolarity.UNKNOWN


def _params(view: NetlistView, ref: str) -> dict[str, str | float]:
    # spicelib echoes the value/model token back as a 'Value' key — drop it (it lives in `model`).
    return {k: v for k, v in view.get_component_parameters(ref).items() if k != "Value"}


def _classify_supply(net: str) -> str | None:
    """Coarse rail classification by name (display/placement hint only; wiring is by-name)."""
    # `!` is Cadence's global-net marker (`vdd!`, `gnd!`) and carries no role information.
    n = net.strip().lower().strip("!")
    # The analog/digital-domain spellings are the ones a real mixed-signal deck uses, and their
    # absence meant a commercial-kit design's sheets were drawn with NO SUPPLY RAIL AT ALL: every
    # `avdd`/`agnd` net fell through to "not a supply", so the rail the reader looks for first was
    # simply not there (issue #159).
    if n in {"0", "gnd", "vgnd", "gnd_a", "vsubs", "agnd", "dgnd", "gnda", "gndd", "vsub"}:
        return "GND"
    if n.startswith(("vdd", "vcc", "vpwr", "vdda", "avdd", "dvdd", "avd", "vcca")):
        return "VDD"
    if n.startswith(("vss", "vee", "vssa", "vnw", "avss", "dvss")):
        return "VSS"
    return None


#: Value forms after which the next two tokens are NOT a controlling node pair.
_NOT_NODES = ("poly", "value", "vol", "cur", "table", "laplace", "freq", "pwl")


def _controlling_nodes(value: str) -> tuple[list[str], str]:
    """Split an ``E``/``G`` value into its controlling node pair and the remainder.

    The netlist parser reports only the OUTPUT branch of a controlled source as nodes; the
    controlling pair lives at the head of the value string (``E1 out 0 in 0 2`` -> nodes
    ``[out, 0]``, value ``"in 0 2"``). Recovering it is what lets the drawn symbol be wired to
    what it actually senses instead of floating.

    Returns ``([], value)`` unchanged for the keyword forms (``POLY``, ``VALUE=``, a Laplace or
    table expression), where the two tokens after the output branch are not nodes at all.
    """
    tok = value.split()
    if len(tok) < 3:
        return [], value
    if tok[0].lower().split("=")[0] in _NOT_NODES or "=" in tok[0] or "(" in tok[0]:
        return [], value
    return tok[:2], " ".join(tok[2:])


def _make_subckt(ref: str, view: NetlistView, nodes: list[str]) -> Device | None:
    """A generic ``X`` instance: formal port names when they line up, else positional pins."""
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


def _make_device(ref: str, view: NetlistView) -> Device | None:
    """Type ``ref`` by prefix and capture its pin→net map, or ``None`` if it can't be modeled.

    The prefix tests come FIRST and stay first — ``XM1`` is a MOSFET, not a subcircuit. But an
    ``X`` reference that fails its primitive's pin-count check falls through to :func:`_make_subckt`
    instead of being dropped: PDKs ship primitives as subcircuits with an extra node (IHP's
    ``XR1 a b sub rhigh`` poly resistor carries the substrate), and those used to be skipped with
    "3 nets but res expects 2" even though the branch below models them fine.

    A SUBCKT still needs a symbol to be *drawn*: :func:`~.mapping.symref_for` resolves subcircuit
    instances through ``_PDK_SUBCKT_SYMREF``, which covers the SG13G2 HBTs and the poly resistors
    (``rhigh``/``rppd``/``rsil``), so ``XR1 a b sub rhigh`` both ingests here and draws. Its third
    net becomes the symbol's ``body=`` attribute (see :func:`~.mapping.body_pin`; the ``.sym`` has
    two pins). A subcircuit with no entry in that table still ingests and is still skipped by the
    emitter with "no symbol mapping" — add the model there to draw it.
    """
    ref_u = ref.upper()
    nodes = view.get_component_nodes(ref)

    if ref_u.startswith(_MOS_PREFIXES):
        if len(nodes) != len(MOS_PINS):
            if ref_u.startswith("X"):
                logger.info(
                    "%s: %d nets, not a %d-pin MOSFET — ingesting as a subcircuit instance",
                    ref,
                    len(nodes),
                    len(MOS_PINS),
                )
                return _make_subckt(ref, view, nodes)
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

    if ref_u.startswith(_VCONTROLLED_PREFIXES + _CCONTROLLED_PREFIXES + _BSOURCE_PREFIXES):
        value = view.get_component_value(ref) or ""
        pins, nets = TWO_TERMINAL_PINS, list(nodes)
        if ref_u.startswith(_VCONTROLLED_PREFIXES):
            ctrl, value = _controlling_nodes(value)
            if ctrl:
                pins, nets = CONTROLLED_PINS, nodes + ctrl
        if len(nets) < len(pins):
            logger.warning(
                "skipping %s: %d nets but a %s source needs %d",
                ref,
                len(nets),
                ref_u[:1],
                len(pins),
            )
            return None
        return Device(
            ref=ref,
            kind=DeviceKind.BSOURCE,
            model=value or None,
            polarity=MosPolarity.UNKNOWN,
            pins=pins,
            nets=dict(zip(pins, nets)),
            params=_params(view, ref),
        )

    for prefixes, kind in _TWO_TERMINAL.items():
        if ref_u.startswith(prefixes):
            if len(nodes) != len(TWO_TERMINAL_PINS):
                if ref_u.startswith("X"):
                    logger.info(
                        "%s: %d nets, not a 2-pin %s — ingesting as a subcircuit instance",
                        ref,
                        len(nodes),
                        kind.value,
                    )
                    return _make_subckt(ref, view, nodes)
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
        return _make_subckt(ref, view, nodes)

    logger.warning("skipping %s: unrecognized device prefix", ref)
    return None


def ingest(view: NetlistView, *, name: str = "circuit", ports: tuple[str, ...] = ()) -> N2XCircuit:
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
