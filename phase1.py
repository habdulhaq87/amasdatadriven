import streamlit as st
import pandas as pd

# Mapping categories to specific images or animations
CATEGORY_IMAGES = {
    "Receiving & QC": "input/delivery.gif",  # Updated to animation
    "Inventory Management": "https://via.placeholder.com/300x200?text=Inventory",
    "Selling the Items": "https://via.placeholder.com/300x200?text=Selling",
    "Post-Sale & Procurement": "https://via.placeholder.com/300x200?text=Post-Sale"
}

def render_phase1():
    # Title and Introduction
    st.title("Phase 1: Early & Doable Improvements")
    st.write("""
    This section outlines how AMAS Hypermarket can **move from the current situation** 
    to the **Phase 1** improvements. Each Category is expanded below, with a comparison 
    between **Current Situation** and **Phase 1** steps, illustrating how basic digitization 
    and streamlined workflows will be introduced.
    """)

    # Load Data
    df = pd.read_csv("amas_data.csv", sep=",")  # Adjust if file path differs

    # Identify unique categories
    categories = df["Category"].unique()

    for i, cat in enumerate(categories):
        cat_data = df[df["Category"] == cat]

        # Display the Category Title
        st.markdown(f"## {cat} — Phase 1 Improvements")

        # Alternate layout for each category
        if i % 2 == 0:
            col_img, col_text = st.columns([1, 3])
        else:
            col_text, col_img = st.columns([3, 1])

        with col_img:
            # Use CATEGORY_IMAGES dictionary to dynamically load images or animations
            image_path = CATEGORY_IMAGES.get(cat, None)
            if image_path:
                st.image(
                    image_path,
                    caption=f"Focusing on Phase 1 for {cat}",
                    use_container_width=True
                )
            else:
                st.warning(f"No image or animation found for {cat}")

        with col_text:
            # For each Aspect in the Category, show a comparison of CurrentSituation vs Phase1
            for _, row in cat_data.iterrows():
                aspect_title = row["Aspect"]
                current_situation = row["CurrentSituation"]
                phase1_improvement = row["Phase1"]

                # Create an expander for each aspect
                with st.expander(f"**{aspect_title}**"):
                    ccol, pcol = st.columns(2)
                    with ccol:
                        st.markdown("**Current Situation**")
                        st.write(current_situation)
                    with pcol:
                        st.markdown("**Phase 1 Improvement**")
                        st.write(phase1_improvement)

        # Add a separator after each category
        st.write("---")

    st.success("""
    By implementing these **Phase 1** steps, AMAS Hypermarket lays the groundwork 
    for more advanced **digitization** and **automation** in Phases 2 and 3, 
    significantly improving daily operations, reducing errors, 
    and preparing for scalable, data-driven growth.
    """)

if __name__ == "__main__":
    render_phase1()
