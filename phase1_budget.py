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


def fetch_task_names_and_ids(conn):
    """Fetch task names and IDs from the subtasks table."""
    query = """
    SELECT id, name
    FROM subtasks;
    """
    return pd.read_sql_query(query, conn)


def render_budget_tab():
    """Render the Budget tab, consolidating budget tables and providing a summary."""
    st.subheader("Phase 1 Budgets")

    conn = sqlite3.connect("subtasks.db")
    budget_tables = fetch_budget_table_names(conn)

    if not budget_tables:
        st.warning("No budget tables found in the database.")
        conn.close()
        return

    # Fetch task names and IDs from the subtasks table
    task_data = fetch_task_names_and_ids(conn)
    task_data["Budget Table"] = task_data["id"].apply(lambda x: f"budget_{x}")

    # Summary Section
    st.markdown("### Summary of Phase 1 Budgets")
    summary_data = []

    for table in budget_tables:
        total_budget = calculate_total_budget(conn, table)

        # Map budget table to its corresponding task name
        task_name = task_data.loc[task_data["Budget Table"] == table, "name"].values
        task_name = task_name[0] if len(task_name) > 0 else "Unknown Task"

        summary_data.append({"Name": task_name, "Total Cost": total_budget})

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df.style.format({"Total Cost": "{:.2f}"}))

    st.write("Below are the available budgets for Phase 1 tasks:")

    # Ensure session state is initialized for selected table
    if "selected_table" not in st.session_state:
        st.session_state.selected_table = None

    # Dropdown to select a budget table
    selected_table = st.selectbox(
        "Select a budget table to view:",
        [table for table in budget_tables if table in task_data["Budget Table"].values],
        format_func=lambda x: task_data.loc[
            task_data["Budget Table"] == x, "name"
        ].values[0],
        key="selected_table",
    )

    if selected_table:
        # Fetch and display the data from the selected budget table
        budget_data = fetch_budget_data(conn, selected_table)

        if budget_data.empty:
            st.warning(f"No data found in {selected_table}.")
        else:
            st.write(f"**Details for {selected_table}:**")
            st.dataframe(
                budget_data.style.format({
                    "Quantity": "{:.2f}",
                    "Unit Cost": "{:.2f}",
                    "Total Cost": "{:.2f}",
                })
            )

    # Close the connection
    conn.close()
