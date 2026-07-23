"""Graph → netlist emission, per dialect, with optional per-PDK device renaming.

Emits one device line per component **from the graph's own data** — deliberately NOT via spicelib's
``add_component`` (it conflates model/value and its ``Component.model`` is broken). The default
(``spice``) output re-parses cleanly with :class:`~spicexplorer_core.spice_engine.NetlistView`;
``spectre``/``hspice`` output re-parses through the core dialect readers (round-trip verified by
graph isomorphism).

The emitter family is a Template Method over one deterministic traversal: the base owns component
ordering, the value slot, and PDK finger/model retargeting; a dialect subclass owns only line
syntax. Syntax facts (param aliases like ``m``↔``multi``, identifier rules) come from the same
:class:`~spicexplorer_core.spice_engine.DialectSpec` tables the readers use, so read and write
cannot drift apart.

The ``pdk`` argument retargets MOS device/model names through the PDK device-name map's reverse
lookup: an IHP graph (``sg13_lv_nmos``) can be emitted with Skywater names
(``sky130_fd_pr__nfet_01v8``) — and composes with ``dialect`` (cross-PDK × cross-dialect).
Passives and sources keep their original value token — cross-PDK *passive* naming is out of
scope (device retargeting is specifically about nmos/pmos devices).

Subcircuit instances are emitted as instance lines referencing ``subckt_name``; nested ``.subckt``
*definitions* are not emitted (a black-box instance node does not carry the definition body). The
``subckt``/``ports`` arguments optionally wrap the emitted devices in one definition — the useful
shape for handing a DUT to another deck.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, ClassVar, Protocol, Sequence

from spicexplorer_core.spice_engine import NetlistDialect

from .model.nodes import (
    CapacitorNode,
    ComponentNode,
    CurrentSourceNode,
    DeviceType,
    InductorNode,
    MosfetNode,
    MosPolarityType,
    ResistorNode,
    SubcktInstanceNode,
    VccsNode,
    VcvsNode,
    VoltageSourceNode,
)
from .pdk import Pdk, mos_flavor

if TYPE_CHECKING:
    from .graph import CircuitGraph

logger = logging.getLogger(__name__)

__all__ = [
    "to_netlist",
    "NetlistEmitter",
    "BaseNetlistEmitter",
    "SpiceEmitter",
    "HspiceEmitter",
    "SpectreEmitter",
]


class NetlistEmitter(Protocol):
    """The emitter seam: render a graph as netlist text in one dialect."""

    dialect: NetlistDialect

    def emit(
        self,
        graph: "CircuitGraph",
        *,
        pdk: Pdk | None = None,
        title: str | None = None,
        subckt: str | None = None,
        ports: Sequence[str] | None = None,
    ) -> str: ...


def to_netlist(
    graph: "CircuitGraph",
    *,
    pdk: Pdk | None = None,
    title: str | None = None,
    dialect: NetlistDialect | str = NetlistDialect.SPICE,
    subckt: str | None = None,
    ports: Sequence[str] | None = None,
) -> str:
    """Render ``graph`` back to netlist text (deterministic; dialect-selectable).

    With ``pdk``, MOS model names are retargeted to that PDK. Without it, each device keeps its
    original model/value token. ``dialect`` picks the output syntax (default ``spice`` — the
    historical output, unchanged). ``subckt="name"`` (with an explicit ``ports`` list) wraps the
    device lines in one subcircuit definition.
    """
    emitter = _EMITTERS[NetlistDialect.coerce(dialect)]
    return emitter.emit(graph, pdk=pdk, title=title, subckt=subckt, ports=ports)


# ---------------------------------------------------------------------------
# The emitter family
# ---------------------------------------------------------------------------
class BaseNetlistEmitter:
    """Shared deterministic traversal; subclasses override line syntax only."""

    dialect: ClassVar[NetlistDialect]

    # -- template method -------------------------------------------------
    def emit(
        self,
        graph: "CircuitGraph",
        *,
        pdk: Pdk | None = None,
        title: str | None = None,
        subckt: str | None = None,
        ports: Sequence[str] | None = None,
    ) -> str:
        lines = self._header(graph, title)
        body = [self._device_line(comp, graph, pdk) for comp in graph.get_components(sort=True)]
        if subckt is not None:
            if not ports:
                raise ValueError(
                    "subckt= requires an explicit ports list (a flat graph carries no port order)"
                )
            lines.append(self._subckt_open(subckt, list(ports)))
            lines.extend(body)
            lines.append(self._subckt_close(subckt))
        else:
            lines.extend(body)
        lines.extend(self._footer())
        return "\n".join(lines) + "\n"

    # -- shared slots ------------------------------------------------------
    def _nets(self, comp: ComponentNode, graph: "CircuitGraph") -> list[str]:
        conns = graph.connections(comp)
        try:
            return [conns[pin.value] for pin in comp._PIN_ORDER]
        except KeyError as exc:
            raise ValueError(
                f"{comp.name}: pin {exc.args[0]!r} is unconnected; cannot emit a device line"
            ) from exc

    def _value(self, comp: ComponentNode, pdk: Pdk | None) -> str:
        # The value-slot must be non-empty: an empty token would shift the last *net* into the
        # model/value position on re-parse, silently changing the circuit. Fail loudly instead.
        value = _value_slot(comp, pdk)
        if not value:
            raise ValueError(
                f"{comp.name}: no model/value token for {type(comp).__name__}; emitting would "
                f"corrupt the netlist (a net would be misread as the model)"
            )
        return value

    def _params(self, comp: ComponentNode, pdk: Pdk | None) -> list[tuple[str, str | float]]:
        # Remaining k=v params (the value/model token lives in the value slot, never duplicated).
        emit_params = _retarget_fingers(comp.params, pdk) if isinstance(comp, MosfetNode) else comp.params
        return [(k, _fmt_param(v)) for k, v in sorted(emit_params.items()) if k != "Value"]

    # -- dialect hooks -------------------------------------------------------
    def _header(self, graph: "CircuitGraph", title: str | None) -> list[str]:
        raise NotImplementedError

    def _footer(self) -> list[str]:
        raise NotImplementedError

    def _device_line(self, comp: ComponentNode, graph: "CircuitGraph", pdk: Pdk | None) -> str:
        raise NotImplementedError

    def _subckt_open(self, name: str, ports: list[str]) -> str:
        raise NotImplementedError

    def _subckt_close(self, name: str) -> str:
        raise NotImplementedError


class SpiceEmitter(BaseNetlistEmitter):
    """The canonical/ngspice-flavored output — byte-identical to the historical emitter."""

    dialect = NetlistDialect.SPICE

    def _header(self, graph: "CircuitGraph", title: str | None) -> list[str]:
        return [f"* {title or graph.name} (emitted by spicexplorer-circuitgraph)"]

    def _footer(self) -> list[str]:
        return [".end"]

    def _device_line(self, comp: ComponentNode, graph: "CircuitGraph", pdk: Pdk | None) -> str:
        nets = " ".join(self._nets(comp, graph))
        value = self._value(comp, pdk)
        # The value-slot is the only field allowed to contain spaces and MUST stay terminal
        # (before params) so multi-token source values like "dc 1.8 ac 1" re-parse correctly.
        params = "".join(f" {k}={v}" for k, v in self._params(comp, pdk))
        return f"{comp.name} {nets} {value}{params}".rstrip()

    def _subckt_open(self, name: str, ports: list[str]) -> str:
        return f".subckt {name} {' '.join(ports)}"

    def _subckt_close(self, name: str) -> str:
        return ".ends"


class HspiceEmitter(SpiceEmitter):
    """HSPICE output — the structural subset is shared SPICE syntax; only the tag differs."""

    dialect = NetlistDialect.HSPICE


_LEADING_DIGIT = re.compile(r"^\d")
_INVALID_ID_CHAR = re.compile(r"[^A-Za-z0-9_]")
_NUMERIC_NET = re.compile(r"^\d+$")
# `dc <v> [ac <v>] [pulse(...)|sin(...)]` or a single token — the source-value shapes the
# readers produce. pulse args are the SPICE positional list `(V1 V2 [TD [TR [TF [PW [PER]]]]])`;
# sin args are `(VO VA FREQ [TD])`.
_SOURCE_VALUE = re.compile(
    r"^(?:dc\s+(?P<dc>\S+))?\s*(?:ac\s+(?P<ac>\S+))?"
    r"\s*(?:pulse\s*\(\s*(?P<pulse>[^)]*?)\s*\))?"
    r"\s*(?:sin\s*\(\s*(?P<sin>[^)]*?)\s*\))?$"
    r"|^(?P<plain>\S+)$",
    re.IGNORECASE,
)
# SPICE pulse positional order → the Spectre `vsource/isource type=pulse` parameter names.
_PULSE_PARAM_ORDER = ("val0", "val1", "delay", "rise", "fall", "width", "period")
# SPICE sin positional order → the Spectre `type=sine` parameter names. VO doubles as the
# source's `dc` operating point (ngspice's time-0/OP value) unless an explicit `dc` is given.
_SIN_PARAM_ORDER = ("sinedc", "ampl", "freq", "delay")


class SpectreEmitter(BaseNetlistEmitter):
    """Spectre output: paren node lists, primitive masters, ``multi=``, ``subckt … ends``.

    Identifier rules (live-trial landmines): a Spectre identifier can't start with a digit
    (``5t`` lexes as a number) and can't contain punctuation (``ota-5t`` lexes as a subtraction) —
    ``sanitize_ref`` maps invalid characters to ``_`` and prefixes digit-led names with ``x``.
    Net names follow the same rule, except purely numeric nodes (``0`` is ground) which are
    legal Spectre nodes and stay literal.
    """

    dialect = NetlistDialect.SPECTRE

    def _header(self, graph: "CircuitGraph", title: str | None) -> list[str]:
        return [
            f"// {title or graph.name} (emitted by spicexplorer-circuitgraph)",
            "simulator lang=spectre",
        ]

    def _footer(self) -> list[str]:
        return []

    def _nets(self, comp: ComponentNode, graph: "CircuitGraph") -> list[str]:
        return [self.sanitize_net(n) for n in super()._nets(comp, graph)]

    def _params(self, comp: ComponentNode, pdk: Pdk | None) -> list[tuple[str, str | float]]:
        return [(k, self._expr(v)) for k, v in super()._params(comp, pdk)]

    def _subckt_open(self, name: str, ports: list[str]) -> str:
        safe_ports = [self.sanitize_net(p) for p in ports]
        return f"subckt {self.sanitize_ref(name)} {' '.join(safe_ports)}"

    def _subckt_close(self, name: str) -> str:
        return f"ends {self.sanitize_ref(name)}"

    @staticmethod
    def sanitize_ref(name: str) -> str:
        """Map invalid identifier characters to ``_``; prefix digit-led names with ``x``."""
        safe = _INVALID_ID_CHAR.sub("_", name)
        return f"x{safe}" if _LEADING_DIGIT.match(safe) else safe

    @classmethod
    def sanitize_net(cls, name: str) -> str:
        """Nets follow the identifier rule, but purely numeric nodes (``0``, ``1``) are legal.

        Node names are **case-folded to lowercase**. SPICE is case-insensitive (ngspice folds
        ``VOUT`` and ``vout`` to one node), but Spectre ``lang=spectre`` is case-SENSITIVE — so
        a source deck that spells an internal net ``VOUT`` while its subckt port / testbench
        probe are lowercase ``vout`` would emit two *distinct* Spectre nodes, silently leaving
        the amplifier output disconnected from the port (observed live: constant garbage AC gain
        on every mixed-case AnalogGym port). Folding nets here — symmetric with the parameter
        case-folding this translator already does — keeps every reference to one node identical.
        Model/master/instance *reference* names are NOT folded (they stay case-exact for the PDK
        model cards); only nets pass through here. Numeric ground/nodes stay literal."""
        if _NUMERIC_NET.match(name):
            return name
        return cls.sanitize_ref(name).lower()

    @staticmethod
    def _expr(value: str | float) -> str | float:
        """SPICE ``{expr}`` braces → bare Spectre expression (``c={CL}`` → ``c=CL``)."""
        if isinstance(value, str):
            v = value.strip()
            if v.startswith("{") and v.endswith("}"):
                return v[1:-1].strip()
        return value

    @staticmethod
    def _ac_small_signal(token: str | float) -> str:
        """One SPICE ``ac <mag>`` marker → the ``mag=`` + ``pacmag=`` pair.

        Spectre's `ac` accepts a SIGNED mag, but `pac` REJECTS pacmag<0 (CMI-2048,
        found live on the differential ±0.5 drive) — a negative periodic excitation
        is spelled ``pacmag=|v| pacphase=180`` instead. Symbolic magnitudes pass
        through unchanged (sign unknowable at emit time)."""
        try:
            v = float(token)
        except (TypeError, ValueError):
            return f"mag={token} pacmag={token}"
        if v < 0:
            return f"mag={token} pacmag={-v:.10g} pacphase=180"
        return f"mag={token} pacmag={token}"

    def _device_line(self, comp: ComponentNode, graph: "CircuitGraph", pdk: Pdk | None) -> str:
        ref = self.sanitize_ref(comp.name)
        nets = " ".join(self._nets(comp, graph))
        params = self._params(comp, pdk)

        if isinstance(comp, MosfetNode):
            master = self.sanitize_ref(self._value(comp, pdk))
            # `m=` is emitted VERBATIM: Spectre honors `m` as the device multiplier on
            # model-card MOS, while `multi` is silently IGNORED with a warning (proven
            # live on KIT65 DEVICE 2026-07-17: m=4 quadruples id/gm, multi=4 does
            # nothing — the old m→multi rename made every multi-finger device run at
            # m=1). `multi` remains a read-side alias in the dialect spec.
            body = " ".join(f"{k}={v}" for k, v in params)
            return f"{ref} ({nets}) {master} {body}".rstrip()

        if isinstance(comp, SubcktInstanceNode):
            master = self.sanitize_ref(self._value(comp, pdk))
            body = " ".join(f"{k}={v}" for k, v in params)
            return f"{ref} ({nets}) {master} {body}".rstrip()

        value = self._value(comp, pdk)
        if isinstance(comp, (VccsNode, VcvsNode)):
            # Spectre's linear controlled-source primitives share the SPICE terminal order
            # (out+ out- ctrl+ ctrl-); the gain parameter is `gm=` for vccs, `gain=` for vcvs.
            master, key = ("vccs", "gm") if isinstance(comp, VccsNode) else ("vcvs", "gain")
            body = "".join(f" {k}={v}" for k, v in params)
            return f"{ref} ({nets}) {master} {key}={self._expr(value)}{body}".rstrip()

        if isinstance(comp, (ResistorNode, CapacitorNode, InductorNode)):
            master, key = {
                DeviceType.RES: ("resistor", "r"),
                DeviceType.CAP: ("capacitor", "c"),
                DeviceType.IND: ("inductor", "l"),
            }[comp.device_type]
            if not _value_is_numericish(value):
                # A model-named passive (e.g. `rupolym`): the token IS the master.
                master, key_part = self.sanitize_ref(value), ""
            else:
                key_part = f" {key}={self._expr(value)}"
            body = "".join(f" {k}={v}" for k, v in params)
            return f"{ref} ({nets}) {master}{key_part}{body}".rstrip()

        if isinstance(comp, (VoltageSourceNode, CurrentSourceNode)):
            master = "vsource" if isinstance(comp, VoltageSourceNode) else "isource"
            if isinstance(comp, VoltageSourceNode) and comp.name.upper().startswith("VIPRB"):
                # the loop-probe MARKER (stb benches): a 0 V source named VIPRB* stands in
                # for Spectre's `iprobe` primitive (the `stb … probe=<name>` target). Any
                # bias/stimulus on it would be silently lost in translation, so only an
                # exact 0 V dc source qualifies.
                probe_val = _SOURCE_VALUE.match(value.strip())
                dc_tok = probe_val and (probe_val.group("dc") or probe_val.group("plain"))
                try:
                    is_zero = dc_tok is not None and float(dc_tok) == 0.0
                except ValueError:
                    is_zero = False
                if not is_zero or (probe_val and (probe_val.group("ac") or probe_val.group("pulse") or probe_val.group("sin"))):
                    raise ValueError(
                        f"{comp.name}: a VIPRB* loop-probe marker must be exactly a 0 V dc "
                        f"source (it becomes a Spectre iprobe), got {value!r}"
                    )
                return f"{ref} ({nets}) iprobe"
            m = _SOURCE_VALUE.match(value.strip())
            if not m or not (
                m.group("dc") or m.group("ac") or m.group("pulse") or m.group("sin") or m.group("plain")
            ):
                raise ValueError(
                    f"{comp.name}: source value {value!r} has no Spectre mapping "
                    f"(stimulus specs beyond dc/ac/pulse/sin are testbench translation — out of scope)"
                )
            parts = []
            dc = m.group("dc") or m.group("plain")
            if dc is None and m.group("sin"):
                # no explicit dc: SPICE uses the sine offset VO as the OP value — mirror it
                dc = m.group("sin").split()[0] if m.group("sin").split() else None
            if dc is not None:
                parts.append(f"dc={self._expr(dc)}")
            if m.group("ac"):
                # the `ac <mag>` marker feeds BOTH small-signal families: a static `ac`
                # analysis reads mag=, a composed periodic `pac` (riding a pss) reads
                # pacmag= — emitting both lets ONE deck marker serve either analysis
                # (golden chopper benches; inert when no pac is composed).
                parts.append(self._ac_small_signal(self._expr(m.group("ac"))))
            if m.group("pulse"):
                # SPICE `pulse(V1 V2 TD TR TF PW PER)` → Spectre `type=pulse val0=… val1=…
                # delay=… rise=… fall=… width=… period=…` (positional, all optional past V2)
                args = m.group("pulse").split()
                if not 2 <= len(args) <= len(_PULSE_PARAM_ORDER):
                    raise ValueError(
                        f"{comp.name}: pulse(...) needs 2-{len(_PULSE_PARAM_ORDER)} args "
                        f"(V1 V2 [TD [TR [TF [PW [PER]]]]]), got {len(args)}: {value!r}"
                    )
                parts.append("type=pulse")
                parts.extend(
                    f"{k}={self._expr(a)}" for k, a in zip(_PULSE_PARAM_ORDER, args)
                )
            if m.group("sin"):
                # SPICE `sin(VO VA FREQ [TD])` → Spectre `type=sine sinedc=… ampl=… freq=…
                # [delay=…]` (THETA damping has no clean Spectre twin — rejected, not dropped)
                args = m.group("sin").split()
                if not 3 <= len(args) <= len(_SIN_PARAM_ORDER):
                    raise ValueError(
                        f"{comp.name}: sin(...) needs 3-{len(_SIN_PARAM_ORDER)} args "
                        f"(VO VA FREQ [TD]), got {len(args)}: {value!r}"
                    )
                parts.append("type=sine")
                parts.extend(
                    f"{k}={self._expr(a)}" for k, a in zip(_SIN_PARAM_ORDER, args)
                )
            body = "".join(
                f" {self._ac_small_signal(v)}" if k.lower() == "ac" else f" {k}={v}"
                for k, v in params
            )
            return f"{ref} ({nets}) {master} {' '.join(parts)}{body}".rstrip()

        # Fallback for any future typed node: SPICE-shaped line (still Spectre-readable via the
        # numeric-master passthrough on re-parse).
        body = "".join(f" {k}={v}" for k, v in params)
        return f"{ref} {nets} {value}{body}".rstrip()


def _value_is_numericish(value: str) -> bool:
    """True for value tokens (``1k``, ``2p``, ``{expr}``, ``1.4e-9``) vs model names (``rupolym``)."""
    return bool(re.match(r"^[+-]?(\d|\.\d|\{|\()", value.strip()))


_EMITTERS: dict[NetlistDialect, BaseNetlistEmitter] = {
    NetlistDialect.SPICE: SpiceEmitter(),
    NetlistDialect.HSPICE: HspiceEmitter(),
    NetlistDialect.SPECTRE: SpectreEmitter(),
}


# ---------------------------------------------------------------------------
# Shared slot helpers (dialect-independent)
# ---------------------------------------------------------------------------
def _fmt_param(v: str | float) -> str | float:
    """Integral floats render as ints (``ng=4`` not ``ng=4.0``) — the JSON contract round-trips
    numeric params as floats, and the emitted netlist must not diverge from the direct path."""
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def _retarget_fingers(params: dict[str, str | float], pdk: Pdk | None) -> dict[str, str | float]:
    """Retarget the canonical finger convention (total ``w`` + ``ng``) to ``pdk``'s.

    The canonical graph (authored IHP-style) carries the *total* width as ``w`` and the finger count
    as ``ng``. Two independent PDK traits adjust this on emit:

    * ``finger_param`` other than ``ng`` (sky130/gf180 use ``nf``) → rename ``ng`` to it, and
    * ``width_per_finger`` → the device's ``w`` is *per finger* (total = w·nf), so divide the total
      width across the fingers: ``w='(w)/(ng)'``.

    A device with no ``ng`` (single finger) is unchanged, as is the default convention (IHP: ``ng``,
    total width). Param names match case-insensitively (SPICE is case-insensitive: ``W=``/``NG=``
    are as legitimate as ``w=``/``ng=``) — a case-sensitive match used to silently skip the width
    division while still renaming the finger param, emitting an N×-too-wide device.
    """
    if pdk is None:
        return params
    ng_key = next((k for k in params if k.lower() == "ng"), None)
    if ng_key is None or (pdk.finger_param == "ng" and not pdk.width_per_finger):
        return params
    out = dict(params)
    ng = _fmt_param(out.pop(ng_key))
    if pdk.width_per_finger:
        w_key = next((k for k in out if k.lower() == "w"), None)
        if w_key is not None:
            out[w_key] = f"'({_fmt_param(out[w_key])})/({ng})'"
    out[pdk.finger_param] = ng
    return out


def _value_slot(comp: ComponentNode, pdk: Pdk | None) -> str:
    """The model/value token after the nodes: a (possibly PDK-renamed) model for MOS, the subckt
    name for an instance, else the device's original value token (spicelib's ``Value`` param)."""
    if isinstance(comp, MosfetNode):
        if pdk is not None:
            if comp.polarity is MosPolarityType.UNKNOWN:
                logger.warning(
                    "%s: unknown polarity — cannot retarget to %s; keeping %r",
                    comp.name, pdk.name, comp.spice_model,
                )
            else:
                renamed = pdk.model_for(
                    DeviceType.MOS, comp.polarity, mos_flavor(comp.spice_model)
                )
                if renamed:
                    return renamed
                logger.warning(
                    "%s: %s has no %s device; keeping source model %r (mixed-PDK netlist)",
                    comp.name, pdk.name, comp.polarity.value, comp.spice_model,
                )
        return comp.spice_model or ""
    if isinstance(comp, SubcktInstanceNode):
        return comp.subckt_name or ""
    return str(comp.params.get("Value", ""))
