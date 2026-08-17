"""The one internal IR (Stage-1 target).

A **typed, ordered, linearizable small-signal netlist** — one dataclass tree every front-end maps
onto and the MNA builder (P3) consumes directly. It sits *below* device physics (it does not know
"this is an OTA") and *above* SPICE syntax (it does not know ``+`` continuations or ``0.18u``).

This IR is **netlist2tf-private**: it is deliberately NOT circuitgraph's ``CircuitGraph`` (the peer
wall — ``doc/plan_netlist2tf.md`` §1). Duplicated *typing* across the two leaf tools is allowed;
*parsing* lives once in ``spicexplorer-core``.

Design properties (plan §4):

* **Ordered + value-typed → byte-identical IR.** Devices are an ordered tuple; ``Net``/``Terminal``/
  ``PortPair`` are frozen value types. The same netlist yields the same IR, so the eventual TF is
  reproducible.
* **Everything sympified at ingestion.** Param strings become sympy ``Expr`` once (numeric values →
  ``Float``/``Rational``; symbolic references → ``Symbol``); :attr:`Circuit2TF.symbolic` records the
  keep-symbolic-vs-numericize decision per symbol name.
* **DC-source short / AC-grounding is an IR fact, but overridable per analysis.** A net's
  :class:`NetRole` is decided once at ingestion (``SUPPLY_DC`` and ``GROUND`` are both AC grounds);
  a later analysis (PSRR, common-mode) re-promotes a supply to a signal input via a *stimulus
  overlay* (P7+) rather than mutating this frozen fact.
* **Differential is anticipated, not yet engaged.** ``Device.match_group`` + the ``_P``/``_N`` net
  pairing are carried from ingestion so the opt-in DM/CM transform (post-R1) needs no re-detection,
  even though R1 ships single-ended + node-pair difference only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import sympy as sp

__all__ = [
    "NetRole",
    "DeviceKind",
    "PinRole",
    "Fidelity",
    "Net",
    "Terminal",
    "PortPair",
    "Device",
    "Circuit2TF",
    "GROUND_NAMES",
]

#: Canonical net names treated as the small-signal/AC ground regardless of role inference.
GROUND_NAMES: frozenset[str] = frozenset({"0", "gnd", "gnd!", "vgnd", "vground"})


# ------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------
class NetRole(str, Enum):
    """Small-signal role of a net. ``GROUND`` and ``SUPPLY_DC`` are both **AC grounds**."""

    GROUND = "ground"  # the reference node (0/gnd) — always 0 V small-signal
    SUPPLY_DC = "supply_dc"  # driven by a pure-DC source → a 0-Ω AC short to ground
    SIGNAL = "signal"  # everything else (inputs, outputs, internal nodes)


class DeviceKind(str, Enum):
    """Device family. The small-signal model registry (P2) keys its expansion on this."""

    NMOS = "nmos"
    PMOS = "pmos"
    MOS = "mos"  # MOSFET of not-yet-resolved polarity
    BJT_NPN = "bjt_npn"
    BJT_PNP = "bjt_pnp"
    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    VSOURCE = "vsource"
    ISOURCE = "isource"
    DIODE = "diode"
    SUBCKT = "subckt"  # an unresolved/opaque X… instance (no registered model)
    UNKNOWN = "unknown"


class PinRole(str, Enum):
    """Terminal role within a device. MOSFET → D/G/S/B; two-terminal → P/N; BJT → C/B/E."""

    DRAIN = "d"
    GATE = "g"
    SOURCE = "s"
    BULK = "b"
    COLLECTOR = "c"
    BASE = "base"
    EMITTER = "e"
    PLUS = "p"
    MINUS = "n"
    PORT = "port"  # generic positional subckt port (role unresolved)


class Fidelity(str, Enum):
    """Small-signal model fidelity — SymXplorer's ladder, expressed as primitive selection (P2)."""

    IDEAL = "ideal"  # gm only
    SOME_PARASITIC = "some_parasitic"  # + ro
    FULL = "full"  # + caps + gmb


# ------------------------------------------------------------------------
# Value types (frozen → hashable, byte-identical)
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class Net:
    """A circuit net (node) with its small-signal role."""

    name: str
    role: NetRole = NetRole.SIGNAL

    @property
    def is_ac_ground(self) -> bool:
        """True for the reference node and any pure-DC supply (both are 0 V small-signal)."""
        return self.role in (NetRole.GROUND, NetRole.SUPPLY_DC)


@dataclass(frozen=True)
class Terminal:
    """One device terminal: a role-tag bound to a net name (in the device's fixed pin order)."""

    role: PinRole
    net: str


@dataclass(frozen=True)
class PortPair:
    """A named analysis port. ``neg == ground`` ⇒ single-ended at that end."""

    pos: str
    neg: str

    def is_single_ended(self, ground: str = "0") -> bool:
        return self.neg == ground or self.neg.lower() in GROUND_NAMES


# ------------------------------------------------------------------------
# Device (holds dicts → conventionally immutable, not a frozen dataclass)
# ------------------------------------------------------------------------
@dataclass
class Device:
    """A typed device: a ref, a family, ordered role-tagged terminals, and sympified params.

    ``params`` values are sympy ``Expr`` (numeric → ``Float``/``Rational``; symbolic → ``Symbol``).
    ``op`` (operating point) is populated only when a sim/PDK has been consulted (off the core path).
    ``match_group`` tags matched devices (a diff pair / a mirror) for the post-R1 DM/CM + EQUALITY
    machinery; it is ``None`` in R1.
    """

    ref: str
    kind: DeviceKind
    terminals: tuple[Terminal, ...]
    model: str | None = None
    params: dict[str, sp.Expr] = field(default_factory=dict)
    op: dict[str, float] | None = None
    match_group: str | None = None

    def net_of(self, role: PinRole) -> str | None:
        """The net wired to the terminal with the given role (first match), or ``None``."""
        for t in self.terminals:
            if t.role is role:
                return t.net
        return None

    @property
    def nets(self) -> tuple[str, ...]:
        """The nets this device touches, in pin order."""
        return tuple(t.net for t in self.terminals)


# ------------------------------------------------------------------------
# IR root
# ------------------------------------------------------------------------
@dataclass
class Circuit2TF:
    """The Stage-1 artifact: a typed small-signal netlist ready for MNA stamping.

    ``nets`` and ``ports`` are name-keyed; ``devices`` is an ordered tuple (deterministic).
    ``params`` are the global ``.param`` values, sympified once. ``symbolic`` is the keep-symbolic
    allow-list: the set of symbol names that remained symbolic after ingestion (everything else is a
    candidate for numeric substitution before the determinant in P3).
    """

    name: str
    nets: dict[str, Net] = field(default_factory=dict)
    devices: tuple[Device, ...] = ()
    ports: dict[str, PortPair] = field(default_factory=dict)
    params: dict[str, sp.Expr] = field(default_factory=dict)
    symbolic: frozenset[str] = frozenset()
    ground: str = "0"

    # -- convenience accessors ------------------------------------------------
    def net(self, name: str) -> Net:
        return self.nets[name]

    def device(self, ref: str) -> Device:
        for d in self.devices:
            if d.ref == ref:
                return d
        raise KeyError(ref)

    def devices_of(self, *kinds: DeviceKind) -> tuple[Device, ...]:
        return tuple(d for d in self.devices if d.kind in kinds)

    @property
    def ac_ground_nets(self) -> tuple[str, ...]:
        """All nets that are small-signal grounds (the reference + every pure-DC supply)."""
        return tuple(sorted(n.name for n in self.nets.values() if n.is_ac_ground))

    @property
    def free_symbols(self) -> frozenset[str]:
        """Every symbol name appearing in any device/global param (sorted-stable when listed)."""
        syms: set[str] = set()
        for d in self.devices:
            for v in d.params.values():
                syms.update(str(s) for s in v.free_symbols)
        for v in self.params.values():
            syms.update(str(s) for s in v.free_symbols)
        return frozenset(syms)

    # -- JSON front-end (round-trippable) ------------------------------------
    def to_dict(self) -> dict:
        """Serialize to a plain JSON-able dict (sympy ``Expr`` → canonical string)."""
        return {
            "name": self.name,
            "ground": self.ground,
            "nets": [{"name": n.name, "role": n.role.value} for n in self.nets.values()],
            "devices": [
                {
                    "ref": d.ref,
                    "kind": d.kind.value,
                    "model": d.model,
                    "terminals": [{"role": t.role.value, "net": t.net} for t in d.terminals],
                    "params": {k: str(v) for k, v in d.params.items()},
                    "op": d.op,
                    "match_group": d.match_group,
                }
                for d in self.devices
            ],
            "ports": {k: [p.pos, p.neg] for k, p in self.ports.items()},
            "params": {k: str(v) for k, v in self.params.items()},
            "symbolic": sorted(self.symbolic),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Circuit2TF":
        """Rebuild an IR from :meth:`to_dict` output (the JSON front-end)."""
        nets = {
            n["name"]: Net(n["name"], NetRole(n["role"])) for n in data.get("nets", [])
        }
        devices = tuple(
            Device(
                ref=d["ref"],
                kind=DeviceKind(d["kind"]),
                terminals=tuple(
                    Terminal(PinRole(t["role"]), t["net"]) for t in d["terminals"]
                ),
                model=d.get("model"),
                # plain sympify (no rational=True): the serialized string is already the canonical
                # form, so a Float stays a Float (rationalizing it would break the round-trip).
                params={k: sp.sympify(v) for k, v in d.get("params", {}).items()},
                op=d.get("op"),
                match_group=d.get("match_group"),
            )
            for d in data.get("devices", [])
        )
        ports = {k: PortPair(v[0], v[1]) for k, v in data.get("ports", {}).items()}
        params = {k: sp.sympify(v) for k, v in data.get("params", {}).items()}
        ir = cls(
            name=data.get("name", "circuit"),
            nets=nets,
            devices=devices,
            ports=ports,
            params=params,
            ground=data.get("ground", "0"),
        )
        ir.symbolic = frozenset(data.get("symbolic", [])) or ir.free_symbols
        return ir
