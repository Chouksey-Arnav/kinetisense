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
| Logo | `web/assets/logo.svg`, `web/assets/mark.svg` | The student made the logo idea with Google Gemini's image generator. Its output was misspelled ("KINIETIQ" with a stray mark). Claude redrew it as a vector file from plain shapes, spelled KINETIQ, and made the Q tab icon. | Gemini (concept image), Claude (SVG files) |
| Rename | `web/app.py`, `web/reference/app.py`, `README.md`, `CLAUDE.md`, `docs/design_system.md`, `docs/data_plan.md`, `web/tools/make_demo_data.py` | The student chose to rename the app from KinetiSense to Kinetiq. Claude replaced the name and put the logo in the app header and tab icon. | Claude |
| AI feature | `web/ai_coach.py` (all functions: `build_context`, `rise_time_ms`, `RateLimiter`, `check_question`, `get_api_key`, `get_model`, `build_messages`, `ask`, `leaks_prompt`, and `SYSTEM_PROMPT`) | At the student's request, Claude designed and wrote the Ask AI feature: the fact sheet the model reads, the model's rules, input limits, per visitor and app wide rate limits, Groq error handling, and the prompt leak check. | Claude |
| AI feature | `web/app.py` (`ask_about`, `groq_client`, `app_limiter`, `send`, `answer`, `ask_page`, the Ask AI buttons on One throw and Compare, phone tab bar CSS, the About page AI section) | Claude wired the Ask AI tab into the app. | Claude |
| Config | `web/.streamlit/secrets.toml.example`, `.gitignore`, `web/requirements.txt` | Claude set up how the Groq key is stored (gitignored `secrets.toml`, environment variable fallback) and pinned `groq==1.7.0`. | Claude (boilerplate only) |
| Tests | `web/tests/test_ai_coach.py`, `web/tools/redteam_ai.py` | Claude wrote 24 unit tests (no network) and a live red team script. The unit tests caught one bug in Claude's own leak check (the scripted refusal counted as a leak). Claude also ran the app in a browser against a fake local Groq server, at desktop and phone widths. Claude never ran it against the real Groq model, because it had no key. | Claude (tests only) |
| Docs | `web/README.md`, `README.md`, `docs/verification_log.md` | Claude documented the key setup, the risks, and the rename. | Claude (documentation only) |
| Runtime AI | Ask AI tab | The app itself now calls an AI model (openai/gpt-oss-120b, run by Groq) when a user asks a question. This must be named in the submission as part of what the app does, separately from the AI that helped build it. | n/a |

## Template for future sessions

| Area | File(s) | Kind of help | Who wrote the code |
|---|---|---|---|
