"""Unit tests for the cross-PDK binding generator (bindings.py) — PDK-free."""

from __future__ import annotations

import pytest

from spicexplorer_analog_db import bindings

_IHP = {"corners": {"lib_file": "cornerMOSlv.lib", "sections": ["mos_tt", "mos_ss"]},
        "devices": {"nmos": {"lv": "sg13_lv_nmos", "hv": "sg13_hv_nmos"},
                    "pmos": {"lv": "sg13_lv_pmos", "hv": "sg13_hv_pmos"}},
        "geometry": {"min_w": "0.18u", "min_l": "0.13u"}}
_SKY = {"corners": {"lib_file": "sky130.lib.spice", "sections": ["tt", "ss", "ff"]},
        "devices": {"nmos": {"core": "sky130_fd_pr__nfet_01v8"},
                    "pmos": {"core": "sky130_fd_pr__pfet_01v8"}},
        "geometry": {"min_w": "0.42u", "min_l": "0.15u"}}
_GF = {"corners": {"lib_file": "sm141064.ngspice", "includes": ["design.ngspice"],
                   "pre_sections": ["noise_corner"], "post_sections": ["fets_mm"],
                   "per_corner": {"tt": ["nfet_03v3_t", "pfet_03v3_t"],
                                  "ss": ["nfet_03v3_s", "pfet_03v3_s"]}},
       "devices": {"nmos": {"core": "nfet_03v3", "io": "nfet_06v0"},
                   "pmos": {"core": "pfet_03v3", "io": "pfet_06v0"}},
       "geometry": {"min_w": "0.22u", "min_l": "0.28u"}}


def _vars(sizing):
    return {v["name"]: v for v in sizing["variables"]}


def test_analoggym_sky130_to_ihp_geometry_gets_micron_suffix():
    """AnalogGym bare-µm W/L -> IHP 'u'-meters; M/cap/current carried verbatim."""
    src = {"variables": [
        {"name": "MOSFET_8_2_W_gm1_PMOS", "default": "1"},
        {"name": "MOSFET_8_2_L_gm1_PMOS", "default": "1"},
        {"name": "MOSFET_8_2_M_gm1_PMOS", "default": "4"},
        {"name": "CAPACITOR_0", "default": "5p"},
        {"name": "CURRENT_0_BIAS", "default": "60u"},
    ]}
    out = _vars(bindings.convert_sizing(src, "ihp-sg13g2", _IHP))
    assert out["MOSFET_8_2_W_gm1_PMOS"]["default"] == "1u"
    assert out["MOSFET_8_2_L_gm1_PMOS"]["default"] == "1u"
    assert out["MOSFET_8_2_M_gm1_PMOS"]["default"] == "4"      # multiplier: PDK-independent
    assert out["CAPACITOR_0"]["default"] == "5p"               # farads: PDK-independent
    assert out["CURRENT_0_BIAS"]["default"] == "60u"           # amps: PDK-independent


def test_in_repo_ihp_to_sky130_strips_suffix_and_bin_clamps():
    """IHP 'u'-meters W/L -> sky130 bare-µm numbers; min bound clamped up to the sky130 bin."""
    src = {"variables": [
        {"name": "x_dut_w_1", "default": "72u", "min": "0.1u", "max": "200u", "unit": "m"},
        {"name": "x_dut_l_1", "default": "0.5u", "min": "0.1u", "max": "5u", "unit": "m"},
        {"name": "x_dut_vb1", "default": 1.225, "min": 0.1, "max": 1.8, "unit": "V"},
        {"name": "x_dut_ib", "default": "34u", "min": "1u", "max": "100u", "unit": "A"},
        {"name": "x_dut_ng_1", "default": 8, "min": 1, "max": 32, "freeze": True},
    ]}
    out = _vars(bindings.convert_sizing(src, "sky130", _SKY))
    assert out["x_dut_w_1"]["default"] == 72 and out["x_dut_w_1"]["max"] == 200
    assert out["x_dut_w_1"]["min"] == 0.42                     # W floor clamp (0.1 -> 0.42)
    assert out["x_dut_l_1"]["default"] == 0.5 and out["x_dut_l_1"]["min"] == 0.15  # L floor clamp
    assert out["x_dut_vb1"] == src["variables"][2]             # volts: verbatim
    assert out["x_dut_ib"]["default"] == "34u"                 # amps: verbatim
    assert out["x_dut_ng_1"]["default"] == 8                   # fingers: verbatim


def test_geometry_default_below_bin_is_clamped_up():
    src = {"variables": [{"name": "x_dut_m1_w", "default": "0.2u", "unit": "m"}]}
    out = _vars(bindings.convert_sizing(src, "sky130", _SKY))
    assert out["x_dut_m1_w"]["default"] == 0.42                # 0.2µm < sky130 W bin -> clamp


def test_gf180_sizing_is_explicit_microns_like_ihp():
    """gf180 has no `.option scale` (explicit-µm 'u'), unlike sky130's bare-µm."""
    src = {"variables": [{"name": "MOSFET_1_W_gm_NMOS", "default": "1"},   # sky130 bare-µm source
                         {"name": "MOSFET_1_M_gm_NMOS", "default": "4"},
                         {"name": "CAPACITOR_0", "default": "5p"}]}
    out = _vars(bindings.convert_sizing(src, "gf180mcu", _GF))
    assert out["MOSFET_1_W_gm_NMOS"]["default"] == "1u"        # geometry -> explicit µm
    assert out["MOSFET_1_M_gm_NMOS"]["default"] == "4" and out["CAPACITOR_0"]["default"] == "5p"


def test_atomic_field_suffix_classifies_as_geometry_without_unit():
    """P4 atomic names on unit-less rows (AnalogGym-inherited sizing): the trailing `_w`/`_l`
    field suffix must still classify as geometry so add-binding re-notes/clamps it."""
    src = {"variables": [{"name": "x_dut_xm12_w", "default": "1"},
                         {"name": "x_dut_xm12_l", "default": "1"},
                         {"name": "x_dut_xm12_m", "default": "4"}]}
    out = _vars(bindings.convert_sizing(src, "gf180mcu", _GF))
    assert out["x_dut_xm12_w"]["default"] == "1u"              # geometry -> explicit µm
    assert out["x_dut_xm12_l"]["default"] == "1u"
    assert out["x_dut_xm12_m"]["default"] == "4"               # fingers: verbatim


def test_gf180_corners_expand_per_device_sections_in_order():
    """gf180 corner order: include(design) → pre(noise_corner) → per-device models → post(fets_mm)."""
    text = bindings._corners_yaml("gf180mcu", _GF)
    import yaml as _yaml
    tt = _yaml.safe_load(text)["corners"]["tt"]
    secs = [b.get("section") for b in tt]
    assert tt[0] == {"lib_file": "design.ngspice"}             # sectionless global include first
    # noise_corner (defines the *_noia params) must precede the device model cards
    assert secs.index("noise_corner") < secs.index("nfet_03v3_t") < secs.index("fets_mm")
    assert "pfet_03v3_t" in secs and secs[-1] == "fets_mm"     # device subckts last


def test_passive_corner_libs_appended_from_real_registries():
    """The registry `passives.libs` block appends the R/C corner-lib lines to every bundle —
    real `_shared/pdk/*.yaml` registries (sky130: none needed; ihp: own libs; gf180: sections)."""
    import yaml as _yaml

    from spicexplorer_analog_db import pdks

    def bundle(pdk, corner):
        text = bindings._corners_yaml(pdk, pdks.load_registry(pdk))
        return _yaml.safe_load(text)["corners"][corner]

    # sky130: passives ride inside the MOS sections — bundle stays a single entry
    assert bundle("sky130", "tt") == [{"lib_file": "sky130.lib.spice", "section": "tt"}]
    # ihp: cornerRES/cornerCAP appended; ss maps to the worst-case passive sections
    assert [e["section"] for e in bundle("ihp-sg13g2", "tt")] == ["mos_tt", "res_typ", "cap_typ"]
    assert [e["section"] for e in bundle("ihp-sg13g2", "ss")] == ["mos_ss", "res_wcs", "cap_wcs"]
    # gf180: res/mimcap model sections + the cap_mim subckt section, AFTER the MOS bundle
    secs = [e.get("section") for e in bundle("gf180mcu", "tt")]
    assert secs.index("fets_mm") < secs.index("res_typical") < secs.index("cap_mim")
    assert "mimcap_typical" in secs and secs[-1] == "cap_mim"
    # sf/fs map passives to typical on both PDKs that need lines
    assert [e["section"] for e in bundle("ihp-sg13g2", "sf")][-2:] == ["res_typ", "cap_typ"]
    assert [e.get("section") for e in bundle("gf180mcu", "fs")][-3:] == ["res_typical", "mimcap_typical", "cap_mim"]


@pytest.mark.parametrize("text,source,target,expected", [
    # block form (AnalogGym): append a new list item, comments/keys around it untouched
    ("# manifest\npdks:\n- sky130\nanalyses: [x]\n", "sky130", "ihp-sg13g2",
     "# manifest\npdks:\n- sky130\n- ihp-sg13g2\nanalyses: [x]\n"),
    # flow form (in-repo OTA): extend the inline list
    ("pdks: [ihp-sg13g2]\nstatus: draft\n", "ihp-sg13g2", "sky130",
     "pdks: [ihp-sg13g2, sky130]\nstatus: draft\n"),
    # flow form with a trailing comment (preserved)
    ("pdks: [ihp-sg13g2, sky130]   # multi-PDK\n", "ihp-sg13g2", "gf180mcu",
     "pdks: [ihp-sg13g2, sky130, gf180mcu]   # multi-PDK\n"),
])
def test_add_pdk_to_manifest_both_forms(tmp_path, text, source, target, expected):
    from spicexplorer_analog_db.model import Circuit

    (tmp_path / "circuit.yaml").write_text(text)
    c = Circuit(id="t", dir=tmp_path, manifest={"pdks": [source]})
    bindings._add_pdk_to_manifest(c, target)
    assert (tmp_path / "circuit.yaml").read_text() == expected
