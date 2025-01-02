import streamlit as st
import vision
import current  # Import the Current Stage module
import home
import phase1
import phase2
import phase3
import roadmap

def main():
    st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

    # --- Sidebar: Logo & Navigation ---
    st.sidebar.image("input/logo.jpg", use_container_width=True)  # Logo in the sidebar
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

    # --- Main Content: Centered Cover Image & Page Logic ---
    # Display a centered cover image
    st.markdown(
        """
        <style>
            .centered-image {
                display: flex;
                justify-content: center;
            }
        </style>
        <div class="centered-image">
            <img src="input/cover.jpg" alt="Cover Image" style="width: 60%; max-width: 800px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    if active_page == "Home":
        home.render_home()

    elif active_page == "Current Stage":
        current.render_current_stage()

    elif active_page == "Vision":
        vision.render_vision()

    elif active_page == "Phase 1":
        phase1.render_phase1()

    elif active_page == "Phase 2":
        phase2.render_phase2()

    elif active_page == "Phase 3":
        phase3.render_phase3()

    elif active_page == "Roadmap":
        roadmap.render_roadmap()

if __name__ == "__main__":
    main()
