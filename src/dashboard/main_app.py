import streamlit as st
import pandas as pd
import os
import sys
import numpy as np
import plotly.graph_objects as go
from PIL import Image
from scipy.interpolate import griddata

from streamlit_image_coordinates import streamlit_image_coordinates

# Project path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

from src.scanner.wifi_scanner import scan_wifi_networks
from src.database.db_manager import (
    create_tables,
    insert_measurement,
    get_all_measurements
)

# Page configuration
st.set_page_config(
    page_title="NetScope Dashboard",
    page_icon="📡",
    layout="wide"
)

# Initialize database and folders
create_tables()
os.makedirs("data/floorplans", exist_ok=True)

# Sidebar
st.sidebar.title("📡 NetScope")
st.sidebar.write("Indoor Wi-Fi Coverage System")

page = st.sidebar.radio(
    "Navigate to",
    [
        "Home",
        "Collect Data",
        "View Map & Heatmap",
        "Statistics & Dead Zones",
        "Filter by Network"
    ]
)

# Load database data
data = get_all_measurements()
df = pd.DataFrame(data) if data else pd.DataFrame()


# =====================================================
# HOME PAGE
# =====================================================

if page == "Home":

    st.title("📡 NetScope")
    st.subheader("Intelligent Indoor Wi-Fi Coverage System")

    st.write(
        "NetScope measures Wi-Fi signal strength at different "
        "locations, displays measurements on a floor plan, "
        "generates heatmaps, and identifies potential dead-zone candidates."
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Measurements", len(df))

    col2.metric(
        "Unique Networks",
        df["ssid"].nunique() if not df.empty else 0
    )

    col3.metric(
        "Strongest Signal",
        f"{df['signal_dbm'].max()} dBm" if not df.empty else "N/A"
    )

    col4.metric(
        "Weakest Signal",
        f"{df['signal_dbm'].min()} dBm" if not df.empty else "N/A"
    )

    st.subheader("Recent Measurements")

    if not df.empty:
        st.dataframe(
            df[
                ["id", "ssid", "signal_dbm", "x", "y", "timestamp"]
            ].head(15),
            use_container_width=True
        )

        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download All Data as CSV",
            data=csv_data,
            file_name="netscope_data.csv",
            mime="text/csv"
        )

    else:
        st.info("No measurements available yet.")


# =====================================================
# COLLECT DATA PAGE
# =====================================================

elif page == "Collect Data":

    st.title("📍 Collect Wi-Fi Measurements")

    if "last_x" not in st.session_state:
        st.session_state["last_x"] = None

    if "last_y" not in st.session_state:
        st.session_state["last_y"] = None

    if "floorplan_path" not in st.session_state:
        st.session_state["floorplan_path"] = None

    st.header("1. Upload Floor Plan")

    uploaded_file = st.file_uploader(
        "Choose a floor-plan image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:

        image_path = os.path.join(
            "data/floorplans",
            uploaded_file.name
        )

        with open(image_path, "wb") as file:
            file.write(uploaded_file.getbuffer())

        st.session_state["floorplan_path"] = image_path
        st.success("Floor plan uploaded successfully!")

    if (
        st.session_state["floorplan_path"] is not None
        and os.path.exists(st.session_state["floorplan_path"])
    ):

        st.header("2. Select Your Location")

        image = Image.open(
            st.session_state["floorplan_path"]
        ).convert("RGB")

        st.write("Click on the floor plan where you are standing:")

        coordinates = streamlit_image_coordinates(
            image,
            key="main_collection_floorplan"
        )

        if coordinates is not None:
            st.session_state["last_x"] = coordinates["x"]
            st.session_state["last_y"] = coordinates["y"]

        if st.session_state["last_x"] is not None:
            st.success(
                f"Selected location: X = {st.session_state['last_x']}, "
                f"Y = {st.session_state['last_y']}"
            )
        else:
            st.warning("Please click on the floor plan.")

        st.header("3. Scan and Save Wi-Fi Data")

        notes = st.text_input(
            "Optional notes",
            placeholder="Example: Classroom, corridor, laboratory"
        )

        if st.button(
            "📡 Scan Wi-Fi & Save Measurement",
            type="primary"
        ):

            if (
                st.session_state["last_x"] is None
                or st.session_state["last_y"] is None
            ):
                st.error("Please select a location first.")

            else:

                with st.spinner("Scanning nearby Wi-Fi networks..."):
                    networks = scan_wifi_networks()

                if not networks:
                    st.error("No Wi-Fi networks found.")

                else:

                    saved_count = 0

                    for network in networks:

                        insert_measurement(
                            ssid=network.get("ssid", "Unknown"),
                            bssid=network.get("bssid"),
                            signal_dbm=network.get("signal"),
                            signal_percent=network.get("signal_percent"),
                            channel=network.get("channel"),
                            frequency=network.get("frequency"),
                            x=st.session_state["last_x"],
                            y=st.session_state["last_y"],
                            notes=notes
                        )

                        saved_count += 1

                    st.success(
                        f"Successfully saved {saved_count} measurements!"
                    )

                    st.subheader("Networks Saved")

                    for network in networks:
                        st.write(
                            f"**{network.get('ssid', 'Unknown')}** — "
                            f"{network.get('signal')} dBm"
                        )

    else:
        st.info("Upload a floor plan to begin.")


# =====================================================
# MAP AND HEATMAP PAGE
# =====================================================

elif page == "View Map & Heatmap":

    st.title("🗺️ Wi-Fi Coverage Map & Heatmap")

    if df.empty:
        st.warning("No measurements available.")
        st.stop()

    ssid_list = [
        "All Networks"
    ] + sorted(df["ssid"].dropna().unique().tolist())

    selected_ssid = st.selectbox(
        "Select Network",
        ssid_list
    )

    if selected_ssid == "All Networks":
        plot_df = df.copy()
    else:
        plot_df = df[df["ssid"] == selected_ssid].copy()

    floorplans = [
        file for file in os.listdir("data/floorplans")
        if file.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not floorplans:
        st.error("No floor plan found.")
        st.stop()

    selected_plan = st.selectbox(
        "Select Floor Plan",
        floorplans
    )

    image = Image.open(
        os.path.join("data/floorplans", selected_plan)
    )

    img_w, img_h = image.size

    fig = go.Figure()

    # Floor-plan background
    fig.add_layout_image(
        dict(
            source=image,
            xref="x",
            yref="y",
            x=0,
            y=img_h,
            sizex=img_w,
            sizey=img_h,
            sizing="stretch",
            opacity=1,
            layer="below"
        )
    )

    # Measurement points
    fig.add_trace(
        go.Scatter(
            x=plot_df["x"],
            y=plot_df["y"],
            mode="markers",
            marker=dict(
                size=12,
                color=plot_df["signal_dbm"],
                colorscale="RdYlGn",
                cmin=-90,
                cmax=-40,
                colorbar=dict(title="Signal dBm")
            ),
            text=plot_df.apply(
                lambda row:
                f"{row['ssid']}<br>{row['signal_dbm']} dBm",
                axis=1
            ),
            hoverinfo="text",
            name="Measurements"
        )
    )

    # Heatmap generation
    if len(plot_df) >= 4:

        try:
            points = plot_df[["x", "y"]].values
            values = plot_df["signal_dbm"].values

            grid_x, grid_y = np.mgrid[
                0:img_w:80j,
                0:img_h:80j
            ]

            grid_z = griddata(
                points,
                values,
                (grid_x, grid_y),
                method="linear"
            )

            fig.add_trace(
                go.Heatmap(
                    x=grid_x[:, 0],
                    y=grid_y[0, :],
                    z=grid_z.T,
                    colorscale="RdYlGn",
                    zmin=-90,
                    zmax=-40,
                    opacity=0.5,
                    showscale=False,
                    name="Signal Heatmap"
                )
            )

        except Exception:
            st.warning(
                "The points are not sufficiently spread out "
                "to generate a smooth heatmap."
            )

    fig.update_xaxes(
        range=[0, img_w],
        showgrid=False
    )

    fig.update_yaxes(
        range=[0, img_h],
        scaleanchor="x",
        showgrid=False
    )

    fig.update_layout(
        height=650,
        title=f"Coverage Map — {selected_ssid}"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "Green = Strong signal | Yellow = Medium signal | "
        "Red = Weak signal"
    )


# =====================================================
# STATISTICS AND DEAD ZONES PAGE
# =====================================================

elif page == "Statistics & Dead Zones":

    st.title("📊 Statistics & Potential Dead Zones")

    if df.empty:
        st.warning("No data available.")
        st.stop()

    threshold = st.sidebar.slider(
        "Weak Signal Threshold (dBm)",
        -90,
        -50,
        -75
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Points", len(df))
    col2.metric("Average Signal", f"{df['signal_dbm'].mean():.1f} dBm")
    col3.metric("Strongest Signal", f"{df['signal_dbm'].max()} dBm")
    col4.metric("Weakest Signal", f"{df['signal_dbm'].min()} dBm")

    weak_points = df[
        df["signal_dbm"] <= threshold
    ]

    st.subheader(
        f"Potential Dead-Zone Candidates ≤ {threshold} dBm"
    )

    st.write(
        f"Found {len(weak_points)} weak points "
        f"out of {len(df)} measurements."
    )

    if not weak_points.empty:

        st.dataframe(
            weak_points[
                [
                    "ssid",
                    "signal_dbm",
                    "x",
                    "y",
                    "timestamp",
                    "notes"
                ]
            ].sort_values("signal_dbm"),
            use_container_width=True
        )

    else:
        st.success(
            "No potential dead-zone candidates found "
            "with the selected threshold."
        )

    st.subheader("Summary by Network")

    summary = df.groupby("ssid").agg(
        Count=("signal_dbm", "count"),
        Average=("signal_dbm", "mean"),
        Minimum=("signal_dbm", "min"),
        Maximum=("signal_dbm", "max")
    ).round(1)

    st.dataframe(
        summary,
        use_container_width=True
    )


# =====================================================
# FILTER BY NETWORK PAGE
# =====================================================

elif page == "Filter by Network":

    st.title("📈 Network-wise Signal History")

    if df.empty:
        st.warning("No data available.")
        st.stop()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    networks = sorted(
        df["ssid"].dropna().unique().tolist()
    )

    selected_network = st.selectbox(
        "Select Network",
        networks
    )

    filtered_df = df[
        df["ssid"] == selected_network
    ].sort_values("timestamp")

    st.subheader("Measurement History")

    st.dataframe(
        filtered_df[
            [
                "signal_dbm",
                "x",
                "y",
                "timestamp",
                "notes"
            ]
        ],
        use_container_width=True
    )

    if len(filtered_df) >= 2:

        st.subheader("Signal Trend Over Time")

        chart_data = filtered_df.set_index(
            "timestamp"
        )[["signal_dbm"]]

        st.line_chart(chart_data)

    else:

        st.info(
            "At least two measurements are required "
            "to display a signal trend."
        )