"""A committed layout provenance record names its extraction without a user's home directory.

**LAY-D11** (audit 2026-09-24): ``out/pex/rc_netlist.sha256`` of the ldo_010 layout entry named its
extracted netlist by an absolute path under the sign-off author's home. analog-db is a release
candidate, and the orchestration layout workflow removes this kind of host path from every
verdict. The record now names it ``$SX_SCRATCH``-relative, and ``pex_sim.recorded_pex_dir`` (the
one reader of that line) expands the variable, so a re-run on a host holding that scratch tree
still finds the recorded extraction with no arguments.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

from spicexplorer_analog_db import paths

_ENTRY = "circuits/ldo_010_capless_lowiq/pdk/ihp-sg13g2/layout-001-fvf-strapped-pass-array"
_HOME = re.compile(r"(?<![\w$])/(?:home|Users)/[^/\s]+/")


def _digests() -> list[Path]:
    return sorted(paths.db_root().glob("circuits/*/pdk/*/layout-*/out/pex/*.sha256"))


def _recorded_line(digest: Path) -> str:
    return next(ln for ln in digest.read_text().splitlines() if ln.startswith("# netlist:"))


def test_no_layout_digest_names_a_home_directory():
    assert _digests(), "the ldo_010 layout entry's digest moved; update this guard"
    leaks = [str(p) for p in _digests() if _HOME.search(p.read_text())]
    assert not leaks, f"absolute home path in a committed provenance digest: {leaks}"


def _pex_sim():
    """The entry's own ``pex_sim.py`` (a script in the entry, not a package module)."""
    spec = importlib.util.spec_from_file_location(
        "ldo_010_layout_pex_sim", paths.db_root() / _ENTRY / "pex_sim.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_recorded_extraction_is_found_under_sx_scratch(tmp_path, monkeypatch):
    entry = paths.db_root() / _ENTRY
    pex_sim = _pex_sim()

    recorded = _recorded_line(entry / "out" / "pex" / "rc_netlist.sha256").split(":", 1)[1].strip()
    assert recorded.startswith("$SX_SCRATCH/"), recorded
    netlist = tmp_path / recorded.removeprefix("$SX_SCRATCH/")
    netlist.parent.mkdir(parents=True)
    netlist.write_text("* the extraction of record\n")

    monkeypatch.setenv("SX_SCRATCH", str(tmp_path))
    assert pex_sim.recorded_pex_dir() == str(netlist.parent)
    monkeypatch.delenv("SX_SCRATCH")
    with pytest.raises(SystemExit, match="is not on this machine"):
        pex_sim.recorded_pex_dir()


def test_the_digest_still_hashes_the_netlist_it_names():
    """The scrub rewrote the ``# netlist:`` line only: the one digest line is a sha256 of the same
    file name the recorded path ends in."""
    digest = paths.db_root() / _ENTRY / "out" / "pex" / "rc_netlist.sha256"
    recorded = Path(_recorded_line(digest).split(":", 1)[1].strip())
    body = [ln for ln in digest.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    assert len(body) == 1, body
    sha, name = body[0].split()
    assert re.fullmatch(r"[0-9a-f]{64}", sha), sha
    assert name == recorded.name


def _write_digest(out: Path, *lines: str) -> None:
    (out / "pex").mkdir(parents=True)
    (out / "pex" / "rc_netlist.sha256").write_text("".join(ln + "\n" for ln in lines))


@pytest.mark.parametrize("form", ["absolute", "$SX_SCRATCH", "${SX_SCRATCH}"])
def test_recorded_pex_dir_reads_an_absolute_or_a_variable_record(tmp_path, monkeypatch, form):
    """``absolute`` is a record written before the scrub: expandvars leaves it as it was."""
    pex_sim = _pex_sim()
    scratch = tmp_path / "scratch"
    netlist = scratch / "w5" / "pex_rc" / "cell_pex.spice"
    netlist.parent.mkdir(parents=True)
    netlist.write_text("* extraction\n")
    monkeypatch.setenv("SX_SCRATCH", str(scratch))
    recorded = str(netlist) if form == "absolute" else f"{form}/w5/pex_rc/cell_pex.spice"
    _write_digest(
        tmp_path / "out", "# cards: 1 R", f"# netlist: {recorded}", f"{'0' * 64}  cell_pex.spice"
    )
    monkeypatch.setattr(pex_sim, "OUT", tmp_path / "out")
    assert pex_sim.recorded_pex_dir() == str(netlist.parent)


@pytest.mark.parametrize(
    "lines",
    [
        pytest.param(None, id="no-digest"),
        pytest.param(("# cards: 1 R", f"{'0' * 64}  cell_pex.spice"), id="no-netlist-line"),
        pytest.param(("# netlist: $SX_SCRATCH/gone/cell_pex.spice",), id="recorded-file-absent"),
    ],
)
def test_recorded_pex_dir_names_the_re_extraction_when_there_is_no_netlist(
    tmp_path, monkeypatch, lines
):
    pex_sim = _pex_sim()
    monkeypatch.setenv("SX_SCRATCH", str(tmp_path / "scratch"))
    monkeypatch.setattr(pex_sim, "OUT", tmp_path / "out")
    if lines is not None:
        _write_digest(tmp_path / "out", *lines)
    with pytest.raises(
        SystemExit, match=r"is not on this machine(?s:.*)--stages pex --pex-mode RC"
    ):
        pex_sim.recorded_pex_dir()


def test_the_entry_readme_no_longer_calls_the_recorded_path_absolute():
    text = (paths.db_root() / _ENTRY / "README.md").read_text()
    assert "an absolute path on the machine" not in text
    assert re.search(r"the digest records it\s+`\$SX_SCRATCH`-relative", text)


# ───────── layout entries cite the platform's layout backend, not its retired prototypes ─────────
# The platform's July-2026 layout prototype scripts under examples/layout/ihp-sg13g2/ (superseded by
# spicexplorer-layout / spicexplorer-signoff and the `sim_engine: layout` backend) are being
# retired. A catalogued circuit's layout entry that points a reader at one of them sends the reader
# to a file that no longer exists. `drawings/` keeps the ported upstream copies as they arrived and
# is out of scope here.

_RETIRED_LAYOUT_PROTOTYPE = re.compile(
    r"examples/layout/ihp-sg13g2/(?:pex_kpex\.py|sim_pex_compare\.py"
    r"|5t_ota/signoff(?:_magic_netgen)?\.py|5t_ota_gf/(?:signoff\.py|optimize_layout\.(?:py|ipynb)))"
)


def _layout_entry_text_files() -> list[Path]:
    root = paths.db_root() / "circuits"
    return sorted(
        p
        for p in root.glob("*/pdk/*/layout-*/**/*")
        if p.is_file() and p.suffix in {".py", ".md", ".yaml", ".yml", ".ipynb", ".txt"}
    )


def test_no_layout_entry_cites_a_retired_platform_layout_prototype():
    files = _layout_entry_text_files()
    assert any(p.name == "optimize_layout.py" for p in files), "drv_001's layout entry moved"
    hits = [
        f"{p.relative_to(paths.db_root())}:{n}"
        for p in files
        for n, ln in enumerate(p.read_text(errors="replace").splitlines(), 1)
        if _RETIRED_LAYOUT_PROTOTYPE.search(ln)
    ]
    assert not hits, f"layout entry cites a retired platform prototype script: {hits}"


@pytest.mark.parametrize(
    "line, hit",
    [
        ("Same pattern as examples/layout/ihp-sg13g2/5t_ota_gf/optimize_layout.py", True),
        ("see examples/layout/ihp-sg13g2/5t_ota/signoff_magic_netgen.py", True),
        ("(``examples/layout/ihp-sg13g2/5t_ota/signoff.py``)", True),
        ("the live flow is examples/layout/ihp-sg13g2/5t_ota_gf/opt/flow.yaml", False),
        ("gen_5t_ota_gf.py stays", False),
    ],
)
def test_retired_prototype_pattern(line, hit):
    assert bool(_RETIRED_LAYOUT_PROTOTYPE.search(line)) is hit
