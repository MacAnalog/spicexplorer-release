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

## `dialects/` — Spectre + HSPICE fixtures

Verbatim copies from analog-db's AnalogGym "Sensing Front End" reference corpus
(`circuits/sfe_*`), which imports **CODA-Team/AnalogGym** (BSD-3-Clause; see the corpus
`PROVENANCE.md` and `LICENSE.AnalogGym` in analog-db). Foundry include paths in the testbench
are already stubbed as `${PDK_ROOT}` upstream in the DB — no PDK content is present:

- `ptat_65_classic.scs` — verbatim Spectre deck (paren node lists, `\` continuations, `multi=`).
- `smcnr_se_2st_amp.orig.sp` — verbatim upstream HSPICE `.subckt` DUT (no `.end`, `xm…` devices).
- `smcnr_se_2st_amp.scs` — the same amplifier's Spectre rendering (cross-dialect equivalence).
- `tb_ac_smcnr_se_2st_amp.sp` — HSPICE testbench (`.option post`/`.measure`/`.lstb`/`.alter`,
  quoted expressions, trailing-`*` inline comments) for directive-classification tests.
