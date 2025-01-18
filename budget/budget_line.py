import streamlit as st
import sqlite3
import pandas as pd
import os

# Initialize the database connection
def initialize_db():
    return sqlite3.connect("subtasks.db")

# Fetch available task IDs and names from the 'subtasks' table
def fetch_task_ids_and_names(conn):
    query = "SELECT id, name, budget FROM subtasks;"
    return pd.read_sql_query(query, conn)

# Create a budget line table for a specific task ID
def create_budget_line_table(conn, task_id):
    table_name = f"budget_{task_id}"
    query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        line_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        detail TEXT,
        unit TEXT,
        quantity REAL,
        unit_cost REAL,
        total_cost REAL,
        notes TEXT
    );
    """
    conn.execute(query)
    conn.commit()

# Insert budget details into the budget line table
def insert_budget_lines(conn, task_id, budget_data):
    table_name = f"budget_{task_id}"
    query = f"""
    INSERT INTO {table_name} (item, detail, unit, quantity, unit_cost, total_cost, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    for _, row in budget_data.iterrows():
        conn.execute(query, (
            row["Item"], row["Detail"], row["Unit"], row["Quantity"],
            row["Unit Cost"], row["Total Cost"], row["Notes"]
        ))
    conn.commit()

# Update the main subtasks budget after inserting budget lines
def update_main_budget(conn, task_id):
    table_name = f"budget_{task_id}"
    query = f"SELECT SUM(total_cost) FROM {table_name};"
    total_budget = conn.execute(query).fetchone()[0] or 0.0

    update_query = "UPDATE subtasks SET budget = ? WHERE id = ?;"
    conn.execute(update_query, (total_budget, task_id))
    conn.commit()

# Render the Streamlit interface
def render_budget_line_page():
    st.title("Budget Line Management")

    conn = initialize_db()

    # Step 1: Choose an existing task ID
    task_data = fetch_task_ids_and_names(conn)
    if task_data.empty:
        st.warning("No tasks found in the database. Please add tasks in the subtasks table first.")
        conn.close()
        return

    st.write("Available Tasks:")
    st.dataframe(task_data)

    task_ids = task_data["id"].tolist()
    selected_task_id = st.selectbox("Select a Task ID to create a budget line:", task_ids)

    # Fetch and display the selected task details
    selected_task = task_data[task_data["id"] == selected_task_id].iloc[0]
    st.write(f"**Selected Task:** {selected_task['name']} (ID: {selected_task_id})")
    st.write(f"**Current Budget:** {selected_task['budget']}")

    # Step 2: Create the budget line table if it doesn't exist
    create_budget_line_table(conn, selected_task_id)
    st.success(f"Budget line table for Task ID {selected_task_id} is ready.")

    # Step 3: Upload a CSV file for budget details
    st.subheader("Upload Budget Details")
    st.write("The CSV file should have the following columns:")
    st.write("`Item, Detail, Unit, Quantity, Unit Cost, Total Cost, Notes`")

    uploaded_file = st.file_uploader("Upload a CSV file with budget details:", type="csv")

    if uploaded_file is not None:
        # Read the uploaded CSV
        budget_data = pd.read_csv(uploaded_file)

        # Validate the uploaded data
        expected_columns = ["Item", "Detail", "Unit", "Quantity", "Unit Cost", "Total Cost", "Notes"]
        if not all(column in budget_data.columns for column in expected_columns):
            st.error(f"Invalid CSV format. Expected columns: {', '.join(expected_columns)}")
        else:
            st.write("Uploaded Budget Details:")
            st.dataframe(budget_data)

            # Insert the budget details into the budget line table
            if st.button("Save Budget Details"):
                insert_budget_lines(conn, selected_task_id, budget_data)
                update_main_budget(conn, selected_task_id)
                st.success(f"Budget details for Task ID {selected_task_id} saved successfully!")
                st.info("Main budget updated in the subtasks table.")

    # Close the database connection
    conn.close()


if __name__ == "__main__":
    render_budget_line_page()
