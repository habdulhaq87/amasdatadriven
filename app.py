import streamlit as st
import vision
import current  # Import the Current Stage module
import home
import phase1

def main():
    st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

    # --- Sidebar: Logo & Navigation ---
    st.sidebar.image("input/logo.jpg", use_container_width=True)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("### AMAS's Data-Driven Strategy for 2025")  # Added header to sidebar

    # Remove references to Phase 2 and Phase 3
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
