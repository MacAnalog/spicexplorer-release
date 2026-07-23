# Unit-test fixtures

Small SPICE netlists copied from the analog example DB so this package's **unit** tests run
without depending on the example database (plan `doc/plan_examples_db.md` §3c part 1). The DB
may be absent on a shallow clone or, after the Phase-4 extraction, live in the
`examples/analog-db/` submodule — leaf unit tests must not require it.

Integration/`slow` tests that genuinely exercise the corpus go through
`spicexplorer_analog_db.paths.db_root()` instead (and skip cleanly when the DB is absent).

The `ota-5t_tb-ac.spice` copy has its `.include ../xschem/*.save` line stripped (xschem-only
metadata, irrelevant to parsing/MNA). Refresh with the platform's example netlists if the
upstream topology changes.
