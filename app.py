import streamlit as st
import home
import current
import vision
import phase1
import phase2
import finance  # make sure finance.py is alongside this file

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

    pages = [
        "Home",
        "Current Stage",
        "Vision",
        "Phase 1",
        "Phase 2",
        "Finance",
    ]

    # keep selection stable across reruns
    default_index = pages.index(st.session_state.get("active_page", "Home"))
    active_page = st.sidebar.radio("Go to", pages, index=default_index, label_visibility="collapsed")
    st.session_state.active_page = active_page

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
        # Prefer a function if provided
        if hasattr(finance, "render_finance") and callable(finance.render_finance):
            finance.render_finance()
        else:
            # If finance.py renders at import-time, just show a tiny note
            st.caption("Finance module loaded. If nothing appears, add a `render_finance()` function in finance.py.")

if __name__ == "__main__":
    main()
