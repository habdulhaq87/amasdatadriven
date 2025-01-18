import streamlit as st
import sqlite3
from subtasks import (
    initialize_subtasks_database,
    upload_csv_subtasks,
    delete_subtask_from_db,
)
from database_phases import render_database_phases_page  # Existing Database Phases functionality
from budget import render_budget_page  # Importing budget management functionality


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


# ------------------- DB HELPERS -------------------
def get_table_names(conn: sqlite3.Connection):
    """
    Fetch the list of all table names in the SQLite database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def fetch_data_from_table(conn: sqlite3.Connection, table_name: str):
    """
    Fetch all data from a specified table as a pandas DataFrame.
    """
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql_query(query, conn)


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
        "Budget Management": lambda c: render_budget_page(c, github_user, github_repo, github_pat),
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))

    if choice == "Database Phases":
        pages[choice](None)  # No direct DB connection needed
    else:
        pages[choice](conn)


# ------------------- MAIN -------------------
if __name__ == "__main__":
    render_backend()
