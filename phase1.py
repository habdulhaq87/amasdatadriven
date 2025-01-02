import streamlit as st
import pandas as pd

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

        # Optional: alternate layout for each category
        # Even category index => image on the left, odd => on the right
        if i % 2 == 0:
            col_img, col_text = st.columns([1, 3])
        else:
            col_text, col_img = st.columns([3, 1])

        with col_img:
            # Generate a placeholder image, or replace with a relevant image for the category
            st.image(
                f"https://via.placeholder.com/300x200?text={cat.replace(' ', '+')}",
                caption=f"Focusing on Phase 1 for {cat}",
                use_container_width=True
            )

        with col_text:
            # For each Aspect in the Category, show a comparison of CurrentSituation vs Phase1
            for _, row in cat_data.iterrows():
                aspect_title = row["Aspect"]
                current_situation = row["CurrentSituation"]
                phase1_improvement = row["Phase1"]

                # Create an expander for each Aspect
                with st.expander(f"**Aspect:** {aspect_title}"):
                    # Two columns: left = Current, right = Phase 1
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
