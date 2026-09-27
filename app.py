import sqlite3
from datetime import date
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


@app.route("/")
def index():
    count = get_db().execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
    return render_template(
        "index.html",
        categories=CATEGORIES,
        today=date.today().isoformat(),
        count=count,
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
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5050)
