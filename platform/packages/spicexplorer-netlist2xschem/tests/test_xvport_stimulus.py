"""The source-value grammar (issue #182).

An xschem source carries its whole stimulus in one attribute; a CDF spreads the same fact
over several parameters. These tests pin the grammar and its inverse — the CDF spellings
themselves live in the device map, where an operator can correct them without touching code.
"""

from __future__ import annotations

import pytest
from spicexplorer_netlist2xschem.virtuoso_export.stimulus import (
    StimulusError,
    format_stimulus,
    parse_stimulus,
)


@pytest.mark.parametrize(
    "text,kind,fields",
    [
        ("1.8", "dc", {"dc": "1.8"}),
        ("dc 0.2", "dc", {"dc": "0.2"}),
        ("dc 0.2 ac 0", "dc", {"dc": "0.2", "ac_mag": "0"}),
        ("dc 0 ac 1 90", "dc", {"dc": "0", "ac_mag": "1", "ac_phase": "90"}),
        ("ac 1", "dc", {"ac_mag": "1"}),
        ("DC 1.2 AC 1", "dc", {"dc": "1.2", "ac_mag": "1"}),
        (
            "pulse(0 1.8 1n 10p 10p 5n 10n)",
            "pulse",
            {
                "val0": "0",
                "val1": "1.8",
                "delay": "1n",
                "rise": "10p",
                "fall": "10p",
                "width": "5n",
                "period": "10n",
            },
        ),
        ("sin(0.9 0.1 1G)", "sin", {"offset": "0.9", "ampl": "0.1", "freq": "1G"}),
        ("sine(0.9 0.1 1G)", "sin", {"offset": "0.9", "ampl": "0.1", "freq": "1G"}),
        ("pwl(0 0 1n 1.8)", "pwl", {"wave": "0 0 1n 1.8"}),
        ("exp(0 1.8 1n 100p)", "exp", {"val0": "0", "val1": "1.8", "delay": "1n", "tau1": "100p"}),
    ],
)
def test_the_recognised_forms(text, kind, fields):
    stim = parse_stimulus(text)
    assert stim.kind == kind
    assert {k: v for k, v in stim.fields.items() if k != "type"} == fields
    assert stim.fields["type"] == kind  # what a CDF's srcType wants


def test_a_dc_prefix_and_a_transient_function_combine_as_in_spice():
    """`V1 a b DC 0 AC 1 SIN(0 1 1k)` is one source, not a choice between two."""
    stim = parse_stimulus("dc 0 ac 1 sin(0 1 1k)")
    assert stim.kind == "sin"
    assert stim.fields["dc"] == "0" and stim.fields["ac_mag"] == "1"
    assert stim.fields["ampl"] == "1" and stim.fields["freq"] == "1k"


@pytest.mark.parametrize(
    "text,says",
    [
        ("", "empty"),
        ("dc", "names no value"),
        ("wobble 3", "cannot read"),
        ("pwl(0 0 1n)", "PAIRS"),
        ("pulse()", "arguments"),
        ("vsup", "non-numeric"),
        ("dc VDD/2", "non-numeric"),
    ],
)
def test_what_it_refuses_and_why(text, says):
    """Every refusal carries its fix. A stimulus nobody parsed must not degrade to a
    warning — that warning is the defect this grammar replaces."""
    with pytest.raises(StimulusError, match=says):
        parse_stimulus(text)


def test_a_symbolic_value_is_accepted_only_on_request():
    assert parse_stimulus("dc VDD/2", symbolic=True).fields["dc"] == "VDD/2"
    # ...and the GRAMMAR is never relaxed by the opt-in
    with pytest.raises(StimulusError, match="cannot read"):
        parse_stimulus("wobble 3", symbolic=True)


@pytest.mark.parametrize(
    "text",
    [
        "dc 0.2",
        "dc 0.2 ac 1",
        "dc 0 ac 1 90",
        "pulse(0 1.8 1n 10p 10p 5n 10n)",
        "sin(0.9 0.1 1G)",
        "pwl(0 0 1n 1.8)",
        "dc 0 ac 1 sin(0 1 1k)",
    ],
)
def test_round_trip_through_the_canonical_fields(text):
    """The reverse port reads the CDF fields back and has to write `value=` again."""
    stim = parse_stimulus(text)
    assert parse_stimulus(format_stimulus(stim.kind, stim.fields)).fields == stim.fields


def test_formatting_stops_at_the_first_argument_the_cellview_did_not_carry():
    """Transient arguments are POSITIONAL: a gap must truncate, never shift.

    A cellview whose `tf` was left at its CDF default would otherwise come back as
    `pulse(0 1.8 1n 10p 5n)` — the pulse width read as the fall time.
    """
    got = format_stimulus("pulse", {"val0": "0", "val1": "1.8", "delay": "1n", "width": "5n"})
    assert got == "pulse(0 1.8 1n)"
