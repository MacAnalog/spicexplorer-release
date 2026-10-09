"""Stage-3 artifacts: the assembled MNA system and the exact transfer function it yields."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import sympy as sp

from .ir import PortPair

if TYPE_CHECKING:
    from ..contract import AssumptionApplied, SolvePath, ValidationReport

__all__ = ["MnaSystem", "RawTransferFunction", "SimplifiedTransferFunction"]


@dataclass
class MnaSystem:
    """An assembled small-signal nodal system, ready to solve for any port-pair TF.

    ``Y`` is the ``n×n`` nodal admittance matrix (conductances + capacitor/inductor admittances +
    VCCS contributions) over the ``n`` node-voltage unknowns; ``index`` maps a *net-class
    representative* to its row. Nets shorted together by a DC source (and every AC-ground net) share
    a class; ``rep`` resolves any net name to its representative. ``ground_rep`` is the reference.
    """

    Y: sp.Matrix
    index: dict[str, int]  # net-class representative -> row/col
    _parent: dict[str, str]  # union-find parent map (net name -> parent)
    ground_rep: str
    name: str = "circuit"
    #: the reference net the circuit declares (``SmallSignalIR.ground``). A port on it is the
    #: reference even when no device in the netlist names it (a deck wired on ``0`` whose plan
    #: calls its ground ``vss``).
    ground: str = "0"
    ports: dict[str, PortPair] = field(default_factory=dict)
    params: dict[str, sp.Expr] = field(default_factory=dict)
    free_symbols: frozenset[str] = frozenset()
    #: refs of devices no model could expand, carried from the SSIR so every downstream
    #: result can say the H(s) is missing their branches (Codex review, item TF-02).
    unmodelled: tuple[str, ...] = ()

    def rep(self, net: str) -> str:
        """The net-class representative of ``net`` (path-compressed lookup)."""
        p = self._parent.get(net, net)
        while p != self._parent.get(p, p):
            p = self._parent.get(p, p)
        return p

    def row_of(self, net: str) -> int | None:
        """The matrix row for a net, or ``None`` if it is the reference (AC ground)."""
        r = self.rep(net)
        if r == self.ground_rep:
            return None
        return self.index.get(r)

    @property
    def n(self) -> int:
        return self.Y.shape[0]


@dataclass
class RawTransferFunction:
    """The exact symbolic transfer function between two ports — the Stage-3 output.

    ``expr`` is ``H(s)`` in canonical ``N(s)/D(s)`` form. ``solve_path`` records the regime that
    produced it (``fully_symbolic`` / ``selectively_numericized``) so the result never overstates
    how symbolic it is; ``kept_symbolic`` is the surviving free-symbol set.
    """

    expr: sp.Expr
    s: sp.Symbol
    output: PortPair
    input: PortPair
    name: str = "circuit"
    analysis: str = "transfer_function"
    drive: str = "dm"  # excitation mode at a two-node input pair: "dm" (±½) | "cm" (both +1)
    solve_path: SolvePath = "fully_symbolic"
    numeric_subs: dict[str, float] = field(default_factory=dict)
    #: refs of devices no model could expand (see MnaSystem.unmodelled).
    unmodelled: tuple[str, ...] = ()

    @property
    def kept_symbolic(self) -> tuple[str, ...]:
        return tuple(sorted(str(x) for x in self.expr.free_symbols if x != self.s))

    def __str__(self) -> str:
        return f"H(s) = {self.expr}"


@dataclass
class SimplifiedTransferFunction:
    """A reduced ``H(s)`` plus the audit trail — the Stage-4 output (P5).

    ``expr`` is the simplified TF (== ``exact`` when nothing fired or on the UNREDUCED fallback);
    ``ledger`` is the ordered list of :class:`~spicexplorer_netlist2tf.contract.AssumptionApplied`
    records; ``validation`` is the end-to-end exact-vs-simplified report. ``unreduced`` is set when
    the final gate failed and ``exact`` was returned rather than ship an unvalidated approximation.
    """

    expr: sp.Expr
    exact: sp.Expr
    raw: RawTransferFunction
    ledger: list[AssumptionApplied] = field(default_factory=list)
    validation: ValidationReport | None = None
    unreduced: bool = False
