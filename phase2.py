import streamlit as st
import pandas as pd

def render_phase2():
    # Title and Introduction
    st.title("Phase 2: Extended Digitization & Standardization")
    st.write("""
    In **Phase 2**, AMAS Hypermarket builds upon the foundations established in **Phase 1**, 
    integrating real-time data flows, standardizing processes, 
    and pushing further toward a cohesive, data-driven environment.
    """)

    # Load Data
    df = pd.read_csv("amas_data.csv", sep=",")  # Update the path if needed
    categories = df["Category"].unique()

    for i, cat in enumerate(categories):
        cat_data = df[df["Category"] == cat]

        # Sub-header for each category
        st.markdown(f"## {cat} — Advancing from Phase 1 to Phase 2")

        # Alternate the layout for variety:
        # Even index => image on the left, text on the right;
        # Odd index => reversed.
        if i % 2 == 0:
            col_img, col_text = st.columns([1, 3])
        else:
            col_text, col_img = st.columns([3, 1])

        with col_img:
            # Use a placeholder image; replace with real images if desired
            st.image(
                f"https://via.placeholder.com/300x200?text={cat.replace(' ', '+')}",
                caption=f"Progressing {cat} from Phase 1 to Phase 2",
                use_container_width=True
            )

        with col_text:
            for _, row in cat_data.iterrows():
                aspect_title = row["Aspect"]
                phase1_improvement = row["Phase1"]   # What we achieved in Phase 1
                phase2_improvement = row["Phase2"]   # Additional steps in Phase 2

                # Create an expander for each Aspect
                with st.expander(f"**Aspect:** {aspect_title}"):
                    # Two columns: left = Phase 1, right = Phase 2
                    ccol, pcol = st.columns(2)
                    with ccol:
                        st.markdown("**Phase 1**")
                        st.write(phase1_improvement)
                    with pcol:
                        st.markdown("**Phase 2**")
                        st.write(phase2_improvement)

        st.write("---")

    st.success("""
    With **Phase 2** fully implemented, AMAS Hypermarket achieves more robust data flows, 
    standardized operations, and deeper analytics—setting the stage for the AI-driven 
    capabilities planned in **Phase 3**.
    """)

if __name__ == "__main__":
    render_phase2()
