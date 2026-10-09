"""The README Status section makes claims about the package that code can outrun.

The section used to say the deterministic core was **frozen** while the same README documented the
dialect, hierarchical, controlled-source and device-flavor work that landed after the freeze —
prose nobody could have caught drifting, because nothing checked it (Codex review, item
CG-plan-frozen). "Frozen or not" is not mechanically checkable and is now simply stated correctly.
The two claims that *are* checkable are pinned here:

* what is **still deferred** — the `[viz]` extra and the Phase-7 surface adapters;
* the **device roster** the Status paragraph advertises vs. the device types the round-trip
  contract actually rebuilds.

Both fail loudly when the code moves and this section does not.
"""

import re
from pathlib import Path

import pytest
from spicexplorer_circuitgraph.contract import _NODE_BY_DEVICE_TYPE
from spicexplorer_circuitgraph.model.nodes import DeviceType

_PKG = Path(__file__).resolve().parents[1]
_PACKAGES = _PKG.parent
README = _PKG / "README.md"


def _status_section() -> str:
    """The text of the `## Status …` section, up to the next level-2 heading."""
    body = README.read_text(encoding="utf-8")
    start = body.index("\n## Status")
    end = body.index("\n## ", start + 1)
    return body[start:end]


# --- "still deferred" is a claim about what is NOT here yet --------------------------------
def test_no_viz_extra_yet():
    """`Still deferred: the matplotlib [viz] helpers` — true only while there is no such extra."""
    tomllib = pytest.importorskip("tomllib")
    meta = tomllib.loads((_PKG / "pyproject.toml").read_text(encoding="utf-8"))
    project = meta["project"]
    extras = project.get("optional-dependencies", {})
    deps = list(project.get("dependencies", [])) + [d for v in extras.values() for d in v]
    assert "viz" not in extras, "a [viz] extra exists — drop it from the README's deferred list"
    assert not [d for d in deps if "matplotlib" in d], (
        "matplotlib is a dependency now — the README still calls the viz helpers deferred"
    )


def test_no_rest_surface_adapter_yet():
    """`Still deferred: the Phase-7 surface adapters` — the platform's REST package must not
    import this one. (The API serves the analog-db template catalogue; it never builds a graph.)"""
    api_src = _PACKAGES / "spicexplorer-api" / "src"
    if not api_src.is_dir():
        pytest.skip("spicexplorer-api is not checked out beside this package")
    importers = [
        str(py.relative_to(_PACKAGES))
        for py in api_src.rglob("*.py")
        if re.search(
            r"^\s*(from|import)\s+spicexplorer_circuitgraph\b", py.read_text(encoding="utf-8"), re.M
        )
    ]
    assert not importers, (
        f"the REST surface imports circuitgraph now ({importers}) — the README still calls the "
        "surface adapters deferred"
    )


# --- the advertised device roster vs. the contract's real one ------------------------------
#: How each contract-supported DeviceType is spelled in the Status paragraph's device roster.
README_TOKEN: dict[DeviceType, str] = {
    DeviceType.MOS: "MOS",
    DeviceType.RES: "R",
    DeviceType.CAP: "C",
    DeviceType.IND: "L",
    DeviceType.VSOURCE: "V",
    DeviceType.ISOURCE: "I",
    DeviceType.VCCS: "VCCS",
    DeviceType.VCVS: "VCVS",
    DeviceType.SUBCKT: "subcircuit",
}


def test_status_names_every_device_type_the_contract_rebuilds():
    supported = set(_NODE_BY_DEVICE_TYPE) | {DeviceType.SUBCKT}
    assert supported == set(README_TOKEN), (
        "the round-trip contract gained or lost a device type — name it in the README Status "
        "roster and in README_TOKEN (VCCS/VCVS were added long after the 'frozen' milestone)"
    )
    roster = re.search(r"typed bipartite graph \(([^)]*)\)", _status_section(), re.S)
    assert roster, "the Status paragraph no longer lists the device roster it used to"
    listed = roster.group(1)
    missing = [
        dt.value
        for dt, token in README_TOKEN.items()
        if not re.search(rf"\b{re.escape(token)}\b", listed)
    ]
    assert not missing, f"device types the Status roster does not name: {missing}"


# --- the retarget parenthetical: which tables declare a threshold ---------------------------
def test_threshold_declarations_match_the_status_paragraph():
    """The Status section explains why a missing THRESHOLD substitutes instead of raising: no
    table declares an `lvt` device, and gf180's `hv_nvt` part is the only threshold declared at
    all. Both halves are read straight off `PDKS`, so a new flavored device fails here."""
    from spicexplorer_circuitgraph.pdk import PDKS, split_flavor

    declared = {
        (pdk.name, dev.model)
        for pdk in PDKS.values()
        for dev in pdk.devices
        if split_flavor(dev.flavor)[1]
    }
    assert declared == {("gf180mcu", "nfet_06v0_nvt")}, (
        f"the set of threshold-declaring devices changed ({sorted(declared)}) — the README's "
        "retarget parenthetical names gf180's `hv_nvt` as the only one"
    )
    lvt = [
        (pdk.name, dev.model)
        for pdk in PDKS.values()
        for dev in pdk.devices
        if "lvt" in split_flavor(dev.flavor)[1].split("_")
    ]
    assert not lvt, (
        f"a table declares an `lvt` device now ({lvt}) — the README claims none does, which is "
        "the whole reason a threshold miss substitutes instead of raising"
    )


# --- the detection families the Status section advertises ----------------------------------
#: How each default template family (its `templates/<dir>/manifest.yaml`) is spelled in the
#: Status section's detection sentence.
FAMILY_TOKEN = {
    "current_mirror": "current mirrors",
    "miscellaneous": "miscellaneous",
    "pseudo_resistor": "pseudo-resistors",
    "transmission_gate": "transmission gates",
}


def test_status_names_every_default_template_family():
    """`find_subcircuits`' default library merges the families named in the Status section. A
    fifth catalogue (or a dropped one) has to reach the prose, not just `templates.py`."""
    from spicexplorer_circuitgraph import templates as tpl

    families = {
        getattr(tpl, name).split("/")[1]
        for name in dir(tpl)
        if name.startswith("_DEFAULT_") and name.endswith("_MANIFEST")
    }
    assert families == set(FAMILY_TOKEN), (
        f"the default template families changed ({sorted(families)}) — name them in the README "
        "Status section's detection sentence and in FAMILY_TOKEN"
    )
    section = _status_section()
    missing = [fam for fam, token in FAMILY_TOKEN.items() if token not in section]
    assert not missing, f"template families the Status section does not name: {missing}"


# --- the per-device roles the detection section names --------------------------------------
def test_readme_names_every_family_role_and_the_role_reset():
    """`annotate_subcircuits` gives every device of a family-role block its family's role
    (`match._FAMILY_ROLES`) and first clears the previous run's `DETERMINISTIC_ROLES`. The README's
    role sentence still named only the first two families after the inverter / cross-coupled roles
    were added to `match.py`; a new family role must be named in the README as well."""
    from spicexplorer_circuitgraph.match import _FAMILY_ROLES

    body = README.read_text(encoding="utf-8")
    start = body.index("`annotate_subcircuits(graph, …)` runs both")
    paragraph = body[start : body.index("\n\n", start)]
    missing = [r.name for r in _FAMILY_ROLES.values() if f"`{r.name}`" not in paragraph]
    assert not missing, f"family roles the annotate_subcircuits paragraph does not name: {missing}"
    assert "`DETERMINISTIC_ROLES`" in paragraph, "the paragraph does not say a re-run clears roles"
