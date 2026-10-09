"""Regression tests for the ``Base_Optimizer`` run/checkpoint defects fixed in WP-01.

Library-level only — a stub ``optimization_step`` stands in for the backend, so no ngspice / PDK:
- OPT-01  an exception inside a trial (not only Ctrl-C) still writes the unsaved trials to a
          ``..._CRASH`` checkpoint, then re-raises the ORIGINAL error.
- OPT-06  the free-text project ``name`` is made path-safe before it becomes a path component
          (a ``/`` nested directories, a ``..`` could leave ``auto_save/``, a ``.`` truncated the stem).
- OPT-13  ``get_best_params(verbose=True)`` logs the (already physical) params with a real
          placeholder and does not denormalize them a second time; ``compute_reward`` has no dead
          ``goal`` parameter.
"""

from __future__ import annotations

import inspect
import json
import logging
import random
import re
import string
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from _spicexplorer_fixtures import EXAMPLE_YAML
from spicexplorer.core.domains import OptimizationLogEntry, OptimizationPoint, Project_Setup
from spicexplorer.core.utils import compute_reward
from spicexplorer.optimization.base import Base_Optimizer, _path_safe

pytestmark = pytest.mark.skipif(not EXAMPLE_YAML.exists(), reason="cascode example missing")


class _StubOpt(Base_Optimizer):
    """Logs one entry per step; raises ``raise_exc`` on step index ``raise_at`` (0-based)."""

    raise_at: int | None = None
    raise_exc: BaseException = RuntimeError("simulated backend crash")

    def _create_optimizer_obj(self) -> bool:
        self.optimizer = object()
        return True

    def parameterize(self) -> Any:
        return {}

    def evaluate(self, parameterization):
        return np.float64(0.0), {}

    def compute_fitness(self, performance_array):
        return np.float64(0.0), {}

    def optimization_step(self):
        step = getattr(self, "_step", 0)
        self._step = step + 1
        if self.raise_at is not None and step == self.raise_at:
            raise self.raise_exc
        score = np.float64(float(step))
        params = {"X_DUT_M1M2_W": float(step)}
        self.optimization_log.append(
            OptimizationLogEntry(
                point=OptimizationPoint(params=params, score=score), fit_summary={}
            )
        )
        return params, score, {}

    def plot_solution(self, parameterization, **kwargs):
        return None


def _opt(tmp_path: Path, budget: int = 10, **kw) -> _StubOpt:
    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    proj.optimizer_config.budget = budget
    opt = _StubOpt(proj, output_root=tmp_path / "ck", **kw)
    return opt


def _entry(w: float) -> OptimizationLogEntry:
    return OptimizationLogEntry(
        point=OptimizationPoint(params={"X_DUT_M1M2_W": w}, score=np.float64(w)), fit_summary={}
    )


def _written(ck: Path) -> dict[str, list[float]]:
    """Every checkpoint under ``ck`` (recursively): file name -> its logged ``X_DUT_M1M2_W`` values."""
    if not ck.exists():
        return {}
    return {
        p.name: [
            e["point"]["params"]["X_DUT_M1M2_W"]
            for e in json.loads(p.read_text())["optimization_log"]
        ]
        for p in sorted(ck.rglob("*.json"))
    }


# ---------- OPT-01: a crashed run keeps its trials ----------


def test_trial_exception_writes_crash_checkpoint_and_reraises(tmp_path):
    """budget 10, the 5th trial raises: the 4 completed trials must reach disk (autosave runs
    every 2500 trials, so before the fix a shorter run lost every trial), and the ORIGINAL error
    still propagates to the caller."""
    opt = _opt(tmp_path)
    opt.raise_at = 4
    with pytest.raises(RuntimeError, match="simulated backend crash") as excinfo:
        opt.optimize()
    assert excinfo.value is opt.raise_exc  # the ORIGINAL object, not a wrapper
    crash = sorted((tmp_path / "ck").glob("*_CRASH_*.json"))
    assert len(crash) == 1, f"no crash checkpoint written: {list((tmp_path / 'ck').glob('*'))}"
    data = json.loads(crash[0].read_text())
    assert len(data["optimization_log"]) == 4
    assert "trial5_CRASH" in crash[0].name  # names the trial that raised
    assert not list((tmp_path / "ck").glob("*_FINAL_*"))  # a crash is not a finished run


def test_crash_checkpoint_failure_never_masks_the_original_error(tmp_path, monkeypatch, caplog):
    """If writing the crash checkpoint itself fails, the caller still sees the trial's error,
    not the checkpoint's — and the failed write is logged, not silently dropped."""
    opt = _opt(tmp_path)
    opt.raise_at = 2

    def _broken_save(name):
        raise OSError("disk full")

    monkeypatch.setattr(opt, "save_checkpoint", _broken_save)
    with caplog.at_level(logging.ERROR, logger="spicexplorer.optimization.base"):
        with pytest.raises(RuntimeError, match="simulated backend crash") as excinfo:
            opt.optimize()
    assert excinfo.value is opt.raise_exc
    assert "could not write the crash checkpoint" in caplog.text
    assert "disk full" in caplog.text  # logger.exception carries the save's own traceback


def test_crash_on_the_first_trial_writes_no_empty_checkpoint(tmp_path):
    """Nothing completed → nothing to save: the crash path shares the ``_FINAL`` gate (log not
    empty), so a run that dies on trial 1 leaves no empty ``_CRASH`` file — and still re-raises."""
    opt = _opt(tmp_path)
    opt.raise_at = 0
    with pytest.raises(RuntimeError, match="simulated backend crash"):
        opt.optimize()
    assert _written(tmp_path / "ck") == {}


def test_crash_with_autosave_disabled_writes_nothing_but_still_reraises(tmp_path):
    """``disable_autosave`` is the caller's opt-out of every checkpoint write (the one-shot API
    routes use it): a crash must honour it — no file — and still propagate the error."""
    opt = _opt(tmp_path)
    opt.disable_autosave = True
    opt.raise_at = 4
    with pytest.raises(RuntimeError, match="simulated backend crash"):
        opt.optimize()
    assert _written(tmp_path / "ck") == {}


def test_crash_after_an_autosave_saves_only_the_unsaved_tail(tmp_path):
    """The autosave already wrote trials 1-3 and emptied the in-memory log, so the ``_CRASH``
    checkpoint holds only trial 4 (the unsaved tail) — together the two files hold every
    completed trial, none twice."""
    opt = _opt(tmp_path)
    opt.autosave_checkpoint_freqeucny = 3
    opt.raise_at = 4
    with pytest.raises(RuntimeError):
        opt.optimize()
    written = _written(tmp_path / "ck")
    assert len(written) == 2, written
    autosave = next(v for k, v in written.items() if "_trial3_" in k)
    crash = next(v for k, v in written.items() if "_trial5_CRASH_" in k)
    assert autosave == [0.0, 1.0, 2.0] and crash == [3.0]


def test_crash_right_after_an_autosave_writes_no_crash_file(tmp_path):
    """The 7th trial raises just after the trial-6 autosave emptied the log: every completed trial
    is already on disk, so no (empty) ``_CRASH`` file is added."""
    opt = _opt(tmp_path)
    opt.autosave_checkpoint_freqeucny = 3
    opt.raise_at = 6
    with pytest.raises(RuntimeError):
        opt.optimize()
    written = _written(tmp_path / "ck")
    assert sorted(written.values()) == [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]
    assert not any("CRASH" in k for k in written), written


def test_crash_checkpoint_loads_back_through_load_checkpoint(tmp_path):
    """ "Never lose trials" means the ``_CRASH`` file is an ordinary, resumable checkpoint."""
    opt = _opt(tmp_path)
    opt.raise_at = 4
    with pytest.raises(RuntimeError):
        opt.optimize()
    (crash,) = (tmp_path / "ck").glob("*_CRASH_*.json")
    resumed = _StubOpt.load_checkpoint(opt.setup_obj, crash, output_root=tmp_path / "resume")
    assert [e.get_params()["X_DUT_M1M2_W"] for e in resumed.optimization_log] == [
        0.0,
        1.0,
        2.0,
        3.0,
    ]
    assert [float(e.get_score()) for e in resumed.optimization_log] == [0.0, 1.0, 2.0, 3.0]


def test_a_non_exception_base_exception_is_checkpointed_and_propagated(tmp_path):
    """``SystemExit`` is a BaseException, not an Exception: the crash path catches BaseException,
    so a ``sys.exit`` inside a trial also keeps the completed trials, and the exit itself still
    reaches the caller unchanged."""
    opt = _opt(tmp_path)
    opt.raise_at = 4
    opt.raise_exc = SystemExit(3)
    with pytest.raises(SystemExit) as excinfo:
        opt.optimize()
    assert excinfo.value.code == 3
    written = _written(tmp_path / "ck")
    assert list(written.values()) == [[0.0, 1.0, 2.0, 3.0]]
    assert "_trial5_CRASH_" in next(iter(written))


def test_crash_still_runs_the_teardown_hooks(tmp_path):
    """The crash path re-raises THROUGH the ``finally`` that releases the OCEAN / measure / derived
    contexts, so a crashed run still frees its license token and sessions."""
    closed: list[str] = []

    class _WithHooks(_StubOpt):
        def _close_ocean_ctx(self):
            closed.append("ocean")

        def _close_measure_ctx(self):
            closed.append("measure")

        def _close_derived_ctx(self):
            closed.append("derived")

    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    proj.optimizer_config.budget = 10
    opt = _WithHooks(proj, output_root=tmp_path / "ck")
    opt.raise_at = 2
    with pytest.raises(RuntimeError):
        opt.optimize()
    assert closed == ["ocean", "measure", "derived"]
    assert len(list((tmp_path / "ck").glob("*_CRASH_*.json"))) == 1


def test_an_error_before_the_first_trial_is_not_masked_by_an_unbound_trial(tmp_path):
    """A malformed budget (an un-coerced ``"10"``) raises inside the ``try`` BEFORE the loop binds
    ``trial``. The crash path must re-raise THAT TypeError — not an ``UnboundLocalError`` from
    naming the checkpoint — and still keep the history the run was resumed with (``trial0``)."""
    opt = _opt(tmp_path)
    opt.optimization_log.append(_entry(7.0))
    opt.optimizer_config.budget = "10"  # type: ignore[assignment]  (the malformed input under test)
    with pytest.raises(TypeError):
        opt.optimize(keep_history=True)
    written = _written(tmp_path / "ck")
    assert list(written.values()) == [[7.0]]
    assert "_trial0_CRASH_" in next(iter(written))


def test_zero_budget_with_retained_history_writes_the_final_checkpoint(tmp_path):
    """``budget=0`` never enters the loop, so ``trial`` used to be unbound when the ``_FINAL``
    save named its file: a resumed run with retained history must still end with it on disk."""
    opt = _opt(tmp_path, budget=0)
    opt.optimization_log.append(_entry(7.0))
    log = opt.optimize(keep_history=True)
    assert log is not None and len(log) == 1
    written = _written(tmp_path / "ck")
    assert list(written.values()) == [[7.0]]
    assert "_trial0_FINAL_" in next(iter(written))


def test_keyboard_interrupt_still_ends_the_run_with_a_final_checkpoint(tmp_path):
    """Ctrl-C behaves as it always did: the run returns normally and writes ``_FINAL``
    (not ``_CRASH``) — the crash path is for every OTHER exception."""
    opt = _opt(tmp_path)
    opt.raise_at = 3
    opt.raise_exc = KeyboardInterrupt()
    log = opt.optimize()
    assert log is not None and len(log) == 3
    names = [p.name for p in (tmp_path / "ck").glob("*.json")]
    assert len(names) == 1 and "_FINAL_" in names[0], names


# ---------- OPT-06: the project name is path-safe ----------


@pytest.mark.parametrize(
    ("raw", "safe"),
    [
        (
            "amp_029 baseline (gain/ugf/pm)",
            "amp_029_baseline_gain_ugf_pm",
        ),  # the shipped Ax demo name
        ("../../escape", "escape"),
        ("ota v1.2", "ota_v1_2"),
        ("a\\b", "a_b"),  # the Windows separator too
        ("_draft_", "draft"),  # leading / trailing '_' trimmed
        ("µA bias", "A_bias"),  # non-ASCII is not in the allowed set
        ("..", ""),  # all-unsafe collapses to empty (the label still has its '_<algo>')
        ("", ""),
        (42, "42"),  # the signature takes `object`: non-str names are str()-ed
        (None, "None"),
        # Already-safe names are UNCHANGED, so existing runs keep their checkpoint names.
        ("CASCODE-OTA", "CASCODE-OTA"),
        ("LogBFGSCMAPlus", "LogBFGSCMAPlus"),
        ("amp_029-v2", "amp_029-v2"),
    ],
)
def test_path_safe_table(raw, safe):
    assert _path_safe(raw) == safe
    assert _path_safe(_path_safe(raw)) == _path_safe(raw)  # a second pass changes nothing


def test_path_safe_output_is_always_one_dot_free_component():
    """Property over seeded random printable names: the result only ever holds ``[A-Za-z0-9_-]``,
    never starts/ends with ``_``, and is a fixed point of ``_path_safe``."""
    rng = random.Random(0)
    alphabet = string.printable + "µé·/\\.."
    for _ in range(500):
        raw = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 24)))
        safe = _path_safe(raw)
        assert re.fullmatch(r"[A-Za-z0-9_-]*", safe), (raw, safe)
        assert not safe.startswith("_") and not safe.endswith("_"), (raw, safe)
        assert _path_safe(safe) == safe
        assert Path(safe or "x").name == (safe or "x")  # never more than one component


def test_safe_names_keep_their_historical_checkpoint_names(tmp_path):
    """Back-compat: for a name made only of ``[A-Za-z0-9_-]`` (the shipped examples) the checkpoint
    path is byte-for-byte what it was before the fix."""
    opt = _opt(tmp_path)
    assert opt.setup_obj.name == "CASCODE-OTA"
    assert opt.get_auto_save_name(append_txt="trial7_FINAL") == (
        tmp_path / "ck" / f"CASCODE-OTA_{opt.setup_obj.optimizer_config.name}_10_trial7_FINAL"
    )


def test_autosave_name_with_slash_stays_one_path_component(tmp_path):
    """The shipped Ax demo name ``amp_029 baseline (gain/ugf/pm)`` split at every ``/`` into
    nested directories under the checkpoint dir."""
    opt = _opt(tmp_path)
    opt.setup_obj.name = "amp_029 baseline (gain/ugf/pm)"
    target = opt.get_auto_save_name(append_txt="trial1")
    assert target.parent == tmp_path / "ck"
    opt.optimization_log.append(
        OptimizationLogEntry(
            point=OptimizationPoint(params={"X_DUT_M1M2_W": 1.0}, score=np.float64(1.0)),
            fit_summary={},
        )
    )
    opt.save_checkpoint(name=target)
    written = [p for p in (tmp_path / "ck").rglob("*") if p.is_file()]
    assert len(written) == 1 and written[0].parent == tmp_path / "ck", written


def test_unsafe_algorithm_name_is_made_path_safe_too(tmp_path, monkeypatch):
    """The algorithm half of the label is free text as well (``optimizer_config.name``): both the
    checkpoint name and the default autosave dir sanitize it through the same helper."""
    opt = _opt(tmp_path)
    opt.setup_obj.optimizer_config.name = "cma/es v2.0"
    target = opt.get_auto_save_name(append_txt="trial1")
    assert target.parent == tmp_path / "ck"
    assert target.name == "CASCODE-OTA_cma_es_v2_0_10_trial1"

    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    proj.optimizer_config.name = "../../up"
    dflt = _StubOpt(proj)
    assert dflt.autosave_checkpoint_dir.parent == (tmp_path / "wr" / "auto_save").resolve()
    assert dflt.autosave_checkpoint_dir.name == f"CASCODE-OTA_up_{dflt._TIMESTAMP}"


def test_default_autosave_dir_cannot_escape_auto_save(tmp_path, monkeypatch):
    """With no ``output_root`` the name becomes ``WORK_ROOT/auto_save/<name>_...``; a ``..`` in
    it must not climb out of ``auto_save/``."""
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    proj = Project_Setup.from_yaml(EXAMPLE_YAML)
    proj.name = "../../escape"
    opt = _StubOpt(proj)
    auto_save = (tmp_path / "wr" / "auto_save").resolve()
    assert opt.autosave_checkpoint_dir.parent == auto_save
    assert auto_save in opt.autosave_checkpoint_dir.resolve().parents
    assert opt.autosave_checkpoint_dir.name == (
        f"escape_{proj.optimizer_config.name}_{opt._TIMESTAMP}"
    )


def test_dotted_name_keeps_the_trial_label_in_the_checkpoint_file(tmp_path):
    """``save_checkpoint`` uses ``with_suffix('.json')``, so a ``.`` in the name cut the stem at
    that dot and dropped the ``_<opt>_<budget>_trialN`` label the API resolves checkpoints by."""
    opt = _opt(tmp_path)
    opt.setup_obj.name = "ota v1.2"
    opt.optimization_log.append(
        OptimizationLogEntry(
            point=OptimizationPoint(params={"X_DUT_M1M2_W": 1.0}, score=np.float64(1.0)),
            fit_summary={},
        )
    )
    opt.save_checkpoint(name=opt.get_auto_save_name(append_txt="trial1_FINAL"))
    written = list((tmp_path / "ck").glob("*.json"))
    assert len(written) == 1 and "_trial1_FINAL_" in written[0].name, written


def test_crash_checkpoint_of_an_unsafe_name_lands_in_the_checkpoint_dir(tmp_path):
    """End to end: the crash path names its file through the same sanitized label."""
    opt = _opt(tmp_path)
    opt.setup_obj.name = "amp_029 baseline (gain/ugf/pm)"
    opt.raise_at = 2
    with pytest.raises(RuntimeError):
        opt.optimize()
    files = [p for p in (tmp_path / "ck").rglob("*") if p.is_file()]
    assert len(files) == 1 and files[0].parent == tmp_path / "ck", files
    assert files[0].name.startswith("amp_029_baseline_gain_ugf_pm_")
    assert "_trial3_CRASH_" in files[0].name


# ---------- OPT-13: get_best_params(verbose) + compute_reward's dead `goal` ----------


def test_get_best_params_verbose_logs_the_physical_params(tmp_path, caplog, monkeypatch):
    """The log entries hold PHYSICAL params (``evaluate`` records the denormalized vector), so
    verbose mode must print them as-is — the old code denormalized them again (wrong values)
    and passed the dict with no ``%s`` placeholder (it never reached the log)."""
    opt = _opt(tmp_path, budget=3)
    opt.disable_autosave = True
    opt.optimize()

    def _no_second_denorm(parameterization):
        raise AssertionError("get_best_params must not denormalize already-physical params")

    monkeypatch.setattr(opt, "denormalize_params", _no_second_denorm)
    with caplog.at_level(logging.INFO, logger="spicexplorer.optimization.base"):
        best = opt.get_best_params(verbose=True)
    assert best is not None
    params, score, _meta = best
    assert params == {"X_DUT_M1M2_W": 2.0} and score == 2.0
    assert "'X_DUT_M1M2_W': 2.0" in caplog.text


def test_get_best_params_quiet_mode_logs_only_the_score(tmp_path, caplog):
    """``verbose=False`` (the default) returns the same best entry and keeps the params out of the
    log; only the score line is emitted."""
    opt = _opt(tmp_path, budget=3)
    opt.disable_autosave = True
    opt.optimize()
    with caplog.at_level(logging.INFO, logger="spicexplorer.optimization.base"):
        best = opt.get_best_params()
    assert best is not None and best[0] == {"X_DUT_M1M2_W": 2.0}
    assert "Optimized x" not in caplog.text
    assert "best score: 2.0" in caplog.text


def test_compute_reward_has_no_dead_goal_parameter():
    """``goal`` was declared (defaulting to EXCEED) but never read — a caller passing it got no
    effect and no error."""
    assert "goal" not in inspect.signature(compute_reward).parameters
    assert list(inspect.signature(compute_reward).parameters) == [
        "curr_val",
        "target_val",
        "reward_type",
        "normalizing_coeff",
    ]
