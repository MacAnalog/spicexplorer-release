from dataclasses import dataclass, field, fields, is_dataclass
from typing import Tuple, Type, TypeVar

import yaml
from spicexplorer.core.domains import SpiceSimulatorType

from .enums import NoiseType

T = TypeVar("T")

def _from_dict(cls: Type[T], data: dict) -> T:
    """Recursively constructs a dataclass instance from a dictionary."""
    kwargs = {}
    for f in fields(cls):
        if f.name in data:
            if is_dataclass(f.type):
                kwargs[f.name] = _from_dict(f.type, data[f.name])
            else:
                kwargs[f.name] = data[f.name]
    return cls(**kwargs)

@dataclass
class BaseHyperparameters:
    @classmethod
    def from_yaml(cls: Type[T], file_path: str) -> T:
        """Loads hyperparameters from a YAML file."""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return _from_dict(cls, data)

# --------------------------------------------
# Hyperparameters - General
# --------------------------------------------
@dataclass
class NoiseHyperparameters(BaseHyperparameters):
    type: str = NoiseType.GAUSSIAN.value
    sigma_initial: float = 0.2
    sigma_min: float = 0.01
    sigma_decay: float = 0.995

@dataclass
class MemoryHyperparameters(BaseHyperparameters):
    buffer_size: int = 100000
    batch_size: int = 64

@dataclass
class TrainingHyperparameters(BaseHyperparameters):
    gamma: float = 0.99
    tau: float = 0.005
    update_every: int = 1
    initial_random_steps: int = 1000
    policy_update_freq: int = 2


# --------------------------------------------
# Hyperparameters - Models
# --------------------------------------------
@dataclass
class ActorMLPHyperparameters(BaseHyperparameters):
    lr: float = 0.001
    hidden_units: Tuple[int, ...] = (256, 128)

@dataclass
class CriticMLPHyperparameters(BaseHyperparameters):
    lr: float = 0.001
    weight_decay: float = 0.0
    grad_clip: float = 1.0
    hidden_units: Tuple[int, ...] = (256, 128)

# --------------------------------------------
# Hyperparameters - Agent Type
# --------------------------------------------

# [DDPG] Hyperparameters
@dataclass
class DDPGConfig(BaseHyperparameters):
    actor: ActorMLPHyperparameters = field(default_factory=ActorMLPHyperparameters)
    critic: CriticMLPHyperparameters = field(default_factory=CriticMLPHyperparameters)
    noise: NoiseHyperparameters = field(default_factory=NoiseHyperparameters)
    memory: MemoryHyperparameters = field(default_factory=MemoryHyperparameters)
    training: TrainingHyperparameters = field(default_factory=TrainingHyperparameters)

# [SAC] Hyperparameters
@dataclass
class AlphaHyperparameters(BaseHyperparameters):
    """Hyperparameters for the entropy temperature alpha in SAC."""
    learn_alpha: bool = True
    alpha_init: float = 0.2
    lr_alpha: float = 0.0003

@dataclass
class SACConfig(BaseHyperparameters):
    actor: ActorMLPHyperparameters = field(default_factory=ActorMLPHyperparameters)
    critic: CriticMLPHyperparameters = field(default_factory=CriticMLPHyperparameters)
    alpha: AlphaHyperparameters = field(default_factory=AlphaHyperparameters)
    memory: MemoryHyperparameters = field(default_factory=MemoryHyperparameters)
    training: TrainingHyperparameters = field(default_factory=TrainingHyperparameters)


# Environment Hyperparameters
@dataclass
class SpiceSimulatorHyperparameters(BaseHyperparameters):
    simulator_type: str = SpiceSimulatorType.NGSPICE.value
    simulator_bin_path: str = "/usr/bin/ngspice"  # Path to the SPICE simulator executable

@dataclass
class EnvHyperparameters(BaseHyperparameters):
    circuit_netlist_path: str = "path/to/circuit.net"
    param_space_path: str     = "path/to/param_space.yaml"
    target_specs_path: str    = "path/to/target_specs.yaml"

    max_episode_steps: int          = 1000
    normalize_observations: bool    = True
    normalize_actions: bool         = True
    seed: int                       = 23

    simulator_config: SpiceSimulatorHyperparameters = field(default_factory=SpiceSimulatorHyperparameters)
