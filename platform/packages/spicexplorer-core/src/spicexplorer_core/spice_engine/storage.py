from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

# For typing
from typing import Any, Dict, List, Mapping, Optional

import numpy as np

# For logging
from spicexplorer_core.logging import setup_loggers

logger = logging.getLogger("spicexplorer.spice_engine.storage")

# ---------------------------------
# Enums Definition
# ---------------------------------


# ---------------------------------
# Type Aliases
# ---------------------------------

ParameterSet = Mapping[str, Any]
MetricSet = Mapping[str, float]

# ---------------------------------
# Class Definition
# ---------------------------------

@dataclass
class Spice_Simulation_Point:
    parameters: ParameterSet
    scalarized_metric: float # AKA "fitness" or "objective value"
    metrics: Optional[MetricSet] = None

    def get_metric(self, name: str, default: Optional[float] = None) -> Optional[float]:
        """Safely get a metric value by name."""
        return self.metrics.get(name, default) if self.metrics else default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a serializable dictionary."""
        return {
            "parameters": dict(self.parameters),
            "scalarized_metric": self.scalarized_metric,
            "metrics": dict(self.metrics) if self.metrics else None,
        }

    def __lt__(self, other: "Spice_Simulation_Point"):
        """Compare points by scalarized metric for sorting."""
        return self.scalarized_metric < other.scalarized_metric

    @staticmethod
    def from_dict(data: dict) -> Spice_Simulation_Point:
        """Reconstruct a simulation point from a dictionary."""
        return Spice_Simulation_Point(
            parameters=data.get("parameters", {}),
            scalarized_metric=data.get("scalarized_metric", 0.0),
            metrics=data.get("metrics"),
        )

@dataclass
class Spice_Simulation_Database:
    parameter_names: Optional[List[str]] = None
    metric_names: Optional[List[str]] = None
    points: List[Spice_Simulation_Point] = field(default_factory=list)


    # ---------------------------
    # Validation & Data Integrity
    # ---------------------------
    def _infer_schema(self, point: Spice_Simulation_Point) -> None:
        """Infer parameter and metric schemas from the first point."""
        if self.parameter_names is None:
            self.parameter_names = list(point.parameters.keys())
            logger.info(f"Inferred parameter schema: {self.parameter_names}")
        if self.metric_names is None and point.metrics:
            self.metric_names = list(point.metrics.keys())
            logger.info(f"Inferred metric schema: {self.metric_names}")

    def _validate_point(self, point: Spice_Simulation_Point) -> None:
        """Ensure the point matches the database schema."""
        if self.parameter_names is None:
            self._infer_schema(point)
        if self.metric_names is None and point.metrics:
            self._infer_schema(point)

        param_keys = set(point.parameters.keys())
        metric_keys = set(point.metrics.keys()) if point.metrics else set()

        if set(self.parameter_names) != param_keys: # type: ignore
            logger.error(f"Parameter mismatch. Expected {self.parameter_names}, got {list(param_keys)}")
            raise ValueError(
                f"Parameter mismatch. Expected {self.parameter_names}, got {list(param_keys)}"
            )

        if self.metric_names:
            if metric_keys != set(self.metric_names):
                logger.error(f"Metric mismatch. Expected {self.metric_names}, got {list(metric_keys)}")
                raise ValueError(
                    f"Metric mismatch. Expected {self.metric_names}, got {list(metric_keys)}"
                )

    # ---------------------------
    # Data Management
    # ---------------------------
    def add_point(self, point: Spice_Simulation_Point) -> None:
        """Add a new simulation point after validation."""
        self._validate_point(point)
        self.points.append(point)
        logger.debug(f"Added point with parameters: {point.parameters}")

    def best_point(self) -> Optional[Spice_Simulation_Point]:
        """Return the point with the best (max) scalarized metric."""
        return max(self.points, key=lambda p: p.scalarized_metric, default=None)

    # ---------------------------
    # Serialization
    # ---------------------------
    def to_json(self, filepath: str) -> None:
        """Save the database and schemas to JSON."""
        data = {
            "parameter_names": self.parameter_names or [],
            "metric_names": self.metric_names or [],
            "points": [p.to_dict() for p in self.points],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(self.points)} simulation points to {filepath}")

    @classmethod
    def load_json(cls, filepath: str) -> Spice_Simulation_Database:
        """Load a database from JSON."""
        with open(filepath, "r") as f:
            data = json.load(f)

        if "points" not in data:
            raise ValueError(f"Invalid database format in {filepath}")

        db = cls(
            parameter_names=data.get("parameter_names"),
            metric_names=data.get("metric_names"),
        )
        db.points = [Spice_Simulation_Point.from_dict(p) for p in data["points"]]
        logger.info(f"Loaded {len(db.points)} points from {filepath}")
        return db

    # ---------------------------
    # Conversion Utilities
    # ---------------------------
    def to_numpy(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convert parameters, scalarized metrics, and individual metrics to numpy arrays."""
        if not self.parameter_names:
            raise ValueError("Parameter schema undefined — cannot convert to numpy.")

        param_matrix, metric_matrix = [], []

        for p in self.points:
            ordered_params = [p.parameters[name] for name in self.parameter_names]
            param_matrix.append(ordered_params)

            if self.metric_names and p.metrics:
                ordered_metrics = [p.metrics.get(name, np.nan) for name in self.metric_names]
                metric_matrix.append(ordered_metrics)
            else:
                metric_matrix.append([np.nan] * len(self.metric_names or []))

        scalars = [p.scalarized_metric for p in self.points]
        return np.array(param_matrix), np.array(metric_matrix), np.array(scalars)

# ---------------------------------
# Example Usage
# ---------------------------------
if __name__ == "__main__":
    logger = setup_loggers()
    logger.info("You are in the spicelib.storage module")

    # User does not specify schema — it will be inferred from the first point
    db = Spice_Simulation_Database()

    p1 = Spice_Simulation_Point(
        parameters={"W": 1e-6, "L": 0.18e-6},
        scalarized_metric=0.92,
        metrics={"gain": 60.1, "bandwidth": 2.3e6},
    )
    db.add_point(p1)  # Schema inferred here

    p2 = Spice_Simulation_Point(
        parameters={"W": 2e-6, "L": 0.18e-6},
        scalarized_metric=0.88,
        metrics={"gain": 62.0, "bandwidth": 2.1e6},
    )
    db.add_point(p2)  # Schema enforced here

    logger.info(f"Schema: params={db.parameter_names}, metrics={db.metric_names}")

    db.to_json("sim_db.json")
    db2 = Spice_Simulation_Database.load_json("sim_db.json")
    logger.info(f"Loaded DB schema: params={db2.parameter_names}, metrics={db2.metric_names}")
