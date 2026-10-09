"""The bidirectional device table: xschem symref ⇄ Virtuoso master.

One YAML file drives both directions. Each rule matches an xschem symbol reference (exact
path or ``fnmatch`` glob) — optionally narrowed by the instance's own attributes — and names
the Cadence master, the xschem-pin → Cadence-terminal alias table, and the xschem-attribute →
CDF-parameter map. ``kit_libs`` is the reverse direction's NDA denylist: instances of masters
in these libraries map back to xschem symrefs by this table only — their symbol *geometry* is
never dumped out of Cadence.

**The symref is not always the discriminator.** A sheet drawn on the GENERIC lane — the only
lane available to a commercial kit, whose symbol library cannot live in a repo — draws every
MOSFET with xschem's ``devices/nmos4.sym`` / ``devices/pmos4.sym`` and carries the kit device
on the INSTANCE (``{name=M1 model=nmos_lvt w=2u l=0.2u}``). Two threshold flavours of the same
polarity are then one symref and must not become one master: a rule may add
``attrs: {model: nmos_lvt}`` (fnmatch, case-insensitive, as SPICE resolves model cards) and it
matches only instances that satisfy every constraint. Order matters as always — first matching
rule wins, so the narrow rules precede the catch-all, and a rule with ``attrs`` never matches a
caller that supplies no attributes.

The built-in default map ports the corpus onto a closed kit's MOS masters (a topology
port — sizing semantics are NOT translated between kits) plus the generic analogLib
passives/sources. Some kits use per-finger widths and callback-derived CDF parameters:
a derived parameter must never be written directly (the callbacks own it), the simulated
multiplier may live under a different CDF name than the display one, and a TOTAL-width
source attribute must be divided by the finger count before it reaches a per-finger CDF
width. A rule's optional ``per_finger: {total: <attr>, fingers: <attr>}`` declares that
division; the IHP sg13g2 xschem ``w`` IS total width (the open wrapper
model passes ``nf=ng`` and computes diffusion areas from ``w/ng``).
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

import yaml

__all__ = [
    "DeviceRule",
    "DeviceMap",
    "StimulusRule",
    "StimulusType",
    "load_device_map",
    "DEFAULT_MAP_YAML",
    "DEFAULT_GLOBALS",
]

#: Nets a Cadence schematic reaches by GLOBAL name rather than by wire. Only SPICE `0` is
#: structurally a reference — a deck's ground is `0` and Virtuoso's is `gnd!`, and without
#: the mapping a ported bench has no ground reference at all (issue #182): every ground
#: terminal lands on an ordinary net called `net0` and spectre refuses the cellview. Supply
#: rails are NOT defaulted: whether `vdd` is global or a drawn port is a design choice, so a
#: map that wants `vdd!` says so.
DEFAULT_GLOBALS = {"0": "gnd!"}


@dataclass(frozen=True)
class StimulusType:
    """Where ONE parsed stimulus kind's canonical fields land in a CDF.

    ``cell`` lets a kind carry its own master — analogLib spreads sources over several cells
    (``vdc`` holds dc/acm/acp, a pulse belongs on ``vpulse``), so the kind chosen by the
    sheet's own value string decides the master. Empty = the rule's own ``cell``.
    """

    cell: str = ""
    params: dict[str, str] = field(default_factory=dict)  # canonical field -> CDF param


@dataclass(frozen=True)
class StimulusRule:
    """The attribute that holds a whole stimulus, and the per-kind CDF field maps.

    The grammar is in `stimulus.py` and produces canonical names only; every CDF spelling
    stays here in the map, so a wrong one is a YAML fix rather than a code change.
    """

    attr: str = "value"
    types: dict[str, StimulusType] = field(default_factory=dict)

    def for_kind(self, kind: str) -> StimulusType | None:
        return self.types.get(kind)

    def cell_kind(self, cell: str) -> str:
        """The stimulus kind whose master is ``cell`` ("" if none declares it)."""
        return next((k for k, t in sorted(self.types.items()) if t.cell == cell), "")


@dataclass(frozen=True)
class DeviceRule:
    """One xschem-symref ⇄ Cadence-master mapping rule."""

    match: str
    lib: str
    cell: str
    view: str = "symbol"
    terms: dict[str, str] = field(default_factory=dict)  # xschem pin -> Cadence term
    params: dict[str, str] = field(default_factory=dict)  # xschem attr -> CDF param
    # {"total": <xschem attr>, "fingers": <xschem attr>} — the named attribute carries the
    # device's TOTAL width while the mapped CDF parameter is per-finger; the emitter divides.
    per_finger: dict[str, str] = field(default_factory=dict)
    # concrete xschem symref emitted by the REVERSE direction (cv2sch) for instances of
    # this master — the match glob is not invertible.
    symref: str = ""
    # The attribute holding a whole stimulus (`value="dc 0.2 ac 0"`), split across the CDF
    # fields that actually hold it. None = this device has no stimulus.
    stimulus: StimulusRule | None = None
    # xschem INSTANCE attribute -> required value (fnmatch glob, case-insensitive). A rule
    # carrying these matches only an instance that satisfies every one of them — the generic
    # lane's discriminator, where one symref carries many kit devices via ``model=``.
    attrs: dict[str, str] = field(default_factory=dict)
    # KIT-INDEPENDENT: this rule names a master that exists in every installation (analogLib
    # primitives and sources), so it is safe to append behind a caller's own rules when a
    # ``--map`` extends the built-ins rather than replacing them. The built-in MOS rules are
    # deliberately NOT generic: they port IHP-drawn MOS onto `FOUNDRY_KIT`, so appending them
    # behind an arbitrary kit's map would silently resolve an uncovered MOSFET to a FOUNDRY_KIT
    # master instead of failing — trading the reported error for a wrong-master port, which
    # is the worse of the two.
    generic: bool = False

    def matches(self, symref: str, attrs: dict[str, str] | None = None) -> bool:
        """Match the full symref or its basename — corpus files reference generic symbols
        both ways (``devices/capa.sym`` and bare ``capa.sym``) — and, for a rule that
        declares ``attrs``, the instance's attributes as well.

        A rule with ``attrs`` never matches when the caller supplies none: the rule asked a
        question about the instance, and an unanswered question is not a yes.
        """
        if not self._symref_matches(symref):
            return False
        if not self.attrs:
            return True
        if attrs is None:
            return False
        for key, pattern in self.attrs.items():
            value = attrs.get(key)
            if value is None or not fnmatch.fnmatch(value.lower(), pattern.lower()):
                return False
        return True

    def _symref_matches(self, symref: str) -> bool:
        if symref == self.match or fnmatch.fnmatch(symref, self.match):
            return True
        base = symref.rsplit("/", 1)[-1]
        pat_base = self.match.rsplit("/", 1)[-1]
        return fnmatch.fnmatch(base, pat_base)

    def literal_attrs(self) -> dict[str, str]:
        """The ``attrs`` constraints that are exact values, for the REVERSE direction to
        stamp back onto the instance. A glob says which instances the rule accepts, not
        which one to write, so a pattern is skipped rather than guessed at."""
        return {k: v for k, v in self.attrs.items() if not any(c in v for c in "*?[")}

    def term_for(self, xschem_pin: str) -> str:
        """The Cadence terminal for an xschem pin name (identity when unmapped)."""
        return self.terms.get(xschem_pin, xschem_pin)


@dataclass(frozen=True)
class DeviceMap:
    """An ordered rule list plus the kit-library denylist (first matching rule wins)."""

    rules: tuple[DeviceRule, ...] = ()
    kit_libs: tuple[str, ...] = ()
    # xschem net name (lower-case) -> Cadence global name. See DEFAULT_GLOBALS.
    globals: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_GLOBALS))

    def lookup(self, symref: str, attrs: dict[str, str] | None = None) -> DeviceRule | None:
        return next((r for r in self.rules if r.matches(symref, attrs)), None)

    def lookup_reverse(self, lib: str, cell: str) -> DeviceRule | None:
        """The rule whose Cadence master is ``lib/cell`` (first wins) — the cv2sch map.

        A rule may reach SEVERAL masters: a stimulus kind carries its own cell (a pulse is an
        ``vpulse``, not a ``vdc``), so the reverse direction also accepts a rule that declares
        this cell under ``stimulus.types`` — otherwise a bench ported out of Cadence would
        come back with its sources unmapped.
        """
        direct = next((r for r in self.rules if r.lib == lib and r.cell == cell), None)
        if direct is not None:
            return direct
        return next(
            (
                r
                for r in self.rules
                if r.lib == lib and r.stimulus is not None and r.stimulus.cell_kind(cell)
            ),
            None,
        )

    def xschem_net(self, cadence_net: str) -> str | None:
        """The xschem net name behind a Cadence global (``gnd!`` -> ``0``), or None.

        The inverse of `global_for`, for the reverse port: a sheet that came back labelled
        ``gnd!`` would no longer netlist to a deck whose ground is ``0``.
        """
        want = cadence_net.strip().lower()
        return next((k for k, v in sorted(self.globals.items()) if v.lower() == want), None)

    def global_for(self, net: str) -> str | None:
        """The Cadence global name for an xschem net, or None if it is an ordinary net.

        Matched case-insensitively: net names are case-insensitive in SPICE, so a sheet
        drawn with `GND` and a map written with `gnd` mean the same net.
        """
        return self.globals.get(net.strip().lower())

    def is_kit_lib(self, lib: str) -> bool:
        return lib in self.kit_libs


# The built-in default. Kept as YAML text so `xvport --dump-map` hands users a working
# starting point for their own kit files.
DEFAULT_MAP_YAML = """\
# xvport device map: xschem symref <-> Cadence master (first matching rule wins).
# `terms`: xschem pin name -> Cadence terminal.  `params`: xschem attr -> CDF param.
#
# YOUR OWN --map EXTENDS THIS FILE'S `generic: true` RULES (the analogLib primitives and
# sources) rather than replacing them: your rules are tried first, these after. So a kit map
# only has to name the devices the kit actually has — it does not have to restate analogLib.
# `--map-replace` turns extension off and starts from nothing.
# The MOS rules below are NOT generic: they port IHP-drawn MOS onto FOUNDRY_KIT, so they are never
# appended behind someone else\'s map (that would resolve an uncovered MOSFET to a FOUNDRY_KIT
# master instead of failing).
devices:
  # IHP sg13g2 MOS drawings -> a licensed kit's core MOS (topology port; sizing is NOT
  # kit-translated). `FOUNDRY_KIT` is a PLACEHOLDER: replace it (and the cell names) with
  # your own kit's library in your map file — `xvport --dump-map` hands you this as a
  # starting point. The CDF shape encoded here is the common one: parameter
  # names are w/l/fingers; wf derives as w*fingers
  # (CDF w is PER-FINGER). The spectre netlister's propMapping is m<-simM, nf<-fingers,
  # w<-wf: the xschem multiplier must land on simM (CDF m is callback-derived — setting it
  # is a silent no-op), and IHP xschem w is TOTAL width (the sg13g2 wrapper passes nf=ng
  # and computes areas from w/ng), so per_finger divides it for the per-finger CDF w.
  - match: "*sg13_lv_nmos*.sym"
    lib: FOUNDRY_KIT
    cell: nmos_lvt
    symref: sg13g2_pr/sg13_lv_nmos.sym
    terms: {D: D, G: G, S: S, B: B}
    params: {w: w, l: l, m: simM, ng: fingers}
    per_finger: {total: w, fingers: ng}
  - match: "*sg13_lv_pmos*.sym"
    lib: FOUNDRY_KIT
    cell: pmos_lvt
    symref: sg13g2_pr/sg13_lv_pmos.sym
    terms: {D: D, G: G, S: S, B: B}
    params: {w: w, l: l, m: simM, ng: fingers}
    per_finger: {total: w, fingers: ng}
  # --- The GENERIC lane (a commercial kit's only lane): one symref, many kit devices. ----
  # Not enabled by default — the generic symbols say nothing about WHICH kit is targeted, so
  # a design on the generic lane passes its own `--map` and the rules below are the shape to
  # copy. Each flavour is its own rule, discriminated by the instance's `model` attribute;
  # `per_finger` is what stops a TOTAL-width source attribute reaching a per-finger CDF `w`.
  #
  # - match: "*/nmos4.sym"
  #   attrs: {model: nmos_lvt}          # narrow rules FIRST — first match wins
  #   lib: <KIT_LIB>
  #   cell: nmos_lvt
  #   symref: devices/nmos4.sym
  #   terms: {d: D, g: G, s: S, b: B}
  #   params: {w: w, l: l, m: simM, nf: fingers}
  #   per_finger: {total: w, fingers: nf}
  # - match: "*/nmos4.sym"
  #   attrs: {model: nch}
  #   lib: <KIT_LIB>
  #   cell: nch
  #   ... (and the pmos4 pair likewise)
  #
  # Generic xschem devices -> analogLib.
  - match: "*/res.sym"
    lib: analogLib
    cell: res
    generic: true
    symref: devices/res.sym
    terms: {P: PLUS, M: MINUS}
    params: {value: r}
  - match: "*/capa*.sym"
    lib: analogLib
    cell: cap
    generic: true
    symref: devices/capa.sym
    terms: {p: PLUS, m: MINUS}
    params: {value: c}
  - match: "*/ind*.sym"
    lib: analogLib
    cell: ind
    generic: true
    symref: devices/ind.sym
    terms: {p: PLUS, m: MINUS}
    params: {value: l}
  # A source's `value` is a whole STIMULUS, not one number: `dc 0.2 ac 0` spreads over
  # vdc/acm/acp, and a pulse or a sine belongs on a different analogLib cell entirely. The
  # grammar lives in stimulus.py; the CDF spellings live here. `params:` is gone from these
  # two rules on purpose — writing the string into `vdc` is what made Cadence invent a design
  # variable named `dc` and left every ported bench at an unknown operating point (#182).
  # Every row below is LIVE-PROBED, not documented: the `dc` row's vdc/acm/acp on 2026-07-16,
  # the transient rows with `cdfGetBaseCellCDF(ddGetObj "analogLib" "<cell>")` on IC23.1,
  # live-probed 2026-09-13 — vpulse is v1/v2/per/td/tr/tf/pw (ipulse i1/i2), vsin is
  # vo/va/freq/td/theta (isin io/ia). The names this file carried until then (`val0`/`val1`,
  # `sinedc`/`ampl`/`damp`) exist on NO analogLib source, so every pulse and sine ported at
  # zero amplitude while the port reported success (#214). If a pulse or sine still comes back
  # wrong on another kit, re-probe its CDF — the fix is a YAML edit, not a code change, and
  # xvSetParams now refuses to load a name the CDF does not have rather than warning to the CIW.
  - match: "*/vsource.sym"
    lib: analogLib
    cell: vdc
    generic: true
    symref: devices/vsource.sym
    terms: {p: PLUS, m: MINUS}
    stimulus:
      attr: value
      types:
        dc:    {cell: vdc,    params: {dc: vdc, ac_mag: acm, ac_phase: acp}}
        pulse: {cell: vpulse, params: {val0: v1, val1: v2, delay: td, rise: tr,
                                       fall: tf, width: pw, period: per, ac_mag: acm}}
        sin:   {cell: vsin,   params: {offset: vo, ampl: va, freq: freq, delay: td,
                                       damp: theta, ac_mag: acm}}
        pwl:   {cell: vpwl,   params: {wave: wave, ac_mag: acm}}
  - match: "*/isource.sym"
    lib: analogLib
    cell: idc
    generic: true
    symref: devices/isource.sym
    terms: {p: PLUS, m: MINUS}
    stimulus:
      attr: value
      types:
        dc:    {cell: idc,    params: {dc: idc, ac_mag: acm, ac_phase: acp}}
        pulse: {cell: ipulse, params: {val0: i1, val1: i2, delay: td, rise: tr,
                                       fall: tf, width: pw, period: per, ac_mag: acm}}
        sin:   {cell: isin,   params: {offset: io, ampl: ia, freq: freq, delay: td,
                                       damp: theta, ac_mag: acm}}
        pwl:   {cell: ipwl,   params: {wave: wave, ac_mag: acm}}
  # behavioral controlled source (live-probed 2026-07-16: analogLib vccs terminals are
  # PLUS/MINUS/NC+/NC-; the transconductance CDF parameter is ggain)
  - match: "*/vccs.sym"
    lib: analogLib
    cell: vccs
    generic: true
    symref: devices/vccs.sym
    terms: {p: PLUS, m: MINUS, cp: "NC+", cm: "NC-"}
    params: {value: ggain}
  # (live-probed 2026-07-27: analogLib vcvs terminals are the same PLUS/MINUS/NC+/NC-;
  # the voltage-gain CDF parameter is egain)
  - match: "*/vcvs.sym"
    lib: analogLib
    cell: vcvs
    generic: true
    symref: devices/vcvs.sym
    terms: {p: PLUS, m: MINUS, cp: "NC+", cm: "NC-"}
    params: {value: egain}

# Nets reached by Cadence GLOBAL name instead of by wire. A deck's ground is SPICE `0`,
# Virtuoso's is `gnd!`; without this the ported bench has no ground reference and spectre
# refuses the cellview. Writing this section REPLACES the default (`globals: {}` = none).
# Supply rails are a design choice, not a structural fact — add `vdd: vdd!` if the sheet's
# rails are meant to be global rather than drawn ports.
globals:
  "0": "gnd!"

# Reverse-direction NDA denylist: masters in these libs map back by table only —
# never dump their symbol geometry out of Cadence.
kit_libs: [FOUNDRY_KIT, analogLib, basic]
"""


def _parse_stimulus_rule(entry: dict | None) -> StimulusRule | None:
    """Read one rule's `stimulus:` section; a malformed one raises rather than degrading."""
    if not entry:
        return None
    if not isinstance(entry, dict):
        raise ValueError(f"stimulus: must be a mapping with `attr` and `types` (got {entry!r})")
    types = entry.get("types") or {}
    if not isinstance(types, dict) or not types:
        raise ValueError(
            "stimulus.types: at least one kind must be declared, e.g. "
            "types: {dc: {params: {dc: vdc, ac_mag: acm}}}"
        )
    parsed: dict[str, StimulusType] = {}
    for kind, spec in types.items():
        spec = spec or {}
        parsed[str(kind).strip().lower()] = StimulusType(
            cell=str(spec.get("cell") or ""),
            params={str(k): str(v) for k, v in (spec.get("params") or {}).items()},
        )
    return StimulusRule(attr=str(entry.get("attr") or "value"), types=parsed)


def _parse_map(data: dict) -> DeviceMap:
    rules = tuple(
        DeviceRule(
            match=entry["match"],
            lib=entry["lib"],
            cell=entry["cell"],
            view=entry.get("view", "symbol"),
            terms={str(k): str(v) for k, v in (entry.get("terms") or {}).items()},
            params={str(k): str(v) for k, v in (entry.get("params") or {}).items()},
            per_finger={str(k): str(v) for k, v in (entry.get("per_finger") or {}).items()},
            symref=str(entry.get("symref") or ""),
            stimulus=_parse_stimulus_rule(entry.get("stimulus")),
            attrs={str(k): str(v) for k, v in (entry.get("attrs") or {}).items()},
            generic=bool(entry.get("generic", False)),
        )
        for entry in data.get("devices") or []
    )
    globals_ = data.get("globals")
    return DeviceMap(
        rules=rules,
        kit_libs=tuple(data.get("kit_libs") or ()),
        # a map that writes `globals:` REPLACES the default (an explicit `globals: {}` is how
        # a caller says "this sheet has no globals"); an absent key keeps `0 -> gnd!`
        globals={str(k).strip().lower(): str(v) for k, v in (globals_ or {}).items()}
        if globals_ is not None
        else dict(DEFAULT_GLOBALS),
    )


def load_device_map(path: str | Path | None = None, *, extend: bool = True) -> DeviceMap:
    """Load a device map from YAML; ``None`` returns the built-in default map.

    ``extend`` (the default) appends the built-in KIT-INDEPENDENT rules — the analogLib
    passives and sources — behind the caller's own. First-match-wins already gives the
    caller's rules priority, so extending never overrides a supplied rule; it only supplies
    the primitives a kit map has no reason to restate.

    **A supplied map used to REPLACE the built-ins outright**, which silently dropped every
    analogLib rule: a CDAC slice's capacitors then resolved to ``<target-lib>/capa_np``,
    a master that does not exist, and the port died inside Virtuoso at the closing paren of
    the generated SKILL naming nothing (issue #205). ``--map`` is not optional on a commercial
    kit, so every such port hit it.

    ``extend=False`` (``--map-replace``) is the old behaviour, for a caller that genuinely
    wants to start from nothing.

    Note what is NOT appended: the built-in IHP→``FOUNDRY_KIT`` MOS rules (see ``DeviceRule.generic``).
    """
    if path is None:
        return _parse_map(yaml.safe_load(DEFAULT_MAP_YAML) or {})
    user = _parse_map(yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {})
    if not extend:
        return user
    builtin = _parse_map(yaml.safe_load(DEFAULT_MAP_YAML) or {})
    return DeviceMap(
        rules=user.rules + tuple(r for r in builtin.rules if r.generic),
        # the NDA denylist is a union: a caller naming its own kit libs must not lose the
        # built-in ones, which is what keeps a reverse port from dumping their geometry.
        kit_libs=tuple(dict.fromkeys(user.kit_libs + builtin.kit_libs)),
        globals=user.globals,
    )
