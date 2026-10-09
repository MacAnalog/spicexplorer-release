"""The sheet-resistance solve and the obstacle map / column allocator.

Both halves that need no EDA tool: the solver runs on synthetic masks (no klayout, no GDS) and
the router is pure geometry. Every process number comes from a tech config, and one test loads a
SYNTHETIC one to prove nothing here is keyed on a PDK name.
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import numpy as np
import pytest
from spicexplorer_core.tech import RoutingRules, Tech
from spicexplorer_layout.rail import (
    Raster,
    component_touching,
    selftest,
    solve_sheet_resistance,
)
from spicexplorer_layout.route import ObstacleMap

SYNTH_TECH = """
metals: {M1: 100, M2: 200}
vias: {V1: 150}
metal_datatype: 3
sheet_ohm_sq: {M1: 0.5, M2: 0.25}
routing:
  grid_um: 0.01
  route_layer: M2
  stub_layer: M1
  stub_width_um: 0.4
  stub_clear_x_um: 0.5
  stub_clear_y_um: 0.5
  column_pitch_um: 1.0
"""


@pytest.fixture
def synth(tmp_path: Path) -> Tech:
    p = tmp_path / "synth-process.yaml"
    p.write_text(textwrap.dedent(SYNTH_TECH))
    return Tech.from_yaml(p)


# ------------------------------------------------------------------------- tech ----


def test_a_synthetic_tech_drives_everything(synth: Tech):
    assert synth.gds_layer("M1") == (100, 3)
    assert synth.sheet_resistance("m2") == 0.25
    assert synth.routing_rules().column_pitch_um == 1.0
    with pytest.raises(KeyError, match="no sheet resistance for 'M9'"):
        synth.sheet_resistance("M9")
    with pytest.raises(KeyError, match="no `em_limits:` section"):
        synth.em_limit("M1")


def test_an_unknown_key_in_a_section_is_an_error(tmp_path: Path):
    p = tmp_path / "bad.yaml"
    p.write_text("metals: {M1: 1}\nvias: {}\nrouting: {grid_um: 0.005, typo_um: 1}\n")
    with pytest.raises(ValueError, match="unknown key"):
        Tech.from_yaml(p)


def test_resolve_takes_a_name_a_path_or_a_tech(synth: Tech, tmp_path: Path):
    assert Tech.resolve(synth) is synth
    assert Tech.resolve("ihp-sg13g2").name == "ihp-sg13g2"
    assert Tech.resolve(None, default="ihp-sg13g2").name == "ihp-sg13g2"
    assert Tech.resolve(tmp_path / "synth-process.yaml").name == "synth-process"


# ------------------------------------------------------------------------- rail ----


def test_the_analytic_bar_reproduces_to_one_percent():
    got, want = selftest()
    assert abs(got - want) / want < 0.01


def test_the_solve_is_independent_of_the_pitch():
    """One grid edge is one square whatever the step, so halving the pitch must not move R."""
    coarse, _ = selftest(pitch=0.1)
    fine, _ = selftest(pitch=0.05)
    assert abs(fine - coarse) / coarse < 0.02


def test_two_bars_in_parallel_halve_the_resistance():
    ny, nx = 4, 41
    mask = np.zeros((ny + 3, nx), bool)
    mask[0:ny, :] = True
    mask[ny + 1 : ny + 1 + 2, :] = False  # a second, disconnected bar is not in the net
    one = solve_sheet_resistance(mask, 1.0, (0, ny - 1, 0, 0), {"e": (0, ny - 1, nx - 1, nx - 1)})
    wide = np.zeros((2 * ny, nx), bool)
    wide[:, :] = True
    two = solve_sheet_resistance(
        wide, 1.0, (0, 2 * ny - 1, 0, 0), {"e": (0, 2 * ny - 1, nx - 1, nx - 1)}
    )
    assert two["e"] == pytest.approx(one["e"] / 2, rel=0.02)


def test_an_l_shape_is_longer_than_the_straight_run():
    n = 41
    bar = np.zeros((4, n), bool)
    bar[:, :] = True
    straight = solve_sheet_resistance(bar, 1.0, (0, 3, 0, 0), {"e": (0, 3, n - 1, n - 1)})["e"]
    ell = np.zeros((n, n), bool)
    ell[0:4, :] = True
    ell[:, n - 4 : n] = True
    bent = solve_sheet_resistance(ell, 1.0, (0, 3, 0, 0), {"e": (n - 4, n - 1, n - 4, n - 1)})["e"]
    assert bent > straight


def test_a_seed_off_the_metal_and_a_terminal_off_the_net_both_raise():
    mask = np.zeros((5, 5), bool)
    mask[0:2, 0:2] = True
    with pytest.raises(ValueError, match="not on the drawn layer"):
        component_touching(mask, (4, 4))
    with pytest.raises(ValueError, match="covers no cell"):
        solve_sheet_resistance(mask, 1.0, (0, 0, 0, 0), {"far": (4, 4, 4, 4)})


def test_the_component_drops_metal_the_pin_cannot_reach():
    mask = np.zeros((5, 9), bool)
    mask[0:2, 0:3] = True
    mask[0:2, 6:9] = True  # a second island, no path between them
    keep = component_touching(mask, (0, 0))
    assert keep.sum() == 6 and not keep[0, 7]


def test_a_raster_maps_um_to_grid_indices():
    r = Raster(np.ones((10, 10), bool), x0=-1.0, y0=-2.0, pitch=0.5)
    assert r.box((-1.0, -2.0)) == (0, 0, 0, 0)
    assert r.box((-1.0, -2.0, 0.0, -1.0)) == (0, 2, 0, 2)
    with pytest.raises(ValueError, match="is \\(x, y\\)"):
        r.box((1.0, 2.0, 3.0))


# ------------------------------------------------------------------------ route ----


def rules(**kw) -> RoutingRules:
    d = dict(
        grid_um=0.005,
        route_layer="Metal2",
        stub_layer="Metal1",
        stub_width_um=0.2,
        stub_clear_x_um=0.28,
        stub_clear_y_um=0.22,
        column_pitch_um=0.6,
    )
    d.update(kw)
    return RoutingRules(**d)


def test_a_stub_through_a_foreign_bar_is_refused():
    """The collision DRC cannot see: two overlapping same-layer shapes are one legal polygon."""
    m = ObstacleMap(rules())
    m.claim_stub_row("gate", y=0.0, x0=0.0, x1=5.0)
    assert not m.stub_clear("vout", y=0.0, xa=1.0, xb=3.0)
    assert m.stub_clear("gate", y=0.0, xa=1.0, xb=3.0)  # its own metal is not an obstacle
    assert m.stub_clear("vout", y=4.0, xa=1.0, xb=3.0)  # far enough away in y


def test_a_column_is_refused_by_a_drawn_rectangle_on_its_own_layer_only():
    """The layer-aware half: a comb drawn as plain rectangles by the power path must block a
    column on ITS layer, and must not force a hop on any other."""
    m = ObstacleMap(rules())
    m.claim_box("Metal2", "vout", 0.0, 0.0, 1.0, 10.0)
    assert not m.column_free("gate", 0.5, 1.0, 5.0, "Metal2")
    assert m.column_free("gate", 0.5, 1.0, 5.0, "Metal3")
    assert m.column_free("vout", 0.5, 1.0, 5.0, "Metal2")  # the box's own net


def test_a_foreign_column_within_the_pad_pitch_is_refused():
    m = ObstacleMap(rules())
    m.claim_vertical("vout", x=1.0, y0=0.0, y1=10.0)
    assert not m.column_free("gate", 1.3, 1.0, 5.0)
    assert m.column_free("gate", 1.7, 1.0, 5.0)


def test_the_nets_own_column_is_a_merge_on_the_same_x_and_a_neighbour_beside_it():
    m = ObstacleMap(rules())
    m.claim_vertical("vout", x=1.0, y0=0.0, y1=10.0)
    assert m.column_free("vout", 1.0, 1.0, 5.0)  # exactly on it: one column, not two
    assert not m.column_free("vout", 1.3, 1.0, 5.0)  # beside it: the pads still abut


def test_alloc_turns_round_when_the_preferred_direction_is_blocked():
    m = ObstacleMap(rules())
    for x in (1.6, 2.2, 2.8):
        m.claim_vertical("vout", x=x, y0=0.0, y1=10.0)
    x = m.alloc("gate", 1.0, 1.0, 5.0)
    assert x == pytest.approx(1.0)  # the start is already free
    m.claim_vertical("gate", x=1.0, y0=1.0, y1=5.0)
    # From 1.6 the walk tries +0.6 (2.2, taken), -0.6 (1.0, taken), +1.2 (2.8, taken) and only
    # then -1.2. Without the turn-round it would have marched on past 2.8 into 3.4.
    assert m.alloc("bias", 1.6, 1.0, 5.0) == pytest.approx(0.4)


def test_alloc_raises_rather_than_drawing_a_short():
    m = ObstacleMap(rules())
    m.claim_box("Metal2", "vout", -100.0, -100.0, 100.0, 100.0)
    with pytest.raises(AssertionError, match="no free Metal2 column"):
        m.alloc("gate", 0.0, 1.0, 5.0, tries=5)


def test_retag_renames_a_net_in_all_three_claim_kinds():
    m = ObstacleMap(rules())
    m.claim_stub_row("old", 0.0, 0.0, 1.0)
    m.claim_box("Metal2", "old", 0.0, 0.0, 1.0, 1.0)
    m.claim_vertical("old", 0.0, 0.0, 1.0)
    m.retag("old", "new")
    assert m.stub_rows[0][0] == "new"
    assert m.boxes[0][1] == "new"
    assert m.verticals[0][0] == "new"


def test_the_router_reads_its_rules_from_a_synthetic_tech(synth: Tech):
    m = ObstacleMap(synth.routing_rules())
    assert m.rules.column_pitch_um == 1.0
    m.claim_vertical("vout", x=0.0, y0=0.0, y1=10.0)  # defaults to the tech's route layer
    assert m.verticals[0][4] == "M2"
    assert not m.column_free("gate", 0.5, 1.0, 5.0)  # 0.5 < the synthetic 1.0 um pitch
    assert m.column_free("gate", 1.5, 1.0, 5.0)


def test_a_refusal_can_name_the_generators_own_knobs():
    """Which parameter widens the gap is a property of the generator, not of the map — a
    refusal that names the platform's words sends the reader looking for knobs that do not
    exist in their repo."""
    m = ObstacleMap(rules())
    m.claim_stub_row("fb", 4.0, -100.0, 100.0, 0.5)
    with pytest.raises(AssertionError, match="widen the device or group gap"):
        m.alloc("vref", 0.0, 4.0, 10.0)
    with pytest.raises(AssertionError, match=r"widen dev_gap/grp_gap"):
        m.alloc("vref", 0.0, 4.0, 10.0, hint="widen dev_gap/grp_gap")


# ------------------------------------------- the rule these modules were rewritten for ----

SRC = Path(__file__).resolve().parents[1] / "src" / "spicexplorer_layout"

#: What a process states and these packages therefore may not: sheet resistances and the
#: routing clearances. Read straight off the packaged tech config -- not retyped as string
#: literals here -- so the needle can never drift from the number it is guarding (reuse review
#: F10: the guard is numeric, not a spelling of one).
_IHP = Tech.builtin("ihp-sg13g2")
_IHP_ROUTING = _IHP.routing_rules()
FORBIDDEN_VALUES: dict[float, str] = {
    _IHP.sheet_resistance(layer): f"{layer} sheet resistance"
    for layer in sorted(_IHP.sheet_ohm_sq or {})
}
FORBIDDEN_VALUES[_IHP_ROUTING.stub_clear_x_um] = "stub clearance in x"
FORBIDDEN_VALUES[_IHP_ROUTING.stub_clear_y_um] = "stub clearance in y"

#: Every leaf package this platform-reuse sweep moved a process number OUT of. Extending this
#: set is how a future sweep (e.g. `signoff/pex.py`'s GDS layer numbers, F11) gets the guard for
#: free -- add the package's `src/` dir here.
PACKAGES = Path(__file__).resolve().parents[2]
FORBIDDEN_LITERAL_SRC_DIRS: dict[str, Path] = {
    "spicexplorer_layout": SRC,
    "spicexplorer_signoff": PACKAGES / "spicexplorer-signoff" / "src" / "spicexplorer_signoff",
    "spicexplorer_harness": PACKAGES / "spicexplorer-harness" / "src" / "spicexplorer_harness",
}

#: Legitimate numeric constants that happen to equal a value in FORBIDDEN_VALUES -- a designer
#: writing a genuinely process-unrelated number that coincides with one of the process's own
#: (e.g. an analytic self-test's arbitrary resistance). Every entry MUST carry a reason; nothing
#: is allowlisted by pattern, only by exact (package, relative file path, enclosing function,
#: value). Keyed on the enclosing function's name, not the line number: an edit ABOVE the
#: allowlisted literal (anywhere in the file) shifts every line number below it, which would
#: silently fail the guard on an unrelated, unedited line with a misleading "hard-coded literal"
#: message -- the function containing the literal moves with it.
ALLOWLIST_PATH = Path(__file__).with_name("forbidden_literal_allowlist.yaml")


def _load_allowlist() -> set[tuple[str, str, str | None, float]]:
    import yaml

    if not ALLOWLIST_PATH.is_file():
        return set()
    rows = yaml.safe_load(ALLOWLIST_PATH.read_text()) or []
    out = set()
    for row in rows:
        assert row.get("reason"), f"allowlist entry with no reason: {row}"
        out.add((row["package"], row["file"], row.get("function"), float(row["value"])))
    return out


def _float_literals(text: str, path: Path) -> list[tuple[float, int, str | None]]:
    """``(value, lineno, enclosing_function)`` for every numeric literal AST parses out of a
    Python source file -- catches ``0.11``, ``.11`` and ``110e-3`` alike, unlike a spelling-exact
    regex, and never matches a number that only appears in a comment or a docstring.
    ``enclosing_function`` is the nearest ``def``/``async def`` the literal sits inside, or
    ``None`` for one at module scope -- the allowlist key, because it survives the file being
    edited above the literal (a line number does not)."""
    tree = ast.parse(text, filename=str(path))
    out: list[tuple[float, int, str | None]] = []

    class _Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def _visit_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_FunctionDef = _visit_def
        visit_AsyncFunctionDef = _visit_def

        def visit_Constant(self, node: ast.Constant) -> None:
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                out.append((float(node.value), node.lineno, self.stack[-1] if self.stack else None))

    _Visitor().visit(tree)
    return out


def _matches_forbidden(value: float) -> str | None:
    for needle, why in FORBIDDEN_VALUES.items():
        if abs(value - needle) <= 1e-9:
            return why
    return None


def find_forbidden_literals() -> dict[str, list[str]]:
    """Every ``(package, file)`` that restates one of ``FORBIDDEN_VALUES`` as a Python numeric
    literal, minus anything on the allowlist. Numeric, not textual: a needle spelled ``0.110``,
    ``0.11``, ``.11`` or ``110e-3`` is caught the same way, within 1e-9."""
    allow = _load_allowlist()
    offenders: dict[str, list[str]] = {}
    for pkg, src in FORBIDDEN_LITERAL_SRC_DIRS.items():
        if not src.is_dir():
            continue
        for p in src.rglob("*.py"):
            rel = p.relative_to(src).as_posix()
            hits = []
            for value, lineno, func in _float_literals(p.read_text(), p):
                why = _matches_forbidden(value)
                if why is None:
                    continue
                if (pkg, rel, func, value) in allow:
                    continue
                hits.append(f"{value!r} ({why}) at line {lineno} (in {func or '<module>'}())")
            if hits:
                offenders[f"{pkg}/{rel}"] = hits
    return offenders


def test_no_module_of_these_packages_restates_a_process_number():
    offenders = find_forbidden_literals()
    assert not offenders, (
        f"process numbers hard-coded in source: {offenders} -- add a tech config entry, or if "
        f"the value is genuinely unrelated, an allowlist row at {ALLOWLIST_PATH} with a reason"
    )


def test_the_numeric_guard_catches_every_spelling_a_regex_missed():
    """F10's catch matrix: `0.110` was caught by the old exact-spelling regex, but `0.11`,
    `.11` and `110e-3` -- all the SAME float -- were not."""
    src = textwrap.dedent(
        """
        A = 0.110
        B = 0.11
        C = .11
        D = 110e-3
        """
    )
    vals = [v for v, _, _ in _float_literals(src, Path("<probe>"))]
    assert all(_matches_forbidden(v) == "Metal1 sheet resistance" for v in vals)
    assert len(vals) == 4


def test_forbidden_literal_scan_covers_signoff_and_harness_too():
    """F10: the guard used to scan only spicexplorer_layout/src -- extend it to the two other
    packages a process number can leak into."""
    assert "spicexplorer_signoff" in FORBIDDEN_LITERAL_SRC_DIRS
    assert "spicexplorer_harness" in FORBIDDEN_LITERAL_SRC_DIRS
    for pkg, src in FORBIDDEN_LITERAL_SRC_DIRS.items():
        if pkg == "spicexplorer_harness" and not src.parent.parent.is_dir():
            continue  # the public tree does not ship the harness package
        assert src.is_dir(), f"{pkg}: {src} does not exist"


def test_allowlist_entries_all_carry_a_reason(tmp_path):
    bad = tmp_path / "allow.yaml"
    bad.write_text(
        "- {package: spicexplorer_layout, file: rail.py, function: selftest, value: 0.11}\n"
    )
    import yaml

    rows = yaml.safe_load(bad.read_text())
    with pytest.raises(AssertionError, match="no reason"):
        for row in rows:
            assert row.get("reason"), f"allowlist entry with no reason: {row}"


def test_a_missing_tech_is_an_error_not_another_processs_numbers():
    """`Tech.resolve(None)` used to fall back to a name written into core. A silent fallback is
    exactly how one process's numbers answer another process's question."""
    import os

    old = os.environ.pop("PDK", None)
    try:
        with pytest.raises(ValueError, match=r"\$PDK is unset"):
            Tech.resolve(None)
        os.environ["PDK"] = "ihp-sg13g2"
        assert Tech.resolve(None).name == "ihp-sg13g2"
    finally:
        os.environ.pop("PDK", None)
        if old is not None:
            os.environ["PDK"] = old


def test_a_probe_on_a_disconnected_island_raises_instead_of_a_bogus_resistance():
    """reuse review F5: a probe reachable only through metal this net does not draw makes the
    conductance matrix singular between the islands. Before the fix, `spsolve` returned a huge,
    finite, meaningless number (a measured repro: -8e13 ohms) instead of raising."""
    mask = np.zeros((5, 9), bool)
    mask[0:2, 0:3] = True  # island containing the pin -- real drawn metal
    mask[0:2, 6:9] = True  # a second island, no path between them -- also real drawn metal
    with pytest.raises(ValueError, match="disconnected island"):
        solve_sheet_resistance(mask, 1.0, (0, 1, 0, 0), {"e": (0, 1, 8, 8)})
