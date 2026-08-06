"""ngspice value-token semantics — the parser the graph's *netlist-side* numbers need.

``spicexplorer_core.eng.parse_value`` is the **YAML DSL's** parser: its single-character suffixes
are case-SENSITIVE (``m`` milli vs ``M`` mega), which is the documented convention of the optimizer's
own configuration language. A netlist token is a different language. ngspice's scale factors are
case-INSENSITIVE and its ``M`` is **milli**, with ``MEG`` the only spelling of mega — so reading a
netlist through the DSL parser gets two families of value wrong:

* ``1M`` is read as mega, making it compare equal to ``1meg`` and unequal to ``1m`` — exactly
  backwards (in a netlist ``1M`` **is** ``1m``, and ``1meg`` is a thousand times either), and
* every upper-case core suffix (``1U``, ``5K``, ``2P``) fails to parse at all.

This module owns the netlist reading. It is deliberately **not** exported: it is an implementation
detail of value comparison (``_signatures.norm_value``) and of Spectre emission, which must turn a
SPICE suffix into a plain number because Spectre's own scale factors are case-sensitive and disagree
(Spectre ``M`` is mega and ``U``/``P`` are not scale factors at all, so an untranslated ``w=1U``
means *one metre*).

The three-way return of :func:`spice_number` is the whole contract:

* a **number** — the token is numeric (with or without a scale factor);
* ``None`` — the token is not a number at all (a model name, a parameter symbol, a braced or
  quoted expression). Callers keep it verbatim;
* a **raise** — the token is written entirely out of number characters and is still not a number
  (``1.2.3``, ``1e+``). Swallowing that into "some string" is how a typo'd width silently stops
  being a width. Tokens that merely *begin* with a digit (``1k;load``, ``3v3_ldo``, ``2N2222``) are
  ngspice-legal and take the ``None`` branch, not this one.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

__all__ = ["spice_number", "format_number"]

# ngspice scale factors, longest-first for the multi-character ones. Case is folded before lookup:
# unlike the DSL parser (and unlike Spectre) a netlist's `M`, `m`, `Meg` and `MEG` all mean what
# their lower-case spelling means. The factors are DECIMAL, and the scaling below is done in
# `Decimal` rather than binary floating point: `5 * 1e-6` is not the same double as `5e-6`, and the
# difference shows up as `w=4.9999999999999996e-06` on an emitted device line.
_MULTI_SUFFIX: tuple[tuple[str, Decimal], ...] = (
    ("meg", Decimal("1e6")),
    ("mil", Decimal("25.4e-6")),  # ngspice's thousandth-of-an-inch, not a metric prefix
)
_SINGLE_SUFFIX: dict[str, Decimal] = {
    "t": Decimal("1e12"),
    "g": Decimal("1e9"),
    "k": Decimal("1e3"),
    "m": Decimal("1e-3"),  # MILLI — `meg` above is the only mega
    "u": Decimal("1e-6"),
    "n": Decimal("1e-9"),
    "p": Decimal("1e-12"),
    "f": Decimal("1e-15"),
    "a": Decimal("1e-18"),
}
_UNSCALED = Decimal(1)

# A number, then an optional all-alphabetic tail. The tail is the scale factor plus any unit the
# deck felt like writing (`1kohm`, `5pF`): ngspice reads the factor and ignores the rest, so we do
# too — an unrecognised tail simply scales by 1 (`1x` is 1.0), which is what the simulator sees.
_NUMBER_WITH_SUFFIX = re.compile(
    r"^([+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?)([a-z]*)$", re.IGNORECASE
)
# "Meant to be a number and nothing else": composed *solely* of the characters a numeric literal is
# made of (digits, sign, decimal point, exponent marker). A token like that which does NOT parse is
# malformed (`1.2.3`, `1e+`) and raises. The test is deliberately NOT "starts with a digit": that
# wider rule also swallows ngspice-legal input — `1k;load` (an in-line `;` comment glued to a value,
# which ngspice-45 reads as 1 kΩ), digit-leading `.subckt` master names (`3v3_ldo`, `1n4148`,
# `2N2222`), `4k7`, `1_000` — none of which is a malformed *number*. Anything carrying a character
# from outside this class is symbolic and passes through verbatim (``None``), as it always did.
_NUMBER_ONLY_CHARS = re.compile(r"^[+-]?[0-9.eE+-]+$")
# Characters that make a token an *expression* rather than a value, even though it may start with a
# digit (`2*w`, `{1u*k}`, `'3.3/2'`). Those are passed through untouched by every caller.
_EXPRESSION_CHARS = frozenset("{}()[]'\"*/^%,= \t")


def spice_number(token: str) -> float | None:
    """Parse one netlist value token with ngspice scale-factor semantics.

    Returns the value, or ``None`` when ``token`` is not a numeric literal (a model name, a
    parameter symbol, a braced/quoted expression — all of which callers must keep verbatim).

    Raises :class:`ValueError` when the token is written *entirely* out of number characters and
    is still not a number (``"1.2.3"``, ``"1e+"``): that is a malformed value, and the old behavior
    — catching every exception and falling back to the raw string — turned a broken width into a
    value that merely compared unequal to everything, with no error anywhere. A token that merely
    *starts* with a digit is not enough: ``1k;load``, ``3v3_ldo`` and ``2N2222`` are all legal
    ngspice input, and rejecting them made a whole deck fail to emit.
    """
    text = token.strip()
    if not text or _EXPRESSION_CHARS & set(text):
        return None
    match = _NUMBER_WITH_SUFFIX.match(text)
    if match is None:
        if _NUMBER_ONLY_CHARS.match(text):
            raise ValueError(f"{token!r} is not a parsable SPICE value")
        return None
    mantissa, suffix = match.group(1), match.group(2).lower()
    try:
        value = Decimal(mantissa)
    except InvalidOperation as exc:  # pragma: no cover - the regex already constrains the mantissa
        raise ValueError(f"{token!r} is not a parsable SPICE value") from exc
    factor = next(
        (f for prefix, f in _MULTI_SUFFIX if suffix.startswith(prefix)),
        _SINGLE_SUFFIX.get(suffix[:1], _UNSCALED),
    )
    return float(value * factor)


def format_number(value: float) -> str:
    """Render a parsed value as a scale-factor-free literal (the form every dialect agrees on).

    Integral values render without a decimal point (``4``, not ``4.0``) so emitted params match the
    direct path; everything else uses Python's shortest round-tripping repr, so no precision is lost
    on the way through.
    """
    if value.is_integer() and abs(value) < 1e16:
        return str(int(value))
    return repr(value)
