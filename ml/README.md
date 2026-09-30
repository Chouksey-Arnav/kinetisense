# ml/

Written by the student. Claude explains, hints and reviews.

## Setup (macOS)

```
cd kinetisense
python3 -m venv .venv
source .venv/bin/activate
pip install -r ml/requirements.txt
jupyter lab
```

## Planned pieces

1. Load and plot raw IMU data (first exercise).
2. Resample to a uniform rate and convert units.
3. Sliding windows and features.
4. Threshold baseline, then a model only if it beats the baseline on held-out sessions.
5. Per-throw metrics with clipping flags.
