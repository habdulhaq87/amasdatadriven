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
from database_phases import render_database_phases_page  # Import the Database Phases functionality

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


def get_table_names(conn: sqlite3.Connection):
    """
    Fetch and return the list of all table names in the SQLite database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def fetch_budget_data(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Fetch all tasks and their budgets for budget management.
    """
    query = "SELECT id, category, name, budget FROM subtasks"
    return pd.read_sql_query(query, conn)


def update_budget(conn: sqlite3.Connection, task_id: int, new_budget: float):
    """
    Update the budget for a specific task.
    """
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE subtasks SET budget = ?, budget_last_updated = ? WHERE id = ?",
        (new_budget, datetime.datetime.now().isoformat(), task_id),
    )
    conn.commit()


def render_budget_page(conn: sqlite3.Connection, github_user, github_repo, github_pat):
    """
    Page for managing and editing budgets.
    """
    st.title("Budget Management")

    budget_data = fetch_budget_data(conn)

    if not budget_data.empty:
        st.write("### Current Budgets")
        st.dataframe(budget_data)

        st.write("#### Edit Task Budgets")
        task_id = st.selectbox("Select a Task ID to Edit", budget_data["id"].unique())
        task_row = budget_data[budget_data["id"] == task_id].iloc[0]

        st.write(f"**Task Name**: {task_row['name']}")
        st.write(f"**Current Budget**: {task_row['budget']}")
        new_budget = st.number_input("Enter New Budget", value=task_row["budget"], step=100.0)

        if st.button("Update Budget"):
            update_budget(conn, task_id, new_budget)
            st.success(f"Budget updated for Task ID {task_id} to {new_budget}")

            # Push the updated database to GitHub
            commit_msg = f"Budget updated for Task ID {task_id} at {datetime.datetime.now()}"
            upload_file_to_github(
                github_user=github_user,
                github_repo=github_repo,
                github_pat=github_pat,
                file_path="subtasks.db",  # Path on GitHub
                local_file_path="subtasks.db",  # Local DB file
                commit_message=commit_msg,
            )

            st.experimental_rerun()
    else:
        st.warning("No tasks found in the database.")


def render_add_subtasks_page(conn: sqlite3.Connection):
    """
    Page for uploading subtasks via CSV (to the 'subtasks' table).
    """
    st.title("Add Subtasks")
    st.write("Upload a CSV of subtasks with the required columns.")
    upload_csv_subtasks(conn)


def render_view_database_page(conn: sqlite3.Connection, github_user, github_repo, github_pat):
    """
    Page to view and manage any table in the database.
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


def render_backend():
    st.set_page_config(page_title="AMAS Data Management", layout="wide")

    # Initialize or connect to the SQLite database
    conn = initialize_subtasks_database()

    # Retrieve GitHub details
    github_user = "habdulhaq87"
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]

    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = {
        "Add Subtasks": lambda c: render_add_subtasks_page(c),
        "View Database": lambda c: render_view_database_page(c, github_user, github_repo, github_pat),
        "Database Phases": lambda _: render_database_phases_page(),
        "Budget Management": lambda c: render_budget_page(c, github_user, github_repo, github_pat),
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))

    if choice == "Database Phases":
        pages[choice](None)
    else:
        pages[choice](conn)


if __name__ == "__main__":
    render_backend()
