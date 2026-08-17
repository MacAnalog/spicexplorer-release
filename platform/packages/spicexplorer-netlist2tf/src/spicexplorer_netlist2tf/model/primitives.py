"""Small-signal primitives — the closed set the MNA builder (P3) knows how to stamp.

A device's small-signal model is **data**: its ``expand`` (P2, ``models.py``) returns only these
primitives, never new matrix math. So a third-party device family can never break the solver — it
can only emit conductances, capacitors, inductors, controlled sources, and nullors that the stamp
table already handles (the design is ported from SLiCAP's stampable-core idea — see ``NOTICE``).

Each primitive is a frozen value type carrying nets (string names) + a sympy ``Expr`` value, so a
list of primitives is hashable/orderable and a small-signal IR is byte-identical for a given netlist.

Sign/orientation conventions (consumed by the P3 stamps):

* :class:`Conductance` / :class:`Capacitor` / :class:`Inductor` — a two-terminal admittance between
  ``n1`` and ``n2`` (order irrelevant).
* :class:`VCCS` — a current ``value · (V[cp] − V[cn])`` flowing **from ``np`` into ``nn``** (a
  ``g``-parameter transconductance: ``Gm d s g s {gm}`` ⇒ ``VCCS(np=d, nn=s, cp=g, cn=s, gm)``).
* :class:`VCVS`/:class:`CCCS`/:class:`CCVS`/:class:`Nullor` — provided for completeness and the
  post-R1 nullor-based analyses; the MOSFET hybrid-pi expansion (P2) needs only VCCS + caps + ro.
* :class:`IndependentV`/:class:`IndependentI` — the excitation/bias sources carried through from the
  netlist; the MNA stage decides DC-short vs AC-drive.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

__all__ = [
    "Primitive",
    "Conductance",
    "Capacitor",
    "Inductor",
    "VCCS",
    "VCVS",
    "CCCS",
    "CCVS",
    "Nullor",
    "IndependentV",
    "IndependentI",
]


@dataclass(frozen=True)
class Primitive:
    """Base small-signal primitive — identified by its (unique, per-instance) ``name``."""

    name: str

    @property
    def nets(self) -> tuple[str, ...]:
        """The nets this primitive touches (overridden per concrete type)."""
        return ()


# ------------------------------------------------------------------------
# Two-terminal admittances
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class Conductance(Primitive):
    """A conductance ``value`` (siemens) between ``n1`` and ``n2``. A resistor is ``1/R``; a
    MOSFET output conductance is ``1/ro``."""

    n1: str = ""
    n2: str = ""
    value: sp.Expr = sp.Integer(0)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.n1, self.n2)


@dataclass(frozen=True)
class Capacitor(Primitive):
    """A capacitance ``value`` (farads) between ``n1`` and ``n2`` (admittance ``s·value``)."""

    n1: str = ""
    n2: str = ""
    value: sp.Expr = sp.Integer(0)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.n1, self.n2)


@dataclass(frozen=True)
class Inductor(Primitive):
    """An inductance ``value`` (henries) between ``n1`` and ``n2`` (impedance ``s·value``)."""

    n1: str = ""
    n2: str = ""
    value: sp.Expr = sp.Integer(0)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.n1, self.n2)


# ------------------------------------------------------------------------
# Controlled sources
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class VCCS(Primitive):
    """Voltage-controlled current source: ``value·(V[cp]−V[cn])`` flows from ``np`` into ``nn``."""

    np: str = ""
    nn: str = ""
    cp: str = ""
    cn: str = ""
    value: sp.Expr = sp.Integer(0)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.np, self.nn, self.cp, self.cn)


@dataclass(frozen=True)
class VCVS(Primitive):
    """Voltage-controlled voltage source: ``V[np]−V[nn] = value·(V[cp]−V[cn])`` (adds a branch)."""

    np: str = ""
    nn: str = ""
    cp: str = ""
    cn: str = ""
    value: sp.Expr = sp.Integer(1)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.np, self.nn, self.cp, self.cn)


@dataclass(frozen=True)
class CCCS(Primitive):
    """Current-controlled current source: output current ``value·I[ctrl_branch]``."""

    np: str = ""
    nn: str = ""
    ctrl: str = ""  # name of the branch whose current controls this source
    value: sp.Expr = sp.Integer(1)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.np, self.nn)


@dataclass(frozen=True)
class CCVS(Primitive):
    """Current-controlled voltage source: ``V[np]−V[nn] = value·I[ctrl_branch]`` (adds a branch)."""

    np: str = ""
    nn: str = ""
    ctrl: str = ""
    value: sp.Expr = sp.Integer(1)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.np, self.nn)


@dataclass(frozen=True)
class Nullor(Primitive):
    """An ideal nullor (nullator ``ip``/``in`` + norator ``op``/``on``) — the ideal-gain primitive
    used by the post-R1 asymptotic-gain / feedback analyses."""

    ip: str = ""
    in_: str = ""
    op: str = ""
    on: str = ""

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.ip, self.in_, self.op, self.on)


# ------------------------------------------------------------------------
# Independent sources (carried through; MNA decides DC-short vs AC-drive)
# ------------------------------------------------------------------------
@dataclass(frozen=True)
class IndependentV(Primitive):
    """An independent voltage source (``np``→``nn``) carrying its DC and AC magnitudes."""

    np: str = ""
    nn: str = ""
    dc: sp.Expr = sp.Integer(0)
    ac: sp.Expr = sp.Integer(0)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.np, self.nn)


@dataclass(frozen=True)
class IndependentI(Primitive):
    """An independent current source (current ``dc``/``ac`` flowing ``np``→``nn``)."""

    np: str = ""
    nn: str = ""
    dc: sp.Expr = sp.Integer(0)
    ac: sp.Expr = sp.Integer(0)

    @property
    def nets(self) -> tuple[str, ...]:
        return (self.np, self.nn)
