# Target Specs to Beat

> **Note:** The figures below are **target / aspirational** specifications for the optimizer to beat — they are *not* measured SPICE results. No `*__tt.json` measurement artifact is committed under `examples/OTA/`.

## Power Consumption (Total)
| Parameter | Value | Unit |
| :--- | :--- | :--- |
| **$I_{DD}$ Total** | 23.82 | uA |
| **Power Total** | 35.73 | uW |

## Open-Loop Performance
| Parameter | Value | Unit / Condition |
| :--- | :--- | :--- |
| **$G_{max}$** | 46.06 | dB at 1 Hz |
| **DC Gain** | 46.06 | dB at 10 Hz |
| **FBW** | 1.38 | MHz |
| **Unity Gain Phase** | -103.19 | ° |
| **UGF** | 252.81 | MHz |
| **Phase Margin (PM)** | 59.00 | ° |

## Noise
| Parameter | Value | Unit |
| :--- | :--- | :--- |
| **Input Referred Noise ($i_{noise}$)** | 1.19 | m |
| **Output Referred Noise ($o_{noise}$)** | 2.29 | m |

## Transient Response
| Parameter | Value | Unit |
| :--- | :--- | :--- |
| **Settling Time ($t_{settle}$)** | 143.73 | ns |



# Reference
## Phase Margin
| PM | Stability Status | Transient Behavior |
| :--- | :--- | :--- |
| < 30°|Poor| Heavy ringing, potential oscillation.
| 45°| Minimum Acceptable | Significant overshoot, slow to settle.
| 60° (Target) | Ideal | Fast settling, minimal to no overshoot.
| > 75° | Very Stable | Very slow response (sluggish)