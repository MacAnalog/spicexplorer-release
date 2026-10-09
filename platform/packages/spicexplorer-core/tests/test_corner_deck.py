"""Corner emission is ONE policy (`plan_corner`) with two appliers.

These lock the deck-TEXT applier (`apply_corner_to_deck`) used by block harnesses that
build their own deck text: quote-tolerant lib swapping, authoritative temperature,
`.options` extras (Monte Carlo seed), idempotency, and in-place `.param` rewriting.
"""

from __future__ import annotations

import re

import pytest
from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride
from spicexplorer_core.spice_engine.deck_prep import (
    apply_corner_to_deck,
    corner_include_strip_pattern,
    corner_lib_strip_pattern,
    plan_corner,
)

DECK = """* pam4 driver bench
.param vcc=4.0
.lib "cornerRES.lib" res_typ
.lib "cornerCAP.lib" cap_typ
.lib "cornerHBT.lib" hbt_typ
.temp 27
.options gmin=1e-12 reltol=1e-3
X1 outp outn dut
.control
op
.endc
.end
"""

SS = Corner(
    name="ss_hot",
    model_includes=[
        ModelInclude("cornerRES.lib", "res_wcs"),
        ModelInclude("cornerCAP.lib", "cap_wcs"),
        ModelInclude("cornerHBT.lib", "hbt_wcs"),
    ],
    temp=125.0,
    supplies=[SupplyOverride("vcc", 3.8)],
    options={"seed": 7},
)


def _lines(deck: str) -> list[str]:
    return [ln.strip() for ln in deck.splitlines()]


def test_quoted_lib_lines_are_swapped_not_duplicated():
    """A deck that QUOTES its lib paths must end up with the corner's section only.

    The pre-existing strip regex used a bare ``\\S*`` prefix, which cannot span the closing
    quote — so a quoted deck kept ``res_typ`` AND gained ``res_wcs``: two sections of one
    lib loaded at once, silently mixing corners.
    """
    out = _lines(apply_corner_to_deck(DECK, SS))
    for lib, keep, drop in (
        ("cornerRES.lib", "res_wcs", "res_typ"),
        ("cornerCAP.lib", "cap_wcs", "cap_typ"),
        ("cornerHBT.lib", "hbt_wcs", "hbt_typ"),
    ):
        assert sum(1 for ln in out if lib in ln) == 1, f"{lib} appears more than once"
        assert f".lib {lib} {keep}" in out
        assert not any(drop in ln for ln in out)


def test_temp_card_stripped_and_option_authoritative():
    """`.temp` OUTRANKS `.options temp=` in ngspice, so a hardcoded card must go."""
    out = _lines(apply_corner_to_deck(DECK, SS))
    assert not any(ln.lower().startswith(".temp ") for ln in out)
    assert ".options temp=125.0" in out
    assert ".options gmin=1e-12 reltol=1e-3" in out  # combined line keeps its siblings


def test_extra_options_and_directive_placement():
    """Monte Carlo seed lands as `.options seed=`, inside the netlist section."""
    out = _lines(apply_corner_to_deck(DECK, SS))
    assert ".options seed=7" in out
    assert out.index(".options seed=7") < out.index(".control")


def test_supply_override_rewrites_in_place():
    out = _lines(apply_corner_to_deck(DECK, SS))
    assert ".param vcc=3.8" in out
    assert ".param vcc=4.0" not in out
    assert out.index(".param vcc=3.8") == 1  # kept its original position


def test_reapply_is_idempotent():
    once = apply_corner_to_deck(DECK, SS)
    assert apply_corner_to_deck(once, SS) == once


def test_two_sections_of_one_lib_both_survive():
    """All strips run before any add (BUG-B11), so a sibling section isn't collapsed."""
    c = Corner(
        name="two",
        model_includes=[
            ModelInclude("cornerHBT.lib", "hbt_typ"),
            ModelInclude("cornerHBT.lib", "hbt_typ_mismatch"),
        ],
    )
    out = _lines(apply_corner_to_deck(DECK, c))
    assert ".lib cornerHBT.lib hbt_typ" in out
    assert ".lib cornerHBT.lib hbt_typ_mismatch" in out


def test_multi_assignment_param_raises_rather_than_guessing():
    deck = "* t\n.param vcc=4.0 vcasc=3.3\n.end\n"
    with pytest.raises(ValueError, match="multi-assignment"):
        apply_corner_to_deck(deck, SS)


def test_undeclared_param_is_appended_with_a_warning(caplog):
    deck = '* t\n.lib "cornerHBT.lib" hbt_typ\n.end\n'
    with caplog.at_level("WARNING"):
        out = _lines(apply_corner_to_deck(deck, SS))
    assert ".param vcc=3.8" in out
    assert "NOT a declared .param" in caplog.text


def test_model_lib_root_prefixes_every_include():
    out = _lines(apply_corner_to_deck(DECK, SS, model_lib_root="/pdk/models"))
    assert ".lib /pdk/models/cornerHBT.lib hbt_wcs" in out
    assert not any(ln.startswith(".lib cornerHBT.lib") for ln in out)


def test_plan_is_pure_and_ordered():
    plan = plan_corner(SS)
    assert plan.instructions[-1] == ".options seed=7"
    assert plan.instructions[-2] == ".options temp=125.0"
    assert plan.params == [("vcc", 3.8)]
    assert plan_corner(SS) == plan  # no hidden state


# ── OPT-F9: the lib strip takes a sectionless `.lib` and is anchored on a path separator ──


def test_sectionless_lib_line_is_replaced_not_kept_alongside():
    """A deck selecting a lib with a bare `.lib <file>` (no section token) must have that line
    replaced by the corner's selection — the strip used to demand a trailing section, so the
    bare line survived and the corner's `.lib` was added ALONGSIDE it."""
    deck = "* t\n.lib x.lib\n.end\n"
    corner = Corner(name="ss", model_includes=[ModelInclude("x.lib", "ss")])
    once = apply_corner_to_deck(deck, corner)
    out = _lines(once)
    assert [ln for ln in out if "x.lib" in ln] == [".lib x.lib ss"]
    assert apply_corner_to_deck(once, corner) == once


def test_lib_strip_is_anchored_on_a_path_separator():
    """`models.lib` names that file under any directory, never a longer basename that merely
    ENDS in it (`nmos_models.lib`) — that is another library, and stripping it would drop its
    device models from the deck."""
    deck = (
        "* t\n"
        ".lib nmos_models.lib tt\n"
        ".lib /pdk/models.lib tt\n"
        '.lib "/pdk/v2/models.lib" tt_hv\n'
        ".end\n"
    )
    corner = Corner(name="ss", model_includes=[ModelInclude("models.lib", "ss")])
    out = _lines(apply_corner_to_deck(deck, corner))
    assert ".lib nmos_models.lib tt" in out
    assert not any("/pdk/" in ln for ln in out)
    assert ".lib models.lib ss" in out


# ── DATA-F3: a sectionless model include is an `.include` (gf180mcu `design.ngspice`) ──

GF_DECK = """* gf180-style bench
.include design.ngspice
.lib sm141064.ngspice noise_corner
.lib sm141064.ngspice nfet_03v3_t
.lib sm141064.ngspice pfet_03v3_t
.lib sm141064.ngspice fets_mm
X1 out inp inn dut
.control
op
.endc
.end
"""


def _gf_corner(tag: str) -> Corner:
    return Corner(
        name=f"gf180mcu_{tag}",
        model_includes=[
            ModelInclude("design.ngspice"),
            ModelInclude("sm141064.ngspice", "noise_corner"),
            ModelInclude("sm141064.ngspice", f"nfet_03v3_{tag}"),
            ModelInclude("sm141064.ngspice", f"pfet_03v3_{tag}"),
            ModelInclude("sm141064.ngspice", "fets_mm"),
        ],
    )


def test_sectionless_include_plans_an_include_card():
    plan = plan_corner(_gf_corner("s"))
    assert plan.instructions[:5] == [
        ".include design.ngspice",
        ".lib sm141064.ngspice noise_corner",
        ".lib sm141064.ngspice nfet_03v3_s",
        ".lib sm141064.ngspice pfet_03v3_s",
        ".lib sm141064.ngspice fets_mm",
    ]
    assert not any("None" in ln for ln in plan.instructions)


def test_sectionless_include_replaces_the_decks_include():
    once = apply_corner_to_deck(GF_DECK, _gf_corner("s"))
    out = _lines(once)
    assert out.count(".include design.ngspice") == 1
    assert ".lib sm141064.ngspice nfet_03v3_s" in out
    assert not any(ln.endswith("_03v3_t") for ln in out)
    assert apply_corner_to_deck(once, _gf_corner("s")) == once


def test_sectionless_include_strips_inc_short_form_and_takes_model_lib_root():
    deck = GF_DECK.replace(".include design.ngspice", '.inc "design.ngspice"')
    out = _lines(apply_corner_to_deck(deck, _gf_corner("f"), model_lib_root="/pdk/models"))
    assert [ln for ln in out if "design.ngspice" in ln] == [".include /pdk/models/design.ngspice"]


# ── the strip patterns themselves, line by line (the appliers compile them IGNORECASE + match) ──


def _strips(pattern: str, line: str) -> bool:
    return re.match(pattern, line, re.IGNORECASE) is not None


@pytest.mark.parametrize("lib_file", ["models.lib", "/any/dir/models.lib"])
@pytest.mark.parametrize(
    "line, stripped",
    [
        pytest.param(".lib models.lib tt", True, id="bare"),
        pytest.param(".lib models.lib", True, id="sectionless"),
        pytest.param("  .LIB models.lib tt", True, id="indented-uppercase"),
        pytest.param(".lib /pdk/v1/models.lib tt", True, id="posix-path"),
        pytest.param(".lib ../models.lib tt", True, id="relative-path"),
        pytest.param('.lib "/pdk/models.lib" tt', True, id="double-quoted"),
        pytest.param(".lib 'models.lib' tt", True, id="single-quoted"),
        pytest.param(".lib C:\\pdk\\models.lib tt", True, id="windows-path"),
        pytest.param(".lib models.lib tt $ trailing comment", True, id="comment"),
        pytest.param(".lib nmos_models.lib tt", False, id="longer-basename-ending-in-it"),
        pytest.param(".lib /pdk/nmos_models.lib tt", False, id="longer-basename-behind-a-path"),
        pytest.param(
            ".lib C:\\pdk\\nmos_models.lib tt", False, id="longer-basename-behind-a-windows-path"
        ),
        pytest.param(".lib models.lib.bak tt", False, id="longer-basename-starting-with-it"),
        pytest.param(".lib /pdk/models.library", False, id="suffix-extended-sectionless"),
        pytest.param(".include models.lib", False, id="an-include-is-not-a-lib-selection"),
        pytest.param("* .lib models.lib tt", False, id="commented-out"),
    ],
)
def test_lib_strip_pattern_line_table(lib_file, line, stripped):
    assert _strips(corner_lib_strip_pattern(lib_file), line) is stripped


@pytest.mark.parametrize(
    "line, stripped",
    [
        pytest.param(".include design.ngspice", True, id="include"),
        pytest.param(".inc design.ngspice", True, id="inc-short-form"),
        pytest.param("  .INCLUDE design.ngspice", True, id="indented-uppercase"),
        pytest.param('.include "/pdk/gf180/design.ngspice"', True, id="quoted-path"),
        pytest.param(".include ../models/design.ngspice", True, id="relative-path"),
        pytest.param(".include my_design.ngspice", False, id="longer-basename-ending-in-it"),
        pytest.param(".include /pdk/my_design.ngspice", False, id="longer-basename-behind-a-path"),
        pytest.param(".include design.ngspice.orig", False, id="longer-basename-starting-with-it"),
        pytest.param(".lib design.ngspice tt", False, id="a-lib-selection-is-not-an-include"),
    ],
)
def test_include_strip_pattern_line_table(line, stripped):
    assert _strips(corner_include_strip_pattern("design.ngspice"), line) is stripped


def test_one_file_as_include_and_as_lib_is_stripped_in_both_forms_exactly_once():
    """The strip set is keyed on (sectioned?, basename): a file pulled in whole AND selected by
    section needs BOTH its `.include` and its `.lib` stripped, and each exactly once however
    many sections of it the corner selects (the plan's "stripped EXACTLY ONCE" promise)."""
    corner = Corner(
        name="mix",
        model_includes=[
            ModelInclude("x.lib"),
            ModelInclude("x.lib", "tt"),
            ModelInclude("/pdk/x.lib", "mm"),
        ],
    )
    plan = plan_corner(corner)
    assert plan.strips[:-2] == [
        corner_include_strip_pattern("x.lib"),
        corner_lib_strip_pattern("x.lib"),
    ]
    deck = "* t\n.include x.lib\n.lib x.lib ss\n.lib x.lib mm_off\nX1 a b dut\n.end\n"
    out = _lines(apply_corner_to_deck(deck, corner))
    assert [ln for ln in out if "x.lib" in ln] == [
        ".include x.lib",
        ".lib x.lib tt",
        ".lib /pdk/x.lib mm",
    ]


def test_a_blank_section_is_treated_as_no_section():
    """`section=""` (a blank value that did not come through the desugar) is sectionless too:
    an `.include` card that replaces the deck's `.include`, never `.lib <file> ` with a blank."""
    corner = Corner(name="blank", model_includes=[ModelInclude("design.ngspice", "")])
    plan = plan_corner(corner)
    assert plan.instructions[0] == ".include design.ngspice"
    assert plan.strips[0] == corner_include_strip_pattern("design.ngspice")
    out = _lines(apply_corner_to_deck(GF_DECK, corner))
    assert [ln for ln in out if "design.ngspice" in ln] == [".include design.ngspice"]
