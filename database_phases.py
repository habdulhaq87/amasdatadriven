import sqlite3
import pandas as pd
import streamlit as st


def initialize_database(db_name: str = "subtasks.db"):
    """
    Initialize or connect to the SQLite database.
    """
    return sqlite3.connect(db_name)


def create_table_from_csv_or_txt(conn: sqlite3.Connection, table_name: str, file, delimiter="\t"):
    """
    Create a new table in the SQLite database from a CSV or TXT file.
    - conn: SQLite connection object
    - table_name: Name of the table to be created
    - file: Uploaded file via Streamlit file uploader
    - delimiter: The delimiter used in the file (default is tab '\t')
    """
    try:
        # Load the file into a pandas DataFrame
        df = pd.read_csv(file, delimiter=delimiter)

        # Write the DataFrame to the SQLite database as a new table
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        st.success(f"Table '{table_name}' successfully created in the database.")
    except Exception as e:
        st.error(f"An error occurred: {e}")


def render_database_phases_page():
    """
    Render the 'Database Phases' page in Streamlit for importing CSV or TXT to 'phases'.
    """
    st.title("Database Phases")
    st.write("Upload a CSV or TXT file to create a new table named 'phases' in the database.")

    # File uploader for CSV or TXT
    file = st.file_uploader("Upload CSV or TXT", type=["csv", "txt"])

    if file is not None:
        # Detect delimiter based on file extension
        delimiter = "\t" if file.name.endswith(".txt") else ","

        # Show preview of the uploaded file
        try:
            df = pd.read_csv(file, delimiter=delimiter)
            st.write("Preview of uploaded file:")
            st.dataframe(df)

            if st.button("Import to Database"):
                # Initialize the database connection
                conn = initialize_database()

                # Create the 'phases' table in the database
                create_table_from_csv_or_txt(conn, "phases", file, delimiter=delimiter)

                # Close the database connection
                conn.close()
        except Exception as e:
            st.error(f"Failed to read the file: {e}")


if __name__ == "__main__":
    render_database_phases_page()
