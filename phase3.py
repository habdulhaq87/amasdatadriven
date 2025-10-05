import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie
import json

# ------------ Lottie Loader ------------
def load_lottie_animation(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

# ------------ Phase 3 Workstreams (Top-Level Budget) ------------
# NOTE: These are the budgeted lines that sum to the base total (11,200).
phase3_workstreams = [
    {
        "Task": "LLM Backend (AI Layer)",
        "Start": "2025-10-11",
        "End": "2025-11-30",
        "Budget": 2300,
        "Lottie": "input/phase3/llm.json",
        "Details": """
- Conversational AI for founders (insights, summaries, proactive alerts)
- Connects to finance, supply, inventory, and HR data
- Forms the intelligence core for Phase 3 automation
        """
    },
    {
        "Task": "Supplier Backend",
        "Start": "2025-10-11",
        "End": "2025-11-20",
        "Budget": 2000,
        "Lottie": "input/phase3/supplier.json",
        "Details": """
- Supplier accounts, POs, invoices, delivery tracking
- Tight integration with Automated Purchase Order logic
        """
    },
    {
        "Task": "Customer Backend",
        "Start": "2025-11-15",
        "End": "2025-12-20",
        "Budget": 2000,
        "Lottie": "input/phase3/customer.json",
        "Details": """
- Customer profiles, loyalty/credit, purchase history
- CRM foundation and personalization data source for the LLM
        """
    },
    {
        "Task": "Bakery Integration",
        "Start": "2025-12-10",
        "End": "2025-12-31",
        "Budget": 1300,
        "Lottie": "input/phase3/bakery.json",
        "Details": """
- Ingredient usage, production, waste tracking, and sales syncing
- Real-time linkage to inventory and supplier ordering
        """
    },
    {
        "Task": "Butchery Integration",
        "Start": "2025-12-10",
        "End": "2025-12-31",
        "Budget": 1300,
        "Lottie": "input/phase3/butchery.json",
        "Details": """
- Batch tracking, yield, waste, costing, and sales syncing
- Improves stock precision and profitability analytics
        """
    },
    {
        "Task": "Enhancements (Total)",
        "Start": "2025-10-11",
        "End": "2025-12-31",
        "Budget": 2300,
        "Lottie": "input/phase3/enhancements.json",
        "Details": """
- Targeted upgrades across: Data Room, Cashier, Automated PO, HR Monitoring
- See detailed sub-allocation in the Enhancements section
        """
    },
]

# ------------ Phase 3 Enhancements (Sub-allocation; do NOT add to total again) ------------
# These roll up to the single "Enhancements (Total)" line above.
phase3_enhancements = [
    {
        "Task": "Data Room Enhancement",
        "Start": "2025-10-11",
        "End": "2025-11-10",
        "Budget": 800,
        "Lottie": "input/phase3/enh_data_room.json",
        "Details": """
- Improve dashboards and metrics coverage
- Double analytic depth across existing modules
        """
    },
    {
        "Task": "Enhanced Cashier System",
        "Start": "2025-11-01",
        "End": "2025-12-10",
        "Budget": 700,
        "Lottie": "input/phase3/enh_cashier.json",
        "Details": """
- Founder/role-aware views: balances, credits, KPIs, alerts
- Deeper analytics, anomaly checks, and permissions
        """
    },
    {
        "Task": "Automated Purchase Order Enhancement",
        "Start": "2025-11-15",
        "End": "2025-12-20",
        "Budget": 500,
        "Lottie": "input/phase3/enh_apo.json",
        "Details": """
- Refine forecasting signals, reorder rules, and approval thresholds
- Strengthen integration with Supplier/Inventory modules
        """
    },
    {
        "Task": "HR Monitoring Enhancement",
        "Start": "2025-12-01",
        "End": "2025-12-20",
        "Budget": 300,
        "Lottie": "input/phase3/enh_hr.json",
        "Details": """
- Attendance, shift analytics, and productivity insights (monitoring only)
- Cross-links with cashier and operations data
        """
    },
]

df = pd.DataFrame(phase3_workstreams)
enh_df = pd.DataFrame(phase3_enhancements)

# ------------ Render App ------------
def render_phase3():
    st.title("Phase 3: Intelligent Integration & Automation")

    st.write("""
This section outlines the **Phase 3** program for AMAS Hypermarket. Five tabs are available below:

- **Plan**: Detailed overview of each Phase 3 workstream.
- **Tasks**: Specific tasks, timelines, budgets, and descriptions.
- **Summary**: High-level summary with a Gantt-style chart for Phase 3.
- **Budget**: Consolidated Phase 3 budget with **15% contingency**.
- **Human Resource**: Team assignments and roles for Phase 3.
    """)

    tab_plan, tab_tasks, tab_summary, tab_budget, tab_team = st.tabs(
        ["Plan", "Tasks", "Summary", "Budget", "Human Resource"]
    )

    # -------- PLAN TAB ---------
    with tab_plan:
        st.subheader("Plan Overview (Top-Level Workstreams)")
        for i, row in df.iterrows():
            lottie_file = row["Lottie"]
            if i % 2 == 0:
                col_img, col_text = st.columns([1, 3])
            else:
                col_text, col_img = st.columns([3, 1])

            with col_img:
                try:
                    st_lottie(load_lottie_animation(lottie_file), height=200, width=180)
                except Exception:
                    st.image(
                        "https://via.placeholder.com/180x200?text=Phase+3",
                        caption=row["Task"], use_container_width=True
                    )
            with col_text:
                st.markdown(f"### {row['Task']}")
                st.markdown(f"**Timeline:** {row['Start']} to {row['End']}")
                st.markdown(f"**Budget:** ${row['Budget']:,}")
                st.markdown(row['Details'])
            st.write("---")

        st.subheader("Enhancements — Sub-allocation (rolls up to 'Enhancements (Total)')")
        for j, row in enh_df.iterrows():
            with st.expander(row["Task"]):
                col_img, col_text = st.columns([1, 3])
                with col_img:
                    try:
                        st_lottie(load_lottie_animation(row["Lottie"]), height=180, width=160)
                    except Exception:
                        st.image(
                            "https://via.placeholder.com/160x180?text=Enhancement",
                            caption=row["Task"], use_container_width=True
                        )
                with col_text:
                    st.markdown(f"**Timeline:** {row['Start']} to {row['End']}")
                    st.markdown(f"**Budget (part of Enhancements Total):** ${row['Budget']:,}")
                    st.markdown("**Details:**")
                    st.markdown(row["Details"])

        # Totals (base + contingency)
        base_total = sum(item['Budget'] for item in phase3_workstreams if isinstance(item['Budget'], int))
        contingency = round(base_total * 0.15, 2)
        grand_total = round(base_total + contingency, 2)

        st.success(f"""
**Phase 3 Window:** 2025-10-11 → 2025-12-31  
**Base subtotal:** ${base_total:,.2f}  
**Contingency (15%):** ${contingency:,.2f}  
**Grand total:** ${grand_total:,.2f}
        """)

    # -------- TASKS TAB ---------
    with tab_tasks:
        st.subheader("Phase 3 Tasks (Top-Level)")
        for _, row in df.iterrows():
            with st.expander(row["Task"]):
                st.markdown(f"**Timeline:** {row['Start']} to {row['End']}")
                st.markdown(f"**Budget:** ${row['Budget']:,}")
                st.markdown("**Details:**")
                st.markdown(row["Details"])

        st.subheader("Enhancements (Breakdown)")
        for _, row in enh_df.iterrows():
            with st.expander(row["Task"]):
                st.markdown(f"**Timeline:** {row['Start']} to {row['End']}")
                st.markdown(f"**Budget (included in Enhancements Total):** ${row['Budget']:,}")
                st.markdown("**Details:**")
                st.markdown(row["Details"])

    # -------- SUMMARY TAB ---------
    with tab_summary:
        st.subheader("Phase 3 Summary & Schedule")

        # Build a combined dataframe for a timeline view (with categories)
        ws_df = df.copy()
        ws_df["Category"] = "Workstream"
        enh_sum_df = enh_df.copy()
        enh_sum_df["Category"] = "Enhancement"

        summary_df = pd.concat([ws_df, enh_sum_df], ignore_index=True)
        summary_df["Start"] = pd.to_datetime(summary_df["Start"])
        summary_df["End"] = pd.to_datetime(summary_df["End"])

        try:
            import plotly.express as px
            fig = px.timeline(
                summary_df, x_start="Start", x_end="End", y="Task", color="Category",
                title="Phase 3 Schedule", labels={'Task': 'Task'}
            )
            fig.update_layout(yaxis_title="Task", xaxis_title="Timeline", legend_title_text="Type")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Install plotly for an interactive timeline summary.")

        st.dataframe(df[["Task", "Start", "End", "Budget"]], use_container_width=True)

    # -------- BUDGET TAB ---------
    with tab_budget:
        st.subheader("Phase 3 Budget (Top-Level)")
        st.dataframe(df[["Task", "Budget"]], use_container_width=True)

        st.markdown("### Enhancements — Sub-allocation (Included in 'Enhancements (Total)')")
        st.dataframe(enh_df[["Task", "Budget"]], use_container_width=True)

        base_total = sum(item['Budget'] for item in phase3_workstreams if isinstance(item['Budget'], int))
        contingency = round(base_total * 0.15, 2)
        grand_total = round(base_total + contingency, 2)

        st.markdown(f"### **Base subtotal:** ${base_total:,.2f}")
        st.markdown(f"### **Contingency (15%):** ${contingency:,.2f}")
        st.success(f"### **Grand total:** ${grand_total:,.2f}")

        st.caption("Note: Enhancement sub-budgets are already included in the 'Enhancements (Total)' line to avoid double counting.")

    # -------- TEAM TAB ---------
    with tab_team:
        st.subheader("Human Resource Assignments — Phase 3")

        team_data = [
            {
                "Name": "Hawkar Ali Abdulhaq",
                "Role": "Project Lead & AI Product Owner",
                "Responsibilities": """
- Define LLM capabilities, prompts, and KPIs
- Own Data Room enhancements and analytics quality
- Align Supplier/Customer backends with business goals
- Oversee Phase 3 delivery, training agenda, and acceptance
                """
            },
            {
                "Name": "Abdullah Kawkas",
                "Role": "Core Engineer (Backends & Integrations)",
                "Responsibilities": """
- Implement Supplier and Customer backends
- Build LLM integration endpoints and data contracts
- Develop bakery/butchery connectors and inventory sync
- Enhance Automated PO, Cashier, and HR monitoring modules
                """
            },
            {
                "Name": "Muhammad Saheed",
                "Role": "Field Operations & Data Steward",
                "Responsibilities": """
- Coordinate supplier onboarding and data validation
- Collect real-world feedback and performance logs
- Support training and go-live readiness for departments
- Monitor data quality for analytics and LLM responses
                """
            },
        ]

        for member in team_data:
            with st.expander(member["Name"]):
                st.markdown(f"**Role:** {member['Role']}")
                st.markdown(member["Responsibilities"])

if __name__ == "__main__":
    render_phase3()
