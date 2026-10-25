"""SQLite connection helpers and ``flask init-db`` CLI."""

import sqlite3
from pathlib import Path

import click
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    """Return a connection for the current request (one per request)."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        # Must run on every connection; SQLite does not persist this setting.
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_e=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


# Income first; expenses M → S → T → Other (O) always last.
CATEGORIES_ORDER_SQL = """
    SELECT code, name, kind FROM categories
    ORDER BY
        CASE kind WHEN 'income' THEN 0 ELSE 1 END,
        CASE code
            WHEN 'M' THEN 1
            WHEN 'S' THEN 2
            WHEN 'T' THEN 3
            WHEN 'O' THEN 4
            ELSE 5
        END
"""


def get_categories():
    """All categories in display order (Other last among expenses)."""
    return get_db().execute(CATEGORIES_ORDER_SQL).fetchall()


def init_db() -> None:
    """Create tables and seed categories from schema.sql."""
    db = get_db()
    schema_path = Path(current_app.root_path) / "schema.sql"
    with open(schema_path, encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()


def init_app(app) -> None:
    """Register teardown and CLI on the Flask app."""
    app.teardown_appcontext(close_db)

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Create the database file and apply schema.sql."""
        # Ensure the instance folder exists before connecting.
        db_path = Path(app.config["DATABASE"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with app.app_context():
            init_db()
        click.echo(f"Initialized the database at {db_path}.")

