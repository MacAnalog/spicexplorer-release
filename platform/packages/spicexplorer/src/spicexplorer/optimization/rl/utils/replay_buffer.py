import logging
import random
from collections import deque, namedtuple
from typing import Any, Dict, Optional

import numpy as np
import torch

from .typing import ExperienceBatch

logger = logging.getLogger("SpiceXplorer")

class ReplayBuffer:
    """Fixed-size buffer to store experience tuples."""

    def __init__(self, buffer_size: int, batch_size: int, device: torch.device, seed: int = 0):
        """
        Initialize a ReplayBuffer object.
        Args:
            buffer_size (int): maximum size of buffer
            batch_size (int): size of each training batch
            device (torch.device): cuda or cpu
            seed (int): random seed
        """
        self.memory = deque(maxlen=buffer_size)
        self.batch_size = batch_size
        self.experience = namedtuple("Experience", field_names=["state", "action", "reward", "next_state", "done", "info"])
        self.device = device
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        logger.info(f"Replay buffer initialized with size {buffer_size} and batch size {batch_size}")


    def add(self, state: np.ndarray, action: np.ndarray, reward: float, next_state: np.ndarray, done: bool, info: Optional[Dict[str, Any]] = None):
        """Add a new experience to memory."""
        e = self.experience(state, action, reward, next_state, done, info)
        self.memory.append(e)

    def sample(self):
        """Randomly sample a batch of experiences from memory."""
        if len(self.memory) < self.batch_size:
            logger.debug("Not enough samples in replay buffer to sample.")
            return None

        experiences = random.sample(self.memory, k=self.batch_size)

        # Convert to PyTorch tensors
        states      = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float().to(self.device)
        actions     = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).float().to(self.device)
        rewards     = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(self.device)
        next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float().to(self.device)
        dones       = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float().to(self.device)

        return ExperienceBatch(states, actions, rewards, next_states, dones)

    def __len__(self):
        """Return the current size of internal memory."""
        return len(self.memory)
