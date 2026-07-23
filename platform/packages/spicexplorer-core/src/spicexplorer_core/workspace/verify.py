"""The verification plan — the spec × test × corner joining table.

``verify/plan.yaml`` binds each spec id to HOW it is verified (which testbench,
which Tier-1 measurement, over which corners × temperatures) and how that matrix
collapses to one pass/fail (``aggregate``). Target VALUES stay canonical in
``spec/targets.yaml`` (jobs reference spec ids, never copy values) — a plan
entry MAY echo an inline ``target:`` but the loader treats
``targets.yaml`` as the source of truth and only falls back to the inline value.

``verify/plan.yaml``::

    specs:
      psrr_db:
        target: ">= 60"        # optional echo; canonical value is spec/targets.yaml
        test: tb_psrr          # testbenches/<tb_id>
        measurement: psrr      # a Tier-1 registry name
        corners: [tt, ss, ff]  # generic labels → resolved per the cell's PDK binding
        temps: [-40, 27, 125]
        aggregate: min         # worst-case-over-matrix

Every run records its matrix ``coordinates``, so "is PSRR met
across corners?" is a query over run history (see :mod:`spicexplorer_core.workspace.state`).
This module is pure data + FS I/O — it never runs a simulation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from spicexplorer_core.eng import parse_value

AGGREGATES = ("min", "max", "mean")
_TARGET_RE = re.compile(r"^\s*(>=|<=|==|=|>|<)\s*(\S+)\s*$")
_OPS = {
    ">=": lambda m, t: m >= t,
    "<=": lambda m, t: m <= t,
    ">": lambda m, t: m > t,
    "<": lambda m, t: m < t,
    "==": lambda m, t: m == t,
    "=": lambda m, t: m == t,
}


@dataclass(frozen=True)
class Target:
    """A parsed comparison like ``>= 60`` — the pass predicate for one spec."""
    op: str
    value: float
    raw: str

    def satisfies(self, measured: float) -> bool:
        return _OPS[self.op](measured, self.value)


def parse_target(raw: str) -> Target:
    """``">= 60"`` / ``"<= 1.8u"`` / ``"== 1.2"`` → a :class:`Target`. The operator is
    REQUIRED (a bare number is ambiguous between a floor and a ceiling); the value goes
    through ``eng.parse_value`` so engineering strings work."""
    m = _TARGET_RE.match(str(raw))
    if not m:
        raise ValueError(f"target {raw!r} must be '<op> <value>' (op ∈ >= <= > < ==)")
    op, val = m.group(1), m.group(2)
    return Target(op=op, value=float(parse_value(val)), raw=str(raw).strip())


@dataclass(frozen=True)
class Spec:
    """One verifiable spec: what to measure, on which test, over which matrix."""
    id: str
    measurement: str
    aggregate: str
    corners: tuple[str, ...]
    temps: tuple[float, ...]
    test: str | None = None
    target: Target | None = None

    def coordinates(self) -> list[dict[str, Any]]:
        """The full (test × corner × temp) point set this spec must be evaluated at —
        the coordinates a run records."""
        return [
            {"spec": self.id, "test": self.test, "corner": c, "temp": t}
            for c in self.corners
            for t in self.temps
        ]

    def aggregate_value(self, values: list[float]) -> float | None:
        """Collapse the matrix's measured values to one number per ``aggregate``."""
        vals = [v for v in values if v is not None]
        if not vals:
            return None
        if self.aggregate == "min":
            return min(vals)
        if self.aggregate == "max":
            return max(vals)
        return sum(vals) / len(vals)  # mean

    def passes(self, values: list[float]) -> bool | None:
        """Does the aggregated matrix meet the target? ``None`` when no target is bound
        or nothing was measured."""
        if self.target is None:
            return None
        agg = self.aggregate_value(values)
        return None if agg is None else self.target.satisfies(agg)


@dataclass(frozen=True)
class VerifyPlan:
    specs: dict[str, Spec]

    def matrix(self) -> list[dict[str, Any]]:
        """Every (spec × test × corner × temp) coordinate the plan demands."""
        return [pt for spec in self.specs.values() for pt in spec.coordinates()]


def load_targets(project_dir: Path) -> dict[str, str]:
    """``spec/targets.yaml`` → ``{spec_id: raw_target_string}`` — the canonical target
    values. Each value is a string (``">= 60"``) or a mapping with a ``target``
    key. Missing file → ``{}``."""
    p = project_dir / "spec" / "targets.yaml"
    if not p.is_file():
        return {}
    data = yaml.safe_load(p.read_text()) or {}
    specs = data.get("specs", data) if isinstance(data, dict) else {}
    out: dict[str, str] = {}
    for sid, val in (specs or {}).items():
        if isinstance(val, dict) and "target" in val:
            out[str(sid)] = str(val["target"])
        elif isinstance(val, (str, int, float)):
            out[str(sid)] = str(val)
    return out


def load_verify_plan(project_dir: Path) -> VerifyPlan | None:
    """Parse ``verify/plan.yaml`` into a :class:`VerifyPlan`, resolving each spec's
    target from ``spec/targets.yaml`` (canonical) and falling back to an inline
    ``target:``. Returns ``None`` when the project has no plan; raises ``ValueError``
    on a malformed entry (fail loud, don't silently drop a spec)."""
    p = project_dir / "verify" / "plan.yaml"
    if not p.is_file():
        return None
    data = yaml.safe_load(p.read_text()) or {}
    raw_specs = data.get("specs") if isinstance(data, dict) else None
    if not isinstance(raw_specs, dict):
        raise ValueError("verify/plan.yaml must have a top-level 'specs:' mapping")

    canonical = load_targets(project_dir)
    specs: dict[str, Spec] = {}
    for sid, body in raw_specs.items():
        if not isinstance(body, dict):
            raise ValueError(f"spec {sid!r} must be a mapping")
        measurement = body.get("measurement")
        if not measurement:
            raise ValueError(f"spec {sid!r} needs a 'measurement'")
        aggregate = str(body.get("aggregate", "min"))
        if aggregate not in AGGREGATES:
            raise ValueError(f"spec {sid!r} aggregate {aggregate!r} not in {AGGREGATES}")
        corners = tuple(str(c) for c in (body.get("corners") or []))
        if not corners:
            raise ValueError(f"spec {sid!r} needs at least one corner")
        temps = tuple(float(t) for t in (body.get("temps") or [27]))
        raw_target = canonical.get(str(sid), body.get("target"))
        target = parse_target(raw_target) if raw_target is not None else None
        specs[str(sid)] = Spec(
            id=str(sid), measurement=str(measurement), aggregate=aggregate,
            corners=corners, temps=temps, test=body.get("test"), target=target,
        )
    return VerifyPlan(specs=specs)
