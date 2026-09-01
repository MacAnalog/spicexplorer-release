"""nevergrad's metamodel under numpy 2 — the crash that ends a run hours in (ledger E-052).

`nevergrad <= 1.0.12` (still the newest release) calls ``float()`` on the 1-element ndarray that
`model.predict(...)` returns inside `metamodel.learn_on_k_best`. numpy 1 warned; numpy 2 raises
``TypeError: only 0-dimensional arrays can be converted to Python scalars``. The guard around the
metamodel catches only `(OverflowError, MetaModelFailure)`, so the `TypeError` escapes and takes
the whole optimization down the first time the metamodel engages — `NGOpt` died at ~trial 250 of a
TCAS-2026 campaign run, i.e. after hours of SPICE.

`optimization.stochastic.nevergrad_compat` backports upstream `main`'s one-line fix
(``float(...)`` -> ``.item()``) at import of the platform's Nevergrad backend. This suite pins:

1. **The bug is real and this numpy rejects it** — the exact conversion nevergrad performs.
2. **The reported failure no longer happens** — `NGOpt` and `MetaModel` complete a budget large
   enough to enter the metamodel (they crash within a second without the patch).
3. **The backport is surgical** — the replacement function still resolves `MetaModelFailure`,
   `registry`, `np`, ... to the *original* module objects, so every `except MetaModelFailure`
   clause in nevergrad still catches; it is idempotent; and it leaves a nevergrad that does not
   carry the buggy expression completely alone.

No SPICE, no PDK — pure nevergrad on an analytic objective; the whole file runs in seconds.
"""
from __future__ import annotations

import inspect

import nevergrad as ng
import numpy as np
import pytest

# Importing the platform's Nevergrad backend is what installs the shim in a real run.
import spicexplorer.optimization.stochastic.nevergrad as sx_nevergrad  # noqa: F401
from nevergrad.optimization import metamodel, optimizerlib
from spicexplorer.optimization.stochastic.nevergrad_compat import (
    _BUGGY_EXPR,
    _PATCH_ATTR,
    apply_numpy2_metamodel_patch,
    is_numpy2_metamodel_patch_active,
)


def _sphere(x) -> float:
    """A trivial, cheap, perfectly learnable objective — the metamodel engages readily on it."""
    return float(np.sum(np.asarray(x, dtype=float) ** 2))


# =========================================================== 1. the mechanism
@pytest.mark.skipif(int(np.__version__.split(".")[0]) < 2,
                    reason="numpy 1 only warns on the ndarray->scalar conversion")
def test_numpy2_rejects_the_conversion_nevergrad_performs():
    """`float(<1-element ndarray>)` — the exact expression at metamodel.py:177 in 1.0.12."""
    with pytest.raises(TypeError, match="0-dimensional"):
        float(np.array([1.5]))


def test_the_shim_targets_a_bug_that_the_installed_nevergrad_actually_had():
    """Guard against patching a phantom: either the release still ships the buggy expression
    (and we replaced it) or it does not (and the shim is inert) — never a silent mismatch."""
    assert is_numpy2_metamodel_patch_active()


# =========================================================== 2. the reported failure
@pytest.mark.parametrize("name, budget, dimension", [
    # `MetaModel` forces the path immediately (archive >= (d(d-1)/2 + 2d + 1) entries).
    ("MetaModel", 60, 5),
    # `NGOpt` is the strategy the campaign ran; the wizard routes into the metamodel a few
    # hundred asks in. Both of these raised TypeError within a second before the backport.
    ("NGOpt", 300, 5),
    ("NGOpt", 300, 8),
])
def test_the_metamodel_path_survives_a_full_budget(name, budget, dimension):
    optimizer = ng.optimizers.registry[name](parametrization=dimension, budget=budget)
    recommendation = optimizer.minimize(_sphere)          # used to raise TypeError here
    value = np.asarray(recommendation.value, dtype=float)
    assert np.all(np.isfinite(value))


def test_the_metamodel_still_converges_and_is_not_merely_disabled():
    """A shim that turned the TypeError into a `MetaModelFailure` would also 'survive' — but it
    would silently disable the metamodel, so an NGOpt arm would measure an optimizer nevergrad
    does not ship. The quadratic surrogate nails a sphere; a fallback-only run does not get near."""
    optimizer = ng.optimizers.registry["MetaModel"](parametrization=3, budget=200)
    # Seeded: this is the one assertion in the file whose margin depends on the metamodel
    # engaging on a particular draw, and an unseeded run of it is a CI flake vector.
    optimizer.parametrization.random_state = np.random.RandomState(0)
    assert _sphere(optimizer.minimize(_sphere).value) < 1e-12


def test_a_metamodel_failure_is_still_raised_and_caught_inside_a_run():
    """A CONSTANT objective trips `learn_on_k_best`'s `max(y) - min(y) > 1e-20` guard on every
    call, so this run is nothing but the MetaModelFailure path. It must complete, not crash —
    which it only can if the replacement function raises the ORIGINAL `MetaModelFailure` class
    that the call sites' `except` clauses reference."""
    optimizer = ng.optimizers.registry["MetaModel"](parametrization=3, budget=60)
    optimizer.minimize(lambda x: 1.0)

    with pytest.raises(metamodel.MetaModelFailure):
        metamodel.learn_on_k_best(optimizer.archive, 10)


# =========================================================== 3. the backport is surgical
def test_the_replacement_runs_against_the_original_module_globals():
    """Compiling with fresh globals would mint a SECOND `MetaModelFailure` class, and every
    `except MetaModelFailure` in nevergrad would stop catching. Pinned by identity."""
    assert metamodel.learn_on_k_best.__globals__ is metamodel.__dict__
    assert metamodel.learn_on_k_best.__globals__["MetaModelFailure"] is metamodel.MetaModelFailure


def test_optimizerlib_is_rebound_too():
    """`optimizerlib` does `from .metamodel import learn_on_k_best`, so it holds its own name and
    would keep calling the buggy original — that is the module the NGOpt path goes through."""
    assert optimizerlib.learn_on_k_best is metamodel.learn_on_k_best


def test_the_patch_is_idempotent():
    """Applied at backend import; a second application must be a no-op, not a re-wrap."""
    before = metamodel.learn_on_k_best
    assert apply_numpy2_metamodel_patch() is False
    assert metamodel.learn_on_k_best is before
    assert getattr(metamodel.learn_on_k_best, _PATCH_ATTR, False) is True


def test_a_nevergrad_without_the_bug_is_left_alone(monkeypatch):
    """The day a fixed release lands, bumping the pin must disable the shim with no code change."""
    def already_fixed(archive, k, algorithm="quad", degree=2, shape=None, para=None):
        return np.zeros(1)

    monkeypatch.setattr(metamodel, "learn_on_k_best", already_fixed)
    assert _BUGGY_EXPR not in inspect.getsource(already_fixed)
    assert apply_numpy2_metamodel_patch() is False
    assert metamodel.learn_on_k_best is already_fixed


def test_the_shim_never_raises_when_the_source_is_unavailable(monkeypatch):
    """A zipped / stripped install has no source to rewrite. The shim must degrade to a logged
    no-op — a run that never reaches the metamodel must not be taken down by the shim itself."""
    def no_source(archive, k, algorithm="quad", degree=2, shape=None, para=None):
        return np.zeros(1)

    monkeypatch.setattr(metamodel, "learn_on_k_best", no_source)
    monkeypatch.setattr(inspect, "getsource",
                        lambda obj: (_ for _ in ()).throw(OSError("could not get source code")))
    assert apply_numpy2_metamodel_patch() is False
    assert is_numpy2_metamodel_patch_active() is False


# =========================================================== 4. wiring
def test_importing_the_platform_backend_installs_the_shim():
    """The shim has to ride the import every engine path already performs — the orchestrator, the
    API runner and the notebooks all reach Nevergrad through this module."""
    assert hasattr(sx_nevergrad, "apply_numpy2_metamodel_patch")
    assert is_numpy2_metamodel_patch_active()
