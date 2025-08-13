import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime
from decimal import Decimal

# ---------------------------------------
# Page setup
# ---------------------------------------
st.set_page_config(page_title="Transaction Entry", layout="wide")
st.title("💸 Transaction Entry")

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

def money(x):
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return x

# -----------------------------
# Load budgets for dropdown
# -----------------------------
try:
    budgets_df = pd.read_sql(
        "SELECT budget_id, budget_line, task FROM budgets ORDER BY budget_line, budget_id",
        conn
    )
except Error as e:
    st.error(f"Failed to load budgets: {e}")
    budgets_df = pd.DataFrame(columns=["budget_id", "budget_line", "task"])

# Map for display
if not budgets_df.empty:
    budgets_df["display"] = budgets_df.apply(
        lambda r: f"{r['budget_line']} — #{r['budget_id']}: {r['task'][:60]}",
        axis=1
    )
else:
    st.info("No budgets found. Please add budgets first.")
    budgets_df["display"] = []

# ======================================================
# Single-entry form
# ======================================================
st.subheader("Add a Single Transaction")

with st.form("tx_form", clear_on_submit=True):
    colA, colB = st.columns([2, 1])
    with colA:
        sel = st.selectbox(
            "Budget (Phase / Item)",
            options=budgets_df["display"].tolist(),
            index=0 if len(budgets_df) > 0 else None,
            placeholder="Select a budget..."
        )
    with colB:
        tx_date = st.date_input("Date", value=date.today(), format="YYYY-MM-DD")

    description = st.text_input("Description", placeholder="What is this transaction?")
    amount = st.number_input("Amount (USD)", min_value=0.00, step=0.01, format="%.2f")
    notes = st.text_area("Notes (optional)", placeholder="Method, Original IQD, or any comments")

    submitted = st.form_submit_button("➕ Add Transaction", type="primary", use_container_width=True)

    if submitted:
        if budgets_df.empty:
            st.error("No budgets available.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            try:
                # Resolve selected budget_id
                row = budgets_df.loc[budgets_df["display"] == sel].iloc[0]
                budget_id = int(row["budget_id"])

                sql = """
                    INSERT INTO transactions
                    (budget_id, transaction_date, description, amount_usd, notes)
                    VALUES (%s, %s, %s, %s, %s)
                """
                params = [
                    budget_id,
                    tx_date,  # date object is OK for mysql-connector
                    description if description.strip() else None,
                    Decimal(f"{amount:.2f}"),
                    notes if notes.strip() else None,
                ]
                cur = conn.cursor()
                cur.execute(sql, params)
                st.success(f"Saved ✅  (Budget #{budget_id} — {row['budget_line']})")
                cur.close()
            except Error as e:
                st.error(f"Insert failed: {e}")

# ======================================================
# Optional: Quick CSV add (same schema or Budget name)
# ======================================================
with st.expander("📥 Bulk Add from CSV (Optional)"):
    st.caption("Accepted headers (preferred): **budget_id, transaction_date (YYYY-MM-DD), description, amount_usd, notes**")
    st.caption("Also supported: **Budget** (budget_line name) instead of budget_id.")
    up = st.file_uploader("Upload CSV", type=["csv"])
    if up is not None:
        try:
            df = pd.read_csv(up)
        except Exception as e:
            st.error(f"CSV read error: {e}")
            df = pd.DataFrame()

        # Normalize columns
        cols = {c.lower().strip(): c for c in df.columns}
        # If Budget name provided, map to budget_id
        if "budget" in cols and "budget_id" not in cols:
            # Build lookup map: budget_line lower -> budget_id(s)
            phase_map = {}
            for _, r in budgets_df.iterrows():
                key = str(r["budget_line"]).strip().lower()
                phase_map.setdefault(key, []).append(int(r["budget_id"]))

            # Create budget_id by first matching id for given phase name
            df["budget_id"] = df[cols["budget"]].apply(
                lambda v: phase_map.get(str(v).strip().lower(), [None])[0]
            )

        # Coerce/rename to expected names
        if "budget_id" not in df.columns and "budget_id" in cols:
            df.rename(columns={cols["budget_id"]: "budget_id"}, inplace=True)
        if "transaction_date" not in df.columns and "date" in cols:
            df.rename(columns={cols["date"]: "transaction_date"}, inplace=True)
        if "description" not in df.columns and "details" in cols:
            df.rename(columns={cols["details"]: "description"}, inplace=True)
        if "amount_usd" not in df.columns and "usd" in cols:
            df.rename(columns={cols["usd"]: "amount_usd"}, inplace=True)
        if "notes" not in df.columns and "method" in cols:
            # Combine method + existing notes if any
            method_col = cols["method"]
            df["notes"] = df.get("notes", "").astype(str).str.strip()
            df["notes"] = df.apply(
                lambda r: (f"Method: {r[method_col]}" if pd.notna(r[method_col]) and str(r[method_col]).strip() else "")
                if r.get("notes","") == "" else
                (r["notes"] + ("; " if r["notes"] else "") + (f"Method: {r[method_col]}" if pd.notna(r[method_col]) and str(r[method_col]).strip() else "")),
                axis=1
            )

        # Clean types
        def to_date(v):
            try:
                return pd.to_datetime(v).date()
            except Exception:
                return None

        def to_decimal(v):
            try:
                return Decimal(str(v).replace(",", ""))
            except Exception:
                return None

        df["budget_id"] = pd.to_numeric(df.get("budget_id"), errors="coerce").astype("Int64")
        df["transaction_date"] = df.get("transaction_date", "").apply(to_date)
        df["amount_usd"] = df.get("amount_usd", "").apply(to_decimal)
        if "description" in df.columns:
            df["description"] = df["description"].astype(str).str.strip()
        if "notes" in df.columns:
            df["notes"] = df["notes"].astype(str).str.strip()

        # Validate required
        req_mask = (
            df["budget_id"].notna() &
            df["transaction_date"].notna() &
            df["amount_usd"].notna()
        )
        bad = df[~req_mask]
        good = df[req_mask].copy()

        st.write("Preview:")
        st.dataframe(df, use_container_width=True)

        if not bad.empty:
            st.warning(f"{len(bad)} rows skipped (missing budget_id / date / amount).")
            st.dataframe(bad, use_container_width=True)

        if not good.empty and st.button("Insert CSV Transactions", use_container_width=True):
            try:
                cur = conn.cursor()
                sql = """
                    INSERT INTO transactions
                    (budget_id, transaction_date, description, amount_usd, notes)
                    VALUES (%s, %s, %s, %s, %s)
                """
                data = [
                    (
                        int(row["budget_id"]),
                        row["transaction_date"],
                        (row["description"] if pd.notna(row["description"]) and row["description"].strip() else None),
                        row["amount_usd"],
                        (row["notes"] if pd.notna(row["notes"]) and row["notes"].strip() else None),
                    )
                    for _, row in good.iterrows()
                ]
                cur.executemany(sql, data)
                st.success(f"Inserted {cur.rowcount} transactions ✅")
                cur.close()
            except Error as e:
                st.error(f"Bulk insert failed: {e}")

# ======================================================
# Recent transactions log
# ======================================================
st.divider()
st.subheader("Recent Transactions")

try:
    recent_q = """
        SELECT
            t.transaction_id,
            t.transaction_date,
            b.budget_line,
            t.description,
            t.amount_usd,
            t.notes
        FROM transactions t
        JOIN budgets b ON b.budget_id = t.budget_id
        ORDER BY t.transaction_date DESC, t.transaction_id DESC
        LIMIT 50
    """
    recent_df = pd.read_sql(recent_q, conn)
    if not recent_df.empty:
        view = recent_df.copy()
        view["amount_usd"] = view["amount_usd"].apply(money)
        st.dataframe(view, use_container_width=True)
    else:
        st.info("No transactions yet.")
except Error as e:
    st.error(f"Could not load recent transactions: {e}")

# ---------------------------------------
# Close connection
# ---------------------------------------
try:
    conn.close()
except:
    pass
