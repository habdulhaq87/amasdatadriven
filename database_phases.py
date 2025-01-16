import streamlit as st
import sqlite3
import pandas as pd
import csv
import io
import datetime
import base64
import json
import requests

# ------------------- GITHUB PUSH HELPER -------------------
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

    # Read local file
    with open(local_file_path, "rb") as file:
        content = file.read()

    b64_content = base64.b64encode(content).decode("utf-8")

    # Check if file exists on GitHub to get its 'sha'
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


# ------------------- DATABASE HELPERS -------------------
def initialize_database(db_name: str = "subtasks.db") -> sqlite3.Connection:
    """Create/connect to the 'subtasks.db' database."""
    return sqlite3.connect(db_name)

def create_table_from_file(conn: sqlite3.Connection, table_name: str, file_content: bytes, delimiter: str = None):
    """
    Create (or replace) a table in 'subtasks.db' by reading the uploaded file_content.
    """
    # Convert bytes to string
    s = file_content.decode("utf-8", errors="ignore")

    # Auto-detect delimiter if none is provided
    if delimiter is None:
        sniffer = csv.Sniffer()
        sample_size = min(len(s), 2048)  # up to 2KB
        sample = s[:sample_size]
        try:
            dialect = sniffer.sniff(sample, delimiters=[",", "\t", ";", "|"])
            delimiter = dialect.delimiter
        except:
            # fallback
            delimiter = ","

    # Read into DataFrame
    df = pd.read_csv(io.StringIO(s), sep=delimiter)

    # Create or replace the table
    df.to_sql(table_name, conn, if_exists="replace", index=False)


# ------------------- STREAMLIT PAGE -------------------
def render_database_phases_page():
    """
    Streamlit page to:
    1) Upload a CSV or TXT.
    2) Create/replace a table in subtask.db.
    3) Push subtask.db to GitHub.
    """
    st.title("Import Data into Database (Phases)")
    st.write("Use this page to import data (CSV/TXT) into a new table in `subtasks.db` and push to GitHub.")

    # GitHub details (please ensure these are correct or in st.secrets)
    github_user = "habdulhaq87"  
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]  # Make sure this is set in your Streamlit secrets

    # Database name and default table name
    db_name = "subtasks.db"
    default_table = "phases"

    # Let the user specify a table name
    table_name = st.text_input("Table name to create or replace", value=default_table)

    # Delimiter choices
    delimiter_choice = st.selectbox(
        "Delimiter (if unsure, pick Auto-detect)",
        ["Auto-detect", "Comma (,)", "Tab (\\t)", "Semicolon (;)", "Pipe (|)"]
    )
    delimiter_map = {
        "Auto-detect": None,
        "Comma (,)": ",",
        "Tab (\\t)": "\t",
        "Semicolon (;)": ";",
        "Pipe (|)": "|",
    }
    chosen_delimiter = delimiter_map[delimiter_choice]

    # File uploader
    file = st.file_uploader("Upload CSV or TXT file", type=["csv", "txt", "tsv"])

    if file is not None:
        # We'll attempt a quick preview
        try:
            file_content = file.read()
            s = file_content.decode("utf-8", errors="ignore")

            # If auto-detect requested
            if chosen_delimiter is None:
                sniffer = csv.Sniffer()
                sample_size = min(len(s), 2048)
                sample = s[:sample_size]
                try:
                    dialect = sniffer.sniff(sample, delimiters=[",", "\t", ";", "|"])
                    autodetected = dialect.delimiter
                except:
                    autodetected = ","
            else:
                autodetected = chosen_delimiter

            # Attempt preview
            df_preview = pd.read_csv(io.StringIO(s), sep=autodetected)
            st.write("**Preview** of the first few rows:")
            st.dataframe(df_preview.head())
        except Exception as e:
            st.warning(f"Could not preview the file: {e}")
            file.seek(0)  # reset pointer in case we still want to import

        # Import to DB
        if st.button("Import & Push to GitHub"):
            try:
                # Re-establish file content pointer if needed
                file.seek(0)
                file_content = file.read()

                # 1) Initialize local DB
                conn = initialize_database(db_name)
                
                # 2) Create or replace table
                create_table_from_file(conn, table_name, file_content, delimiter=chosen_delimiter)
                st.success(f"Table '{table_name}' created or replaced in '{db_name}'.")

                conn.commit()
                conn.close()

                # 3) Push to GitHub
                commit_msg = f"Create or update table '{table_name}' at {datetime.datetime.now()}"
                upload_file_to_github(
                    github_user=github_user,
                    github_repo=github_repo,
                    github_pat=github_pat,
                    file_path=db_name,       # on GitHub, same name
                    local_file_path=db_name, # local name
                    commit_message=commit_msg
                )
            except Exception as e:
                st.error(f"An error occurred during import or push: {e}")

if __name__ == "__main__":
    st.set_page_config(page_title="Phases Database Import", layout="wide")
    render_database_phases_page()
