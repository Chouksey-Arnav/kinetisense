# A small made-up session for TESTS ONLY. The app itself ships with no data.
# Throw 1 has one axis pinned at 4000 (clipped). Throw 3 peaks above 4000 with no axis clipped.
# Written by Claude (Anthropic). Logged in AI_USAGE.md.
import numpy as np
import pandas as pd


def make_session():
    peak_t = [5.0, 12.0, 19.0, 27.0]
    peak_v = [4338.3, 2149.5, 4901.2, 3134.1]
    clipped = [True, False, False, False]
    rows, throws = [], []
    for i, (pt, pv, cl) in enumerate(zip(peak_t, peak_v, clipped), start=1):
        if cl:
            rest = np.sqrt(pv ** 2 - 4000.0 ** 2)
            base = np.array([4000.0, rest * 0.8, rest * 0.6])
        else:
            u = np.array([0.55, 0.65, 0.52])
            base = pv * u / np.linalg.norm(u)
        k = np.arange(-500, 501)
        pulse = np.exp(-0.5 * (k / 1000 / 0.03) ** 2)[:, None]
        g = base * pulse
        mag = np.sqrt((g ** 2).sum(axis=1))
        rows.append(pd.DataFrame({"throw_id": str(i), "time_s": np.round(pt + k / 1000, 3), "gx": g[:, 0],
                                  "gy": g[:, 1], "gz": g[:, 2], "gyro_mag": mag}).round(3))
        throws.append({"throw_id": str(i), "peak_time_s": pt, "peak_dps": round(float(mag.max()), 1), "clipped": cl})
    throws = pd.DataFrame(throws)
    throws["rank"] = throws.peak_dps.rank(ascending=False, method="min").astype(int)
    return throws, pd.concat(rows, ignore_index=True)
