# data/

Raw recordings live in `data/raw/` and are not committed (see `.gitignore`). Never commit names, faces or video of a minor. Use anonymous thrower IDs such as `T01`.

Every recording session gets one row in `data/sessions.csv` (copy `sessions_template.csv`). Split train and test by whole session, never by random windows.

Fields: session_id, date, thrower_id, device (phone or kinetisense), sample_rate_hz, gyro_units (dps or rad_s), mounting_location, ball_type, throw_type, adult_present, notes.

Targets for the first pass: at least 50 throws and 150 non-throws across at least 3 sessions. Treat that as a minimum, not enough for confident F1 claims.
