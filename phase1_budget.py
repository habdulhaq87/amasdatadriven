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


def render_budget_tab():
    """Render the Budget tab, consolidating budget tables and providing a summary."""
    st.subheader("Phase 1 Budgets")

    conn = sqlite3.connect("subtasks.db")
    budget_tables = fetch_budget_table_names(conn)

    if not budget_tables:
        st.warning("No budget tables found in the database.")
        conn.close()
        return

    # Summary Section
    st.markdown("### Summary of Phase 1 Budgets")
    summary_data = []

    for table in budget_tables:
        total_budget = calculate_total_budget(conn, table)
        summary_data.append({"Budget Table": table, "Total Cost": total_budget})

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df.style.format({"Total Cost": "{:.2f}"}))

    st.write("Below are the available budgets for Phase 1 tasks:")

    # Allow the user to select a specific budget table
    selected_table = st.selectbox("Select a budget table to view:", budget_tables)

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
