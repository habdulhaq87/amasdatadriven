import streamlit as st
import pandas as pd
import plotly.express as px
from subtasks import (
    initialize_subtasks_database,
    fetch_subtasks_from_db
)

def render_phase1_summary():
    """
    Streamlit UI for Phase 1 Summary with a Gantt chart-style visualization.
    """
    st.title("Client Dashboard: Phase 1 Summary")
    st.subheader("Time Schedule and Task Overview")

    # Initialize or connect to the database
    conn = initialize_subtasks_database()

    # Fetch existing tasks from the database
    tasks = fetch_subtasks_from_db(conn)

    if tasks.empty:
        st.write("No tasks available in the database.")
        return

    # Prepare data for visualization
    tasks['start_time'] = pd.to_datetime(tasks['start_time'])
    tasks['deadline'] = pd.to_datetime(tasks['deadline'])

    # Gantt chart visualization
    fig = px.timeline(
        tasks,
        x_start="start_time",
        x_end="deadline",
        y="aspect",
        color="progress",
        hover_data=["person_involved", "name", "budget"],
        title="Task Schedule and Progress",
    )
    fig.update_layout(
        yaxis_title="Aspect",
        xaxis_title="Timeline",
        coloraxis_colorbar=dict(
            title="Progress (%)",
        ),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Task Table
    st.subheader("Detailed Task Information")
    st.dataframe(
        tasks[["aspect", "start_time", "deadline", "person_involved", "progress"]],
        use_container_width=True,
    )

if __name__ == "__main__":
    render_phase1_summary()
