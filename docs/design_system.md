# Kinetiq design system

Logo: `web/assets/logo.svg` (wordmark) and `web/assets/mark.svg` (the Q, used as the browser tab icon). Both use the ink color `#1a1a17`. Use the files, never retype the name in a font.

The look of the web app in `web/app.py`. Written by Claude and logged in `AI_USAGE.md`. Updated in session 4: the old version mixed a dark navy page, cream buttons, pastel cards and three fonts, which is why the app looked inconsistent. This version picks one base and borrows one thing.

`web/reference/` still shows the older dark direction. It is out of date. Follow this file.

## The idea in one line

It should feel like a phone app, not a website: a cream page and dark ink from heylemon.ai, with one blue accent taken from raisedhand.ai and darkened so it is readable on cream. Data comes first. No hero, no marketing sections.

Why light and not dark: coaches look at this outside at a field, in the sun. Dark screens wash out there.

## Font

One family: **Inter** (400, 500, 600), loaded in `web/.streamlit/config.toml`. Headings are the same font, just weight 600. No serif, no mono.

## Colors

| Token | Hex | Where it goes |
|---|---|---|
| Page | `#fbfbed` | background (heylemon cream) |
| Input | `#f1f0e2` | dropdowns, inputs |
| Border | `#e6e4d3` | every border and card |
| Ink | `#1a1a17` | text (heylemon) |
| Accent | `#3d5bd9` | selected tab, focus, single chart line |
| Limit | `#c8601a` | sensor limit only (bars that hit it, the dashed line) |
| Faint | `#b9b7a8` | chart crosshair |

Chart lines, in this order: `#3d5bd9`, `#1d8a5e`, `#a34fbf`. Checked with a colorblind palette validator against white. All checks pass. Orange is kept out of the line colors so it only ever means "sensor limit". Compare stops at 3 throws because there are only 3 tested colors.

Accent on cream is 5.4:1 contrast, ink on cream is 16.7:1.

## Layout

- `layout="centered"`: a single column. It fills a phone and sits in the middle on a computer.
- Tabs: Throws, One throw, Compare, About. On a computer they sit under the app name. Under 640px wide they stick to the bottom of the screen like an iPhone tab bar.
- Cards are `st.container(border=True)` and `st.metric(border=True)`. One kind of card everywhere.
- Big numbers sit in a `st.container(horizontal=True)` row so they stay side by side on a phone. Three short labels at most, or they wrap.
- The throw list is buttons. Tapping one opens that throw.

## Charts

- Altair only.
- Line charts show the numbers for the picked moment in a small box in a top corner, on the side away from your finger. **Not a tooltip.** Testing showed that on a touch screen a tap moves the crosshair but never opens a Vega tooltip, so tooltips don't work on an iPhone.
- The 4,000 °/s limit line only goes on the Each direction view. The limit is per direction, so the total can go past 4,000 without hitting it.

## Motion

None, on purpose. Streamlit redraws on every tap, and entrance animations replay and flicker.

## Streamlit rules that will bite you

1. Theme goes in `web/.streamlit/config.toml`, and you must run `streamlit` from inside `web/`. Before session 4 this file did not exist in `web/`, so the app fell back to default fonts.
2. Style only things you named with `key=` (Streamlit adds a class `st-key-<key>`). The two exceptions in `app.py` are hiding Streamlit's top bar and its page padding. Those could break on a Streamlit update.
3. `:orange[...]` and `st.warning` use Streamlit's own colors, not ours. Don't use them.

## Words on screen

Plain words, like you'd say them to a teammate. No slogans. No dashes as punctuation. Every label has to be true for the data behind it.

| Do not write | Write instead |
|---|---|
| "Every throw, explained." | "How fast the forearm spun on each throw." |
| "Verified" (before real data exists) | "No recordings yet" |
| "Optimal", "elite" | "Under the limit", "Hit the limit" |
| "Proves consistency" | "Those throws sped up and slowed down at about the same time" |
| "Measures pitch speed" | "Measures how fast the forearm spins" |
