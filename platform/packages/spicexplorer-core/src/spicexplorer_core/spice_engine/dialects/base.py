"""Netlist-dialect foundation — detect a dialect and normalize it to the canonical SPICE subset.

The strategy is
**normalize-to-canonical**: a per-dialect :class:`BaseDialectReader` rewrites the *structural
subset* of a foreign netlist (subckt definitions, device instances, params, globals) into the
canonical SPICE text that spicelib already parses, and preserves every non-structural statement
(analyses, ``.measure``/measurement cards, options, model cards, includes) as a classified,
verbatim :class:`Directive`. Nothing is translated between dialects and nothing is silently
dropped: a statement is either canonicalized, kept as a directive, or raises.

Two invariants callers can rely on:

* **Foundry includes are never resolved or inlined** on the dialect path — ``include``/``.lib``
  statements become directives only (NDA posture; analog-db stubs them as ``${PDK_ROOT}``).
* The canonical text is self-contained for *topology*: it starts with a ``*`` title line and ends
  with ``.end`` (both hard spicelib requirements) and contains only structural statements.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

__all__ = [
    "NetlistDialect",
    "Directive",
    "DialectSpec",
    "ParsedDeck",
    "BaseDialectReader",
    "DialectSyntaxError",
    "detect_dialect",
]


class NetlistDialect(str, Enum):
    """The netlist dialects the platform can read (and circuitgraph can emit).

    ``SPICE`` is the canonical/ngspice-flavored dialect — the one spicelib parses natively and
    the only one with a simulation pipeline today. Values mirror the optimizer DSL's
    ``SpiceSimulatorType`` (``"ngspice"`` coerces to ``SPICE``).
    """

    SPICE = "spice"
    SPECTRE = "spectre"
    HSPICE = "hspice"

    @classmethod
    def coerce(cls, value: "NetlistDialect | str") -> "NetlistDialect":
        """Accept an enum member or a (case-insensitive) string, with ``"ngspice"`` → SPICE."""
        if isinstance(value, cls):
            return value
        text = str(value).strip().lower()
        if text == "ngspice":
            text = "spice"
        try:
            return cls(text)
        except ValueError:
            raise ValueError(
                f"unknown netlist dialect {value!r} (expected one of "
                f"{[m.value for m in cls]} or 'ngspice'/'auto')"
            ) from None


@dataclass(frozen=True)
class Directive:
    """A non-structural statement preserved verbatim (continuations already joined).

    ``kind`` is a coarse classification for callers that want to filter:
    ``include`` | ``analysis`` | ``measure`` | ``option`` | ``model`` | ``alter`` |
    ``library`` | ``unknown``.
    """

    kind: str
    text: str


@dataclass(frozen=True)
class DialectSpec:
    """Per-dialect syntax facts shared by the readers here and the circuitgraph emitters.

    One table per dialect so read and write can't drift apart.
    """

    dialect: NetlistDialect
    line_comment: tuple[str, ...]        # tokens opening a whole-line comment
    inline_comment: tuple[str, ...]      # tokens opening a trailing comment (quote-aware)
    continuation_leading: str | None     # SPICE/HSPICE: "+" at start of the next line
    continuation_trailing: str | None    # Spectre: "\" at end of the continued line
    subckt_open: str                     # "subckt" (Spectre) / ".subckt" (SPICE-family)
    subckt_close: str                    # "ends" / ".ends"
    param_aliases: dict[str, str] = field(default_factory=dict)  # canonical → dialect (e.g. m→multi)
    identifier_leading_digit_ok: bool = True  # Spectre: False (`5t_ota` must be renamed)


@dataclass(frozen=True)
class ParsedDeck:
    """A dialect reader's output: canonical SPICE text + everything needed for fidelity."""

    canonical_text: str
    dialect: NetlistDialect
    directives: tuple[Directive, ...]
    name_map: dict[str, str]      # canonical ref (UPPERCASE, as spicelib reports) → original name
    warnings: tuple[str, ...]


class DialectSyntaxError(ValueError):
    """A structural statement the reader does not understand (fail-loud, never drop devices)."""


# ----------------------------------------------------------------------
# Dialect detection
# ----------------------------------------------------------------------
_SPECTRE_LANG = re.compile(r"^\s*simulator\s+lang\s*=\s*spectre\b", re.IGNORECASE | re.MULTILINE)
_SPICE_LANG = re.compile(r"^\s*simulator\s+lang\s*=\s*spice\b", re.IGNORECASE | re.MULTILINE)
# Un-dotted structural keywords are the strongest textual Spectre markers.
_SPECTRE_SUBCKT = re.compile(r"^\s*(inline\s+)?subckt\s+\S+", re.MULTILINE)
_SPECTRE_ENDS = re.compile(r"^\s*ends\b", re.MULTILINE)
_SPECTRE_PARAMETERS = re.compile(r"^\s*parameters\s+\S+=", re.MULTILINE)
_SPECTRE_COMMENT = re.compile(r"^\s*//", re.MULTILINE)
# `<name> (` — a paren node list right after the ref token (never legal in SPICE-family decks).
_SPECTRE_PAREN_INST = re.compile(r"^\s*[A-Za-z]\w*\s+\(", re.MULTILINE)
# HSPICE-only cards that a generic-SPICE deck can't carry. Deliberately conservative: weak
# signals (`.measure`, `.temp`, quoted expressions) also exist in ngspice-adjacent decks, and a
# false HSPICE positive would change behavior for existing SPICE callers.
_HSPICE_STRONG = re.compile(
    r"^\s*\.(lstb|alter\b|check\s|malias|del\s+lib|option\s[^\n]*\bpost\b|protect\b|unprotect\b|eom\b)",
    re.IGNORECASE | re.MULTILINE,
)


def detect_dialect(text: str, filename: str | Path | None = None) -> NetlistDialect:
    """Best-effort dialect sniff: extension hint first, then content markers.

    Conservative by construction — a deck is only called SPECTRE/HSPICE on strong evidence;
    everything else stays SPICE (plain structural HSPICE parses fine on the SPICE path).
    """
    if filename is not None and Path(filename).suffix.lower() == ".scs":
        return NetlistDialect.SPECTRE
    if _SPECTRE_LANG.search(text):
        return NetlistDialect.SPECTRE
    spectre_score = sum(
        1
        for pat in (_SPECTRE_SUBCKT, _SPECTRE_ENDS, _SPECTRE_PARAMETERS, _SPECTRE_COMMENT, _SPECTRE_PAREN_INST)
        if pat.search(text)
    )
    # `subckt`+`ends` without dots, or any two independent markers, is decisive.
    if spectre_score >= 2 and not _SPICE_LANG.search(text):
        return NetlistDialect.SPECTRE
    if _HSPICE_STRONG.search(text):
        return NetlistDialect.HSPICE
    return NetlistDialect.SPICE


# ----------------------------------------------------------------------
# Shared lexing passes
# ----------------------------------------------------------------------
class BaseDialectReader:
    """Shared lexing for dialect readers: quote-aware comment stripping and continuation joins.

    Subclasses set :attr:`spec` and implement :meth:`read`. The helpers are deliberately
    line-oriented (netlists are line languages) and quote-aware — ``'...'`` and ``"..."`` spans
    are opaque, so a ``//`` or ``$`` inside a quoted expression never starts a comment.
    """

    spec: DialectSpec  # set by subclass

    # -- comments -------------------------------------------------------
    @classmethod
    def _strip_inline_comment(cls, line: str, tokens: tuple[str, ...]) -> str:
        """Cut ``line`` at the first comment token found *outside* quotes."""
        if not tokens or not line:
            return line
        quote: str | None = None
        i = 0
        while i < len(line):
            ch = line[i]
            if quote is not None:
                if ch == quote:
                    quote = None
                i += 1
                continue
            if ch in ("'", '"'):
                quote = ch
                i += 1
                continue
            for tok in tokens:
                if line.startswith(tok, i):
                    return line[:i].rstrip()
            i += 1
        return line

    # -- continuations ---------------------------------------------------
    @staticmethod
    def _join_trailing(lines: list[str], marker: str) -> list[str]:
        """Join lines ending in ``marker`` (Spectre's ``\\``) with their successors."""
        out: list[str] = []
        buf: str | None = None
        for line in lines:
            stripped = line.rstrip()
            if stripped.endswith(marker):
                part = stripped[: -len(marker)].rstrip()
                buf = part if buf is None else f"{buf} {part}"
                continue
            if buf is not None:
                out.append(f"{buf} {stripped}".strip())
                buf = None
            else:
                out.append(line)
        if buf is not None:  # dangling continuation — keep what we have
            out.append(buf)
        return out

    @staticmethod
    def _join_leading(lines: list[str], marker: str) -> list[str]:
        """Join lines *starting* with ``marker`` (SPICE/HSPICE ``+``) onto their predecessor."""
        out: list[str] = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith(marker) and out:
                out[-1] = f"{out[-1].rstrip()} {stripped[len(marker):].strip()}"
            else:
                out.append(line)
        return out

    # -- API ---------------------------------------------------------------
    def read(self, text: str) -> ParsedDeck:  # pragma: no cover - interface
        raise NotImplementedError
