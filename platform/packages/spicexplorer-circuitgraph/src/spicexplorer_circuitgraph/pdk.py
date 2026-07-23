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
    "FOUNDRY_N65", "PDKS", "get_pdk", "mos_flavor",
]


def mos_flavor(model_token: str | None) -> str:
    """The threshold/voltage-class flavor encoded in a generic MOS token, else ``""`` (the core
    device). The convention is ``<polarity>[_<flavor>]`` on the *abstract* token: ``nmos`` → ``""``,
    ``nmos_hv`` → ``"hv"``, ``pmos_io`` → ``"io"``. PDK *model* names (``sg13_hv_nmos``) are NOT
    parsed here — their flavor is declared on the :class:`PdkDevice`."""
    if not model_token:
        return ""
    token = model_token.strip().lower()
    for pol in ("nmos", "pmos"):
        if token == pol:
            return ""
        if token.startswith(pol + "_"):
            return token[len(pol) + 1 :]
    return ""


@dataclass(frozen=True)
class PdkDevice:
    """One PDK device/model and what it maps to in the canonical graph model."""

    model: str  # PDK model/cell name, e.g. "sg13_lv_nmos"
    device_type: DeviceType
    polarity: MosPolarityType = MosPolarityType.UNKNOWN
    flavor: str = ""  # threshold/voltage class (e.g. "hv"); "" is the core/default device


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

        An exact ``flavor`` match wins; when the requested flavor is absent the **first**
        default-flavor (``""``) device of that (kind, polarity) is the fallback — so an unflavored
        caller keeps the historical first-match behavior byte-for-byte (the core/default device),
        while a ``flavor="hv"`` caller resolves the hv model when the table declares one.
        """
        fallback: str | None = None
        for dev in self.devices:
            if dev.device_type is not device_type:
                continue
            if device_type is DeviceType.MOS and dev.polarity is not polarity:
                continue
            if dev.flavor == flavor:
                return dev.model
            if fallback is None and dev.flavor == "":
                fallback = dev.model
        return fallback


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
        PdkDevice("sky130_fd_pr__nfet_g5v0d10v5", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("sky130_fd_pr__pfet_g5v0d10v5", DeviceType.MOS, MosPolarityType.PMOS),
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
        PdkDevice("nfet_06v0", DeviceType.MOS, MosPolarityType.NMOS),
        PdkDevice("pfet_06v0", DeviceType.MOS, MosPolarityType.PMOS),
        PdkDevice("nfet_06v0_nvt", DeviceType.MOS, MosPolarityType.NMOS),
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
        PdkDevice("DEVICE", DeviceType.MOS, MosPolarityType.PMOS),
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
