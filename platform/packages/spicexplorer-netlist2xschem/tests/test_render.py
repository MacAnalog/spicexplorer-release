"""Render + round-trip.

The pure host check confirms graceful degradation when xschem is absent. The ``slow`` tests run only
where xschem is on PATH (the EDA container: ``docker compose exec api pytest -m slow``):

* SVG export produces a non-empty file;
* the round-trip — generate ``.sch`` → ``xschem -n -s`` → parse with ``NetlistView`` — reproduces the
  original device set and per-device net connectivity (the true correctness gate for place+wire+map).
"""

import importlib
import os
import re
import subprocess
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import build_sch, from_file, render, xschem_available
from spicexplorer_netlist2xschem.ingest import N2XCircuit, ingest
from spicexplorer_netlist2xschem.render import write_xschemrc
from spicexplorer_netlist2xschem.sym_library import SymLibrary, default_search_paths

FIXTURES = Path(__file__).parent / "fixtures"

requires_xschem = pytest.mark.skipif(not xschem_available(), reason="xschem not on PATH")


@pytest.mark.skipif(xschem_available(), reason="only meaningful when xschem is absent")
def test_render_graceful_without_xschem(tmp_path):
    sch = tmp_path / "c.sch"
    sch.write_text("v {xschem version=3.4.6 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n")
    result = render(sch, fmt="png")
    assert result.available is False
    assert result.image_path is None
    assert result.sch_path == sch  # the .sch is untouched and still valid for the UI viewer


def _normalize(circuit: N2XCircuit) -> dict[str, frozenset[str]]:
    """ref (upper, X-stripped) -> the frozenset of nets it touches (lower)."""
    out: dict[str, frozenset[str]] = {}
    for d in circuit.devices:
        ref = d.ref.upper().lstrip("X")
        out[ref] = frozenset(n.lower() for n in d.nets.values())
    return out


@requires_xschem
@pytest.mark.slow
def test_svg_export_smoke(tmp_path):
    circuit = from_file(FIXTURES / "ota-5t_tb-ac.spice", into="xota", name="ota-5t")
    sch = tmp_path / "ota-5t.sch"
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2").text)
    result = render(sch, fmt="svg", outdir=tmp_path)
    assert result.available is True
    assert result.fmt == "svg"
    assert result.image_path is not None and result.image_path.stat().st_size > 0


@requires_xschem
@pytest.mark.slow
@pytest.mark.parametrize(
    ("fixture", "kw"),
    [
        ("ota-5t_tb-ac.spice", {"into": "xota", "name": "ota-5t"}),
        ("ota-improved.spice", {"name": "ota-improved"}),
        ("folded_cascode.spice", {"into": "XDUT", "name": "folded"}),
    ],
)
def test_roundtrip_devices_and_connectivity(tmp_path, fixture, kw):
    """Generated .sch → xschem SPICE netlist → reparse: same devices + same per-device net sets.

    The true correctness gate for place+wire+map across the default topology+hybrid pipeline (rails,
    spines, port pins, gate-facing flips) — connectivity must survive aggressive wiring on every shape.
    """
    from spicexplorer_core.spice_engine import NetlistView

    circuit = from_file(FIXTURES / fixture, **kw)
    sch = tmp_path / f"{kw['name']}.sch"
    # Build (and later resolve) against the real vendored libs PLUS the checked-in fixture lib, which
    # carries the default clean ``*_np`` symbols — so this passes even against a stale EDA image (whose
    # baked symbol dirs predate the _np twins).
    lib = SymLibrary([*default_search_paths(), FIXTURES / "sym"])
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2", lib=lib).text)

    lib_path = os.pathsep.join([*(str(p) for p in default_search_paths()), str(FIXTURES / "sym")])
    # Seed the symbol path via our own rcfile so resolution is independent of the image HOME/xschemrc.
    rc = write_xschemrc(tmp_path, lib_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = lib_path
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-x", "-q", "-n", "-s", "-o", str(tmp_path), str(sch)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(tmp_path),
    )
    spice = tmp_path / f"{kw['name']}.spice"
    assert spice.is_file(), "xschem produced no netlist"

    reparsed = ingest(NetlistView.from_file(spice), name="roundtrip")
    original, roundtrip = _normalize(circuit), _normalize(reparsed)
    assert set(roundtrip) == set(original), (
        f"device set differs: only-original={set(original) - set(roundtrip)} "
        f"only-roundtrip={set(roundtrip) - set(original)}"
    )
    for ref, nets in original.items():
        assert roundtrip[ref] == nets, f"{ref}: nets {roundtrip[ref]} != original {nets}"


@requires_xschem
@pytest.mark.slow
def test_roundtrip_ihp_poly_resistor_keeps_all_three_nets_and_its_params(tmp_path):
    """`XR1 a b sub rhigh w=… l=…` → .sch → xschem's netlister → back: all three nets and both
    sizing params survive, so the 3-node PDK resistor really is drawable (not just ingestible)."""
    from spicexplorer_core.spice_engine import NetlistView
    from spicexplorer_netlist2xschem import from_string

    src = "* poly resistor\nXR1 a b sub rhigh w=0.5u l=340u\n.end\n"
    circuit = from_string(src, name="rtest")
    lib = SymLibrary([*default_search_paths(), FIXTURES / "sym"])
    sch = tmp_path / "rtest.sch"
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2", lib=lib).text)

    lib_path = os.pathsep.join([*(str(p) for p in default_search_paths()), str(FIXTURES / "sym")])
    rc = write_xschemrc(tmp_path, lib_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = lib_path
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-x", "-q", "-n", "-s", "-o", str(tmp_path), str(sch)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(tmp_path),
    )
    spice = tmp_path / "rtest.spice"
    assert spice.is_file(), "xschem produced no netlist"
    text = spice.read_text()

    back = ingest(NetlistView.from_file(spice), name="roundtrip")
    assert len(back.devices) == 1
    d = back.devices[0]
    assert d.ref.upper() == "XR1" and (d.model or "").lower() == "rhigh"
    assert list(d.nets.values()) == ["a", "b", "sub"], f"nets changed: {d.nets} in {text!r}"
    params = {k.lower(): str(v) for k, v in d.params.items()}
    assert params.get("w") == "0.5u" and params.get("l") == "340u"


@requires_xschem
@pytest.mark.slow
def test_roundtrip_braced_param_value_survives_the_netlister(tmp_path):
    """`VREF vref vss dc {vref_val}` → .sch → xschem's netlister → back: the `.param` reference is
    still there. Before the brace escaping it came back as `VREF vref vss 3` — vsource.sym's
    template default, substituted silently at exit 0, so the deck ran at the wrong supply."""
    from spicexplorer_netlist2xschem import from_string

    circuit = from_string("* v\nVREF vref vss dc {vref_val}\n.end\n", name="vtest")
    lib = SymLibrary([*default_search_paths(), FIXTURES / "sym"])
    sch = tmp_path / "vtest.sch"
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2", lib=lib).text)

    lib_path = os.pathsep.join([*(str(p) for p in default_search_paths()), str(FIXTURES / "sym")])
    rc = write_xschemrc(tmp_path, lib_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = lib_path
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-x", "-q", "-n", "-s", "-o", str(tmp_path), str(sch)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(tmp_path),
    )
    spice = tmp_path / "vtest.spice"
    assert spice.is_file(), "xschem produced no netlist"
    line = next(ln for ln in spice.read_text().splitlines() if ln.upper().startswith("VREF"))
    assert "{vref_val}" in line, f"the .param reference did not survive: {line!r}"


@requires_xschem
@pytest.mark.slow
def test_roundtrip_a_voltage_source_netlists_only_its_value(tmp_path):
    """`VDD avdd 0 dc 1` -> .sch -> xschem's netlister -> `VDD avdd 0 dc 1`, and nothing else.

    The vendored source symbols were simplified out of xschem's `tcleval()` ternary by
    CONCATENATING the two substitutions: `format="@name @pinlist @value@savecurrent"`. The
    template default then landed against the value in every netlisted card -- `VDD avdd 0 1false`,
    `Vmeas a b 0false` -- which no simulator reads as a source. Every drawn testbench was affected
    and the sheet still rendered, so it only showed up on re-netlisting. The emitter's own guard
    (emit.py: carry `savecurrent` on the instance) cannot help: with this format the substitution
    leaks whatever the value is.
    """
    from spicexplorer_netlist2xschem import from_string

    circuit = from_string("* v\nVDD avdd 0 dc 1\n.end\n", name="vdc")
    # ONLY the hermetic fixture copy: this has to assert the symbol this repo ships, and any
    # other xschem library on the search path would silently answer for it.
    lib = SymLibrary([FIXTURES / "sym"])
    sch = tmp_path / "vdc.sch"
    # show_device_params=True is the bench case: the value is on the face of the sheet, so the
    # symbol under test is vsource.sym itself rather than its no-params twin.
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2", lib=lib, show_device_params=True).text)

    lib_path = str(FIXTURES / "sym")
    rc = write_xschemrc(tmp_path, lib_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = lib_path
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-x", "-q", "-n", "-s", "-o", str(tmp_path), str(sch)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(tmp_path),
    )
    spice = tmp_path / "vdc.spice"
    assert spice.is_file(), "xschem produced no netlist"
    line = next(ln for ln in spice.read_text().splitlines() if ln.upper().startswith("VDD"))
    assert line.split() == ["VDD", "avdd", "0", "dc", "1"], f"the card carries junk: {line!r}"


@requires_xschem
@pytest.mark.slow
def test_roundtrip_two_net_pdk_capacitor_keeps_its_sizing(tmp_path):
    """`XCFF a b cap_cmim w=7u l=7u m=2` → .sch → xschem's netlister → back: w, l and m survive.
    Before, the two-net instance drew as the generic capa.sym and came back `XCFF a b cap_cmim m=1`
    — the sizing silently gone, and with it three of the LDO's failing assertion rows."""
    from spicexplorer_core.spice_engine import NetlistView
    from spicexplorer_netlist2xschem import from_string

    circuit = from_string("* c\nXCFF a b cap_cmim w=7u l=7u m=2\n.end\n", name="ctest")
    lib = SymLibrary([*default_search_paths(), FIXTURES / "sym"])
    sch = tmp_path / "ctest.sch"
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2", lib=lib).text)

    lib_path = os.pathsep.join([*(str(p) for p in default_search_paths()), str(FIXTURES / "sym")])
    rc = write_xschemrc(tmp_path, lib_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = lib_path
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-x", "-q", "-n", "-s", "-o", str(tmp_path), str(sch)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(tmp_path),
    )
    spice = tmp_path / "ctest.spice"
    assert spice.is_file(), "xschem produced no netlist"

    back = ingest(NetlistView.from_file(spice), name="roundtrip")
    assert len(back.devices) == 1
    d = back.devices[0]
    assert d.ref.upper() == "XCFF" and (d.model or "").lower() == "cap_cmim"
    assert list(d.nets.values()) == ["a", "b"], f"nets changed: {d.nets}"
    params = {k.lower(): str(v) for k, v in d.params.items()}
    assert (params.get("w"), params.get("l"), params.get("m")) == ("7u", "7u", "2"), params


# --- the render reports success only when it actually drew something (issue #159) ---------

BACKGROUND_ONLY = (
    '<?xml version="1.0"?>\n<svg width="100" height="100">\n<style>.s{}</style>\n'
    '<rect width="100" height="100" fill="black"/>\n</svg>\n'
)


def test_a_background_only_export_counts_as_nothing_drawn():
    from spicexplorer_netlist2xschem.render import drawn_elements

    assert drawn_elements(BACKGROUND_ONLY) == 0
    assert drawn_elements(BACKGROUND_ONLY.replace("<rect", "<path d='M0 0'/><rect")) == 1


@requires_xschem
def test_a_sheet_xschem_cannot_open_is_a_failure_not_a_success(tmp_path):
    """xschem exits 0 and writes a valid ~3 kB SVG holding only the background when it could
    not read the schematic. Judging by file size reported that as a rendered sheet of record."""
    sch = tmp_path / "missing.sch"
    sch.write_text("v {xschem version=3.4.6 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n")
    sch.unlink()
    sch.parent.joinpath("missing.sch").write_text("")  # empty, unparseable as a schematic

    res = render(sch, outdir=tmp_path / "img")
    assert res.image_path is None
    assert "drew NOTHING" in res.log


@requires_xschem
def test_a_relative_path_from_another_pwd_still_renders(tmp_path, monkeypatch):
    """xschem resolves a relative schematic argument against the PWD ENVIRONMENT VARIABLE, not
    the process's working directory. Any caller that is not a real shell `cd` used to get a
    valid-but-empty SVG and a success verdict."""
    src = FIXTURES / "sym"
    net = "* t\nM1 out in 0 0 nmos w=2u l=0.15u\n.end\n"
    from spicexplorer_netlist2xschem import build_sch, from_string
    from spicexplorer_netlist2xschem.sym_library import SymLibrary, default_search_paths

    work = tmp_path / "work"
    work.mkdir()
    doc = build_sch(
        from_string(net), pdk="", lib=SymLibrary(default_search_paths()), wiring="labels"
    )
    (work / "t.sch").write_text(doc.text if hasattr(doc, "text") else str(doc))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PWD", str(tmp_path))  # a stale PWD, exactly as a non-shell caller has
    res = render(Path("work/t.sch"))

    assert res.image_path is not None, res.log
    assert res.strokes > 0
    assert src.exists()  # fixtures untouched


@requires_xschem
def test_the_finger_count_survives_the_round_trip(tmp_path):
    """The whole point of the `extra=` carry: what is drawn re-netlists as what was read."""
    from spicexplorer_netlist2xschem import build_sch, from_string
    from spicexplorer_netlist2xschem.sym_library import SymLibrary, default_search_paths
    from spicexplorer_netlist2xschem.virtuoso_export.endcheck import xschem_source_netlist

    net = "* t\nM1 out in 0 0 nmos_lvt w=32.4747u l=0.15u nf=16 m=2\n.end\n"
    doc = build_sch(
        from_string(net), pdk="", lib=SymLibrary(default_search_paths()), wiring="labels"
    )
    sch = tmp_path / "t.sch"
    sch.write_text(doc.text if hasattr(doc, "text") else str(doc))

    back = xschem_source_netlist(sch, tmp_path / "nl").read_text()
    card = next(ln for ln in back.splitlines() if ln.startswith("M1"))
    assert "nf=16" in card and "w=32.4747u" in card and "m=2" in card


def test_the_generated_rc_is_light_by_default_and_dark_on_request():
    """xschem's own default is the dark scheme, whose strokes come out pale on the white page a
    report is printed on — every commercial-kit render had to be post-processed by hand."""
    from spicexplorer_netlist2xschem.render import _rcfile_text

    assert "set dark_colorscheme 0" in _rcfile_text("/x")
    assert "dark_colorscheme" not in _rcfile_text("/x", dark=True)


def test_an_open_pdk_symbol_library_is_not_appended_for_another_kit():
    """A commercial-kit design's own denylist trips on the vendored open-PDK symbol dir, which
    used to be appended whatever --pdk said (issue #159)."""
    from spicexplorer_netlist2xschem.sym_library import VENDORED_PDK, default_search_paths

    for_other = [str(p) for p in default_search_paths("generic-n65")]
    for_ihp = [str(p) for p in default_search_paths(VENDORED_PDK)]

    assert not any(VENDORED_PDK in p for p in for_other)
    assert any(VENDORED_PDK in p for p in for_ihp)
    # the generic devices/ library is every PDK's, and must survive the scoping
    assert any(p.endswith("xschem_library") for p in for_other)


def test_geometry_outside_the_viewport_is_brought_back_and_a_fitting_export_is_untouched():
    from spicexplorer_netlist2xschem.render import fit_viewport

    head = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="80" version="1.1">'
    inside = f'{head}\n<path class="l4" d="M 10 10 L 90 70"/>\n</svg>\n'
    assert fit_viewport(inside) == inside  # byte-identical when nothing falls out

    clipped = f'{head}\n<path class="l4" d="M -40 10 L 90 70"/>\n<text x="-40" y="12">agnd</text>\n</svg>\n'
    out = fit_viewport(clipped)
    assert 'viewBox="-48 -8 ' in out
    assert 'width="156"' in out  # -48 .. 108


def test_a_class_name_is_not_mistaken_for_a_coordinate():
    """`class="l4"` and `stroke-width="7.9"` are numbers too; reading them put the viewport at
    x=888816 on the first real sheet."""
    from spicexplorer_netlist2xschem.render import fit_viewport

    svg = (
        '<svg width="100" height="80">\n'
        '<path class="l4" stroke-width="7.92177" d="M 10 10 L 90 70"/>\n</svg>\n'
    )
    assert fit_viewport(svg) == svg


def test_a_translated_text_element_widens_the_viewport():
    """xschem places every string with ``transform="translate(..)"`` and no ``x``/``y``, so reading
    coordinates off attributes alone made ``fit_viewport`` a no-op for the very case it was added
    for: a port name at the left edge stayed clipped (issue #224)."""
    from spicexplorer_netlist2xschem.render import fit_viewport

    head = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="80" version="1.1">'
    svg = (
        f"{head}\n"
        '<path class="l4" d="M 10 10 L 90 70"/>\n'
        '<text fill="#222222" xml:space="preserve" font-size="8" '
        'transform="translate(-30, 40)" >rstb</text>\n'
        "</svg>\n"
    )
    out = fit_viewport(svg)
    # the label's anchor is at x=-30; the viewport must reach it (plus the 8-unit margin)
    assert 'viewBox="-38 -8 146 96"' in out
    assert 'width="146"' in out  # -38 .. 108 (the 8-unit margin on each side)


def test_the_drawn_width_of_an_edge_label_is_reserved_not_just_its_anchor():
    """A right-edge label ANCHORED inside the sheet still runs off it — the bug is the string's
    width, which the SVG never states, so it is estimated from font-size x character count."""
    from spicexplorer_netlist2xschem.render import fit_viewport

    head = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="80">'
    svg = (
        f"{head}\n"
        '<path class="l4" d="M 10 10 L 90 70"/>\n'
        '<text font-size="10" transform="translate(95, 40)" >vdd_supply</text>\n'
        "</svg>\n"
    )
    out = fit_viewport(svg)
    # 10 chars * 10 units * 0.6 em = 60 units of text, from x=95 -> 155, then the 8-unit margin
    assert 'viewBox="-8 -8 171 96"' in out
    assert 'width="171"' in out


def test_translate_without_a_comma_and_an_end_anchored_label():
    """``translate(X Y)`` (no comma) is the same placement, and ``text-anchor="end"`` runs the
    string LEFTWARD from its anchor — the direction the reserved width has to follow."""
    from spicexplorer_netlist2xschem.render import fit_viewport

    head = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="80">'
    svg = (
        f"{head}\n"
        '<path class="l4" d="M 10 10 L 90 70"/>\n'
        '<text font-size="10" text-anchor="end" transform="translate(20 40)" >clkb</text>\n'
        "</svg>\n"
    )
    out = fit_viewport(svg)
    # 4 chars * 10 * 0.6 = 24 units, leftward from x=20 -> -4, then the 8-unit margin
    assert 'viewBox="-12 -8 120 96"' in out
    assert 'width="120"' in out


def test_an_entity_in_a_label_counts_as_one_character():
    """``&amp;`` draws as one glyph; counting its five source characters would over-reserve."""
    from spicexplorer_netlist2xschem.render import _text_box

    xs, _ = _text_box(' font-size="10" transform="translate(0, 0)" ', "a&amp;b")
    assert xs == [0.0, 3 * 10 * 0.6]


# --- the exported SVG must survive a renderer that reads only attributes (issue #225) ----------

_STYLED = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="700">\n'
    '<style type="text/css">\n'
    ".l7{\n fill: #ff0000; fill-opacity: 0.5;\n  stroke: #ff0000;\n"
    "  stroke-linecap:round;\n  stroke-width: 0.407379;\n}\n"
    ".l21{\n fill: none;\n  stroke: #fdb200;\n  stroke-linecap:round;\n"
    "  stroke-width: 0.407379;\n}\n"
    "</style>\n"
    '<path class="l7" d="M302.928 569.607L302.928 586.582"/>\n'
    '<path class="l21" d="M90.7518 630.903L896.08 630.903"/>\n'
    '<path class="l21" d="M90.2 630.4L91.2 630.4L91.2 631.3L90.2 631.3L90.2 630.4z"/>\n'
    '<path class="l7" stroke="#00ff00" d="M10 10L20 20"/>\n'
    "</svg>\n"
)


def _tag(svg: str, marker: str) -> str:
    import re as _re

    return next(t for t in _re.findall(r"<path[^>]*>", svg) if marker in t)


def test_class_declarations_are_inlined_as_presentation_attributes():
    """Styling carried only by a CSS class is invisible to a renderer that does not apply the
    stylesheet, so the declarations are copied onto the element (issue #225)."""
    from spicexplorer_netlist2xschem.render import stroke_safe_svg

    out = stroke_safe_svg(_STYLED)
    tag = _tag(out, "M302.928")
    assert 'stroke="#ff0000"' in tag
    assert 'stroke-width="0.407379"' in tag
    assert 'fill="#ff0000"' in tag
    assert "<style" in out  # the stylesheet STAYS: a conformant renderer keeps using it unchanged


def test_the_inlined_attributes_come_after_the_class_attribute():
    """ImageMagick applies attributes in source order and lets a later ``class`` overwrite an
    earlier one, so a ``fill`` written BEFORE ``class`` is undone by the rule it must beat —
    measured as an identical raster with the supply rails still missing."""
    from spicexplorer_netlist2xschem.render import stroke_safe_svg

    tag = _tag(stroke_safe_svg(_STYLED), "M302.928")
    assert tag.index("class=") < tag.index("fill=")


def test_a_zero_area_unfilled_path_is_given_a_fill_equal_to_its_stroke():
    """``fill:none`` paths are not drawn AT ALL by ImageMagick's built-in renderer, stroke included
    — which is why a highlight palette decides which wires survive rasterization. A path enclosing
    zero area can be filled with no effect anywhere, so it is."""
    from spicexplorer_netlist2xschem.render import stroke_safe_svg

    out = stroke_safe_svg(_STYLED)
    assert 'fill="#fdb200"' in _tag(out, "M90.7518")  # the two-point supply rail
    assert 'fill="none"' in _tag(out, "M90.2 630.4")  # a CLOSED outline keeps its unfilled interior


def test_an_attribute_the_element_already_carries_is_never_overridden():
    from spicexplorer_netlist2xschem.render import stroke_safe_svg

    tag = _tag(stroke_safe_svg(_STYLED), "M10 10")
    assert 'stroke="#00ff00"' in tag
    assert 'stroke="#ff0000"' not in tag


def test_fill_opacity_is_read_but_not_inlined():
    """ImageMagick multiplies the STROKE by ``fill-opacity`` too, so inlining xschem's 0.5 highlight
    would hand it half-strength wires. The stylesheet keeps it for renderers that are correct."""
    from spicexplorer_netlist2xschem.render import stroke_safe_svg

    assert "fill-opacity=" not in stroke_safe_svg(_STYLED)
    assert "fill-opacity: 0.5" in stroke_safe_svg(_STYLED)  # still in the <style> block


def test_an_svg_with_no_stylesheet_is_returned_unchanged():
    from spicexplorer_netlist2xschem.render import stroke_safe_svg

    svg = '<svg width="10" height="10"><path stroke="#000" d="M0 0L9 9"/></svg>'
    assert stroke_safe_svg(svg) == svg


def _fake_run(written: list[str]):
    def run(cmd, **kwargs):  # noqa: ANN001, ANN003 - a stand-in for subprocess.run
        import subprocess as _sp

        png = next(a for a in cmd if str(a).endswith(".png"))
        Path(png).write_bytes(b"\x89PNG\r\n\x1a\n")
        written.append(str(cmd[0]))
        return _sp.CompletedProcess(cmd, 0, "", "")

    return run


def test_rsvg_convert_is_preferred_over_imagemagick(tmp_path, monkeypatch, caplog):
    import sys

    # the package re-exports the `render` FUNCTION under that name, so ask for the module
    render_mod = importlib.import_module("spicexplorer_netlist2xschem.render")

    monkeypatch.setitem(sys.modules, "cairosvg", None)  # force the import to fail
    monkeypatch.setattr(
        render_mod.shutil,
        "which",
        lambda name: f"/usr/bin/{name}",  # both tools present
    )
    used: list[str] = []
    monkeypatch.setattr(render_mod.subprocess, "run", _fake_run(used))
    svg = tmp_path / "s.svg"
    svg.write_text('<svg width="1000" height="700"></svg>')
    with caplog.at_level("WARNING"):
        rasterizer, note = render_mod._rasterize(svg, tmp_path / "s.png", 1600)
    assert rasterizer == "rsvg-convert"
    assert used == ["/usr/bin/rsvg-convert"]
    assert "#225" not in note and not caplog.records  # nothing to warn about


def test_the_imagemagick_fallback_warns_loudly_and_names_the_issue(tmp_path, monkeypatch, caplog):
    """The MSVG fallback loses drawing, so taking it is never silent (issue #225)."""
    import sys

    # the package re-exports the `render` FUNCTION under that name, so ask for the module
    render_mod = importlib.import_module("spicexplorer_netlist2xschem.render")

    monkeypatch.setitem(sys.modules, "cairosvg", None)
    monkeypatch.setattr(
        render_mod.shutil,
        "which",
        lambda name: None if name == "rsvg-convert" else "/usr/bin/magick",
    )
    used: list[str] = []
    monkeypatch.setattr(render_mod.subprocess, "run", _fake_run(used))
    svg = tmp_path / "s.svg"
    svg.write_text('<svg width="800" height="700"></svg>')
    with caplog.at_level("WARNING"):
        rasterizer, note = render_mod._rasterize(svg, tmp_path / "s.png", 1600)
    assert rasterizer == "imagemagick"
    assert used == ["/usr/bin/magick"]
    assert "issue #225" in note and "MISSING WIRES" in note
    assert any("issue #225" in r.getMessage() for r in caplog.records)


def test_no_rasterizer_at_all_is_reported_not_guessed(tmp_path, monkeypatch):
    import sys

    # the package re-exports the `render` FUNCTION under that name, so ask for the module
    render_mod = importlib.import_module("spicexplorer_netlist2xschem.render")

    monkeypatch.setitem(sys.modules, "cairosvg", None)
    monkeypatch.setattr(render_mod.shutil, "which", lambda name: None)
    svg = tmp_path / "s.svg"
    svg.write_text('<svg width="10" height="10"></svg>')
    rasterizer, note = render_mod._rasterize(svg, tmp_path / "s.png", 1600)
    assert rasterizer is None
    assert "No rasterizer available." in note


# --- the generated xschemrc records no checkout (issue #248) ------------------------------

#: A two-pin symbol that exists only beside the sheet under test, so the ONLY way xschem can
#: resolve it is the design-local library entry the rc writes.
_LOCAL_SYM = """v {xschem version=3.4.4 file_version=1.2}
G {}
K {type=resistor
format="@name @pinlist @value"
template="name=R1 value=1k"
}
V {}
S {}
E {}
L 4 -20 0 -10 0 {}
L 4 10 0 20 0 {}
B 5 -22.5 -2.5 -17.5 2.5 {name=p dir=inout}
B 5 17.5 -2.5 22.5 2.5 {name=m dir=inout}
"""

_LOCAL_SCH = """v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
C {local_block.sym} 0 0 0 0 {name=R1 value=1k}
N -60 0 -20 0 { lab=in}
N 20 0 60 0 { lab=out}
"""


def test_the_output_directory_writes_itself_as_a_dot_and_keeps_the_rest_absolute(tmp_path):
    """The rc is a build product a design COMMITS beside its sheets, so it may not record which
    checkout drew them (issue #248): its own directory is `.`, an entry nested inside it is
    relative to it, and an entry outside it is untouched."""
    from spicexplorer_netlist2xschem.render import _rcfile_text

    out = tmp_path / "doc" / "schematics"
    (out / "blocks").mkdir(parents=True)
    outside = tmp_path / "platform" / "docker" / "xschem_library"
    outside.mkdir(parents=True)
    lib_path = os.pathsep.join([str(out), str(out / "blocks"), str(outside)])

    text = _rcfile_text(lib_path, relative_to=out)

    assert "append XSCHEM_LIBRARY_PATH {:.}" in text
    assert "append XSCHEM_LIBRARY_PATH {:blocks}" in text
    assert f"append XSCHEM_LIBRARY_PATH {{:{outside}}}" in text
    assert str(out) not in text  # no entry names the build directory any more


def test_the_same_sheet_written_from_two_directories_gives_a_byte_identical_rc(tmp_path):
    """Two checkouts, one committed file: what used to differ was exactly the line naming the
    build directory (in one design, three revisions naming three checkouts, the last a throwaway
    worktree)."""
    shared = tmp_path / "shared" / "xschem_library"
    shared.mkdir(parents=True)
    rcs = []
    for name in ("checkout-a", "some/deeper/checkout-b"):
        out = tmp_path / name / "doc" / "schematics"
        out.mkdir(parents=True)
        lib_path = os.pathsep.join([str(out), str(shared)])
        rcs.append(write_xschemrc(out, lib_path).read_bytes())

    assert rcs[0] == rcs[1]
    assert b":." in rcs[0]


@requires_xschem
def test_a_renetlist_from_the_output_dir_still_resolves_the_design_local_symbols(tmp_path):
    """`.` is not just tidier, it RESOLVES: xschem run from the output directory finds a symbol
    that exists nowhere else, with no absolute entry and no env var to fall back on."""
    out = tmp_path / "schematics"
    out.mkdir()
    (out / "local_block.sym").write_text(_LOCAL_SYM)
    (out / "cell.sch").write_text(_LOCAL_SCH)

    rc = write_xschemrc(out, str(out))
    assert ":." in rc.read_text() and str(out) not in rc.read_text()

    # No XSCHEM_LIBRARY_PATH in the environment: the rc's `.` is the only thing that can resolve
    # the symbol. The schematic argument is ABSOLUTE and `PWD` matches `cwd`, exactly as
    # :func:`render` invokes xschem (it resolves a relative sheet against `$PWD`, not against cwd).
    env = {k: v for k, v in os.environ.items() if k != "XSCHEM_LIBRARY_PATH"}
    env["PWD"] = str(out)
    subprocess.run(
        [
            "xschem",
            "--rcfile",
            str(rc),
            "-x",
            "-q",
            "-n",
            "-s",
            "-o",
            str(out),
            str(out / "cell.sch"),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(out),
    )
    netlist = out / "cell.spice"
    assert netlist.is_file(), "xschem produced no netlist"
    card = [ln for ln in netlist.read_text().splitlines() if ln.startswith("R1 ")]
    assert card, f"the design-local symbol did not resolve:\n{netlist.read_text()}"


@requires_xschem
def test_two_renders_of_one_sheet_from_two_directories_write_the_same_rc(tmp_path):
    """The end-to-end shape of issue #248: render the same sheet into two different output
    directories and the committed `xschemrc` is byte-identical."""
    written = []
    for name in ("build-a", "nested/build-b"):
        out = tmp_path / name
        out.mkdir(parents=True)
        (out / "local_block.sym").write_text(_LOCAL_SYM)
        sch = out / "cell.sch"
        sch.write_text(_LOCAL_SCH)
        result = render(sch, fmt="svg", outdir=out, library_path=str(out))
        assert result.available and result.image_path is not None, result.log
        written.append((out / "xschemrc").read_bytes())

    assert written[0] == written[1]


# --- the sheet's own text survives the export, or is reported (issue #239) ----------------

#: The shape from issue #239: the TITLE is the topmost object on the page (`y = -200`), above the
#: topmost wire (`y = -140`), and the sheet is narrow enough that xschem's export window — sized
#: from the DRAWN objects and padded to the export aspect — does not reach it. The record is then
#: absent from the SVG, not clipped in it.
TITLE_ABOVE_BBOX = FIXTURES / "title_above_bbox.sch"
_TITLE = "slice level 0 -- sheet of record"


def test_a_text_record_outside_the_drawn_window_is_detected_as_missing():
    """The guard reads the records, not a count: the reported sheet had 20 `<text>` elements and
    no title, because symbol text outnumbers a sheet's own records many times over."""
    from spicexplorer_netlist2xschem.render import missing_sheet_text

    sch = TITLE_ABOVE_BBOX.read_text()
    no_title = '<svg><text x="0" y="0">out_a</text><text x="0" y="0">in_a</text></svg>'
    with_title = f'<svg><text x="0" y="0">{_TITLE}</text></svg>'

    assert missing_sheet_text(sch, no_title) == (_TITLE,)
    assert missing_sheet_text(sch, with_title) == ()


def test_a_substituted_or_hidden_record_is_not_judged():
    """`@name` is resolved at draw time and `hide=true` draws nothing — neither can be decided by
    looking for the file's own string, so neither is reported as a drop."""
    from spicexplorer_netlist2xschem.render import missing_sheet_text

    sch = (
        "v {xschem version=3.4.4 file_version=1.2}\nG {}\nK {}\nV {}\nS {}\nE {}\n"
        "T {@name} 0 0 0 0 0.4 0.4 {}\n"
        "T {a note} 0 20 0 0 0.4 0.4 {hide=true}\n"
        "T {the visible one} 0 40 0 0 0.4 0.4 {}\n"
        "N 0 0 100 0 {}\n"
    )
    assert missing_sheet_text(sch, "<svg></svg>") == ("the visible one",)


def test_the_extent_object_is_invisible_and_leaves_the_record_where_it_was():
    """The fix adds geometry, it does not move the author's caption: a layer-0 line (the
    background colour in both schemes) across the text's extent."""
    from spicexplorer_netlist2xschem.render import with_text_extents

    sch = TITLE_ABOVE_BBOX.read_text()
    patched = with_text_extents(sch, (_TITLE,))

    assert f"T {{{_TITLE}}} -40 -200 0 0 0.4 0.4 {{}}" in patched  # the record is untouched
    added = [ln for ln in patched.splitlines() if ln.startswith("L ")]
    assert len(added) == 1 and added[0].startswith("L 0 -40 -200 ")
    assert with_text_extents(sch, ()) == sch  # nothing asked for, nothing added


@requires_xschem
def test_the_title_is_dropped_by_xschem_and_the_render_brings_it_back(tmp_path):
    """The issue end to end. Exporting the fixture as-is loses the title; `render()` notices,
    re-exports from a copy carrying the extent object, and the title is in the SVG."""
    from spicexplorer_netlist2xschem.render import missing_sheet_text

    sch = tmp_path / TITLE_ABOVE_BBOX.name
    sch.write_text(TITLE_ABOVE_BBOX.read_text())
    before = sch.read_bytes()

    # 1. the defect: a plain export of this sheet has no title in it at all
    plain = tmp_path / "plain"
    plain.mkdir()
    rc = write_xschemrc(plain, str(tmp_path))
    subprocess.run(
        [
            "xschem",
            "--rcfile",
            str(rc),
            "-x",
            "-q",
            "--svg",
            "--plotfile",
            str(plain / "plain.svg"),
            str(sch),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(plain),
    )
    raw = (plain / "plain.svg").read_text()
    assert _TITLE not in raw, "the fixture no longer reproduces the drop"
    assert missing_sheet_text(sch.read_text(), raw) == (_TITLE,)

    # 2. the fix: render() gets it back, and says nothing is missing. Default color_nets=True, so
    # this also covers the select_all/hilight export path, not just plain `--svg`.
    result = render(sch, fmt="svg", outdir=tmp_path)
    assert result.available and result.image_path is not None, result.log
    assert result.texts_dropped == (), result.log
    exported = result.image_path.read_text()
    assert _TITLE in exported
    assert result.text_elements >= 1
    assert sch.read_bytes() == before  # the committed .sch is never modified
    assert not [p for p in tmp_path.iterdir() if p.name.startswith(".n2x-extent-")]
    assert "n2x-extent" not in exported  # the scratch copy's path does not leak into the image
    # the extent line is drawn on layer 0 — the BACKGROUND colour, in either colour scheme
    assert 'class="l0"' in exported
    assert re.search(r"\.l0\{[^}]*fill:\s*#ffffff", exported), "layer 0 is not the light background"


@requires_xschem
def test_a_sheet_whose_text_already_renders_is_not_touched(tmp_path):
    """Every sheet this package generates places its title ABOVE the drawn objects and renders it
    today (the export window is padded to the export aspect, so a wide sheet reaches it). The
    guard must not rewrite those: no drop reported, no second export."""
    circuit = from_file(FIXTURES / "ota-5t_tb-ac.spice", into="xota", name="ota-5t")
    lib = SymLibrary([*default_search_paths(), FIXTURES / "sym"])
    sch = tmp_path / "ota-5t.sch"
    sch.write_text(build_sch(circuit, pdk="ihp-sg13g2", lib=lib, title="ota-5t sheet").text)
    lib_path = os.pathsep.join([*(str(p) for p in default_search_paths()), str(FIXTURES / "sym")])

    result = render(sch, fmt="svg", outdir=tmp_path, library_path=lib_path)

    assert result.texts_dropped == (), result.log
    assert "extent object" not in result.log  # no re-export happened
    assert "ota-5t sheet" in (result.image_path or sch).read_text()
