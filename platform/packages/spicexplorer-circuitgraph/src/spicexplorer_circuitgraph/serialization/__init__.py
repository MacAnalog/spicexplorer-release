"""Pluggable, comparable serialization strategies — which representation LLMs reason about
best is an open research question, so the views are pluggable and comparable.

``serialize(graph, "net_centric")`` renders a graph through a named strategy; ``list_strategies()``
enumerates them; ``evaluate_strategies(graph)`` ranks them on deterministic metrics. New strategies
register themselves on import (see ``strategies.py``).
"""

from . import strategies as strategies  # noqa: F401 — import for @register side effects
from .base import (
    Serializer,
    all_strategies,
    get_strategy,
    list_strategies,
    register,
    serialize,
    unregister,
)
from .metrics import StrategyMetrics, evaluate_strategies, evaluate_strategy

__all__ = [
    "Serializer",
    "register",
    "unregister",
    "serialize",
    "get_strategy",
    "list_strategies",
    "all_strategies",
    "StrategyMetrics",
    "evaluate_strategies",
    "evaluate_strategy",
]
