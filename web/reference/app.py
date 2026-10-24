"""KinetiSense web viewer, REFERENCE DESIGN.

Written by Claude (AI) as an example of the design system in docs/design_system.md.
It is logged in AI_USAGE.md. It is not the submission app. Read it, then build
your own version in web/app.py. Do not copy it in without disclosing that.

Run:  cd web/reference  then  streamlit run app.py
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# ---------- constants ----------
DATA_DIR = Path(__file__).resolve().parent.parent / "sample_data"
DATA_IS_SYNTHETIC = True
AXIS_LIMIT_DPS = 4000          # datasheet range per axis, not yet verified on the device
ACCENT = "#8fa8ff"
MAX_COMPARE = 3                # the chart palette is colorblind tested for 3 lines only
NEEDED = {"throws": {"throw_id", "peak_time_s", "peak_dps", "clipped"},
          "samples": {"throw_id", "time_s", "gx", "gy", "gz", "gyro_mag"}}

st.set_page_config(page_title="KinetiSense", page_icon="⚾", layout="wide")

# ---------- styles: one keyframe, one card, one label style ----------
st.html("""<style>
@keyframes rise{from{opacity:0;transform:translateY(12px);filter:blur(4px)}}
[class*="st-key-card"]{background:#0b0e14;border:1px solid #1c2230;border-radius:20px;padding:24px;
  animation:rise .6s cubic-bezier(.2,.7,.3,1) both;transition:border-color .2s}
[class*="st-key-card"]:hover{border-color:#2c3550}
.st-key-card2{animation-delay:.08s}.st-key-card3{animation-delay:.16s}.st-key-card4{animation-delay:.24s}
.eyebrow{font:500 11px 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#8b93a7;margin:0}
.demo{color:#fab219}
.lede{color:#8b93a7;font-size:15px;max-width:640px;margin:0}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>""")


# ---------- data ----------
@st.cache_data
def load_data():
    throws = pd.read_csv(DATA_DIR / "demo_throws.csv")
    samples = pd.read_csv(DATA_DIR / "demo_samples.csv")
    for name, df in (("throws", throws), ("samples", samples)):
        missing = NEEDED[name] - set(df.columns)
        if df.empty or missing:
            st.error(f"{name} file is empty or missing columns: {sorted(missing)}")
            st.stop()
    throws["throw_id"] = throws["throw_id"].astype(str)
    samples["throw_id"] = samples["throw_id"].astype(str)
    return throws, samples


def throw_window(samples, throws, throw_id):
    """Samples for one throw, with time in ms relative to its peak."""
    peak = throws.loc[throws.throw_id == throw_id, "peak_time_s"].iloc[0]
    w = samples[samples.throw_id == throw_id].copy()
    w["t_ms"] = ((w.time_s - peak) * 1000).round()
    return w


# ---------- small UI helpers ----------
def header(eyebrow, title, lede):
    demo = ' · <span class="demo">Demo data, synthetic</span>' if DATA_IS_SYNTHETIC else ""
    st.html(f'<p class="eyebrow">{eyebrow}{demo}</p>')
    st.title(title)
    st.html(f'<p class="lede">{lede}</p>')


def line_chart(df, y, color=None, y_title="Angular velocity (°/s)", extra=None):
    """Line chart with a hover crosshair. The tooltip lists every line at that moment."""
    names = sorted(df[color].unique()) if color else [y]
    hover = alt.selection_point(fields=["t_ms"], nearest=True, on="pointerover", empty=False)
    base = alt.Chart(df).encode(x=alt.X("t_ms:Q", title="Time from peak (ms)"))
    line = base.mark_line(strokeWidth=2).encode(
        y=alt.Y(f"{y}:Q", title=y_title),
        color=alt.Color(f"{color}:N", title=None) if color else alt.value(ACCENT))
    dots = line.mark_point(filled=True, size=60).encode(
        opacity=alt.condition(hover, alt.value(1), alt.value(0)))
    wide = base.transform_pivot(color, value=y, groupby=["t_ms"]) if color else base
    rule = wide.mark_rule(color="#5b6378").encode(
        opacity=alt.condition(hover, alt.value(1), alt.value(0)),
        tooltip=[alt.Tooltip("t_ms:Q", title="ms from peak")] +
                [alt.Tooltip(f"{n}:Q", format=",.0f", title=n if color else "°/s") for n in names],
    ).add_params(hover)
    layers = [line, dots, rule] + ([extra] if extra is not None else [])
    return alt.layer(*layers).properties(height=320, background="transparent")


# ---------- pages ----------
def throw_page():
    throws, samples = load_data()
    header("Throw analysis", "One throw, up close",
           "Forearm angular velocity from the wrist sensor, centered on the moment of peak rotation.")

    with st.container(key="card1"):
        tid = st.selectbox("Throw", throws.throw_id, format_func=lambda t: f"Throw {t}")
    row = throws[throws.throw_id == tid].iloc[0]

    with st.container(key="card2"):
        a, b, c = st.columns(3)
        a.metric("Peak angular velocity", f"{row.peak_dps:,.0f} °/s",
                 help="Combined speed of all three gyro axes at the peak.")
        b.metric("Peak happened at", f"{row.peak_time_s:.2f} s", help="Seconds into the recording.")
        c.metric("Sensor range", "Reached" if row.clipped else "Within range",
                 help=f"Whether any single axis hit the {AXIS_LIMIT_DPS:,} °/s datasheet range.")
        if row.clipped:
            st.warning(f"One axis reached {AXIS_LIMIT_DPS:,} °/s, the most the sensor can record. "
                       "The real peak was at least this high, so the number above is a lower bound.",
                       icon=":material/warning:")

    with st.container(key="card3"):
        view = st.segmented_control("View", ["Combined", "Per axis"], default="Combined",
                                    label_visibility="collapsed")
        w = throw_window(samples, throws, tid)
        if view == "Per axis":
            axes = w.melt(id_vars="t_ms", value_vars=["gx", "gy", "gz"], var_name="axis", value_name="dps")
            axes["dps"] = axes.dps.abs()
            limit = alt.Chart(pd.DataFrame({"y": [AXIS_LIMIT_DPS]})).mark_rule(
                color="#fab219", strokeDash=[4, 4]).encode(y="y:Q")
            st.altair_chart(line_chart(axes, "dps", "axis", "Axis speed, absolute (°/s)", limit),
                            use_container_width=True)
            st.caption(f"Dashed line: the {AXIS_LIMIT_DPS:,} °/s range of each axis. "
                       "A flat top on that line means the axis was clipped.")
        else:
            st.altair_chart(line_chart(w, "gyro_mag"), use_container_width=True)
            st.caption("Hover the curve to read exact values. The sensor range applies to each axis, "
                       "so switch to Per axis to see it.")


def compare_page():
    throws, samples = load_data()
    header("Compare", "Throws side by side",
           "Curves are lined up at their peaks so the shapes can be compared directly.")

    with st.container(key="card1"):
        ids = st.multiselect("Throws", throws.throw_id, default=list(throws.throw_id[:2]),
                             max_selections=MAX_COMPARE, format_func=lambda t: f"Throw {t}")
    if not ids:
        st.info("Pick at least one throw.")
        return

    with st.container(key="card2"):
        df = pd.concat(throw_window(samples, throws, t) for t in ids)
        df["throw"] = "Throw " + df.throw_id
        st.altair_chart(line_chart(df, "gyro_mag", "throw"), use_container_width=True)
        st.caption("Similar shapes suggest similar timing. A handful of throws cannot prove consistency.")

    with st.container(key="card3"):
        table = throws[throws.throw_id.isin(ids)].rename(columns={
            "throw_id": "Throw", "peak_dps": "Peak (°/s)", "peak_time_s": "Peak at (s)",
            "clipped": "Sensor range reached"})
        st.dataframe(table, hide_index=True, use_container_width=True)


def about_page():
    throws, _ = load_data()
    header("About", "What KinetiSense measures",
           "A wrist worn motion sensor and a viewer for youth pitchers.")
    cards = [
        ("What it does", f"Records forearm angular velocity during throws and shows each one. "
                         f"This dataset has {len(throws)} throws."),
        ("What it does not do", "It does not measure pitch speed, ball spin, injury risk or health."),
        ("Sensor range", f"Each axis can record up to {AXIS_LIMIT_DPS:,} °/s according to the datasheet. "
                         "This has not been verified on the real device yet."),
        ("AI use", "AI tools helped with parts of this project. Every use is listed in AI_USAGE.md."),
    ]
    for i, (title, body) in enumerate(cards, start=1):
        with st.container(key=f"card{i}"):
            st.subheader(title)
            st.write(body)


# ---------- navigation ----------
st.navigation([
    st.Page(throw_page, title="Throw analysis", icon=":material/show_chart:", default=True),
    st.Page(compare_page, title="Compare", icon=":material/stacked_line_chart:"),
    st.Page(about_page, title="About", icon=":material/info:"),
], position="top").run()
