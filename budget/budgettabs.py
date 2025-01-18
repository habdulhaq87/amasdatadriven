# File: budgettabs.py
import streamlit as st
import pandas as pd
import sqlite3
import datetime
import requests
import base64
import json


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
        file_path="subtasks.db",
        local_file_path="subtasks.db",
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
    except Exception:
        return None


def create_budget_line_table(conn: sqlite3.Connection, task_id: int):
    """
    Create a budget line table for a specific task ID.
    """
    table_name = f"budget_{task_id}"
    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        line_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        detail TEXT,
        unit TEXT,
        quantity REAL,
        unit_cost REAL,
        total_cost REAL,
        notes TEXT
    );
    """
    conn.execute(query)
    conn.commit()


def insert_budget_lines(conn: sqlite3.Connection, task_id: int, budget_data: pd.DataFrame):
    """
    Insert budget lines into the corresponding budget line table and sync the main budget.
    """
    table_name = f"budget_{task_id}"
    query = f"""
    INSERT INTO {table_name} (item, detail, unit, quantity, unit_cost, total_cost, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    for _, row in budget_data.iterrows():
        conn.execute(query, (
            row["Item"], row["Detail"], row["Unit"], row["Quantity"],
            row["Unit Cost"], row["Total Cost"], row["Notes"]
        ))
    conn.commit()
    sync_budget(conn, task_id)


def sync_budget(conn: sqlite3.Connection, task_id: int):
    """
    Sync the 'budget' value in the 'subtasks' table with the sum of 'total_cost'
    from the 'budget_<task_id>' table.
    """
    table_name = f"budget_{task_id}"
    query_sum = f"SELECT SUM(total_cost) FROM {table_name};"
    total_cost = conn.execute(query_sum).fetchone()[0] or 0.0

    query_update = "UPDATE subtasks SET budget = ? WHERE id = ?;"
    conn.execute(query_update, (total_cost, task_id))
    conn.commit()


def delete_budget_line(conn: sqlite3.Connection, task_id: int, line_item_id: int):
    """
    Delete a specific budget line by line_item_id from the budget_<task_id> table and sync the main budget.
    """
    table_name = f"budget_{task_id}"
    query = f"DELETE FROM {table_name} WHERE line_item_id = ?;"
    conn.execute(query, (line_item_id,))
    conn.commit()
    sync_budget(conn, task_id)


def render_edit_budget_page(conn: sqlite3.Connection, github_user: str, github_repo: str, github_pat: str):
    """
    Tab: Edit Budget
    """
    st.subheader("Edit Budget")

    df = fetch_tasks(conn)
    if df.empty:
        st.warning("No tasks found in the database.")
        return

    st.write("Below is the current list of tasks with their budget:")
    st.dataframe(df)

    task_ids = df["id"].unique()
    selected_id = st.selectbox("Select a Task ID to edit:", task_ids)

    row = df.loc[df["id"] == selected_id].iloc[0]
    current_budget = float(row["budget"]) if not pd.isna(row["budget"]) else 0.0

    new_budget = st.number_input("New Budget:", value=current_budget, step=100.0)

    if st.button("Save Changes"):
        query = "UPDATE subtasks SET budget = ? WHERE id = ?;"
        conn.execute(query, (new_budget, selected_id))
        conn.commit()

        st.success(f"Task ID {selected_id} updated with new budget.")
        push_db_to_github(commit_message=f"Updated Task ID {selected_id}: Budget changes")


def render_view_budget_lines_page(conn: sqlite3.Connection):
    """
    Tab: View Budget Lines and Import CSV
    """
    st.subheader("View & Modify Budget Lines")

    df = fetch_tasks(conn)
    if df.empty:
        st.warning("No tasks found in the database.")
        return

    st.write("Below are the available tasks with budgets:")
    st.dataframe(df)

    task_ids = df["id"].unique()
    selected_id = st.selectbox("Select a Task ID to view and modify budget lines:", task_ids)

    create_budget_line_table(conn, selected_id)

    budget_lines = fetch_budget_lines(conn, selected_id)
    if budget_lines is None or budget_lines.empty:
        st.warning(f"No budget lines found for Task ID {selected_id}.")
    else:
        st.write(f"Budget Lines for Task ID {selected_id}:")
        st.dataframe(budget_lines)

        st.write("To delete a row, select the line_item_id below:")
        line_item_ids = budget_lines["line_item_id"].tolist()
        selected_line_item_id = st.selectbox("Select line_item_id to delete:", line_item_ids)

        if st.button("Delete Selected Line"):
            delete_budget_line(conn, selected_id, selected_line_item_id)
            st.success(f"Line Item {selected_line_item_id} deleted successfully!")
            push_db_to_github(commit_message=f"Deleted Line Item {selected_line_item_id} for Task ID {selected_id}")

    st.subheader("Upload Budget Details")
    uploaded_file = st.file_uploader("Upload a CSV file with budget details:", type="csv")

    if uploaded_file is not None:
        budget_data = pd.read_csv(uploaded_file)
        expected_columns = ["Item", "Detail", "Unit", "Quantity", "Unit Cost", "Total Cost", "Notes"]
        if not all(column in budget_data.columns for column in expected_columns):
            st.error(f"Invalid CSV format. Expected columns: {', '.join(expected_columns)}")
        else:
            st.write("Uploaded Budget Details:")
            st.dataframe(budget_data)

            if st.button("Save Uploaded Budget Details"):
                insert_budget_lines(conn, selected_id, budget_data)
                st.success(f"Budget details for Task ID {selected_id} saved successfully!")
                push_db_to_github(commit_message=f"Updated budget lines for Task ID {selected_id}")


def render_budget_page(conn: sqlite3.Connection, github_user: str, github_repo: str, github_pat: str):
    """
    Main function to render the budget page with tabs.
    """
    st.title("Budget Management")

    tab1, tab2 = st.tabs(["Edit Budget", "View & Modify Budget Lines"])

    with tab1:
        render_edit_budget_page(conn, github_user, github_repo, github_pat)

    with tab2:
        render_view_budget_lines_page(conn)
