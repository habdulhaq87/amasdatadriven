import streamlit as st
from subtasks import (
    initialize_subtasks_database,
    upload_csv_subtasks,
    fetch_subtasks_from_db
)

def render_add_subtasks_page(conn):
    """
    Page for uploading subtasks via CSV.
    """
    st.title("Add Subtasks")
    st.write("Upload a CSV of subtasks with the required columns.")
    upload_csv_subtasks(conn)


def render_view_database_page(conn):
    """
    Page to view the existing subtasks database as a simple table.
    """
    st.title("View Subtasks Database")

    df = fetch_subtasks_from_db(conn)
    if not df.empty:
        st.dataframe(df)  # Renders the data as a table
    else:
        st.write("No subtasks found in the database.")


def render_backend():
    st.set_page_config(page_title="AMAS Data Management", layout="wide")

    # Initialize or connect to the SQLite database
    conn = initialize_subtasks_database()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = {
        "Add Subtasks": render_add_subtasks_page,
        "View Database": render_view_database_page
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))

    # Render the chosen page
    pages[choice](conn)


if __name__ == "__main__":
    render_backend()
