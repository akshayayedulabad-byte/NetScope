import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from PIL import Image
import os
import sys
from scipy.interpolate import griddata

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.database.db_manager import get_all_measurements

st.set_page_config(page_title="NetScope Map & Heatmap", layout="wide")
st.title("NetScope – Floor Map & Signal Heatmap")

data = get_all_measurements()
df = pd.DataFrame(data) if data else pd.DataFrame()

if df.empty:
    st.warning("No measurements found. Please collect some data first.")
    st.stop()

# Select network
ssid_list = ["All Networks"] + sorted(df["ssid"].dropna().unique().tolist())
selected_ssid = st.selectbox("Filter by Network (SSID)", ssid_list)

if selected_ssid != "All Networks":
    df = df[df["ssid"] == selected_ssid]

# Floor plan selection
floorplan_folder = "data/floorplans"
floorplans = [f for f in os.listdir(floorplan_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

if not floorplans:
    st.error("No floor plan images found in data/floorplans/")
    st.stop()

selected_plan = st.selectbox("Select Floor Plan", floorplans)
image_path = os.path.join(floorplan_folder, selected_plan)
image = Image.open(image_path)
img_width, img_height = image.size

# Create figure
fig = go.Figure()

# Background image
fig.add_layout_image(
    dict(
        source=image,
        xref="x", yref="y",
        x=0, y=img_height,
        sizex=img_width, sizey=img_height,
        sizing="stretch", opacity=1, layer="below"
    )
)

# Measurement points
fig.add_trace(go.Scatter(
    x=df["x"], y=df["y"],
    mode="markers",
    marker=dict(
        size=12,
        color=df["signal_dbm"],
        colorscale="RdYlGn",
        cmin=-90, cmax=-40,
        colorbar=dict(title="Signal (dBm)"),
        line=dict(width=1, color="black")
    ),
    text=df.apply(lambda r: f"SSID: {r['ssid']}<br>Signal: {r['signal_dbm']} dBm<br>Time: {r['timestamp']}", axis=1),
    hoverinfo="text",
    name="Measurements"
))

# Heatmap (only if enough points)
if len(df) >= 4:
    st.subheader("Signal Strength Heatmap")
    grid_x, grid_y = np.mgrid[0:img_width:100j, 0:img_height:100j]
    points = df[["x", "y"]].values
    values = df["signal_dbm"].values

    try:
        grid_z = griddata(points, values, (grid_x, grid_y), method="cubic", fill_value=np.nan)
        fig.add_trace(go.Heatmap(
            x=grid_x[:, 0], y=grid_y[0, :], z=grid_z.T,
            colorscale="RdYlGn",
            zmin=-90, zmax=-40,
            opacity=0.55,
            colorbar=dict(title="Signal (dBm)"),
            name="Heatmap"
        ))
    except Exception as e:
        st.warning("Could not generate smooth heatmap (need more well-spread points). Showing points only.")

fig.update_xaxes(range=[0, img_width], showgrid=False)
fig.update_yaxes(range=[0, img_height], scaleanchor="x", showgrid=False)
fig.update_layout(
    width=1000, height=650,
    title=f"Wi-Fi Coverage Map – {selected_ssid}",
    margin=dict(l=10, r=10, t=40, b=10)
)

st.plotly_chart(fig, use_container_width=True)

st.info("Green = Strong signal | Yellow = Medium | Red = Weak signal (potential dead-zone candidate)")