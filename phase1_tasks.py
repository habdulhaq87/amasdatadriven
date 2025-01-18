import streamlit as st
import pandas as pd
import sqlite3
from subtasks import (
    initialize_subtasks_database,
    fetch_subtasks_from_db
)

def render_phase1_tasks_ui():
    """
    Streamlit UI for Phase 1 tasks with an improved card-like interface.
    """
    # Optional: Set page config for a wider layout
    st.set_page_config(page_title="Client Dashboard: Phase 1", layout="wide")

    # Inject custom CSS for card styling
    st.markdown(
        """
        <style>
        /* Main background if you want a light grey overall page color
        body {
            background-color: #f5f5f5;
        }
        */

        /* Card container style */
        .task-card {
            background-color: #fff;
            border: 1px solid #ddd;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
        }

        /* Task title */
        .task-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #333;
        }

        /* Task info labels */
        .task-info {
            font-size: 0.95rem;
            margin-bottom: 0.3rem;
            line-height: 1.4;
            color: #555;
        }
        .task-info strong {
            color: #222;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Client Dashboard: Phase 1 Tasks")

    # Initialize/connect to the database
    conn = initialize_subtasks_database()

    # Fetch existing tasks from the database
    tasks = fetch_subtasks_from_db(conn)

    if tasks.empty:
        st.warning("No tasks available in the database.")
        return

    st.subheader("Task Overview")

    # Create a card for each task
    for _, task in tasks.iterrows():
        with st.container():
            st.markdown("<div class='task-card'>", unsafe_allow_html=True)

            # Display the task title
            st.markdown(
                f"<div class='task-title'>"
                f"Task ID {task['id']}: {task['name']}"
                f"</div>",
                unsafe_allow_html=True
            )

            # Split details into two columns
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(
                    f"<div class='task-info'><strong>Category:</strong> {task['category']}</div>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='task-info'><strong>Aspect:</strong> {task['aspect']}</div>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='task-info'><strong>Current Situation:</strong> {task['current_situation']}</div>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='task-info'><strong>Detail:</strong> {task['detail']}</div>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='task-info'><strong>Start Time:</strong> {task['start_time']}</div>", 
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"<div class='task-info'><strong>Outcome:</strong> {task['outcome']}</div>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='task-info'><strong>Person Involved:</strong> {task['person_involved']}</div>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='task-info'><strong>Budget:</strong> ${task['budget']}</div>", 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='task-info'><strong>Deadline:</strong> {task['deadline']}</div>", 
                    unsafe_allow_html=True
                )

                # Progress bar (ensure it's a float for st.progress)
                progress_value = float(task['progress']) if not pd.isnull(task['progress']) else 0
                st.progress(progress_value, text=f"Progress: {progress_value}%")

            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_phase1_tasks_ui()
