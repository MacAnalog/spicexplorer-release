"""Export detected functional sub-circuits to the neutral *xschem block-annotation* contract.

A **producer** for the ``spicexplorer/xschem-block-annotations@1`` schema that the schematic generator
``spicexplorer-netlist2xschem`` consumes to draw labelled boxes around recognised blocks (current
mirrors, differential pairs, …). This module only serialises *this* package's own match results — it
never imports the peer tool; the JSON schema is the single point of coupling, so the detector and the
renderer evolve independently as long as both honour the schema.

The mapping from a resolved :class:`~spicexplorer_circuitgraph.match.MirrorGroup` to blocks:

* the group itself → one top-level *block* (``parent_id = None``), its ``alternates`` folded into the
  block's ``alternates`` list (other templates matching the *same* devices);
* each :attr:`~spicexplorer_circuitgraph.match.MirrorGroup.subsumed` match (e.g. the simple sub-mirror
  inside a cascode) → a *nested* block whose ``parent_id`` is the group's id, so the renderer draws it
  as an inner box.

Typical use (the producer half of the detect → annotate → render pipeline)::

    from spicexplorer_circuitgraph import (
        CircuitGraph, find_subcircuits, group_matches, write_subcircuit_annotations,
    )

    graph = CircuitGraph.from_netlist(view, name="ota")
    groups = group_matches(find_subcircuits(graph))
    write_subcircuit_annotations(groups, "ota.blocks.json")   # → feed to netlist2xschem --annotations
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .graph import CircuitGraph
from .match import MirrorGroup, SubcircuitMatch
from .templates import TemplateLibrary, default_subcircuit_library

logger = logging.getLogger(__name__)

__all__ = [
    "ANNOTATION_SCHEMA",
    "export_subcircuit_annotations",
    "write_subcircuit_annotations",
]

# The neutral contract this module emits — kept byte-identical to the consumer's
# ``spicexplorer_netlist2xschem.ANNOTATION_SCHEMA`` (the two packages share the string, not an import).
ANNOTATION_SCHEMA = "spicexplorer/xschem-block-annotations@1"


def _human_label(
    family: str, polarity: str, mirror_class: str, *, n_outputs: int | None = None
) -> str:
    """A descriptive, downstream-friendly block label.

    Built as ``"<POLARITY> <Class> <Family>"`` in title case — e.g. ``"NMOS Cascode Current Mirror"``,
    ``"PMOS Simple Current Mirror"``, ``"NMOS Differential Pair"`` — so a reader (or an LLM consuming
    the contract) gets the device polarity, the specific topology, and the block family at a glance.
    The polarity stays fully upper-cased (``NMOS``/``PMOS``); the class qualifier is dropped when it
    merely repeats the family (a differential pair's class *is* ``differential_pair``). For a mirror
    that feeds more than one output an ``(N outputs)`` suffix makes the ``1:N`` fan-out explicit."""
    fam = (family or "block").replace("_", " ").title()
    parts: list[str] = []
    if polarity:
        parts.append(polarity.upper())
    if mirror_class and mirror_class != family:
        parts.append(mirror_class.replace("_", " ").title())
    parts.append(fam)
    label = " ".join(parts)
    if n_outputs and n_outputs > 1:
        label += f" ({n_outputs} outputs)"
    return label


def _port_names(rep_ports: dict[str, str], matches: tuple[SubcircuitMatch, ...]) -> dict[str, str]:
    """Map each of a block's **boundary host nets** to its template **port name** (``supply`` /
    ``ref_in`` / ``out`` / ``in_p`` / ``in_n`` / ``CM_tail`` / ``bias`` / …).

    ``rep_ports`` is the group's representative ``port-role → host-net`` map; ``matches`` are the group's
    member matches (just the match itself for a subsumed sub-block), each carrying its own ``ports``. A
    mirror that fans out to several outputs has one ``out`` *role* spread over many host nets — its extra
    copies are numbered ``out_2``, ``out_3``, … (the "increment per extra output" convention), so the
    renderer can label every pin even when the template declares the role once. Deterministic: the
    representative net keeps the bare role, the remaining nets follow in sorted order; the first role
    (sorted) to claim a shared net wins."""
    role_nets: dict[str, list[str]] = {role: [net] for role, net in rep_ports.items()}
    for m in matches:
        for role, net in m.ports.items():
            role_nets.setdefault(role, [])
            if net not in role_nets[role]:
                role_nets[role].append(net)
    names: dict[str, str] = {}
    for role in sorted(role_nets):
        nets = role_nets[role]
        for i, net in enumerate([nets[0], *sorted(nets[1:])]):
            names.setdefault(net, role if i == 0 else f"{role}_{i + 1}")
    return names


def _device_slots(matches: tuple[SubcircuitMatch, ...]) -> dict[str, str]:
    """Map each host device → the template device-slot it fills, unioned across a group's members.

    The inverse of a match's ``device_map`` (template → host). The *host → template* direction is the
    one a stamping renderer needs and the only one that stays well-defined for a multi-output mirror:
    its N copies all fill the template's single output slot, so a template → host dict would collide,
    but every host device maps to exactly one slot. Used by ``netlist2xschem`` to lay each host device
    at its template's symmetric coordinate. Deterministic (sorted)."""
    slots: dict[str, str] = {}
    for m in matches:
        for tpl_dev, host_dev in m.device_map.items():
            slots.setdefault(host_dev, tpl_dev)
    return {h: slots[h] for h in sorted(slots)}


def _block_roles(devices: tuple[str, ...], role_index: dict[str, str]) -> dict[str, str]:
    """The block's per-device deterministic roles: host device → ``StructuralRole`` value.

    Read from the annotated graph's ``structural_role`` overlay (``role_index``); devices the
    deterministic pass left untagged are simply absent, so the map never invents a role."""
    return {d: role_index[d] for d in sorted(devices) if d in role_index}


def _match_block(
    match: SubcircuitMatch,
    *,
    block_id: str,
    parent_id: str | None,
    sch_index: dict[str, str],
    rules_index: dict[str, list[str]],
    role_index: dict[str, str],
) -> dict:
    """Serialise one raw match (a subsumed sub-block) to a block entry."""
    return {
        "block_id": block_id,
        "devices": list(match.devices),
        "label": _human_label(
            match.family, match.polarity, match.mirror_class, n_outputs=len(match.output_devices)
        ),
        "family": match.family,
        "parent_id": parent_id,
        "alternates": [],
        "template_id": match.template_id,
        "role": match.mirror_class,
        "polarity": match.polarity,
        "template_sch": sch_index.get(match.template_id, ""),
        "device_slots": _device_slots((match,)),
        "port_names": _port_names(match.ports, (match,)),
        "rules_ref": list(rules_index.get(match.template_id, [])),
        "roles": _block_roles(match.devices, role_index),
    }


def _group_blocks(
    group: MirrorGroup,
    sch_index: dict[str, str],
    rules_index: dict[str, list[str]],
    role_index: dict[str, str],
) -> list[dict]:
    """A resolved group → its top-level block plus one nested block per subsumed match."""
    blocks = [
        {
            "block_id": group.group_id,
            "devices": list(group.devices),
            "label": _human_label(
                group.family,
                group.polarity,
                group.mirror_class,
                n_outputs=len(group.output_devices),
            ),
            "family": group.family,
            "parent_id": None,
            "alternates": [alt.template_id for alt in group.alternates],
            "template_id": group.template_id,
            "role": group.mirror_class,
            "polarity": group.polarity,
            "template_sch": sch_index.get(group.template_id, ""),
            "device_slots": _device_slots(group.members),
            "port_names": _port_names(group.ports, group.members),
            "rules_ref": list(rules_index.get(group.template_id, [])),
            "roles": _block_roles(group.devices, role_index),
        }
    ]
    for idx, sub in enumerate(group.subsumed):
        blocks.append(
            _match_block(
                sub,
                block_id=f"{group.group_id}::sub{idx}:{sub.template_id}",
                parent_id=group.group_id,
                sch_index=sch_index,
                rules_index=rules_index,
                role_index=role_index,
            )
        )
    return blocks


def _root_relative(path: Path, root: Path | None) -> str:
    """``path`` relative to the workspace root when it lives under it, else absolute."""
    if root is not None:
        try:
            return str(path.relative_to(root))
        except ValueError:  # lives outside the workspace root — emit it absolute
            pass
    return str(path)


def _template_indexes(
    groups: list[MirrorGroup], library: TemplateLibrary | None
) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Per-template lookup tables for the block entries, both workspace-root-relative:

    * ``template_id → block-template .sch path`` — the hand-drawn symmetric layout shipped beside
      each template, used by the renderer for *stamping*;
    * ``template_id → [design-rule doc path, …]`` — the family manifest's registered ``rules:``
      docs (``rules_ref``), so a downstream agent resolves "what do I do with this block" from data.

    Paths are emitted relative to ``spicexplorer_core.project_root()`` so the consumer (a peer that
    never imports this package) resolves them against *its* root — the JSON contract stays the only
    coupling. Resolved only for the template ids actually present; absent schematics/rules (or a
    packaged install without the examples tree) simply yield no entry, and consumers degrade."""
    needed = {g.template_id for g in groups} | {
        s.template_id for g in groups for s in g.subsumed
    }
    if not needed:
        return {}, {}
    try:
        lib = library if library is not None else default_subcircuit_library()
    except Exception as exc:  # examples tree absent / manifest unreadable — degrade gracefully
        logger.debug("no template library for schematic/rules resolution: %s", exc)
        return {}, {}
    try:
        from spicexplorer_core import project_root

        root = project_root()
    except Exception:  # pragma: no cover - root marker absent
        root = None
    sch_index: dict[str, str] = {}
    rules_index: dict[str, list[str]] = {}
    by_id = {t.id: t for t in lib}
    for tid in needed:
        tpl = by_id.get(tid)
        if tpl is None:
            continue
        sch = tpl.resolved_schematic()
        if sch is not None:
            sch_index[tid] = _root_relative(sch, root)
        rules = [_root_relative(p, root) for p in tpl.rules_paths if p.is_file()]
        if rules:
            rules_index[tid] = rules
    return sch_index, rules_index


def export_subcircuit_annotations(
    source: CircuitGraph | list[MirrorGroup] | tuple[MirrorGroup, ...],
    *,
    library: TemplateLibrary | None = None,
) -> dict:
    """Serialise detected sub-circuits to the ``xschem-block-annotations@1`` dict.

    ``source`` is either a list of resolved :class:`~spicexplorer_circuitgraph.match.MirrorGroup`
    (from :func:`~spicexplorer_circuitgraph.group_matches`) or an *annotated* ``CircuitGraph`` whose
    ``subcircuit_matches`` overlay was populated by
    :func:`~spicexplorer_circuitgraph.annotate_subcircuits`. The returned dict is ready to
    ``json.dump`` and feed to ``netlist2xschem``'s ``--annotations`` (the device names are the host
    instance refs — the join key to the schematic).

    Each block additionally carries (additive, schema still ``@1``) a ``template_sch`` — the path to the
    block's hand-drawn symmetric layout, relative to the workspace root — and ``device_slots`` mapping
    every host device to the template device-slot it fills. Together they let the renderer *stamp* the
    template's symmetric geometry onto the host devices (differential branches drawn symmetrically)
    instead of placing the block algorithmically. ``library`` overrides the template catalogue used to
    resolve those paths (defaults to the full shipped catalogue); the fields are simply omitted when no
    template schematic is available, so a consumer that ignores them is unaffected.

    A ``port_names`` map (boundary host net → the template's **functional port name**: ``supply`` /
    ``ref_in`` / ``out`` / ``in_p`` / …) is also carried, with a fanned-out mirror's extra outputs
    numbered ``out_2``, ``out_3``, … — so a renderer drawing a block as a subcircuit symbol can label its
    pins by what they *are* (``out``, ``ref_in``) rather than by the host net that happens to land on them.

    Two further additive-optional fields surface the governing design knowledge per block (schema
    still ``@1``):

    * ``rules_ref`` — the workspace-root-relative path(s) of the family manifest's registered
      design-rule doc(s) (the manifest ``rules:`` block), so a downstream symmetry/sizing/layout
      agent resolves "what do I do with this block" from data. Empty when the catalogue carries no
      rules (or the examples tree is absent).
    * ``roles`` — the per-device **deterministic** structural roles (host device →
      :class:`~spicexplorer_circuitgraph.model.nodes.StructuralRole` value, e.g.
      ``current_mirror_reference``) that :func:`~spicexplorer_circuitgraph.annotate_subcircuits`
      assigned. Populated only when ``source`` is an *annotated* ``CircuitGraph`` (the roles live on
      its components); exporting a bare group list — where no role pass ran — leaves it ``{}``.
      Consumers must treat present roles as ground truth (see ``DETERMINISTIC_ROLES``).
    """
    if isinstance(source, CircuitGraph):
        groups = source.subcircuit_matches
        role_index = {
            c.name: role.value
            for c in source.get_components()
            if (role := getattr(c, "structural_role", None)) is not None
        }
    else:
        groups, role_index = list(source), {}
    sch_index, rules_index = _template_indexes(groups, library)
    blocks = [
        block
        for group in groups
        for block in _group_blocks(group, sch_index, rules_index, role_index)
    ]
    return {"schema": ANNOTATION_SCHEMA, "blocks": blocks}


def write_subcircuit_annotations(
    source: CircuitGraph | list[MirrorGroup] | tuple[MirrorGroup, ...],
    path: str | Path,
    *,
    library: TemplateLibrary | None = None,
) -> Path:
    """Write :func:`export_subcircuit_annotations` to ``path`` as pretty JSON; return the path."""
    out = Path(path)
    out.write_text(json.dumps(export_subcircuit_annotations(source, library=library), indent=2) + "\n")
    return out
