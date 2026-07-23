"""Functional-subcircuit template library.

A *template* is a small, pre-defined functional sub-circuit (e.g. a simple current mirror) that the
matcher (:mod:`match`) overlays onto an input netlist. Templates are catalogued in a YAML manifest
(``spicexplorer/subcircuit-template-library@1``) that gives each a STABLE unique ``id`` and points
at its netlist; matches are tagged with that id.

The library is data-driven and leaf-pure: it reads a manifest the caller chooses. The convenience
:func:`default_current_mirror_library` resolves the hand-authored current-mirror catalogue shipped
under ``<analog-db>/templates/current_mirror`` (``$SPICEXPLORER_ANALOG_DB`` else the
``examples/analog-db`` submodule), but
nothing in the matching core hard-codes that path — point :meth:`TemplateLibrary.from_manifest` at
any catalogue with the same schema.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from spicexplorer_core.spice_engine import NetlistView

from .graph import CircuitGraph

logger = logging.getLogger(__name__)

SCHEMA = "spicexplorer/subcircuit-template-library@1"

# Where the shipped catalogues live, relative to the analog-db corpus root.
_DEFAULT_CM_MANIFEST = "templates/current_mirror/manifest.yaml"
_DEFAULT_MISC_MANIFEST = "templates/miscellaneous/manifest.yaml"
_DEFAULT_PR_MANIFEST = "templates/pseudo_resistor/manifest.yaml"
_DEFAULT_TG_MANIFEST = "templates/transmission_gate/manifest.yaml"


def _analog_db_root() -> Path:
    """The analog-db corpus the shipped template catalogues live in.

    ``$SPICEXPLORER_ANALOG_DB`` (an out-of-tree corpus checkout — the same override the
    optimizer's ``analog_db_root`` honors, restated here because a leaf tool never imports
    a peer) else ``<project_root>/examples/analog-db`` (the submodule).
    """
    import os

    from spicexplorer_core import project_root

    env = os.environ.get("SPICEXPLORER_ANALOG_DB", "").strip()
    if env:
        return Path(env).expanduser()
    return project_root() / "examples/analog-db"


@dataclass
class SubcircuitTemplate:
    """One catalogued functional sub-circuit: a stable id + a netlist + port roles.

    ``ports`` maps a *port role* (``supply`` / ``ref_in`` / ``out`` / ``bias`` / …) to the net name
    used for it inside the template netlist — used after a match to label the host nets, not to drive
    the (name-independent) match itself. The :attr:`graph` is built lazily on first access.

    ``tail_sources`` is the *anchor allow-list* for a dependent (``CM_tail``) template: the ids of the
    current-mirror templates whose output a differential pair's tail may legitimately sit on (a
    physically-correct restriction — an NMOS pair is sunk by an NMOS mirror, never a PMOS one). Empty
    means *any* detected current mirror qualifies (the looser default). See
    :func:`~spicexplorer_circuitgraph.match._admit_anchored`.

    ``match_bulk`` (manifest key ``match_bulk: true``) opts *this template* into bulk-aware matching:
    the matcher keeps MOS bulk/body edges in the projection for this template's embedding test even
    when the global ``match_bulk`` option is off (the detection default). It is a one-way strictness
    knob — it can only *add* the bulk constraint, never remove a globally-requested one. Use it for
    templates whose identity **is** the bulk wiring (a rail-tied transmission gate vs its body-tied
    twin, a pseudo-resistor's isolated-well discriminator); bulk-blind templates are unaffected.

    ``rules_paths`` are the family manifest's registered design-rule documents (the manifest-level
    ``rules:`` block, resolved to absolute paths) — carried per template so a merged library keeps
    each family's pointers. Surfaced to consumers as the annotation contract's ``rules_ref``.
    """

    id: str
    netlist_path: Path
    mirror_class: str = ""
    polarity: str = ""
    role: str = ""
    family: str = ""
    display_name: str = ""
    ports: dict[str, str] = field(default_factory=dict)
    tail_sources: list[str] = field(default_factory=list)
    match_bulk: bool = False  # per-template bulk-aware matching (see the class docstring)
    rules_paths: tuple[Path, ...] = ()  # the family's design-rule doc(s), absolute
    schematic_path: Path | None = None  # hand-drawn xschem .sch of this block (symmetric layout)
    _graph: CircuitGraph | None = field(default=None, repr=False, compare=False)

    def resolved_schematic(self) -> Path | None:
        """The block's hand-drawn ``.sch``, used by downstream schematic *stamping*.

        Prefers an explicit ``schematic`` manifest key; otherwise derives it from the netlist by the
        catalogue convention (the runnable deck lives in a ``simulation/`` subdir beside the schematic,
        e.g. ``…/nmos_current_sink/simulation/basic_current_mirror.spice`` ↔
        ``…/nmos_current_sink/basic_current_mirror.sch``). Returns the path only when it exists, else
        ``None`` — the renderer just falls back to algorithmic placement for that block."""
        candidates: list[Path] = []
        if self.schematic_path is not None:
            candidates.append(self.schematic_path)
        np = self.netlist_path
        if np.parent.name == "simulation":
            candidates.append(np.parent.parent / f"{np.stem}.sch")
        candidates.append(np.with_suffix(".sch"))
        return next((c for c in candidates if c.is_file()), None)

    @property
    def graph(self) -> CircuitGraph:
        """The template's :class:`CircuitGraph` (built once, cached).

        No PDK is passed: polarity resolves from the ``nmos``/``pmos`` substring in the model name,
        so a template authored with IHP ``sg13_lv_*`` and a target authored with neutral
        ``nmos``/``pmos`` tokens both classify identically.
        """
        if self._graph is None:
            if not self.netlist_path.exists():
                raise FileNotFoundError(
                    f"template {self.id!r}: netlist not found at {self.netlist_path}"
                )
            view = NetlistView.from_file(self.netlist_path)
            self._graph = CircuitGraph.from_netlist(view, name=self.id)
        return self._graph

    @property
    def device_count(self) -> int:
        return self.graph.component_count


class TemplateLibrary:
    """An ordered collection of :class:`SubcircuitTemplate`, loaded from a manifest."""

    def __init__(self, templates: list[SubcircuitTemplate], *, family: str = "") -> None:
        self.family = family
        self._templates = list(templates)
        ids = [t.id for t in self._templates]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ValueError(f"duplicate template id(s) in library: {sorted(dupes)}")
        self._by_id = {t.id: t for t in self._templates}

    # --- construction --------------------------------------------------------------------------
    @classmethod
    def from_manifest(cls, manifest_path: str | Path) -> "TemplateLibrary":
        """Load a template library from a ``subcircuit-template-library`` YAML manifest.

        Netlist paths in the manifest are resolved relative to the manifest's own directory.
        """
        path = Path(manifest_path)
        if not path.exists():
            raise FileNotFoundError(f"template manifest not found: {path}")
        data = yaml.safe_load(path.read_text()) or {}
        schema = data.get("schema", "")
        if schema != SCHEMA:
            logger.warning(
                "template manifest %s has schema %r (expected %r); proceeding best-effort",
                path,
                schema,
                SCHEMA,
            )
        family = data.get("family", "")
        base = path.parent
        # The manifest-level `rules:` block — the family's design-rule doc registrations. Optional
        # (older/rules-less manifests simply carry none); resolved against the manifest dir and
        # attached to every template of this family so a merged library keeps per-family pointers.
        rules_paths = tuple(
            (base / entry["path"]).resolve()
            for entry in data.get("rules", []) or []
            if isinstance(entry, dict) and entry.get("path")
        )
        templates: list[SubcircuitTemplate] = []
        for entry in data.get("templates", []):
            tid = entry.get("id")
            netlist = entry.get("netlist")
            if not tid or not netlist:
                logger.warning("skipping template entry missing id/netlist: %r", entry)
                continue
            schematic = entry.get("schematic")
            templates.append(
                SubcircuitTemplate(
                    id=tid,
                    netlist_path=(base / netlist).resolve(),
                    mirror_class=entry.get("class", ""),
                    polarity=entry.get("polarity", ""),
                    role=entry.get("role", ""),
                    family=entry.get("family", family),
                    display_name=entry.get("display_name", ""),
                    ports=dict(entry.get("ports", {})),
                    tail_sources=list(entry.get("tail_sources", [])),
                    match_bulk=bool(entry.get("match_bulk", False)),
                    rules_paths=rules_paths,
                    schematic_path=(base / schematic).resolve() if schematic else None,
                )
            )
        if not templates:
            raise ValueError(f"template manifest {path} defined no usable templates")
        return cls(templates, family=family)

    @classmethod
    def merge(cls, *libraries: "TemplateLibrary", family: str = "") -> "TemplateLibrary":
        """Concatenate several libraries into one (preserving order; ids must stay unique).

        Used to assemble the full shipped catalogue (current mirrors + miscellaneous) into a single
        library so :func:`~spicexplorer_circuitgraph.match.find_subcircuits` can resolve cross-family
        dependencies (e.g. a differential pair anchored to a current-mirror output) in one pass. The
        duplicate-id guard in :meth:`__init__` still applies across the combined set.
        """
        templates = [t for lib in libraries for t in lib]
        return cls(templates, family=family)

    # --- access --------------------------------------------------------------------------------
    @property
    def templates(self) -> list[SubcircuitTemplate]:
        return list(self._templates)

    def get(self, template_id: str) -> SubcircuitTemplate:
        return self._by_id[template_id]

    def filter(
        self, *, polarity: str | None = None, mirror_class: str | None = None
    ) -> list[SubcircuitTemplate]:
        """Templates narrowed by polarity and/or class (both case-insensitive)."""
        out = self._templates
        if polarity is not None:
            out = [t for t in out if t.polarity.lower() == polarity.lower()]
        if mirror_class is not None:
            out = [t for t in out if t.mirror_class.lower() == mirror_class.lower()]
        return list(out)

    def __iter__(self):
        return iter(self._templates)

    def __len__(self) -> int:
        return len(self._templates)

    def __repr__(self) -> str:
        return f"TemplateLibrary(family={self.family!r}, {len(self)} templates)"


def default_current_mirror_library() -> TemplateLibrary:
    """The hand-authored current-mirror catalogue shipped with the platform examples.

    Resolves ``templates/current_mirror/manifest.yaml`` against the analog-db corpus root
    (``$SPICEXPLORER_ANALOG_DB`` else ``<project_root>/examples/analog-db``). Raises :class:`FileNotFoundError` when the examples tree
    is not present (e.g. a packaged install without the examples) — pass an explicit manifest to
    :meth:`TemplateLibrary.from_manifest` in that case.
    """
    return TemplateLibrary.from_manifest(_analog_db_root() / _DEFAULT_CM_MANIFEST)


def default_miscellaneous_library() -> TemplateLibrary:
    """The hand-authored *miscellaneous* catalogue (differential pairs, …) shipped with the examples.

    Resolves ``templates/miscellaneous/manifest.yaml`` against the analog-db corpus root
    (``$SPICEXPLORER_ANALOG_DB`` else ``<project_root>/examples/analog-db``). Some of its templates are *dependent* — a differential pair
    declares a ``CM_tail`` port that the matcher only admits when it lands on a detected current-mirror
    output — so this catalogue is normally matched alongside the current mirrors (see
    :func:`default_subcircuit_library`). Raises :class:`FileNotFoundError` when the examples tree is
    not present.
    """
    return TemplateLibrary.from_manifest(_analog_db_root() / _DEFAULT_MISC_MANIFEST)


def default_pseudo_resistor_library() -> TemplateLibrary:
    """The hand-authored *pseudo-resistor* catalogue (Guglielmi 2020 series cells) shipped with the
    examples.

    Resolves ``templates/pseudo_resistor/manifest.yaml`` against the analog-db corpus root
    (``$SPICEXPLORER_ANALOG_DB`` else ``<project_root>/examples/analog-db``). All templates are independent (no ``CM_tail`` anchoring);
    matched devices are tagged :attr:`~spicexplorer_circuitgraph.model.nodes.StructuralRole.MOS_PSEUDO_RESISTOR`.
    Raises :class:`FileNotFoundError` when the examples tree is not present.
    """
    return TemplateLibrary.from_manifest(_analog_db_root() / _DEFAULT_PR_MANIFEST)


def default_transmission_gate_library() -> TemplateLibrary:
    """The hand-authored *transmission-gate* catalogue (the CMOS pass pair) shipped with the examples.

    Resolves ``templates/transmission_gate/manifest.yaml`` against the analog-db corpus root
    (``$SPICEXPLORER_ANALOG_DB`` else ``<project_root>/examples/analog-db``). The canonical ``tg.pair.cmos`` template is bulk-blind (it
    recognises both bulk styles); a catalogue that additionally registers the rail-tied variant with
    ``match_bulk: true`` splits the two drawings apart (the bulk-strict variant wins as the primary on
    a rail-bulk host, the bulk-blind one is kept as its alternate — see ``match.group_matches``).
    Matched devices are tagged :attr:`~spicexplorer_circuitgraph.model.nodes.StructuralRole.MOS_ANALOG_SWITCH`.
    Raises :class:`FileNotFoundError` when the examples tree is not present.
    """
    return TemplateLibrary.from_manifest(_analog_db_root() / _DEFAULT_TG_MANIFEST)


def default_subcircuit_library() -> TemplateLibrary:
    """The full shipped catalogue: current mirrors + miscellaneous + pseudo-resistors +
    transmission gates, merged into one library.

    This is the default library used by :func:`~spicexplorer_circuitgraph.match.find_subcircuits`.
    Combining the families in a single library is what lets dependent templates resolve against the
    independently-detected ones in the same pass — e.g. a differential pair (``CM_tail`` port) is only
    reported when its tail node is a current-mirror output found in the same host.
    """
    libraries = [default_current_mirror_library(), default_miscellaneous_library()]
    # The pseudo-resistor / transmission-gate catalogues were *rules-only* manifests (an empty
    # `templates:` list, which `from_manifest` rejects) before their first designs landed in
    # analog-db. Tolerate that state so a checkout whose analog-db submodule predates the designs
    # still gets the core catalogue instead of a crash; a missing examples tree entirely still
    # raises FileNotFoundError above, matching the historical behaviour.
    for loader in (default_pseudo_resistor_library, default_transmission_gate_library):
        try:
            libraries.append(loader())
        except ValueError as exc:
            logger.warning("skipping optional template family (%s): %s", loader.__name__, exc)
    return TemplateLibrary.merge(*libraries, family="subcircuit")
