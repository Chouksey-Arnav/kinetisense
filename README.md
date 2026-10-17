# KinetiSense

A wearable motion tracker for youth and high school baseball pitchers. It straps to the outer forearm and is meant to record forearm angular velocity during throws, then show each throw in a web app.

Built by Arnav Chouksey and Vatsalya Vishnoi for the Congressional App Challenge and eCYBERMISSION.

## Status

Early stage (2026-09-30). Parts are ordered and have not arrived. No real sensor data exists yet. The only data in this repo's tooling is a synthetic generator for practice. Nothing here measures pitch speed, and nothing here has been validated.

## Where to find things

| What | Link |
|---|---|
| How training data is made, labeled and used honestly | [docs/data_plan.md](docs/data_plan.md) |
| Verified facts, corrections, open questions | [docs/verification_log.md](docs/verification_log.md) |
| Every AI contribution, by session | [AI_USAGE.md](AI_USAGE.md) |
| Working rules for the AI coach | [CLAUDE.md](CLAUDE.md) |
| ML and analysis (setup instructions) | [ml/README.md](ml/README.md) |
| Python packages for ML | [ml/requirements.txt](ml/requirements.txt) |
| Practice data generator (fake data) | [ml/tools/make_synthetic_session.py](ml/tools/make_synthetic_session.py) |
| Data folder rules and privacy | [data/README.md](data/README.md) |
| Session metadata template | [data/sessions_template.csv](data/sessions_template.csv) |
| Firmware (Pico 2 W) | [firmware/README.md](firmware/README.md) |
| Web app | [web/README.md](web/README.md) |

## Notebooks

All notebooks use synthetic practice data only. Nothing in them is a result.

| Notebook | What it does |
|---|---|
| [ml/notebooks/01_load_and_plot.ipynb](ml/notebooks/01_load_and_plot.ipynb) | Load a session, compute gyro magnitude, plot it |
| [ml/notebooks/02_find_throws.ipynb](ml/notebooks/02_find_throws.ipynb) | 1 second windows, threshold detector, tp/fp/fn/tn (draft) |
| [ml/exercises/03_honest_threshold.md](ml/exercises/03_honest_threshold.md) | Next exercise: test on unseen sessions, fix the window boundary bug |

## Rules this project follows

- All coding and technical development is done by the student team. AI is used as a teacher and reviewer, plus boilerplate that is labeled as such in [AI_USAGE.md](AI_USAGE.md).
- Claims are limited to what data supports. No "measures pitch speed" without radar validation, no injury prevention claims, and no comparison claiming to beat other products.
- No names, faces or video of minors are committed. Throwers get anonymous IDs.
