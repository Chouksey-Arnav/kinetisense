# How to run it:
#   cd web
#   streamlit run app.py
# (You have to be inside web/ or the theme in web/.streamlit/config.toml won't load.)

import base64
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import ai_coach

# ---------------------------------------------------------------
# Settings. Change things here, not deep in the code.
# ---------------------------------------------------------------
RECORDINGS = Path(__file__).resolve().parent / "recordings"  # drop throws.csv and samples.csv here (git ignores this folder)
ASSETS = Path(__file__).resolve().parent / "assets"  # logo.svg (the wordmark) and mark.svg (the Q, for the browser tab)
SENSOR_LIMIT = 4000       # most the sensor can read in one direction (°/s). From the datasheet, not tested yet
WINDOW_MS = 200           # how far before and after the peak we show on the throw chart
MAX_COMPARE = 3           # our chart colors only pass the colorblind check for 3 lines
BLUE, ORANGE, FAINT = "#3d5bd9", "#c8601a", "#b9b7a8"  # orange only ever means "sensor limit"
AVATARS = {"user": ":material/person:", "assistant": ":material/auto_awesome:"}  # keeps orange out of the chat
TABS = ["Throws", "One throw", "Compare", "About"]  # Ask AI is not a tab: it's the button that floats over every page
DATA_TABS = TABS[:3]  # the pages that need recordings
SUGGESTIONS = {
    "Throws": ["Explain this session in plain words", "Which throws hit the sensor limit, and what does that mean?",
               "How different were my fastest and slowest throws?", "What can't this data tell me?"],
    "Compare": ["What's different about these throws?", "Do these lines have the same shape?",
                "What can't a few throws tell me?"],
    "None": ["How does the sensor measure a throw?", "What does °/s mean?", "What can't this app tell me?"],
}

# The columns each CSV has to have, or the app says which ones are missing
NEEDED = {"throws.csv": {"throw_id", "peak_time_s", "peak_dps", "clipped"},
          "samples.csv": {"throw_id", "time_s", "gx", "gy", "gz", "gyro_mag"}}

st.set_page_config(page_title="Kinetiq", page_icon=str(ASSETS / "mark.svg"), layout="centered")

# ---------------------------------------------------------------
# Styles. Colors and the font are in config.toml. This is only what a
# config file can't do: the top bar, list rows, and the tab bar that
# sits at the bottom of the screen on a phone like a real app.
# ---------------------------------------------------------------
st.html("""<style>
/* hide Streamlit's own top bar and trim the empty space it leaves */
header[data-testid="stHeader"] { display: none; }
[data-testid="stMainBlockContainer"] { padding: 1.25rem 1rem 6rem; }

.top { display: flex; justify-content: space-between; align-items: center; }
.top img { height: 20px; display: block; }

/* the Ask AI button floats over every page, bottom right, always one tap away */
.st-key-fab { position: fixed; right: 16px; bottom: 20px; z-index: 101; width: auto; }
.st-key-fab button { min-height: 48px; border-radius: 999px; padding: 0 20px; box-shadow: 0 8px 24px #3d5bd959; }
.st-key-fab button p { font-weight: 600; }

[class*="st-key-row"] button { min-height: 52px; }
[class*="st-key-row"] button > div { width: 100%; justify-content: flex-start; }  /* list rows read left to right */

/* on a phone the tabs move to the bottom, where your thumb is */
@media (max-width: 640px) {
  .st-key-tabs { position: fixed; left: 0; right: 0; bottom: 0; z-index: 100; padding: 10px 12px 14px;
                 background: #fbfbedf2; backdrop-filter: blur(12px); border-top: 1px solid #e6e4d3; }
  /* four tabs have to fit in one row on a 375px wide phone */
  .st-key-tabs button { padding: 0 4px; min-width: 0; }
  .st-key-tabs button p { font-size: 13px; white-space: nowrap; }
  .st-key-fab { bottom: 88px; }  /* sits just above the tab bar */
}
</style>""")


# ---------------------------------------------------------------
# Loading the data
# ---------------------------------------------------------------
def parse(throws, samples):
    """Check a pair of tables and add the plain-English numbers we show everywhere.
    Returns (throws, samples, None) if they're fine, or (None, None, what's wrong)."""
    for name, df in (("throws.csv", throws), ("samples.csv", samples)):
        missing = NEEDED[name] - set(df.columns)
        if missing:
            return None, None, f"{name} is missing these columns: {sorted(missing)}"
        if df.empty:
            return None, None, f"{name} has no rows in it."
    throws, samples = throws.copy(), samples.copy()
    throws["throw_id"] = throws["throw_id"].astype(str)
    samples["throw_id"] = samples["throw_id"].astype(str)
    if throws.throw_id.duplicated().any():
        return None, None, "throws.csv lists the same throw_id twice."
    lost = set(throws.throw_id) - set(samples.throw_id)
    if lost:
        return None, None, f"samples.csv has no rows for throw {sorted(lost)[0]}."
    throws["turns"] = throws.peak_dps / 360  # 360° is one full turn, so this is turns per second
    throws["rank"] = throws.peak_dps.rank(ascending=False, method="min").astype(int)  # 1 = fastest
    return throws, samples, None


@st.cache_data
def read_folder():
    """Both CSVs from web/recordings/, if they're there. Returns (throws, samples, problem), all None if no files."""
    paths = {name: RECORDINGS / name for name in NEEDED}
    if not all(p.exists() for p in paths.values()):
        return None, None, None
    return parse(pd.read_csv(paths["throws.csv"]), pd.read_csv(paths["samples.csv"]))


def load_data():
    """The recordings to show: ones loaded in the app win, then web/recordings/. None if there are none."""
    if "upload" in st.session_state:
        return st.session_state.upload
    throws, samples, problem = read_folder()
    if problem:
        st.error(problem)
    return (throws, samples) if throws is not None else None


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


def screen_label():
    """Words for what the user is looking at, so the AI can start from there."""
    tab = st.session_state.get("tab")
    if tab == "One throw" and st.session_state.get("pick"):
        return f"One throw page, looking at throw {st.session_state.pick}"
    if tab == "Compare" and st.session_state.get("cmp"):
        return f"Compare page, looking at throws {', '.join(st.session_state.cmp)}"
    return f"{tab} page, whole session"


def open_ai():
    """Runs when you tap the floating Ask AI button."""
    st.session_state.ai_open = True
    st.session_state.screen = screen_label()


def ask_about(question, screen):
    """Runs when you tap an "Ask AI" button inside a page. Opens the chat and sends the question."""
    st.session_state.ai_open = True
    st.session_state.pending = question
    st.session_state.screen = screen


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

    st.button("Ask AI about this session", icon=":material/auto_awesome:", on_click=ask_about,
              args=("Explain this session in plain words.", "Throws page, whole session"))
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

    st.button("Ask AI about this throw", icon=":material/auto_awesome:", on_click=ask_about,
              args=(f"Explain throw {tid} to me. How does it compare to the rest of the session?",
                    f"One throw page, looking at throw {tid}, {view} view"))


# ---------------------------------------------------------------
# Compare: throws on top of each other, lined up at their fastest moment
# ---------------------------------------------------------------
def compare_page(throws):
    st.title("Compare", anchor=False)
    st.caption("Every throw is lined up at its fastest moment, so you can see if they had the same shape.")
    ids = st.multiselect(f"Pick up to {MAX_COMPARE} throws", throws.throw_id, default=list(throws.throw_id[:2]), key="cmp",
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

    names = ", ".join(ids)
    st.button("Ask AI to compare these", icon=":material/auto_awesome:", on_click=ask_about,
              args=(f"Compare throws {names}. What's different about them?", f"Compare page, looking at throws {names}"))


# ---------------------------------------------------------------
# Ask AI: questions about this session, answered by a model on Groq. All the
# rules and safety checks are in ai_coach.py. This part is only the chat screen.
# ---------------------------------------------------------------
@st.cache_resource
def groq_client(key):
    """One connection to Groq, reused by every visitor."""
    import groq
    return groq.Groq(api_key=key, timeout=20, max_retries=1)


@st.cache_resource
def app_limiter():
    """One question counter for the whole app (cache_resource means everyone shares it)."""
    return ai_coach.RateLimiter(ai_coach.GLOBAL_LIMIT_PER_HOUR)


def send(text):
    """Runs when you tap a suggested question."""
    st.session_state.pending = text


def answer(question, throws, samples, key):
    """Check the question, ask Groq, and save both to the chat. Problems show as a warning instead."""
    q, problem = ai_coach.check_question(question, st.session_state.setdefault("ai_limits", {}))
    if problem is None and not app_limiter().allow():
        problem = "The AI has answered a lot of questions this hour. Try again later."
    if problem:
        st.warning(problem)
        return

    chat = st.session_state.chat
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(q)
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("Looking at your throws..." if throws is not None else "Thinking..."):
            context = ai_coach.build_context(throws, samples, SENSOR_LIMIT, False,
                                             st.session_state.get("screen", "Throws page, whole session"))
            reply, error = ai_coach.ask(groq_client(key), ai_coach.get_model(st.secrets), q, chat, context, SENSOR_LIMIT)
        if error:
            st.error(error)
            return
        st.markdown(reply)
    chat += [{"role": "user", "content": q}, {"role": "assistant", "content": reply}]


def suggestions(has_data):
    """Starter questions that fit the page you were on when you opened the chat."""
    tab = st.session_state.get("tab")
    if not has_data:
        return SUGGESTIONS["None"]
    if tab == "One throw" and st.session_state.get("pick"):
        t = st.session_state.pick
        return [f"Explain throw {t} to me", f"Did throw {t} hit the sensor limit?", "How do I read this chart?"]
    return SUGGESTIONS.get(tab, SUGGESTIONS["Throws"])


@st.dialog("Ask Kinetiq AI", width="large")
def ai_dialog(data):
    """The chat. It's a pop-up over whatever page you're on, so closing it puts you right back."""
    throws, samples = data if data else (None, None)
    st.caption("Ask anything about your throws or how the sensor works. The AI only sees the numbers in this app, "
               "and it can be wrong, so check anything important against the charts.")
    key = ai_coach.get_api_key(st.secrets)
    if not key:
        st.info("The AI is turned off because there's no Groq API key on this computer. "
                "web/README.md says how to add one. Everything else in the app works without it.")
        return

    chat = st.session_state.setdefault("chat", [])
    pending = st.session_state.pop("pending", None)
    log = st.container(height=340, border=False)  # the conversation scrolls here; the box stays put below it
    typed = st.chat_input("Ask about your throws", max_chars=ai_coach.MAX_QUESTION_CHARS)
    question = typed or pending
    with log:
        for m in chat:
            with st.chat_message(m["role"], avatar=AVATARS[m["role"]]):
                st.markdown(m["content"])
        if question:
            answer(question, throws, samples, key)
        elif not chat:
            for s in suggestions(throws is not None):
                st.button(s, on_click=send, args=(s,), icon=":material/auto_awesome:")
    if chat:
        st.button("Clear chat", on_click=lambda: st.session_state.chat.clear(), type="tertiary")


# ---------------------------------------------------------------
# About: how it works, what the numbers mean, what it can't do, who made it
# ---------------------------------------------------------------
def about_page(throws):
    st.title("About", anchor=False)
    data = ("No recordings are loaded yet." if throws is None else
            f"{len(throws)} throws are loaded from files you gave the app. The app can't tell a real recording from "
            "made-up numbers, so only load recordings you know are real.")
    st.markdown(f"""
### How it works
1. A small sensor goes on the outside of the throwing forearm, held on with a strap.
2. While you throw, it keeps checking how fast the forearm is spinning. Our sensor checks its spin many times a second.
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

### The Ask AI button
The Ask AI button floats over every page. Ask AI sends this session's numbers and your question to a language model (gpt-oss-120b by OpenAI, run by Groq). It gets numbers only, no names or video. It is told not to guess pitch speed, give medical advice or grade your throws, and it can still make mistakes, so the charts are the real answer. With no recordings loaded it can still explain how the sensor and the app work. The logo was first sketched with Google Gemini's image generator, then Claude redrew it as a sharp vector file.
""")


# ---------------------------------------------------------------
# Nothing loaded yet: say so plainly and let them load a recording
# ---------------------------------------------------------------
def empty_state():
    st.title("No recordings yet", anchor=False)
    st.caption("This app only shows recordings from the Kinetiq sensor. Load one to see your throws. "
               "You can still tap Ask AI to ask how the sensor works.")
    with st.container(border=True):
        a = st.file_uploader("throws.csv", type="csv", help="One row per throw: " + ", ".join(sorted(NEEDED["throws.csv"])))
        b = st.file_uploader("samples.csv", type="csv", help="Sensor readings: " + ", ".join(sorted(NEEDED["samples.csv"])))
        if a and b:
            throws, samples, problem = parse(pd.read_csv(a), pd.read_csv(b))
            if problem:
                st.error(problem)
            else:
                st.session_state.upload = (throws, samples)
                st.rerun()
    st.caption("Or put both files in web/recordings/ and restart the app. Columns are listed in web/README.md.")


# ---------------------------------------------------------------
# The app itself: a small top bar, the tabs, then whichever page is picked
# ---------------------------------------------------------------
data = load_data()
throws = data[0] if data else None
logo = base64.b64encode((ASSETS / "logo.svg").read_bytes()).decode()  # inlined so it works with no network
st.html(f'<div class="top"><img src="data:image/svg+xml;base64,{logo}" alt="Kinetiq"></div>')

st.session_state.setdefault("tab", TABS[0])
with st.container(key="tabs"):
    tab = st.segmented_control("Page", TABS, key="tab", required=True, label_visibility="collapsed", width="stretch")

if tab in DATA_TABS and data is None:
    empty_state()
else:
    {"Throws": throws_page, "One throw": one_page, "Compare": compare_page, "About": about_page}[tab](throws)
    if tab == "About" and "upload" in st.session_state:
        st.button("Remove the loaded recordings", on_click=lambda: st.session_state.pop("upload"))

st.button("Ask AI", key="fab", icon=":material/auto_awesome:", type="primary", on_click=open_ai)
if st.session_state.pop("ai_open", False):
    ai_dialog(data)
