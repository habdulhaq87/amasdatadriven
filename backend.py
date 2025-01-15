import base64
import datetime
import io
import json
import requests
import streamlit as st
import pandas as pd

# Function to fetch file SHA and content from GitHub
def get_file_sha_and_content(
    github_user: str,
    github_repo: str,
    github_pat: str,
    file_path: str,
) -> (str, pd.DataFrame):
    url = f"https://api.github.com/repos/{github_user}/{github_repo}/contents/{file_path}"
    headers = {"Authorization": f"Bearer {github_pat}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        sha = data["sha"]
        content_str = base64.b64decode(data["content"]).decode("utf-8")
        csv_buffer = io.StringIO(content_str)
        df = pd.read_csv(csv_buffer, sep=",")
        return sha, df
    else:
        st.error(f"Failed to fetch {file_path} from GitHub: {response.status_code}")
        st.stop()

# Function to render each page
def render_page(df, page_name):
    if page_name == "Home":
        st.title("Home Page")
        st.write("Welcome to the AMAS Data Management System!")
        st.dataframe(df)
    else:
        st.title(f"Details for: {page_name}")
        tabs = st.tabs(["View", "Edit"])

        # Filter row data for the selected Aspect
        row_data = df[df["Aspect"] == page_name].iloc[0]

        # View Tab
        with tabs[0]:
            st.subheader("View Data")
            for col, value in row_data.items():
                st.write(f"**{col}**: {value}")

        # Edit Tab
        with tabs[1]:
            st.subheader("Edit Data")
            editable_data = {}
            for col, value in row_data.items():
                editable_data[col] = st.text_input(f"Edit {col}", str(value))

            if st.button(f"Save Changes for {page_name}"):
                # Update the DataFrame with the edited data
                df.update(pd.DataFrame([editable_data]))
                st.success("Changes saved. Be sure to commit changes to GitHub.")

# Main function
def render_backend():
    st.set_page_config(page_title="AMAS Data Management", layout="wide")

    # Sidebar for page navigation
    st.sidebar.title("Navigation")
    github_user = "habdulhaq87"
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]  
    file_path = "amas_data.csv"

    sha, df = get_file_sha_and_content(github_user, github_repo, github_pat, file_path)

    # Dynamically populate the sidebar
    pages = ["Home"] + df["Aspect"].dropna().unique().tolist()

    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    # Create buttons for navigation
    for page in pages:
        if st.sidebar.button(page):
            st.session_state.current_page = page

    # Render the currently selected page
    render_page(df, st.session_state.current_page)

if __name__ == "__main__":
    render_backend()
