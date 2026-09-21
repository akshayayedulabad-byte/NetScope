import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.database.db_manager import get_all_measurements

st.set_page_config(page_title="NetScope Statistics", layout="wide")
st.title("NetScope – Statistics & Potential Dead-Zone Candidates")

data = get_all_measurements()
df = pd.DataFrame(data) if data else pd.DataFrame()

if df.empty:
    st.warning("No data available.")
    st.stop()

# Threshold for weak signal (you can change this)
WEAK_THRESHOLD = -75   # dBm

st.sidebar.header("Settings")
WEAK_THRESHOLD = st.sidebar.slider("Weak Signal Threshold (dBm)", -90, -50, -75)

# Overall statistics
st.subheader("Overall Signal Statistics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Points", len(df))
col2.metric("Average Signal", f"{df['signal_dbm'].mean():.1f} dBm")
col3.metric("Strongest", f"{df['signal_dbm'].max()} dBm")
col4.metric("Weakest", f"{df['signal_dbm'].min()} dBm")

# Potential dead-zone candidates
weak_df = df[df["signal_dbm"] <= WEAK_THRESHOLD].copy()
st.subheader(f"Potential Dead-Zone Candidates (≤ {WEAK_THRESHOLD} dBm)")
st.write(f"Found **{len(weak_df)}** potential weak areas out of {len(df)} total measurements.")

if not weak_df.empty:
    st.dataframe(
        weak_df[["ssid", "signal_dbm", "x", "y", "timestamp", "notes"]].sort_values("signal_dbm"),
        use_container_width=True
    )
else:
    st.success("No potential dead-zone candidates found with the current threshold.")

# Per network summary
st.subheader("Signal Summary by Network")
summary = df.groupby("ssid").agg(
    count=("signal_dbm", "count"),
    avg_signal=("signal_dbm", "mean"),
    min_signal=("signal_dbm", "min"),
    max_signal=("signal_dbm", "max")
).round(1).sort_values("avg_signal")
st.dataframe(summary, use_container_width=True)