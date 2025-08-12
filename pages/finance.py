import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date

st.set_page_config(page_title="Finance", layout="wide")
st.title("💼 Finance")

# ---- Open a connection using st.secrets["mysql"] ----
cfg = st.secrets["mysql"]
conn = mysql.connector.connect(
    host=cfg["host"],
    port=int(cfg["port"]),
    user=cfg["user"],
    password=cfg["password"],
    database=cfg["database"],
    autocommit=True,
)

tab_budgets, tab_transactions = st.tabs(["📊 Budgets", "📜 Transactions"])

def money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return x

# =========================
# 📊 Budgets tab
# =========================
with tab_budgets:
    st.subheader("Overall Budget Overview")

    try:
        total_budget_df = pd.read_sql("SELECT COALESCE(SUM(budget_usd),0) AS total_budget FROM budgets", conn)
        total_spend_df  = pd.read_sql("SELECT COALESCE(SUM(amount_usd),0) AS total_spend FROM transactions", conn)
        total_budget = float(total_budget_df.iloc[0]["total_budget"]) if not total_budget_df.empty else 0.0
        total_spend  = float(total_spend_df.iloc[0]["total_spend"]) if not total_spend_df.empty else 0.0
        total_remaining = total_budget - total_spend

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Budget", money(total_budget))
        c2.metric("Total Spending", money(total_spend))
        c3.metric("Remaining", money(total_remaining))

        st.divider()

        budgets_q = """
            SELECT
                b.budget_id,
                b.budget_line,
                b.task,
                b.sub_tasks,
                b.start_date,
                b.end_date,
                b.budget_usd,
                COALESCE(t.spent, 0) AS spent,
                (COALESCE(b.budget_usd,0) - COALESCE(t.spent,0)) AS remaining,
                b.justification
            FROM budgets b
            LEFT JOIN (
                SELECT budget_id, SUM(amount_usd) AS spent
                FROM transactions
                GROUP BY budget_id
            ) t ON b.budget_id = t.budget_id
            ORDER BY b.budget_id ASC
        """
        df_budgets = pd.read_sql(budgets_q, conn)

        with st.expander("Filter"):
            q = st.text_input("Search (Budget Line / Task contains…)", "")
            if q.strip():
                mask = (
                    df_budgets["budget_line"].str.contains(q, case=False, na=False) |
                    df_budgets["task"].str_contains(q, case=False, na=False)
                    if hasattr(df_budgets["task"], "str_contains") else
                    df_budgets["task"].str.contains(q, case=False, na=False)
                )
                df_view = df_budgets[mask].copy()
            else:
                df_view = df_budgets.copy()

        show_df = df_view.copy()
        for col in ["budget_usd", "spent", "remaining"]:
            if col in show_df.columns:
                show_df[col] = show_df[col].apply(money)

        st.dataframe(
            show_df[[
                "budget_id", "budget_line", "task", "start_date", "end_date",
                "budget_usd", "spent", "remaining", "justification"
            ]],
            use_container_width=True,
        )

        csv_b = df_view.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Budgets CSV", data=csv_b, file_name="budgets_overview.csv", mime="text/csv")

    except Error as e:
        st.error(f"Database error (budgets): {e}")

# =========================
# 📜 Transactions tab
# =========================
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

        csv_t = df_tx.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Transactions CSV", data=csv_t, file_name="transactions_view.csv", mime="text/csv")

    except Error as e:
        st.error(f"Database error (transactions): {e}")
    finally:
        try:
            conn.close()
        except:
            pass
