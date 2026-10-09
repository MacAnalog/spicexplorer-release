"""The process description, as data — one file per PDK, read by every lane.

The rule this module exists to enforce: **the platform carries logic, a PDK carries numbers.**
A GDS layer number, a sheet resistance, an electromigration limit, a routing clearance — none
of them belongs in a Python file, because a function with an IHP number in it is a function
that cannot run on another process, and a second process gets a second copy of the function.

So every such number lives in ``spicexplorer_core/techs/<pdk>.yaml`` (or a file the caller
owns), and every function that needs one takes a ``tech=``. The config sits in **core** rather
than in a leaf tool because both ``spicexplorer_layout`` (routing, sheet-resistance solves,
the EM lane's stackup) and ``spicexplorer_signoff`` (current density) need the same numbers,
and leaf tools never import each other.

    from spicexplorer_core.tech import Tech

    tech = Tech.builtin("ihp-sg13g2")       # or Tech.from_yaml("my-process.yaml")
    tech.gds_layer("Metal1")                # (8, 0)
    tech.sheet_resistance("Metal1")         # 0.110 Ohm/square
    tech.routing.column_pitch_um            # 0.6 um

A key the file does not state is an error, not a default: a routing rule quietly defaulting to
another process's number is exactly the failure this module removes. The one exception is a
whole *section*, which may be absent when a lane does not use it — asking a tech with no
``routing:`` block for a routing rule says so by name.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

__all__ = ["EmLimit", "RoutingRules", "Tech", "builtin_techs", "techs_dir"]


def techs_dir() -> Path:
    return Path(__file__).resolve().parent / "techs"


def builtin_techs() -> list[str]:
    """The PDK names :meth:`Tech.builtin` accepts."""
    return sorted(p.stem for p in techs_dir().glob("*.yaml"))


def _only_known(cls, d: Mapping[str, Any], where: str):
    names = {f.name for f in fields(cls)}
    unknown = sorted(set(d) - names)
    if unknown:
        raise ValueError(
            f"{cls.__name__}({where}): unknown key(s) {unknown}; valid: {sorted(names)}"
        )
    return cls(**d)


@dataclass(frozen=True)
class EmLimit:
    """One conductor's electromigration limit, as the process spec states it.

    A wire carries ``per_um_ma`` mA per µm of drawn width at or above ``wide_um``, and a flat
    ``narrow_ma`` total in the qualified narrow band ``[narrow_um, wide_um)``. A via/contact
    layer instead carries ``per_via_ma`` mA per cut and ignores width. ``min_width_rule`` is
    cited when the width floor comes from the rule deck rather than the EM spec.
    """

    per_um_ma: float | None = None
    wide_um: float | None = None
    narrow_ma: float | None = None
    narrow_um: float | None = None
    per_via_ma: float | None = None
    cut: str = "via"
    min_width_rule: str = ""

    @property
    def is_via(self) -> bool:
        return self.per_via_ma is not None

    @property
    def min_qualified_um(self) -> float | None:
        """Narrowest drawn width this layer has a number for; ``None`` for a via layer."""
        if self.is_via:
            return None
        for v in (self.narrow_um, self.wide_um):
            if v:
                return v
        return None


@dataclass(frozen=True)
class RoutingRules:
    """The drawn-geometry rules a generator's obstacle map and column allocator obey."""

    grid_um: float
    route_layer: str
    stub_layer: str
    stub_width_um: float
    stub_clear_x_um: float
    stub_clear_y_um: float
    column_pitch_um: float

    def snap(self, v: float) -> float:
        return round(round(v / self.grid_um) * self.grid_um, 4)


@dataclass(frozen=True)
class Tech:
    """One process, as data. ``name`` is the PDK id; every other field is a section."""

    name: str
    metals: dict[str, int]
    vias: dict[str, int]
    metal_datatype: int = 0
    text_datatype: int = 25
    sheet_ohm_sq: dict[str, float] | None = None
    em_limits: dict[str, EmLimit] | None = None
    routing: RoutingRules | None = None
    raw: dict[str, Any] | None = None  # every section, including the lanes this class ignores

    # ---------------------------------------------------------------- loading ----
    @classmethod
    def from_yaml(cls, path: str | Path, *, name: str | None = None) -> Tech:
        import yaml

        path = Path(path)
        d = yaml.safe_load(path.read_text()) or {}
        d = d.get("tech", d)
        return cls.from_dict(d, name=name or path.stem, where=str(path))

    @classmethod
    def from_dict(cls, d: Mapping[str, Any], *, name: str, where: str = "<dict>") -> Tech:
        em = d.get("em_limits")
        rt = d.get("routing")
        return cls(
            name=name,
            metals=dict(d.get("metals") or {}),
            vias=dict(d.get("vias") or {}),
            metal_datatype=int(d.get("metal_datatype", 0)),
            text_datatype=int(d.get("text_datatype", 25)),
            sheet_ohm_sq=dict(d["sheet_ohm_sq"]) if d.get("sheet_ohm_sq") else None,
            em_limits=(
                {k: _only_known(EmLimit, v, f"{where}:em_limits.{k}") for k, v in em.items()}
                if em
                else None
            ),
            routing=_only_known(RoutingRules, rt, f"{where}:routing") if rt else None,
            raw=dict(d),
        )

    @classmethod
    def builtin(cls, name: str) -> Tech:
        """A tech packaged with the platform. Unknown names list what IS available."""
        p = techs_dir() / f"{name}.yaml"
        if not p.is_file():
            raise ValueError(f"no builtin tech {name!r}; available: {builtin_techs()}")
        return cls.from_yaml(p, name=name)

    @classmethod
    def resolve(cls, tech: Tech | str | Path | None, default: str | None = None) -> Tech:
        """Accept whatever a caller has: a :class:`Tech`, a builtin name, a YAML path, or None.

        The one place the fallback is applied, so a function signature can read
        ``tech: Tech | str | None = None`` without each one repeating it. With nothing passed
        the process comes from ``$PDK`` — **never** from a name written into this file. A
        hard-coded default is how one process's numbers end up silently answering another
        process's question, so an unset ``$PDK`` and no ``default=`` is an error that says so.
        """
        if isinstance(tech, cls):
            return tech
        if tech is None:
            name = default or os.environ.get("PDK") or ""
            if not name:
                raise ValueError(
                    "no tech given and $PDK is unset: pass tech= (a Tech, a builtin name or a "
                    f"YAML path) or set PDK. Builtin: {builtin_techs()}"
                )
            return cls.builtin(name)
        p = Path(tech)
        if p.suffix in (".yaml", ".yml") or p.is_file():
            return cls.from_yaml(p)
        return cls.builtin(str(tech))

    # ---------------------------------------------------------------- lookups ----
    def _layer_number(self, layer: str) -> int:
        for table in (self.metals, self.vias):
            for k, v in table.items():
                if k.lower() == layer.lower():
                    return int(v)
        raise KeyError(
            f"{self.name}: no layer {layer!r} in the tech config "
            f"(metals: {sorted(self.metals)}; vias: {sorted(self.vias)})"
        )

    def gds_layer(self, layer: str, *, datatype: int | None = None) -> tuple[int, int]:
        """``(number, datatype)`` for a named layer — what a GDS reader wants."""
        return (
            self._layer_number(layer),
            self.metal_datatype if datatype is None else int(datatype),
        )

    def sheet_resistance(self, layer: str) -> float:
        """Ohm per square of a named conductor."""
        if not self.sheet_ohm_sq:
            raise KeyError(f"{self.name}: this tech config states no `sheet_ohm_sq:` section")
        for k, v in self.sheet_ohm_sq.items():
            if k.lower() == layer.lower():
                return float(v)
        raise KeyError(
            f"{self.name}: no sheet resistance for {layer!r} (have: {sorted(self.sheet_ohm_sq)})"
        )

    def em_limit(self, layer: str) -> EmLimit:
        """The electromigration limit of a named conductor."""
        if not self.em_limits:
            raise KeyError(f"{self.name}: this tech config states no `em_limits:` section")
        for k, v in self.em_limits.items():
            if k.lower() == layer.lower():
                return v
        raise KeyError(
            f"{self.name}: no electromigration limit for {layer!r} (have: {sorted(self.em_limits)})"
        )

    def routing_rules(self) -> RoutingRules:
        if self.routing is None:
            raise KeyError(f"{self.name}: this tech config states no `routing:` section")
        return self.routing
