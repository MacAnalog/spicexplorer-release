from enum import Enum


# --------------------------------------------
# General
# --------------------------------------------
class NoiseType(Enum):
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"

# --------------------------------------------
# Custom RL Specific
# --------------------------------------------

class ActorCriticType(Enum):
    MLP = "mlp"
    CNN = "cnn"
    RNN = "rnn"
    GAT = "gat"
    GCN = "gcn"

class ReplayBufferType(Enum):
    STANDARD = "standard"
    PRIORITIZED = "prioritized"

class ExplorationStrategy(Enum):
    EPSILON_GREEDY = "epsilon_greedy"
    NOISE_ADDITION = "noise_addition"
    PARAMETER_NOISE = "parameter_noise"

