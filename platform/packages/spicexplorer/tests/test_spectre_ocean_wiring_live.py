"""LIVE proof of the FULL native-Spectre + OCEAN wiring (opt-in; needs Cadence).

Drives the whole production path on a Cadence-equipped host: a YAML project with
`sim_engine: spectre` and a testbench that is a native Spectre `.scs` FILE (via `netlist:`,
exactly like an ngspice `.spice`) → the orchestrator builds the simulator through the real
`build_simulator` factory (native-file injection mode) → a real `optimize()` loop, where
each candidate's design variable is rewritten into the deck's `parameters` line and every
`target_spec`'s `measurement` recipe is evaluated by a live persistent `ocean` session and
scored under its spec name.

The two things this pins that the offline fakes can't: (1) design-param injection actually
reaches Spectre — the swept input width MOVES `gm1` across candidates (a fixed deck would
give identical results, the exact footgun of running a `.scs` verbatim); (2) the OCEAN
license session is auto-opened by the loop and closed at `optimize()` teardown.

The deck is generated once from the committed ngspice 5T-OTA tb (deck origin is orthogonal
to the native-file path under test). Opt-in gating: bridge + `SPICEXPLORER_FOUNDRY65_MODELS`
(NDA — env only, never the repo) + `VB_CADENCE_CSHRC`. The models path is written into a
tmp YAML at runtime, never committed.
"""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import numpy as np
import pytest

pytestmark = pytest.mark.slow

_MODELS = os.environ.get("SPICEXPLORER_FOUNDRY65_MODELS", "")


@pytest.mark.skipif(
    not (_MODELS and Path(_MODELS).expanduser().is_file()),
    reason="set SPICEXPLORER_FOUNDRY65_MODELS to the FOUNDRY-65 Spectre model library .scs",
)
def test_live_full_loop_native_scs_injection_moves_the_metric(tmp_path: Path) -> None:
    pytest.importorskip("virtuoso_bridge", reason="virtuoso-bridge not installed in this venv")
    from spicexplorer.backends.ocean_metrics import OceanMetricsError, OceanMetricsSession
    from spicexplorer.backends.spectre_deck import (
        ac_analysis,
        dc_oppoint_analysis,
        deck_spec_from_ngspice,
        render_spectre_deck,
    )
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
    )
    from spicexplorer_core import project_root

    try:
        OceanMetricsSession.from_vb_env().close()
    except OceanMetricsError:
        pytest.skip("VB_CADENCE_CSHRC not resolvable — no Cadence shell for ocean")

    # --- 1. materialize a native Spectre `.scs` testbench (the YAML `netlist:` target). ---
    example = project_root() / "examples/OTA/5t-ota/ihp-sg13g2/spice/ota-5t_tb-ac.spice"
    deck = render_spectre_deck(
        deck_spec_from_ngspice(
            example, pdk="FOUNDRY-n65", source_pdk="ihp-sg13g2",
            analyses=(dc_oppoint_analysis(), ac_analysis(1e3, 1e8, 101)),
            parameters={"vcm": 0.6},
        )
    )
    tb_scs = tmp_path / "spice" / "ota_5t_tb_ac.scs"
    tb_scs.parent.mkdir(parents=True, exist_ok=True)
    tb_scs.write_text(deck)

    # --- 2. a Spectre project that sweeps the input-pair width + scores 3 OCEAN metrics. ---
    models = str(Path(_MODELS).expanduser())
    yaml_body = f"""
project:
  name: live-native-scs-loop
  description: full loop over a native Spectre .scs, scored by OCEAN
  simulator: spectre
  sim_engine: spectre
  ws_root: {tmp_path}
  netlist: spice/ota_5t_tb_ac.scs
  outdir: out
  tech_spec: {{name: FOUNDRY-n65, constraints: {{}}}}
  dut_params:
    - {{name: x_dut_nfet_input_w, min_val: 0.3u, max_val: 2u}}
  testbenches:
    - {{name: tb_ac, netlist: spice/ota_5t_tb_ac.scs, params: []}}
  pvt:
    mode: single
    active_corner: tt_27C_1V20
    corners:
      - name: tt_27C_1V20
        enabled: true
        model_includes: [{{lib_file: {models}, section: tt_lvt}}]
        supply: {{node: vdd, value: 1.2}}
        temp: 27
  optimizer_config:
    name: SamplingSearch
    type: nevergrad
    random_seed: 3
    budget: 3
    target_specs:
      - {{name: gm1, testbench: tb_ac, sim_type: op, goal: exceed, target: 1e-4, range: 1e-3,
         measurement: {{builder: device_op_param, instance: XOTA.XM1, param: gm}}}}
      - {{name: vtail, testbench: tb_ac, sim_type: op, goal: exceed, target: 0.1, range: 1,
         measurement: {{builder: op_node_voltage, node: XOTA.tail}}}}
      - {{name: gain_db, testbench: tb_ac, sim_type: ac, goal: exceed, target: -1, range: 5,
         measurement: {{builder: ac_gain_db_at, signal: v_out, freq_hz: 1000.0}}}}
"""
    yaml_path = tmp_path / "project_setup.yaml"
    yaml_path.write_text(textwrap.dedent(yaml_body))

    # --- 3. build through the REAL factory + run the loop (OCEAN session auto-managed). ---
    orch = Circuit_Optimizer_Orchestrator_with_SPICE(
        project_setup_path=yaml_path,
        optimizer_type=Optimizer_Type_Enum.NEVERGRAD_CONSTRAINT,
    )
    orch.project_setup.parallel_sim = False
    opt = orch.get_optimizer()
    opt.disable_autosave = True
    opt.parameterize()
    log = opt.optimize()  # optimize()'s finally closes the OCEAN session (license released)

    assert log is not None and len(log) == 3
    fits = [e.fit_summary or {} for e in log]
    widths = [float(e.point.params["x_dut_nfet_input_w"]) for e in log]
    gm1 = [float(fs["gm1"]["curr_val"]) for fs in fits]
    vtail = [float(fs["vtail"]["curr_val"]) for fs in fits]
    gain = [float(fs["gain_db"]["curr_val"]) for fs in fits]
    print(f"\nLIVE loop: widths={widths}\n  gm1={gm1}\n  vtail={vtail}\n  gain_db={gain}")

    # every OCEAN metric evaluated on every candidate (no NaN escape)
    assert all(np.isfinite(v) for v in gm1 + vtail + gain), (gm1, vtail, gain)
    # physically sane (5T-OTA op point + unity-buffer AC; loose — this is a swept design)
    assert all(g > 0 for g in gm1), gm1                    # transconductance is positive
    assert all(0.0 < v < 1.3 for v in vtail), vtail        # a bias-node voltage under 1.2 V rail
    assert all(-15.0 < g < 6.0 for g in gain), gain        # unity-buffer, wide band
    # THE injection proof: sweeping the input width MOVED the metrics across candidates — a
    # fixed/verbatim deck would give identical results. Distinct gm1 ⇒ params reached Spectre.
    assert len({round(v, 12) for v in gm1}) > 1, f"gm1 constant across candidates: {gm1}"
