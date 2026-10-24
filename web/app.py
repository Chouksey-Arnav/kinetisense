import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# --- CONSTANTS ---
# per ST datasheet range; real clipping level still to be verified on the device
# REMINDER ON SWAP DAY: Restart the Streamlit app after replacing data files to clear cache.
SENSOR_LIMIT_DPS = 4000
DATA_IS_SYNTHETIC = True


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="KinetiSense Throw Analyzer",
    page_icon="⚾",
    layout="wide"
)


if DATA_IS_SYNTHETIC:
    st.warning("DEMO DATA: synthetic dataset.")


# --- DATA LOADING & VALIDATION ---
@st.cache_data
def load_data():
    data_dir = Path(__file__).parent / "sample_data"
    throws_path = data_dir / "demo_throws.csv"
    samples_path = data_dir / "demo_samples.csv"
    
    if not throws_path.exists():
        st.error(f"Error: Could not find 'demo_throws.csv' in '{data_dir}/'. Please generate the required demo files.")
        st.stop()
    if not samples_path.exists():
        st.error(f"Error: Could not find 'demo_samples.csv' in '{data_dir}/'. Please generate the required demo files.")
        st.stop()
        
    throws_df = pd.read_csv(throws_path)
    samples_df = pd.read_csv(samples_path)
    
    # Check if dataframes are empty to prevent crashes
    if throws_df.empty:
        st.error("Error: 'demo_throws.csv' is empty. Please provide valid throw records.")
        st.stop()
    if samples_df.empty:
        st.error("Error: 'demo_samples.csv' is empty. Please provide valid sample records.")
        st.stop()
    
    # Check for required columns in throws
    required_throw_cols = ['throw_id', 'peak_time_s', 'peak_dps', 'clipped']
    for col in required_throw_cols:
        if col not in throws_df.columns:
            st.error(f"Error: Missing required column '{col}' in demo_throws.csv")
            st.stop()
            
    # Check for required columns in samples
    required_sample_cols = ['throw_id', 'time_s', 'gyro_mag']
    for col in required_sample_cols:
        if col not in samples_df.columns:
            st.error(f"Error: Missing required column '{col}' in demo_samples.csv")
            st.stop()
    
    # Ensure throw_id types match as strings to prevent silent failures
    throws_df['throw_id'] = throws_df['throw_id'].astype(str)
    samples_df['throw_id'] = samples_df['throw_id'].astype(str)
    
    # Check for blank or missing values in 'clipped'
    if throws_df['clipped'].isna().any():
        st.error("Error: Found blank or missing values in the 'clipped' column of throws data.")
        st.stop()
        
    # Check that every throw_id in throws appears in samples
    throws_set = set(throws_df['throw_id'])
    samples_set = set(samples_df['throw_id'])
    
    missing_samples = throws_set - samples_set
    if missing_samples:
        st.error(f"Error: The following throw IDs have no sample rows in demo_samples.csv: {missing_samples}")
        st.stop()
        
    return throws_df, samples_df


throws_df, samples_df = load_data()


# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Throw Analysis", "Compare Throws", "About and Limits"])


# ==========================================
# PAGE 1: THROW ANALYSIS
# ==========================================
if page == "Throw Analysis":
    st.title("⚾ Throw Analysis & Comparison")
    st.write("Inspect individual throw metrics, sensor limits, and multi-throw telemetry overlays.")
    
    selected_throw = st.selectbox("Select Throw", throws_df['throw_id'].tolist())
    
    throw_row = throws_df[throws_df['throw_id'] == selected_throw].iloc[0]
    throw_samples = samples_df[samples_df['throw_id'] == selected_throw]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Throw ID", throw_row['throw_id'])
    col2.metric("Peak Time (s)", f"{throw_row['peak_time_s']:.2f}")
    col3.metric("Peak Angular Velocity (deg/s)", f"{throw_row['peak_dps']:.1f}")
    
    is_clipped = bool(throw_row['clipped'])
    if is_clipped:
        st.error(
            f"⚠️ **Sensor Saturation Warning:** At least one axis reached the sensor limit ({SENSOR_LIMIT_DPS} deg/s). "
            f"The true peak is higher than the number shown. For clipped throws, the shown peak is a minimum."
        )
        
    # Plotting angular velocity profile
    fig, ax = plt.subplots(figsize=(10, 4))
    
    if not throw_samples.empty:
        time_rel = throw_samples['time_s'] - throw_row['peak_time_s']
        ax.plot(time_rel, throw_samples['gyro_mag'], label="Combined Gyro Magnitude", color="blue", linewidth=2)
    
    ax.axhline(y=SENSOR_LIMIT_DPS, color="orange", linestyle="--", linewidth=2, label="Sensor Limit (per axis)")
    ax.scatter([0], [throw_row['peak_dps']], color="red", s=60, zorder=5, label="Peak Moment")
    
    ax.set_xlabel("Time from Peak (seconds)", fontsize=12)
    ax.set_ylabel("Angular Velocity (deg/s)", fontsize=12)
    ax.set_title(f"Throw {selected_throw} Angular Velocity Profile", fontsize=14)
    ax.legend(loc="lower right")
    ax.grid(True, linestyle=":", alpha=0.6)
    
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Note: The orange dashed line represents the per-axis sensor limit (4000 deg/s). The blue line shows combined magnitude, which can exceed the single-axis limit vectorially without indicating clipping.")


# ==========================================
# PAGE 2: COMPARE THROWS
# ==========================================
elif page == "Compare Throws":
    st.title("📊 Multi-Throw Comparison")
    st.write("Compare telemetry profiles across multiple throws simultaneously.")
    
    selected_compared = st.multiselect("Select throws to compare", throws_df['throw_id'].tolist(), default=throws_df['throw_id'].tolist()[:2])
    
    if not selected_compared:
        st.info("Please select at least one throw to compare.")
    else:
        fig, ax = plt.subplots(figsize=(10, 4))
        
        for t_id in selected_compared:
            t_row = throws_df[throws_df['throw_id'] == t_id].iloc[0]
            t_samples = samples_df[samples_df['throw_id'] == t_id]
            if not t_samples.empty:
                time_rel = t_samples['time_s'] - t_row['peak_time_s']
                ax.plot(time_rel, t_samples['gyro_mag'], label=f"Throw {t_id}", linewidth=1.5)
                
        ax.axhline(y=SENSOR_LIMIT_DPS, color="orange", linestyle="--", linewidth=2, label="Sensor Limit (per axis)")
        ax.set_xlabel("Time from Peak (seconds)", fontsize=12)
        ax.set_ylabel("Angular Velocity (deg/s)", fontsize=12)
        ax.set_title("Multi-Throw Telemetry Comparison", fontsize=14)
        ax.legend(loc="upper right")
        ax.grid(True, linestyle=":", alpha=0.6)
        
        st.pyplot(fig)
        plt.close(fig)
        st.caption("Note: The orange dashed line represents the per-axis sensor limit (4000 deg/s). Individual traces show combined magnitude.")


# ==========================================
# PAGE 3: ABOUT AND LIMITS
# ==========================================
elif page == "About and Limits":
    st.title("ℹ️ About KinetiSense")
    st.write("System scope, data boundaries, and technical disclosures.")
    
    st.subheader("System Scope:")
    if DATA_IS_SYNTHETIC:
        st.write(f"This demo contains {len(throws_df)} throws. KinetiSense is an analytics web viewer designed to display processed wearable IMU sensor data, specifically focusing on forearm rotational velocity during athletic throws.")
    else:
        st.write(f"This dataset contains {len(throws_df)} throws. KinetiSense is an analytics web viewer designed to display processed wearable IMU sensor data, specifically focusing on forearm rotational velocity during athletic throws.")
    
    st.subheader("System Boundaries & Scope:")
    if DATA_IS_SYNTHETIC:
        st.warning(
            "• **Demo Data:** Uses synthetic/fake dataset for demonstration purposes.\n"
            "• **Motion Scope:** Measures forearm rotation only (does not measure pitch velocity, health status, or injury risk).\n"
            "• **Sensor Limits:** The 4000 deg/s limit represents per-axis hardware saturation. When saturated, the true rotational speed is higher than recorded."
        )
    else:
        st.warning(
            "• **Motion Scope:** Measures forearm rotation only (does not measure pitch velocity, health status, or injury risk).\n"
            "• **Sensor Limits:** The 4000 deg/s limit represents per-axis hardware saturation. When saturated, the true rotational speed is higher than recorded."
        )
        
    st.subheader("AI Assistance Disclosure:")
    st.write("AI assistance was used during development to streamline documentation structuring and code implementation.")
