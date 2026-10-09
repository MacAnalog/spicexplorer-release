"""``--collapse``: repeated cells moved one drawing level down, the result proven by flattening (#264).

Two synthetic top levels, no design and no kit:

* ``fixtures/blockdiag/blockdiag_top.spice`` (the #243 fixture): 40 instances of nine generic
  cells ``blk_a`` … ``blk_i``, each drawn with its generated block symbol;
* ``CHAIN`` below: four ``stage`` slices in series (the nets between them belong inside the
  group), each with an output ``qb`` that nothing else connects to, a ``load`` on the last one and
  a ``bgen`` driving a ``bias`` net the slices share.

Every grouping is proven by :func:`check_collapsed` (the finished sheets flattened through both
levels, terminal by terminal, against the input) and, where xschem is installed, by xschem's own
netlist of the finished hierarchy flattened the same way.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    BlockPin,
    SymLibrary,
    build_sch,
    from_file,
    from_string,
    generate_block_symbol,
    parse_symbol,
    write_hierarchy,
)
from spicexplorer_netlist2xschem.cli import main
from spicexplorer_netlist2xschem.collapse import (
    PORT,
    CollapseCheck,
    CollapsedResult,
    CollapseGroup,
    _natural,
    build_collapsed_sch,
    check_collapsed,
    parse_collapse,
)
from spicexplorer_netlist2xschem.ingest import N2XCircuit
from spicexplorer_netlist2xschem.sym_library import default_search_paths

FIXTURES = Path(__file__).parent / "fixtures"
BLOCKDIAG = FIXTURES / "blockdiag"
CELLS = [f"blk_{c}" for c in "abcdefghi"]
PDK = "collapse-fixture"  # a token no symbol is registered under

CHAIN = """* four stage slices in series, a load and a bias generator (synthetic)
.subckt stage in clk bias out qb vdd vss
R1 out vss 1k
.ends stage
.subckt load in vdd vss
R1 in vss 1k
.ends load
.subckt bgen bias vdd vss
R1 bias vss 1k
.ends bgen
.subckt chain_top in clk out vdd vss
XS0 in clk bias n1 qb0 vdd vss stage
XS1 n1 clk bias n2 qb1 vdd vss stage
XS2 n2 clk bias n3 qb2 vdd vss stage
XS3 n3 clk bias out qb3 vdd vss stage
XL0 out vdd vss load
XB0 bias vdd vss bgen
.ends chain_top
xtop in clk out vdd vss chain_top
.end
"""
CHAIN_SYMBOLS = {
    "stage": [
        BlockPin("in", "left"),
        BlockPin("clk", "left"),
        BlockPin("bias", "left", "inout"),
        BlockPin("out", "right"),
        BlockPin("qb", "right"),
        BlockPin("vdd", "top"),
        BlockPin("vss", "bottom"),
    ],
    "load": [BlockPin("in", "left"), BlockPin("vdd", "top"), BlockPin("vss", "bottom")],
    "bgen": [BlockPin("bias", "right"), BlockPin("vdd", "top"), BlockPin("vss", "bottom")],
}

#: the four groupings measured on the 40-block fixture, default placement:
#: (--collapse values, top-sheet instances, {group cell: (slices on its sheet, ports)})
GROUPINGS = [
    (
        ["front=blk_a,blk_b", "mid=blk_c,blk_g,blk_d,blk_h"],
        6,
        {"front": (16, 14), "mid": (20, 18)},
    ),
    (
        ["front=blk_a,blk_b", "mid=blk_c,blk_g", "back=blk_d,blk_h,blk_e"],
        5,
        {"front": (16, 14), "mid": (12, 20), "back": (10, 15)},
    ),
    (
        ["blk_a", "blk_b", "blk_c", "blk_d", "blk_e", "blk_g", "blk_h"],
        9,
        {
            "blk_a_bank": (8, 13),
            "blk_b_bank": (8, 20),
            "blk_c_bank": (8, 23),
            "blk_d_bank": (4, 18),
            "blk_e_bank": (2, 9),
            "blk_g_bank": (4, 7),
            "blk_h_bank": (4, 8),
        },
    ),
    (["blk_a"], 33, {"blk_a_bank": (8, 13)}),
]


@pytest.fixture
def lib() -> SymLibrary:
    return SymLibrary([FIXTURES / "sym", FIXTURES])


def _top() -> N2XCircuit:
    return from_file(BLOCKDIAG / "blockdiag_top.spice", into="xtop", name="blockdiag_top")


def _chain() -> N2XCircuit:
    return from_string(CHAIN, into="xtop", name="chain_top")


def _cells() -> dict[str, str]:
    return {c: (BLOCKDIAG / f"{c}.sym").read_text() for c in CELLS}


def _chain_cells() -> dict[str, str]:
    return {c: generate_block_symbol(c, pins).text for c, pins in CHAIN_SYMBOLS.items()}


def _collapse(lib: SymLibrary, specs: list[str], circuit: N2XCircuit | None = None, **kw):
    """Collapse with every sheet routed by channels, as the measurements here were taken; pass
    ``router=None`` for the default (per-route) planner."""
    circuit = circuit or _top()
    kw.setdefault("cell_symbols", _cells() if circuit.name == "blockdiag_top" else _chain_cells())
    kw.setdefault("router", "channel")
    if kw["router"] is None:
        del kw["router"]
    groups = [parse_collapse(s) for s in specs]
    return circuit, build_collapsed_sch(circuit, groups, pdk=PDK, lib=lib, **kw)


def _instances(text: str) -> list[str]:
    """The component lines of a sheet that are cell instances (not labels, not port pins)."""
    return [ln for ln in text.splitlines() if ln.startswith("C {") and "name=x" in ln.lower()]


# ------------------------------------------------------------------------------- the spec


def test_a_cell_alone_names_its_group_after_the_cell():
    assert parse_collapse("blk_a") == CollapseGroup("blk_a_bank", ("blk_a",))
    assert parse_collapse(" front = BLK_A, blk_b ") == CollapseGroup("front", ("blk_a", "blk_b"))


@pytest.mark.parametrize(
    ("spec", "message"),
    [
        ("", "expected CELL"),
        ("front=", "expected CELL"),
        ("front=blk_a,", "expected CELL"),
        ("front=blk a", "not a cell name"),
        ("=blk_a", "not a SPICE identifier"),
        ("9front=blk_a", "not a SPICE identifier"),
        ("front=blk_a,BLK_A", "named twice"),
    ],
)
def test_a_malformed_spec_is_refused(spec, message):
    with pytest.raises(ValueError, match=message):
        parse_collapse(spec)


def test_bus_bits_sort_in_numeric_order():
    assert sorted(["d10", "d2", "clk", "D1"], key=_natural) == ["clk", "D1", "d2", "d10"]


# ------------------------------------------------------------------ the 40-block fixture


@pytest.mark.parametrize(("specs", "after", "cells"), GROUPINGS)
def test_the_top_sheet_carries_one_instance_per_group(lib, specs, after, cells):
    """40 instances on the flat top sheet; one per group plus the ungrouped ones afterwards."""
    circuit, result = _collapse(lib, specs)
    assert (result.device_count, result.parent_instances) == (40, after)
    drawn = {g: (len(refs), len(result.block_pins[g])) for g, refs in result.groups.items()}
    assert drawn == cells
    assert len(_instances(result.parent_text)) == after
    assert result.warnings == ()
    grouped = sum(len(refs) for refs in result.groups.values())
    assert after == 40 - grouped + len(result.groups)


@pytest.mark.parametrize(("specs", "after", "cells"), GROUPINGS)
def test_every_slice_is_drawn_on_its_group_sheet_and_nowhere_else(lib, specs, after, cells):
    circuit, result = _collapse(lib, specs)
    drawn = {g: len(_instances(result.children[f"{g}.sch"])) for g in result.groups}
    assert drawn == {g: len(refs) for g, refs in result.groups.items()}
    assert set(result.children) == {f"{g}.sch" for g in result.groups}  # no sheet per slice
    on_top = {ln.split("name=")[1].split()[0].rstrip("}") for ln in _instances(result.parent_text)}
    for refs in result.groups.values():
        assert on_top.isdisjoint(refs)


@pytest.mark.parametrize("router", [None, "channel"])
@pytest.mark.parametrize(("specs", "after", "cells"), GROUPINGS)
def test_the_flattened_sheets_are_the_netlist(lib, specs, after, cells, router):
    """The proof: 227 instance terminals and 6 declared ports on 46 nets, both directions, with
    either router drawing the sheets."""
    circuit, result = _collapse(lib, specs, router=router)
    check = check_collapsed(result, circuit, lib=lib)
    assert check.identical, check
    assert (check.terminals, check.nets) == (233, 46)
    assert set(result.routers.values()) == {router or "per-route"}


def test_ports_are_what_the_parent_declares_or_the_rest_of_the_level_touches(lib):
    circuit, result = _collapse(lib, ["front=blk_a,blk_b", "blk_c"])
    a_to_b = {f"a{i}" for i in range(8)}  # blk_a -> blk_b only: inside `front`
    assert set(result.block_pins["front"]) == {
        "clk",
        "en",
        "rst",
        "vin",
        "vdd",
        "vss",
        *(f"d{i}" for i in range(8)),
    }
    assert a_to_b.isdisjoint(result.block_pins["front"])
    # `vin` reaches only blk_a slices, and is a port because the parent declares it
    assert "vin" in result.block_pins["front"]
    assert set(result.block_pins["blk_c_bank"]) == {
        "rst",
        "vdd",
        "vss",
        *(f"d{i}" for i in range(8)),
        *(f"bias{i}" for i in range(4)),
        *(f"o{i}" for i in range(8)),
    }


def test_the_group_symbol_sides_its_pins_from_the_slice_symbols(lib):
    """Inputs left, outputs right, vdd on top, vss at the bottom, as the blk_a/blk_b symbols say."""
    _, result = _collapse(lib, ["front=blk_a,blk_b"])
    pins = {p.name: p for p in parse_symbol(result.symbols["front.sym"]).pins}
    assert {n for n, p in pins.items() if p.x < 0 and p.dir == "in"} == {"clk", "en", "rst", "vin"}
    assert {n for n, p in pins.items() if p.x > 0 and p.dir == "out"} == {f"d{i}" for i in range(8)}
    assert pins["vdd"].y < 0 < pins["vss"].y
    right = sorted((p for p in pins.values() if p.dir == "out"), key=lambda p: p.y)
    assert [p.name for p in right] == [f"d{i}" for i in range(8)]  # d0 at the top


def test_the_group_sheet_declares_the_symbols_ports_with_their_directions(lib):
    """xschem reports an error for a sheet port whose direction differs from the symbol pin's."""
    _, result = _collapse(lib, ["front=blk_a,blk_b"])
    sheet = result.children["front.sch"]
    ports = {
        ln.split("lab=")[1].rstrip("}"): ln.split("}")[0].split("/")[-1]
        for ln in sheet.splitlines()
        if "pin.sym}" in ln and "lab_pin" not in ln
    }
    assert ports == {
        **dict.fromkeys(["clk", "en", "rst", "vin"], "ipin.sym"),
        **dict.fromkeys([f"d{i}" for i in range(8)], "opin.sym"),
        **dict.fromkeys(["vdd", "vss"], "iopin.sym"),
    }


def test_the_group_sheet_places_its_symbols_by_file_name(lib):
    """A sheet inside blocks/ must not say blocks/ again (xschem resolves from the sheet's dir)."""
    _, result = _collapse(lib, ["front=blk_a,blk_b"])
    assert "C {blk_a.sym}" in result.children["front.sch"]
    assert "blocks/" not in result.children["front.sch"]
    assert "C {blocks/front.sym}" in result.parent_text
    assert "C {blocks/blk_e.sym}" in result.parent_text


@pytest.mark.parametrize(("specs", "after", "cells"), GROUPINGS[:1] + GROUPINGS[2:])
def test_every_sheet_is_routed_by_channels_with_nothing_joined_by_name(lib, specs, after, cells):
    """The grid pitch clears the largest symbol: at GridPlacer's 240 the group symbols overlap."""
    _, result = _collapse(lib, specs)
    assert set(result.routers.values()) == {"channel"}
    assert all(named == () for named in result.nets_by_name.values())


def test_the_three_group_split_is_measured_not_hidden(lib):
    """blk_c with blk_g on one sheet: the channel router leaves 3 nets to their names (#243 limits)."""
    _, result = _collapse(lib, GROUPINGS[1][0])
    assert set(result.routers.values()) == {"channel"}
    assert {s: n for s, n in result.nets_by_name.items() if n} == {"mid": ("o0", "o4", "rst")}


def test_two_runs_are_byte_identical(lib):
    first = _collapse(lib, GROUPINGS[0][0])[1]
    second = _collapse(lib, GROUPINGS[0][0])[1]
    assert (first.parent_text, first.children, first.symbols) == (
        second.parent_text,
        second.children,
        second.symbols,
    )


# ------------------------------------------------------------------------ the chain fixture


def test_nets_between_slices_and_unconnected_pins_stay_inside_the_group(lib):
    circuit, result = _collapse(lib, ["stage"], _chain())
    assert result.groups == {"stage_bank": ("XS0", "XS1", "XS2", "XS3")}
    assert set(result.block_pins["stage_bank"]) == {"bias", "clk", "in", "out", "vdd", "vss"}
    assert result.parent_instances == 3
    check = check_collapsed(result, circuit, lib=lib)
    assert check.identical, check
    # 4 x 7 stage pins + 3 load + 3 bgen, and 5 declared ports; n1-n3 and qb0-qb3 are 7 of the 13 nets
    assert (check.terminals, check.nets) == (39, 13)


def test_a_pin_the_slices_only_share_is_drawn_bidirectional(lib):
    """``bias`` is an inout pin on every slice: left side, dir=inout, an iopin on the sheet."""
    _, result = _collapse(lib, ["stage"], _chain())
    pins = {p.name: p for p in parse_symbol(result.symbols["stage_bank.sym"]).pins}
    assert (pins["bias"].x < 0, pins["bias"].dir) == (True, "inout")
    assert (pins["out"].x > 0, pins["out"].dir) == (True, "out")
    assert "iopin.sym} " in next(
        ln for ln in result.children["stage_bank.sch"].splitlines() if "lab=bias}" in ln
    )


def test_a_slice_net_on_node_0_becomes_a_port_named_0(lib):
    """Node 0 follows the port rule like any other net: the load and the bias generator touch it
    outside the group, so ``stage_bank`` gets a pin named ``0``, at the bottom (a GND net). The
    flattened sheets still equal the netlist."""
    text = (
        CHAIN.replace(" vdd vss stage", " vdd 0 stage")
        .replace(" vdd vss load", " vdd 0 load")
        .replace(" vdd vss bgen", " vdd 0 bgen")
        .replace(".subckt chain_top in clk out vdd vss", ".subckt chain_top in clk out vdd")
        .replace("xtop in clk out vdd vss chain_top", "xtop in clk out vdd chain_top")
    )
    circuit = from_string(text, into="xtop", name="chain_top")
    assert circuit.supply["0"] == "GND" and "0" not in circuit.ports
    _, result = _collapse(lib, ["stage"], circuit)
    assert result.block_pins["stage_bank"] == ("0", "bias", "clk", "in", "out", "vdd")
    ground = next(p for p in parse_symbol(result.symbols["stage_bank.sym"]).pins if p.name == "0")
    assert ground.y > 0  # bottom side
    check = check_collapsed(result, circuit, lib=lib)
    assert check.identical, check
    assert (check.terminals, check.nets) == (38, 13)  # 34 instance terminals + 4 declared ports


def test_a_declared_port_that_only_slices_touch_is_still_a_port(lib):
    """``in`` reaches only XS0; it is a port because chain_top declares it."""
    circuit, result = _collapse(lib, ["stage"], _chain())
    assert "in" in result.block_pins["stage_bank"]
    assert "qb0" not in result.block_pins["stage_bank"]


# ------------------------------------------------------------------ the check catches faults


def _tampered(result: CollapsedResult, **changes) -> CollapsedResult:
    from dataclasses import replace

    return replace(result, **changes)


def test_the_check_sees_a_port_pin_relabelled_on_a_group_sheet(lib):
    circuit, result = _collapse(lib, ["front=blk_a,blk_b"])
    sheet = result.children["front.sch"].replace("lab=d0}", "lab=d1}")
    check = check_collapsed(
        _tampered(result, children={**result.children, "front.sch": sheet}), circuit, lib=lib
    )
    assert not check.identical
    assert check.port_mismatch and "d0" in check.port_mismatch[0]
    assert ("d0", "d1") in check.merged


def test_the_check_sees_an_instance_missing_from_the_parent(lib):
    circuit, result = _collapse(lib, ["front=blk_a,blk_b"])
    parent = "\n".join(ln for ln in result.parent_text.splitlines() if "name=XU39" not in ln)
    check = check_collapsed(_tampered(result, parent_text=parent), circuit, lib=lib)
    assert not check.identical
    assert {k for k in check.missing if k[0] == "XU39"} == {
        ("XU39", p) for p in ("rst", "ib", "en", "vdd", "vss")
    }


def test_the_check_sees_a_group_instance_missing_from_the_parent(lib):
    """Without its instance the group's port nets no longer reach the parent: every one splits."""
    circuit, result = _collapse(lib, ["front=blk_a,blk_b"])
    parent = "\n".join(ln for ln in result.parent_text.splitlines() if "name=xfront" not in ln)
    check = check_collapsed(_tampered(result, parent_text=parent), circuit, lib=lib)
    assert set(check.split) == set(result.block_pins["front"])  # all 14, vdd/vss/vin too


def test_the_check_sees_a_declared_port_missing_from_the_parent(lib):
    circuit, result = _collapse(lib, ["stage"], _chain())
    parent = "\n".join(
        ln for ln in result.parent_text.splitlines() if not ("pin.sym}" in ln and "lab=in}" in ln)
    )
    check = check_collapsed(_tampered(result, parent_text=parent), circuit, lib=lib)
    assert check.missing == ((PORT, "in"),)


def _slice_line(result: CollapsedResult, ref: str, group: str = "front") -> str:
    """A slice's instance line from its group sheet, as the parent sheet would place it."""
    line = next(ln for ln in result.children[f"{group}.sch"].splitlines() if f"name={ref} " in ln)
    return line.replace("C {blk_a.sym}", "C {blocks/blk_a.sym}")


def test_the_check_sees_a_slice_drawn_on_the_top_sheet_as_well(lib):
    """XU00 left on the parent sheet and drawn on ``front`` too: every terminal still compares
    equal, since both copies sit on the same nets; the repeated instance is what gives it away."""
    circuit, result = _collapse(lib, ["front=blk_a,blk_b"])
    parent = result.parent_text + _slice_line(result, "XU00") + "\n"
    check = check_collapsed(_tampered(result, parent_text=parent), circuit, lib=lib)
    assert not check.identical
    assert check.duplicate == ("XU00",)
    assert (check.split, check.merged, check.missing, check.extra) == ((), (), (), ())


def test_the_check_sees_a_slice_drawn_twice_on_its_group_sheet(lib):
    circuit, result = _collapse(lib, ["front=blk_a,blk_b"])
    sheet = result.children["front.sch"]
    twice = sheet + _slice_line(result, "XU01").replace("C {blocks/", "C {") + "\n"
    check = check_collapsed(
        _tampered(result, children={**result.children, "front.sch": twice}), circuit, lib=lib
    )
    assert check.duplicate == ("XU01",) and not check.identical


def test_a_slice_with_no_symbol_is_reported_not_drawn(lib):
    """No symbol for blk_b: its 8 instances are skipped with a warning, and the check fails."""
    cells = {c: t for c, t in _cells().items() if c != "blk_b"}
    circuit, result = _collapse(lib, ["front=blk_a,blk_b"], cell_symbols=cells)
    assert sum("XU08: no symbol mapping" in w for w in result.warnings) == 1
    check = check_collapsed(result, circuit, lib=lib)
    assert not check.identical
    assert ("XU08", "din") in check.missing  # the input's own pin name: no symbol to align to
    pins = {p.name: p for p in parse_symbol(result.symbols["front.sym"]).pins}
    assert pins["d0"].dir == "in"  # the only slice pin on d0 is a blk_b output nobody could read


# ------------------------------------------------------------------------ refused, or warned


@pytest.mark.parametrize(
    ("specs", "message"),
    [
        (["front=blk_a", "back=blk_b,blk_a"], "'blk_a' is in both 'front' and 'back'"),
        (["front=blk_a", "FRONT=blk_b"], "two groups are named"),
        (["blk_a=blk_b"], "already a cell or an instance"),
        (["U00=blk_a"], "already a cell or an instance"),  # its instance would be xU00 = XU00
    ],
)
def test_a_grouping_that_cannot_be_drawn_is_refused(lib, specs, message):
    with pytest.raises(ValueError, match=message):
        _collapse(lib, specs)


def test_a_cell_with_no_instance_or_one_instance_groups_nothing(lib):
    circuit, result = _collapse(lib, ["blk_x", "blk_f", "pair=blk_i,blk_zz"])
    assert result.warnings == (
        "--collapse blk_x_bank: no instance of 'blk_x' at this level",
        "--collapse blk_x_bank: 0 instance(s), nothing grouped "
        "(a group of one adds a level and removes no instance)",
        "--collapse blk_f_bank: 1 instance(s), nothing grouped "
        "(a group of one adds a level and removes no instance)",
        "--collapse pair: no instance of 'blk_zz' at this level",
        "--collapse pair: 1 instance(s), nothing grouped "
        "(a group of one adds a level and removes no instance)",
    )
    assert (result.parent_instances, result.groups, result.children) == (40, {}, {})
    assert check_collapsed(result, circuit, lib=lib).identical


def test_a_group_no_net_leaves_is_not_formed(lib):
    circuit = from_string("* two slices on their own\nX1 a b cell\nX2 a b cell\n.end\n", name="c")
    result = build_collapsed_sch(circuit, [parse_collapse("cell")], pdk=PDK, lib=lib)
    assert result.warnings[0] == "--collapse cell_bank: no net leaves the group, nothing grouped"
    assert result.groups == {}


# ------------------------------------------------------------- the two build_sch hooks


def test_build_sch_draws_a_cell_with_the_symbol_named_for_this_call(lib):
    """``cell_symbols`` resolves blk_a here only; the other cells have no symbol under this token."""
    doc = build_sch(_top(), pdk=PDK, lib=lib, cell_symbols={"blk_a": "blockdiag/blk_a.sym"})
    assert doc.device_count == 8
    assert sum("no symbol mapping" in w for w in doc.warnings) == 32


def test_build_sch_draws_exactly_the_ports_it_is_given(lib):
    cells = {c: f"blockdiag/{c}.sym" for c in CELLS}
    inferred = build_sch(_top(), pdk=PDK, lib=lib, cell_symbols=cells)
    given = build_sch(_top(), pdk=PDK, lib=lib, cell_symbols=cells, port_roles={"dout": "out"})

    def ports(text: str) -> dict[str, str]:
        return {
            ln.split("lab=")[1].rstrip("}"): ln.split("}")[0].split("/")[-1]
            for ln in text.splitlines()
            if "pin.sym}" in ln and "lab_pin" not in ln
        }

    assert set(ports(inferred.text)) == {"clk", "rst", "vin", "dout", "vdd", "vss"}
    assert ports(given.text) == {"dout": "opin.sym"}


# ------------------------------------------------------------------ xschem's own netlist


def _xschem_netlist(result: CollapsedResult, name: str, tmp_path: Path) -> tuple[str, str]:
    from spicexplorer_netlist2xschem.render import write_xschemrc

    work = tmp_path / name
    write_hierarchy(result, work, parent_name=name)
    entries = [str(FIXTURES / "sym"), str(FIXTURES / "sym" / "devices")]
    for root in default_search_paths():
        entries.append(str(root))
        if (root / "devices").is_dir():
            entries.append(str(root / "devices"))
    library_path = os.pathsep.join(dict.fromkeys(entries))
    rc = write_xschemrc(work, library_path)
    proc = subprocess.run(
        [
            "xschem",
            "--rcfile",
            str(rc),
            "-n",
            "-q",
            "-x",
            "-o",
            str(work),
            str(work / f"{name}.sch"),
        ],
        env=dict(os.environ, XSCHEM_LIBRARY_PATH=library_path, PWD=str(work)),
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(work),
    )
    out = work / f"{name}.spice"
    assert out.is_file(), proc.stderr
    return out.read_text(), proc.stdout + proc.stderr


def _terminals(circuit: N2XCircuit) -> dict[tuple[str, str], str]:
    return {(d.ref.upper(), pin): net for d in circuit.devices for pin, net in d.nets.items()}


def _flatten_back(text: str, groups: dict[str, tuple[str, ...]]) -> dict[tuple[str, str], tuple]:
    """xschem's netlist, each group instance spliced inline: a formal port is the caller's net.

    A terminal met twice (a slice netlisted at the top level and inside its group) is an error,
    not a second write over the first.
    """
    back = from_string(text, name="back")
    out: dict[tuple[str, str], tuple] = {}

    def put(key: tuple[str, str], net: tuple) -> None:
        assert key not in out, f"{key} netlisted more than once"
        out[key] = net

    for d in back.devices:
        if (d.model or "") not in groups:
            for pin, net in d.nets.items():
                put((d.ref.upper(), pin), ("", net))
            continue
        for e in from_string(text, name="group", into=d.ref).devices:
            for pin, net in e.nets.items():
                put((e.ref.upper(), pin), ("", d.nets[net]) if net in d.nets else (d.ref, net))
    return out


def test_flattening_the_netlist_refuses_a_slice_met_twice():
    """No xschem needed: a netlist with XU00 both at the top level and inside ``front``."""
    text = """* synthetic
.subckt blk_a p q vdd vss
R1 p q 1k
.ends blk_a
.subckt front a b vdd vss
XU00 a b vdd vss blk_a
XU01 b a vdd vss blk_a
.ends front
XU00 a b vdd vss blk_a
xfront a b vdd vss front
.end
"""
    with pytest.raises(AssertionError, match=r"\('XU00', 'p'\) netlisted more than once"):
        _flatten_back(text, {"front": ("XU00", "XU01")})
    single = text.replace("XU00 a b vdd vss blk_a\nxfront", "xfront")
    assert len(_flatten_back(single, {"front": ("XU00", "XU01")})) == 8


@pytest.mark.skipif(shutil.which("xschem") is None, reason="xschem is not on PATH")
@pytest.mark.parametrize(
    ("which", "specs"), [("blockdiag_top", GROUPINGS[0][0]), ("chain_top", ["stage"])]
)
def test_xschem_netlists_the_collapsed_hierarchy_back_to_the_input(lib, tmp_path, which, specs):
    circuit, result = _collapse(lib, specs, _top() if which == "blockdiag_top" else _chain())
    text, log = _xschem_netlist(result, which, tmp_path)
    assert "IS MISSING" not in text and "Unmatched" not in log, log
    before, after = _terminals(circuit), _flatten_back(text, result.groups)
    assert set(before) == set(after)
    forward: dict[str, tuple] = {}
    backward: dict[tuple, str] = {}
    for key in sorted(before):
        assert forward.setdefault(before[key], after[key]) == after[key], f"{key}: net split"
        assert backward.setdefault(after[key], before[key]) == before[key], f"{key}: nets merged"
    assert (len(before), len(forward)) == ((227, 46) if which == "blockdiag_top" else (34, 13))


# ---------------------------------------------------------------------------------- the CLI


def _cli_args(tmp_path: Path, *extra: str) -> list[str]:
    cells = [f"--cell-symbol={c}={BLOCKDIAG / f'{c}.sym'}" for c in CELLS]
    return [
        str(BLOCKDIAG / "blockdiag_top.spice"),
        "--into",
        "xtop",
        "--name",
        "blockdiag_top",
        "--pdk",
        "generic",
        "-o",
        str(tmp_path / "top.sch"),
        *cells,
        *extra,
    ]


def test_the_cli_writes_the_collapsed_hierarchy_and_proves_it(tmp_path, capsys):
    rc = main(
        _cli_args(
            tmp_path,
            "--collapse",
            "front=blk_a,blk_b",
            "--collapse",
            "mid=blk_c,blk_g,blk_d,blk_h",
            "--router",
            "channel",
        )
    )
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "top sheet: 40 -> 6 instances; 2 group cells" in out
    assert "front: 16 instances, 14 ports, channel router, 0 nets by name" in out
    assert "233 terminals on 46 nets, identical to the netlist" in out
    blocks = tmp_path / "blocks"
    assert sorted(p.name for p in blocks.iterdir()) == sorted(
        [*(f"{c}.sym" for c in CELLS), "front.sch", "front.sym", "mid.sch", "mid.sym"]
    )


def test_the_cli_draws_every_collapsed_sheet_per_route_unless_asked(tmp_path, capsys):
    """Without ``--router channel`` each sheet is drawn by the default planner; the proof holds."""
    rc = main(_cli_args(tmp_path, "--collapse", "front=blk_a,blk_b"))
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "front: 16 instances, 14 ports, per-route router" in out
    assert "channel router" not in out
    assert "233 terminals on 46 nets, identical to the netlist" in out


def test_the_cli_takes_an_explicit_placer_for_every_sheet(tmp_path, capsys):
    rc = main(_cli_args(tmp_path, "--collapse", "blk_a", "--placer", "grid"))
    assert rc == 0
    assert "top sheet: 40 -> 33 instances" in capsys.readouterr().out


def test_the_cli_exits_1_when_the_flattened_sheets_differ(tmp_path, capsys, monkeypatch):
    from spicexplorer_netlist2xschem import cli

    bad = CollapseCheck(terminals=1, nets=1, split=("clk",), missing=(("XU00", "clk"),))
    monkeypatch.setattr(cli, "check_collapsed", lambda *a, **k: bad)
    assert main(_cli_args(tmp_path, "--collapse", "blk_a")) == 1
    captured = capsys.readouterr()
    assert "NOT identical to the netlist" in captured.out
    assert (
        "nets split: clk" in captured.err and "terminals missing: ('XU00', 'clk')" in captured.err
    )


def test_the_cli_exits_1_when_a_slice_is_drawn_twice(tmp_path, capsys, monkeypatch):
    """The real check on a hierarchy whose parent sheet also carries XU00: exit 1, and the
    report says which instance was drawn more than once."""
    from spicexplorer_netlist2xschem import cli

    real = cli.build_collapsed_sch

    def with_xu00_on_top(*a, **k):
        result = real(*a, **k)
        return _tampered(result, parent_text=result.parent_text + _slice_line(result, "XU00"))

    monkeypatch.setattr(cli, "build_collapsed_sch", with_xu00_on_top)
    report = tmp_path / "top.json"
    argv = _cli_args(tmp_path, "--collapse", "front=blk_a,blk_b", "--report", str(report))
    assert main(argv) == 1
    captured = capsys.readouterr()
    assert "NOT identical to the netlist" in captured.out
    assert "instances drawn more than once: XU00" in captured.err
    check = json.loads(report.read_text())["check"]
    assert (check["identical"], check["duplicate"]) == (False, ["XU00"])


def test_the_cli_exits_1_when_a_cell_has_no_symbol(tmp_path, capsys):
    """No --cell-symbol: every slice is skipped, and the flattened sheets show it."""
    args = [a for a in _cli_args(tmp_path, "--collapse", "blk_a") if "--cell-symbol" not in a]
    assert main(args) == 1
    captured = capsys.readouterr()
    assert "NOT identical to the netlist" in captured.out
    assert "terminals missing: ('<port>', 'dout'), ('XU00', 'clk')" in captured.err
    assert "warning: blk_a_bank: XU00: no symbol mapping" in captured.err


def test_the_cli_prints_the_warnings(tmp_path, capsys):
    assert main(_cli_args(tmp_path, "--collapse", "blk_a", "--collapse", "blk_f")) == 0
    assert "warning: --collapse blk_f_bank: 1 instance(s)" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        (["--collapse", "front="], "expected CELL"),
        (["--collapse", "blk_a", "--cell-symbol", "blk_a"], "expects CELL=PATH.sym"),
        (["--collapse", "blk_a", "--cell-symbol", "blk_a=/nonexistent/blk_a.sym"], "no such file"),
        (["--hierarchical"], "--cell-symbol needs --collapse"),
        (["--collapse", "blk_a", "--hierarchical"], "does not combine"),
        (["--collapse", "front=blk_a", "--collapse", "back=blk_a"], "is in both"),
    ],
)
def test_the_cli_refuses_what_it_cannot_draw(tmp_path, capsys, extra, message):
    assert main(_cli_args(tmp_path, *extra)) == 2
    assert message in capsys.readouterr().err
