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
    ACCESS_CODE = "2025"

    # Use session state to track if the user is authenticated
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # If not authenticated, show the access code input
    if not st.session_state.authenticated:
        st.sidebar.markdown("## Enter Access Code")
        user_code = st.sidebar.text_input("Access Code", type="password")

        if user_code == ACCESS_CODE:
            st.session_state.authenticated = True  # Set authenticated to True
            st.sidebar.success("Access granted!")
        else:
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
    }

    # Create buttons in the sidebar and update the active page
    active_page = "Home"  # Default page
    for page_name in pages.keys():
        if st.sidebar.button(page_name):
            active_page = page_name

    # --- Quick Links Section ---
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown("<h4>Quick Links</h4>", unsafe_allow_html=True)

    # Report button
    if st.sidebar.button("Report", key="report_link"):
        st.sidebar.markdown(
            '<a href="https://amasreport.streamlit.app/" target="_blank" '
            'style="display: block; text-align: center; background-color: #e0e0e0; padding: 10px; border-radius: 5px; color: black; text-decoration: none;">Go to Report</a>',
            unsafe_allow_html=True,
        )

    # Database button
    if st.sidebar.button("Database", key="db_link"):
        st.sidebar.markdown(
            '<a href="https://amasbackend.streamlit.app/" target="_blank" '
            'style="display: block; text-align: center; background-color: #d3d3d3; padding: 10px; border-radius: 5px; color: black; text-decoration: none;">Go to Database</a>',
            unsafe_allow_html=True,
        )

    # Budget button
    if st.sidebar.button("Budget", key="budget_link"):
        st.sidebar.markdown(
            '<a href="https://budgetapp.streamlit.app/" target="_blank" '
            'style="display: block; text-align: center; background-color: #b0b0b0; padding: 10px; border-radius: 5px; color: black; text-decoration: none;">Go to Budget</a>',
            unsafe_allow_html=True,
        )

    # --- Main Content ---
    if active_page == "Home":
        home.render_home()

    elif active_page == "Current Stage":
        current.render_current_stage()

    elif active_page == "Vision":
        vision.render_vision()

    elif active_page == "Phase 1":
        phase1.render_phase1()

if __name__ == "__main__":
    main()
