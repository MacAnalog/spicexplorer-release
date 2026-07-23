"""DUT-parameterization resolution — the ``spicexplorer/params@1`` contract, platform side.

Analog-db ships a
per-circuit ``abstract/params.yaml`` separating *what CAN vary* (``devices:`` — the atomic
per-instance inventory) from *what SHOULD vary together* (``groups:``/``ratios:`` — shipped
default tying, tagged with machine-readable ``kind`` reasons). This module is the platform's
**engine-neutral** consumer of that contract:

* :func:`load_params_file` — parse + validate a ``params.yaml`` into :class:`CircuitParams`
  (the convenience ``analog_db.load_circuit_params(circuit)`` returns ``None`` when a circuit
  simply hasn't adopted the contract yet).
* :func:`resolve_knob` — a ``dut_params`` name may be an **atomic symbol** (returned
  unchanged), ``<group>.<field>`` (→ the group's **FIRST member's** atomic symbol for that
  field — the free knob under the tie lowering, where every tie line references the first
  member), or a bare **group name** when the group ties exactly one field.
* :func:`shadow_params` — the ``ungroup:`` semantics. *Untying = shadowing*: a
  tie is just ``.param x_dut_xm4_l = {x_dut_xm3_l}`` in the lowered deck, so dissolving it
  means re-defining every **non-first** member-field symbol at its *current resolved default*
  (an explicit ``.param x_dut_xm4_l = 5u``), which makes those symbols independently
  addressable — they may then appear as their own ``dut_params``. Selector shapes::

      ungroup:
        - nmos_mirror_l        # one group, by name
        - kind:mirror_length   # every group of a kind (dissolve ties by category)
        - ratio:XM7            # the ratios: entry whose ref (derived instance) is XM7

  A dissolved ``ratios:`` entry shadows the *derived* instance's symbol at its computed
  default (``param(of) × ratio``).
* :func:`netlist_param_defaults` — reads the ``.param`` header of a lowered deck (the
  committed ``raw/`` decks inline it), the source of the "current resolved default" values.

The projection wiring lives in ``Project_Setup.from_yaml`` (``core/domains.py``): optional
``params_file:`` + ``ungroup:`` keys resolve ``dut_params`` names and append **frozen**
shadow ``dut_params`` — which ride the optimizer's existing verbatim ``.param`` rewrite
(``NevergradMixin.parameterize`` injects a frozen param's ``val`` into every candidate), so
the optimizer core needs **zero changes** and both engine lanes get the same treatment
through the ``Simulator`` protocol. Absent keys → exactly the legacy behavior.

DEFAULT POSTURE: shipped projections stay low-dimensional (~5-8 curated knobs) —
atomic granularity is *availability*, not the default search space.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml
from spicexplorer_core.eng import parse_value

__all__ = [
    "ParamsError",
    "ParamGroup",
    "ParamRatio",
    "CircuitParams",
    "load_params_file",
    "resolve_knob",
    "select_ungroup",
    "shadow_params",
    "netlist_param_defaults",
]

PARAMS_SCHEMA = "spicexplorer/params@1"


class ParamsError(ValueError):
    """A params.yaml contract violation, or an unresolvable knob / ungroup selector."""


@dataclass(frozen=True)
class ParamGroup:
    """One shipped default tie: ``tie`` fields shared across ``members`` (first = tie target)."""

    name: str
    kind: str
    members: tuple[str, ...]
    tie: tuple[str, ...]
    description: str | None = None


@dataclass(frozen=True)
class ParamRatio:
    """One mirror gain as data: ``param(ref) = param(of) × ratio`` (ref = derived instance)."""

    param: str
    ref: str
    of: str
    ratio: str | float
    is_integer: bool = False
    description: str | None = None

    def value(self) -> float:
        """The ratio as a float — an exact-fraction string (``"17/3"``) or a plain number."""
        if isinstance(self.ratio, str):
            try:
                return float(Fraction(self.ratio.strip()))
            except (ValueError, ZeroDivisionError) as exc:
                raise ParamsError(
                    f"ratio {self.ref}←{self.of}: unparsable ratio {self.ratio!r} "
                    f"(expected a fraction like '17/3' or a number)"
                ) from exc
        return float(self.ratio)


@dataclass(frozen=True)
class CircuitParams:
    """A parsed ``abstract/params.yaml`` (``spicexplorer/params@1``).

    ``devices`` maps instance id → {field → atomic symbol *or* frozen numeric literal};
    ``groups``/``ratios`` are the shipped default tying.
    """

    devices: dict[str, dict[str, str | float]]
    groups: tuple[ParamGroup, ...] = ()
    ratios: tuple[ParamRatio, ...] = ()
    source: Path | None = field(default=None, compare=False)

    def group(self, name: str) -> ParamGroup:
        for g in self.groups:
            if g.name == name:
                return g
        raise ParamsError(
            f"unknown group {name!r}; available groups: {sorted(g.name for g in self.groups)}"
        )

    def groups_of_kind(self, kind: str) -> tuple[ParamGroup, ...]:
        return tuple(g for g in self.groups if g.kind == kind)

    def symbol(self, instance: str, field_name: str) -> str:
        """The atomic symbol for one instance-field; loud on a missing row or a frozen literal."""
        try:
            row = self.devices[instance]
        except KeyError:
            raise ParamsError(
                f"instance {instance!r} is not in the devices: inventory "
                f"(have {sorted(self.devices)})"
            ) from None
        if field_name not in row:
            raise ParamsError(
                f"instance {instance!r} has no field {field_name!r} in the devices: "
                f"inventory (has {sorted(row)})"
            )
        sym = row[field_name]
        if not isinstance(sym, str):
            raise ParamsError(
                f"{instance}.{field_name} is a frozen numeric literal ({sym!r}) in the "
                f"inventory — it has no atomic symbol to address"
            )
        return sym


def load_params_file(path: str | Path) -> CircuitParams:
    """Parse + validate a ``spicexplorer/params@1`` file into :class:`CircuitParams`.

    Raises :class:`ParamsError` on a missing file or any contract violation (wrong schema
    tag, empty inventory, group members / ratio instances absent from ``devices:``, tie
    fields a member doesn't carry). Callers that treat absence as "contract not adopted
    yet" should check existence first (see ``analog_db.load_circuit_params``).
    """
    p = Path(path)
    if not p.is_file():
        raise ParamsError(f"params file not found: {p}")
    with p.open() as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ParamsError(f"malformed params file (not a mapping): {p}")
    if data.get("schema") != PARAMS_SCHEMA:
        raise ParamsError(
            f"{p}: schema is {data.get('schema')!r}, expected {PARAMS_SCHEMA!r}"
        )
    devices_raw = data.get("devices")
    if not isinstance(devices_raw, dict) or not devices_raw:
        raise ParamsError(f"{p}: devices: must be a non-empty mapping (the atomic inventory)")
    devices: dict[str, dict[str, str | float]] = {}
    for inst, row in devices_raw.items():
        if not isinstance(row, dict) or not row:
            raise ParamsError(f"{p}: devices.{inst} must be a non-empty {{field: symbol}} mapping")
        devices[str(inst)] = {str(k): v for k, v in row.items()}

    groups: list[ParamGroup] = []
    for i, g in enumerate(data.get("groups") or []):
        try:
            group = ParamGroup(
                name=str(g["name"]),
                kind=str(g["kind"]),
                members=tuple(str(m) for m in g["members"]),
                tie=tuple(str(t) for t in g["tie"]),
                description=g.get("description"),
            )
        except (KeyError, TypeError) as exc:
            raise ParamsError(f"{p}: groups[{i}] is malformed (needs name/kind/members/tie): {exc}") from exc
        if len(group.members) < 2:
            raise ParamsError(f"{p}: group {group.name!r} needs at least 2 members")
        for member in group.members:
            if member not in devices:
                raise ParamsError(
                    f"{p}: group {group.name!r} member {member!r} is not in the devices: inventory"
                )
            for tie_field in group.tie:
                if tie_field not in devices[member]:
                    raise ParamsError(
                        f"{p}: group {group.name!r} ties field {tie_field!r} but member "
                        f"{member!r} has no such field"
                    )
        groups.append(group)
    names = [g.name for g in groups]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise ParamsError(f"{p}: duplicate group name(s) {dupes}")

    ratios: list[ParamRatio] = []
    for i, r in enumerate(data.get("ratios") or []):
        try:
            ratio = ParamRatio(
                param=str(r["param"]),
                ref=str(r["ref"]),
                of=str(r["of"]),
                ratio=r["ratio"],
                is_integer=bool(r.get("is_integer", False)),
                description=r.get("description"),
            )
        except (KeyError, TypeError) as exc:
            raise ParamsError(f"{p}: ratios[{i}] is malformed (needs param/ref/of/ratio): {exc}") from exc
        for inst in (ratio.ref, ratio.of):
            if inst not in devices:
                raise ParamsError(f"{p}: ratios[{i}] instance {inst!r} is not in the devices: inventory")
            if ratio.param not in devices[inst]:
                raise ParamsError(
                    f"{p}: ratios[{i}] instance {inst!r} has no field {ratio.param!r}"
                )
        ratio.value()  # validate the fraction eagerly — a typo should fail at load
        ratios.append(ratio)

    return CircuitParams(devices=devices, groups=tuple(groups), ratios=tuple(ratios), source=p)


def resolve_knob(cp: CircuitParams, name: str) -> str:
    """Resolve one ``dut_params`` name against the contract → an atomic symbol.

    * ``<group>.<field>`` → the group's FIRST member's atomic symbol for that field
      (the free knob under the tie lowering; loud on an unknown group or an untied field).
    * a bare group name → resolvable only when the group ties exactly ONE field.
    * anything else → returned unchanged (an atomic symbol, or a free bias knob like
      ``i_tail`` that never appears in the inventory — unchanged legacy behavior).
    """
    if "." in name:
        group_name, _, field_name = name.partition(".")
        group = cp.group(group_name)  # loud on an unknown group
        if field_name not in group.tie:
            raise ParamsError(
                f"knob {name!r}: field {field_name!r} is not tied by group "
                f"{group_name!r} (tie: {list(group.tie)}) — tie it in params.yaml or "
                f"address the member's atomic symbol directly"
            )
        return cp.symbol(group.members[0], field_name)
    for group in cp.groups:
        if group.name == name:
            if len(group.tie) == 1:
                return cp.symbol(group.members[0], group.tie[0])
            raise ParamsError(
                f"knob {name!r} names a group that ties {list(group.tie)} — ambiguous; "
                f"write '{name}.<field>'"
            )
    return name


def select_ungroup(
    cp: CircuitParams, selectors: Iterable[str]
) -> tuple[list[ParamGroup], list[ParamRatio]]:
    """Expand ``ungroup:`` selectors → the groups + ratios to dissolve.

    Selector shapes: ``"<group_name>"`` | ``"kind:<kind>"`` | ``"ratio:<ref-instance>"``.
    Every selector must match something — a typo'd name/kind fails loudly, never silently
    keeps the tie.
    """
    groups: list[ParamGroup] = []
    ratios: list[ParamRatio] = []
    for raw in selectors:
        sel = str(raw).strip()
        if sel.startswith("kind:"):
            kind = sel[len("kind:"):].strip()
            matched = cp.groups_of_kind(kind)
            if not matched:
                raise ParamsError(
                    f"ungroup selector {sel!r} matches no group; kinds present: "
                    f"{sorted({g.kind for g in cp.groups})}"
                )
            groups.extend(g for g in matched if g not in groups)
        elif sel.startswith("ratio:"):
            ref = sel[len("ratio:"):].strip()
            matched_r = [r for r in cp.ratios if r.ref == ref]
            if not matched_r:
                raise ParamsError(
                    f"ungroup selector {sel!r} matches no ratios: entry; refs present: "
                    f"{sorted(r.ref for r in cp.ratios)}"
                )
            ratios.extend(r for r in matched_r if r not in ratios)
        else:
            group = cp.group(sel)  # loud on an unknown name
            if group not in groups:
                groups.append(group)
    return groups, ratios


def shadow_params(
    cp: CircuitParams,
    selectors: Iterable[str],
    defaults: Mapping[str, Any],
) -> dict[str, str | float]:
    """The shadowing set for dissolved ties: ``{member_symbol: current default}``.

    For each dissolved group, every **non-first** member-field symbol maps to the tie
    target's (first member's) current default, looked up in ``defaults`` (symbol →
    value — typically :func:`netlist_param_defaults` of the lowered deck, or a
    ``sizing.yaml`` mapping). For each dissolved ratio, the *derived* instance's symbol
    maps to its computed default (``param(of) × ratio``). Emitting these as explicit
    ``.param`` definitions overrides the shipped tie lines while leaving first members
    untouched — the tied and untied decks are numerically identical until a shadowed
    symbol is actually swept.
    """
    groups, ratios = select_ungroup(cp, selectors)
    shadows: dict[str, str | float] = {}
    for group in groups:
        first = group.members[0]
        for tie_field in group.tie:
            target_sym = cp.symbol(first, tie_field)
            default = defaults.get(target_sym)
            if default is None:
                raise ParamsError(
                    f"ungroup {group.name!r}: no current default for tie target "
                    f"{target_sym!r} ({first}.{tie_field}) in the provided defaults — "
                    f"cannot compute the shadow value"
                )
            if isinstance(default, str) and "{" in default:
                raise ParamsError(
                    f"ungroup {group.name!r}: tie target {target_sym!r} default "
                    f"{default!r} is an expression, not a literal — the first member "
                    f"should carry the atomic default in the lowered deck"
                )
            for member in group.members[1:]:
                shadows[cp.symbol(member, tie_field)] = default
    for ratio in ratios:
        derived_sym = cp.symbol(ratio.ref, ratio.param)
        base = cp.devices[ratio.of][ratio.param]
        if isinstance(base, str):  # a symbol — look its default up
            base_default = defaults.get(base)
            if base_default is None:
                raise ParamsError(
                    f"ungroup ratio:{ratio.ref}: no current default for base symbol "
                    f"{base!r} ({ratio.of}.{ratio.param}) in the provided defaults"
                )
            base_val = float(parse_value(str(base_default)))
        else:  # a frozen literal in the inventory — it IS the default
            base_val = float(base)
        computed = base_val * ratio.value()
        if abs(computed - round(computed)) < 1e-9:
            computed = float(round(computed))
        shadows[derived_sym] = computed
    return shadows


# one or more `name = value` assignments on a .param card; a value is `{expr}`, a quoted
# 'expr', or a bare token (eng-strings like 0.5u included)
_ASSIGN_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\{[^}]*\}|'[^']*'|[^\s]+)")
_INCLUDE_RE = re.compile(r"^\.(?:include|inc)\s+['\"]?([^'\"\s]+)", re.IGNORECASE)


def netlist_param_defaults(path: str | Path, *, _seen: set[Path] | None = None) -> dict[str, str]:
    """The ``.param`` definitions of a deck, as ``{name: value_string}`` (later wins).

    The committed ``raw/`` decks inline their whole ``.param`` header, so a top-level
    parse suffices; one level of ``.include`` (relative to the deck's directory) is
    followed defensively, missing include targets skipped. ``+`` continuation lines
    are folded into their ``.param`` card.
    """
    p = Path(path)
    seen = _seen if _seen is not None else set()
    rp = p.resolve()
    if rp in seen or not p.is_file():
        return {}
    seen.add(rp)
    params: dict[str, str] = {}
    lines = p.read_text().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("*"):
            continue
        inc = _INCLUDE_RE.match(line)
        if inc:
            target = Path(inc.group(1))
            if not target.is_absolute():
                target = p.parent / target
            params.update(netlist_param_defaults(target, _seen=seen))
            continue
        if not line.lower().startswith(".param"):
            continue
        card = line[len(".param"):]
        while i < len(lines) and lines[i].lstrip().startswith("+"):
            card += " " + lines[i].lstrip()[1:]
            i += 1
        for m in _ASSIGN_RE.finditer(card):
            params[m.group(1)] = m.group(2)
    return params
