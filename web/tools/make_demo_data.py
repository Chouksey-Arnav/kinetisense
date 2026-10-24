"""Builds contract-format demo files (throws + samples) matching the KinetiSense data contract.
Throws 1 and 5 have one axis pinned at 4000 (truly clipped). Throw 4 peaks at 4901.2 with NO axis clipped.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)

peak_t = [5.394, 11.929, 18.971, 27.121, 33.459, 39.862, 47.738, 54.171]
peak_v = [4338.3, 2149.5, 2981.6, 4901.2, 4080.4, 3134.1, 4537.2, 4120.5]
clipped = [True, False, False, False, True, False, False, False]

rows, throws = [], []
for i, (pt, pv, cl) in enumerate(zip(peak_t, peak_v, clipped), start=1):
    if cl:
        gx = 4000.0
        rest = np.sqrt(pv**2 - gx**2)
        base = np.array([gx, rest * 0.8, rest * 0.6])
    else:
        u = np.array([0.55, 0.65, 0.52]); u /= np.linalg.norm(u)
        base = pv * u
    k = np.arange(-500, 501)
    t = np.round(pt + k / 1000, 3)
    pulse = np.exp(-0.5 * (k / 1000 / 0.03) ** 2)[:, None]
    g = base * pulse
    a = np.tile([0.0, 0.0, 1.0], (len(k), 1)) + 0.01 * pulse
    mag = np.sqrt((g ** 2).sum(axis=1))
    df = pd.DataFrame({"throw_id": i, "time_s": t, "gx": g[:, 0], "gy": g[:, 1], "gz": g[:, 2],
                       "ax": a[:, 0], "ay": a[:, 1], "az": a[:, 2], "gyro_mag": mag}).round(3)
    rows.append(df)
    throws.append({"throw_id": i, "peak_time_s": pt, "peak_dps": round(float(df.gyro_mag.max()), 1), "clipped": cl})

pd.concat(rows, ignore_index=True).to_csv(out / "demo_samples.csv", index=False)
pd.DataFrame(throws).to_csv(out / "demo_throws.csv", index=False)
print(pd.DataFrame(throws).to_string(index=False))
