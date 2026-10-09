# from .main import main
from .deck_run import DeckRunError, RunResult, deck_digest, run_deck
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
from .save_list import (
    ANALYSIS_KINDS,
    SaveList,
    apply_save_list_to_deck,
    deck_analyses,
    load_save_list,
)
from .sim_log import classify_line, fatal_lines, parse_measures
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
    "NGSpice_Wrapper",
    "LTspice_Wrapper",
    "Sim_Execution_Type",
    "Sim_Engines_Type",
    "Ngspice_Plot_Type",
    "resolve_ngspice_plot_type",
    # The `Simulator` seam: protocols + the ngspice adapters that satisfy them.
    "Simulator",
    "SimResult",
    "SimHandle",
    "NgspiceSimResult",
    "NgspiceSimHandle",
    "NetlistView",
    "NetlistViewLike",
    "NetlistDialect",
    "DialectSpec",
    "DialectSyntaxError",
    "Directive",
    "ParsedDeck",
    "detect_dialect",
    "get_reader",
    # The deck-string lane: text in, run directory out (beside the file-centric wrapper).
    "run_deck",
    "RunResult",
    "DeckRunError",
    "deck_digest",
    # The save list: a YAML override of a deck's `.save`/`save` statements (rawfile storage).
    "ANALYSIS_KINDS",
    "SaveList",
    "apply_save_list_to_deck",
    "deck_analyses",
    "load_save_list",
    # Log-text rules shared with the waveview log panel.
    "classify_line",
    "parse_measures",
    "fatal_lines",
]
