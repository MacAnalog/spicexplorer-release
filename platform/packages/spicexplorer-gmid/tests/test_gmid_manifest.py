"""Tests for the typed LUT manifest models and LUTRegistry.

All fast (no SPICE, no DB import).  The fixture manifest is the committed sky130 NMOS sidecar
copied to ``tests/fixtures/`` — the same approach as the LUT fixtures.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from spicexplorer_gmid import (
    AxisSpec,
    DeviceTable,
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
    assert l_ax.step is None                         # non-uniform → no step
    assert l_ax.values is not None and len(l_ax.values) == 8

    vgs_ax = m.axis("VGS_V")
    assert vgs_ax.n == 37
    assert vgs_ax.step == pytest.approx(0.05)
    assert vgs_ax.values is None                     # uniform → no explicit values

    vsb_ax = m.axis("VSB_V")
    assert vsb_ax.stored == "magnitude"              # pmos convention


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
    """A corrupt manifest JSON is skipped silently — the catalog never raises."""
    bad = registry_root / "sky130" / "bad_device__tt.manifest.json"
    bad.write_text("not valid json{")
    reg = LUTRegistry(registry_root)
    luts = reg.list_available("sky130")
    assert all(l.device != "bad_device" for l in luts)  # noqa: E741
