import streamlit as st
import pandas as pd
import sqlite3
from subtasks import (
    initialize_subtasks_database,
    fetch_subtasks_from_db
)

def render_phase1_tasks_ui():
    """
    Streamlit UI for Phase 1 tasks with a collapsible and visually appealing interface.
    """
    st.title("Client Dashboard: Phase 1 Tasks")

    # Initialize or connect to the database
    conn = initialize_subtasks_database()

    # Fetch existing tasks from the database
    tasks = fetch_subtasks_from_db(conn)

    if tasks.empty:
        st.write("No tasks available in the database.")
        return

    st.subheader("Task Overview")

    # Display tasks in collapsible tabs
    for _, task in tasks.iterrows():
        with st.expander(f"Task ID {task['id']}: {task['name']}"):
            st.markdown(f"**Category:** {task['category']}")
            st.markdown(f"**Aspect:** {task['aspect']}")
            st.markdown(f"**Current Situation:** {task['current_situation']}")
            st.markdown(f"**Detail:** {task['detail']}")
            st.markdown(f"**Start Time:** {task['start_time']}")
            st.markdown(f"**Outcome:** {task['outcome']}")
            st.markdown(f"**Person Involved:** {task['person_involved']}")
            st.markdown(f"**Budget:** ${task['budget']}")
            st.markdown(f"**Deadline:** {task['deadline']}")
            st.progress(task['progress'], text=f"Progress: {task['progress']}%")

if __name__ == "__main__":
    render_phase1_tasks_ui()
