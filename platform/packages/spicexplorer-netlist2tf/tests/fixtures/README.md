# Unit-test fixtures

Small SPICE netlists copied from the analog example DB so this package's **unit** tests run
without depending on the example database (plan `doc/archive/plan_examples_db.md` §3c part 1). The DB
may be absent on a shallow clone or, after the Phase-4 extraction, live in the
`examples/analog-db/` submodule — leaf unit tests must not require it.

Integration/`slow` tests that genuinely exercise the corpus go through
`spicexplorer_analog_db.paths.db_root()` instead (and skip cleanly when the DB is absent).

The `ota-5t_tb-ac.spice` copy has its `.include ../xschem/*.save` line stripped (xschem-only
metadata, irrelevant to parsing/MNA). Refresh with the platform's example netlists if the
upstream topology changes.

`ota-5t_open_loop_ngspice.txt` is a **recorded simulator answer**, not a netlist: the `name = value`
lines ngspice printed for `test_n2tf_slow_sim.test_ihp_ota_open_loop_matches_ngspice_ac` (each PSP
device's operating point, then the open-loop `.ac` measures `a0` / `f3db` / `ugf`). The fast test
`test_n2tf_ota_bench_helpers.py` replays it through the whole OD-8 acceptance, so the netlist2tf half
runs on hosts with no ngspice or IHP PDK. Recorded 2026-09-25 (ngspice-45, IHP sg13g2 open PDK,
`mos_tt`, 27 °C). Re-record it where the live test runs — when the OTA fixture, the probe list or the
PDK models change — by capturing that test's ngspice stdout and keeping only the lines its `_VALUE`
pattern matches.
