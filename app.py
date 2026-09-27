import sqlite3
from datetime import date, datetime
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "expenses.db"
CATEGORIES = ["Food", "Rent", "Transport", "Shopping", "Bills", "Fun", "Other"]

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.executescript((BASE_DIR / "schema.sql").read_text())


def shift_month(month, delta):
    year, mon = map(int, month.split("-"))
    index = year * 12 + (mon - 1) + delta
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


@app.route("/")
def index():
    month = request.args.get("month", "")
    try:
        month_start = datetime.strptime(month, "%Y-%m")
    except ValueError:
        month_start = datetime.now()
        month = month_start.strftime("%Y-%m")

    db = get_db()
    expenses = db.execute(
        """SELECT id, amount, category, spent_on, note FROM expenses
           WHERE substr(spent_on, 1, 7) = ?
           ORDER BY spent_on DESC, id DESC""",
        (month,),
    ).fetchall()
    by_category = db.execute(
        """SELECT category, SUM(amount) AS total, COUNT(*) AS n FROM expenses
           WHERE substr(spent_on, 1, 7) = ?
           GROUP BY category
           ORDER BY total DESC""",
        (month,),
    ).fetchall()

    return render_template(
        "index.html",
        categories=CATEGORIES,
        today=date.today().isoformat(),
        expenses=expenses,
        by_category=by_category,
        total=sum(row["total"] for row in by_category),
        biggest=by_category[0]["total"] if by_category else 0,
        month=month,
        month_label=month_start.strftime("%B %Y"),
        prev_month=shift_month(month, -1),
        next_month=shift_month(month, 1),
    )


@app.post("/add")
def add_expense():
    try:
        amount = float(request.form["amount"])
        spent_on = date.fromisoformat(request.form["spent_on"]).isoformat()
    except (KeyError, ValueError):
        abort(400)
    category = request.form.get("category")
    if amount <= 0 or category not in CATEGORIES:
        abort(400)

    db = get_db()
    db.execute(
        "INSERT INTO expenses (amount, category, spent_on, note) VALUES (?, ?, ?, ?)",
        (amount, category, spent_on, request.form.get("note", "").strip()),
    )
    db.commit()
    return redirect(url_for("index", month=spent_on[:7]))


@app.post("/delete/<int:expense_id>")
def delete_expense(expense_id):
    db = get_db()
    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    return redirect(url_for("index", month=request.args.get("month")))


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5050)
