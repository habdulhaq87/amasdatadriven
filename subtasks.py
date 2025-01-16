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

def fetch_subtasks_from_db(conn):
    """Fetch all subtasks from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks")
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
  
