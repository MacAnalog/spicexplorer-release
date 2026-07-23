"""Unit coverage for the native-Spectre + OCEAN wiring pieces (no Cadence, no bridge).

- `render_native_scs`: inject design params / corner into a hand-written `.scs` in place.
- `deck_spec_from_native`: the library composer (opt-in), still available.
- `SpectreSimResult.raw_dir` / `merge_scalars`: the OCEAN merge surface + `_raw_dir_of`.
- `_build_spectre` threading: a native `.scs` `netlist:` → native-file injection mode,
  forwarding `native_scs`/`work_dir`/`deck_dir`/`vb_env_file` — asserted by stubbing the
  lazy `create_spectre_simulator` (the bridge is not installed here).
- ngspice ignores the new Spectre-only kwargs (byte-identical construction).
"""

from __future__ import annotations

import numpy as np
import pytest
from _spicexplorer_fixtures import requires_ngspice
from spicexplorer.backends import spectre as spectre_mod
from spicexplorer.backends.spectre import SpectreSimResult, _raw_dir_of
from spicexplorer.backends.spectre_deck import (
    SpectreDeckSpec,
    deck_spec_from_native,
    render_native_scs,
    render_spectre_deck,
)
from spicexplorer.optimization.simulator_factory import build_simulator
from spicexplorer_core.spice_engine import NGSpice_Wrapper

RC_DECK = "* RC\nV1 in 0 dc 0 ac 1\nR1 in out 1k\nC1 out 0 100p\n.ac dec 5 1k 1Meg\n.end\n"

NATIVE_SCS = """// 5T-OTA AC tb
simulator lang=spectre
global 0
include "def_models.scs" section=tt_lvt
parameters vdd=1.2 vcm=0.6 w0=1u l0=0.2u
include "dut.scs"
v1 (vdd 0) vsource dc=vdd
xota (v_out vinp vcm vdd 0) ota w=w0 l=l0
dcOp dc
ac ac start=1 stop=1e8 dec=101
"""


# -- render_native_scs (the netlist-file injection) -------------------------------
def test_native_scs_injects_params_swaps_corner_and_preserves_the_rest():
    out = render_native_scs(
        NATIVE_SCS,
        parameters={"W0": 2e-6, "vcm": 0.7},  # design var (case-folded) + a supply
        corner_includes=['include "/pdk/m.scs" section=ss_lvt'],
        temp=85.0,
    )
    assert "parameters vdd=1.2 vcm=0.7 w0=2e-06 l0=0.2u" in out  # merged over defaults
    assert "section=ss_lvt" in out and "tt_lvt" not in out       # corner replaced
    assert 'include "dut.scs"' in out                            # DUT include (no section) kept
    assert "ac ac start=1 stop=1e8 dec=101" in out               # analyses verbatim
    assert "tempOptions options temp=85" in out


def test_native_scs_no_overrides_is_effectively_verbatim():
    out = render_native_scs(NATIVE_SCS)
    for token in ('section=tt_lvt', 'include "dut.scs"', "ac ac start=1", "dcOp dc"):
        assert token in out


def test_native_scs_inserts_a_parameters_line_when_the_deck_has_none():
    deck = "// x\nsimulator lang=spectre\nglobal 0\nv1 (a 0) vsource dc=1\ndcOp dc\n"
    out = render_native_scs(deck, parameters={"w0": 1e-6})
    lines = out.splitlines()
    assert "parameters w0=1e-06" in lines
    # inserted right after the header, before the stimulus
    assert lines.index("parameters w0=1e-06") < lines.index("v1 (a 0) vsource dc=1")


def test_native_scs_handles_backslash_continuation():
    deck = "simulator lang=spectre\nglobal 0\nparameters a=1 b=2 \\\n  c=3\ndcOp dc\n"
    out = render_native_scs(deck, parameters={"b": 20})
    assert "parameters a=1 b=20 c=3" in out


# -- deck_spec_from_native (library composer, opt-in) -----------------------------
def test_deck_spec_from_native_assembles_a_composable_spec():
    spec = deck_spec_from_native(
        "tb_ac", 'xdut (v_out) dut', subckt_blocks=['include "dut.scs"'],
        parameters={"vdd": 1.2}, analyses=["dcOp dc", 'ac ac start=1 stop=1e6 dec=10'],
    )
    assert isinstance(spec, SpectreDeckSpec)
    assert spec.analyses == ("dcOp dc", 'ac ac start=1 stop=1e6 dec=10')
    text = render_spectre_deck(spec, parameters={"vdd": 1.1})
    assert "parameters vdd=1.1" in text and 'include "dut.scs"' in text


# -- SpectreSimResult.raw_dir / merge_scalars ------------------------------------
class _Res:
    def __init__(self, data, metadata=None):
        self.data = data
        self.metadata = metadata or {}


def test_raw_dir_of_reads_metadata_output_dir():
    assert _raw_dir_of(_Res({}, {"output_dir": "/tmp/run.raw"})) == "/tmp/run.raw"
    assert _raw_dir_of(_Res({}, {})) is None
    assert _raw_dir_of(_Res({})) is None


def test_merge_scalars_are_authoritative_over_bare_and_prefixed_psf_keys():
    r = SpectreSimResult({"ac_v_out": 0.5, "ugf": 1.0, "ac_gain": 0.5}, raw_dir="/tmp/x.raw")
    assert r.raw_dir == "/tmp/x.raw"
    r.merge_scalars({"ugf": 42.0, "pm": 70.0, "gain": 30.0})
    assert r.scalar("ugf", "ac") == pytest.approx(42.0)   # bare collision → OCEAN wins
    assert r.scalar("gain", "ac") == pytest.approx(30.0)  # ac_ prefixed collision → OCEAN wins
    assert r.scalar("pm", "ac") == pytest.approx(70.0)    # no collision
    assert r.scalar("v_out", "ac") == pytest.approx(0.5)  # untouched PSF signal


def test_missing_merged_metric_is_nan():
    assert np.isnan(SpectreSimResult({}, raw_dir="/tmp/x.raw").scalar("absent", "ac"))


# -- _build_spectre threading (stub the lazy bridge factory) ---------------------
@pytest.fixture
def spy_create(monkeypatch):
    calls = {}

    def _spy(*args, **kwargs):
        calls.update(kwargs)
        calls["_args"] = args
        return "SENTINEL_SIM"

    monkeypatch.setattr(spectre_mod, "create_spectre_simulator", _spy)
    return calls


def test_build_spectre_routes_scs_netlist_to_native_file_mode(spy_create, tmp_path):
    deck = tmp_path / "tb_ac.scs"
    deck.write_text(NATIVE_SCS)
    sim = build_simulator(
        "spectre",
        testbench_name="tb_ac",
        netlist_filename=deck,
        work_dir=tmp_path / "raw",
        deck_dir=tmp_path / "decks",
        vb_env_file="/home/x/.virtuoso-bridge/local.env",
    )
    assert sim == "SENTINEL_SIM"
    assert spy_create["native_scs"] == deck
    assert spy_create["work_dir"] == tmp_path / "raw"
    assert spy_create["deck_dir"] == tmp_path / "decks"
    assert spy_create["vb_env_file"] == "/home/x/.virtuoso-bridge/local.env"
    assert "deck_spec" not in spy_create and spy_create.get("netlist") is None


def test_build_spectre_rejects_a_non_scs_netlist(tmp_path):
    with pytest.raises(NotImplementedError, match=r"\.scs"):
        build_simulator("spectre", netlist_filename=tmp_path / "tb.cir")


@requires_ngspice
def test_ngspice_ignores_the_new_spectre_kwargs(tmp_path):
    deck = tmp_path / "rc.cir"
    deck.write_text(RC_DECK)
    sim = build_simulator(
        "ngspice",
        netlist_filename=deck,
        testbench_name="rc",
        output_folder=tmp_path / "runs",
        work_dir=tmp_path / "wd",
        deck_dir=tmp_path / "dd",
        vb_env_file="/whatever",
    )
    assert isinstance(sim, NGSpice_Wrapper)
