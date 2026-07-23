"""Unit tests for deck_prep: the PDK slim-corner-lib swap + noise solver guard.

Pure (no live ngspice / no real PDK): a fake slim lib is written to a tmp
`$PDK_ROOT/<subdir>/libs.tech/ngspice/corners/` layout and `plan_slim_swap` is exercised
across the safety gates. The multi-corner test replicates the strip+add sequence
`_prepare_ngspice_netlist` runs, proving slim sections don't accumulate when one editor is
re-used across PVT corners.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
from spicexplorer_core.spice_engine.deck_prep import (
    SLIM_LIB_SPECS,
    noise_needs_sparse,
    plan_slim_swap,
)

SLIM = "sky130_slim.lib.spice"


def _abs_slim(root, subdir="sky130A") -> str:
    """The absolute path plan_slim_swap emits for a slim lib under ``root/<subdir>/…/corners/``.

    The lib lives in corners/, which is OFF ngspice's sourcepath, so the plan references it by
    absolute path (a bare basename fails to resolve — proven in-container).
    """
    return str(Path(root) / subdir / "libs.tech" / "ngspice" / "corners" / SLIM)

_SLIM_FIXTURE = """\
* SLIM sky130 corner library — GENERATED (test fixture).
* Families: nfet_01v8, pfet_01v8.
.lib tt
.option scale=1.0u
.include "x_nfet_tt"
.endl tt
.lib ss
.include "x_nfet_ss"
.endl ss
.lib ff
.include "x_nfet_ff"
.endl ff
"""


def _write_slim(root, subdir):
    corners = root / subdir / "libs.tech" / "ngspice" / "corners"
    corners.mkdir(parents=True)
    (corners / SLIM).write_text(_SLIM_FIXTURE)


@pytest.fixture
def pdk_with_slim(tmp_path, monkeypatch):
    """A tmp $PDK_ROOT holding a generated slim lib (families nfet_01v8/pfet_01v8; tt/ss/ff)."""
    _write_slim(tmp_path, "sky130A")
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    monkeypatch.setenv("SPICEXPLORER_SKY130_SLIM_LIB", "auto")
    monkeypatch.delenv("SPICEXPLORER_SLIM_LIB", raising=False)
    return tmp_path


def _core_deck(section="tt", dev="sky130_fd_pr__nfet_01v8"):
    return [
        f".lib sky130.lib.spice {section}",
        ".temp 27",
        f"XM1 d g s b {dev} l=2 w=1",
        "Vd d 0 1",
    ]


def _swap(*args, **kwargs):
    """Run plan_slim_swap and reduce to (slim_lib, sections) | None for concise asserts."""
    plan = plan_slim_swap(*args, **kwargs)
    return None if plan is None else (plan.slim_lib, plan.sections)


def test_registry_has_sky130():
    assert "sky130" in {s.name for s in SLIM_LIB_SPECS}


def test_auto_covered_swaps(pdk_with_slim):
    assert _swap(_core_deck()) == (_abs_slim(pdk_with_slim), ["tt"])


def test_auto_emits_resolvable_absolute_path(pdk_with_slim):
    # regression: the slim lib lives in corners/, which is NOT on ngspice's sourcepath, so a
    # bare `.lib sky130_slim.lib.spice` errors ("Could not find library file"). The plan must
    # carry an absolute, on-disk path — verified end-to-end in the docker base image.
    plan = plan_slim_swap(_core_deck())
    assert plan is not None
    assert os.path.isabs(plan.slim_lib)
    assert plan.slim_lib.endswith(SLIM)
    assert Path(plan.slim_lib).is_file()


def test_docker_sky130_layout_resolves(tmp_path, monkeypatch):
    # the vendored docker image uses `$PDK_ROOT/sky130/...` (not the native `sky130A/`)
    _write_slim(tmp_path, "sky130")
    monkeypatch.setenv("PDK_ROOT", str(tmp_path))
    monkeypatch.setenv("SPICEXPLORER_SKY130_SLIM_LIB", "auto")
    assert _swap(_core_deck()) == (_abs_slim(tmp_path, "sky130"), ["tt"])


def test_auto_uncovered_family_keeps_full(pdk_with_slim):
    assert _swap(_core_deck(dev="sky130_fd_pr__nfet_01v8_lvt")) is None


def test_ihp_deck_no_swap(pdk_with_slim):
    assert _swap([".lib cornerMOSlv.lib mos_tt", "XM1 d g s b sg13_lv_nmos"]) is None


def test_disabled_per_spec_env(pdk_with_slim, monkeypatch):
    monkeypatch.setenv("SPICEXPLORER_SKY130_SLIM_LIB", "0")
    assert _swap(_core_deck()) is None


def test_disabled_global_env(pdk_with_slim, monkeypatch):
    monkeypatch.delenv("SPICEXPLORER_SKY130_SLIM_LIB", raising=False)
    monkeypatch.setenv("SPICEXPLORER_SLIM_LIB", "off")
    assert _swap(_core_deck()) is None


def test_undefined_section_keeps_full(pdk_with_slim):
    assert _swap(_core_deck(section="sf")) is None  # fixture defines tt/ss/ff only


def test_include_deck_keeps_full(pdk_with_slim):
    assert _swap([".lib sky130.lib.spice tt", '.include "dut.sp"']) is None


def test_no_visible_devices_keeps_full(pdk_with_slim):
    assert _swap([".lib sky130.lib.spice tt", "Vd d 0 1"]) is None


def test_devices_scanned_from_deck_text_not_editor(pdk_with_slim):
    # analog-db shape: editor has the .lib + an opaque `XDUT ... amp` (no device token — the
    # devices live in a `.subckt` body SpiceEditor hides). Coverage must come from the deck TEXT.
    editor = [".lib sky130.lib.spice tt", "XDUT vdd vout vinp vinn ibias vss amp_001_5t"]
    deck_text = editor + [
        ".subckt amp_001_5t vdd vout vinp vinn ibias vss",
        "XM1 outm vinp tail vss sky130_fd_pr__nfet_01v8 l=2 w=1",
        ".ends",
    ]
    assert _swap(editor, device_scan_lines=deck_text) == (_abs_slim(pdk_with_slim), ["tt"])
    assert _swap(editor) is None  # without the deck text, devices invisible → fail-safe


def test_explicit_name_trusted_without_pdk(monkeypatch):
    monkeypatch.delenv("PDK_ROOT", raising=False)
    monkeypatch.setenv("SPICEXPLORER_SKY130_SLIM_LIB", "my_custom.lib.spice")
    assert _swap(_core_deck()) == ("my_custom.lib.spice", ["tt"])


def test_comment_device_ref_ignored(pdk_with_slim):
    deck = [
        ".lib sky130.lib.spice tt",
        "* could use sky130_fd_pr__nfet_01v8_lvt but does not",
        "XM1 d g s b sky130_fd_pr__nfet_01v8 l=2 w=1",
    ]
    assert _swap(deck) == (_abs_slim(pdk_with_slim), ["tt"])


def _apply_prepare_swap(lines):
    """Replicate _prepare_ngspice_netlist's slim-swap on a plain line list."""
    plan = plan_slim_swap(lines)
    if plan is None:
        return list(lines)
    full_re = re.compile(plan.full_lib_strip, re.IGNORECASE)
    slim_re = re.compile(plan.slim_lib_strip, re.IGNORECASE)
    kept = [ln for ln in lines if not (isinstance(ln, str) and (full_re.match(ln) or slim_re.match(ln)))]
    kept += [f".lib {plan.slim_lib} {s}" for s in plan.sections]
    return kept


def test_multicorner_no_accumulation(pdk_with_slim):
    """One editor re-used across tt→ss→ff must never carry >1 slim `.lib` line."""
    full_strip = re.compile(r"^\s*\.lib\s+\S*sky130\.lib\.spice\s+\S+", re.IGNORECASE)
    slim_strip = re.compile(r"^\s*\.lib\s+\S*sky130_slim\.lib\.spice\s+\S+", re.IGNORECASE)
    lines = _apply_prepare_swap(_core_deck(section="tt"))  # tt run
    for corner in ("ss", "ff"):
        lines = [ln for ln in lines if not full_strip.match(ln)]  # apply_corner re-adds full lib
        lines.append(f".lib sky130.lib.spice {corner}")
        lines = _apply_prepare_swap(lines)
        slim_libs = [ln for ln in lines if slim_strip.match(ln)]
        assert slim_libs == [f".lib {_abs_slim(pdk_with_slim)} {corner}"], f"corner {corner}: {slim_libs}"


def test_repeated_run_idempotent(pdk_with_slim):
    once = _apply_prepare_swap(_core_deck())
    twice = _apply_prepare_swap(once)
    assert [ln for ln in twice if SLIM in ln] == [ln for ln in once if SLIM in ln]


# ---- noise solver guard (PDK-agnostic) ----------------------------------------------
def test_noise_detected_from_control_block():
    deck = [".control", "noise v(vout) Vinp dec 101 1k 100MEG", ".endc"]
    assert noise_needs_sparse([], deck, "amp_001_dc_op") is True


def test_noise_detected_from_testbench_name():
    assert noise_needs_sparse([], [], "amp_001_sky130_noise") is True


def test_no_noise_no_sparse():
    assert noise_needs_sparse([".op"], [".op"], "amp_001_dc_op") is False


def test_existing_solver_option_skips(monkeypatch):
    assert noise_needs_sparse([".option klu"], ["noise v(vout) Vinp dec 101 1k 100MEG"], "noise") is False


def test_noise_guard_disabled(monkeypatch):
    monkeypatch.setenv("SPICEXPLORER_NGSPICE_NOISE_SPARSE", "0")
    assert noise_needs_sparse([], [], "amp_noise") is False
