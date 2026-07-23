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
param tables (CDF→attr), and the ``per_finger`` multiplication (a kit's CDF width may
be per-finger; the xschem attribute carries total width).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from spicexplorer_core.eng import parse_value

from .devmap import DeviceMap, DeviceRule
from .emit_il import _si
from .xform import DEFAULT_SCALE, from_cadence, rot_flip_for

__all__ = [
    "XvportNDAError",
    "SchDump",
    "SymDump",
    "cv2sch",
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
            xCoord(cadr(sh~>bBox)) yCoord(cadr(sh~>bBox))))))
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
    """Parsed symbol dump: drawing shapes, labels, terminals (in termOrder)."""

    lines: list[list[tuple[float, float]]] = field(default_factory=list)
    rects: list[tuple[float, float, float, float]] = field(default_factory=list)
    polygons: list[list[tuple[float, float]]] = field(default_factory=list)
    ellipses: list[tuple[float, float, float, float]] = field(default_factory=list)
    labels: list[tuple[float, float, str]] = field(default_factory=list)
    pins: list[tuple[str, str, float, float]] = field(default_factory=list)


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
                name=rest[0], lib=rest[1], cell=rest[2],
                x=float(rest[3]), y=float(rest[4]), orient=rest[5],
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
        elif kind == "LB":
            dump.labels.append((float(rest[0]), float(rest[1]), " ".join(rest[2:])))
        elif kind == "P":
            dump.pins.append((rest[0], rest[1], float(rest[2]), float(rest[3])))
    return dump


# --- inverse parameter mapping ----------------------------------------------------------


def _reverse_params(
    rule: DeviceRule, cdf_params: dict[str, str], warnings: list[str], inst: str
) -> dict[str, str]:
    """CDF parameter deltas → xschem attrs through the inverted rule table.

    The ``per_finger`` inverse multiplies the per-finger CDF width back up to xschem's
    TOTAL width; ``simM`` maps back to ``m`` like any other table entry. Unmapped CDF
    deltas (derived params such as ``wf``, ``totalM``) are dropped silently — they are
    recomputed from the mapped ones.
    """
    inv = {cdf: attr for attr, cdf in rule.params.items()}
    attrs = {inv[k]: v for k, v in cdf_params.items() if k in inv}
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
        out.append(
            f"C {{devices/lab_wire.sym}} {_f(xx)} {_f(yy)} 0 0 {{name=l{i} lab={text}}}\n"
        )
    for i, (name, direction, x, y) in enumerate(sorted(dump.pins), start=1):
        sym = _PIN_SYM.get(direction, "iopin.sym")
        xx, yy = from_cadence(x, y, scale)
        out.append(f"C {{{sym}}} {_f(xx)} {_f(yy)} 0 0 {{name=p{i} lab={name}}}\n")
    for inst in dump.instances:
        rule = devmap.lookup_reverse(inst.lib, inst.cell)
        if rule is not None:
            symref = rule.symref or inst.cell + ".sym"
            attrs = _reverse_params(rule, inst.params, warnings, inst.name)
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
        attr_text = "".join(f"\n{k}={v}" for k, v in sorted(attrs.items()))
        out.append(
            f"C {{{symref}}} {_f(xx)} {_f(yy)} {rot} {flip} "
            f"{{name={inst.name}{attr_text}\n}}\n"
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


def cv2sym(
    client: Any, lib: str, cell: str, devmap: DeviceMap, *, scale: float = DEFAULT_SCALE
) -> tuple[str, list[str]]:
    """Reverse-port ``lib/cell/symbol`` to xschem ``.sym`` text (NDA-denylist-guarded)."""
    dump = dump_symbol(client, lib, cell, devmap)
    return emit_sym_text(dump, scale=scale)
