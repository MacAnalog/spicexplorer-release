"""keep_raw_artifacts: the per-trial raw cleanup switch (viewer open-by-run-id support).

`Spice_Base_Optimizer.clean_up(delete_raw_only=True)` runs at the end of EVERY
evaluate(); with `keep_raw_artifacts` set it must become a no-op so the run dir keeps
its .raw waveforms — and a full cleanup (delete_raw_only=False) must stay unaffected
by the flag (end-of-run housekeeping is not retention's concern).
"""

from __future__ import annotations

from spicexplorer.optimization.base import Spice_Base_Optimizer


class _RecordingWrapper:
    def __init__(self):
        self.calls: list[dict] = []

    def clean_up(self, **kwargs):
        self.calls.append(kwargs)


class _ConcreteOpt(Spice_Base_Optimizer):
    """clean_up under test needs no optimizer behavior — satisfy the ABC with no-ops."""

    def _create_optimizer_obj(self): ...
    def compute_fitness(self, performance_array): ...
    def evaluate(self, *a, **k): ...
    def optimization_step(self): ...
    def parameterize(self): ...


def _stub(keep: bool) -> tuple[Spice_Base_Optimizer, _RecordingWrapper]:
    opt = object.__new__(_ConcreteOpt)  # skip __init__: clean_up needs only these two attrs
    wrapper = _RecordingWrapper()
    opt.spicelib_wrappers = {"tb": wrapper}  # pyright: ignore[reportAttributeAccessIssue] — test double
    opt.keep_raw_artifacts = keep
    return opt, wrapper


def test_default_trial_cleanup_deletes_raws():
    opt, wrapper = _stub(keep=False)
    opt.clean_up(delete_raw_only=True)
    assert wrapper.calls == [{"keep_netlist": True, "keep_logs": True, "keep_raw": False}]


def test_keep_raw_skips_trial_cleanup():
    opt, wrapper = _stub(keep=True)
    opt.clean_up(delete_raw_only=True)
    assert wrapper.calls == []


def test_keep_raw_does_not_block_full_cleanup():
    opt, wrapper = _stub(keep=True)
    opt.clean_up(delete_raw_only=False)
    assert wrapper.calls == [{"delete_directories": True}]


def test_wrapper_without_cleanup_tolerated():
    opt, _ = _stub(keep=False)
    opt.spicelib_wrappers = {"tb": object()}  # pyright: ignore[reportAttributeAccessIssue] — no-cleanup backend
    opt.clean_up(delete_raw_only=True)  # must not raise
