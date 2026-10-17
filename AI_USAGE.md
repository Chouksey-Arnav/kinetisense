# AI usage log

Required for the Congressional App Challenge. Every AI contribution is listed here, and must also be disclosed in the submission materials themselves. Be specific: file, function, and kind of help.

## Project-level disclosures

- The original project plan document (hardware list, architecture, ML plan, timeline) was generated with AI assistance. The student's own decisions are recorded in the sections below.
- Claude Code (Anthropic) is used as a teacher and code reviewer. The student writes the ML core.

## Session 1 (2026-09-30)

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
| Review | none | Claude reviewed the project plan, found problems (accelerometer saturation, weak detector framing, enclosure strap slot geometry, firmware timing, rules risks) and verified CAC and eCYBERMISSION dates against the primary sources. | n/a |
| Scaffolding | `CLAUDE.md`, `AI_USAGE.md`, `.gitignore`, `docs/verification_log.md`, `ml/requirements.txt`, `ml/README.md`, `data/README.md`, `data/sessions_template.csv`, `firmware/README.md`, `web/README.md` | Claude wrote these boilerplate and documentation files. | Claude (boilerplate only) |
| Docs | `docs/verification_log.md` | Claude recorded the student's answers (co-builder, phone, radar, advisor, JavaScript experience) in the log. | Claude (documentation only) |
| Boilerplate | `ml/tools/make_synthetic_session.py` | Claude wrote a synthetic IMU data generator for practice. Fake data, never used for evaluation. | Claude (boilerplate only) |
| Docs | `README.md` | Claude wrote the root README with links to existing files. | Claude (documentation only) |
| Docs | `docs/data_plan.md`, `README.md` | Claude wrote the data plan (how real training data is recorded, labeled, split, and used honestly) and added its link to the README. | Claude (documentation only) |
| ML core | none yet | No ML code written by Claude. The student writes the first data loading and plotting analysis. | Student |

## Session 2 (2026-10-17)

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
| Review | `ml/notebooks/02_find_throws.ipynb`, `ml/notebooks/01_load_and_plot-Copy1.ipynb` | Claude reviewed both notebooks and ran the student's threshold logic on 30 unseen synthetic sessions (throwaway script, not committed) to test the 2100 threshold. Findings: tuned and judged on one session, misses about 11% of throws on unseen sessions, and a window boundary bug double counts throws. No code was changed. | n/a |
| Docs | `ml/exercises/03_honest_threshold.md` | Claude wrote the next exercise handout and quiz. Documentation only, contains no ML code. | Claude (documentation only) |
| Docs | `README.md` | Claude updated the Notebooks section to link the existing notebooks and exercise. | Claude (documentation only) |
| ML core | `ml/notebooks/01_load_and_plot.ipynb`, `ml/notebooks/02_find_throws.ipynb` | No ML code written by Claude. Student wrote both notebooks. | Student |

## Template for future sessions

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
