# NOTE: `tf_models` (Pole_Zero_TF, …) was once re-exported here. It pulled
# `control` + `sympy` and its exports were unused anywhere, yet importing
# `spicexplorer.core.domains` runs this __init__ — so the re-export dragged those heavy
# deps into every consumer of the DSL (incl. the api's score_service). It was the target-TF
# model set of the Bode optimizer and was deleted with it (retired 2026-09-26).
from .domains import Project_Setup

__all__ = [
    # Domain Classes
    "Project_Setup",
]
