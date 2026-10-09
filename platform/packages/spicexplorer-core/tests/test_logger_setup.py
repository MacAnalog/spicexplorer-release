"""Logger setup (OPT-14): no ``./logs`` in the caller's CWD, no handler leak.

Both setup functions mutate process-global state (the ``spicexplorer``/``spicelib``/
``std_redirect`` loggers, and ``sys.stdout`` for the suppression variant), so every
test runs under :func:`isolated_logging`, which restores it and closes what the test
opened.
"""

import logging
import sys

import pytest
from spicexplorer_core.logging import logger_setup

_LOGGERS = ("spicexplorer", "std_redirect", "spicelib", "spicelib.SimRunner")


@pytest.fixture
def isolated_logging(monkeypatch):
    monkeypatch.setattr(sys, "stdout", sys.stdout)  # restored after the stdout proxy
    saved = {}
    for name in _LOGGERS:
        lg = logging.getLogger(name)
        saved[name] = (list(lg.handlers), lg.level, lg.propagate)
    yield
    for name, (handlers, level, propagate) in saved.items():
        lg = logging.getLogger(name)
        for h in lg.handlers:
            if h not in handlers:
                h.close()
        lg.handlers[:] = handlers
        lg.setLevel(level)
        lg.propagate = propagate


_SETUPS = pytest.mark.parametrize(
    "setup",
    [
        logger_setup.setup_loggers,
        logger_setup.setup_loggers_with_spicelib_suppression,
    ],
)


@_SETUPS
def test_default_log_dir_is_under_work_root_not_cwd(setup, isolated_logging, tmp_path, monkeypatch):
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    setup()
    assert not (cwd / "logs").exists()
    assert list((tmp_path / "wr" / "logs").glob("SpiceXplorer_*.log"))


@_SETUPS
@pytest.mark.parametrize("as_str", [False, True], ids=["path", "str"])
def test_explicit_parent_folder_is_still_honoured(
    setup, as_str, isolated_logging, tmp_path, monkeypatch
):
    # Callers pass a Path (the API) or a plain string (scripts); the old f-string
    # path accepted both. An explicit folder must not resolve/create WORK_ROOT either.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("WORK_ROOT", str(tmp_path / "wr"))
    run = tmp_path / "run"
    setup(out_logname="Run7", parent_folder=str(run) if as_str else run)
    assert list((run / "logs").glob("Run7_*.log"))
    assert not (tmp_path / "wr").exists()
    assert not (tmp_path / "logs").exists()


def test_spicelib_logging_reinit_leaks_no_handlers(isolated_logging, tmp_path):
    parent = logging.getLogger("spicelib")
    child = logging.getLogger("spicelib.SimRunner")
    first = logging.FileHandler(tmp_path / "first.log")
    second = logging.FileHandler(tmp_path / "second.log")
    try:
        logger_setup.setup_spicelib_logging(first)
        assert len(parent.handlers) == 2  # console + file, each once
        logger_setup.setup_spicelib_logging(second)
        assert len(parent.handlers) == 2
        for lg in (parent, child):
            assert first not in lg.handlers  # the earlier init's handler is gone
        child.info("probe-record")
        assert (tmp_path / "second.log").read_text().count("probe-record") == 1
        assert "probe-record" not in (tmp_path / "first.log").read_text()
    finally:
        first.close()
        second.close()


def test_spicelib_logging_reinit_detaches_handlers_left_on_children(isolated_logging, tmp_path):
    # The pre-fix init attached the parent's handlers to every ``spicelib.*`` child as
    # well, and a long-lived Python process still carries them: a re-init must take them off.
    parent = logging.getLogger("spicelib")
    child = logging.getLogger("spicelib.SimRunner")
    sibling = logging.getLogger("spicelibrary")  # shares the prefix, is not a child
    old = logging.FileHandler(tmp_path / "old.log")
    new = logging.FileHandler(tmp_path / "new.log")
    try:
        logger_setup.setup_spicelib_logging(old)
        leaked = list(parent.handlers)
        for h in leaked:  # the state the pre-fix init left behind
            child.addHandler(h)
        sibling.setLevel(logging.WARNING)
        sibling.addHandler(old)

        logger_setup.setup_spicelib_logging(new)

        assert not set(leaked) & set(child.handlers)
        assert sibling.level == logging.WARNING and sibling.handlers == [old]  # untouched
        child.info("probe-record")
        assert (tmp_path / "new.log").read_text().count("probe-record") == 1
        assert "probe-record" not in (tmp_path / "old.log").read_text()
    finally:
        for lg in (child, sibling):
            for h in (old, new):
                lg.removeHandler(h)
        sibling.setLevel(logging.NOTSET)
        old.close()
        new.close()
