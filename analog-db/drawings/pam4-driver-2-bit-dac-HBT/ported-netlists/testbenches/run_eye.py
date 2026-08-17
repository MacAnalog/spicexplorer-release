"""48 GBaud PAM-4 eye on the combined (pam4) DUT -> results/pam4_eye.png
plus level/eye metrics in results/pam4_eye_metrics.yaml.

Same stimulus as the EIC reference: seed-7 random MSB/LSB streams, 120
symbols, 200 mV input swing, 4 ps edges.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml

from driver_lib import run_eye

RESULTS = Path(__file__).parent.parent / "results"
RESULTS.mkdir(exist_ok=True)

BAUD = 48e9
NSYM = 120

random.seed(7)
msb_bits = [random.randint(0, 1) for _ in range(NSYM)]
lsb_bits = [random.randint(0, 1) for _ in range(NSYM)]

t, vout, t0_ns, baud, log = run_eye(msb_bits=msb_bits, lsb_bits=lsb_bits,
                                    baud_hz=BAUD, vswing_mv=200.0)
if t is None:
    print("FAILED"); print(log[-1500:]); sys.exit(1)

T = 1.0 / baud
t_an0 = t0_ns * 1e-9 + 6 * T          # discard first symbols (settling)
m = t >= t_an0
tt, vv = t[m], vout[m]
phase = (tt - t_an0) % (2 * T)        # fold into a 2-UI window

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(phase * 1e12, vv, ",", color="navy", alpha=0.3)
ax.set_xlabel("time within 2 UI [ps]")
ax.set_ylabel("V_out differential [V]")
ax.set_title(f"PAM-4 output eye @ {baud/1e9:.0f} GBaud (200 mV input)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(RESULTS / "pam4_eye.png", dpi=130)

# --- level statistics at the sampling instant (center of UI) ---------------
center = T
win = (phase > center - 0.08 * T) & (phase < center + 0.08 * T)
samp = np.sort(vv[win])

# cluster samples into the 4 PAM levels by the 3 largest gaps
gaps = np.diff(samp)
cut_idx = np.sort(np.argsort(gaps)[-3:])
groups = np.split(samp, cut_idx + 1)
levels = [float(np.mean(g)) for g in groups]
eyes = [float(groups[i+1].min() - groups[i].max()) for i in range(3)]
amps = np.diff(levels)
metrics = {
    "baud_ghz": BAUD / 1e9,
    "n_symbols": NSYM,
    "vin_swing_mv": 200.0,
    "vout_pp_v": round(float(vv.max() - vv.min()), 3),
    "levels_v": [round(x, 3) for x in levels],
    "eye_openings_v": [round(x, 3) for x in eyes],
    # PAM-4 level-separation mismatch ratio (IEEE 802.3): 3*min/avg spacing
    "rlm": round(float(3 * amps.min() / amps.sum()), 3),
}
(RESULTS / "pam4_eye_metrics.yaml").write_text(
    yaml.dump(metrics, sort_keys=False))
print(yaml.dump(metrics, sort_keys=False))
print(f"eye PNG: {RESULTS/'pam4_eye.png'}")
