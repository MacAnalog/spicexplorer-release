"""Parse a SPICE source value into the CANONICAL stimulus fields a CDF spreads over.

An xschem source carries its whole stimulus in ONE attribute — ``value="dc 0.2 ac 0"``,
``value="pulse(0 1.8 1n 10p 10p 5n 10n)"`` — while Virtuoso spreads the same fact over a
handful of CDF parameters (``vdc``/``acm``/``acp``, or ``srcType`` plus ``val0``/``val1``/
``period``/…). Writing the string into one field is not a near miss: Cadence reads the word
``dc`` as a design variable and the bench's operating point becomes whatever that variable
happens to hold, while the port still reports success (issue #182).

This module is the **grammar only**. It returns canonical field names — ``dc``, ``ac_mag``,
``val0``, … — and never a CDF parameter name: which CDF field each one lands in is kit and
cell knowledge, and lives in the device map beside every other CDF fact (``stimulus.types``
in ``devmap.py``). That split is what lets an operator fix a wrong CDF spelling in YAML
instead of in Python.

Recognised forms (a DC/AC prefix and one transient function may combine, as in SPICE):

* ``0.2`` — a bare value is the DC operating point
* ``dc 0.2``, ``dc 0.2 ac 1``, ``dc 0 ac 1 90``, ``ac 1`` (DC defaults to 0)
* ``pulse(v0 v1 [td [tr [tf [pw [per]]]]])``
* ``sin(vo va freq [td [damp]])`` (``sine`` accepted)
* ``pwl(t0 v0 t1 v1 …)`` — the points are handed over verbatim as one ``wave`` field
* ``exp(v1 v2 [td1 [tau1 [td2 [tau2]]]])``

Anything else raises `StimulusError` carrying the fix. A stimulus nobody parsed is the one
case that must NOT degrade to a warning — the whole defect this replaces was a warning.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from spicexplorer_core.eng import parse_value

__all__ = [
    "Stimulus",
    "StimulusError",
    "CANONICAL_FIELDS",
    "parse_stimulus",
    "format_stimulus",
]

#: Every canonical field this grammar can produce, grouped by the form that yields it. A
#: device map's `stimulus.types.<kind>.params` maps a subset of these onto CDF parameters.
CANONICAL_FIELDS: dict[str, tuple[str, ...]] = {
    "dc": ("type", "dc", "ac_mag", "ac_phase"),
    "pulse": (
        "type",
        "dc",
        "ac_mag",
        "ac_phase",
        "val0",
        "val1",
        "delay",
        "rise",
        "fall",
        "width",
        "period",
    ),
    "sin": ("type", "dc", "ac_mag", "ac_phase", "offset", "ampl", "freq", "delay", "damp"),
    "pwl": ("type", "dc", "ac_mag", "ac_phase", "wave"),
    "exp": ("type", "dc", "ac_mag", "ac_phase", "val0", "val1", "delay", "tau1", "delay2", "tau2"),
}

#: positional argument names of each transient function, in SPICE order
_POSITIONAL: dict[str, tuple[str, ...]] = {
    "pulse": ("val0", "val1", "delay", "rise", "fall", "width", "period"),
    "sin": ("offset", "ampl", "freq", "delay", "damp"),
    "exp": ("val0", "val1", "delay", "tau1", "delay2", "tau2"),
}
_ALIASES = {"sine": "sin", "pwlfile": "pwl"}
_FUNC = re.compile(r"\b(pulse|sin|sine|exp|pwl|pwlfile)\b\s*(\(([^)]*)\)|([^()]*))", re.I)


class StimulusError(ValueError):
    """A source value this grammar does not understand, with the fix attached."""


@dataclass(frozen=True)
class Stimulus:
    """One parsed source value: its transient kind plus the canonical fields it set."""

    kind: str  # dc | pulse | sin | pwl | exp — the `type` a CDF's srcType wants
    fields: dict[str, str] = field(default_factory=dict)  # canonical name -> value as written

    def __post_init__(self) -> None:
        object.__setattr__(self, "fields", dict(self.fields))


def _numeric(token: str) -> bool:
    try:
        float(parse_value(token))
    except Exception:
        return False
    return True


def _check(where: str, values: dict[str, str], *, symbolic: bool) -> None:
    if symbolic:
        return
    bad = {k: v for k, v in values.items() if k != "wave" and not _numeric(v)}
    if bad:
        raise StimulusError(
            f"{where}: non-numeric stimulus value(s) "
            + ", ".join(f"{k}={v!r}" for k, v in sorted(bad.items()))
            + " — resolve the expression in the sheet, or pass --allow-symbolic to write it "
            "verbatim and check the CDF by hand"
        )


def parse_stimulus(text: str, *, symbolic: bool = False) -> Stimulus:
    """Parse a SPICE source value string (see the module docstring for the grammar).

    ``symbolic=True`` accepts a value that is not a number (a design variable or an
    expression) and hands it through unevaluated — the caller has opted into checking the
    CDF by hand. It never relaxes the *grammar*: an unrecognised stimulus still raises.
    """
    raw = " ".join(text.strip().split())
    if not raw:
        raise StimulusError("empty stimulus")
    where = f"stimulus {raw!r}"
    fields: dict[str, str] = {}

    # one transient function, if any — pulled out first so its arguments are not read as
    # dc/ac tokens
    kind = "dc"
    m = _FUNC.search(raw)
    if m is not None:
        kind = _ALIASES.get(m.group(1).lower(), m.group(1).lower())
        args = (m.group(3) if m.group(3) is not None else m.group(4) or "").replace(",", " ")
        tokens = args.split()
        if kind == "pwl":
            if len(tokens) < 2 or len(tokens) % 2:
                raise StimulusError(
                    f"{where}: pwl takes time/value PAIRS (got {len(tokens)} number(s)) — "
                    "pwl(0 0 1n 1.8)"
                )
            fields["wave"] = " ".join(tokens)
        else:
            names = _POSITIONAL[kind]
            if not tokens or len(tokens) > len(names):
                raise StimulusError(
                    f"{where}: {kind} takes 1..{len(names)} arguments ({' '.join(names)}), "
                    f"got {len(tokens)}"
                )
            fields.update(dict(zip(names, tokens)))
        raw = (raw[: m.start()] + " " + raw[m.end() :]).strip()

    # the dc/ac prefix, whatever is left of it
    tokens = raw.split()
    i = 0
    while i < len(tokens):
        word = tokens[i].lower()
        if word == "dc" and i + 1 < len(tokens):
            fields["dc"] = tokens[i + 1]
            i += 2
        elif word == "ac" and i + 1 < len(tokens):
            fields["ac_mag"] = tokens[i + 1]
            i += 2
            if i < len(tokens) and _numeric(tokens[i]) and tokens[i].lower() not in ("dc", "ac"):
                fields["ac_phase"] = tokens[i]
                i += 1
        elif i == 0 and len(tokens) == 1 and word not in ("dc", "ac"):
            # a bare value IS the dc operating point ("1.8")
            fields["dc"] = tokens[0]
            i += 1
        elif word in ("dc", "ac"):
            raise StimulusError(f"{where}: `{word}` names no value — write `{word} <value>`")
        else:
            raise StimulusError(
                f"{where}: cannot read {' '.join(tokens[i:])!r} — expected `dc <v>`, "
                "`ac <mag> [phase]`, or one of pulse()/sin()/pwl()/exp()"
            )

    if not fields:
        raise StimulusError(f"{where}: nothing to set")
    _check(where, fields, symbolic=symbolic)
    fields["type"] = kind
    return Stimulus(kind=kind, fields=fields)


def format_stimulus(kind: str, fields: dict[str, str]) -> str:
    """The inverse of `parse_stimulus`: canonical fields back into a SPICE value string.

    Used by the reverse port (cv2sch), which reads a source's CDF fields out of Cadence and
    has to write the sheet's one `value=` attribute again. A transient function's arguments
    are POSITIONAL, so the run stops at the first one the cellview did not carry rather than
    shifting every later argument one place left.
    """
    kind = _ALIASES.get(kind.lower(), kind.lower())
    prefix = []
    if "dc" in fields:
        prefix.append(f"dc {fields['dc']}")
    if "ac_mag" in fields:
        prefix.append(f"ac {fields['ac_mag']}")
        if "ac_phase" in fields:
            prefix.append(fields["ac_phase"])
    if kind == "dc":
        return " ".join(prefix)
    if kind == "pwl":
        wave = fields.get("wave", "").strip()
        body = f"pwl({wave})" if wave else ""
    else:
        args = []
        for name in _POSITIONAL[kind]:
            if name not in fields:
                break
            args.append(fields[name])
        body = f"{kind}({' '.join(args)})" if args else ""
    return " ".join([*prefix, body]).strip()
