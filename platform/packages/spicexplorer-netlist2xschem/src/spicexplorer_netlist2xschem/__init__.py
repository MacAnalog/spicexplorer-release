"""SpiceXplorer netlist→xschem tool (``spicexplorer_netlist2xschem``).

A **leaf tool** that turns a SPICE netlist into an xschem schematic (``.sch``) — and, when xschem is
available, renders it to PNG/SVG. It reads the netlist through
``spicexplorer_core.spice_engine.NetlistView`` and depends on ``spicexplorer-core`` **only** — never on
a peer tool.

The pipeline is ``ingest → map → place → wire → emit``:

    from spicexplorer_netlist2xschem import from_file, build_sch

    circuit = from_file("ota-improved.spice")          # NetlistView -> N2XCircuit
    doc = build_sch(circuit, pdk="ihp-sg13g2")          # -> SchDocument(text, warnings, ...)
    Path("ota.sch").write_text(doc.text)                # immediately viewable in the UI's xschem viewer

Devices are placed on a grid and pins are wired by net-name label (no auto-router), which is correct
and round-trips through xschem's netlister. ``render`` turns the ``.sch`` into an image via headless
xschem, degrading gracefully to ``.sch``-only when xschem is absent.
"""

from .analysis import TopologyInfo, analyze
from .annotate import annotate_sch
from .annotation import (
    ANNOTATION_SCHEMA,
    BlockAnnotation,
    BlockAnnotationSet,
    annotation_lines,
)
from .connectivity import Route, Seg, Terminal, conflicting_routes, contaminated_nets
from .contract import XschemFromNetlistRequest, XschemSchematicResult, result_from
from .emit import SchDocument, build_sch, to_sch
from .geometry import Transform, apply_transform, snap
from .hierarchy import (
    HierarchicalResult,
    build_hierarchical_sch,
    write_hierarchy,
)
from .ingest import (
    Device,
    DeviceKind,
    MosPolarity,
    N2XCircuit,
    from_file,
    from_string,
    ingest,
)
from .mapping import LABEL_SYMREF, align_pins, port_symref, symref_for
from .placement import (
    GridPlacer,
    PhasedPlacer,
    PlacementHints,
    Placer,
    TopologyPlacer,
)
from .render import RenderResult, render, xschem_available
from .sch_parser import (
    SchBox,
    SchComponent,
    Schematic,
    SchLine,
    SchText,
    SchWire,
    parse_sch,
)
from .stamp import (
    BlockStamp,
    TemplateStampPlacer,
    build_block_stamps,
    resolve_template_sch,
)
from .sym_library import Symbol, SymLibrary, SymPin, parse_symbol
from .symbol_gen import clean_symbol
from .wiring import (
    ConnectionPlan,
    NetLabel,
    PlacedDevice,
    PortPin,
    Wire,
    build_labels,
    plan_connections,
)

__all__ = [
    # ingest
    "Device",
    "DeviceKind",
    "MosPolarity",
    "N2XCircuit",
    "from_file",
    "from_string",
    "ingest",
    # symbols
    "SymLibrary",
    "Symbol",
    "SymPin",
    "parse_symbol",
    # .sch parsing (reverse of emit)
    "Schematic",
    "SchComponent",
    "SchWire",
    "SchBox",
    "SchText",
    "SchLine",
    "parse_sch",
    # geometry
    "Transform",
    "apply_transform",
    "snap",
    # mapping
    "symref_for",
    "align_pins",
    "port_symref",
    "LABEL_SYMREF",
    # analysis
    "analyze",
    "TopologyInfo",
    # connectivity
    "Seg",
    "Terminal",
    "Route",
    "contaminated_nets",
    "conflicting_routes",
    # placement / wiring
    "Placer",
    "PlacementHints",
    "GridPlacer",
    "TopologyPlacer",
    "PhasedPlacer",
    # strategy 2 — template stamping
    "TemplateStampPlacer",
    "BlockStamp",
    "build_block_stamps",
    "resolve_template_sch",
    # strategy 1 — true xschem hierarchy
    "build_hierarchical_sch",
    "write_hierarchy",
    "HierarchicalResult",
    "clean_symbol",
    "NetLabel",
    "Wire",
    "PortPin",
    "PlacedDevice",
    "ConnectionPlan",
    "build_labels",
    "plan_connections",
    # emit
    "build_sch",
    "to_sch",
    "SchDocument",
    # functional-block annotation overlay
    "BlockAnnotation",
    "BlockAnnotationSet",
    "ANNOTATION_SCHEMA",
    "annotation_lines",
    "annotate_sch",
    # render
    "render",
    "RenderResult",
    "xschem_available",
    # contract
    "XschemFromNetlistRequest",
    "XschemSchematicResult",
    "result_from",
]
