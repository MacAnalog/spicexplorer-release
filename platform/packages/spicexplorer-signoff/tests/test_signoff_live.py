"""Live signoff on the prototype 5T-OTA GDS — needs klayout + the IHP PDK (+ kpex for PEX).

Marked ``slow``; each test skips with the missing capability as the reason.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_core import project_root
from spicexplorer_signoff import probe, run_drc, run_lvs, run_pex

EX = project_root() / "examples" / "layout" / "ihp-sg13g2" / "5t_ota_gf"
GDS, NET, CELL = EX / "ota_5t_gf.gds", EX / "ota_5t_gf_lvs.spice", "ota_5t_gf"
P = probe()

pytestmark = pytest.mark.slow


@pytest.mark.skipif(
    not (P.drc_ok and GDS.is_file()), reason="klayout + PDK DRC deck + example GDS needed"
)
def test_drc_live(tmp_path):
    r = run_drc(GDS, CELL, tmp_path / "drc")
    assert r.available and r.passed and r.n_violations == 0 and r.report_path


@pytest.mark.skipif(
    not (P.lvs_ok and GDS.is_file()), reason="klayout + PDK LVS deck + example GDS needed"
)
def test_lvs_live(tmp_path):
    r = run_lvs(GDS, NET, CELL, tmp_path / "lvs")
    assert r.available and r.passed and r.matched and r.netlist_sha


@pytest.mark.skipif(not (P.pex_ok and GDS.is_file()), reason="kpex (+ ruby>=2.6 klayout) needed")
def test_pex_live(tmp_path):
    r = run_pex(GDS, CELL, NET, tmp_path / "pex", mode="CC")
    assert r.ok and r.n_c > 0 and r.netlist_path and Path(r.netlist_path).is_file()
    assert 0.5 < r.per_net_c_ff["vinp"] < 5.0  # ~1.2 fF on the prototype
