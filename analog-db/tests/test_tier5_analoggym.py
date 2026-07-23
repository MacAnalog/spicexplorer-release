"""Phase-5 gate: the AnalogGym amplifier corpus is imported, classified, and schema/generation/
assembly valid. PDK-free."""

from __future__ import annotations

from pathlib import Path

import pytest

from spicexplorer_analog_db import model, verify
from spicexplorer_analog_db.importers import analoggym


def _analoggym_ids() -> list[str]:
    out = []
    for cid in model.list_circuit_ids():
        prov = model.load_circuit(cid).manifest.get("provenance", {})
        if prov.get("source") == "AnalogGym":
            out.append(cid)
    return out


def test_at_least_15_analoggym_amplifiers_imported():
    ids = _analoggym_ids()
    assert len(ids) >= 15, f"only {len(ids)} AnalogGym circuits: {ids}"


@pytest.mark.parametrize("cid", _analoggym_ids())
def test_analoggym_circuit_clears_t0_t2(cid):
    results = verify.run_tier0([cid]) + verify.run_tier1([cid]) + verify.run_tier2([cid])
    failures = [r for r in results if r.status == "fail"]
    assert not failures, "\n".join(f"{r.tier} {r.check}: {r.reason}" for r in failures)


def test_classification_is_data_driven():
    """Folder name → compensation/stages, and the paper attribution is data-driven."""
    assert analoggym.parse_folder("Leung_NMCNR_Pin_3") == {
        "author": "Leung", "compensation": "NMCNR", "stages": 3
    }
    c = model.load_circuit("amp_009_leung_nmcnr")
    m = c.manifest
    assert m["compensation"] == "NMCNR" and m["stages"] == 3
    assert m["provenance"]["license"] == "BSD-3-Clause"
    # upstream folder + the pre-accession legacy id
    assert m["provenance"]["aliases"] == ["Leung_NMCNR_Pin_3", "leung_nmcnr_pin_3"]
    assert m["ports"] == ["vss", "vdd", "vinn", "vinp", "vout"]  # normalized from gnda/vdda


def test_abstract_is_pdk_neutral_and_lowers_to_sky130():
    from spicexplorer_analog_db import generate

    c = model.load_circuit("amp_003_fan_smc")
    text = (c.dir / "abstract" / "netlist.spice").read_text()
    # inspect device lines only (the comment header documents the gnda→vss/vdda→vdd renames)
    body = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("*"))
    assert "sky130_fd_pr__" not in body and "nmos" in body and "pmos" in body
    assert "vdda" not in body.lower() and "gnda" not in body.lower()
    lowered = generate.lowered_netlist(c, "sky130")
    assert "sky130_fd_pr__nfet_01v8" in lowered and "sky130_fd_pr__pfet_01v8" in lowered


def _amplifier_dir() -> Path | None:
    """The AnalogGym source (a platform submodule) — absent in a standalone DB checkout."""
    try:
        from spicexplorer_core import project_root

        amp = project_root() / "submodules" / "AnalogGym" / "AnalogGym" / "Amplifier"
    except Exception:
        return None
    return amp if (amp / "spice_netlist").is_dir() else None


def test_importer_is_reproducible_from_source(tmp_path):
    """Re-importing from the AnalogGym source reproduces the committed abstract netlist
    (drift guard). Skips when the source submodule is absent."""
    amp = _amplifier_dir()
    if amp is None:
        pytest.skip("AnalogGym source submodule absent (standalone DB checkout)")
    analoggym.import_circuit(amp, "Fan_SMC_Pin_3", tmp_path)
    fresh = (tmp_path / "amp_003_fan_smc" / "abstract" / "netlist.spice").read_text()
    committed = (model.load_circuit("amp_003_fan_smc").dir / "abstract" / "netlist.spice").read_text()
    assert fresh == committed, "committed abstract drifted from a fresh import"
