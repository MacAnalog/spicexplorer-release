"""Cross-PDK binding generator.

Given a circuit that is already bound to one PDK, synthesize the binding for ANOTHER PDK so a
clone is ready-to-run in *both* — no post-processing. ``add_binding(circuit, target_pdk)`` writes

  pdk/<target>/devices.map.yaml   generic kind -> the target PDK's default device per polarity
  pdk/<target>/corners.yaml       the target PDK's corner libs (from the _shared registry)
  pdk/<target>/sizing.yaml        the source sizing CONVERTED into the target unit convention

and appends ``<target>`` to circuit.yaml's ``pdks`` list (preserving comments). The lowered
``pdk/<target>/netlist.spice`` is produced afterwards by ``analog-db generate`` (it iterates the
manifest's ``pdks``); Tier 1 then drift-guards it.

**The unit convention (the one real subtlety).** sky130 ngspice runs with ``.option scale=1u`` —
its sizing W/L are BARE microns; IHP geometry is in meters written with a ``u`` suffix. So a
geometry value ``1`` (sky130, = 1 µm) is ``1u`` (IHP), and vice-versa (``_shared/PDK_SIM.md``).
Conversion canonicalizes every geometry value to microns, clamps defaults/min-bounds up to the
target PDK's W/L bin floor (a device below the bin won't simulate), and re-emits in the target's
notation. Everything else — the ``M`` multiplier, capacitances (F), bias currents (A), bias
voltages (V), integer finger counts — is PDK-independent and carried verbatim.

This is a dev-time tool (the produced files are committed); it is not on any runtime path.
"""

from __future__ import annotations

import re
from typing import Any

import yaml

from . import pdks
from .model import Circuit

# PDKs whose ngspice decks apply `.option scale=1u`, so sizing W/L are bare microns (no 'u').
# Every other PDK (ihp-sg13g2) writes geometry explicitly in meters with a 'u' suffix.
_SCALE_UM_PDKS = {"sky130"}

# The default device per polarity in a _shared/pdk/<pdk>.yaml `devices` map, in preference order
# (low-voltage / core variant first), e.g. ihp {lv,hv} -> lv, sky130 {core,io} -> core.
_PREFERRED_DEVICE_KEYS = ("lv", "core")


class BindingError(ValueError):
    pass


def _num(um: float) -> float | int:
    """A clean numeric microns value (int when integral) for the bare-µm (sky130) notation."""
    return int(um) if float(um).is_integer() else um


def _fmt(um: float) -> str:
    """A clean decimal string for the explicit-µm (IHP) notation: 27.241, 0.13, 1, 200."""
    return f"{um:.6g}"


def _to_um(value: Any) -> float:
    """A geometry value as microns. sky130 = bare microns; IHP = microns with a trailing 'u'."""
    s = str(value).strip().lower()
    if s.endswith("u"):
        s = s[:-1].strip()
    return float(s)


def _emit_um(um: float, target_pdk: str) -> float | int | str:
    """Re-emit a microns value in the target PDK's notation (bare number vs 'Nu' string)."""
    if target_pdk in _SCALE_UM_PDKS:
        return _num(um)
    return f"{_fmt(um)}u"


def _geom_kind(var: dict[str, Any]) -> str | None:
    """``'w'``/``'l'`` if this knob is a transistor width/length, else ``None`` (PDK-independent).

    In-repo OTAs tag geometry with ``unit: m`` (names like ``x_dut_..._w``); AnalogGym role-encodes
    it in the symbol (``MOSFET_.._W_..`` / ``_L_``). ``M``/cap/current/voltage/fingers are neither.
    """
    name = var["name"]
    if var.get("unit") == "m":                       # in-repo OTA geometry (meters)
        if re.search(r"_w(_|$)", name):
            return "w"
        if re.search(r"_l(_|$)", name):
            return "l"
        return "w"                                   # a unit:m knob is geometry; default to W floor
    if re.search(r"_W_", name):                      # AnalogGym role-encoded geometry
        return "w"
    if re.search(r"_L_", name):
        return "l"
    # lowercase conventions: leading ``w_``/``l_`` knobs (w_in, l_load), lowercase
    # role-encoded ``..._w_...`` (mosfet_0_8_w_biascm_pmos), and the P4 atomic field
    # suffix on unit-less rows inherited from AnalogGym imports (``x_dut_xm12_w``)
    if re.search(r"^w_|_w_|_w$", name):
        return "w"
    if re.search(r"^l_|_l_|_l$", name):
        return "l"
    return None


def _bin_floor(registry: dict[str, Any]) -> dict[str, float]:
    """The target PDK's minimum W/L in microns (below the bin, models don't evaluate)."""
    geom = registry.get("geometry", {})
    return {"w": _to_um(geom.get("min_w", 0)), "l": _to_um(geom.get("min_l", 0))}


def _convert_var(var: dict[str, Any], target_pdk: str, floor: dict[str, float]) -> dict[str, Any]:
    """One sizing variable converted to the target PDK (geometry re-noted + bin-clamped)."""
    kind = _geom_kind(var)
    if kind is None:
        return dict(var)                             # PDK-independent — carry verbatim
    out = dict(var)
    for field in ("default", "min", "max"):
        if out.get(field) in (None, ""):
            continue
        um = _to_um(out[field])
        if field != "max":                           # clamp default + lower bound up to the bin
            um = max(um, floor[kind])
        out[field] = _emit_um(um, target_pdk)
    return out


def convert_sizing(
    source_sizing: dict[str, Any], target_pdk: str, target_registry: dict[str, Any]
) -> dict[str, Any]:
    """The source ``sizing.yaml`` dict converted to ``target_pdk`` (order preserved)."""
    floor = _bin_floor(target_registry)
    return {
        "schema": "spicexplorer/sizing@1",
        "pdk": target_pdk,
        "variables": [_convert_var(v, target_pdk, floor) for v in source_sizing.get("variables", [])],
    }


def _device_models(registry: dict[str, Any]) -> dict[str, str]:
    """{nmos, pmos} default device names from a _shared/pdk registry (lv/core variant)."""
    out: dict[str, str] = {}
    for pol in ("nmos", "pmos"):
        spec = registry["devices"][pol]
        if isinstance(spec, dict):
            out[pol] = next((spec[k] for k in _PREFERRED_DEVICE_KEYS if k in spec), next(iter(spec.values())))
        else:
            out[pol] = spec
    return out


def _devices_map_yaml(target_pdk: str, registry: dict[str, Any]) -> str:
    m = _device_models(registry)
    return (
        f"# Generic device kind -> {target_pdk} device name. Cross-PDK binding generated by\n"
        f"# `analog-db add-binding` (per-topology override of circuitgraph's built-in table).\n"
        f"pdk: {target_pdk}\ndevices:\n"
        f"  nmos: {{model: {m['nmos']}}}\n"
        f"  pmos: {{model: {m['pmos']}}}\n"
    )


def _passive_corner_entries(registry: dict[str, Any], corner: str) -> list[str]:
    """The extra ``{lib_file, section}`` entries for the PDK passive (R/C) corner libs.

    From the registry's ``passives.libs`` block — additive lines appended after the MOS bundle so
    a netlist instancing a PDK resistor/cap resolves its models (empty for a PDK whose MOS corner
    sections already carry the passives, e.g. sky130).
    """
    entries: list[str] = []
    libs = (registry.get("passives") or {}).get("libs") or {}
    for kind in ("res", "cap"):
        blk = libs.get(kind)
        if not blk:
            continue
        sections = [*blk["per_corner"].get(corner, []), *blk.get("post_sections", [])]
        entries += [f"    - {{lib_file: {blk['lib_file']}, section: {s}}}" for s in sections]
    return entries


def _corners_yaml(target_pdk: str, registry: dict[str, Any]) -> str:
    cfg = registry["corners"]
    lib = cfg["lib_file"]
    head = [
        f"# Corner bundles for {target_pdk} (D-6): PDK libs stay out-of-repo, referenced by",
        "# lib_file (+ section). Cross-PDK binding generated by `analog-db add-binding`.",
        f"pdk: {target_pdk}",
        "corners:",
    ]
    lines: list[str] = []
    if "per_corner" in cfg:
        # Per-device corner sections (gf180): each corner is, in order, the sectionless includes
        # (global stat/noise switches), the corner-independent pre_sections (e.g. noise_corner —
        # its params are referenced by the model cards, so it must load FIRST), the corner's
        # per-device model sections, then the post_sections (the device subckts).
        includes = cfg.get("includes", [])
        pre = cfg.get("pre_sections", [])
        post = cfg.get("post_sections", [])
        for name, sections in cfg["per_corner"].items():
            lines.append(f"  {name}:")
            lines += [f"    - {{lib_file: {inc}}}" for inc in includes]
            lines += [f"    - {{lib_file: {lib}, section: {s}}}" for s in [*pre, *sections, *post]]
            lines += _passive_corner_entries(registry, name)
    else:
        # Single corner lib with one section per corner (ihp/sky130); strip a `mos_` section prefix.
        for section in cfg["sections"]:
            name = section[4:] if section.startswith("mos_") else section
            passive = _passive_corner_entries(registry, name)
            if passive:
                lines.append(f"  {name}:")
                lines.append(f"    - {{lib_file: {lib}, section: {section}}}")
                lines += passive
            else:
                lines.append(f"  {name}: [{{lib_file: {lib}, section: {section}}}]")
    return "\n".join([*head, *lines, "default_corner: tt"]) + "\n"


def _sizing_yaml(sizing: dict[str, Any], source_pdk: str, target_pdk: str) -> str:
    body = yaml.safe_dump(sizing, sort_keys=False, width=100)
    return (
        f"# Sizing for the {target_pdk} binding — generated by `analog-db add-binding` from the\n"
        f"# {source_pdk} sizing (geometry re-noted to {target_pdk}'s unit convention + bin-clamped).\n"
        f"# A starting point; re-tune defaults/bounds for {target_pdk} device physics as needed.\n"
        + body
    )


def _add_pdk_to_manifest(circuit: Circuit, target_pdk: str) -> None:
    """Append ``target_pdk`` to circuit.yaml's ``pdks`` list, preserving comments/formatting.

    Handles both the flow form (``pdks: [a, b]``) and the block form (``pdks:`` then ``- a``).
    """
    path = circuit.dir / "circuit.yaml"
    lines = path.read_text().splitlines()
    out: list[str] = []
    done = False
    i = 0
    while i < len(lines):
        ln = lines[i]
        flow = re.match(r"^(\s*pdks:\s*)\[([^\]]*)\](.*)$", ln)   # `pdks: [a, b]  # optional comment`
        block = re.match(r"^(\s*)pdks:\s*$", ln)
        if flow and not done:
            items = [x.strip() for x in flow.group(2).split(",") if x.strip()]
            items.append(target_pdk)
            out.append(f"{flow.group(1)}[{', '.join(items)}]{flow.group(3)}")
            done = True
            i += 1
        elif block and not done:
            out.append(ln)
            indent = block.group(1)
            i += 1
            while i < len(lines) and re.match(rf"^{indent}-\s+\S", lines[i]):
                out.append(lines[i])
                i += 1
            out.append(f"{indent}- {target_pdk}")
            done = True
        else:
            out.append(ln)
            i += 1
    if not done:
        raise BindingError(f"{path}: no `pdks:` key to extend")
    path.write_text("\n".join(out) + "\n")


def add_binding(circuit: Circuit, target_pdk: str, source_pdk: str | None = None) -> list[str]:
    """Synthesize the ``target_pdk`` binding for ``circuit`` from an existing one.

    Writes devices.map/corners/sizing under ``pdk/<target_pdk>/`` and registers the PDK in
    circuit.yaml. Returns the relative paths written. Run ``analog-db generate`` afterwards to
    emit the lowered ``netlist.spice``. Raises ``BindingError`` if the PDK is already bound, no
    source binding exists, or the target PDK has no ``_shared/pdk/<target>.yaml`` registry.
    """
    if target_pdk in circuit.pdks:
        raise BindingError(f"{circuit.id}: pdk {target_pdk!r} already bound")
    source_pdk = source_pdk or (circuit.pdks[0] if circuit.pdks else None)
    if source_pdk is None:
        raise BindingError(f"{circuit.id}: no source pdk binding to convert from")
    if target_pdk not in pdks.registry_ids():
        raise BindingError(f"{target_pdk!r}: no _shared/pdk/{target_pdk}.yaml registry")

    registry = pdks.load_registry(target_pdk)
    bdir = circuit.dir / "pdk" / target_pdk
    bdir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []

    (bdir / "devices.map.yaml").write_text(_devices_map_yaml(target_pdk, registry))
    (bdir / "corners.yaml").write_text(_corners_yaml(target_pdk, registry))
    new_sizing = convert_sizing(circuit.sizing(source_pdk), target_pdk, registry)
    (bdir / "sizing.yaml").write_text(_sizing_yaml(new_sizing, source_pdk, target_pdk))
    for name in ("devices.map.yaml", "corners.yaml", "sizing.yaml"):
        written.append(str((bdir / name).relative_to(circuit.dir)))

    _add_pdk_to_manifest(circuit, target_pdk)
    written.append("circuit.yaml")
    return written
