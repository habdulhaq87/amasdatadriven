import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie
import json

def load_lottie_animation(filepath):
    """Load a Lottie animation from a JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)

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

    # Load Lottie animations
    arrive_animation = load_lottie_animation("input/arrive.json")
    inventory_animation = load_lottie_animation("input/inventory.json")
    store_animation = load_lottie_animation("input/store.json")
    order_animation = load_lottie_animation("input/order.json")
    postsell_animation = load_lottie_animation("input/postsell.json")

    # Identify unique categories
    categories = df["Category"].unique()

    for i, cat in enumerate(categories):
        cat_data = df[df["Category"] == cat]

        # Display the Category Title
        st.markdown(f"## {cat} — Phase 1 Improvements")

        # Alternate layout for images and animations
        if i % 2 == 0:
            col_img, col_text = st.columns([1, 3])
        else:
            col_text, col_img = st.columns([3, 1])

        with col_img:
            # Use Lottie animations for specific categories
            if cat == "Receiving & QC":
                st_lottie(arrive_animation, key="receiving_qc", height=200, width=180)
            elif cat == "Inventory Management":
                st_lottie(inventory_animation, key="inventory_management", height=200, width=180)
            elif cat == "Store-Level Operations":
                st_lottie(store_animation, key="store_operations", height=200, width=180)
            elif cat == "Selling the Items":
                st_lottie(order_animation, key="selling_items", height=200, width=180)
            elif cat == "Post-Sale & Procurement":
                st_lottie(postsell_animation, key="post_sale", height=200, width=180)
            else:
                # Placeholder for other categories
                st.image(
                    f"https://via.placeholder.com/300x200?text={cat.replace(' ', '+')}",
                    caption=f"Focusing on Phase 1 for {cat}",
                    use_container_width=True
                )

        with col_text:
            # For each Aspect in the Category, compare CurrentSituation vs. Phase1
            for _, row in cat_data.iterrows():
                aspect_title = row["Aspect"]
                current_situation = row["CurrentSituation"]
                phase1_improvement = row["Phase1"]

                # Create an expander using only the aspect's name
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
