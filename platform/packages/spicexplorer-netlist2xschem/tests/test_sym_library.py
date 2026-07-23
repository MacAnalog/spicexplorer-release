"""Symbol parsing — pin names, pin centre coordinates, and the K-block template.

Verified against the checked-in vendored ``.sym`` copies. Pin coordinate = box centre
``((x1+x2)/2, (y1+y2)/2)``.
"""


def test_nmos_pins_and_template(sym_lib):
    sym = sym_lib.load("sg13g2_pr/sg13_lv_nmos.sym")
    assert sym is not None
    assert sym.type == "nmos"
    coords = {p.name: (p.x, p.y) for p in sym.pins}
    assert coords == {"D": (20.0, -30.0), "G": (-20.0, 0.0), "S": (20.0, 30.0), "B": (20.0, 0.0)}
    # template carries the netlist defaults + the spiceprefix that drives instance naming
    assert sym.template["spiceprefix"].upper() == "X"
    assert sym.template["model"] == "sg13_lv_nmos"
    for key in ("w", "l", "ng", "m"):
        assert key in sym.template


def test_pmos_pins_swapped_but_named_dgsb(sym_lib):
    sym = sym_lib.load("sg13g2_pr/sg13_lv_pmos.sym")
    assert sym is not None and sym.type == "pmos"
    coords = {p.name: (p.x, p.y) for p in sym.pins}
    # same pin *names* as nmos; D/S are geometrically swapped (D at +y) — alignment is by name.
    assert coords == {"D": (20.0, 30.0), "G": (-20.0, 0.0), "S": (20.0, -30.0), "B": (20.0, 0.0)}


def test_resistor_pins_P_M(sym_lib):
    sym = sym_lib.load("devices/res.sym")
    assert sym is not None and sym.type == "resistor"
    assert {p.name: (p.x, p.y) for p in sym.pins} == {"P": (0.0, -30.0), "M": (0.0, 30.0)}


def test_two_terminal_lowercase_pins(sym_lib):
    for ref in (
        "devices/capa.sym",
        "devices/ind.sym",
        "devices/vsource.sym",
        "devices/isource.sym",
    ):
        sym = sym_lib.load(ref)
        assert sym is not None, ref
        names = sorted(p.name for p in sym.pins)
        assert names == ["m", "p"], f"{ref} pins {names}"


def test_lab_wire_single_pin_at_origin(sym_lib):
    sym = sym_lib.load("devices/lab_wire.sym")
    assert sym is not None and sym.type == "label"
    assert len(sym.pins) == 1
    assert (sym.pins[0].x, sym.pins[0].y) == (0.0, 0.0)


def test_pin_lookup_is_case_insensitive(sym_lib):
    sym = sym_lib.load("sg13g2_pr/sg13_lv_nmos.sym")
    assert sym.pin("d") is sym.pin("D")
    assert sym.pin("missing") is None


def test_unresolvable_symbol_returns_none(sym_lib):
    assert sym_lib.load("does/not/exist.sym") is None
