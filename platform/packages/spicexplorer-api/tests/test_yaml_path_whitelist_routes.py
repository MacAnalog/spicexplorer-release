"""Regression: the project-loading routes must funnel their caller-supplied yaml_path through the
`_validated_yaml_path` whitelist choke point (BUG-B2, cross_repo_audit).

`/score`, `/simulate/once`, `/sanity-check`, and `/spec/{name}/sensitivity` all called
`Project_Setup.from_yaml(<caller path>)` directly — an arbitrary-file-read + existence-oracle +
error-echo surface. The fix routes each through `require_yaml_under_allowed_root`, which 400s a
path that isn't a real `.yaml`/`.yml` under an allowed root (repo `examples/`, the work root, or an
`spx_uploaded_*` temp file). These call the route functions directly and assert the 400 — no live
SPICE, PDK, or app boot needed (a rejected path never reaches `from_yaml`).
"""
import asyncio
import sys

import pytest
from _api_fixtures import EXAMPLE_YAML, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT))
pytest.importorskip("fastapi", reason="ui extra not installed")

from fastapi import HTTPException  # noqa: E402

# right suffix but outside every allowed root; no-suffix arbitrary system file; and a `..`
# traversal that STARTS inside an allowed root (examples/) yet resolves back out to /etc — the
# whitelist resolves before the containment check, so this must still be rejected.
_OUTSIDE = "/etc/foo.yaml"
_NO_SUFFIX = "/etc/passwd"
_TRAVERSAL = str(REPO_ROOT / "examples") + "/../../../../../../../../../../etc/shadow.yaml"


def _invoke_score(path: str):
    from spicexplorer_api.routes.score import ScoreRequest, score_endpoint
    return score_endpoint(ScoreRequest(yaml_path=path, metric_values={}))


def _invoke_simulate(path: str):
    from spicexplorer_api.routes.simulate import SimulateOnceRequest, simulate_once
    return asyncio.run(simulate_once(SimulateOnceRequest(yaml_path=path, params={"w": 1.0})))


def _invoke_sanity(path: str):
    from spicexplorer_api.routes.sanity import SanityRequest, sanity_check
    return asyncio.run(sanity_check(SanityRequest(yaml_path=path)))


def _invoke_sensitivity(path: str):
    from spicexplorer_api.routes.sensitivity import spec_sensitivity
    return asyncio.run(spec_sensitivity("some_spec", yaml_path=path))


_ROUTES = [
    ("score", _invoke_score),
    ("simulate", _invoke_simulate),
    ("sanity", _invoke_sanity),
    ("sensitivity", _invoke_sensitivity),
]


@pytest.mark.parametrize("name,invoke", _ROUTES)
@pytest.mark.parametrize("bad", [_OUTSIDE, _NO_SUFFIX, _TRAVERSAL])
def test_route_rejects_out_of_whitelist_yaml_path(name, invoke, bad):
    with pytest.raises(HTTPException) as ei:
        invoke(bad)
    assert ei.value.status_code == 400, f"{name} accepted out-of-whitelist path {bad!r}"


def test_require_helper_accepts_in_bounds_example():
    """The choke point accepts a real .yaml under an allowed root (the example project)."""
    from spicexplorer_api.routes.checkpoint import require_yaml_under_allowed_root
    assert require_yaml_under_allowed_root(str(EXAMPLE_YAML)) == EXAMPLE_YAML.resolve()


def test_score_in_bounds_missing_file_is_404_not_400():
    """An in-bounds but non-existent .yaml passes the whitelist (so NOT 400) and 404s normally —
    proving the choke point accepts valid paths rather than blanket-rejecting."""
    from spicexplorer_api.routes.score import ScoreRequest, score_endpoint
    missing = EXAMPLE_YAML.parent / "___no_such_project___.yaml"
    with pytest.raises(HTTPException) as ei:
        score_endpoint(ScoreRequest(yaml_path=str(missing), metric_values={}))
    assert ei.value.status_code == 404
