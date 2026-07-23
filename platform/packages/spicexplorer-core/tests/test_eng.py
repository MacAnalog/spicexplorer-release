"""Edge-case contract tests for ``eng.parse_value`` / ``eng.resolve_reference``.

The parser feeds every YAML knob, API param, and sizing value in the platform — a silent
mis-parse corrupts designs. These tests pin the contract: what parses, and (just as load-bearing)
what RAISES instead of guessing.
"""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_core.eng import parse_value, resolve_reference


@pytest.mark.parametrize("text,expected", [
    ("0.18u", 1.8e-7),
    ("50f", 5e-14),
    ("1.2k", 1.2e3),
    ("-1.5u", -1.5e-6),          # negative engineering value
    ("-3k", -3e3),
    ("1e-6", 1e-6),              # exponent notation, no suffix
    ("1E+3", 1e3),
    ("2.5e-15", 2.5e-15),
    ("2M", 2e6),                 # mega (single-char uppercase 'M')
    ("3m", 3e-3),                # milli (lowercase) — the m/M and m/meg distinctions are load-bearing
    ("5MEG", 5e6),               # ngspice mega, uppercase multi-char
    ("5meg", 5e6),               # ngspice mega, lowercase (real netlists use this spelling)
    ("5Meg", 5e6),               # ngspice mega, mixed case — 'meg' is matched case-insensitively
    ("2meg", 2e6),               # same value as '2M' via the multi-char spelling (was a crash)
    ("100MEG", 1e8),             # longest-suffix-first: not stripped to float('100ME')
    ("  1.5k  ", 1.5e3),         # surrounding whitespace
    ("1.8", 1.8),
    ("0", 0.0),
])
def test_parse_value_accepts(text, expected):
    out = parse_value(text)
    assert isinstance(out, np.float64)
    assert out == pytest.approx(expected, rel=1e-12)


def test_parse_value_numbers_pass_through():
    assert parse_value(1.8) == np.float64(1.8)
    assert parse_value(3) == np.float64(3.0)
    assert np.isinf(parse_value("inf")) and np.isinf(parse_value("INF"))


@pytest.mark.parametrize("text", [
    "1x",       # unknown suffix must raise, never silently return 1.0
    "u",        # suffix with no number
    "meg",      # multi-char suffix with no number (float('') raises)
    "1U",       # single-char multipliers are case-sensitive: 'U' is not micro — raise, don't guess
    "2K",       # 'K' is not kilo (single-char case-sensitivity preserved)
    "",
    "abc",
])
def test_parse_value_rejects(text):
    with pytest.raises(ValueError):
        parse_value(text)


def test_parse_value_m_vs_meg_distinction():
    """The load-bearing distinction: 'm' is milli, 'meg' (any case) is mega — they must not collide,
    and neither may crash (the reported '5MEG'/'5meg' regression)."""
    assert parse_value("5m") == pytest.approx(5e-3)      # milli
    assert parse_value("5meg") == pytest.approx(5e6)     # mega, lowercase
    assert parse_value("5MEG") == pytest.approx(5e6)     # mega, uppercase
    assert parse_value("5Meg") == pytest.approx(5e6)     # mega, mixed case
    # a mega spelling is 1e9x its milli namesake — the whole point of longest-suffix-first
    assert parse_value("5meg") / parse_value("5m") == pytest.approx(1e9)


def test_parse_value_none_is_descriptive():
    with pytest.raises(ValueError, match="None"):
        parse_value(None)  # a present-but-empty YAML key


def test_resolve_reference_hits_constraint_then_falls_back():
    constraints = {"W_M1": 5e-6, "1u": 42.0}
    assert resolve_reference("W_M1", constraints) == np.float64(5e-6)      # reference hit
    assert resolve_reference("0.5u", constraints) == pytest.approx(5e-7)   # miss → parsed
    assert resolve_reference(2.0, constraints) == np.float64(2.0)          # numeric passthrough
    # a constraint key that LOOKS like an engineering value shadows parsing — documented contract
    assert resolve_reference("1u", constraints) == np.float64(42.0)


def test_resolve_reference_unknown_nonnumeric_raises():
    with pytest.raises(ValueError):
        resolve_reference("W_M99", {})  # not a constraint, not parseable
