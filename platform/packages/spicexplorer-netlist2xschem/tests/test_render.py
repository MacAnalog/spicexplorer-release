"""Render + round-trip.

The pure host check confirms graceful degradation when xschem is absent. The ``slow`` tests run only
where xschem is on PATH (the EDA container: ``docker compose exec api pytest -m slow``):

* SVG export produces a non-empty file;
* the round-trip — generate ``.sch`` → ``xschem -n -s`` → parse with ``NetlistView`` — reproduces the
  original device set and per-device net connectivity (the true correctness gate for place+wire+map).
"""

import os
import subprocess
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import build_sch, from_file, render, xschem_available
from spicexplorer_netlist2xschem.ingest import N2XCircuit, ingest
from spicexplorer_netlist2xschem.render import write_xschemrc
from spicexplorer_netlist2xschem.sym_library import SymLibrary, default_search_paths

FIXTURES = Path(__file__).parent / "fixtures"

requires_xschem = pytest.mark.skipif(not xschem_available(), reason="xschem not on PATH")


@pytest.mark.skipif(xschem_available(), reason="only meaningful when xschem is absent")
def test_render_graceful_without_xschem(tmp_path):
    sch = tmp_path / "c.sch"
    sch.write_text("v {xschem version=3.4.6 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n")
    result = render(sch, fmt="png")
    assert result.available is False
    assert result.image_path is None
    assert result.sch_path == sch  # the .sch is untouched and still valid for the UI viewer


def _normalize(circuit: N2XCircuit) -> dict[str, frozenset[str]]:
    """ref (upper, X-stripped) -> the frozenset of nets it touches (lower)."""
    out: dict[str, frozenset[str]] = {}
    for d in circuit.devices:
        ref = d.ref.upper().lstrip("X")
        out[ref] = frozenset(n.lower() for n in d.nets.values())
    return out


@requires_xschem
@pytest.mark.slow
def test_svg_export_smoke(tmp_path):
    circuit = from_file(FIXTURES / "ota-5t_tb-ac.spice", into="xota", name="ota-5t")
    sch = tmp_path / "ota-5t.sch"
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2").text)
    result = render(sch, fmt="svg", outdir=tmp_path)
    assert result.available is True
    assert result.fmt == "svg"
    assert result.image_path is not None and result.image_path.stat().st_size > 0


@requires_xschem
@pytest.mark.slow
@pytest.mark.parametrize(
    ("fixture", "kw"),
    [
        ("ota-5t_tb-ac.spice", {"into": "xota", "name": "ota-5t"}),
        ("ota-improved.spice", {"name": "ota-improved"}),
        ("folded_cascode.spice", {"into": "XDUT", "name": "folded"}),
    ],
)
def test_roundtrip_devices_and_connectivity(tmp_path, fixture, kw):
    """Generated .sch → xschem SPICE netlist → reparse: same devices + same per-device net sets.

    The true correctness gate for place+wire+map across the default topology+hybrid pipeline (rails,
    spines, port pins, gate-facing flips) — connectivity must survive aggressive wiring on every shape.
    """
    from spicexplorer_core.spice_engine import NetlistView

    circuit = from_file(FIXTURES / fixture, **kw)
    sch = tmp_path / f"{kw['name']}.sch"
    # Build (and later resolve) against the real vendored libs PLUS the checked-in fixture lib, which
    # carries the default clean ``*_np`` symbols — so this passes even against a stale EDA image (whose
    # baked symbol dirs predate the _np twins).
    lib = SymLibrary([*default_search_paths(), FIXTURES / "sym"])
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2", lib=lib).text)

    lib_path = os.pathsep.join(
        [*(str(p) for p in default_search_paths()), str(FIXTURES / "sym")]
    )
    # Seed the symbol path via our own rcfile so resolution is independent of the image HOME/xschemrc.
    rc = write_xschemrc(tmp_path, lib_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = lib_path
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-x", "-q", "-n", "-s", "-o", str(tmp_path), str(sch)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(tmp_path),
    )
    spice = tmp_path / f"{kw['name']}.spice"
    assert spice.is_file(), "xschem produced no netlist"

    reparsed = ingest(NetlistView.from_file(spice), name="roundtrip")
    original, roundtrip = _normalize(circuit), _normalize(reparsed)
    assert set(roundtrip) == set(original), (
        f"device set differs: only-original={set(original) - set(roundtrip)} "
        f"only-roundtrip={set(roundtrip) - set(original)}"
    )
    for ref, nets in original.items():
        assert roundtrip[ref] == nets, f"{ref}: nets {roundtrip[ref]} != original {nets}"
