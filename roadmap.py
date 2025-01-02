import streamlit as st
import pandas as pd

def render_roadmap():
    st.title("Roadmap: Implementation Steps")

    st.write("""
    This roadmap provides a **high-level timeline** for AMAS Hypermarket's 
    transition to a **fully data-driven operation**, broken into three phases. 
    Each phase includes **key steps**, **deliverables**, and **responsibilities**, 
    ensuring clarity on **what** needs to be done, **who** is responsible, 
    and **when** it should be completed.
    """)

    # Load roadmap data
    df = pd.read_csv("roadmap.csv")

    # Iterate through each row to display the phases
    for idx, row in df.iterrows():
        phase = row["Phase"]
        duration = row["Duration"]
        key_steps = row["KeySteps"]
        deliverables = row["Deliverables"]
        responsibility = row["Responsibility"]

        # Sub-header for each phase
        st.markdown(f"## {phase} — {duration}")

        # Create columns to lay out the text and an image (optional)
        col_text, col_img = st.columns([3, 1])

        with col_text:
            # Expanders for Key Steps, Deliverables, Responsibility
            with st.expander("Key Steps", expanded=True):
                st.write(key_steps)

            with st.expander("Deliverables"):
                st.write(deliverables)

            with st.expander("Responsibility"):
                st.write(responsibility)

        with col_img:
            # Use a placeholder image or replace with a relevant image for each phase
            st.image(
                f"https://via.placeholder.com/300x200?text={phase.replace(' ', '+')}",
                caption=f"{phase} Overview",
                use_container_width=True
            )

        # Separator
        st.write("---")

    st.success("""
    By following this roadmap, AMAS Hypermarket will **systematically implement** 
    each phase of the data-driven strategy. This structured approach ensures 
    accountability, measurable progress, and a clear path toward achieving 
    a fully data-driven retail environment.
    """)

if __name__ == "__main__":
    render_roadmap()
