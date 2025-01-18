import streamlit as st
import vision
import current
import home
import phase1
import report

def main():
    # Ensure set_page_config is the first Streamlit call
    st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

    # Access Code Authentication
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

    st.sidebar.image("input/logo.jpg", use_container_width=True)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("### AMAS's Data-Driven Strategy for 2025")

    pages = {
        "Home": home.render_home,
        "Current Stage": current.render_current_stage,
        "Vision": vision.render_vision,
        "Phase 1": phase1.render_phase1,
        "Report": report.render_report,
    }

    active_page = "Home"
    for page_name, render_func in pages.items():
        if st.sidebar.button(page_name):
            active_page = page_name

    pages[active_page]()

if __name__ == "__main__":
    main()
