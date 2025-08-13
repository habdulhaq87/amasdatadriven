# app.py
import streamlit as st
import home
import current
import vision
import phase1
import phase2
import finance  # must expose render_finance()

# ----------------------------------------------------
# Page config
# ----------------------------------------------------
st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

# ----------------------------------------------------
# Auth (simple access code)
# ----------------------------------------------------
ACCESS_CODE = "2025"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.sidebar.image("input/logo.jpg", use_container_width=True)
    st.sidebar.title("Navigation")
    st.sidebar.markdown("### AMAS's Data-Driven Strategy for 2025")

    with st.sidebar.form("auth_form", clear_on_submit=False):
        code = st.text_input("Enter Access Code", type="password")
        submitted = st.form_submit_button("Unlock")
    if submitted:
        if code == ACCESS_CODE:
            st.session_state.authenticated = True
            st.sidebar.success("Access granted!")
        else:
            st.sidebar.error("Invalid access code.")
            st.stop()
    else:
        st.stop()

# ----------------------------------------------------
# Sidebar navigation (persistent)
# ----------------------------------------------------
st.sidebar.image("input/logo.jpg", use_container_width=True)
st.sidebar.title("Navigation")
st.sidebar.markdown("### AMAS's Data-Driven Strategy for 2025")

PAGES = {
    "Home": "Home",
    "Current Stage": "Current Stage",
    "Vision": "Vision",
    "Phase 1": "Phase 1",
    "Phase 2": "Phase 2",
    "Finance": "Finance",
}

# Persist selected page across reruns
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

selected = st.sidebar.radio(
    "Go to",
    list(PAGES.keys()),
    index=list(PAGES.keys()).index(st.session_state.active_page),
)

st.session_state.active_page = selected

# ----------------------------------------------------
# Main content router
# ----------------------------------------------------
page = st.session_state.active_page

if page == "Home":
    home.render_home()
elif page == "Current Stage":
    current.render_current_stage()
elif page == "Vision":
    vision.render_vision()
elif page == "Phase 1":
    phase1.render_phase1()
elif page == "Phase 2":
    phase2.render_phase2()
elif page == "Finance":
    finance.render_finance()
