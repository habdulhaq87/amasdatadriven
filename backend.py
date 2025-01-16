import streamlit as st
import pandas as pd
from subtasks import (
    initialize_subtasks_database,
    upload_csv_subtasks,
    fetch_subtasks_from_db,
    delete_subtask_from_db,
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
    Page to view and manage the existing subtasks database as a table.
    """
    st.title("View Subtasks Database")

    # Fetch data from the database
    df = fetch_subtasks_from_db(conn)

    if not df.empty:
        # Add a "Delete" column with checkboxes
        st.write("Select rows to delete by checking the boxes.")
        df['Delete'] = False  # Temporary column for checkboxes
        for index in df.index:
            df.at[index, 'Delete'] = st.checkbox(f"Delete row {df.loc[index, 'id']}", key=f"delete_{index}")

        # Display the table without the "Delete" column
        st.dataframe(df.drop(columns=["Delete"]))

        # Handle delete action
        if st.button("Delete Selected Rows"):
            rows_to_delete = df[df['Delete'] == True]
            if not rows_to_delete.empty:
                for subtask_id in rows_to_delete['id']:
                    delete_subtask_from_db(conn, subtask_id)
                st.success(f"Deleted {len(rows_to_delete)} selected row(s).")
                st.experimental_rerun()  # Refresh the page to update the table
            else:
                st.warning("No rows selected for deletion.")
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
        "View Database": render_view_database_page,
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))

    # Render the chosen page
    pages[choice](conn)


if __name__ == "__main__":
    render_backend()
