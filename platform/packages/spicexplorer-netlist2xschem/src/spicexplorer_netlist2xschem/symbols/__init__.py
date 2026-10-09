"""Generated-symbol data for :mod:`spicexplorer_netlist2xschem`.

Today this holds one thing: :mod:`~spicexplorer_netlist2xschem.symbols.analog_icons`, the reusable
**functional-icon glyph library** (opamp/OTA triangle, comparator, integrator, chopper, ADC/DAC,
LDO, switch/sampler). A glyph is a *function of the generated pin geometry*, not a checked-in
``.sym`` file — see that module's docstring for why (an xschem ``type=subcircuit`` symbol binds its
child schematic to the symbol FILE's basename, so a SHARED icon file cannot be placed on a sheet;
the icon has to be written per cell).
"""

from . import analog_icons

__all__ = ["analog_icons"]
