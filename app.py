import streamlit as st
import vision
import current  # Import the Current Stage module
import home
import phase1
import report  # Import the temporary Report module

def main():
    st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

    # --- Access Code Authentication ---
    # Define the access code
    ACCESS_CODE = "2505"

    # Create an input box for the user to enter the access code
    st.sidebar.markdown("## Enter Access Code")
    user_code = st.sidebar.text_input("Access Code", type="password")

    # Check if the access code is correct
    if user_code != ACCESS_CODE:
        st.sidebar.error("Invalid access code. Please try again.")
        st.stop()  # Stop the app if the code is incorrect

    # --- Sidebar: Logo & Navigation ---
    st.sidebar.image("input/logo.jpg", use_container_width=True)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("### AMAS's Data-Driven Strategy for 2025")  # Added header to sidebar

    # Updated pages to include "Report"
    pages = {
        "Home": "Home",
        "Current Stage": "Current Stage",
        "Vision": "Vision",
        "Phase 1": "Phase 1",
        "Report": "Report",  # New entry
    }

    # Create buttons in the sidebar and update the active page
    active_page = "Home"  # Default page
    for page_name in pages.keys():
        if st.sidebar.button(page_name):
            active_page = page_name

    # --- Main Content ---
    if active_page == "Home":
        home.render_home()

    elif active_page == "Current Stage":
        current.render_current_stage()

    elif active_page == "Vision":
        vision.render_vision()

    elif active_page == "Phase 1":
        phase1.render_phase1()

    elif active_page == "Report":
        report.render_report()  # Call the report module

if __name__ == "__main__":
    main()
