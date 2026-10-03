# Data plan: how KinetiSense gets its training data

Read this before you record, label, or train anything.

**One sentence:** training data is real recordings plus the answers you write down, and the only data allowed to back a claim is data that was really recorded.

---

## 1. The honesty rule

There are three kinds of data in this project. Each has a different job.

| Kind | What it is | Allowed use | Never use it for |
|---|---|---|---|
| **Synthetic** | Fake data made by `ml/tools/make_synthetic_session.py` | Practice: loading, plotting, windows, metrics, building the app | Results, validation, "the model trained on this", anything in the submission as evidence |
| **Phone** | Real recordings from a phone strapped to the forearm | Backup if the device is late. Real signals, lower quality | Claims about the KinetiSense device |
| **Device** | Real recordings from the KinetiSense device | Calibrating the detector, testing it, the replay app, the submission | Nothing is off limits, but it must be labeled honestly |

Why this matters: synthetic data contains exactly what we put into it, so any detector scores perfectly on it. That proves nothing about real throws. If a judge asks for the data, every claim has to trace back to a real recording.

---

## 2. Words you need

- **Recording:** one file from the device or phone, for example 20 seconds of readings.
- **Label:** the correct answer for a piece of data. Here it is `throw` or `not_throw`. A human supplies it, never the model.
- **Window:** a short slice of a recording, for example 1 second.
- **Feature:** one number that summarizes a window, for example the peak gyro magnitude.
- **Training table:** one row per window, with feature columns and a label column.
- **Session:** one outing, on one day, with one thrower and one setup. A session contains many recordings.
- **Split:** dividing the data into a part used to build the detector and a part kept hidden to test it.

---

## 3. The pipeline, step by step

```
record -> label -> cut into windows -> compute features -> training table -> split -> build detector -> test it
```

### Worked example

You record a 20 second file called `s01_f07.bin`. Your log sheet says: "file 07: 2 throws, 3 arm swings."

1. **Plot it.** You see 5 spikes in the gyro magnitude.
2. **Label it.** You write one row per event in the labels file:

   | file | event_time_s | label |
   |---|---|---|
   | s01_f07 | 3.2 | not_throw |
   | s01_f07 | 6.8 | throw |
   | s01_f07 | 9.1 | not_throw |
   | s01_f07 | 12.4 | throw |
   | s01_f07 | 16.0 | not_throw |

3. **Cut into windows.** Slide a 1 second window along the file. A window that contains an event gets that event's label. Windows with no event are `not_throw`.
4. **Features.** For each window, compute the peak gyro magnitude and other simple numbers.
5. **Table.** Every window becomes one row: `peak_gyro, ..., label`.
6. **Split.** Build the detector on some sessions. Test it on sessions it has never seen.

---

## 4. Where files go

```
data/raw/s01/            recordings from session s01 (NOT committed to git)
data/raw/s01/labels.csv  one row per labeled event (not committed)
data/sessions.csv        one row per session (see data/README.md)
web/sample_data/         a few anonymous throws, copied here so the public app can replay them
```

Naming: `s01_f07` means session 01, file 07. Thrower IDs are always `T01`, `T02`. No names, faces, or video of a minor are ever committed.

---

## 5. The throw session log sheet

Print this or copy it. Fill one row per throw during the session.

| file number | throw number | radar mph | effort (easy/medium/hard) | notes |
|---|---|---|---|---|

Rules:
- Write the radar number right after the throw, not later.
- Vary effort on purpose. If every throw is the same speed, you cannot learn a relationship.
- Write down any throw that felt wrong or was dropped.

---

## 6. Three ways to label

Use at least two and compare them.

1. **The log sheet.** Count of throws per file. Fast but approximate.
2. **Plot and mark.** Plot each file, find the spikes, write their times in `labels.csv`.
3. **Phone video.** Slow motion video confirms what happened when. Do not keep video with faces in the repo.

If two methods disagree, look at that recording again and decide. Note the disagreement in `docs/challenges.md`.

---

## 7. Splitting honestly

- Split by **whole session**, never by random windows. Neighboring windows overlap and look almost identical, so a random split lets the test data leak into the training data and gives fake accuracy.
- With only one throw session, the honest option is to hold out entire recordings. Say clearly that this is a weak test.
- Never tune a threshold using the data you test on.

---

## 8. How much data, and what "training" really means

- Expect **20 to 30 real throws** from one session. That is far too few to train a neural network or any complicated model.
- Expect **hundreds of non-throw examples**. These are cheap: ten minutes of walking, swinging, catching and stretching.
- So "training" in this project means: pick a threshold on the peak gyro magnitude using the real data, then test it on recordings you held out.
- You may also try a simple model (logistic regression). It only gets used if it beats the threshold on held-out data. If the threshold wins, report that. It is a fine result.
- Always report the sample size and the limits: one thrower, one session, small N.

---

## 9. Before any data touches a result, check

- [ ] Is it real (device or phone)? If it is synthetic, stop.
- [ ] Is it in `data/sessions.csv` with the date, device, sample rate, and units?
- [ ] Do the units match the datasheet (dps and g)?
- [ ] Has it been checked for clipping (gyro at +/-4000 dps, accel at +/-30 g)?
- [ ] Are its labels double checked by a second method?
- [ ] Is the test data separate from the data used to choose the threshold?

---

## 10. What the submission may say

Good:
- "We built and practiced the pipeline on synthetic data, then calibrated and tested a threshold detector on N real throws from one pitcher."
- "The sensor reports forearm angular velocity. In our small test it correlated with radar speed at r = X (N = Y, one thrower)."

Not allowed:
- "The model was trained on [synthetic data]."
- "KinetiSense measures pitch speed" (unless the validation really supports it).
- "Prevents injury." Never.
- Any number you cannot trace back to a real recording.
