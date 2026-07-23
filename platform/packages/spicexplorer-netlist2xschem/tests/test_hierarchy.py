"""Strategy 1 — render a netlist as a true xschem hierarchy of block subcircuit symbols.

The correctness that makes the hierarchy re-netlist to the original is a *join invariant*: each
generated block symbol's pins must be exactly its child ``.sch``'s subckt ports (the boundary nets),
and the parent must drop a net label on every one of those pins. The host-runnable tests assert that
invariant without xschem; a ``slow`` test does the real Docker round-trip (``xschem -n`` the parent,
flatten, compare connectivity) when xschem + circuitgraph are present.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from spicexplorer_netlist2xschem import (
    build_hierarchical_sch,
    from_file,
    parse_sch,
    write_hierarchy,
)
from spicexplorer_netlist2xschem.render import write_xschemrc
from spicexplorer_netlist2xschem.sym_library import (
    SymLibrary,
    default_search_paths,
    parse_symbol,
)

cg = pytest.importorskip("spicexplorer_circuitgraph")

from spicexplorer_core import project_root  # noqa: E402
from spicexplorer_core.spice_engine import NetlistView  # noqa: E402
from spicexplorer_netlist2xschem import BlockAnnotationSet  # noqa: E402

EXAMPLE = "examples/analog-db/circuits/amp_001_5t/abstract/netlist.spice"


def _ota5t():
    p = project_root() / EXAMPLE
    if not p.exists():
        return None, None
    from spicexplorer_circuitgraph import (
        CircuitGraph,
        find_subcircuits,
        group_matches,
    )
    from spicexplorer_circuitgraph.annotations import export_subcircuit_annotations

    g = CircuitGraph.from_netlist(NetlistView.from_file(p), name="ota5t")
    aset = BlockAnnotationSet.from_dict(
        export_subcircuit_annotations(group_matches(find_subcircuits(g)))
    )
    return from_file(p), aset


def test_hierarchy_blocks_become_symbols_and_children():
    circuit, aset = _ota5t()
    if circuit is None:
        pytest.skip("analog-db amp_001_5t example not checked out")
    res = build_hierarchical_sch(circuit, aset, title="ota5t")
    assert res.block_count == 3
    assert len(res.children) == 3 and len(res.symbols) == 3
    assert not res.warnings
    # The parent instantiates each generated block symbol exactly once.
    parent = parse_sch(res.parent_text)
    insts = [c for c in parent.components if c.symref.startswith("blocks/")]
    assert len(insts) == 3
    assert {c.symref for c in insts} == {f"blocks/{n}" for n in res.symbols}


def test_symbol_pins_are_the_boundary_nets_present_in_the_child():
    """The join invariant: a block symbol's pins are exactly the block's boundary nets, and every one
    of those nets actually appears inside the child schematic.

    xschem uses the *symbol's* pins as the subcircuit's port list (matching child nets by name), so the
    authoritative interface is the symbol — not whatever extra ipins ``build_sch`` happens to draw in
    the child. This asserts that interface is the computed boundary and that each pin connects to a real
    child net; the Docker round-trip is the end-to-end proof it re-netlists correctly."""
    circuit, aset = _ota5t()
    if circuit is None:
        pytest.skip("analog-db amp_001_5t example not checked out")
    res = build_hierarchical_sch(circuit, aset)
    for sym_file, sym_text in res.symbols.items():
        name = sym_file[:-4]  # strip .sym
        sym_pins = {p.name for p in parse_symbol(sym_text).pins}
        assert sym_pins == set(res.block_pins[name]), f"{name}: symbol pins != boundary nets"
        assert sym_pins, "a block exposes at least one boundary pin"
        # Every symbol pin's net must exist somewhere in the child (on a device or a label).
        child = parse_sch(res.children[f"{name}.sch"])
        child_nets = {c.lab for c in child.components if c.lab} | {
            w.lab for w in child.wires if w.lab
        }
        assert sym_pins <= child_nets, f"{name}: pins {sym_pins - child_nets} absent from child"


def test_parent_names_every_block_pin():
    """The parent shows connections by net colouring: every pin grows a short stub + a net-name label.
    So for the hierarchy to re-netlist, each boundary-net pin's net must appear as a parent label. The
    Docker round-trip is the end-to-end proof."""
    circuit, aset = _ota5t()
    if circuit is None:
        pytest.skip("analog-db amp_001_5t example not checked out")
    res = build_hierarchical_sch(circuit, aset)
    parent = parse_sch(res.parent_text)
    named = {c.lab for c in parent.components if c.lab}
    for sym_file, sym_text in res.symbols.items():
        for p in parse_symbol(sym_text).pins:
            assert p.name in named, f"block pin net {p.name!r} of {sym_file} is unnamed on the parent"


def test_block_symbol_pins_display_template_role_but_connect_by_net():
    """A block symbol's pins are *drawn* with their template functional name (``out`` / ``ref_in`` /
    ``supply`` / …) for readability, but each pin's connection ``name`` stays the host net — so xschem
    still matches it to the child subckt port and the hierarchy re-netlists unchanged."""
    circuit, aset = _ota5t()
    if circuit is None:
        pytest.skip("analog-db amp_001_5t example not checked out")
    res = build_hierarchical_sch(circuit, aset)
    pmos = next(t for f, t in res.symbols.items() if "cm_pmos" in f)
    sym = parse_symbol(pmos)
    # connection names are the host nets (the join key), NOT the functional role names
    pin_nets = {p.name for p in sym.pins}
    assert {"vdd", "vout", "outm"} <= pin_nets
    assert not ({"supply", "out", "ref_in"} & pin_nets)
    # the functional role names are drawn as pin-label text instead
    assert "T {supply}" in pmos
    assert "T {out}" in pmos and "T {ref_in}" in pmos


def test_diff_pair_block_exposes_its_input_pins():
    """A differential pair's gate inputs touch *only* the pair, yet they are external circuit inputs —
    the block symbol must still expose them as pins (regression: a boundary computed only from
    device-shared nets dropped them, so the dp box showed no inputs)."""
    circuit, aset = _ota5t()
    if circuit is None:
        pytest.skip("analog-db amp_001_5t example not checked out")
    res = build_hierarchical_sch(circuit, aset)
    dp = next(t for f, t in res.symbols.items() if f.startswith("dp_"))
    pin_nets = {p.name for p in parse_symbol(dp).pins}
    assert {"vinp", "vinn"} <= pin_nets, f"diff-pair inputs missing from its symbol pins: {pin_nets}"
    assert "T {in_p}" in dp and "T {in_n}" in dp  # drawn with their functional role names


def test_generate_block_symbol_label_is_display_only():
    """``BlockPin.label`` sets the drawn text; ``net`` stays the connection name — incl. an incremented
    ``out_2`` for a fanned-out mirror output."""
    from spicexplorer_netlist2xschem.symbol_gen import BlockPin, generate_block_symbol

    sym = generate_block_symbol(
        "blk",
        [
            BlockPin("vss", "bottom", "inout", label="supply"),
            BlockPin("oa", "right", "out", label="out"),
            BlockPin("ob", "right", "out", label="out_2"),
        ],
    )
    assert {p.name for p in parse_symbol(sym.text).pins} == {"vss", "oa", "ob"}
    assert "T {supply}" in sym.text and "T {out_2}" in sym.text
    assert "{name=ob dir=out}" in sym.text  # connection name = net, even when the label is "out_2"


def test_write_hierarchy_materialises_blocks_dir(tmp_path):
    circuit, aset = _ota5t()
    if circuit is None:
        pytest.skip("analog-db amp_001_5t example not checked out")
    res = build_hierarchical_sch(circuit, aset)
    parent = write_hierarchy(res, tmp_path, parent_name="ota5t")
    assert parent.is_file() and parent.name == "ota5t.sch"
    blocks = tmp_path / "blocks"
    assert len(list(blocks.glob("*.sym"))) == 3
    assert len(list(blocks.glob("*.sch"))) == 3


# --- the real round-trip, in the EDA container (xschem present) -------------------------------
def _flatten(text: str) -> str:
    """Inline one-level flattener for the generated block subckts (test harness only)."""
    subs: dict[str, tuple[list[str], list[str]]] = {}
    top: list[str] = []
    cur = None
    for raw in text.splitlines():
        ln = raw.strip()
        low = ln.lower()
        if low.startswith(".subckt "):
            t = ln.split()
            cur = t[1]
            subs[cur] = (t[2:], [])
        elif low.startswith(".ends"):
            cur = None
        elif not ln or ln.startswith("*") or low.startswith(".end"):
            continue
        elif cur is None:
            top.append(ln)
        else:
            subs[cur][1].append(ln)
    out: list[str] = []
    inst = 0
    for ln in top:
        t = ln.split()
        if t[0][:1] in "xX" and t[-1] in subs:
            ports, devs = subs[t[-1]]
            actual = t[1:-1]
            if len(actual) != len(ports):
                out.append(ln)
                continue
            inst += 1
            nm = dict(zip(ports, actual))
            for dl in devs:
                dt = dl.split()
                new = [f"{dt[0]}__{inst}"]
                for tok in dt[1:]:
                    if "=" in tok or tok.lower().startswith(("sg13", "nmos", "pmos", "nfet", "pfet")):
                        new.append(tok)
                    else:
                        new.append(nm.get(tok, f"{t[-1]}_{inst}_{tok}"))
                out.append(" ".join(new))
        else:
            out.append(ln)
    return "* flat\n" + "\n".join(out) + "\n.end\n"


@pytest.mark.slow
def test_hierarchy_round_trips_via_xschem(tmp_path):
    """Real gate: xschem netlists the parent (descending into children); flattened == original."""
    if shutil.which("xschem") is None:
        pytest.skip("xschem not on PATH (run in the EDA container)")
    circuit, aset = _ota5t()
    if circuit is None:
        pytest.skip("analog-db amp_001_5t example not checked out")
    # Build (and resolve) against the fixture lib too, so the default clean ``*_np`` symbols are found
    # even against a stale EDA image whose baked symbol dirs predate them.
    fixtures_sym = Path(__file__).parent / "fixtures" / "sym"
    lib = SymLibrary([*default_search_paths(), fixtures_sym])
    res = build_hierarchical_sch(circuit, aset, lib=lib)
    write_hierarchy(res, tmp_path, parent_name="ota5t")

    # Seed the symbol search path (generic + PDK symbols), the checked-in fixture lib (which carries
    # the clean ``*_np`` symbol twins) AND the parent dir, so the generated blocks/*.sym resolve.
    lib_path = os.pathsep.join(
        [*(str(p) for p in default_search_paths()), str(fixtures_sym), str(tmp_path)]
    )
    rc = write_xschemrc(tmp_path, lib_path)
    env = os.environ.copy()
    env["XSCHEM_LIBRARY_PATH"] = lib_path
    subprocess.run(
        ["xschem", "--rcfile", str(rc), "-x", "-q", "-n", "-s", "-o", str(tmp_path),
         str(tmp_path / "ota5t.sch")],
        env=env, capture_output=True, text=True, timeout=120, cwd=str(tmp_path),
    )
    netlist = tmp_path / "ota5t.spice"
    assert netlist.is_file(), "xschem produced no netlist for the hierarchy"
    flat = _flatten(netlist.read_text())
    original = (project_root() / EXAMPLE).read_text()
    assert cg.netlists_equivalent(original, flat), "flattened hierarchy != original connectivity"
