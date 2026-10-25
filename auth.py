"""Authentication blueprint, Flask-Login, and ``flask create-user`` CLI."""

import sqlite3
from urllib.parse import urljoin, urlparse

import click
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

from db import get_db

bp = Blueprint("auth", __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to continue."
login_manager.login_message_category = "info"


class User(UserMixin):
    """Minimal user object for Flask-Login (loaded from SQLite)."""

    def __init__(self, id_: int, username: str) -> None:
        self.id = id_
        self.username = username


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    row = get_db().execute(
        "SELECT id, username FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if row is None:
        return None
    return User(row["id"], row["username"])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


def _is_safe_url(target: str | None) -> bool:
    """Only allow redirects back to this host (avoid open redirects)."""
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        row = get_db().execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (form.username.data.strip(),),
        ).fetchone()
        if row is None or not check_password_hash(row["password_hash"], form.password.data):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(User(row["id"], row["username"]))
        next_url = request.args.get("next")
        if _is_safe_url(next_url):
            return redirect(next_url)
        return redirect(url_for("index"))

    return render_template("auth/login.html", form=form)


@bp.route("/me")
@login_required
def me():
    return render_template("auth/me.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def init_app(app) -> None:
    """Wire LoginManager, blueprint, and CLI onto the application."""
    login_manager.init_app(app)
    app.register_blueprint(bp)

    @app.cli.command("create-user")
    @click.argument("username")
    def create_user_command(username: str) -> None:
        """Create a user; prompts for a password (not echoed)."""
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        password_hash = generate_password_hash(password)

        with app.app_context():
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username.strip(), password_hash),
                )
                db.commit()
            except sqlite3.IntegrityError:
                raise click.ClickException(f"User {username!r} already exists.")

        click.echo(f"Created user {username!r}.")
