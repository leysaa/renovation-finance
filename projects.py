"""Projects blueprint: list, create, edit, delete (scoped to logged-in user)."""

from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from flask_wtf.csrf import generate_csrf
from wtforms import DateField, FloatField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from db import get_categories, get_db

bp = Blueprint("projects", __name__, url_prefix="/projects")

STATUSES = ("active", "completed")
STATUS_LABELS = {
    "active": "Active",
    "completed": "Completed",
}
# Short labels for transaction category segmented control (project detail).
CATEGORY_SHORT_LABELS = {
    "I": "Income",
    "M": "Materials",
    "S": "Labour",
    "T": "Tools",
    "O": "Other",
}


class ProjectForm(FlaskForm):
    name = StringField("Project name", validators=[DataRequired(), Length(max=200)])
    owner_name = StringField("Building owner", validators=[Optional(), Length(max=200)])
    address = StringField("Address", validators=[Optional(), Length(max=300)])
    city = StringField("City", validators=[Optional(), Length(max=100)])
    area_m2 = FloatField(
        "Area (m²)",
        validators=[Optional(), NumberRange(min=0, message="Must be zero or positive.")],
    )
    budget = FloatField(
        "Budget (€)",
        validators=[Optional(), NumberRange(min=0, message="Must be zero or positive.")],
    )
    start_date = DateField("Start date", validators=[Optional()], format="%Y-%m-%d")
    end_date = DateField("End date", validators=[Optional()], format="%Y-%m-%d")
    status = SelectField(
        "Status",
        choices=[(s, STATUS_LABELS[s]) for s in STATUSES],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Notes", validators=[Optional(), Length(max=5000)])
    submit = SubmitField("Save project")


class DeleteProjectForm(FlaskForm):
    submit = SubmitField("Delete project permanently")


def _empty_to_none(value):
    return value if value not in ("", None) else None


def get_project_for_user(project_id: int):
    """Return the project row or 404 if it does not belong to the current user."""
    row = get_db().execute(
        "SELECT * FROM projects WHERE id = ? AND user_id = ?",
        (project_id, current_user.id),
    ).fetchone()
    if row is None:
        abort(404)
    return row


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def _project_form_from_row(row) -> ProjectForm:
    form = ProjectForm()
    form.name.data = row["name"]
    form.owner_name.data = row["owner_name"]
    form.address.data = row["address"]
    form.city.data = row["city"]
    form.area_m2.data = row["area_m2"]
    form.budget.data = row["budget"]
    form.start_date.data = _parse_date(row["start_date"])
    form.end_date.data = _parse_date(row["end_date"])
    form.status.data = row["status"]
    form.notes.data = row["notes"]
    return form


def _form_to_values(form: ProjectForm) -> dict:
    return {
        "name": form.name.data.strip(),
        "owner_name": _empty_to_none((form.owner_name.data or "").strip()) or None,
        "address": _empty_to_none((form.address.data or "").strip()) or None,
        "city": _empty_to_none((form.city.data or "").strip()) or None,
        "area_m2": form.area_m2.data,
        "budget": form.budget.data,
        "start_date": form.start_date.data.isoformat() if form.start_date.data else None,
        "end_date": form.end_date.data.isoformat() if form.end_date.data else None,
        "status": form.status.data,
        "notes": _empty_to_none((form.notes.data or "").strip()) or None,
    }


@bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status")
    if status_filter and status_filter not in STATUSES:
        status_filter = None

    sql = """
        SELECT
            p.id,
            p.name,
            p.owner_name,
            p.address,
            p.city,
            p.status,
            p.budget,
            COALESCE(SUM(CASE WHEN c.kind = 'income' THEN t.amount END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN c.kind = 'expense' THEN t.amount END), 0) AS total_expense
        FROM projects p
        LEFT JOIN transactions t ON t.project_id = p.id
        LEFT JOIN categories c ON c.code = t.code
        WHERE p.user_id = ?
    """
    params: list = [current_user.id]
    if status_filter:
        sql += " AND p.status = ?"
        params.append(status_filter)
    sql += """
        GROUP BY p.id
        ORDER BY p.name COLLATE NOCASE ASC
    """
    projects = get_db().execute(sql, params).fetchall()

    return render_template(
        "projects/list.html",
        projects=projects,
        status_filter=status_filter,
        status_labels=STATUS_LABELS,
        csrf_token=generate_csrf(),
    )


@bp.route("/<int:project_id>/")
@login_required
def detail(project_id: int):
    """Project detail: transactions, filters, and summary totals."""
    project = get_project_for_user(project_id)

    code_filter = request.args.get("code") or None
    date_from = request.args.get("date_from") or None
    date_to = request.args.get("date_to") or None

    categories = get_categories()
    valid_codes = {c["code"] for c in categories}
    if code_filter and code_filter not in valid_codes:
        code_filter = None

    where = ["t.project_id = ?"]
    params: list = [project_id]
    if code_filter:
        where.append("t.code = ?")
        params.append(code_filter)
    if date_from:
        where.append("t.date >= ?")
        params.append(date_from)
    if date_to:
        where.append("t.date <= ?")
        params.append(date_to)
    where_sql = " AND ".join(where)

    transactions = get_db().execute(
        f"""
        SELECT
            t.id, t.amount, t.date, t.description, t.code,
            c.name AS category_name, c.kind AS category_kind
        FROM transactions t
        JOIN categories c ON c.code = t.code
        WHERE {where_sql}
        ORDER BY t.date DESC, t.id DESC
        """,
        params,
    ).fetchall()

    # Summary chips always reflect the full project (ignore list filters).
    totals = get_db().execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN c.kind = 'income' THEN t.amount END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN c.kind = 'expense' THEN t.amount END), 0) AS total_expense
        FROM transactions t
        JOIN categories c ON c.code = t.code
        WHERE t.project_id = ?
        """,
        (project_id,),
    ).fetchone()

    total_income = totals["total_income"]
    total_expense = totals["total_expense"]
    balance = total_income - total_expense
    budget_used_pct = None
    if project["budget"] is not None and project["budget"] > 0:
        budget_used_pct = min(100.0 * total_expense / project["budget"], 999.9)

    return render_template(
        "projects/detail.html",
        project=project,
        transactions=transactions,
        categories=categories,
        code_filter=code_filter,
        date_from=date_from,
        date_to=date_to,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        budget_used_pct=budget_used_pct,
        status_labels=STATUS_LABELS,
        category_short_labels=CATEGORY_SHORT_LABELS,
        csrf_token=generate_csrf(),
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = ProjectForm()
    if form.validate_on_submit():
        v = _form_to_values(form)
        db = get_db()
        db.execute(
            """
            INSERT INTO projects (
                user_id, name, owner_name, address, city, area_m2, budget,
                start_date, end_date, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user.id,
                v["name"],
                v["owner_name"],
                v["address"],
                v["city"],
                v["area_m2"],
                v["budget"],
                v["start_date"],
                v["end_date"],
                v["status"],
                v["notes"],
            ),
        )
        db.commit()
        flash(f"Project “{v['name']}” created.", "success")
        return redirect(url_for("projects.index"))

    return render_template("projects/form.html", form=form, title="New project")


@bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def edit(project_id: int):
    row = get_project_for_user(project_id)
    if request.method == "GET":
        form = _project_form_from_row(row)
    else:
        form = ProjectForm()

    if form.validate_on_submit():
        v = _form_to_values(form)
        db = get_db()
        db.execute(
            """
            UPDATE projects SET
                name = ?, owner_name = ?, address = ?, city = ?,
                area_m2 = ?, budget = ?, start_date = ?, end_date = ?,
                status = ?, notes = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                v["name"],
                v["owner_name"],
                v["address"],
                v["city"],
                v["area_m2"],
                v["budget"],
                v["start_date"],
                v["end_date"],
                v["status"],
                v["notes"],
                project_id,
                current_user.id,
            ),
        )
        db.commit()
        flash(f"Project “{v['name']}” updated.", "success")
        return redirect(url_for("projects.detail", project_id=project_id))

    return render_template(
        "projects/form.html",
        form=form,
        title="Edit project",
        project_id=project_id,
    )


@bp.route("/<int:project_id>/delete", methods=["GET", "POST"])
@login_required
def delete(project_id: int):
    row = get_project_for_user(project_id)
    form = DeleteProjectForm()

    if form.validate_on_submit():
        db = get_db()
        db.execute(
            "DELETE FROM projects WHERE id = ? AND user_id = ?",
            (project_id, current_user.id),
        )
        db.commit()
        flash(f"Project “{row['name']}” deleted.", "success")
        return redirect(url_for("projects.index"))

    return render_template(
        "projects/delete_confirm.html",
        project=row,
        form=form,
    )


def init_app(app) -> None:
    app.register_blueprint(bp)
