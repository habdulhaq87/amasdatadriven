import streamlit as st
import pandas as pd
import sqlite3
from subtasks import (
    initialize_subtasks_database,
    upload_csv_subtasks,
    render_saved_subtasks,
)

# Optional GitHub functions, if you still need them:
# --------------------------------------------------
# import base64
# import datetime
# import io
# import json
# import requests

# def get_file_sha_and_content(...):
#     # Implementation here if needed
#     pass

# def upload_file_to_github(...):
#     # Implementation here if needed
#     pass
# --------------------------------------------------

def render_add_subtasks_page(conn):
    """
    Page for uploading subtasks via CSV.
    """
    st.title("Add Subtasks")
    st.write("Upload a CSV of subtasks with the required columns.")
    upload_csv_subtasks(conn)


def render_view_database_page(conn):
    """
    Page to view and manage the existing subtasks database.
    """
    st.title("View Subtasks Database")
    st.write("Review and edit saved subtasks below.")
    render_saved_subtasks(conn)


def render_backend():
    st.set_page_config(page_title="AMAS Data Management", layout="wide")
    
    # Create or connect to the subtasks database
    conn = initialize_subtasks_database()
    
    # Define the pages available in the sidebar
    pages = {
        "Add Subtasks": render_add_subtasks_page,
        "View Database": render_view_database_page,
    }
    
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", list(pages.keys()))
    
    # Render the chosen page
    pages[choice](conn)


if __name__ == "__main__":
    render_backend()
