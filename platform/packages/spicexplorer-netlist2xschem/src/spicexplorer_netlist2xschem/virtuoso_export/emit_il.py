"""Emit a deterministic, self-contained SKILL ``.il`` that rebuilds an xschem ``.sch``
as a Virtuoso schematic cellview (Mode A: placement + net-label connectivity).

The artifact is plain text a human can read, diff, golden-test, and ``load()`` in a CIW —
no bridge required to *generate* it. Structure:

* two helper procedures, defined once —
  ``xvSetParams`` sets CDF parameters **and fires their callbacks** (the ``dbReplaceProp``
  shortcut silently skips callback-derived CDF params), falling
  back to plain properties for masters without CDF (local subcircuit symbols);
  ``xvLabelTerm`` resolves an instance terminal's *actual* pin centre at load time (master
  pin geometry differs between xschem and the kit — the one thing that cannot be computed
  offline) and draws a short labeled wire stub in the direction the original drawing left
  that pin;
* one ``let`` per cellview: open ``"w"``, place instances at scaled xschem coordinates with
  the live-verified orient table, set params, label every terminal, create interface pins,
  ``schCheck`` + ``dbSave``, and print an ``xvport:`` summary line with the marker counts.

Net-label connectivity (same name ⇒ same net) is deliberate: it is immune to pin-geometry
mismatch between the xschem drawing and the Cadence masters, and it is the bridge's verified
recipe.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from spicexplorer_core.eng import parse_value

from ..sch_parser import Schematic
from ..sym_library import SymLibrary
from .devmap import DeviceMap, DeviceRule
from .netex import NetExtraction, extract_nets
from .xform import DEFAULT_SCALE, direction_to_cadence, orient_for, to_cadence

__all__ = ["EmitResult", "emit_schematic_il"]

_STUB_LEN = 0.25
_LABEL_HEIGHT = 0.0625

_NAME_OK = re.compile(r"[^A-Za-z0-9_!]")

_PIN_MASTER = {"in": "ipin", "out": "opin", "inout": "iopin"}
_PIN_DIRECTION = {"in": "input", "out": "output", "inout": "inputOutput"}

_HELPERS = """\
; --- xvport helpers (idempotent redefinition) --------------------------------
procedure( xvSetParams(cv instName pairs)
  let((inst iCDF cCDF saved p cb cdfgData cdfgForm)
    inst = car(setof(x cv~>instances x~>name == instName))
    unless(inst error("xvport: instance not found: %s" instName))
    iCDF = cdfGetInstCDF(inst)
    if( !iCDF
      then  ; no CDF (e.g. a local subcircuit symbol) -> plain string properties
        foreach(pair pairs dbReplaceProp(inst car(pair) "string" cadr(pair)))
      else
        cCDF = cdfGetCellCDF(ddGetObj(inst~>libName inst~>cellName))
        saved = makeTable('s)
        foreach(p cCDF~>parameters setarray(saved p~>name p~>value))
        foreach(p cCDF~>parameters
          when(get(iCDF p~>name) putpropq(p get(iCDF p~>name)~>value value)))
        cdfgData = cCDF
        cdfgForm = cCDF
        foreach(pair pairs
          p = get(cCDF car(pair))
          if(p
            then p~>value = cadr(pair)
            else printf("xvport: WARNING unknown CDF param %s on %s\\n" car(pair) instName)))
        foreach(pair pairs
          p = get(cCDF car(pair))
          when(p
            cb = p~>callback
            when(cb && cb != "" errset(evalstring(cb) t))))
        cdfUpdateInstParam(inst)
        foreach(p cCDF~>parameters putpropq(p arrayref(saved p~>name) value))
    )
    t
  ))

procedure( xvLabelTerm(cv instName termName netName dx dy len)
  let((inst term pin fig bb cx cy ex ey)
    inst = car(setof(x cv~>instances x~>name == instName))
    unless(inst error("xvport: instance not found: %s" instName))
    term = car(setof(x inst~>master~>terminals x~>name == termName))
    unless(term error("xvport: terminal %s not found on %s" termName instName))
    pin = car(term~>pins)
    fig = car(pin~>figs)
    unless(fig fig = pin~>fig)
    unless(fig error("xvport: no pin figure for %s.%s" instName termName))
    bb = dbTransformBBox(fig~>bBox inst~>transform)
    cx = quotient(plus(xCoord(car(bb)) xCoord(cadr(bb))) 2.0)
    cy = quotient(plus(yCoord(car(bb)) yCoord(cadr(bb))) 2.0)
    ex = plus(cx times(dx len))
    ey = plus(cy times(dy len))
    schCreateWire(cv "route" "full" list(list(cx cy) list(ex ey)) 0 0 0 nil nil)
    schCreateWireLabel(cv nil list(quotient(plus(cx ex) 2.0) quotient(plus(cy ey) 2.0))
      netName "lowerCenter" if(dx == 0 "R90" "R0") "stick" @HEIGHT@ nil)
    t
  ))

procedure( xvPatchTerm(cv instName termName tx ty)
  ; wire-mode: connect the instance terminal's real pin centre to the (scaled) point where
  ; the xschem drawing expects that pin — zero patch when the geometries already agree.
  let((inst term pin fig bb cx cy)
    inst = car(setof(x cv~>instances x~>name == instName))
    unless(inst error("xvport: instance not found: %s" instName))
    term = car(setof(x inst~>master~>terminals x~>name == termName))
    unless(term error("xvport: terminal %s not found on %s" termName instName))
    pin = car(term~>pins)
    fig = car(pin~>figs)
    unless(fig fig = pin~>fig)
    unless(fig error("xvport: no pin figure for %s.%s" instName termName))
    bb = dbTransformBBox(fig~>bBox inst~>transform)
    cx = quotient(plus(xCoord(car(bb)) xCoord(cadr(bb))) 2.0)
    cy = quotient(plus(yCoord(car(bb)) yCoord(cadr(bb))) 2.0)
    when(or(abs(difference(cx tx)) > 0.001 abs(difference(cy ty)) > 0.001)
      schCreateWire(cv "route" "full" list(list(cx cy) list(tx ty)) 0 0 0 nil nil))
    t
  ))
; ------------------------------------------------------------------------------
""".replace("@HEIGHT@", f"{_LABEL_HEIGHT:g}")


@dataclass
class EmitResult:
    """The emitted ``.il`` text plus the expectation table ``--verify`` diffs against."""

    il: str
    # (instance, cadence term) -> net — what read_schematic should report after the load.
    expected_bindings: dict[tuple[str, str], str] = field(default_factory=dict)
    expected_ports: dict[str, str] = field(default_factory=dict)  # pin name -> direction
    instances: dict[str, tuple[str, str]] = field(default_factory=dict)  # name -> (lib, cell)
    warnings: list[str] = field(default_factory=list)


def _s(text: str) -> str:
    """Escape a string for a SKILL double-quoted literal."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


# instance attrs that are drawing bookkeeping, never device parameters
_BOOKKEEPING_ATTRS = frozenset({"name", "model", "spiceprefix", "url", "description"})


def _sanitize(name: str, *, prefix: str) -> str:
    clean = _NAME_OK.sub("_", name.lstrip("#"))
    if not clean:
        clean = prefix
    if clean[0].isdigit():
        clean = f"{prefix}{clean}"
    return clean


def _fmt(v: float) -> str:
    return f"{v:.6g}"


_SI_SUFFIXES = ((1.0, ""), (1e-3, "m"), (1e-6, "u"), (1e-9, "n"), (1e-12, "p"), (1e-15, "f"))


def _si(value: float) -> str:
    """An engineering string the CDF accepts (1e-07 -> ``"100n"``)."""
    if value == 0:
        return "0"
    for scale, suffix in _SI_SUFFIXES:
        if abs(value) >= scale:
            return f"{value / scale:.6g}{suffix}"
    return f"{value:.6g}"


def _apply_per_finger(rule: DeviceRule, attrs: dict[str, str], params: dict[str, str]) -> str | None:
    """Divide a TOTAL-width attribute by the finger count before it reaches a PER-FINGER CDF
    parameter (``rule.per_finger`` — e.g. IHP xschem ``w`` is total, a kit CDF ``w`` is often
    per-finger). Mutates ``params``; returns a warning when the division is needed but
    impossible (symbolic values), in which case the width parameter is dropped rather than
    silently netlisting at ``fingers ×`` its intended size."""
    total_attr = rule.per_finger.get("total")
    fingers_attr = rule.per_finger.get("fingers")
    if not total_attr or not fingers_attr:
        return None
    cdf_w = rule.params.get(total_attr)
    if cdf_w is None or cdf_w not in params:
        return None
    ng_raw = attrs.get(fingers_attr, "")
    if ng_raw in ("", "1"):
        return None  # one finger: total == per-finger
    try:
        total = float(parse_value(attrs[total_attr]))
        ng = float(parse_value(ng_raw))
    except Exception:
        dropped = params.pop(cdf_w)
        return (
            f"cannot derive per-finger {cdf_w} from {total_attr}={attrs[total_attr]!r} / "
            f"{fingers_attr}={ng_raw!r} — dropping {cdf_w}={dropped!r} (set it manually)"
        )
    if ng <= 0:
        dropped = params.pop(cdf_w)
        return f"invalid finger count {fingers_attr}={ng_raw!r} — dropping {cdf_w}={dropped!r}"
    params[cdf_w] = _si(total / ng)
    return None


def _islands(
    segments: list[tuple[float, float, float, float]],
) -> list[list[tuple[float, float, float, float]]]:
    """Group segments into geometrically connected islands (shared endpoints).

    Segments arrive pre-split at every electrical node (see ``NetExtraction``), so
    endpoint identity is the whole connectivity story here.
    """

    def key(x: float, y: float) -> tuple[int, int]:
        return (round(x * 2), round(y * 2))

    parent: dict[tuple[int, int], tuple[int, int]] = {}

    def find(k: tuple[int, int]) -> tuple[int, int]:
        parent.setdefault(k, k)
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    for x1, y1, x2, y2 in segments:
        ra, rb = find(key(x1, y1)), find(key(x2, y2))
        if ra != rb:
            parent[rb] = ra
    groups: dict[tuple[int, int], list[tuple[float, float, float, float]]] = {}
    for seg in segments:
        groups.setdefault(find(key(seg[0], seg[1])), []).append(seg)
    return [groups[root] for root in sorted(groups)]


def emit_schematic_il(
    sch: Schematic,
    *,
    lib: str,
    cell: str,
    devmap: DeviceMap,
    symlib: SymLibrary | None = None,
    scale: float = DEFAULT_SCALE,
    source_name: str = "",
    netex: NetExtraction | None = None,
    local_cells: set[str] | None = None,
    mode: str = "labels",
    local_prefix: str = "",
) -> EmitResult:
    """Render ``sch`` into a Mode-A ``.il`` building ``lib/cell`` (see module docstring).

    Unmapped device symrefs are treated as *local* symbols — instances of
    ``(lib, <basename>, symbol)`` in the target library itself; the ``--with-symbols``
    hierarchy walk is what creates those masters first (it passes them as ``local_cells``
    so they don't warn).

    ``mode="labels"`` (default) connects every terminal with a named wire stub;
    ``mode="wires"`` instead draws the xschem wire segments verbatim (scaled), labels each
    net once on its longest segment, and geometrically patches each terminal's real pin
    centre to the drawing's pin point (a zero-length no-op for ported local symbols, whose
    pin geometry is a scaled copy of the xschem one).

    ``local_prefix`` prepends every locally-created master cell reference (the ``--prefix``
    escape hatch when an xschem basename collides with a kit cell name).
    """
    if mode not in ("labels", "wires"):
        raise ValueError(f"mode must be 'labels' or 'wires', got {mode!r}")
    symlib = symlib or SymLibrary.default()
    nx = netex or extract_nets(sch, symlib)
    result = EmitResult(il="", warnings=list(nx.warnings))

    # sanitized net names, with a deterministic collision guard (two distinct xschem
    # names may sanitize identically — a silent merge would rewire the circuit)
    net_alias: dict[str, str] = {}
    taken_nets: set[str] = set()
    for raw in sorted(nx.nets):
        clean = base = _sanitize(raw, prefix="net")
        n = 2
        while clean in taken_nets:
            clean = f"{base}_{n}"
            n += 1
        if clean != base:
            result.warnings.append(
                f"net name collision after sanitization: {raw!r} -> {clean!r}"
            )
        taken_nets.add(clean)
        net_alias[raw] = clean
    inst_names: dict[str, str] = {}  # raw component name -> final (collision-free) name
    body: list[str] = []

    body.append(f'cv = dbOpenCellViewByType("{_s(lib)}" "{_s(cell)}" "schematic" "schematic" "w")')

    # --- instances + params ---------------------------------------------------
    for comp in sch.components:
        if not comp.is_device or comp.is_port:
            continue
        sym = symlib.load(comp.symref)
        if sym is None:
            continue  # already warned by extract_nets
        if sym.type == "label":
            continue
        rule = devmap.lookup(comp.symref)
        pf_warning: str | None = None
        if rule is not None:
            mlib, mcell, mview = rule.lib, rule.cell, rule.view
            params = {
                rule.params[k]: v for k, v in comp.attrs.items() if k in rule.params and v != ""
            }
            pf_warning = _apply_per_finger(rule, comp.attrs, params)
        else:
            stem = comp.symref.rsplit("/", 1)[-1]
            stem = stem[:-4] if stem.endswith(".sym") else stem
            mlib, mcell, mview = lib, _sanitize(f"{local_prefix}{stem}", prefix="cell"), "symbol"
            params = {}
            if mcell not in (local_cells or ()):
                msg = (
                    f"unmapped symref {comp.symref} -> local master {mlib}/{mcell} "
                    f"(port its symbol first)"
                )
                if msg not in result.warnings:
                    result.warnings.append(msg)
            dropped = sorted(
                k for k, v in comp.attrs.items() if k not in _BOOKKEEPING_ATTRS and v != ""
            )
            if dropped:
                result.warnings.append(
                    f"instance {_sanitize(comp.name, prefix='I')}: unmapped local master — "
                    f"xschem parameter(s) {dropped} are NOT transferred"
                )
        inst = base_inst = _sanitize(comp.name, prefix="I")
        n = 2
        while inst in result.instances:
            inst = f"{base_inst}_{n}"
            n += 1
        if inst != base_inst:
            result.warnings.append(
                f"instance name collision after sanitization: {comp.name!r} -> {inst!r}"
            )
        inst_names[comp.name] = inst
        if pf_warning:
            result.warnings.append(f"instance {inst}: {pf_warning}")
        x, y = to_cadence(comp.x, comp.y, scale)
        orient = orient_for(comp.rot, comp.flip)
        body.append(
            "let((m) "
            f'm = dbOpenCellViewByType("{_s(mlib)}" "{_s(mcell)}" "{_s(mview)}" nil "r") '
            f'unless(m error("xvport: master not found: {_s(mlib)}/{_s(mcell)}")) '
            f'dbCreateInst(cv m "{_s(inst)}" list({_fmt(x)} {_fmt(y)}) "{orient}"))'
        )
        result.instances[inst] = (mlib, mcell)
        if params:
            pairs = " ".join(f'list("{_s(k)}" "{_s(v)}")' for k, v in sorted(params.items()))
            body.append(f'xvSetParams(cv "{_s(inst)}" list({pairs}))')
            unresolved = [
                v
                for v in params.values()
                if re.search(r"[A-Za-z_]{2,}", v) and not re.fullmatch(r"[0-9.]+[a-zA-Z]*", v)
            ]
            if unresolved:
                result.warnings.append(
                    f"instance {inst}: symbolic parameter value(s) {unresolved} passed verbatim"
                )

    # --- connectivity ------------------------------------------------------------
    if mode == "wires":
        # the drawing's wires, verbatim (scaled); zero-length segments are dropped
        for net in sorted(nx.net_segments):
            for x1, y1, x2, y2 in nx.net_segments[net]:
                p1 = to_cadence(x1, y1, scale)
                p2 = to_cadence(x2, y2, scale)
                if p1 == p2:
                    continue
                body.append(
                    'schCreateWire(cv "route" "full" '
                    f"list(list({_fmt(p1[0])} {_fmt(p1[1])}) list({_fmt(p2[0])} {_fmt(p2[1])})) "
                    "0 0 0 nil nil)"
                )
        # A net is often drawn as several disjoint islands joined only by equal labels
        # (rails especially). Virtuoso needs the name on EVERY island, so label the
        # longest segment of each geometrically-connected island of each net.
        for net in sorted(nx.net_segments):
            for island in _islands(nx.net_segments[net]):
                x1, y1, x2, y2 = max(island, key=lambda s: abs(s[2] - s[0]) + abs(s[3] - s[1]))
                mx, my = to_cadence((x1 + x2) / 2.0, (y1 + y2) / 2.0, scale)
                rot = "R90" if abs(x2 - x1) < abs(y2 - y1) else "R0"
                body.append(
                    f"schCreateWireLabel(cv nil list({_fmt(mx)} {_fmt(my)}) "
                    f'"{_s(net_alias[net])}" "lowerCenter" "{rot}" "stick" '
                    f"{_LABEL_HEIGHT:g} nil)"
                )

    for (inst_name, pin_name), pn in sorted(nx.pin_nets.items()):
        comp = sch.component(inst_name)
        if comp is None:
            continue
        rule = devmap.lookup(comp.symref)
        term = rule.term_for(pin_name) if rule is not None else pin_name
        inst = inst_names.get(inst_name, _sanitize(inst_name, prefix="I"))
        net = net_alias[pn.net]
        if mode == "wires" and pn.on_wire:
            tx, ty = to_cadence(pn.x, pn.y, scale)
            body.append(f'xvPatchTerm(cv "{_s(inst)}" "{_s(term)}" {_fmt(tx)} {_fmt(ty)})')
        else:  # labels mode — and the wire-mode fallback for nets with no drawn segments
            dx, dy = direction_to_cadence(*pn.stub_dir)
            body.append(
                f'xvLabelTerm(cv "{_s(inst)}" "{_s(term)}" "{_s(net)}" '
                f"{_fmt(dx)} {_fmt(dy)} {_fmt(_STUB_LEN)})"
            )
        result.expected_bindings[(inst, term)] = net

    # --- interface pins ---------------------------------------------------------
    seen_pins: set[str] = set()
    for port in nx.ports:
        pname = net_alias.get(port.name, _sanitize(port.name, prefix="net"))
        if pname in seen_pins:
            result.warnings.append(f"duplicate port {pname} — keeping the first")
            continue
        seen_pins.add(pname)
        direction = _PIN_DIRECTION[port.direction]
        master = _PIN_MASTER[port.direction]
        px, py = to_cadence(port.x, port.y, scale)
        body.append(
            f'schCreatePin(cv dbOpenCellViewByType("basic" "{master}" "symbol") '
            f'"{_s(pname)}" "{direction}" nil list({_fmt(px)} {_fmt(py)}) "R0")'
        )
        result.expected_ports[pname] = direction

    # --- check + save -----------------------------------------------------------
    body.append("schCheck(cv)")
    body.append(
        'let((sev) sev = setof(m cv~>markers m~>severity == "error") '
        f'printf("xvport: built {_s(lib)}/{_s(cell)} insts=%d nets=%d errors=%d\\n" '
        "length(cv~>instances) length(cv~>nets) length(sev)))"
    )
    body.append("dbSave(cv)")
    body.append("dbClose(cv)")

    src = f" from {source_name}" if source_name else ""
    header = (
        f"; xvport Mode A schematic build{src}\n"
        f"; target: {lib}/{cell}/schematic   scale={scale}   generator: spicexplorer xvport\n"
        f'; load in CIW:  load("<this file>")\n'
    )
    inner = "\n  ".join(body)
    result.il = f"{header}\n{_HELPERS}\nlet((cv)\n  {inner}\n)\n"
    return result
