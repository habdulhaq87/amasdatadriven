import streamlit as st
import pandas as pd

def render_phase3():
    # Title and Introduction
    st.title("Phase 3: Advanced Analytics & Automation")
    st.write("""
    **Phase 3** brings AMAS Hypermarket to **full data-driven maturity**, 
    building on the real-time data flows and standardization achieved in Phase 2. 
    This stage leverages **AI-driven** insights, cashierless checkout, 
    predictive stock allocation, and more to ensure true end-to-end automation.
    """)

    # Load Data
    df = pd.read_csv("amas_data.csv", sep=",")  # Update path if needed
    categories = df["Category"].unique()

    for i, cat in enumerate(categories):
        cat_data = df[df["Category"] == cat]

        # Sub-header for each category
        st.markdown(f"## {cat} — Elevating from Phase 2 to Phase 3")

        # Alternate layout (image left or right)
        if i % 2 == 0:
            col_img, col_text = st.columns([1, 3])
        else:
            col_text, col_img = st.columns([3, 1])

        with col_img:
            st.image(
                f"https://via.placeholder.com/300x200?text={cat.replace(' ', '+')}",
                caption=f"Moving {cat} into Phase 3",
                use_container_width=True
            )

        with col_text:
            for _, row in cat_data.iterrows():
                aspect_title = row["Aspect"]
                phase2_improvement = row["Phase2"]  # Phase 2 achievements
                phase3_improvement = row["Phase3"]  # Phase 3 enhancements

                # Create an expander for each Aspect
                with st.expander(f"**Aspect:** {aspect_title}"):
                    # Two columns: left = Phase 2, right = Phase 3
                    ccol, pcol = st.columns(2)
                    with ccol:
                        st.markdown("**Phase 2**")
                        st.write(phase2_improvement)
                    with pcol:
                        st.markdown("**Phase 3**")
                        st.write(phase3_improvement)

        st.write("---")

    st.success("""
    By fully adopting **Phase 3**, AMAS Hypermarket will harness 
    advanced analytics, AI-driven automation, and cutting-edge 
    operational strategies—culminating in a **truly data-driven** ecosystem 
    that boosts efficiency, profitability, and customer satisfaction.
    """)

if __name__ == "__main__":
    render_phase3()
