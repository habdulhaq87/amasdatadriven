import streamlit as st
import pandas as pd

def render_current_stage():
    # Title and Introduction
    st.title("Current Stage: AMAS Hypermarket")
    st.write("""
    This section provides a **high-level overview** of AMAS Hypermarket’s **current situation**, 
    categorized into functional areas (e.g., Receiving & QC, Inventory Management, etc.). 
    Each category is accompanied by an image and a list of **key aspects** 
    that describe existing challenges or operational workflows.
    """)

    # Load Data
    df = pd.read_csv("amas_data.csv", sep=",")  # Adjust the path if needed
    categories = df["Category"].unique()

    # Define specific images for categories
    category_images = {
        "Receiving & QC": "input/receiving.jpg",
        "Inventory Management": "input/inventory.jpg",
        "Selling the Items": "input/(14).JPG",
        "Post-Sale & Procurement": "input/(12).JPG",
    }

    # For styling consistency, alternate the layout for each category:
    # Even-index categories: Image on left, text on right.
    # Odd-index categories: Text on left, image on right.
    for i, cat in enumerate(categories):
        cat_data = df[df["Category"] == cat]

        st.markdown(f"### {cat}")  # Display the category name as a sub-header

        if i % 2 == 0:
            # Image on the LEFT, text on the RIGHT
            col1, col2 = st.columns([1, 3])
        else:
            # Image on the RIGHT, text on the LEFT
            col2, col1 = st.columns([3, 1])

        with col1:
            # Use the specified image for the category
            image_path = category_images.get(cat, None)  # Default to None if category not in dictionary
            if image_path:
                st.image(
                    image_path,
                    caption=f"Current Stage: {cat}",
                    use_container_width=True
                )
            else:
                st.warning(f"No image found for {cat}. Using placeholder.")
                st.image(
                    f"https://via.placeholder.com/300x200?text={cat.replace(' ', '+')}",
                    caption=f"Current Stage: {cat}",
                    use_container_width=True
                )

        with col2:
            # Build a bullet-list for all aspects under this category
            bullet_points = []
            for _, row in cat_data.iterrows():
                aspect = row["Aspect"]
                situation = row["CurrentSituation"]
                bullet_points.append(f"- **{aspect}:** {situation}")

            # Join all bullet points together
            st.markdown("\n".join(bullet_points))

    st.write("---")
    st.info("This overview captures the **status quo** at AMAS Hypermarket. For more details on the future roadmap and how we plan to transition to a data-driven operation, explore the other sections from the sidebar.")


if __name__ == "__main__":
    render_current_stage()
