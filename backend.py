import streamlit as st
import pandas as pd
import sqlite3

from subtasks import (
    initialize_subtasks_database,
    upload_csv_subtasks,        # still specifically uploads to 'subtasks' table
    delete_subtask_from_db,     # specifically deletes from 'subtasks' table
)

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


def render_view_database_page(conn: sqlite3.Connection):
    """
    Page to view and manage any table in the database:
      - Select a table from a dropdown
      - View its contents in a dataframe
      - Delete a row by ID
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
                    delete_row_by_id(conn, selected_table, row_id)
                    st.success(f"Row with ID {row_id} has been deleted from '{selected_table}'.")
                    
                    # Refresh and display the updated data
                    updated_df = fetch_data_from_table(conn, selected_table)
                    if not updated_df.empty:
                        st.dataframe(updated_df)
                    else:
                        st.write(f"'{selected_table}' is now empty.")
                else:
                    st.warning(f"ID {row_id} not found in the '{selected_table}' table.")
        else:
            st.write(f"'{selected_table}' table is empty.")


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
