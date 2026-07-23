"""Spectre → canonical-SPICE structural normalizer.

Handles the Spectre netlist grammar as observed in real decks (the analog-db AnalogGym/ferrosim
reference corpora and Virtuoso `createNetlist` output): ``//`` comments, trailing-``\\``
continuations, ``subckt … ends`` blocks (parenthesised or bare port lists), paren node lists on
instances, ``parameters`` statements, primitive masters (``resistor``/``capacitor``/…),
``include … [section=…]``, ``simulator lang=`` switching, and brace blocks (``statistics { … }``).

Statement disposition (see the plan's fail-loud rule):

* structural → rewritten into canonical SPICE;
* recognized non-structural (analyses, options, models, includes, libraries) → a verbatim
  :class:`~.base.Directive`;
* unrecognized *structural-looking* lines → :class:`~.base.DialectSyntaxError` — a device is
  never silently dropped.
"""

from __future__ import annotations

import re

from .base import (
    BaseDialectReader,
    DialectSpec,
    DialectSyntaxError,
    Directive,
    NetlistDialect,
    ParsedDeck,
)

__all__ = ["SpectreReader", "SPECTRE_SPEC"]

SPECTRE_SPEC = DialectSpec(
    dialect=NetlistDialect.SPECTRE,
    line_comment=("//",),
    inline_comment=("//",),
    continuation_leading=None,
    continuation_trailing="\\",
    subckt_open="subckt",
    subckt_close="ends",
    param_aliases={"m": "multi"},
    identifier_leading_digit_ok=False,
)

# Masters that are Spectre *analyses/controls*, not devices, when they appear in the master slot
# (`name <master> k=v …`). In-file subckt definitions shadow these (checked first).
_ANALYSIS_MASTERS = frozenset(
    "ac dc tran noise xf sp pz sens stb pss pac pnoise pxf psp qpss qpac qpnoise qpxf qpsp "
    "hb hbac hbnoise hbxf envlp montecarlo sweep info dcmatch acmatch stz pstb pdisto emir "
    "options set alter altergroup check checklimit paramtest reliability cktrom "
    "jitterevent".split()
)

_NUMERIC_START = re.compile(r"^[+-]?(\d|\.\d)")

# Statements identified by their *head* token (no instance name in front).
_CONTROL_HEADS = frozenset(
    "save options set ic nodeset shell export assert alter altergroup statistics paramtest "
    "checklimit info".split()
)

# Spectre primitive masters → (canonical ref prefix, value-parameter name).
_PRIMITIVES: dict[str, tuple[str, str | None]] = {
    "resistor": ("R", "r"),
    "capacitor": ("C", "c"),
    "inductor": ("L", "l"),
    "vsource": ("V", None),  # value assembled from dc/mag
    "isource": ("I", None),
    "iprobe": ("V", None),   # a 0 V ammeter — canonical `V… n1 n2 0`
    # linear controlled sources — the read-side inverse of circuitgraph's SpectreEmitter
    # (which emits `vccs gm=…` / `vcvs gain=…`); canonical G/E cards
    "vccs": ("G", "gm"),
    "vcvs": ("E", "gain"),
}

_LANG_RE = re.compile(r"^\s*simulator\s+lang\s*=\s*(spectre|spice)\b", re.IGNORECASE)
# `name ( n1 n2 … ) rest` — the unambiguous paren-node-list instance form.
_PAREN_INST_RE = re.compile(r"^(?P<name>\S+)\s*\((?P<nodes>[^)]*)\)\s*(?P<rest>.*)$")


def _split_tokens(text: str) -> list[str]:
    """Whitespace-split that keeps quoted strings and ``[…]`` vector params as single tokens."""
    tokens: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    depth = 0
    for ch in text:
        if quote is not None:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            continue
        if ch == "[":
            depth += 1
            buf.append(ch)
            continue
        if ch == "]":
            depth = max(0, depth - 1)
            buf.append(ch)
            continue
        if ch.isspace() and depth == 0:
            if buf:
                tokens.append("".join(buf))
                buf = []
            continue
        buf.append(ch)
    if buf:
        tokens.append("".join(buf))
    return tokens


class SpectreReader(BaseDialectReader):
    """Normalize Spectre netlist text into the canonical SPICE structural subset."""

    spec = SPECTRE_SPEC

    def read(self, text: str) -> ParsedDeck:
        directives: list[Directive] = []
        warnings: list[str] = []
        name_map: dict[str, str] = {}
        out: list[str] = ["* spectre netlist normalized by spicexplorer-core dialects"]

        # Virtuoso bus-bit names (`TRIM_OS\<1\>`) use characters spicelib's tokenizer cannot
        # carry — canonicalize them to `_`-delimited names, consistently across the whole deck
        # (net identity is preserved; the substitution applies to every occurrence).
        if "\\<" in text or "\\>" in text:
            text = text.replace("\\<", "_").replace("\\>", "_")
            warnings.append("bus-bit names canonicalized: `\\<N\\>` → `_N_`")

        segments = self._split_lang_segments(text.splitlines())

        # Pre-pass: every subckt name defined anywhere in the deck (drives the X-prefix rule and
        # shadows analysis-keyword masters).
        subckt_names: set[str] = set()
        for lang, stmts in segments:
            if lang != "spectre":
                continue
            for stmt in stmts:
                toks = _split_tokens(stmt)
                if toks and toks[0].lower() == "subckt" and len(toks) > 1:
                    subckt_names.add(toks[1])
                elif len(toks) > 2 and toks[0].lower() == "inline" and toks[1].lower() == "subckt":
                    subckt_names.add(toks[2])

        brace_depth = 0
        brace_buf: list[str] = []
        for lang, stmts in segments:
            if lang == "spice":
                # SPICE-language segment: already canonical — pass through verbatim.
                out.extend(stmts)
                continue
            for stmt in stmts:
                if brace_depth > 0:
                    brace_buf.append(stmt)
                    brace_depth += stmt.count("{") - stmt.count("}")
                    if brace_depth <= 0:
                        directives.append(Directive("unknown", " ".join(brace_buf)))
                        warnings.append(f"brace block preserved as a directive: {brace_buf[0][:60]}…")
                        brace_buf, brace_depth = [], 0
                    continue
                opened = stmt.count("{") - stmt.count("}")
                if opened > 0:
                    brace_depth = opened
                    brace_buf = [stmt]
                    continue
                self._transform(stmt, out, directives, warnings, name_map, subckt_names)
        if brace_buf:
            directives.append(Directive("unknown", " ".join(brace_buf)))
            warnings.append("unterminated brace block preserved as a directive")

        out.append(".end")
        return ParsedDeck(
            canonical_text="\n".join(out) + "\n",
            dialect=NetlistDialect.SPECTRE,
            directives=tuple(directives),
            name_map=name_map,
            warnings=tuple(warnings),
        )

    # ------------------------------------------------------------------
    def _split_lang_segments(self, lines: list[str]) -> list[tuple[str, list[str]]]:
        """Split raw lines into ``(lang, statements)`` segments at ``simulator lang=`` switches.

        Spectre segments get the Spectre lexing (``//`` comments stripped, trailing-``\\``
        continuations joined); SPICE segments are passed through raw (spicelib handles their
        ``*`` comments and leading-``+`` continuations natively).
        """
        segments: list[tuple[str, list[str]]] = []
        current_lang = "spectre"
        current: list[str] = []

        def flush() -> None:
            nonlocal current
            if not current:
                return
            if current_lang == "spectre":
                stripped = [self._strip_inline_comment(ln, ("//",)) for ln in current]
                joined = self._join_trailing(stripped, "\\")
                # Real-world hand-written Spectre decks (e.g. the ferrosim run decks) also use
                # SPICE-style leading-`+` continuations; no legal Spectre statement starts with
                # `+`, so joining them is unambiguous.
                segments.append(("spectre", self._join_leading(joined, "+")))
            else:
                segments.append(("spice", current))
            current = []

        for line in lines:
            m = _LANG_RE.match(line)
            if m:
                flush()
                current_lang = m.group(1).lower()
                continue
            current.append(line)
        flush()
        return segments

    # ------------------------------------------------------------------
    def _transform(
        self,
        stmt: str,
        out: list[str],
        directives: list[Directive],
        warnings: list[str],
        name_map: dict[str, str],
        subckt_names: set[str],
    ) -> None:
        stripped = stmt.strip()
        if not stripped:
            out.append("")
            return
        if stripped.startswith("*"):  # netlister banners etc. — keep as a canonical comment
            out.append(stripped)
            return

        toks = _split_tokens(stripped)
        head = toks[0].lower()

        if head == "inline" and len(toks) > 1 and toks[1].lower() == "subckt":
            toks = toks[1:]
            head = "subckt"

        if head == "subckt":
            name = toks[1]
            ports = [p for t in toks[2:] for p in (t.strip("()"),) if p and p not in ("(", ")")]
            out.append(f".subckt {name} {' '.join(ports)}".rstrip())
            return
        if head == "ends":
            out.append(".ends")
            return
        if head == "parameters":
            out.append(f".param {' '.join(toks[1:])}")
            return
        if head == "global":
            out.append(f".global {' '.join(toks[1:])}")
            return
        if head in ("include", "ahdl_include"):
            directives.append(Directive("include", stripped))
            return
        if head == "model":
            directives.append(Directive("model", stripped))
            return
        if head in ("library", "endlibrary", "section", "endsection"):
            directives.append(Directive("library", stripped))
            warnings.append(f"library-file statement preserved as a directive: {stripped[:60]}")
            return
        if head in ("real", "integer"):
            directives.append(Directive("unknown", stripped))
            warnings.append(f"typed parameter declaration preserved as a directive: {stripped[:60]}")
            return
        if head in _CONTROL_HEADS:
            kind = "option" if head in ("save", "options", "set", "ic", "nodeset") else "analysis"
            directives.append(Directive(kind, stripped))
            return

        # Instance or named analysis: `name [(nodes)] master k=v …` / `name n1 n2 … master k=v …`
        name, nodes, master, params = self._parse_instance(stripped, toks)
        if master is None:
            raise DialectSyntaxError(f"unrecognized Spectre statement: {stripped!r}")

        # A "master" that starts with a digit can't be a Spectre identifier — this is a
        # SPICE-style shorthand line (`V1 a b 1.4 type=dc`) inside a spectre segment (mixed
        # hand-written decks do this). It is already canonical: pass it through.
        if _NUMERIC_START.match(master):
            out.append(stripped)
            return

        if master in subckt_names or master.lower() in {s.lower() for s in subckt_names}:
            self._emit_instance(name, nodes, master, params, "X", out, name_map)
            return
        if master.lower() in _ANALYSIS_MASTERS:
            directives.append(Directive("analysis", stripped))
            return
        prim = _PRIMITIVES.get(master.lower())
        if prim is not None:
            self._emit_primitive(name, nodes, master, params, prim, out, warnings, name_map)
            return
        # A model master we can't resolve (models live in never-read PDK files). Trust the
        # instance's own ref letter only when it is *consistent with the arity* (a `dev1` must
        # not become a 4-terminal "diode"); otherwise type by arity, else keep a black box.
        first = name[:1].upper()
        arity = len(nodes)
        if first == "M" and arity == 4:
            prefix = "M"
        elif first == "Q" and arity in (3, 4, 5):
            prefix = "Q"
        elif first == "D" and arity == 2:
            prefix = "D"
        elif first == "J" and arity == 3:
            prefix = "J"
        elif arity == 4:
            prefix = "M"
            warnings.append(f"{name}: 4-terminal instance of unknown master {master!r} typed as MOS")
        else:
            prefix = "X"
            warnings.append(f"{name}: instance of unknown master {master!r} kept as a black box")
        self._emit_instance(name, nodes, master, params, prefix, out, name_map)

    # ------------------------------------------------------------------
    @staticmethod
    def _parse_instance(
        stmt: str, toks: list[str]
    ) -> tuple[str, list[str], str | None, list[str]]:
        """Split an instance statement into (name, nodes, master, k=v params)."""
        m = _PAREN_INST_RE.match(stmt)
        if m:
            rest = _split_tokens(m.group("rest"))
            if not rest:
                return m.group("name"), m.group("nodes").split(), None, []
            return m.group("name"), m.group("nodes").split(), rest[0], rest[1:]
        # Bare form: nodes are the tokens between the name and the last non-`k=v` token (the
        # master); params are the trailing `k=v` tokens.
        params_at = next((i for i, t in enumerate(toks) if "=" in t), len(toks))
        if params_at < 2:  # no master/node tokens before the params — not an instance
            return toks[0], [], None, []
        name = toks[0]
        master = toks[params_at - 1]
        nodes = toks[1 : params_at - 1]
        return name, nodes, master, toks[params_at:]

    def _emit_instance(
        self,
        name: str,
        nodes: list[str],
        master: str,
        params: list[str],
        prefix: str,
        out: list[str],
        name_map: dict[str, str],
    ) -> None:
        ref = name
        if not ref.upper().startswith(prefix):
            ref = prefix + name
            name_map[ref.upper()] = name
        rewritten = [self._rewrite_param(p) for p in params]
        line = f"{ref} {' '.join(nodes)} {master}"
        if rewritten:
            line += " " + " ".join(rewritten)
        out.append(line)

    @staticmethod
    def _rewrite_param(token: str) -> str:
        """Per-param canonicalization: Spectre ``multi=`` is SPICE ``m=``, and whitespace inside
        ``[…]`` vector values becomes ``,`` so the parameter stays one spicelib token."""
        key, sep, value = token.partition("=")
        if not sep:
            return token
        if "[" in value:
            value = re.sub(r"\s+", ",", value)
        if key.lower() == "multi":
            return f"m={value}"
        return f"{key}={value}"

    def _emit_primitive(
        self,
        name: str,
        nodes: list[str],
        master: str,
        params: list[str],
        prim: tuple[str, str | None],
        out: list[str],
        warnings: list[str],
        name_map: dict[str, str],
    ) -> None:
        prefix, value_key = prim
        kv = {}
        order = []
        for tok in params:
            key, sep, value = tok.partition("=")
            if not sep:
                warnings.append(f"{name}: bare token {tok!r} on primitive {master!r} kept verbatim")
                order.append((tok, None))
                continue
            kv[key.lower()] = value
            order.append((key.lower(), value))

        if value_key is not None:
            value = kv.pop(value_key, None)
            if value is None:
                # A `resistor` with no r= (e.g. a model-based variant) — keep the master token as
                # the value slot so nothing shifts on re-parse.
                warnings.append(f"{name}: primitive {master!r} has no {value_key}= — master kept as value token")
                value = master
        elif master.lower() == "iprobe":
            value = "0"
        else:  # vsource / isource — assemble from dc/mag
            dc = kv.pop("dc", None)
            mag = kv.pop("mag", None)
            if mag is not None:
                value = f"dc {dc or 0} ac {mag}"
            else:
                value = dc if dc is not None else "0"

        ref = name
        if not ref.upper().startswith(prefix):
            ref = prefix + name
            name_map[ref.upper()] = name
        rest = " ".join(
            f"{k}={v}" if v is not None else k
            for k, v in order
            if v is None or kv.get(k) == v  # only the params not consumed into the value slot
        )
        line = f"{ref} {' '.join(nodes)} {value}"
        if rest:
            line += " " + rest
        out.append(line)
