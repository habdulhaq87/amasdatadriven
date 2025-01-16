import sqlite3
import pandas as pd
import streamlit as st
import datetime

def initialize_subtasks_database():
    """Initialize the SQLite database for subtasks."""
    conn = sqlite3.connect("subtasks.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            aspect TEXT,
            current_situation TEXT,
            name TEXT,
            detail TEXT,
            start_time TEXT,
            outcome TEXT,
            person_involved TEXT,
            budget REAL,
            deadline TEXT,
            progress INTEGER
        )
        """
    )
    conn.commit()
    return conn

def fetch_subtasks_for_page(conn, aspect):
    """Fetch subtasks related to a specific page (aspect)."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks WHERE aspect = ?", (aspect,))
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)

def save_subtasks_to_db(conn, subtasks):
    """Save a list of subtasks to the database."""
    cursor = conn.cursor()
    for subtask in subtasks:
        cursor.execute(
            """
            INSERT INTO subtasks (
                category, aspect, current_situation, name, detail,
                start_time, outcome, person_involved, budget, deadline, progress
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                subtask.get("Category", ""),
                subtask.get("Aspect", ""),
                subtask.get("CurrentSituation", ""),
                subtask.get("Name", ""),
                subtask.get("Detail", ""),
                subtask.get("StartTime").isoformat() if subtask.get("StartTime") else None,
                subtask.get("Outcome", ""),
                subtask.get("PersonInvolved", ""),
                subtask.get("Budget", 0.0),
                subtask.get("Deadline").isoformat() if subtask.get("Deadline") else None,
                subtask.get("Progress", 0),
            ),
        )
    conn.commit()

def update_subtask_in_db(conn, subtask):
    """Update an existing subtask in the database."""
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE subtasks
        SET category = ?,
            aspect = ?,
            current_situation = ?,
            name = ?,
            detail = ?,
            start_time = ?,
            outcome = ?,
            person_involved = ?,
            budget = ?,
            deadline = ?,
            progress = ?
        WHERE id = ?
        """,
        (
            subtask.get("Category", ""),
            subtask.get("Aspect", ""),
            subtask.get("CurrentSituation", ""),
            subtask.get("Name", ""),
            subtask.get("Detail", ""),
            subtask.get("StartTime").isoformat() if subtask.get("StartTime") else None,
            subtask.get("Outcome", ""),
            subtask.get("PersonInvolved", ""),
            subtask.get("Budget", 0.0),
            subtask.get("Deadline").isoformat() if subtask.get("Deadline") else None,
            subtask.get("Progress", 0),
            subtask.get("id"),
        ),
    )
    conn.commit()

def delete_subtask_from_db(conn, subtask_id):
    """Delete a subtask from the database by its ID."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()

def render_saved_subtasks(conn, aspect):
    """Render the saved subtasks for the current page in an interactive Streamlit UI."""
    st.subheader(f"View and Modify Subtasks for {aspect}")
    saved_subtasks = fetch_subtasks_for_page(conn, aspect)
    if not saved_subtasks.empty:
        for _, subtask in saved_subtasks.iterrows():
            with st.expander(f"Subtask ID: {subtask['id']}"):
                editable_subtask = {
                    "id": subtask["id"],
                    "Category": st.text_input("Category", subtask["category"], key=f"category_{subtask['id']}"),
                    "Aspect": subtask["aspect"],
                    "CurrentSituation": st.text_area("Current Situation", subtask["current_situation"], key=f"current_situation_{subtask['id']}"),
                    "Name": st.text_input("Name", subtask["name"], key=f"name_{subtask['id']}"),
                    "Detail": st.text_area("Detail", subtask["detail"], key=f"detail_{subtask['id']}"),
                    "StartTime": st.date_input("Start Time", pd.to_datetime(subtask["start_time"]) if subtask["start_time"] else datetime.date.today(), key=f"start_time_{subtask['id']}"),
                    "Outcome": st.text_area("Outcome", subtask["outcome"], key=f"outcome_{subtask['id']}"),
                    "PersonInvolved": st.text_input("Person Involved", subtask["person_involved"], key=f"person_involved_{subtask['id']}"),
                    "Budget": st.number_input("Budget", subtask["budget"], step=100.0, key=f"budget_{subtask['id']}"),
                    "Deadline": st.date_input("Deadline", pd.to_datetime(subtask["deadline"]) if subtask["deadline"] else datetime.date.today(), key=f"deadline_{subtask['id']}"),
                    "Progress": st.slider("Progress (%)", 0, 100, subtask["progress"], key=f"progress_{subtask['id']}")
                }

                if st.button(f"Save Changes for Subtask {subtask['id']}", key=f"save_{subtask['id']}"):
                    update_subtask_in_db(conn, editable_subtask)
                    st.success(f"Subtask {subtask['id']} updated successfully!")

                if st.button(f"Delete Subtask {subtask['id']}", key=f"delete_{subtask['id']}"):
                    delete_subtask_from_db(conn, subtask["id"])
                    st.success(f"Subtask {subtask['id']} deleted successfully!")
                    st.experimental_set_query_params(refresh=True)
    else:
        st.write(f"No subtasks found for {aspect}.")
