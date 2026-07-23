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

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

__all__ = ["SymPin", "Symbol", "SymLibrary", "default_search_paths"]

# `B <layer> x1 y1 x2 y2 {attrs}` — a pin box. Coordinates may be float; attrs are single-line.
_B_RECORD = re.compile(
    r"^B\s+\S+\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+\{(.*)\}\s*$"
)
_ATTR = re.compile(r"(\w+)\s*=\s*(\"(?:\\.|[^\"\\])*\"|\S+)")
# `template="..."` inside the K block — value may span lines and contain escaped quotes.
_TEMPLATE = re.compile(r'template\s*=\s*"((?:\\.|[^"\\])*)"', re.DOTALL)
_KTYPE = re.compile(r"\btype\s*=\s*(\S+)")


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

    def pin(self, name: str) -> SymPin | None:
        """The pin named ``name`` (case-insensitive), or ``None``."""
        lname = name.lower()
        return next((p for p in self.pins if p.name.lower() == lname), None)


def _unquote(token: str) -> str:
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        token = token[1:-1]
    return token.replace('\\"', '"').replace("\\\\", "\\")


def _extract_k_block(text: str) -> str | None:
    """Return the inner text of the first ``K { ... }`` block (brace-matched, quote-aware)."""
    m = re.search(r"\bK\s*\{", text)
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


def _parse_template(k_block: str) -> dict[str, str]:
    m = _TEMPLATE.search(k_block)
    if m is None:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip().lower()] = _unquote(val.strip())
    return out


def parse_symbol(text: str, ref: str = "") -> Symbol:
    """Parse ``.sym`` text into a :class:`Symbol` (pins + ``K{}`` type/template)."""
    pins: list[SymPin] = []
    for line in text.splitlines():
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
    return Symbol(
        ref=ref,
        type=type_m.group(1) if type_m else None,
        pins=tuple(pins),
        template=_parse_template(k_block),
    )


def default_search_paths() -> list[Path]:
    """Ordered dirs against which a ``symref`` resolves, for the IHP-vendored layout.

    Prefers the container layout when running inside the EDA image (``XSCHEM_LIBRARY_PATH`` /
    ``PDK_ROOT`` set), and falls back to the host-vendored ``docker/`` copies. A ``symref`` like
    ``sg13g2_pr/sg13_lv_nmos.sym`` resolves under the PDK xschem dir; ``devices/res.sym`` under the
    generic library dir.
    """
    roots: list[Path] = []
    # Container: XSCHEM_LIBRARY_PATH is "/opt/xschem_library:/opt/xschem_library/devices"; the first
    # entry contains devices/. PDK_ROOT/<PDK>/libs.tech/xschem contains sg13g2_pr/.
    for entry in os.environ.get("XSCHEM_LIBRARY_PATH", "").split(os.pathsep):
        if entry:
            roots.append(Path(entry))
    pdk_root, pdk = os.environ.get("PDK_ROOT"), os.environ.get("PDK", "ihp-sg13g2")
    if pdk_root:
        roots.append(Path(pdk_root) / pdk / "libs.tech" / "xschem")
    # Host: the vendored docker/ copies under the platform repo root.
    try:
        from spicexplorer_core import project_root

        base = project_root()
        roots.append(base / "docker" / "pdk" / "ihp-sg13g2" / "libs.tech" / "xschem")
        roots.append(base / "docker" / "xschem_library")
    except Exception:  # pragma: no cover - project_root marker absent
        pass
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
    def default(cls) -> "SymLibrary":
        """A library over the vendored IHP + generic symbol dirs (container or host layout)."""
        return cls()

    def resolve(self, symref: str) -> Path | None:
        """The first existing file for ``symref`` across the search paths, else ``None``."""
        for root in self.search_paths:
            candidate = root / symref
            if candidate.is_file():
                return candidate
        return None

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
