"""Emit a deterministic, self-contained SKILL ``.il`` that rebuilds an xschem ``.sch``
as a Virtuoso schematic cellview (Mode A: placement + net-label connectivity).

The artifact is plain text a human can read, diff, golden-test, and ``load()`` in a CIW —
no bridge required to *generate* it. Structure:

* two helper procedures, defined once —
  ``xvSetParams`` sets CDF parameters **and fires their callbacks** (the ``dbReplaceProp``
  shortcut silently skips callback-derived CDF params), falling
  back to plain properties for masters without CDF (local subcircuit symbols). A name the
  master's CDF has not got aborts the load with ``error()`` naming every such name and the
  master: it used to ``printf`` to the CIW, which nothing client-side reads, so a map
  spelling the CDF for a different kit ported an entire bench of dead sources and still
  reported success. ``load_il`` turns that into a non-zero ``xvport`` exit on stderr.
  It then writes every named parameter the CDF setter left unwritten as a plain instance
  property: ``cdfUpdateInstParam`` stores only what DIFFERS from the master's CDF default, so
  a device sized AT its default used to carry no property at all and a lost sizing read back
  identical to a correct port;
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

import math
import re
from dataclasses import dataclass, field

from spicexplorer_core.eng import parse_value

from ..sch_parser import Schematic
from ..sym_library import SymLibrary
from .devmap import DeviceMap, DeviceRule
from .netex import NetExtraction, PinNet, extract_nets
from .stimulus import StimulusError, parse_stimulus
from .xform import DEFAULT_SCALE, direction_to_cadence, orient_for, to_cadence

__all__ = ["EmitResult", "emit_schematic_il"]

_STUB_LEN = 0.25
_LABEL_HEIGHT = 0.0625

#: Minimum centre-to-centre distance, in Cadence user units, between two placed instances.
#:
#: **`--scale` scales the PLACEMENT and nothing else.** `dbCreateInst` takes no magnification,
#: so the masters keep their own size however tightly the instances are placed, and `_STUB_LEN`
#: is likewise a constant in user units handed to a real `schCreateWire`. Tighten the scale far
#: enough and a terminal's label stub reaches into the neighbouring instance and connects to its
#: pin — silently. Bulk terminals go first, because they sit at the symbol edge: reducing
#: `--scale` from the default to 0.004 moved five bulk terminals onto the wrong nets while every
#: device kept its correct model and w/l/m, the cellview opened normally, and a DC operating
#: point would still have solved (issue #204). A per-device parameter diff passes that.
#:
#: The value is the point at which the MASTERS THEMSELVES would start to overlap: the reporter
#: measured a symbol at about one user unit tall, so two adjacent instances need about one unit
#: centre to centre before their bodies touch, let alone their stubs. It is NOT derived from
#: master geometry — that lives in the Cadence library and is invisible from here.
#:
#: Calibration, so the next person can move it with evidence rather than taste:
#:   * 1.25 — the tightest pitch in this repo's own corpus at the default scale (a bench whose
#:     VIN and RL sit that far apart), and it ports correctly. The floor must be below this.
#:   * ~0.4 — the reported sheet at `--scale 0.004`, which rewired five bulk terminals. 0.004 is
#:     0.32x the default, so whatever its pitch was at 0.0125, it was about a third of it there.
#: Raise this if a port at a pitch above it is ever found rewired; lower it only with a sheet
#: that ports correctly below it.
_MIN_INSTANCE_PITCH = 1.0

#: A stub may never reach more than this fraction of the way to the nearest neighbouring
#: instance, whatever the scale.
_STUB_PITCH_FRACTION = 0.4

_NAME_OK = re.compile(r"[^A-Za-z0-9_!]")

_PIN_MASTER = {"in": "ipin", "out": "opin", "inout": "iopin"}
_PIN_DIRECTION = {"in": "input", "out": "output", "inout": "inputOutput"}

_HELPERS = """\
; --- xvport helpers (idempotent redefinition) --------------------------------
procedure( xvSetParams(cv instName pairs)
  let((inst iCDF cCDF saved p cb unknown cdfgData cdfgForm)
    inst = car(setof(x cv~>instances x~>name == instName))
    unless(inst error("xvport: instance not found: %s" instName))
    iCDF = cdfGetInstCDF(inst)
    if( !iCDF
      then  ; no CDF (e.g. a local subcircuit symbol) -> plain string properties
        foreach(pair pairs dbReplaceProp(inst car(pair) "string" cadr(pair)))
      else
        cCDF = cdfGetCellCDF(ddGetObj(inst~>libName inst~>cellName))
        ; A CDF name this master has not got is a WRONG PORT, not a warning: the value goes
        ; nowhere and the instance keeps its template default, so a pulse source ports at
        ; zero amplitude while everything reports success (#214). Collect every such name
        ; and FAIL THE LOAD -- load_il turns the SKILL error into a non-zero xvport exit with
        ; the text on stderr, where the old printf only reached the CIW nobody is reading.
        ; This runs BEFORE the save/restore block below, so an aborted call cannot leave the
        ; base cell's CDF holding this instance's values for the rest of the session.
        unknown = nil
        foreach(pair pairs unless(get(cCDF car(pair)) unknown = cons(car(pair) unknown)))
        when(unknown
          error("xvport: unknown CDF param(s) %s on instance %s (master %s/%s) -- the device map spells them for a different kit. Probe the real names with cdfGetBaseCellCDF and fix the map's params/stimulus rows; nothing was written for this instance." buildString(reverse(unknown) ", ") instName inst~>libName inst~>cellName))
        saved = makeTable('s)
        foreach(p cCDF~>parameters setarray(saved p~>name p~>value))
        foreach(p cCDF~>parameters
          when(get(iCDF p~>name) putpropq(p get(iCDF p~>name)~>value value)))
        cdfgData = cCDF
        cdfgForm = cCDF
        foreach(pair pairs
          p = get(cCDF car(pair))
          when(p p~>value = cadr(pair)))
        foreach(pair pairs
          p = get(cCDF car(pair))
          when(p
            cb = p~>callback
            when(cb && cb != "" errset(evalstring(cb) t))))
        cdfUpdateInstParam(inst)
        foreach(p cCDF~>parameters putpropq(p arrayref(saved p~>name) value))
        ; cdfUpdateInstParam stores only what DIFFERS from the master's CDF default, so a device
        ; sized AT its default carries no instance property at all: 72 of 302 MOS instances in one
        ; ported library had no `w` whatever, and a read-back that asks the CDF for the EFFECTIVE
        ; value prints the right number over a width the port never wrote -- a lost sizing and a
        ; correct port read back IDENTICAL (#241). Write what the CDF setter left unwritten, so the
        ; schematic states its own sizing to the database, the netlister and the human opening it.
        ; Only where the property is ABSENT: a value the callbacks normalised (the w -> wf
        ; derivation) is the one that must survive. It runs AFTER the base cell's CDF has been
        ; restored above -- it touches the instance only, and an error here must not leave that
        ; CDF holding this instance's values for the rest of the session (#214).
        foreach(pair pairs
          unless(dbFindProp(inst car(pair))
            dbReplaceProp(inst car(pair) "string" cadr(pair))))
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


def _closest_pair(
    placed: list[tuple[str, float, float]],
) -> tuple[float | None, tuple[str, str] | None]:
    """The smallest centre-to-centre distance among placed instances, and the pair at it.

    ``(None, None)`` for fewer than two instances — a single-instance sheet has no neighbour
    to be rewired onto. O(n²) over instances, which is a sheet-sized number.
    """
    best: float | None = None
    who: tuple[str, str] | None = None
    for i in range(len(placed)):
        ni, xi, yi = placed[i]
        for j in range(i + 1, len(placed)):
            nj, xj, yj = placed[j]
            d = math.hypot(xi - xj, yi - yj)
            if best is None or d < best:
                best, who = d, (ni, nj)
    return best, who


@dataclass
class EmitResult:
    """The emitted ``.il`` text plus the expectation table ``--verify`` diffs against."""

    il: str
    # (instance, cadence term) -> net — what read_schematic should report after the load.
    expected_bindings: dict[tuple[str, str], str] = field(default_factory=dict)
    expected_ports: dict[str, str] = field(default_factory=dict)  # pin name -> direction
    instances: dict[str, tuple[str, str]] = field(default_factory=dict)  # name -> (lib, cell)
    warnings: list[str] = field(default_factory=list)
    # Reasons this port must NOT be loaded: a stimulus nobody could read, a CDF field the
    # map does not route, a symbolic value the caller did not opt into, a device symbol that
    # resolved to nothing. A warning the caller returns 0 alongside is how a silently-wrong
    # circuit reaches the editor.
    errors: list[str] = field(default_factory=list)
    # The sheet's simulator-directive blocks, in drawing order: (block name, verbatim text).
    # They are annotations, not circuit elements (#215), so nothing here builds them as
    # objects — but dropping them without a word is how a ported testbench arrives with the
    # stimulus, the DUT and no measurement setup (#250). The caller writes them beside the
    # `.il` and warns; `directives_note` additionally draws them into the cellview.
    directives: list[tuple[str, str]] = field(default_factory=list)
    # Device instances the sheet has and this `.il` does NOT build, in drawing order, by their
    # drawn names. Every entry also has an error above; the list is what lets a downstream
    # check (the netcheck) name them, since neither netlister it compares can see them (#226).
    dropped: list[str] = field(default_factory=list)
    # Parameter provenance for the cell (#241). `params_explicit` counts the (instance, CDF
    # parameter) pairs this `.il` writes EXPLICITLY -- every one the device map names and the
    # sheet gives a value for, whether or not it equals the master's CDF default, so a size that
    # happens to be the default is still a property in the database and not a silent inheritance.
    # `params_omitted` names the ones the emitter deliberately did not write, with the reason.
    params_explicit: int = 0
    params_omitted: list[str] = field(default_factory=list)

    def param_summary(self) -> str:
        """The per-cell line a caller records instead of a bare IDENTICAL (#241).

        Omissions are grouped by REASON and named three-at-a-time: a 300-instance port omits
        the same parameter for the same reason 300 times, and a line nobody can read is a line
        nobody records.
        """
        line = f"{self.params_explicit} params explicit"
        if not self.params_omitted:
            return line
        groups: dict[str, list[str]] = {}
        for entry in self.params_omitted:
            name, _, why = entry.partition(": ")
            groups.setdefault(why, []).append(name)
        parts = [
            f"{why}: {', '.join(names[:3])}" + (", …" if len(names) > 3 else "")
            for why, names in groups.items()
        ]
        return f"{line}, {len(self.params_omitted)} omitted ({'; '.join(parts)})"


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


def _apply_per_finger(
    rule: DeviceRule, attrs: dict[str, str], params: dict[str, str]
) -> tuple[str | None, str | None]:
    """Divide a TOTAL-width attribute by the finger count before it reaches a PER-FINGER CDF
    parameter (``rule.per_finger`` — e.g. IHP xschem ``w`` is total, a kit CDF ``w`` is often
    per-finger). Mutates ``params``; returns ``(warning, dropped CDF parameter)`` when the
    division is needed but impossible (symbolic values), in which case the width parameter is
    dropped rather than silently netlisting at ``fingers ×`` its intended size. The dropped
    name is what the per-cell parameter summary reports as omitted."""
    total_attr = rule.per_finger.get("total")
    fingers_attr = rule.per_finger.get("fingers")
    if not total_attr or not fingers_attr:
        return None, None
    cdf_w = rule.params.get(total_attr)
    if cdf_w is None or cdf_w not in params:
        return None, None
    ng_raw = attrs.get(fingers_attr, "")
    if ng_raw in ("", "1"):
        return None, None  # one finger: total == per-finger
    try:
        total = float(parse_value(attrs[total_attr]))
        ng = float(parse_value(ng_raw))
    except Exception:
        dropped = params.pop(cdf_w)
        return (
            f"cannot derive per-finger {cdf_w} from {total_attr}={attrs[total_attr]!r} / "
            f"{fingers_attr}={ng_raw!r} — dropping {cdf_w}={dropped!r} (set it manually)",
            cdf_w,
        )
    if ng <= 0:
        dropped = params.pop(cdf_w)
        return (
            f"invalid finger count {fingers_attr}={ng_raw!r} — dropping {cdf_w}={dropped!r}",
            cdf_w,
        )
    params[cdf_w] = _si(total / ng)
    return None, None


def _stimulus_params(
    rule: DeviceRule, attrs: dict[str, str], *, symbolic: bool
) -> tuple[dict[str, str], str, list[str]]:
    """Split a source's one stimulus attribute across the CDF fields that hold it.

    Returns ``(params, cell, errors)`` — the CDF pairs to set, the master this stimulus kind
    belongs on (a pulse is a different analogLib cell from a dc source), and the reasons the
    port must FAIL. Nothing here degrades to a warning: an unreadable stimulus written into
    one field is how a bench ends up sitting at an operating point nobody chose (#182), and
    that used to be a warning the port returned 0 alongside.
    """
    assert rule.stimulus is not None
    text = attrs.get(rule.stimulus.attr, "")
    if not text.strip():
        return {}, rule.cell, []
    try:
        stim = parse_stimulus(text, symbolic=symbolic)
    except StimulusError as exc:
        return {}, rule.cell, [str(exc)]
    spec = rule.stimulus.for_kind(stim.kind)
    if spec is None:
        known = ", ".join(sorted(rule.stimulus.types)) or "(none)"
        return (
            {},
            rule.cell,
            [
                f"the map declares no CDF fields for a {stim.kind!r} stimulus on "
                f"{rule.lib}/{rule.cell} (it declares: {known}) — add "
                f"stimulus.types.{stim.kind}.params to the rule"
            ],
        )
    params: dict[str, str] = {}
    unmapped: list[str] = []
    for canonical, value in sorted(stim.fields.items()):
        cdf = spec.params.get(canonical)
        if cdf is None:
            # `type` is only needed by a CDF that selects the waveform itself (srcType); a
            # per-kind cell carries the fact in the master instead, so it is never missing.
            if canonical != "type":
                unmapped.append(f"{canonical}={value}")
            continue
        params[cdf] = value
    errors = []
    if unmapped:
        errors.append(
            f"stimulus {text!r} sets {', '.join(unmapped)}, which this map does not route to "
            f"any CDF parameter of {stim.kind!r} — add them to stimulus.types.{stim.kind}."
            "params (dropping them would change the stimulus silently)"
        )
    return params, (spec.cell or rule.cell), errors


#: Point-coincidence tolerance, in xschem units, for the stub-collision test below.
_STUB_TOL = 0.51


def _perpendiculars(d: tuple[float, float]) -> tuple[tuple[float, float], tuple[float, float]]:
    """The two axis-aligned unit directions perpendicular to ``d`` (never a signed zero)."""
    return ((-d[1] + 0.0, d[0] + 0.0), (d[1] + 0.0, -d[0] + 0.0))


def _same_stub_line(p: PinNet, dp: tuple[float, float], q: PinNet, dq: tuple[float, float]) -> bool:
    """True when two terminals' label stubs run along ONE line (so their labels can collide).

    Same direction, and the offset between the two pins is parallel to it: both stubs then
    lie on the same ray, and the only thing holding their labels apart is the distance
    between the pins *on the Cadence master*, which the xschem drawing does not determine.
    """
    if dp != dq:
        return False
    ox, oy = q.x - p.x, q.y - p.y
    return abs(ox * dp[1] - oy * dp[0]) <= _STUB_TOL  # perpendicular component ~ 0


def _decollide_stub_dirs(
    sch: Schematic,
    nx: NetExtraction,
    labeled: list[tuple[str, str]],
    *,
    allow_collinear: bool = False,
) -> tuple[dict[tuple[str, str], tuple[float, float]], list[str], list[str]]:
    """Fan out the Mode-A label stubs of one instance that would be drawn on one line.

    ``xvLabelTerm`` draws each stub from the terminal's *Cadence* pin centre, resolved at
    load time — the drawing's pin spacing is not the master's. Tie a device's bulk to its
    source with the straight run between them (both pins in one column of the xschem symbol)
    and both terminals leave in the same direction along that column: on the master, whose
    two pins may be a fraction of ``_STUB_LEN`` apart, the two stubs overlap and one label
    wins, leaving both terminals on an auto-named net while every netlist gate stays green
    (#236).

    Returns ``(direction per labeled terminal, warnings, errors)``. A re-aimed terminal keeps
    its pin and its net and only turns its stub 90 degrees, to the perpendicular pointing AWAY
    from the instance origin — two distinct directions from one point give two distinct label
    points for any master geometry, which is the only guarantee available offline.

    The fan-out is then CHECKED, per instance, against the invariant it exists to establish:
    no two of an instance's stubs may still run along one line. Three terminals of one device
    on a single straight run (drain, source and bulk dropped onto one rail — the shape a unit
    gate load has) is the case with no answer: one stub keeps the run, and neither
    perpendicular is provably outward when the pins sit on the instance's own axis. Such an
    instance is REFUSED, naming it and its terminals, rather than built wrong — a load that
    cannot be expressed as labels must stop the port, not produce a plausible cellview whose
    terminals land on auto-named nets that every netlist gate calls equivalent (#267).
    ``allow_collinear=True`` (the CLI's ``--allow-collinear-labels``) downgrades that refusal
    to a warning, for a caller who has verified the built cellview net by net.
    """
    dirs: dict[tuple[str, str], tuple[float, float]] = {k: nx.pin_nets[k].stub_dir for k in labeled}
    warnings: list[str] = []
    errors: list[str] = []
    by_inst: dict[str, list[tuple[str, str]]] = {}
    for key in labeled:
        by_inst.setdefault(key[0], []).append(key)

    for inst_name in sorted(by_inst):
        comp = sch.component(inst_name)
        if comp is None:
            continue
        keys = by_inst[inst_name]
        # cluster the terminals that share one stub line (`dirs` still holds the drawing's
        # own directions here)
        for cluster in _stub_line_groups(nx, keys, dirs):
            if len(cluster) < 2:
                continue
            d = nx.pin_nets[cluster[0]].stub_dir
            # the terminal furthest along the stub direction keeps its aim: its stub is the
            # one that does not have to cross a sibling pin to get out
            order = sorted(
                cluster,
                key=lambda k: (
                    -(nx.pin_nets[k].x * d[0] + nx.pin_nets[k].y * d[1]),
                    k,
                ),
            )
            for key in order[1:]:
                pn = nx.pin_nets[key]
                rx, ry = pn.x - comp.x, pn.y - comp.y
                chosen: tuple[float, float] | None = None
                for cand in sorted(_perpendiculars(d), key=lambda c: -(c[0] * rx + c[1] * ry)):
                    if cand[0] * rx + cand[1] * ry <= 0:
                        continue  # inward (or undecidable): a stub into the body can short
                    if any(
                        _same_stub_line(nx.pin_nets[other], dirs[other], pn, cand)
                        for other in keys
                        if other != key
                    ):
                        continue
                    chosen = cand
                    break
                if chosen is None:
                    # Nothing to aim this terminal at. Leave its stub where the drawing put
                    # it and carry on with the rest of the cluster — the residual check
                    # below is the one that decides the port, so a cluster with one
                    # unfixable terminal is reported once, naming every terminal still on
                    # that line, instead of aborting the fan-out half-done (#267).
                    continue
                dirs[key] = chosen
                warnings.append(
                    f"instance {inst_name}: terminals "
                    f"{', '.join(k[1] for k in cluster)} would draw their net labels along "
                    f"one line (same direction, same column) — {key[1]}'s stub is re-aimed "
                    f"to ({chosen[0]:g}, {chosen[1]:g}) so the two labels land on distinct "
                    f"points whatever the master's pin spacing is (#236)"
                )
        # the invariant, re-derived from the FINAL directions (#267)
        for group in _stub_line_groups(nx, keys, dirs):
            if len(group) < 2:
                continue
            msg = (
                f"instance {inst_name}: terminals "
                f"{', '.join(sorted(k[1] for k in group))} draw their Mode-A net labels "
                f"along one line and cannot be fanned out (no perpendicular points away "
                f"from the instance origin, or every direction is taken). On the Cadence "
                f"master those pins may sit closer than the stub length, so the labels "
                f"land on one point and one wins — leaving the terminals on an auto-named "
                f"net that no netlist gate sees. Port this sheet with --mode wires (the "
                f"default), draw the tie as a detour around the body, or pass "
                f"--allow-collinear-labels if you have verified the built cellview net by "
                f"net."
            )
            if allow_collinear:
                warnings.append(msg + " [--allow-collinear-labels]")
            else:
                errors.append(msg)
    return dirs, warnings, errors


def _stub_line_groups(
    nx: NetExtraction,
    keys: list[tuple[str, str]],
    dirs: dict[tuple[str, str], tuple[float, float]],
) -> list[list[tuple[str, str]]]:
    """Group one instance's labeled terminals by the LINE their stubs run along."""
    groups: list[list[tuple[str, str]]] = []
    for key in sorted(keys):
        pn = nx.pin_nets[key]
        for group in groups:
            head = nx.pin_nets[group[0]]
            if _same_stub_line(head, dirs[group[0]], pn, dirs[key]):
                group.append(key)
                break
        else:
            groups.append([key])
    return groups


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
    allow_dense: bool = False,
    allow_collinear: bool = False,
    local_prefix: str = "",
    symbolic: bool = False,
    directives_note: bool = True,
) -> EmitResult:
    """Render ``sch`` into a Mode-A ``.il`` building ``lib/cell`` (see module docstring).

    Unmapped device symrefs are treated as *local* symbols — instances of
    ``(lib, <basename>, symbol)`` in the target library itself; the ``--with-symbols``
    hierarchy walk is what creates those masters first (it passes them as ``local_cells``
    so they don't warn).

    ``mode="labels"`` connects every terminal with a named wire stub; ``mode="wires"``
    instead draws the xschem wire segments verbatim (scaled), labels each net once on its
    longest segment, and geometrically patches each terminal's real pin centre to the
    drawing's pin point (a zero-length no-op for ported local symbols, whose pin geometry is
    a scaled copy of the xschem one). A labels-mode cellview NETLISTS correctly and shows no
    wiring, so the ``xvport`` CLI defaults to ``wires`` (#267); this keyword's default is
    unchanged, so a library caller keeps the behaviour it had.

    ``allow_collinear=True`` downgrades the refusal of an instance whose Mode-A stubs still
    run along one line after the fan-out (see :func:`_decollide_stub_dirs`) to a warning.

    ``local_prefix`` prepends every locally-created master cell reference (the ``--prefix``
    escape hatch when an xschem basename collides with a kit cell name).

    ``symbolic=True`` opts into parameter values that are not numbers (a design variable, an
    expression): they are written to the CDF verbatim and reported as warnings. By default
    such a value is an **error** in ``result.errors`` — Cadence turns an unresolved word into
    a design variable, so a port that returned 0 used to hand back a cellview whose devices
    and sources were sized by whatever those variables happened to hold (#182).

    ``directives_note=True`` (the default) additionally draws the sheet's directive blocks
    (``code``/``code_shown``) into the cellview as schematic NOTE labels below the drawn
    objects — text a human opening the cellview can read. They are annotations, never
    circuit objects: they do not netlist, and the built circuit is identical without them.
    The text is also returned in ``result.directives`` whatever the flag says, so the caller
    can write it out beside the ``.il`` and warn that it was not ported as circuitry (#250).

    A DEVICE whose ``symref`` resolves to no ``.sym`` on the search path is likewise an
    **error** (and is listed in ``result.dropped``): it has no pin geometry, so it cannot be
    placed at all, and a port that drops a device builds a different circuit than the one
    drawn. An annotation that does not resolve (``title``/``code``/``noconn`` — anything
    ``SchComponent.is_device`` excludes) is not a circuit element and stays silent (#226).
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
        # A net the map declares GLOBAL keeps its Cadence global name (`0` -> `gnd!`) instead
        # of being sanitized into an ordinary net. Without it a ported bench has no ground:
        # `0` sanitizes to `net0`, every ground terminal lands on that ordinary net, and
        # spectre refuses to read the cellview (#182).
        cadence_global = devmap.global_for(raw)
        if cadence_global is not None:
            net_alias[raw] = cadence_global
            taken_nets.add(cadence_global)
            continue
        clean = base = _sanitize(raw, prefix="net")
        n = 2
        while clean in taken_nets:
            clean = f"{base}_{n}"
            n += 1
        if clean != base:
            result.warnings.append(f"net name collision after sanitization: {raw!r} -> {clean!r}")
        taken_nets.add(clean)
        net_alias[raw] = clean
    inst_names: dict[str, str] = {}
    placed: list[tuple[str, float, float]] = []  # raw component name -> final (collision-free) name
    body: list[str] = []

    body.append(f'cv = dbOpenCellViewByType("{_s(lib)}" "{_s(cell)}" "schematic" "schematic" "w")')

    # --- instances + params ---------------------------------------------------
    for comp in sch.components:
        if not comp.is_device or comp.is_port:
            continue
        sym = symlib.load(comp.symref)
        if sym is None:
            # No symbol -> no pins -> nothing to place. This used to be a WARNING the port
            # returned 0 alongside: the cellview was built with the device missing, and the
            # netcheck then compared it against an xschem re-netlist of the SAME unresolvable
            # source and called the pair equivalent — a comparator bench ported green with no
            # comparator in it (#226). Refuse instead, and say where the symbol was looked for.
            roots = ", ".join(str(r) for r in symlib.search_paths) or "<no search path>"
            result.dropped.append(comp.name)
            msg = (
                f"instance {comp.name}: symbol not resolvable: {comp.symref} — it would be "
                f"DROPPED, building a cellview the sheet does not describe. searched: {roots}. "
                "Put the symbol on the search path (next to the source `.sch`, in its parent, "
                "or in a vendored library), or port the sheet from the directory it lives in."
            )
            if msg not in result.errors:
                result.errors.append(msg)
            continue
        if sym.type == "label":
            continue
        rule = devmap.lookup(comp.symref, comp.attrs)
        pf_warning: str | None = None
        pf_dropped: str | None = None
        # (CDF parameter, why) for every value this instance HAS and the `.il` still will not
        # write — the other half of the explicit-parameter contract (#241).
        omitted: list[tuple[str, str]] = []
        stim_errors: list[str] = []
        if rule is not None:
            mlib, mcell, mview = rule.lib, rule.cell, rule.view
            params = {
                rule.params[k]: v for k, v in comp.attrs.items() if k in rule.params and v != ""
            }
            # A parameter the map names and the sheet gives no value for cannot be written —
            # the master's CDF default will supply it. Name it, so "N explicit, M from the
            # default" is a thing a caller can record (#241).
            omitted += [
                (rule.params[k], f"the sheet sets no {k}")
                for k in sorted(rule.params)
                if not comp.attrs.get(k)
            ]
            if rule.stimulus is not None:
                # A source's `value` is a whole stimulus, and the kind it declares can pick a
                # different master (a pulse is not an analogLib `vdc`), so this may override
                # the rule's cell.
                stim_params, mcell, stim_errors = _stimulus_params(
                    rule, comp.attrs, symbolic=symbolic
                )
                params.pop(rule.params.get(rule.stimulus.attr, ""), None)
                params.update(stim_params)
            pf_warning, pf_dropped = _apply_per_finger(rule, comp.attrs, params)
            if pf_dropped is not None and pf_warning is not None:
                omitted.append((pf_dropped, pf_warning))
        else:
            stem = comp.symref.rsplit("/", 1)[-1]
            stem = stem[:-4] if stem.endswith(".sym") else stem
            mlib, mcell, mview = lib, _sanitize(f"{local_prefix}{stem}", prefix="cell"), "symbol"
            params = {}
            if mcell not in (local_cells or ()):
                # Not mapped by any rule AND not a master this run creates: there is nothing
                # for `dbOpenCellViewByType` to open. Emitting it anyway produced a SKILL file
                # that failed to load at the closing paren of the outermost form, naming
                # nothing — the cause was visible only by grepping the generated .il for
                # "master not found" (issue #205). Refuse at emit time instead, and say what
                # is missing.
                model = comp.attrs.get("model", "")
                msg = (
                    f"no map rule for symref {comp.symref}"
                    + (f" (model={model})" if model else "")
                    + f" — it would resolve to {mlib}/{mcell}, which nothing creates. "
                    "Add a rule for it (`xvport dump-map` is a working starting point), "
                    "or pass --with-symbols to port its symbol first."
                )
                if msg not in result.errors:
                    result.errors.append(msg)
            dropped = sorted(
                k for k, v in comp.attrs.items() if k not in _BOOKKEEPING_ATTRS and v != ""
            )
            if dropped:
                result.warnings.append(
                    f"instance {_sanitize(comp.name, prefix='I')}: unmapped local master — "
                    f"xschem parameter(s) {dropped} are NOT transferred"
                )
                omitted += [
                    (k, "unmapped local master — no rule names a CDF parameter for it")
                    for k in dropped
                ]
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
        for err in stim_errors:
            result.errors.append(f"instance {inst}: {err}")
        x, y = to_cadence(comp.x, comp.y, scale)
        placed.append((inst, x, y))
        orient = orient_for(comp.rot, comp.flip)
        body.append(
            "let((m) "
            f'm = dbOpenCellViewByType("{_s(mlib)}" "{_s(mcell)}" "{_s(mview)}" nil "r") '
            f'unless(m error("xvport: master not found: {_s(mlib)}/{_s(mcell)}")) '
            f'dbCreateInst(cv m "{_s(inst)}" list({_fmt(x)} {_fmt(y)}) "{orient}"))'
        )
        result.instances[inst] = (mlib, mcell)
        result.params_omitted += [f"{inst}.{name}: {why}" for name, why in omitted]
        # Every pair below reaches the database as an instance property, default-valued or not
        # (see the `dbFindProp`/`dbReplaceProp` pass in xvSetParams) — so it is EXPLICIT.
        result.params_explicit += len(params)
        if params:
            pairs = " ".join(f'list("{_s(k)}" "{_s(v)}")' for k, v in sorted(params.items()))
            body.append(f'xvSetParams(cv "{_s(inst)}" list({pairs}))')
            unresolved = [
                v
                for v in params.values()
                if re.search(r"[A-Za-z_]{2,}", v) and not re.fullmatch(r"[0-9.]+[a-zA-Z]*", v)
            ]
            if unresolved:
                where = result.warnings if symbolic else result.errors
                where.append(
                    f"instance {inst}: symbolic parameter value(s) {unresolved} passed verbatim"
                    + (
                        " (--allow-symbolic): check the CDF by hand"
                        if symbolic
                        else " — Cadence makes a design variable of an unresolved word, so the "
                        "ported device is sized by whatever that variable holds. Resolve it in "
                        "the sheet, or pass --allow-symbolic to accept it"
                    )
                )

    # --- scale sanity: the masters do NOT scale, only the placement does ---------
    # See _MIN_INSTANCE_PITCH. Computed over placed instance ORIGINS only; ports, labels and
    # wire vertices are excluded because nothing is instantiated at them.
    stub_len = _STUB_LEN
    pitch, near = _closest_pair(placed)
    if pitch is not None and near is not None:
        stub_len = min(_STUB_LEN, _STUB_PITCH_FRACTION * pitch)
        if pitch < _MIN_INSTANCE_PITCH:
            needed = scale * _MIN_INSTANCE_PITCH / pitch
            msg = (
                f"--scale {scale:g} places {near[0]} and {near[1]} {pitch:.4g} user units "
                f"apart, under the {_MIN_INSTANCE_PITCH:g}-unit minimum. Cadence masters do "
                f"not scale with --scale, so at this pitch a terminal's label stub can land "
                f"on a neighbouring instance's pin and silently rewire the cellview — bulk "
                f"terminals first, which no per-device parameter diff catches. Raise --scale "
                f"to at least {needed:.4g}, or pass --allow-dense if you have verified the "
                f"built cellview net by net."
            )
            if allow_dense:
                result.warnings.append(msg + " [--allow-dense]")
            else:
                result.errors.append(msg)

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

    # Terminals that get a drawn, labeled stub — the ones whose labels can collide.
    labeled = [
        key
        for key, pn in sorted(nx.pin_nets.items())
        if sch.component(key[0]) is not None and not (mode == "wires" and pn.on_wire)
    ]
    stub_dirs, fan_warnings, fan_errors = _decollide_stub_dirs(
        sch, nx, labeled, allow_collinear=allow_collinear
    )
    result.warnings.extend(fan_warnings)
    result.errors.extend(fan_errors)

    for (inst_name, pin_name), pn in sorted(nx.pin_nets.items()):
        comp = sch.component(inst_name)
        if comp is None:
            continue
        rule = devmap.lookup(comp.symref, comp.attrs)
        term = rule.term_for(pin_name) if rule is not None else pin_name
        inst = inst_names.get(inst_name, _sanitize(inst_name, prefix="I"))
        net = net_alias[pn.net]
        if mode == "wires" and pn.on_wire:
            tx, ty = to_cadence(pn.x, pn.y, scale)
            body.append(f'xvPatchTerm(cv "{_s(inst)}" "{_s(term)}" {_fmt(tx)} {_fmt(ty)})')
        else:  # labels mode — and the wire-mode fallback for nets with no drawn segments
            dx, dy = direction_to_cadence(*stub_dirs.get((inst_name, pin_name), pn.stub_dir))
            body.append(
                f'xvLabelTerm(cv "{_s(inst)}" "{_s(term)}" "{_s(net)}" '
                f"{_fmt(dx)} {_fmt(dy)} {_fmt(stub_len)})"
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

    # --- directives (annotation only; never a circuit object) --------------------
    for comp in sch.directives:
        text = comp.directive_text
        if text.strip():
            result.directives.append((comp.name or "directives", text))
    if result.directives and directives_note:
        # below everything drawn, so the note never overlaps the circuit
        ys = [y for _n, _x, y in placed]
        xs = [x for _n, x, _y in placed]
        for port in nx.ports:
            px, py = to_cadence(port.x, port.y, scale)
            xs.append(px)
            ys.append(py)
        for segs in nx.net_segments.values():
            for x1, y1, x2, y2 in segs:
                for sx, sy in (to_cadence(x1, y1, scale), to_cadence(x2, y2, scale)):
                    xs.append(sx)
                    ys.append(sy)
        for pn in nx.pin_nets.values():
            px, py = to_cadence(pn.x, pn.y, scale)
            xs.append(px)
            ys.append(py)
        left = min(xs) if xs else 0.0
        step = 2 * _LABEL_HEIGHT
        cursor = (min(ys) if ys else 0.0) - 4 * _LABEL_HEIGHT
        body.append("; --- sheet directives, as NOTE text: annotation, not circuit objects ---")
        for name, text in result.directives:
            for line in [f"{name}:"] + text.splitlines():
                if not line.strip():
                    continue
                body.append(
                    f"schCreateNoteLabel(cv list({_fmt(left)} {_fmt(cursor)}) "
                    f'"{_s(line.rstrip())}" "lowerLeft" "R0" "stick" {_LABEL_HEIGHT:g})'
                )
                cursor -= step

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
        f"; params: {result.param_summary()}\n"
        f'; load in CIW:  load("<this file>")\n'
    )
    inner = "\n  ".join(body)
    result.il = f"{header}\n{_HELPERS}\nlet((cv)\n  {inner}\n)\n"
    return result
