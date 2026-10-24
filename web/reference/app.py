# How to run it:
#   cd web
#   streamlit run app.py
# (You have to be inside web/ or the theme in web/.streamlit/config.toml won't load.)

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------
# Settings. Change things here, not deep in the code.
# ---------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent / "sample_data"
DATA_IS_SYNTHETIC = True  # only flip to False when the CSVs are REAL recordings
SENSOR_LIMIT = 4000       # most the sensor can read in one direction (°/s). From the datasheet, not tested yet
WINDOW_MS = 200           # how far before and after the peak we show on the throw chart
MAX_COMPARE = 3           # our chart colors only pass the colorblind check for 3 lines
BLUE, ORANGE, FAINT = "#3d5bd9", "#c8601a", "#b9b7a8"  # orange only ever means "sensor limit"
TABS = ["Throws", "One throw", "Compare", "About"]

# The columns each CSV has to have, or the app stops with a clear message
NEEDED = {"demo_throws.csv": {"throw_id", "peak_time_s", "peak_dps", "clipped"},
          "demo_samples.csv": {"throw_id", "time_s", "gx", "gy", "gz", "gyro_mag"}}

st.set_page_config(page_title="Kinetiq", page_icon="⚾", layout="centered")

# ---------------------------------------------------------------
# Styles. Colors and the font are in config.toml. This is only what a
# config file can't do: the top bar, list rows, and the tab bar that
# sits at the bottom of the screen on a phone like a real app.
# ---------------------------------------------------------------
st.html("""<style>
/* hide Streamlit's own top bar and trim the empty space it leaves */
header[data-testid="stHeader"] { display: none; }
[data-testid="stMainBlockContainer"] { padding: 1.25rem 1rem 6rem; }

.top { display: flex; justify-content: space-between; align-items: center; font-weight: 600; font-size: 17px; }
.pill { font-size: 12px; font-weight: 500; color: #8a4410; background: #fbe6d4; border-radius: 999px; padding: 3px 10px; }

[class*="st-key-row"] button { min-height: 52px; }
[class*="st-key-row"] button > div { width: 100%; justify-content: flex-start; }  /* list rows read left to right */

/* on a phone the tabs move to the bottom, where your thumb is */
@media (max-width: 640px) {
  .st-key-tabs { position: fixed; left: 0; right: 0; bottom: 0; z-index: 100; padding: 10px 12px 14px;
                 background: #fbfbedf2; backdrop-filter: blur(12px); border-top: 1px solid #e6e4d3; }
}
</style>""")


# ---------------------------------------------------------------
# Loading the data
# ---------------------------------------------------------------
@st.cache_data
def load_data():
    """Read both CSVs, check them, and add the plain-English numbers we show everywhere."""
    frames = {}
    for name, cols in NEEDED.items():
        path = DATA_DIR / name
        if not path.exists():
            st.error(f"Can't find {path}. The app needs both CSV files in web/sample_data/.")
            st.stop()
        df = pd.read_csv(path)
        missing = cols - set(df.columns)
        if missing:
            st.error(f"{name} is missing these columns: {sorted(missing)}")
            st.stop()
        if df.empty:
            st.error(f"{name} has no rows in it.")
            st.stop()
        df["throw_id"] = df["throw_id"].astype(str)
        frames[name] = df

    throws, samples = frames["demo_throws.csv"], frames["demo_samples.csv"]
    throws["turns"] = throws.peak_dps / 360  # 360° is one full turn, so this is turns per second
    throws["rank"] = throws.peak_dps.rank(ascending=False, method="min").astype(int)  # 1 = fastest
    return throws, samples


def throw_window(throw_id):
    """One throw's samples, with time counted in milliseconds from its fastest moment."""
    throws, samples = load_data()
    peak_time = throws.loc[throws.throw_id == throw_id, "peak_time_s"].iloc[0]
    w = samples[samples.throw_id == throw_id].copy()
    w["t_ms"] = ((w.time_s - peak_time) * 1000).round().astype(int)
    w = w[w.t_ms.abs() <= WINDOW_MS]
    # words for the chart readout, so nobody has to decode "-33"
    w["when"] = w.t_ms.map(lambda t: "Fastest moment" if t == 0 else f"{abs(t)} ms {'before' if t < 0 else 'after'}")
    return w


# ---------------------------------------------------------------
# Helpers so every page looks the same
# ---------------------------------------------------------------
def ordinal(n):
    """1 -> 1st, 2 -> 2nd, 3 -> 3rd, 11 -> 11th"""
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n if n < 20 else n % 10, 'th') }"


def stats(*items):
    """A row of big numbers. horizontal=True keeps them side by side on a phone instead of stacking."""
    with st.container(horizontal=True):
        for label, value in items:
            st.metric(label, value, border=True)


def line_chart(df, series, limit=False):
    """Spin over time, one line per value in the `series` column.
    Hover or tap anywhere and the numbers for that moment show up in a top corner.
    (We don't use a tooltip because on an iPhone a tap never makes one show up.)"""
    names = list(df[series].unique())
    pick = alt.selection_point(fields=["t_ms"], nearest=True, on="pointerover", empty=False)
    base = alt.Chart(df).encode(x=alt.X("t_ms:Q", title="ms from the fastest moment (0)"))
    lines = base.mark_line(strokeWidth=2).encode(
        y=alt.Y("dps:Q", title="Spin (°/s)"),
        color=alt.Color(f"{series}:N", sort=names, title=None,
                        legend=alt.Legend(orient="top") if len(names) > 1 else None))
    # pivot turns rows into one column per line, so each moment has every line's number in one row
    moments = base.transform_pivot(series, value="dps", groupby=["t_ms", "when"])
    rule = moments.mark_rule(color=FAINT).encode(opacity=alt.condition(pick, alt.value(1), alt.value(0))).add_params(pick)
    # builds text like "12 ms before / Throw 1: 4,317 °/s / Throw 2: 2,139 °/s"
    words = " + '\\n' + ".join(f"'{n}: ' + format(datum['{n}'], ',.0f') + ' °/s'" for n in names)
    # the box goes on the side away from your finger (right if you picked before 0, left if after),
    # so it never covers the part of the line you're looking at. x is in pixels here, not ms
    picked = moments.transform_filter(pick).transform_calculate(
        label=f"datum.when + '\\n' + {words}", left="datum.t_ms < 0 ? width - 124 : 2", right="datum.left + 122")
    box = picked.mark_rect(fill="#fbfbed", opacity=.95, stroke="#e6e4d3", cornerRadius=8).encode(
        x=alt.X("left:Q", scale=None), x2="right:Q", y=alt.value(2), y2=alt.value(14 + 15 * (len(names) + 1)))
    readout = picked.mark_text(align="left", baseline="top", lineBreak="\n", fontSize=12, color="#1a1a17", dx=8).encode(
        x=alt.X("left:Q", scale=None), y=alt.value(8), text="label:N")
    layers = [lines, rule, box, readout]
    if limit:
        layers.append(alt.Chart(pd.DataFrame({"y": [SENSOR_LIMIT]}))
                      .mark_rule(color=ORANGE, strokeDash=[4, 4]).encode(y="y:Q"))
    st.altair_chart(alt.layer(*layers).properties(height=280), width="stretch")


def open_throw(throw_id):
    """Runs when you tap a throw in the list. Jumps to the One throw tab with that throw picked."""
    st.session_state.tab = "One throw"
    st.session_state.pick = throw_id


# ---------------------------------------------------------------
# Throws: the whole session, then a list you can tap
# ---------------------------------------------------------------
def throws_page(throws):
    fastest = throws.loc[throws.peak_dps.idxmax()]
    st.title("This session", anchor=False)
    st.caption("How fast the forearm spun on each throw. Tap one to see the whole throw.")
    stats(("Throws", len(throws)), ("Fastest (°/s)", f"{fastest.peak_dps:,.0f}"),
          ("Hit the limit", int(throws.clipped.sum())))

    with st.container(border=True):
        df = throws.assign(status=throws.clipped.map({True: "Hit the limit", False: "Under the limit"}))
        st.altair_chart(alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
            x=alt.X("throw_id:N", sort=None, title="Throw", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("peak_dps:Q", title="Top speed (°/s)"),
            color=alt.Color("status:N", legend=None,
                            scale=alt.Scale(domain=["Under the limit", "Hit the limit"], range=[BLUE, ORANGE])),
            tooltip=[alt.Tooltip("throw_id:N", title="Throw"),
                     alt.Tooltip("peak_dps:Q", title="Top speed (°/s)", format=",.0f"),
                     alt.Tooltip("status:N", title="Sensor")],
        ).properties(height=260), width="stretch")
        st.caption(f"Orange bars hit the sensor limit, so the real top speed could be higher. A blue bar can still go "
                   f"past {SENSOR_LIMIT:,}, because the limit counts each direction on its own, not the total.")

    for t in throws.itertuples():
        note = "  ·  hit the limit" if t.clipped else ""
        st.button(f"**Throw {t.throw_id}**  ·  {t.peak_dps:,.0f} °/s{note}", key=f"row{t.throw_id}",
                  width="stretch", on_click=open_throw, args=(t.throw_id,))


# ---------------------------------------------------------------
# One throw: the numbers for it, then the whole motion
# ---------------------------------------------------------------
def one_page(throws):
    st.title("One throw", anchor=False)
    peaks = throws.set_index("throw_id").peak_dps
    tid = st.selectbox("Throw", throws.throw_id, key="pick",
                       format_func=lambda t: f"Throw {t}  ·  {peaks[t]:,.0f} °/s")
    row = throws.set_index("throw_id").loc[tid]

    stats(("Top speed (°/s)", f"{row.peak_dps:,.0f}"), (f"Rank of {len(throws)}", ordinal(row["rank"])))
    turns = f"That's about {row.turns:.1f} full turns of the forearm a second, just for an instant."
    if row.clipped:
        st.markdown(f"{turns} **It hit the sensor limit,** though. One direction reached {SENSOR_LIMIT:,} °/s, "
                    "which is the most the sensor can read, so the real top speed was at least this fast.")
    else:
        st.markdown(f"{turns} It stayed under the sensor limit, so this is the full reading.")

    with st.container(border=True):
        view = st.segmented_control("View", ["Total", "Each direction"], default="Total", required=True,
                                    label_visibility="collapsed")
        w = throw_window(tid)
        if view == "Total":
            line_chart(w.assign(line="Total", dps=w.gyro_mag), "line")
        else:
            axes = w.melt(id_vars=["t_ms", "when"], value_vars=["gx", "gy", "gz"], var_name="line", value_name="dps")
            axes["line"] = axes.line.str[1]  # "gx" -> "x"
            axes["dps"] = axes.dps.abs()     # the limit is the same both ways, so we only plot how big it is
            line_chart(axes, "line", limit=True)

    with st.expander("How do I read this?"):
        st.markdown("- Left to right is time. **0** is the moment the forearm spun the fastest.\n"
                    "- Left of 0 it's speeding up. Right of 0 it's slowing down.\n"
                    "- Higher means spinning faster.\n"
                    f"- In **Each direction**, the dashed orange line is the {SENSOR_LIMIT:,} °/s sensor limit. "
                    "If a line touches it, that direction maxed out.\n"
                    "- Hover or tap anywhere on the chart to see the exact numbers.")


# ---------------------------------------------------------------
# Compare: throws on top of each other, lined up at their fastest moment
# ---------------------------------------------------------------
def compare_page(throws):
    st.title("Compare", anchor=False)
    st.caption("Every throw is lined up at its fastest moment, so you can see if they had the same shape.")
    ids = st.multiselect(f"Pick up to {MAX_COMPARE} throws", throws.throw_id, default=list(throws.throw_id[:2]),
                         max_selections=MAX_COMPARE, format_func=lambda t: f"Throw {t}")
    if not ids:
        st.info("Pick at least one throw.")
        return

    with st.container(border=True):
        df = pd.concat(throw_window(t) for t in ids)
        line_chart(df.assign(line="Throw " + df.throw_id, dps=df.gyro_mag), "line")
    st.caption("If two lines look alike, those throws sped up and slowed down at about the same time. "
               "A few throws can't tell you if someone is consistent though. That takes a lot more throws.")

    picked = throws.set_index("throw_id").loc[ids]
    st.dataframe(pd.DataFrame({
        "Throw": "Throw " + picked.index,
        "Top speed (°/s)": picked.peak_dps.map("{:,.0f}".format),
        "Rank": picked["rank"].map(ordinal),
        "Hit the limit": picked.clipped.map({True: "Yes", False: "No"}),
    }), hide_index=True)


# ---------------------------------------------------------------
# About: how it works, what the numbers mean, what it can't do, who made it
# ---------------------------------------------------------------
def about_page(throws):
    st.title("About", anchor=False)
    data = (f"These {len(throws)} throws are fake. A computer program made them so you can try the app "
            "before our sensor is ready." if DATA_IS_SYNTHETIC
            else f"These {len(throws)} throws are real recordings from our sensor.")
    st.markdown(f"""
### How it works
1. A small sensor goes on the outside of the throwing forearm, held on with a strap.
2. While you throw, it keeps checking how fast the forearm is spinning. The demo data checks 1,000 times a second.
3. Our code finds the fastest moment in each throw, and this app shows it.

### What the numbers mean
- **°/s** means degrees per second, so how fast the forearm is spinning. One full turn is 360°, so 3,600 °/s is 10 turns a second.
- **The fastest moment** is the instant the forearm spun the fastest. Every chart puts it at 0.
- **ms** means milliseconds. 1,000 ms is one second, so -50 ms is 50 ms before the fastest moment.
- **x, y and z** are the three directions the sensor measures spin in. Think of three skewers through the forearm at right angles.
- **The sensor limit** is {SENSOR_LIMIT:,} °/s in each direction. If a throw hits it, the real speed was at least that fast, so we flag it.

### What it can't tell you
It doesn't measure pitch speed, ball spin, injury risk or arm health. It only measures how fast the forearm spins. To turn that into pitch speed we'd have to test it against a radar gun, and we haven't done that yet.

### The data
{data} The {SENSOR_LIMIT:,} °/s limit comes from the sensor's datasheet. We haven't checked it on our own sensor yet.

### Who made it
Arnav Chouksey and Vatsalya Vishnoi, for the Congressional App Challenge.

We used Claude, an AI, to write the code and design of this app. Every time we used AI on this project is written down in AI_USAGE.md in our code.
""")


# ---------------------------------------------------------------
# The app itself: a small top bar, the tabs, then whichever page is picked
# ---------------------------------------------------------------
throws, _ = load_data()
demo = '<span class="pill">Demo data</span>' if DATA_IS_SYNTHETIC else ""
st.html(f'<div class="top">Kinetiq {demo}</div>')

st.session_state.setdefault("tab", TABS[0])
with st.container(key="tabs"):
    tab = st.segmented_control("Page", TABS, key="tab", required=True, label_visibility="collapsed", width="stretch")

{"Throws": throws_page, "One throw": one_page, "Compare": compare_page, "About": about_page}[tab](throws)
