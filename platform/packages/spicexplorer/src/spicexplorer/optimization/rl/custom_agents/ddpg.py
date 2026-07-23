import logging
from typing import Optional

import numpy as np
import torch
import torch.nn.functional as F
import torch.optim as optim

from ..models.actor import MLPActor
from ..models.base import BaseActor, BaseCritic
from ..models.critic import MLPCritic
from ..utils.hyperparameters import DDPGConfig
from ..utils.replay_buffer import ReplayBuffer
from ..utils.typing import ExperienceBatch
from ..utils.utils import trunc_normal
from .base import BaseActorCriticRLAgent

# ------------------ Module Logger ------------------

logger = logging.getLogger("spicexplorer.optimization.rl.agents.ddpg")

# ------------------ Classes ------------------

class DDPGAgent(BaseActorCriticRLAgent):
    """Interacts with and learns from the environment using DDPG."""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        actor_model_class: MLPActor,
        critic_model_class: MLPCritic,
        hyperparams: DDPGConfig,
        device: torch.device,
        seed: int = 0,
        model_load_path: Optional[str] = None,
    ):
        """
        Initialize an Agent object.
        """
        super().__init__(state_dim, action_dim, hyperparams, device, seed)
        self.hyperparams = hyperparams

        logger.info(f"DDPG Agent Initializing with seed: {self.seed}")
        logger.info(f"Using device: {self.device}")

        # Initialize time step (for updating every UPDATE_EVERY steps)
        self.t_step = 0

        # Actor Network (w/ Target Network)
        self._create_actor(actor_model_class=actor_model_class)

        # Critic Network (w/ Target Network)
        self._create_critic(critic_model_class=critic_model_class)

        # Noise process
        self.current_noise_sigma = self.hyperparams.noise.sigma_initial

        # Replay memory
        self.memory = ReplayBuffer(
            hyperparams.memory.buffer_size,
            hyperparams.memory.batch_size,
            self.device,
            self.seed,
        )

        # Populate models and optimizers for state saving/loading
        self._configure_model_save()

        if model_load_path:
            try:
                self.load_state(model_load_path)
            except FileNotFoundError:
                logger.warning("No agent state files found. Agent will start fresh.")

    # Abstract method overwrite [Private]
    def _create_actor(self, actor_model_class: BaseActor):
        self.actor_local : BaseActor = actor_model_class(
            self.state_dim, self.action_dim, seed=self.seed, hyperparams=self.hyperparams.actor
        ).to(self.device)

        self.actor_target : BaseActor = actor_model_class(
            self.state_dim, self.action_dim, seed=self.seed, hyperparams=self.hyperparams.actor
        ).to(self.device)

        # Create optimizer
        self.actor_optimizer = optim.Adam(
            self.actor_local.parameters(), lr=self.hyperparams.actor.lr
        )
        self.hard_update(self.actor_local, self.actor_target)

    def _create_critic(self, critic_model_class: BaseCritic):

        self.critic_local : BaseCritic = critic_model_class(
            self.state_dim, self.action_dim, seed=self.seed, hyperparams=self.hyperparams.critic
        ).to(self.device)

        self.critic_target : BaseCritic = critic_model_class(
            self.state_dim, self.action_dim, seed=self.seed, hyperparams=self.hyperparams.critic
        ).to(self.device)

        self.critic_optimizer = optim.Adam(
            self.critic_local.parameters(),
            lr=self.hyperparams.critic.lr,
            weight_decay=self.hyperparams.critic.weight_decay,
        )
        self.hard_update(self.critic_local, self.critic_target)

    def _configure_model_save(self):
        self.models = {
            "actor_local": self.actor_local,
            "actor_target": self.actor_target,
            "critic_local": self.critic_local,
            "critic_target": self.critic_target,
        }
        self.optimizers = {
            "actor_optimizer": self.actor_optimizer,
            "critic_optimizer": self.critic_optimizer,
        }
        self.agent_var_keys = ["total_env_steps", "current_noise_sigma", "t_step"]

    # Abstract method overwrite [Public]
    def step(
        self,
        state: np.ndarray,
        action: np.ndarray,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        info: Optional[dict] = None,
    ):
        """Save experience in replay memory, and use random sample from buffer to learn."""
        self.memory.add(state, action, reward, next_state, done, info)
        self.total_env_steps += 1

        self.t_step = (self.t_step + 1) % self.hyperparams.training.update_every
        if self.t_step == 0:
            if (
                len(self.memory) >= self.hyperparams.memory.batch_size
                and self.total_env_steps
                > self.hyperparams.training.initial_random_steps
            ):
                experiences = self.memory.sample()
                if experiences:
                    self.learn(experiences, self.hyperparams.training.gamma)

    def select_action(self, state: np.ndarray, add_noise: bool = True) -> np.ndarray:
        """Returns actions for given state as per current policy."""
        state_tensor = torch.from_numpy(state).float().unsqueeze(0).to(self.device)

        if (
            add_noise
            and self.total_env_steps
            < self.hyperparams.training.initial_random_steps
        ):
            action = np.random.uniform(-1.0, 1.0, self.action_dim)
            return action.astype(np.float32)

        self.actor_local.eval()
        with torch.no_grad():
            action = self.actor_local(state_tensor).cpu().data.numpy().flatten()
        self.actor_local.train()

        if add_noise:
            if self.hyperparams.noise.type == "uniform":
                noise_val = np.random.uniform(
                    -self.current_noise_sigma, self.current_noise_sigma, self.action_dim
                )
                action = action + noise_val
            elif self.hyperparams.noise.type == "truncnorm":
                action = trunc_normal(
                    action, self.current_noise_sigma, low=-1.0, high=1.0
                )
            elif self.hyperparams.noise.type == "gaussian":
                noise_val = np.random.normal(
                    0, self.current_noise_sigma, size=self.action_dim
                )
                action = action + noise_val

            action = np.clip(action, -1.0, 1.0)

            self.current_noise_sigma = max(
                self.hyperparams.noise.sigma_min,
                self.current_noise_sigma * self.hyperparams.noise.sigma_decay,
            )

        return action.astype(np.float32)

    def learn(self, experiences: ExperienceBatch, gamma: float):

        # Update critic
        actions_next    = self.actor_target(experiences.next_states)
        Q_targets_next  = self.critic_target(experiences.next_states, actions_next)
        Q_targets       = experiences.rewards + (gamma * Q_targets_next * (1 - experiences.dones))
        Q_expected      = self.critic_local(experiences.states, experiences.actions)

        critic_loss = F.mse_loss(Q_expected, Q_targets)

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        torch.nn.utils.clip_grad_norm_(
            self.critic_local.parameters(), self.hyperparams.critic.grad_clip
        )
        self.critic_optimizer.step()

        # Update actor
        actions_pred = self.actor_local(experiences.states)
        actor_loss = -self.critic_local(experiences.states, actions_pred).mean()
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # Update target networks
        self.soft_update(
            self.critic_local, self.critic_target, self.hyperparams.training.tau
        )
        self.soft_update(
            self.actor_local, self.actor_target, self.hyperparams.training.tau
        )

        self.actor_loss_val = actor_loss.item()
        self.critic_loss_val = critic_loss.item()
