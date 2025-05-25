import streamlit as st
import pandas as pd
from streamlit_lottie import st_lottie
import json

def load_lottie_animation(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

# --- Proportionally compressed dates ---
# Function to scale date within the new window
from datetime import datetime, timedelta

old_start = datetime(2025,6,1)
old_end   = datetime(2025,8,31)
new_start = datetime(2025,6,1)
new_end   = datetime(2025,7,31)

def scale_date(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    old_span = (old_end - old_start).days
    new_span = (new_end - new_start).days
    delta = (d - old_start).days
    new_delta = round(delta * new_span / old_span)
    return (new_start + timedelta(days=new_delta)).strftime("%Y-%m-%d")

phase2_tasks = [
    {
        "Task": "Operational Monitoring & Visualization Dashboard",
        "Start": scale_date("2025-06-01"),
        "End":   scale_date("2025-08-01"),
        "Budget": 3200,
        "Lottie": "input/phase2/monitoring.json",
        "Details": """
- Real-Time Data Room (dashboard, inventory alerts, sales analysis)
- D3 Visualizations (stacked bar, heatmap, bullet, sunburst, bubble charts)
- Store Map Visualization (real-time inventory map, heatmap for sales/critical items)
        """
    },
    {
        "Task": "Security, Performance Testing & Kurdish Translation",
        "Start": scale_date("2025-06-15"),
        "End":   scale_date("2025-08-15"),
        "Budget": 2300,
        "Lottie": "input/phase2/security.json",
        "Details": """
- Penetration testing, load & performance tests, pilot market test
- Implement security enhancements
- UI and documentation Kurdish localization and validation
        """
    },
    {
        "Task": "Data Collection for Machine Learning",
        "Start": scale_date("2025-06-15"),
        "End":   scale_date("2025-08-15"),
        "Budget": 1700,
        "Lottie": "input/phase2/datacollection.json",
        "Details": """
- Internal/external data acquisition (sales, inventory, supplier, weather, economic, etc)
- ML-optimized data preparation (forecasting, dynamic pricing, demand modeling)
        """
    },
    {
        "Task": "Financial & HR Automation",
        "Start": scale_date("2025-07-01"),
        "End":   scale_date("2025-08-31"),
        "Budget": 2800,
        "Lottie": "input/phase2/Automation.json",
        "Details": """
- Automate supplier payments & invoice reconciliation
- AI-enabled HR process automation (task analysis, pilot)
- Define progressive automation milestones
        """
    },
    {
        "Task": "Training and Capacity Building",
        "Start": scale_date("2025-08-01"),
        "End":   scale_date("2025-08-31"),
        "Budget": 1200,
        "Lottie": "input/phase2/helpdesk.json",
        "Details": """
- Staff & supplier system training (usage, security, D3 dashboards)
- Supplier onboarding, continuous feedback
- User manuals, videos, FAQs
        """
    },
]
df = pd.DataFrame(phase2_tasks)

def render_phase2():
    st.title("Phase 2: Advanced Digitization & Automation")
    st.write("""
    This section outlines how AMAS Hypermarket will move forward with **Phase 2** improvements. Four tabs are available below:

    - **Plan**: Detailed overview of each Phase 2 workstream.
    - **Tasks**: Specific tasks, timelines, budgets, and descriptions.
    - **Summary**: High-level summary and Gantt-style chart of Phase 2.
    - **Budget**: Consolidated Phase 2 budget view.
    """)

    tab_plan, tab_tasks, tab_summary, tab_budget = st.tabs(["Plan", "Tasks", "Summary", "Budget"])

    # -------- PLAN TAB ---------
    with tab_plan:
        st.subheader("Plan Overview")
        st.write("""
Below is a **task-by-task** breakdown of Phase 2 improvements. Each task features relevant Lottie animations, timeline, and main activities.
        """)
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
                        "https://via.placeholder.com/180x200?text=Phase+2",
                        caption=row["Task"], use_container_width=True
                    )
            with col_text:
                st.markdown(f"### {row['Task']}")
                st.markdown(f"**Timeline:** {row['Start']} to {row['End']}")
                st.markdown(f"**Budget:** ${row['Budget']:,}")
                st.markdown(row['Details'])
            st.write("---")

        st.success(f"""
By implementing these **Phase 2** steps, AMAS Hypermarket will achieve real-time operational visibility, 
improved security, robust data for AI, automated finance & HR, and fully trained teams/suppliers.  
**Total budget:** ${df['Budget'].sum():,}.
        """)

    # -------- TASKS TAB ---------
    with tab_tasks:
        st.subheader("Phase 2 Tasks")
        st.write("Details of each Phase 2 task, with timeline and budget.")
        for _, row in df.iterrows():
            with st.expander(row["Task"]):
                st.markdown(f"**Timeline:** {row['Start']} to {row['End']}")
                st.markdown(f"**Budget:** ${row['Budget']:,}")
                st.markdown("**Details:**")
                st.markdown(row["Details"])

    # -------- SUMMARY TAB ---------
    with tab_summary:
        st.subheader("Phase 2 Summary")
        st.write("Below is a summary schedule and table of Phase 2 activities.")
        summary_df = df.copy()
        summary_df["Start"] = pd.to_datetime(summary_df["Start"])
        summary_df["End"] = pd.to_datetime(summary_df["End"])
        try:
            import plotly.express as px
            fig = px.timeline(
                summary_df, x_start="Start", x_end="End", y="Task", color="Budget",
                title="Phase 2 Task Schedule", labels={'Task': 'Task'}
            )
            fig.update_layout(yaxis_title="Task", xaxis_title="Timeline", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Install plotly for interactive timeline summary.")

        st.dataframe(df[["Task", "Start", "End", "Budget"]], use_container_width=True)

    # -------- BUDGET TAB ---------
    with tab_budget:
        st.subheader("Phase 2 Budget")
        st.write("Overview of budget per Phase 2 workstream.")
        st.dataframe(df[["Task", "Budget"]], use_container_width=True)
        st.markdown(f"### **Total Phase 2 Budget: ${df['Budget'].sum():,}**")
        st.info("Training and Capacity Building is offered free of charge for this phase.")

if __name__ == "__main__":
    render_phase2()
