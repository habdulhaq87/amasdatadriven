import streamlit as st
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

    # --- Main Content ---
    if active_page == "Home":
        # Call the render_home function to display the home page content
        home.render_home()

    elif active_page == "Current Stage":
        # Display the Current Stage page
        current.render_current_stage()

    elif active_page == "Vision":
        # Display the Vision page
        vision.render_vision()

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
