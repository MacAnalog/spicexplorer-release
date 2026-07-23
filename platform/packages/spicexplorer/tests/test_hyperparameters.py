from pathlib import Path

import pytest

# RL (DDPG/SAC) is the dormant torch-backed path — skip when the optional [torch]
# extra isn't installed (a torch-free install of spicexplorer is fully supported).
pytest.importorskip("torch", reason="RL features require: pip install 'spicexplorer[torch]'")

from spicexplorer.optimization.rl.utils.hyperparameters import DDPGConfig


def test_ddpg_hyperparameters_from_yaml():
    hyperparams = DDPGConfig.from_yaml(str(Path(__file__).parent / "ddpg_hyperparameters.yaml"))

    assert hyperparams.actor.lr == 5e-4
    assert hyperparams.actor.hidden_units == [256, 128]
    assert hyperparams.critic.grad_clip == 1.0
    assert hyperparams.memory.buffer_size == 500000
    assert hyperparams.training.gamma == 0.99
