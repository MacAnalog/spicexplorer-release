"""HSPICE → canonical-SPICE structural normalizer.

HSPICE's *structural* subset (``.subckt``/``.ends``, device lines, ``+`` continuations) is
largely spicelib-compatible already, so this reader is deliberately thin — it normalizes only
what actually breaks or degrades a parse, as established by auditing the AnalogGym decks:

* HSPICE-only simulation cards (``.measure``/``.lstb``/``.alter``/``.check``/``.option``/…)
  become verbatim :class:`~.base.Directive`\\ s — spicelib never sees them;
* ``.alter`` starts an *alternate run*: the base deck is parsed, every statement from the first
  ``.alter`` to ``.end`` is preserved as ``alter`` directives;
* ``$`` inline comments and the trailing ``*word`` inline comments seen in real AnalogGym
  testbenches (``xi1 … SMCNR_SE_2st_AMP    *ADM``) are stripped quote-awarely;
* spaces around ``=`` and inside ``'…'`` expressions are collapsed
  (``.PARAM t = '3.2 / GBW'`` → ``.PARAM t='3.2/GBW'``) so each parameter is one token;
* a missing ``* title`` first line / ``.end`` terminator (common in bare-subckt DUT files) is
  supplied — both are hard spicelib requirements.

Expressions stay verbatim strings — never evaluated.
"""

from __future__ import annotations

from .base import (
    BaseDialectReader,
    DialectSpec,
    Directive,
    NetlistDialect,
    ParsedDeck,
)

__all__ = ["HspiceReader", "HSPICE_SPEC"]

HSPICE_SPEC = DialectSpec(
    dialect=NetlistDialect.HSPICE,
    line_comment=("*",),
    inline_comment=("$",),
    continuation_leading="+",
    continuation_trailing=None,
    subckt_open=".subckt",
    subckt_close=".ends",
    param_aliases={},
    identifier_leading_digit_ok=True,
)

# Card → directive kind. Everything here is excluded from the canonical text.
_CARD_KINDS: dict[str, str] = {
    ".include": "include",
    ".inc": "include",
    ".lib": "include",
    ".del": "include",
    ".model": "model",
    ".dc": "analysis",
    ".ac": "analysis",
    ".tran": "analysis",
    ".op": "analysis",
    ".tf": "analysis",
    ".pz": "analysis",
    ".noise": "analysis",
    ".four": "analysis",
    ".disto": "analysis",
    ".sens": "analysis",
    ".lstb": "analysis",
    ".meas": "measure",
    ".measure": "measure",
    ".check": "measure",
    ".option": "option",
    ".options": "option",
    ".temp": "option",
    ".ic": "option",
    ".nodeset": "option",
    ".save": "option",
    ".probe": "option",
    ".print": "option",
    ".plot": "option",
    ".graph": "option",
    ".width": "option",
    ".title": "option",
    ".data": "option",
    ".enddata": "option",
    ".protect": "option",
    ".unprotect": "option",
    ".malias": "option",
    ".vec": "option",
    ".if": "option",
    ".elseif": "option",
    ".else": "option",
    ".endif": "option",
}

# Cards kept in the canonical text (the structural subset).
_STRUCTURAL_CARDS = frozenset((".subckt", ".ends", ".eom", ".param", ".global", ".end"))


def _strip_hspice_inline_comments(line: str) -> str:
    """Cut at ``$`` or at a whitespace-preceded ``*<letter>`` — both outside quotes.

    The ``*`` rule is a heuristic for the nonstandard trailing comments observed in real decks;
    a quoted ``'a *0.5'`` expression is protected (quote-aware scan), and ``1k*2`` has no
    preceding whitespace, so multiplication survives.
    """
    quote: str | None = None
    for i, ch in enumerate(line):
        if quote is not None:
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            continue
        if ch == "$":
            return line[:i].rstrip()
        if (
            ch == "*"
            and i > 0
            and line[i - 1].isspace()
            and i + 1 < len(line)
            and (line[i + 1].isalpha() or line[i + 1] == "_")
        ):
            return line[:i].rstrip()
    return line


def _collapse_assignments(line: str) -> str:
    """Normalize token boundaries: ``k = v`` → ``k=v``; ``'expr'`` → de-spaced ``{expr}``.

    The brace rewrite matters: spicelib parses ``{…}`` expressions everywhere but **silently
    drops** a ``.param`` whose value is single-quoted (HSPICE style) — verified against
    spicelib 1.x. Double-quoted strings (filenames) pass through verbatim.
    """
    out: list[str] = []
    quote: str | None = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote is not None:
            if ch == quote:
                out.append("}" if quote == "'" else ch)
                quote = None
            elif ch.isspace() and quote == "'":
                pass  # expressions ignore whitespace — drop it so the token stays whole
            else:
                out.append(ch)
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            out.append("{" if ch == "'" else ch)
            i += 1
            continue
        if ch == "=":
            # strip the whitespace we already emitted / are about to skip
            while out and out[-1].isspace():
                out.pop()
            out.append("=")
            i += 1
            while i < len(line) and line[i].isspace():
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


class HspiceReader(BaseDialectReader):
    """Normalize HSPICE netlist text into the canonical SPICE structural subset."""

    spec = HSPICE_SPEC

    def read(self, text: str) -> ParsedDeck:
        directives: list[Directive] = []
        warnings: list[str] = []
        out: list[str] = ["* hspice netlist normalized by spicexplorer-core dialects"]

        # Comments first (whole-line kept verbatim; inline stripped), then join `+` continuations
        # so classification sees whole statements.
        prepared: list[str] = []
        for line in text.splitlines():
            if line.lstrip().startswith("*"):
                prepared.append(line.strip())
                continue
            prepared.append(_strip_hspice_inline_comments(line))
        statements = self._join_leading(prepared, "+")

        in_alter = False
        saw_end = False
        for stmt in statements:
            stripped = stmt.strip()
            if not stripped or stripped.startswith("*"):
                if not in_alter:
                    out.append(stripped)
                continue
            # `.IF(cond)` glues the condition to the card token — split it off for the lookup.
            card = stripped.split(None, 1)[0].lower().split("(")[0]
            if card == ".alter":
                in_alter = True
                directives.append(Directive("alter", stripped))
                continue
            if in_alter:
                if card == ".end":
                    in_alter = False
                    saw_end = True
                    out.append(".end")
                else:
                    directives.append(Directive("alter", stripped))
                continue
            if card.startswith("."):
                if card in _STRUCTURAL_CARDS:
                    if card == ".end":
                        saw_end = True
                        out.append(".end")
                    elif card == ".eom":
                        out.append(".ends")
                    else:
                        out.append(_collapse_assignments(stripped))
                    continue
                kind = _CARD_KINDS.get(card)
                if kind is None:
                    kind = "unknown"
                    warnings.append(f"unrecognized card preserved as a directive: {stripped[:60]}")
                directives.append(Directive(kind, stripped))
                continue
            # Device / instance line — canonical after token normalization.
            out.append(_collapse_assignments(stripped))

        if not saw_end:
            out.append(".end")
        return ParsedDeck(
            canonical_text="\n".join(out) + "\n",
            dialect=NetlistDialect.HSPICE,
            directives=tuple(directives),
            name_map={},
            warnings=tuple(warnings),
        )
