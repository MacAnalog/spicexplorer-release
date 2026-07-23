"""Device → symbol reference + canonical-pin → symbol-pin alignment.

This is the one place a silent mis-wire can hide: the netlist thinks in canonical pin names
(``DRAIN/GATE/SOURCE/BULK``, ``P/N``) while each symbol declares its own (``D/G/S/B``; ``P/M`` for
``res.sym``; lowercase ``p/m`` for ``capa/ind/vsource/isource``). The alias tables below are verified
against the vendored IHP + generic ``.sym`` files and exercised exhaustively in ``test_mapping.py``.
"""

from __future__ import annotations

from .ingest import Device, DeviceKind, MosPolarity
from .sym_library import Symbol, SymPin

__all__ = ["symref_for", "align_pins", "label_symref", "LABEL_SYMREF", "port_symref"]

LABEL_SYMREF = "devices/lab_wire.sym"  # the in-schematic net-name label (single pin at its origin)
# Port pins, by direction. Each is a single-pin symbol (pin at its origin) carrying the net in `lab`.
_PORT_SYMREF = {
    "in": "devices/ipin.sym",
    "out": "devices/opin.sym",
    "inout": "devices/iopin.sym",
}

# MOS symbols (both polarities) declare D/G/S/B.
_MOS_PIN_ALIAS = {"DRAIN": "D", "GATE": "G", "SOURCE": "S", "BULK": "B"}
# res.sym uses P/M; capa/ind/vsource/isource use lowercase p/m.
_RES_PIN_ALIAS = {"P": "P", "N": "M"}
_TWOT_PIN_ALIAS = {"P": "p", "N": "m"}

# PDK MOSFET symbols, keyed by (pdk, polarity). IHP only for v1; extend here for more PDKs.
_PDK_MOS_SYMREF: dict[tuple[str, MosPolarity], str] = {
    ("ihp-sg13g2", MosPolarity.NMOS): "sg13g2_pr/sg13_lv_nmos.sym",
    ("ihp-sg13g2", MosPolarity.PMOS): "sg13g2_pr/sg13_lv_pmos.sym",
}
# Generic device symbols from the bundled xschem library.
_GENERIC_SYMREF: dict[DeviceKind, str] = {
    DeviceKind.RES: "devices/res.sym",
    DeviceKind.CAP: "devices/capa.sym",
    DeviceKind.IND: "devices/ind.sym",
    DeviceKind.VSOURCE: "devices/vsource.sym",
    DeviceKind.ISOURCE: "devices/isource.sym",
}


def label_symref() -> str:
    """The symref used for net-name labels."""
    return LABEL_SYMREF


def port_symref(direction: str) -> str:
    """The port-pin ``.sym`` for a port direction (``in``/``out``/``inout``); ``inout`` is the default."""
    return _PORT_SYMREF.get(direction, _PORT_SYMREF["inout"])


def _clean_symref(symref: str) -> str:
    """The "no-params" twin of a device symref — the same symbol minus its parameter-display text.

    All clean variants are vendored flat in the generic ``devices/`` library with a ``_np`` suffix
    (``sg13g2_pr/sg13_lv_nmos.sym`` → ``devices/sg13_lv_nmos_np.sym``), generated once by
    :func:`~spicexplorer_netlist2xschem.symbol_gen.clean_symbol`. They keep identical pins + ``K``-block,
    so a device drawn with them wires and netlists the same — only the ``w=…``/``l=…``/``model`` text is
    gone."""
    stem = symref.rsplit("/", 1)[-1][:-4]  # basename without ".sym"
    return f"devices/{stem}_np.sym"


def symref_for(dev: Device, *, pdk: str | None, show_params: bool = True) -> str | None:
    """The ``.sym`` reference for ``dev``, or ``None`` if there's no mapping (caller skips + warns).

    Subcircuit instances have no generic symbol (the definition's ``.sym`` is circuit-specific), so
    they return ``None`` in v1. When ``show_params`` is ``False`` the device is mapped to its clean
    "no-params" symbol twin (see :func:`_clean_symref`) so the schematic doesn't draw the sizing text.
    """
    base = (
        _PDK_MOS_SYMREF.get((pdk or "", dev.polarity))
        if dev.kind is DeviceKind.MOS
        else _GENERIC_SYMREF.get(dev.kind)
    )
    if base is None:
        return None
    return base if show_params else _clean_symref(base)


def _pin_alias(dev: Device) -> dict[str, str]:
    if dev.kind is DeviceKind.MOS:
        return _MOS_PIN_ALIAS
    if dev.kind is DeviceKind.RES:
        return _RES_PIN_ALIAS
    return _TWOT_PIN_ALIAS  # cap/ind/vsource/isource


def align_pins(dev: Device, sym: Symbol) -> dict[str, SymPin]:
    """Map each canonical pin of ``dev`` to the :class:`SymPin` it should wire to on ``sym``.

    Primitives use a fixed alias table; subckt instances match formal-port names to symbol pin names
    (case-insensitive), falling back to positional order. Pins that can't be matched are omitted, so
    the caller can detect an incomplete alignment and skip the device rather than mis-wire it.
    """
    out: dict[str, SymPin] = {}
    if dev.kind is DeviceKind.SUBCKT:
        for i, canon in enumerate(dev.pins):
            sp = sym.pin(canon) or (sym.pins[i] if i < len(sym.pins) else None)
            if sp is not None:
                out[canon] = sp
        return out

    alias = _pin_alias(dev)
    for canon in dev.pins:
        sp = sym.pin(alias.get(canon, canon))
        if sp is not None:
            out[canon] = sp
    return out
