"""`spice_engine.psfascii` — the one psfascii contract the optimizer's adapter and the viewer share.

Pure-text checks need nothing; the wave reader needs `psf_utils`, which the wave-reading tools
declare (not core), so those tests skip where it is absent.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from spicexplorer_core.spice_engine import psfascii as P

INFO = """HEADER
"PSFversion" "1.00"
"analysis type" "info"
TYPE
"bsim4" STRUCT(
"ids" FLOAT DOUBLE PROP(
"units" "A"
)
"gm" FLOAT DOUBLE
"region" INT BYTE
) PROP(
"key" "inst"
)
VALUE
"X0.M0" "bsim4" (
1.5e-05
2.5e-04
2
) PROP(
"model" "nmos_lvt.10"
)
"M1" "bsim4" (
3e-05
4e-04
1
)
END
"""


def test_parse_info_structs_zips_members_with_values_and_tolerates_prop() -> None:
    out = P.parse_info_structs(INFO)
    assert out == {
        "X0.M0:ids": 1.5e-05,
        "X0.M0:gm": 2.5e-04,
        "X0.M0:region": 2.0,
        "M1:ids": 3e-05,
        "M1:gm": 4e-04,
        "M1:region": 1.0,
    }


def test_read_oppoint_info_skips_ade_model_dumps(tmp_path: Path) -> None:
    (tmp_path / "dcOpInfo.info").write_text(INFO)
    (tmp_path / "modelParameter.info").write_text(INFO.replace("X0.M0", "SECRET"))
    out = P.read_oppoint_info(tmp_path)
    assert "X0.M0:gm" in out and not any(k.startswith("SECRET") for k in out)
    assert P.read_oppoint_info(tmp_path / "missing") == {}


def test_resolve_sweep_ext_and_sidebands() -> None:
    assert P.resolve_sweep_ext("ac") == ("ac", ".ac")
    assert P.resolve_sweep_ext("noise_spectrum") == ("noise_spectrum", ".noise")
    assert P.resolve_sweep_ext("pss") == ("pss", ".fd.pss")
    assert P.resolve_sweep_ext("pac") == ("pac", ".0.pac")
    assert P.resolve_sweep_ext("pac.3") == ("pac", ".3.pac")
    assert P.resolve_sweep_ext("op") is None


def test_ext_to_analysis_is_the_canonical_inverse_longest_first() -> None:
    exts = list(P.EXT_TO_ANALYSIS)
    assert exts.index(".fd.pss") < exts.index(".ac")
    for ext, key in P.EXT_TO_ANALYSIS.items():
        assert P.SWEEP_EXT[key] == ext


def test_find_swept_psf_prefers_the_contract_named_sibling(tmp_path: Path) -> None:
    for name in (
        "dcOp.dc",
        "dc.dc",
        "pss.td.pss",
        "pss.fd.pss",
        "pac.pac",
        "pac.10.pac",
        "pac.0.pac",
    ):
        (tmp_path / name).write_text("")
    assert P.find_swept_psf(tmp_path, "dc").name == "dc.dc"
    assert P.find_swept_psf(tmp_path, "pss").name == "pss.fd.pss"
    assert P.find_swept_psf(tmp_path, "pac").name == "pac.0.pac"
    assert P.find_swept_psf(tmp_path, "pac.10").name == "pac.10.pac"
    assert P.find_swept_psf(tmp_path, "op") is None
    assert P.find_swept_psf(None, "ac") is None
    assert P.find_swept_psf(tmp_path / "nope", "ac") is None


def _write_ac(path: Path, freq: np.ndarray, h: np.ndarray) -> None:
    lines = [
        "HEADER",
        '"PSFversion" "1.00"',
        '"simulator" "spectre"',
        '"analysis type" "ac"',
        '"analysis name" "ac"',
        "TYPE",
        '"sweep" FLOAT DOUBLE PROP(',
        '"key" "sweep"',
        ")",
        '"V" COMPLEX DOUBLE PROP(',
        '"units" "V"',
        '"key" "node"',
        ")",
        "SWEEP",
        '"freq" "sweep" PROP(',
        '"sweep_direction" 0',
        '"units" "Hz"',
        ")",
        "TRACE",
        '"out" "V"',
        "VALUE",
    ]
    for f, v in zip(freq, h):
        lines.append(f'"freq" {f:.15e}')
        lines.append(f'"out" ({v.real:.15e} {v.imag:.15e})')
    lines.append("END")
    path.write_text("\n".join(lines) + "\n")


def test_read_psf_aliases_the_abscissa_and_reads_complex_traces(tmp_path: Path) -> None:
    pytest.importorskip("psf_utils")
    freq = np.logspace(0, 3, 7)
    h = 1.0 / (1.0 + 1j * freq / 100.0)
    _write_ac(tmp_path / "ac.ac", freq, h)
    d = P.read_swept_psf(tmp_path, "ac")
    assert set(d) >= {"freq", "frequency", "out"}
    np.testing.assert_allclose(d["frequency"], freq)
    np.testing.assert_allclose(d["out"], h)
    # one file, analysis inferred from its name
    d2 = P.read_psf(tmp_path / "ac.ac")
    assert "frequency" in d2
    assert P.read_swept_psf(tmp_path, "tran") == {}
