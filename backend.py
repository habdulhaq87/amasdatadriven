import streamlit as st
import pandas as pd

def render_backend():
    st.title("Database Editor: AMAS Data Management")

    st.write("""
    **Welcome to the AMAS Data Editor!**  
    Here, you can **view, modify, and save** changes to your `amas_data.csv` file.  
    **Instructions**:
    1. Make any changes directly in the interactive table below.
    2. Click **"Save Changes"** to write all modifications back to the CSV.
    3. Use caution—saved changes cannot be undone from within this tool.
    """)

    # Load the existing CSV data
    try:
        df = pd.read_csv("amas_data.csv")
    except FileNotFoundError:
        st.error("`amas_data.csv` not found. Please ensure it exists in the app directory.")
        return

    # Display editable data editor
    st.subheader("Editable Data")
    st.info("You can double-click cells to edit them. Scroll horizontally for additional fields.")

    edited_df = st.experimental_data_editor(
        df, 
        num_rows="dynamic",  # allows adding new rows
        use_container_width=True
    )

    st.write("---")

    # Save button
    if st.button("Save Changes"):
        # Write the updated dataframe to CSV
        edited_df.to_csv("amas_data.csv", index=False)
        st.success("Your changes have been saved to `amas_data.csv`!")

def main():
    st.set_page_config(page_title="AMAS Database Editor", layout="wide")
    render_backend()

if __name__ == "__main__":
    main()
