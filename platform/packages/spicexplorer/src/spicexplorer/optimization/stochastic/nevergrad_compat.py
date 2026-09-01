"""Compatibility shims for the pinned `nevergrad` release under numpy 2.

Nevergrad's metamodel helper (`nevergrad.optimization.metamodel.learn_on_k_best`) calls
``float()`` on the 1-element ndarray that `model.predict(...)` returns::

    def loss_function_sm(x):
        return float(model.predict(trans(np.asarray(x, dtype=X[0].dtype).flatten()[None, :])))

Under numpy 1 that was a `DeprecationWarning`; numpy >= 2 raises
``TypeError: only 0-dimensional arrays can be converted to Python scalars``. The call sites that
guard the metamodel (`optimizerlib.py` `_MetaModel._internal_ask_candidate`) catch only
`(OverflowError, MetaModelFailure)`, so the `TypeError` escapes and **kills the whole run** the
first time the metamodel engages — for `NGOpt` that is a few hundred trials in, i.e. after hours
of SPICE. Observed in the TCAS-2026 campaign (ledger E-052): `NGOpt` died at ~trial 250 in
`nevergrad/optimization/metamodel.py:177` with `nevergrad==1.0.12` + numpy 2.

Upstream has fixed it on `main` (`float(...)` -> `.item()`), but **no release carries the fix**:
1.0.12 (2025-04-23) is still the newest sdist/wheel on PyPI, so there is no version floor to
raise. This module therefore backports the upstream one-line change at import time:
`learn_on_k_best`'s own source is recompiled against the *original* module globals with that
single expression replaced, so the resulting function is byte-for-byte upstream `main` and every
name it closes over (`MetaModelFailure`, `registry`, `np`, ...) still resolves to the identical
objects the rest of nevergrad holds — a fresh-globals `exec` would mint a *second*
`MetaModelFailure` class and silently break every `except MetaModelFailure` clause.

Why not simply translate the `TypeError` into `MetaModelFailure` (which every call site already
catches)? That keeps runs alive but permanently disables the metamodel from the first engagement
onwards, so an `NGOpt` arm would measure an optimizer nevergrad does not ship. The point of the
shim is to run the algorithm as authored, not a degraded variant of it.

The patch is deliberately timid: it is a no-op (and never raises) when the installed nevergrad
does not carry the exact buggy expression — so the day a fixed release lands, upgrading the pin
disables this shim without a code change.

Upstream reference: https://github.com/facebookresearch/nevergrad — `nevergrad/optimization/
metamodel.py`, `loss_function_sm` on `main` vs. the released 1.0.12.
"""
from __future__ import annotations

import inspect
import logging
from typing import Any, Dict

logger = logging.getLogger("spicexplorer.optimization.stochastic.nevergrad_compat")

#: The exact expression nevergrad <= 1.0.12 ships inside `learn_on_k_best.loss_function_sm`.
#: Matched verbatim (whitespace included) so a reformatted / already-fixed release is left alone.
_BUGGY_EXPR = "return float(model.predict(trans(np.asarray(x, dtype=X[0].dtype).flatten()[None, :])))"

#: Upstream `main`'s replacement, re-indented to sit where `_BUGGY_EXPR` was (12 spaces in).
_FIXED_EXPR = (
    "x = np.asarray(x, dtype=X[0].dtype).flatten()[None, :]\n"
    "            return model.predict(trans(x)).item()"
)

#: Marker set on the replacement function so the patch is idempotent across re-imports.
_PATCH_ATTR = "_spicexplorer_numpy2_backport"


def apply_numpy2_metamodel_patch() -> bool:
    """Backport upstream's numpy-2 fix onto `nevergrad`'s `learn_on_k_best`.

    Returns True when this call installed the patch, False when it was unnecessary (already
    applied, nevergrad missing, source unavailable, or a release that no longer carries the bug).
    Never raises: a run that never reaches the metamodel must not be taken down by the shim.
    """
    try:
        from nevergrad.optimization import metamodel, optimizerlib

        original = getattr(metamodel, "learn_on_k_best", None)
        if original is None:
            logger.debug("nevergrad has no `metamodel.learn_on_k_best`; nothing to patch.")
            return False
        if getattr(original, _PATCH_ATTR, False):
            return False  # idempotent: already backported in this interpreter

        try:
            source = inspect.getsource(original)
        except (OSError, TypeError):  # zipped install / C-accelerated / stripped source
            logger.debug("nevergrad's `learn_on_k_best` source is unavailable; skipping the "
                         "numpy-2 backport (NGOpt may die when the metamodel engages).")
            return False

        occurrences = source.count(_BUGGY_EXPR)
        if occurrences != 1:
            logger.debug(
                f"nevergrad's `learn_on_k_best` does not carry the numpy-2 bug verbatim "
                f"({occurrences} match(es)); leaving it untouched.")
            return False

        patched_source = source.replace(_BUGGY_EXPR, _FIXED_EXPR, 1)
        # Compile against the ORIGINAL module globals so `MetaModelFailure`, `registry`, `np`,
        # `tp`, `utils`, ... are the very objects the rest of nevergrad already holds. The `def`
        # binds into `namespace` (the exec locals), so `metamodel.learn_on_k_best` only moves
        # where we move it, below.
        namespace: Dict[str, Any] = {}
        code = compile(patched_source, f"<spicexplorer numpy-2 backport of {metamodel.__file__}>", "exec")
        exec(code, metamodel.__dict__, namespace)  # noqa: S102 - upstream source + one expression
        patched = namespace["learn_on_k_best"]
        setattr(patched, _PATCH_ATTR, True)

        metamodel.learn_on_k_best = patched
        # `optimizerlib` binds the name at import (`from .metamodel import learn_on_k_best`), so
        # it holds its own reference and must be rebound too. `differentialevolution` calls it
        # through the module attribute and therefore follows automatically.
        if getattr(optimizerlib, "learn_on_k_best", None) is original:
            optimizerlib.learn_on_k_best = patched

        logger.info(
            "patched nevergrad's `learn_on_k_best` for numpy 2 (backport of the upstream "
            "`float(...)` -> `.item()` fix; see nevergrad_compat.__doc__ / ledger E-052).")
        return True
    except Exception as exc:  # pragma: no cover - defensive: a shim must never break import
        logger.warning(f"could not apply the nevergrad numpy-2 metamodel backport: "
                       f"{exc.__class__.__name__}: {exc}")
        return False


def is_numpy2_metamodel_patch_active() -> bool:
    """True when `nevergrad`'s metamodel entry point is numpy-2 safe in this interpreter.

    Either because this module backported the fix, or because the installed nevergrad no longer
    carries the buggy expression (a future release) — both are "safe to run NGOpt".
    """
    try:
        from nevergrad.optimization import metamodel

        fn = getattr(metamodel, "learn_on_k_best", None)
        if fn is None:
            return False
        if getattr(fn, _PATCH_ATTR, False):
            return True
        try:
            return _BUGGY_EXPR not in inspect.getsource(fn)
        except (OSError, TypeError):
            return False
    except Exception:  # pragma: no cover - same defensiveness as above
        return False
