# File: budgetapp.py
import streamlit as st
import pandas as pd
import sqlite3
import datetime
import base64
import json
import requests


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

    # Check if the file exists on GitHub to get 'sha'
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


def push_db_to_github(commit_message: str = None):
    """
    Helper to push 'subtasks.db' to your GitHub repo with a default or custom commit message.
    """
    if commit_message is None:
        commit_message = f"Update subtasks.db at {datetime.datetime.now()}"

    github_user = "habdulhaq87"
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]

    upload_file_to_github(
        github_user=github_user,
        github_repo=github_repo,
        github_pat=github_pat,
        file_path="subtasks.db",       # GitHub path
        local_file_path="subtasks.db", # Local file
        commit_message=commit_message,
    )


def fetch_tasks(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Fetch tasks (or subtasks) from the DB with the actual column names.
    """
    query = """
    SELECT
        id,
        category,
        name,
        budget
    FROM subtasks
    """
    return pd.read_sql_query(query, conn)


def fetch_budget_lines(conn: sqlite3.Connection, task_id: int) -> pd.DataFrame:
    """
    Fetch budget lines for a specific task ID.
    """
    table_name = f"budget_{task_id}"
    query = f"SELECT * FROM {table_name};"
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        return None  # Return None if the table does not exist


def render_edit_budget_page(conn: sqlite3.Connection, github_user: str, github_repo: str, github_pat: str):
    """
    Tab: Edit Budget
    """
    st.subheader("Edit Budget")

    # Fetch tasks from the DB
    df = fetch_tasks(conn)
    if df.empty:
        st.warning("No tasks found in the database.")
        return

    st.write("Below is the current list of tasks with their budget:")
    st.dataframe(df)

    # Select a task to edit
    task_ids = df["id"].unique()
    selected_id = st.selectbox("Select a Task ID to edit:", task_ids)

    # Retrieve the row for the selected ID
    row = df.loc[df["id"] == selected_id].iloc[0]

    # Input fields for editing
    current_budget = float(row["budget"]) if not pd.isna(row["budget"]) else 0.0

    new_budget = st.number_input("New Budget:", value=current_budget, step=100.0)

    # Save changes button
    if st.button("Save Changes"):
        query = "UPDATE subtasks SET budget = ? WHERE id = ?;"
        conn.execute(query, (new_budget, selected_id))
        conn.commit()

        st.success(f"Task ID {selected_id} updated with new budget.")
        push_db_to_github(commit_message=f"Updated Task ID {selected_id}: Budget changes")


def render_view_budget_lines_page(conn: sqlite3.Connection):
    """
    Tab: View Budget Lines
    """
    st.subheader("View Budget Lines")

    # Fetch tasks from the DB
    df = fetch_tasks(conn)
    if df.empty:
        st.warning("No tasks found in the database.")
        return

    st.write("Below are the available tasks with budgets:")
    st.dataframe(df)

    # Select a task to view budget lines
    task_ids = df["id"].unique()
    selected_id = st.selectbox("Select a Task ID to view budget lines:", task_ids)

    # Fetch budget lines for the selected task
    budget_lines = fetch_budget_lines(conn, selected_id)
    if budget_lines is None:
        st.warning(f"No budget lines found for Task ID {selected_id}.")
    else:
        st.write(f"Budget Lines for Task ID {selected_id}:")
        st.dataframe(budget_lines)


def render_budget_page(conn: sqlite3.Connection, github_user: str, github_repo: str, github_pat: str):
    """
    Main function to render the budget page with three tabs.
    """
    st.title("Budget Management")

    tab1, tab2 = st.tabs(["Edit Budget", "View Budget Lines"])

    with tab1:
        render_edit_budget_page(conn, github_user, github_repo, github_pat)

    with tab2:
        render_view_budget_lines_page(conn)


def main():
    st.set_page_config(page_title="Budget Management", layout="wide")

    # Initialize SQLite connection
    conn = sqlite3.connect("subtasks.db")

    # GitHub credentials
    github_user = "habdulhaq87"
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]

    render_budget_page(conn, github_user, github_repo, github_pat)


if __name__ == "__main__":
    main()
