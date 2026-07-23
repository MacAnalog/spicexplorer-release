"""Offline tests for the Spectre gm/ID extraction lane (no Spectre needed).

Covers: registry-driven config (incl. the `simulator` parallelization knobs), deck
generation (NDA-clean — neutral wrapper + generic section only), the pygmid reduction
matrices (the bsim4 igcd/igcs gate-current fold), LUT assembly geometry, the manifest
sidecar, and the CLI wiring (`--dry-run`).
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from spicexplorer_analog_db import cli, gmid_spectre
from spicexplorer_analog_db.gmid_spectre import SpectreGmidConfig

PDK = "FOUNDRY-n65"


@pytest.fixture()
def cfg() -> SpectreGmidConfig:
    return SpectreGmidConfig.from_registry(PDK)


# ── config from the registry gmid block ─────────────────────────────────────────────────────


def test_config_reads_registry_block(cfg: SpectreGmidConfig) -> None:
    assert (cfg.nmos, cfg.pmos) == ("DEVICE", "DEVICE")
    assert cfg.lib_file == "FOUNDRY_n65_models.scs"
    assert cfg.corner == "tt"
    # the fine validated grids
    assert cfg.vgs == (0, 0.025, 1.5)
    assert cfg.vds == (0, 0.025, 1.8)
    assert cfg.length_um[0] == pytest.approx(0.06)
    # licensed kit → out-of-repo output root
    assert ".spicexplorer" in str(cfg.out_root)


def test_config_simulator_knobs_and_overrides() -> None:
    cfg = SpectreGmidConfig.from_registry(PDK)
    assert cfg.workers == 12  # gmid.simulator.workers
    assert cfg.timeout_s == 1200  # gmid.simulator.timeout_s
    over = SpectreGmidConfig.from_registry(PDK, workers=3, timeout_s=60, width_um=4.0)
    assert (over.workers, over.timeout_s, over.width_um) == (3, 60, 4.0)


def test_config_rejects_unknown_corner_and_ngspice_pdk() -> None:
    with pytest.raises(ValueError, match="corner 'xx' not in registry"):
        SpectreGmidConfig.from_registry(PDK, corner="xx")
    # an ngspice-routed PDK must be steered to the open-lane tool
    with pytest.raises(ValueError, match="use `analog-db gmid-extract`"):
        SpectreGmidConfig.from_registry("ihp-sg13g2")


def test_axes_shapes(cfg: SpectreGmidConfig) -> None:
    ax = gmid_spectre.axes(cfg)
    assert len(ax["VGS"]) == 61 and len(ax["VDS"]) == 73 and len(ax["VSB"]) == 11
    assert ax["VGS"][1] - ax["VGS"][0] == pytest.approx(0.025)


# ── deck generation ─────────────────────────────────────────────────────────────────────────


def test_deck_is_nda_clean_and_well_formed(cfg: SpectreGmidConfig) -> None:
    deck = gmid_spectre.build_deck(cfg, l_um=0.5, vsb=0.2)
    # neutral wrapper + GENERIC section only — never a kit path or kit section name
    assert 'FOUNDRY_n65_models.scs" section=tt' in deck
    assert "KIT65" not in deck.lower() and "/CMC" not in deck
    # both polarities, mirrored biases, nested sweep{dc}
    assert "XMN (vdn vgn 0 vbn) DEVICE" in deck
    assert "XMP (vdp vgp 0 vbp) DEVICE" in deck
    assert "vbsn (vbn 0) vsource dc=-sb" in deck and "vbsp (vbp 0) vsource dc=sb" in deck
    assert "sweepvds sweep param=ds" in deck and "sweepvgs dc param=gs" in deck
    # the gate-current channel components are in the save list (the 100× fix)
    for probe in ("XMN:igcd", "XMN:igcs", "XMP:igcd", "XMP:igcs"):
        assert probe in deck


# ── reduction / assembly (synthetic job data, no simulator) ─────────────────────────────────


def _tiny_cfg() -> SpectreGmidConfig:
    cfg = SpectreGmidConfig.from_registry(PDK)
    cfg.vgs, cfg.vds, cfg.vsb = (0, 0.5, 1.0), (0, 0.6, 1.2), (0, 0.4, 0.4)
    cfg.length_um = [0.5, 1.0]
    return cfg


def _fake_jobs(cfg: SpectreGmidConfig) -> dict:
    ax = gmid_spectre.axes(cfg)
    shape = (len(ax["VGS"]), len(ax["VDS"]))
    jobs = {}
    for i in range(len(ax["L"])):
        for j in range(len(ax["VSB"])):
            data = {}
            for p in ("N", "P"):
                sgn = 1.0 if p == "N" else -1.0  # odd quantities come back sign-mirrored
                data[f"XM{p}:ids"] = sgn * np.full(shape, 1e-5)
                data[f"XM{p}:vth"] = sgn * np.full(shape, 0.3)
                data[f"XM{p}:igd"] = sgn * np.full(shape, 1e-9)
                data[f"XM{p}:igcd"] = sgn * np.full(shape, 1e-7)  # channel ≫ edge
                data[f"XM{p}:igs"] = sgn * np.full(shape, 2e-9)
                data[f"XM{p}:igcs"] = sgn * np.full(shape, 2e-7)
                for q in ("gm", "gmbs", "gds", "cgg"):
                    data[f"XM{p}:{q}"] = np.full(shape, 1.0)
                for q in ("cgs", "csg", "cgd", "cdg", "cgb"):
                    data[f"XM{p}:{q}"] = np.full(shape, -2.0)  # bsim4 intrinsic caps negative
                data[f"XM{p}:cdd"] = np.full(shape, 3.0)
                data[f"XM{p}:css"] = np.full(shape, 4.0)
                data[f"XM{p}:cjd"] = np.full(shape, 0.5)
                data[f"XM{p}:cjs"] = np.full(shape, 0.25)
            jobs[i, j] = data
    return jobs


def test_assemble_folds_gate_current_and_signs() -> None:
    cfg = _tiny_cfg()
    jobs = _fake_jobs(cfg)
    for pol in ("n", "p"):
        lut = gmid_spectre.assemble(cfg, jobs, pol)
        assert lut["ID"].shape == (2, 3, 3, 2)  # (L, VGS, VDS, VSB)
        # odd quantities are stored POSITIVE for both polarities (Murmann convention)
        assert np.all(lut["ID"] > 0) and np.all(lut["VT"] > 0)
        # IGD/IGS are the TOTALS: edge + channel (1n+100n / 2n+200n)
        assert lut["IGD"].flat[0] == pytest.approx(1.01e-7)
        assert lut["IGS"].flat[0] == pytest.approx(2.02e-7)
        # cap conventions: intrinsic sign flip; junction folded into CDD/CSS
        assert lut["CGS"].flat[0] == pytest.approx(2.0)
        assert lut["CDD"].flat[0] == pytest.approx(3.5)
        assert lut["CSS"].flat[0] == pytest.approx(4.25)
        # noise keys intentionally absent (fail-loud, not silent zeros)
        assert "STH" not in lut and "SFL" not in lut


def test_manifest_sidecar(tmp_path) -> None:
    cfg = _tiny_cfg()
    cfg.out_root = tmp_path
    lut = gmid_spectre.assemble(cfg, _fake_jobs(cfg), "n")
    path = gmid_spectre.write_lut(cfg, lut, "n")
    man_path = gmid_spectre.write_manifest(cfg, lut, "n", extracted_at="2026-07-22T00:00:00+00:00")
    assert path.name == "DEVICE__tt.pkl" and path.parent.name == PDK
    man = json.loads(man_path.read_text())
    assert man["schema"] == "spicexplorer/gmid-lut@1"
    assert man["model"]["corner_lines"] == ['include "FOUNDRY_n65_models.scs" section=tt']
    assert man["dimensions"]["VSB_V"]["stored"] == "magnitude"
    assert "IGD" in man["params"] and "STH" not in man["params"]
    assert man["provenance"]["tool"] == "analog-db gmid-extract-spectre"


# ── CLI wiring ──────────────────────────────────────────────────────────────────────────────


def test_cli_dry_run_prints_deck(capsys) -> None:
    rc = cli.main(["gmid-extract-spectre", "--pdk", PDK, "--dry-run"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "sweepvds sweep param=ds" in out and "DEVICE" in out and "DEVICE" in out


def test_cli_rejects_open_pdk(capsys) -> None:
    rc = cli.main(["gmid-extract-spectre", "--pdk", "ihp-sg13g2", "--dry-run"])
    assert rc == 2
    assert "gmid-extract" in capsys.readouterr().err
