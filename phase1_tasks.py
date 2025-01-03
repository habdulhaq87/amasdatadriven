import streamlit as st
import pandas as pd

def render_phase1_tasks():
    """
    Displays the Phase 1 tasks for each category/aspect,
    including Person in Charge, Deliverable, Start/End Dates, Budget, and Charter,
    with an enhanced UI.
    """

    st.title("Phase 1: Tasks")

    st.write("""
    Below you will find the **Phase 1 tasks** extracted from `amas_data.csv`, 
    including details such as Person in Charge, Deliverables, Start/End Dates, Budget, and more.
    """)

    # Load Data
    df = pd.read_csv("amas_data.csv", sep=",")

    # Check if columns for Phase 1 tasks exist to avoid KeyErrors
    required_columns = [
        "Category", "Aspect", 
        "Phase1_Person in Charge", 
        "Phase1_Deliverable", 
        "Phase1_Start Date", 
        "Phase1_End Date", 
        "Phase1_Budget",
        "Phase1_Charter"
    ]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns for Phase 1 tasks: {missing_cols}")
        return

    # Group tasks by category for an organized display
    categories = df["Category"].unique()

    for cat in categories:
        cat_data = df[df["Category"] == cat]

        # Section header for each Category
        st.markdown(f"## {cat} — Phase 1 Tasks")

        # Iterate over each row (Aspect) within this Category
        for _, row in cat_data.iterrows():
            aspect_title = row["Aspect"]
            # Retrieve Phase 1 columns
            person_in_charge = row["Phase1_Person in Charge"]
            deliverable = row["Phase1_Deliverable"]
            start_date = row["Phase1_Start Date"]
            end_date = row["Phase1_End Date"]
            budget = row["Phase1_Budget"]
            charter = row["Phase1_Charter"]

            # We only show the expander if there's an Aspect name
            with st.expander(f"**{aspect_title}**", expanded=False):
                # We'll create a two-column layout for clarity
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown(f"**:bust_in_silhouette: Person in Charge**")
                    st.markdown(person_in_charge if pd.notnull(person_in_charge) else "N/A")

                    st.markdown(f"**:dart: Deliverable**")
                    st.markdown(deliverable if pd.notnull(deliverable) else "N/A")

                    st.markdown(f"**:date: Start Date**")
                    st.markdown(start_date if pd.notnull(start_date) else "N/A")

                with col2:
                    st.markdown(f"**:hourglass_flowing_sand: End Date**")
                    st.markdown(end_date if pd.notnull(end_date) else "N/A")

                    st.markdown(f"**:moneybag: Budget**")
                    st.markdown(budget if pd.notnull(budget) else "N/A")

                    st.markdown(f"**:scroll: Charter**")
                    st.markdown(charter if pd.notnull(charter) else "N/A")

        st.write("---")

    st.info("""
    This view summarizes who is responsible for each Phase 1 task, 
    the key deliverables, timelines, and budgets. 
    Once tasks are updated in `amas_data.csv`, they will automatically appear here.
    """)

if __name__ == "__main__":
    render_phase1_tasks()
