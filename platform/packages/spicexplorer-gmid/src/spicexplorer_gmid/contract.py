"""The single typed I/O contract for the gm/ID sizing tool (Pydantic v2).

This module is the **one source of truth** for the tool's data shapes — the same models feed the
library API, the (later, R5) OpenAPI→TS codegen, and MCP schemas. Keep it free of behaviour:
``tables.py`` / ``sizing.py`` / ``passives.py`` produce these, nothing here computes.

Unit convention (the gm/ID methodology's native mixed-SI, matching the committed pygmid LUTs):

* lengths/widths ``L``, ``W`` in **micrometres (µm)**;
* voltages ``vgs``, ``vds``, ``vsb`` in **volts (V)**;
* ``gm_id`` (gm/ID) in **1/V**; current density ``jd`` (ID/W) in **A/µm**;
* absolute current ``ID`` in **A**, transconductance ``gm`` in **S**;
* capacitance densities ``cgg_w``/``cdd_w`` in **F/µm**, absolutes ``cgg``/``cdd`` in **F**;
* ``ft`` (transit frequency, gm/(2π·Cgg)) in **Hz**; ``av0`` (gm/gds, intrinsic gain) dimensionless.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ── LUT manifest models (the typed registry record beside each committed .pkl) ────────────────────


class AxisSpec(BaseModel):
    """One run-dimension grid: count, range, and uniform step or explicit values.

    All committed LUTs record four dimensions: ``L_um``, ``VGS_V``, ``VDS_V``, ``VSB_V``.
    A uniform grid carries a ``step``; a non-uniform grid (e.g. the L axis) carries explicit
    ``values``. ``stored="magnitude"`` means the LUT stores ``|VSB|`` (pmos sign convention).
    """

    model_config = ConfigDict(frozen=True)

    n: int = Field(description="number of grid points")
    min: float = Field(description="minimum value")
    max: float = Field(description="maximum value")
    step: float | None = Field(default=None, description="uniform step (None if non-uniform)")
    values: list[float] | None = Field(default=None, description="explicit values (non-uniform grid)")
    stored: str | None = Field(
        default=None,
        description="storage convention, e.g. 'magnitude' for VSB (LUT stores |VSB|)",
    )


class LUTConditions(BaseModel):
    """Fixed extraction conditions shared across the entire LUT sweep (W/nfing/temp)."""

    model_config = ConfigDict(frozen=True)

    temp_k: float = Field(description="simulation temperature [K]")
    width_um: float = Field(description="characterization width [µm]")
    nfing: int = Field(description="number of fingers used for characterization")


class LUTModelRecord(BaseModel):
    """Exact model-card resolution: the .lib/.include lines that pulled the model."""

    model_config = ConfigDict(frozen=True)

    corner_lines: list[str] = Field(description=".lib/.include lines that resolved the model card")
    variant_override: str | None = Field(default=None, description="device-variant override (LV/HV) if any")
    info: str = Field(description="human-readable description from the LUT INFO header")


class LUTProvenance(BaseModel):
    """Extraction provenance: tool, ngspice version, timestamp."""

    model_config = ConfigDict(frozen=True)

    tool: str
    ngspice: str | None = None
    extracted_at: str | None = None


class LUTManifest(BaseModel):
    """Self-describing registration record for a committed gm/ID LUT.

    Records the full run dimensions (VGS/VDS/VSB/L grids, W/nfing/temp), corner, the exact
    model-card lines, stored parameter names, and extraction provenance.  The ``.pkl`` holds
    the numeric data; the manifest holds *what it is and how it was made*.

    Loaded from the ``<device>__<corner>.manifest.json`` sidecar via
    :meth:`from_path`, or obtained through :class:`~spicexplorer_gmid.LUTRegistry`.
    Attached to a loaded :class:`~spicexplorer_gmid.DeviceTable` as ``.manifest``.

    Example::

        from spicexplorer_gmid import LUTRegistry
        reg = LUTRegistry("/path/to/_shared/gmid")
        m = reg.find("sky130", "sky130_fd_pr__nfet_01v8")
        print(m.corner)                              # "tt"
        print(m.conditions.temp_k)                  # 300.0
        print(m.model.corner_lines)                 # ['.lib sky130.lib.spice tt']
        print(m.dimensions["L_um"].values)          # [0.15, 0.18, 0.2, ...]
        print(m.dimensions["VGS_V"].step)           # 0.05
        print(m.dimensions["VSB_V"].stored)         # "magnitude"
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    schema_id: str = Field(alias="schema", description="schema version identifier")
    pdk: str
    device: str
    model_family: str = Field(description="model family: 'bsim4' (sky130/gf180) or 'psp' (ihp)")
    polarity: str = Field(description="'n' or 'p'")
    corner: str
    model: LUTModelRecord
    conditions: LUTConditions
    dimensions: dict[str, AxisSpec] = Field(
        description="run dimensions keyed by 'L_um', 'VGS_V', 'VDS_V', 'VSB_V'"
    )
    params: list[str] = Field(description="stored electrical parameter names, e.g. ['ID','GM',...]")
    lut_file: str = Field(description=".pkl filename (relative to its pdk sub-directory)")
    provenance: LUTProvenance

    @classmethod
    def from_path(cls, path: Path | str) -> LUTManifest:
        """Load from a ``.manifest.json`` sidecar file."""
        return cls.model_validate_json(Path(path).read_text())

    def axis(self, name: str) -> AxisSpec:
        """Look up one run dimension by name (e.g. ``'L_um'``, ``'VGS_V'``)."""
        if name not in self.dimensions:
            raise KeyError(f"{name!r} not in dimensions: {sorted(self.dimensions)}")
        return self.dimensions[name]


class OperatingPoint(BaseModel):
    """A small-signal operating point read off a gm/ID lookup table at one (gm/ID, L, VDS, VSB).

    Everything but the four chosen coordinates is *interpolated from the table* — no square-law
    hand formula is used anywhere.
    """

    model_config = ConfigDict(frozen=True)

    gm_id: float = Field(description="gm/ID, the chosen inversion coordinate [1/V]")
    L: float = Field(description="channel length [µm]")
    vds: float = Field(description="drain–source voltage [V]")
    vsb: float = Field(default=0.0, description="source–bulk voltage [V]")

    vgs: float = Field(description="gate–source voltage solved from gm/ID via lookup_vgs [V]")
    jd: float = Field(description="current density ID/W [A/µm]")
    av0: float = Field(description="intrinsic gain gm/gds [-]")
    ft: float = Field(description="transit frequency gm/(2π·Cgg) [Hz]")
    cgg_w: float = Field(description="gate capacitance per width [F/µm]")
    cdd_w: float = Field(description="drain capacitance per width [F/µm]")


class SanityGate(BaseModel):
    """One design-rule check attached to a sized device (the verification ledger).

    ``status`` is the three-state outcome and ``ok`` the boolean verdict of the *measurement*:

    * ``"ok"`` — the check ran and the measurement is inside its window (``ok=True``);
    * ``"fail"`` — the check ran and the measurement is outside it (``ok=False``); this **blocks**
      :attr:`SizedDevice.passed`;
    * ``"unchecked"`` — the measurement is outside the window, but the caller expressed no intent
      that direction, so it is reported as an **advisory** and does *not* block ``passed``
      (``ok=False``, because rendering an unchecked direction as green is exactly the failure mode
      this state exists to remove).

    ``status`` defaults to ``"ok"``/``"fail"`` from ``ok``, so every gate that has no advisory
    direction keeps the plain two-state behaviour without naming it.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    ok: bool
    detail: str
    status: Literal["ok", "unchecked", "fail"] = Field(
        default="ok",
        description="three-state outcome; 'unchecked' is advisory and never blocks `passed`",
    )

    @model_validator(mode="before")
    @classmethod
    def _default_status_from_ok(cls, data: object) -> object:
        """An omitted ``status`` mirrors ``ok`` — every pre-existing two-state gate is unchanged."""
        if isinstance(data, dict) and "status" not in data:
            return {**data, "status": "ok" if data.get("ok", True) else "fail"}
        return data

    @property
    def blocking(self) -> bool:
        """True when this gate's outcome counts against :attr:`SizedDevice.passed`."""
        return self.status != "unchecked"


class GeometryBounds(BaseModel):
    """Per-PDK W/L envelope (from the analog-db registry ``geometry`` block), all in µm.

    Passed *in* to the sizing call — the leaf tool never imports the DB; the caller resolves these.
    """

    model_config = ConfigDict(frozen=True)

    l_min: float | None = None
    l_max: float | None = None
    w_min: float | None = None
    w_max: float | None = None


class SizedDevice(BaseModel):
    """A transistor sized to a transconductance / current target with its verification gates.

    ``gates`` is the assumptions/checks ledger (netlist2tf's "every assumption explicit" discipline
    applied to sizing); ``passed`` is true only when every **blocking** gate holds — a gate whose
    ``status`` is ``"unchecked"`` is an advisory the caller never asked to be gated on (see
    :class:`SanityGate`) and is reported without vetoing the sizing.
    """

    model_config = ConfigDict(frozen=True)

    W: float = Field(description="total device width [µm]")
    L: float = Field(description="channel length [µm]")
    nf: int = Field(default=1, description="number of fingers (W split evenly across them)")
    ID: float = Field(description="drain bias current [A]")
    gm: float = Field(description="transconductance [S]")
    cgg: float = Field(description="absolute gate capacitance cgg_w·W [F]")
    cdd: float = Field(description="absolute drain capacitance cdd_w·W [F]")
    op: OperatingPoint
    gates: list[SanityGate] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True iff every *blocking* sanity gate holds (``"unchecked"`` advisories don't veto)."""
        return all(g.ok for g in self.gates if g.blocking)

    @property
    def wf(self) -> float:
        """Per-finger width [µm]."""
        return self.W / self.nf


class SizedPassive(BaseModel):
    """A resistor or capacitor sized from PDK sheet-resistance / area-capacitance constants."""

    model_config = ConfigDict(frozen=True)

    kind: Literal["resistor", "capacitor"]
    target: float = Field(description="requested value (Ω for resistor, F for capacitor)")
    value: float = Field(description="realised value with the rounded geometry")
    # resistor geometry
    w_um: float | None = Field(default=None, description="resistor width [µm]")
    l_um: float | None = Field(default=None, description="resistor length [µm]")
    squares: float | None = Field(default=None, description="number of squares L/W [-]")
    # capacitor geometry
    area_um2: float | None = Field(default=None, description="capacitor plate area [µm²]")


class SizingReport(BaseModel):
    """A named collection of sized devices/passives — the per-block sizing result + assumptions.

    Per goals.md principle 3 (one Pydantic contract per tool): this is the serialisable artifact an
    orchestrator emits to ``sizing.yaml`` and an analysis surface (R5) returns.
    """

    model_config = ConfigDict(frozen=True)

    title: str
    devices: dict[str, SizedDevice] = Field(default_factory=dict)
    passives: dict[str, SizedPassive] = Field(default_factory=dict)
    assumptions: list[str] = Field(
        default_factory=list,
        description="free-text ledger of the choices behind this sizing (corner, gm/ID per role, …)",
    )

    @property
    def passed(self) -> bool:
        """True iff every device's gates pass (passives are closed-form, always 'ok')."""
        return all(d.passed for d in self.devices.values())
