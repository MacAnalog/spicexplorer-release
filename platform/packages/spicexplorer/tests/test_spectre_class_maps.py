"""Every COMMITTED class bench map renders — the Spectre template-DB drift guard.

The amplifier/ia/ldo maps were render/live-proven when they landed, but only ad-hoc;
this pins ALL committed ``_shared/classes/<class>/spectre-benches.yaml`` maps (now
including buffer / comparator / diff_pair / gain_stage / temp_sensor) against REAL
member-circuit params: every bench's analysis statements and calculator rows must
render with zero unresolved placeholders, and every mapped bench must have at least
one member circuit that actually binds it (map↔corpus drift is a failure, not a skip).

Offline — no simulator, no bridge; pure template rendering over committed data.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

try:
    from spicexplorer.backends.analog_db import analog_db_root

    _ROOT: Path | None = analog_db_root(None)
except Exception:  # AnalogDbUnavailable / import errors → no checkout, skip all
    _ROOT = None


def _cases() -> list:
    if _ROOT is None or not (_ROOT / "_shared/classes").is_dir():
        return [pytest.param(None, None, None,
                             id="no-analog-db",
                             marks=pytest.mark.skip(reason="analog-db checkout absent"))]
    members_by_class: dict[str, list[Path]] = {}
    for cdir in sorted((_ROOT / "circuits").iterdir()):
        cy = cdir / "circuit.yaml"
        if cy.is_file():
            klass = (yaml.safe_load(cy.read_text()) or {}).get("class")
            members_by_class.setdefault(str(klass), []).append(cdir)
    cases = []
    for map_path in sorted((_ROOT / "_shared/classes").glob("*/spectre-benches.yaml")):
        cls = map_path.parent.name
        benches = (yaml.safe_load(map_path.read_text()) or {}).get("benches") or {}
        for tb in benches:
            member = next(
                (c.name for c in members_by_class.get(cls, [])
                 if (c / "analyses" / f"{tb}.yaml").is_file()),
                None,
            )
            cases.append(pytest.param(cls, tb, member, id=f"{cls}:{tb}"))
    return cases


@pytest.mark.parametrize(("cls", "tb", "member"), _cases())
def test_class_bench_map_renders(cls: str, tb: str, member: str | None) -> None:
    from spicexplorer.backends import spectre_templates
    from spicexplorer.backends.analog_db import _spectre_context, load_analysis, pdk_supply

    assert member is not None, (
        f"class map {cls!r} lists bench {tb!r} but NO member circuit binds "
        f"analyses/{tb}.yaml — map/corpus drift"
    )
    params = load_analysis(member, tb).get("params", {})
    try:
        supply = pdk_supply("tsmc-n65")
    except Exception:
        supply = None  # no closed-lane PDK registry entry in this checkout
    context = _spectre_context(tb, params, supply=supply)

    statements = spectre_templates.bench_analyses(tb, context, circuit_class=cls)
    assert statements, f"{cls}:{tb} rendered no analysis statements"
    for s in statements:
        assert "{" not in s and "}" not in s, f"unresolved placeholder in {s!r}"

    # the calculator route must render too ([] is fine — not every bench has rows)
    rows = spectre_templates.bench_measurements(tb, context, circuit_class=cls)
    assert isinstance(rows, list)
