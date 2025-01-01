import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

    # --- Sidebar Navigation ---
    menu_items = [
        "Home", 
        "Current Stage", 
        "Vision", 
        "Phase 1", 
        "Phase 2", 
        "Phase 3", 
        "Roadmap"
    ]
    choice = st.sidebar.selectbox("Navigation", menu_items)

    # --- Load Data ---
    # Make sure amas_data.csv is in the same directory or adjust the path accordingly
    df = pd.read_csv("amas_data.csv", sep=",")  # or just pd.read_csv("amas_data.csv") if comma is default

    # --- Main Content ---
    if choice == "Home":
        st.title("Amas Hypermarket: Data-Driven Strategy App")
        st.write("""
        **Welcome to the Amas Hypermarket Data-Driven Strategy App!**

        This application outlines the current challenges and the roadmap for transforming Amas 
        Hypermarket into a fully data-driven retail operation. Use the sidebar to navigate 
        through various sections, where you'll find insights into the current situation, 
        a future vision, and the phased implementation plan (Phase 1, Phase 2, and Phase 3), 
        culminating in a roadmap for successful adoption.
        """)
        st.write("Below is a quick look at the data stored in `amas_data.csv` (for reference):")
        st.dataframe(df)

    elif choice == "Current Stage":
        st.title("Current Stage")
        st.write("""
        Below is an overview of the **current situation** for each category at Amas Hypermarket, 
        based on our observations and the data in `amas_data.csv`. 
        Expand each **Aspect** to see more details.
        """)

        # Optional: Search bar for aspects, categories, or current situation text
        search_query = st.text_input("Search aspects, categories, or keywords in the current situation:", "")
        if search_query:
            # Filter rows if they contain the search query (case-insensitive)
            filtered_df = df[
                df["Category"].str.contains(search_query, case=False) |
                df["Aspect"].str.contains(search_query, case=False) |
                df["CurrentSituation"].str.contains(search_query, case=False)
            ]
        else:
            filtered_df = df

        # Group by category so each category is shown under a header
        categories = filtered_df["Category"].unique()
        for cat in categories:
            cat_data = filtered_df[filtered_df["Category"] == cat]
            st.subheader(cat)  # Show category name
            # Create an expander for each aspect
            for idx, row in cat_data.iterrows():
                with st.expander(f"**Aspect:** {row['Aspect']}"):
                    st.write(f"**Current Situation:**\n{row['CurrentSituation']}")

    elif choice == "Vision":
        st.title("Vision")
        st.write("**Placeholder**: Present the ultimate data-driven vision for Amas Hypermarket here.")

    elif choice == "Phase 1":
        st.title("Phase 1")
        st.write("**Placeholder**: Outline Early & Doable steps here.")

    elif choice == "Phase 2":
        st.title("Phase 2")
        st.write("**Placeholder**: Describe Extended Digitization & Standardization steps here.")

    elif choice == "Phase 3":
        st.title("Phase 3")
        st.write("**Placeholder**: Advanced Analytics & Automation phase details here.")

    elif choice == "Roadmap":
        st.title("Roadmap")
        st.write("**Placeholder**: Provide a timeline and milestones for Phases 1–3 here.")

if __name__ == "__main__":
    main()
