import logging
from typing import Any, Callable, Dict, Optional, Tuple, Type

import numpy as np

# Domain Imports
from spicexplorer.core.domains import (
    AgentConfig,
    AgentType,
    DDPGConfig,
    NoiseConfig,
    NoiseType,
    SACConfig,
)

# Stable Baselines3 Imports
from stable_baselines3 import DDPG, SAC, TD3
from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise

logger = logging.getLogger("spicexplorer.rl_factory")

# Type definition for the Registry Value: (Agent Class, Adapter Function)
RegistryEntry = Tuple[Type[BaseAlgorithm], Callable[[Any, Any], Dict[str, Any]]]

class RLAgentFactory:
    """
    A Factory class to instantiate RL Agents based on the AgentType Enum.
    It adapts the Domain Configuration objects into SB3-compatible kwargs.
    """

    # Stores { AgentType : (Class, AdapterFunction) }
    _registry: Dict[AgentType, RegistryEntry] = {}

    @classmethod
    def register(cls,
                 agent_type: AgentType,
                 agent_class: Type[BaseAlgorithm],
                 adapter_func: Callable[[Any, Optional[Any]], Dict[str, Any]]):
        """
        Register a new agent type (Standard or Custom).

        :param agent_type: The Enum key (e.g., AgentType.PPO)
        :param agent_class: The class object (e.g., PPO)
        :param adapter_func: A function f(config, env) -> dict that returns kwargs.
        """
        cls._registry[agent_type] = (agent_class, adapter_func)
        logger.debug(f"Registered RL Agent: {agent_type.value} -> {agent_class.__name__}")

    @classmethod
    def create_agent(cls,
                     agent_type: AgentType,
                     env: Any,
                     config: AgentConfig,
                     **runtime_kwargs) -> BaseAlgorithm:
        """
        Creates and returns an instantiated RL agent.

        :param agent_type: Enum indicating which agent to build.
        :param env: The Gym environment (needed for input dimensions and noise generation).
        :param config: The configuration dataclass (e.g., DDPGConfig).
        :param runtime_kwargs: Extra args passed at runtime (e.g., tensorboard_log, verbose).
        """
        if agent_type not in cls._registry:
            valid_keys = [k.value for k in cls._registry.keys()]
            logger.critical(f"AgentType '{agent_type}' is not registered. Available: {valid_keys}")
            raise ValueError(f"Unknown AgentType: {agent_type}")

        agent_class, adapter_func = cls._registry[agent_type]

        # 1. Adapt Config -> Agent Kwargs
        try:
            agent_kwargs = adapter_func(config, env)
        except AttributeError as e:
            logger.error(f"Configuration mismatch for {agent_type}. Check if yaml matches Config class. Error: {e}")
            raise

        # 2. Merge Runtime Overrides (e.g., tensorboard paths, seed)
        agent_kwargs.update(runtime_kwargs)

        # 3. Instantiate
        logger.info(f"Instantiating {agent_class.__name__} ({agent_type.value})")
        logger.debug(f"Agent Params: {agent_kwargs}")

        return agent_class(env=env, **agent_kwargs)

# -------------------------------------------------------------------------
#                               ADAPTERS
# -------------------------------------------------------------------------
# These functions translate Domain Configs to SB3 parameters.
# -------------------------------------------------------------------------

def _create_action_noise(noise_config: NoiseConfig, env: Any):
    """Helper to create SB3 Noise Objects."""
    if env is None: return None

    n_actions = env.action_space.shape[-1]

    if noise_config.type == NoiseType.OU:
        return OrnsteinUhlenbeckActionNoise(
            mean=np.zeros(n_actions),
            sigma=noise_config.sigma_initial * np.ones(n_actions)
        )
    elif noise_config.type == NoiseType.GAUSSIAN:
        return NormalActionNoise(
            mean=np.zeros(n_actions),
            sigma=noise_config.sigma_initial * np.ones(n_actions)
        )
    return None

def _adapter_common(config: AgentConfig) -> Dict[str, Any]:
    """Extracts common parameters found in most AgentConfigs."""
    # Note: PPO/SAC configs in your domain don't inherit from a common base
    # that holds 'training' or 'memory', so we assume the attributes exist.
    return {
        "policy": "MlpPolicy",
        "learning_rate": config.actor.lr,
        "gamma": config.training.gamma,
        "batch_size": config.memory.batch_size,
        "verbose": 1,
    }

def _adapter_ppo(config: Any, env: Any) -> Dict[str, Any]:
    # PPO doesn't use the 'memory' block the same way (it uses n_steps),
    # but we map what we can.
    # Note: Your current domain PPO config wasn't fully defined in the prompt,
    # assuming generic handling or that you might add PPOConfig later.
    kwargs = {
        "policy": "MlpPolicy",
        "verbose": 1,
        # Defaulting generic params if specific config missing
        "learning_rate": getattr(config, 'lr', 1e-4),
    }
    return kwargs

def _adapter_ddpg(config: DDPGConfig, env: Any) -> Dict[str, Any]:
    kwargs = _adapter_common(config)
    kwargs.update({
        "tau": config.training.tau,
        "train_freq": (config.training.update_every, "episode"),
        "gradient_steps": -1, # Train as much as collected
        "action_noise": _create_action_noise(config.noise, env),
        "policy_kwargs": dict(net_arch=dict(pi=list(config.actor.hidden_units), qf=list(config.critic.hidden_units)))
    })
    return kwargs

def _adapter_td3(config: DDPGConfig, env: Any) -> Dict[str, Any]:
    # TD3 shares configuration structure with DDPG usually
    kwargs = _adapter_ddpg(config, env)
    kwargs["policy_delay"] = config.training.policy_update_freq
    return kwargs

def _adapter_sac(config: SACConfig, env: Any) -> Dict[str, Any]:
    kwargs = _adapter_common(config)

    # Handle Alpha (Entropy Regularization)
    ent_coef = "auto" if config.alpha.learn_alpha else config.alpha.alpha_init

    kwargs.update({
        "tau": config.training.tau,
        "train_freq": config.training.update_every,
        "ent_coef": ent_coef,
        # SAC allows passing target_entropy if needed, usually 'auto' is fine
        "policy_kwargs": dict(net_arch=dict(pi=list(config.actor.hidden_units), qf=list(config.critic.hidden_units)))
    })
    return kwargs

# -------------------------------------------------------------------------
#                           BOOTSTRAPPING
# -------------------------------------------------------------------------
# Register the standard agents immediately when this module is imported.

RLAgentFactory.register(AgentType.DDPG, DDPG, _adapter_ddpg)
RLAgentFactory.register(AgentType.TD3,  TD3,  _adapter_td3)
RLAgentFactory.register(AgentType.SAC,  SAC,  _adapter_sac)
# RLAgentFactory.register(AgentType.PPO,  PPO,  _adapter_ppo) # Uncomment when PPOConfig is defined
