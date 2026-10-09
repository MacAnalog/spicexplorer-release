"""Quoted values ingest, and the audit's silent wrong answers are fixed (ROAD-02, LEAF-F05).

Each test reproduces one finding of the 2026-09-24 framework audit. Before the fix every one of them
either crashed with an unrelated error or returned a plausible-looking wrong answer:

* ROAD-02 — a single-quoted SPICE value (``C0 a b 'CAPACITOR_0'``, the form analog-db exports)
  reached sympy as a string literal and crashed ingestion on 46/72 corpus circuits;
* an unknown output net resolved to AC ground (``H(s) = 0``);
* ``M1`` and ``XM1`` minted one symbol set, silently matching two independent transistors;
* ``L = 0`` gave a NaN transfer function;
* an AC-bearing V source was left open in a driving-point analysis (``Z_out`` 1 kΩ, not 500 Ω);
* TF-1..TF-4 of the cross-repo audit: a partial operating point filled with ball-park values
  without saying so, a NaN magnitude passed the DOMINANCE check unnoticed, a DC pole raised
  ``TypeError``, and an unparseable ``ac`` token was dropped with no warning (``'inf'`` crashed).
"""

from __future__ import annotations

import cmath
import logging
import math

import pytest
import sympy as sp
from spicexplorer_netlist2tf import (
    Circuit2TF,
    PortPair,
    SymbolMint,
    asymptotic_gain,
    build_system,
    extract_tf,
    from_string,
    input_impedance,
    loop_gain,
    output_impedance,
    small_signal_model,
    transfer_function,
    transimpedance,
)
from spicexplorer_netlist2tf.assumptions import (
    DOMINANCE,
    Assumption,
    transconductance_dominates,
)
from spicexplorer_netlist2tf.ingest import sympify_value
from spicexplorer_netlist2tf.mna import _drop_port_stimulus
from spicexplorer_netlist2tf.model.ir import Fidelity
from spicexplorer_netlist2tf.model.primitives import IndependentV, Inductor
from spicexplorer_netlist2tf.numeric import complex_value_at
from spicexplorer_netlist2tf.simplify import _apply_dominance, simplify_tf
from spicexplorer_netlist2tf.tf import S


def _system(deck: str, level: Fidelity = Fidelity.SOME_PARASITIC):
    return build_system(small_signal_model(from_string(deck), level=level))


# ------------------------------------------------------------------------
# ROAD-02 — quoted values
# ------------------------------------------------------------------------
def test_single_quoted_symbol_parses_like_a_brace_expression():
    assert sympify_value("'CAPACITOR_0'") == sp.Symbol("capacitor_0")
    assert sympify_value("'CAPACITOR_0'") == sympify_value("{CAPACITOR_0}")


def test_double_quoted_expression_parses():
    assert sympify_value('"2*W"') == 2 * sp.Symbol("w")


def test_quoted_number_and_nested_delimiters_parse():
    assert sympify_value("'1p'") == sympify_value("1p")
    assert sympify_value("'{2*W}'") == 2 * sp.Symbol("w")


@pytest.mark.parametrize("token", ["{'2*W'}", "'{2*W}'", "\"{'2*W'}\"", "' {2*W} '", "{ '2*W' }"])
def test_delimiters_unwrap_in_any_nesting_and_padding(token):
    """Braces and quotes are removed in whichever order they nest, with whitespace between layers
    (a padded ``' {2*W} '`` left its braces on and read as a set before the inner strip)."""
    assert sympify_value(token) == 2 * sp.Symbol("w")


@pytest.mark.parametrize("token", ["''", '""', "{}", "'{}'", "{''}", "' '"])
def test_an_empty_delimited_token_raises_naming_it(token):
    with pytest.raises(ValueError, match=r"empty value token"):
        sympify_value(token)


@pytest.mark.parametrize("token", ["'CL", "CL'", "'CL\"", "\"CL'", "'"])
def test_a_lone_or_mismatched_quote_is_not_stripped(token):
    """Only a MATCHING outer pair is a delimiter; anything else still raises (a stray quote
    silently dropped would turn a malformed token into a plausible symbol)."""
    with pytest.raises(ValueError):
        sympify_value(token)


def test_quoted_source_keyword_values_parse():
    ir = from_string("* v\nV1 a 0 dc 'VDC' ac '1'\nR1 a 0 1k\n.end")
    params = next(d for d in ir.devices if d.ref.upper() == "V1").params
    assert params["dc"] == sp.Symbol("vdc") and params["ac"] == 1


@pytest.mark.parametrize("token", ["True", "(1, 2)"])
def test_a_token_that_is_not_an_expression_raises_value_error(token):
    """sympify can return a non-``Expr`` (a bool, a tuple, a Python str): name the token instead
    of crashing in ``_lower_symbols`` or leaking the object into the IR."""
    with pytest.raises(ValueError, match=r"not an expression"):
        sympify_value(token)


# The shape analog-db's abstract netlists use: quoted design-variable values on a bias source and
# a compensation cap (circuits/amp_003_fan_smc/abstract/netlist.spice).
QUOTED_DECK = """* quoted design variables
xm1 out in vss vss nmos l=x_dut_xm1_l w=x_dut_xm1_w m=x_dut_xm1_m
I0 vdd out 'CURRENT_0_BIAS'
C0 in out 'CAPACITOR_0'
.end
"""


def test_quoted_deck_ingests_with_symbolic_values():
    ir = from_string(QUOTED_DECK)
    by_ref = {d.ref.upper(): d for d in ir.devices}
    assert by_ref["C0"].params["value"] == sp.Symbol("capacitor_0")
    assert by_ref["I0"].params["dc"] == sp.Symbol("current_0_bias")
    assert {"capacitor_0", "current_0_bias"} <= {str(s) for s in ir.free_symbols}


def test_quoted_value_reaches_the_transfer_function():
    quoted = transfer_function("* rc\nR1 in out R\nC1 out 0 'CL'\n.end", ("out", "0"), ("in", "0"))
    braced = transfer_function("* rc\nR1 in out R\nC1 out 0 {CL}\n.end", ("out", "0"), ("in", "0"))
    assert quoted.tf_exact_expr == braced.tf_exact_expr
    assert "cl" in quoted.tf_exact_expr


# ------------------------------------------------------------------------
# LEAF-F05 — unknown net
# ------------------------------------------------------------------------
RC = "* rc\nR1 in out 1k\nC1 out 0 1p\n.end"
# the inverting amp of test_n2tf_analyses: A∞ = -Rf/Rs through M1's loop
_INV = (
    "* inv\nVin inx 0 ac 1\nRs inx ing rs\nRf ing out rfb\nM1 out ing 0 0 nmos\nRD out 0 rd\n.end"
)


def test_unknown_output_net_raises():
    with pytest.raises(ValueError, match=r"'outt'"):
        extract_tf(_system(RC), ("outt", "0"), ("in", "0"))


def test_unknown_output_net_raises_through_the_public_api():
    with pytest.raises(ValueError, match=r"'outt'"):
        transfer_function(RC, ("outt", "0"), ("in", "0"))


def test_unknown_input_net_of_a_pair_raises_instead_of_inverting_the_sign():
    """A typo'd ``in+`` of a two-node pair was read as AC ground, so the dm drive landed on
    ``in-`` alone: the right magnitude with the sign flipped."""
    deck = "* diff\nR1 inp out 1k\nR2 inn out 1k\nR3 out 0 1k\n.end"
    with pytest.raises(ValueError, match=r"'inpp'"):
        extract_tf(_system(deck), ("out", "0"), ("inpp", "inn"))


def test_a_ground_alias_absent_from_the_netlist_is_still_ground():
    """``gnd`` is a reference name, not a typo, even when the netlist only uses ``0``."""
    h = extract_tf(_system("* div\nR1 in out 1k\nR2 out 0 1k\n.end"), ("out", "gnd"), ("in", "gnd"))
    assert h.expr == sp.Rational(1, 2)


def test_a_ground_alias_is_case_insensitive():
    h = extract_tf(_system("* div\nR1 in out 1k\nR2 out 0 1k\n.end"), ("out", "GND"), ("in", "Gnd"))
    assert h.expr == sp.Rational(1, 2)


def test_a_ground_net_spelled_by_the_netlist_is_known():
    """A circuit grounded on ``vss`` (``ground="vss"``): its reference net is known, not a typo."""
    h = transfer_function(
        "* div\nR1 in out 1k\nR2 out vss 1k\n.end", ("out", "vss"), ("in", "vss"), ground="vss"
    )
    assert sp.sympify(h.tf_exact_expr) == sp.Rational(1, 2)


def test_the_declared_ground_is_known_when_no_device_names_it():
    """A deck wired on ``0`` whose plan declares ``vss`` its ground: a port on ``vss`` is the
    reference, not a typo (the orchestration analysis workflow passes the plan's ground this way)."""
    h = transfer_function(
        "* div\nR1 in out 1k\nR2 out 0 1k\n.end", ("out", "vss"), ("in", "vss"), ground="vss"
    )
    assert sp.sympify(h.tf_exact_expr) == sp.Rational(1, 2)


def test_a_typo_of_the_declared_ground_still_raises():
    with pytest.raises(ValueError, match=r"output net 'vsss' is not in the circuit"):
        transfer_function(
            "* div\nR1 in out 1k\nR2 out 0 1k\n.end", ("out", "vsss"), ("in", "vss"), ground="vss"
        )


def test_unknown_negative_net_of_a_pair_raises():
    """The check covers BOTH members of a pair: a typo'd reference net was AC ground as well."""
    with pytest.raises(ValueError, match=r"output net 'gndd'"):
        extract_tf(_system(RC), ("out", "gndd"), ("in", "0"))


@pytest.mark.parametrize(
    ("output", "input_", "role", "net"),
    [(("outt", "0"), ("in", "0"), "output", "outt"), (("out", "0"), ("inn", "0"), "input", "inn")],
)
def test_the_error_names_the_role_the_net_and_the_known_nets(output, input_, role, net):
    with pytest.raises(ValueError, match=rf"{role} net '{net}' is not in the circuit") as exc:
        extract_tf(_system(RC), output, input_)
    assert "known nets: 0, in, out" in str(exc.value)


def test_a_long_known_net_list_is_truncated_with_a_count():
    chain = "".join(f"R{i} n{i} n{i + 1} 1k\n" for i in range(25))
    with pytest.raises(ValueError, match=r"… \(27 nets\)$") as exc:
        extract_tf(_system(f"* chain\n{chain}R99 n25 0 1k\n.end"), ("typo", "0"), ("n0", "0"))
    shown = str(exc.value).split("known nets: ")[1].split(", … ")[0].split(", ")
    assert len(shown) == 20 and shown[:3] == ["0", "n0", "n1"]


def test_unknown_net_in_a_port_pair_object_raises():
    with pytest.raises(ValueError, match=r"output net 'outt'"):
        extract_tf(_system(RC), PortPair("outt", "0"), ("in", "0"))


def test_a_named_port_is_resolved_then_checked():
    ok = transfer_function(RC, "o", "i", ports={"o": ("out", "0"), "i": ("in", "0")})
    assert ok.tf_exact_expr == transfer_function(RC, ("out", "0"), ("in", "0")).tf_exact_expr
    with pytest.raises(ValueError, match=r"output net 'outt'"):
        transfer_function(RC, "o", "i", ports={"o": ("outt", "0"), "i": ("in", "0")})


def test_an_unknown_port_name_and_a_malformed_port_still_raise():
    system = _system(RC)
    with pytest.raises(KeyError, match=r"unknown named port 'nope'"):
        extract_tf(system, "nope", ("in", "0"))
    with pytest.raises(TypeError, match=r"port must be a name"):
        extract_tf(system, ("out", "0", "x"), ("in", "0"))


def test_unknown_injection_net_of_a_transimpedance_raises():
    with pytest.raises(ValueError, match=r"injection net 'ouy'"):
        transimpedance(_system(RC), ("out", "0"), ("ouy", "0"))


def test_unknown_net_of_a_driving_point_port_raises():
    deck = "* z\nVin in 0 dc 0 ac 1\nR1 in out 1k\nR2 out 0 1k\n.end"
    with pytest.raises(ValueError, match=r"port net 'outt'"):
        output_impedance(deck, ("outt", "0"))
    with pytest.raises(ValueError, match=r"port net 'inn'"):
        output_impedance(deck, ("out", "0"), zero_input=("inn", "0"))


def test_unknown_output_net_of_an_asymptotic_gain_raises():
    with pytest.raises(ValueError, match=r"output net 'outt'"):
        asymptotic_gain(_INV, ("outt", "0"), None, "M1", level=Fidelity.IDEAL)


# ------------------------------------------------------------------------
# LEAF-F05 — SymbolMint collision guard
# ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "deck",
    [
        "* bare first\nM1 a g 0 0 nmos\nXM1 b g 0 0 nmos\nR1 a 0 1k\nR2 b 0 1k\n.end",
        "* wrapped first\nXM1 b g 0 0 nmos\nM1 a g 0 0 nmos\nR1 a 0 1k\nR2 b 0 1k\n.end",
    ],
)
def test_m1_and_xm1_get_distinct_symbols_in_either_order(deck):
    ssir = small_signal_model(from_string(deck))
    m1, xm1 = ssir.symbols["M1"], ssir.symbols["XM1"]
    assert m1["gm"] != xm1["gm"] and m1["ro"] != xm1["ro"]
    # the bare device keeps the short label; the X-wrapped one carries its full ref
    assert (str(m1["gm"]), str(xm1["gm"])) == ("gm_m1", "gm_xm1")


def test_every_symbol_of_the_renamed_device_carries_the_same_label(caplog):
    """The rename is per REF, not per symbol: gm, ro (and every later symbol) of XM1 read ``…_xm1``,
    and the collision is reported once, naming both refs."""
    deck = "* two\nXM1 b g 0 0 nmos\nM1 a g 0 0 nmos\nR1 a 0 1k\nR2 b 0 1k\n.end"
    with caplog.at_level(logging.WARNING, logger="spicexplorer_netlist2tf.models"):
        ssir = small_signal_model(from_string(deck))
    assert {k: str(v) for k, v in ssir.symbols["XM1"].items()} == {"gm": "gm_xm1", "ro": "ro_xm1"}
    assert {k: str(v) for k, v in ssir.symbols["M1"].items()} == {"gm": "gm_m1", "ro": "ro_m1"}
    warned = [r.getMessage() for r in caplog.records if "SymbolMint" in r.getMessage()]
    assert len(warned) == 1 and "M1" in warned[0] and "XM1" in warned[0], warned


def test_distinct_labels_mint_as_before_and_do_not_warn(caplog):
    """No collision → the ``_label`` names are unchanged (X-wrappers still strip) and no warning."""
    deck = "* two\nM1 a g 0 0 nmos\nXM2 b g 0 0 nmos\nR1 a 0 1k\nR2 b 0 1k\n.end"
    with caplog.at_level(logging.WARNING, logger="spicexplorer_netlist2tf.models"):
        ssir = small_signal_model(from_string(deck))
    assert (str(ssir.symbols["M1"]["gm"]), str(ssir.symbols["XM2"]["gm"])) == ("gm_m1", "gm_m2")
    assert not [r for r in caplog.records if "SymbolMint" in r.getMessage()]


def test_a_mint_without_refs_renames_the_later_ref_and_stays_stable(caplog):
    """Without the up-front ``refs`` the first ref to mint keeps the label; a bare ``M1`` minting
    after ``XM1`` took ``m1`` would want ``m1`` again, so it steps to ``m1_2`` — never a shared
    symbol — and every later symbol of each ref keeps its first label."""
    mint = SymbolMint()
    with caplog.at_level(logging.WARNING, logger="spicexplorer_netlist2tf.models"):
        names = [
            str(mint.sym(base, ref))
            for base, ref in [
                ("gm", "XM1"),
                ("gm", "M1"),
                ("ro", "M1"),
                ("ro", "XM1"),
                ("gm", "M2"),
            ]
        ]
    assert names == ["gm_m1", "gm_m1_2", "ro_m1_2", "ro_m1", "gm_m2"]
    assert mint.names == frozenset(names)
    assert len([r for r in caplog.records if "SymbolMint" in r.getMessage()]) == 1


def test_a_mint_seeded_with_refs_is_order_independent():
    for refs in (["M1", "XM1"], ["XM1", "M1"]):
        mint = SymbolMint(refs)
        assert (str(mint.sym("gm", "XM1")), str(mint.sym("gm", "M1"))) == ("gm_xm1", "gm_m1")


def test_colliding_devices_stay_independent_in_the_tf():
    deck = "* two\nM1 a g 0 0 nmos\nXM1 b g 0 0 nmos\nR1 a 0 1k\nR2 b 0 1k\n.end"
    h = extract_tf(_system(deck), ("b", "0"), ("g", "0"))
    assert "gm_xm1" in str(h.expr) and "gm_m1" not in str(h.expr)


def test_loop_gain_probe_resolves_the_colliding_devices_own_symbol():
    """``loop_gain(..., probe="XM1")`` must probe XM1's gm, not the bare M1 that shares its label."""
    deck = (
        "* mirror\nXM1 d d 0 0 nmos\nM1 o d 0 0 nmos\n"
        "R1 vdd d 10k\nR2 vdd o 10k\nV1 vdd 0 dc 1\n.end"
    )
    t = loop_gain(deck, "XM1")
    assert "gm_xm1" in t.tf_exact_expr and "gm_m1" not in t.tf_exact_expr


def test_probe_resolution_is_case_insensitive_like_spice():
    deck = (
        "* mirror\nXM1 d d 0 0 nmos\nM1 o d 0 0 nmos\n"
        "R1 vdd d 10k\nR2 vdd o 10k\nV1 vdd 0 dc 1\n.end"
    )
    assert loop_gain(deck, "xm1").tf_exact_expr == loop_gain(deck, "XM1").tf_exact_expr


def test_asymptotic_gain_probe_resolves_the_colliding_devices_own_symbol():
    """The inverting amp's loop runs through XM1; an unrelated bare ``M1`` shares its label. A∞ is
    still −Rf/Rs and the loop gain carries XM1's gm (the ``_label`` rule alone probed M1)."""
    deck = _INV.replace("M1 out", "XM1 out").replace(".end", "M1 z ing 0 0 nmos\nRZ z 0 1k\n.end")
    res = asymptotic_gain(deck, ("out", "0"), None, "XM1", level=Fidelity.IDEAL)
    rs, rfb = sp.symbols("rs rfb")
    assert sp.simplify(res.as_sympy() - (-rfb / rs)) == 0
    assert "gm_xm1" in res.component_tfs["loop_gain"]


# ------------------------------------------------------------------------
# LEAF-F05 — L = 0 guard
# ------------------------------------------------------------------------
def test_zero_inductance_raises_instead_of_a_nan_tf():
    with pytest.raises(ValueError, match=r"L1"):
        small_signal_model(from_string("* l\nR1 in out 1k\nL1 out 0 0\n.end"))


@pytest.mark.parametrize("value", ["0.0", "0p", "{0}", "'0'", "{L0*0}"])
def test_every_spelling_of_a_zero_inductance_raises(value):
    with pytest.raises(ValueError, match=r"L1: zero-inductance element"):
        small_signal_model(from_string(f"* l\nR1 in out 1k\nL1 out 0 {value}\n.end"))


@pytest.mark.parametrize(
    ("value", "expected"), [("1n", sp.Rational(1, 10**9)), ("LX", sp.Symbol("lx"))]
)
def test_a_nonzero_or_symbolic_inductance_still_models(value, expected):
    ssir = small_signal_model(from_string(f"* l\nR1 in out 1k\nL1 out 0 {value}\n.end"))
    (ind,) = [p for p in ssir.primitives if isinstance(p, Inductor)]
    assert (ind.name, ind.value) == ("l@L1", expected)


def test_a_float_zero_inductance_from_the_json_front_end_raises():
    """``Circuit2TF.from_dict`` reads ``"0.0"`` as the exact ``0`` (L-PF-4), which the ``== 0``
    half of the guard catches. A hand-built ``Float(0.0)``, which sympy (≥ 1.13) no longer counts
    ``== 0``, is caught by the ``is_zero`` half."""
    data = from_string("* l\nR1 in out 1k\nL1 out 0 1n\n.end").to_dict()
    (l1,) = [d for d in data["devices"] if d["ref"].upper() == "L1"]
    l1["params"]["value"] = "0.0"
    ir = Circuit2TF.from_dict(data)
    params = next(d for d in ir.devices if d.ref.upper() == "L1").params
    assert params["value"] == 0 and not isinstance(params["value"], sp.Float)
    with pytest.raises(ValueError, match=r"L1: zero-inductance element"):
        small_signal_model(ir)
    params["value"] = sp.Float(0.0)
    with pytest.raises(ValueError, match=r"L1: zero-inductance element"):
        small_signal_model(ir)


# ------------------------------------------------------------------------
# LEAF-F05 — driving-point analyses short AC-bearing V sources
# ------------------------------------------------------------------------
def _divider_tb(spec: str) -> str:
    return f"* z\nVin in 0 {spec}\nR1 in out 1k\nR2 out 0 1k\n.end"


@pytest.mark.parametrize("spec", ["dc 1", "dc 0 ac 1"])
def test_output_impedance_is_the_same_for_a_dc_and_an_ac_source(spec):
    res = output_impedance(_divider_tb(spec), ("out", "0"))
    assert sp.sympify(res.tf_exact_expr) == 500


def test_input_impedance_at_the_stimulus_port_replaces_the_stimulus():
    """The source across the measured port is the one the test current replaces (Zin as the
    stimulus sees it) — shorting it would read the port as AC ground."""
    res = input_impedance(_divider_tb("dc 0 ac 1"), ("in", "0"))
    assert sp.sympify(res.tf_exact_expr) == 2000


def test_input_impedance_shorts_the_other_stimulus_of_a_differential_pair():
    deck = (
        "* diff\nVinp inp 0 dc 0 ac 0.5\nVinn inn 0 dc 0 ac -0.5\nR1 inp inn 1k\nR2 inn 0 1k\n.end"
    )
    res = input_impedance(deck, ("inp", "0"))
    assert sp.sympify(res.tf_exact_expr) == 1000


def test_input_impedance_of_a_floating_port_replaces_a_vcm_referenced_dm_pair():
    """analog-db's standard DM bench (ac_zin_diff): each half of the ±0.5 pair runs from one port
    net to vcm, which is AC ground. The floating test current replaces BOTH halves; shorting them
    put the whole port at AC ground."""
    deck = (
        "* zin dm\nVcm vcm 0 dc 0.9\nVinp vinp vcm dc 0 ac 0.5\nVinn vinn vcm dc 0 ac -0.5\n"
        "Rp vinp mid 10k\nRn vinn mid 10k\nRm mid 0 1meg\n.end"
    )
    res = input_impedance(deck, ("vinp", "vinn"))
    assert sp.sympify(res.tf_exact_expr) == 20000


def test_an_ac_source_across_a_floating_port_is_replaced():
    deck = "* z\nVx a b dc 0 ac 1\nR1 a 0 1k\nR2 b 0 1k\n.end"
    assert sp.sympify(input_impedance(deck, ("a", "b")).tf_exact_expr) == 2000


def test_a_dc_source_across_the_port_stays_a_short():
    """Only an AC stimulus is replaced by the test current; a DC source across the port is an AC
    short, as before (the port reads 0 Ω, not the 2 kΩ of the resistors behind it)."""
    deck = "* z\nVx a b dc 1\nR1 a 0 1k\nR2 b 0 1k\n.end"
    assert sp.sympify(input_impedance(deck, ("a", "b")).tf_exact_expr) == 0


def test_an_ac_source_from_the_port_to_a_live_net_is_shorted_not_dropped():
    """``Vs`` runs from the port net to ``b``, which is neither ground nor the other port row: it
    does not drive the port, so it is a short (R1 ∥ R2 = 500 Ω); dropping it read 1 kΩ."""
    deck = "* z\nR1 a 0 1k\nVs a b dc 0 ac 1\nR2 b 0 1k\n.end"
    assert sp.sympify(input_impedance(deck, ("a", "0")).tf_exact_expr) == 500


def _vsource_names(ssir) -> set[str]:  # noqa: ANN001
    return {p.name for p in ssir.primitives if isinstance(p, IndependentV)}


def test_drop_port_stimulus_removes_only_the_port_stimulus():
    deck = (
        "* two stimuli\nVin in 0 dc 0 ac 1\nVb b 0 dc 1\nR1 in out 1k\nR2 out b 1k\n"
        "Vt t 0 dc 0 ac 1\nR3 t out 1k\n.end"
    )
    ssir = small_signal_model(from_string(deck))
    before = _vsource_names(ssir)
    kept = _drop_port_stimulus(ssir, build_system(ssir), ("in", "0"))
    assert before - _vsource_names(kept) == {n for n in before if n.upper().endswith("VIN")}
    # the other AC source (Vt), the DC source (Vb) and every passive stay
    assert len(kept.primitives) == len(ssir.primitives) - 1
    assert _vsource_names(ssir) == before and len(before) == 3  # the input IR is not mutated


def test_a_symbolic_ac_stimulus_at_the_port_is_replaced():
    """``ac {VAC}`` is AC-bearing (unbound, or bound through ``subs``), so at its own port the test
    current replaces it — Zin reads the resistors behind the port, not a short."""
    deck = "* z\nVin in 0 dc 0 ac {VAC}\nR1 in out 1k\nR2 out 0 1k\n.end"
    assert sp.sympify(input_impedance(deck, ("in", "0")).tf_exact_expr) == 2000
    assert sp.sympify(input_impedance(deck, ("in", "0"), subs={"vac": 1}).tf_exact_expr) == 2000


# ------------------------------------------------------------------------
# TF-1 — disclose ball-park fills under a partial operating point
# ------------------------------------------------------------------------
CS = "* cs\nM1 out in 0 0 nmos\nRL out 0 RL\nCL out 0 CL\n.end"


def _cs_raw():
    return extract_tf(_system(CS), ("out", "0"), ("in", "0"))


def test_partial_operating_point_names_the_ball_park_fills():
    st = simplify_tf(_cs_raw(), "ideal", operating_point={"gm_m1": 1e-3, "ro_m1": 1e5})
    assert st.validation is not None and st.validation.notes is not None
    assert "cl" in st.validation.notes and "rl" in st.validation.notes
    assert "gm_m1" not in st.validation.notes


def test_complete_operating_point_carries_no_ball_park_note():
    op = {"gm_m1": 1e-3, "ro_m1": 1e5, "rl": 1e4, "cl": 1e-12}
    st = simplify_tf(_cs_raw(), "ideal", operating_point=op)
    assert st.validation is not None and st.validation.notes is None


def test_extra_operating_point_keys_do_not_count_as_fills():
    op = {"gm_m1": 1e-3, "ro_m1": 1e5, "rl": 1e4, "cl": 1e-12, "unused_param": 1.0}
    st = simplify_tf(_cs_raw(), "ideal", operating_point=op)
    assert st.validation is not None and st.validation.notes is None


def test_no_operating_point_keeps_the_whole_op_note():
    st = simplify_tf(_cs_raw(), "ideal")
    assert st.validation is not None
    assert st.validation.notes == "ball-park operating point (no defs supplied)"


def test_an_empty_operating_point_names_every_symbol_as_filled():
    """``{}`` is a supplied (if empty) operating point, not "none": every symbol is a fill."""
    st = simplify_tf(_cs_raw(), "ideal", operating_point={})
    assert st.validation is not None
    assert st.validation.notes == (
        "ball-park values filled for cl, gm_m1, rl, ro_m1 (not in the supplied operating point)"
    )


def test_no_validation_means_no_note():
    st = simplify_tf(_cs_raw(), "ideal", operating_point={"gm_m1": 1e-3}, validate=False)
    assert st.validation is None


# ------------------------------------------------------------------------
# TF-2 — NaN-aware DOMINANCE arbiter
# ------------------------------------------------------------------------
SF = "* sf\nM1 vdd in out 0 nmos\nRS out 0 RS\n.end"


def test_nan_magnitude_is_rejected_not_waved_through():
    """Source follower: the gain denominator is ``gm·ro·rs + ro + rs``. With ``ro`` NaN every
    comparison is False, so the step came back NO_OP instead of 'cannot arbitrate'."""
    raw = extract_tf(_system(SF), ("out", "0"), ("in", "0"))
    st = simplify_tf(
        raw,
        [transconductance_dominates("M1")],
        validate=False,
        operating_point={"gm_m1": 1e-3, "ro_m1": math.nan, "rs": 1e4},
    )
    (rec,) = st.ledger
    assert rec.status == "REJECTED_NUMERICS"
    assert "nan" in rec.description.lower()


@pytest.mark.parametrize("nan_name", ["a_nan", "z_nan"])  # sorts before / after the big sibling
def test_nan_sibling_is_rejected_whatever_its_position(nan_name):
    """``max`` over NaNs is order-dependent: a NaN listed first hid a sibling that contradicts
    the declared dominance."""
    gm, big, unbound = sp.symbols(f"gm_m1 m_big {nan_name}", positive=True)
    expr = 1 / (gm + big + unbound)
    a = Assumption(id="gm_dominates:m1", kind=DOMINANCE, payload={"dominant": "gm_m1"})
    _, rec = _apply_dominance(expr, a, {"gm_m1": 1e-3, "m_big": 1.0}, 100.0, 0)
    assert rec.status == "REJECTED_NUMERICS"


_GM, _SMALL, _X, _Y = sp.symbols("gm_m1 m_small x_u y_u", positive=True)
_A_GM = Assumption(id="gm_dominates:m1", kind=DOMINANCE, payload={"dominant": "gm_m1"})


def test_a_nan_dominant_term_is_rejected_and_the_expression_kept():
    """NaN on the DOMINANT side: ``other > NaN`` is False, so the old guard never fired."""
    expr = 1 / (_GM + _SMALL)
    new, rec = _apply_dominance(expr, _A_GM, {"gm_m1": math.nan, "m_small": 1e-9}, 100.0, 0)
    assert new == expr
    assert (rec.status, rec.validated, rec.dropped_terms) == ("REJECTED_NUMERICS", False, [])
    assert "cannot arbitrate gm_m1" in rec.description


def test_finite_dominance_still_applies():
    new, rec = _apply_dominance(
        1 / (_GM + _SMALL), _A_GM, {"gm_m1": 1e-3, "m_small": 1e-9}, 100.0, 0
    )
    assert (new, rec.status, rec.dropped_terms) == (1 / _GM, "APPLIED", ["m_small"])


def test_finite_contradiction_is_still_reported_as_a_contradiction():
    _, rec = _apply_dominance(1 / (_GM + _SMALL), _A_GM, {"gm_m1": 1e-3, "m_small": 1.0}, 100.0, 0)
    assert rec.status == "REJECTED_NUMERICS" and "not numerically largest" in rec.description


def test_a_nan_in_a_sum_without_the_dominant_symbol_does_not_block_the_step():
    """Only sums that contain the dominant symbol are checked: a NaN in any other sum is ignored."""
    expr = (_X + _Y) / (_GM + _SMALL)
    new, rec = _apply_dominance(
        expr, _A_GM, {"gm_m1": 1e-3, "m_small": 1e-9, "x_u": math.nan, "y_u": 1.0}, 100.0, 0
    )
    assert (new, rec.status) == ((_X + _Y) / _GM, "APPLIED")


# ------------------------------------------------------------------------
# TF-3 — DC pole
# ------------------------------------------------------------------------
def test_dc_pole_evaluates_to_infinity():
    assert complex_value_at(1 / S, {}) == complex(math.inf)
    assert complex_value_at(-1 / (S * sp.Symbol("c")), {"c": 1e-12}) == complex(math.inf)


def test_finite_values_are_unchanged():
    assert complex_value_at(1 / (1 + S), {}) == 1
    assert abs(complex_value_at(1 / S, {}, 1.0) - 1 / (2j * math.pi)) < 1e-12


def test_higher_order_dc_poles_are_infinite_too():
    assert complex_value_at(1 / S**2, {}) == complex(math.inf)
    assert complex_value_at((1 + S) / (S * (2 + S)), {}) == complex(math.inf)


def test_a_nan_everywhere_stays_nan_not_infinite():
    """``nan.is_finite`` is None, not False: an undefined value must not be reported as a pole."""
    val = complex_value_at(1 + S * sp.nan, {})
    assert cmath.isnan(val.real) and not math.isinf(val.real)


def test_a_finite_dc_fallback_is_unchanged():
    """Pre-existing fallback kept by the DC-pole fix: NaN at the requested frequency, finite at DC
    → the DC value (not infinity)."""
    assert complex_value_at(sp.Piecewise((sp.nan, sp.Ne(S, 0)), (3, True)), {}, 1.0) == 3


# ------------------------------------------------------------------------
# TF-4 — dropped ac/dc tokens warn; 'inf' ingests
# ------------------------------------------------------------------------
def test_unparseable_ac_token_warns(caplog):
    with caplog.at_level(logging.WARNING, logger="spicexplorer_netlist2tf.ingest"):
        ir = from_string("* v\nVin in 0 dc 0 ac 1..0\nR1 in 0 1k\n.end")
    assert "ac" not in next(d for d in ir.devices if d.ref.upper() == "VIN").params
    assert any("VIN" in r.getMessage().upper() and "1..0" in r.getMessage() for r in caplog.records)


def test_unparseable_bare_dc_token_warns(caplog):
    with caplog.at_level(logging.WARNING, logger="spicexplorer_netlist2tf.ingest"):
        from_string("* i\nI1 in 0 1..0\nR1 in 0 1k\n.end")
    assert any("I1" in r.getMessage().upper() and "1..0" in r.getMessage() for r in caplog.records)


@pytest.mark.parametrize("spec", ["pulse(0 1 0 1n 1n 5n 10n)", "SIN(0.9 0.1 1k)", "pwl (0 0 1u 1)"])
def test_a_transient_only_source_does_not_warn(caplog, spec):
    """A transient function has no small-signal value and its DC is irrelevant here, so skipping it
    is not a dropped token (the bare-dc warning fired on every pulse/sin bench in the corpus)."""
    with caplog.at_level(logging.WARNING, logger="spicexplorer_netlist2tf.ingest"):
        ir = from_string(f"* tran\nV1 a 0 {spec}\nR1 a 0 1k\n.end")
        from_string("* i\nI1 in 0 1..0\nR1 in 0 1k\n.end")
    assert "dc" not in next(d for d in ir.devices if d.ref.upper() == "V1").params
    msgs = [r.getMessage() for r in caplog.records]
    assert not any("V1" in m.upper() for m in msgs), msgs
    assert any("I1" in m.upper() and "1..0" in m for m in msgs)


def _ingest_warnings(caplog, deck: str):  # noqa: ANN001
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="spicexplorer_netlist2tf.ingest"):
        ir = from_string(deck)
    return ir, [r.getMessage() for r in caplog.records]


@pytest.mark.parametrize(
    "spec",
    [
        "EXP(0 1 1n 1n 2n 3n)",
        "sffm(0 1 1k 5 1k)",
        "AM(1 0 1k 10)",
        "trnoise(1n 0.5n 0 0)",
        "trrandom(1 10n 0 1)",
        "Pulse (0 1 0 1n 1n 5n 10n)",
        "sin (0 1 1k)",
        "PWL(0 0 1u 1)",
    ],
)
def test_every_transient_function_is_recognised(caplog, spec):
    ir, msgs = _ingest_warnings(caplog, f"* tran\nV1 a 0 {spec}\nR1 a 0 1k\n.end")
    assert "dc" not in next(d for d in ir.devices if d.ref.upper() == "V1").params
    assert not msgs, msgs


def test_a_bare_dc_value_before_a_transient_function_is_still_read(caplog):
    """``V1 a 0 0.9 sin(…)`` is DC 0.9 plus a transient: only a spec that OPENS with the function
    has no DC token."""
    ir, msgs = _ingest_warnings(caplog, "* v\nV1 a 0 0.9 sin(0 1 1k)\nR1 a 0 1k\n.end")
    assert next(d for d in ir.devices if d.ref.upper() == "V1").params["dc"] == sp.Rational(9, 10)
    assert not msgs, msgs


def test_a_keyword_spec_with_a_transient_tail_parses_silently(caplog):
    ir, msgs = _ingest_warnings(caplog, "* v\nV1 a 0 dc 0 ac 1 sin(0 1 1k)\nR1 a 0 1k\n.end")
    assert next(d for d in ir.devices if d.ref.upper() == "V1").params == {"dc": 0, "ac": 1}
    assert not msgs, msgs


def test_unparseable_dc_keyword_token_warns(caplog):
    ir, msgs = _ingest_warnings(caplog, "* v\nV1 a 0 dc 1..0 ac 1\nR1 a 0 1k\n.end")
    assert next(d for d in ir.devices if d.ref.upper() == "V1").params == {"ac": 1}
    assert any("V1" in m.upper() and "dc value '1..0'" in m for m in msgs), msgs


@pytest.mark.parametrize("spec", ["dc 0 ac 1", "IBIAS", "0", "dc {VCM} ac 'VAC'"])
def test_a_parseable_spec_does_not_warn(caplog, spec):
    _, msgs = _ingest_warnings(caplog, f"* v\nV1 a 0 {spec}\nR1 a 0 1k\n.end")
    assert not msgs, msgs


@pytest.mark.parametrize("token", ["INF", "Inf", "'inf'", "{inf}", " inf "])
def test_every_spelling_of_infinity_ingests(token):
    assert sympify_value(token) == sp.oo


def test_inf_ingests_as_sympy_infinity():
    assert sympify_value("inf") == sp.oo
    assert sympify_value(float("inf")) == sp.oo
    assert sympify_value(float("-inf")) == -sp.oo
    ir = from_string("* open\nR1 in out inf\nR2 out 0 1k\n.end")
    assert next(d for d in ir.devices if d.ref.upper() == "R1").params["value"] == sp.oo
