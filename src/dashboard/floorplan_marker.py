import streamlit as st
from PIL import Image
import os
from streamlit_image_coordinates import streamlit_image_coordinates

# Page settings
st.set_page_config(
    page_title="NetScope - Floor Plan Marker",
    layout="wide"
)

st.title("NetScope – Floor Plan Location Marker")
st.write("Upload a floor-plan image and click on it to mark your location.")

# Create folder
os.makedirs("data/floorplans", exist_ok=True)

# Upload image
uploaded_file = st.file_uploader(
    "Upload Floor Plan Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:

    # Save the image
    image_path = os.path.join(
        "data/floorplans",
        uploaded_file.name
    )

    with open(image_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    # Open image
    image = Image.open(image_path).convert("RGB")

    img_width, img_height = image.size

    st.success(
        f"Floor plan loaded: {uploaded_file.name} "
        f"({img_width} × {img_height} pixels)"
    )

    st.write("Click anywhere on the floor plan:")

    # Display image and capture click coordinates
    coordinates = streamlit_image_coordinates(
        image,
        key="floorplan_image"
    )

    # Display coordinates
    if coordinates is not None:

        x = coordinates["x"]
        y = coordinates["y"]

        st.success("Location marked successfully!")

        st.markdown("### Clicked Coordinates")
        st.write(f"**X = {x}**")
        st.write(f"**Y = {y}**")

        # Store coordinates for future stages
        st.session_state["last_x"] = x
        st.session_state["last_y"] = y
        st.session_state["floorplan_path"] = image_path

        st.info(
            "These coordinates can be used during Wi-Fi data collection."
        )

else:
    st.info("Please upload a floor-plan image to begin.")