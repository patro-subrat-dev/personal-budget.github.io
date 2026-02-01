import click
import datetime
from .db import get_connection, init_db, add_transaction, list_transactions, monthly_summary

DB_DEFAULT = "budget.db"


@click.group()
@click.option("--db", default=DB_DEFAULT, help="Path to sqlite DB file")
@click.pass_context
def cli(ctx, db):
    ctx.ensure_object(dict)
    ctx.obj["db"] = db


@cli.command()
@click.option("--type", type=click.Choice(["income", "expense"]), required=True)
@click.option("--amount", type=float, required=True)
@click.option("--category", type=str, default="General")
@click.option("--desc", type=str, default="")
@click.option("--date", type=str, default=None, help="Date in YYYY-MM-DD (default: today)")
@click.pass_context
def add(ctx, type, amount, category, desc, date):
    db = ctx.obj["db"]
    conn = get_connection(db)
    init_db(conn)
    if not date:
        date = datetime.date.today().isoformat()
    rowid = add_transaction(conn, date, amount, category, desc, type)
    click.echo(f"Added transaction id={rowid}")


@cli.command(name="list")
@click.option("--limit", default=50, type=int)
@click.pass_context
def _list(ctx, limit):
    db = ctx.obj["db"]
    conn = get_connection(db)
    init_db(conn)
    rows = list_transactions(conn, limit)
    for r in rows:
        click.echo(f"{r[0]:>3} | {r[1]} | {r[5]:7} | {r[2]:8.2f} | {r[3]} | {r[4]}")


@cli.command()
@click.option("--year", type=int, required=True)
@click.option("--month", type=int, required=True)
@click.pass_context
def summary(ctx, year, month):
    db = ctx.obj["db"]
    conn = get_connection(db)
    init_db(conn)
    s = monthly_summary(conn, year, month)
    click.echo(f"Year: {year}, Month: {month:02d}")
    click.echo(f"Income:  {s['income']:.2f}")
    click.echo(f"Expense: {s['expense']:.2f}")
    click.echo(f"Net:     {s['net']:.2f}")
