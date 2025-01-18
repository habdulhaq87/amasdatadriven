# File: budgetapp.py
import streamlit as st
import sqlite3
from budgettabs import render_budget_page


def main():
    st.set_page_config(page_title="Budget Management", layout="wide")

    # Initialize SQLite connection
    conn = sqlite3.connect("subtasks.db")

    # GitHub credentials
    github_user = "habdulhaq87"
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]

    # Render the budget page with tabs
    render_budget_page(conn, github_user, github_repo, github_pat)

    # Close the database connection when the app ends
    conn.close()


if __name__ == "__main__":
    main()
