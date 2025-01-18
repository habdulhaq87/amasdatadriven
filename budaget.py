# File: budget.py
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

    # Check if file exists on GitHub to get 'sha'
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

def fetch_tasks(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Fetch tasks (or subtasks) from the DB with the actual column names.
    Adjust these columns if your table differs!
    """
    query = """
    SELECT
        id,
        category,
        aspect,
        current_situation,
        name,
        detail,
        start_time,
        outcome,
        person_involved,
        budget,
        deadline,
        progress
    FROM subtasks
    """
    return pd.read_sql_query(query, conn)

def update_task_budget_and_timeline(
    conn: sqlite3.Connection,
    task_id: int,
    new_budget: float,
    new_start_time: datetime.date,
    new_deadline: datetime.date,
):
    """
    Update budget, start_time, and deadline for a given task ID.
    Make sure these columns match your actual DB schema exactly!
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE subtasks
        SET
            budget = ?,
            start_time = ?,
            deadline = ?
        WHERE id = ?
        """,
        (
            new_budget,
            new_start_time.isoformat() if new_start_time else None,
            new_deadline.isoformat() if new_deadline else None,
            task_id,
        ),
    )
    conn.commit()

def render_budget_page(conn: sqlite3.Connection, github_user: str, github_repo: str, github_pat: str):
    """
    Streamlit page: Budget & Timeline Management.
    Allows editing budget, start_time, and deadline in 'subtasks'.
    """
    st.title("Budget & Timeline Management")

    # 1) Fetch tasks from the DB
    df = fetch_tasks(conn)

    if df.empty:
        st.warning("No tasks found in the database.")
        return

    st.write("Below is the current list of tasks with their budget, start time, and deadline:")
    st.dataframe(df)

    # 2) Select a task by ID
    task_ids = df["id"].unique()
    selected_id = st.selectbox("Select a Task ID to edit:", task_ids)

    # 3) Retrieve the row for that selected ID
    row = df.loc[df["id"] == selected_id].iloc[0]

    # 4) Current values
    current_budget = float(row["budget"]) if not pd.isna(row["budget"]) else 0.0
    current_start_time = row["start_time"] if isinstance(row["start_time"], str) else None
    current_deadline = row["deadline"] if isinstance(row["deadline"], str) else None

    # 5) Create input widgets
    new_budget = st.number_input("New Budget:", value=current_budget, step=100.0)

    # Convert stored strings to dates
    try:
        st_time = datetime.datetime.strptime(current_start_time, "%Y-%m-%d").date() if current_start_time else datetime.date.today()
    except:
        st_time = datetime.date.today()

    try:
        dl_time = datetime.datetime.strptime(current_deadline, "%Y-%m-%d").date() if current_deadline else datetime.date.today()
    except:
        dl_time = datetime.date.today()

    new_start_date = st.date_input("Start Time:", value=st_time)
    new_deadline_date = st.date_input("Deadline:", value=dl_time)

    # 6) Button to update
    if st.button("Save Changes"):
        # Update local DB
        update_task_budget_and_timeline(conn, selected_id, new_budget, new_start_date, new_deadline_date)
        st.success(f"Task ID {selected_id} updated with new budget, start time, and deadline.")

        # 7) Optional: push to GitHub
        commit_msg = f"Updated budget/timeline for Task ID {selected_id} at {datetime.datetime.now()}"
        upload_file_to_github(
            github_user=github_user,
            github_repo=github_repo,
            github_pat=github_pat,
            file_path="subtasks.db",
            local_file_path="subtasks.db",
            commit_message=commit_msg,
        )

        # 8) Refresh display
        st.experimental_rerun()
