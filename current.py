import streamlit as st
import pandas as pd

def render_current_stage():
    st.title("Current Stage")
    st.write("""
    Below is an overview of the **current situation** for each category at Amas Hypermarket, 
    based on our observations and the data in `amas_data.csv`. 
    Expand each **Aspect** to see more details.
    """)

    # Load Data
    df = pd.read_csv("amas_data.csv", sep=",")  # Adjust the file path if needed

    # Group by category so each category is shown under a header
    categories = df["Category"].unique()
    for cat in categories:
        cat_data = df[df["Category"] == cat]
        st.subheader(cat)  # Show category name
        # Create an expander for each aspect
        for idx, row in cat_data.iterrows():
            with st.expander(f"**Aspect:** {row['Aspect']}"):
                st.write(f"**Current Situation:**\n{row['CurrentSituation']}")
