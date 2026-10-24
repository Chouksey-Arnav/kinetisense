# web/

Streamlit web viewer that replays finished throws: metrics table, per-throw graph, multi-throw comparison, and an About and Limits page. It only displays data. Peaks, magnitudes and clipped flags are computed in `ml/` and arrive as finished columns in the data files.

## Run locally

```
cd web
pip install -r requirements.txt
streamlit run app.py
```

## Data

`sample_data/demo_throws.csv` and `sample_data/demo_samples.csv` are synthetic stand-in data made by `tools/make_demo_data.py`. They are not a real recording. The app shows a DEMO DATA banner while `DATA_IS_SYNTHETIC = True` in `app.py`.

## Swap day (when real data exists)

1. Replace the two CSV files, keeping the same column names.
2. Set `DATA_IS_SYNTHETIC = False` only if the data is truly real.
3. Restart the app. The app caches the files and will keep showing old numbers otherwise.

## Limits

Forearm angular velocity only. The 4000 deg/s line is the datasheet range per axis. The real saturation level on the device is not yet verified.
