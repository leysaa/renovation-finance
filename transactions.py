"""Transaction CRUD under a project (ownership checked via projects.user_id)."""

from datetime import date
from urllib.parse import urlencode

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from db import get_categories, get_db
from projects import get_project_for_user

bp = Blueprint("transactions", __name__)


class TransactionForm(FlaskForm):
    code = SelectField("Category", validators=[DataRequired()])
    amount = FloatField(
        "Amount (€)",
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Amount must be greater than zero."),
        ],
    )
    date = DateField("Date", validators=[DataRequired()], format="%Y-%m-%d")
    description = StringField("Description", validators=[Optional(), Length(max=500)])
    submit = SubmitField("Save transaction")


class DeleteTransactionForm(FlaskForm):
    submit = SubmitField("Delete transaction")


def _detail_url(project_id: int, **filters) -> str:
    """Build project detail URL, keeping active transaction filters."""
    params = {k: v for k, v in filters.items() if v}
    base = url_for("projects.detail", project_id=project_id)
    if not params:
        return base
    return f"{base}?{urlencode(params)}"


def _filter_args_from_request() -> dict:
    return {
        "code": request.args.get("code") or request.form.get("code_filter") or None,
        "date_from": request.args.get("date_from") or request.form.get("date_from_filter") or None,
        "date_to": request.args.get("date_to") or request.form.get("date_to_filter") or None,
    }


def _load_category_choices():
    rows = get_categories()
    return [(r["code"], f"{r['name']} ({r['kind']})") for r in rows]


def _get_transaction_for_user(project_id: int, transaction_id: int):
    row = get_db().execute(
        """
        SELECT t.*
        FROM transactions t
        JOIN projects p ON p.id = t.project_id
        WHERE t.id = ? AND t.project_id = ? AND p.user_id = ?
        """,
        (transaction_id, project_id, current_user.id),
    ).fetchone()
    if row is None:
        abort(404)
    return row


def _transaction_form_from_row(row) -> TransactionForm:
    form = TransactionForm()
    form.code.choices = _load_category_choices()
    form.code.data = row["code"]
    form.amount.data = row["amount"]
    form.date.data = date.fromisoformat(row["date"])
    form.description.data = row["description"]
    return form


@bp.route("/projects/<int:project_id>/transactions/new", methods=["GET", "POST"])
@login_required
def create(project_id: int):
    project = get_project_for_user(project_id)
    form = TransactionForm()
    form.code.choices = _load_category_choices()
    filters = _filter_args_from_request()

    if form.validate_on_submit():
        db = get_db()
        db.execute(
            """
            INSERT INTO transactions (project_id, code, amount, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project_id,
                form.code.data,
                form.amount.data,
                form.date.data.isoformat(),
                (form.description.data or "").strip() or None,
            ),
        )
        db.commit()
        flash("Transaction added.", "success")
        return redirect(_detail_url(project_id, **filters))

    return render_template(
        "transactions/form.html",
        form=form,
        title="Add transaction",
        project=project,
        cancel_url=_detail_url(project_id, **filters),
        list_filters=filters,
        categories=get_categories(),
    )


@bp.route(
    "/projects/<int:project_id>/transactions/<int:transaction_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit(project_id: int, transaction_id: int):
    project = get_project_for_user(project_id)
    row = _get_transaction_for_user(project_id, transaction_id)
    filters = _filter_args_from_request()

    if request.method == "GET":
        form = _transaction_form_from_row(row)
    else:
        form = TransactionForm()
        form.code.choices = _load_category_choices()

    if form.validate_on_submit():
        db = get_db()
        db.execute(
            """
            UPDATE transactions SET code = ?, amount = ?, date = ?, description = ?
            WHERE id = ? AND project_id = ?
            """,
            (
                form.code.data,
                form.amount.data,
                form.date.data.isoformat(),
                (form.description.data or "").strip() or None,
                transaction_id,
                project_id,
            ),
        )
        db.commit()
        flash("Transaction updated.", "success")
        return redirect(_detail_url(project_id, **filters))

    return render_template(
        "transactions/form.html",
        form=form,
        title="Edit transaction",
        project=project,
        cancel_url=_detail_url(project_id, **filters),
        list_filters=filters,
        categories=get_categories(),
    )


@bp.route(
    "/projects/<int:project_id>/transactions/<int:transaction_id>/delete",
    methods=["GET", "POST"],
)
@login_required
def delete(project_id: int, transaction_id: int):
    project = get_project_for_user(project_id)
    row = _get_transaction_for_user(project_id, transaction_id)
    form = DeleteTransactionForm()
    filters = _filter_args_from_request()

    if form.validate_on_submit():
        db = get_db()
        db.execute(
            "DELETE FROM transactions WHERE id = ? AND project_id = ?",
            (transaction_id, project_id),
        )
        db.commit()
        flash("Transaction deleted.", "success")
        return redirect(_detail_url(project_id, **filters))

    return render_template(
        "transactions/delete_confirm.html",
        project=project,
        transaction=row,
        form=form,
        cancel_url=_detail_url(project_id, **filters),
        list_filters=filters,
    )


def init_app(app) -> None:
    app.register_blueprint(bp)
