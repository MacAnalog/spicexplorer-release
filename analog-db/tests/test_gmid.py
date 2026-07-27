"""Unit tests for the gm/ID LUT extraction subsystem (gmid.py) — PDK-free (no ngspice)."""

from __future__ import annotations

import numpy as np
import pytest

from spicexplorer_analog_db import gmid, pdks


# ── config / axes ─────────────────────────────────────────────────────────────────────────────
def test_from_registry_loads_defaults_and_infers_polarity():
    n = gmid.GmidConfig.from_registry("sky130")
    assert n.family == "bsim4" and n.device == "sky130_fd_pr__nfet_01v8" and n.polarity == "n"
    p = gmid.GmidConfig.from_registry("sky130", device="sky130_fd_pr__pfet_01v8")
    assert p.polarity == "p"
    ihp = gmid.GmidConfig.from_registry("ihp-sg13g2")
    assert ihp.family == "psp" and ihp.probe_inst == "n.xm1.nsg13_lv_nmos"


def test_axes_grid_matches_ngspice_compose():
    cfg = gmid.GmidConfig.from_registry("sky130", vgs=(0, 0.5, 1.0), vds=(0, 0.5, 1.0),
                                        vsb=(0, -0.4, -0.4), length_um=[0.15, 1.0])
    ax = gmid.axes(cfg)
    assert list(ax["VGS"]) == [0.0, 0.5, 1.0]
    assert list(ax["VSB"]) == [0.0, 0.4]            # stored positive
    assert list(ax["L"]) == [0.15, 1.0]


# ── deck generation (the per-family branches) ──────────────────────────────────────────────────
def test_deck_bsim4_sky130():
    cfg = gmid.GmidConfig.from_registry("sky130")
    deck, txt = gmid.build_deck(cfg, pdks.load_registry("sky130"))
    assert "XM1 d g 0 b sky130_fd_pr__nfet_01v8" in deck and " nf=1 " in deck   # BSIM4 ports + nf
    # the instance MUST reference the lx/wx params — a literal L would make `alterparam lx` a
    # no-op and every "L" slice identical (the bug the gate notebooks caught)
    assert " L={lx} W={wx} " in deck and "alterparam lx=$var1" in deck
    assert ".noise v(n) vg lin 1 1 1 1" in deck                                  # BSIM4 noise method
    assert "@m.xm1.msky130_fd_pr__nfet_01v8[gmbs]" in deck                       # BSIM4 gmb name + probe
    assert "onoise.m.xm1.msky130_fd_pr__nfet_01v8.1overf" in deck
    assert ".lib sky130.lib.spice tt" in deck and txt.endswith(".txt")


def test_deck_psp_ihp_uses_ng_and_op_and_direct_noise():
    cfg = gmid.GmidConfig.from_registry("ihp-sg13g2")
    deck, _ = gmid.build_deck(cfg, pdks.load_registry("ihp-sg13g2"))
    assert "XM1 0 g d b sg13_lv_nmos" in deck and " ng=1 " in deck               # PSP ports + ng (not nf)
    assert ".op" in deck and ".noise" not in deck                                # PSP: direct sid/sfl, no .noise
    assert "@n.xm1.nsg13_lv_nmos[gmb]" in deck and "@n.xm1.nsg13_lv_nmos[sid]" in deck
    assert ".lib cornerMOSlv.lib mos_tt" in deck                                 # mos_ prefix mapped


def test_deck_pmos_mirrors_bias_polarity():
    cfg = gmid.GmidConfig.from_registry("sky130", device="sky130_fd_pr__pfet_01v8",
                                        vgs=(0, 0.5, 1.5), vds=(0, 0.5, 1.5), vsb=(0, -0.5, -0.5))
    deck, _ = gmid.build_deck(cfg, pdks.load_registry("sky130"))
    # pmos mirrors the biases: vg/vd swept negative (stop = sgn*1.5 + half-step = -1.75, step -0.5)
    assert "stop=-1.75 step=-0.5" in deck
    assert "DC -0 " not in deck and "DC 0 AC 1" in deck                          # zero start not '-0'


# ── HV/LV variant corner resolution (the `gmid.variants` override) ────────────────────────────────
def test_variant_swaps_corner_lib_ihp_hv():
    """An ihp HV device (separate corner lib) resolves cornerMOShv.lib; the LV device keeps lv."""
    lv = gmid.GmidConfig.from_registry("ihp-sg13g2")
    hv = gmid.GmidConfig.from_registry("ihp-sg13g2", device="sg13_hv_nmos")
    assert lv.corner_override == {} and hv.corner_override == {"lib_file": "cornerMOShv.lib"}
    deck_lv, _ = gmid.build_deck(lv, pdks.load_registry("ihp-sg13g2"))
    deck_hv, _ = gmid.build_deck(hv, pdks.load_registry("ihp-sg13g2"))
    assert ".lib cornerMOSlv.lib mos_tt" in deck_lv
    assert ".lib cornerMOShv.lib mos_tt" in deck_hv and "cornerMOSlv.lib" not in deck_hv


def test_variant_swaps_sections_gf180_io():
    """A gf180 6V IO device pulls the `typical` + 06v0 model sections (not the 3.3 V default)."""
    io = gmid.GmidConfig.from_registry("gf180mcu", device="nfet_06v0")
    assert io.corner_override == {
        "includes": ["design.ngspice"],
        "per_corner": {"tt": ["typical", "nfet_06v0_t", "pfet_06v0_t"]},
    }
    deck, _ = gmid.build_deck(io, pdks.load_registry("gf180mcu"))
    assert ".lib sm141064.ngspice nfet_06v0_t" in deck and "nfet_03v3_t" not in deck
    # the statistical/mismatch params the 6V subckt formals reference (2026-07-25)
    assert ".include design.ngspice" in deck


def test_variant_corner_not_available_is_clear_error():
    """The gf180 6V variant is typical-only here → a non-tt corner errors clearly, not a KeyError."""
    io = gmid.GmidConfig.from_registry("gf180mcu", device="pfet_06v0", corner="ss")
    with pytest.raises(ValueError, match="not available for this device"):
        gmid.build_deck(io, pdks.load_registry("gf180mcu"))


# ── txt → LUT parse (synthetic; the reshape + cap/noise reduction) ───────────────────────────────
def _synth_bsim4_txt(rows: list[dict]) -> str:
    """A minimal `wrdata noise1.all`-shaped table (incl. the duplicate `frequency` column)."""
    params = ["id", "gmbs", "vth", "gm", "gds", "cgg", "cgs", "cgd", "cgb",
              "cdd", "css", "cgdo", "cgso", "capbd", "capbs", "l"]
    pre = "@m.xm1.mDEV["
    header = ["frequency"] + [f"{pre}{p}]" for p in params] + ["@vg[dc]", "@vd[dc]", "@vb[dc]",
             "frequency", "onoise.m.xm1.mDEV.id", "onoise.m.xm1.mDEV.1overf"]
    lines = [" ".join(header)]
    for r in rows:
        vals = ["1.0"] + [str(r.get(p, 0.0)) for p in params] + \
               [str(r["vg"]), str(r["vd"]), str(r["vb"]), "1.0", str(r.get("n_id", 0.0)), str(r.get("n_1f", 0.0))]
        lines.append(" ".join(vals))
    return "\n".join(lines) + "\n"


def test_parse_reshapes_and_reduces_caps():
    # 1 L × 2 VGS × 1 VDS × 1 VSB; foreach order = (L,VGS,VDS,VSB) → 2 rows
    rows = [
        {"vg": 0.4, "vd": 0.9, "vb": 0.0, "id": 1e-7, "gm": 2e-6, "gds": 1e-7, "vth": 0.5,
         "cgg": 1e-15, "cgs": -6e-16, "cgd": -2e-16, "cgb": -2e-16, "cdd": 3e-16, "css": 4e-16,
         "cgdo": 1e-16, "cgso": 1e-16, "capbd": 5e-17, "capbs": 5e-17, "gmbs": 4e-7, "n_id": 2e-12, "n_1f": 3e-12},
        {"vg": 0.8, "vd": 0.9, "vb": 0.0, "id": 1e-4, "gm": 1e-3, "gds": 5e-6, "vth": 0.5,
         "cgg": 2e-15, "cgs": -1.2e-15, "cgd": -4e-16, "cgb": -3e-16, "cdd": 6e-16, "css": 8e-16,
         "cgdo": 1e-16, "cgso": 1e-16, "capbd": 5e-17, "capbs": 5e-17, "gmbs": 2e-4, "n_id": 5e-12, "n_1f": 7e-12},
    ]
    cfg = gmid.GmidConfig.from_registry("sky130", vgs=(0.4, 0.4, 0.8), vds=(0.9, 0.9, 0.9),
                                        vsb=(0, 0, 0), length_um=[0.15])
    lut = gmid.parse_lut(_synth_bsim4_txt(rows), cfg)
    assert lut["GM"].shape == (1, 2, 1, 1)
    assert lut["ID"][0, 1, 0, 0] == pytest.approx(1e-4)
    assert lut["GM"][0, 1, 0, 0] == pytest.approx(1e-3)
    # CGG = cgg + cgdo + cgso ; CGD = -cgd + cgdo (BSIM4 sign flip); STH = onoise_id**2
    assert lut["CGG"][0, 0, 0, 0] == pytest.approx(1e-15 + 1e-16 + 1e-16)
    assert lut["CGD"][0, 0, 0, 0] == pytest.approx(-(-2e-16) + 1e-16)
    assert lut["STH"][0, 1, 0, 0] == pytest.approx((5e-12) ** 2)
    assert lut["GMB"][0, 1, 0, 0] == pytest.approx(2e-4)   # bsim4 'gmbs' → GMB


def test_parse_rejects_wrong_row_count():
    # 3 rows but VGS×VDS×VSB = 2×1×1 = 2 → 3 % 2 ≠ 0 (a dropped/non-converged point)
    rows = [{"vg": v, "vd": 0.9, "vb": 0.0} for v in (0.4, 0.8, 0.4)]  # 2 unique VGS, 3 rows
    cfg = gmid.GmidConfig.from_registry("sky130", length_um=[0.15])
    with pytest.raises(ValueError, match="not divisible"):
        gmid.parse_lut(_synth_bsim4_txt(rows), cfg)


def test_parse_rejects_truncated_row_loudly():
    """A truncated wrdata row used to be silently FILTERED — which can still reshape into a
    consistent-but-wrong grid (e.g. 2 rows → 1 surviving row parses as a 1-point LUT)."""
    rows = [{"vg": v, "vd": 0.9, "vb": 0.0, "id": 1e-6} for v in (0.4, 0.8)]
    txt = _synth_bsim4_txt(rows)
    lines = txt.splitlines()
    lines[1] = " ".join(lines[1].split()[:-1])          # chop the last column of row 1
    cfg = gmid.GmidConfig.from_registry("sky130", length_um=[0.15])
    with pytest.raises(ValueError, match="malformed wrdata row"):
        gmid.parse_lut("\n".join(lines) + "\n", cfg)


def test_parse_rejects_non_finite_values():
    """NaN/inf in the sweep output (a non-converged bias point) must refuse the LUT — a poisoned
    table corrupts every pygmid interpolation downstream, silently."""
    rows = [
        {"vg": 0.4, "vd": 0.9, "vb": 0.0, "id": float("nan"), "gm": 1e-5},
        {"vg": 0.8, "vd": 0.9, "vb": 0.0, "id": 1e-4, "gm": 1e-3},
    ]
    cfg = gmid.GmidConfig.from_registry("sky130", length_um=[0.15])
    with pytest.raises(ValueError, match="non-finite"):
        gmid.parse_lut(_synth_bsim4_txt(rows), cfg)


def test_variant_first_match_wins(monkeypatch):
    """Overlapping ``gmid.variants`` regexes: the FIRST match supplies the corner override —
    ordering in the registry is the contract."""
    from spicexplorer_analog_db import pdks as pdks_mod

    real = pdks.load_registry("ihp-sg13g2")
    rigged = dict(real)
    rigged["gmid"] = dict(real["gmid"])
    rigged["gmid"]["variants"] = [
        {"match": "_hv_", "corners": {"lib_file": "first.lib"}},
        {"match": "hv",   "corners": {"lib_file": "second.lib"}},   # also matches sg13_hv_nmos
    ]
    monkeypatch.setattr(pdks_mod, "load_registry", lambda name: rigged)
    cfg = gmid.GmidConfig.from_registry("ihp-sg13g2", device="sg13_hv_nmos")
    assert cfg.corner_override == {"lib_file": "first.lib"}


def test_parse_pmos_stores_positive_magnitude_axes():
    """A pmos deck sweeps biases NEGATIVE; the LUT must store positive magnitudes (the gm/ID
    convention) AND keep arrays aligned. Regression: the bug stored raw negative VGS/VDS, which
    `np.unique` then sorted REVERSED relative to the foreach-ordered arrays — mislabelling every
    pmos slice (strong inversion ended up tagged as VGS≈0)."""
    # foreach order (L, VGS, VDS, VSB): VGS = [0, -0.8] (a pmos sweep), one VDS=-0.9, one VSB.
    rows = [
        {"vg": 0.0, "vd": -0.9, "vb": 0.0, "id": 1e-9, "gm": 1e-9, "gds": 1e-10, "vth": -0.5,
         "cgg": 1e-15, "cgs": -6e-16, "cgd": -2e-16, "cgb": -2e-16, "cdd": 3e-16, "css": 4e-16,
         "cgdo": 1e-16, "cgso": 1e-16, "capbd": 5e-17, "capbs": 5e-17, "gmbs": 1e-10},
        {"vg": -0.8, "vd": -0.9, "vb": 0.0, "id": 1e-4, "gm": 1e-3, "gds": 5e-6, "vth": -0.5,
         "cgg": 2e-15, "cgs": -1.2e-15, "cgd": -4e-16, "cgb": -3e-16, "cdd": 6e-16, "css": 8e-16,
         "cgdo": 1e-16, "cgso": 1e-16, "capbd": 5e-17, "capbs": 5e-17, "gmbs": 2e-4},
    ]
    cfg = gmid.GmidConfig.from_registry(
        "sky130", device="sky130_fd_pr__pfet_01v8",
        vgs=(0, -0.8, -0.8), vds=(-0.9, -0.9, -0.9), vsb=(0, 0, 0), length_um=[0.15],
    )
    lut = gmid.parse_lut(_synth_bsim4_txt(rows), cfg)
    # axes are positive magnitudes
    assert lut["VGS"].min() >= 0 and lut["VGS"].max() == pytest.approx(0.8)
    assert lut["VDS"].max() == pytest.approx(0.9)
    # alignment: the |VGS|=0.8 slice (index 1) holds the strong-inversion current, not |VGS|=0
    assert lut["ID"][0, 1, 0, 0] == pytest.approx(1e-4)
    assert lut["ID"][0, 0, 0, 0] == pytest.approx(1e-9)
    assert lut["GM"][0, 1, 0, 0] / lut["ID"][0, 1, 0, 0] == pytest.approx(10.0)  # gm/ID > 0


def test_registry_corners_defaults_and_reads():
    assert gmid.registry_corners("sky130") == ["tt", "ss", "ff"]


def test_lut_convenience_loads_and_errors_clearly():
    # the common case: one call, registry-default device, the committed tt LUT
    nch = gmid.lut("sky130")
    assert nch["INFO"]  # a Lookup (or dict) with the header populated
    # an uncommitted (device × corner): a clear error naming what's committed + the extract command
    with pytest.raises(FileNotFoundError, match="gmid-extract --pdk sky130"):
        gmid.lut("sky130", corner="ss")


# ── LUT manifest (the registry record beside each .pkl) ──────────────────────────────────────────
def test_build_manifest_captures_dimensions_corner_and_model():
    cfg = gmid.GmidConfig.from_registry("sky130", device="sky130_fd_pr__pfet_01v8")
    lut = {
        "INFO": "x", "CORNER": "TT", "TEMP": 300.0, "NFING": 1, "W": 5.0,
        "L": np.array([0.15, 0.5, 2.0]), "VGS": np.array([0.0, 0.5, 1.0, 1.5]),
        "VDS": np.array([0.0, 0.9]), "VSB": np.array([0.0, 0.4]),
        "ID": np.zeros((3, 4, 2, 2)), "GM": np.zeros((3, 4, 2, 2)),
    }
    m = gmid.build_manifest(cfg, lut)
    assert m["corner"] == "tt" and m["model_family"] == "bsim4" and m["polarity"] == "p"
    assert m["model"]["corner_lines"] == [".lib sky130.lib.spice tt"]            # the EXACT model
    assert m["dimensions"]["L_um"]["values"] == [0.15, 0.5, 2.0]                  # non-uniform L grid
    assert m["dimensions"]["VGS_V"] == {"n": 4, "min": 0.0, "max": 1.5, "step": 0.5}
    assert m["dimensions"]["VSB_V"]["stored"] == "magnitude"
    assert set(m["params"]) == {"ID", "GM"}                                       # axes/scalars excluded
    assert m["conditions"] == {"temp_k": 300.0, "width_um": 5.0, "nfing": 1}


def test_manifest_reader_and_list_luts():
    rows = gmid.list_luts("sky130")
    assert {r["device"] for r in rows} >= {"sky130_fd_pr__nfet_01v8", "sky130_fd_pr__pfet_01v8"}
    assert all(r["manifest"] for r in rows)                 # every committed LUT has its manifest
    m = gmid.manifest("sky130", "sky130_fd_pr__pfet_01v8")  # matches the committed pfet LUT grid
    assert m["pdk"] == "sky130" and m["dimensions"]["L_um"]["n"] == 8 and m["lut_file"].endswith(".pkl")
    with pytest.raises(FileNotFoundError, match="gmid-extract"):
        gmid.manifest("sky130", "sky130_fd_pr__pfet_01v8", corner="ss")  # uncommitted corner


# ── simulator block + per-L parallel extraction (the native/docker-less lane) ────────────────────
def test_simulator_settings_reads_registry_block():
    for pdk in ("ihp-sg13g2", "sky130", "gf180mcu"):
        sim = gmid.simulator_settings(pdk)
        assert sim["runner"] == "auto" and sim["workers"] >= 1 and sim["timeout_s"] > 0


def test_extract_parallel_merges_per_l_slices(monkeypatch):
    cfg = gmid.GmidConfig.from_registry("sky130")
    cfg.length_um = [0.15, 0.5, 2.0]
    shape = (1, 4, 3, 2)  # each per-L job returns a single-L slice

    def fake_extract(one_cfg, run):
        assert len(one_cfg.length_um) == 1  # fan-out is one job per L
        val = float(one_cfg.length_um[0])
        return {
            "INFO": "x", "CORNER": "TT", "TEMP": 300.0, "NFING": 1, "W": 5.0,
            "L": np.array(one_cfg.length_um), "VGS": np.zeros(4), "VDS": np.zeros(3),
            "VSB": np.zeros(2), "ID": np.full(shape, val), "GM": np.full(shape, 10 * val),
        }

    monkeypatch.setattr(gmid, "extract", fake_extract)
    lut = gmid.extract_parallel(cfg, run=None, workers=3)
    assert lut["ID"].shape == (3, 4, 3, 2)
    assert list(lut["L"]) == [0.15, 0.5, 2.0]                      # L order preserved
    assert lut["ID"][0].flat[0] == 0.15 and lut["ID"][2].flat[0] == 2.0
    assert lut["GM"][1].flat[0] == 5.0                              # slices land at their own index


def test_extract_parallel_single_worker_falls_through(monkeypatch):
    cfg = gmid.GmidConfig.from_registry("sky130")
    called = {}

    def fake_extract(one_cfg, run):
        called["lengths"] = list(one_cfg.length_um)
        return {"L": np.array(one_cfg.length_um)}

    monkeypatch.setattr(gmid, "extract", fake_extract)
    gmid.extract_parallel(cfg, run=None, workers=1)
    assert called["lengths"] == cfg.length_um                       # classic one-deck path


def test_extract_parallel_rejects_inconsistent_slices(monkeypatch):
    cfg = gmid.GmidConfig.from_registry("sky130")
    cfg.length_um = [0.15, 0.5]

    def fake_extract(one_cfg, run):  # second job drops a VGS row (non-converged point)
        n_vgs = 4 if one_cfg.length_um[0] == 0.15 else 3
        return {"L": np.array(one_cfg.length_um), "ID": np.zeros((1, n_vgs, 3, 2))}

    monkeypatch.setattr(gmid, "extract", fake_extract)
    with pytest.raises(ValueError, match="inconsistent"):
        gmid.extract_parallel(cfg, run=None, workers=2)
