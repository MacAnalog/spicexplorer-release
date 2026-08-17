"""P6 — end-to-end ``transfer_function`` one-liner + the R1 acceptance bar.

The R1 bar (plan §10 / plan_next_steps §R1): a library API + README quickstart + deterministic
tracked-fixture tests + a single Pydantic contract. Solved end to end on real OTA-core topologies;
the committed enable-bearing subckts are also exercised through ingest→model→build (a full solve of
those needs the DC-input stimulus overlay — P7).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import sympy as sp
from spicexplorer_core.spice_engine import NetlistView
from spicexplorer_netlist2tf import (
    Fidelity,
    TransferFunctionResult,
    transfer_function,
)

_FIX = Path(__file__).resolve().parent / "fixtures"

# A real 5T OTA core (diff pair + mirror load, ideal tail) — well-posed for a single-ended TF.
_OTA = """* 5T OTA core
M1 outn vinp tail 0 nmos
M2 outp vinn tail 0 nmos
M3 outn outn vdd vdd pmos
M4 outp outn vdd vdd pmos
Itail tail 0 dc ib
.end
"""

_CS = "* cs\nM1 out in 0 0 nmos\nRL out 0 RL\n.end"


# ------------------------------------------------------------------------
# The one-liner
# ------------------------------------------------------------------------
def test_one_liner_returns_contract_from_text():
    res = transfer_function(_CS, ("out", "0"), ("in", "0"))
    assert isinstance(res, TransferFunctionResult)
    gm, ro, rl = sp.symbols("gm_m1 ro_m1 rl")
    assert sp.simplify(res.as_sympy_exact() - (-gm * ro * rl / (ro + rl))) == 0
    assert res.conv_type == "se"
    assert res.model_level == "some_parasitic"


def test_one_liner_ota_validated_numeric_gain():
    op = {f"gm_m{i}": 1e-3 for i in (1, 2, 3, 4)} | {f"ro_m{i}": 1e5 for i in (1, 2, 3, 4)}
    res = transfer_function(_OTA, ("outp", "0"), ("vinp", "vinn"), operating_point=op)
    assert res.conv_type == "diff"
    # single-ended OTA gain gm1·(ro2∥ro4) ≈ 1e-3 · 50k = 50 → |Av| well above unity
    assert res.dc_gain.value is not None and abs(res.dc_gain.value) > 10


def test_one_liner_simplify_bundle():
    # Opt into reduction: the 'ideal' bundle drops dominated terms, validated against exact.
    op = {f"gm_m{i}": 1e-3 for i in (1, 2, 3, 4)} | {f"ro_m{i}": 1e5 for i in (1, 2, 3, 4)}
    res = transfer_function(_OTA, ("outp", "0"), ("vinp", "vinn"),
                            assumptions="ideal", operating_point=op)
    assert res.validation is not None and res.validation.passed
    # the simplified form is no longer than the exact (terms were dropped or it's unchanged)
    assert len(res.tf_simplified_expr) <= len(res.tf_exact_expr)


def test_one_liner_deterministic():
    a = transfer_function(_CS, ("out", "0"), ("in", "0"))
    b = transfer_function(_CS, ("out", "0"), ("in", "0"))
    assert a.tf_exact_expr == b.tf_exact_expr
    assert a.model_dump_json() == b.model_dump_json()


def test_one_liner_selective_numericization():
    res = transfer_function(_CS, ("out", "0"), ("in", "0"), subs={"ro_m1": 2e4, "rl": 1e4})
    assert res.solve_path == "selectively_numericized"
    assert res.kept_symbolic == ["gm_m1"]


# ------------------------------------------------------------------------
# Real committed fixtures — exercised through the pipeline
# ------------------------------------------------------------------------
def test_pipeline_accepts_netlistview_source():
    # A NetlistView is a valid source; ingest the committed 5T subckt definition.
    tb = _FIX / "ota-5t_tb-ac.spice"
    ota = NetlistView.from_file(tb).get_subcircuit_named("ota")
    assert ota is not None
    # The bare subckt has DC-only enable gates that float at this level → a clean, explicit error
    # (the stimulus overlay that ties DC inputs to AC ground is P7).
    with pytest.raises(ValueError, match="singular"):
        transfer_function(ota, ("vout", "0"), ("vinp", "vinn"))


def test_full_fidelity_ota_has_poles():
    # FULL fidelity over a 4-transistor OTA is past the fully-symbolic ceiling, so numericize via
    # subs (the selective-numericization lever) — fast, and still exercises the full cap set → poles.
    subs = ({f"gm_m{i}": 1e-3 for i in (1, 2, 3, 4)}
            | {f"ro_m{i}": 1e5 for i in (1, 2, 3, 4)}
            | {f"{c}_m{i}": 1e-14 for i in (1, 2, 3, 4) for c in ("cgs", "cgd", "cdb", "csb")}
            | {"gmb_m%d" % i: 2e-4 for i in (1, 2, 3, 4)})
    res = transfer_function(_OTA, ("outp", "0"), ("vinp", "vinn"),
                            level=Fidelity.FULL, subs=subs, operating_point=subs)
    assert len(res.poles) >= 1  # caps now create finite poles
    assert res.model_level == "full"
    assert res.solve_path == "selectively_numericized"
