import streamlit as st
import pandas as pd
from PIL import Image, ExifTags

# Mapping categories to images
CATEGORY_IMAGES = {
    "Receiving & QC": "input/receiving.jpg",
    "Inventory Management": "input/inventory.jpg",
    "Selling the Items": "input/cashier.JPG",
    "Post-Sale & Procurement": "input/post.JPG",
    "Store-Level Operations": "input/store.JPG"  # Added Store-Level Operations image
}

def correct_image_orientation(image_path):
    """
    Correct the orientation of an image using EXIF metadata.
    Returns the corrected image.
    """
    try:
        image = Image.open(image_path)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = image._getexif()
        if exif is not None:
            orientation = exif.get(orientation, None)
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
        return image
    except (AttributeError, KeyError, IndexError):
        # If no EXIF data is found or an error occurs, return the image as is
        return Image.open(image_path)

def render_current_stage():
    # Title and Introduction
    st.title("Current Stage: AMAS Hypermarket")
    st.write("""
    This section provides a **high-level overview** of AMAS Hypermarket’s **current situation**, 
    categorized into functional areas (e.g., Receiving & QC, Inventory Management, etc.). 
    Each category is accompanied by a relevant image and a list of **key aspects** 
    that describe existing challenges or operational workflows.
    """)

    # Load Data
    df = pd.read_csv("amas_data.csv", sep=",")  # Adjust the path if needed
    categories = df["Category"].unique()

    # For styling consistency, alternate the layout for each category:
    # Even-index categories: Image on left, text on right.
    # Odd-index categories: Text on left, image on right.
    for i, cat in enumerate(categories):
        cat_data = df[df["Category"] == cat]

        # Sub-header for the category
        st.markdown(f"### {cat}")

        # Determine layout: image left/right alternation
        if i % 2 == 0:
            col1, col2 = st.columns([1, 3])  # Image on the left
        else:
            col2, col1 = st.columns([3, 1])  # Image on the right

        # Display image and caption
        with col1:
            image_path = CATEGORY_IMAGES.get(cat, None)
            if image_path:
                corrected_image = correct_image_orientation(image_path)
                st.image(
                    corrected_image,
                    caption=f"Current Stage: {cat}",
                    use_container_width=True
                )
            else:
                st.warning(f"No image found for category: {cat}")

        # Display the aspects and challenges as bullet points
        with col2:
            bullet_points = []
            for _, row in cat_data.iterrows():
                aspect = row["Aspect"]
                situation = row["CurrentSituation"]
                bullet_points.append(f"- **{aspect}:** {situation}")

            st.markdown("\n".join(bullet_points))

    # Add a separator and summary info
    st.write("---")
    st.info("""
    This overview captures the **status quo** at AMAS Hypermarket. 
    For more details on the future roadmap and how we plan to transition 
    to a data-driven operation, explore the other sections from the sidebar.
    """)

if __name__ == "__main__":
    render_current_stage()
