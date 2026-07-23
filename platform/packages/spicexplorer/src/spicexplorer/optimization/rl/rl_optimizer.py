import logging
from typing import Any, Dict, Tuple

import numpy as np

# Internal Imports
from spicexplorer.core.domains import (
    AgentConfig,
    AgentType,
    DDPGConfig,
    Project_Setup,
    SACConfig,
    TestbenchParams,
)
from spicexplorer_core.spice_engine.spicelib import NGSpice_Wrapper

# Stable Baselines3 (for vector envs)
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv

# Import Base Classes and Environment
from ..base import Spice_Constraint_Satisfaction
from .circuit_env import SpiceGymEnv
from .rl_factory import RLAgentFactory

logger = logging.getLogger("spicexplorer.optimization.rl_optimizer")

class RL_Spice_Optimizer(Spice_Constraint_Satisfaction):
    """
    RL-based optimizer using Stable-Baselines3.
    Inherits simulation and scoring logic from Spice_Constraint_Satisfaction.
    Uses RLAgentFactory to support DDPG, SAC, TD3, etc.
    """
    def __init__(self, setup_obj: Project_Setup, spicelib_wrapper: Dict[TestbenchParams, NGSpice_Wrapper]):
        super().__init__(setup_obj=setup_obj, spicelib_wrappers=spicelib_wrapper)
        self.vec_env = None
        self.model = None

    # --- 1. Setup Phase ---
    def parameterize(self) -> Any:
        # RL uses the Gym Env spaces managed by the Environment class.
        # We return the raw params for reference/consistency with base class.
        return self.setup_obj.dut_params

    def _create_optimizer_obj(self) -> bool:
        """Initialize the Vectorized Environment and the RL Agent via Factory."""
        logger.info("Initializing RL Environment and Agent...")

        # A. Setup Vector Environment
        # ---------------------------
        # We need a lambda to create the env for SubprocVecEnv
        # We pass 'self.evaluate_adapter' so the Env can call back to this class
        def make_env():
            return SpiceGymEnv(setup_obj=self.setup_obj, eval_callback=self.evaluate_adapter)

        # Number of parallel environments (could be configurable in future)
        n_envs = 1
        # Use DummyVecEnv for simpler debugging or single-threaded execution
        # Use SubprocVecEnv for true parallelism (requires careful pickling of self)
        if n_envs > 1:
            self.vec_env = SubprocVecEnv([make_env for _ in range(n_envs)])
        else:
            self.vec_env = DummyVecEnv([make_env])

        # B. Identify Agent Type & Config
        # -------------------------------
        config = self.setup_obj.optimizer_config.agent_config
        agent_type = self._infer_agent_type(config)

        # C. Create Agent via Factory
        # ---------------------------
        self.model = RLAgentFactory.create_agent(
            agent_type=agent_type,
            env=self.vec_env,
            config=config,
            # Runtime overrides
            tensorboard_log=str(self.setup_obj.outdir / "tensorboard"),
            seed=self.setup_obj.optimizer_config.random_seed
        )

        self.optimizer = self.model # Base class reference
        return True

    def _infer_agent_type(self, config: AgentConfig) -> AgentType:
        """Helper to deduce Enum from the Config Class type."""
        if isinstance(config, SACConfig): return AgentType.SAC
        if isinstance(config, DDPGConfig): return AgentType.DDPG
        # Default fallback
        logger.warning("Agent config type not recognized, defaulting to DDPG.")
        return AgentType.DDPG

    # --- 2. Adaptation Layer (Gym <-> Framework) ---

    def evaluate_adapter(self, action_dict: Dict[str, float], is_normalized_input: bool = False):
        """
        Callback used by SpiceGymEnv.
        Adapts the Gym action (typically [-1, 1]) to the Base_Optimizer evaluate() signature.
        """
        if is_normalized_input:
            real_params = self._map_gym_action_to_physical(action_dict)
        else:
            real_params = action_dict

        # Call the parent class's evaluate logic (runs simulation, computes reward)
        return super().evaluate(real_params)

    def _map_gym_action_to_physical(self, norm_params: Dict[str, float]) -> Dict[str, float]:
        """
        Maps Gym's [-1, 1] range to physical values.
        Handles both Linear and Logarithmic scaling based on Param definition.
        """
        phys_params = {}
        for name, val in norm_params.items():
            param = self.setup_obj.get_param_by_name(name)
            if param is None: continue

            # Clamp input to [-1, 1] just in case
            val_clamped = max(-1.0, min(1.0, val))

            # Normalize 0..1 first (easier to work with)
            # [-1, 1] -> [0, 1]
            val_01 = (val_clamped + 1.0) / 2.0

            if param.log_scale:
                # Log Scale Mapping: exp( val_01 * (ln(max) - ln(min)) + ln(min) )
                phys_params[name] = param.compute_log_normalization(val_01)
            else:
                # Linear Scale Mapping: min + val_01 * (max - min)
                phys_params[name] = param.compute_lin_normalization(val_01)

        return phys_params

    # --- 3. Execution Phase ---

    def optimization_step(self) -> Tuple[Dict[str, np.floating], np.floating, Dict[str, Any]]:
        """
        Executes a block of training steps.
        """
        # 1. Determine how many steps to train this cycle
        # We can grab this from the config
        steps_per_trial = self.setup_obj.optimizer_config.agent_config.training.max_episode_steps

        # 2. Train the model
        self.model.learn(total_timesteps=steps_per_trial, reset_num_timesteps=False)

        # 3. Return the latest result for logging in the main loop
        # Check if we have logs; if strict RL training just started, log might be empty
        if len(self.optimization_log) > 0:
            last_entry = self.optimization_log[-1]
            return last_entry.point.params, last_entry.point.score, last_entry.fit_summary
        else:
            # Fallback if no simulation completed yet (rare)
            return {}, 0.0, {}

