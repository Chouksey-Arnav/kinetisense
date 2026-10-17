# Exercise 3: make the threshold honest

Written by Claude as a teaching handout (documentation, no ML code). You write every line of the notebook.

## Why this exercise exists

Notebook 2 picked a threshold of 2100 using one synthetic session, then judged it on that same session. A review ran your exact logic on 30 sessions it had never seen (fake data from `make_synthetic_session.py`, so this shows fragility, not real performance):

| Threshold | Throws caught | Extra detections |
|---|---|---|
| 1500 | 240 of 240 | 4 |
| 2100 | 214 of 240 | 2 |

Your chosen 2100 missed about 1 throw in 9. Nothing in session 0 could have told you that, because session 0 happened to contain no throw between 1500 and 2149.

## Tasks

**A. Generate new sessions.** From the repo root run `python ml/tools/make_synthetic_session.py --out data/synthetic/seed1 --seed 1`, and the same for seeds 2 to 5. Use relative paths in your notebook (no `/Users/...`), so it runs on Vatsalya's laptop too.

**B. Freeze, then test.** Choose the threshold from seed 0 only. Write it down. Then run it on seeds 1 to 5 without changing it. Report tp, fp, fn, tn for each. If you change the threshold after looking at seeds 1 to 5, those seeds are no longer a test.

**C. Choose a threshold by reasoning, not by the edge.** Session 0 says anything from about 902 to 2149 works. Explain in your own words why picking a value 49 below the lowest throw peak is fragile, and where in that range you would put it and why. Remember real data has no generator to tell you the gap exists.

**D. The baseline everyone forgets.** What accuracy does a detector that always says `not_throw` get on your 60 windows? Compute it. Then say why precision and recall are better than accuracy here.

**E. The boundary bug.** Find a case where a throw sits right at the edge of two 1 second windows. What does your detector report? Propose a fix and try it. Two reasonable options: overlapping windows, or finding peaks directly with `scipy.signal.find_peaks` (look up `height` and `distance`). Pick one and defend it.

**F. Messier fake data.** The generator draws swings at 300 to 900 dps. Real catching, shaking and ball transfers may be faster. Edit your copy of the swing peak range to 300 to 2500, regenerate, and rerun. What breaks? This is the real problem a threshold detector will face.

## Quiz (answer in a markdown cell, no looking)

1. Why do we split by session and not by random window?
2. Why can the synthetic result never appear in the submission as evidence?
3. Your detector uses `>` on a window maximum. What kind of mistake does a single noisy sample cause?
4. In `a & ~b`, what does each symbol do, and why can't you use `and` here?
5. If real throws from the volunteer pitcher peak around 1200 dps, what happens to a threshold of 2100?
