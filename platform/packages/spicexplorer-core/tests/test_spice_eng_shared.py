"""One suffix table, one test — the two netlist-reading consumers may not drift apart.

`spicexplorer-netlist2tf` and `spicexplorer-circuitgraph` both turn netlist value tokens into
numbers. They used to do it with separate tables, and answered `1M` a factor of 10**9 apart:
netlist2tf read it as mega (it tried the YAML DSL parser first, which is deliberately
case-SENSITIVE) while circuitgraph read it as milli, which is what a netlist means
(Codex review, items TF-01 and CG-01).

Both now read `spicexplorer_core.spice_eng`. This test drives BOTH consumers over the same tokens,
so re-introducing a private table in either one fails here. Core's own active-area walk
(`measurements.area`) reads deck tokens too and is driven over the same table (OPT-04).

Core declares neither consumer as a dependency (they depend on core, not the reverse), so the
consumer tests skip when that package is not installed; the core-only tests always run.
"""

from __future__ import annotations

import pytest
from spicexplorer_core.spice_eng import spice_number

# (token, value) — ngspice semantics: case-insensitive, `m` is milli, `meg` is the only mega.
SUFFIX_CASES = [
    ("1M", 1e-3),
    ("1m", 1e-3),
    ("1Meg", 1e6),
    ("1MEG", 1e6),
    ("1meg", 1e6),
    ("1k", 1e3),
    ("1K", 1e3),
    ("1u", 1e-6),
    ("1U", 1e-6),
    ("1n", 1e-9),
    ("1N", 1e-9),
    ("1p", 1e-12),
    ("1P", 1e-12),
    ("1f", 1e-15),
    ("1F", 1e-15),
    ("1g", 1e9),
    ("1G", 1e9),
    ("1t", 1e12),
    ("1T", 1e12),
    ("1a", 1e-18),
    ("1.8", 1.8),
    ("1e-6", 1e-6),
    ("-2.5k", -2.5e3),
    (".5u", 0.5e-6),
    ("1kohm", 1e3),
    ("5pF", 5e-12),  # trailing unit letters are ignored, as ngspice ignores them
    # Both non-ASCII spellings of micro. ngspice accepts neither, but the netlist2tf table this
    # module replaced accepted U+00B5, and a value pasted from a datasheet carries one of the two
    # often enough that losing it would silently demote `2.5\u00b5F` to a symbolic token.
    ("1\u00b5", 1e-6),
    ("1\u03bc", 1e-6),
    ("2.5\u00b5F", 2.5e-6),
    ("1\u00b5m", 1e-6),
]


@pytest.mark.parametrize("token,expected", SUFFIX_CASES)
def test_core_table(token, expected):
    assert spice_number(token) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("token,expected", SUFFIX_CASES)
def test_netlist2tf_agrees_with_the_table(token, expected):
    pytest.importorskip("spicexplorer_netlist2tf")
    from spicexplorer_netlist2tf.ingest import sympify_value

    assert float(sympify_value(token)) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("token,expected", SUFFIX_CASES)
def test_circuitgraph_agrees_with_the_table(token, expected):
    pytest.importorskip("spicexplorer_circuitgraph")
    from spicexplorer_circuitgraph.emit import SpectreEmitter

    rendered = SpectreEmitter._expr(token)
    assert float(rendered) == pytest.approx(expected, rel=1e-12)


@pytest.mark.parametrize("token,expected", SUFFIX_CASES)
def test_area_walk_agrees_with_the_table(token, expected):
    """The active-area walk reads deck geometry tokens; it used the DSL parser until OPT-04."""
    from spicexplorer_core.measurements.area import resolve_param_value

    assert resolve_param_value(token, {}) == pytest.approx(expected, rel=1e-12)


def test_the_two_consumers_agree_token_for_token():
    """The disagreement itself, pinned: same token, same number, in both tools."""
    pytest.importorskip("spicexplorer_circuitgraph")
    pytest.importorskip("spicexplorer_netlist2tf")
    from spicexplorer_circuitgraph.emit import SpectreEmitter
    from spicexplorer_netlist2tf.ingest import sympify_value

    for token, _ in SUFFIX_CASES:
        tf = float(sympify_value(token))
        cg = float(SpectreEmitter._expr(token))
        assert tf == pytest.approx(cg, rel=1e-12), (
            f"{token!r}: netlist2tf {tf} vs circuitgraph {cg}"
        )


def test_milli_and_mega_are_a_factor_of_a_million_apart():
    """The specific regression: `1M` must be milli, and `1meg` a million times it."""
    milli, mega = spice_number("1M"), spice_number("1meg")
    assert milli is not None and mega is not None, "both are numeric tokens"
    assert milli == pytest.approx(1e-3)
    assert mega == pytest.approx(1e6)
    assert mega / milli == pytest.approx(1e9)


def test_symbolic_tokens_are_not_numbers():
    assert spice_number("CL") is None
    assert spice_number("2N2222") is None  # digit-leading model name, ngspice-legal
    assert spice_number("{2*w}") is None  # an expression, kept verbatim by callers


def test_malformed_number_raises():
    with pytest.raises(ValueError):
        spice_number("1.2.3")
