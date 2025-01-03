import streamlit as st
import pandas as pd

def render_phase1_tasks():
    """
    Displays the Phase 1 tasks for each category/aspect,
    including Person in Charge, Deliverable, Start/End Dates, Budget, and Charter.
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
        # Filter rows for this category
        cat_data = df[df["Category"] == cat]

        # If there are no tasks for this category in Phase 1 (check person in charge or deliverables?), 
        # we can still display it if desired, or skip if there's no relevant data.
        # We'll display any aspect that has a Phase1_Person in Charge (even if empty).
        st.markdown(f"## {cat} — Phase 1 Tasks")

        for _, row in cat_data.iterrows():
            aspect_title = row["Aspect"]

            # Build expander for each aspect's tasks
            with st.expander(f"**{aspect_title}**"):
                person_in_charge = row["Phase1_Person in Charge"]
                deliverable = row["Phase1_Deliverable"]
                start_date = row["Phase1_Start Date"]
                end_date = row["Phase1_End Date"]
                budget = row["Phase1_Budget"]
                charter = row["Phase1_Charter"]

                # Layout columns or just display each field with markdown
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Person in Charge**")
                    st.write(person_in_charge if pd.notnull(person_in_charge) else "N/A")

                    st.markdown("**Deliverable**")
                    st.write(deliverable if pd.notnull(deliverable) else "N/A")

                    st.markdown("**Start Date**")
                    st.write(start_date if pd.notnull(start_date) else "N/A")

                with col2:
                    st.markdown("**End Date**")
                    st.write(end_date if pd.notnull(end_date) else "N/A")

                    st.markdown("**Budget**")
                    st.write(budget if pd.notnull(budget) else "N/A")

                    st.markdown("**Charter**")
                    st.write(charter if pd.notnull(charter) else "N/A")

        st.write("---")

    st.info("""
    This view summarizes who is responsible for each Phase 1 task, 
    the key deliverables, timelines, and budgets. 
    Once tasks are updated in `amas_data.csv`, they will automatically appear here.
    """)

if __name__ == "__main__":
    render_phase1_tasks()
