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
    DialectSyntaxError,
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
}

# Conditional assembly. NOT in _CARD_KINDS: these were classified `option`, which drops the CARD
# and lets the device lines between the cards fall through as ordinary devices — so every branch's
# devices ended up in one circuit, in parallel (Codex review, items DIA-01 and CG-02). The deck
# still simulates; it is simply not the circuit anyone wrote, and from the graph side the same
# merge makes a round-trip equivalence test faithfully reproduce a wrong graph.
#
# The reader refuses instead of choosing. Choosing would mean evaluating the condition, and the
# condition reads `.param` values that may be swept, overridden on the command line, or set in a
# `.alter` block — the taken branch is a property of a RUN, not of the text, so there is no correct
# answer this layer can give. Refusing is the same contract as `DialectSyntaxError` already states:
# fail loud, never drop devices.
_CONDITIONAL_CARDS = frozenset((".if", ".elseif", ".else", ".endif"))
# Directive kinds that DEFINE the circuit even though the card is not structural text. A conditional
# picking between corner libraries or two `.model` cards for the same device is the same defect
# wearing different clothes: keeping both arms leaves two conflicting definitions of one device, so
# these refuse alongside devices. Analyses, options and measures do not — a `.tran` behind
# `.IF(RUN_TRAN==1)` is a real pattern in the corpora these readers were built against, and keeping
# both arms of THAT changes nothing about the circuit.
_DEFINING_KINDS = frozenset(("model", "include", "library"))

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


def _conditional_refusal(opening_card: str, offender: str) -> str:
    """The message for a device (or other emitted card) found inside a `.if`/`.else` branch."""
    return (
        f"HSPICE conditional assembly is not supported around netlist structure: {offender[:60]!r} "
        f"sits inside {opening_card[:60]!r}. Which branch is taken depends on parameter values "
        "resolved at run time — a `.param` that a sweep, the command line or a `.alter` block may "
        "override — so the taken branch is a property of a RUN, not of this text, and the reader "
        "cannot choose one. Emitting every branch instead (which is what it used to do) puts all "
        "of their devices in the same circuit, in parallel: a deck that still simulates and is "
        "not the circuit you wrote. Resolve the conditional before handing the deck over — expand "
        "the branch you mean into a plain netlist, one deck per configuration, or lift the choice "
        "out into the parameter set the sweep already varies. Conditionals that guard only "
        "directives (a `.tran` behind `.IF(RUN_TRAN==1)`) are still accepted and reported as "
        "`conditional` directives."
    )


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
        # Open `.if`/`.elseif`/`.else` blocks, innermost last; each entry is the card that opened
        # the block, so a refusal can quote the condition rather than just the offending device.
        conditionals: list[str] = []
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
            if card in _CONDITIONAL_CARDS:
                if card == ".endif":
                    if conditionals:
                        conditionals.pop()
                elif card == ".if":
                    conditionals.append(stripped)
                elif conditionals:  # `.elseif` / `.else` — same block, next arm
                    conditionals[-1] = stripped
                else:  # an arm with no `.if` above it
                    conditionals.append(stripped)
                # Kept as a directive rather than dropped: a caller inspecting the deck can see
                # that a branch existed, which classifying it as `option` hid completely.
                directives.append(Directive("conditional", stripped))
                continue
            if conditionals and (
                card in _STRUCTURAL_CARDS
                or not card.startswith(".")
                or _CARD_KINDS.get(card) in _DEFINING_KINDS
            ):
                # Something that defines the circuit, inside a conditional branch.
                raise DialectSyntaxError(_conditional_refusal(conditionals[-1], stripped))
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

        if any(d.kind == "conditional" for d in directives):
            warnings.append(
                "HSPICE conditional cards were preserved as directives but NOT evaluated: the "
                "statements they guard are emitted unconditionally. What this reader RECOGNISES as "
                "defining the circuit inside a branch — a device, a `.model`, a corner `.lib` — is "
                "refused outright; what remains here is analyses, options, measures, `.alter`, and "
                "any card this reader does not recognise — an unrecognised card carries a warning "
                "of its own and, like every directive, is dropped from the canonical text. Every "
                "guarded analysis will run regardless of its condition."
            )
        if not saw_end:
            out.append(".end")
        return ParsedDeck(
            canonical_text="\n".join(out) + "\n",
            dialect=NetlistDialect.HSPICE,
            directives=tuple(directives),
            name_map={},
            warnings=tuple(warnings),
        )
