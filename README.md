# Expense Tracker

A small web app for logging what you spend and seeing where your money goes each month.

Built with [Flask](https://flask.palletsprojects.com/) and SQLite. There's no JavaScript framework or build step, and it has a single Python dependency.

## Features

- Add expenses with an amount, category, date and optional note
- Browse month by month with a running total
- Bar chart of spending by category for the selected month
- Delete expenses with a two-click confirm
- Responsive layout with automatic light and dark mode

## Getting started

You need Python 3.10 or newer.

```bash
git clone https://github.com/ggfret/expense-tracker.git
cd expense-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5050.

The database file `expenses.db` is created automatically on first run and is ignored by git, so your data stays on your machine.

## Project structure

```
app.py              Flask routes and database queries
schema.sql          Table definition
templates/          HTML pages (Jinja templates)
static/style.css    Styling
```

## How it works

Each page is a Flask route in `app.py`. The home page runs two SQL queries for the selected month: one that lists the expenses, and a `GROUP BY category` query that powers the total and the chart. Forms post to `/add` and `/delete/<id>`, which update the database and redirect back to the month you were viewing.

## Ideas for later

- Edit an existing expense
- Export a month to CSV
- Custom categories and a currency setting
- Deploy it online with user accounts

## License

[MIT](LICENSE)
