import base64
import datetime
import io
import json
import requests
import streamlit as st
import pandas as pd

def get_file_sha_and_content(github_user, github_repo, github_pat, file_path):
    """Retrieve the SHA and content of a file (CSV) in GitHub via REST API."""
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

def update_file_in_github(github_user, github_repo, github_pat, file_path, new_df, old_sha, commit_message):
    """Commit changes back to GitHub."""
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

def view_data(df):
    """View dataset."""
    st.title("View Data")
    st.dataframe(df, use_container_width=True)

def edit_data(df):
    """Edit dataset."""
    st.title("Edit Data")
    today = datetime.date.today()
    editable_rows = []

    for i, row in df.iterrows():
        st.subheader(f"Edit Row {i + 1}: {row.get('Aspect', 'N/A')}")
        start_date_val = pd.to_datetime(row.get("Phase1_Start Date", ""), errors="coerce").date()
        if pd.isna(start_date_val):
            start_date_val = today

        end_date_val = pd.to_datetime(row.get("Phase1_End Date", ""), errors="coerce").date()
        if pd.isna(end_date_val):
            end_date_val = today

        budget_val = float(row.get("Phase1_Budget", 0.0))

        updated_row = {
            "Category": st.text_input(f"Category (Row {i + 1})", row.get("Category", "")),
            "Aspect": st.text_input(f"Aspect (Row {i + 1})", row.get("Aspect", "")),
            "CurrentSituation": st.text_area(f"Current Situation (Row {i + 1})", row.get("CurrentSituation", "")),
            "Phase1": st.text_area(f"Phase 1 (Row {i + 1})", row.get("Phase1", "")),
            "Phase1_Person in Charge": st.text_input(f"Person in Charge (Row {i + 1})", row.get("Phase1_Person in Charge", "")),
            "Phase1_Deliverable": st.text_input(f"Deliverable (Row {i + 1})", row.get("Phase1_Deliverable", "")),
            "Phase1_Start Date": st.date_input(f"Start Date (Row {i + 1})", start_date_val),
            "Phase1_End Date": st.date_input(f"End Date (Row {i + 1})", end_date_val),
            "Phase1_Budget": st.number_input(f"Budget (Row {i + 1})", value=budget_val, step=100.0),
            "Phase1_Charter": st.text_area(f"Charter (Row {i + 1})", row.get("Phase1_Charter", "")),
        }
        editable_rows.append(updated_row)

    if st.button("Save Changes"):
        updated_df = pd.DataFrame(editable_rows)
        return updated_df
    return df

# Main function for sidebar navigation
def render_backend():
    st.set_page_config(page_title="AMAS Data Management", layout="wide")

    github_user = "habdulhaq87"
    github_repo = "amasdatadriven"
    github_pat = st.secrets["github"]["pat"]
    file_path = "amas_data.csv"

    sha, df = get_file_sha_and_content(github_user, github_repo, github_pat, file_path)

    # Sidebar navigation
    page = st.sidebar.radio("Navigation", ["View Data", "Edit Data"])
    
    if page == "View Data":
        view_data(df)
    elif page == "Edit Data":
        updated_df = edit_data(df)
        if not updated_df.equals(df):
            commit_msg = f"Update CSV via Streamlit at {datetime.datetime.now()}"
            update_file_in_github(
                github_user=github_user,
                github_repo=github_repo,
                github_pat=github_pat,
                file_path=file_path,
                new_df=updated_df,
                old_sha=sha,
                commit_message=commit_msg
            )

if __name__ == "__main__":
    render_backend()
