import sqlite3
from typing import List, Tuple

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL
);
"""


def get_connection(db_path: str = "budget.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    return conn


def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript(DB_SCHEMA)
    conn.commit()


def add_transaction(conn: sqlite3.Connection, date: str, amount: float, category: str, description: str, ttype: str):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (date, amount, category, description, type) VALUES (?, ?, ?, ?, ?)",
        (date, amount, category, description, ttype),
    )
    conn.commit()
    return cur.lastrowid


def list_transactions(conn: sqlite3.Connection, limit: int = 50) -> List[Tuple]:
    cur = conn.cursor()
    cur.execute("SELECT id, date, amount, category, description, type FROM transactions ORDER BY id DESC LIMIT ?", (limit,))
    return cur.fetchall()


def monthly_summary(conn: sqlite3.Connection, year: int, month: int) -> dict:
    cur = conn.cursor()
    like = f"{year:04d}-{month:02d}%"
    cur.execute(
        "SELECT type, SUM(amount) FROM transactions WHERE date LIKE ? GROUP BY type",
        (like,),
    )
    rows = cur.fetchall()
    summary = {"income": 0.0, "expense": 0.0}
    for typ, total in rows:
        summary[typ] = float(total or 0.0)
    summary["net"] = summary["income"] - summary["expense"]
    return summary


def get_all_transactions(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT id, date, amount, category, description, type FROM transactions ORDER BY id ASC")
    return cur.fetchall()


def import_transactions_from_csv(conn: sqlite3.Connection, csv_text: str) -> dict:
    """Import transactions from CSV text. Returns dict with counts and errors.

    CSV expected columns: date, amount, category, description, type
    """
    import io
    import csv

    reader = csv.DictReader(io.StringIO(csv_text))
    imported = 0
    errors = []
    for i, row in enumerate(reader, start=2):
        try:
            date = row.get("date")
            if not date:
                raise ValueError("missing date")
            if "amount" not in row or row.get("amount") == "":
                raise ValueError("missing amount")
            amount = float(row.get("amount"))
            category = row.get("category", "General") or "General"
            description = row.get("description", "") or ""
            ttype = row.get("type")
            if ttype not in ("income", "expense"):
                raise ValueError("type must be 'income' or 'expense'")
            add_transaction(conn, date, amount, category, description, ttype)
            imported += 1
        except Exception as e:
            errors.append({"line": i, "row": row, "error": str(e)})
    return {"imported": imported, "errors": errors}


def category_totals(conn: sqlite3.Connection, year: int, month: int) -> dict:
    cur = conn.cursor()
    like = f"{year:04d}-{month:02d}%"
    cur.execute(
        "SELECT category, SUM(amount) FROM transactions WHERE date LIKE ? AND type='expense' GROUP BY category",
        (like,),
    )
    expense_rows = cur.fetchall()
    cur.execute(
        "SELECT category, SUM(amount) FROM transactions WHERE date LIKE ? AND type='income' GROUP BY category",
        (like,),
    )
    income_rows = cur.fetchall()
    return {
        "expense": {r[0]: float(r[1] or 0.0) for r in expense_rows},
        "income": {r[0]: float(r[1] or 0.0) for r in income_rows},
    }
