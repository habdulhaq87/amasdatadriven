import streamlit as st
import importlib

# ----------------------------------------------------
# Page setup (call set_page_config before any output)
# ----------------------------------------------------
st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

# Core pages (eager imports are fine)
import home
import current
import vision
import phase1
import phase2


def lazy_import(*module_names: str):
    """Try importing modules in order; return the first that exists, else None."""
    for name in module_names:
        try:
            return importlib.import_module(name)
        except ModuleNotFoundError:
            continue
    return None


def main():
    st.title("Amas Data-Driven Strategy")

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
            if user_code:  # only show error if they've typed something
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
        mod = lazy_import("finance")
        if mod is None:
            st.error("Finance module not found. Make sure `finance.py` is in the app folder.")
        else:
            if hasattr(mod, "render_finance"):
                mod.render_finance()
            # else: assume the module renders on import (no-op here)

    elif active_page == "Transaction Entry":
        mod = lazy_import("transaction_entry", "Transaction_Entry")
        if mod is None:
            st.error(
                "Transaction Entry module not found. "
                "Add `transaction_entry.py` (or `Transaction_Entry.py`) to your app folder."
            )
        else:
            if hasattr(mod, "render_transaction_entry"):
                mod.render_transaction_entry()
            # else: assume the module renders on import (no-op here)


if __name__ == "__main__":
    main()
