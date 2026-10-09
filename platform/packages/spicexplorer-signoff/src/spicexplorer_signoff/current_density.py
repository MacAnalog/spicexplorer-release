"""Electromigration budgets: is each net's metal wide enough (and via count high enough) for the
current it carries?

**Nothing else in the signoff chain answers this.** A rule deck checks geometry, and a 0.2 µm wire
is geometrically legal; LVS compares devices and nets, and a 0.2 µm wire is the same net as a
20 µm one; PEX models the wire's *resistance*, which at these lengths is milliohms and moves no
metric. So a cell can pass DRC, LVS, PEX and every bench and still not be manufacturable at its
rated load — the LDO cell of record carried 10 mA on 0.2–0.8 µm Metal1, 12–28× over the limit.

This is arithmetic, not geometry: **no GDS is parsed**. The caller writes down, per net, the
current it carries and the conductor it is drawn on, and gets back the over-factor. The nets that
matter are few (supply, ground, output) and each is one line.

The limits themselves are **configuration, not code**: they live in the shared tech file
(`spicexplorer_core/techs/<pdk>.yaml`, section `em_limits:`) and this module carries only the
arithmetic, so a second process is a second YAML file rather than a second copy of `limit_for`.
Every entry point takes `tech=` (a `Tech`, a builtin PDK name, or a path); `pdk=` is the same
argument under its older name.

IHP SG13G2 limits are transcribed from the PDK's own `SG13G2_os_process_spec.pdf` §2.15
("Maximum Current Densities", 11 years @105 °C, note A.v), which is more specific than the
rule-of-thumb "1 mA/µm on any metal": Metal1 is 1 mA/µm above 0.36 µm and a **flat** 0.36 mA
between 0.16 and 0.36 µm, while Metal2–Metal5 are 2 mA/µm above 0.3 µm and a flat 0.6 mA between
0.2 and 0.3 µm. Below the qualified band there is no number to check against, and this module says
so rather than inventing one.

§2.15 states no qualified width band for TopMetal1/TopMetal2, which would make a per-µm rule
divide-by-anything: 10 mA "fits" in 0.67 µm of TopMetal1 arithmetically, but no such wire can be
drawn. The floor therefore comes from the PDK's own rule deck — TM1.a (1.64 µm,
``klayout/tech/drc/rule_decks/5_22_topmetal1.drc``) and TM2.a (2.00 µm,
``5_25_topmetal2.drc``) — so a width this module scores is a width that can exist.
"""

from __future__ import annotations

import functools
import json
import math
import os
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from spicexplorer_core.tech import Tech

__all__ = [
    "Budget",
    "CurrentDensityResult",
    "CurrentDensityViolation",
    "LayerLimit",
    "limits",
    "budgets_from_brief",
    "check_current_density",
    "limit_for",
    "unqualified_reason",
]


@dataclass(frozen=True)
class LayerLimit:
    """One conductor's electromigration limit.

    A wire carries ``per_um_ma`` mA per µm of drawn width at or above ``wide_um``, and a flat
    ``narrow_ma`` total in the qualified narrow band ``[narrow_um, wide_um)``. A via/contact layer
    instead carries ``per_via_ma`` mA per cut and ignores width.
    """

    name: str
    per_um_ma: float | None = None
    wide_um: float | None = None
    narrow_ma: float | None = None
    narrow_um: float | None = None
    per_via_ma: float | None = None
    cut: str = "via"  # what one cut is called in this layer's rule wording (Contact: "cnt")
    min_width_rule: str = ""  # cited when the floor comes from the rule deck, not the EM spec

    @property
    def is_via(self) -> bool:
        return self.per_via_ma is not None

    @property
    def min_qualified_um(self) -> float | None:
        """Narrowest drawn width this layer has a number for. ``None`` for a via/contact layer."""
        if self.is_via:
            return None
        for v in (self.narrow_um, self.wide_um):
            if v:
                return v
        return None


@functools.lru_cache(maxsize=8)
def _limits(key: str) -> dict[str, LayerLimit]:
    try:
        tech = Tech.resolve(key or None)
    except (ValueError, OSError):
        # An unknown process is a check that CANNOT run, and every caller here already
        # reports that as a failure with a reason. Raising instead would turn a reportable
        # gap into a crash inside a signoff flow.
        return {}
    if not tech.em_limits:
        return {}
    return {
        name.lower(): LayerLimit(
            name=name,
            per_um_ma=e.per_um_ma,
            wide_um=e.wide_um,
            narrow_ma=e.narrow_ma,
            narrow_um=e.narrow_um,
            per_via_ma=e.per_via_ma,
            cut=e.cut,
            min_width_rule=e.min_width_rule,
        )
        for name, e in tech.em_limits.items()
    }


def limits(tech: Tech | str | Path | None = None) -> dict[str, LayerLimit]:
    """The electromigration table of one process, keyed by lower-cased layer name.

    Loaded from the tech config, cached per key. An alias the IHP deck uses for its contact
    layer (``cnt``) is resolved here rather than duplicated in the YAML.
    """
    key = tech.name if isinstance(tech, Tech) else ("" if tech is None else str(tech))
    table = dict(_limits(key))
    if "contact" in table:
        table.setdefault("cnt", table["contact"])
    return table


@dataclass(frozen=True)
class Budget:
    """What one net carries on one conductor: ``current_a`` amps on ``layer``.

    ``width_um`` is the drawn width for a metal layer (ignored for a via/contact layer);
    ``n_vias`` the number of cuts for a via/contact layer (ignored for a metal). ``note`` is free
    text that rides through to the violation — name the place ("vdd rail", "vout pin").
    """

    net: str
    current_a: float
    layer: str
    width_um: float = 0.0
    n_vias: int = 1
    note: str = ""


@dataclass
class CurrentDensityViolation:
    net: str
    layer: str
    current_a: float
    limit_a: float
    over_factor: float  # current / limit; > 1 is a violation
    rule: str  # the limit that was applied, in words
    width_um: float = 0.0
    n_vias: int = 1
    note: str = ""


@dataclass
class CurrentDensityResult:
    """A verdict shaped like the other runners'. Nothing was checked when ``available=False`` (the
    process has no limits table) or when ``skipped=True`` (no budget was given). Neither is a pass:
    ``passed`` is False in both, and ``reason`` says which."""

    passed: bool
    available: bool
    n_violations: int = 0
    n_checked: int = 0
    violations: list[CurrentDensityViolation] = field(default_factory=list)
    worst_over_factor: float = 0.0
    pdk: str = ""
    reason: str = ""  # why unavailable or skipped, or which budgets could not be checked
    skipped: bool = False  # no budget was given: n_checked is 0, and it is not a pass

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _resolve_label(resolved: Tech | str | Path | None) -> str:
    """A human label for ``resolved``, without ever hard-coding a PDK name in this module.

    Goes through the real resolution path (:meth:`Tech.resolve`) so the label always names
    what would actually be used to look up limits — never a placeholder process. When nothing
    resolves (no ``tech=``/``pdk=`` given and ``$PDK`` unset), names the environment variable
    rather than inventing a default PDK.
    """
    if isinstance(resolved, Tech):
        return resolved.name
    try:
        return Tech.resolve(resolved).name
    except (ValueError, OSError):
        if resolved is not None:
            return str(resolved)
        pdk_env = os.environ.get("PDK")
        return f"$PDK={pdk_env!r}" if pdk_env else "$PDK (unset)"


def limit_for(
    layer: str,
    *,
    width_um: float = 0.0,
    n_vias: int = 1,
    pdk: str | None = None,
    tech: Tech | str | Path | None = None,
) -> tuple[float, str] | None:
    """The current limit in **amps** for ``layer`` at this width / via count, and the rule in words.

    ``None`` when the PDK or the layer is unknown, when a metal is drawn narrower than the
    qualified band (the process spec gives no number there — widen it, or ask the foundry), or
    when a via count is below one. The returned limit is always **strictly positive**: a limit of
    zero is not "everything violates it", it is a check that could not run.
    """
    table = limits(tech if tech is not None else pdk)
    if not table:
        return None
    lim = table.get(layer.lower())
    if lim is None:
        return None
    if lim.is_via:
        n = int(n_vias)
        assert lim.per_via_ma is not None
        if n < 1:
            return None
        return lim.per_via_ma * 1e-3 * n, f"{lim.name} {lim.per_via_ma:g} mA/{lim.cut} x {n}"
    if width_um <= 0:
        return None
    if lim.wide_um is not None and lim.per_um_ma is not None and width_um >= lim.wide_um:
        return (
            lim.per_um_ma * 1e-3 * width_um,
            f"{lim.name} {lim.per_um_ma:g} mA/um x {width_um:g} um",
        )
    if lim.narrow_ma is not None and lim.narrow_um is not None and width_um >= lim.narrow_um:
        return (
            lim.narrow_ma * 1e-3,
            f"{lim.name} {lim.narrow_ma:g} mA total ({lim.narrow_um:g}-{lim.wide_um:g} um wide)",
        )
    return None


def unqualified_reason(
    layer: str,
    *,
    width_um: float = 0.0,
    n_vias: int = 1,
    pdk: str | None = None,
    tech: Tech | str | Path | None = None,
) -> str:
    """Why :func:`limit_for` returned ``None`` — in words a designer can act on."""
    resolved = tech if tech is not None else pdk
    label = _resolve_label(resolved)
    table = limits(resolved)
    if not table:
        return f"no `em_limits:` section in the tech config for {label!r}"
    lim = table.get(layer.lower())
    if lim is None:
        return f"unknown layer {layer!r} for {label} — not in the tech config's `em_limits:`"
    if lim.is_via:
        return f"{lim.name}: {n_vias} {lim.cut}(s) carry no current — the count must be at least 1"
    floor = lim.min_qualified_um
    where = f" ({lim.min_width_rule})" if lim.min_width_rule else ""
    if floor is None:
        return f"{lim.name}: no qualified width band in the table"
    return (
        f"{lim.name} drawn {width_um:g} um, under the {floor:g} um minimum qualified "
        f"width{where} — widen it, or ask the foundry for a number"
    )


def check_current_density(
    budgets: Iterable[Budget],
    *,
    pdk: str | None = None,
    tech: Tech | str | Path | None = None,
) -> CurrentDensityResult:
    """Score every budget against the PDK's electromigration limits.

    A budget whose limit cannot be resolved (unknown layer, sub-qualified width) is **not** a pass:
    it lands in ``reason`` and the result fails, because silence from a check that did not run is
    not evidence. An empty ``budgets`` checks nothing: the result is ``skipped=True`` with
    ``passed=False``, ``n_checked=0`` and a reason. A skip is not a pass and not a violation, so
    read ``skipped`` before reading ``passed`` as a failure.
    """
    budgets = list(budgets)
    resolved = tech if tech is not None else pdk
    # Resolve with the REAL (possibly-None) argument, never through a hard-coded PDK name —
    # `_resolve_label` only names the process that `limits()` itself would land on.
    table = limits(resolved)
    if not table:
        label = _resolve_label(resolved)
        return CurrentDensityResult(
            False,
            False,
            pdk=label,
            reason=(
                f"no `em_limits:` section in the tech config for {label!r} — add one to "
                "spicexplorer_core/techs/<pdk>.yaml (from the process spec), or pass tech="
            ),
        )
    label = _resolve_label(resolved)
    if not budgets:
        # L-PF-20: this used to fall through to `passed=True, n_checked=0`
        return CurrentDensityResult(
            passed=False,
            available=True,
            pdk=label,
            reason=(
                "no budget given, so nothing was checked: pass one Budget per net that carries "
                "current (supply, ground, output) on the conductor the layout draws it on"
            ),
            skipped=True,
        )
    viol: list[CurrentDensityViolation] = []
    unchecked: list[str] = []
    for b in budgets:
        # A current that is not a finite number is not a measurement, and the comparison below
        # cannot say anything about it: `abs(nan) > limit` is False, so a NaN used to be scored as
        # a PASS and counted in n_checked — the exact "silence from a check that did not run" this
        # function's docstring rules out. ±Inf failed the other way, becoming a violation whose
        # `over_factor` was inf and which then broke `json.dumps(..., allow_nan=False)`. Both go
        # where every other un-runnable check goes: `unchecked`, which fails the result and is
        # excluded from n_checked. The same applies to the geometry: `width_um=+inf` scaled the
        # limit to infinity, so an arbitrarily large current passed the comparison below.
        bad = next(
            (
                (name, value)
                for name, value in (("current_a", b.current_a), ("width_um", b.width_um))
                if not math.isfinite(value)
            ),
            None,
        )
        if bad is not None:
            unchecked.append(
                f"{b.net}: {bad[0]} is {bad[1]} on {b.layer}, not a finite number — an "
                "electromigration check cannot be run against it. Fix the extraction or the "
                "budget that produced it" + (f" [{b.note}]" if b.note else "")
            )
            continue
        if not b.layer.strip():
            # budgets_from_brief writes one for a brief net `drawn` leaves out; "unknown layer ''"
            # would send the reader to the tech config instead of the layout
            unchecked.append(
                f"{b.net}: not drawn — the budget names no conductor to check "
                f"{b.current_a:g} A against" + (f" [{b.note}]" if b.note else "")
            )
            continue
        got = limit_for(b.layer, width_um=b.width_um, n_vias=b.n_vias, tech=resolved)
        if got is None:
            unchecked.append(
                f"{b.net}: "
                + unqualified_reason(b.layer, width_um=b.width_um, n_vias=b.n_vias, tech=resolved)
                + (f" [{b.note}]" if b.note else "")
            )
            continue
        limit_a, rule = got  # limit_for never returns 0 A, so over_factor is always finite
        if abs(b.current_a) > limit_a:
            viol.append(
                CurrentDensityViolation(
                    net=b.net,
                    layer=b.layer,
                    current_a=b.current_a,
                    limit_a=limit_a,
                    over_factor=abs(b.current_a) / limit_a,
                    rule=rule,
                    width_um=b.width_um,
                    n_vias=b.n_vias,
                    note=b.note,
                )
            )
    reason = ""
    if unchecked:
        reason = "could not be checked -- " + "; ".join(unchecked)
    return CurrentDensityResult(
        passed=not viol and not unchecked,
        available=True,
        n_violations=len(viol),
        n_checked=len(budgets) - len(unchecked),
        violations=viol,
        worst_over_factor=max((v.over_factor for v in viol), default=0.0),
        pdk=label,
        reason=reason,
    )


# ------------------------------------------------------------------ from the layout brief ----

#: One drawn conductor: ``(layer, width_um)`` or ``(layer, width_um, n_vias)``.
Conductor = Sequence[Any]


def _conductors(value: Conductor | Sequence[Conductor]) -> list[Conductor]:
    """One conductor, or a list of them (a strap AND the via stack that feeds it)."""
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence) or not value:
        raise ValueError(f"a drawn conductor is (layer, width_um[, n_vias]), got {value!r}")
    return [value] if isinstance(value[0], str) else list(value)


def budgets_from_brief(
    brief: Mapping[str, Any] | str | Path,
    drawn: Mapping[str, Conductor | Sequence[Conductor]],
) -> list[Budget]:
    """The layout brief's ``currents`` block, on the conductors the layout actually drew.

    ``brief`` is the parsed ``brief.json`` or its path; each row of its ``currents`` list names a
    ``net`` and its current ``i_ma`` (mA). ``drawn`` maps a net to the conductor it is drawn on,
    ``(layer, width_um, n_vias)`` (``n_vias`` defaults to 1), or to a list of them; every conductor
    becomes one :class:`Budget` carrying ``i_ma * 1e-3`` A, for :func:`check_current_density`.

    Nothing drops out silently. A brief net with no ``drawn`` entry becomes a Budget on no layer,
    which :func:`check_current_density` reports as unchecked and fails; a ``drawn`` net the brief
    has no current for raises :class:`KeyError` (a misspelt name would otherwise be ignored); a
    brief with no ``currents`` rows raises :class:`ValueError`, because an empty list of budgets
    checks nothing (:func:`check_current_density` would report it as skipped). A ``currents`` block
    that is not a list of mappings, or an ``i_ma`` that is not a number, raises :class:`TypeError`.
    """
    data: Mapping[str, Any] = (
        brief if isinstance(brief, Mapping) else json.loads(Path(brief).read_text())
    )
    raw = data.get("currents") or []
    if isinstance(raw, (Mapping, str, bytes)) or not isinstance(raw, Sequence):
        raise TypeError(f"the brief's `currents` must be a list of {{net, i_ma}} rows, got {raw!r}")
    rows = list(raw)
    for r in rows:
        if not isinstance(r, Mapping):
            raise TypeError(f"a `currents` row must be a {{net, i_ma}} mapping, got {r!r}")
    if not rows:
        raise ValueError(
            "the brief has no `currents` rows — nothing to check the drawn metal against (a check "
            "with nothing to check is not a pass)"
        )
    unknown = sorted(set(drawn) - {str(r.get("net")) for r in rows})
    if unknown:
        raise KeyError(
            f"drawn nets {unknown} have no row in the brief's `currents` block — nothing to check "
            "them against (a misspelt net name?)"
        )
    out: list[Budget] = []
    for r in rows:
        net, i_ma = str(r["net"]), r["i_ma"]
        if isinstance(i_ma, bool) or not isinstance(i_ma, (int, float)):
            raise TypeError(f"`currents` row {net!r}: `i_ma` must be a number (mA), got {i_ma!r}")
        current_a = float(i_ma) * 1e-3
        kind, what = r.get("kind", ""), r.get("what", "")
        note = ": ".join(str(x) for x in (kind, what) if x)
        if net not in drawn:  # layer '' -> check_current_density reports it as not drawn
            out.append(Budget(net, current_a, "", note=note))
            continue
        for c in _conductors(drawn[net]):
            layer, width_um, *rest = c
            n_vias = int(rest[0]) if rest else 1
            out.append(Budget(net, current_a, str(layer), float(width_um), n_vias, note))
    return out
