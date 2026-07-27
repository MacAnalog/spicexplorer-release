"""The bidirectional device table: xschem symref ⇄ Virtuoso master.

One YAML file drives both directions. Each rule matches an xschem symbol reference (exact
path or ``fnmatch`` glob) and names the Cadence master, the xschem-pin → Cadence-terminal
alias table, and the xschem-attribute → CDF-parameter map. ``kit_libs`` is the reverse
direction's NDA denylist: instances of masters in these libraries map back to xschem symrefs
by this table only — their symbol *geometry* is never dumped out of Cadence.

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

__all__ = ["DeviceRule", "DeviceMap", "load_device_map", "DEFAULT_MAP_YAML"]


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

    def matches(self, symref: str) -> bool:
        """Match the full symref or its basename — corpus files reference generic symbols
        both ways (``devices/capa.sym`` and bare ``capa.sym``)."""
        if symref == self.match or fnmatch.fnmatch(symref, self.match):
            return True
        base = symref.rsplit("/", 1)[-1]
        pat_base = self.match.rsplit("/", 1)[-1]
        return fnmatch.fnmatch(base, pat_base)

    def term_for(self, xschem_pin: str) -> str:
        """The Cadence terminal for an xschem pin name (identity when unmapped)."""
        return self.terms.get(xschem_pin, xschem_pin)


@dataclass(frozen=True)
class DeviceMap:
    """An ordered rule list plus the kit-library denylist (first matching rule wins)."""

    rules: tuple[DeviceRule, ...] = ()
    kit_libs: tuple[str, ...] = ()

    def lookup(self, symref: str) -> DeviceRule | None:
        return next((r for r in self.rules if r.matches(symref)), None)

    def lookup_reverse(self, lib: str, cell: str) -> DeviceRule | None:
        """The rule whose Cadence master is ``lib/cell`` (first wins) — the cv2sch map."""
        return next((r for r in self.rules if r.lib == lib and r.cell == cell), None)

    def is_kit_lib(self, lib: str) -> bool:
        return lib in self.kit_libs


# The built-in default. Kept as YAML text so `xvport --dump-map` hands users a working
# starting point for their own kit files.
DEFAULT_MAP_YAML = """\
# xvport device map: xschem symref <-> Cadence master (first matching rule wins).
# `terms`: xschem pin name -> Cadence terminal.  `params`: xschem attr -> CDF param.
devices:
  # IHP sg13g2 MOS drawings -> FOUNDRYN65 (topology port; sizing is NOT kit-translated).
  # FOUNDRYN65 CDF (live-verified 2026-07-16): names are w/l/fingers; wf derives as w*fingers
  # (CDF w is PER-FINGER). The spectre netlister's propMapping is m<-simM, nf<-fingers,
  # w<-wf: the xschem multiplier must land on simM (CDF m is callback-derived — setting it
  # is a silent no-op), and IHP xschem w is TOTAL width (the sg13g2 wrapper passes nf=ng
  # and computes areas from w/ng), so per_finger divides it for the per-finger CDF w.
  - match: "*sg13_lv_nmos*.sym"
    lib: FOUNDRYN65
    cell: DEVICE
    symref: sg13g2_pr/sg13_lv_nmos.sym
    terms: {D: D, G: G, S: S, B: B}
    params: {w: w, l: l, m: simM, ng: fingers}
    per_finger: {total: w, fingers: ng}
  - match: "*sg13_lv_pmos*.sym"
    lib: FOUNDRYN65
    cell: DEVICE
    symref: sg13g2_pr/sg13_lv_pmos.sym
    terms: {D: D, G: G, S: S, B: B}
    params: {w: w, l: l, m: simM, ng: fingers}
    per_finger: {total: w, fingers: ng}
  # Generic xschem devices -> analogLib.
  - match: "*/res.sym"
    lib: analogLib
    cell: res
    symref: devices/res.sym
    terms: {P: PLUS, M: MINUS}
    params: {value: r}
  - match: "*/capa*.sym"
    lib: analogLib
    cell: cap
    symref: devices/capa.sym
    terms: {p: PLUS, m: MINUS}
    params: {value: c}
  - match: "*/ind*.sym"
    lib: analogLib
    cell: ind
    symref: devices/ind.sym
    terms: {p: PLUS, m: MINUS}
    params: {value: l}
  - match: "*/vsource.sym"
    lib: analogLib
    cell: vdc
    symref: devices/vsource.sym
    terms: {p: PLUS, m: MINUS}
    params: {value: vdc}
  - match: "*/isource.sym"
    lib: analogLib
    cell: idc
    symref: devices/isource.sym
    terms: {p: PLUS, m: MINUS}
    params: {value: idc}
  # behavioral controlled source (live-probed 2026-07-16: analogLib vccs terminals are
  # PLUS/MINUS/NC+/NC-; the transconductance CDF parameter is ggain)
  - match: "*/vccs.sym"
    lib: analogLib
    cell: vccs
    symref: devices/vccs.sym
    terms: {p: PLUS, m: MINUS, cp: "NC+", cm: "NC-"}
    params: {value: ggain}
  # (live-probed 2026-07-27: analogLib vcvs terminals are the same PLUS/MINUS/NC+/NC-;
  # the voltage-gain CDF parameter is egain)
  - match: "*/vcvs.sym"
    lib: analogLib
    cell: vcvs
    symref: devices/vcvs.sym
    terms: {p: PLUS, m: MINUS, cp: "NC+", cm: "NC-"}
    params: {value: egain}

# Reverse-direction NDA denylist: masters in these libs map back by table only —
# never dump their symbol geometry out of Cadence.
kit_libs: [FOUNDRYN65, KIT65gplus, KIT65gpgv2od3, KIT65v, analogLib, basic]
"""


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
        )
        for entry in data.get("devices") or []
    )
    return DeviceMap(rules=rules, kit_libs=tuple(data.get("kit_libs") or ()))


def load_device_map(path: str | Path | None = None) -> DeviceMap:
    """Load a device map from YAML; ``None`` returns the built-in default map."""
    text = Path(path).read_text(encoding="utf-8") if path is not None else DEFAULT_MAP_YAML
    return _parse_map(yaml.safe_load(text) or {})
