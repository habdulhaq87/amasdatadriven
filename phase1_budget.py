import streamlit as st
import sqlite3
import pandas as pd


def fetch_budget_table_names(conn):
    """Fetch all table names in the database that match the 'budget_{id}' pattern."""
    query = """
    SELECT name
    FROM sqlite_master
    WHERE type='table' AND name LIKE 'budget_%';
    """
    return [row[0] for row in conn.execute(query).fetchall()]


def fetch_budget_data(conn, table_name):
    """Fetch data from a specific budget table."""
    query = f"SELECT * FROM {table_name};"
    return pd.read_sql_query(query, conn)


def calculate_total_budget(conn, table_name):
    """Calculate the total budget for a specific table."""
    query = f"SELECT SUM(total_cost) AS total_budget FROM {table_name};"
    result = conn.execute(query).fetchone()
    return result[0] if result and result[0] else 0.0


def fetch_task_names(conn):
    """Fetch the ID and name of tasks from the 'subtasks' table."""
    query = "SELECT id, name FROM subtasks;"
    return pd.read_sql_query(query, conn)


def render_budget_tab():
    """Render the Budget tab, showing all budget tables with detailed views."""
    st.subheader("Phase 1 Budgets")

    conn = sqlite3.connect("subtasks.db")
    budget_tables = fetch_budget_table_names(conn)

    if not budget_tables:
        st.warning("No budget tables found in the database.")
        conn.close()
        return

    # Fetch task names to map IDs to names
    task_names_df = fetch_task_names(conn)
    task_names_dict = dict(zip(task_names_df["id"], task_names_df["name"]))

    # Summary Section
    st.markdown("### Summary of Phase 1 Budgets")
    summary_data = []

    for table in budget_tables:
        task_id = int(table.split("_")[1])  # Extract the ID from the table name
        task_name = task_names_dict.get(task_id, "Unknown Task")  # Map ID to name
        total_budget = calculate_total_budget(conn, table)
        summary_data.append({"Task ID": task_id, "Task Name": task_name, "Total Cost": total_budget})

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df.style.format({"Total Cost": "{:.1f}"}))

    # Display all available budget tables in an interactive UI
    st.markdown("### View Detailed Budgets")
    for table in budget_tables:
        task_id = int(table.split("_")[1])  # Extract the ID from the table name
        task_name = task_names_dict.get(task_id, "Unknown Task")  # Map ID to name
        total_budget = calculate_total_budget(conn, table)

        with st.expander(f"Task ID {task_id}: {task_name} (Total Cost: {total_budget:.1f})"):
            budget_data = fetch_budget_data(conn, table)
            if budget_data.empty:
                st.warning(f"No data found in {table}.")
            else:
                st.dataframe(
                    budget_data.style.format({
                        "Quantity": "{:.1f}",
                        "Unit Cost": "{:.1f}",
                        "Total Cost": "{:.1f}",
                    })
                )

    # Close the connection
    conn.close()
