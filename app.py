import streamlit as st
import pandas as pd

# App configuration
st.set_page_config(
    page_title="Amas Data Driven Migration Strategy",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation
menu = ["Home", "Current Situation", "Phase 1", "Phase 2", "Phase 3", "Roadmap"]
selection = st.sidebar.radio("Navigate", menu)

# App content
if selection == "Home":
    st.title("Amas Data Driven Migration Strategy")
    st.write(
        """
        ### Vision
        In the ideal future, **AMAS Hypermarket** functions as a fully integrated, data-driven operation where every decision—whether in receiving, store-level management, or final sales—is guided by real-time insights and predictive analytics.

        #### Seamless Delivery & Receiving
        - **Automated Scanning & PO Cross-Referencing**: Deliveries are instantly verified against purchase orders using barcode or QR code scanning. Any discrepancy—be it quantity or expiration date—triggers an immediate alert, ensuring fast resolution and minimal waste.
        - **Real-Time Quality Control**: AI-driven QC systems detect and flag damaged or near-expiry items automatically, integrating these findings into the inventory record for swift corrective actions.

        #### Fully Integrated Inventory Management
        - **End-to-End Visibility**: A centralized system links supplier databases to backroom storage and the sales floor, eliminating blind spots.
        - **Smart Stock Allocation**: AI-powered categorization and tracking ensure items are optimally placed and replenished, reducing stockouts and overstocks.

        #### Optimized Store Operations
        - **Dynamic Shelf Stocking**: Shelves update in real time based on product demand, sales trends, and planned promotions. Category groupings are continually refined to improve customer flow and increase cross-sell opportunities.
        - **Data-Driven Promotions & Pricing**: A rule-based engine adjusts pricing and promotions in near real time, guided by factors like sales velocity, competitor data, and stock levels, maximizing profitability and customer satisfaction.

        #### Advanced Selling & Dashboard Monitoring
        - **AI-Enhanced Customer Interaction**: The store layout and product placements are informed by foot-traffic analysis, demographic data, and historical purchase behaviors, resulting in a seamless, personalized shopping experience.
        - **Centralized Dashboards**: Managers and staff have continuous visibility into key performance metrics—sales data, inventory fluctuations, staff productivity—enabling proactive interventions and better decision-making.

        #### Human Management Supported by Data
        - **Real-Time Task Prioritization**: From receiving alerts about near-expiry items to identifying best-selling products that need restocking, data drives each workstream, minimizing manual guesswork.
        - **Optimized Scheduling & Performance Tracking**: Staff scheduling aligns with predicted customer flow, while clear, data-based performance metrics motivate and guide employee development.
        """
    )

elif selection == "Current Situation":
    st.title("Current Situation")
    st.write(
        """
        **Challenges Identified:**
        - Manual processes dominate delivery verification, stock management, and pricing.
        - Barcode errors and inconsistencies disrupt operations.
        - No real-time visibility into inventory, resulting in inefficiencies and blind spots.
        - Customer feedback and promotional impact lack structured analysis.
        """
    )

elif selection == "Phase 1":
    st.title("Phase 1: Early & Doable")
    st.write(
        """
        **Key Actions:**
        - Implement barcode scanning for deliveries.
        - Centralize record-keeping in a single spreadsheet or database.
        - Upskill one in-house programmer with Python training to automate basic tasks.
        - Conduct short training sessions for the finance director on automated PO approvals.
        """
    )

elif selection == "Phase 2":
    st.title("Phase 2: Extended Digitization & Standardization")
    st.write(
        """
        **Key Actions:**
        - Integrate real-time data updates for deliveries, inventory, and QC.
        - Digitize pricing and promotions into a centralized system.
        - Introduce dashboards for real-time visibility of operations and inventory.
        - Standardize processes across departments to eliminate ad-hoc decisions.
        """
    )

elif selection == "Phase 3":
    st.title("Phase 3: Advanced Analytics & Automation")
    st.write(
        """
        **Key Actions:**
        - Deploy AI-driven predictive stock allocation and dynamic pricing.
        - Implement AI-based shelf-life forecasting and optimized store layouts.
        - Introduce cashierless checkout systems or advanced POS for seamless operations.
        - Use advanced dashboards to combine all operational metrics for data-driven decision-making.
        """
    )

elif selection == "Roadmap":
    st.title("Roadmap")
    st.write(
        """
        **Timeline:**

        **Phase 1 (0–2 Months):**
        - Purchase scanners and implement basic barcode scanning.
        - Train finance director and in-house programmer.
        - Roll out centralized record-keeping.

        **Phase 2 (2–4 Months):**
        - Deploy integrated software modules (e.g., Phenix).
        - Implement dashboards and partial automation of pricing/promotions.
        - Train staff for standardized workflows.

        **Phase 3 (4–6 Months):**
        - Roll out AI functionalities like predictive restocking and dynamic planograms.
        - Pilot advanced POS or cashierless checkout.
        - Refine predictive models and ensure scalability.
        """
    )
