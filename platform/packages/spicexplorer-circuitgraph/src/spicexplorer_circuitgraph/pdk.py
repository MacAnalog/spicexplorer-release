"""PDK device-name awareness.

spicelib carries **zero** PDK semantics — a device's model name is just an opaque token in
its value slot, with no notion of nmos/pmos or of how one PDK names a device versus another.
This module owns that knowledge: the mapping between a PDK's model/cell names and the graph's
canonical (device kind, MOS polarity). It is the single place PDK naming lives and powers two
directions:

* **build:** classify a model name -> kind/polarity (a robust complement to the
  ``nmos``/``pmos`` substring heuristic), and
* **emit (Phase 4):** pick the PDK-specific model name for a graph node when writing a netlist
  (``model_for``), so an IHP graph can be re-emitted with e.g. Skywater names.

Seeded for IHP ``sg13g2``; Skywater is the next target. Extend the device tables as needed.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model.nodes import DeviceType, MosPolarityType

__all__ = [
    "PdkDevice", "Pdk", "IHP_SG13G2", "SKYWATER_SKY130", "GF180MCU", "ANALOGGYM_FOUNDRY",
    "FOUNDRY_N65", "PDKS", "get_pdk", "mos_flavor", "model_flavor", "split_flavor",
    "THRESHOLD_FLAVORS",
]

#: The **threshold** half of the flavor vocabulary. A threshold label says which Vth bin of the
#: same oxide the device sits in — it is a bias-point difference, not a safety one, and every PDK
#: spells (and bins) it differently. Everything else a flavor carries is a **voltage class**
#: (``hv``, ``io``, ``3v3``): a different oxide/rating, where substituting the core device puts a
#: 3.3 V part on a 1.8 V model and the deck still simulates. The two are treated differently on
#: retarget — see :meth:`Pdk.resolve_model`.
THRESHOLD_FLAVORS: frozenset[str] = frozenset({"lvt", "ulvt", "hvt", "nvt"})


def split_flavor(flavor: str) -> tuple[str, str]:
    """Split a flavor label into its ``(voltage_class, threshold)`` halves.

    The ``flavor`` field carries two vocabularies at once and they do not mean the same thing::

        split_flavor("hv")      -> ("hv", "")      # a voltage class: thick-oxide / IO device
        split_flavor("lvt")     -> ("", "lvt")     # a threshold bin of the CORE device
        split_flavor("hv_nvt")  -> ("hv", "nvt")   # gf180's native-Vt 6 V part: both
        split_flavor("io")      -> ("io", "")

    Underscore-joined tokens are partitioned by membership in :data:`THRESHOLD_FLAVORS`; anything
    unrecognized is treated as part of the voltage class, so an unknown label keeps the strict
    (raise-on-mismatch) treatment rather than silently becoming substitutable.
    """
    if not flavor:
        return "", ""
    tokens = [t for t in flavor.strip().lower().split("_") if t]
    thresholds = [t for t in tokens if t in THRESHOLD_FLAVORS]
    classes = [t for t in tokens if t not in THRESHOLD_FLAVORS]
    return "_".join(classes), "_".join(thresholds)


def mos_flavor(model_token: str | None) -> str:
    """The threshold/voltage-class flavor encoded in a generic MOS token, else ``""`` (the core
    device). The convention is ``<polarity>[_<flavor>]`` on the *abstract* token: ``nmos`` → ``""``,
    ``nmos_hv`` → ``"hv"``, ``pmos_io`` → ``"io"``. PDK *model* names (``sg13_hv_nmos``) are NOT
    parsed here — their flavor is declared on the :class:`PdkDevice`, and
    :func:`model_flavor` is the lookup that reads it."""
    if not model_token:
        return ""
    token = model_token.strip().lower()
    for pol in ("nmos", "pmos"):
        if token == pol:
            return ""
        if token.startswith(pol + "_"):
            return token[len(pol) + 1 :]
    return ""


def model_flavor(model_token: str | None) -> str:
    """The flavor of a MOS token, whatever kind of token it is — the retarget-side lookup.

    A *registered PDK model name* resolves through its :class:`PdkDevice` **declaration**
    (``sg13_hv_nmos`` → ``"hv"``): a PDK spells its voltage class its own way, so the device table
    is the only authority and no generic parse can substitute for it. Anything unregistered falls
    back to the abstract ``<polarity>[_<flavor>]`` convention (:func:`mos_flavor`), so a graph
    authored with generic ``nmos``/``nmos_hv`` tokens keeps working.

    This is what makes cross-PDK retargeting flavor-aware: without it a source model's declared
    class is invisible at emit time and every device looks like the core device, so an ``hv`` part
    lands on a core model of a *lower voltage class* with nothing to signal it (see
    :meth:`Pdk.model_for`, which refuses that substitution).
    """
    if not model_token:
        return ""
    for pdk in PDKS.values():
        dev = pdk.classify(model_token)
        if dev is not None and dev.device_type is DeviceType.MOS:
            return dev.flavor
    return mos_flavor(model_token)


@dataclass(frozen=True)
class PdkDevice:
    """One PDK device/model and what it maps to in the canonical graph model."""

    model: str  # PDK model/cell name, e.g. "sg13_lv_nmos"
    device_type: DeviceType
    polarity: MosPolarityType = MosPolarityType.UNKNOWN
    # Flavor label, not a voltage. It carries TWO vocabularies (see :func:`split_flavor`): a
    # voltage class (``"hv"``, ``"io"``) and/or a threshold bin (``"lvt"``, ``"nvt"``), joined by
    # ``_`` when both apply (gf180's ``"hv_nvt"``). Only the voltage class is retarget-strict.
    # ``""`` is the core/default device and ``"hv"``
    # is "the thick-oxide / high-voltage IO device of this PDK". The label is what cross-PDK
    # retargeting matches on, so declaring it honestly is load-bearing — a device left at ``""``
    # advertises itself as a core device and can be substituted for one. Two PDKs' ``hv`` parts are
    # the same *class*, not the same rating (IHP 3.3 V, sky130 5 V, gf180 6 V): retargeting keeps
    # an IO device an IO device, and the resulting sizing/bias is still the designer's to re-check.
    flavor: str = ""


@dataclass(frozen=True)
class Pdk:
    """A PDK's device table + the two lookups the build/emit paths need.

    ``finger_param`` / ``width_per_finger`` capture how this PDK's MOS device expresses fingers,
    so emission can retarget the canonical graph convention. The graph is authored IHP-style:
    ``w`` is the **total** device width and ``ng`` the finger count. A PDK whose primitive instead
    takes a **per-finger** width plus a differently-named finger param (sky130: ``nf``) needs the
    width divided across fingers and the count renamed on emit (see ``emit._retarget_fingers``).
    """

    name: str
    devices: tuple[PdkDevice, ...]
    finger_param: str = "ng"          # the instance param naming the finger/gate count
    width_per_finger: bool = False    # True: device `w` is per-finger (total = w*fingers), not total

    def classify(self, model_name: str | None) -> PdkDevice | None:
        """Resolve a model name to its :class:`PdkDevice` (case-insensitive); ``None`` if unknown."""
        if not model_name:
            return None
        key = model_name.strip().lower()
        for dev in self.devices:
            if dev.model.lower() == key:
                return dev
        return None

    def model_for(
        self,
        device_type: DeviceType,
        polarity: MosPolarityType = MosPolarityType.UNKNOWN,
        flavor: str = "",
    ) -> str | None:
        """Reverse lookup for emission: the PDK model name for a (kind, polarity, flavor).

        The **first** device matching (kind, polarity, flavor) exactly wins, so an unflavored
        caller keeps the historical first-match behavior byte-for-byte (the core/default device).

        A requested **non-empty** flavor this table does not declare returns ``None``; it must
        never degrade to the core device. That fallback used to exist and was a silent
        voltage-class change — a ``flavor="hv"`` (3.3 V IHP) device retargeted to sky130 came out
        as ``sky130_fd_pr__nfet_01v8``, a 1.8 V core model, with no warning and no way for a
        caller to tell. Emission turns the ``None`` into a raise (see
        ``emit._value_slot``); the fix for a legitimately-missing part is to declare it in the
        target table, not to guess.

        This is the **exact-match** lookup. Retargeting goes through :meth:`resolve_model`, which
        keeps this strictness for a voltage class and substitutes (loudly) for a threshold.
        """
        for dev in self.devices:
            if dev.device_type is not device_type:
                continue
            if device_type is DeviceType.MOS and dev.polarity is not polarity:
                continue
            if dev.flavor == flavor:
                return dev.model
        return None

    def resolve_model(
        self,
        device_type: DeviceType,
        polarity: MosPolarityType = MosPolarityType.UNKNOWN,
        flavor: str = "",
    ) -> tuple[str | None, str]:
        """Retarget lookup: ``(model, substitution_note)`` — the flavor-aware :meth:`model_for`.

        The two vocabularies :func:`split_flavor` separates are handled differently, because the
        consequence of getting them wrong is different:

        * **voltage class** (``hv``/``io``/…): never substituted. A 3.3 V part emitted as a 1.8 V
          core model produces a deck that simulates and answers a different circuit, so a target
          that declares no device of that class returns ``(None, "")`` and the caller raises.
        * **threshold** (``lvt``/``ulvt``/``hvt``/``nvt``): substituted with the same voltage
          class's device and a note naming the substitution. A threshold retarget is a bias-point
          change the designer re-checks anyway, and no reference table declares a threshold today
          — so raising on it makes ``nmos_lvt`` un-retargetable to *every* PDK, including
          ``FOUNDRY-n65`` whose default NMOS is literally ``DEVICE``.

        An exact hit always wins, so a table that *does* declare the threshold keeps it.
        """
        exact = self.model_for(device_type, polarity, flavor)
        if exact is not None:
            return exact, ""
        voltage_class, threshold = split_flavor(flavor)
        if not threshold:
            return None, ""  # a pure voltage-class miss — the caller must not substitute
        fallback = self.model_for(device_type, polarity, voltage_class)
        if fallback is None:
            return None, ""  # the voltage class itself is missing — likewise a caller-side raise
        kept = f"{voltage_class!r}-class " if voltage_class else "core "
        return fallback, (
            f"{self.name} declares no {threshold!r}-threshold {kept}device; using {fallback!r} "
            f"instead — the threshold flavor is NOT preserved, so re-check the bias point "
            f"(declare the {threshold!r} device in the {self.name} table to keep it)"
        )


# --- IHP sg13g2 (primary test PDK) — a seed table; extend as coverage grows ----------------
IHP_SG13G2 = Pdk(
    name="ihp-sg13g2",
    devices=(
        PdkDevice("sg13_lv_nmos", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("sg13_lv_pmos", DeviceType.MOS, MosPolarityType.PMOS),
        PdkDevice("sg13_hv_nmos", DeviceType.MOS, MosPolarityType.NMOS, flavor="hv"),
        PdkDevice("sg13_hv_pmos", DeviceType.MOS, MosPolarityType.PMOS, flavor="hv"),
        PdkDevice("rhigh", DeviceType.RES),
        PdkDevice("rsil", DeviceType.RES),
        PdkDevice("rppd", DeviceType.RES),
        PdkDevice("cap_cmim", DeviceType.CAP),
        PdkDevice("cap_rfcmim", DeviceType.CAP),
    ),
)

# --- Skywater sky130 (second target — used for cross-PDK device renaming) ------------------
SKYWATER_SKY130 = Pdk(
    name="sky130",
    # sky130 MOS are BSIM4 subckts that pass `w`+`nf` straight to the device. BSIM4 treats `w` as
    # the TOTAL width and bins on the per-finger width `w/nf` itself — so we emit `nf=ng` and keep
    # `w` TOTAL (NOT `w/ng`). Dividing here too would double-divide → a sub-µm per-finger device in a
    # defective model bin (`Dsub<0`/`Vsat<0`), the root cause of the multi-finger sky130 no-run
    # cluster. Verified at the subckt source + by sim (W=5,nf=1 ok; W=5,nf=114 bad bin; W=570,nf=114
    # ok). Single-finger (ng=1) emission is unchanged either way.
    finger_param="nf",
    width_per_finger=False,
    devices=(
        PdkDevice("sky130_fd_pr__nfet_01v8", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("sky130_fd_pr__pfet_01v8", DeviceType.MOS, MosPolarityType.PMOS),
        # The 5 V IO pair is this PDK's high-voltage class — declared, so an `hv` source device
        # retargets onto it instead of onto the 1.8 V core model.
        PdkDevice("sky130_fd_pr__nfet_g5v0d10v5", DeviceType.MOS, MosPolarityType.NMOS, flavor="hv"),
        PdkDevice("sky130_fd_pr__pfet_g5v0d10v5", DeviceType.MOS, MosPolarityType.PMOS, flavor="hv"),
        PdkDevice("sky130_fd_pr__res_high_po", DeviceType.RES),
        PdkDevice("sky130_fd_pr__cap_mim_m3_1", DeviceType.CAP),
    ),
)

# --- GlobalFoundries gf180mcu (third target — open_pdks/volare build) ----------------------
# ngspice device names are short (no `gf180mcu_fd_pr__` prefix): nfet_03v3 / pfet_03v3 (3.3V core)
# and the 6V0 IO devices. Geometry is explicit µm (no `.option scale`, like IHP). Like sky130 it is
# BSIM4 with `nf` → `w` is TOTAL (the device bins on `w/nf`); emit `nf=ng`, keep `w` total. (Same
# correction as sky130; both BSIM4 PDKs share the universal `nf` semantics — see SKYWATER_SKY130.)
GF180MCU = Pdk(
    name="gf180mcu",
    finger_param="nf",
    width_per_finger=False,
    devices=(
        PdkDevice("nfet_03v3", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("pfet_03v3", DeviceType.MOS, MosPolarityType.PMOS),
        # The 6 V IO pair is this PDK's high-voltage class (see the sky130 note); the native-Vt
        # 6 V device is its own class, so it never stands in for a plain `hv` request.
        PdkDevice("nfet_06v0", DeviceType.MOS, MosPolarityType.NMOS, flavor="hv"),
        PdkDevice("pfet_06v0", DeviceType.MOS, MosPolarityType.PMOS, flavor="hv"),
        PdkDevice("nfet_06v0_nvt", DeviceType.MOS, MosPolarityType.NMOS, flavor="hv_nvt"),
    ),
)

# Device-NAME map for the AnalogGym / ferrosim reference corpora in analog-db (FOUNDRY-style
# `nch_*`/`pch_*` spellings). The names come from the public upstream repos (BSD-3 / MIT) —
# this table carries **no foundry PDK content** and exists so polarity classification and
# `find_subcircuits` work on the reference decks out of the box. First entry per polarity is
# the reverse-lookup (`model_for`) default.
ANALOGGYM_FOUNDRY = Pdk(
    name="analoggym-FOUNDRY",
    finger_param="nf",
    width_per_finger=False,
    devices=(
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.PMOS),
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.PMOS),
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.NMOS),
        # The 1.8 V thick-oxide PMOS is the corpus' high-voltage class (there is no NMOS twin in
        # this reference table, so an `hv` NMOS request correctly finds nothing).
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.PMOS, flavor="hv"),
    ),
)

# --- FOUNDRY N65 (the virtuoso-bridge / Spectre target) ------------------------------------
# Device-NAME table only — model names as they appear in netlists, no foundry model content
# (same posture as ANALOGGYM_FOUNDRY). LVT first: it is the `model_for` default per polarity and
# the flavor validated live (self-contained corner sections).
# The models are BSIM4 with the universal `nf` finger semantics: `w` stays TOTAL (see sky130).
FOUNDRY_N65 = Pdk(
    name="FOUNDRY-n65",
    finger_param="nf",
    width_per_finger=False,
    devices=(
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.PMOS),
        PdkDevice("nch", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("pch", DeviceType.MOS, MosPolarityType.PMOS),
    ),
)

PDKS: dict[str, Pdk] = {
    IHP_SG13G2.name: IHP_SG13G2,
    SKYWATER_SKY130.name: SKYWATER_SKY130,
    GF180MCU.name: GF180MCU,
    ANALOGGYM_FOUNDRY.name: ANALOGGYM_FOUNDRY,
    FOUNDRY_N65.name: FOUNDRY_N65,
}


def get_pdk(name: str) -> Pdk | None:
    """Look up a registered PDK by name (e.g. ``"ihp-sg13g2"``)."""
    return PDKS.get(name)
