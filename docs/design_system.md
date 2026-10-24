# KinetiSense design system

The look and structure of the web app in `web/`. Claude wrote this spec and the app from screenshots and the real CSS of raisedhand.ai and heylemon.ai. Both are logged in `AI_USAGE.md`.

## The idea in one line

raisedhand's dark navy canvas and light blue accent, with heylemon's serif headings, mono labels, pastel number cards and cream buttons. Every number on screen comes with a plain sentence that says what it means.

## What came from where

| From raisedhand.ai | From heylemon.ai |
|---|---|
| Near black navy page with a soft glow at the top | Serif headings with one word in italics ("Every throw, *explained*.") |
| Light blue accent `#9dbcff` on the italic words | Small mono labels in caps, like "• HOW IT WORKS •" |
| Fade up out of a blur animation, curve `cubic-bezier(.32,.72,0,1)` | Big rounded hero card with a color gradient and film grain |
| Thin strip across the top (we use it for the demo data notice) | Numbered steps: 01 · STRAP ON, 02 · THROW, 03 · READ |
| Pill shaped buttons | Pastel number cards (violet, green, peach) and the cream button |

## Fonts

All free from Google Fonts. `web/.streamlit/config.toml` loads them.

| Use | Font | Weight | Size |
|---|---|---|---|
| Body, buttons, inputs | Inter | 400 | 16px |
| Page titles and card titles | Source Serif 4 (italic for the accent word) | 500 | 48px titles, 72px on the home hero |
| Big numbers | Source Serif 4 | 500 | 42px |
| Small labels above titles | Geist Mono | 500 | 11.5px, caps, letter spacing 0.16em |

## Colors

| Token | Hex | Where it goes |
|---|---|---|
| Page | `#05070d` | background, with a navy glow `#1d2b5c` at the top |
| Card | white at 2.5% | card background |
| Card border | white at 7%, 15% on hover | every card |
| Text | `#eceef4` | main text |
| Muted text | `#a3aabb` | descriptions, notes |
| Accent | `#9dbcff` | italic heading words, selected tab, the one throw chart line |
| Warning | `#fab219` | demo banner, sensor limit line, throws that hit the limit |
| Cream | `#fbfbed` | main button, the peak marker |
| Pastels | `#c5c2ff`, `#bcec70`, `#ffcb87` | the three number cards on All throws |

Compare chart lines, in this order: `#3987e5`, `#d95926`, `#199e70`. They passed a colorblind check against the card color. A fourth color does not pass, so Compare stops at 3 throws.

## Shape and motion

- Cards: 26px corners, 26px padding. Hero: 32px corners. Buttons: full pill.
- One animation: cards fade up 10px out of a 14px blur over 0.8s. Cards in a row start 0.1s apart.
- Hover: card border gets a little brighter. Nothing else moves.
- Charts: hover shows a line and a tooltip written in words ("54 ms before the fastest moment").
- If the computer asks for reduced motion, all of it turns off.

## Pages

1. **Start here**: hero, the three steps, six cards that explain every number (°/s, peak, ms, throw numbers, sensor limit, x y z), and what it does not measure.
2. **All throws**: three pastel number cards, then a bar per throw with the session average and limit hits marked.
3. **One throw**: pick a throw, three explained numbers (top spin with turns per second, % vs the session average with rank, sensor limit status), then the chart with a "How to read this" list beside it. A switch shows spin in each direction with the 4,000 limit line.
4. **Compare**: up to 3 throws lined up at their fastest moment, plus a small table.
5. **About**: what it is, what it does not do, where the data comes from, the sensor limit, AI use.

## Streamlit rules that will bite you

1. Theme goes in `config.toml`. Run `streamlit` from `web/` or it won't load.
2. Streamlit loads the heading font but does not apply it, so `app.py` sets it on `h1, h2, h3` in CSS.
3. Cards come from `st.container(key="card1")`. Streamlit adds the class `st-key-card1`, and the CSS targets that.
4. Put CSS in `st.html("<style>...</style>")`, not `st.markdown`.
5. Never write CSS selectors on Streamlit's own structure. Only style things you named with `key=`.

## Words on screen

Every label has to be true for the data behind it.

| Do not write | Write instead |
|---|---|
| Active dataset verified | Demo mode: these throws were made by a computer |
| Optimal | In range |
| Elite arm acceleration | One direction reached 4,000 °/s |
| Peak Acceleration Point | Fastest moment |
| Time to Peak Arm Speed | (dropped, it was a timestamp) |
| Overlapping curves prove consistency | Similar shapes mean similar timing. A few throws can't prove consistency |
