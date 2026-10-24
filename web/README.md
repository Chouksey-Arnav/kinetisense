# web/

Streamlit app that shows finished throws in plain language: a Start here page that explains every number, an All throws overview, a One throw page, a Compare page, and an About page. It only displays data. Peaks, magnitudes and clipped flags are computed in `ml/` and arrive as finished columns in the data files.

Claude (AI) wrote this version of the app and its theme. See `AI_USAGE.md`.

## Run locally

```
cd web
pip install -r requirements.txt
streamlit run app.py
```

Run it from inside `web/`. The colors and fonts live in `web/.streamlit/config.toml`, and Streamlit only reads that file from the folder you start in.

## Look and feel

Dark navy canvas and light blue accent from raisedhand.ai. Serif headings, mono labels, pastel stat cards and cream buttons from heylemon.ai. Full spec in `docs/design_system.md`.

## Data

`sample_data/demo_throws.csv` and `sample_data/demo_samples.csv` are synthetic stand-in data made by `tools/make_demo_data.py`. They are not a real recording. The app shows a Demo mode banner while `DATA_IS_SYNTHETIC = True` in `app.py`.

## Swap day (when real data exists)

1. Replace the two CSV files, keeping the same column names.
2. Set `DATA_IS_SYNTHETIC = False` only if the data is truly real.
3. Restart the app. The app caches the files and will keep showing old numbers otherwise.

## Limits

Forearm angular velocity only. The 4000 deg/s line is the datasheet range per axis. The real saturation level on the device is not yet verified.
