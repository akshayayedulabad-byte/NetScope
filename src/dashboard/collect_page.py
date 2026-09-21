import streamlit as st
from PIL import Image
import os
import sys

from streamlit_image_coordinates import streamlit_image_coordinates

# Add project root to Python path
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
    page_title="NetScope - Collect Data",
    layout="wide"
)

st.title("NetScope – Real-Time Wi-Fi Data Collection")

# Create database tables
create_tables()

# Create floor-plan folder
os.makedirs("data/floorplans", exist_ok=True)

# Session state
if "last_x" not in st.session_state:
    st.session_state["last_x"] = None

if "last_y" not in st.session_state:
    st.session_state["last_y"] = None

if "floorplan_path" not in st.session_state:
    st.session_state["floorplan_path"] = None


# 1. Upload floor plan
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


# 2. Click on floor plan
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
        key="collection_floorplan"
    )

    if coordinates is not None:
        st.session_state["last_x"] = coordinates["x"]
        st.session_state["last_y"] = coordinates["y"]

    if st.session_state["last_x"] is not None:
        st.success(
            f"Location selected: X = {st.session_state['last_x']}, "
            f"Y = {st.session_state['last_y']}"
        )
    else:
        st.warning("Please click on the floor plan first.")


    # 3. Scan and save
    st.header("3. Scan Wi-Fi and Save")

    notes = st.text_input(
        "Optional notes",
        placeholder="Example: Classroom, corridor, laboratory"
    )

    if st.button(
        "Scan Wi-Fi & Save Measurement",
        type="primary"
    ):

        if (
            st.session_state["last_x"] is None
            or st.session_state["last_y"] is None
        ):
            st.error("Please select a location first!")

        else:
            with st.spinner("Scanning nearby Wi-Fi networks..."):
                networks = scan_wifi_networks()

            if not networks:
                st.error(
                    "No Wi-Fi networks found. Please turn on Wi-Fi."
                )

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
                    f"Successfully saved {saved_count} Wi-Fi measurements "
                    f"at X = {st.session_state['last_x']}, "
                    f"Y = {st.session_state['last_y']}"
                )

                st.balloons()

                st.subheader("Networks Saved")

                for network in networks:
                    st.write(
                        f"**{network.get('ssid', 'Unknown')}** → "
                        f"{network.get('signal')} dBm"
                    )

# Total records
st.divider()

total_measurements = len(get_all_measurements())

st.metric(
    "Total measurements in database",
    total_measurements
)