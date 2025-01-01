import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="Amas Data-Driven Strategy", layout="wide")

    # --- Sidebar Navigation ---
    menu_items = [
        "Home", 
        "Current Stage", 
        "Vision", 
        "Phase 1", 
        "Phase 2", 
        "Phase 3", 
        "Roadmap"
    ]
    choice = st.sidebar.selectbox("Navigation", menu_items)

    # --- Load Data ---
    # Adjust the file path to match your setup, e.g., "./amas_data.csv" if in the same folder
    df = pd.read_csv("amas_data.csv")

    # --- Main Content ---
    if choice == "Home":
        st.title("Amas Hypermarket: Data-Driven Strategy App")
        st.write("""
        **Welcome to the Amas Hypermarket Data-Driven Strategy App!**

        This application outlines the current challenges and the roadmap for transforming Amas 
        Hypermarket into a fully data-driven retail operation. Use the sidebar to navigate 
        through various sections, where you'll find insights into the current situation, 
        a future vision, and the phased implementation plan (Phase 1, Phase 2, and Phase 3), 
        culminating in a roadmap for successful adoption.
        """)
        st.write("Below is a quick look at the data stored in `amas_data.csv` (for reference):")
        st.dataframe(df)

    elif choice == "Current Stage":
        st.title("Current Stage")
        st.write("**Placeholder**: Describe the current situation in more detail here. You can integrate specific data from `amas_data.csv` as needed.")

    elif choice == "Vision":
        st.title("Vision")
        st.write("**Placeholder**: Present the ultimate data-driven vision for Amas Hypermarket here. Include references to the desired end-state of operations, AI-driven processes, etc.")

    elif choice == "Phase 1":
        st.title("Phase 1")
        st.write("**Placeholder**: Outline Early & Doable steps, referencing relevant rows in `amas_data.csv`. For example, scanning, basic automation, etc.")

    elif choice == "Phase 2":
        st.title("Phase 2")
        st.write("**Placeholder**: Describe Extended Digitization & Standardization, referencing what you plan to automate more deeply.")

    elif choice == "Phase 3":
        st.title("Phase 3")
        st.write("**Placeholder**: Present the Advanced Analytics & Automation phase, featuring AI-driven forecasting, real-time planogram adjustments, etc.")

    elif choice == "Roadmap":
        st.title("Roadmap")
        st.write("**Placeholder**: Provide a high-level timeline (e.g., 0-2 months for Phase 1, 2-4 months for Phase 2, etc.). You can add tables, visuals, or bullet points.")


if __name__ == "__main__":
    main()
