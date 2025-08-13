import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import date

def render_finance():
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

    tab_budgets, tab_transactions, tab_summary, tab_entry, tab_edit = st.tabs(
        ["📊 Budgets", "📜 Transactions", "📈 Phase Summary", "➕ New Transaction", "📝 Edit Budgets"]
    )

    def money(x):
        try:
            return f"${float(x):,.2f}"
        except Exception:
            return x

    # ======================================================
    # 📊 Budgets tab — VERTICAL PHASE CARDS (one per row)
    # ======================================================
    with tab_budgets:
        st.subheader("Budgets by Phase")

        try:
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

            df_cards = pd.merge(df_phase_budget, df_phase_spent, on="phase", how="left").fillna({"spent_total": 0})
            df_cards["remaining_total"] = df_cards["budget_total"] - df_cards["spent_total"]

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

            if df_cards.empty:
                st.info("No budgets found yet.")
            else:
                for _, row in df_cards.iterrows():
                    phase_name = row["phase"]
                    budget_total = float(row["budget_total"])
                    spent_total = float(row["spent_total"])
                    remaining_total = float(row["remaining_total"])

                    with st.container(border=True):
                        st.markdown(f"### {phase_name}")

                        m1, m2, m3 = st.columns(3)
                        m1.metric("Budget", money(budget_total))
                        m2.metric("Spent", money(spent_total))
                        m3.metric("Remaining", money(remaining_total))

                        items_this = df_items[df_items["phase"] == phase_name].copy()
                        tasks_count = len(items_this)
                        if not items_this.empty:
                            start_min = items_this["start_date"].min()
                            end_max = items_this["end_date"].max()
                            st.caption(f"Tasks: **{tasks_count}**  |  Timeline: **{start_min} → {end_max}**")
                        else:
                            st.caption("Tasks: **0**")

                        with st.expander("Details"):
                            if items_this.empty:
                                st.write("No items in this phase yet.")
                            else:
                                view = items_this[[
                                    "task", "start_date", "end_date", "budget_usd", "spent", "remaining", "justification"
                                ]].copy()
                                for col in ["budget_usd", "spent", "remaining"]:
                                    view[col] = view[col].apply(money)
                                st.dataframe(view, use_container_width=True, height=260)

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
            budget_lookup = pd.read_sql("SELECT budget_id, budget_line, task FROM budgets ORDER BY budget_line, budget_id ASC", conn)
            options = ["(All)"] + budget_lookup["budget_line"].tolist()
            sel_budget_name = st.selectbox("Filter by Budget Line", options, index=0)

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

    # ======================================================
    # ➕ New Transaction tab — checkbox table + form
    # ======================================================
    with tab_entry:
        st.subheader("Add New Transaction")

        try:
            q_budget_table = """
                SELECT
                    b.budget_id,
                    b.budget_line,
                    b.task,
                    COALESCE(b.budget_usd, 0) AS budget_usd,
                    COALESCE(x.spent, 0) AS spent
                FROM budgets b
                LEFT JOIN (
                    SELECT budget_id, SUM(amount_usd) AS spent
                    FROM transactions
                    GROUP BY budget_id
                ) x ON x.budget_id = b.budget_id
                ORDER BY b.budget_line, b.budget_id
            """
            df_budgets = pd.read_sql(q_budget_table, conn)

            if df_budgets.empty:
                st.info("No budgets available. Please add budgets first.")
            else:
                df_budgets["Select"] = False
                show = df_budgets.copy()
                show["Budget (USD)"] = show["budget_usd"].apply(money)
                show["Spent"] = show["spent"].apply(money)
                show = show[["Select", "budget_id", "budget_line", "task", "Budget (USD)", "Spent"]]

                st.caption("Select ONE budget (phase/task):")
                edited = st.data_editor(
                    show,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Select": st.column_config.CheckboxColumn(default=False, help="Tick to select this budget"),
                        "budget_id": st.column_config.NumberColumn("Budget ID", disabled=True),
                        "budget_line": st.column_config.TextColumn("Phase", disabled=True),
                        "task": st.column_config.TextColumn("Task", disabled=True),
                        "Budget (USD)": st.column_config.TextColumn(disabled=True),
                        "Spent": st.column_config.TextColumn(disabled=True),
                    }
                )

                selected_rows = edited[edited["Select"] == True]
                selected_count = len(selected_rows)
                selected_budget_id = int(selected_rows["budget_id"].iloc[0]) if selected_count == 1 else None

                if selected_count == 0:
                    st.info("No budget selected yet.")
                elif selected_count > 1:
                    st.warning("Please select **only one** budget to proceed.")
                else:
                    st.success(f"Selected Budget ID: {selected_budget_id}")

                st.markdown("---")

                c1, c2 = st.columns(2)
                with c1:
                    tx_date = st.date_input("Transaction date", value=date.today())
                    amount = st.number_input("Amount (USD)", min_value=0.00, step=0.01, format="%.2f")
                with c2:
                    description = st.text_input("Description", value="", placeholder="e.g., Food & transport")
                    notes = st.text_input("Notes (optional)", value="", placeholder="Method: Cash; IQD: 1,000,000")

                if st.button("Save Transaction", type="primary"):
                    if selected_count != 1:
                        st.error("Please select exactly one budget in the table above.")
                    elif amount <= 0:
                        st.error("Amount must be greater than 0.")
                    else:
                        try:
                            cur = conn.cursor()
                            cur.execute(
                                """
                                INSERT INTO transactions
                                (budget_id, transaction_date, description, amount_usd, notes)
                                VALUES (%s, %s, %s, %s, %s)
                                """,
                                (selected_budget_id, tx_date, description or None, amount, notes or None)
                            )
                            st.success("Transaction saved ✅")
                        except Error as e:
                            st.error(f"Insert failed: {e}")
                        finally:
                            try:
                                cur.close()
                            except:
                                pass

                with st.expander("Recent Transactions"):
                    preview_q = """
                        SELECT t.transaction_id, b.budget_line, t.transaction_date, t.description, t.amount_usd, t.notes
                        FROM transactions t
                        JOIN budgets b ON b.budget_id = t.budget_id
                        ORDER BY t.transaction_id DESC
                        LIMIT 20
                    """
                    df_recent = pd.read_sql(preview_q, conn)
                    if not df_recent.empty:
                        show_recent = df_recent.copy()
                        show_recent["amount_usd"] = show_recent["amount_usd"].apply(money)
                        st.dataframe(show_recent, use_container_width=True)
                    else:
                        st.caption("No transactions yet.")

        except Error as e:
            st.error(f"Database error (New Transaction tab): {e}")

    # ======================================================
    # 📝 Edit Budgets tab — inline cell editing & SAVE
    # ======================================================
    with tab_edit:
        st.subheader("Edit Budgets (inline)")

        try:
            # Load current budgets
            src = pd.read_sql(
                """
                SELECT
                    budget_id,
                    budget_line,
                    task,
                    sub_tasks,
                    start_date,
                    end_date,
                    budget_usd,
                    justification
                FROM budgets
                ORDER BY budget_id ASC
                """,
                conn
            )

            st.caption("Edit any field below (except **budget_id**). Then click **Save Changes**.")
            edited = st.data_editor(
                src,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "budget_id": st.column_config.NumberColumn("budget_id", disabled=True, help="Primary key"),
                    "budget_line": st.column_config.TextColumn("budget_line"),
                    "task": st.column_config.TextColumn("task"),
                    "sub_tasks": st.column_config.TextColumn("sub_tasks", help="Optional"),
                    "start_date": st.column_config.DateColumn("start_date", help="YYYY-MM-DD"),
                    "end_date": st.column_config.DateColumn("end_date", help="YYYY-MM-DD"),
                    "budget_usd": st.column_config.NumberColumn("budget_usd", step=0.01, format="%.2f"),
                    "justification": st.column_config.TextColumn("justification", help="Optional"),
                }
            )

            def _norm(v):
                """Normalize empty strings/NaN to None for DB, cast types."""
                if pd.isna(v) or (isinstance(v, str) and v.strip() == ""):
                    return None
                return v

            if st.button("Save Changes", type="primary"):
                try:
                    updates = []
                    for i in range(len(edited)):
                        row_new = edited.iloc[i]
                        row_old = src.iloc[i]

                        # Check if anything changed (excluding None vs "" noise)
                        changed = False
                        for col in ["budget_line", "task", "sub_tasks", "start_date", "end_date", "budget_usd", "justification"]:
                            v_new = _norm(row_new[col])
                            v_old = _norm(row_old[col])
                            if str(v_new) != str(v_old):
                                changed = True
                                break

                        if not changed:
                            continue

                        updates.append((
                            _norm(row_new["budget_line"]),
                            _norm(row_new["task"]),
                            _norm(row_new["sub_tasks"]),
                            _norm(row_new["start_date"]),
                            _norm(row_new["end_date"]),
                            float(row_new["budget_usd"]) if not pd.isna(row_new["budget_usd"]) else None,
                            _norm(row_new["justification"]),
                            int(row_new["budget_id"])
                        ))

                    if not updates:
                        st.info("No changes detected.")
                    else:
                        cur = conn.cursor()
                        cur.executemany(
                            """
                            UPDATE budgets
                            SET budget_line=%s,
                                task=%s,
                                sub_tasks=%s,
                                start_date=%s,
                                end_date=%s,
                                budget_usd=%s,
                                justification=%s
                            WHERE budget_id=%s
                            """,
                            updates
                        )
                        st.success(f"Saved changes for {cur.rowcount} row(s) ✅")
                        try:
                            cur.close()
                        except:
                            pass
                except Error as e:
                    st.error(f"Update failed: {e}")

        except Error as e:
            st.error(f"Database error (Edit Budgets): {e}")

    # ---------------------------------------
    # Close connection
    # ---------------------------------------
    try:
        conn.close()
    except:
        pass
