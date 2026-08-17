"""The typed ``Assumption`` object + the declaration library (Tier A factories, Tier B bundles).

The atom of the differentiator (plan §6): a declarable, serializable assumption whose **kind** — not a
free-form sympy relation — fixes how it maps to a rewrite and where it sits in the deterministic phase
order. Typing the kind separately from the content is the whole point; conflating them into a raw
``Eq``/``Lt`` is exactly what makes lcapy's and SLiCAP's facilities un-auditable.

Five kinds cover the physics:

* ``DOMINANCE``       — "A ≫ B": within a sum, drop the term(s) dominated by a named quantity.
* ``SMALLNESS``       — "X → 0": a quantity is negligible everywhere it appears.
* ``POLE_SEPARATION`` — "p1 ≪ p2": dominant-pole collapse / factoring of the denominator.
* ``BAND_LIMIT``      — "|s·k| ≪ 1 over the band": frequency-scoped smallness on an s-bearing product.
* ``EQUALITY``        — "gm_m1 = gm_m2": matched-device / mirror symmetry; a lossless symbol collapse.

An :class:`Assumption` is serializable (``payload`` is sympy-parseable strings/numbers), so an agent
passes them as JSON and a designer builds the same objects via the Tier-A factories.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import _label

__all__ = [
    "Assumption",
    "DOMINANCE",
    "SMALLNESS",
    "POLE_SEPARATION",
    "BAND_LIMIT",
    "EQUALITY",
    "KINDS",
    # Tier A factories
    "intrinsic_gain_large",
    "transconductance_dominates",
    "neglect_cap",
    "neglect_cgd",
    "neglect_overlap_caps",
    "matched_pair",
    "dominant_pole",
    "inband",
    # Tier B bundles
    "BUNDLES",
    "resolve",
]

DOMINANCE = "DOMINANCE"
SMALLNESS = "SMALLNESS"
POLE_SEPARATION = "POLE_SEPARATION"
BAND_LIMIT = "BAND_LIMIT"
EQUALITY = "EQUALITY"
KINDS = frozenset({DOMINANCE, SMALLNESS, POLE_SEPARATION, BAND_LIMIT, EQUALITY})

#: ordering class per kind for the deterministic phase pipeline (lower runs first).
PHASE = {EQUALITY: 0, SMALLNESS: 1, DOMINANCE: 2, BAND_LIMIT: 3, POLE_SEPARATION: 4}


@dataclass(frozen=True)
class Assumption:
    """A typed, serializable simplification assumption.

    ``payload`` is kind-specific and holds sympy-parseable strings / numbers:

    * ``DOMINANCE``       — ``{"dominant": "<expr>"}`` (the quantity that dominates its sum);
    * ``SMALLNESS``       — ``{"symbol": "<name>"}`` (the quantity sent to 0);
    * ``EQUALITY``        — ``{"a": "<keep>", "b": "<replace>"}`` (replace device-``b`` symbols by ``a``'s);
    * ``BAND_LIMIT``      — ``{"f_hi": <hz>}``;
    * ``POLE_SEPARATION`` — ``{}``.
    """

    id: str
    kind: str
    payload: dict = field(default_factory=dict)
    scope: str = "GLOBAL"
    justification: str = ""

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ValueError(f"unknown assumption kind {self.kind!r}; one of {sorted(KINDS)}")

    @property
    def phase(self) -> int:
        return PHASE[self.kind]


# ------------------------------------------------------------------------
# Tier A — named canonical factories (parameterized by device/symbol)
# ------------------------------------------------------------------------
def intrinsic_gain_large(dev: str) -> Assumption:
    """``gm·ro ≫ 1`` for ``dev`` (DOMINANCE): drop the additive ``1`` next to ``gm·ro``."""
    lb = _label(dev)
    return Assumption(
        id=f"gm_ro_large:{dev}", kind=DOMINANCE,
        payload={"dominant": f"gm_{lb}*ro_{lb}"}, scope="DEVICE",
        justification="intrinsic gain gm·ro >> 1 (strong inversion)",
    )


def transconductance_dominates(dev: str) -> Assumption:
    """``gm ≫ go`` for ``dev`` (DOMINANCE): in any sum with ``gm``, drop the conductance terms."""
    lb = _label(dev)
    return Assumption(
        id=f"gm_dominates:{dev}", kind=DOMINANCE,
        payload={"dominant": f"gm_{lb}"}, scope="DEVICE",
        justification="transconductance dominates output conductance (gm >> gds)",
    )


def neglect_cap(dev: str, role: str) -> Assumption:
    """Neglect one capacitance of ``dev`` (SMALLNESS), e.g. ``role='cgd'`` → ``cgd_<dev> → 0``."""
    lb = _label(dev)
    return Assumption(
        id=f"neglect_{role}:{dev}", kind=SMALLNESS,
        payload={"symbol": f"{role}_{lb}"}, scope="DEVICE",
        justification=f"{role} negligible in band",
    )


def neglect_cgd(dev: str) -> Assumption:
    """Neglect the gate-drain (Miller) overlap cap of ``dev`` (removes the feedforward zero)."""
    return neglect_cap(dev, "cgd")


def neglect_overlap_caps(dev: str) -> list[Assumption]:
    """Neglect both overlap caps (``cgd``, ``cgs``) of ``dev``."""
    return [neglect_cap(dev, "cgd"), neglect_cap(dev, "cgs")]


def matched_pair(keep: str, replace: str) -> Assumption:
    """Matched devices (EQUALITY): replace every ``replace``-device symbol by ``keep``'s (lossless)."""
    return Assumption(
        id=f"matched:{keep}={replace}", kind=EQUALITY,
        payload={"a": _label(keep), "b": _label(replace)}, scope="DEVICE",
        justification="matched pair / current-mirror symmetry",
    )


def dominant_pole() -> Assumption:
    """Dominant-pole collapse (POLE_SEPARATION) on the denominator."""
    return Assumption(id="dominant_pole", kind=POLE_SEPARATION, payload={}, scope="GLOBAL",
                      justification="widely separated poles p1 << p2")


def inband(f_hi: float) -> Assumption:
    """Band-limit (BAND_LIMIT): drop ``s``-terms negligible up to ``f_hi`` Hz."""
    return Assumption(id=f"inband:{f_hi:g}", kind=BAND_LIMIT, payload={"f_hi": float(f_hi)},
                      scope="BAND", justification=f"in-band approximation up to {f_hi:g} Hz")


# ------------------------------------------------------------------------
# Tier B — bundles (resolved against the symbols present in an expression)
# ------------------------------------------------------------------------
def _device_labels(symbol_names: set[str]) -> set[str]:
    """Device labels appearing as ``gm_<lbl>`` (the input-transconductance marker)."""
    return {n[len("gm_"):] for n in symbol_names if n.startswith("gm_")}


def _bundle_low_freq(symbols: set[str]) -> list[Assumption]:
    out: list[Assumption] = []
    for lb in sorted(_device_labels(symbols)):
        out.append(transconductance_dominates(lb))
    return out


def _bundle_ideal(symbols: set[str]) -> list[Assumption]:
    out = _bundle_low_freq(symbols)
    for lb in sorted(_device_labels(symbols)):
        out.append(intrinsic_gain_large(lb))
    return out


#: bundle name -> resolver(symbol_names) -> [Assumption]. ``"full"`` = nothing dropped (safe default).
BUNDLES = {
    "full": lambda symbols: [],
    "low_freq": _bundle_low_freq,
    "ideal": _bundle_ideal,
    "dominant_pole": lambda symbols: [*_bundle_low_freq(symbols), dominant_pole()],
}


def resolve(
    spec: str | Assumption | list, symbol_names: set[str]
) -> list[Assumption]:
    """Resolve a bundle name, a single :class:`Assumption`, or a list thereof into assumptions."""
    if isinstance(spec, str):
        if spec not in BUNDLES:
            raise ValueError(f"unknown bundle {spec!r}; one of {sorted(BUNDLES)}")
        return BUNDLES[spec](symbol_names)
    if isinstance(spec, Assumption):
        return [spec]
    out: list[Assumption] = []
    for item in spec:
        out.extend(resolve(item, symbol_names))
    return out
