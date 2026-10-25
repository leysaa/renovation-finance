"""Application factory, configuration, and blueprint registration."""

import os
from pathlib import Path

from flask import Flask, redirect, url_for
from flask_login import login_required

import auth
import db
import charts
import export_data
import projects
import transactions


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # Local dev fallback only — set SECRET_KEY in production (e.g. PythonAnywhere).
    default_secret = "dev-only-change-me"
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", default_secret),
        DATABASE=str(Path(app.instance_path) / "building.db"),
    )

    if test_config is not None:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    auth.init_app(app)
    projects.init_app(app)
    transactions.init_app(app)
    charts.init_app(app)
    export_data.init_app(app)

    @app.template_filter("eur")
    def eur_filter(value):
        """Format amounts in euros (always 2 decimals)."""
        if value is None:
            return "—"
        return f"€{value:.2f}"

    @app.route("/")
    @login_required
    def index():
        """Home redirects to the project list."""
        return redirect(url_for("projects.index"))

    return app
