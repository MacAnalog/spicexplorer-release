"""Stage 2 — small-signal modeling: replace each device with primitives at a chosen fidelity.

The device-model spec is **data** (SLiCAP's two-layer idea, made type-safe — see ``NOTICE``): a
:class:`SmallSignalModel` declares which device families it linearizes and an ``expand`` that emits
only :mod:`.model.primitives`. Adding a device family (a custom BJT, an op-amp macromodel) is one
``register_model(...)`` call — **nothing in the MNA core changes**, and because ``expand`` returns
only known primitives a third-party model can never break the solver.

The **fidelity ladder** is expressed as *primitive selection*, not four hardcoded matrices
(SymXplorer's ladder, re-expressed): a MOSFET emits

* ``IDEAL``          → ``gm`` VCCS only;
* ``SOME_PARASITIC`` → ``+ ro`` (output conductance);
* ``FULL``           → ``+ gmb`` body VCCS ``+ Cgs/Cgd/Cdb/Csb``.

Symbols introduced per instance (``gm_m1``, ``ro_m1``, …) are minted unique by a :class:`SymbolMint`.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

import sympy as sp

from .model.ir import Circuit2TF, Device, DeviceKind, Fidelity, PinRole
from .model.primitives import (
    VCCS,
    Capacitor,
    Conductance,
    IndependentI,
    IndependentV,
    Inductor,
    Primitive,
)
from .model.ssir import SmallSignalIR

logger = logging.getLogger(__name__)

__all__ = [
    "SymbolMint",
    "SmallSignalModel",
    "MODEL_REGISTRY",
    "register_model",
    "small_signal_model",
]

# Fidelity ordering for "at least this much detail" comparisons.
_FIDELITY_RANK = {Fidelity.IDEAL: 0, Fidelity.SOME_PARASITIC: 1, Fidelity.FULL: 2}


def _label(ref: str) -> str:
    """A short, readable per-instance label for minted symbols (strip an X-wrapper: ``XM1`` → ``m1``)."""
    up = ref.upper()
    if up.startswith(("XM", "XR", "XC", "XL")):
        return ref[1:].lower()
    return ref.lower()


# ------------------------------------------------------------------------
# Symbol minting
# ------------------------------------------------------------------------
class SymbolMint:
    """Mints per-instance-unique small-signal symbols (``gm`` for ``M1`` → ``gm_m1``).

    Tracks every symbol it has produced so a model never collides two devices, while leaving matched
    devices free to be tagged equal later (an EQUALITY assumption ``gm_m2 → gm_m1``, P5).
    """

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def sym(self, base: str, ref: str) -> sp.Symbol:
        name = f"{base}_{_label(ref)}"
        self._seen.add(name)
        return sp.Symbol(name, positive=True)

    @property
    def names(self) -> frozenset[str]:
        return frozenset(self._seen)


# ------------------------------------------------------------------------
# The model spec
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class SmallSignalModel:
    """A data-driven small-signal model: which families it linearizes + how it expands.

    ``expand(device, mint, fidelity) -> (primitives, introduced_symbols)`` returns only
    :mod:`.model.primitives` and the ``{role: Symbol}`` map it minted (recorded on the SSIR).
    """

    name: str
    kinds: frozenset[DeviceKind]
    expand: Callable[[Device, SymbolMint, Fidelity], tuple[list[Primitive], dict[str, sp.Symbol]]]


MODEL_REGISTRY: dict[DeviceKind, SmallSignalModel] = {}


def register_model(model: SmallSignalModel) -> None:
    """Register ``model`` as the default for each :class:`DeviceKind` it declares (public API)."""
    for kind in model.kinds:
        MODEL_REGISTRY[kind] = model


# ------------------------------------------------------------------------
# Built-in expansions
# ------------------------------------------------------------------------
def _bulk_net(dev: Device) -> str:
    """The bulk net, defaulting to the source when a 3-terminal MOS omits it (so ``Vbs = 0``)."""
    b = dev.net_of(PinRole.BULK)
    return b if b is not None else (dev.net_of(PinRole.SOURCE) or "0")


def expand_mosfet(
    dev: Device, mint: SymbolMint, fidelity: Fidelity
) -> tuple[list[Primitive], dict[str, sp.Symbol]]:
    """Hybrid-pi MOSFET expansion (topology ported from SLiCAP ``M``@39 — see ``NOTICE``).

    ``gm`` (gate VCCS) at every fidelity; ``ro`` (output conductance) from SOME_PARASITIC; ``gmb``
    (body VCCS) + ``Cgs/Cgd/Cdb/Csb`` at FULL. A missing bulk ties to the source (``gmb`` inert).
    """
    d = dev.net_of(PinRole.DRAIN) or "0"
    g = dev.net_of(PinRole.GATE) or "0"
    s = dev.net_of(PinRole.SOURCE) or "0"
    b = _bulk_net(dev)
    rank = _FIDELITY_RANK[fidelity]

    prims: list[Primitive] = []
    syms: dict[str, sp.Symbol] = {}

    # gm: I(d->s) = gm·(V[g]-V[s])  (Gm d s g s {gm})
    gm = mint.sym("gm", dev.ref)
    syms["gm"] = gm
    prims.append(VCCS(name=f"gm@{dev.ref}", np=d, nn=s, cp=g, cn=s, value=gm))

    # ro: output conductance go = 1/ro between d and s
    if rank >= _FIDELITY_RANK[Fidelity.SOME_PARASITIC]:
        ro = mint.sym("ro", dev.ref)
        syms["ro"] = ro
        prims.append(Conductance(name=f"ro@{dev.ref}", n1=d, n2=s, value=1 / ro))

    # gmb + junction/overlap caps
    if rank >= _FIDELITY_RANK[Fidelity.FULL]:
        gmb = mint.sym("gmb", dev.ref)
        syms["gmb"] = gmb
        prims.append(VCCS(name=f"gmb@{dev.ref}", np=d, nn=s, cp=b, cn=s, value=gmb))
        for role, (na, nb) in {
            "cgs": (g, s),
            "cgd": (g, d),
            "cdb": (d, b),
            "csb": (s, b),
        }.items():
            c = mint.sym(role, dev.ref)
            syms[role] = c
            prims.append(Capacitor(name=f"{role}@{dev.ref}", n1=na, n2=nb, value=c))

    return prims, syms


def _two_terminal_nets(dev: Device) -> tuple[str, str]:
    p = dev.net_of(PinRole.PLUS) or dev.nets[0]
    n = dev.net_of(PinRole.MINUS) or dev.nets[1]
    return p, n


def expand_resistor(
    dev: Device, mint: SymbolMint, fidelity: Fidelity
) -> tuple[list[Primitive], dict[str, sp.Symbol]]:
    p, n = _two_terminal_nets(dev)
    val = dev.params.get("value", mint.sym("r", dev.ref))
    if val == 0 or getattr(val, "is_zero", False):
        # 1/0 would become sympy `zoo` and surface as a silent NaN transfer function
        raise ValueError(
            f"{dev.ref}: zero-resistance element — a hard short is not modelable; "
            f"connect the two nets directly (or give the resistor a real value)"
        )
    prims: list[Primitive] = [Conductance(name=f"r@{dev.ref}", n1=p, n2=n, value=1 / val)]
    return prims, {}


def expand_capacitor(
    dev: Device, mint: SymbolMint, fidelity: Fidelity
) -> tuple[list[Primitive], dict[str, sp.Symbol]]:
    p, n = _two_terminal_nets(dev)
    val = dev.params.get("value", mint.sym("c", dev.ref))
    prims: list[Primitive] = [Capacitor(name=f"c@{dev.ref}", n1=p, n2=n, value=val)]
    return prims, {}


def expand_inductor(
    dev: Device, mint: SymbolMint, fidelity: Fidelity
) -> tuple[list[Primitive], dict[str, sp.Symbol]]:
    p, n = _two_terminal_nets(dev)
    val = dev.params.get("value", mint.sym("l", dev.ref))
    prims: list[Primitive] = [Inductor(name=f"l@{dev.ref}", n1=p, n2=n, value=val)]
    return prims, {}


def _independent_source(dev: Device) -> Primitive:
    p, n = _two_terminal_nets(dev)
    dc = dev.params.get("dc", sp.Integer(0))
    ac = dev.params.get("ac", sp.Integer(0))
    if dev.kind is DeviceKind.ISOURCE:
        return IndependentI(name=f"i@{dev.ref}", np=p, nn=n, dc=dc, ac=ac)
    return IndependentV(name=f"v@{dev.ref}", np=p, nn=n, dc=dc, ac=ac)


def _register_builtins() -> None:
    register_model(SmallSignalModel(
        "mos.hybrid_pi",
        frozenset({DeviceKind.NMOS, DeviceKind.PMOS, DeviceKind.MOS}),
        expand_mosfet,
    ))
    register_model(SmallSignalModel("passive.resistor", frozenset({DeviceKind.RESISTOR}), expand_resistor))
    register_model(SmallSignalModel("passive.capacitor", frozenset({DeviceKind.CAPACITOR}), expand_capacitor))
    register_model(SmallSignalModel("passive.inductor", frozenset({DeviceKind.INDUCTOR}), expand_inductor))


_register_builtins()


# ------------------------------------------------------------------------
# Stage function
# ------------------------------------------------------------------------
@dataclass
class _Skipped:
    refs: list[str] = field(default_factory=list)


def small_signal_model(
    ir: Circuit2TF,
    level: Fidelity = Fidelity.SOME_PARASITIC,
    *,
    models: dict[DeviceKind, SmallSignalModel] | None = None,
) -> SmallSignalIR:
    """Linearize every device in ``ir`` at fidelity ``level`` → a :class:`SmallSignalIR`.

    Independent V/I sources are carried through as excitation primitives. A device whose family has
    no registered model (an opaque subckt, an unknown element) is skipped with a warning — the MNA
    stage then sees a circuit it can fully stamp. ``models`` overrides/extends the registry per call.
    """
    registry = {**MODEL_REGISTRY, **(models or {})}
    primitives: list[Primitive] = []
    symbols: dict[str, dict[str, sp.Symbol]] = {}
    mint = SymbolMint()
    skipped: list[str] = []

    for dev in ir.devices:
        if dev.kind in (DeviceKind.VSOURCE, DeviceKind.ISOURCE):
            primitives.append(_independent_source(dev))
            continue
        model = registry.get(dev.kind)
        if model is None:
            skipped.append(dev.ref)
            continue
        prims, syms = model.expand(dev, mint, level)
        primitives.extend(prims)
        if syms:
            symbols[dev.ref] = syms

    if skipped:
        logger.warning(
            "small_signal_model: %d device(s) have no registered model and were skipped: %s",
            len(skipped), ", ".join(skipped),
        )

    return SmallSignalIR(
        name=ir.name,
        primitives=tuple(primitives),
        nets=dict(ir.nets),
        ports=dict(ir.ports),
        params=dict(ir.params),
        ground=ir.ground,
        fidelity=level,
        symbols=symbols,
    )
