import streamlit as st
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
    Page to view and manage the existing subtasks database with delete functionality,
    but without using st.experimental_rerun().
    """
    st.title("View Subtasks Database")

    # Fetch data from the database
    df = fetch_subtasks_from_db(conn)

    if not df.empty:
        st.write("Below is the list of all subtasks:")
        st.dataframe(df)

        # Input for row ID to delete
        st.write("### Delete a Subtask")
        row_id = st.number_input("Enter the ID of the row to delete:", min_value=1, step=1)

        # Button to delete the selected row
        if st.button("Delete"):
            if row_id in df["id"].values:
                delete_subtask_from_db(conn, row_id)
                st.success(f"Subtask with ID {row_id} has been deleted.")

                # Re-fetch and display the updated table (so you see changes immediately)
                updated_df = fetch_subtasks_from_db(conn)
                if not updated_df.empty:
                    st.dataframe(updated_df)
                else:
                    st.write("No subtasks found in the database.")
            else:
                st.warning("The entered ID does not exist in the database.")
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
