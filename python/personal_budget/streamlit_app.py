import streamlit as st
import datetime
import io
import csv
from personal_budget.db import get_connection, init_db, add_transaction, list_transactions, monthly_summary, get_all_transactions, category_totals

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

    # Category breakdown
    cats = category_totals(conn, int(year), int(month))
    if cats["expense"]:
        st.subheader("Expense by category")
        for c, amt in cats["expense"].items():
            st.write(f"- {c}: {amt:.2f}")
    if cats["income"]:
        st.subheader("Income by category")
        for c, amt in cats["income"].items():
            st.write(f"- {c}: {amt:.2f}")

# Import / Export CSV
st.header("Import / Export CSV")
# Download template
with open("..\\PERSONAL_BUDGET_TEMPLATE.csv", "r", encoding="utf-8") as f:
    template = f.read()
st.download_button("Download CSV template", template.encode("utf-8"), file_name="PERSONAL_BUDGET_TEMPLATE.csv", mime="text/csv")

uploaded = st.file_uploader("Upload CSV (date,amount,category,description,type)", type=["csv"]) 
if uploaded:
    text = uploaded.read().decode("utf-8")
    conn = get_connection(DB_PATH)
    init_db(conn)
    result = import_transactions_from_csv(conn, text)
    if result["imported"]:
        st.success(f"Imported {result['imported']} transactions")
    if result["errors"]:
        st.warning(f"{len(result['errors'])} rows failed to import")
        st.subheader("Import errors")
        st.table([{"line": e["line"], "error": e["error"], "row": e["row"]} for e in result["errors"]])

# Export all transactions to CSV
if st.button("Export transactions to CSV"):
    rows_all = get_all_transactions(conn)
    import pandas as pd
    df = pd.DataFrame(rows_all, columns=["id", "date", "amount", "category", "description", "type"])
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv_bytes, file_name=f"transactions_all.csv", mime="text/csv")

# Visual reports
st.header("Reports & Charts")
import pandas as pd
rows_all = get_all_transactions(conn)
if rows_all:
    df = pd.DataFrame(rows_all, columns=["id", "date", "amount", "category", "description", "type"])
    df["date"] = pd.to_datetime(df["date"])

    # Expense by category
    exp_by_cat = df[df["type"] == "expense"].groupby("category")["amount"].sum().sort_values(ascending=False)
    if not exp_by_cat.empty:
        st.subheader("Expense by category")
        st.bar_chart(exp_by_cat)

    # Monthly trend
    df["ym"] = df["date"].dt.to_period("M").dt.to_timestamp()
    trend = df.groupby(["ym", "type"])['amount'].sum().unstack(fill_value=0)
    if not trend.empty:
        st.subheader("Monthly trend (income vs expense)")
        st.line_chart(trend)
else:
    st.info("No data for reports yet.")
