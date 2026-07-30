"""Trace snapshots + PNG/HTML export (snapshot.py) — offline, both engines.

The synthetic fixtures cover every template kind: the Spectre raw dir carries
ac / dc / tran / noise / pss / stb sweeps plus op-point data (which must be SKIPPED,
not fail), the ngspice fixtures a single-pole AC and a first-order transient.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from spicexplorer_waveview import (
    PLOT_TEMPLATES,
    PlotTemplate,
    export_htmls,
    export_pngs,
    load_result,
    load_traces,
    save_traces,
    snapshot,
)
from spicexplorer_waveview.testing import synth_ac_raw, synth_spectre_raw_dir, synth_tran_raw


@pytest.fixture()
def spectre_ds(tmp_path: Path):
    synth_spectre_raw_dir(tmp_path / "raw")
    return load_result(tmp_path / "raw")


# ------------------------------------------------------------------ trace store
def test_traces_roundtrip_is_faithful(spectre_ds, tmp_path: Path) -> None:
    out = save_traces(spectre_ds, tmp_path / "run.traces.npz", label="rt")
    back = load_traces(out)
    assert back.engine == spectre_ds.engine and back.source == spectre_ds.source
    assert set(back.analyses) == set(spectre_ds.analyses)
    for key, an in spectre_ds.analyses.items():
        b = back.analyses[key]
        assert b.sweep == an.sweep and set(b.signals) == set(an.signals)
        assert b.scalars == pytest.approx(an.scalars)
        for name, sig in an.signals.items():
            got = b.signals[name].data
            assert got.dtype.kind == np.asarray(sig.data).dtype.kind  # complex survives
            np.testing.assert_allclose(got, sig.data)


def test_traces_selection_keeps_the_sweep(spectre_ds, tmp_path: Path) -> None:
    out = save_traces(
        spectre_ds, tmp_path / "sel.npz", analyses=["ac"], signals={"ac": ["vout"]}
    )
    back = load_traces(out)
    assert set(back.analyses) == {"ac"}
    an = back.analyses["ac"]
    assert an.sweep in an.signals, "the abscissa must always ride along"
    assert set(an.signals) == {an.sweep, "vout"}


def test_traces_version_guard(spectre_ds, tmp_path: Path) -> None:
    out = save_traces(spectre_ds, tmp_path / "v.npz")
    with np.load(out) as npz:
        manifest = json.loads(str(npz["__manifest__"][()]))
        arrays = {k: npz[k] for k in npz.files if k != "__manifest__"}
    manifest["version"] = 99
    np.savez_compressed(out, __manifest__=np.array(json.dumps(manifest)), **arrays)
    with pytest.raises(ValueError, match="version"):
        load_traces(out)


def test_stored_traces_feed_the_measurement_registry(spectre_ds, tmp_path: Path) -> None:
    # the round-trip is a real WaveDataset: Tier-1 recipes evaluate on stored traces
    from spicexplorer_core.measurements import measure
    from spicexplorer_waveview import DatasetResult

    back = load_traces(save_traces(spectre_ds, tmp_path / "m.npz"))
    res = DatasetResult(back)
    gain = measure(res, {"meas": "dcgain", "out": "vout"}, default_analysis="ac")
    assert np.isfinite(gain)


# ------------------------------------------------------------------ PNG export
def test_export_pngs_covers_every_swept_kind_and_skips_point_data(
    spectre_ds, tmp_path: Path
) -> None:
    skipped: list[tuple[str, str]] = []
    written = export_pngs(
        spectre_ds, tmp_path / "png", on_skip=lambda a, r: skipped.append((a, r))
    )
    names = {p.name for p in written}
    for kind in ("ac", "dc", "tran", "noise", "pss", "stb", "pac"):
        assert any(kind in n for n in names), f"no PNG for {kind}: {names}"
    for p in written:
        assert p.stat().st_size > 1024, f"suspiciously small PNG: {p}"
    assert any("op" in a for a, _ in skipped), "op-point data should be skipped, not fail"


def test_ngspice_ac_and_tran_render(tmp_path: Path) -> None:
    synth_ac_raw(tmp_path / "ac.raw")
    synth_tran_raw(tmp_path / "tran.raw")
    for stem in ("ac", "tran"):
        ds = load_result(tmp_path / f"{stem}.raw")
        written = export_pngs(ds, tmp_path / "png", prefix=f"{stem}_")
        assert written and all(p.stat().st_size > 1024 for p in written)


def test_template_override_per_analysis(spectre_ds, tmp_path: Path) -> None:
    # per-analysis template seam: force the ac analysis onto a single-panel xy style
    override = {"ac": PlotTemplate("xy", "custom-ac", x_label="f [Hz]")}
    written = export_pngs(spectre_ds, tmp_path / "png", analyses=["ac"], templates=override)
    assert len(written) == 1 and written[0].stat().st_size > 1024
    # the default table is untouched
    assert PLOT_TEMPLATES["ac"].style == "bode"


def test_per_signal_breakouts_and_combined(spectre_ds, tmp_path: Path) -> None:
    """A multi-trace analysis writes the combined image PLUS one autoscaled breakout
    per selected trace (a mV ripple next to a rail is invisible on shared axes);
    per_signal=False keeps the combined image only."""
    written = export_pngs(spectre_ds, tmp_path / "brk", analyses=["dc"])
    names = sorted(p.name for p in written)
    assert "dc.png" in names, names
    assert "dc.vin.png" in names and "dc.vout.png" in names, names
    combined_only = export_pngs(
        spectre_ds, tmp_path / "single", analyses=["dc"], per_signal=False
    )
    assert [p.name for p in combined_only] == ["dc.png"]


def test_noise_selection_keeps_densities_only(spectre_ds, tmp_path: Path) -> None:
    """The noise family plots DENSITY signals only: Spectre's `gain` transfer curve
    (input-referral bookkeeping) must stay out of the V/√Hz plot."""
    written = export_pngs(spectre_ds, tmp_path / "png", analyses=["noise"])
    names = {p.name for p in written}
    assert "noise.out.png" in names and "noise.in.png" in names, names
    assert not any(".gain." in n for n in names), names


def test_zero_traces_are_dropped(tmp_path: Path) -> None:
    """Numerically-zero traces (AC-grounded rails) draw only the −6000 dB log floor
    and squash the real transfer — the default selection drops them."""
    from spicexplorer_waveview.testing import _write_swept

    d = tmp_path / "dead-raw"
    d.mkdir()
    f = np.logspace(0, 6, 21)
    _write_swept(d / "ac.ac", "ac", "ac", "freq", "Hz", f,
                 {"vout": (100.0 / (1 + 1j * f / 1e3)), "vmid": (1.0 / (1 + 1j * f / 1e3)),
                  "vdd": np.zeros(21, dtype=complex)})
    written = export_pngs(load_result(d), tmp_path / "png")
    names = {p.name for p in written}
    assert "ac.vout.png" in names and "ac.vmid.png" in names, names
    assert not any(".vdd." in n for n in names), names


def test_ngspice_derived_vectors_currents_and_osdi_internals_excluded(tmp_path: Path) -> None:
    """An ngspice raw lists deck-derived `let` vectors (dcgain, ph, …), branch currents
    (`i(vdd)`) and OSDI device-internal nodes (`v(n.x…#di)`) next to the real
    `v(<node>)` traces — the default selection keeps the nodes only."""
    from spicexplorer_waveview.testing import write_ngspice_ascii_raw

    f = np.logspace(0, 6, 21)
    h = (100.0 / (1 + 1j * f / 1e3))
    p = tmp_path / "derived.raw"
    write_ngspice_ascii_raw(
        p,
        [("AC Analysis",
          [("frequency", "frequency"), ("v(vout)", "voltage"), ("v(vmid)", "voltage"),
           ("dcgain", "voltage"), ("i(vdd)", "current"),
           ("v(n.xdut.xm0.nsg13_lv_pmos#di)", "voltage")],
          [f.astype(complex), h, h / 10.0, np.full(21, 40.0 + 0j), h / 1e6, h / 1e3])],
    )
    written = export_pngs(load_result(p), tmp_path / "png")
    names = {p2.name for p2 in written}
    assert "ac.v_vout_.png" in names and "ac.v_vmid_.png" in names, names
    assert not any("dcgain" in n or "i_vdd_" in n or "#" in n or "_di_" in n for n in names), names


def test_export_htmls_covers_kinds_and_shares_plotlyjs(spectre_ds, tmp_path: Path) -> None:
    out = tmp_path / "html"
    written = export_htmls(spectre_ds, out, annotations={"ac": {"dcgain [dB]": 60.0}})
    names = {p.name for p in written}
    for kind in ("ac", "dc", "tran", "noise", "pss", "stb", "pac"):
        assert any(kind in n for n in names), f"no HTML for {kind}: {names}"
    # "directory" mode: ONE shared plotly.min.js, so each page stays small
    assert (out / "plotly.min.js").is_file()
    for p in written:
        assert p.stat().st_size < 500_000, f"page embeds plotly.js?: {p}"
    assert "dcgain" in (out / "ac.html").read_text()  # annotations ride the subtitle


def test_annotations_are_stamped(spectre_ds, tmp_path: Path) -> None:
    plain = export_pngs(spectre_ds, tmp_path / "plain", analyses=["ac"])
    annotated = export_pngs(
        spectre_ds, tmp_path / "anno", analyses=["ac"],
        annotations={"ac": {"dcgain [dB]": 40.0, "ugf [Hz]": 1.8e7}},
    )
    assert annotated[0].stat().st_size != plain[0].stat().st_size  # the box drew something


# ------------------------------------------------------------------ the one-liner
def test_snapshot_one_liner(tmp_path: Path) -> None:
    synth_spectre_raw_dir(tmp_path / "raw")
    result = snapshot(tmp_path / "raw", tmp_path / "out", label="demo")
    assert result["traces"] is not None and Path(result["traces"]).is_file()
    assert result["pngs"] and all(Path(p).is_file() for p in result["pngs"])
    assert all(Path(p).name.startswith("demo_") for p in result["pngs"])
    assert result["htmls"] and all(Path(p).is_file() for p in result["htmls"])
    assert (tmp_path / "out" / "plotly.min.js").is_file()
    assert result["skipped"], "op-point analyses report as skipped"
    # the stored traces round-trip standalone
    back = load_traces(result["traces"])
    assert "ac" in back.analyses


def test_snapshot_excludes_pac_sidebands_by_default(tmp_path: Path) -> None:
    """Key traces only: the pac BASEBAND snapshots, the 30-odd sideband PSFs a real
    run leaves stay out unless include_sidebands=True."""
    synth_spectre_raw_dir(tmp_path / "raw")
    default = snapshot(tmp_path / "raw", tmp_path / "d", label="d")
    assert any("_pac." in p.name for p in default["pngs"])  # baseband present
    assert not any("pac_sb" in p.name for p in default["pngs"])
    assert not any("pac_sb" in p.name for p in default["htmls"])
    assert not any("pac_sb" in k for k in load_traces(default["traces"]).analyses)
    full = snapshot(tmp_path / "raw", tmp_path / "f", label="f", include_sidebands=True)
    assert any("pac_sb" in p.name for p in full["pngs"])
