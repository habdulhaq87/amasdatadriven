import streamlit as st
import sqlite3
import pandas as pd
import datetime

# Initialize the database
def initialize_database():
    conn = sqlite3.connect("tasks.db")  # Replace with your actual DB file
    return conn

# Fetch all tasks for budget management
def fetch_budget_data(conn):
    query = "SELECT id, category, name, budget, budget_last_updated FROM tasks"
    return pd.read_sql_query(query, conn)

# Update the budget in the database
def update_budget(conn, task_id, new_budget):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET budget = ?, budget_last_updated = ? WHERE id = ?",
        (new_budget, datetime.datetime.now().isoformat(), task_id),
    )
    conn.commit()

# Render the Budget Editing Page
def render_budget_page():
    st.title("Budget Management")

    conn = initialize_database()
    budget_data = fetch_budget_data(conn)

    if not budget_data.empty:
        st.write("### Current Budgets")
        st.dataframe(budget_data)

        st.write("#### Edit Task Budgets")
        task_id = st.selectbox("Select a Task ID to Edit", budget_data["id"].unique())
        task_row = budget_data[budget_data["id"] == task_id].iloc[0]

        st.write(f"**Task Name**: {task_row['name']}")
        st.write(f"**Current Budget**: {task_row['budget']}")
        new_budget = st.number_input("Enter New Budget", value=task_row["budget"], step=100.0)

        if st.button("Update Budget"):
            update_budget(conn, task_id, new_budget)
            st.success(f"Budget updated for Task ID {task_id} to {new_budget}")

            # Optional: Push the database to GitHub (use your GitHub integration function)
            # push_db_to_github("Budget updated for Task ID {task_id}")

            st.experimental_rerun()  # Refresh the page to show updated data
    else:
        st.warning("No tasks found in the database.")

if __name__ == "__main__":
    render_budget_page()
