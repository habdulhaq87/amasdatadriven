import streamlit as st
import pandas as pd
import sqlite3
from subtasks import (
    initialize_subtasks_database,
    fetch_subtasks_from_db
)

def render_phase1_tasks_ui():
    """
    Streamlit UI for Phase 1 tasks with a cleaner, more structured presentation.
    """

    st.set_page_config(page_title="Client Dashboard", layout="wide")
    st.title("Client Dashboard: Phase 1 Tasks")

    # Add a subtle styling touch (can be removed or customized).
    st.markdown(
        """
        <style>
        /* Center the main title */
        .css-18e3th9 {
            text-align: center;
        }
        /* Increase the font size for subheaders */
        .css-1j0bp8a h2 {
            font-size: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Initialize or connect to the database
    conn = initialize_subtasks_database()

    # Fetch existing tasks from the database
    tasks = fetch_subtasks_from_db(conn)

    if tasks.empty:
        st.write("No tasks available in the database.")
        return

    st.subheader("Task Overview")
    st.write("Below are the tasks for Phase 1. Click on each task to expand its details.")

    # Display tasks in collapsible expanders
    for _, task in tasks.iterrows():
        with st.expander(f"Task ID {task['id']}: {task['name']}"):
            # Use columns to organize information side by side
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown(f"**Category:** {task['category']}")
                st.markdown(f"**Aspect:** {task['aspect']}")
                st.markdown(f"**Current Situation:** {task['current_situation']}")
                st.markdown(f"**Detail:** {task['detail']}")

            with col2:
                st.markdown(f"**Start Time:** {task['start_time']}")
                st.markdown(f"**Outcome:** {task['outcome']}")
                st.markdown(f"**Person Involved:** {task['person_involved']}")
                st.markdown(f"**Budget:** `${task['budget']}`")
                st.markdown(f"**Deadline:** {task['deadline']}")

            # Display progress bar at the bottom of the expander
            progress_percentage = task['progress'] if task['progress'] <= 100 else 100
            st.progress(progress_percentage, text=f"Progress: {progress_percentage}%")

if __name__ == "__main__":
    render_phase1_tasks_ui()
