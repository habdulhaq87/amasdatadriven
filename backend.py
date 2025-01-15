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

# Function to update the file in GitHub
def update_file_in_github(
    github_user: str,
    github_repo: str,
    github_pat: str,
    file_path: str,
    new_df: pd.DataFrame,
    old_sha: str,
    commit_message: str = "Update CSV via Streamlit",
):
    url = f"https://api.github.com/repos/{github_user}/{github_repo}/contents/{file_path}"
    headers = {"Authorization": f"Bearer {github_pat}"}

    csv_str = new_df.to_csv(index=False)
    b64_content = base64.b64encode(csv_str.encode("utf-8")).decode("utf-8")

    payload = {
        "message": commit_message,
        "content": b64_content,
        "sha": old_sha,
    }

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code in [200, 201]:
        st.success("Your changes have been committed to GitHub!")
    else:
        st.error(f"Failed to update {file_path}: {response.status_code}\n{response.text}")

# Function to render each page
def render_page(df, page_name):
    if page_name == "Home":
        st.title("Home Page")
        st.write("Welcome to the AMAS Data Management System!")
        st.dataframe(df)
    else:
        row_index = int(page_name.split(" ")[-1]) - 1
        row_data = df.iloc[row_index]

        st.title(f"Details for Row {row_index + 1}")
        for col, value in row_data.items():
            st.write(f"**{col}**: {value}")

        # Add edit functionality here if required

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
    pages = ["Home"] + [f"Row {i + 1}" for i in range(len(df))]
    selected_page = st.sidebar.radio("Select Page:", pages)

    render_page(df, selected_page)

if __name__ == "__main__":
    render_backend()
