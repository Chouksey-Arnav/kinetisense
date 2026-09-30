"""Synthetic IMU session generator.

BOILERPLATE written by Claude. This is FAKE data, only roughly plausible.
Use it to practice loading, plotting and resampling before real data exists.
Never use it to evaluate a detector or to make any claim about throwing.

Writes three files:
  synthetic_1000hz.csv  the sensor you are buying (fast)
  synthetic_100hz.csv   like a phone: every 10th sample, jittery timestamps
  synthetic_events.csv  ground truth: when each event happened and its true peak

Columns: time_s, gx, gy, gz (deg/s), ax, ay, az (g)
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

GYRO_LIMIT_DPS = 4000  # ICM-20649 top range (to verify against the datasheet)
ACCEL_LIMIT_G = 30


def pulse(t, center, sigma):
    return np.exp(-0.5 * ((t - center) / sigma) ** 2)


def make_session(duration_s=60, fs=1000, n_throws=8, n_swings=8, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(0, duration_s, 1 / fs)
    n = len(t)

    # Background: slow walking sway plus sensor noise, gravity on z.
    sway = np.sin(2 * np.pi * 1.9 * t)[:, None]
    gyro = 40 * sway * rng.uniform(0.5, 1, 3) + rng.normal(0, 3, (n, 3))
    accel = np.array([0, 0, 1.0]) + 0.3 * sway * rng.uniform(0.5, 1, 3)
    accel = accel + rng.normal(0, 0.02, (n, 3))

    events = []
    throw_times = np.linspace(5, duration_s - 5, n_throws) + rng.uniform(-1, 1, n_throws)
    swing_times = throw_times + (duration_s / n_throws) / 2  # halfway between throws

    for label, times in (("throw", throw_times), ("not_throw", swing_times)):
        for c in times:
            if label == "throw":
                peak, sigma = rng.uniform(1500, 5500), 0.008  # short and violent (width is a guess, verify with real data)
            else:
                peak, sigma = rng.uniform(300, 900), 0.15  # slow arm swing
            direction = rng.normal(size=3)
            direction[0] += 2  # mostly one axis, like a real forearm
            direction /= np.linalg.norm(direction)
            p = pulse(t, c, sigma)[:, None]
            gyro += peak * p * direction
            accel += 25 * (peak / 2000) ** 2 * p * direction  # roughly omega squared
            events.append({"event_time_s": c, "label": label, "true_peak_dps": peak})

    gyro = np.clip(gyro, -GYRO_LIMIT_DPS, GYRO_LIMIT_DPS)  # sensor saturates per axis
    accel = np.clip(accel, -ACCEL_LIMIT_G, ACCEL_LIMIT_G)

    cols = ["gx", "gy", "gz", "ax", "ay", "az"]
    full = pd.DataFrame(np.hstack([gyro, accel]), columns=cols)
    full.insert(0, "time_s", t)

    # Phone-like: decimate WITHOUT filtering, and report jittery timestamps.
    phone = full.iloc[:: fs // 100].copy()
    phone["time_s"] = np.sort(phone["time_s"] + rng.normal(0, 0.002, len(phone)))
    return full, phone, pd.DataFrame(events).sort_values("event_time_s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/synthetic")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    full, phone, events = make_session(seed=args.seed)
    full.to_csv(out / "synthetic_1000hz.csv", index=False)
    phone.to_csv(out / "synthetic_100hz.csv", index=False)
    events.to_csv(out / "synthetic_events.csv", index=False)
    print(f"wrote {len(full)} rows at 1000 Hz, {len(phone)} rows at 100 Hz, {len(events)} events to {out}")
