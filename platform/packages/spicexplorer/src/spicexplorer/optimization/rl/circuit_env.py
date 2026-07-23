import logging
from typing import Callable, Optional

import gymnasium as gym
import numpy as np
from gymnasium import spaces

# Internal Imports
from spicexplorer.core.domains import Project_Setup, RLTrainingConfig

# ------------------ Module Logger ------------------

logger = logging.getLogger("spicexplorer.optimization.rl.gymenv")

# ------------------ Classes ------------------
FLOAT_TYPE = np.float32

class SpiceGymEnv(gym.Env):
    """
    A Gym Adapter that connects an RL Agent to the SpiceXplorer Framework.
    Delegates simulation logic to the Optimizer via a callback.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self,
                 eval_callback: Callable,
                 setup_obj: Project_Setup,
                 config: RLTrainingConfig, # Updated from EnvHyperparameters
                 run_name: Optional[str] = "default",
                 render_mode=None):
        super().__init__()

        self.setup_obj = setup_obj
        self.eval_callback = eval_callback
        self.config = config
        self.run_name = run_name
        self.render_mode = render_mode

        # 1. Define Action Space (Normalized [-1, 1])
        self.action_dim = len(setup_obj.dut_params) # Saved as attribute
        self.action_space = spaces.Box(
            low=-1.0, high=1.0,
            shape=(self.action_dim,),
            dtype=FLOAT_TYPE
        )

        # 2. Define Observation Space (Normalized Specs)
        self.state_dim = len(setup_obj.optimizer_config.target_specs.targets) # Saved as attribute
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(self.state_dim,),
            dtype=FLOAT_TYPE
        )

        self.current_episode_step = 0

    def step(self, action: np.ndarray):
        self.current_episode_step += 1

        # A. Map Action -> Dictionary
        param_dict = {}
        for i, param in enumerate(self.setup_obj.dut_params):
             # Optimizer handles mapping [-1, 1] -> [min, max]
             param_dict[param.name] = float(action[i])

        # B. Delegate Simulation
        # The callback handles the "Heavy Lifting" (Simulating & Scoring)
        score, fit_summary = self.eval_callback(param_dict, is_normalized_input=True)

        # C. Construct Observation State
        obs_list = []
        target_names = self.setup_obj.optimizer_config.target_specs.list_target_names()

        for spec_name in target_names:
            # Safely get value, default to 0.0 if missing/failed
            val = fit_summary.get(spec_name, {}).get('curr_val', 0.0)
            # Handle SPICE failures (NaN/Inf) gracefully
            if not np.isfinite(val):
                logger.warning(f"got invalid value for {spec_name}")
                val = 0.0
            obs_list.append(val)

        observation = np.array(obs_list, dtype=FLOAT_TYPE)

        # D. Termination Logic
        terminated = False # We usually don't terminate early in circuit sizing unless we crash

        # Truncate if we hit the max steps defined in RLTrainingConfig
        truncated = self.current_episode_step >= self.config.max_episode_steps

        return observation, float(score), terminated, truncated, fit_summary

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_episode_step = 0

        # BEST PRACTICE:
        # Instead of returning zeros, we ideally return the metrics of the "Nominal" (start) design.
        # However, running a SPICE sim just for reset() is expensive.
        # Compromise: Return zeros, but ensure your Agent uses 'VecNormalize'
        # to handle the scaling differences quickly.
        observation = np.zeros(self.state_dim, dtype=FLOAT_TYPE)

        return observation, {}

    def render(self):
        if self.render_mode == "human":
            pass

    def close(self):
        pass
