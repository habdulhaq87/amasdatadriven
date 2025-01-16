import base64
import datetime
import io
import json
import requests
import sqlite3
import streamlit as st
import pandas as pd

# Function to fetch file SHA and content from GitHub
def get_file_sha_and_content(
    github_user: str,
    github_repo: str,
    github_pat: str,
    file_path: str,
) -> (str, pd.DataFrame):
    url = f"https://api.github.com/repos/{github_user}/{github_repo}/contents/{file_path}"
    headers = {"Authorization": f"Bearer {github_pat}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        sha = data["sha"]
        content_str = base64.b64decode(data["content"]).decode("utf-8")
        csv_buffer = io.StringIO(content_str)
        df = pd.read_csv(csv_buffer, sep=",")
        return sha, df
    else:
        st.error(f"Failed to fetch {file_path} from GitHub: {response.status_code}")
        st.stop()

# Function to upload a file to GitHub
def upload_file_to_github(
    github_user: str,
    github_repo: str,
    github_pat: str,
    file_path: str,
    local_file_path: str,
    commit_message: str,
):
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

# Function to initialize SQLite database
def initialize_database():
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

# Function to fetch subtasks from SQLite database
def fetch_subtasks_from_db(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)

# Function to save subtasks to SQLite database
def save_subtasks_to_db(conn, subtasks):
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
                subtask.get("StartTime").isoformat() if subtask.get("StartTime") else None,
                subtask.get("Outcome", ""),
                subtask.get("PersonInvolved", ""),
                subtask.get("Budget", 0.0),
                subtask.get("Deadline").isoformat() if subtask.get("Deadline") else None,
                subtask.get("Progress", 0),
            ),
        )
    conn.commit()

# Function to delete a subtask from SQLite database
def delete_subtask_from_db(conn, subtask_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()

# Function to render each page
def render_page(df, page_name, conn, github_user, github_repo, github_pat):
    if page_name == "Home":
        st.title("Home Page")
        st.write("Welcome to the AMAS Data Management System!")
        st.dataframe(df)
    else:
        st.title(f"Details for: {page_name}")
        tabs = st.tabs(["View", "Edit", "Subtasks", "View Saved Subtasks"])

        row_data = df[df["Aspect"] == page_name].iloc[0]

        with tabs[0]:
            st.subheader("View Data")
            for col, value in row_data.items():
                st.write(f"**{col}**: {value}")

        with tabs[1]:
            st.subheader("Edit Data")
            editable_data = {}
            for col, value in row_data.items():
                editable_data[col] = st.text_input(f"Edit {col}", str(value))
            if st.button(f"Save Changes for {page_name}"):
                df.update(pd.DataFrame([editable_data]))
                st.success("Changes saved. Be sure to commit changes to GitHub.")

        with tabs[2]:
            st.subheader("Subtasks")

            if "subtasks" not in st.session_state:
                st.session_state.subtasks = []

            for i, subtask in enumerate(st.session_state.subtasks):
                with st.expander(f"Subtask {i + 1}"):
                    subtask["Category"] = row_data["Category"]
                    st.write(f"**Category of Task {i + 1}:** {subtask['Category']}")

                    subtask["Aspect"] = row_data["Aspect"]
                    st.write(f"**Aspect of Task {i + 1}:** {subtask['Aspect']}")

                    subtask["CurrentSituation"] = row_data["CurrentSituation"]
                    st.write(f"**Current Situation of Task {i + 1}:** {subtask['CurrentSituation']}")

                    subtask["Name"] = st.text_input(f"Name of Task {i + 1}", subtask.get("Name", ""))
                    subtask["Detail"] = st.text_area(f"Detail of Task {i + 1}", subtask.get("Detail", ""))
                    subtask["StartTime"] = st.date_input(f"Start Time of Task {i + 1}", subtask.get("StartTime", datetime.date.today()))
                    subtask["Outcome"] = st.text_area(f"Outcome of Task {i + 1}", subtask.get("Outcome", ""))
                    subtask["PersonInvolved"] = st.text_input(f"Person Involved in Task {i + 1}", subtask.get("PersonInvolved", ""))
                    subtask["Budget"] = st.number_input(f"Budget of Task {i + 1}", subtask.get("Budget", 0.0), step=100.0)
                    subtask["Deadline"] = st.date_input(f"Deadline of Task {i + 1}", subtask.get("Deadline", datetime.date.today()))
                    subtask["Progress"] = st.slider(f"Progress of Task {i + 1} (%)", 0, 100, subtask.get("Progress", 0))

            if st.button("Add Subtask"):
                st.session_state.subtasks.append({})

            if st.button(f"Save Subtasks for {page_name}"):
                save_subtasks_to_db(conn, st.session_state.subtasks)
                upload_file_to_github(
                    github_user,
                    github_repo,
                    github_pat,
                    "subtasks.db",
                    "subtasks.db",
                    f"Update subtasks for {page_name} at {datetime.datetime.now()}"
                )

        with tabs[3]:
            st.subheader("View Saved Subtasks")
            saved_subtasks = fetch_subtasks_from_db(conn)
            if not saved_subtasks.empty:
                for _, subtask in saved_subtasks.iterrows():
                    with st.expander(f"Subtask ID: {subtask['id']}"):
                        st.write(f"**Category:** {subtask['category']}")
                        st.write(f"**Aspect:** {subtask['aspect']}")
                        st.write(f"**Current Situation:** {subtask['current_situation']}")
                        st.write(f"**Name:** {subtask['name']}")
                        st.write(f"**Detail:** {subtask['detail']}")
                        st.write(f"**Start Time:** {subtask['start_time']}")
                        st.write(f"**Outcome:** {subtask['outcome']}")
                        st.write(f"**Person Involved:** {subtask['person_involved']}")
                        st.write(f"**Budget:** ${subtask['budget']}")
                        st.write(f"**Deadline:** {subtask['deadline']}")
                        st.write(f"**Progress:** {subtask['progress']}%")

                        if st.button(f"Delete Subtask {subtask['id']}", key=f"delete_{subtask['id']}"):
                            delete_subtask_from_db(conn, subtask['id'])
                            st.session_state.refresh = not st.session_state.get("refresh", False)

            else:
                st.write("No subtasks found in the database.")

# Main function
def render_backend():
    st.set_page_config(page_title="AMAS Data Management", layout="wide")

    st.sidebar.title("Navigation")
    github_user = "habdulhaq87"
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]
    file_path = "amas_data.csv"

    sha, df = get_file_sha_and_content(github_user, github_repo, github_pat, file_path)

    conn = initialize_database()

    pages = ["Home"] + df["Aspect"].dropna().unique().tolist()

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    for page in pages:
        if st.sidebar.button(page):
            st.session_state.current_page = page

    render_page(df, st.session_state.current_page, conn, github_user, github_repo, github_pat)

if __name__ == "__main__":
    render_backend()
