"""Tests for the typed LUT manifest models and LUTRegistry.

All fast (no SPICE, no DB import).  The fixture manifest is the committed sky130 NMOS sidecar
copied to ``tests/fixtures/`` — the same approach as the LUT fixtures.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path

import pytest
from spicexplorer_gmid import (
    AxisSpec,
    DeviceTable,
    GmidError,
    LUTManifest,
    LUTRegistry,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SKY130_PKL = FIXTURES / "sky130_fd_pr__nfet_01v8__tt.pkl"
SKY130_MAN = FIXTURES / "sky130_fd_pr__nfet_01v8__tt.manifest.json"


# ── LUTManifest (typed model) ─────────────────────────────────────────────────────────────────────


def test_manifest_loads_from_committed_sidecar():
    m = LUTManifest.from_path(SKY130_MAN)
    assert m.pdk == "sky130"
    assert m.device == "sky130_fd_pr__nfet_01v8"
    assert m.model_family == "bsim4"
    assert m.polarity == "n"
    assert m.corner == "tt"


def test_manifest_model_record():
    m = LUTManifest.from_path(SKY130_MAN)
    assert m.model.corner_lines == [".lib sky130.lib.spice tt"]
    assert m.model.variant_override is None
    assert "sky130" in m.model.info.lower()


def test_manifest_conditions():
    m = LUTManifest.from_path(SKY130_MAN)
    assert m.conditions.temp_k == pytest.approx(300.0)
    assert m.conditions.width_um == pytest.approx(5.0)
    assert m.conditions.nfing == 1


def test_manifest_dimensions_typed():
    m = LUTManifest.from_path(SKY130_MAN)

    l_ax = m.axis("L_um")
    assert isinstance(l_ax, AxisSpec)
    assert l_ax.n == 8
    assert l_ax.min == pytest.approx(0.15)
    assert l_ax.max == pytest.approx(4.0)
    assert l_ax.step is None  # non-uniform → no step
    assert l_ax.values is not None and len(l_ax.values) == 8

    vgs_ax = m.axis("VGS_V")
    assert vgs_ax.n == 37
    assert vgs_ax.step == pytest.approx(0.05)
    assert vgs_ax.values is None  # uniform → no explicit values

    vsb_ax = m.axis("VSB_V")
    assert vsb_ax.stored == "magnitude"  # pmos convention


def test_manifest_params_list():
    m = LUTManifest.from_path(SKY130_MAN)
    assert "GM" in m.params
    assert "ID" in m.params
    assert "CGG" in m.params


def test_manifest_provenance():
    m = LUTManifest.from_path(SKY130_MAN)
    assert m.provenance.tool == "analog-db gmid-extract"
    assert m.provenance.ngspice is not None
    assert m.provenance.extracted_at is not None


def test_manifest_axis_raises_on_unknown_key():
    m = LUTManifest.from_path(SKY130_MAN)
    with pytest.raises(KeyError, match="not in dimensions"):
        m.axis("W_um")


def test_manifest_schema_id_round_trips():
    raw = json.loads(SKY130_MAN.read_text())
    assert raw["schema"] == "spicexplorer/gmid-lut@1"
    m = LUTManifest.from_path(SKY130_MAN)
    assert m.schema_id == "spicexplorer/gmid-lut@1"


# ── DeviceTable.load() manifest auto-discovery ───────────────────────────────────────────────────


def test_device_table_loads_manifest_from_sidecar():
    nch = DeviceTable.load(SKY130_PKL)
    assert nch.manifest is not None
    assert nch.manifest.pdk == "sky130"
    assert nch.manifest.model_family == "bsim4"
    assert nch.manifest.dimensions["L_um"].n == 8


def test_device_table_manifest_is_none_without_sidecar(tmp_path: Path):
    """Loading a .pkl with no adjacent sidecar → manifest is None (not an error)."""
    pkl_copy = tmp_path / "test.pkl"
    shutil.copy(SKY130_PKL, pkl_copy)
    tbl = DeviceTable.load(pkl_copy)
    assert tbl.manifest is None


# ── LUTRegistry ──────────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def registry_root(tmp_path: Path) -> Path:
    """A minimal registry directory tree with the sky130 nmos LUT + manifest."""
    pdk_dir = tmp_path / "sky130"
    pdk_dir.mkdir()
    shutil.copy(SKY130_PKL, pdk_dir)
    shutil.copy(SKY130_MAN, pdk_dir)
    return tmp_path


def test_registry_list_available(registry_root: Path):
    reg = LUTRegistry(registry_root)
    luts = reg.list_available()
    assert len(luts) == 1
    assert luts[0].pdk == "sky130"
    assert luts[0].device == "sky130_fd_pr__nfet_01v8"


def test_registry_list_available_pdk_filter(registry_root: Path):
    reg = LUTRegistry(registry_root)
    assert len(reg.list_available("sky130")) == 1
    assert len(reg.list_available("ihp-sg13g2")) == 0


def test_registry_find(registry_root: Path):
    reg = LUTRegistry(registry_root)
    m = reg.find("sky130", "sky130_fd_pr__nfet_01v8")
    assert m.corner == "tt"
    assert m.conditions.temp_k == pytest.approx(300.0)


def test_registry_find_missing_raises_key_error(registry_root: Path):
    reg = LUTRegistry(registry_root)
    with pytest.raises(KeyError, match="sky130"):
        reg.find("sky130", "sky130_fd_pr__nfet_01v8", corner="ss")


def test_registry_load_attaches_manifest(registry_root: Path):
    reg = LUTRegistry(registry_root)
    nch = reg.load("sky130", "sky130_fd_pr__nfet_01v8")
    assert nch.manifest is not None
    assert nch.manifest.corner == "tt"
    assert nch.manifest.dimensions["VGS_V"].step == pytest.approx(0.05)


def test_registry_list_skips_corrupt_sidecar(registry_root: Path, tmp_path: Path):
    """A corrupt manifest JSON is skipped (with a logged warning) — the catalog never raises."""
    bad = registry_root / "sky130" / "bad_device__tt.manifest.json"
    bad.write_text("not valid json{")
    reg = LUTRegistry(registry_root)
    luts = reg.list_available("sky130")
    assert all(l.device != "bad_device" for l in luts)  # noqa: E741


# ── GM-4: an unreadable sidecar is reported, and only a corrupt FILE is absorbed ─────────────────


def _schema_drifted_pair(dest_dir: Path) -> Path:
    """The committed fixture pair copied into ``dest_dir``, its manifest's ``schema`` key renamed.

    A schema-field rename is the realistic way a sidecar stops validating: the ``.pkl`` next to it
    is untouched and loads fine. Returns the sidecar path.
    """
    shutil.copy(SKY130_PKL, dest_dir)
    man = json.loads(SKY130_MAN.read_text())
    man["schema_v2"] = man.pop("schema")
    sidecar = dest_dir / SKY130_MAN.name
    sidecar.write_text(json.dumps(man))
    return sidecar


def test_device_table_load_warns_about_an_unreadable_sidecar(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """The load still succeeds (the table is fine), but the sidecar it could not read is named.

    ``except Exception: pass`` turned the rename into ``manifest=None`` with no warning, on every
    load of every LUT, while ``LUTManifest.from_path`` raises ``ValidationError: schema Field
    required`` on the very same file.
    """
    sidecar = _schema_drifted_pair(tmp_path)
    with caplog.at_level(logging.WARNING):
        tbl = DeviceTable.load(tmp_path / SKY130_PKL.name)
    assert tbl.manifest is None
    assert str(sidecar) in caplog.text


def test_registry_list_warns_about_the_sidecar_it_skips(
    registry_root: Path, caplog: pytest.LogCaptureFixture
):
    """The catalog still never raises on a corrupt sidecar — but the LUT it drops is reported."""
    sidecar = _schema_drifted_pair(registry_root / "sky130")
    with caplog.at_level(logging.WARNING):
        luts = LUTRegistry(registry_root).list_available("sky130")
    assert luts == []
    assert str(sidecar) in caplog.text


def _reader_bug(cls: type[LUTManifest], path: Path | str) -> LUTManifest:
    raise TypeError("a bug in the sidecar reader, not a corrupt sidecar")


@pytest.mark.parametrize("entry", ["DeviceTable.load", "LUTRegistry.list_available"])
def test_an_unexpected_sidecar_error_is_not_swallowed(
    registry_root: Path, monkeypatch: pytest.MonkeyPatch, entry: str
):
    """Only the failures of a corrupt FILE are absorbed; anything else is a bug and propagates."""
    monkeypatch.setattr(LUTManifest, "from_path", classmethod(_reader_bug))
    with pytest.raises(TypeError, match="bug in the sidecar reader"):
        if entry == "DeviceTable.load":
            DeviceTable.load(registry_root / "sky130" / SKY130_PKL.name)
        else:
            LUTRegistry(registry_root).list_available()


# Each way a sidecar FILE can be corrupt, reached through a real file (not a monkeypatch): together
# they exercise every type in ``_load_sidecar``'s tuple — pydantic's ValidationError (which is also
# how it reports malformed JSON), UnicodeDecodeError from ``read_text``, and OSError below.
_CORRUPT_SIDECARS = [
    pytest.param(b"", id="empty-ValidationError"),
    pytest.param(b'{"schema": "gmid-lut-manifest/1", ', id="truncated-json-ValidationError"),
    pytest.param(b"\xff\xfe{\x00}\x00", id="not-utf8-UnicodeDecodeError"),
]


@pytest.mark.parametrize("content", _CORRUPT_SIDECARS)
def test_device_table_load_survives_every_corrupt_sidecar_file(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, content: bytes
):
    """The table loads, ``manifest`` is ``None``, and the warning names the file — for bytes that
    are not UTF-8 (``read_text`` raises before pydantic sees anything) as for JSON that does not
    validate."""
    shutil.copy(SKY130_PKL, tmp_path)
    sidecar = tmp_path / SKY130_MAN.name
    sidecar.write_bytes(content)
    with caplog.at_level(logging.WARNING, logger="spicexplorer_gmid.tables"):
        tbl = DeviceTable.load(tmp_path / SKY130_PKL.name)
    assert tbl.manifest is None
    assert tbl.L_grid.size == 8  # the table itself is untouched by its sidecar
    assert str(sidecar) in caplog.text and "unreadable LUT manifest sidecar" in caplog.text


@pytest.mark.parametrize("content", _CORRUPT_SIDECARS)
def test_registry_list_skips_every_corrupt_sidecar_file_and_keeps_the_good_one(
    registry_root: Path, caplog: pytest.LogCaptureFixture, content: bytes
):
    bad = registry_root / "sky130" / "bad_device__tt.manifest.json"
    bad.write_bytes(content)
    with caplog.at_level(logging.WARNING, logger="spicexplorer_gmid.tables"):
        luts = LUTRegistry(registry_root).list_available()
    assert [m.device for m in luts] == ["sky130_fd_pr__nfet_01v8"]
    assert str(bad) in caplog.text


def test_registry_list_skips_a_sidecar_path_it_cannot_read(
    registry_root: Path, caplog: pytest.LogCaptureFixture
):
    """An ``OSError`` is a corrupt-file failure too: a *directory* that matches the sidecar glob
    raises ``IsADirectoryError`` from ``read_text`` — skipped and named, the real LUT still listed."""
    odd = registry_root / "sky130" / "ghost_device__tt.manifest.json"
    odd.mkdir()
    with caplog.at_level(logging.WARNING, logger="spicexplorer_gmid.tables"):
        luts = LUTRegistry(registry_root).list_available("sky130")
    assert [m.device for m in luts] == ["sky130_fd_pr__nfet_01v8"]
    assert str(odd) in caplog.text


@pytest.mark.skipif(
    not hasattr(os, "geteuid") or os.geteuid() == 0, reason="root reads a mode-000 file anyway"
)
def test_device_table_load_survives_a_sidecar_it_may_not_read(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    """``DeviceTable.load`` reads a sidecar only if ``is_file()``, so its ``OSError`` is a file that
    exists but cannot be opened — permission denied: warned, not fatal to the load."""
    shutil.copy(SKY130_PKL, tmp_path)
    sidecar = tmp_path / SKY130_MAN.name
    shutil.copy(SKY130_MAN, sidecar)
    sidecar.chmod(0)
    try:
        with caplog.at_level(logging.WARNING, logger="spicexplorer_gmid.tables"):
            tbl = DeviceTable.load(tmp_path / SKY130_PKL.name)
    finally:
        sidecar.chmod(0o644)
    assert tbl.manifest is None
    assert str(sidecar) in caplog.text


def test_a_readable_sidecar_logs_nothing(registry_root: Path, caplog: pytest.LogCaptureFixture):
    """The warning is for the unreadable case only — a good sidecar loads with no warning."""
    with caplog.at_level(logging.WARNING, logger="spicexplorer_gmid.tables"):
        tbl = DeviceTable.load(registry_root / "sky130" / SKY130_PKL.name)
        luts = LUTRegistry(registry_root).list_available()
    assert tbl.manifest is not None and len(luts) == 1
    assert caplog.records == []


# ── G-6: suffixed LUTs (__<T>C temperature / __wf<W>u finger width) ──────────────────────────────
#
# The LUT extractor tags a filename whenever it is off the historic nominal (27 °C, a 5 µm finger).
# The registry could only ever build "<device>__<corner>", so those variants were unaddressable.

DEVICE = "sky130_fd_pr__nfet_01v8"


def _variant(
    pdk_dir: Path, stem: str, *, width_um: float | None = None, temp_k: float | None = None
) -> None:
    """Drop a `<stem>.pkl` + `<stem>.manifest.json` pair, mirroring what the extractor writes.

    ``lut_file`` is left at the un-suffixed name **on purpose**: analog-db's ``build_manifest``
    hardcodes ``f"{device}__{corner}.pkl"``, so every tagged manifest on disk names the wrong data
    file. The registry must not resolve the ``.pkl`` through that field.
    """
    shutil.copy(SKY130_PKL, pdk_dir / f"{stem}.pkl")
    man = json.loads(SKY130_MAN.read_text())
    if width_um is not None:
        man["conditions"]["width_um"] = width_um
    if temp_k is not None:
        man["conditions"]["temp_k"] = temp_k
    (pdk_dir / f"{stem}.manifest.json").write_text(json.dumps(man))


@pytest.fixture
def suffixed_root(registry_root: Path) -> Path:
    """The plain 27 °C/5 µm LUT plus a 1 µm-finger and a −40 °C variant."""
    pdk_dir = registry_root / "sky130"
    _variant(pdk_dir, f"{DEVICE}__tt__wf1u", width_um=1.0)
    _variant(pdk_dir, f"{DEVICE}__tt__-40C", temp_k=233.15)
    return registry_root


def test_registry_find_addresses_a_finger_width_variant(suffixed_root: Path):
    reg = LUTRegistry(suffixed_root)
    m = reg.find("sky130", DEVICE, wf_um=1.0)
    assert m.conditions.width_um == pytest.approx(1.0)
    assert reg.find("sky130", DEVICE).conditions.width_um == pytest.approx(5.0)  # untagged default


def test_registry_find_addresses_a_temperature_variant(suffixed_root: Path):
    reg = LUTRegistry(suffixed_root)
    assert reg.find("sky130", DEVICE, temp_c=-40).conditions.temp_k == pytest.approx(233.15)
    # the nominal is spelled with NO suffix, so asking for it explicitly finds the plain file
    assert reg.find("sky130", DEVICE, temp_c=27).conditions.temp_k == pytest.approx(300.0)
    assert reg.find("sky130", DEVICE, wf_um=5.0).conditions.width_um == pytest.approx(5.0)


def test_registry_load_reads_the_addressed_pkl_not_the_manifests_lut_file(suffixed_root: Path):
    """The tagged sidecars all say ``lut_file: sky130_fd_pr__nfet_01v8__tt.pkl`` — the wrong file."""
    reg = LUTRegistry(suffixed_root)
    tbl = reg.load("sky130", DEVICE, wf_um=1.0)
    assert tbl.source is not None and tbl.source.name == f"{DEVICE}__tt__wf1u.pkl"
    assert tbl.manifest is not None and tbl.manifest.conditions.width_um == pytest.approx(1.0)


def test_registry_load_will_not_substitute_the_untagged_pkl(suffixed_root: Path):
    """A tagged manifest whose own .pkl is missing must raise — never fall back to the nominal one."""
    (suffixed_root / "sky130" / f"{DEVICE}__tt__wf1u.pkl").unlink()
    reg = LUTRegistry(suffixed_root)
    with pytest.raises(FileNotFoundError, match="wf1u"):
        reg.load("sky130", DEVICE, wf_um=1.0)


def test_registry_find_missing_variant_lists_the_tagged_stems(suffixed_root: Path):
    reg = LUTRegistry(suffixed_root)
    with pytest.raises(KeyError) as exc:
        reg.find("sky130", DEVICE, wf_um=0.5)
    listed = str(exc.value)
    assert "wf0p5u" in listed and "wf1u" in listed and "-40C" in listed


def test_registry_rejects_a_mis_tagged_variant(registry_root: Path):
    """A file named for 1 µm whose sidecar records 5 µm is a data-integrity error, not a table."""
    _variant(registry_root / "sky130", f"{DEVICE}__tt__wf1u")  # conditions left at 5 µm
    reg = LUTRegistry(registry_root)
    with pytest.raises(GmidError, match="refusing to serve"):
        reg.find("sky130", DEVICE, wf_um=1.0)
