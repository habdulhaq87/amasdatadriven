import streamlit as st

def render_home():
    # Title and Intro
    st.title("Welcome to the Amas Data-Driven Strategy App")

    st.write("""
    This application serves as a **strategic tool** for AMAS Hypermarket, guiding 
    the transition from **manual operations** to a **fully data-driven model**. 
    By introducing effective digitization, standardization, and advanced analytics, 
    AMAS can significantly enhance operational efficiency, reduce errors, 
    and improve the overall customer experience.
    """)

    # Observational Findings
    st.markdown("### Observational Study & Key Challenges")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(
            "input/manual.jpg",
            caption="On-site Observations",
            use_container_width=True
        )
    with col2:
        st.write("""
        During a four-day observational study, multiple **challenges** were identified:
        - Manual receiving and stock management
        - Inconsistent pricing
        - Limited systems integration
        - Duplicate or mismatched barcodes
        - Decentralized workflows

        These issues often stem from **heavy reliance on manual processes**, 
        leading to potential errors, inefficiencies, and fragmented data handling.
        """)

    # Phases Overview
    st.markdown("### Proposed Strategy & Phases")
    st.write("""
    By transitioning toward a more **data-driven model**, AMAS Hypermarket stands 
    to **greatly enhance efficiency**, reduce errors, and **improve the overall 
    customer experience**. The proposed strategy details **three implementation phases**:
    """)

    # Phase 1, 2, 3 in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Phase 1")
        st.write("""
        **Early & Doable**  
        - Introduce simple barcode scanning  
        - Centralized record-keeping  
        - Short training sessions for key staff  
        - Upskill one in-house programmer for automation
        """)

    with col2:
        st.subheader("Phase 2")
        st.write("""
        **Extended Digitization & Standardization**  
        - Integrate real-time data for deliveries, inventory, QC  
        - Standardize pricing and promotion practices  
        - Reduce ad-hoc decisions with analytics-driven insights
        """)

    with col3:
        st.subheader("Phase 3")
        st.write("""
        **Advanced Analytics & Automation**  
        - AI-based shelf-life forecasting  
        - Predictive stock allocation  
        - Cashierless checkout  
        - Real-time decision-making across procurement, promotions, and layout
        """)

    st.markdown("### Timeline & Roadmap")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(
            "input/roadmap.jpg",
            caption="Implementation Path",
            use_container_width=True
        )
    with col2:
        st.write("""
        The roadmap outlines **specific steps, resources**, 
        and **projected outcomes** for each phase. By adopting these strategies, 
        AMAS can minimize **manual interventions**, boost **workforce productivity**, 
        and ensure that operations **scale effectively** as the hypermarket grows.

        The **ultimate goal** is to establish a culture where **data informs daily decisions**—
        from stocking shelves to setting prices—leading to a **more agile, efficient, 
        and customer-focused retail environment**.
        """)

    # Final Note
    st.write("---")
    st.success("""
    **Get started** by exploring the **Current Stage** to see the challenges 
    and existing workflows, then move on to the **Vision** 
    for a glimpse of the ideal data-driven future.
    """)


if __name__ == "__main__":
    render_home()
