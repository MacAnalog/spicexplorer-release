"""Device factory — map a SPICE reference designator to a typed :class:`ComponentNode`.

Dispatch is by reference-designator prefix. MOS polarity is resolved via the PDK map first
(when one is supplied), then a ``nmos``/``pmos`` model-name substring fallback.

An **unrecognized** device returns ``None``; the caller (the graph build) decides whether to
skip-and-warn or raise — the prototype unconditionally aborted the whole build, which this
replaces. Two cases yield ``None``:

* an unknown prefix (e.g. a generic subckt instance ``X…`` that is not ``XM/XR/XC/XL`` — those
  are modeled as typed-port subckt instances elsewhere), and
* an **arity mismatch**: the netlist wires a different number of nets than the typed node's fixed
  pin set. This catches a subckt instance that slipped through the ``XM/XR/XC/XL`` heuristic
  (e.g. ``Xmirror``) *and* a device with an unexpected terminal count — so the build never adds a
  half-connected phantom node.

Controlled sources (``G`` = VCCS, ``E`` = VCVS) are supported in their **linear 4-terminal** form
only (``G1 n+ n- nc+ nc- value``); the behavioral shapes (POLY, ``value=``, ``table=``,
``Laplace=``) also yield ``None``. spicelib parses G/E as two-node devices with the controlling
pair inside the value token — :func:`wired_nets` splits them back out for the graph build.
"""

from __future__ import annotations

import logging
import re

from spicexplorer_core.spice_engine import NetlistViewLike

from .model.edges import SubcktPort
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
from .pdk import Pdk

logger = logging.getLogger(__name__)

# Characters that disqualify a token from being a plain net name (an expression, a k=v
# parameter, or a POLY(...) header — none of which the linear controlled-source card has).
_NON_NET_CHARS = frozenset("=(){}")


def _split_controlled_value(value: str) -> tuple[tuple[str, str], str, dict[str, str]] | None:
    """Split spicelib's controlled-source value token into ``((nc+, nc-), gain, tail_params)``.

    spicelib models a ``G``/``E`` element as a *two-node* device: for the linear 4-terminal card
    ``G1 n+ n- nc+ nc- <gain> [k=v …]`` everything past the output pair rides in the ``Value``
    param (``"nc+ nc- <gain> [k=v …]"``). This splits the controlling nets and the gain back out
    (the gain survives verbatim — it may be a bare symbol like ``GM``, an eng string, or a braced
    ``{expr}``). Returns ``None`` for the non-linear forms (``POLY``, ``value=``, ``table=``,
    ``Laplace=``, current-controlled ``Vnam`` shapes) — the caller degrades to skip-and-warn.
    """
    tokens = value.split()
    # Peel trailing k=v parameters (e.g. `m=2`); a braced gain never contains `=`.
    tail: dict[str, str] = {}
    while tokens and "=" in tokens[-1]:
        key, _, val = tokens.pop().partition("=")
        tail[key] = val
    if len(tokens) < 3:
        return None
    ctrl_p, ctrl_n = tokens[0], tokens[1]
    if _NON_NET_CHARS & set(ctrl_p + ctrl_n):
        return None  # not plain net names (POLY(...) header, expression, …)
    gain = " ".join(tokens[2:])
    if len(tokens) > 3 and not (gain.startswith("{") and gain.endswith("}")):
        return None  # multi-token gain is only legal as one braced {expr}
    if "=" in gain:
        return None
    return (ctrl_p, ctrl_n), gain, tail


def wired_nets(comp: ComponentNode, view: NetlistViewLike) -> list[str]:
    """All nets the netlist wires to ``comp``, in ``_PIN_ORDER`` order.

    For most devices this is exactly ``view.get_component_nodes``; a controlled source (G/E)
    additionally carries its two controlling nets inside the spicelib value token (see
    :func:`_split_controlled_value`) — they are appended here so the graph can connect CP/CN.
    """
    nets = list(view.get_component_nodes(comp.name))
    if isinstance(comp, (VccsNode, VcvsNode)):
        split = _split_controlled_value(str(view.get_component_value(comp.name)))
        if split is not None:
            nets.extend(split[0])
    return nets


class DeviceFactory:
    """Builds typed nodes from a :class:`~spicexplorer_core.spice_engine.NetlistView`."""

    # NOTE: the ``XM/XR/XC/XL`` compound prefixes treat an X-wrapped primitive as that primitive.
    # A generic subckt instance whose name starts with one of these is caught by the arity guard
    # in ``create`` *unless* it happens to have the same port count as the primitive — that
    # residual ambiguity is resolved by Phase 2's subckt resolution.
    MOS_PREFIXES = ("M", "XM")
    RES_PREFIXES = ("R", "XR")
    CAP_PREFIXES = ("C", "XC")
    IND_PREFIXES = ("L", "XL")
    VSOURCE_PREFIXES = ("V",)
    ISOURCE_PREFIXES = ("I",)
    VCCS_PREFIXES = ("G",)
    VCVS_PREFIXES = ("E",)

    def __init__(self, pdk: Pdk | None = None) -> None:
        self._pdk = pdk

    def create(self, reference: str, view: NetlistViewLike) -> ComponentNode | None:
        """Return a typed node for ``reference``, or ``None`` if it can't be modeled cleanly.

        ``None`` means either an unrecognized prefix or an arity mismatch (the netlist wires a
        different number of nets than the typed node's fixed pin set) — in both cases the build
        skips it rather than creating a phantom.
        """
        node = self._typed_node(reference, view)
        if node is None:
            return None
        n_nets = len(wired_nets(node, view))
        if n_nets != len(node._PIN_ORDER):
            logger.warning(
                "skipping %s: netlist wires %d nets but %s expects %d pins",
                reference,
                n_nets,
                type(node).__name__,
                len(node._PIN_ORDER),
            )
            return None
        return node

    def _typed_node(self, reference: str, view: NetlistViewLike) -> ComponentNode | None:
        """Type the device by prefix (no arity check — that is :meth:`create`'s job)."""
        ref_u = reference.upper()

        if ref_u.startswith(self.MOS_PREFIXES):
            model = view.get_component_value(reference)
            # 'Value' duplicates the model name on the MOS path → drop it from params.
            params = {k: v for k, v in view.get_component_parameters(reference).items() if k != "Value"}
            return MosfetNode(
                name=reference,
                device_type=DeviceType.MOS,
                polarity=self._mos_polarity(model),
                spice_model=model,
                params=params,
            )

        if ref_u.startswith(self.RES_PREFIXES):
            return ResistorNode(
                name=reference,
                device_type=DeviceType.RES,
                params=view.get_component_parameters(reference),
            )

        if ref_u.startswith(self.CAP_PREFIXES):
            return CapacitorNode(
                name=reference,
                device_type=DeviceType.CAP,
                params=view.get_component_parameters(reference),
            )

        if ref_u.startswith(self.IND_PREFIXES):
            return InductorNode(
                name=reference,
                device_type=DeviceType.IND,
                params=view.get_component_parameters(reference),
            )

        if ref_u.startswith(self.VSOURCE_PREFIXES):
            return VoltageSourceNode(
                name=reference,
                device_type=DeviceType.VSOURCE,
                params=view.get_component_parameters(reference),
            )

        if ref_u.startswith(self.ISOURCE_PREFIXES):
            return CurrentSourceNode(
                name=reference,
                device_type=DeviceType.ISOURCE,
                params=view.get_component_parameters(reference),
            )

        if ref_u.startswith(self.VCCS_PREFIXES + self.VCVS_PREFIXES):
            return self._controlled_source(reference, view)

        # Generic subcircuit instance (the XM/XR/XC/XL primitives were matched above). Model it as
        # a black-box component with an open, named port set: formal .SUBCKT-header port names when
        # resolvable, else positional "1".."N". Ports always equal the instance's net count, so this
        # never trips the arity guard.
        if ref_u.startswith("X"):
            instance_nets = view.get_component_nodes(reference)
            if not instance_nets:  # portless/unwired instance — don't create a phantom node
                logger.warning("skipping %s: subckt instance has no connected nets", reference)
                return None
            formal = view.get_subcircuit_ports(reference)
            # Use the formal .SUBCKT port names only when resolvable, correctly sized, AND unique:
            # edges/connections are keyed by port name, so duplicate names would collide. Otherwise
            # fall back to positional "1".."N", which is always unique.
            if formal and len(formal) == len(instance_nets) and len(set(formal)) == len(formal):
                names: list[str] = formal
            else:
                if formal:
                    logger.warning(
                        "subckt %s: formal ports %s unusable (wrong count or duplicates); "
                        "using positional port names",
                        reference,
                        formal,
                    )
                names = [str(i) for i in range(1, len(instance_nets) + 1)]
            return SubcktInstanceNode(
                name=reference,
                device_type=DeviceType.SUBCKT,
                _PIN_ORDER=tuple(SubcktPort(name) for name in names),
                subckt_name=view.get_component_value(reference),
                params=view.get_component_parameters(reference),
            )

        return None

    def _controlled_source(self, reference: str, view: NetlistViewLike) -> ComponentNode | None:
        """A linear 4-terminal ``G`` (VCCS) / ``E`` (VCVS) card.

        The gain lands in ``params["Value"]`` *verbatim* (bare symbols like ``GM`` survive — the
        analog-db behavioral macromodels rely on it). Non-linear forms (POLY / ``value=`` /
        ``table=`` / ``Laplace=``) return ``None`` — the build skips-and-warns like any other
        unsupported device rather than adding a mis-pinned node.
        """
        split = _split_controlled_value(str(view.get_component_value(reference)))
        if split is None:
            logger.warning(
                "%s: only the linear 4-terminal controlled-source card "
                "(`%s n+ n- nc+ nc- value`) is supported",
                reference,
                reference,
            )
            return None
        _ctrl_nets, gain, tail = split
        params: dict[str, str | float] = {
            k: v for k, v in view.get_component_parameters(reference).items() if k != "Value"
        }
        params.update(tail)
        params["Value"] = gain
        if reference.upper().startswith(self.VCCS_PREFIXES):
            return VccsNode(name=reference, device_type=DeviceType.VCCS, params=params)
        return VcvsNode(name=reference, device_type=DeviceType.VCVS, params=params)

    def _mos_polarity(self, model: str | None) -> MosPolarityType:
        """PDK map first (authoritative), then a model-name fallback: the classic ``nmos``/
        ``pmos`` substrings, else a token-prefix test for the common foundry spellings
        (``DEVICE``, ``nfet_03v3``, ``DEVICE``, …). Token-wise (split on ``_``/digits'
        neighbors) so ``pinch``-style names can't false-positive on ``nch``."""
        if self._pdk is not None:
            dev = self._pdk.classify(model)
            if dev is not None and dev.polarity is not MosPolarityType.UNKNOWN:
                return dev.polarity
        if model:
            lowered = model.lower()
            if "nmos" in lowered:
                return MosPolarityType.NMOS
            if "pmos" in lowered:
                return MosPolarityType.PMOS
            for token in re.split(r"[^a-z0-9]+", lowered):
                if token.startswith(("nch", "nfet")):
                    return MosPolarityType.NMOS
                if token.startswith(("pch", "pfet")):
                    return MosPolarityType.PMOS
        return MosPolarityType.UNKNOWN
