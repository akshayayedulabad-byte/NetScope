import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.database.db_manager import get_all_measurements, create_tables

st.set_page_config(page_title="NetScope Dashboard", layout="wide", page_icon="📡")

create_tables()

st.title("📡 NetScope – Intelligent Indoor Wi-Fi Coverage System")
st.markdown("### College PBL Project Dashboard")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Home",
    "Collect Data",
    "View Map & Heatmap",
    "Statistics & Dead Zones",
    "Filter by Network"
])

data = get_all_measurements()
df = pd.DataFrame(data) if data else pd.DataFrame()

if page == "Home":
    st.header("Welcome to NetScope")
    st.write("This system measures Wi-Fi signal strength, maps it on a floor plan, generates heatmaps, and identifies potential dead-zone candidates.")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Measurements", len(df))
    col2.metric("Unique Networks", df["ssid"].nunique() if not df.empty else 0)
    col3.metric("Strongest Signal", f"{df['signal_dbm'].max()} dBm" if not df.empty else "N/A")
    col4.metric("Weakest Signal", f"{df['signal_dbm'].min()} dBm" if not df.empty else "N/A")

    st.subheader("Recent Measurements")
    if not df.empty:
        st.dataframe(df[["id", "ssid", "signal_dbm", "x", "y", "timestamp"]].head(15), use_container_width=True)
    else:
        st.info("No data yet. Go to 'Collect Data' page and start scanning.")

elif page == "Collect Data":
    st.info("Open the Collect Data page separately for best experience:")
    st.code("streamlit run src/dashboard/collect_page.py")

elif page == "View Map & Heatmap":
    st.info("This page will be completed in Stage 9 & 10. Coming next...")

elif page == "Statistics & Dead Zones":
    st.info("This page will be completed in Stage 11.")

elif page == "Filter by Network":
    st.info("This page will be completed in Stage 12.")