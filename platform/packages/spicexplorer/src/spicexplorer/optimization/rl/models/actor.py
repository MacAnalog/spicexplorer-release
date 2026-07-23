import torch.nn as nn
import torch.nn.functional as F

from ..utils.hyperparameters import DDPGConfig
from .base import BaseActor


# ------------------------
# Multi-Layer Perceptron Actor Model
# ------------------------
class MLPActor(BaseActor):
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        seed: int,
        hyperparams: DDPGConfig,
    ):
        super().__init__(state_dim, action_dim, seed, hyperparams)
        hidden_units = hyperparams.actor.hidden_units

        layers = []
        input_dim = state_dim
        for hidden_dim in hidden_units:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        layers.append(nn.Linear(input_dim, action_dim))

        self.network = nn.Sequential(*layers)
        self.network.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            nn.init.xavier_uniform_(m.weight)
            nn.init.constant_(m.bias, 0)

    def forward(self, state):
        return F.tanh(self.network(state))


# ------------------------

