import sqlite3
import pandas as pd
import streamlit as st

def initialize_subtasks_database():
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

def fetch_subtasks_from_db(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)

def save_subtasks_to_db(conn, subtasks):
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

def delete_subtask_from_db(conn, subtask_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()

def render_saved_subtasks(conn):
    st.subheader("View Saved Subtasks")
    saved_subtasks = fetch_subtasks_from_db(conn)
    if not saved_subtasks.empty:
        for _, subtask in saved_subtasks.iterrows():
            with st.expander(f"Subtask ID: {subtask['id']}"):
                st.write(f"**Category:** {subtask['category']}")
                st.write(f"**Aspect:** {subtask['aspect']}")
                st.write(f"**Current Situation:** {subtask['current_situation']}")
                st.write(f"**Name:** {subtask['name']}")
                st.write(f"**Detail:** {subtask['detail']}")
                st.write(f"**Start Time:** {subtask['start_time']}")
                st.write(f"**Outcome:** {subtask['outcome']}")
                st.write(f"**Person Involved:** {subtask['person_involved']}")
                st.write(f"**Budget:** ${subtask['budget']}")
                st.write(f"**Deadline:** {subtask['deadline']}")
                st.write(f"**Progress:** {subtask['progress']}%")

                if st.button(f"Delete Subtask {subtask['id']}", key=f"delete_{subtask['id']}"):
                    delete_subtask_from_db(conn, subtask['id'])
                    st.session_state.refresh = not st.session_state.get("refresh", False)
    else:
        st.write("No subtasks found in the database.")
