# Personal Budget Tracker

A simple, beginner-friendly Python CLI to track income and expenses. Data is stored in a local SQLite database (`budget.db`).

## Features ✅
- Add income/expense transactions
- List recent transactions
- Monthly summary (total income, total expense, net)

## Quick start 🚀
1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Initialize the DB (first run will create `budget.db` automatically):

```bash
python -m personal_budget.main add --type expense --amount 12.50 --category Food --desc "Lunch"
```

3. List transactions:

```bash
python -m personal_budget.main list
```

4. Monthly summary:

```bash
python -m personal_budget.main summary --year 2026 --month 1
```

---

## Streamlit UI (optional)

Start the simple web UI with Streamlit:

```bash
# from workspace root
streamlit run python/personal_budget/personal_budget/streamlit_app.py
```
or
```bash
& C:/Users/rars4/SUBRAT/.venv/Scripts/python.exe -m streamlit run c:/Users/rars4/SUBRAT/python/personal_budget/streamlit_app.py
```

This opens a small web UI where you can add transactions and view summaries.


## Tests

Run tests with:

```bash
pytest -q
```

## License

MIT
