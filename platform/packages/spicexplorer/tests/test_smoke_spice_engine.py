"""Smoke tests for spicexplorer.spice_engine.

Coverage:
  - NGSpice_Wrapper can be instantiated against the example OTA netlist
  - Sanity check confirms ngspice binary + model libraries are reachable
  - Parameter update roundtrip does not raise
  - A real AC simulation runs end-to-end and returns a RawRead (slow)
"""

from _spicexplorer_fixtures import EXAMPLE_TB_NETLIST, requires_ngspice, slow


@requires_ngspice
def test_ngspice_wrapper_imports():
    """Library-level import works and exposes key symbols."""
    from spicexplorer_core.spice_engine import (
        Ngspice_Plot_Type,
        NGSpice_Wrapper,
        Sim_Execution_Type,
    )

    assert NGSpice_Wrapper is not None
    assert hasattr(Sim_Execution_Type, "RUN_AND_WAIT")
    assert hasattr(Ngspice_Plot_Type, "AC")


@requires_ngspice
def test_ngspice_wrapper_instantiation(tmp_path):
    """NGSpice_Wrapper can be constructed without raising."""
    from spicexplorer_core.spice_engine import NGSpice_Wrapper

    wrapper = NGSpice_Wrapper(
        netlist_filename=EXAMPLE_TB_NETLIST,
        testbench_name="tb_loopgain_smoke",
        output_folder=tmp_path / "spice_out",
    )
    assert wrapper is not None


@requires_ngspice
def test_ngspice_sanity_check(tmp_path):
    """run_sanity_check() passes when ngspice binary and model libraries are found."""
    from spicexplorer_core.spice_engine import NGSpice_Wrapper

    wrapper = NGSpice_Wrapper(
        netlist_filename=EXAMPLE_TB_NETLIST,
        testbench_name="tb_loopgain_smoke",
        output_folder=tmp_path / "spice_out",
    )
    ok = wrapper.run_sanity_check()
    assert ok, "run_sanity_check() returned False — check ngspice installation and model library paths"


@requires_ngspice
def test_ngspice_update_params(tmp_path):
    """update_params() accepts a valid parameter dict and does not raise."""
    from spicexplorer_core.spice_engine import NGSpice_Wrapper

    wrapper = NGSpice_Wrapper(
        netlist_filename=EXAMPLE_TB_NETLIST,
        testbench_name="tb_loopgain_smoke",
        output_folder=tmp_path / "spice_out",
    )
    # Use a known DUT parameter from the OTA cascode design
    wrapper.update_params({"X_DUT_M1M2_W": 2e-6, "X_DUT_L": 300e-9})


@requires_ngspice
@slow
def test_ngspice_run_and_wait(tmp_path):
    """A real ngspice simulation completes and returns a non-None RawRead."""
    from spicexplorer_core.spice_engine import NGSpice_Wrapper

    wrapper = NGSpice_Wrapper(
        netlist_filename=EXAMPLE_TB_NETLIST,
        testbench_name="tb_loopgain_smoke",
        output_folder=tmp_path / "spice_out",
    )
    raw, log_path, status = wrapper.run_and_wait(exe_log=False)
    assert raw is not None, f"Simulation returned no RawRead — status: {status}, log: {log_path}"
