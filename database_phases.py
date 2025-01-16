import io
import csv
import sqlite3
import pandas as pd
import streamlit as st

def initialize_database(db_name: str = "subtasks.db"):
    """
    Initialize or connect to the SQLite database.
    """
    return sqlite3.connect(db_name)

def create_table_from_csv(conn: sqlite3.Connection, table_name: str, file_content: bytes, delimiter: str = None):
    """
    Create or replace a table in the SQLite database from uploaded file content.
    
    :param conn: SQLite connection object
    :param table_name: Name of the table to create
    :param file_content: The raw bytes of the uploaded file
    :param delimiter: Delimiter to use. If None, attempt auto-detection.
    """
    try:
        # Convert bytes to string for pandas
        s = file_content.decode("utf-8", errors="ignore")
        
        # If delimiter is None => Try auto-detect
        if delimiter is None:
            # Use Python's CSV Sniffer for basic detection
            sniffer = csv.Sniffer()
            # We need a sample to sniff
            sample_size = min(len(s), 2048)  # sniff up to 2KB
            sample = s[:sample_size]

            # If the file has a header row, this helps detect delim
            try:
                dialect = sniffer.sniff(sample, delimiters=[",", "\t", ";", "|"])
                delimiter = dialect.delimiter
            except:
                # Fallback if detection fails
                delimiter = ","

        # Now read the CSV with the chosen delimiter
        df = pd.read_csv(io.StringIO(s), sep=delimiter)

        # Write the DataFrame to the SQLite database as a new table
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        st.success(f"Table '{table_name}' successfully created (or replaced) in the database!")
        st.write(f"**Detected/Chosen Delimiter:** `{delimiter}`")
        st.write("**Preview of Imported Data:**")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"An error occurred: {e}")

def render_database_phases_page():
    """
    Render the 'Database Phases' page in Streamlit
    to import CSV/TXT/etc. into a new or replaced table in 'subtasks.db'.
    """
    st.title("Import into Database: Phases")
    st.write("Upload a file to create (or replace) a table in the database.")

    # Option to name the table (by default "phases")
    table_name = st.text_input("Name of the new table:", value="phases")

    # Choose delimiter
    delimiter_choice = st.selectbox(
        "Choose a delimiter or auto-detect:",
        ["Auto-detect", "Comma (,)", "Tab (\\t)", "Semicolon (;)", "Pipe (|)"]
    )
    # Map selection to actual delimiter or None
    delimiter_map = {
        "Auto-detect": None,
        "Comma (,)": ",",
        "Tab (\\t)": "\t",
        "Semicolon (;)": ";",
        "Pipe (|)": "|",
    }
    chosen_delimiter = delimiter_map[delimiter_choice]

    # File uploader
    file = st.file_uploader("Upload your CSV/TXT file", type=["csv", "txt", "tsv"])

    if file is not None:
        # Before importing, try to preview with the chosen delimiter
        # Convert the file to bytes
        file_content = file.read()

        try:
            # Attempt reading the file with the chosen delimiter (or auto-detect)
            # We'll parse it in a temporary DataFrame for preview
            s = file_content.decode("utf-8", errors="ignore")

            # If chosen_delimiter is None => auto-detect
            if chosen_delimiter is None:
                # Sniff
                sniffer = csv.Sniffer()
                sample_size = min(len(s), 2048)
                sample = s[:sample_size]
                try:
                    dialect = sniffer.sniff(sample, delimiters=[",", "\t", ";", "|"])
                    chosen_delimiter = dialect.delimiter
                except:
                    # fallback to comma
                    chosen_delimiter = ","

            df_preview = pd.read_csv(io.StringIO(s), sep=chosen_delimiter)
            st.write("**Preview of Uploaded File:**")
            st.dataframe(df_preview.head())
        except Exception as e:
            st.warning(f"Could not preview the file with the chosen method: {e}")
            st.write("You can still attempt the import below.")

        if st.button("Import to Database"):
            # Initialize the database connection
            conn = initialize_database()

            # Actually create the table
            create_table_from_csv(conn, table_name, file_content, delimiter=delimiter_map[delimiter_choice])

            # Close the database connection
            conn.close()

if __name__ == "__main__":
    render_database_phases_page()
