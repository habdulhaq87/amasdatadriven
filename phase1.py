import streamlit as st
import pandas as pd
import sqlite3
from streamlit_lottie import st_lottie
import json

# Import the two modules for tasks & summary
import phase1_tasks
import phase1_summary


def load_lottie_animation(filepath):
    """Load a Lottie animation from a JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def fetch_budget_table_names(conn):
    """Fetch all table names in the database that match the 'budget_{id}' pattern."""
    query = """
    SELECT name
    FROM sqlite_master
    WHERE type='table' AND name LIKE 'budget_%';
    """
    return [row[0] for row in conn.execute(query).fetchall()]


def fetch_budget_data(conn, table_name):
    """Fetch data from a specific budget table."""
    query = f"SELECT * FROM {table_name};"
    return pd.read_sql_query(query, conn)


def render_budget_tab():
    """Render the Budget tab, consolidating budget tables."""
    st.subheader("Phase 1 Budgets")

    conn = sqlite3.connect("subtasks.db")
    budget_tables = fetch_budget_table_names(conn)

    if not budget_tables:
        st.warning("No budget tables found in the database.")
        conn.close()
        return

    st.write("Below are the available budgets for Phase 1 tasks:")

    # Allow the user to select a specific budget table
    selected_table = st.selectbox("Select a budget table to view:", budget_tables)

    if selected_table:
        # Fetch and display the data from the selected budget table
        budget_data = fetch_budget_data(conn, selected_table)

        if budget_data.empty:
            st.warning(f"No data found in {selected_table}.")
        else:
            st.write(f"**Details for {selected_table}:**")
            st.dataframe(budget_data)

    # Close the connection
    conn.close()


def render_phase1():
    # Title and Introduction
    st.title("Phase 1: Early & Doable Improvements")
    st.write("""
    This section outlines how AMAS Hypermarket can **move from the current situation** 
    to the **Phase 1** improvements. Four tabs are available below:
    
    - **Plan**: Detailed comparison of current vs. Phase 1 improvements.
    - **Tasks**: Shows the relevant Phase 1 tasks, including Person in Charge, Deliverables, 
      timelines, budgets, and more.
    - **Summary**: A high-level summary of Phase 1 activities, including timelines and budget.
    - **Budget**: Consolidated view of Phase 1 budgets for all subtasks.
    """)

    # Create four tabs: Plan, Tasks, Summary, Budget
    tab_plan, tab_tasks, tab_summary, tab_budget = st.tabs(["Plan", "Tasks", "Summary", "Budget"])

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
        phase1_tasks.render_phase1_tasks_ui()

    # --- SUMMARY TAB ---
    with tab_summary:
        st.subheader("Phase 1 Summary")
        st.write("""
        Below is a **high-level summary** of Phase 1 activities, aggregated across 
        categories, tasks, timelines, and budgets.
        """)
        phase1_summary.render_phase1_summary()

    # --- BUDGET TAB ---
    with tab_budget:
        render_budget_tab()


if __name__ == "__main__":
    render_phase1()
