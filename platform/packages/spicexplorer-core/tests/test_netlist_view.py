"""Tests for spicexplorer_core.spice_engine.NetlistView.

Exercised against the **real** IHP sg13g2 example netlists committed under ``examples/OTA/``
(pure parsing — no ngspice or PDK needed). Three complementary fixtures:

* ``cascode/ota-improved.spice``      — a flat transistor + V-source netlist (no subckt).
* ``5t-ota/ota-5t_tb-ac.spice``       — a testbench whose DUT is a generic subckt *instance*.
* ``folded_cascode/cora_testbench_ac.spice`` — a testbench with a (hyphen-free) ``opamp``
  subckt we can step into.

A couple of hermetic inline-string cases cover the constructors and the clean-name step-in
path without depending on the example tree.
"""

import glob
from pathlib import Path

import pytest
from spicexplorer_core.spice_engine import NetlistView

# --- example fixtures (tracked in the repo; resolved via the workspace root anchor) ---
_FIX = Path(__file__).resolve().parent / "fixtures"
CASCODE_FLAT = _FIX / "ota-improved.spice"
OTA5T_TB = _FIX / "ota-5t_tb-ac.spice"
FOLDED_TB = _FIX / "cora_testbench_ac.spice"
ALL_NETLISTS = sorted(glob.glob(str(_FIX / "*.spice")))


# ----------------------------------------------------------------------
# Hermetic basics (inline strings — no file dependency)
# ----------------------------------------------------------------------
_INLINE = """\
* inline smoke netlist (clean, hyphen-free subckt name)
.subckt inv vin vout vdd vss
XM1 vout vin vss vss sg13_lv_nmos w=1u l=0.13u
XM2 vout vin vdd vdd sg13_lv_pmos w=2u l=0.13u
.ends inv
X1 in out vdd vss inv
R1 out vss 10k
V1 vdd vss 1.8
.end
"""


def test_from_string_top_level_is_single_level():
    v = NetlistView.from_string(_INLINE)
    comps = set(v.get_components())
    assert {"X1", "R1", "V1"} <= comps  # subckt instance + passives/sources
    assert "XM1" not in comps          # primitives inside the subckt are NOT at this level


def test_from_string_clean_name_step_in():
    v = NetlistView.from_string(_INLINE)
    inner = v.get_subcircuit("X1")
    assert isinstance(inner, NetlistView)
    assert {"XM1", "XM2"} <= set(inner.get_components())
    assert inner.get_component_value("XM1") == "sg13_lv_nmos"
    # .subckt inv pins (vin vout vdd vss); XM1 = vout vin vss vss.
    assert inner.get_component_nodes("XM1") == ["vout", "vin", "vss", "vss"]


# ----------------------------------------------------------------------
# Broad smoke: every committed example netlist must parse + enumerate
# ----------------------------------------------------------------------
def test_example_fixtures_present():
    assert ALL_NETLISTS, "no example netlists found under examples/OTA — fixtures missing?"


@pytest.mark.parametrize(
    "path", ALL_NETLISTS, ids=lambda p: p.split("fixtures/")[-1]
)
def test_every_example_parses_and_enumerates(path):
    v = NetlistView.from_file(path)
    assert v.get_components(), f"{path} parsed to zero components"
    assert v.get_all_nodes(), f"{path} parsed to zero nodes"


# ----------------------------------------------------------------------
# Flat cascode DUT (no subckt) — rich assertions
# ----------------------------------------------------------------------
def test_cascode_flat_enumeration():
    v = NetlistView.from_file(CASCODE_FLAT)
    comps = set(v.get_components())
    assert len(comps) == 24
    # transistors (spicelib upper-cases reference designators)
    assert {"XM1", "XM2", "XM1C", "XM4C", "XMPD1"} <= comps
    # four voltage sources at top level (V/Vmeas)
    assert {"V1", "V2", "VMEAS1", "VMEAS4"} <= comps
    # it is a flat netlist: no subcircuit definitions
    assert v.get_subcircuit_names() == []


def test_cascode_flat_device_reads():
    v = NetlistView.from_file(CASCODE_FLAT)
    assert v.get_component_value("XM1") == "sg13_lv_nmos"   # input pair n-fet
    assert v.get_component_value("XM4") == "sg13_lv_pmos"   # p-load
    assert v.get_component_nodes("XM1") == ["net4", "vinp", "tail", "vss"]
    assert {"w", "l", "ng", "m"} <= {k.lower() for k in v.get_component_parameters("XM1")}
    assert {"vdd", "vss", "vout", "vinp", "vinn", "tail"} <= set(v.get_all_nodes())


# ----------------------------------------------------------------------
# 5t-ota testbench — generic subckt INSTANCE at top level
# ----------------------------------------------------------------------
def test_5tota_testbench_top_level():
    v = NetlistView.from_file(OTA5T_TB)
    assert set(v.get_components()) == {"VDD", "VSS", "C1", "VIN", "I0", "VENABLE", "XOTA"}
    assert {"v_dd", "v_out", "v_in", "v_ss", "net1", "v_ena", "GND"} <= set(v.get_all_nodes())


def test_hyphenated_subckt_name_resolves_via_truncated_prefix_fallback():
    """spicelib's subckt-name regex is ``[\\w.]+`` (no hyphen), so ``.subckt ota-5t`` is
    registered under the truncated name ``ota``. ``get_subcircuit`` bridges that: the instance's
    referenced name (``ota-5t``) falls back to the longest truncated-prefix match.
    """
    v = NetlistView.from_file(OTA5T_TB)
    assert v.get_subcircuit_names() == ["ota"]          # truncated at the hyphen (spicelib fact)
    inner = v.get_subcircuit("xota")                    # …but the instance still steps in
    assert "XM1" in inner.get_components()


def test_truncated_prefix_fallback_requires_a_separator():
    """The fallback must not mis-resolve a *different* subckt that happens to share a prefix:
    ``otabuf`` is not a truncation of ``ota`` (the next char is alphanumeric)."""
    nl = (
        "* c\n.subckt ota a b\nR1 a b 1k\n.ends\n"
        "X1 1 2 otabuf\n.end\n"
    )
    v = NetlistView.from_string(nl)
    with pytest.raises(Exception):
        v.get_subcircuit("X1")


# ----------------------------------------------------------------------
# folded_cascode testbench — real step-in into a hyphen-free subckt
# ----------------------------------------------------------------------
def test_subcircuit_ports_resolvable_and_unresolvable():
    v = NetlistView.from_file(FOLDED_TB)
    # hyphen-free `opamp` resolves → formal header port names, in order
    assert v.get_subcircuit_ports("X1") == ["vin-", "vin+", "vout", "vdd", "ib", "vss"]
    # hyphenated subckt resolves through the truncated-prefix fallback
    assert NetlistView.from_file(OTA5T_TB).get_subcircuit_ports("XOTA") == [
        "vdd", "vout", "vinp", "vinn", "ibias_20u", "d_ena", "vss",
    ]
    # a genuinely missing definition is still None (callers fall back to positional)
    nl = "* c\nX1 1 2 3 nowhere\n.end\n"
    assert NetlistView.from_string(nl).get_subcircuit_ports("X1") is None


def test_subcircuit_ports_handles_continuation_lines():
    nl = "* c\n.subckt big a b c\n+ d e f\nR1 a b 1k\n.ends\nX1 1 2 3 4 5 6 big\n.end\n"
    assert NetlistView.from_string(nl).get_subcircuit_ports("X1") == ["a", "b", "c", "d", "e", "f"]


def test_folded_cascode_step_in():
    v = NetlistView.from_file(FOLDED_TB)
    assert "X1" in v.get_components()
    assert v.get_subcircuit_names() == ["opamp"]

    inner = v.get_subcircuit("X1")
    inner_comps = set(inner.get_components())
    assert len(inner_comps) == 16
    mosfets = {c for c in inner_comps if c.startswith("XM")}
    assert len(mosfets) == 14 and {"XM0", "XM13"} <= mosfets
    assert {"vin+", "vin-", "vout", "vdd", "vss"} <= set(inner.get_all_nodes())
    assert inner.get_component_value("XM0") == "sg13_lv_pmos"
    assert inner.get_component_nodes("XM0") == ["vdd", "ib", "net1", "vdd"]


# ── input-format edge cases ──────────────────────────────────


def test_crlf_line_endings_parse():
    v = NetlistView.from_string("* title\r\nR1 in out 1k\r\nC1 out 0 100p\r\n.end\r\n")
    assert v.get_components() == ["R1", "C1"]


def test_missing_end_raises_clear_syntax_error():
    with pytest.raises(SyntaxError, match=r"\.END"):
        NetlistView.from_string("* title\nR1 in out 1k\n")


def test_missing_star_title_line_raises():
    """spicelib refuses a netlist whose first line doesn't match `^\\*` — a real-world trap
    (ngspice itself would silently swallow the first line as a title). Pinned so the failure
    mode stays a loud error, not silent device loss."""
    with pytest.raises(Exception, match="pattern"):
        NetlistView.from_string("R1 in out 1k\nC1 out 0 100p\n.end\n")
