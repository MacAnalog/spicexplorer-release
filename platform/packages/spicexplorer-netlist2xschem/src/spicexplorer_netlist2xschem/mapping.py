"""Device → symbol reference + canonical-pin → symbol-pin alignment.

This is the one place a silent mis-wire can hide: the netlist thinks in canonical pin names
(``DRAIN/GATE/SOURCE/BULK``, ``P/N``) while each symbol declares its own (``D/G/S/B``; ``P/M`` for
``res.sym``; lowercase ``p/m`` for ``capa/ind/vsource/isource``). The alias tables below are verified
against the vendored IHP + generic ``.sym`` files and exercised exhaustively in ``test_mapping.py``.
"""

from __future__ import annotations

from collections.abc import Iterable

from .ingest import Device, DeviceKind, MosPolarity
from .sym_library import Symbol, SymPin

__all__ = [
    "symref_for",
    "vendored_pdks",
    "foreign_mos_models",
    "GENERIC_PDK_TOKENS",
    "is_pdk_primitive",
    "align_pins",
    "body_pin",
    "label_symref",
    "LABEL_SYMREF",
    "port_symref",
]

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
#: A controlled source carries the CONTROLLING pair on top of its two output terminals. The
#: generic symbols name that pair ``cp``/``cm`` (vcvs/vccs/cccs/ccvs alike), while ingest's
#: canonical names are ``CP``/``CN`` — so ``CN`` has no alias, alignment comes back incomplete
#: and the caller skips the device. Every controlled source on a testbench sheet is affected:
#: an input or output balun, a behavioural CMFB, a Gm stage.
_CTRL_PIN_ALIAS = {"P": "p", "N": "m", "CP": "cp", "CN": "cm"}

# PDK MOSFET symbols, keyed by (pdk, polarity). A PDK whose symbol library can be vendored gets
# its own entry; every other PDK falls back to `_GENERIC_MOS_SYMREF`.
_PDK_MOS_SYMREF: dict[tuple[str, MosPolarity], str] = {
    ("ihp-sg13g2", MosPolarity.NMOS): "sg13g2_pr/sg13_lv_nmos.sym",
    ("ihp-sg13g2", MosPolarity.PMOS): "sg13g2_pr/sg13_lv_pmos.sym",
}
#: The MOS model names each vendored PDK actually has. A netlist whose MOSFETs name none of
#: these is not that PDK's, and drawing it with that PDK's symbols produces a sheet that
#: RE-NETLISTS CORRECTLY and passes a netlist-identity gate while showing another foundry's
#: devices (issue #203). A schematic of record is trusted *because* it is generated, so that
#: failure screens as real to exactly the reviewer least able to catch it.
#:
#: Only a PDK with vendored symbols needs an entry: the generic lane draws neutral symbols and
#: makes no claim about which kit a model belongs to, so it has nothing to be wrong about.
_PDK_MOS_MODELS: dict[str, frozenset[str]] = {
    "ihp-sg13g2": frozenset({"sg13_lv_nmos", "sg13_lv_pmos", "sg13_hv_nmos", "sg13_hv_pmos"}),
}

#: Tokens that ask for the generic lane by name. A commercial-kit design passes its own kit
#: token (`generic-n65`), which is equally unmapped — but a caller who wants the neutral symbols
#: deliberately should be able to say so without being warned about it every single build.
GENERIC_PDK_TOKENS = frozenset({"generic", "none", ""})

#: Fallback MOSFET symbols for a PDK with no entry above: xschem's own 4-terminal generics, which
#: ship with xschem and need no vendored library.
#:
#: This is what makes a design on a COMMERCIAL kit drawable at all. Such a kit's symbols cannot be
#: vendored here — they are under NDA and live only on the EDA server — so before this fallback
#: every MOSFET of such a netlist resolved to ``None`` and was skipped with a warning: the
#: generator emitted an EMPTY sheet for a ten-transistor amplifier. The generic symbol carries the
#: model name on the INSTANCE (``model=nch_25 w=… l=… m=…``), so the drawing still re-netlists to
#: exactly the devices the netlist named and passes the netlist-identity gate.
#:
#: The convention is not invented here: it is what the lab's existing commercial-kit schematics
#: already use, e.g. ``C {devices/nmos4.sym} … {name=MAT model=nch_25 w=97.2u l=8u m=1}``.
_GENERIC_MOS_SYMREF: dict[MosPolarity, str] = {
    MosPolarity.NMOS: "devices/nmos4.sym",
    MosPolarity.PMOS: "devices/pmos4.sym",
}
# PDK subckt-primitive symbols, keyed by (pdk, model name lowercased). Some PDK primitives are
# shipped as subckts over a native model (the SG13G2 HBT is a .subckt wrapping a VBIC card), so
# they arrive as DeviceKind.SUBCKT with the subckt name in ``model``. Pin alignment rides the
# SUBCKT positional fallback in :func:`align_pins`: netlist order (c b e bn) == symbol pin order
# (C B E S) for the entries below. No clean "no-params" twins are vendored for these, so the
# mapping intentionally ignores ``show_params``.
# The SG13G2 poly resistors are 3-NODE subcircuits (`XR1 P M sub rhigh w=.. l=..`) drawn with a
# TWO-pin symbol: their `format` line is "@spiceprefix@name @pinlist @body @model w=@w l=@l m=@m
# b=@b", so the substrate node is the instance's `body=` attribute, not a pin. :func:`body_pin`
# below is what routes that third net there; without it these would have to stay undrawable.
_PDK_SUBCKT_SYMREF: dict[tuple[str, str], str] = {
    ("ihp-sg13g2", "npn13g2"): "sg13g2_pr/npn13G2.sym",
    ("ihp-sg13g2", "npn13g2l"): "sg13g2_pr/npn13G2l.sym",
    ("ihp-sg13g2", "npn13g2v"): "sg13g2_pr/npn13G2v.sym",
    ("ihp-sg13g2", "rhigh"): "sg13g2_pr/rhigh.sym",
    ("ihp-sg13g2", "rppd"): "sg13g2_pr/rppd.sym",
    ("ihp-sg13g2", "rsil"): "sg13g2_pr/rsil.sym",
    # Two-net primitives. These do NOT arrive as DeviceKind.SUBCKT — `XCFF a b cap_cmim w=7u l=7u`
    # has exactly two nets, so `_make_device` types it by prefix as a CAP and it never reached the
    # subckt path that rescued rhigh. `symref_for` below prefers this table for any X-prefixed
    # instance whose model matches, which is what routes w/l/m onto the instance instead of the
    # generic capa.sym's single `value` slot.
    ("ihp-sg13g2", "cap_cmim"): "sg13g2_pr/cap_cmim.sym",
    ("ihp-sg13g2", "cap_rfcmim"): "sg13g2_pr/cap_rfcmim.sym",
    ("ihp-sg13g2", "dantenna"): "sg13g2_pr/dantenna.sym",
    ("ihp-sg13g2", "dpantenna"): "sg13g2_pr/dpantenna.sym",
    # DELIBERATELY ABSENT: cap_cpara. Its symbol writes the whole template on ONE line
    # (`template="name=C1 model=cparasitic C=10f spiceprefix=X"`) and `sym_library._parse_template`
    # splits on newlines only, so it parses as a single bogus `name` entry with no `model` or
    # `spiceprefix` — `is_pdk_primitive` cannot see it. Mapping the model before that is fixed
    # would just draw a symbol that drops the capacitance. (Its uppercase `C` key is no longer a
    # second blocker: `_parse_template` now preserves key case.)
    # DELIBERATELY ABSENT: ntap1/ptap1 (+ their _ring twins). Their `format` is a `tcleval(...)`
    # that computes an `R=` from w and l, so the netlister emits a resistance the input never
    # carried — measured on xschem 3.4.5, with symbolic sizes too:
    #   XXtap net1 net2 ntap1 R={ 1.0 / ( ... r_w * r_l ... )} w=r_w l=r_l
    # A round trip through them is therefore not value-preserving. "No symbol mapping" (the device
    # is skipped, and said so) beats drawing one that changes the netlist.
}
# Generic device symbols from the bundled xschem library.
_GENERIC_SYMREF: dict[DeviceKind, str] = {
    DeviceKind.RES: "devices/res.sym",
    DeviceKind.CAP: "devices/capa.sym",
    DeviceKind.IND: "devices/ind.sym",
    DeviceKind.VSOURCE: "devices/vsource.sym",
    DeviceKind.ISOURCE: "devices/isource.sym",
}
#: A behavioural/controlled source's symbol is chosen by its REFERENCE letter, not its kind:
#: they share everything placement cares about and nothing a reader does.
_SOURCE_SYMREF: dict[str, str] = {
    "B": "devices/bsource.sym",
    "E": "devices/vcvs.sym",
    "G": "devices/vccs.sym",
    "F": "devices/cccs.sym",
    "H": "devices/ccvs.sym",
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


def register_subckt_symbol(pdk: str, model: str, symref: str) -> None:
    """Register a DESIGN's own ``.sym`` for one subcircuit model, so instances of it are drawn.

    A subcircuit instance resolves only through the PDK primitive table, so a testbench sheet whose
    DUT is ``XDUT ... my_cell`` has no symbol for it and the instance is dropped from the drawing
    with a warning. A design that has generated a symbol for its own cell registers it here; the
    ``.sym`` must be on the symbol library search path. Registering the same pair twice with the
    same symref is a no-op; with a different one it raises, so two designs cannot collide silently.
    """
    key = (pdk, model.lower())
    seen = _PDK_SUBCKT_SYMREF.get(key)
    if seen is not None and seen != symref:
        raise ValueError(f"{pdk}/{model} is already drawn as {seen!r}, not {symref!r}")
    _PDK_SUBCKT_SYMREF[key] = symref


def symref_for(dev: Device, *, pdk: str | None, show_params: bool = True) -> str | None:
    """The ``.sym`` reference for ``dev``, or ``None`` if there's no mapping (caller skips + warns).

    Subcircuit instances resolve only through the ``_PDK_SUBCKT_SYMREF`` table (PDK primitives
    shipped as subckts: the SG13G2 HBTs and poly resistors); other subckts return ``None`` (the definition's
    ``.sym`` is circuit-specific). When ``show_params`` is ``False`` the device is mapped to its
    clean "no-params" symbol twin (see :func:`_clean_symref`) so the schematic doesn't draw the
    sizing text — except PDK subckt primitives, which have no vendored twin and keep their symbol.
    """
    model = (dev.model or "").split()[0].lower() if dev.model else ""
    if dev.kind is DeviceKind.SUBCKT:
        return _PDK_SUBCKT_SYMREF.get((pdk or "", model))
    if dev.ref[:1] in ("X", "x"):
        # A subcircuit CALL that the prefix test typed as a primitive because its net count happens
        # to match one (`XCFF a b cap_cmim`, two nets, typed CAP). The PDK symbol wins over the
        # generic one: it has the model's own `format` line, so w/l/m ride the instance. A genuine
        # primitive (`C1 a b 1p`) has no X and keeps capa.sym.
        pdk_ref = _PDK_SUBCKT_SYMREF.get((pdk or "", model))
        if pdk_ref is not None:
            return pdk_ref
    if dev.kind is DeviceKind.BSOURCE:
        # No "no-params" twin: the expression IS the device, and hiding it draws a source
        # nobody can read.
        return _SOURCE_SYMREF.get(dev.ref[:1].upper())
    base = (
        _PDK_MOS_SYMREF.get((pdk or "", dev.polarity), _GENERIC_MOS_SYMREF.get(dev.polarity))
        if dev.kind is DeviceKind.MOS
        else _GENERIC_SYMREF.get(dev.kind)
    )
    if base is None:
        return None
    return base if show_params else _clean_symref(base)


def vendored_pdks() -> frozenset[str]:
    """The PDK tokens that have a vendored symbol library; every other token draws generic."""
    return frozenset(p for p, _ in _PDK_MOS_SYMREF) | frozenset(p for p, _ in _PDK_SUBCKT_SYMREF)


def foreign_mos_models(devices: Iterable[Device], pdk: str | None) -> list[str]:
    """MOS model names in ``devices`` that do not belong to ``pdk`` (sorted, de-duplicated).

    Empty when ``pdk`` has no vendored symbols — the generic lane carries the model on the
    instance and claims nothing about the kit — and empty when every model checks out.
    """
    known = _PDK_MOS_MODELS.get((pdk or "").strip().lower())
    if not known:
        return []
    seen = {
        model
        for dev in devices
        if dev.kind is DeviceKind.MOS
        and (model := (dev.model or "").split()[0].lower() if dev.model else "")
        and model not in known
    }
    return sorted(seen)


def is_pdk_primitive(dev: Device, sym: Symbol) -> bool:
    """True when ``sym`` is a PDK primitive's own symbol rather than a generic device symbol.

    Sniffed from the template, which is xschem's own convention and needs no second table: a PDK
    primitive declares both the ``model`` it instantiates and the ``spiceprefix`` (``X``) that
    calls it, while ``capa.sym``/``res.sym``/``vsource.sym`` declare neither. MOS symbols declare
    both but are already handled by their own branch everywhere this is consulted.

    It decides two things: pins align POSITIONALLY (a PDK symbol names its pins ``c0``/``c1``,
    ``d0``/``d1`` — nothing the canonical ``P``/``N`` alias tables can match, so alias alignment
    silently produced an empty map and the device was skipped as "pins could not be aligned"), and
    the instance carries ``model``/``spiceprefix`` plus the template's own parameter keys instead
    of the generic single ``value`` slot.
    """
    return (
        dev.kind is not DeviceKind.MOS and "model" in sym.template and "spiceprefix" in sym.template
    )


def body_pin(dev: Device, sym: Symbol) -> str | None:
    """The device pin whose net rides on the symbol's ``body`` ATTRIBUTE instead of a wire.

    A PDK primitive shipped as a subcircuit may carry one more node than its symbol has pins: the
    SG13G2 poly resistors (``rhigh``/``rppd``/``rsil``) are ``X<name> P M sub <model> w=.. l=..``
    but ship a two-pin symbol whose template declares ``body=sub!`` and whose ``format`` writes
    ``@pinlist @body @model``. Putting that node on ``body=`` is what makes the device drawable AND
    keeps the netlist round trip exact — a wire could not reproduce a node that has no pin.

    ``None`` (the normal case) when the symbol has no ``body`` template attribute or the pin counts
    already agree, so every other device keeps every net on a real pin.
    """
    if dev.kind is not DeviceKind.SUBCKT or "body" not in sym.template:
        return None
    if len(dev.pins) != len(sym.pins) + 1:
        return None
    return dev.pins[-1]


def _pin_alias(dev: Device) -> dict[str, str]:
    if dev.kind is DeviceKind.MOS:
        return _MOS_PIN_ALIAS
    if dev.kind is DeviceKind.RES:
        return _RES_PIN_ALIAS
    if dev.kind is DeviceKind.BSOURCE:
        return _CTRL_PIN_ALIAS
    return _TWOT_PIN_ALIAS  # cap/ind/vsource/isource


def align_pins(dev: Device, sym: Symbol) -> dict[str, SymPin]:
    """Map each canonical pin of ``dev`` to the :class:`SymPin` it should wire to on ``sym``.

    Primitives use a fixed alias table; subckt instances match formal-port names to symbol pin names
    (case-insensitive), falling back to positional order. Pins that can't be matched are omitted, so
    the caller can detect an incomplete alignment and skip the device rather than mis-wire it.
    """
    out: dict[str, SymPin] = {}
    if dev.kind is DeviceKind.SUBCKT or is_pdk_primitive(dev, sym):
        body = body_pin(dev, sym)
        # Positional order is the order the pins appear in the .sym FILE, which is the order
        # xschem's netlister writes `@pinlist` in — NOT `pinnumber` order. rhigh.sym is the case
        # that proves it: its pins are M then P in the file but numbered P=1, M=2, and the
        # round-trip test shows xschem emits the M net first. Wiring by pinnumber silently swaps
        # the two resistor terminals on the way back out.
        for i, canon in enumerate(dev.pins):
            if canon == body:
                continue  # carried as the `body=` attribute; deliberately not wired
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
