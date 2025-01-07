import streamlit as st

def render_report():
    # Display the title
    st.title("AMAS Data-Driven Strategy Report")
    st.subheader("A Comprehensive Approach to Transforming Operations in 2025")

    # Add custom hover effect for the report cover
    st.markdown(
        """
        <style>
        .image-container {
            position: relative;
            display: inline-block;
            cursor: pointer;
        }

        .image-container img {
            width: 400px;
            transition: transform 0.3s ease;
        }

        .image-container:hover img {
            transform: scale(1.5);
            z-index: 10;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Add the image with hover effect
    st.markdown(
        """
        <div class="image-container">
            <img src="input/report.jpg" alt="AMAS Hypermarket - Data-Driven Strategy for 2025">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Add a description below the cover
    st.markdown(
        """
        #### Report Overview
        This report outlines AMAS Hypermarket's data-driven transformation strategy for 2025. 
        It focuses on modernizing operations, improving customer experiences, and enhancing decision-making 
        through advanced analytics and automation.
        """
    )

    # Add a button for future functionality
    st.button("Download Full Report (Coming Soon)")
