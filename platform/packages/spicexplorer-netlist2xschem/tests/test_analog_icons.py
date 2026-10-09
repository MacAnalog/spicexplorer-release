"""Functional icons — a block symbol that says what the block IS, and still netlists identically.

The whole feature rests on one structural claim: **an icon replaces the body lines and nothing
else**. Every ``B`` pin record, every stub and every pin label is the plain block symbol's, byte for
byte, so an icon cannot move, rename or reorder a pin (gates 1 and 3 are untouchable by a drawing
change). These tests assert that claim three ways — byte comparison, parsed pin list, and the real
xschem netlister on a two-level hierarchy — and then assert the part a netlist gate can *never* see:
that a ``+`` lands beside the pin that is actually the non-inverting input, and that nothing is
drawn when the pin names do not say which input is which.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    BlockAnnotation,
    BlockAnnotationSet,
    build_hierarchical_sch,
    from_string,
    parse_symbol,
    write_hierarchy,
)
from spicexplorer_netlist2xschem.render import write_xschemrc
from spicexplorer_netlist2xschem.sym_library import SymLibrary, default_search_paths
from spicexplorer_netlist2xschem.symbol_gen import (
    BlockPin,
    generate_block_symbol,
    generate_icon_symbol,
)
from spicexplorer_netlist2xschem.symbols import analog_icons

FIXTURES = Path(__file__).parent / "fixtures"
SYM_ROOT = FIXTURES / "sym"

ICONS = analog_icons.icon_names()

#: A pin list that exercises all four sides and names its inputs conventionally.
PINS = [
    BlockPin("clk", "left", "in"),
    BlockPin("vin", "left", "in"),
    BlockPin("vip", "left", "in"),
    BlockPin("vout", "right", "out", label="out"),
    BlockPin("vdd", "top", "inout"),
    BlockPin("vss", "bottom", "inout"),
]


def _tail(text: str) -> list[str]:
    """Everything from the first pin record on — pins, stubs, labels, the name/instance text."""
    lines = text.splitlines()
    first = next(i for i, ln in enumerate(lines) if ln.startswith("B "))
    return lines[first:]


def _body(text: str) -> list[str]:
    """The drawn body: the ``L`` records before the first pin record."""
    lines = text.splitlines()
    first = next(i for i, ln in enumerate(lines) if ln.startswith("B "))
    return [ln for ln in lines[:first] if ln.startswith("L ")]


# --------------------------------------------------------------- the pins cannot move ----------


@pytest.mark.parametrize("icon", ICONS)
def test_an_icon_changes_the_body_and_only_the_body(icon):
    """Byte comparison: pins, stubs and labels are the plain symbol's; only the body lines differ."""
    plain = generate_block_symbol("blk", PINS)
    drawn = generate_icon_symbol("blk", PINS, icon, scale=1.0)
    assert _tail(drawn.text) == _tail(plain.text), (
        f"{icon}: an icon moved something that is not the body"
    )
    assert drawn.pins == plain.pins, f"{icon}: an icon moved a connection point"
    assert _body(drawn.text) != _body(plain.text), f"{icon}: nothing was drawn"


@pytest.mark.parametrize("icon", ICONS)
def test_the_pin_list_xschem_reads_is_unchanged(icon):
    """Parsed the way xschem parses it: same pins, same order, same directions, same coordinates."""
    plain = parse_symbol(generate_block_symbol("blk", PINS).text)
    drawn = parse_symbol(generate_icon_symbol("blk", PINS, icon, scale=1.0).text)
    assert [(p.name, p.x, p.y, p.dir) for p in drawn.pins] == [
        (p.name, p.x, p.y, p.dir) for p in plain.pins
    ]
    # The stock ``type=subcircuit`` + ``@symname`` format is what makes a PER-CELL icon work at
    # all: a shared icon file would bind every instance's child schematic to the icon's own
    # basename, and a ``@value``-style format would add a spurious port on top of that.
    text = generate_icon_symbol("blk", PINS, icon, scale=1.0).text
    assert "type=subcircuit" in text
    assert "@symname" in text and "@value" not in text


@pytest.mark.parametrize("icon", ICONS)
def test_an_icon_fits_a_two_pin_block_and_a_thirty_pin_block(icon):
    """A glyph is a function of the generated geometry — it draws at any pin count, and inside the box."""
    for pins in (
        [BlockPin("a", "left"), BlockPin("b", "right")],
        [BlockPin(f"i{i}", "left") for i in range(15)]
        + [BlockPin(f"o{i}", "right") for i in range(15)],
    ):
        sym = generate_icon_symbol("blk", pins, icon, scale=1.0)
        # the body box the plain symbol drew for the SAME pin list is the frame a glyph must stay in
        corners = [
            int(v) for ln in _body(generate_block_symbol("blk", pins).text) for v in ln.split()[2:6]
        ]
        half_w, half_h = max(corners[0::2]), max(corners[1::2])
        for ln in _body(sym.text):
            _, _layer, x1, y1, x2, y2, *_rest = ln.split()
            for x in (int(x1), int(x2)):
                assert abs(x) <= half_w, f"{icon}: drew outside the body at x={x}"
            for y in (int(y1), int(y2)):
                assert abs(y) <= half_h + 1, f"{icon}: drew outside the body at y={y}"


def test_scale_grows_the_symbol_without_touching_the_pin_list():
    """The per-icon scale exists because the body is sized from the PIN COUNT (a 7-pin block beside
    a 56-pin one is unreadable). It may move the geometry; it may not touch a pin's identity."""
    plain = generate_block_symbol("blk", PINS)
    big = generate_icon_symbol("blk", PINS, "opamp", scale=2.0)
    assert list(big.pins) == list(plain.pins)  # same nets, same order
    assert all(
        abs(big.pins[net][0]) > abs(plain.pins[net][0])
        or abs(big.pins[net][1]) > abs(plain.pins[net][1])
        for net in plain.pins
    )
    assert [p.dir for p in parse_symbol(big.text).pins] == [
        p.dir for p in parse_symbol(plain.text).pins
    ]


def test_a_scale_spec_and_an_explicit_scale_agree():
    assert (
        generate_icon_symbol("blk", PINS, "opamp@1.6").text
        == generate_icon_symbol("blk", PINS, "opamp", scale=1.6).text
    )


# ------------------------------------------------- the marks follow the pins, or are not drawn ---


def _plus_mark_y(text: str) -> int | None:
    """The y of the ``+`` mark's vertical stroke (the only short vertical body line at |x| < half)."""
    verticals = [
        (int(a), int(b), int(c), int(d))
        for _, _layer, a, b, c, d, *_ in (ln.split() for ln in _body(text))
        if int(a) == int(c) and abs(int(b) - int(d)) < 40
    ]
    return (verticals[0][1] + verticals[0][3]) // 2 if verticals else None


def test_the_input_marks_are_read_from_the_pin_list_not_from_a_position():
    """The member's finding, generalised: a ``.subckt`` header that lists ``clk vin vip`` puts the
    INVERTING input above the non-inverting one, so a ``+`` drawn at a fixed "upper third" of the
    body marks the wrong pin — and re-netlists perfectly while doing it. Swap the two inputs in the
    pin list and the marks must swap with them."""
    a = generate_icon_symbol("cmp", PINS, "comparator", scale=1.0)
    swapped = [
        BlockPin("clk", "left", "in"),
        BlockPin("vip", "left", "in"),
        BlockPin("vin", "left", "in"),
        *PINS[3:],
    ]
    b = generate_icon_symbol("cmp", swapped, "comparator", scale=1.0)
    y_a, y_b = _plus_mark_y(a.text), _plus_mark_y(b.text)
    assert y_a is not None and y_b is not None, "the + mark was not drawn"
    # vip is the third left pin in `a` and the second in `b`; the mark sits on its row either way.
    assert abs(y_a - a.pins["vip"][1]) < 20
    assert abs(y_b - b.pins["vip"][1]) < 20
    assert y_a != y_b, "the mark did not follow the pin"


def test_unconventional_input_names_draw_no_mark_and_say_so():
    """No guess. A block whose inputs are ``a``/``b`` gets the triangle and no ``+``/``-`` at all,
    plus a note naming the pins it looked at — a wrong mark is worse than no mark."""
    pins = [BlockPin("a", "left"), BlockPin("b", "left"), BlockPin("z", "right")]
    sym = generate_icon_symbol("amp", pins, "opamp")
    assert _plus_mark_y(sym.text) is None
    assert any("+/-" in w for w in sym.warnings)
    assert "a, b, z" in sym.warnings[0]


def test_a_lone_input_named_vin_is_not_marked_as_inverting():
    """``vin`` is the inverting input of a ``vip``/``vin`` pair — and the ONLY input of many cells.
    It may only ever be marked when its non-inverting partner is there too."""
    pins = [BlockPin("vin", "left"), BlockPin("vout", "right")]
    sym = generate_icon_symbol("amp", pins, "opamp")
    assert _plus_mark_y(sym.text) is None
    assert sym.warnings


def test_the_clock_wedge_lands_on_the_clock_pin():
    sym = generate_icon_symbol("cmp", PINS, "comparator", scale=1.0)
    assert not sym.warnings  # clk found, +/- found
    plain_cmp = generate_icon_symbol(
        "cmp", [p for p in PINS if p.net != "clk"], "comparator", scale=1.0
    )
    assert any("no clock mark" in w for w in plain_cmp.warnings)


# ------------------------------------------------------------------- the registry + the mapping --


def test_every_icon_the_issue_asked_for_is_registered():
    assert set(ICONS) == {
        "adc",
        "chopper",
        "comparator",
        "dac",
        "integrator",
        "ldo",
        "opamp",
        "switch",
    }
    assert analog_icons.resolve("OTA") is analog_icons.resolve("opamp")
    assert analog_icons.resolve("sampler") is analog_icons.resolve("switch")


def test_an_unknown_icon_names_the_ones_that_exist():
    with pytest.raises(ValueError, match="comparator"):
        analog_icons.parse_spec("triangle-ish")
    with pytest.raises(ValueError, match="scale"):
        analog_icons.parse_spec("opamp@huge")


def test_the_automatic_mapping_only_fires_where_it_is_unambiguous():
    """A recognised block type maps to an icon only when the mapping asserts nothing extra.

    The shipped detector catalogue recognises transistor-level families; a transmission gate IS an
    analog switch, a differential pair is one *stage* of an amplifier and not an opamp, and a
    current mirror is not any of these icons. Guessing here would put a functional claim on a sheet
    of record that no gate can contradict."""
    tg = analog_icons.icon_for_family("transmission_gate")
    assert tg is not None and tg.name == "switch"
    comparator = analog_icons.icon_for_family("comparator")
    assert comparator is not None and comparator.name == "comparator"
    assert analog_icons.icon_for_family("differential_pair") is None
    assert analog_icons.icon_for_family("current_mirror") is None
    assert analog_icons.icon_for_family("cross_coupled") is None
    by_template = analog_icons.icon_for_family("", "tg.pair.cmos")
    assert by_template is not None and by_template.name == "switch"
    assert analog_icons.icon_for_family("", "cm.nmos.simple") is None


# ------------------------------------------------------------------------- the hierarchy lane ----

NETLIST = """\
* a strobed stage and a pass pair -- two blocks, so the sheet is a two-level hierarchy
XM1 vout vip vtail vss nmos_a w=2u l=0.5u
XM2 vob  vin vtail vss nmos_a w=2u l=0.5u
XM3 vtail clk vss vss nmos_a w=4u l=0.5u
XM4 vout smp vob vss nmos_a w=1u l=0.5u
XM5 vob  smp vout vdd pmos_b w=1u l=0.5u
.end
"""


def _hierarchy(**kwargs):
    circuit = from_string(NETLIST, name="stage")
    aset = BlockAnnotationSet(
        (
            BlockAnnotation(
                "cmp_stage",
                ("XM1", "XM2", "XM3"),
                family="comparator",
                port_name_map=(("vin", "vin"), ("vip", "vip"), ("clk", "clk")),
            ),
            BlockAnnotation("pass_pair", ("XM4", "XM5"), family="transmission_gate"),
        )
    )
    return build_hierarchical_sch(circuit, aset, lib=SymLibrary([SYM_ROOT]), **kwargs)


def test_a_recognised_block_type_is_drawn_with_its_icon_automatically():
    res = _hierarchy()
    assert res.icons == {"cmp_stage": "comparator", "pass_pair": "switch"}
    assert "@symname" in res.symbols["cmp_stage.sym"]


def test_an_explicit_request_wins_and_a_typo_is_reported():
    res = _hierarchy(icons={"cmp_stage": "opamp", "no_such_cell": "ldo"})
    assert res.icons["cmp_stage"] == "opamp"
    assert any("no_such_cell" in w and "no block matched" in w for w in res.warnings)


def test_auto_icons_can_be_turned_off():
    assert _hierarchy(auto_icons=False).icons == {}


def test_the_icon_symbol_has_the_same_pins_as_the_plain_one_in_the_hierarchy():
    plain = _hierarchy(auto_icons=False)
    drawn = _hierarchy()
    for name in plain.symbols:
        assert _tail(drawn.symbols[name]) == _tail(plain.symbols[name])
    assert plain.block_pins == drawn.block_pins
    assert (
        plain.parent_text == drawn.parent_text
    )  # the sheet places the same cells at the same spots


# ------------------------------------------------------------------- gate 1, through real xschem -


def _xschem_netlist(work: Path, stem: str) -> str:
    """Netlist a written hierarchy with real headless xschem (the third-party oracle)."""
    entries = [str(SYM_ROOT), str(SYM_ROOT / "devices"), str(work)]
    for root in default_search_paths():
        entries.append(str(root))
        if (root / "devices").is_dir():
            entries.append(str(root / "devices"))
    library_path = os.pathsep.join(dict.fromkeys(entries))
    rc = write_xschemrc(work, library_path)
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
            str(work),
            str(work / f"{stem}.sch"),
        ],
        env=dict(os.environ, XSCHEM_LIBRARY_PATH=library_path),
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(work),
    )
    out = work / f"{stem}.spice"
    assert out.is_file(), "xschem produced no netlist"
    return "\n".join(
        ln for ln in out.read_text().splitlines() if ln.strip() and not ln.startswith("*")
    )


@pytest.mark.skipif(shutil.which("xschem") is None, reason="xschem is not on PATH")
@pytest.mark.parametrize("icon", ICONS)
def test_the_icon_hierarchy_netlists_byte_for_byte_like_the_plain_one(tmp_path, icon):
    """Gate 1, per icon, on a two-level hierarchy, through the netlister that actually matters.

    Both sheets are written with the same cell names to the same layout, netlisted by xschem itself
    (which descends into each child ``.sch``), and compared as text: same ``.subckt`` headers, same
    port order, same instance calls, same devices. Every registered icon is exercised — including
    the ones whose default scale is not 1.0 (``ldo``, ``chopper``), where the pin COORDINATES do
    move and only their names, order and directions are held fixed. A functional icon is a drawing
    change and may not be anything else."""
    plain_dir, icon_dir = tmp_path / "plain", tmp_path / "icons"
    plain_dir.mkdir()
    icon_dir.mkdir()
    write_hierarchy(_hierarchy(auto_icons=False), plain_dir, parent_name="topcell")
    write_hierarchy(
        _hierarchy(icons={"cmp_stage": icon, "pass_pair": icon}, auto_icons=False),
        icon_dir,
        parent_name="topcell",
    )
    plain_net = _xschem_netlist(plain_dir, "topcell")
    icon_net = _xschem_netlist(icon_dir, "topcell")
    assert ".subckt" in icon_net, "xschem did not descend into the children"
    assert icon_net == plain_net


@pytest.mark.skipif(shutil.which("xschem") is None, reason="xschem is not on PATH")
def test_a_shared_icon_file_cannot_be_placed_which_is_why_the_symbol_is_per_cell(tmp_path):
    """The behaviour that decides the whole shape of this feature, reproduced here (#264).

    Place ONE shared icon ``.sym`` for a cell and take the master from the instance
    (``format="@name @pinlist @value"`` + ``value=<cell>``), the way a shared icon library would
    have to work. xschem binds a ``type=subcircuit`` symbol's child schematic to the symbol FILE's
    basename, so it emits an **empty** ``.subckt icon`` — the real cell is never descended into —
    and puts a spurious ``value`` PORT on its header, so the call has N nets while the cell
    declares N+1. That is why the glyph is shared and the ``.sym`` is written per cell."""
    work = tmp_path / "shared"
    work.mkdir()
    write_hierarchy(_hierarchy(), work, parent_name="topcell")
    blocks = work / "blocks"
    (blocks / "icon.sym").write_text(
        (blocks / "cmp_stage.sym")
        .read_text()
        .replace('format="@name @pinlist @symname @params"', 'format="@name @pinlist @value"')
    )
    (work / "shared.sch").write_text(
        (work / "topcell.sch")
        .read_text()
        .replace("C {blocks/cmp_stage.sym} ", "C {blocks/icon.sym} ")
        .replace("{name=xcmp_stage}", "{name=xcmp_stage value=cmp_stage}")
    )
    net = _xschem_netlist(work, "shared")
    empty = [ln for ln in net.splitlines() if ln.startswith(".subckt icon ")]
    assert empty, "the shared-symbol failure did not reproduce; revisit the per-cell rule"
    assert empty[0].split()[-1] == "value", "no spurious port — the @-derived port is gone"
    # …and the cell it was supposed to draw is never expanded: the icon block holds no devices.
    body = net.splitlines()[net.splitlines().index(empty[0]) + 1]
    assert body.startswith(".ends"), f"expected an empty .subckt icon, got {body!r}"
    assert "xcmp_stage" in net and " cmp_stage" in net  # the CALL is right; the definition is not


# ------------------------------------------------------------------------------- the CLI ---------


def _cli_inputs(tmp_path: Path) -> tuple[Path, Path]:
    """The netlist + annotations JSON a ``--hierarchical --icon`` run needs."""
    netlist = tmp_path / "stage.spice"
    netlist.write_text(NETLIST)
    blocks = tmp_path / "stage.blocks.json"
    BlockAnnotationSet(
        (
            BlockAnnotation("cmp_stage", ("XM1", "XM2", "XM3"), family="comparator"),
            BlockAnnotation("pass_pair", ("XM4", "XM5"), family="transmission_gate"),
        )
    ).save(blocks)
    return netlist, blocks


def test_cli_rejects_an_unknown_icon_by_name(tmp_path, capsys):
    from spicexplorer_netlist2xschem.cli import main

    netlist, blocks = _cli_inputs(tmp_path)
    rc = main(
        [
            str(netlist),
            "--hierarchical",
            "--annotations",
            str(blocks),
            "--icon",
            "cmp_stage=squiggle",
        ]
    )
    assert rc == 2
    assert "comparator" in capsys.readouterr().err  # it names the icons that do exist


def test_cli_rejects_an_icon_request_outside_the_hierarchy_lane(tmp_path, capsys):
    """The flat lane draws devices, not block symbols — an --icon there would silently do nothing."""
    from spicexplorer_netlist2xschem.cli import main

    netlist, _blocks = _cli_inputs(tmp_path)
    rc = main([str(netlist), "--icon", "cmp_stage=comparator"])
    assert rc == 2
    assert "generate_icon_symbol" in capsys.readouterr().err  # it says what to do instead


def test_cli_draws_the_requested_icon_and_reports_what_it_drew(tmp_path, capsys):
    from spicexplorer_netlist2xschem.cli import main

    netlist, blocks = _cli_inputs(tmp_path)
    rc = main(
        [
            str(netlist),
            "--pdk",
            "generic",
            "--hierarchical",
            "--annotations",
            str(blocks),
            "-o",
            str(tmp_path / "top.sch"),
            "--icon",
            "cmp_stage=opamp@1.4",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "icons: cmp_stage=opamp, pass_pair=switch" in out
    sym = (tmp_path / "blocks" / "cmp_stage.sym").read_text()
    plain_pins = {p.name for p in parse_symbol(sym).pins}
    assert plain_pins == {"clk", "vin", "vip", "vob", "vout", "vss"}
