import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date

# ---------------------------------------
# Page setup
# ---------------------------------------
st.set_page_config(page_title="Finance", layout="wide")
st.title("💼 Finance")

# ---------------------------------------
# DB connection (from st.secrets)
# ---------------------------------------
cfg = st.secrets["mysql"]
conn = mysql.connector.connect(
    host=cfg["host"],
    port=int(cfg["port"]),
    user=cfg["user"],
    password=cfg["password"],
    database=cfg["database"],
    autocommit=True,
)

tab_budgets, tab_transactions, tab_summary = st.tabs(["📊 Budgets", "📜 Transactions", "📈 Phase Summary"])

def money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return x

# ======================================================
# 📊 Budgets tab — PHASE CARDS (no big table)
# ======================================================
with tab_budgets:
    st.subheader("Budgets by Phase")

    try:
        # Phase-level totals (one row per budget_line / phase)
        q_phase_budget = """
            SELECT
                b.budget_line AS phase,
                COALESCE(SUM(b.budget_usd), 0) AS budget_total
            FROM budgets b
            GROUP BY b.budget_line
            ORDER BY b.budget_line
        """
        df_phase_budget = pd.read_sql(q_phase_budget, conn)

        q_phase_spent = """
            SELECT
                b.budget_line AS phase,
                COALESCE(SUM(t.amount_usd), 0) AS spent_total
            FROM transactions t
            JOIN budgets b ON b.budget_id = t.budget_id
            GROUP BY b.budget_line
            ORDER BY b.budget_line
        """
        df_phase_spent = pd.read_sql(q_phase_spent, conn)

        # Merge totals
        df_cards = pd.merge(df_phase_budget, df_phase_spent, on="phase", how="left").fillna({"spent_total": 0})
        df_cards["remaining_total"] = df_cards["budget_total"] - df_cards["spent_total"]

        # Details per budget item to show inside each card
        q_items = """
            SELECT
                b.budget_id,
                b.budget_line AS phase,
                b.task,
                b.start_date,
                b.end_date,
                b.budget_usd,
                COALESCE(x.spent, 0) AS spent,
                (COALESCE(b.budget_usd,0) - COALESCE(x.spent,0)) AS remaining,
                b.justification
            FROM budgets b
            LEFT JOIN (
                SELECT budget_id, SUM(amount_usd) AS spent
                FROM transactions
                GROUP BY budget_id
            ) x ON x.budget_id = b.budget_id
            ORDER BY b.budget_line, b.budget_id
        """
        df_items = pd.read_sql(q_items, conn)

        # Card grid (2 or 3 per row depending on width — we’ll do 3)
        if df_cards.empty:
            st.info("No budgets found yet.")
        else:
            cols_per_row = 3
            rows = (len(df_cards) + cols_per_row - 1) // cols_per_row
            idx = 0
            for _ in range(rows):
                columns = st.columns(cols_per_row)
                for c in columns:
                    if idx >= len(df_cards):
                        break
                    row = df_cards.iloc[idx]
                    phase_name = row["phase"]
                    budget_total = float(row["budget_total"])
                    spent_total = float(row["spent_total"])
                    remaining_total = float(row["remaining_total"])

                    with c:
                        # Card container
                        with st.container(border=True):
                            st.markdown(f"### {phase_name}")
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Budget", money(budget_total))
                            m2.metric("Spent", money(spent_total))
                            m3.metric("Remaining", money(remaining_total))

                            # Mini details: tasks count + date span
                            items_this = df_items[df_items["phase"] == phase_name].copy()
                            tasks_count = len(items_this)
                            if not items_this.empty:
                                start_min = items_this["start_date"].min()
                                end_max = items_this["end_date"].max()
                                st.caption(f"Tasks: **{tasks_count}**  |  Timeline: **{start_min} → {end_max}**")
                            else:
                                st.caption("Tasks: **0**")

                            # Expand for per-task details
                            with st.expander("Details"):
                                if items_this.empty:
                                    st.write("No items in this phase yet.")
                                else:
                                    # Show a small, readable table for the phase only
                                    view = items_this[[
                                        "task", "start_date", "end_date", "budget_usd", "spent", "remaining", "justification"
                                    ]].copy()
                                    # Pretty money
                                    for col in ["budget_usd", "spent", "remaining"]:
                                        view[col] = view[col].apply(money)
                                    st.dataframe(view, use_container_width=True, height=260)

                    idx += 1

            # Global summary metrics at the bottom
            st.divider()
            total_budget = float(df_cards["budget_total"].sum())
            total_spent = float(df_cards["spent_total"].sum())
            total_remaining = total_budget - total_spent
            g1, g2, g3 = st.columns(3)
            g1.metric("Total Budget (All Phases)", money(total_budget))
            g2.metric("Total Spending (All Phases)", money(total_spent))
            g3.metric("Total Remaining (All Phases)", money(total_remaining))

    except Error as e:
        st.error(f"Database error (Budgets tab): {e}")

# ======================================================
# 📜 Transactions tab — filterable list
# ======================================================
with tab_transactions:
    st.subheader("Transactions")

    try:
        # Budget dropdown
        budget_lookup = pd.read_sql("SELECT budget_id, budget_line FROM budgets ORDER BY budget_line ASC", conn)
        options = ["(All)"] + budget_lookup["budget_line"].tolist()
        sel_budget_name = st.selectbox("Filter by Budget Line", options, index=0)

        # Date range
        c1, c2 = st.columns(2)
        with c1:
            start_date = st.date_input("Start date", value=date(2025, 1, 1))
        with c2:
            end_date = st.date_input("End date", value=date.today())

        base_q = """
            SELECT
                t.transaction_id,
                t.budget_id,
                b.budget_line,
                t.transaction_date,
                t.description,
                t.amount_usd,
                t.notes
            FROM transactions t
            JOIN budgets b ON b.budget_id = t.budget_id
            WHERE t.transaction_date BETWEEN %s AND %s
        """
        params = [start_date, end_date]
        if sel_budget_name != "(All)":
            base_q += " AND b.budget_line = %s"
            params.append(sel_budget_name)
        base_q += " ORDER BY t.transaction_date ASC, t.transaction_id ASC"

        df_tx = pd.read_sql(base_q, conn, params=params)

        # Totals
        tx_total = float(df_tx["amount_usd"].sum()) if not df_tx.empty else 0.0
        st.metric("Total in view", money(tx_total))

        show_tx = df_tx.copy()
        if not show_tx.empty:
            show_tx["amount_usd"] = show_tx["amount_usd"].apply(money)

        st.dataframe(
            show_tx[[
                "transaction_id", "budget_line", "transaction_date", "description", "amount_usd", "notes"
            ]] if not show_tx.empty else show_tx,
            use_container_width=True
        )

        st.download_button(
            "⬇️ Download Transactions CSV",
            data=df_tx.to_csv(index=False).encode("utf-8"),
            file_name="transactions_view.csv",
            mime="text/csv"
        )

    except Error as e:
        st.error(f"Database error (Transactions tab): {e}")

# ======================================================
# 📈 Phase Summary tab — totals row included
# ======================================================
with tab_summary:
    st.subheader("Phase Summary (Budget vs. Spent vs. Remain)")

    try:
        phase_budget_q = """
            SELECT
                b.budget_line AS phase,
                COALESCE(SUM(b.budget_usd), 0) AS budget_total
            FROM budgets b
            GROUP BY b.budget_line
            ORDER BY b.budget_line
        """
        df_budget = pd.read_sql(phase_budget_q, conn)

        phase_spend_q = """
            SELECT
                b.budget_line AS phase,
                COALESCE(SUM(t.amount_usd), 0) AS spent_total
            FROM transactions t
            JOIN budgets b ON b.budget_id = t.budget_id
            GROUP BY b.budget_line
            ORDER BY b.budget_line
        """
        df_spend = pd.read_sql(phase_spend_q, conn)

        # Merge & compute remain
        df_phase = pd.merge(df_budget, df_spend, on="phase", how="left").fillna({"spent_total": 0})
        df_phase["remain"] = df_phase["budget_total"] - df_phase["spent_total"]

        total_row = pd.DataFrame([{
            "phase": "Total",
            "budget_total": df_phase["budget_total"].sum(),
            "spent_total": df_phase["spent_total"].sum(),
            "remain": (df_phase["budget_total"].sum() - df_phase["spent_total"].sum())
        }])
        df_out = pd.concat([df_phase, total_row], ignore_index=True)

        show = df_out.rename(columns={
            "phase": "Phases",
            "budget_total": "Budget",
            "spent_total": "USD Amount",
            "remain": "Remain"
        }).copy()
        for col in ["Budget", "USD Amount", "Remain"]:
            show[col] = show[col].apply(money)

        st.dataframe(show, use_container_width=True)

        st.download_button(
            "⬇️ Download Phase Summary CSV",
            data=df_out.to_csv(index=False).encode("utf-8"),
            file_name="phase_summary.csv",
            mime="text/csv"
        )

    except Error as e:
        st.error(f"Database error (Summary tab): {e}")

# ---------------------------------------
# Close connection
# ---------------------------------------
try:
    conn.close()
except:
    pass
