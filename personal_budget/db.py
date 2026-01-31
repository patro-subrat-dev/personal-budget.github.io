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
