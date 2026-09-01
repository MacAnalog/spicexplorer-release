"""Engine-neutral measurement library.

Canonical, version-controlled definitions of the analog figures of merit computed from a
:class:`~spicexplorer_core.spice_engine.protocol.SimResult` — **the same math for ngspice
and Spectre**. Two layers:

* :mod:`~spicexplorer_core.measurements.waveforms` — pure ``numpy`` math over raw arrays
  (DC gain / UGF / phase margin / f\\ :sub:`3dB` / GBW / settling / slew / integrated
  noise). No simulator coupling; unit-tested against synthetic transfer functions.
* :mod:`~spicexplorer_core.measurements.registry` — maps a declarative ``{meas: …}``
  recipe to the right ``SimResult`` signals and evaluates the math (:func:`measure`),
  with load-time recipe validation (:func:`validate_recipe`).

The optimizer's Tier-1 path (``optimization/measure_integration.py``) merges these values
into each result under the target-spec name, so the scorer seam
(``result.scalar(name, analysis)``) is unchanged.
"""

from spicexplorer_core.measurements.registry import (
    known_measurements,
    measure,
    validate_recipe,
)
from spicexplorer_core.measurements.waveforms import (
    band_worst_db,
    bandwidth_3db,
    dc_gain_db,
    dc_gain_linear,
    gain_bandwidth_product,
    gain_margin_db,
    harmonic_amplitudes,
    hd_ratio,
    icmr_band,
    iip3_from_harmonics,
    iip3_from_two_tone,
    integrated_noise,
    level_crossing_freq,
    magnitude_at_db,
    magnitude_db,
    phase_margin,
    phase_noise_dbc,
    rejection_db,
    settling_time,
    sfdr_from_harmonics,
    slew_rate,
    spot_noise_density,
    thd_from_harmonics,
    thd_from_waveform,
    two_tone_indices,
    unity_gain_freq,
)

__all__ = [
    # registry
    "measure",
    "validate_recipe",
    "known_measurements",
    # waveform math
    "magnitude_db",
    "dc_gain_db",
    "dc_gain_linear",
    "rejection_db",
    "icmr_band",
    "two_tone_indices",
    "iip3_from_harmonics",
    "iip3_from_two_tone",
    "unity_gain_freq",
    "phase_margin",
    "gain_margin_db",
    "bandwidth_3db",
    "gain_bandwidth_product",
    "magnitude_at_db",
    "band_worst_db",
    "level_crossing_freq",
    "settling_time",
    "slew_rate",
    "integrated_noise",
    "spot_noise_density",
    "phase_noise_dbc",
    "harmonic_amplitudes",
    "thd_from_waveform",
    "thd_from_harmonics",
    "hd_ratio",
    "sfdr_from_harmonics",
]
