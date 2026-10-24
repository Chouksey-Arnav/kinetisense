# web/

Streamlit web viewer for Kinetiq that replays finished throws: metrics table, per-throw graph, multi-throw comparison, an Ask AI tab, and an About and Limits page. It only displays data. Peaks, magnitudes and clipped flags are computed in `ml/` and arrive as finished columns in the data files.

## Run locally

```
cd web
pip install -r requirements.txt
streamlit run app.py
```

## Ask AI and the Groq key

The Ask AI tab sends the session's numbers (never names or video) to a model on Groq and shows the answer. All of its code, rules and safety checks are in `ai_coach.py`. Without a key the tab says the AI is off and the rest of the app works normally, offline included.

### Add the key on your own computer (do this)

```
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Open `.streamlit/secrets.toml` and paste the key in place of `gsk_paste_your_key_here`. That file is in `.gitignore`, so git never uploads it. Check with `git status`: it must not show up. Run the app from inside `web/` or Streamlit won't find the file.

Second option: set an environment variable instead (`export GROQ_API_KEY=gsk_...` on Mac). The app checks `secrets.toml` first, then this.

### If you put the app online (Streamlit Community Cloud)

Paste the same `GROQ_API_KEY = "..."` line into the app's Settings, Secrets box. Never commit it. A public link means strangers can use your key, so the app caps questions at 30 per visitor and 200 per hour for everyone (`ai_coach.py`, top of the file). Use a free tier key with no card attached, so the worst case is the AI going quiet, not a bill.

### Rules that matter

- A private repo does not make a committed key safe. Git keeps it in history forever, and judges may ask for the source. If a key ever lands in a commit, delete it in the Groq console and make a new one. `tests/test_ai_coach.py` fails if anything that looks like a Groq key is committed.
- The model's hidden instructions (`SYSTEM_PROMPT`) are not secret from anyone who reads the code. The app blocks answers that repeat them, which keeps the chat on task. Put nothing secret in them.
- The AI is told never to estimate pitch speed, give injury or medical advice, grade throws, or compare to other products. That lowers the risk. It does not make it zero. Run the red team check below before any demo.

### Test it

```
python -m pytest tests          # no key or internet needed (pip install pytest first)
python tools/redteam_ai.py      # real attacks against the real model, needs the key
```

Change the model by adding `GROQ_MODEL = "..."` to `secrets.toml`, then run the red team check again, and update the model name on the About page.

## Logo

`assets/logo.svg` is the wordmark and `assets/mark.svg` is the browser tab icon. Both are drawn from plain shapes, so no font is needed and they stay sharp at any size.

## Data

`sample_data/demo_throws.csv` and `sample_data/demo_samples.csv` are synthetic stand-in data made by `tools/make_demo_data.py`. They are not a real recording. The app shows a DEMO DATA banner while `DATA_IS_SYNTHETIC = True` in `app.py`.

## Swap day (when real data exists)

1. Replace the two CSV files, keeping the same column names.
2. Set `DATA_IS_SYNTHETIC = False` only if the data is truly real.
3. Restart the app. The app caches the files and will keep showing old numbers otherwise.

## Limits

Forearm angular velocity only. The 4000 deg/s line is the datasheet range per axis. The real saturation level on the device is not yet verified.
