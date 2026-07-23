import logging
from typing import Tuple

import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim
from spicexplorer.optimization.rl.models.base import BaseActor, BaseCritic

from ..utils.hyperparameters import SACConfig
from ..utils.replay_buffer import ReplayBuffer
from ..utils.typing import ExperienceBatch
from .base import BaseActorCriticRLAgent

# ------------------ Module Logger ------------------

logger = logging.getLogger("spicexplorer.optimization.rl.agents.sac")

# ------------------ Classes ------------------

class SACAgent(BaseActorCriticRLAgent):
    """Interacts with and learns from the environment using SAC."""

    def __init__(self,
                 state_dim: int,
                 action_dim: int,
                 actor_model_class,
                 critic_model_class,
                 hyperparams: SACConfig,
                 device: torch.device,
                 seed: int = 0,
                 model_load_path: str = None
                 ):
        """
        Initialize an Agent object.
        """
        super().__init__(state_dim, action_dim, hyperparams, device, seed)
        self.hyperparams = hyperparams

        # Actor Network
        self._create_actor(actor_model_class=actor_model_class)

        # Critic Networks (Twin Q-functions)
        self._create_critic(critic_model_class=critic_model_class)

        # Entropy Temperature (Alpha)
        self.learn_alpha = self.hyperparams.alpha.learn_alpha
        # Target entropy is usually -action_dim
        self.target_entropy = -float(self.action_dim) # Ensure it's float
        logger.info(f"SAC Target Entropy: {self.target_entropy}")

        if self.learn_alpha:
            self.log_alpha = torch.tensor(np.log(self.hyperparams.alpha.initial_value), requires_grad=True, device=self.device, dtype=torch.float32)
            self.alpha_optimizer = optim.Adam([self.log_alpha], lr=self.hyperparams.alpha.lr)
            self.alpha = self.log_alpha.exp().item()
        else:
            self.alpha = self.hyperparams.alpha.initial_value
            self.log_alpha = torch.tensor(np.log(self.alpha), device=self.device, dtype=torch.float32) # Keep it as a tensor

        # Replay memory
        self.memory = ReplayBuffer(
            buffer_size=self.hyperparams.replay_buffer.buffer_size,
            batch_size=self.hyperparams.replay_buffer.batch_size,
            device=self.device,
            seed=self.seed)

        self.t_step = 0
        self.total_env_steps = 0
        self.total_updates_counter = 0

        self.actor_loss_val = 0.0
        self.critic1_loss_val = 0.0
        self.critic2_loss_val = 0.0
        self.critic_loss_val = 0.0 # For combined plotting
        self.alpha_loss_val = 0.0

        if model_load_path:
            self.load_state(model_load_path)

    # Abstract method overwrite [Private]
    def _create_actor(self, actor_model_class: BaseActor):
        self.actor_local        = actor_model_class(self.state_dim, self.action_dim, seed=self.seed, for_sac=True).to(self.device) # Ensure for_sac=True
        self.actor_optimizer    = optim.Adam(self.actor_local.parameters(), lr=self.hyperparams.actor.lr)

    def _create_critic(self, critic_model_class: BaseCritic):
        state_dim = self.state_dim
        action_dim = self.action_dim

        # -> Critic #1
        self.critic1_local      = critic_model_class(state_dim, action_dim, seed=self.seed).to(self.device)
        self.critic1_target     = critic_model_class(state_dim, action_dim, seed=self.seed).to(self.device)
        self.critic1_optimizer  = optim.Adam(self.critic1_local.parameters(), lr=self.hyperparams.critic.lr,
                                           weight_decay=self.hyperparams.critic.weight_decay)
        self.hard_update(self.critic1_local, self.critic1_target)

        # -> Critic #2
        self.critic2_local  = critic_model_class(state_dim, action_dim, seed=self.seed + 1 ).to(self.device)
        self.critic2_target = critic_model_class(state_dim, action_dim, seed=self.seed + 1 ).to(self.device)

        self.critic2_optimizer = optim.Adam(self.critic2_local.parameters(), lr=self.hyperparams.critic.lr,
                                           weight_decay=self.hyperparams.critic.weight_decay)
        self.hard_update(self.critic2_local, self.critic2_target)

    # Abstract method overwrite [Public]
    def step(self, state: np.ndarray, action: np.ndarray, reward: float, next_state: np.ndarray, done: bool, info: dict| None = None):
        self.memory.add(state, action, reward, next_state, done)
        self.total_env_steps += 1

        self.t_step = (self.t_step + 1) % self.hyperparams.agent.update_every
        if self.t_step == 0:
            if len(self.memory) >= self.hyperparams.replay_buffer.batch_size and self.total_env_steps > self.hyperparams.agent.initial_random_steps:
                experiences = self.memory.sample()
                if experiences:
                    self.learn(experiences, self.hyperparams.agent.gamma)

    def select_action(self, state: np.ndarray, add_noise: bool = True, evaluate: bool = False) -> np.ndarray:
        state_tensor = torch.from_numpy(state).float().unsqueeze(0).to(self.device)

        if add_noise and self.total_env_steps < self.hyperparams.agent.initial_random_steps:
            action = np.random.uniform(-1.0, 1.0, self.action_dim)
            return action.astype(np.float32)

        self.actor_local.eval()
        with torch.no_grad():
            if evaluate: # During evaluation, typically use the squashed mean
                 _, _, action_mean_squashed = self._get_action_log_prob(state_tensor)
                 action_np = action_mean_squashed.cpu().data.numpy().flatten()
            else: # Sample for exploration during training steps
                action_tensor, _, _ = self._get_action_log_prob(state_tensor)
                action_np = action_tensor.cpu().data.numpy().flatten()
        self.actor_local.train()

        return action_np.astype(np.float32)

    def learn(self, experiences: ExperienceBatch, gamma: float):

        self.total_updates_counter += 1

        # ---------------------------- Update Critic Networks ---------------------------- #
        with torch.no_grad():
            next_actions_sampled, next_log_probs, _ = self._get_action_log_prob(experiences.next_states)
            Q1_targets_next = self.critic1_target(experiences.next_states, next_actions_sampled)
            Q2_targets_next = self.critic2_target(experiences.next_states, next_actions_sampled)
            Q_targets_next_min = torch.min(Q1_targets_next, Q2_targets_next) - self.alpha * next_log_probs
            Q_targets = experiences.rewards + (gamma * Q_targets_next_min * (1 - experiences.dones))

        # Critic 1 Loss
        Q1_expected = self.critic1_local(experiences.states, experiences.actions)
        critic1_loss = F.mse_loss(Q1_expected, Q_targets)
        self.critic1_optimizer.zero_grad()
        critic1_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.critic1_local.parameters(), 1.0)
        self.critic1_optimizer.step()
        self.critic1_loss_val = critic1_loss.item()

        # Critic 2 Loss
        Q2_expected = self.critic2_local(experiences.states, experiences.actions)
        critic2_loss = F.mse_loss(Q2_expected, Q_targets)
        self.critic2_optimizer.zero_grad()
        critic2_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.critic2_local.parameters(), 1.0)
        self.critic2_optimizer.step()
        self.critic2_loss_val = critic2_loss.item()

        self.critic_loss_val = (self.critic1_loss_val + self.critic2_loss_val) / 2.0

        # ---------------- Delayed Actor and Alpha Updates ------------------- #
        if self.total_updates_counter % self.hyperparams.agent.policy_update_freq == 0:
            # Actor Update
            actions_pred_sampled, log_probs_pred, _ = self._get_action_log_prob(experiences.states) # Resample actions for actor update
            Q1_pred_for_actor = self.critic1_local(experiences.states, actions_pred_sampled)
            Q2_pred_for_actor = self.critic2_local(experiences.states, actions_pred_sampled)
            Q_pred_min_for_actor = torch.min(Q1_pred_for_actor, Q2_pred_for_actor)

            actor_loss = (self.alpha * log_probs_pred - Q_pred_min_for_actor).mean()
            self.actor_optimizer.zero_grad()
            actor_loss.backward()
            self.actor_optimizer.step()
            self.actor_loss_val = actor_loss.item()

            # Alpha (Entropy Temperature) Update
            if self.learn_alpha:
                # Use the same log_probs_pred, but detach them as they are not part of alpha's gradient path here
                alpha_loss = -(self.log_alpha.exp() * (log_probs_pred.detach() + self.target_entropy)).mean()
                self.alpha_optimizer.zero_grad()
                alpha_loss.backward()
                self.alpha_optimizer.step()
                self.alpha = self.log_alpha.exp().item()
                self.alpha_loss_val = alpha_loss.item()

            # Soft update target critic networks
            self.soft_update(self.critic1_local, self.critic1_target, self.hyperparams.agent.tau)
            self.soft_update(self.critic2_local, self.critic2_target, self.hyperparams.agent.tau)

    # Helper Methods
    def _get_action_log_prob(self, state) -> Tuple[torch.Tensor, ...]:
        mean, log_std = self.actor_local(state) # Actor directly returns mean and log_std
        std = log_std.exp()

        normal_dist = torch.distributions.Normal(mean, std)
        x_t = normal_dist.rsample()  # Reparameterization trick: sample from N(0,1) then scale and shift
        y_t = torch.tanh(x_t)     # Squash action to [-1, 1] action space
        action = y_t

        # Calculate log_prob, accounting for the tanh squashing
        # log_prob = normal_dist.log_prob(x_t) - torch.log(1 - y_t.pow(2) + epsilon)
        # More stable:
        log_prob = normal_dist.log_prob(x_t)
        log_prob -= torch.log((1 - y_t.pow(2)) + 1e-6) # Add epsilon for numerical stability
        log_prob = log_prob.sum(dim=1, keepdim=True)

        mean_squashed = torch.tanh(mean) # Squashed mean for deterministic evaluation
        return action, log_prob, mean_squashed
