"""CLI smoke tests — generation works without xschem; --render degrades gracefully on host."""

import json
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import ANNOTATION_SCHEMA, xschem_available
from spicexplorer_netlist2xschem.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_writes_sch(tmp_path, capsys):
    out = tmp_path / "out.sch"
    rc = main([str(FIXTURES / "mixed_devices.spice"), "-o", str(out)])
    assert rc == 0
    assert out.is_file()
    text = out.read_text()
    assert text.startswith("v {xschem version=")
    # Params are suppressed by default: devices use the clean no-params symbol twins.
    assert "devices/sg13_lv_nmos_np.sym" in text
    assert "sg13g2_pr/sg13_lv_nmos.sym" not in text
    assert "wrote" in capsys.readouterr().out


def test_cli_show_params_uses_full_symbol(tmp_path):
    out = tmp_path / "out.sch"
    assert main([str(FIXTURES / "mixed_devices.spice"), "-o", str(out), "--show-params"]) == 0
    text = out.read_text()
    assert "sg13g2_pr/sg13_lv_nmos.sym" in text  # --show-params keeps the param-drawing symbol
    assert "_np.sym" not in text


def test_cli_default_output_path(tmp_path):
    netlist = tmp_path / "tiny.spice"
    netlist.write_text("* tiny\nXM1 out in 0 0 sg13_lv_nmos w=1u l=0.13u ng=1 m=1\n.end\n")
    rc = main([str(netlist)])
    assert rc == 0
    assert (tmp_path / "tiny.sch").is_file()


def test_cli_missing_file_errors(tmp_path):
    assert main([str(tmp_path / "nope.spice")]) == 2


def test_cli_render_without_xschem_is_graceful(tmp_path, capsys):
    out = tmp_path / "out.sch"
    rc = main([str(FIXTURES / "mixed_devices.spice"), "-o", str(out), "--render", "png"])
    assert rc == 0  # never fails just because xschem is absent
    assert out.is_file()
    if not xschem_available():
        assert "skipped image render" in capsys.readouterr().err


def test_cli_subckt_descent(tmp_path):
    out = tmp_path / "ota5t.sch"
    rc = main([str(FIXTURES / "ota-5t_tb-ac.spice"), "--into", "xota", "-o", str(out)])
    assert rc == 0
    # 13 device instances inside the subckt
    assert out.read_text().count("spiceprefix=X") == 13


def test_the_topology_placer_is_reachable_from_the_command_line(tmp_path, capsys):
    """It was implemented and had no way in: the CLI constructed the default and nothing else, so
    a 20-device amp came out in ONE row 5300 units wide with no flag to change it (issue #159)."""
    from spicexplorer_netlist2xschem.cli import PLACERS, main
    from spicexplorer_netlist2xschem.placement import TopologyPlacer
    from spicexplorer_netlist2xschem.sch_parser import parse_sch

    assert PLACERS["topology"] is TopologyPlacer

    # a mirror bank: every device on ONE level, which is the shape that collapses into a single
    # wide row under the default placer — the reported case.
    net = tmp_path / "bank.spice"
    net.write_text(
        "* bank\n"
        + "".join(f"M{i} o{i} vb avdd avdd pmos w=4u l=0.15u\n" for i in range(1, 9))
        + ".end\n"
    )

    def layout(placer: str) -> list[tuple[float, float]]:
        out = tmp_path / f"{placer}.sch"
        assert main([str(net), "-o", str(out), "--pdk", "", "--placer", placer]) == 0
        comps = parse_sch(out.read_text()).components
        return sorted((c.x, c.y) for c in comps if "mos4" in c.symref)

    phased, topology, grid = layout("phased"), layout("topology"), layout("grid")
    assert len(phased) == len(topology) == len(grid) == 8  # every placer placed every device
    assert topology != phased, "--placer topology changed nothing: the flag is not threaded"
    assert grid != phased


def test_a_rail_is_drawn_for_the_analog_supply_names(tmp_path):
    """The same sheets, before: `avdd`/`agnd` were not classified, so no rail was drawn at all."""
    from spicexplorer_netlist2xschem.cli import main

    net = tmp_path / "c.spice"
    net.write_text(
        "* c\nM1 out in agnd agnd nmos w=2u l=0.15u\nM2 out in avdd avdd pmos w=4u l=0.15u\n.end\n"
    )
    out = tmp_path / "c.sch"
    assert main([str(net), "-o", str(out), "--pdk", ""]) == 0
    text = out.read_text()
    assert "lab=avdd" in text and "lab=agnd" in text
    assert any(ln.startswith("N ") for ln in text.splitlines())  # wires, i.e. rails


# --- #203: a sheet of record must not be drawn with another foundry's symbols ------------

_KIT_NETLIST = """\
* an 8-bit SAR comparator core, licensed-kit masters
.subckt cmp di1 di2 von vop clk vdd vss
xm1 von clk vdd vdd pmos_hvt w=1u l=0.06u m=1
xm2 vop clk vdd vdd pmos_hvt w=1u l=0.06u m=1
xm5 von di1 vss vss nmos_hvt w=2u l=0.06u m=1
xm6 vop di2 vss vss nmos_hvt w=2u l=0.06u m=1
.ends
xcmp di1 di2 von vop clk vdd vss cmp
.end
"""


def _kit(tmp_path):
    p = tmp_path / "cmp.spice"
    p.write_text(_KIT_NETLIST)
    return p


def test_default_pdk_refuses_a_netlist_from_another_kit(tmp_path, capsys):
    """The reported trap: no --pdk, so the ihp-sg13g2 default drew IHP symbols over licensed-kit models.

    The sheet rendered, re-netlisted correctly and passed a netlist-identity gate — only the
    drawing was from the wrong foundry, which is the one defect a *generated* schematic is
    trusted not to have.
    """
    out = tmp_path / "cmp.sch"
    rc = main([str(_kit(tmp_path)), "-o", str(out), "--into", "xcmp"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "would draw its own symbols" in err
    assert "nmos_hvt" in err and "pmos_hvt" in err
    assert "--allow-foreign-symbols" in err
    assert not out.exists()


def test_a_commercial_kit_token_draws_generic_symbols_and_says_so(tmp_path, capsys):
    out = tmp_path / "cmp.sch"
    assert (
        main([str(_kit(tmp_path)), "-o", str(out), "--into", "xcmp", "--pdk", "generic-n65"]) == 0
    )
    text = out.read_text()
    assert "nmos4" in text and "pmos4" in text  # neutral symbols
    assert "sg13" not in text  # and NOT the other foundry's
    assert "nmos_hvt" in text  # the kit model rides the instance
    err = capsys.readouterr().err
    assert "no vendored symbol library for --pdk generic-n65" in err  # the token announces itself
    assert "ihp-sg13g2" in err  # ...and names what IS mapped


def test_generic_token_is_the_quiet_deliberate_choice(tmp_path, capsys):
    out = tmp_path / "cmp.sch"
    assert main([str(_kit(tmp_path)), "-o", str(out), "--into", "xcmp", "--pdk", "generic"]) == 0
    err = capsys.readouterr().err
    assert "no vendored symbol library" not in err
    assert "would draw its own symbols" not in err


def test_allow_foreign_symbols_still_warns(tmp_path, capsys):
    out = tmp_path / "cmp.sch"
    rc = main([str(_kit(tmp_path)), "-o", str(out), "--into", "xcmp", "--allow-foreign-symbols"])
    assert rc == 0
    assert "sg13" in out.read_text()  # the escape really does draw them
    assert "drawing ihp-sg13g2 symbols over foreign MOS models" in capsys.readouterr().err


def test_a_real_sg13g2_netlist_is_unaffected(tmp_path, capsys):
    """The default must stay silent and correct for the PDK it is the default for."""
    p = tmp_path / "ihp.spice"
    p.write_text(
        "* IHP SG13G2\n"
        ".subckt inv a y vdd vss\n"
        "xm1 y a vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1\n"
        "xm2 y a vss vss sg13_lv_nmos w=1u l=0.13u ng=1 m=1\n"
        ".ends\n"
        "xinv a y vdd vss inv\n.end\n"
    )
    out = tmp_path / "inv.sch"
    assert main([str(p), "-o", str(out), "--into", "xinv"]) == 0
    assert "sg13_lv_nmos" in out.read_text()
    err = capsys.readouterr().err
    assert "would draw its own symbols" not in err
    assert "no vendored symbol library" not in err


# --- a file that is not the @1 annotation contract (LEAF-F12) --------------------------------------

_NOT_THE_CONTRACT = [
    # analog-db's structural.json: the @1 string on a `groups`-shaped document
    ({"schema": ANNOTATION_SCHEMA, "circuit": "amp", "groups": []}, "no 'blocks'"),
    (
        {"schema": "spicexplorer/xschem-block-annotations@2", "blocks": []},
        "unsupported annotation schema",
    ),
]


@pytest.mark.parametrize(("payload", "says"), _NOT_THE_CONTRACT, ids=["groups-shape", "new-major"])
def test_cli_refuses_a_non_contract_annotations_file(tmp_path, capsys, payload, says):
    ann = tmp_path / "amp.blocks.json"
    ann.write_text(json.dumps(payload))
    out = tmp_path / "out.sch"
    rc = main([str(FIXTURES / "mixed_devices.spice"), "-o", str(out), "--annotations", str(ann)])
    # a one-line error, not an unannotated schematic that looks like "nothing detected"
    assert rc == 1
    err = capsys.readouterr().err
    assert f"error: failed to read annotations {ann}" in err and says in err
    assert "Traceback" not in err
    assert not out.exists()


@pytest.mark.parametrize(("payload", "says"), _NOT_THE_CONTRACT, ids=["groups-shape", "new-major"])
def test_cli_annotate_existing_refuses_a_non_contract_annotations_file(
    tmp_path, capsys, payload, says
):
    ann = tmp_path / "amp.blocks.json"
    ann.write_text(json.dumps(payload))
    out = tmp_path / "out.sch"
    rc = main(
        [
            str(FIXTURES / "title_above_bbox.sch"),
            "--annotate-existing",
            "--annotations",
            str(ann),
            "-o",
            str(out),
        ]
    )
    assert rc == 1
    err = capsys.readouterr().err
    assert f"error: failed to read annotations {ann}" in err and says in err
    assert not out.exists()
