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

## Template for future sessions

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
