import sqlite3
import pandas as pd
import streamlit as st

def initialize_subtasks_database():
    """
    Initialize the SQLite database for subtasks.
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
    Fetch all subtasks from the database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subtasks")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def save_subtasks_to_db(conn, subtasks):
    """
    Save a list of subtasks to the database.
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


def update_subtask_in_db(conn, subtask_id, updated_data):
    """
    Update a subtask in the database.
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


def delete_subtask_from_db(conn, subtask_id):
    """
    Delete a subtask from the database by its ID.
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()


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
            st.success("CSV subtasks imported successfully!")


def render_saved_subtasks(conn):
    """
    Render the saved subtasks in an interactive Streamlit UI with edit and delete functionality,
    plus an option to upload subtasks from a CSV file.
    """
    st.subheader("View and Edit Saved Subtasks")

    # Allow CSV upload here
    upload_csv_subtasks(conn)

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
                    st.success(f"Subtask {subtask['id']} updated successfully!")

                if st.button(f"Delete Subtask {subtask['id']}", key=f"delete_{subtask['id']}"):
                    delete_subtask_from_db(conn, subtask["id"])
                    st.success(f"Subtask {subtask['id']} deleted successfully!")
    else:
        st.write("No subtasks found in the database.")
