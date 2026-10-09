"""Loading gm/ID tables by name: `default_roots`, `load_lut`, `search_luts`, `finger_width_set`.

A design repo's working directory is neither the platform checkout nor the table store, so a
design has no root to hand `LUTRegistry` (#157). These tests check the order the roots are
searched in, the text of the "no table" error, the finger-width set opened by name (#280), and
the listing of every table file, temperature and finger-width tables included (#290).
"""

from __future__ import annotations

import json
import pickle
import shutil
from pathlib import Path

import pytest
from _gmid_fixtures import perturbed_lut
from spicexplorer_gmid import (
    DeviceTable,
    FingerWidthSet,
    GmidError,
    OperatingPoint,
    default_roots,
    finger_width_set,
    load_lut,
    search_luts,
)
from spicexplorer_gmid.registry import DB_RELATIVE, ROOTS_ENV, USER_STORE

FIXTURES = Path(__file__).parent / "fixtures"
REAL_PKL = FIXTURES / "sky130_fd_pr__nfet_01v8__tt.pkl"
REAL_MAN = FIXTURES / "sky130_fd_pr__nfet_01v8__tt.manifest.json"


def _lut(pdk_dir: Path, device: str, corner: str = "tt", *, pdk: str = "kitpdk") -> None:
    """Drop a real `.pkl` + manifest pair under a name of our choosing.

    The fixture LUT is copied rather than synthesized: the manifest schema is closed, so a
    hand-written stub tests the validator instead of the discovery.
    """
    pdk_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(REAL_PKL, pdk_dir / f"{device}__{corner}.pkl")
    man = json.loads(REAL_MAN.read_text())
    man |= {"pdk": pdk, "device": device, "corner": corner, "lut_file": f"{device}__{corner}.pkl"}
    (pdk_dir / f"{device}__{corner}.manifest.json").write_text(json.dumps(man))


def test_the_search_order_is_the_installation_a_design_actually_sees(tmp_path, monkeypatch):
    """Explicit override, then the per-user store the Spectre lane writes, then `$SX_ROOT`.

    `$SX_ROOT` before the enclosing checkout on purpose: a design should get the shared
    installation's tables, not whichever platform checkout happens to be above its cwd.
    """
    monkeypatch.setenv(ROOTS_ENV, str(tmp_path / "explicit"))
    monkeypatch.setenv("SX_ROOT", str(tmp_path / "shared"))
    roots = [str(r) for r in default_roots()]
    assert roots[0] == str(tmp_path / "explicit")
    assert roots[1] == str(Path(USER_STORE).expanduser())  # the Spectre lane's own out_root
    assert str(tmp_path / "shared" / "spicexplorer-platform" / DB_RELATIVE) in roots


def test_a_design_loads_a_kit_table_from_the_out_of_repo_store(tmp_path, monkeypatch):
    """The licensed-kit case: the table is in `~/.spicexplorer/gmid`, in no repo at all."""
    store = tmp_path / "store"
    _lut(store / "generic-n65", "nmos_lvt")
    monkeypatch.setenv(ROOTS_ENV, str(store))
    t = load_lut("generic-n65", "nmos_lvt")
    assert t.source == store / "generic-n65" / "nmos_lvt__tt.pkl"
    assert t.manifest is not None and t.manifest.device == "nmos_lvt"
    assert [m.device for m in search_luts("generic-n65")] == ["nmos_lvt"]


def test_an_earlier_root_shadows_a_later_one(tmp_path, monkeypatch):
    """A table extracted locally wins over a committed one of the same name."""
    first, second = tmp_path / "a", tmp_path / "b"
    _lut(first / "kitpdk", "nch")
    _lut(second / "kitpdk", "nch")
    monkeypatch.setenv(ROOTS_ENV, f"{first}:{second}")
    assert load_lut("kitpdk", "nch").source == first / "kitpdk" / "nch__tt.pkl"
    assert len(search_luts("kitpdk")) == 1  # listed once, not twice


def test_the_failure_names_every_root_and_what_it_holds(tmp_path, monkeypatch):
    """An empty store and an absent PDK are different problems with different fixes.

    A message that does not distinguish them is what sent a design agent off to write its own
    interpolator, so the distinction is asserted, not assumed.
    """
    present, absent = tmp_path / "present", tmp_path / "gone"
    _lut(present / "kitpdk", "nch")
    monkeypatch.setenv(ROOTS_ENV, f"{absent}:{present}")
    monkeypatch.delenv("SX_ROOT", raising=False)
    with pytest.raises(KeyError) as exc:
        load_lut("othpdk", "nch")
    said = str(exc.value)
    assert f"{absent} (no such directory)" in said
    assert f"{present} (holds: kitpdk)" in said
    assert "gmid-extract-spectre" in said and USER_STORE in said

    with pytest.raises(KeyError) as exc2:
        load_lut("kitpdk", "pch")
    assert "holds: nch__tt" in str(exc2.value)  # the PDK is there; that device is not


def test_an_in_memory_table_needs_no_file(tmp_path):
    """What an extractor's `assemble()` returns is loadable as it stands."""
    store = tmp_path / "s"
    _lut(store / "kitpdk", "nch")
    data = pickle.loads((store / "kitpdk" / "nch__tt.pkl").read_bytes())
    t = DeviceTable.from_lut_dict(data)
    assert t.source is None
    assert list(t.L_grid) == list(data["L"])
    with pytest.raises(ValueError, match="not a pygmid LUT"):
        DeviceTable.from_lut_dict({"L": [1.0]})


# ----- finger_width_set: a device's finger-width tables, opened by name (#280) -----------------
#
# A design that sizes a finger narrower than the 5 um of the nominal table needs the companion
# tables `<device>__<corner>__wf<W>u`. Before #280 the by-name loader existed only in
# `spicexplorer_analog_db`, which design code cannot import (skill-library #21), so every design
# listed the widths and called `load_lut` once per width.

# The bias point every interpolation check reads: reachable on both the sky130 fixture and the
# perturbed 1 um companion (its gm/ID band is about 0.78 of the fixture's).
_GM_ID, _L, _VDS = 12.0, 0.5, 0.9
# A narrow-finger companion table: the fixture with each stored array scaled by a different factor,
# so an interpolated value differs from both ends.
_COMPANION_SCALE = {"ID": 1.6, "GM": 1.25, "GDS": 0.9, "CGG": 1.1, "CDD": 1.2}


def _wf_lut(
    pdk_dir: Path,
    stem: str,
    *,
    width_um: float = 5.0,
    temp_k: float = 300.0,
    pdk: str = "kitpdk",
    device: str = "nch",
    lut_file: str | None = None,
) -> None:
    """Write a `<stem>.pkl` + `<stem>.manifest.json` pair whose manifest records `width_um`.

    The 5 um table is the sky130 fixture as committed; any other width is the fixture with its
    arrays scaled by `_COMPANION_SCALE`, so interpolating between the two gives a result that
    differs from both endpoints. The manifest's `lut_file` field is `<stem>.pkl` unless
    `lut_file` is given.
    """
    pdk_dir.mkdir(parents=True, exist_ok=True)
    if width_um == 5.0:
        shutil.copy(REAL_PKL, pdk_dir / f"{stem}.pkl")
    else:
        perturbed_lut(pdk_dir / f"{stem}.pkl", scale=_COMPANION_SCALE, headers={"W": width_um})
    man = json.loads(REAL_MAN.read_text())
    man |= {"pdk": pdk, "device": device, "corner": "tt", "lut_file": lut_file or f"{stem}.pkl"}
    man["conditions"] |= {"width_um": width_um, "temp_k": temp_k}
    (pdk_dir / f"{stem}.manifest.json").write_text(json.dumps(man))


def _message(exc: pytest.ExceptionInfo[KeyError]) -> str:
    """The KeyError text as written; `str()` of a KeyError is its repr, with `\\n` escaped."""
    return exc.value.args[0]


def test_finger_width_set_opens_every_width_the_store_holds(tmp_path):
    """Issue #280 acceptance: a store holding the 5 um and 1 um tables gives [1.0, 5.0].

    The store also holds a -40 C table of the same device and a 1 um table of another device;
    neither belongs to the nominal-temperature `nch` set.
    """
    kit = tmp_path / "store" / "kitpdk"
    _wf_lut(kit, "nch__tt")
    _wf_lut(kit, "nch__tt__wf1u", width_um=1.0)
    _wf_lut(kit, "nch__tt__-40C", temp_k=233.15)
    _wf_lut(kit, "pch__tt__wf1u", width_um=1.0, device="pch")

    fs = finger_width_set("kitpdk", "nch", roots=[tmp_path / "store"])

    assert isinstance(fs, FingerWidthSet)
    assert fs.finger_widths == [1.0, 5.0]
    assert fs.table_at(1.0).source == kit / "nch__tt__wf1u.pkl"
    assert fs.table_at(5.0).source == kit / "nch__tt.pkl"
    op = fs.at(_GM_ID, _L, _VDS, wf=3)
    assert isinstance(op, OperatingPoint)
    # wf = 3 um sits halfway between 1 um and 5 um: the mean of the two tables' answers.
    jd_1, jd_5 = (fs.table_at(w).at(_GM_ID, _L, _VDS).jd for w in (1.0, 5.0))
    assert jd_1 != pytest.approx(jd_5)
    assert op.jd == pytest.approx(0.5 * (jd_1 + jd_5))


def test_finger_width_set_reads_a_sub_micron_tag_and_a_temperature(tmp_path):
    """`__wf0p5u` is 0.5 um; `temp_c` selects the `__<T>C` tables and only those."""
    kit = tmp_path / "store" / "kitpdk"
    _wf_lut(kit, "nch__tt")
    _wf_lut(kit, "nch__tt__-40C", temp_k=233.15)
    _wf_lut(kit, "nch__tt__-40C__wf0p5u", width_um=0.5, temp_k=233.15)

    cold = finger_width_set("kitpdk", "nch", temp_c=-40, roots=[tmp_path / "store"])
    assert cold.finger_widths == [0.5, 5.0]
    assert cold.table_at(0.5).source == kit / "nch__tt__-40C__wf0p5u.pkl"
    assert cold.table_at(5.0).source == kit / "nch__tt__-40C.pkl"
    nominal = finger_width_set("kitpdk", "nch", roots=[tmp_path / "store"])
    assert nominal.finger_widths == [5.0]


def test_finger_width_set_skips_a_tag_load_lut_cannot_address(tmp_path):
    """`__wf1p0u` and `__wf5u` are not names `lut_stem` writes, so `load_lut` could never open them.

    Listing them would turn a stray file into a `KeyError` for the whole set.
    """
    kit = tmp_path / "store" / "kitpdk"
    _wf_lut(kit, "nch__tt")
    _wf_lut(kit, "nch__tt__wf1p0u", width_um=1.0)
    _wf_lut(kit, "nch__tt__wf5u")
    assert finger_width_set("kitpdk", "nch", roots=[tmp_path / "store"]).finger_widths == [5.0]


def test_explicit_widths_open_exactly_those(tmp_path):
    kit = tmp_path / "store" / "kitpdk"
    _wf_lut(kit, "nch__tt")
    _wf_lut(kit, "nch__tt__wf1u", width_um=1.0)
    root = [tmp_path / "store"]
    assert finger_width_set("kitpdk", "nch", widths=(5,), roots=root).finger_widths == [5.0]
    # a width given twice, once as int and once as float, is one table
    both = finger_width_set("kitpdk", "nch", widths=[1, 1.0, 5], roots=root)
    assert both.finger_widths == [1.0, 5.0]


def test_missing_widths_raise_one_keyerror_naming_roots_holdings_and_found_widths(tmp_path):
    """Issue #280 acceptance: `widths=(0.5, 1, 5)` against a 1 um + 5 um store.

    Every missing width is reported in the one error, not only the first one tried.
    """
    gone, store = tmp_path / "gone", tmp_path / "store"
    kit = store / "kitpdk"
    _wf_lut(kit, "nch__tt")
    _wf_lut(kit, "nch__tt__wf1u", width_um=1.0)
    (tmp_path / "other" / "otherpdk").mkdir(parents=True)

    with pytest.raises(KeyError) as exc:
        finger_width_set(
            "kitpdk", "nch", widths=(0.25, 0.5, 1, 5), roots=[gone, tmp_path / "other", store]
        )
    said = _message(exc)
    assert "0.25, 0.5 µm" in said and "nch__tt__wf0p25u" in said and "nch__tt__wf0p5u" in said
    assert "found: 1, 5 µm" in said
    assert f"{gone} (no such directory)" in said
    assert f"{tmp_path / 'other'} (holds: otherpdk)" in said
    assert f"{kit} (holds: nch__tt, nch__tt__wf1u)" in said
    assert "gmid-extract-spectre" in said and USER_STORE in said


def test_found_lists_every_width_the_roots_hold_not_only_the_requested_ones(tmp_path):
    """`found:` is what the roots hold, so a caller who asked for the wrong width sees the right one.

    The store holds 0.5, 1 and 5 um; the caller asks for 0.25 and 1 um. The 0.5 and 5 um tables
    are neither requested nor opened, and `found:` still names them.
    """
    kit = tmp_path / "store" / "kitpdk"
    _wf_lut(kit, "nch__tt")
    _wf_lut(kit, "nch__tt__wf0p5u", width_um=0.5)
    _wf_lut(kit, "nch__tt__wf1u", width_um=1.0)
    with pytest.raises(KeyError) as exc:
        finger_width_set("kitpdk", "nch", widths=(0.25, 1), roots=[tmp_path / "store"])
    said = _message(exc)
    assert "at finger width 0.25 µm (nch__tt__wf0p25u)" in said
    assert "found: 0.5, 1, 5 µm" in said


def test_no_table_at_any_width_raises_keyerror(tmp_path):
    (tmp_path / "store" / "kitpdk").mkdir(parents=True)
    with pytest.raises(KeyError) as exc:
        finger_width_set("kitpdk", "nch", roots=[tmp_path / "store"])
    said = _message(exc)
    assert "no gm/ID LUT for kitpdk/nch__tt at any finger width" in said
    assert "found: none" in said
    assert f"{tmp_path / 'store' / 'kitpdk'} (holds: nothing)" in said


def test_the_first_root_holding_a_width_serves_it(tmp_path):
    """Each width is resolved by `load_lut`: the first root holding that width serves it."""
    local, shared = tmp_path / "local", tmp_path / "shared"
    _wf_lut(local / "kitpdk", "nch__tt")
    _wf_lut(shared / "kitpdk", "nch__tt")
    _wf_lut(shared / "kitpdk", "nch__tt__wf1u", width_um=1.0)
    fs = finger_width_set("kitpdk", "nch", roots=[local, shared])
    assert fs.finger_widths == [1.0, 5.0]
    assert fs.table_at(5.0).source == local / "kitpdk" / "nch__tt.pkl"
    assert fs.table_at(1.0).source == shared / "kitpdk" / "nch__tt__wf1u.pkl"


def test_finger_width_set_searches_the_default_roots(tmp_path, monkeypatch):
    """With no `roots=`, the search order is `default_roots()`, the one `load_lut` uses."""
    store = tmp_path / "store"
    _wf_lut(store / "kitpdk", "nch__tt")
    _wf_lut(store / "kitpdk", "nch__tt__wf1u", width_um=1.0)
    monkeypatch.setenv(ROOTS_ENV, str(store))
    monkeypatch.delenv("SX_ROOT", raising=False)
    assert finger_width_set("kitpdk", "nch").finger_widths == [1.0, 5.0]


@pytest.mark.parametrize(
    "stem, recorded_um, widths",
    [
        ("nch__tt__wf1u", 5.0, None),  # named for 1 um, records 5 um
        ("nch__tt", 1.0, (5,)),  # the untagged 5 um name, records 1 um
    ],
)
def test_a_mis_tagged_table_is_refused_not_placed_at_the_wrong_width(
    tmp_path, stem, recorded_um, widths
):
    """The set places each table at the width its name gives, so the manifest must agree.

    The untagged row checks that the 5 um table is opened as an explicit 5 um request: opened
    with no width, `find` would not compare the recorded width at all.
    """
    kit = tmp_path / "store" / "kitpdk"
    if stem != "nch__tt":
        _wf_lut(kit, "nch__tt")
    _wf_lut(kit, stem, width_um=recorded_um)
    with pytest.raises(GmidError, match="refusing to serve"):
        finger_width_set("kitpdk", "nch", widths=widths, roots=[tmp_path / "store"])


@pytest.mark.parametrize("widths", [(), (0.0,), (-1.0, 5.0), (float("nan"),), (float("inf"),)])
def test_widths_must_be_positive_and_finite(tmp_path, widths):
    with pytest.raises(ValueError, match="widths"):
        finger_width_set("kitpdk", "nch", widths=widths, roots=[tmp_path])


# ----- search_luts: one entry per table file (#290) --------------------------------------------
#
# The listing was keyed on (PDK, device, corner), so a temperature table (`__<T>C`) or a
# finger-width table (`__wf<W>u`) of a device merged into the first table listed for that device
# and corner. It is now keyed on the PDK and the table's file stem, the name `load_lut` opens.

_SKY_NCH = "sky130_fd_pr__nfet_01v8"


def _conditions(mans) -> list[tuple[float, float]]:
    """(temp_k [K], width_um [µm]) of each listed manifest, in listing order."""
    return [(m.conditions.temp_k, m.conditions.width_um) for m in mans]


def test_search_luts_lists_every_table_of_a_device_in_one_root(tmp_path):
    """Issue #290, first reproduction: one root holding the 27 C, -40 C and 1 um tables of one
    device lists three entries, in manifest file-name order."""
    one = tmp_path / "one"
    _wf_lut(one / "sky130", f"{_SKY_NCH}__tt", pdk="sky130", device=_SKY_NCH)
    _wf_lut(one / "sky130", f"{_SKY_NCH}__tt__wf1u", width_um=1.0, pdk="sky130", device=_SKY_NCH)
    _wf_lut(one / "sky130", f"{_SKY_NCH}__tt__-40C", temp_k=233.15, pdk="sky130", device=_SKY_NCH)

    listed = search_luts("sky130", roots=[one])

    assert [m.lut_file for m in listed] == [
        f"{_SKY_NCH}__tt.pkl",
        f"{_SKY_NCH}__tt__-40C.pkl",
        f"{_SKY_NCH}__tt__wf1u.pkl",
    ]
    assert _conditions(listed) == [(300.0, 5.0), (233.15, 5.0), (300.0, 1.0)]


def test_search_luts_lists_a_tagged_table_and_the_untagged_one_from_two_roots(tmp_path):
    """Issue #290, second reproduction: a 1 um table extracted locally does not hide the 5 um
    table of the shared root, the one `load_lut(pdk, device)` opens."""
    local, shared = tmp_path / "local", tmp_path / "shared"
    _wf_lut(local / "sky130", f"{_SKY_NCH}__tt__wf1u", width_um=1.0, pdk="sky130", device=_SKY_NCH)
    _wf_lut(shared / "sky130", f"{_SKY_NCH}__tt", pdk="sky130", device=_SKY_NCH)

    listed = search_luts("sky130", roots=[local, shared])

    assert [m.lut_file for m in listed] == [f"{_SKY_NCH}__tt__wf1u.pkl", f"{_SKY_NCH}__tt.pkl"]
    assert load_lut("sky130", _SKY_NCH, roots=[local, shared]).source == (
        shared / "sky130" / f"{_SKY_NCH}__tt.pkl"
    )


def test_search_luts_keys_on_the_manifest_file_name_not_its_lut_file_field(tmp_path):
    """The ngspice lane (`analog-db gmid-extract`) writes `lut_file` as `<device>__<corner>.pkl`
    for every table, tagged or not, so that field cannot tell the three tables apart.

    The listing reads the table name from the manifest's own file name instead.
    """
    kit = tmp_path / "store" / "kitpdk"
    _wf_lut(kit, "nch__tt", lut_file="nch__tt.pkl")
    _wf_lut(kit, "nch__tt__-40C", temp_k=233.15, lut_file="nch__tt.pkl")
    _wf_lut(kit, "nch__tt__wf1u", width_um=1.0, lut_file="nch__tt.pkl")

    listed = search_luts("kitpdk", roots=[tmp_path / "store"])

    assert _conditions(listed) == [(300.0, 5.0), (233.15, 5.0), (300.0, 1.0)]


def test_search_luts_lists_a_table_name_in_two_roots_once_from_the_earlier_root(tmp_path):
    """The same stem in two roots is one table as far as `load_lut` is concerned: the earlier
    root serves it, so the earlier root's manifest is the one listed.

    The two copies differ only in the `lut_file` field, which is what tells them apart here. The
    second root's 2 um table sorts after the repeated stem, so it is listed only if the repeated
    stem is skipped and the rest of that root is still read.
    """
    first, second = tmp_path / "a", tmp_path / "b"
    _wf_lut(first / "kitpdk", "nch__tt__wf1u", width_um=1.0, lut_file="from-first.pkl")
    _wf_lut(second / "kitpdk", "nch__tt__wf1u", width_um=1.0, lut_file="from-second.pkl")
    _wf_lut(second / "kitpdk", "nch__tt")
    _wf_lut(second / "kitpdk", "nch__tt__wf2u", width_um=2.0)

    listed = search_luts("kitpdk", roots=[first, second])

    assert [m.lut_file for m in listed] == ["from-first.pkl", "nch__tt.pkl", "nch__tt__wf2u.pkl"]
    assert [m.conditions.width_um for m in listed] == [1.0, 5.0, 2.0]


def test_search_luts_keeps_one_table_name_under_two_pdks_apart(tmp_path):
    """`nch__tt` under two PDKs is two tables; the `pdk` argument selects one PDK's."""
    store = tmp_path / "store"
    _wf_lut(store / "kitpdk", "nch__tt")
    _wf_lut(store / "otherpdk", "nch__tt", pdk="otherpdk")

    assert [m.pdk for m in search_luts(roots=[store])] == ["kitpdk", "otherpdk"]
    assert [m.pdk for m in search_luts("otherpdk", roots=[store])] == ["otherpdk"]
    assert search_luts("absentpdk", roots=[store]) == []
