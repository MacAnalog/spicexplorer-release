"""The small-signal IR (Stage-2 artifact) — the linearized circuit, ready for MNA stamping (P3).

``small_signal_model(ir, level)`` (``models.py``) produces this: every device replaced by the
primitives its small-signal model emits, plus the independent sources carried through, plus a
per-device map of the symbols introduced (``gm_m1``, ``ro_m1``, …) so later stages can find them
without re-deriving. Nets/ports/ground are carried from the :class:`Circuit2TF` unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import sympy as sp

from .ir import Fidelity, Net, PortPair
from .primitives import Primitive

__all__ = ["SmallSignalIR"]


@dataclass
class SmallSignalIR:
    """A linearized circuit: stampable primitives + introduced-symbol bookkeeping."""

    name: str
    primitives: tuple[Primitive, ...]
    nets: dict[str, Net] = field(default_factory=dict)
    ports: dict[str, PortPair] = field(default_factory=dict)
    params: dict[str, sp.Expr] = field(default_factory=dict)
    ground: str = "0"
    fidelity: Fidelity = Fidelity.SOME_PARASITIC
    #: per-device-ref → {role: sympy Symbol} for the small-signal symbols the model introduced.
    symbols: dict[str, dict[str, sp.Symbol]] = field(default_factory=dict)
    #: refs of devices no registered model could expand — they contribute NOTHING to the MNA,
    #: so every downstream H(s) is missing their branches. Stage 2 also logs a warning, but a
    #: log line is easy to lose in a busy run: assert on this instead.
    unmodelled: tuple[str, ...] = ()

    @property
    def introduced_symbols(self) -> frozenset[str]:
        """Every small-signal symbol name introduced by Stage 2 (``gm_m1``, ``ro_m1``, …)."""
        return frozenset(str(s) for m in self.symbols.values() for s in m.values())

    def primitives_of(self, ref: str) -> tuple[Primitive, ...]:
        """The primitives that came from one device (matched by the ``<type>_<ref>`` name prefix)."""
        return tuple(p for p in self.primitives if p.name.endswith(f"@{ref}"))
