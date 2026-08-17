"""The single Pydantic I/O contract (`TransferFunctionResult`) + its sub-models.

This is the *one* serializable source feeding OpenAPI→TS codegen and the MCP tool schema when the
adapters land (deferred to orchestration). Symbols/expressions are canonical sympy **strings**;
numerics are floats. The result carries BOTH the agent-structured fields (read `tf_simplified_expr`,
`poles[].value_*`, `assumptions_applied[]`, `validation.passed` as data) AND the designer LaTeX/sympy
views (computed lazily from the same canonical fields — not a second source of truth).

`AssumptionApplied` and `ValidationReport` live here too (the one-contract rule); they are populated
by Stage 4 (P5) and remain empty/None on the exact-only path.
"""

from __future__ import annotations

from typing import cast

import sympy as sp
from pydantic import BaseModel, Field

__all__ = [
    "SymbolicValue",
    "ComplexRoot",
    "AssumptionApplied",
    "ValidationReport",
    "TransferFunctionResult",
]


class SymbolicValue(BaseModel):
    """A symbolic quantity with an optional numeric evaluation at an operating point."""

    expr: str  # canonical sympy string, e.g. "-gm_m1*ro_m1"
    latex: str | None = None
    value: float | None = None  # numeric eval at the operating point, if available


class ComplexRoot(BaseModel):
    """A pole or zero — symbolic location plus optional numeric coordinates."""

    expr: str  # symbolic location, e.g. "1/(ro_m1*cl)"
    latex: str | None = None
    value_real: float | None = None  # rad/s
    value_imag: float | None = None
    frequency_hz: float | None = None
    q: float | None = None
    multiplicity: int = 1


class AssumptionApplied(BaseModel):
    """One ordered step in the simplification ledger (Stage 4 / P5)."""

    name: str
    kind: str  # DOMINANCE | SMALLNESS | POLE_SEPARATION | BAND_LIMIT | EQUALITY
    description: str
    condition: str = ""  # symbolic precondition, e.g. "gm_m1*ro_m1 >> 1"
    scope: str = "GLOBAL"  # GLOBAL | DEVICE | SUBEXPR | BAND
    justification: str = ""
    substitution: str | None = None
    dropped_terms: list[str] = Field(default_factory=list)
    order: int = 0
    status: str = "APPLIED"  # APPLIED | REJECTED_NUMERICS | NO_OP | REJECTED_VALIDATION | SUGGESTED
    numeric_ratio: float | None = None
    validated: bool | None = None
    relative_error: float | None = None


class ValidationReport(BaseModel):
    """Exact-vs-simplified numeric error over a frequency sweep (Stage 4 trust gate / P5)."""

    operating_point: dict[str, float] = Field(default_factory=dict)
    freq_hz_min: float | None = None
    freq_hz_max: float | None = None
    num_points: int | None = None
    max_relative_error: float | None = None
    max_magnitude_error_db: float | None = None
    max_phase_error_deg: float | None = None
    passed: bool | None = None
    tolerance: float | None = None
    method: str = "lambdify_numpy"  # "lambdify_numpy" | "ngspice_ac" (gated)
    notes: str | None = None


class TransferFunctionResult(BaseModel):
    """The single I/O contract — agent-structured fields AND designer LaTeX/sympy views."""

    # provenance / what was asked
    name: str = "circuit"
    output_nodes: tuple[str, str]  # (pos, neg); neg an AC ground => single-ended
    input_nodes: tuple[str, str]
    conv_type: str = "se"  # "se" | "diff" | "cm" | "fully_diff"
    model_level: str = "some_parasitic"
    kept_symbolic: list[str] = Field(default_factory=list)
    solve_path: str = "fully_symbolic"
    free_symbols: list[str] = Field(default_factory=list)
    analysis: str = "transfer_function"
    component_tfs: dict[str, str] = Field(default_factory=dict)  # ratio metrics: {"a_dm": "...", ...}

    # the transfer function, exact and simplified
    tf_exact_expr: str
    tf_exact_latex: str | None = None
    tf_simplified_expr: str  # == exact when no assumptions fired / UNREDUCED fallback
    tf_simplified_latex: str | None = None

    # S5 readable parameterization (of the simplified TF)
    dc_gain: SymbolicValue
    poles: list[ComplexRoot] = Field(default_factory=list)
    zeros: list[ComplexRoot] = Field(default_factory=list)
    zpk_latex: str | None = None
    gbw_hz: SymbolicValue | None = None

    # S4 trust surface (P5)
    assumptions_applied: list[AssumptionApplied] = Field(default_factory=list)
    validation: ValidationReport | None = None

    # ---- designer convenience: computed from *_expr, not serialized ----
    def as_sympy(self) -> sp.Expr:
        """The simplified ``H(s)`` as a live sympy expression."""
        return cast("sp.Expr", sp.sympify(self.tf_simplified_expr))

    def as_sympy_exact(self) -> sp.Expr:
        """The exact ``H(s)`` as a live sympy expression."""
        return cast("sp.Expr", sp.sympify(self.tf_exact_expr))

    @property
    def latex(self) -> str:
        """LaTeX of the simplified TF (lazily computed if not already stored)."""
        return self.tf_simplified_latex or sp.latex(self.as_sympy())

    def _repr_latex_(self) -> str:  # Jupyter pretty-print
        return f"$$H(s) = {self.latex}$$"
