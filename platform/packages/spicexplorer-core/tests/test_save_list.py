"""The save list: a YAML file that OVERRIDES a deck's `.save`/`.probe`/`save` statements.

Offline only — the transform is pure text, so nothing here needs a simulator. The one `slow`
case runs real ngspice and checks the rawfile actually carries only the listed signals.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import textwrap

import pytest
from spicexplorer_core.spice_engine import (
    ANALYSIS_KINDS,
    SaveList,
    apply_save_list_to_deck,
    deck_analyses,
    load_save_list,
    run_deck,
)

needs_ngspice = pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice not on PATH")

DECK_WITH_SAVES = textwrap.dedent(
    """\
    * a bench that saves everything
    v1 a 0 1
    r1 a b 1k
    c1 b 0 1n
    .save all
    .probe v(a)
    .tran 1n 1u
    .control
    save v(a) v(b)
    run
    write sim.raw
    quit
    .endc
    .end
    """
)

DECK_NO_SAVE = textwrap.dedent(
    """\
    * a bench that saves nothing explicitly
    v1 a 0 1
    r1 a b 1k
    .ac dec 10 1 1meg
    .control
    run
    write sim.raw
    quit
    .endc
    .end
    """
)


def _saves(deck: str) -> list[str]:
    """Every save-ish statement left in a deck, normalised."""
    out = []
    for ln in deck.splitlines():
        s = ln.strip()
        low = s.lower()
        if low.startswith((".save", ".probe")) or low.split()[:1] == ["save"]:
            out.append(" ".join(s.split()))
    return out


# --------------------------------------------------------------------------------- schema


def test_from_mapping_accepts_the_documented_shape():
    sl = SaveList.from_mapping(
        {
            "version": 1,
            "default": ["v(out)"],
            "tran": ["v(out)", "i(vdd)"],
            "ac": ["v(out)"],
            "benches": {"loop_ac": ["v(out)", "v(fb)"]},
        }
    )
    assert sl.all is False
    assert sl.default == ("v(out)",)
    assert sl.analyses["tran"] == ("v(out)", "i(vdd)")
    assert sl.benches["loop_ac"] == ("v(out)", "v(fb)")


def test_unknown_top_level_key_is_refused_with_a_fix():
    with pytest.raises(ValueError) as e:
        SaveList.from_mapping({"transient": ["v(out)"]}, where="save.yaml")
    assert "transient" in str(e.value) and "FIX:" in str(e.value)
    assert "tran" in str(e.value)


def test_empty_signal_list_is_refused():
    with pytest.raises(ValueError) as e:
        SaveList.from_mapping({"tran": []})
    assert "FIX:" in str(e.value)


def test_non_string_signal_is_refused():
    with pytest.raises(ValueError) as e:
        SaveList.from_mapping({"tran": ["v(out)", 3]})
    assert "FIX:" in str(e.value)


def test_all_and_signals_together_is_refused():
    with pytest.raises(ValueError) as e:
        SaveList.from_mapping({"all": True, "tran": ["v(out)"]})
    assert "FIX:" in str(e.value)


def test_analysis_kinds_are_the_documented_closed_set():
    assert ANALYSIS_KINDS == ("op", "dc", "ac", "tran", "noise")


def test_load_save_list_reads_yaml(tmp_path):
    p = tmp_path / "save.yaml"
    p.write_text("default: [v(out)]\ntran: ['v(*)']\n")
    sl = load_save_list(p)
    assert sl.default == ("v(out)",)
    assert sl.analyses["tran"] == ("v(*)",)


def test_importing_spice_engine_does_not_load_the_yaml_parser():
    """pyyaml is a core dependency, but ``load_save_list`` imports it lazily (documented claim).

    A fresh interpreter is needed: this test process has long since imported ``yaml``.
    """
    code = (
        "import sys, spicexplorer_core, spicexplorer_core.spice_engine, "
        "spicexplorer_core.spice_engine.save_list; print('yaml' in sys.modules)"
    )
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=120, check=True
    )
    assert out.stdout.strip() == "False", out.stdout + out.stderr


# ------------------------------------------------------------------------------ resolution


def test_resolution_prefers_bench_then_kind_then_default():
    sl = SaveList.from_mapping({"default": ["v(d)"], "tran": ["v(t)"], "benches": {"b1": ["v(b)"]}})
    assert sl.resolve(bench="b1", kinds=("tran",)) == ("v(b)",)
    assert sl.resolve(bench="other", kinds=("tran",)) == ("v(t)",)
    assert sl.resolve(bench="other", kinds=("ac",)) == ("v(d)",)


def test_resolution_with_no_applicable_entry_is_none():
    sl = SaveList.from_mapping({"tran": ["v(t)"]})
    assert sl.resolve(bench="x", kinds=("ac",)) is None


def test_resolution_unions_several_kinds_in_declared_order():
    sl = SaveList.from_mapping({"ac": ["v(a)"], "tran": ["v(t)", "v(a)"]})
    assert sl.resolve(kinds=("tran", "ac")) == ("v(a)", "v(t)")


def test_all_resolves_to_the_all_sentinel():
    sl = SaveList.from_mapping({"all": True})
    assert sl.resolve(kinds=("tran",)) == ("all",)


# ------------------------------------------------------------------------- kind detection


def test_deck_analyses_reads_body_cards_and_control_commands():
    assert deck_analyses(DECK_WITH_SAVES) == ("tran",)
    assert deck_analyses(DECK_NO_SAVE) == ("ac",)
    control_only = "* t\n.control\nop\nnoise v(out) v1 dec 10 1 1k\n.endc\n.end\n"
    assert deck_analyses(control_only) == ("op", "noise")


def test_deck_analyses_ignores_comments_and_lookalike_words():
    deck = "* .tran in a comment\nvtran a 0 1\n.op\n.end\n"
    assert deck_analyses(deck) == ("op",)


# ----------------------------------------------------------------------------- the rewrite


def test_existing_saves_are_replaced_by_exactly_the_lists_signals():
    sl = SaveList.from_mapping({"tran": ["v(b)", "i(v1)"]})
    out = apply_save_list_to_deck(DECK_WITH_SAVES, sl, bench="t")
    assert _saves(out) == [".save v(b) i(v1)", "save v(b) i(v1)"]
    assert "all" not in out.split(".control")[0].lower().replace(
        "* a bench that saves everything", ""
    )


def test_a_deck_with_no_save_gets_the_list():
    sl = SaveList.from_mapping({"ac": ["v(b)"]})
    out = apply_save_list_to_deck(DECK_NO_SAVE, sl, bench="t")
    assert _saves(out) == [".save v(b)", "save v(b)"]
    assert ".ac dec 10 1 1meg" in out


def test_no_applicable_entry_leaves_the_deck_byte_identical():
    sl = SaveList.from_mapping({"noise": ["onoise_spectrum"]})
    assert apply_save_list_to_deck(DECK_WITH_SAVES, sl, bench="t") == DECK_WITH_SAVES


def test_none_save_list_leaves_the_deck_byte_identical():
    assert apply_save_list_to_deck(DECK_WITH_SAVES, None) == DECK_WITH_SAVES


def test_wildcards_pass_through_verbatim():
    sl = SaveList.from_mapping({"tran": ["v(x.*)", "@m1[id]"]})
    out = apply_save_list_to_deck(DECK_WITH_SAVES, sl)
    assert ".save v(x.*) @m1[id]" in out


def test_all_true_emits_save_all():
    sl = SaveList.from_mapping({"all": True})
    out = apply_save_list_to_deck(DECK_NO_SAVE, sl)
    assert _saves(out) == [".save all", "save all"]


def test_the_control_save_precedes_the_analysis_command():
    sl = SaveList.from_mapping({"tran": ["v(b)"]})
    out = apply_save_list_to_deck(DECK_WITH_SAVES, sl).splitlines()
    i_save = next(i for i, ln in enumerate(out) if ln.strip() == "save v(b)")
    i_run = next(i for i, ln in enumerate(out) if ln.strip() == "run")
    assert out[i_save - 1].strip().lower() == ".control"
    assert i_save < i_run


def test_a_deck_with_no_control_block_gets_only_the_card():
    deck = "* t\nv1 a 0 1\n.save all\n.tran 1n 1u\n.end\n"
    sl = SaveList.from_mapping({"tran": ["v(a)"]})
    out = apply_save_list_to_deck(deck, sl)
    assert _saves(out) == [".save v(a)"]
    assert out.splitlines()[-1].strip() == ".end"


def test_the_rewrite_is_idempotent():
    sl = SaveList.from_mapping({"tran": ["v(b)"]})
    once = apply_save_list_to_deck(DECK_WITH_SAVES, sl)
    assert apply_save_list_to_deck(once, sl) == once


# ------------------------------------------------------------------------------- run_deck


def _fake(tmp_path):
    exe = tmp_path / "bin" / "ngspice"
    exe.parent.mkdir(exist_ok=True)
    exe.write_text("#!/bin/sh\necho 'fake raw' > sim.raw\nexit 0\n")
    exe.chmod(0o755)
    return exe


def test_run_deck_without_a_save_list_writes_the_deck_verbatim(tmp_path):
    r = run_deck(DECK_WITH_SAVES, label="p", workdir=tmp_path / "w", ngspice=_fake(tmp_path))
    assert r.deck.read_text() == DECK_WITH_SAVES
    assert r.deck_text == DECK_WITH_SAVES


def test_run_deck_applies_the_save_list_before_hashing(tmp_path):
    sl = SaveList.from_mapping({"tran": ["v(b)"]})
    plain = run_deck(DECK_WITH_SAVES, label="p", workdir=tmp_path / "w", ngspice=_fake(tmp_path))
    saved = run_deck(
        DECK_WITH_SAVES,
        label="p",
        workdir=tmp_path / "w",
        ngspice=_fake(tmp_path),
        save_list=sl,
    )
    assert _saves(saved.deck.read_text()) == [".save v(b)", "save v(b)"]
    assert saved.dir != plain.dir, "the as-run deck is a different deck and gets its own dir"


def test_run_deck_bench_defaults_to_the_label(tmp_path):
    sl = SaveList.from_mapping({"benches": {"p": ["v(a)"]}, "default": ["v(b)"]})
    r = run_deck(
        DECK_WITH_SAVES, label="p", workdir=tmp_path / "w", ngspice=_fake(tmp_path), save_list=sl
    )
    assert ".save v(a)" in r.deck.read_text()


# ----------------------------------------------------------------------------------- live


@pytest.mark.slow
@needs_ngspice
def test_live_rawfile_carries_only_the_listed_signals(tmp_path):
    deck = textwrap.dedent(
        """\
        * rc chain
        v1 a 0 dc 0 pulse(0 1 1n 1n 1n 100n 200n)
        r1 a b 1k
        c1 b 0 1n
        r2 b c 1k
        c2 c 0 1n
        .save all
        .control
        set filetype=ascii
        tran 1n 400n
        write sim.raw
        quit
        .endc
        .end
        """
    )
    sl = SaveList.from_mapping({"tran": ["v(c)"]})
    wide = run_deck(deck, label="wide", workdir=tmp_path)
    slim = run_deck(deck, label="slim", workdir=tmp_path, save_list=sl)
    assert wide.raw is not None and slim.raw is not None
    wide_vars = wide.raw.read_text(errors="replace")
    slim_vars = slim.raw.read_text(errors="replace")
    assert "v(a)" in wide_vars.lower()
    assert "v(a)" not in slim_vars.lower(), "the save list did not reach ngspice"
    assert "v(c)" in slim_vars.lower()
    assert slim.raw.stat().st_size < wide.raw.stat().st_size


# ------------------------------------------------------- the file-centric wrapper entry point

WRAPPER_DECK = textwrap.dedent(
    """\
    * rc chain for the wrapper
    v1 a 0 dc 0 pulse(0 1 1n 1n 1n 100n 200n)
    r1 a b 1k
    c1 b 0 1n
    r2 b c 1k
    c2 c 0 1n
    .save all
    .control
    save all
    tran 1n 400n
    .endc
    .end
    """
)


def _wrapper(tmp_path, **kw):
    from spicexplorer_core.spice_engine import NGSpice_Wrapper
    from spicexplorer_core.spice_engine.spicelib import _WIPED_OUTPUT_FOLDERS

    tmp_path.mkdir(parents=True, exist_ok=True)
    deck = tmp_path / "wrap.cir"
    deck.write_text(WRAPPER_DECK)
    out = tmp_path / "runs"
    _WIPED_OUTPUT_FOLDERS.discard(out.resolve())
    return deck, NGSpice_Wrapper(
        netlist_filename=deck, output_folder=out, testbench_name="wrap", **kw
    )


@needs_ngspice
def test_wrapper_runs_a_rewritten_copy_and_never_edits_the_caller_netlist(tmp_path):
    """The LDO-scale entry point: `NGSpice_Wrapper(save_list=...)`.

    The rewrite must land in the wrapper's own disposable `output_folder` (so the caller's
    netlist is byte-identical afterwards) and must carry BOTH emitted statements.
    """
    sl = SaveList.from_mapping({"tran": ["v(c)"]})
    deck, w = _wrapper(tmp_path, save_list=sl)
    assert deck.read_text() == WRAPPER_DECK, "the caller's netlist must never be touched"
    assert w.netlist_filename != deck
    assert w.netlist_filename.parent == (tmp_path / "runs")
    assert _saves(w.netlist_filename.read_text()) == [".save v(c)", "save v(c)"]


@needs_ngspice
def test_wrapper_names_the_rewrite_for_the_testbench_not_the_netlist_stem(tmp_path):
    """Sibling wrappers share one `output_folder`; two benches over one deck must not collide."""
    sl = SaveList.from_mapping({"benches": {"tb_a": ["v(b)"], "tb_b": ["v(c)"]}})
    deck, _ = _wrapper(tmp_path, save_list=sl)
    from spicexplorer_core.spice_engine import NGSpice_Wrapper

    out = tmp_path / "runs"
    a = NGSpice_Wrapper(
        netlist_filename=deck, output_folder=out, testbench_name="tb_a", save_list=sl
    )
    b = NGSpice_Wrapper(
        netlist_filename=deck, output_folder=out, testbench_name="tb_b", save_list=sl
    )
    assert a.netlist_filename != b.netlist_filename
    assert _saves(a.netlist_filename.read_text()) == [".save v(b)", "save v(b)"]
    assert _saves(b.netlist_filename.read_text()) == [".save v(c)", "save v(c)"]


@needs_ngspice
def test_wrapper_without_a_save_list_runs_the_caller_netlist_itself(tmp_path):
    deck, w = _wrapper(tmp_path)
    assert w.netlist_filename == deck


@needs_ngspice
def test_wrapper_save_list_that_says_nothing_about_this_deck_is_a_no_op(tmp_path):
    sl = SaveList.from_mapping({"benches": {"someone_else": ["v(b)"]}})
    deck, w = _wrapper(tmp_path, save_list=sl)
    assert w.netlist_filename == deck


@needs_ngspice
def test_wrapper_editor_round_trips_both_emitted_statements(tmp_path):
    """`SpiceEditor` stores a `.control` block opaquely — prove BOTH statements survive it.

    The runner hands ngspice the editor's OWN rendering of the netlist, not the file on disk,
    so a save that the editor drops would never reach the simulator.
    """
    sl = SaveList.from_mapping({"tran": ["v(c)"]})
    _, w = _wrapper(tmp_path, save_list=sl)
    rendered = tmp_path / "as_run.cir"
    assert w.editor is not None
    w.editor.save_netlist(rendered)
    assert _saves(rendered.read_text()) == [".save v(c)", "save v(c)"]


# ngspice's `-r` rawfile is only written for a BODY analysis card; an analysis run from inside
# a `.control` block writes nothing unless the block says `write`. The live case below therefore
# uses body cards — the control-block half is covered by the editor round-trip test above.
WRAPPER_LIVE_DECK = textwrap.dedent(
    """\
    * rc chain, body cards only
    v1 a 0 dc 0 pulse(0 1 1n 1n 1n 100n 200n)
    r1 a b 1k
    c1 b 0 1n
    r2 b c 1k
    c2 c 0 1n
    .save all
    .tran 1n 400n
    .end
    """
)


@pytest.mark.slow
@needs_ngspice
def test_wrapper_live_rawfile_carries_only_the_listed_signals(tmp_path):
    from spicexplorer_core.spice_engine import NGSpice_Wrapper
    from spicexplorer_core.spice_engine.spicelib import _WIPED_OUTPUT_FOLDERS

    sl = SaveList.from_mapping({"tran": ["v(c)"]})
    raws = {}
    for tag, lst in (("wide", None), ("slim", sl)):
        d = tmp_path / tag
        d.mkdir(parents=True)
        deck = d / "live.cir"
        deck.write_text(WRAPPER_LIVE_DECK)
        out = d / "runs"
        _WIPED_OUTPUT_FOLDERS.discard(out.resolve())
        w = NGSpice_Wrapper(
            netlist_filename=deck, output_folder=out, testbench_name=tag, save_list=lst
        )
        raw, _, _ = w.run_and_wait(label=tag)
        assert raw is not None, f"{tag}: ngspice produced no rawfile"
        raws[tag] = {str(n).lower() for n in raw.get_trace_names()}
    assert any(n.startswith("v(a") for n in raws["wide"])
    assert not any(n.startswith("v(a") for n in raws["slim"]), "the save list did not reach ngspice"
    assert any(n.startswith("v(c") for n in raws["slim"])
    assert len(raws["slim"]) < len(raws["wide"])
