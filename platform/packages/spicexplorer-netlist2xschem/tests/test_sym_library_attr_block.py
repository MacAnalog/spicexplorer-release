"""``parse_symbol`` reads the global-attribute block whether the file spells it ``K {}`` or ``G {}``.

The block-symbol generator writes ``G {}`` (xschem's older spelling, which xschem still honours);
before this, the reader looked only for ``K`` and every GENERATED symbol parsed with ``type=None``
and ``fmt=""`` while netlisting correctly — a test asserting on either got a silent empty value."""

from __future__ import annotations

from spicexplorer_netlist2xschem.sym_library import parse_symbol
from spicexplorer_netlist2xschem.symbol_gen import BlockPin, generate_block_symbol

_K_SYM = """v {xschem version=3.4.4 file_version=1.2}
K {type=nmos
format="@name @pinlist @model w=@w l=@l"
template="name=M1 model=nfet w=1u l=0.5u"}
B 5 -2.5 -12.5 2.5 -7.5 {name=D dir=inout}
"""


def _pins() -> list[BlockPin]:
    return [
        BlockPin("in", "left", "in"),
        BlockPin("out", "right", "out"),
        BlockPin("vdd", "top", "inout"),
        BlockPin("vss", "bottom", "inout"),
    ]


def test_a_generated_block_symbol_parses_with_its_type_and_format():
    sym = generate_block_symbol("blk", _pins())
    assert "G {" in sym.text and "K {" not in sym.text  # the generator's spelling, as today
    parsed = parse_symbol(sym.text, ref="blk.sym")
    assert parsed.type == "subcircuit"
    assert "@symname" in parsed.fmt
    assert parsed.template.get("name") == "x1"
    assert {p.name for p in parsed.pins} == {"in", "out", "vdd", "vss"}


def test_a_k_block_symbol_still_parses():
    parsed = parse_symbol(_K_SYM, ref="nmos.sym")
    assert parsed.type == "nmos"
    assert parsed.fmt == "@name @pinlist @model w=@w l=@l"
    assert parsed.template == {"name": "M1", "model": "nfet", "w": "1u", "l": "0.5u"}


def test_k_wins_when_a_file_carries_both_spellings():
    text = _K_SYM + 'G {type=other\nformat="@name"\ntemplate="name=Z"}\n'
    parsed = parse_symbol(text)
    assert parsed.type == "nmos"
    assert parsed.template["name"] == "M1"
