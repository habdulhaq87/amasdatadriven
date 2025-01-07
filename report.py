import streamlit as st

def render_report():
    # Display the title
    st.title("AMAS Data-Driven Strategy Report")
    st.subheader("A Comprehensive Approach to Transforming Operations in 2025")

    # Add a placeholder for the report cover
    st.markdown("### Report Cover")

    # Display the report cover image with reduced size
    st.image("input/report.jpg", caption="AMAS Hypermarket - Data-Driven Strategy for 2025", width=400)

    # Add a description below the cover
    st.markdown(
        """
        #### Report Overview
        This report outlines AMAS Hypermarket's data-driven transformation strategy for 2025. 
        It focuses on modernizing operations, improving customer experiences, and enhancing decision-making 
        through advanced analytics and automation.
        """
    )

    # Hyperlink to the report
    st.markdown(
        """
        [📄 **View Full Report**](https://docs.google.com/document/d/1RmrlmdwNbBSVWaDItfdf65bSJTIrlg29o56KmKywdto/edit?usp=sharing)
        """
    )
