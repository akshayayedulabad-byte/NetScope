import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.database.db_manager import get_all_measurements

st.set_page_config(page_title="NetScope Filter", layout="wide")
st.title("NetScope – Filter by Network & History")

df = pd.DataFrame(get_all_measurements())

if df.empty:
    st.warning("No data found.")
    st.stop()

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

ssid = st.selectbox("Select Network", sorted(df["ssid"].unique()))
filtered = df[df["ssid"] == ssid].sort_values("timestamp")

st.subheader(f"All measurements for: {ssid}")
st.dataframe(filtered[["signal_dbm", "x", "y", "timestamp", "notes"]], use_container_width=True)

# Simple historical comparison
st.subheader("Recent Measurements")

if not df.empty:
    st.dataframe(
        df[["id", "ssid", "signal_dbm", "x", "y", "timestamp"]].head(15),
        use_container_width=True
    )

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download All Data as CSV",
        data=csv_data,
        file_name="netscope_data.csv",
        mime="text/csv"
    )

else:
    st.info("No data yet. Go to 'Collect Data' page and start scanning.")