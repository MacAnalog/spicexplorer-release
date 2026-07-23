import logging

import numpy as np

logger = logging.getLogger("spicexplorer.optimization.rl.utils.utils")

def trunc_normal(mean: np.ndarray, std: float, low: float = -1.0, high: float = 1.0) -> np.ndarray:
    """Generates samples from a truncated normal distribution."""
    logger.debug(f"Generating truncated normal samples with mean {mean}, std {std}, low {low}, high {high}")
    samples = np.random.normal(loc=mean, scale=std, size=mean.shape)
    return np.clip(samples, low, high)
