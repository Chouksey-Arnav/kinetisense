# Verification log

Status of every claim in the original (AI-generated) project plan. Update as items get checked. Do not put an unverified item in the submission.

## Verified (2026-09-30)

- CAC 2026 deadline: Monday Oct 26, 2026, 12:00 pm EDT. Source: 2026 CAC Rules PDF.
- Teams up to 4, at least half in the same district, one entry per student, apps created after Oct 30, 2025 are eligible.
- Demo video 1 to 3 minutes, public on YouTube or Vimeo, with names, app name, one-sentence purpose, target audience, tools and languages, functionality.
- AI rule: "All coding and technical development must be done by the student or student team." AI use must be fully disclosed in the submission materials and must not be the entirety of the technical development. No other party may hold rights or interest in the app.
- Judges may request the app and source code. Failure to honor the request has consequences (see rules section 7).
- eCYBERMISSION 2026 to 2027: grades rising 6 to 9, teams of 2 to 4 with an adult advisor, registration Aug 12, 2026 to Feb 24, 2027, Mission Folder Mar 3, 2027, virtual judging Mar 10 to 24, winners Apr 30, 2027. Source: usaeop.com. Rules about reusing work from another competition are NOT stated there. Read the official rules.

## Unverified (do not use yet)

- CAC district registration deadline of Oct 15, 2026 (not in the rules PDF). Check the participating districts page and screenshot it.
- Motus specs (+/-4000 dps, +/-24 g, 1000 Hz) and the description of Motus as modeled elbow torque from a proprietary mocap-trained model.
- ICM-20649 specs: gyro +/-500/1000/2000/4000 dps, accel +/-4/8/16/30 g, max ODR near 1.1 kHz, FIFO size, DLPF options. Read the datasheet.
- Which Pimoroni LiPo SHIM shipped (PIM557 versus adafruit.com/product/5612 in the old notes).
- Adafruit #3898 battery dimensions and whether it has a protection circuit.
- Shoulder internal rotation values of 6000 to 9000 dps. Cite a primary source before quoting.
- Phone sensor-logging app sample rates (Phyphox, SensorLog).

## Corrections to the original plan

- The old plan said the district registration deadline was Sep 15. That was wrong (Oct 15 claimed, still unverified).
- The plan said a forearm sensor does not see shoulder rotation. Wrong in part: the forearm gyro measures the forearm's total angular velocity, which includes humeral rotation carried through the elbow. Clipping at +/-4000 dps is likely for strong throwers.
- Accelerometer saturation is likely. Centripetal acceleration is omega squared times radius: about 31 g at 2000 dps and 0.25 m, over 100 g at 4000 dps. Order of magnitude only. Verify with real data. Do not build features on peak acceleration.
- Throw versus non-throw detection is probably solved by a gyro-magnitude threshold. Evaluate ML against it honestly.
- Phone data at about 100 Hz undersamples a throw peak. Use it for pipeline development only.
- Enclosure v3: the 4 mm strap slot cannot pass a 3/4 inch (19 mm) strap, and the stack probably exceeds the 11 mm cavity height. Measure real parts first.
- iPhone hotspots default to 5 GHz, and the Pico 2 W is 2.4 GHz only.

## Claims policy

Allowed once supported: "measures forearm angular velocity", "differs from modeled metrics such as Motus elbow torque". Not allowed: "measures pitch speed" without radar validation, "prevents injury", "beats Motus".

## Open questions

- Friend: identity, district, grade, registered on team, role.
- Volunteer pitcher: who, age, parent or coach sign-off, available dates.
- Which SHIM shipped, and parts arrival date.
- Demo phone (iPhone or Android).
- Radar gun source. eCYBERMISSION adult advisor.
- Does the student know JavaScript? Decides the web stack.

## Decisions

- Sensor: ICM-20649. Enclosure: 95A TPU, OpenSCAD v3 as a starting point (needs fixes above).
- ML and evaluation code in Python, written by the student.
- Web app must have replay mode that works with no hardware and no network.
- Pending: transport (Wi-Fi hotspot to a local server versus cloud versus Web Bluetooth), web stack, firmware language after measurements.
