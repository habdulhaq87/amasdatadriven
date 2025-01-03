import streamlit as st
import pandas as pd
import datetime

def render_phase1_summary():
    """
    Provides a high-level summary for Phase 1 data, including
    - Count of tasks
    - Aggregated budget
    - Earliest start date and latest end date
    - Summaries per category
    """

    st.title("Phase 1: Summary")

    st.write("""
    This tab provides **overall** Phase 1 information extracted from `amas_data.csv`, 
    including activity counts, timelines, and aggregated budgets.
    """)

    # Load CSV data
    try:
        df = pd.read_csv("amas_data.csv", sep=",")
    except FileNotFoundError:
        st.error("`amas_data.csv` not found. Please ensure it exists in the app directory.")
        return

    # Required Phase 1 columns
    required_cols = [
        "Category", "Aspect",
        "Phase1_Person in Charge",
        "Phase1_Deliverable",
        "Phase1_Start Date",
        "Phase1_End Date",
        "Phase1_Budget"
    ]
    # Optional: "Phase1_Charter" can be included if needed for advanced summaries

    # Check columns existence
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(f"Missing columns required for Phase 1 summary: {missing}")
        return

    # Make a copy of relevant columns
    phase1_df = df[required_cols].copy()

    # Convert dates and budgets to appropriate types
    phase1_df["Phase1_Start Date"] = pd.to_datetime(phase1_df["Phase1_Start Date"], errors="coerce")
    phase1_df["Phase1_End Date"] = pd.to_datetime(phase1_df["Phase1_End Date"], errors="coerce")
    phase1_df["Phase1_Budget"] = pd.to_numeric(phase1_df["Phase1_Budget"], errors="coerce").fillna(0.0)

    # ===== PER-CATEGORY SUMMARY =====
    st.subheader("Summary by Category")

    # Group by Category, calculating aggregates
    cat_group = phase1_df.groupby("Category").agg(
        tasks_count=("Aspect", "count"),
        earliest_start=("Phase1_Start Date", "min"),
        latest_end=("Phase1_End Date", "max"),
        total_budget=("Phase1_Budget", "sum"),
    ).reset_index()

    # Display a DataFrame with formatted columns
    # Convert earliest_start, latest_end to string for display if not null
    cat_group["earliest_start"] = cat_group["earliest_start"].dt.date.astype(str)
    cat_group["latest_end"] = cat_group["latest_end"].dt.date.astype(str)

    st.dataframe(cat_group.style.format({
        "total_budget": "{:,.2f}"
    }), use_container_width=True)

    # ===== OVERALL SUMMARY =====
    st.subheader("Overall Phase 1 Summary")

    # Calculate total tasks
    total_tasks = phase1_df["Aspect"].count()
    total_budget = phase1_df["Phase1_Budget"].sum()
    earliest_start = phase1_df["Phase1_Start Date"].min()
    latest_end = phase1_df["Phase1_End Date"].max()

    # Convert to date for display
    earliest_start_str = earliest_start.date().isoformat() if pd.notnull(earliest_start) else "N/A"
    latest_end_str = latest_end.date().isoformat() if pd.notnull(latest_end) else "N/A"

    # Display
    colA, colB = st.columns([1, 1])
    with colA:
        st.metric("Total Tasks", total_tasks)
        st.metric("Earliest Start Date", earliest_start_str)
    with colB:
        st.metric("Total Budget", f"${total_budget:,.2f}")
        st.metric("Latest End Date", latest_end_str)

    st.info("""
    **Notes**:
    - **Tasks Count** is the total number of Aspects under Phase 1.
    - **Earliest/Latest Dates** are derived from all tasks' start/end fields.
    - **Total Budget** is the sum of `Phase1_Budget` across all tasks.
    """)


if __name__ == "__main__":
    render_phase1_summary()
