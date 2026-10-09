"""Minimal xschem ``.sym`` parser — just the pin geometry and the ``K{}`` template.

A schematic that wires by net-name needs each symbol's *pin coordinates* (to drop a net-label on
every pin) and its *attribute defaults* (``model``/``w``/``l``/``ng``/``m``/``value``…). Both live in
the ``.sym`` file:

* pins are ``B <layer> x1 y1 x2 y2 {name=<PIN> dir=...}`` records — single line each; the pin's
  connection point is the **box centre** ``((x1+x2)/2, (y1+y2)/2)``;
* the ``K { ... }`` block carries ``type=``, ``format=`` and a multi-line ``template="..."`` of
  ``key=value`` defaults.

We deliberately ignore every other record (``L/P/A/T/N/C/V/S/E/G``): they are draw-only and irrelevant
to placement + wiring. The parser is a small, dependency-free port of the format the UI's TS parser reads.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ["SymPin", "Symbol", "SymLibrary", "default_search_paths", "VENDORED_PDK"]

# `B <layer> x1 y1 x2 y2 {attrs}` — a pin box. Coordinates may be float; attrs are single-line.
_B_RECORD = re.compile(
    r"^B\s+\S+\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+\{(.*)\}\s*$"
)
_ATTR = re.compile(r"(\w+)\s*=\s*(\"(?:\\.|[^\"\\])*\"|\S+)")
# `template="..."` inside the K block — value may span lines and contain escaped quotes.
_TEMPLATE = re.compile(r'template\s*=\s*"((?:\\.|[^"\\])*)"', re.DOTALL)
_KTYPE = re.compile(r"\btype\s*=\s*(\S+)")
# `format="..."` inside the K block — the line that decides what an instance actually NETLISTS.
_FORMAT = re.compile(r'format\s*=\s*"((?:\\.|[^"\\])*)"', re.DOTALL)


@dataclass(frozen=True)
class SymPin:
    """A symbol pin: its declared ``name`` and its symbol-local connection point ``(x, y)``."""

    name: str
    x: float
    y: float
    dir: str = "inout"


@dataclass(frozen=True)
class Symbol:
    """A parsed symbol: its ``symref``, the ``K{}`` ``type``, its pins, and its template defaults."""

    ref: str
    type: str | None
    pins: tuple[SymPin, ...]
    template: dict[str, str] = field(default_factory=dict)
    #: The symbol's ``format`` line verbatim. An attribute on an instance is only netlisted if
    #: this line names it, so "the emitter wrote it onto the instance" and "the netlist carries
    #: it" are different claims — xschem's generic MOS netlists ``w``, ``l``, ``m`` and whatever
    #: sits in ``@extra``, and nothing else. Reading the line is what lets the emitter tell.
    fmt: str = ""
    #: Symbol-local ``(x0, y0, x1, y1)`` over every drawn line, box, polygon and arc (text
    #: excluded), or ``None`` for a symbol that draws none. The wiring layer uses it as the body
    #: of a block symbol: a pin's position says nothing about how far a body reaches on a side
    #: that has no pins, and a wire drawn across a body reads as a connection to it.
    bbox: tuple[float, float, float, float] | None = None

    def netlists(self, key: str) -> bool:
        """True when this symbol's ``format`` line substitutes ``@<key>``."""
        return bool(re.search(rf"@{re.escape(key)}\b", self.fmt))

    def pin(self, name: str) -> SymPin | None:
        """The pin named ``name`` (case-insensitive), or ``None``."""
        lname = name.lower()
        return next((p for p in self.pins if p.name.lower() == lname), None)


def _unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        token = token[1:-1]
    return token.replace('\\"', '"').replace("\\\\", "\\")


def _extract_k_block(text: str) -> str | None:
    """Return the inner text of the symbol's global-attribute block (brace-matched, quote-aware).

    xschem writes it as ``K { ... }`` and still reads the older ``G { ... }`` spelling — and honours
    either for ``type=`` / ``format=`` / ``template=``. The block-symbol generator in this package
    writes ``G {}`` (the round-trip through xschem proves it descends), so a reader that looked only
    for ``K`` returned ``type=None`` / ``fmt=""`` for every generated symbol while xschem netlisted
    it correctly. ``K`` wins when a file carries both."""
    m = re.search(r"\bK\s*\{", text) or re.search(r"\bG\s*\{", text)
    if m is None:
        return None
    i = m.end()  # just past the opening brace
    depth, in_q, esc, buf = 1, False, False, []
    while i < len(text):
        c = text[i]
        if esc:
            buf.append(c)
            esc = False
        elif c == "\\":
            buf.append(c)
            esc = True
        elif c == '"':
            in_q = not in_q
            buf.append(c)
        elif not in_q and c == "{":
            depth += 1
            buf.append(c)
        elif not in_q and c == "}":
            depth -= 1
            if depth == 0:
                return "".join(buf)
            buf.append(c)
        else:
            buf.append(c)
        i += 1
    return "".join(buf)  # unterminated — return what we have


#: One ``key=value`` pair of a ``template`` string. The value is a quoted run (``"…"`` / ``'…'``), a
#: braced run (``{…}``) or a bare token, so a value containing spaces survives intact.
_TEMPLATE_PAIR = re.compile(
    r"""([A-Za-z_][\w.]*)\s*=\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\{[^}]*\}|\S*)"""
)


def _parse_template(k_block: str) -> dict[str, str]:
    """The symbol's ``template`` string as a dict of defaults.

    xschem writes a template BOTH ways, and both are legal:

    * one pair per LINE — the IHP symbols, ``devices/res.sym``;
    * several pairs on ONE line, space separated — xschem's own generic devices, e.g.
      ``template="name=V1 value=3 savecurrent=false"`` (``vsource``, ``isource``, ``nmos4``,
      ``pmos4``).

    Splitting on newlines alone read the single-line form as one giant ``name`` key, so every other
    key was invisible: those symbols appeared to declare no ``savecurrent``, no ``model``, no
    ``spiceprefix``. The visible symptom was a source that re-netlisted as
    ``VBNC vbnc 0 0.894false`` — xschem evaluating its ``tcleval()`` ternary against a key the
    instance never carried, because the emitter could not know the key existed.
    """
    m = _TEMPLATE.search(k_block)
    if m is None:
        return {}
    out: dict[str, str] = {}
    for key, val in _TEMPLATE_PAIR.findall(m.group(1)):
        # Key case is PRESERVED: xschem resolves a `format` line's `@Nx` against the template key
        # spelled exactly that way, so lowercasing it meant the HBTs' `Nx` never matched and every
        # instance silently netlisted the template default (`Nx=1`) however the netlist sized it.
        # Every ROLE key (name/model/spiceprefix/body/value/w/l/m/b/ng), which the emitter looks up
        # by lowercase literal, is already lowercase in every vendored and IHP symbol; only HBT
        # parameters (`Nx`, `El`) carry case. `mapping`'s table guard fails loudly if that changes.
        out[key.strip()] = _unquote(val.strip())
    return out


def _graphic_points(line: str) -> list[tuple[float, float]]:
    """The corner points of one ``L``/``B``/``P``/``A`` record (an arc as its enclosing square)."""
    tok = line.split()
    try:
        if tok[0] in ("L", "B"):
            x1, y1, x2, y2 = (float(v) for v in tok[2:6])
            return [(x1, y1), (x2, y2)]
        if tok[0] == "P":
            n = int(tok[2])
            vals = [float(v) for v in tok[3 : 3 + 2 * n]]
            return list(zip(vals[0::2], vals[1::2]))
        cx, cy, r = (float(v) for v in tok[2:5])  # "A": centre and radius
        return [(cx - r, cy - r), (cx + r, cy + r)]
    except (IndexError, ValueError):
        return []  # a malformed record draws nothing we can measure


def parse_symbol(text: str, ref: str = "") -> Symbol:
    """Parse ``.sym`` text into a :class:`Symbol` (pins + the ``K{}``/``G{}`` type, format and template)."""
    pins: list[SymPin] = []
    drawn: list[tuple[float, float]] = []
    for line in text.splitlines():
        if line[:2] in ("L ", "B ", "P ", "A "):
            drawn.extend(_graphic_points(line))
        m = _B_RECORD.match(line.strip())
        if m is None:
            continue
        x1, y1, x2, y2 = (float(m.group(i)) for i in range(1, 5))
        attrs = {k: _unquote(v) for k, v in _ATTR.findall(m.group(5))}
        pins.append(
            SymPin(
                name=attrs.get("name", ""),
                x=(x1 + x2) / 2.0,
                y=(y1 + y2) / 2.0,
                dir=attrs.get("dir", "inout"),
            )
        )
    k_block = _extract_k_block(text) or ""
    type_m = _KTYPE.search(k_block)
    fmt_m = _FORMAT.search(k_block)
    return Symbol(
        ref=ref,
        type=type_m.group(1) if type_m else None,
        pins=tuple(pins),
        template=_parse_template(k_block),
        fmt=_unquote(fmt_m.group(1)) if fmt_m else "",
        bbox=(
            (
                min(x for x, _ in drawn),
                min(y for _, y in drawn),
                max(x for x, _ in drawn),
                max(y for _, y in drawn),
            )
            if drawn
            else None
        ),
    )


#: The one open PDK whose xschem symbols this repo vendors.
VENDORED_PDK = "ihp-sg13g2"


def default_search_paths(pdk: str | None = None) -> list[Path]:
    """Ordered dirs against which a ``symref`` resolves.

    Prefers the container layout when running inside the EDA image (``XSCHEM_LIBRARY_PATH`` /
    ``PDK_ROOT`` set), and falls back to the host-vendored ``docker/`` copies. A ``symref`` like
    ``sg13g2_pr/sg13_lv_nmos.sym`` resolves under the PDK xschem dir; ``devices/res.sym`` under the
    generic library dir.

    ``pdk`` scopes the PDK half. The only vendored kit is the open ``ihp-sg13g2``, and its symbol
    directory used to be appended WHATEVER PDK was asked for — so a commercial-kit design drawing
    on the generic lane got an open-PDK symbol library on its search path and in its generated
    ``xschemrc``, which trips such a design's own denylist (issue #159). Naming a different PDK now
    leaves it out; ``None`` keeps every root, which is what a caller with no PDK opinion wants.
    """
    roots: list[Path] = []
    want = (pdk or "").strip().lower()
    # Container: XSCHEM_LIBRARY_PATH is "/opt/xschem_library:/opt/xschem_library/devices"; the first
    # entry contains devices/. PDK_ROOT/<PDK>/libs.tech/xschem contains sg13g2_pr/.
    for entry in os.environ.get("XSCHEM_LIBRARY_PATH", "").split(os.pathsep):
        if entry:
            roots.append(Path(entry))
    pdk_root, env_pdk = os.environ.get("PDK_ROOT"), os.environ.get("PDK", VENDORED_PDK)
    if pdk_root and (not want or want == env_pdk.strip().lower()):
        roots.append(Path(pdk_root) / env_pdk / "libs.tech" / "xschem")
    # Host: the vendored docker/ copies under the platform repo root.
    try:
        from spicexplorer_core import project_root

        base = project_root()
        if not want or want == VENDORED_PDK:
            roots.append(base / "docker" / "pdk" / VENDORED_PDK / "libs.tech" / "xschem")
        roots.append(base / "docker" / "xschem_library")  # the generic devices/, every PDK needs it
    except Exception:  # pragma: no cover - project_root marker absent
        logger.debug("project_root() unavailable; vendored symbol dirs not added", exc_info=True)
    # De-dupe, keep order.
    seen: set[Path] = set()
    return [r for r in roots if not (r in seen or seen.add(r))]


class SymLibrary:
    """Resolve + parse ``.sym`` files from an ordered list of search-path roots (cached)."""

    def __init__(self, search_paths: list[Path] | None = None) -> None:
        self.search_paths: list[Path] = (
            list(search_paths) if search_paths else default_search_paths()
        )
        self._cache: dict[str, Symbol | None] = {}

    @classmethod
    @lru_cache(maxsize=1)
    def default(cls) -> SymLibrary:
        """A library over the vendored IHP + generic symbol dirs (container or host layout)."""
        return cls()

    def resolve(self, symref: str) -> Path | None:
        """The first existing file for ``symref`` across the search paths, else ``None``."""
        for root in self.search_paths:
            candidate = root / symref
            if candidate.is_file():
                return candidate
        return None

    def register(self, symref: str, text: str) -> None:
        """Make ``symref`` load as the symbol ``text``, which is not written to a file yet.

        A generated symbol is placed and wired before its file exists;
        :func:`~.collapse.build_collapsed_sch` registers each group cell's ``blocks/<name>.sym``.
        """
        self._cache[symref] = parse_symbol(text, ref=symref)

    def load(self, symref: str) -> Symbol | None:
        """Parse the symbol for ``symref`` (cached). Returns ``None`` if it can't be resolved."""
        if symref not in self._cache:
            path = self.resolve(symref)
            self._cache[symref] = (
                parse_symbol(path.read_text(encoding="utf-8", errors="replace"), ref=symref)
                if path is not None
                else None
            )
        return self._cache[symref]
