"""The PAM-4 HBT drawing's layout lane imports without the retired platform prototype (B-ADB-2).

``drawings/pam4-driver-2-bit-dac-HBT/ported-netlists/layout/signoff.py`` used to load the
platform's ``examples/layout/ihp-sg13g2/5t_ota/signoff.py`` by a relative path when it was
imported. The platform retired that directory (RET-LAYOUT-PROTO), so importing ``signoff.py``,
and through it ``optimize_layout.py`` and notebook 02, raised FileNotFoundError. It now calls the
``spicexplorer_signoff`` package. Outside a platform checkout the old relative path resolves to
no file, so importing the module here reproduces the retired-directory case.

The two runners keep the ``(passed, text)`` pair their callers unpack. A GDS that does not exist
fails both, with or without KLayout and a PDK on the host, so the check below needs neither.
It does need the ``spicexplorer_signoff`` package, which analog-db declares only as its optional
``layout`` extra, so the module skips when that package is not installed.
"""

from __future__ import annotations

import importlib.util

import pytest

from spicexplorer_analog_db import paths

pytest.importorskip(
    "spicexplorer_signoff", reason="the optional `layout` extra (spicexplorer-signoff) is absent"
)

LAYOUT = paths.db_root() / "drawings" / "pam4-driver-2-bit-dac-HBT" / "ported-netlists" / "layout"


def _load_signoff():
    spec = importlib.util.spec_from_file_location("pam4_hbt_layout_signoff", LAYOUT / "signoff.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_layout_signoff_module_imports():
    mod = _load_signoff()
    assert callable(mod.run_drc) and callable(mod.run_lvs)


def test_run_drc_and_run_lvs_return_the_passed_text_pair(tmp_path):
    mod = _load_signoff()
    gds = str(tmp_path / "absent.gds")
    passed, text = mod.run_drc(gds, "pam4drv_lsb_lay", str(tmp_path / "drc"))
    assert passed is False and isinstance(text, str) and text
    passed, text = mod.run_lvs(
        gds, str(tmp_path / "absent.spice"), "pam4drv_lsb_lay", str(tmp_path / "lvs")
    )
    assert passed is False and isinstance(text, str) and text
