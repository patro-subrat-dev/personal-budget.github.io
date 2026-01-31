import streamlit as st
import datetime
from personal_budget.db import get_connection, init_db, add_transaction, list_transactions, monthly_summary

DB_PATH = "budget.db"

st.title("Personal Budget — Simple Tracker 🧾")

st.markdown("A tiny Streamlit UI to add transactions and view lists/summaries.")

# Add transaction form
with st.form("add_txn"):
    ttype = st.selectbox("Type", ["income", "expense"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    category = st.text_input("Category", value="General")
    desc = st.text_input("Description", value="")
    date = st.date_input("Date", value=datetime.date.today())
    submitted = st.form_submit_button("Add transaction")

    if submitted:
        conn = get_connection(DB_PATH)
        init_db(conn)
        add_transaction(conn, date.isoformat(), float(amount), category, desc, ttype)
        st.success("Transaction added")

st.header("Recent transactions")
conn = get_connection(DB_PATH)
init_db(conn)
rows = list_transactions(conn, limit=100)
if rows:
    table = [
        {"id": r[0], "date": r[1], "type": r[5], "amount": r[2], "category": r[3], "desc": r[4]}
        for r in rows
    ]
    st.table(table)
else:
    st.info("No transactions yet. Add one above!")

st.header("Monthly summary")
col1, col2 = st.columns(2)
with col1:
    year = st.number_input("Year", min_value=2000, max_value=2100, value=datetime.date.today().year)
with col2:
    month = st.number_input("Month", min_value=1, max_value=12, value=datetime.date.today().month)

if st.button("Show summary"):
    s = monthly_summary(conn, int(year), int(month))
    st.metric("Income", f"{s['income']:.2f}")
    st.metric("Expense", f"{s['expense']:.2f}")
    st.metric("Net", f"{s['net']:.2f}")
