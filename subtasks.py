import sqlite3
import pandas as pd
import streamlit as st
import datetime
import base64
import json
import requests
from database_phases import render_database_phases_page  # Existing Database Phases functionality


# ========================= GITHUB PUSH FUNCTION =========================
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

    # Read local file into memory
    with open(local_file_path, "rb") as file:
        content = file.read()

    b64_content = base64.b64encode(content).decode("utf-8")

    # Check if file already exists on GitHub to get its 'sha'
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
    
    # Use st.secrets or your own method for these values:
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


# ========================= DATABASE SETUP =========================
def initialize_subtasks_database():
    """
    Initialize (or connect to) the SQLite database for subtasks.
    """
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
    """
    Fetch all subtasks from the database as a pandas DataFrame.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def save_subtasks_to_db(conn, subtasks):
    """
    Save a list of subtasks to the database (INSERT).
    Then push the updated 'subtasks.db' to GitHub.
    """
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
                subtask["StartTime"].isoformat() if subtask.get("StartTime") else None,
                subtask.get("Outcome", ""),
                subtask.get("PersonInvolved", ""),
                subtask.get("Budget", 0.0),
                subtask["Deadline"].isoformat() if subtask.get("Deadline") else None,
                subtask.get("Progress", 0),
            ),
        )
    conn.commit()

    # Push the updated DB to GitHub
    push_db_to_github(commit_message="Add new subtasks.")


def update_subtask_in_db(conn, subtask_id, updated_data):
    """
    Update a subtask in the database by its ID.
    Then push the updated 'subtasks.db' to GitHub.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE subtasks
        SET category = ?, aspect = ?, current_situation = ?, name = ?, detail = ?,
            start_time = ?, outcome = ?, person_involved = ?, budget = ?, deadline = ?, progress = ?
        WHERE id = ?
        """,
        (
            updated_data.get("category", ""),
            updated_data.get("aspect", ""),
            updated_data.get("current_situation", ""),
            updated_data.get("name", ""),
            updated_data.get("detail", ""),
            updated_data.get("start_time", None),
            updated_data.get("outcome", ""),
            updated_data.get("person_involved", ""),
            updated_data.get("budget", 0.0),
            updated_data.get("deadline", None),
            updated_data.get("progress", 0),
            subtask_id,
        ),
    )
    conn.commit()

    # Push the updated DB to GitHub
    push_db_to_github(commit_message=f"Update subtask {subtask_id}.")


def delete_subtask_from_db(conn, subtask_id):
    """
    Delete a subtask from the database by its ID.
    Then push the updated 'subtasks.db' to GitHub.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()

    # Push the updated DB to GitHub
    push_db_to_github(commit_message=f"Delete subtask {subtask_id}.")


# ========================= UI FUNCTIONS =========================
def upload_csv_subtasks(conn):
    """
    Provide a file uploader to import subtasks from a CSV file.
    The CSV is expected to have columns:
      Category, Aspect, Current Situation, Name, Detail, Start Time, 
      Outcome, Person Involved, Budget, Deadline, Progress (%)
    """
    st.subheader("Upload Subtasks from CSV")
    csv_file = st.file_uploader("Upload CSV", type=["csv"])

    if csv_file is not None:
        df = pd.read_csv(csv_file)

        st.write("Preview of uploaded CSV:")
        st.dataframe(df.head())

        if st.button("Import CSV"):
            new_subtasks = []

            for _, row in df.iterrows():
                subtask = {
                    "Category": row.get("Category", ""),
                    "Aspect": row.get("Aspect", ""),
                    "CurrentSituation": row.get("Current Situation", ""),
                    "Name": row.get("Name", ""),
                    "Detail": row.get("Detail", ""),
                    "StartTime": pd.to_datetime(row["Start Time"]).date() if row.get("Start Time") else None,
                    "Outcome": row.get("Outcome", ""),
                    "PersonInvolved": row.get("Person Involved", ""),
                    "Budget": float(row.get("Budget", 0.0)),
                    "Deadline": pd.to_datetime(row["Deadline"]).date() if row.get("Deadline") else None,
                    "Progress": int(row.get("Progress (%)", 0)),
                }
                new_subtasks.append(subtask)

            # Now save the newly uploaded subtasks to the database
            save_subtasks_to_db(conn, new_subtasks)
            st.success("CSV subtasks imported and pushed to GitHub successfully!")


def render_saved_subtasks(conn):
    """
    Render the saved subtasks in an interactive Streamlit UI with:
      - CSV upload
      - Edit
      - Delete
    Each operation triggers a GitHub push.
    """
    st.subheader("View and Edit Saved Subtasks")

    # Allow CSV upload here
    upload_csv_subtasks(conn)

    # Fetch and display existing subtasks
    saved_subtasks = fetch_subtasks_from_db(conn)

    if not saved_subtasks.empty:
        for _, subtask in saved_subtasks.iterrows():
            with st.expander(f"Subtask ID: {subtask['id']}"):
                updated_data = {}

                updated_data["category"] = st.text_input("Category", subtask["category"], key=f"category_{subtask['id']}")
                updated_data["aspect"] = st.text_input("Aspect", subtask["aspect"], key=f"aspect_{subtask['id']}")
                updated_data["current_situation"] = st.text_area("Current Situation", subtask["current_situation"], key=f"current_situation_{subtask['id']}")
                updated_data["name"] = st.text_input("Name", subtask["name"], key=f"name_{subtask['id']}")
                updated_data["detail"] = st.text_area("Detail", subtask["detail"], key=f"detail_{subtask['id']}")
                updated_data["start_time"] = st.text_input("Start Time", subtask["start_time"], key=f"start_time_{subtask['id']}")
                updated_data["outcome"] = st.text_area("Outcome", subtask["outcome"], key=f"outcome_{subtask['id']}")
                updated_data["person_involved"] = st.text_input("Person Involved", subtask["person_involved"], key=f"person_involved_{subtask['id']}")
                updated_data["budget"] = st.number_input("Budget", subtask["budget"], step=100.0, key=f"budget_{subtask['id']}")
                updated_data["deadline"] = st.text_input("Deadline", subtask["deadline"], key=f"deadline_{subtask['id']}")
                updated_data["progress"] = st.slider("Progress (%)", 0, 100, subtask["progress"], key=f"progress_{subtask['id']}")

                if st.button(f"Save Changes for Subtask {subtask['id']}", key=f"save_{subtask['id']}"):
                    update_subtask_in_db(conn, subtask["id"], updated_data)
                    st.success(f"Subtask {subtask['id']} updated and pushed to GitHub.")

                if st.button(f"Delete Subtask {subtask['id']}", key=f"delete_{subtask['id']}"):
                    delete_subtask_from_db(conn, subtask["id"])
                    st.success(f"Subtask {subtask['id']} deleted and pushed to GitHub.")
    else:
        st.write("No subtasks found in the database.")
