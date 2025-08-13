import streamlit as st
import importlib

import home
import current
import vision
import phase1
import phase2

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

    # Note: radio is more reliable than multiple buttons for navigation state
    pages = [
        "Home",
        "Current Stage",
        "Vision",
        "Phase 1",
        "Phase 2",
        "Finance",
        "Transaction Entry",
    ]
    active_page = st.sidebar.radio("Go to", pages, index=0)

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
        # Lazy import to avoid startup errors / circular imports
        try:
            finance = importlib.import_module("finance")
            # Call a render function if it exists; otherwise assume module renders on import
            if hasattr(finance, "render_finance"):
                finance.render_finance()
        except ModuleNotFoundError as e:
            st.error(f"Finance module not found: {e}")
    elif active_page == "Transaction Entry":
        try:
            tx = importlib.import_module("transaction_entry")  # or "Transaction_Entry" if that's your filename
            if hasattr(tx, "render_transaction_entry"):
                tx.render_transaction_entry()
        except ModuleNotFoundError as e:
            st.error(f"Transaction Entry module not found: {e}")

if __name__ == "__main__":
    main()
