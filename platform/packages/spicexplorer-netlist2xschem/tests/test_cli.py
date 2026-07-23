"""CLI smoke tests — generation works without xschem; --render degrades gracefully on host."""

from pathlib import Path

from spicexplorer_netlist2xschem import xschem_available
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
