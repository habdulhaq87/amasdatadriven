import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------- Phase 2 Task/Budget Data ----------------
phase2_tasks = [
    {
        "Task": "Operational Monitoring & Visualization Dashboard",
        "Start": "2025-06-01",
        "End": "2025-07-15",
        "Budget": 2500,
        "Details": """
        - Real-Time Data Room (dashboard, inventory alerts, sales analysis)
        - D3 Visualizations (stacked bar, heatmap, bullet, sunburst, bubble charts)
        - Store Map Visualization (real-time inventory map, heatmap for sales/critical items)
        """
    },
    {
        "Task": "Security, Performance Testing & Kurdish Translation",
        "Start": "2025-06-15",
        "End": "2025-08-15",
        "Budget": 2500,
        "Details": """
        - Penetration testing, load & performance tests, pilot market test
        - Implement security enhancements
        - UI and documentation Kurdish localization and validation
        """
    },
    {
        "Task": "Data Collection for Machine Learning",
        "Start": "2025-06-15",
        "End": "2025-08-15",
        "Budget": 2500,
        "Details": """
        - Internal/external data acquisition (sales, inventory, supplier, weather, economic, etc)
        - ML-optimized data preparation (forecasting, dynamic pricing, demand modeling)
        """
    },
    {
        "Task": "Financial & HR Automation",
        "Start": "2025-07-01",
        "End": "2025-08-31",
        "Budget": 3000,
        "Details": """
        - Automate supplier payments & invoice reconciliation
        - AI-enabled HR process automation (task analysis, pilot)
        - Define progressive automation milestones
        """
    },
    {
        "Task": "Training and Capacity Building",
        "Start": "2025-08-01",
        "End": "2025-08-31",
        "Budget": 0,
        "Details": """
        - Staff & supplier system training (usage, security, D3 dashboards)
        - Supplier onboarding, continuous feedback
        - User manuals, videos, FAQs
        """
    },
]
df_phase2 = pd.DataFrame(phase2_tasks)

# ----------------- Streamlit UI ---------------------------
st.set_page_config(page_title="Phase 2: AMAS Hypermarket", layout="wide")

st.title("Phase 2: Advanced Digitization & Automation Plan")
st.write("""
This section details the plan, tasks, summary, and budget for Phase 2 of AMAS Hypermarket's digital transformation.
""")

# ------------- Tabs Setup -------------
tab_plan, tab_tasks, tab_summary, tab_budget = st.tabs(["Plan", "Tasks", "Summary", "Budget"])

# --------- PLAN TAB -----------
with tab_plan:
    st.header("Plan Overview")
    for idx, row in df_phase2.iterrows():
        with st.expander(f"{row['Task']} ({row['Start']} to {row['End']})"):
            st.write(f"**Budget:** ${row['Budget']:,}")
            st.markdown(row['Details'])

    st.success(
        "Phase 2 builds on foundational improvements, focusing on real-time visibility, security, data readiness, "
        "financial and HR automation, and thorough staff/supplier capacity building. The total budget is "
        f"${df_phase2['Budget'].sum():,}."
    )

# ---------- TASKS TAB -----------
with tab_tasks:
    st.header("Phase 2 Tasks (Detailed)")
    for idx, row in df_phase2.iterrows():
        with st.expander(f"{row['Task']}"):
            st.markdown(f"**Timeline:** {row['Start']} to {row['End']}")
            st.markdown(f"**Budget:** ${row['Budget']:,}")
            st.markdown("**Details:**")
            st.markdown(row['Details'])

# ---------- SUMMARY TAB -----------
with tab_summary:
    st.header("Timeline Summary & Gantt Chart")
    gantt_df = df_phase2.copy()
    gantt_df['Start'] = pd.to_datetime(gantt_df['Start'])
    gantt_df['End'] = pd.to_datetime(gantt_df['End'])
    gantt_df['Task Short'] = gantt_df['Task'].apply(lambda x: x.split('&')[0].split('(')[0][:35])

    fig = px.timeline(
        gantt_df,
        x_start="Start",
        x_end="End",
        y="Task Short",
        color="Budget",
        title="Phase 2 Task Schedule",
        labels={'Task Short': 'Task'}
    )
    fig.update_layout(yaxis_title="Task", xaxis_title="Timeline", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Phase 2 Task Table")
    st.dataframe(df_phase2[["Task", "Start", "End", "Budget"]], use_container_width=True)

# ----------- BUDGET TAB -----------
with tab_budget:
    st.header("Phase 2 Budget Overview")
    st.write("The following table summarizes the budget per task line for Phase 2.")
    st.dataframe(df_phase2[["Task", "Budget"]], use_container_width=True, hide_index=True)
    st.markdown(f"### **Total Phase 2 Budget: ${df_phase2['Budget'].sum():,}**")
    st.info("Training and Capacity Building is offered free of charge for this phase.")

