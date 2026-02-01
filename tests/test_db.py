import sys
from pathlib import Path
import tempfile
import sqlite3

# Ensure package import works when running tests from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from personal_budget import db


def test_add_and_list_transactions(tmp_path):
    db_file = tmp_path / "test_budget.db"
    conn = db.get_connection(str(db_file))
    db.init_db(conn)
    tid1 = db.add_transaction(conn, "2026-01-01", 100.0, "Salary", "Jan salary", "income")
    tid2 = db.add_transaction(conn, "2026-01-02", 25.5, "Food", "Lunch", "expense")
    rows = db.list_transactions(conn)
    assert len(rows) == 2
    assert rows[0][0] == tid2
    assert rows[1][0] == tid1


def test_monthly_summary(tmp_path):
    db_file = tmp_path / "test_budget2.db"
    conn = db.get_connection(str(db_file))
    db.init_db(conn)
    db.add_transaction(conn, "2026-01-01", 1000.0, "Salary", "Jan salary", "income")
    db.add_transaction(conn, "2026-01-05", 200.0, "Groceries", "Weekly shop", "expense")
    s = db.monthly_summary(conn, 2026, 1)
    assert s["income"] == 1000.0
    assert s["expense"] == 200.0
    assert s["net"] == 800.0
