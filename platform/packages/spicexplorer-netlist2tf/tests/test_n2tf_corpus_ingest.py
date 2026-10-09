"""Every analog-db deck ingests (ROAD-02 corpus guard), and every ``ac_open_loop`` bench, on every
PDK, models every device, names its own input and builds a solvable MNA system (WP-50, #310).

The single-quoted values analog-db exports (``C0 a b 'CAPACITOR_0'``) crashed ingestion on 46 of
the 72 abstract netlists. analog-db's own Tier-1 ``n2tf:ingest`` check only SKIPS on an exception
for a circuit with no symbolic metric, so a regression there goes unreported; this sweep fails
and names the deck.

The MNA check stops before the symbolic determinant: :func:`check_solvable` is an exact rank at
random values, milliseconds per bench, where the determinant runs for minutes on a 3-stage
amplifier. It is the gate; the per-deck transfer functions are the corpus script's job
(``scripts/corpus_sweep.py``, table in ``results/corpus_sweep.md``). A bench that stops solving
fails here with the refusal, which names the nets. Before the case-insensitive net fix (B-PF-5)
amp_002, amp_003 and amp_011 were singular at the default level: their subckt bodies spell
``VOUT``/``VINN``/``VINP`` in upper case, and those nets came through as floating ``VOUT_xdut``.

Gated on the nested ``examples/analog-db`` checkout, like the core area-walk demo tests: without
it the parameter lists are empty and pytest skips.
"""

from __future__ import annotations

import pytest
from spicexplorer_core import project_root
from spicexplorer_netlist2tf import (
    Fidelity,
    build_system,
    detect_ac_input,
    from_file,
    small_signal_model,
)
from spicexplorer_netlist2tf.mna import SingularSystemError, check_solvable

_DB = project_root() / "examples/analog-db"
_ABSTRACT = sorted(_DB.glob("circuits/*/abstract/netlist.spice"))
_AC_OPEN_LOOP = sorted(_DB.glob("raw/**/ac_open_loop.spice"))

#: Three of the sky130 benches refused at ``Fidelity.IDEAL`` (the sweep's ``ideal`` column lists all
#: 14), and the net each refusal names: a replica
#: branch where only MOS drains meet, which has no conductance without ``ro`` (L-PF-40).
_REFUSED_AT_IDEAL = {
    "amp_002_alfio_raffc": ("DM_1_xdut",),
    "amp_003_fan_smc": ("DM_1_xdut",),
    "amp_011_peng_iac": ("net7_xdut",),
}


def _id(path) -> str:  # noqa: ANN001
    return str(path.relative_to(_DB))


@pytest.mark.parametrize("deck", _ABSTRACT, ids=_id)
def test_abstract_netlist_ingests(deck):
    ir = from_file(deck)
    assert ir.devices, f"{_id(deck)} ingested no devices"


@pytest.mark.parametrize("deck", _AC_OPEN_LOOP, ids=_id)
def test_raw_ac_open_loop_bench_ingests(deck):
    ir = from_file(deck)
    assert ir.devices, f"{_id(deck)} ingested no devices"


@pytest.mark.parametrize("deck", _AC_OPEN_LOOP, ids=_id)
def test_ac_open_loop_bench_builds_a_solvable_mna(deck):
    ssir = small_signal_model(from_file(deck))  # the default level, SOME_PARASITIC
    # the G VCCS cards (amp_025, amp_028, amp_030, amp_031) are modelled since #310
    assert ssir.unmodelled == ()
    # the bench's one AC source, or its DM pair (Vinp vinp vcm ac 0.5 / Vinn vinn vcm ac -0.5)
    check_solvable(build_system(ssir), detect_ac_input(ssir))  # raises SingularSystemError


@pytest.mark.parametrize("circuit", sorted(_REFUSED_AT_IDEAL))
def test_ideal_level_refusal_names_the_drain_only_net(circuit):
    deck = _DB / "raw" / circuit / "sky130" / "ac_open_loop.spice"
    if not deck.is_file():
        pytest.skip("examples/analog-db is not checked out")
    ssir = small_signal_model(from_file(deck), level=Fidelity.IDEAL)
    with pytest.raises(SingularSystemError) as exc:
        check_solvable(build_system(ssir), detect_ac_input(ssir))
    assert exc.value.nets == _REFUSED_AT_IDEAL[circuit]
    assert "no current depends on the voltage" in str(exc.value)
