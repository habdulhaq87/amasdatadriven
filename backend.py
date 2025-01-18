import streamlit as st
import pandas as pd
import sqlite3
import datetime
import base64
import json
import requests

from subtasks import (
    initialize_subtasks_database,
    upload_csv_subtasks,
    delete_subtask_from_db,
)

from database_phases import render_database_phases_page  # Existing Database Phases functionality


# ------------------- GITHUB UPLOAD FUNCTION -------------------
def upload_file_to_github(
    github_user: str,
    github_repo: str,
    github_pat: str,
    file_path: str,
    local_file_path: str,
    commit_message: str,
):
    """
    Upload or update a file (e.g., 'subtasks.db') in the given GitHub repo.
    """
    url = f"https://api.github.com/repos/{github_user}/{github_repo}/contents/{file_path}"
    headers = {"Authorization": f"Bearer {github_pat}"}

    with open(local_file_path, "rb") as file:
        content = file.read()

    b64_content = base64.b64encode(content).decode("utf-8")

    # First, check if the file exists on GitHub to get its 'sha'
    response = requests.get(url, headers=headers)
    sha = response.json()["sha"] if response.status_code == 200 else None

    payload = {
        "message": commit_message,
        "content": b64_content,
        "sha": sha,
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code in [200, 201]:
        st.success("Database successfully pushed to GitHub.")
    else:
        st.error(f"Failed to upload file to GitHub: {response.status_code}\n{response.text}")


# ------------------- DB HELPERS -------------------
def get_table_names(conn: sqlite3.Connection):
    """
    Fetch the list of all table names in the SQLite database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def fetch_data_from_table(conn: sqlite3.Connection, table_name: str) -> pd.DataFrame:
    """
    Fetch all data from a specified table as a pandas DataFrame.
    """
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql_query(query, conn)


# ------------------- BUDGET & TIMELINE FUNCTIONS -------------------
def fetch_tasks_for_budget_timeline(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Fetch tasks from 'subtasks' including Budget, Start Time, and Deadline.
    Adjust column names if your DB differs.
    """
    query = """
    SELECT
        id,
        Category,
        Name,
        Budget,
        [Start Time] as start_time,
        Deadline
    FROM subtasks
    """
    return pd.read_sql_query(query, conn)


def update_task_budget_and_timeline(
    conn: sqlite3.Connection,
    task_id: int,
    new_budget: float,
    new_start: datetime.date,
    new_end: datetime.date
):
    """
    Update the budget, start_time, and deadline for a given task ID.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE subtasks
        SET
            Budget = ?,
            [Start Time] = ?,
            Deadline = ?
        WHERE id = ?
        """,
        (
            new_budget,
            new_start.isoformat() if new_start else None,
            new_end.isoformat() if new_end else None,
            task_id
        ),
    )
    conn.commit()


def render_budget_page(conn: sqlite3.Connection, github_user: str, github_repo: str, github_pat: str):
    """
    Page for managing and editing Budget, Start Time, and End Time for tasks.
    """
    st.title("Budget & Timeline Management")

    # 1) Fetch tasks
    df = fetch_tasks_for_budget_timeline(conn)

    if df.empty:
        st.warning("No tasks found in the database.")
        return

    st.write("Below are the tasks/subtasks, including budgets and timelines:")
    st.dataframe(df)

    # 2) Select a task to edit
    task_ids = df["id"].unique()
    selected_id = st.selectbox("Select a Task ID to edit:", task_ids)

    # 3) Extract current row data
    row = df.loc[df["id"] == selected_id].iloc[0]
    current_budget = row["Budget"] if not pd.isna(row["Budget"]) else 0.0

    # Handle date parsing for Start Time
    if isinstance(row["start_time"], str) and row["start_time"]:
        try:
            start_date_obj = datetime.datetime.strptime(row["start_time"], "%Y-%m-%d").date()
        except ValueError:
            start_date_obj = datetime.date.today()
    else:
        start_date_obj = datetime.date.today()

    # Handle date parsing for Deadline
    if isinstance(row["Deadline"], str) and row["Deadline"]:
        try:
            end_date_obj = datetime.datetime.strptime(row["Deadline"], "%Y-%m-%d").date()
        except ValueError:
            end_date_obj = datetime.date.today()
    else:
        end_date_obj = datetime.date.today()

    # 4) Input widgets
    new_budget = st.number_input("Budget:", value=float(current_budget), step=100.0)
    new_start_date = st.date_input("Start Time:", value=start_date_obj)
    new_end_date = st.date_input("Deadline:", value=end_date_obj)

    if st.button("Save Changes"):
        # 5) Update DB
        update_task_budget_and_timeline(conn, selected_id, new_budget, new_start_date, new_end_date)
        st.success(f"Task ID {selected_id} updated with new budget, start time, and end time.")

        # 6) Push changes to GitHub
        commit_msg = f"Updated budget/timeline for Task {selected_id} at {datetime.datetime.now()}"
        upload_file_to_github(
            github_user=github_user,
            github_repo=github_repo,
            github_pat=github_pat,
            file_path="subtasks.db",
            local_file_path="subtasks.db",
            commit_message=commit_msg
        )

        # Refresh page
        st.experimental_rerun()


# ------------------- ADDING SUBTASKS PAGE -------------------
def render_add_subtasks_page(conn: sqlite3.Connection):
    """
    Page for uploading subtasks via CSV (to the 'subtasks' table).
    """
    st.title("Add Subtasks")
    st.write("Upload a CSV with columns matching the 'subtasks' schema.")
    upload_csv_subtasks(conn)


# ------------------- VIEW DATABASE PAGE -------------------
def render_view_database_page(conn: sqlite3.Connection, github_user, github_repo, github_pat):
    """
    Page to view any table in the DB (read-only here).
    """
    st.title("View Database")
    tables = get_table_names(conn)
    if not tables:
        st.write("No tables found in the database.")
        return

    selected_table = st.selectbox("Select a table to view", options=tables)
    if selected_table:
        df = fetch_data_from_table(conn, selected_table)
        if not df.empty:
            st.write(f"### Table: {selected_table}")
            st.dataframe(df)
        else:
            st.write(f"'{selected_table}' is empty.")


# ------------------- MAIN BACKEND RENDER -------------------
def render_backend():
    st.set_page_config(page_title="AMAS Data Management", layout="wide")

    # Initialize DB
    conn = initialize_subtasks_database()

    # GitHub credentials
    github_user = "habdulhaq87"
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]

    # Navigation
    st.sidebar.title("Navigation")
    pages = {
        "Add Subtasks": lambda c: render_add_subtasks_page(c),
        "View Database": lambda c: render_view_database_page(c, github_user, github_repo, github_pat),
        "Database Phases": lambda _: render_database_phases_page(),
        # Budget & Timeline management
        "Budget & Timeline": lambda c: render_budget_page(c, github_user, github_repo, github_pat),
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))

    if choice == "Database Phases":
        pages[choice](None)  # No direct DB connection needed
    else:
        pages[choice](conn)


# ------------------- MAIN -------------------
if __name__ == "__main__":
    render_backend()
