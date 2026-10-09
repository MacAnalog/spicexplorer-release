"""Reverse porting: Virtuoso cellviews → xschem ``.sch``/``.sym`` files.

The two readback gaps the bridge does not cover — schematic *wire geometry* and symbol
*drawing shapes* — are filled by SKILL dump snippets in this module, executed through the
bridge's public ``execute_skill`` (the submodule stays pristine). Each dump
returns a plain line-oriented text record set (the daemon-safest transport), parsed here.

**NDA denylist (enforced):** a cellview living in a ``kit_libs`` library is never
dumped — not its schematic, not its symbol geometry. :func:`_require_not_kit` raises
*before any client call*; kit-master *instances* inside a user schematic are fine — only
their name/placement/params are read, and they map back to xschem symrefs via the device
table (each rule's ``symref``).

Inverse transforms mirror the forward ones exactly: ``ORIENT_INVERSE`` (all 8 orients),
``from_cadence`` (y-negation + 1/scale, snapped to xschem's 0.5-unit resolution), reversed
param tables (CDF→attr, ``simM``→``m``), and the ``per_finger`` multiplication (a kit's CDF
width may be per-finger; the xschem attribute carries total width = ``w × fingers``).

Symbol shapes: line/rect/polygon/ellipse, and an ``arc`` as its ``ellipseBBox`` plus
``startAngle``/``stopAngle`` (an ``SA`` record → an xschem ``A`` record). Any other
device-layer shape type is named in a warning, never dropped without one. The
``arc`` branch reads the database attributes as documented (angles in radians); it has not
yet been run against a live daemon.

:func:`cv2sch_hierarchy` (``xvport cv2sch --with-symbols``) walks a schematic's user cells
depth-first and ports each one's ``.sym`` and ``.sch``; the kit-master check still refuses kit masters.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from spicexplorer_core.eng import parse_value

from .devmap import DeviceMap, DeviceRule
from .emit_il import _si
from .stimulus import format_stimulus
from .xform import DEFAULT_SCALE, from_cadence, rot_flip_for

__all__ = [
    "XvportNDAError",
    "SchDump",
    "SymDump",
    "cv2sch",
    "cv2sch_hierarchy",
    "cv2sym",
    "dump_schematic",
    "dump_symbol",
    "emit_sch_text",
    "emit_sym_text",
]

_SCH_SKEL = "v {xschem version=3.4.5 file_version=1.2\n}\nG {}\nK {}\nV {}\nS {}\nE {}\n"

_PIN_SYM = {"input": "ipin.sym", "output": "opin.sym", "inputOutput": "iopin.sym"}
_PIN_DIR = {"input": "in", "output": "out", "inputOutput": "inout"}


class XvportNDAError(RuntimeError):
    """Refusal to dump geometry/content of a kit-library cellview (NDA denylist)."""


def _require_not_kit(devmap: DeviceMap, lib: str, cell: str, what: str) -> None:
    if devmap.is_kit_lib(lib):
        raise XvportNDAError(
            f"refusing to dump the {what} of {lib}/{cell}: {lib!r} is in the kit_libs "
            "NDA denylist — kit masters map back through the device table only"
        )


# --- SKILL dumps (line-oriented records; parsed below) --------------------------------

_SCH_DUMP = """\
let((cv out)
  cv = dbOpenCellViewByType("@LIB@" "@CELL@" "schematic" nil "r")
  unless(cv error("xvport: cellview not found: @LIB@/@CELL@"))
  out = ""
  foreach(sh cv~>shapes
    when(sh~>objType == "line" && car(sh~>lpp) == "wire"
      sprintf(out "%sW" out)
      foreach(p sh~>points sprintf(out "%s %L %L" out xCoord(p) yCoord(p)))
      sprintf(out "%s\\n" out))
    when(sh~>objType == "label"
      sprintf(out "%sL %L %L %s\\n" out xCoord(sh~>xy) yCoord(sh~>xy) sh~>theLabel)))
  foreach(term cv~>terminals
    let((fig bb)
      fig = car(car(term~>pins)~>figs)
      unless(fig fig = car(term~>pins)~>fig)
      when(fig
        bb = fig~>bBox
        sprintf(out "%sP %s %s %L %L\\n" out term~>name term~>direction
          quotient(plus(xCoord(car(bb)) xCoord(cadr(bb))) 2.0)
          quotient(plus(yCoord(car(bb)) yCoord(cadr(bb))) 2.0)))))
  foreach(inst cv~>instances
    unless(inst~>libName == "basic"
      sprintf(out "%sI %s %s %s %L %L %s\\n" out inst~>name inst~>libName inst~>cellName
        xCoord(inst~>xy) yCoord(inst~>xy) inst~>orient)
      let((icdf)
        icdf = cdfGetInstCDF(inst)
        when(icdf
          foreach(p icdf~>parameters
            when(p~>value != p~>defValue
              sprintf(out "%sM %s %s %L\\n" out inst~>name p~>name p~>value)))))))
  out)
"""

_SYM_DUMP = """\
let((cv out order)
  cv = dbOpenCellViewByType("@LIB@" "@CELL@" "symbol" nil "r")
  unless(cv error("xvport: symbol view not found: @LIB@/@CELL@"))
  out = ""
  foreach(sh cv~>shapes
    when(car(sh~>lpp) == "device"
      case(sh~>objType
        ("line"
          sprintf(out "%sSL" out)
          foreach(p sh~>points sprintf(out "%s %L %L" out xCoord(p) yCoord(p)))
          sprintf(out "%s\\n" out))
        ("rect"
          sprintf(out "%sSR %L %L %L %L\\n" out
            xCoord(car(sh~>bBox)) yCoord(car(sh~>bBox))
            xCoord(cadr(sh~>bBox)) yCoord(cadr(sh~>bBox))))
        ("polygon"
          sprintf(out "%sSP" out)
          foreach(p sh~>points sprintf(out "%s %L %L" out xCoord(p) yCoord(p)))
          sprintf(out "%s\\n" out))
        ("ellipse"
          sprintf(out "%sSE %L %L %L %L\\n" out
            xCoord(car(sh~>bBox)) yCoord(car(sh~>bBox))
            xCoord(cadr(sh~>bBox)) yCoord(cadr(sh~>bBox))))
        ("arc"
          sprintf(out "%sSA %L %L %L %L %L %L\\n" out
            xCoord(car(sh~>ellipseBBox)) yCoord(car(sh~>ellipseBBox))
            xCoord(cadr(sh~>ellipseBBox)) yCoord(cadr(sh~>ellipseBBox))
            sh~>startAngle sh~>stopAngle))
        ("label" nil)
        (t sprintf(out "%sSX %s\\n" out sh~>objType))))
    when(sh~>objType == "label"
      sprintf(out "%sLB %L %L %s\\n" out xCoord(sh~>xy) yCoord(sh~>xy) sh~>theLabel)))
  order = cv~>termOrder
  unless(order order = cv~>terminals~>name)
  foreach(tn order
    let((term fig bb)
      term = car(setof(x cv~>terminals x~>name == tn))
      when(term
        fig = car(car(term~>pins)~>figs)
        unless(fig fig = car(term~>pins)~>fig)
        when(fig
          bb = fig~>bBox
          sprintf(out "%sP %s %s %L %L\\n" out term~>name term~>direction
            quotient(plus(xCoord(car(bb)) xCoord(cadr(bb))) 2.0)
            quotient(plus(yCoord(car(bb)) yCoord(cadr(bb))) 2.0))))))
  out)
"""


# --- dump result models ----------------------------------------------------------------


@dataclass
class DumpInstance:
    name: str
    lib: str
    cell: str
    x: float
    y: float
    orient: str
    params: dict[str, str] = field(default_factory=dict)


@dataclass
class SchDump:
    """Parsed schematic dump: wire polylines, labels, interface pins, instances."""

    wires: list[list[tuple[float, float]]] = field(default_factory=list)
    labels: list[tuple[float, float, str]] = field(default_factory=list)
    pins: list[tuple[str, str, float, float]] = field(default_factory=list)  # name dir x y
    instances: list[DumpInstance] = field(default_factory=list)


@dataclass
class SymDump:
    """Parsed symbol dump: drawing shapes, labels, terminals (in termOrder).

    ``arcs`` are ``(x1, y1, x2, y2, start, stop)``: the arc's ``ellipseBBox`` corners plus
    its ``startAngle``/``stopAngle`` as the database holds them (radians, counter-clockwise
    from +x in Cadence's y-up frame). ``skipped`` names each device-layer shape whose
    ``objType`` the dump has no branch for, so the emitter can warn about what it did not port.
    """

    lines: list[list[tuple[float, float]]] = field(default_factory=list)
    rects: list[tuple[float, float, float, float]] = field(default_factory=list)
    polygons: list[list[tuple[float, float]]] = field(default_factory=list)
    ellipses: list[tuple[float, float, float, float]] = field(default_factory=list)
    arcs: list[tuple[float, float, float, float, float, float]] = field(default_factory=list)
    labels: list[tuple[float, float, str]] = field(default_factory=list)
    pins: list[tuple[str, str, float, float]] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def _unquote(tok: str) -> str:
    return tok[1:-1] if len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"' else tok


def _pairs(tokens: list[str]) -> list[tuple[float, float]]:
    vals = [float(t) for t in tokens]
    return list(zip(vals[0::2], vals[1::2]))


def _run_dump(client: Any, skill: str, *, timeout: int = 120) -> str:
    result = client.execute_skill(skill, timeout=timeout)
    status = getattr(result, "status", None)
    ok = getattr(status, "value", str(status)).lower() in {"success", "ok"}
    errors = getattr(result, "errors", None)
    if errors or not ok:
        raise RuntimeError(f"xvport reverse dump failed: {'; '.join(errors or [str(status)])}")
    text = str(getattr(result, "output", "") or "")
    # the daemon returns the SKILL string value quoted, with escaped inner quotes/newlines
    text = _unquote(text.strip())
    return text.replace("\\n", "\n").replace('\\"', '"')


def dump_schematic(client: Any, lib: str, cell: str, devmap: DeviceMap) -> SchDump:
    """Dump ``lib/cell/schematic`` (wires + labels + pins + instances + CDF deltas)."""
    _require_not_kit(devmap, lib, cell, "schematic")
    text = _run_dump(client, _SCH_DUMP.replace("@LIB@", lib).replace("@CELL@", cell))
    dump = SchDump()
    by_name: dict[str, DumpInstance] = {}
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        kind, rest = parts[0], parts[1:]
        if kind == "W":
            dump.wires.append(_pairs(rest))
        elif kind == "L":
            dump.labels.append((float(rest[0]), float(rest[1]), " ".join(rest[2:])))
        elif kind == "P":
            dump.pins.append((rest[0], rest[1], float(rest[2]), float(rest[3])))
        elif kind == "I":
            inst = DumpInstance(
                name=rest[0],
                lib=rest[1],
                cell=rest[2],
                x=float(rest[3]),
                y=float(rest[4]),
                orient=rest[5],
            )
            dump.instances.append(inst)
            by_name[inst.name] = inst
        elif kind == "M" and rest[0] in by_name:
            by_name[rest[0]].params[rest[1]] = _unquote(" ".join(rest[2:]))
    return dump


def dump_symbol(client: Any, lib: str, cell: str, devmap: DeviceMap) -> SymDump:
    """Dump ``lib/cell/symbol`` drawing shapes + labels + terminals (NDA-denylist-guarded)."""
    _require_not_kit(devmap, lib, cell, "symbol geometry")
    text = _run_dump(client, _SYM_DUMP.replace("@LIB@", lib).replace("@CELL@", cell))
    dump = SymDump()
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        kind, rest = parts[0], parts[1:]
        if kind == "SL":
            dump.lines.append(_pairs(rest))
        elif kind == "SR":
            dump.rects.append(tuple(float(t) for t in rest[:4]))  # type: ignore[arg-type]
        elif kind == "SP":
            dump.polygons.append(_pairs(rest))
        elif kind == "SE":
            dump.ellipses.append(tuple(float(t) for t in rest[:4]))  # type: ignore[arg-type]
        elif kind == "SA":
            dump.arcs.append(tuple(float(t) for t in rest[:6]))  # type: ignore[arg-type]
        elif kind == "SX":
            dump.skipped.append(" ".join(rest) or "?")
        elif kind == "LB":
            dump.labels.append((float(rest[0]), float(rest[1]), " ".join(rest[2:])))
        elif kind == "P":
            dump.pins.append((rest[0], rest[1], float(rest[2]), float(rest[3])))
    return dump


# --- inverse parameter mapping ----------------------------------------------------------


def _reverse_stimulus(rule: DeviceRule, cdf_params: dict[str, str], *, cell: str) -> dict[str, str]:
    """Recompose a source's one xschem ``value=`` from the CDF fields that hold it.

    The forward direction spreads `dc 0.2 ac 0` over vdc/acm/acp (and a pulse over a
    different master entirely), so without this inverse a bench read back out of Cadence
    would return with its sources blank — the same information loss in the other direction.
    """
    if rule.stimulus is None:
        return {}
    kind = rule.stimulus.cell_kind(cell) or ("dc" if "dc" in rule.stimulus.types else "")
    spec = rule.stimulus.for_kind(kind) if kind else None
    if spec is None:
        return {}
    inv = {cdf: canonical for canonical, cdf in spec.params.items()}
    fields = {inv[k]: v for k, v in cdf_params.items() if k in inv}
    value = format_stimulus(kind, fields) if fields else ""
    return {rule.stimulus.attr: value} if value else {}


def _reverse_params(
    rule: DeviceRule, cdf_params: dict[str, str], warnings: list[str], inst: str, *, cell: str = ""
) -> dict[str, str]:
    """CDF parameter deltas → xschem attrs through the inverted rule table.

    The ``per_finger`` inverse multiplies the per-finger CDF width back up to xschem's
    TOTAL width; ``simM`` maps back to ``m`` like any other table entry. Unmapped CDF
    deltas (derived params such as ``wf``, ``totalM``) are dropped silently — they are
    recomputed from the mapped ones.
    """
    inv = {cdf: attr for attr, cdf in rule.params.items()}
    attrs = {inv[k]: v for k, v in cdf_params.items() if k in inv}
    attrs.update(_reverse_stimulus(rule, cdf_params, cell=cell))
    total_attr = rule.per_finger.get("total")
    fingers_attr = rule.per_finger.get("fingers")
    if total_attr and fingers_attr and total_attr in attrs:
        ng_raw = attrs.get(fingers_attr, "1")
        if ng_raw not in ("", "1"):
            try:
                per = float(parse_value(attrs[total_attr]))
                ng = float(parse_value(ng_raw))
                attrs[total_attr] = _si(per * ng)
            except Exception:
                warnings.append(
                    f"instance {inst}: cannot recompute total {total_attr} from per-finger "
                    f"{attrs[total_attr]!r} x {fingers_attr}={ng_raw!r} — left per-finger"
                )
    return attrs


# --- .sch / .sym text emission ----------------------------------------------------------


def _f(v: float) -> str:
    return f"{v:g}"


def _attr(value: str) -> str:
    """Quote an attribute value that needs it.

    A value with whitespace is ONE value only inside quotes — a recomposed stimulus
    (`value=dc 0.2 ac 1`) re-parses as `value=dc` plus two stray tokens otherwise, which
    is the same information loss the forward direction was fixed for.
    """
    if value and not any(c in value for c in ' \t"{}'):
        return value
    escaped = (
        value.replace("\\", "\\\\").replace('"', '\\"').replace("{", "\\{").replace("}", "\\}")
    )
    return f'"{escaped}"'


def emit_sch_text(
    dump: SchDump,
    devmap: DeviceMap,
    *,
    lib: str,
    scale: float = DEFAULT_SCALE,
) -> tuple[str, list[str]]:
    """Render a schematic dump into xschem ``.sch`` text (wires + labels + pins +
    instances). ``lib`` is the dumped cellview's own library: instances of *that* library
    are local cells and become ``<cell>.sym`` references (reverse-port their symbols
    alongside); kit/analogLib masters map back through the device table."""
    warnings: list[str] = []
    out: list[str] = [_SCH_SKEL]
    for pts in dump.wires:
        xp = [from_cadence(x, y, scale) for x, y in pts]
        for (x1, y1), (x2, y2) in zip(xp, xp[1:]):
            out.append(f"N {_f(x1)} {_f(y1)} {_f(x2)} {_f(y2)} {{}}\n")
    for i, (x, y, text) in enumerate(sorted(dump.labels), start=1):
        xx, yy = from_cadence(x, y, scale)
        text = devmap.xschem_net(text) or text  # `gnd!` is the sheet's `0`
        out.append(f"C {{devices/lab_wire.sym}} {_f(xx)} {_f(yy)} 0 0 {{name=l{i} lab={text}}}\n")
    for i, (name, direction, x, y) in enumerate(sorted(dump.pins), start=1):
        sym = _PIN_SYM.get(direction, "iopin.sym")
        xx, yy = from_cadence(x, y, scale)
        name = devmap.xschem_net(name) or name
        out.append(f"C {{{sym}}} {_f(xx)} {_f(yy)} 0 0 {{name=p{i} lab={name}}}\n")
    for inst in dump.instances:
        rule = devmap.lookup_reverse(inst.lib, inst.cell)
        if rule is not None:
            symref = rule.symref or inst.cell + ".sym"
            attrs = _reverse_params(rule, inst.params, warnings, inst.name, cell=inst.cell)
            # a generic-lane rule is discriminated by an instance attribute the symref
            # cannot carry (``model=``); write it back or the round trip loses the flavour
            attrs.update(rule.literal_attrs())
        elif inst.lib == lib:
            symref = f"{inst.cell}.sym"
            attrs = dict(inst.params)
        else:
            symref = f"{inst.cell}.sym"
            attrs = dict(inst.params)
            warnings.append(
                f"instance {inst.name}: master {inst.lib}/{inst.cell} has no reverse "
                f"mapping — emitted as a local {symref} reference"
            )
        try:
            rot, flip = rot_flip_for(inst.orient)
        except KeyError:
            rot, flip = 0, 0
            warnings.append(
                f"instance {inst.name}: orient {inst.orient!r} not in the 8-entry table "
                "— emitted unrotated"
            )
        xx, yy = from_cadence(inst.x, inst.y, scale)
        attr_text = "".join(f"\n{k}={_attr(v)}" for k, v in sorted(attrs.items()))
        out.append(
            f"C {{{symref}}} {_f(xx)} {_f(yy)} {rot} {flip} {{name={inst.name}{attr_text}\n}}\n"
        )
    return "".join(out), warnings


def emit_sym_text(dump: SymDump, *, scale: float = DEFAULT_SCALE) -> tuple[str, list[str]]:
    """Render a symbol dump into xschem ``.sym`` text (drawing + pins + name texts)."""
    warnings: list[str] = []
    pin_names = {name for name, _d, _x, _y in dump.pins}
    out: list[str] = [
        "v {xschem version=3.4.5 file_version=1.2\n}\n",
        'G {}\nK {type=subcircuit\nformat="@name @pinlist @symname"\ntemplate="name=x1"\n}\n',
        "V {}\nS {}\nE {}\n",
    ]
    for pts in dump.lines:
        xp = [from_cadence(x, y, scale) for x, y in pts]
        for (x1, y1), (x2, y2) in zip(xp, xp[1:]):
            out.append(f"L 4 {_f(x1)} {_f(y1)} {_f(x2)} {_f(y2)} {{}}\n")
    for x1, y1, x2, y2 in dump.rects:
        (a, b), (c, d) = from_cadence(x1, y1, scale), from_cadence(x2, y2, scale)
        for p, q in (((a, b), (c, b)), ((c, b), (c, d)), ((c, d), (a, d)), ((a, d), (a, b))):
            out.append(f"L 4 {_f(p[0])} {_f(p[1])} {_f(q[0])} {_f(q[1])} {{}}\n")
    for pts in dump.polygons:
        xp = [from_cadence(x, y, scale) for x, y in pts]
        flat = " ".join(f"{_f(x)} {_f(y)}" for x, y in xp)
        out.append(f"P 4 {len(xp)} {flat} {{}}\n")
    for x1, y1, x2, y2 in dump.ellipses:
        (a, b), (c, d) = from_cadence(x1, y1, scale), from_cadence(x2, y2, scale)
        cx, cy = (a + c) / 2, (b + d) / 2
        r = (abs(c - a) + abs(d - b)) / 4
        if abs(abs(c - a) - abs(d - b)) > 1e-6:
            warnings.append("non-circular ellipse approximated by a circle in the .sym")
        out.append(f"A 4 {_f(cx)} {_f(cy)} {_f(r)} 0 360 {{}}\n")
    for x1, y1, x2, y2, start, stop in dump.arcs:
        # Both frames measure the angle counter-clockwise as drawn (Cadence y-up; xschem
        # y-down with `cy - r*sin`), so the y-negation leaves it unchanged: only radians ->
        # degrees, and the stop angle becomes xschem's CCW sweep (a wrap past +x included).
        (a, b), (c, d) = from_cadence(x1, y1, scale), from_cadence(x2, y2, scale)
        cx, cy = (a + c) / 2, (b + d) / 2
        r = (abs(c - a) + abs(d - b)) / 4
        if abs(abs(c - a) - abs(d - b)) > 1e-6:
            warnings.append("non-circular arc approximated by a circular arc in the .sym")
        a1 = round(math.degrees(start) % 360.0, 6) % 360.0
        sweep = round(math.degrees(stop - start) % 360.0, 6) % 360.0 or 360.0
        out.append(f"A 4 {_f(cx)} {_f(cy)} {_f(r)} {_f(a1)} {_f(sweep)} {{}}\n")
    for kind, n in sorted(Counter(dump.skipped).items()):
        warnings.append(
            f"{n} device-layer {kind!r} shape(s) not ported — the symbol dump has no "
            "branch for that shape type"
        )
    for x, y, text in dump.labels:
        if text in pin_names:
            continue  # regenerated with the pin below
        mapped = {"[@partName]": "@symname", "[@instanceName]": "@name"}.get(text, text)
        xx, yy = from_cadence(x, y, scale)
        out.append(f"T {{{mapped}}} {_f(xx)} {_f(yy)} 0 0 0.2 0.2 {{}}\n")
    for name, direction, x, y in dump.pins:  # dump order == termOrder == @pinlist order
        xx, yy = from_cadence(x, y, scale)
        d = _PIN_DIR.get(direction, "inout")
        out.append(
            f"B 5 {_f(xx - 2.5)} {_f(yy - 2.5)} {_f(xx + 2.5)} {_f(yy + 2.5)} "
            f"{{name={name} dir={d}}}\n"
        )
        out.append(f"T {{{name}}} {_f(xx)} {_f(yy - 5)} 0 0 0.15 0.15 {{}}\n")
    return "".join(out), warnings


# --- entry points -----------------------------------------------------------------------


def cv2sch(
    client: Any, lib: str, cell: str, devmap: DeviceMap, *, scale: float = DEFAULT_SCALE
) -> tuple[str, list[str]]:
    """Reverse-port ``lib/cell/schematic`` to xschem ``.sch`` text."""
    dump = dump_schematic(client, lib, cell, devmap)
    return emit_sch_text(dump, devmap, lib=lib, scale=scale)


def cv2sch_hierarchy(
    client: Any, lib: str, cell: str, devmap: DeviceMap, *, scale: float = DEFAULT_SCALE
) -> tuple[dict[str, str], list[str]]:
    """Reverse-port ``lib/cell/schematic`` and, depth-first, every user cell under it.

    Returns ``{file name: text}`` in walk order — ``<cell>.sch`` first, then each sub-cell's
    ``<sub>.sym`` and ``<sub>.sch`` — plus the warnings. The names are the ones
    :func:`emit_sch_text` references (``{<sub>.sym}``), so the files belong in one directory.

    A master is descended into only when the device table does not map it back AND it is not
    in ``kit_libs``: a mapped master (every kit and ``analogLib`` device) is written as its
    rule's ``symref``, and an unmapped kit master is named in a warning and **never dumped**
    (plan D6 — checked here before any client call, and again inside each dump). A sub-cell
    with a symbol but no schematic view (a behavioural cell) ports its ``.sym`` alone, with a
    warning; each master is dumped once, however many instances it has.
    """
    _require_not_kit(devmap, lib, cell, "schematic")
    top = dump_schematic(client, lib, cell, devmap)
    text, warnings = emit_sch_text(top, devmap, lib=lib, scale=scale)
    files: dict[str, str] = {f"{cell}.sch": text}
    owner: dict[str, tuple[str, str]] = {cell: (lib, cell)}  # file stem -> the master it holds
    seen: set[tuple[str, str]] = {(lib, cell)}

    def walk(dump: SchDump) -> None:
        for inst in dump.instances:
            key = (inst.lib, inst.cell)
            if key in seen or devmap.lookup_reverse(inst.lib, inst.cell) is not None:
                continue
            seen.add(key)
            where = f"{inst.lib}/{inst.cell}"
            if devmap.is_kit_lib(inst.lib):
                warnings.append(
                    f"{where}: not dumped — {inst.lib!r} is in the kit_libs NDA denylist; "
                    "map the master in the device table to port its instances"
                )
                continue
            if inst.cell in owner:
                other = "/".join(owner[inst.cell])
                warnings.append(f"{where}: not ported — its files would overwrite those of {other}")
                continue
            owner[inst.cell] = key
            sym_text, sym_warn = emit_sym_text(
                dump_symbol(client, inst.lib, inst.cell, devmap), scale=scale
            )
            files[f"{inst.cell}.sym"] = sym_text
            warnings.extend(f"{where}: {w}" for w in sym_warn)
            try:
                sub = dump_schematic(client, inst.lib, inst.cell, devmap)
            except RuntimeError as exc:
                if "cellview not found" not in str(exc):
                    raise
                warnings.append(f"{where}: no schematic view — ported its symbol only")
                continue
            sub_text, sub_warn = emit_sch_text(sub, devmap, lib=inst.lib, scale=scale)
            files[f"{inst.cell}.sch"] = sub_text
            warnings.extend(f"{where}: {w}" for w in sub_warn)
            walk(sub)

    walk(top)
    return files, warnings


def cv2sym(
    client: Any, lib: str, cell: str, devmap: DeviceMap, *, scale: float = DEFAULT_SCALE
) -> tuple[str, list[str]]:
    """Reverse-port ``lib/cell/symbol`` to xschem ``.sym`` text (NDA-denylist-guarded)."""
    dump = dump_symbol(client, lib, cell, devmap)
    return emit_sym_text(dump, scale=scale)
