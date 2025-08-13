import streamlit as st
import vision
import current
import home
import phase1
import phase2
import finance  # must have render_finance()

def main():
    st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

    # --- Access Code Authentication ---
    ACCESS_CODE = "2025"
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.sidebar.markdown("## Enter Access Code")
        user_code = st.sidebar.text_input("Access Code", type="password")
        if user_code == ACCESS_CODE:
            st.session_state.authenticated = True
            st.sidebar.success("Access granted!")
        else:
            st.sidebar.error("Invalid access code. Please try again.")
            st.stop()

    # --- Sidebar: Logo & Navigation ---
    st.sidebar.image("input/logo.jpg", use_container_width=True)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("### AMAS's Data-Driven Strategy for 2025")

    pages = {
        "Home": "Home",
        "Current Stage": "Current Stage",
        "Vision": "Vision",
        "Phase 1": "Phase 1",
        "Phase 2": "Phase 2",
        "Finance": "Finance",
    }

    active_page = "Home"
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
    elif active_page == "Phase 2":
        phase2.render_phase2()
    elif active_page == "Finance":
        # Call the finance page renderer
        finance.render_finance()

if __name__ == "__main__":
    main()
