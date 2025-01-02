import streamlit as st
import pandas as pd

def render_current_stage():
    st.title("Current Stage")
    st.write("""
    Below is an overview of the **current situation** for each category at Amas Hypermarket, 
    based on our observations and the data in `amas_data.csv`. 
    Expand each **Aspect** to view details in a visually engaging layout.
    """)

    # Load Data
    df = pd.read_csv("amas_data.csv", sep=",")  # Adjust the file path if needed

    # Group by category so each category is shown under a header
    categories = df["Category"].unique()
    for cat in categories:
        st.subheader(cat)  # Show category name as a subheader
        
        # Extract rows for the current category
        cat_data = df[df["Category"] == cat]
        
        for _, row in cat_data.iterrows():
            with st.expander(f"**Aspect:** {row['Aspect']}"):
                # Create a two-column layout inside the expander
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    # Placeholder image for each aspect; feel free to replace with actual images
                    st.image(
                        "https://via.placeholder.com/300x200?text=Current+Stage",
                        caption="Current Situation Image",
                        use_container_width=True
                    )
                
                with col2:
                    st.markdown(f"**Current Situation:**\n{row['CurrentSituation']}")

    st.write("---")
    st.info("End of Current Stage overview. Use the sidebar to navigate to other sections.")
