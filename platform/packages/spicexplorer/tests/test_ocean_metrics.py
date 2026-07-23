"""Offline tests — OCEAN metrics emitter, parser, and the persistent-session machinery.

No Cadence anywhere: the session tests drive `OceanMetricsSession` against
`tests/fake_ocean.py` (a python stand-in that answers the emitted SKILL blocks), so the
pipe/poll/respawn/timeout logic is fully exercised in the fast suite. The real-ocean
counterpart lives in `test_ocean_metrics_live.py` (opt-in, needs Cadence).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
from spicexplorer.backends.ocean_metrics import (
    OceanMeasurement,
    OceanMetricsError,
    OceanMetricsSession,
    ac_bandwidth_3db,
    ac_gain_db_at,
    ac_peak_mag,
    device_op_param,
    op_node_voltage,
    parse_metrics_text,
    render_measure_block,
)

FAKE_OCEAN = Path(__file__).parent / "fake_ocean.py"


def _fake_session(tmp_path: Path, **kwargs) -> OceanMetricsSession:
    return OceanMetricsSession(
        work_dir=tmp_path / "work",
        _argv=[sys.executable, str(FAKE_OCEAN)],
        **kwargs,
    )


# -- measurement defs ---------------------------------------------------------
def test_measurement_validation() -> None:
    with pytest.raises(ValueError, match="name"):
        OceanMeasurement("bad name", "ac", "1")
    with pytest.raises(ValueError, match="result"):
        OceanMeasurement("ok", 'ac"', "1")
    with pytest.raises(ValueError, match="one non-empty SKILL line"):
        OceanMeasurement("ok", "ac", "1\n2")


def test_helpers_strip_leading_slash() -> None:
    # naming truth: headless-raw signals are BARE — v("/v_out") is OCN-6054
    m = ac_gain_db_at("gain_db", "/v_out", 1e3)
    assert 'v("v_out")' in m.expr and "/v_out" not in m.expr
    assert 'OP("XOTA.XM1" "gm")' in device_op_param("gm1", "/XOTA.XM1", "gm").expr


# -- emitter -------------------------------------------------------------------
def test_render_block_shape(tmp_path: Path) -> None:
    ms = [
        ac_gain_db_at("gain_db", "v_out", 1e3),
        ac_bandwidth_3db("bw_hz", "v_out"),
        op_node_voltage("vtail", "XOTA.tail"),
        device_op_param("gm1", "XOTA.XM1", "gm"),
    ]
    block = render_measure_block(tmp_path, ms, tmp_path / "out.metrics")
    # one openResults, one selectResults per result GROUP, in measurement order
    assert block.count("openResults(") == 1
    assert block.count('selectResults("ac")') == 1  # gain_db + bw_hz share one select
    assert block.index('selectResults("ac")') < block.index('selectResults("dc")')
    assert block.index('selectResults("dc")') < block.index('selectResults("dcOpInfo")')
    # every metric has a NaN fallback and the sentinel closes the file
    for name in ("gain_db", "bw_hz", "vtail", "gm1"):
        assert f'"{name}=NaN\\n"' in block
    assert "__spicexplorer_ocean_done__=1" in block
    assert block.rstrip().endswith("close(__sxq_port)")


def test_render_block_rejects_duplicates_and_unsafe_paths(tmp_path: Path) -> None:
    m = ac_peak_mag("peak", "v_out")
    with pytest.raises(ValueError, match="duplicate"):
        render_measure_block(tmp_path, [m, m], tmp_path / "o")
    with pytest.raises(ValueError, match="unsafe"):
        render_measure_block('raw"dir', [m], tmp_path / "o")
    with pytest.raises(ValueError, match="at least one"):
        render_measure_block(tmp_path, [], tmp_path / "o")


# -- parser ---------------------------------------------------------------------
def test_parse_metrics_text() -> None:
    text = (
        "gain_db=-1.3473800000e+00\n"
        "bw_hz=1.8126900000e+07\n"
        "pm_deg=NaN\n"
        "some ocean chatter > that is not a metric\n"
        "__spicexplorer_ocean_done__=1\n"
    )
    parsed = parse_metrics_text(text)
    assert parsed["gain_db"] == pytest.approx(-1.34738)
    assert parsed["bw_hz"] == pytest.approx(1.81269e7)
    assert math.isnan(parsed["pm_deg"])
    assert "__spicexplorer_ocean_done__" not in parsed
    assert len(parsed) == 3


# -- session against the fake ocean ---------------------------------------------
def test_session_roundtrip_and_warm_reuse(tmp_path: Path) -> None:
    raw = tmp_path / "cand.raw"
    raw.mkdir()
    ms = [ac_gain_db_at("gain_db", "v_out", 1e3), device_op_param("gm1", "XOTA.XM1", "gm")]
    with _fake_session(tmp_path) as sess:
        assert not sess.is_alive  # lazy spawn
        first = sess.measure(raw, ms, label="cand a")  # label sanitized into the filename
        assert first == {"gain_db": 42.0, "gm1": 42.0}
        # audit trail: the submitted SKILL persists beside the metrics file
        assert (tmp_path / "work" / "0001_cand_a.il").read_text().startswith("setq(__sxq_port")
        assert sess.is_alive and sess.last_eval_seconds is not None
        pid = sess._proc.pid  # type: ignore[union-attr]
        second = sess.measure(raw, ms)
        assert second == {"gain_db": 42.0, "gm1": 42.0}
        assert sess._proc is not None and sess._proc.pid == pid  # warm reuse, no respawn
    assert not sess.is_alive  # close() ended the process


def test_session_missing_raw_dir(tmp_path: Path) -> None:
    with _fake_session(tmp_path) as sess:
        with pytest.raises(OceanMetricsError, match="raw dir"):
            sess.measure(tmp_path / "nope.raw", [ac_peak_mag("peak", "v_out")])


def test_session_respawns_after_death(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SXQ_FAKE_DIE_AFTER", "1")
    raw = tmp_path / "cand.raw"
    raw.mkdir()
    ms = [ac_peak_mag("peak", "v_out")]
    with _fake_session(tmp_path) as sess:
        assert sess.measure(raw, ms) == {"peak": 42.0}
        pid = sess._proc.pid  # type: ignore[union-attr]
        sess._proc.wait(timeout=10)  # type: ignore[union-attr]  # fake exits after write
        assert sess.measure(raw, ms) == {"peak": 42.0}  # transparent respawn
        assert sess._proc is not None and sess._proc.pid != pid


def test_session_timeout_kills_and_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SXQ_FAKE_HANG", "1")
    raw = tmp_path / "cand.raw"
    raw.mkdir()
    with _fake_session(tmp_path, startup_timeout=0.3, eval_timeout=0.3) as sess:
        with pytest.raises(OceanMetricsError, match="timed out"):
            sess.measure(raw, [ac_peak_mag("peak", "v_out")])
        assert not sess.is_alive  # a hung ocean is killed, never left holding a license


# -- cshrc resolution -------------------------------------------------------------
def test_from_vb_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VB_CADENCE_CSHRC", raising=False)
    cshrc = tmp_path / "cadence.cshrc"
    cshrc.write_text("# fake cshrc\n")
    env_file = tmp_path / "local.env"
    env_file.write_text(f'export VB_CADENCE_CSHRC="{cshrc}"\n')
    sess = OceanMetricsSession.from_vb_env(env_file, work_dir=tmp_path / "w")
    assert str(cshrc) in " ".join(sess._argv)
    sess.close()

    with pytest.raises(OceanMetricsError, match="VB_CADENCE_CSHRC"):
        OceanMetricsSession.from_vb_env(tmp_path / "absent.env")


def test_ctor_requires_existing_cshrc(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        OceanMetricsSession(tmp_path / "missing.cshrc")
    with pytest.raises(ValueError, match="cshrc is required"):
        OceanMetricsSession()


def test_session_measure_batch_one_submission(tmp_path: Path) -> None:
    # batching: N candidates ride ONE stdin submission; results come back in order
    raws = []
    for i in range(3):
        r = tmp_path / f"cand{i}.raw"
        r.mkdir()
        raws.append(r)
    ms = [ac_peak_mag("peak", "v_out")]
    with _fake_session(tmp_path) as sess:
        out = sess.measure_batch(raws, ms, label="gen 0")
        assert out == [{"peak": 42.0}] * 3
        pid = sess._proc.pid  # type: ignore[union-attr]
        assert sess.measure_batch(raws[:2], ms) == [{"peak": 42.0}] * 2
        assert sess._proc is not None and sess._proc.pid == pid  # warm reuse across batches
        assert sess.measure_batch([], ms) == []
        with pytest.raises(OceanMetricsError, match="raw dir"):
            sess.measure_batch([tmp_path / "nope.raw"], ms)
