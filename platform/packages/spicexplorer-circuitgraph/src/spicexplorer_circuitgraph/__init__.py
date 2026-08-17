"""SpiceXplorer circuit-graph tool (``spicexplorer_circuitgraph``).

A **leaf tool** that turns a netlist into a typed bipartite circuit graph (nets ⟷ components)
and serializes it to JSON / textual views for downstream (deterministic or LLM) consumption. It
reads the netlist through ``spicexplorer_core.spice_engine.NetlistView`` and depends on
``spicexplorer-core`` **only** — never on a peer tool, never on LangGraph/LangChain.

Typical use (library-first):

    from spicexplorer_core.spice_engine import NetlistView
    from spicexplorer_circuitgraph import CircuitGraph, CircuitGraphDoc

    view = NetlistView.from_file("ota.spice")
    graph = CircuitGraph.from_netlist(view, name="ota")
    serialize(graph, "net_centric", include_params=True)   # an LLM-facing view (pick a strategy)
    evaluate_strategies(graph)                              # compare all views on deterministic metrics
    doc = CircuitGraphDoc.from_graph(graph)                 # round-trippable contract
    graph2 = doc.to_graph()                                 # rebuild from the contract
"""

from spicexplorer_core.spice_engine import NetlistDialect

from ._signatures import MatchOptions
from .annotations import (
    ANNOTATION_SCHEMA,
    export_subcircuit_annotations,
    write_subcircuit_annotations,
)
from .compare import (
    GraphComparison,
    IOPort,
    compare_graphs,
    compare_netlists,
    graphs_equivalent,
    netlists_equivalent,
)
from .contract import CircuitGraphDoc, CircuitGraphMeta, ComponentModel, NetModel, PortModel
from .emit import (
    BaseNetlistEmitter,
    HspiceEmitter,
    NetlistEmitter,
    SpectreEmitter,
    SpiceEmitter,
    to_netlist,
)
from .graph import CircuitGraph
from .match import (
    MirrorGroup,
    SubcircuitMatch,
    annotate_subcircuits,
    find_subcircuits,
    find_template_matches,
    group_matches,
)
from .model.edges import SubcktPort, SubcktPortRole
from .model.nodes import (
    DETERMINISTIC_ROLES,
    RESIDUE_ROLES,
    CircuitStageRole,
    StructuralRole,
    SubCircuitElectricalRole,
    SubcktInstanceNode,
)
from .paths import (
    DiffKind,
    GraphPath,
    PathDiff,
    PathList,
    PathSegment,
    PathStep,
    StepDiffKind,
    diff_paths,
    find_paths_between,
    shortest_paths_between,
)
from .pdk import (
    ANALOGGYM_REF,
    GF180MCU,
    IHP_SG13G2,
    SKYWATER_SKY130,
    GENERIC_N65,
    Pdk,
    PdkDevice,
    get_pdk,
    model_flavor,
    mos_flavor,
    split_flavor,
)
from .port_spec import get_port_spec
from .serialization import (
    Serializer,
    StrategyMetrics,
    evaluate_strategies,
    get_strategy,
    list_strategies,
    register,
    serialize,
    unregister,
)
from .templates import (
    SubcircuitTemplate,
    TemplateLibrary,
    default_current_mirror_library,
    default_miscellaneous_library,
    default_pseudo_resistor_library,
    default_subcircuit_library,
    default_transmission_gate_library,
)
from .translate import TranslatedDesign, translate_ngspice_to_spectre

__all__ = [
    "CircuitGraph",
    "CircuitGraphDoc",
    "CircuitGraphMeta",
    "ComponentModel",
    "NetModel",
    "PortModel",
    "SubcktInstanceNode",
    "SubcktPort",
    "SubcktPortRole",
    # role vocabularies + the deterministic/residue partition (annotation seam)
    "StructuralRole",
    "SubCircuitElectricalRole",
    "CircuitStageRole",
    "DETERMINISTIC_ROLES",
    "RESIDUE_ROLES",
    "to_netlist",
    "NetlistDialect",
    "NetlistEmitter",
    "BaseNetlistEmitter",
    "SpiceEmitter",
    "SpectreEmitter",
    "HspiceEmitter",
    "Pdk",
    "PdkDevice",
    "mos_flavor",
    "model_flavor",
    "split_flavor",
    "IHP_SG13G2",
    "SKYWATER_SKY130",
    "GF180MCU",
    "ANALOGGYM_REF",
    "GENERIC_N65",
    "get_pdk",
    "TranslatedDesign",
    "translate_ngspice_to_spectre",
    "get_port_spec",
    # serialization (Phase 3)
    "serialize",
    "list_strategies",
    "get_strategy",
    "register",
    "unregister",
    "Serializer",
    "evaluate_strategies",
    "StrategyMetrics",
    # comparison (netlist equivalence via labeled graph isomorphism)
    "compare_graphs",
    "compare_netlists",
    "graphs_equivalent",
    "netlists_equivalent",
    "GraphComparison",
    "IOPort",
    "MatchOptions",
    # subcircuit detection (overlay functional templates via subgraph monomorphism)
    "find_subcircuits",
    "find_template_matches",
    "group_matches",
    "annotate_subcircuits",
    "SubcircuitMatch",
    "MirrorGroup",
    # export detected sub-circuits to the neutral xschem block-annotation contract
    "export_subcircuit_annotations",
    "write_subcircuit_annotations",
    "ANNOTATION_SCHEMA",
    # template library
    "TemplateLibrary",
    "SubcircuitTemplate",
    "default_current_mirror_library",
    "default_miscellaneous_library",
    "default_pseudo_resistor_library",
    "default_subcircuit_library",
    "default_transmission_gate_library",
    # path tracing & diffing (net-to-net device paths, structural path diff)
    "find_paths_between",
    "shortest_paths_between",
    "diff_paths",
    "GraphPath",
    "PathList",
    "PathStep",
    "PathDiff",
    "PathSegment",
    "DiffKind",
    "StepDiffKind",
]
