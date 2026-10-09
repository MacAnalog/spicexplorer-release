"""A transfer function must say when devices were silently left out of it (TF-02).

`small_signal_model` records every device no registered model could expand in
`SmallSignalIR.unmodelled` and logs a warning — but the value stopped there. The convenience API
returned a `TransferFunctionResult` with no trace of it, so a caller holding an H(s) built from a
circuit with dropped branches could not tell it apart from a complete one. A log line in a busy
optimizer run is not a signal anyone reads.

The value is now carried MnaSystem -> RawTransferFunction -> TransferFunctionResult.
"""

from __future__ import annotations

from spicexplorer_netlist2tf import transfer_function

# A resistive divider (fully modelled) plus a switch, a device kind no small-signal model claims.
# Its control terminals reuse existing nodes so that dropping it leaves no floating net — the
# point is a circuit that still solves while being quietly incomplete.
DECK_WITH_UNMODELLED = """* divider with an unmodellable device on the output
R1 in out 1k
R2 out 0 1k
S1 out 0 in 0 sw_model
.end
"""

DECK_CLEAN = """* the same divider, every device modelled
R1 in out 1k
R2 out 0 1k
.end
"""


def test_result_surfaces_the_dropped_device():
    result = transfer_function(DECK_WITH_UNMODELLED, ("out", "0"), ("in", "0"))
    assert result.unmodelled == ["S1"], (
        "the transfer function was returned with no indication that S1 was dropped"
    )


def test_clean_circuit_reports_nothing_dropped():
    result = transfer_function(DECK_CLEAN, ("out", "0"), ("in", "0"))
    assert result.unmodelled == []


def test_the_incomplete_and_complete_results_are_distinguishable():
    """The whole point: the two H(s) are identical, so the field is the only difference."""
    incomplete = transfer_function(DECK_WITH_UNMODELLED, ("out", "0"), ("in", "0"))
    complete = transfer_function(DECK_CLEAN, ("out", "0"), ("in", "0"))
    assert incomplete.tf_exact_expr == complete.tf_exact_expr
    assert incomplete.unmodelled != complete.unmodelled


def test_the_field_survives_serialization():
    """An agent reading the JSON contract must see it too."""
    result = transfer_function(DECK_WITH_UNMODELLED, ("out", "0"), ("in", "0"))
    assert result.model_dump()["unmodelled"] == ["S1"]
