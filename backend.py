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
        tabs = st.tabs(["View", "Edit", "Subtasks"])

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

        # Subtasks Tab
        with tabs[2]:
            st.subheader("Subtasks")

            subtasks = []
            for i in range(1, 6):
                with st.expander(f"Subtask {i}"):
                    category = st.text_input(f"Category of Task {i}", key=f"cat_{i}")
                    aspect = st.text_input(f"Aspect of Task {i}", key=f"asp_{i}")
                    current_situation = st.text_area(f"Current Situation of Task {i}", key=f"cs_{i}")
                    name = st.text_input(f"Name of Task {i}", key=f"name_{i}")
                    detail = st.text_area(f"Detail of Task {i}", key=f"detail_{i}")
                    start_time = st.date_input(f"Start Time of Task {i}", key=f"start_{i}")
                    outcome = st.text_area(f"Outcome of Task {i}", key=f"outcome_{i}")
                    person_involved = st.text_input(f"Person Involved in Task {i}", key=f"person_{i}")
                    budget = st.number_input(f"Budget of Task {i}", key=f"budget_{i}", step=100.0)
                    deadline = st.date_input(f"Deadline of Task {i}", key=f"deadline_{i}")
                    progress = st.slider(f"Progress of Task {i} (%)", 0, 100, key=f"progress_{i}")

                    # Collecting subtask data
                    subtask = {
                        "Category": category,
                        "Aspect": aspect,
                        "CurrentSituation": current_situation,
                        "Name": name,
                        "Detail": detail,
                        "StartTime": start_time,
                        "Outcome": outcome,
                        "PersonInvolved": person_involved,
                        "Budget": budget,
                        "Deadline": deadline,
                        "Progress": progress,
                    }
                    subtasks.append(subtask)

            if st.button(f"Save Subtasks for {page_name}"):
                # Handle saving subtasks
                st.success(f"Subtasks for {page_name} saved successfully.")

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
