import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest

# RL factory needs the dormant torch-backed agents — skip without the [torch] extra.
pytest.importorskip("torch", reason="RL features require: pip install 'spicexplorer[torch]'")


def _install_stable_baselines3_stub():
    sb3_module = ModuleType("stable_baselines3")
    sb3_module.PPO = MagicMock(__name__="PPO")
    sb3_module.SAC = MagicMock(__name__="SAC")
    sb3_module.DDPG = MagicMock(__name__="DDPG")
    sb3_module.TD3 = MagicMock(__name__="TD3")

    common_module = ModuleType("stable_baselines3.common")
    base_class_module = ModuleType("stable_baselines3.common.base_class")
    base_class_module.BaseAlgorithm = object

    noise_module = ModuleType("stable_baselines3.common.noise")

    class _NoiseBase:
        def __init__(self, mean, sigma):
            self.mean = mean
            self.sigma = sigma

    class NormalActionNoise(_NoiseBase):
        pass

    class OrnsteinUhlenbeckActionNoise(_NoiseBase):
        pass

    noise_module.NormalActionNoise = NormalActionNoise
    noise_module.OrnsteinUhlenbeckActionNoise = OrnsteinUhlenbeckActionNoise

    sys.modules["stable_baselines3"] = sb3_module
    sys.modules["stable_baselines3.common"] = common_module
    sys.modules["stable_baselines3.common.base_class"] = base_class_module
    sys.modules["stable_baselines3.common.noise"] = noise_module

    return sb3_module


sb3 = _install_stable_baselines3_stub()

from spicexplorer.core.domains import (  # noqa: E402
    AgentType,
    DDPGConfig,
    NetworkConfig,
    NoiseConfig,
    NoiseType,
    ReplayBufferConfig,
    RLTrainingConfig,
    SACAlphaConfig,
    SACConfig,
)
from spicexplorer.optimization.rl.rl_factory import RLAgentFactory  # noqa: E402


def _dummy_env():
    return SimpleNamespace(action_space=SimpleNamespace(shape=(2,)))


def test_ddpg_adapter_translation():
    env = _dummy_env()
    config = DDPGConfig(
        actor=NetworkConfig(lr=1e-4, hidden_units=(64, 64)),
        critic=NetworkConfig(hidden_units=(32, 32)),
        noise=NoiseConfig(type=NoiseType.GAUSSIAN, sigma_initial=0.3),
        memory=ReplayBufferConfig(batch_size=32),
        training=RLTrainingConfig(gamma=0.95, tau=0.01, update_every=4),
    )

    RLAgentFactory.create_agent(AgentType.DDPG, env, config)

    call_kwargs = sb3.DDPG.call_args.kwargs
    assert call_kwargs["learning_rate"] == 1e-4
    assert call_kwargs["gamma"] == 0.95
    assert call_kwargs["batch_size"] == 32
    assert call_kwargs["tau"] == 0.01
    assert call_kwargs["train_freq"] == (4, "episode")
    assert call_kwargs["action_noise"].sigma.tolist() == [0.3, 0.3]


def test_sac_adapter_translation():
    env = _dummy_env()
    config = SACConfig(
        actor=NetworkConfig(lr=3e-4, hidden_units=(256, 256)),
        critic=NetworkConfig(hidden_units=(128, 128)),
        alpha=SACAlphaConfig(learn_alpha=False, alpha_init=0.5),
        memory=ReplayBufferConfig(batch_size=16),
        training=RLTrainingConfig(gamma=0.97, tau=0.02, update_every=2),
    )

    RLAgentFactory.create_agent(AgentType.SAC, env, config)

    call_kwargs = sb3.SAC.call_args.kwargs
    assert call_kwargs["learning_rate"] == 3e-4
    assert call_kwargs["gamma"] == 0.97
    assert call_kwargs["batch_size"] == 16
    assert call_kwargs["tau"] == 0.02
    assert call_kwargs["train_freq"] == 2
    assert call_kwargs["ent_coef"] == 0.5


def test_unknown_agent_type_raises():
    class FakeType:
        value = "fake"

    try:
        RLAgentFactory.create_agent(FakeType(), _dummy_env(), DDPGConfig())
    except ValueError as exc:
        assert "Unknown AgentType" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown agent type")
