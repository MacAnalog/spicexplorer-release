"""Stage 3 — symbolic MNA construction + transfer-function extraction.

``build_system`` stamps the small-signal primitives into one nodal admittance matrix; ``extract_tf``
augments it with a unit excitation at the requested input port, solves by Cramer's rule, and returns
the **exact** canonical ``H(s)``. This S1→S3 bridge (typed IR → MNA) is the genuinely-new code; the
stamp table + Cramer/normalize idea is ported from SLiCAP (MIT, attributed in ``NOTICE``), but
re-expressed sympy-native over netlist2tf's own primitives.

Two physical conventions are baked in here (decided once at ingestion, plan §4):

* every **AC-ground** net (the reference + each pure-DC supply) is the matrix reference (V = 0);
* a **DC voltage source** (``ac == 0``) is a 0-Ω AC short — its two nets merge into one node-class.
  An AC-bearing netlist source and every current source are excitations, so they are dropped from
  the homogeneous matrix; the TF excitation is applied at the *named port* instead.
"""

from __future__ import annotations

import logging
from typing import cast

import sympy as sp

from .model.ir import GROUND_NAMES, PortPair
from .model.primitives import (
    VCCS,
    Capacitor,
    Conductance,
    IndependentI,
    IndependentV,
    Inductor,
)
from .model.raw_tf import MnaSystem, RawTransferFunction
from .model.ssir import SmallSignalIR
from .tf import S, canonical_tf, cramer_numerator, determinant

logger = logging.getLogger(__name__)

__all__ = [
    "build_system",
    "detect_ac_input",
    "extract_tf",
    "driving_point_impedance",
    "transimpedance",
    "gain_decomposition",
    "loop_gain_from_system",
    "split_linear_in",
]

PortLike = "str | tuple[str, str] | PortPair"


# ------------------------------------------------------------------------
# Union-find over nets (DC shorts + AC-ground merging)
# ------------------------------------------------------------------------
class _DSU:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def _apply_subs(expr: sp.Expr, subs: dict[str, float]) -> sp.Expr:
    """Substitute numeric values by *name* (assumption-insensitive) for selective numericization."""
    if not subs:
        return expr
    repl: dict[sp.Basic, sp.Basic] = {
        sym: sp.Float(subs[str(sym)]) for sym in expr.free_symbols if str(sym) in subs
    }
    return expr.xreplace(repl) if repl else expr


def _is_ac_ground(ssir: SmallSignalIR, net: str) -> bool:
    n = ssir.nets.get(net)
    if n is not None and n.is_ac_ground:
        return True
    return net == ssir.ground or net.lower() in GROUND_NAMES


def detect_ac_input(ssir: SmallSignalIR) -> tuple[str, str]:
    """The netlist's own AC stimulus as an input port: the unique V source with ``ac != 0``.

    This is the stimulus-overlay base case — a *testbench-level* netlist (``Vin in 0 dc VCM ac 1``)
    names its own input, so the caller doesn't have to. Raises ``ValueError`` when the netlist has
    no AC source, more than one, or only an AC *current* source (drive that port explicitly, or via
    :func:`driving_point_impedance`, instead).
    """
    v_ac = [p for p in ssir.primitives if isinstance(p, IndependentV) and p.ac != 0]
    i_ac = [p for p in ssir.primitives if isinstance(p, IndependentI) and p.ac != 0]
    if len(v_ac) == 1 and not i_ac:
        return (v_ac[0].np, v_ac[0].nn)
    found = ", ".join(p.name for p in (*v_ac, *i_ac)) or "none"
    raise ValueError(
        f"cannot auto-detect the input port: expected exactly one AC voltage source in the "
        f"netlist, found {found}. Pass input=(pos, neg) explicitly."
    )


# ------------------------------------------------------------------------
# Build
# ------------------------------------------------------------------------
def build_system(
    ssir: SmallSignalIR,
    *,
    subs: dict[str, float] | None = None,
    extra_grounds: set[str] | None = None,
    exclude_grounds: set[str] | None = None,
    short_all_sources: bool = False,
) -> MnaSystem:
    """Stamp ``ssir`` into a nodal admittance matrix :class:`MnaSystem`.

    ``subs`` numerically substitutes the named symbols before stamping (selective numericization);
    whatever is omitted stays symbolic. ``extra_grounds`` ties additional nets to the AC reference —
    this is the **source-zeroing** primitive: an open-loop ``Z_out`` grounds the input port so the
    input excitation is set to zero (P7 derived analyses).

    ``exclude_grounds`` is the **net-role override** (the §5b stimulus overlay): the named nets are
    *not* merged into the AC reference even if their role says so, and V-source shorts touching them
    are skipped — this is how PSRR re-promotes a supply rail to a drivable signal input without
    mutating the frozen IR. ``short_all_sources`` zeroes *every* independent V source (``ac`` ones
    included) — the return-ratio convention for ``loop_gain``, where the homogeneous network is
    analyzed with all excitations off.
    """
    subs = subs or {}
    extra = extra_grounds or set()
    excl = exclude_grounds or set()
    dsu = _DSU()

    # All nets a primitive or the SSIR knows about (deterministic order).
    all_nets: set[str] = set(ssir.nets) | set(extra)
    for p in ssir.primitives:
        all_nets.update(p.nets)
    for net in sorted(all_nets):
        dsu.find(net)

    # Merge every AC-ground net (and any caller-zeroed net) into one reference class.
    ground_members = sorted(
        n for n in all_nets if (_is_ac_ground(ssir, n) or n in extra) and n not in excl
    )
    ground_anchor = ground_members[0] if ground_members else ssir.ground
    dsu.find(ground_anchor)
    for g in ground_members:
        dsu.union(ground_anchor, g)

    # DC voltage sources are AC shorts → union their nets (all of them under the return-ratio
    # convention; never the ones touching an excluded/overridden net).
    for p in ssir.primitives:
        if not isinstance(p, IndependentV):
            continue
        if p.np in excl or p.nn in excl:
            continue
        if short_all_sources or _apply_subs(p.ac, subs) == 0:
            dsu.union(p.np, p.nn)

    ground_rep = dsu.find(ground_anchor)

    # Non-ground class representatives become node unknowns (sorted → deterministic indexing).
    reps = sorted({dsu.find(n) for n in all_nets} - {ground_rep})
    index = {rep: i for i, rep in enumerate(reps)}
    n = len(index)
    Y = sp.zeros(n, n)

    def row(net: str) -> int | None:
        r = dsu.find(net)
        return None if r == ground_rep else index[r]

    def stamp_y(a: str, b: str, y: sp.Expr) -> None:
        ia, ib = row(a), row(b)
        if ia is not None:
            Y[ia, ia] += y
        if ib is not None:
            Y[ib, ib] += y
        if ia is not None and ib is not None:
            Y[ia, ib] -= y
            Y[ib, ia] -= y

    for p in ssir.primitives:
        if isinstance(p, (IndependentV, IndependentI)):
            continue  # excitations — not part of the homogeneous matrix
        if isinstance(p, Conductance):
            stamp_y(p.n1, p.n2, _apply_subs(p.value, subs))
        elif isinstance(p, Capacitor):
            stamp_y(p.n1, p.n2, S * _apply_subs(p.value, subs))
        elif isinstance(p, Inductor):
            stamp_y(p.n1, p.n2, 1 / (S * _apply_subs(p.value, subs)))
        elif isinstance(p, VCCS):
            _stamp_vccs(Y, row, p, subs)
        else:
            raise NotImplementedError(
                f"MNA stamp for primitive {type(p).__name__} ({p.name}) is not in R1 "
                "(only VCCS + conductance/capacitor/inductor; controlled-source/nullor stamps land later)"
            )

    free = frozenset(str(x) for x in Y.free_symbols if x != S)
    return MnaSystem(
        Y=Y,
        index=index,
        _parent=dict(dsu.parent),
        ground_rep=ground_rep,
        name=ssir.name,
        ports=dict(ssir.ports),
        params=dict(ssir.params),
        free_symbols=free,
    )


def _stamp_vccs(Y: sp.Matrix, row, p: VCCS, subs: dict[str, float]) -> None:  # noqa: ANN001
    """``value·(V[cp]−V[cn])`` flows from ``np`` into ``nn`` (KCL: leaves np, enters nn)."""
    g = _apply_subs(p.value, subs)
    rnp, rnn, ccp, ccn = row(p.np), row(p.nn), row(p.cp), row(p.cn)
    for r, sign in ((rnp, 1), (rnn, -1)):
        if r is None:
            continue
        if ccp is not None:
            Y[r, ccp] += sign * g
        if ccn is not None:
            Y[r, ccn] -= sign * g


# ------------------------------------------------------------------------
# Extract
# ------------------------------------------------------------------------
def _as_pair(port: object, system: MnaSystem) -> PortPair:
    if isinstance(port, PortPair):
        return port
    if isinstance(port, str):
        if port in system.ports:
            return system.ports[port]
        raise KeyError(f"unknown named port {port!r}; known: {sorted(system.ports)}")
    if isinstance(port, (tuple, list)) and len(port) == 2:
        return PortPair(str(port[0]), str(port[1]))
    raise TypeError(f"port must be a name, (pos, neg) pair, or PortPair; got {port!r}")


def _augment(system: MnaSystem, inp: PortPair, drive: str) -> tuple[sp.Matrix, sp.Matrix]:
    """The augmented (matrix, rhs) with a unit excitation at ``inp`` (one branch per driven node).

    Excitation targets (to ground) so that V[in+] − V[in−] = 1 (dm) or both nodes sit at +1 (cm).
    Driving each non-ground input node to a defined level — rather than one source across the
    pair — is what keeps a differential input of two high-impedance (gate-only) nodes well-posed:
    a single across-the-pair source would fix only their difference and leave the common-mode
    level floating (a singular system).
    """
    n = system.n
    r_ip, r_in = system.row_of(inp.pos), system.row_of(inp.neg)
    if r_ip is None and r_in is None:
        raise ValueError(
            f"input port {(inp.pos, inp.neg)} is entirely at AC ground — nothing to excite"
        )

    if r_ip is not None and r_in is not None:
        if drive == "cm":
            targets = [(r_ip, sp.Integer(1)), (r_in, sp.Integer(1))]
        else:
            targets = [(r_ip, sp.Rational(1, 2)), (r_in, sp.Rational(-1, 2))]
    elif r_in is None:  # single-ended: in− is ground
        targets = [(r_ip, sp.Integer(1))]
    else:  # in+ is ground
        targets = [(r_in, sp.Integer(-1) if drive == "dm" else sp.Integer(1))]

    # Augmented matrix: node unknowns + one source branch per driven input node.
    nb = len(targets)
    A = sp.zeros(n + nb, n + nb)
    A[:n, :n] = system.Y
    rhs = sp.zeros(n + nb, 1)
    for k, (r, value) in enumerate(targets):
        br = n + k
        A[r, br] += 1  # KCL coupling of the branch current
        A[br, r] += 1  # V[node] = value constraint
        rhs[br] = value
    return A, rhs


def extract_tf(
    system: MnaSystem,
    output,  # noqa: ANN001 — PortLike
    input,  # noqa: ANN001 — PortLike
    *,
    analysis: str = "transfer_function",
    drive: str = "dm",
    numeric_subs: dict[str, float] | None = None,
) -> RawTransferFunction:
    """Solve ``system`` for ``H(s) = (V[out+] − V[out−]) / V_drive``.

    A unit voltage excitation is augmented at the input port (a branch current unknown), the system
    is solved by Cramer's rule, and the result is canonicalized. ``output``/``input`` may each be a
    named port, a ``(pos, neg)`` tuple, or a :class:`PortPair` (``neg`` an AC ground ⇒ single-ended).

    ``drive`` selects the excitation mode for a two-node input pair: ``"dm"`` (default) drives
    ``±½`` so ``V[in+] − V[in−] = 1`` (H is the gain from the *differential* input); ``"cm"``
    drives both nodes to ``+1`` (H is the gain from the *common-mode* input — the DM/CM engine's
    second half). For a single-ended input the two modes coincide.
    """
    if drive not in ("dm", "cm"):
        raise ValueError(f"drive must be 'dm' or 'cm', got {drive!r}")
    out = _as_pair(output, system)
    inp = _as_pair(input, system)
    A, rhs = _augment(system, inp, drive)

    detA = determinant(A)
    if detA == 0:
        raise ValueError("MNA system is singular (no unique solution) — check the netlist topology")

    def node_voltage(net: str) -> sp.Expr:
        col = system.row_of(net)
        if col is None:
            return sp.Integer(0)  # an AC-ground node
        return cramer_numerator(A, rhs, col) / detA

    h = canonical_tf(node_voltage(out.pos) - node_voltage(out.neg))
    subs = numeric_subs or {}
    return RawTransferFunction(
        expr=h,
        s=S,
        output=out,
        input=inp,
        name=system.name,
        analysis=analysis,
        drive=drive,
        solve_path="selectively_numericized" if subs else "fully_symbolic",
        numeric_subs=dict(subs),
    )


def split_linear_in(expr: sp.Expr, k: sp.Symbol) -> tuple[sp.Expr, sp.Expr]:
    """Split a polynomial-in-``k`` expression as ``expr = c0 + k·c1`` (Blackman's lemma setup).

    A single VCCS is a rank-one update ``k·u·vᵀ`` to the admittance matrix, so any determinant (or
    Cramer numerator) is **exactly linear** in that one ``k`` — the algebraic fact behind the
    return-ratio decomposition. Raises when ``k`` appears nonlinearly (e.g. a symbol shared by two
    devices after an EQUALITY fold) — pick an unfolded probe instead.
    """
    p = sp.Poly(sp.expand(expr), k)
    if p.degree() > 1:
        raise ValueError(
            f"probe symbol {k} appears nonlinearly (degree {p.degree()}) — is it shared by "
            "several devices (matched-pair fold)? Probe a device with its own unfolded symbol."
        )
    c0 = p.coeff_monomial(1)
    c1 = p.coeff_monomial(k) if p.degree() == 1 else sp.Integer(0)
    return cast("sp.Expr", c0), cast("sp.Expr", c1)


def loop_gain_from_system(
    system: MnaSystem,
    probe_symbol: str,
    *,
    numeric_subs: dict[str, float] | None = None,
) -> RawTransferFunction:
    """Return ratio ``T(s)`` of the controlled source named by ``probe_symbol`` (e.g. ``gm_m1``).

    Blackman / asymptotic-gain decomposition (SLiCAP S4b, ported): the homogeneous determinant is
    linear in the probe's gain ``k`` (rank-one update), ``D(k) = D0 + k·D1``, and the return ratio
    is ``T = k·D1/D0``. Build the system with ``short_all_sources=True`` (return-ratio convention)
    and keep the probe symbol out of ``subs``. ``T`` needs no ports; the probe's branch nets are
    recorded as provenance.
    """
    k = next((x for x in system.Y.free_symbols if str(x) == probe_symbol), None)
    if k is None:
        raise ValueError(
            f"probe symbol {probe_symbol!r} is not in the system "
            f"(numericized via subs, or wrong device ref?); symbolic: {sorted(system.free_symbols)}"
        )
    assert isinstance(k, sp.Symbol)
    detY = determinant(system.Y)
    d0, d1 = split_linear_in(detY, k)
    if d0 == 0:
        raise ValueError(
            "D(k=0) is singular — with the probe device off the network has no unique solution "
            "(is the loop the only thing biasing a node?); loop gain is undefined here"
        )
    t = canonical_tf(cast("sp.Expr", k * d1 / d0))
    subs = numeric_subs or {}
    port = PortPair(probe_symbol, "0")  # provenance only — T is portless
    return RawTransferFunction(
        expr=t, s=S, output=port, input=port, name=system.name, analysis="loop_gain",
        solve_path="selectively_numericized" if subs else "fully_symbolic",
        numeric_subs=dict(subs),
    )


def gain_decomposition(
    system: MnaSystem,
    output,  # noqa: ANN001 — PortLike
    input,  # noqa: ANN001 — PortLike
    probe_symbol: str,
    *,
    drive: str = "dm",
    numeric_subs: dict[str, float] | None = None,
) -> dict[str, RawTransferFunction]:
    """The asymptotic-gain decomposition of one port-pair gain around one controlled source.

    With ``k`` the probe's gain, the augmented solve gives ``H(k) = (N0 + k·N1)/(D0 + k·D1)``
    (both exactly linear in ``k`` — rank-one update), which is identically

        ``H = (A∞·T + ρ) / (1 + T)``,   ``T = k·D1/D0``,  ``A∞ = N1/D1``,  ``ρ = N0/D0``

    — SLiCAP's S4b feedback view: ``T`` the return ratio *as seen from this excitation* (the
    augmented matrix pins the driven input, so independent-source zeroing is built in), ``A∞`` the
    ideal-feedback gain (probe → ∞, e.g. the 1/β of a buffer), ``ρ`` the direct transmission.
    Returns ``{"gain", "loop_gain", "asymptotic_gain", "direct_transmission"}`` as raw TFs.
    """
    out = _as_pair(output, system)
    inp = _as_pair(input, system)
    k = next((x for x in system.Y.free_symbols if str(x) == probe_symbol), None)
    if k is None:
        raise ValueError(
            f"probe symbol {probe_symbol!r} is not in the system "
            f"(numericized via subs, or wrong device ref?); symbolic: {sorted(system.free_symbols)}"
        )
    assert isinstance(k, sp.Symbol)

    A, rhs = _augment(system, inp, drive)
    detA = determinant(A)
    d0, d1 = split_linear_in(detA, k)
    if d0 == 0:
        raise ValueError("D(k=0) is singular — the decomposition is undefined at this probe")
    if d1 == 0:
        raise ValueError(
            f"the determinant does not depend on {probe_symbol} — the probe is outside "
            "every feedback loop seen from this excitation (T would be identically 0)"
        )

    def numerator(net_pos: str, net_neg: str) -> sp.Expr:
        total = sp.Integer(0)
        for net, sign in ((net_pos, 1), (net_neg, -1)):
            col = system.row_of(net)
            if col is not None:
                total += sign * cramer_numerator(A, rhs, col)
        return total

    n_expr = numerator(out.pos, out.neg)
    n0, n1 = split_linear_in(n_expr, k)

    subs = numeric_subs or {}
    solve_path = "selectively_numericized" if subs else "fully_symbolic"

    def raw(expr: sp.Expr, analysis: str) -> RawTransferFunction:
        return RawTransferFunction(
            expr=canonical_tf(expr), s=S, output=out, input=inp, name=system.name,
            analysis=analysis, drive=drive, solve_path=solve_path, numeric_subs=dict(subs),
        )

    return {
        "gain": raw(cast("sp.Expr", n_expr / detA), "transfer_function"),
        "loop_gain": raw(cast("sp.Expr", k * d1 / d0), "loop_gain"),
        "asymptotic_gain": raw(cast("sp.Expr", n1 / d1), "asymptotic_gain"),
        "direct_transmission": raw(cast("sp.Expr", n0 / d0), "direct_transmission"),
    }


def transimpedance(
    system: MnaSystem,
    output,  # noqa: ANN001 — PortLike
    injection,  # noqa: ANN001 — PortLike
    *,
    analysis: str = "transimpedance",
    numeric_subs: dict[str, float] | None = None,
) -> RawTransferFunction:
    """Transimpedance ``Z_T(s) = (V[out+] − V[out−]) / I_inj`` for a unit current forced into ``injection``.

    Same test-current injection as :func:`driving_point_impedance` — a nodal RHS, all independent
    sources off — but read at a *different* port. That one degree of freedom is what makes the
    primitive usable for **noise**: a device's channel-noise generator is a current source across
    two nodes, so ``|Z_T(jω)|² · S_i(f)`` is that generator's contribution to the output PSD, and
    the ratio to the signal ``H(s)`` refers it to the input. It is also the plain answer for any
    current-input block (a TIA's gain, a photodiode front-end).

    ``injection`` is the ``(from, to)`` node pair the current is pushed *into* at ``from`` and
    pulled *out of* at ``to``; an AC-ground member is simply dropped (a single-ended injection).
    """
    out = _as_pair(output, system)
    inj = _as_pair(injection, system)
    r_p, r_n = system.row_of(inj.pos), system.row_of(inj.neg)
    if r_p is None and r_n is None:
        raise ValueError(
            f"injection port {(inj.pos, inj.neg)} is entirely at AC ground — nothing to drive"
        )

    rhs = sp.zeros(system.n, 1)
    if r_p is not None:
        rhs[r_p] += 1
    if r_n is not None:
        rhs[r_n] -= 1

    detA = determinant(system.Y)
    if detA == 0:
        raise ValueError("MNA system is singular (no unique solution) — check the netlist topology")

    def node_voltage(net: str) -> sp.Expr:
        col = system.row_of(net)
        return sp.Integer(0) if col is None else cramer_numerator(system.Y, rhs, col) / detA

    z = canonical_tf(node_voltage(out.pos) - node_voltage(out.neg))
    subs = numeric_subs or {}
    return RawTransferFunction(
        expr=z, s=S, output=out, input=inj, name=system.name, analysis=analysis,
        solve_path="selectively_numericized" if subs else "fully_symbolic",
        numeric_subs=dict(subs),
    )


def driving_point_impedance(
    system: MnaSystem,
    port,  # noqa: ANN001 — PortLike
    *,
    analysis: str = "input_impedance",
    numeric_subs: dict[str, float] | None = None,
) -> RawTransferFunction:
    """Driving-point impedance ``Z(s) = V_x / I_x`` at ``port`` (the test-source-injection primitive).

    A **unit test current** is injected into the port (a nodal RHS — no extra branch) with all
    independent sources off (already the case in the homogeneous matrix); the resulting port voltage
    *is* the impedance. For an open-loop ``Z_out`` the caller grounds the input port via
    ``build_system(extra_grounds=...)`` first (source-zeroing). A port with no admittance path (an
    ideal MOS gate at SOME_PARASITIC) is infinite impedance → a clean, explicit error.
    """
    p = _as_pair(port, system)
    rp, rn = system.row_of(p.pos), system.row_of(p.neg)
    if rp is None and rn is None:
        raise ValueError(f"port {(p.pos, p.neg)} is entirely at AC ground — impedance is 0")

    rhs = sp.zeros(system.n, 1)
    if rp is not None:
        rhs[rp] += 1
    if rn is not None:
        rhs[rn] -= 1

    detA = determinant(system.Y)
    if detA == 0:
        raise ValueError(
            "driving-point impedance is singular/infinite at this port (a high-impedance node with "
            "no admittance path — e.g. an ideal MOS gate at SOME_PARASITIC; raise the model fidelity "
            "to include gate caps, or ground the opposite port for an open-loop measurement)"
        )

    def node_voltage(net: str) -> sp.Expr:
        col = system.row_of(net)
        return sp.Integer(0) if col is None else cramer_numerator(system.Y, rhs, col) / detA

    z = canonical_tf(node_voltage(p.pos) - node_voltage(p.neg))
    subs = numeric_subs or {}
    return RawTransferFunction(
        expr=z, s=S, output=p, input=p, name=system.name, analysis=analysis,
        solve_path="selectively_numericized" if subs else "fully_symbolic",
        numeric_subs=dict(subs),
    )
