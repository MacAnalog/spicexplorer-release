"""The API's run path refuses the retired RL engine (platform doc/TODO.md §16, owner ruling 2026-09-25).

The UI's run path builds its streaming optimizer through the SAME `optimizer_type_from_config`
function that script runs use, so a saved project that still says `optimizer_config.type:
reinforcement_learning` fails there with the retirement named — `_run_live` records that as the
run's error — instead of silently running some other engine. The platform-side proof of the
retirement is `packages/spicexplorer/tests/test_rl_retired.py`.
"""

from __future__ import annotations

import asyncio

import pytest
from _api_fixtures import EXAMPLE_YAML
from spicexplorer.core.domains import Project_Setup
from spicexplorer_api.services import optimizer_runner as runner


def _project(engine: str) -> Project_Setup:
    project = Project_Setup.from_yaml(EXAMPLE_YAML)
    project.optimizer_config.type = engine
    return project


def _build(engine: str) -> type:
    loop = asyncio.new_event_loop()
    try:
        state = runner.RunState(
            run_id=f"retired-{engine}", queue=asyncio.Queue(), loop=loop, budget=1
        )
        return runner._streaming_optimizer_class(state, _project(engine))
    finally:
        loop.close()


def test_the_run_lane_refuses_the_retired_rl_engine_naming_the_retirement():
    with pytest.raises(
        ValueError,
        match=r"'reinforcement_learning' is no longer supported: "
        r"the RL optimizer backend was retired",
    ):
        _build("reinforcement_learning")


def test_the_run_lane_still_builds_the_nevergrad_engine():
    from spicexplorer.optimization.stochastic.nevergrad import Nevergrad_Spice_Single_Objective

    assert issubclass(_build("nevergrad"), Nevergrad_Spice_Single_Objective)
