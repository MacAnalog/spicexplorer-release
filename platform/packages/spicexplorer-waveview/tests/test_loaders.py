"""Loader semantics: ngspice .raw + Spectre psfascii dirs → WaveDataset.

Includes the PARITY pins: the dataset's arrays must match what the engines' own
result adapters (core `NgspiceSimResult`, the optimizer's `read_swept_psf`) read from
the same artifact — waveview restates those contracts instead of importing them, and
these tests are what keep the restatement honest.
"""

from __future__ import annotations

import numpy as np
import pytest
from spicexplorer_waveview import load_result, sniff_engine
from spicexplorer_waveview.testing import synth_ac_raw, synth_spectre_raw_dir, synth_tran_raw


@pytest.fixture()
def ac_raw(tmp_path):
    path = tmp_path / "tb_ac.raw"
    truth = synth_ac_raw(path)
    return path, truth


@pytest.fixture()
def spectre_dir(tmp_path):
    root = tmp_path / "amp-raw"
    truth = synth_spectre_raw_dir(root)
    return root, truth


# --- sniffing -----------------------------------------------------------------
def test_sniff_ngspice_raw(ac_raw):
    path, _ = ac_raw
    assert sniff_engine(path) == "ngspice"


def test_sniff_spectre_dir(spectre_dir):
    root, _ = spectre_dir
    assert sniff_engine(root) == "spectre"


def test_sniff_unknown(tmp_path):
    p = tmp_path / "mystery.bin"
    p.write_bytes(b"\x00\x01\x02")
    assert sniff_engine(p) is None
    with pytest.raises(ValueError, match="could not determine the engine"):
        load_result(p)


def test_load_missing_path(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_result(tmp_path / "nope.raw")


# --- ngspice loader --------------------------------------------------------------
def test_ngspice_ac_analysis(ac_raw):
    path, truth = ac_raw
    ds = load_result(path)
    assert ds.engine == "ngspice"
    assert set(ds.analyses) == {"ac"}
    an = ds.analyses["ac"]
    assert an.native_name == "AC Analysis"
    assert an.sweep == "frequency"
    assert an.n_points == truth["n"]
    sig = an.signals["v(vout)"]
    assert sig.is_complex
    assert sig.units == "V"
    assert an.signals["frequency"].units == "Hz"


def test_ngspice_parity_with_core_result(ac_raw):
    """Dataset arrays == what core's NgspiceSimResult reads from the same raw."""
    from spicelib import RawRead
    from spicexplorer_core.spice_engine.spicelib import NgspiceSimResult

    path, _ = ac_raw
    ds = load_result(path)
    core_result = NgspiceSimResult(RawRead(raw_filename=str(path)))
    np.testing.assert_allclose(
        ds.analyses["ac"].signals["v(vout)"].data,
        core_result.wave("v(vout)", "ac"),
    )


def test_ngspice_tran(tmp_path):
    path = tmp_path / "tb_tran.raw"
    synth_tran_raw(path)
    ds = load_result(path)
    an = ds.analyses["tran"]
    assert an.sweep == "time"
    v = an.signals["v(vout)"].data
    assert not np.iscomplexobj(v)
    assert v.max() == pytest.approx(1.0, rel=1e-3)


def test_ngspice_unknown_plot_title_kept(tmp_path):
    from spicexplorer_waveview.testing import write_ngspice_ascii_raw

    p = tmp_path / "exotic.raw"
    write_ngspice_ascii_raw(
        p,
        [("Exotic Custom Analysis", [("time", "time"), ("v(x)", "voltage")],
          [np.linspace(0, 1, 10), np.ones(10)])],
    )
    ds = load_result(p)
    assert "exotic_custom_analysis" in ds.analyses  # slugified, not dropped
    assert any("unrecognised" in w for w in ds.warnings)


def test_ngspice_multi_plot_file(tmp_path):
    """One raw with several plots (a real deck's .control writes them all)."""
    from spicexplorer_waveview.testing import write_ngspice_ascii_raw

    f = np.logspace(0, 6, 21)
    t = np.linspace(0, 1e-3, 11)
    p = tmp_path / "multi.raw"
    write_ngspice_ascii_raw(
        p,
        [
            ("AC Analysis", [("frequency", "frequency"), ("v(out)", "voltage")],
             [f.astype(complex), (1.0 / (1 + 1j * f / 1e3))]),
            ("Transient Analysis", [("time", "time"), ("v(out)", "voltage")], [t, t * 10.0]),
            ("Operating Point", [("v(out)", "voltage")], [np.array([0.6])]),
            ("Transient Analysis", [("time", "time"), ("v(out)", "voltage")], [t, t * 20.0]),
        ],
    )
    ds = load_result(p)
    assert set(ds.analyses) == {"ac", "tran", "op", "tran:2"}
    # first tran keeps the canonical key (first-match parity with core extraction)
    assert ds.analyses["tran"].signals["v(out)"].data[-1] == pytest.approx(1e-3 * 10)
    assert ds.analyses["op"].scalars["v(out)"] == pytest.approx(0.6)


# --- spectre loader --------------------------------------------------------------
def test_spectre_analysis_map(spectre_dir):
    root, _ = spectre_dir
    ds = load_result(root)
    assert ds.engine == "spectre"
    assert {"ac", "dc", "op", "tran", "noise", "pss", "stb", "pac"} <= set(ds.analyses)
    assert ds.analyses["ac"].sweep == "freq"
    # abscissa aliases: registry recipes ask for "frequency"/"time"
    assert "frequency" in ds.analyses["ac"].signals
    assert "time" in ds.analyses["tran"].signals


def test_spectre_pac_baseband_and_sidebands(spectre_dir):
    """`pac.0.pac` claims the canonical `pac` key (the baseband transfer, backend
    parity); a non-baseband sideband lands under `pac_sb`; the metadata-only
    `pac.pac` parent is skipped by name — never parsed, never a warning."""
    root, _ = spectre_dir
    ds = load_result(root)
    pac = ds.analyses["pac"]
    assert pac.native_name == "pac.0.pac" and pac.sweep == "freq"
    assert "frequency" in pac.signals  # canonical abscissa alias
    np.testing.assert_allclose(np.abs(pac.signals["vout"].data), 20.0)
    sb = next(an for k, an in ds.analyses.items() if k.startswith("pac_sb"))
    np.testing.assert_allclose(np.abs(sb.signals["vout"].data), 0.5)
    assert not any("pac.pac" in w for w in ds.warnings)
    # noise-family aliases resolve onto the density sweep (Spectre semantics)
    assert ds.resolve_analysis("noise_spectrum") is ds.analyses["noise"]


def test_spectre_op_point(spectre_dir):
    root, truth = spectre_dir
    ds = load_result(root)
    op = ds.analyses["op"]
    assert op.native_name == "dcOp.dc"  # non-swept PSF claimed the analysis
    assert op.scalars["VDD"] == pytest.approx(1.2)
    assert op.scalars["X0.M0:gm"] == pytest.approx(1e-3)
    assert op.scalars["X0.M1:vth"] == pytest.approx(0.46)
    # NDA-guard: the modelParameter.info decoy must never be parsed
    assert not any("poison" in k for k in op.scalars)
    assert not any("nch_model" in k for k in op.scalars)


def test_spectre_pss_is_complex_harmonics(spectre_dir):
    root, _ = spectre_dir
    ds = load_result(root)
    h = ds.analyses["pss"].signals["vout"].data
    assert np.iscomplexobj(h)
    assert h.size == 6


def test_spectre_parity_with_backend_reader(spectre_dir):
    """Dataset arrays == what the optimizer's read_swept_psf reads (contract pin)."""
    spectre_backend = pytest.importorskip("spicexplorer.backends.spectre")
    root, _ = spectre_dir
    ds = load_result(root)
    for analysis in ("ac", "tran", "noise", "pss", "stb"):
        backend_signals = spectre_backend.read_swept_psf(root, analysis)
        assert backend_signals, f"backend read no {analysis} signals"
        for name, arr in backend_signals.items():
            mine = ds.find_signal(analysis, name)
            assert mine is not None, f"{analysis}:{name} missing from dataset"
            np.testing.assert_allclose(mine.data, arr, err_msg=f"{analysis}:{name}")


def test_spectre_mixed_case_suffixed_key_reachable(spectre_dir):
    """A sibling PSF whose stem carries mixed case must stay resolvable by its listed key."""
    import shutil

    root, _ = spectre_dir
    shutil.copy(root / "dc.dc", root / "dcSweep2.dc")
    ds = load_result(root)
    key = next(k for k in ds.analyses if k.startswith("dc:"))
    assert "dcSweep2" in key  # stem case preserved in the listed key…
    assert ds.resolve_analysis(key) is ds.analyses[key]  # …and reachable verbatim


def test_spectre_real_signal_beats_abscissa_alias(tmp_path):
    """A REAL trace named like an abscissa alias must win over the alias (backend parity:
    read_swept_psf overwrites the alias with the trace)."""
    from spicexplorer_waveview.testing import _write_swept

    d = tmp_path / "alias-raw"
    d.mkdir()
    f = np.logspace(0, 6, 11)
    real_frequency_net = np.linspace(5.0, 6.0, 11)  # a net someone named "frequency"
    _write_swept(d / "ac.ac", "ac", "ac", "freq", "Hz", f,
                 {"vout": (1.0 / (1 + 1j * f / 1e3)), "frequency": real_frequency_net.astype(complex)})
    ds = load_result(d)
    got = np.real(ds.analyses["ac"].signals["frequency"].data)
    np.testing.assert_allclose(got, real_frequency_net)

    spectre_backend = pytest.importorskip("spicexplorer.backends.spectre")
    backend = spectre_backend.read_swept_psf(d, "ac")
    np.testing.assert_allclose(np.real(backend["frequency"]), real_frequency_net)


def test_spectre_stb_margin_sibling(spectre_dir):
    """stb.margin.stb: numeric margins load as scalars; the STRING verdict is skipped."""
    root, _ = spectre_dir
    ds = load_result(root)
    # the swept loop-gain keeps the canonical key; the margin PSF rides a suffixed key
    assert ds.analyses["stb"].sweep is not None
    margin_keys = [k for k in ds.analyses if k.startswith("stb:")]
    assert len(margin_keys) == 1
    margin = ds.analyses[margin_keys[0]]
    assert margin.scalars["phaseMargin"] == pytest.approx(90.0)
    assert "stb_state" not in margin.signals  # string signal skipped…
    assert any("non-numeric" in w for w in ds.warnings)  # …and disclosed


def test_spectre_cache_and_logfile_ignored(spectre_dir):
    root, _ = spectre_dir
    ds = load_result(root)
    assert not any(".cache" in (an.native_name or "") for an in ds.analyses.values())
    # the only tolerated diagnostic is the margin PSF's skipped-string disclosure
    assert all("non-numeric" in w for w in ds.warnings)


# --- binary raw memory regression --------------------------------------------------
def test_binary_raw_signals_own_their_buffers(tmp_path):
    """Regression: loading a binary Normal-Access raw must COPY each signal out.

    spicelib's lazy path re-reads the plot's entire binary section on every
    cache-miss `get_wave` and hands back a VIEW pinning that call's full-file
    buffer. Loading trace-by-trace therefore held traces × file-size of memory —
    a 3239-signal loopgain raw (57 MB) OOM-killed the API worker. The loader now
    bulk-reads the plot once and copies each signal, so every loaded array must
    own its buffer (`.base is None`); a view would resurrect the leak.
    """
    from spicelib import RawWrite
    from spicelib.raw.raw_write import Trace as WTrace

    n = 256
    freq = np.logspace(0, 8, n)
    w = RawWrite(plot_name="AC Analysis", fastacces=False)
    w.add_trace(
        WTrace("frequency", freq.astype(complex), whattype="frequency", numerical_type="complex")
    )
    poles = [10.0 ** (3 + (i % 5)) for i in range(24)]
    for i, fp in enumerate(poles):
        w.add_trace(
            WTrace(
                f"v(n{i})", 1.0 / (1.0 + 1j * freq / fp), whattype="voltage",
                numerical_type="complex",
            )
        )
    p = tmp_path / "wide_binary.raw"
    w.save(str(p))

    ds = load_result(p)
    assert "ac" in ds.analyses
    an = ds.analyses["ac"]
    assert len(an.signals) == 25
    # sweep detection must survive the lazy binary path: plot.axis only exists after
    # the trace data is read, so probing it too early reported sweep=None (and /wave
    # then fell back to the point index as abscissa)
    assert an.sweep == "frequency"
    # parity: the data survived the bulk-read + copy round-trip
    got = an.signals["v(n0)"].data
    np.testing.assert_allclose(np.asarray(got), 1.0 / (1.0 + 1j * freq / poles[0]), rtol=1e-6)
    # the memory invariant itself
    for sig in an.signals.values():
        arr = np.asarray(sig.data)
        assert arr.base is None, f"{sig.name} is a view — it pins the whole-plot buffer"
