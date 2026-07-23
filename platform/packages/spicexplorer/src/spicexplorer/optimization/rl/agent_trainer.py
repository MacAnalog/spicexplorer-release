import os
from collections import deque

import numpy as np
from rl_framework.utils import CSVLogger, log_message


class ResultTracker:
    """Handles Pareto dominance and saving the best-performing circuit designs."""
    def __init__(self, results_dir, target_specs):
        self.results_dir = os.path.join(results_dir, "best_episode_data")
        os.makedirs(self.results_dir, exist_ok=True)
        self.target_specs = target_specs
        self.best_reward = -float('inf')
        self.primary_saved = False
        self.specs_in_dir = {}
        self.all_time_bests = {}

    def update(self, episode_num, reward, info, env):
        """Logic for checking if the current episode is the 'best' yet."""
        raw_obs = info.get('raw_observation', {})
        current_specs = self._extract_specs(raw_obs)

        # 1. Check if all range targets are met
        met_ranges = all(s.get('is_met', True) for s in current_specs.values())

        if met_ranges:
            # 2. Pareto Dominance or Improvement Logic here
            should_save = self._check_dominance(current_specs)
            if should_save:
                self._save_best_data(episode_num, reward, current_specs, env)
                self.primary_saved = True
                self.specs_in_dir = current_specs

    def _extract_specs(self, raw_obs):
        # Move the complex nested loop from the original script to here
        # Return a dictionary of {spec_name: {val, is_met, etc.}}
        pass

    def _check_dominance(self, current_specs):
        # Implementation of the Pareto comparison logic
        return True

    def _save_best_data(self, ep, reward, specs, env):
        # Implementation of shutil.copy2 and json.dump for best results
        log_message("INFO", f"Saved new best data from Episode {ep}")

class RLTrainer:
    """The central Orchestrator for RL training."""
    def __init__(self, env, agent, config, run_id):
        self.env = env
        self.agent = agent
        self.config = config
        self.run_id = run_id

        # Hyperparameters
        self.train_hp = config.get("training_hyperparameters", {})
        self.max_episodes = self.train_hp.get("max_episodes", 1000)
        self.early_stop_patience = self.train_hp.get("early_stop_patience", 50)

        # State tracking
        self.scores_deque = deque(maxlen=100)
        self.best_moving_avg = -float('inf')
        self.stop_flag_path = "stop_optimize.flag" # Simplified for example

    def run(self, tracker: ResultTracker, logger: CSVLogger):
        """Primary training loop."""
        for episode in range(1, self.max_episodes + 1):
            if self._check_stop_signal():
                break

            score, steps, info = self._run_episode(episode)

            # Update metrics
            self.scores_deque.append(score)
            avg_score = np.mean(self.scores_deque)

            # Log results
            logger.log([episode, score, steps, avg_score])

            # Track best models (Modular call)
            tracker.update(episode, score, info, self.env)

            # Check for Early Stopping
            if self._should_early_stop(avg_score):
                log_message("INFO", "Early stopping triggered.")
                break

            if episode % self.train_hp.get("save_interval", 100) == 0:
                self.agent.save_state(f"agent_{self.run_id}")

    def _run_episode(self, episode_num):
        state, info = self.env.reset(seed=episode_num)
        total_reward = 0
        steps = 0

        for _ in range(self.env.max_steps_per_episode):
            action = self.agent.select_action(state, add_noise=True)
            next_state, reward, term, trunc, info = self.env.step(action)

            self.agent.step(state, action, reward, next_state, (term or trunc))

            state = next_state
            total_reward += reward
            steps += 1
            if term or trunc:
                break
        return total_reward, steps, info

    def _check_stop_signal(self):
        return os.path.exists(self.stop_flag_path)

    def _should_early_stop(self, current_avg):
        # Implementation of the patience logic
        return False
