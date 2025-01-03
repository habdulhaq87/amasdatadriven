import streamlit as st
import pandas as pd

def render_backend():
    st.title("Database Editor: AMAS Data Management")

    st.write("""
    **Welcome to the AMAS Data Editor!**  
    Here, you can **view, modify, and save** changes to your `amas_data.csv` file.  
    **Instructions**:
    1. Make changes to the table below using the provided fields.
    2. Click **"Save Changes"** to write all modifications back to the CSV.
    3. Use caution—saved changes cannot be undone from within this tool.
    """)

    # Load the existing CSV data
    try:
        df = pd.read_csv("amas_data.csv")
    except FileNotFoundError:
        st.error("`amas_data.csv` not found. Please ensure it exists in the app directory.")
        return

    # Display current dataset
    st.subheader("Current Dataset")
    st.dataframe(df, use_container_width=True)

    # Editable section for rows
    st.write("---")
    st.subheader("Edit Data")
    editable_rows = []
    for i, row in df.iterrows():
        with st.expander(f"Edit Row {i + 1}: {row['Aspect']}"):
            updated_row = {
                "Category": st.text_input(f"Category (Row {i + 1})", row["Category"]),
                "Aspect": st.text_input(f"Aspect (Row {i + 1})", row["Aspect"]),
                "CurrentSituation": st.text_area(f"Current Situation (Row {i + 1})", row["CurrentSituation"]),
                "Phase1": st.text_area(f"Phase 1 (Row {i + 1})", row["Phase1"]),
                "Phase1_Person in Charge": st.text_input(f"Person in Charge (Row {i + 1})", row["Phase1_Person in Charge"]),
                "Phase1_Deliverable": st.text_input(f"Deliverable (Row {i + 1})", row["Phase1_Deliverable"]),
                "Phase1_Start Date": st.date_input(f"Start Date (Row {i + 1})", pd.to_datetime(row["Phase1_Start Date"], errors="coerce")),
                "Phase1_End Date": st.date_input(f"End Date (Row {i + 1})", pd.to_datetime(row["Phase1_End Date"], errors="coerce")),
                "Phase1_Budget": st.number_input(f"Budget (Row {i + 1})", value=float(row["Phase1_Budget"]) if pd.notnull(row["Phase1_Budget"]) else 0.0),
                "Phase1_Charter": st.text_area(f"Charter (Row {i + 1})", row["Phase1_Charter"]),
            }
            editable_rows.append(updated_row)

    # Save changes
    if st.button("Save Changes"):
        updated_df = pd.DataFrame(editable_rows)
        updated_df.to_csv("amas_data.csv", index=False)
        st.success("Your changes have been saved to `amas_data.csv`!")

def main():
    st.set_page_config(page_title="AMAS Database Editor", layout="wide")
    render_backend()

if __name__ == "__main__":
    main()
