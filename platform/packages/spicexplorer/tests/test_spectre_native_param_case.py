"""Native-`.scs` parameter injection is CASE-CORRECT and never silently inert (O-3).

Spectre is case-sensitive. `render_native_scs` used to fold every injected key to
lowercase, so a deck declaring `parameters VDD=0.9 … ILOAD=0.5m` (the shape committed at
`analog-db/circuits/ldo_009_fer_5t_pass/spectre/28nm/ldo.scs`) kept its baked defaults and
the override was appended as an inert `vdd=…`. Two silent failures followed:

* every optimizer candidate simulated the IDENTICAL circuit — a flat score curve that
  reads as "converged" on the deck's own defaults;
* every PVT *voltage* corner ran at the baked rail, because `apply_corner` injects
  supplies keyed by `SupplyOverride.node` (typically `VDD`) through the same dict.

Injection now matches declarations case-insensitively, writes back with the deck's own
casing, and WARNS on any key the deck never declares (the ngspice lane's
`update_params` posture: warn + keep the deck's behaviour, never abort).

Follow-up 1 (audit of the O-3 fix itself): case-insensitive MATCHING must not become
case-insensitive REWRITING. The rewrite loop matched on `.lower()` and so moved EVERY
case-variant — on the committed `cmp_002_strongarm` run decks
(`parameters vdd=0.9 … VDD=0.9`) one injected key moved two distinct Spectre symbols.
Exactly one symbol moves per injected key, and the collision is named in a WARNING.

Follow-up 2 (re-verify of that fix): the resolution rule it adopted, "first declaration
wins", was itself wrong — it made an EXACT-spelling injection lose. On the same committed
decks the live rail is the UPPERCASE `VDD` (`netlist/tb/tb_cmp_offset_search.scs:4` is
`v_vdd_supply (VDD 0) vsource dc=VDD`; nothing reads the lowercase `vdd`), yet
`{'VDD': 0.81}` was redirected onto the dead lowercase symbol and the live rail kept its
baked 0.9 — a silently inert injection, i.e. O-3 itself, restored. The rule is now:

1. an **exact spelling match always wins**;
2. no exact match + exactly ONE declared case-variant → that variant (the genuine O-3 case:
   the deck declares `VDD`, `apply_corner`/the optimizer injects `vdd`);
3. no exact match + two-or-more variants → `AmbiguousParameterCaseError`. There is no
   evidence for either choice and both wrong answers are silent at run time.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pytest
from spicexplorer.backends.spectre import SpectreSimulator
from spicexplorer.backends.spectre_deck import (
    AmbiguousParameterCaseError,
    _parse_param_tokens,
    render_native_scs,
)
from spicexplorer_core.pvt import Corner, ModelInclude, SupplyOverride

# The committed ldo_009 deck's shape: an UPPERCASE parameter namespace.
UPPER_SCS = """// LDO tb
simulator lang=spectre
global 0
parameters VDD=0.9 VREF=0.55 ILOAD=0.5m
include "/pdk/models.scs" section=top_tt
v_vdd (VDDA 0) vsource dc=VDD
i_dcload (VOUT 0) isource dc=ILOAD
dcOp dc
"""

# The committed cmp_002_strongarm run decks' shape (analog-db @ed4d7c48,
# `circuits/cmp_002_strongarm/spectre/28nm/netlist/runs/pss_pnoise_plain.scs:4`): TWO
# case-variants of the same name, at DIFFERENT values, on ONE `parameters` statement.
# Spectre is case-sensitive, so `vdd` and `VDD` are two distinct symbols — the shape is
# authored (4 of the 8 committed decks carry the differing pair), not a copy-paste slip.
# The LIVE rail in that circuit is the UPPERCASE one: `netlist/tb/tb_cmp_offset_search.scs`
# drives `v_vdd_supply (VDD 0) vsource dc=VDD` and nothing in the tree reads lowercase `vdd`.
CASE_COLLIDING_SCS = """// Transient input-offset search using the plain StrongARM comparator.
simulator lang=spectre
global 0
parameters vdd=0.95 code=7 f=1G Vcm=0.475 Vid=1m VDD=0.9
include "${PDK_ROOT}/models/spectre/toplevel.scs" section=top_tt
include "dut/cmp_strongarm.scs"
"""


def _params_of(text: str) -> dict[str, str]:
    """The deck's single `parameters` statement, parsed back to {name: value}."""
    line = next(ln for ln in text.splitlines() if ln.startswith("parameters "))
    return _parse_param_tokens(line[len("parameters ") :])


def test_injection_rewrites_an_uppercase_declared_parameter() -> None:
    """The deck's OWN `VDD`/`ILOAD` move — no inert lowercase twin is left behind."""
    out = render_native_scs(UPPER_SCS, parameters={"VDD": 1.1, "ILOAD": 2e-3})
    params = _params_of(out)
    assert params == {"VDD": "1.1", "VREF": "0.55", "ILOAD": "0.002"}
    assert "vdd=" not in out and "iload=" not in out  # nothing appended, nothing shadowed


def test_a_lowercase_injection_key_finds_the_uppercase_declaration() -> None:
    """The optimizer's own key casing is irrelevant — the DECK's spelling decides."""
    params = _params_of(render_native_scs(UPPER_SCS, parameters={"vdd": 1.1}))
    assert params["VDD"] == "1.1"
    assert "vdd" not in params  # a second, case-different declaration would be inert


def test_each_candidate_renders_a_DIFFERENT_effective_circuit() -> None:
    """The headline consequence: sweeping a design var must move the value Spectre reads."""
    effective = [
        _params_of(render_native_scs(UPPER_SCS, parameters={"ILOAD": i}))["ILOAD"]
        for i in (0.5e-3, 1.0e-3, 1.5e-3)
    ]
    assert effective == ["0.0005", "0.001", "0.0015"]
    assert len(set(effective)) == 3


def test_an_undeclared_injection_key_warns_loudly(caplog) -> None:
    """No silent no-op: a key the deck never declares is announced, then appended."""
    with caplog.at_level(logging.WARNING, logger="spicexplorer.backends.spectre_deck"):
        out = render_native_scs(UPPER_SCS, parameters={"VDD": 1.1, "w_pass": 8e-5})
    warnings = [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]
    assert any("w_pass" in msg for msg in warnings), warnings
    assert not any("VDD" in msg.split("Declared")[0] for msg in warnings)  # declared → silent
    params = _params_of(out)
    assert params["VDD"] == "1.1" and params["w_pass"] == "8e-05"


def test_a_declared_key_never_warns(caplog) -> None:
    with caplog.at_level(logging.WARNING, logger="spicexplorer.backends.spectre_deck"):
        render_native_scs(UPPER_SCS, parameters={"VDD": 1.1, "iload": 1e-3})
    assert [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING] == []


# ------------------------------------------------ case-VARIANT collisions (O-3 follow-up)
def test_injection_moves_exactly_one_case_variant_symbol() -> None:
    """The committed cmp_002 shape: injecting `vdd` must NOT also rewrite the distinct `VDD`.

    BEFORE: `{'vdd': 0.81}` rendered `parameters vdd=0.81 … VDD=0.81` — one key, two symbols.
    """
    params = _params_of(render_native_scs(CASE_COLLIDING_SCS, parameters={"vdd": 0.81}))
    assert params["vdd"] == "0.81"   # the EXACT spelling the caller named
    assert params["VDD"] == "0.9"    # a DIFFERENT Spectre symbol: untouched
    # nothing else drifted
    assert params["code"] == "7" and params["Vcm"] == "0.475" and params["Vid"] == "1m"


def test_an_exact_spelling_injection_moves_that_exact_symbol() -> None:
    """The rule that "first declaration wins" broke: naming `VDD` must move `VDD`.

    The live rail of the committed cmp_002 decks IS the uppercase `VDD` (the testbench reads
    `dc=VDD`; nothing reads lowercase `vdd`), so under "first declaration wins" a PVT voltage
    corner keyed `SupplyOverride(node='VDD')` moved the dead lowercase symbol and left the
    real rail at its baked value — a silently inert injection, O-3 all over again.

    BEFORE: `{'VDD': 0.81}` rendered `parameters vdd=0.81 … VDD=0.9`.
    """
    params = _params_of(render_native_scs(CASE_COLLIDING_SCS, parameters={"VDD": 0.81}))
    assert params["VDD"] == "0.81"   # BEFORE: "0.9" — the live rail never moved
    assert params["vdd"] == "0.95"   # BEFORE: "0.81" — the dead symbol moved instead


def test_a_case_variant_rail_follows_only_its_own_spelling() -> None:
    """Two rails, two spellings, two independent injections — neither drags the other.

    (The predecessor of this test was named/documented "a 1.8 V rail must not follow a 0.3 V
    injection" while asserting that it did: under "first declaration wins" `{'vdd': 0.30}`
    landed on `VDD`, dropping the 1.8 V rail to 0.3 V. Exact-match-wins is what actually
    delivers the claim, so name, docstring and assertion now agree.)
    """
    deck = "simulator lang=spectre\nglobal 0\nparameters VDD=1.8 vdd=0.25\n"
    # the lowercase 0.25 V symbol is the one named → the 1.8 V rail stays put
    assert _params_of(render_native_scs(deck, parameters={"vdd": 0.30})) == {
        "VDD": "1.8",   # BEFORE: "0.3" — the 1.8 V rail DID follow the injection
        "vdd": "0.3",   # BEFORE: "0.25" — the named symbol did NOT move
    }
    # …and the mirror: naming the uppercase rail moves only it
    assert _params_of(render_native_scs(deck, parameters={"VDD": 0.30})) == {
        "VDD": "0.3",
        "vdd": "0.25",
    }


def test_an_ambiguous_case_variant_injection_raises_instead_of_guessing() -> None:
    """No exact match + two declared variants = no evidence for either. Refuse, don't guess.

    BEFORE: `{'Vdd': 0.30}` silently resolved onto the first declaration.
    """
    deck = "simulator lang=spectre\nglobal 0\nparameters VDD=1.8 vdd=0.25\n"
    with pytest.raises(AmbiguousParameterCaseError) as exc:
        render_native_scs(deck, parameters={"Vdd": 0.30}, source="tb_ldo.scs")
    msg = str(exc.value)
    assert "tb_ldo.scs" in msg                       # the deck
    assert "'Vdd'" in msg                            # the key
    assert "VDD" in msg and "vdd" in msg             # the candidates


def test_a_case_variant_collision_is_announced(caplog) -> None:
    """Silent is the failure mode: name both spellings so the deck can be fixed."""
    with caplog.at_level(logging.WARNING, logger="spicexplorer.backends.spectre_deck"):
        render_native_scs(CASE_COLLIDING_SCS, parameters={"vdd": 0.81})
    warnings = [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING]
    assert any("CASE-VARIANT" in m and "vdd" in m and "VDD" in m for m in warnings), warnings


def test_no_collision_warning_without_a_collision(caplog) -> None:
    """The warning must stay actionable — an ordinary deck never trips it."""
    with caplog.at_level(logging.WARNING, logger="spicexplorer.backends.spectre_deck"):
        render_native_scs(UPPER_SCS, parameters={"vdd": 1.1})
    assert [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING] == []


def _cmp_002_run_decks() -> "list[Path]":
    """The 8 committed cmp_002 run decks, or a skip when analog-db is not checked out."""
    root = Path(__file__).resolve().parents[3] / "examples/analog-db/circuits"
    runs = root / "cmp_002_strongarm/spectre/28nm/netlist/runs"
    if not runs.is_dir():
        pytest.skip("examples/analog-db submodule not checked out")
    return sorted(runs.glob("*.scs"))


def test_the_committed_cmp_002_decks_still_declare_the_colliding_pair() -> None:
    """Guard on the real corpus: if analog-db ever renames the pair this test may retire.

    Runs all three resolution rules against the REAL committed deck text (8 decks, 4 of them
    declaring the pair at DIFFERENT values), not a synthetic transcription of it.
    """
    decks = _cmp_002_run_decks()
    colliding, differing = [], []
    for deck in decks:
        text = deck.read_text()
        params = _params_of(text)
        if not ("vdd" in params and "VDD" in params):
            continue
        colliding.append(deck.name)
        if params["vdd"] != params["VDD"]:
            differing.append(deck.name)

        # rule 1 — an exact spelling wins, in BOTH directions, and moves nothing else
        upper = _params_of(render_native_scs(text, parameters={"VDD": 0.81}, source=str(deck)))
        assert upper["VDD"] == "0.81", deck.name   # BEFORE: params["VDD"] — the live rail
        assert upper["vdd"] == params["vdd"], deck.name  # BEFORE: "0.81"
        lower = _params_of(render_native_scs(text, parameters={"vdd": 0.81}, source=str(deck)))
        assert lower["vdd"] == "0.81", deck.name
        assert lower["VDD"] == params["VDD"], deck.name

        # rule 3 — a spelling the deck does not declare is ambiguous here, so it raises
        with pytest.raises(AmbiguousParameterCaseError):
            render_native_scs(text, parameters={"Vdd": 0.81}, source=str(deck))

    assert len(decks) == 8, [d.name for d in decks]
    assert len(colliding) == 8, colliding
    assert len(differing) == 4, differing  # the 4 that carry vdd=0.95 vs VDD=0.9


def test_a_collision_free_committed_deck_still_takes_the_case_insensitive_fallback() -> None:
    """Rule 2 on real committed bytes — the genuine O-3 case must keep working.

    `amp_001_5t/spectre/28nm/netlist/runs/vdd_0p9.scs` declares `parameters VDD=0.9` and
    nothing else, so a lowercase injection has exactly one candidate and must take it.
    """
    root = Path(__file__).resolve().parents[3] / "examples/analog-db/circuits"
    deck = root / "amp_001_5t/spectre/28nm/netlist/runs/vdd_0p9.scs"
    if not deck.is_file():
        pytest.skip("examples/analog-db submodule not checked out")
    text = deck.read_text()
    assert _params_of(text) == {"VDD": "0.9"}, "fixture drifted — retarget this test"
    out = _params_of(render_native_scs(text, parameters={"vdd": 0.81}, source=str(deck)))
    assert out == {"VDD": "0.81"}   # the deck's own spelling moved, nothing inert appended


class _FakeBridge:
    """Duck-typed stand-in for the bridge `SpectreSimulator` (records what it was handed)."""

    def __init__(self) -> None:
        self.calls: list[tuple[Path, dict[str, Any]]] = []

    def run_simulation(self, netlist: Path, params: dict[str, Any]) -> Any:
        self.calls.append((Path(netlist), dict(params)))
        return type("_Res", (), {"data": {}, "metadata": {}})()


def test_a_pvt_voltage_corner_reaches_an_uppercase_declared_rail(tmp_path: Path) -> None:
    """`apply_corner` keys supplies by `SupplyOverride.node` — an uppercase `VDD` node
    against an uppercase-declared deck used to leave the corner running the baked rail."""
    deck = tmp_path / "ldo.scs"
    deck.write_text(UPPER_SCS)
    bridge = _FakeBridge()
    sim = SpectreSimulator(bridge, native_scs=deck, deck_dir=tmp_path / "runs")
    sim.update_params({"ILOAD": 1.5e-3})
    sim.apply_corner(
        Corner(
            name="ss_125C_0V81",
            model_includes=[ModelInclude(lib_file="models.scs", section="top_ss")],
            temp=125.0,
            supplies=[SupplyOverride(node="VDD", value=0.81)],
        ),
        model_lib_root="/opt/kit",
    )
    sim.run(label="ldo__ss")

    rendered = _params_of(bridge.calls[-1][0].read_text())
    assert rendered["VDD"] == "0.81"    # the corner's rail, not the deck's baked 0.9
    assert rendered["ILOAD"] == "0.0015"
    assert "vdd" not in rendered
