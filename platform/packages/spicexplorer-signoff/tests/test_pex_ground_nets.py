"""``run_pex(ground_nets=...)`` and the self-loop count (MacAnalog/spicexplorer-platform#281).

WP-21 added ``summarize_parasitics(ground_nets=...)`` for a substrate that carries a pin name, and
nothing passed it through: ``run_pex`` summed with the default aliases only, so ``sub`` on the
PAM-4 driver cell came back as a signal net. The netlist here is ``fixtures/kpex_ground_aliases
.spice``, shaped on recorded kpex CC output of that cell: a ``sub`` pin, the self-loop
``Cext_51 sub sub 23.0904f``, and ground C on VSUBS / vss / GND / Vss / 0. kpex is a stand-in
script that writes that netlist where kpex writes its own. The last test reads the recorded
extractions of the driver cells themselves from the analog-db submodule and skips without it.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from spicexplorer_core.paths import project_root
from spicexplorer_signoff import PexResult
from spicexplorer_signoff.pex import (
    GROUND_NETS,
    ParasiticSummary,
    run_pex,
    scan_parasitics,
    summarize_parasitics,
)

FIX = Path(__file__).parent / "fixtures"
_NETLIST = (FIX / "kpex_ground_aliases.spice").read_text()


@pytest.fixture
def fake_kpex(tmp_path, monkeypatch):
    """`kpex` that writes the PAM-4-shaped netlist to `<out_dir>/<gds stem>__<cell>/`."""
    (tmp_path / "top.gds").write_bytes(b"")
    (tmp_path / "top.sp").write_text(".subckt cell sub inp outp vss\n.ends\n")
    exe = tmp_path / "kpex"
    exe.write_text(
        "#!/usr/bin/env python3\nimport pathlib, sys\na = sys.argv\n"
        "gds, cell = pathlib.Path(a[a.index('--gds') + 1]), a[a.index('--cell') + 1]\n"
        "d = pathlib.Path(a[a.index('--out_dir') + 1]) / f'{gds.stem}__{cell}'\n"
        "d.mkdir(parents=True, exist_ok=True)\n"
        f"(d / f'{{cell}}_k25d_pex_netlist.spice').write_text({_NETLIST!r})\n"
    )
    exe.chmod(0o755)
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_exe", lambda: str(exe))
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_klayout_exe", lambda: str(exe))
    return tmp_path


def test_run_pex_forwards_ground_nets_and_records_what_it_applied(fake_kpex):
    """The #281 reproduction: on the base `run_pex` took no `ground_nets` at all."""
    r = run_pex(
        fake_kpex / "top.gds", "cell", fake_kpex / "top.sp", fake_kpex / "out", ground_nets=("SUB",)
    )
    assert r.ok, r.reason
    assert "sub" not in r.per_net_c_ff and "outp|sub" not in r.coupling_ff
    assert r.per_net_c_ff["outp"] == pytest.approx(4.25)  # its 2.5 fF to sub is C to ground now
    assert r.ground_nets == ["0", "gnd", "sub", "vss", "vsubs"]
    assert r.n_self == 1 and r.n_c == 9  # Cext_51 sub sub is the one self-loop


def test_run_pex_default_keeps_a_substrate_pin_as_a_signal_net(fake_kpex):
    """Negative case, and the default is unchanged: without `ground_nets`, `sub` is a signal net."""
    r = run_pex(fake_kpex / "top.gds", "cell", fake_kpex / "top.sp", fake_kpex / "out")
    assert r.ok, r.reason
    assert r.per_net_c_ff["sub"] == pytest.approx(2.5) and r.coupling_ff[
        "outp|sub"
    ] == pytest.approx(2.5)
    assert r.ground_nets == sorted(GROUND_NETS) and r.n_self == 1
    assert (r.n_c, r.n_r, r.per_net_c_ff, r.coupling_ff) == summarize_parasitics(
        FIX / "kpex_ground_aliases.spice"
    )


def test_run_pex_summary_equals_summarize_parasitics_on_the_same_netlist(fake_kpex):
    r = run_pex(
        fake_kpex / "top.gds", "cell", fake_kpex / "top.sp", fake_kpex / "out", ground_nets=["sub"]
    )
    assert (r.n_c, r.n_r, r.per_net_c_ff, r.coupling_ff) == summarize_parasitics(
        FIX / "kpex_ground_aliases.spice", ground_nets=["sub"]
    )


def test_scan_parasitics_counts_self_loops_and_skips_unreadable_values(tmp_path):
    """Both self-loops (on ground and on a signal net) are counted in n_self and nowhere else; a C
    card whose value does not parse is neither a card nor a self-loop."""
    net = tmp_path / "c_pex.spice"
    net.write_text(
        ".subckt c a b vss\n"
        "C1 a b 1f\nC2 vss vss 5f\nC3 VSUBS 0 2f\nC4 a a 9f\nC5 b GND 0.5f\nC6 a a notanumber\n"
        "R1 a b 10\n.ends c\n"
    )
    s = scan_parasitics(net, ground_nets=("Extra",))
    assert isinstance(s, ParasiticSummary)
    assert (s.n_c, s.n_r, s.n_self) == (3, 1, 2)
    assert s.per_net_c_ff == pytest.approx({"a": 1.0, "b": 1.5})
    assert s.ground_nets == ["0", "extra", "gnd", "vss", "vsubs"]
    assert tuple(s[:4]) == summarize_parasitics(net, ground_nets=("Extra",))


def test_pex_result_new_fields_default_empty():
    """A PexResult built from an older record (orchestration replays recorded ones) gets empty
    values for the two fields, so a record without them reads as "nothing recorded"."""
    d = PexResult(True, True).to_dict()
    assert d["ground_nets"] == [] and d["n_self"] == 0


def test_run_pex_failure_records_no_ground_set(tmp_path, monkeypatch):
    monkeypatch.setattr("spicexplorer_signoff.pex.kpex_exe", lambda: None)
    r = run_pex(
        tmp_path / "x.gds", "cell", tmp_path / "x.sp", tmp_path / "out", ground_nets=("sub",)
    )
    assert not r.available and r.ground_nets == [] and r.n_self == 0


_PAM4_PEX = (
    project_root()
    / "examples/analog-db/drawings/pam4-driver-2-bit-dac-HBT/ported-netlists/layout/out/pex"
)


@pytest.mark.parametrize("name", ["lsb", "msb", "pam4", "pam4_best"])
def test_recorded_pam4_extractions_with_sub_as_ground(name):
    """The PAM-4 driver cells named in #281, on their recorded kpex CC extractions in analog-db
    (``sub`` is the first ``.SUBCKT`` pin). By default ``sub`` is a signal net with its own C sum
    and coupling pairs; with ``ground_nets=("sub",)`` both are gone, every other net keeps the
    same sum, and the one ``sub sub`` self-loop card is counted in ``n_self``."""
    net = _PAM4_PEX / f"dut_{name}_post.spice"
    if not net.is_file():
        pytest.skip(f"analog-db submodule not checked out: {net} missing")
    dflt = scan_parasitics(net)
    sub = scan_parasitics(net, ground_nets=("sub",))
    assert dflt.per_net_c_ff["sub"] > 0
    assert any("sub" in pair.split("|") for pair in dflt.coupling_ff)
    assert "sub" not in sub.per_net_c_ff
    assert not any("sub" in pair.split("|") for pair in sub.coupling_ff)
    others = {k: v for k, v in dflt.per_net_c_ff.items() if k != "sub"}
    assert sub.per_net_c_ff == pytest.approx(others)
    assert (sub.n_c, sub.n_self) == (dflt.n_c, 1) and dflt.n_self == 1
    assert "sub" in sub.ground_nets and "sub" not in dflt.ground_nets


def test_the_verdict_records_the_halo_it_ran_at(fake_kpex):
    """Two extractions compare only at one halo, so the verdict names it (L-PF-22); None is the
    tech file's own halo (no `--halo` passed to kpex)."""
    wide = run_pex(
        fake_kpex / "top.gds", "cell", fake_kpex / "top.sp", fake_kpex / "o1", halo_um=20.0
    )
    tech = run_pex(fake_kpex / "top.gds", "cell", fake_kpex / "top.sp", fake_kpex / "o2")
    assert wide.ok and tech.ok
    assert (wide.halo_um, tech.halo_um) == (20.0, None)
    assert wide.to_dict()["halo_um"] == 20.0
