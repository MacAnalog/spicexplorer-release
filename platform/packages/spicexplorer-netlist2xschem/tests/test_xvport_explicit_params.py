"""Every parameter the device map names is written EXPLICITLY (platform#241).

`cdfUpdateInstParam` stores only what differs from the master's CDF default, so a device
sized at its default carried no instance property at all: 72 of 302 MOS instances in one
ported library had no `w` whatever, and a read-back that asks the CDF for the *effective*
value prints the right number over a width the port never wrote — a lost sizing and a correct
port read back IDENTICAL.

Fixture-only, like every Virtuoso-side test here: the assertions are over the generated `.il`
text and the emit result. Nothing loads the SKILL into a CIW (no daemon on this host), so the
`dbFindProp`/`dbReplaceProp` pass is proven to be EMITTED, in the right place, and not proven
to behave as intended against a live master.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_netlist2xschem.sch_parser import parse_sch
from spicexplorer_netlist2xschem.virtuoso_export import emit_schematic_il, load_device_map
from spicexplorer_netlist2xschem.virtuoso_export.cli import main
from spicexplorer_netlist2xschem.virtuoso_export.symlib import symlib_for_source

FIXTURES = Path(__file__).parent / "fixtures" / "xvport"
TGATE = FIXTURES / "transmission_gate_pair.sch"
_SCH_SKEL = "v {xschem version=3.4.5 file_version=1.2\n}\nG {}\nK {}\nV {}\nS {}\nE {}\n"


def _emit(name: str = "transmission_gate_pair.sch", *, text: str | None = None):
    src = FIXTURES / name
    sch = parse_sch(text if text is not None else src.read_text(encoding="utf-8"))
    return emit_schematic_il(
        sch, lib="LIBX", cell="tgate", devmap=load_device_map(), symlib=symlib_for_source(src)
    )


# --- the SKILL the emitter writes ------------------------------------------------------


def test_the_cdf_setter_is_followed_by_an_explicit_property_write():
    il = _emit().il
    assert "cdfUpdateInstParam(inst)" in il
    fill = "foreach(pair pairs\n          unless(dbFindProp(inst car(pair))\n"
    assert fill in il, "no explicit instance-property pass after the CDF setter"
    # ORDER matters: the fill exists to catch what cdfUpdateInstParam declined to store.
    assert il.index(fill) > il.index("cdfUpdateInstParam(inst)")


def test_the_explicit_write_only_fills_what_the_cdf_setter_left_absent():
    """`unless(dbFindProp …)`: a value the CDF callbacks normalised (the ``w`` → ``wf``
    derivation) is the one the database must keep — the fill never overwrites it."""
    il = _emit().il
    assert "unless(dbFindProp(inst car(pair))" in il
    assert 'dbReplaceProp(inst car(pair) "string" cadr(pair))' in il


def test_a_master_without_cdf_still_gets_every_parameter_as_a_property():
    """The no-CDF branch was already explicit; keep it that way (no regression)."""
    il = _emit().il
    assert 'foreach(pair pairs dbReplaceProp(inst car(pair) "string" cadr(pair)))' in il


def test_every_mapped_value_is_handed_to_the_setter_whatever_it_is():
    """The emitter never filters by value — including a width that equals a CDF default."""
    il = _emit().il
    assert 'xvSetParams(cv "M1" list(list("fingers" "1") list("l" "0.13u") ' in il
    assert 'list("w" "0.15u")' in il


# --- the per-cell summary --------------------------------------------------------------


def test_the_summary_counts_every_explicit_parameter():
    result = _emit()
    written = sum(
        line.count('list("') for line in result.il.splitlines() if "xvSetParams(cv " in line
    )
    assert result.params_explicit == written == 8
    assert result.params_omitted == []
    assert result.param_summary() == "8 params explicit"


def test_an_omitted_parameter_is_named_with_the_reason_it_was_omitted():
    result = _emit("mos_fingered.sch")
    assert result.params_explicit == 7
    assert len(result.params_omitted) == 1
    (omitted,) = result.params_omitted
    assert omitted.startswith("M2.w: cannot derive per-finger w")
    assert result.param_summary().startswith(
        "7 params explicit, 1 omitted (cannot derive per-finger w"
    )
    assert result.param_summary().endswith(": M2.w)")


def test_a_parameter_the_sheet_never_sets_is_reported_as_coming_from_the_default():
    """ "N explicit, M from the default" is the row the read-back gate wants (#241)."""
    result = _emit(
        text=_SCH_SKEL + "C {sg13g2_pr/sg13_lv_nmos.sym} 0 0 0 0 {name=M1 l=0.13u ng=1 m=1}\n"
    )
    assert result.params_explicit == 3  # l, fingers, simM — the map also names w
    assert result.params_omitted == ["M1.w: the sheet sets no w"]
    assert result.param_summary() == "3 params explicit, 1 omitted (the sheet sets no w: M1.w)"


def test_the_same_reason_on_many_instances_stays_one_readable_group():
    """A 300-instance port omits the same parameter 300 times; the line must stay readable."""
    result = _emit("amp_001_5t.sch")
    assert len(result.params_omitted) == 6
    assert result.params_omitted[0] == "M1.fingers: the sheet sets no ng"
    assert result.param_summary() == (
        "18 params explicit, 6 omitted (the sheet sets no ng: M1.fingers, M2.fingers, "
        "M3.fingers, …)"
    )


def test_an_unmapped_local_master_reports_its_untransferred_parameters():
    """No rule names a CDF parameter for these, so they cannot be written — say which."""
    sch = parse_sch(_SCH_SKEL + "C {transmission_gate_pair.sym} 0 0 0 0 {name=x1 gain=2}\n")
    result = emit_schematic_il(
        sch,
        lib="LIBX",
        cell="t",
        devmap=load_device_map(),
        symlib=symlib_for_source(TGATE),
        local_cells={"transmission_gate_pair"},
    )
    assert result.params_omitted == [
        "x1.gain: unmapped local master — no rule names a CDF parameter for it"
    ]
    assert result.params_explicit == 0


# --- where a caller reads it -----------------------------------------------------------


def test_the_il_header_states_the_parameter_provenance():
    assert "; params: 8 params explicit\n" in _emit().il


def test_the_cli_prints_a_per_cell_summary_line(tmp_path, capsys):
    rc = main(
        ["sch2cv", str(TGATE), "--lib", "LIBX", "--cell", "tgate", "-o", str(tmp_path / "t.il")]
    )
    out = capsys.readouterr().out
    assert "xvport: params LIBX/tgate: 8 params explicit" in out
    assert rc == 0


@pytest.mark.parametrize("fixture", ["transmission_gate_pair.sch", "mos_fingered.sch"])
def test_the_summary_is_deterministic(fixture):
    assert _emit(fixture).param_summary() == _emit(fixture).param_summary()
