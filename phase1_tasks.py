import streamlit as st
import pandas as pd
import sqlite3
from subtasks import (
    initialize_subtasks_database,
    fetch_subtasks_from_db,
    update_subtask_in_db,
    delete_subtask_from_db
)

def render_phase1_tasks_ui():
    """
    Streamlit UI for managing Phase 1 tasks with collapsible tabs for each task.
    """
    st.title("Phase 1 Tasks Management")

    # Initialize or connect to the database
    conn = initialize_subtasks_database()

    # Fetch existing tasks from the database
    tasks = fetch_subtasks_from_db(conn)

    if tasks.empty:
        st.write("No tasks available in the database.")
        return

    st.subheader("Current Tasks")

    # Display tasks in collapsible tabs
    for _, task in tasks.iterrows():
        with st.expander(f"Task ID {task['id']}: {task['name']}"):
            st.write(f"**Category:** {task['category']}")
            st.write(f"**Aspect:** {task['aspect']}")
            st.write(f"**Current Situation:** {task['current_situation']}")
            st.write(f"**Detail:** {task['detail']}")
            st.write(f"**Start Time:** {task['start_time']}")
            st.write(f"**Outcome:** {task['outcome']}")
            st.write(f"**Person Involved:** {task['person_involved']}")
            st.write(f"**Budget:** {task['budget']}")
            st.write(f"**Deadline:** {task['deadline']}")
            st.write(f"**Progress:** {task['progress']}%")

            # Editable fields
            updated_data = {}
            updated_data["category"] = st.text_input("Category", task["category"], key=f"category_{task['id']}")
            updated_data["aspect"] = st.text_input("Aspect", task["aspect"], key=f"aspect_{task['id']}")
            updated_data["current_situation"] = st.text_area("Current Situation", task["current_situation"], key=f"current_situation_{task['id']}")
            updated_data["name"] = st.text_input("Name", task["name"], key=f"name_{task['id']}")
            updated_data["detail"] = st.text_area("Detail", task["detail"], key=f"detail_{task['id']}")
            updated_data["start_time"] = st.text_input("Start Time", task["start_time"], key=f"start_time_{task['id']}")
            updated_data["outcome"] = st.text_area("Outcome", task["outcome"], key=f"outcome_{task['id']}")
            updated_data["person_involved"] = st.text_input("Person Involved", task["person_involved"], key=f"person_involved_{task['id']}")
            updated_data["budget"] = st.number_input("Budget", value=task["budget"], step=100.0, key=f"budget_{task['id']}")
            updated_data["deadline"] = st.text_input("Deadline", task["deadline"], key=f"deadline_{task['id']}")
            updated_data["progress"] = st.slider("Progress (%)", 0, 100, value=task["progress"], key=f"progress_{task['id']}")

            # Update button
            if st.button(f"Update Task {task['id']}"):
                update_subtask_in_db(conn, task['id'], updated_data)
                st.success(f"Task ID {task['id']} updated successfully!")

            # Delete button
            if st.button(f"Delete Task {task['id']}"):
                delete_subtask_from_db(conn, task['id'])
                st.success(f"Task ID {task['id']} deleted successfully!")

if __name__ == "__main__":
    render_phase1_tasks_ui()
