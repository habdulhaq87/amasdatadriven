import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie
import json

# Import the phase1_tasks module
import phase1_tasks

def load_lottie_animation(filepath):
    """Load a Lottie animation from a JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)

def render_phase1():
    # Title and Introduction
    st.title("Phase 1: Early & Doable Improvements")
    st.write("""
    This section outlines how AMAS Hypermarket can **move from the current situation** 
    to the **Phase 1** improvements. Two tabs are available below:
    - **Plan**: Detailed comparison of current vs. Phase 1 improvements.
    - **Tasks**: Shows the relevant Phase 1 tasks, including Person in Charge, Deliverables, 
      timelines, budgets, and more.
    """)

    # Create two tabs: Plan and Tasks
    tab_plan, tab_tasks = st.tabs(["Plan", "Tasks"])

    # --- PLAN TAB ---
    with tab_plan:
        st.subheader("Plan Overview")
        st.write("""
        Below is a **category-by-category** comparison of the **current situation** 
        versus the **Phase 1** improvements. Each category includes relevant Lottie animations 
        or placeholders, along with expanders for specific aspects.
        """)

        # Load Data
        df = pd.read_csv("amas_data.csv", sep=",")  # Adjust if file path differs

        # Load Lottie animations
        arrive_animation   = load_lottie_animation("input/arrive.json")
        inventory_animation = load_lottie_animation("input/inventory.json")
        store_animation    = load_lottie_animation("input/store.json")
        order_animation    = load_lottie_animation("input/order.json")
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
                # Decide the Lottie animation vs. placeholder
                if cat == "Receiving & QC":
                    st_lottie(arrive_animation,    key="receiving_qc",     height=200, width=180)
                elif cat == "Inventory Management":
                    st_lottie(inventory_animation, key="inventory_manage", height=200, width=180)
                elif cat == "Store-Level Operations":
                    st_lottie(store_animation,     key="store_operations", height=200, width=180)
                elif cat == "Selling the Items":
                    st_lottie(order_animation,     key="selling_items",    height=200, width=180)
                elif cat == "Post-Sale & Procurement":
                    st_lottie(postsell_animation,  key="post_sale",        height=200, width=180)
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
                    aspect_title       = row["Aspect"]
                    current_situation  = row["CurrentSituation"].replace("\\n", "\n")
                    phase1_improvement = row["Phase1"].replace("\\n", "\n")

                    with st.expander(f"**{aspect_title}**"):
                        ccol, pcol = st.columns(2)
                        with ccol:
                            st.markdown("**Current Situation**")
                            st.markdown(current_situation)
                        with pcol:
                            st.markdown("**Phase 1 Improvement**")
                            st.markdown(phase1_improvement)

            # Add a separator after each category
            st.write("---")

        st.success("""
        By implementing these **Phase 1** steps, AMAS Hypermarket lays the groundwork 
        for more advanced **digitization** and **automation** in Phases 2 and 3, 
        significantly improving daily operations, reducing errors, 
        and preparing for scalable, data-driven growth.
        """)

    # --- TASKS TAB ---
    with tab_tasks:
        st.subheader("Phase 1 Tasks")
        st.write("""
        Below are the **Phase 1 tasks** from `amas_data.csv`, detailing who is responsible, 
        deliverables, start/end dates, budget, and more.
        """)

        # Call the function from phase1_tasks module
        phase1_tasks.render_phase1_tasks()

if __name__ == "__main__":
    render_phase1()
