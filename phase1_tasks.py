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
    Streamlit UI for managing Phase 1 tasks.
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

    # Display tasks in a table format
    st.dataframe(tasks)

    # Select a task to update or delete
    task_ids = tasks["id"].tolist()
    selected_task_id = st.selectbox("Select Task ID to Manage", options=task_ids)

    if selected_task_id:
        # Get the selected task details
        selected_task = tasks[tasks["id"] == selected_task_id].iloc[0]

        with st.expander("Update Task Details"):
            # Editable fields
            updated_data = {}
            updated_data["category"] = st.text_input("Category", selected_task["category"])
            updated_data["aspect"] = st.text_input("Aspect", selected_task["aspect"])
            updated_data["current_situation"] = st.text_area("Current Situation", selected_task["current_situation"])
            updated_data["name"] = st.text_input("Name", selected_task["name"])
            updated_data["detail"] = st.text_area("Detail", selected_task["detail"])
            updated_data["start_time"] = st.text_input("Start Time", selected_task["start_time"])
            updated_data["outcome"] = st.text_area("Outcome", selected_task["outcome"])
            updated_data["person_involved"] = st.text_input("Person Involved", selected_task["person_involved"])
            updated_data["budget"] = st.number_input("Budget", value=selected_task["budget"], step=100.0)
            updated_data["deadline"] = st.text_input("Deadline", selected_task["deadline"])
            updated_data["progress"] = st.slider("Progress (%)", 0, 100, value=selected_task["progress"])

            # Update button
            if st.button("Update Task"):
                update_subtask_in_db(conn, selected_task_id, updated_data)
                st.success(f"Task ID {selected_task_id} updated successfully!")

        with st.expander("Delete Task"):
            # Delete button
            if st.button(f"Delete Task ID {selected_task_id}"):
                delete_subtask_from_db(conn, selected_task_id)
                st.success(f"Task ID {selected_task_id} deleted successfully!")

if __name__ == "__main__":
    render_phase1_tasks_ui()
