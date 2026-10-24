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

## Session 2 (2026-10-24)

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
| Firmware | `firmware/main.py` | Claude wrote the Part 1 constants block (addresses, registers, settings bytes, conversion factors) from datasheet values it extracted and the student then checked. Claude explained I2C, registers and write/readback. Claude reviewed the student's Parts 2 and 3, found two bugs in Part 2 (wrong register name, and the expected ID compared against the wrong constant), and asked for raw hex numbers to be replaced with the named constants. | Student (Parts 2 and 3). Claude (constants only). |
| Review and testing | `web/app.py` | Claude reviewed five versions of the website and ran each in a local test harness (8 demo throws, per-axis clipping check, 12 bad-file cases, run from two folders). Findings sent back to the co-builder: relative data path, missing column checks, missing plot cleanup, empty-file crash, unclear disclosure. The test harness is not committed. | Co-builder (Vatsalya). He also states that AI helped with code implementation. Exact split still to be confirmed with him. |
| Boilerplate | `web/tools/make_demo_data.py`, `web/sample_data/demo_throws.csv`, `web/sample_data/demo_samples.csv` | Claude wrote the generator and generated the synthetic stand-in data. It is fake, contains no real recording, and the site labels it DEMO DATA. | Claude (boilerplate only) |
| Boilerplate | `web/requirements.txt`, `web/README.md` | Claude wrote the dependency pins (the versions it tested with) and the README. | Claude (boilerplate only) |
| Teaching | none | Claude explained concepts (imports, constants, hex, bytes, I2C, `struct.unpack`, git staging, commit, fast-forward merge). | n/a |
| Research | none | Claude extracted facts from the ISM330DHCX and Pico 2 W datasheets and flagged datasheet errors. Values are still unverified on the real device until tested. | n/a |
| Planning | none | Claude drafted a prompt for another AI to write a presentation script. Any script that comes from it will be rewritten by the students and disclosed. | n/a |

## Session 3 (2026-10-24)

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
| Review | `web/app.py` | Claude ran the site in a browser, took screenshots, and reviewed the UI. Found: empty card boxes (an HTML div opened in one `st.markdown` call cannot wrap a widget), white Streamlit header left over on a dark page, three near identical keyframes, wording that claims more than the data supports ("verified" on synthetic data, "Optimal", "elite", "prove", "Peak Acceleration Point", "Time to Peak Arm Speed" for a recording timestamp). | n/a |
| Recommendations | none | Claude recommended a design and motion plan (theme in `.streamlit/config.toml`, keyed `st.container` cards, one shared keyframe, interactive charts, reduced motion support) based on screenshots of heylemon.ai and raisedhand.ai. Claude tested the approach in a throwaway prototype that is not committed. No app code was changed. | n/a |
| Reference code | `web/reference/app.py`, `web/reference/.streamlit/config.toml` | At the student's request, Claude wrote a complete reference version of the web viewer that shows the design system working (theme config, keyed cards, one entrance animation, Altair charts with hover, honest labels). It is a separate example to read, not the submission app. If any of it is copied into `web/app.py`, that must be logged here as Claude written code. | Claude (reference only) |
| Docs | `docs/design_system.md` and a shared Claude Docs copy | Claude wrote the design spec (fonts, colors, spacing, motion, file structure, Streamlit pitfalls, honest wording) for the student to send to the co-builder. Chart colors were checked with a colorblind palette validator. | Claude (documentation only) |

## Session 4 (2026-10-24)

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
| App code | `web/app.py` | At the student's request, Claude rewrote the whole web app: five pages (Start here, All throws, One throw, Compare, About), plain language explanations of every number, hover tooltips written in words, and the new design. The co-builder's earlier version is replaced. | Claude |
| Theme | `web/.streamlit/config.toml` | Claude wrote the theme (colors, fonts, radius) blending raisedhand.ai and heylemon.ai, based on their real CSS. | Claude |
| Docs | `docs/design_system.md`, `web/README.md`, `web/requirements.txt` | Claude rewrote the design spec and README, removed matplotlib and pinned altair. Removed `web/reference/`, which the new app replaces. | Claude |
| Testing | none | Claude ran the app in a browser, checked every page, hover tooltips, the home buttons, a phone sized screen, and a broken data file. Chart colors were checked with a colorblind palette validator. | n/a |

## Template for future sessions

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
