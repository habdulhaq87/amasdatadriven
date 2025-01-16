import sqlite3
import pandas as pd
import streamlit as st


def initialize_database(db_name: str = "subtasks.db"):
    """
    Initialize or connect to the SQLite database.
    """
    return sqlite3.connect(db_name)


def create_table_from_csv(conn: sqlite3.Connection, table_name: str, csv_file):
    """
    Create a new table in the SQLite database from a CSV file.
    - conn: SQLite connection object
    - table_name: Name of the table to be created
    - csv_file: CSV file uploaded via Streamlit file uploader
    """
    try:
        # Load the CSV into a pandas DataFrame
        df = pd.read_csv(csv_file)

        # Write the DataFrame to the SQLite database as a new table
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        st.success(f"Table '{table_name}' successfully created in the database.")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def render_database_phases_page():
    """
    Render the 'Database Phases' page in Streamlit for importing CSV to 'phases'.
    """
    st.title("Database Phases")
    st.write("Upload a CSV file to create a new table named 'phases' in the database.")

    # File uploader for CSV
    csv_file = st.file_uploader("Upload CSV", type=["csv"])

    if csv_file is not None:
        # Show preview of the uploaded file
        st.write("Preview of uploaded CSV:")
        df = pd.read_csv(csv_file)
        st.dataframe(df)

        if st.button("Import to Database"):
            # Initialize the database connection
            conn = initialize_database()

            # Create the 'phases' table in the database
            create_table_from_csv(conn, "phases", csv_file)

            # Close the database connection
            conn.close()


if __name__ == "__main__":
    render_database_phases_page()
