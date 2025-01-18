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


def render_budget_tab():
    """Render the Budget tab, consolidating budget tables."""
    st.subheader("Phase 1 Budgets")

    conn = sqlite3.connect("subtasks.db")
    budget_tables = fetch_budget_table_names(conn)

    if not budget_tables:
        st.warning("No budget tables found in the database.")
        conn.close()
        return

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
            st.dataframe(budget_data)

    # Close the connection
    conn.close()
