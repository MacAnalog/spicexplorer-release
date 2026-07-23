import logging
from abc import ABC, abstractmethod

import torch

from ..utils.hyperparameters import BaseHyperparameters

logger = logging.getLogger("SpiceXplorer")


class BaseActor(torch.nn.Module, ABC):
    """Abstract base class for actor networks."""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        seed: int,
        hyperparams: BaseHyperparameters,
    ) -> None:
        """Initialize the actor network.
        Args:
            state_dim: Dimension of the state space.
            action_dim: Dimension of the action space.
            seed: Random seed.
            hyperparams: Dictionary of hyperparameters.
        """
        super().__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.seed = seed
        self.hyperparams = hyperparams
        torch.manual_seed(seed)

    @abstractmethod
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Define the forward pass of the actor network.
        Args:
            state: Input tensor of states.
        Returns:
            Output tensor of actions.
        """
        raise NotImplementedError


class BaseCritic(torch.nn.Module, ABC):
    """Abstract base class for critic networks."""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        seed: int,
        hyperparams: BaseHyperparameters,
    ) -> None:
        """Initialize the critic network.
        Args:
            state_dim: Dimension of the state space.
            action_dim: Dimension of the action space.
            seed: Random seed.
            hyperparams: Dictionary of hyperparameters.
        """
        super().__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.seed = seed
        self.hyperparams = hyperparams
        torch.manual_seed(seed)

    @abstractmethod
    def forward(self, state: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """Define the forward pass of the critic network.
        Args:
            state: Input tensor of states.
            action: Input tensor of actions.
        Returns:
            Output tensor of Q-values.
        """
        raise NotImplementedError

