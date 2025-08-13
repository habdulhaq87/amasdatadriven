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

tab_budgets, tab_transactions, tab_summary = st.tabs(
    ["📊 Budgets", "📜 Transactions", "📈 Phase Summary"]
)

# -----------------------
# Helpers
# -----------------------
def fmt_money(val):
    """Format a number as $X,XXX.XX. Pass through strings like 'XXXX' safely."""
    try:
        # Handle Decimals/ints/floats
        if pd.isna(val):
            return "$—"
        return f"${float(val):,.2f}"
    except Exception:
        # If it's a string like 'XXXX', just return it
        s = "" if val is None else str(val)
        return s

def cast_cols_to_str(df: pd.DataFrame, cols):
    """Force specific columns to string (prevents Arrow dtype inference errors)."""
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(str)
    return df

# ======================================================
# 📊 Budgets tab — VERTICAL PHASE CARDS (one per row)
# ======================================================
with tab_budgets:
    st.subheader("Budgets by Phase")

    try:
        # Phase-level totals
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

        # Merge totals; if any text slipped into numeric columns upstream, coerce to numeric
        for d in (df_phase_budget, df_phase_spent):
            for c in d.columns:
                if c not in ("phase",):
                    d[c] = pd.to_numeric(d[c], errors="coerce")

        df_cards = pd.merge(df_phase_budget, df_phase_spent, on="phase", how="left").fillna({"spent_total": 0})
        df_cards["remaining_total"] = df_cards["budget_total"] - df_cards["spent_total"]

        # Per-item details for each phase
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

        # Coerce numeric columns safely in item details
        for c in ("budget_usd", "spent", "remaining"):
            if c in df_items.columns:
                df_items[c] = pd.to_numeric(df_items[c], errors="coerce")

        if df_cards.empty:
            st.info("No budgets found yet.")
        else:
            # One full-width card per phase (VERTICAL STACK)
            for _, row in df_cards.iterrows():
                phase_name = row["phase"]
                budget_total = row["budget_total"]
                spent_total = row["spent_total"]
                remaining_total = row["remaining_total"]

                with st.container(border=True):
                    st.markdown(f"### {phase_name}")

                    # Metrics in one line (render as formatted strings)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Budget", fmt_money(budget_total))
                    m2.metric("Spent", fmt_money(spent_total))
                    m3.metric("Remaining", fmt_money(remaining_total))

                    # Quick info
                    items_this = df_items[df_items["phase"] == phase_name].copy()
                    tasks_count = len(items_this)
                    if not items_this.empty:
                        start_min = items_this["start_date"].min()
                        end_max = items_this["end_date"].max()
                        st.caption(f"Tasks: **{tasks_count}**  |  Timeline: **{start_min} → {end_max}**")
                    else:
                        st.caption("Tasks: **0**")

                    # Expand for details
                    with st.expander("Details"):
                        if items_this.empty:
                            st.write("No items in this phase yet.")
                        else:
                            view = items_this[[
                                "task", "start_date", "end_date", "budget_usd", "spent", "remaining", "justification"
                            ]].copy()
                            # Format money columns as strings
                            for col in ["budget_usd", "spent", "remaining"]:
                                view[col] = view[col].apply(fmt_money)
                            # Ensure Arrow doesn't try to coerce to numeric
                            view = cast_cols_to_str(view, ["budget_usd", "spent", "remaining"])
                            st.dataframe(view, use_container_width=True, height=260)

            # Global summary at the bottom
            st.divider()
            total_budget = pd.to_numeric(df_cards["budget_total"], errors="coerce").sum()
            total_spent = pd.to_numeric(df_cards["spent_total"], errors="coerce").sum()
            total_remaining = total_budget - total_spent
            g1, g2, g3 = st.columns(3)
            g1.metric("Total Budget (All Phases)", fmt_money(total_budget))
            g2.metric("Total Spending (All Phases)", fmt_money(total_spent))
            g3.metric("Total Remaining (All Phases)", fmt_money(total_remaining))

    except Error as e:
        st.error(f"Database error (Budgets tab): {e}")

# ======================================================
# 📜 Transactions tab — filterable list
# ======================================================
with tab_transactions:
    st.subheader("Transactions")

    try:
        # Budget dropdown
        budget_lookup = pd.read_sql(
            "SELECT budget_id, budget_line FROM budgets ORDER BY budget_line ASC", conn
        )
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

        # Coerce numeric (in case)
        if "amount_usd" in df_tx.columns:
            df_tx["amount_usd"] = pd.to_numeric(df_tx["amount_usd"], errors="coerce")

        tx_total = float(df_tx["amount_usd"].sum()) if not df_tx.empty else 0.0
        st.metric("Total in view", fmt_money(tx_total))

        show_tx = df_tx.copy()
        if not show_tx.empty:
            show_tx["amount_usd"] = show_tx["amount_usd"].apply(fmt_money)
            show_tx = cast_cols_to_str(show_tx, ["amount_usd"])

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

        # Coerce numerics to avoid stray strings
        for d in (df_budget, df_spend):
            for c in d.columns:
                if c not in ("phase",):
                    d[c] = pd.to_numeric(d[c], errors="coerce")

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
            "phase": "Budget Line / Phase",
            "budget_total": "Budget",
            "spent_total": "USD Amount",
            "remain": "Remain"
        }).copy()

        # Format money columns and force them to string for display (Arrow-safe)
        for col in ["Budget", "USD Amount", "Remain"]:
            show[col] = show[col].apply(fmt_money)
        show = cast_cols_to_str(show, ["Budget", "USD Amount", "Remain"])

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
