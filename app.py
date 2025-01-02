import streamlit as st
import pandas as pd
import vision
import current  # Import the Current Stage module
import home

def main():
    st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

    # --- Sidebar Buttons for Navigation ---
    st.sidebar.title("Navigation")
    pages = {
        "Home": "Home",
        "Current Stage": "Current Stage",
        "Vision": "Vision",
        "Phase 1": "Phase 1",
        "Phase 2": "Phase 2",
        "Phase 3": "Phase 3",
        "Roadmap": "Roadmap",
    }

    # Create buttons in the sidebar and update the active page
    active_page = "Home"  # Default page
    for page_name in pages.keys():
        if st.sidebar.button(page_name):
            active_page = page_name
    if active_page == "Home":
        home.render_home()
    # --- Main Content ---
    if active_page == "Home":
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
        df = pd.read_csv("amas_data.csv", sep=",")
        st.dataframe(df)

    elif active_page == "Current Stage":
        current.render_current_stage()  # Call the Current Stage function from current.py

    elif active_page == "Vision":
        vision.render_vision()  # Call the Vision function from vision.py

    elif active_page == "Phase 1":
        st.title("Phase 1")
        st.write("**Placeholder**: Outline Early & Doable steps here.")

    elif active_page == "Phase 2":
        st.title("Phase 2")
        st.write("**Placeholder**: Describe Extended Digitization & Standardization steps here.")

    elif active_page == "Phase 3":
        st.title("Phase 3")
        st.write("**Placeholder**: Advanced Analytics & Automation phase details here.")

    elif active_page == "Roadmap":
        st.title("Roadmap")
        st.write("**Placeholder**: Provide a timeline and milestones for Phases 1–3 here.")

if __name__ == "__main__":
    main()
