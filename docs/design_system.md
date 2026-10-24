# Kinetiq design system

Logo: `web/assets/logo.svg` (wordmark) and `web/assets/mark.svg` (the Q, used as the browser tab icon). Both use the ink color `#1a1a17`. Use the files, never retype the name in a font.

The look and structure for the web viewer in `web/`. Written by Claude from screenshots of raisedhand.ai and heylemon.ai, and logged in `AI_USAGE.md`. A working example lives in `web/reference/`. To run it:

```
cd web/reference
streamlit run app.py
```

The example is there to read and learn from. Build the real thing yourselves in `web/app.py`. If any of it gets copied in, write that down in `AI_USAGE.md`.

## The idea in one line

A dark, quiet page with one accent color, thin borders, and motion only where it helps someone read the data. The direction is raisedhand.ai, with one borrowed detail from heylemon.ai: the small spaced out mono labels.

## Fonts

| Use | Font | Weight | Size |
|---|---|---|---|
| Everything (body, buttons, inputs) | Inter | 400 | 15 to 16px |
| Page title (h1) | Inter | 600 | 40px (2.5rem) |
| Card title (h2/h3) | Inter | 600 | 18 to 22px |
| Big numbers (`st.metric`) | Inter | 400 | 32px (2rem) |
| Eyebrow labels above titles | JetBrains Mono | 500 | 11px, UPPERCASE, letter spacing 0.14em |

Two families only. Both load from Google Fonts in `config.toml`, so there are no font files to manage.

## Colors

| Token | Hex | Where it goes |
|---|---|---|
| Page | `#05070b` | page background |
| Card | `#0b0e14` | card background |
| Input | `#0d1118` | dropdowns, inputs |
| Border | `#1c2230` | every border |
| Border hover | `#2c3550` | card border on hover |
| Text | `#e6e8ee` | main text |
| Muted text | `#8b93a7` | subtitles, eyebrow labels |
| Faint | `#5b6378` | hover crosshair line |
| Accent | `#8fa8ff` | selected nav, focus, the single throw chart line |
| Warning | `#fab219` | DEMO DATA label, sensor range line |

Chart lines when comparing throws, in this order: `#3987e5`, `#d95926`, `#199e70`.

These three were run through a colorblind checker against the card color and passed. A fourth color does not pass, so Compare allows three throws at most.

Rule: one accent. No gold borders, no glows, no gradients, no glass blur.

## Shape and spacing

- Cards: 20px corner radius, 1px border, 24px padding.
- Inputs and buttons: 14px radius (`baseRadius` in `config.toml`).
- Space between cards: Streamlit's default gap. Do not add margins by hand.

## Motion

Only three things move.

| What | How | Timing |
|---|---|---|
| Cards appearing on page load | rise 12px, fade in, unblur 4px | 0.6s, curve `cubic-bezier(.2,.7,.3,1)`, each card 0.08s after the last |
| Card hover | border color only | 0.2s |
| Charts | Altair's built in hover crosshair | instant |

Nothing loops, pulses or bounces. If the computer has "reduce motion" turned on, all of it switches off (`prefers-reduced-motion`).

## How the files are laid out

```
web/
  .streamlit/config.toml   theme: colors, fonts, radius (no CSS needed for these)
  app.py
    constants              data folder, sensor limit, accent, max compare
    st.set_page_config
    styles                 one st.html <style> block: keyframe, card, eyebrow, reduced motion
    load_data()            reads both CSVs, checks columns, stops with a clear error
    throw_window()         one throw's samples, time measured from its peak
    header()               eyebrow + title + one line description
    line_chart()           Altair line with hover crosshair
    throw_page()           select throw, 3 metrics, chart (Combined or Per axis)
    compare_page()         pick up to 3 throws, overlay chart, small table
    about_page()           what it does, what it does not, sensor range, AI use
    st.navigation(..., position="top")
```

Each page is a function. Navigation sits along the top like a website, not in a sidebar.

## Streamlit rules that will bite you

1. **Theme goes in `config.toml`, not CSS.** That one file fixes the white header bar, the red radio dots, the input colors and the fonts. Run `streamlit` from the folder that contains `.streamlit/`, or the theme will not load.
2. **Cards come from `st.container(key="card1")`.** Streamlit adds a CSS class `st-key-card1`, and your CSS targets that. Opening `<div>` in one `st.markdown` and closing it in another does not work. It draws an empty box.
3. **Put CSS in `st.html("<style>...</style>")`, not `st.markdown`.** In testing, CSS variables like `--i` broke inside `st.markdown`.
4. **Never write selectors on Streamlit's own structure** like `.stMainBlockContainer>div>div`. They broke in testing and will break on updates. Only style things you named with `key=`.
5. **Use `st.metric(..., border=True)` and `st.altair_chart`.** Do not hand write HTML metric cards or use matplotlib. Altair charts let judges hover and read exact values. A matplotlib picture can't do that.

## Words on screen

Every label has to be true for the data behind it. Judges can open the code.

| Do not write | Write instead | Why |
|---|---|---|
| "Active dataset verified" | "Demo data, synthetic" | The data is generated, not recorded |
| "Optimal ✓" | "Within range" | Not clipped does not mean good |
| "Elite arm acceleration" | "One axis reached 4,000 °/s" | Clipping says nothing about skill |
| "Peak Acceleration Point" | "Peak angular velocity" | The dot is velocity, not acceleration |
| "Time to Peak Arm Speed" | "Peak happened at" | It is a time stamp in the recording |
| "Overlapping curves prove consistency" | "Similar shapes suggest similar timing" | A few throws prove nothing |
| 4000 line on the combined curve | 4000 line on the Per axis view only | The limit is per axis. The combined value can go past 4000 without clipping |
