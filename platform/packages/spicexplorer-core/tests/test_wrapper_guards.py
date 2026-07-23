"""Guards on the ngspice wrapper's destructive/finicky construction behavior.

``NGSpice_Wrapper._validate`` wipes ``output_folder`` on construction; pointing it at the
directory holding the input netlist used to DELETE THE NETLIST (found building the core
quickstart notebook). The guard now refuses; these tests pin both sides.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from spicexplorer_core.spice_engine import NGSpice_Wrapper
from spicexplorer_core.spice_engine.spicelib import _WIPED_OUTPUT_FOLDERS

RC_DECK = """* RC low-pass (spicelib requires this leading `*` title line)
V1 in 0 dc 0 ac 1
R1 in out 1k
C1 out 0 100p
.ac dec 5 1k 1Meg
.end
"""

needs_ngspice = pytest.mark.skipif(
    shutil.which("ngspice") is None, reason="ngspice not on PATH"
)


def test_output_folder_containing_netlist_is_refused(tmp_path: Path):
    deck = tmp_path / "rc.cir"
    deck.write_text(RC_DECK)
    with pytest.raises(ValueError, match="output_folder.*would be deleted"):
        NGSpice_Wrapper(netlist_filename=deck, output_folder=tmp_path)
    assert deck.exists(), "the guard must fire BEFORE any deletion"
    # nested inside the output folder is just as fatal
    with pytest.raises(ValueError, match="would be deleted"):
        NGSpice_Wrapper(netlist_filename=deck, output_folder=tmp_path.parent)


@needs_ngspice
def test_separate_output_folder_constructs_and_wipes_only_itself(tmp_path: Path):
    deck = tmp_path / "rc.cir"
    deck.write_text(RC_DECK)
    out = tmp_path / "runs"
    out.mkdir()
    (out / "stale.raw").write_text("old artifact")
    # A never-before-seen folder is a first-touch → the documented wipe still fires.
    _WIPED_OUTPUT_FOLDERS.discard(out.resolve())
    w = NGSpice_Wrapper(netlist_filename=deck, output_folder=out, testbench_name="guard")
    assert deck.exists()                      # input untouched
    assert not (out / "stale.raw").exists()   # output folder re-created (documented behavior)
    assert w.editor is not None


@needs_ngspice
def test_sibling_wrappers_sharing_output_folder_do_not_clobber(tmp_path: Path):
    """High-sev regression: `_validate` used to rmtree the shared `output_folder`
    unconditionally, so the 2nd..Nth sibling wrapper (the orchestrator builds one per
    testbench, all pointed at the project `outdir`) wiped the earlier siblings' artifacts
    *mid-construction*. The wipe must now happen only on the first touch this process.
    """
    deck = tmp_path / "rc.cir"
    deck.write_text(RC_DECK)
    shared = tmp_path / "outdir"
    _WIPED_OUTPUT_FOLDERS.discard(shared.resolve())

    # Sibling A prepares the shared folder, then "produces" a per-run artifact.
    a = NGSpice_Wrapper(netlist_filename=deck, output_folder=shared, testbench_name="tbA")
    artifact = shared / "run_1_tbA" / "result.raw"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("A's precious sim output")

    # Sibling B, built for another testbench, points at the SAME folder.
    b = NGSpice_Wrapper(netlist_filename=deck, output_folder=shared, testbench_name="tbB")

    assert artifact.exists(), "sibling wrapper clobbered the shared output_folder"
    assert artifact.read_text() == "A's precious sim output"
    assert a.editor is not None and b.editor is not None


@needs_ngspice
def test_output_folder_rewiped_after_registry_reset(tmp_path: Path):
    """Complement to the sibling test: once a folder is forgotten (e.g. a fresh process),
    a wrapper targeting it is a first-touch again and DOES wipe — the single-wrapper
    clean-slate contract is preserved, not silently disabled."""
    deck = tmp_path / "rc.cir"
    deck.write_text(RC_DECK)
    out = tmp_path / "runs2"

    first = NGSpice_Wrapper(netlist_filename=deck, output_folder=out, testbench_name="one")
    (out / "leftover.raw").write_text("from the first wrapper's session")
    assert first.editor is not None

    # Simulate a brand-new process: the registry no longer knows this folder.
    _WIPED_OUTPUT_FOLDERS.discard(out.resolve())

    NGSpice_Wrapper(netlist_filename=deck, output_folder=out, testbench_name="two")
    assert not (out / "leftover.raw").exists(), "first-touch must still wipe a stale folder"


# --------------------------------------------------------------------------------------
# Dead naming conventions must stay dead (bug report 2026-07-10): parameter values are
# written VERBATIM — no unit suffix keyed off a C*/R* name prefix — and the X_DUT
# classification is a case-insensitive, display-only heuristic.
# --------------------------------------------------------------------------------------
class _StubNetlist:
    """Records set_* calls; knows every parameter (validation always passes)."""

    def __init__(self):
        self.params: dict[str, str] = {}
        self.component_values: dict[str, str] = {}
        self.component_params: dict[str, dict] = {}

    def get_parameter(self, key):
        return "1"

    def set_parameter(self, key, value):
        self.params[key] = value

    def set_component_value(self, key, value):
        self.component_values[key] = value

    def set_component_parameters(self, name, **kwargs):
        self.component_params[name] = kwargs


def _bare_ltspice_wrapper():
    from spicexplorer_core.spice_engine.spicelib import LTspice_Wrapper

    wrapper = LTspice_Wrapper.__new__(LTspice_Wrapper)  # skip __init__ (needs LTspice)
    wrapper.netlist = _StubNetlist()
    return wrapper


def test_ltspice_update_params_writes_c_and_r_params_verbatim():
    # the old convention appended 'p' to C* and 'k' to R* names — CL 5e-14 became
    # "5e-14p" (= 5e-26 F). Names carry no unit semantics anymore: verbatim SI only.
    w = _bare_ltspice_wrapper()
    assert w.update_params({"CL": 5e-14, "RFB": 1e5, "x_dut_nfet_w": 5e-7, "Cc": 2e-12})
    assert w.netlist.params == {
        "CL": "5e-14", "RFB": "100000.0", "x_dut_nfet_w": "5e-07", "Cc": "2e-12",
    }


def test_ltspice_update_component_values_verbatim_and_iterates_items():
    w = _bare_ltspice_wrapper()
    # iterating the dict without .items() used to crash on the first multi-char key
    assert w.update_component_values({"C1": 1e-12, "R1": 2e3})
    assert w.netlist.component_values == {"C1": "1e-12", "R1": "2000.0"}
    assert w.update_component_parameters({"XM1": {"w": 1e-6}})
    assert w.netlist.component_params == {"XM1": {"w": 1e-6}}


def test_ngspice_dut_param_heuristic_is_case_insensitive():
    w = NGSpice_Wrapper.__new__(NGSpice_Wrapper)  # display-only helper needs no engine
    w._dut_parameter_prefix = "X_DUT"
    assert w._is_dut_param("x_dut_nfet_input_w")  # analog-db raw decks are lowercase
    assert w._is_dut_param("X_DUT_PFET_LOAD_L")
    assert not w._is_dut_param("w_pass")  # LDO knobs have no prefix — TB by heuristic,
    assert not w._is_dut_param("VDD")     # the YAML dut_params list stays authoritative
