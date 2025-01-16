import streamlit as st
import pandas as pd
import sqlite3
import datetime
import base64
import json
import requests

from subtasks import (
    initialize_subtasks_database,
    upload_csv_subtasks,        # uploads to 'subtasks' table
    delete_subtask_from_db,     # existing function to delete from 'subtasks' table (unused here)
)
from database_phases import render_database_phases_page  # Import the new Database Phases functionality

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

def fetch_data_from_table(conn: sqlite3.Connection, table_name: str) -> pd.DataFrame:
    """
    Fetch all data from the specified table as a pandas DataFrame.
    """
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql_query(query, conn)

def delete_row_by_id(conn: sqlite3.Connection, table_name: str, row_id: int):
    """
    Delete a row by ID from the specified table.
    Assumes each table has an 'id' column.
    """
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
    conn.commit()

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

    # Fetch all table names from the database
    tables = get_table_names(conn)
    if not tables:
        st.write("No tables found in the database.")
        return

    # Let the user select which table to view
    selected_table = st.selectbox("Select a table to view", options=tables)

    if selected_table:
        # Fetch and display data from the chosen table
        df = fetch_data_from_table(conn, selected_table)

        if not df.empty:
            st.write(f"### Table: {selected_table}")
            st.dataframe(df)

            # Deletion controls
            st.write("#### Delete a Row by ID")
            row_id = st.number_input("Enter the ID of the row to delete:", min_value=1, step=1)

            if st.button("Delete"):
                if "id" in df.columns and row_id in df["id"].values:
                    # 1) Delete from the local database
                    delete_row_by_id(conn, selected_table, row_id)
                    st.success(f"Row with ID {row_id} has been deleted from '{selected_table}'.")

                    # 2) Push the updated database to GitHub
                    commit_msg = f"Delete row {row_id} from {selected_table} at {datetime.datetime.now()}"
                    upload_file_to_github(
                        github_user=github_user,
                        github_repo=github_repo,
                        github_pat=github_pat,
                        file_path="subtasks.db",      # path on GitHub
                        local_file_path="subtasks.db",# local DB file
                        commit_message=commit_msg,
                    )

                    # 3) Refresh and display the updated data
                    updated_df = fetch_data_from_table(conn, selected_table)
                    if not updated_df.empty:
                        st.dataframe(updated_df)
                    else:
                        st.write(f"'{selected_table}' is now empty.")
                else:
                    st.warning(f"ID {row_id} not found in the '{selected_table}' table.")
        else:
            st.write(f"'{selected_table}' table is empty.")

def render_phases_page():
    """
    Temporary 'Phases' page for placeholder content.
    """
    st.title("Phases")
    st.write("This is a placeholder for the Phases page.")
    st.write("You can add content related to project phases or workflows here.")

def render_backend():
    st.set_page_config(page_title="AMAS Data Management", layout="wide")

    # Initialize or connect to the SQLite database
    conn = initialize_subtasks_database()

    # Retrieve GitHub details
    github_user = "habdulhaq87"  # Example user
    github_repo = "amasdatadriven"  # Example repo
    github_pat = st.secrets["github"]["pat"]

    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = {
        "Add Subtasks": lambda c: render_add_subtasks_page(c),
        "View Database": lambda c: render_view_database_page(c, github_user, github_repo, github_pat),
        "Phases": lambda _: render_phases_page(),
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))

    # Render the chosen page
    if choice == "Phases":
        pages[choice](None)
    else:
        pages[choice](conn)

if __name__ == "__main__":
    render_backend()
