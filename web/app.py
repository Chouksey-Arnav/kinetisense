
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

BLUE, FAINT, WARN = "#9dbcff", "#5b6378", "#fab219"
PASTELS = ["#c5c2ff", "#bcec70", "#ffcb87"]  # violet, green, peach from heylemon.ai

# The columns each CSV has to have, or the app stops with a clear message
NEEDED = {"demo_throws.csv": {"throw_id", "peak_time_s", "peak_dps", "clipped"},
          "demo_samples.csv": {"throw_id", "time_s", "gx", "gy", "gz", "gyro_mag"}}

st.set_page_config(page_title="KinetiSense", page_icon="⚾", layout="wide")

# ---------------------------------------------------------------
# Styles. Colors and fonts are in config.toml, so this is only the
# stuff a config file can't do: cards, the hero, labels and motion.
# Every card is an st.container(key="card...") so we can target it here.
# ---------------------------------------------------------------
GRAIN = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E"
         "%3CfeTurbulence type='fractalNoise' baseFrequency='.9'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")
st.html(f"""<style>
/* soft navy glow at the top of every page (raisedhand) */
.stApp {{ background: radial-gradient(1100px 520px at 50% -8%, #1d2b5c66, transparent 70%), #05070d; }}
/* serif headings (heylemon). config.toml loads the font, but Streamlit doesn't put it on headings for us */
h1, h2, h3 {{ font-family: 'Source Serif 4', Georgia, serif !important; letter-spacing: -.02em; }}
h1 em, h2 em {{ color: {BLUE}; }}

/* one animation for the whole app: fade up out of a blur (raisedhand's "lp-focus") */
@keyframes focus {{ from {{ opacity: 0; filter: blur(14px); transform: translateY(10px); }} }}
[class*="st-key-card"], .st-key-hero {{ animation: focus .8s cubic-bezier(.32,.72,0,1) both; }}
.st-key-card2, .st-key-card5, .st-key-card8 {{ animation-delay: .1s; }}  /* cards in a row come in one after another */
.st-key-card3, .st-key-card6, .st-key-card9 {{ animation-delay: .2s; }}

/* cards: big soft corners (heylemon), thin border, border lights up on hover */
[class*="st-key-card"] {{ background: #ffffff06; border: 1px solid #ffffff12; border-radius: 26px; padding: 26px;
                          transition: border-color .25s; }}
[class*="st-key-card"]:hover {{ border-color: #ffffff26; }}

/* the hero: violet (heylemon) melting into navy (raisedhand), with a little film grain */
.st-key-hero {{ position: relative; overflow: hidden; border-radius: 32px; padding: 72px 48px; text-align: center;
               background: radial-gradient(90% 70% at 50% 0%, #574cfd55, transparent 65%),
                           radial-gradient(70% 60% at 85% 100%, #2a4690aa, transparent 70%), #0b0f1c; }}
.st-key-hero::before {{ content: ""; position: absolute; inset: 0; background: url("{GRAIN}"); opacity: .07; pointer-events: none; }}
.st-key-hero h1 {{ font-size: clamp(2.6rem, 6vw, 4.6rem); line-height: 1.05; }}
.st-key-hero h1, .st-key-hero p {{ text-align: center; margin-left: auto; margin-right: auto; }}

/* small mono labels above titles, like "• HOW IT WORKS •" (heylemon) */
.eyebrow {{ font: 500 11.5px 'Geist Mono', monospace; letter-spacing: .16em; text-transform: uppercase; color: #8b93a7; margin: 0; }}
.lede {{ color: #a3aabb; font-size: 16.5px; line-height: 1.6; max-width: 640px; margin: 0; }}
.step {{ font: 500 11px 'Geist Mono', monospace; letter-spacing: .14em; text-transform: uppercase; color: {BLUE}; }}

/* big number cards. Pastel ones copy heylemon's stat row */
.stat {{ border-radius: 22px; padding: 22px 24px; height: 100%; background: #ffffff08; border: 1px solid #ffffff12; }}
.stat .big {{ font: 500 2.6rem/1.1 'Source Serif 4', serif; letter-spacing: -.02em; }}
.stat .label {{ font-weight: 600; margin-top: 6px; }}
.stat .note {{ color: #a3aabb; font-size: 14px; line-height: 1.5; margin-top: 8px; }}
.stat.pastel {{ color: #1a1a17; border: 0; }}
.stat.pastel .note {{ color: #1a1a17b3; }}

/* the cream pill button (heylemon) */
[data-testid="stBaseButton-primary"] {{ background: #fbfbed; color: #1a1a17; border: 0; }}
[data-testid="stBaseButton-primary"]:hover {{ background: #ffffff; color: #1a1a17; }}

/* thin strip across the top of every page (raisedhand has one for its launch offer) */
.banner {{ text-align: center; font-size: 13.5px; color: #e9d9b0; background: #fab21914; border: 1px solid #fab21933;
           border-radius: 999px; padding: 8px 16px; margin: 0 auto; max-width: 760px; }}

/* if someone's computer asks for less motion, we turn all of it off */
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}
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
        if df.empty or missing:
            st.error(f"{name} is empty or missing these columns: {sorted(missing)}")
            st.stop()
        df["throw_id"] = df["throw_id"].astype(str)
        frames[name] = df

    throws, samples = frames["demo_throws.csv"], frames["demo_samples.csv"]
    throws["turns"] = throws.peak_dps / 360  # 360° is one full turn, so this is turns per second
    throws["rank"] = throws.peak_dps.rank(ascending=False, method="min").astype(int)  # 1 = fastest
    throws["vs_avg"] = (throws.peak_dps / throws.peak_dps.mean() - 1) * 100       # % above or below average
    return throws, samples


def throw_window(throw_id):
    """One throw's samples, with time counted in milliseconds from its fastest moment."""
    throws, samples = load_data()
    peak_time = throws.loc[throws.throw_id == throw_id, "peak_time_s"].iloc[0]
    w = samples[samples.throw_id == throw_id].copy()
    w["t_ms"] = ((w.time_s - peak_time) * 1000).round().astype(int)
    w = w[w.t_ms.abs() <= WINDOW_MS]
    # words for the hover tooltip, so nobody has to decode "-33"
    w["when"] = w.t_ms.map(lambda t: "the fastest moment" if t == 0
                           else f"{abs(t)} ms {'before' if t < 0 else 'after'} the fastest moment")
    w["turns"] = w.gyro_mag / 360
    return w


# ---------------------------------------------------------------
# Little helpers so every page looks the same
# ---------------------------------------------------------------
def ordinal(n):
    """1 -> 1st, 2 -> 2nd, 3 -> 3rd, 11 -> 11th"""
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n if n < 20 else n % 10, 'th') }"


def eyebrow(text):
    st.html(f'<p class="eyebrow">• {text} •</p>')


def lede(text):
    st.html(f'<p class="lede">{text}</p>')


def stat(big, label, note, color=None):
    """A big number with a label and one plain sentence under it."""
    cls, bg = ("stat pastel", f' style="background:{color}"') if color else ("stat", "")
    st.html(f'<div class="{cls}"{bg}><div class="big">{big}</div>'
            f'<div class="label">{label}</div><div class="note">{note}</div></div>')


def hover(base, tooltip):
    """The hover crosshair: a line follows your mouse and a tooltip shows the numbers there."""
    pick = alt.selection_point(fields=["t_ms"], nearest=True, on="pointerover", empty=False)
    rule = base.mark_rule(color=FAINT).encode(
        opacity=alt.condition(pick, alt.value(1), alt.value(0)), tooltip=tooltip).add_params(pick)
    return rule, pick


X_AXIS = alt.X("t_ms:Q", title="Milliseconds from the fastest moment (0 = fastest, minus = before)")


# ---------------------------------------------------------------
# Page 1: Start here. Explains everything before showing any data.
# ---------------------------------------------------------------
def home_page():
    throws, _ = load_data()

    with st.container(key="hero"):
        eyebrow("Meet KinetiSense · forearm spin tracker")
        st.title("Every throw, *explained*.", anchor=False)
        lede("A small sensor straps to a pitcher's forearm and records how fast the forearm spins during each throw. "
             "This app turns those numbers into something any coach, player or judge can read.")
        st.write("")
        _, left, right, _ = st.columns([1, 1.2, 1.2, 1])  # the empty columns keep the buttons centered
        if left.button("See all throws", type="primary", use_container_width=True):
            st.switch_page(PAGES["all"])
        if right.button("How to read the numbers", use_container_width=True):
            st.switch_page(PAGES["one"])

    st.write("")
    eyebrow("How it works")
    st.header("Strap on. Throw. *Read it.*", anchor=False)
    steps = [("01 · Strap on", "The sensor sits on the outside of the throwing forearm, held by a strap."),
             ("02 · Throw", "It measures spin many times per second. In this demo it's 1,000 times per second, "
                            "so we catch the arm's fastest moment."),
             ("03 · Read", "Each throw shows up here: its top spin speed, when it happened, and a chart of the whole motion.")]
    for i, (col, (title, body)) in enumerate(zip(st.columns(3), steps), start=1):
        with col.container(key=f"card{i}"):
            st.html(f'<div class="step">{title}</div>')
            st.write(body)

    st.write("")
    eyebrow("The numbers in plain words")
    st.header("What every number *means*", anchor=False)
    words = [
        ("°/s (degrees per second)", "How fast the forearm is spinning. One full turn is 360°, "
         "so 3,600 °/s means 10 full turns per second at that instant."),
        ("Peak, or fastest moment", "The single instant in a throw when the forearm spins the fastest. "
         "Every chart lines up at this moment, called 0."),
        ("ms (milliseconds)", "One thousandth of a second. 100 ms is a tenth of a second. "
         "−50 ms means 50 ms before the fastest moment."),
        ("Throw 1, Throw 2, …", "Throws are numbered in the order they happened in the session."),
        ("Sensor limit (4,000 °/s)", "The most the sensor can read in one direction. If a throw hits it, "
         "the real speed was at least that high, so we flag it."),
        ("x, y, z", "The sensor tracks spin around three directions, like three skewers through the forearm "
         "at right angles. The 4,000 limit applies to each one on its own."),
    ]
    for start, row in ((4, words[:3]), (7, words[3:])):  # two rows of three
        for i, (col, (term, meaning)) in enumerate(zip(st.columns(3), row), start=start):
            with col.container(key=f"card{i}"):
                st.subheader(term, anchor=False)
                st.write(meaning)

    st.write("")
    with st.container(key="cardlimits"):
        st.subheader("What it does *not* measure", anchor=False)
        st.write("KinetiSense does not measure pitch speed (mph), ball spin, injury risk or arm health. "
                 "It measures forearm spin only. Turning that into pitch speed would need radar testing we haven't done yet.")


# ---------------------------------------------------------------
# Page 2: All throws. The whole session at a glance.
# ---------------------------------------------------------------
def all_page():
    throws, _ = load_data()
    fastest = throws.loc[throws.peak_dps.idxmax()]
    hit = int(throws.clipped.sum())

    eyebrow("All throws")
    st.title("The whole session, *at a glance*", anchor=False)
    lede("Each bar is one throw. Taller means the forearm spun faster at its peak. Hover a bar for details.")
    st.write("")

    a, b, c = st.columns(3)
    with a:
        stat(f"{len(throws)}", "throws in this session", "Numbered in the order they happened.", PASTELS[0])
    with b:
        stat(f"{fastest.peak_dps:,.0f} °/s", f"fastest throw (Throw {fastest.throw_id})",
             f"About {fastest.turns:.1f} full turns per second at its peak.", PASTELS[1])
    with c:
        stat(f"{hit}", "throws hit the sensor limit",
             f"Their real peak was at least {SENSOR_LIMIT:,} °/s in one direction.", PASTELS[2])

    st.write("")
    with st.container(key="card1"):
        df = throws.assign(label="Throw " + throws.throw_id,
                           status=throws.clipped.map({True: "Hit sensor limit", False: "Within sensor range"}))
        bars = alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, size=38).encode(
            x=alt.X("label:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("peak_dps:Q", title="Fastest spin in the throw (°/s)"),
            color=alt.Color("status:N", title=None, legend=alt.Legend(orient="top"),
                            scale=alt.Scale(domain=["Within sensor range", "Hit sensor limit"], range=[BLUE, WARN])),
            tooltip=[alt.Tooltip("label:N", title="Throw"),
                     alt.Tooltip("peak_dps:Q", title="Fastest spin (°/s)", format=",.0f"),
                     alt.Tooltip("turns:Q", title="Turns per second", format=".1f"),
                     alt.Tooltip("status:N", title="Sensor")])
        # dashed line for the session average, so you can see which throws were above it
        avg = alt.Chart(df).mark_rule(color="#a3aabb", strokeDash=[4, 4]).encode(y="mean(peak_dps):Q")
        st.altair_chart((bars + avg).properties(height=340, background="transparent"), use_container_width=True)
        st.caption(f"The dashed line is the session average ({throws.peak_dps.mean():,.0f} °/s). "
                   "Yellow bars hit the sensor limit, so their real peak could be higher than the bar shows. "
                   f"A throw can pass {SENSOR_LIMIT:,} in total without hitting the limit, "
                   "because the limit is for each direction on its own.")


# ---------------------------------------------------------------
# Page 3: One throw, up close. Explains the chart right next to it.
# ---------------------------------------------------------------
def one_page():
    throws, _ = load_data()

    eyebrow("One throw")
    st.title("One throw, *up close*", anchor=False)
    lede("Pick a throw to see how fast the forearm spun, how that compares to the rest of the session, "
         "and the whole motion from speeding up to slowing down.")
    st.write("")

    with st.container(key="card1"):
        peaks = throws.set_index("throw_id").peak_dps
        tid = st.selectbox("Pick a throw (numbered in the order they happened)", throws.throw_id,
                           format_func=lambda t: f"Throw {t}  ·  {peaks[t]:,.0f} °/s")
    row = throws.set_index("throw_id").loc[tid]

    # three explained numbers instead of three bare ones
    rank = "The fastest" if row["rank"] == 1 else f"{ordinal(row['rank'])} fastest"
    above = "above" if row.vs_avg >= 0 else "below"
    a, b, c = st.columns(3)
    with a:
        stat(f"{row.peak_dps:,.0f} °/s", "fastest spin in this throw",
             f"That's about {row.turns:.1f} full turns of the forearm per second, for an instant.")
    with b:
        stat(f"{abs(row.vs_avg):.0f}% {above}", "this session's average",
             f"{rank} of {len(throws)} throws in this session.")
    with c:
        if row.clipped:
            stat("Hit limit", "sensor maxed out", f"One direction reached {SENSOR_LIMIT:,} °/s, the most the sensor "
                 "can read. The real peak was at least as fast as shown.")
        else:
            stat("In range", "sensor did not max out", f"No direction reached the {SENSOR_LIMIT:,} °/s limit, "
                 "so this peak is the full reading.")

    st.write("")
    with st.container(key="card2"):
        view = st.segmented_control("Chart view", ["Total spin", "Spin in each direction"],
                                    default="Total spin", label_visibility="collapsed")
        w = throw_window(tid)
        chart, how_to = st.columns([3, 1.1])

        if view == "Spin in each direction":
            axes = w.melt(id_vars=["t_ms", "when"], value_vars=["gx", "gy", "gz"], var_name="dir", value_name="dps")
            axes["dir"] = axes.dir.str[1]   # "gx" -> "x"
            axes["dps"] = axes.dps.abs()    # the limit is the same both ways, so we plot the size only
            base = alt.Chart(axes).encode(x=X_AXIS)
            rule, pick = hover(base, [alt.Tooltip("when:N", title="When"), alt.Tooltip("dir:N", title="Direction"),
                                      alt.Tooltip("dps:Q", title="Spin (°/s)", format=",.0f")])
            lines = base.mark_line(strokeWidth=2).encode(
                y=alt.Y("dps:Q", title="Spin in one direction (°/s)"), color=alt.Color("dir:N", title="Direction"))
            limit = alt.Chart(pd.DataFrame({"y": [SENSOR_LIMIT]})).mark_rule(color=WARN, strokeDash=[4, 4]).encode(y="y:Q")
            layers = [lines, rule, limit]
            how = ("**How to read this**\n\n1. Each line is spin around one direction (x, y or z).\n"
                   f"2. The dashed yellow line is the {SENSOR_LIMIT:,} °/s sensor limit.\n"
                   "3. A line touching it means that direction maxed out.")
        else:
            base = alt.Chart(w).encode(x=X_AXIS)
            rule, pick = hover(base, [alt.Tooltip("when:N", title="When"),
                                      alt.Tooltip("gyro_mag:Q", title="Spin (°/s)", format=",.0f"),
                                      alt.Tooltip("turns:Q", title="Turns per second", format=".1f")])
            line = base.mark_line(strokeWidth=2.2, color=BLUE).encode(y=alt.Y("gyro_mag:Q", title="Forearm spin (°/s)"))
            dot = line.mark_point(filled=True, size=70, color=BLUE).encode(
                opacity=alt.condition(pick, alt.value(1), alt.value(0)))
            # label the peak right on the chart so nobody has to hunt for it
            peak = w[w.t_ms == 0]
            peak_dot = alt.Chart(peak).mark_point(filled=True, size=90, color="#fbfbed").encode(x="t_ms:Q", y="gyro_mag:Q")
            peak_txt = peak_dot.mark_text(dx=12, dy=4, align="left", color="#fbfbed").encode(
                text=alt.value(f"Fastest moment: {row.peak_dps:,.0f} °/s"))
            layers = [line, dot, rule, peak_dot, peak_txt]
            how = ("**How to read this**\n\n1. Left to right is time. 0 is the fastest moment.\n"
                   "2. Higher means the forearm is spinning faster.\n"
                   "3. Left of 0 the spin is speeding up. Right of 0 it's slowing down.\n\n"
                   "Hover the line to read any moment.")

        chart.altair_chart(alt.layer(*layers).properties(height=360, background="transparent"),
                           use_container_width=True)
        how_to.markdown(how)


# ---------------------------------------------------------------
# Page 4: Compare. Lay throws on top of each other.
# ---------------------------------------------------------------
def compare_page():
    throws, _ = load_data()

    eyebrow("Compare")
    st.title("Throws, *side by side*", anchor=False)
    lede("Every throw is lined up at its fastest moment, so you can compare the shapes directly. "
         "Similar shapes mean the arm sped up and slowed down with similar timing.")
    st.write("")

    with st.container(key="card1"):
        ids = st.multiselect(f"Pick up to {MAX_COMPARE} throws", throws.throw_id, default=list(throws.throw_id[:2]),
                             max_selections=MAX_COMPARE, format_func=lambda t: f"Throw {t}")
    if not ids:
        st.info("Pick at least one throw above.")
        return

    with st.container(key="card2"):
        df = pd.concat(throw_window(t) for t in ids)
        df["throw"] = "Throw " + df.throw_id
        names = sorted(df.throw.unique())
        base = alt.Chart(df).encode(x=X_AXIS)
        lines = base.mark_line(strokeWidth=2).encode(y=alt.Y("gyro_mag:Q", title="Forearm spin (°/s)"),
                                                     color=alt.Color("throw:N", title=None))
        # pivot turns rows into one column per throw, so the tooltip lists every throw at that moment
        rule, _ = hover(base.transform_pivot("throw", value="gyro_mag", groupby=["t_ms", "when"]),
                        [alt.Tooltip("when:N", title="When")] +
                        [alt.Tooltip(f"{n}:Q", title=f"{n} (°/s)", format=",.0f") for n in names])
        st.altair_chart(alt.layer(lines, rule).properties(height=360, background="transparent"),
                        use_container_width=True)
        st.caption("A few throws can't prove a pitcher is consistent. It takes many throws over many sessions.")

    with st.container(key="card3"):
        table = throws[throws.throw_id.isin(ids)]
        st.dataframe(pd.DataFrame({
            "Throw": "Throw " + table.throw_id,
            "Fastest spin (°/s)": table.peak_dps.map("{:,.0f}".format),
            "Turns per second": table.turns.map("{:.1f}".format),
            "Rank in session": table["rank"].map(ordinal),
            "Hit sensor limit": table.clipped.map({True: "Yes", False: "No"}),
        }), hide_index=True, use_container_width=True)


# ---------------------------------------------------------------
# Page 5: About. Who made it, what it can't do, and how we used AI.
# ---------------------------------------------------------------
def about_page():
    throws, _ = load_data()

    eyebrow("About")
    st.title("About *KinetiSense*", anchor=False)
    lede("Built by Arnav Chouksey and Vatsalya Vishnoi for the Congressional App Challenge.")
    st.write("")

    cards = [
        ("What it is", "A wearable sensor for youth pitchers that straps to the outer forearm and records how fast "
         "the forearm spins during a throw. This app shows those throws."),
        ("What it does not do", "It does not measure pitch speed, ball spin, injury risk or health. "
         "We won't claim any of that unless real testing backs it up."),
        ("The data you're looking at", f"These {len(throws)} throws are demo data made by a computer program, not a "
         "real recording. They let you try the app while we finish the hardware."
         if DATA_IS_SYNTHETIC else f"These {len(throws)} throws are real recordings from the sensor."),
        ("Sensor limit", f"The sensor can read up to {SENSOR_LIMIT:,} °/s in each direction, according to its "
         "datasheet. We haven't confirmed that on our own device yet."),
        ("How we used AI", "An AI (Claude) wrote the code and design of this app. "
         "Every AI use in the project is listed in AI_USAGE.md in our code."),
    ]
    for i, (title, body) in enumerate(cards, start=1):
        with st.container(key=f"card{i}"):
            st.subheader(title, anchor=False)
            st.write(body)


# ---------------------------------------------------------------
# Navigation along the top, like a website
# ---------------------------------------------------------------
PAGES = {
    "home": st.Page(home_page, title="Start here", icon=":material/home:", default=True),
    "all": st.Page(all_page, title="All throws", icon=":material/bar_chart:"),
    "one": st.Page(one_page, title="One throw", icon=":material/show_chart:"),
    "compare": st.Page(compare_page, title="Compare", icon=":material/stacked_line_chart:"),
    "about": st.Page(about_page, title="About", icon=":material/info:"),
}
page = st.navigation(list(PAGES.values()), position="top")

if DATA_IS_SYNTHETIC:
    st.html('<div class="banner">Demo mode: these throws were made by a computer so you can try the app. '
            'Real sensor data comes next.</div>')

page.run()
