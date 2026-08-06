"""Netlist value tokens: read with ngspice rules, written with the target dialect's.

Two halves of one bug. Reading: parameter comparison used the YAML DSL's *case-sensitive* parser,
so ``1M`` was read as mega (making it equal to ``1meg`` and unequal to ``1m`` — the opposite of
what the simulator does) and every upper-case suffix failed to parse and degraded to a raw string,
so ``w=1U`` and ``w=1u`` were reported as different widths. Writing: the Spectre lane copied SPICE
suffix tokens through into a dialect whose scale factors are case-sensitive and disagree, so
``w=1U`` reached Spectre as *one metre*.
"""

import pytest
from spicexplorer_circuitgraph import CircuitGraph, netlists_equivalent, to_netlist
from spicexplorer_circuitgraph._eng import spice_number
from spicexplorer_circuitgraph._signatures import norm_value
from spicexplorer_core.spice_engine import NetlistView


def _graph(text: str) -> CircuitGraph:
    return CircuitGraph.from_netlist(NetlistView.from_string(text, dialect="auto"))


# ---------------------------------------------------------------------------
# Reading — ngspice scale-factor semantics
# ---------------------------------------------------------------------------
def test_suffix_case_is_irrelevant_in_a_netlist():
    assert norm_value("1U") == norm_value("1u") == "1e-06"
    assert norm_value("5K") == norm_value("5k") == "5000"
    assert norm_value("2P") == norm_value("2p") == "2e-12"


def test_m_is_milli_and_only_meg_is_mega():
    assert norm_value("1M") == norm_value("1m") == "0.001"
    assert norm_value("1MEG") == norm_value("1meg") == norm_value("1Meg") == "1000000"
    assert norm_value("1M") != norm_value("1meg")


def test_eng_equal_spellings_still_compare_equal():
    assert norm_value("0.18u") == norm_value("180n") == norm_value(1.8e-7)


def test_a_malformed_numeric_token_raises_instead_of_degrading_to_a_string():
    # `1.2.3` is shaped like a value and is not one. Falling back to the raw string made it
    # "compare unequal to everything" with no error anywhere.
    with pytest.raises(ValueError, match="not a parsable SPICE value"):
        norm_value("1.2.3")


def test_genuinely_symbolic_values_are_not_numbers_and_do_not_raise():
    assert norm_value("{w*2}") == "{w*2}"
    assert norm_value("'x_cfb1'") == "'x_cfb1'"
    assert norm_value("SG13_LV_NMOS") == "sg13_lv_nmos"
    assert norm_value("dc 1.8 ac 1") == "dc 1.8 ac 1"
    assert spice_number("rupolym") is None


def test_trailing_units_are_ignored_like_ngspice_does():
    assert spice_number("1kohm") == 1000.0
    assert spice_number("5pF") == pytest.approx(5e-12)


# ---------------------------------------------------------------------------
# Reading — the comparison built on top of it
# ---------------------------------------------------------------------------
def test_upper_and_lower_case_widths_are_one_width():
    a = "* a\nM1 d g s 0 nch w=1U l=2U\n.end\n"
    b = "* b\nM1 d g s 0 nch w=1u l=2u\n.end\n"
    assert netlists_equivalent(a, b, match_params=True)


def test_a_milliohm_is_not_a_megohm():
    milli = "* milli\nR1 a b 1M\n.end\n"
    mega = "* mega\nR1 a b 1meg\n.end\n"
    same_milli = "* same\nR1 a b 1m\n.end\n"
    assert not netlists_equivalent(milli, mega, match_params=True)
    assert netlists_equivalent(milli, same_milli, match_params=True)


# ---------------------------------------------------------------------------
# Writing — the Spectre lane must not ship a SPICE suffix
# ---------------------------------------------------------------------------
def test_spectre_emission_resolves_spice_suffixes():
    deck = to_netlist(
        _graph("* suffixes\nM1 d g s 0 nch w=1U l=2U\nR1 a b 1meg\nC1 a b 1P\n.end\n"),
        dialect="spectre",
    )
    assert "w=1e-06" in deck and "l=2e-06" in deck  # `1U` is ONE METRE to Spectre
    assert "r=1000000" in deck  # `1meg` is one milliohm to Spectre
    assert "c=1e-12" in deck  # `1P` is one farad to Spectre
    assert "1U" not in deck and "1P" not in deck and "1meg" not in deck


def test_spectre_emission_leaves_suffix_free_numbers_and_symbols_alone():
    deck = to_netlist(
        _graph("* plain\nR1 a b 1.8\nC1 a b 1e-12\nR2 a b {RFB}\nV1 a 0 dc 1.8\n.end\n"),
        dialect="spectre",
    )
    assert "r=1.8" in deck and "c=1e-12" in deck and "r=RFB" in deck and "dc=1.8" in deck


def test_spice_emission_still_copies_the_source_token_verbatim():
    # ngspice reads its own suffixes; only the Spectre lane needs the rewrite, and the SPICE
    # output stays byte-identical to the source spelling.
    deck = to_netlist(_graph("* verbatim\nR1 a b 1meg\nC1 a b 1P\n.end\n"))
    assert "R1 a b 1meg" in deck and "C1 a b 1P" in deck


# ---------------------------------------------------------------------------
# The malformed-number raise is narrow: number-shaped ≠ merely digit-leading
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "token",
    [
        "1k;load",  # ngspice-45 in-line `;` comment glued to a value — reads as 1 kΩ
        "3v3_ldo",  # a digit-leading .subckt master name (idiomatic for analog IP)
        "1n4148",  # …and for part numbers
        "2N2222",
        "4k7",  # the European decimal-in-the-suffix spelling
        "1_000",
    ],
)
def test_digit_leading_symbolic_tokens_pass_through_instead_of_raising(token):
    """Every one of these is legal ngspice input; none of them is a malformed *number*.

    The raise is for a token written entirely out of number characters that still is not a number.
    Widening it to "starts with a digit" rejected whole decks the simulator runs: `R1 a 0 1k;load`
    failed Spectre emission, and a `.subckt 3v3_ldo` deck failed to compare against ITSELF.
    """
    assert spice_number(token) is None
    assert norm_value(token) == token.lower()


@pytest.mark.parametrize("token", ["1.2.3", "1e+", "1e--3", "..5"])
def test_a_token_made_only_of_number_characters_still_raises(token):
    with pytest.raises(ValueError, match="not a parsable SPICE value"):
        spice_number(token)


def test_a_semicolon_comment_no_longer_breaks_spectre_emission():
    deck = "* semi\nR1 a 0 1k;load\nV1 a 0 1\n.end\n"
    emitted = to_netlist(_graph(deck), dialect="spectre")
    assert "R1 (a 0) resistor r=1k;load" in emitted  # verbatim, exactly as on the pre-fix baseline


def test_a_digit_leading_subckt_master_compares_equal_to_itself():
    deck = (
        "* ldo\n.subckt 3v3_ldo a b\nR1 a b 1k\n.ends\n"
        "X1 vin mid 3v3_ldo\nR2 mid 0 2k\nV1 vin 0 dc 1\n.end\n"
    )
    assert netlists_equivalent(deck, deck, match_params=True)


def test_a_digit_led_token_with_an_alphabetic_tail_is_still_read_as_a_number():
    # The boundary the ngspice "ignore the trailing unit" rule sits on, pinned rather than changed:
    # `3sigma` reads as 3 (that IS what ngspice does with such a token), so it compares equal to
    # `3` under match_params=True. `3v3_ldo` above does NOT, because `_` is not a unit letter.
    assert spice_number("3sigma") == 3.0
    assert norm_value("3sigma") == norm_value("3") == "3"
