# from .main import main
from .dialects import (
    DialectSpec,
    DialectSyntaxError,
    Directive,
    NetlistDialect,
    ParsedDeck,
    detect_dialect,
    get_reader,
)
from .netlist_view import NetlistView, NetlistViewLike
from .protocol import SimHandle, SimResult, Simulator
from .spicelib import (
    LTspice_Wrapper,
    Ngspice_Plot_Type,
    NGSpice_Wrapper,
    NgspiceSimHandle,
    NgspiceSimResult,
    Sim_Engines_Type,
    Sim_Execution_Type,
    resolve_ngspice_plot_type,
)

__all__ = [
    'NGSpice_Wrapper', 'LTspice_Wrapper', 'Sim_Execution_Type', 'Sim_Engines_Type',
    'Ngspice_Plot_Type', 'resolve_ngspice_plot_type',
    # The `Simulator` seam: protocols + the ngspice adapters that satisfy them.
    'Simulator', 'SimResult', 'SimHandle', 'NgspiceSimResult', 'NgspiceSimHandle',
    'NetlistView', 'NetlistViewLike',
    'NetlistDialect', 'DialectSpec', 'DialectSyntaxError', 'Directive', 'ParsedDeck',
    'detect_dialect', 'get_reader',
]
