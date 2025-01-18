# File: budget.py
import streamlit as st
import pandas as pd
import sqlite3
import datetime


def push_db_to_github(
    github_user: str,
    github_repo: str,
    github_pat: str,
    file_path: str = "subtasks.db",
    local_file_path: str = "subtasks.db",
    commit_message: str = None,
):
    """
    Push the 'subtasks.db' file to GitHub.
    """
    if commit_message is None:
        commit_message = f"Update subtasks.db at {datetime.datetime.now()}"

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


def fetch_tasks(conn: sqlite3.Connection) -> pd.DataFrame:
    """
    Fetch tasks (or subtasks) from the database.
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
    Update the budget, start_time, and deadline for a given task ID.
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

    st.write("Below is the current list of tasks with their budget, start time, and deadline:")
    st.dataframe(df)

    # Select a task to edit
    task_ids = df["id"].unique()
    selected_id = st.selectbox("Select a Task ID to edit:", task_ids)

    # Retrieve the row for the selected ID
    row = df.loc[df["id"] == selected_id].iloc[0]

    # Input fields for editing
    current_budget = float(row["budget"]) if not pd.isna(row["budget"]) else 0.0
    current_start_time = row["start_time"] if isinstance(row["start_time"], str) else None
    current_deadline = row["deadline"] if isinstance(row["deadline"], str) else None

    def parse_date_or_today(date_str):
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            return datetime.date.today()

    new_budget = st.number_input("New Budget:", value=current_budget, step=100.0)
    new_start_date = st.date_input("Start Time:", value=parse_date_or_today(current_start_time))
    new_deadline_date = st.date_input("Deadline:", value=parse_date_or_today(current_deadline))

    # Save changes button
    if st.button("Save Changes"):
        update_task_budget_and_timeline(conn, selected_id, new_budget, new_start_date, new_deadline_date)
        st.success(f"Task ID {selected_id} updated with new budget, start time, and deadline.")

        push_db_to_github(
            github_user=github_user,
            github_repo=github_repo,
            github_pat=github_pat,
            commit_message=f"Updated Task ID {selected_id}: Budget/Timeline changes",
        )
        st.info("Changes saved. Refresh the page to see the updates.")


def render_import_budget_page():
    """
    Tab: Import Budget
    Placeholder for budget import functionality.
    """
    st.subheader("Import Budget")
    st.write("This functionality is under development.")


def render_budget_page(conn: sqlite3.Connection, github_user: str, github_repo: str, github_pat: str):
    """
    Main function to render the budget page with two tabs.
    """
    st.title("Budget Management")

    tab1, tab2 = st.tabs(["Edit Budget", "Import Budget"])

    with tab1:
        render_edit_budget_page(conn, github_user, github_repo, github_pat)

    with tab2:
        render_import_budget_page()
