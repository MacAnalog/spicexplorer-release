"""Base_Optimizer.save_checkpoint / load_checkpoint must round-trip a real run.

save_checkpoint used to stringify each entry's ``log_file`` (a Dict[str, Path]) to
a repr AND mutate the live entry; load_checkpoint then couldn't feed that string
back through dacite (WrongTypeError), so the API had to route around the library's
own primitive. Now ``log_file`` serializes as a proper Dict[str, str] and load
tolerates the legacy string form (dropping it to None).
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from spicexplorer.core.domains import (
    OptimizationLog,
    OptimizationLogEntry,
    OptimizationPoint,
)
from spicexplorer.optimization.base import Base_Optimizer


class _StubOptimizer(Base_Optimizer):
    """Concrete Base_Optimizer with no-op abstracts — exercises only the
    checkpoint save/load code, with no ngspice/optimizer backend."""

    def _create_optimizer_obj(self):
        return True

    def parameterize(self):
        return None

    def optimization_step(self):
        return None, 0.0, {}

    def evaluate(self, *a, **k):
        return 0.0, {}

    def compute_fitness(self, *a, **k):
        return 0.0, {}

    def plot_solution(self, *a, **k):
        return None


def _stub_setup():
    return SimpleNamespace(name="proj", optimizer_config=SimpleNamespace(name="algo", budget=4))


def _entry(score, log_file):
    return OptimizationLogEntry(
        point=OptimizationPoint(params={"w": 1e-6}, score=score),
        fit_summary={"gain": {"curr_val": 55.0, "score": -1.0}},
        log_file=log_file,
    )


def test_save_checkpoint_serializes_log_file_as_dict_not_repr(tmp_path):
    opt = _StubOptimizer(setup_obj=_stub_setup())
    opt.optimization_log = OptimizationLog([_entry(0.5, {"ac": Path("/runs/1/ac.log")})])
    opt.save_checkpoint(name=tmp_path / "ck")

    (written,) = list(tmp_path.glob("ck*.json"))
    raw = json.loads(written.read_text())
    lf = raw["optimization_log"][0]["log_file"]
    assert lf == {"ac": "/runs/1/ac.log"}  # a real dict, NOT "{'ac': PosixPath(...)}"


def test_save_checkpoint_does_not_mutate_live_entry(tmp_path):
    e = _entry(0.5, {"ac": Path("/runs/1/ac.log")})
    opt = _StubOptimizer(setup_obj=_stub_setup())
    opt.optimization_log = OptimizationLog([e])
    opt.save_checkpoint(name=tmp_path / "ck")
    assert e.log_file == {"ac": Path("/runs/1/ac.log")}  # untouched (old code clobbered it to str)


def test_load_checkpoint_roundtrips_new_dict_form(tmp_path):
    opt = _StubOptimizer(setup_obj=_stub_setup())
    opt.optimization_log = OptimizationLog([_entry(0.5, {"ac": Path("/x/ac.log")})])
    opt.save_checkpoint(name=tmp_path / "ck")

    ck = next(tmp_path.glob("ck*.json"))
    reloaded = _StubOptimizer.load_checkpoint(setup_obj=_stub_setup(), path_to_checkpoint=ck)
    assert len(reloaded.optimization_log) == 1
    assert reloaded.optimization_log[0].get_score() == 0.5
    assert reloaded.optimization_log[0].log_file == {"ac": "/x/ac.log"}


def test_load_checkpoint_tolerates_legacy_stringified_log_file(tmp_path):
    """A pre-fix checkpoint stored log_file as the repr of a dict containing
    PosixPath(...) — not a literal. Load must not crash; it drops it to None."""
    ck = tmp_path / "legacy_2020-01-01_00-00-00.json"
    ck.write_text(json.dumps({
        "schema_version": 999,  # also exercises the version-mismatch warning path
        "optimization_log": [{
            "point": {"params": {"w": 1e-6}, "score": 0.5, "metadata": {}},
            "fit_summary": {"gain": {"curr_val": 55.0, "score": -1.0}},
            "log_file": "{'ac': PosixPath('/x/ac.log')}",
        }],
    }))
    reloaded = _StubOptimizer.load_checkpoint(setup_obj=_stub_setup(), path_to_checkpoint=ck)
    assert len(reloaded.optimization_log) == 1
    assert reloaded.optimization_log[0].log_file is None  # unparseable → dropped, no crash
    assert reloaded.optimization_log[0].get_score() == 0.5
