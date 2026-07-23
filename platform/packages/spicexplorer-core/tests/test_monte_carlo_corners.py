"""monte_carlo_corners — statistical sample-corner cloning (the /simulate MC lane).

A sample corner = the base corner with every process include swapped to its
``<section>_mismatch`` sibling (when the library defines one) plus a unique
``.options seed`` so the PDK's agauss() draws differ per sample.
"""
import pytest
from spicexplorer_core.pvt import Corner, ModelInclude, monte_carlo_corners

LIB_TEXT = """\
* fake corner lib
.LIB mos_tt
  .param a=1
.ENDL mos_tt
.LIB mos_tt_mismatch
  .param a=1
  .include fake_mod_mismatch.lib
.ENDL mos_tt_mismatch
.LIB res_typ
  .param r=1
.ENDL res_typ
"""


@pytest.fixture
def pdk_root(tmp_path):
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "cornerFAKE.lib").write_text(LIB_TEXT)
    return tmp_path


def _base() -> Corner:
    return Corner(
        name="tt_27C_1V50",
        model_includes=[
            ModelInclude(lib_file="cornerFAKE.lib", section="mos_tt"),
            ModelInclude(lib_file="cornerFAKE.lib", section="res_typ"),
        ],
        temp=27.0,
        params={"VDD": 1.5},
    )


def test_swaps_mismatch_sections_and_seeds(pdk_root):
    samples = monte_carlo_corners(_base(), 3, seed0=10, lib_search_roots=[str(pdk_root)])
    assert [c.name for c in samples] == ["mc1", "mc2", "mc3"]
    assert [c.options["seed"] for c in samples] == [10, 11, 12]
    for c in samples:
        # mos_tt has a mismatch sibling → swapped; res_typ has none → kept as-is.
        assert [(i.lib_file, i.section) for i in c.model_includes] == [
            ("cornerFAKE.lib", "mos_tt_mismatch"),
            ("cornerFAKE.lib", "res_typ"),
        ]
        assert c.temp == 27.0 and c.params == {"VDD": 1.5} and c.enabled


def test_raises_when_no_statistical_sections(tmp_path):
    (tmp_path / "cornerFAKE.lib").write_text(".LIB mos_tt\n.ENDL mos_tt\n")
    with pytest.raises(ValueError, match="no '<section>_mismatch'"):
        monte_carlo_corners(_base(), 4, lib_search_roots=[str(tmp_path)])


def test_raises_when_libs_not_found(tmp_path):
    with pytest.raises(ValueError, match="statistical sections"):
        monte_carlo_corners(_base(), 4, lib_search_roots=[str(tmp_path)])


def test_requires_at_least_two_samples(pdk_root):
    with pytest.raises(ValueError, match="at least 2"):
        monte_carlo_corners(_base(), 1, lib_search_roots=[str(pdk_root)])


def test_samples_are_independent_copies(pdk_root):
    samples = monte_carlo_corners(_base(), 2, lib_search_roots=[str(pdk_root)])
    samples[0].params["VDD"] = 9.9
    assert samples[1].params["VDD"] == 1.5
