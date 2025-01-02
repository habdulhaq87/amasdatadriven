import streamlit as st

def render_vision():
    # Title and Introduction
    st.title("Vision: The Ultimate Data-Driven Hypermarket")
    st.write("""
    Imagine a future where **every decision** at AMAS Hypermarket—whether in receiving, store-level management, 
    or final sales—is guided by real-time insights and **predictive analytics**. 
    Here's how a fully integrated, data-driven operation transforms every aspect of AMAS Hypermarket:
    """)

    # Layout for Vision Sections
    st.markdown("### Seamless Delivery & Receiving")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(
            "input/seamless.jpeg",
            caption="Automated Receiving",
            use_container_width=True
        )
    with col2:
        st.markdown("""
        - **Automated Scanning & PO Cross-Referencing**: Deliveries are instantly verified against purchase orders using barcode or QR code scanning. Any discrepancy—be it quantity or expiration date—triggers an immediate alert, ensuring fast resolution and minimal waste.
        - **Real-Time Quality Control**: AI-driven QC systems detect and flag damaged or near-expiry items automatically, integrating these findings into the inventory record for swift corrective actions.
        """)

    st.markdown("### Fully Integrated Inventory Management")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        - **End-to-End Visibility**: A centralized system links supplier databases to backroom storage and the sales floor, eliminating blind spots.
        - **Smart Stock Allocation**: AI-powered categorization and tracking ensure items are optimally placed and replenished, reducing stockouts and overstocks.
        """)
    with col2:
        st.image(
            "input/integ.jpeg",
            caption="Integrated Inventory",
            use_container_width=True
        )

    st.markdown("### Optimized Store Operations")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(
            "input/well.jpeg",
            caption="Optimized Shelving",
            use_container_width=True
        )
    with col2:
        st.markdown("""
        - **Dynamic Shelf Stocking**: Shelves update in real time based on product demand, sales trends, and planned promotions. Category groupings are continually refined to improve customer flow and increase cross-sell opportunities.
        - **Data-Driven Promotions & Pricing**: A rule-based engine adjusts pricing and promotions in near real time, guided by factors like sales velocity, competitor data, and stock levels, maximizing profitability and customer satisfaction.
        """)

    st.markdown("### Advanced Selling & Dashboard Monitoring")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        - **AI-Enhanced Customer Interaction**: The store layout and product placements are informed by foot-traffic analysis, demographic data, and historical purchase behaviors, resulting in a seamless, personalized shopping experience.
        - **Centralized Dashboards**: Managers and staff have continuous visibility into key performance metrics—sales data, inventory fluctuations, staff productivity—enabling proactive interventions and better decision-making.
        """)
    with col2:
        st.image(
            "input/ceo.jpeg",
            caption="Real-Time Dashboards",
            use_container_width=True
        )

    st.markdown("### Human Management Supported by Data")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(
            "input/hr.jpg",
            caption="Data-Driven Staff Management",
            use_container_width=True
        )
    with col2:
        st.markdown("""
        - **Real-Time Task Prioritization**: From receiving alerts about near-expiry items to identifying best-selling products that need restocking, data drives each workstream, minimizing manual guesswork.
        - **Optimized Scheduling & Performance Tracking**: Staff scheduling aligns with predicted customer flow, while clear, data-based performance metrics motivate and guide employee development.
        """)

    st.write("---")
    st.success("This vision represents the future of AMAS Hypermarket—an operation where **data informs every decision**, boosting efficiency, customer satisfaction, and profitability.")

if __name__ == "__main__":
    render_vision()
