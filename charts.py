"""Chart JSON APIs and overview page (SQL aggregates only)."""

from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from db import get_db
from projects import STATUS_LABELS, get_project_for_user

bp = Blueprint("charts", __name__)

IOS_GREEN = "#34c759"
IOS_RED = "#ff3b30"
IOS_BLUE = "#007aff"
EXPENSE_COLORS = ["#ff9500", "#ff3b30", "#af52de", "#8e8e93"]


@bp.route("/overview")
@login_required
def overview():
    return render_template("projects/overview.html")


@bp.route("/overview/balance-by-project.json")
@login_required
def balance_by_project_json():
    rows = get_db().execute(
        """
        SELECT
            p.id,
            p.name,
            COALESCE(SUM(CASE WHEN c.kind = 'income' THEN t.amount END), 0)
            - COALESCE(SUM(CASE WHEN c.kind = 'expense' THEN t.amount END), 0) AS balance
        FROM projects p
        LEFT JOIN transactions t ON t.project_id = p.id
        LEFT JOIN categories c ON c.code = t.code
        WHERE p.user_id = ?
        GROUP BY p.id
        ORDER BY p.name COLLATE NOCASE ASC
        """,
        (current_user.id,),
    ).fetchall()

    labels = [r["name"] for r in rows]
    values = [round(r["balance"], 2) for r in rows]
    ids = [r["id"] for r in rows]
    colors = [IOS_GREEN if v >= 0 else IOS_RED for v in values]

    return jsonify({"labels": labels, "values": values, "project_ids": ids, "colors": colors})


@bp.route("/projects/<int:project_id>/charts")
@login_required
def project_charts(project_id: int):
    """Charts for one project (separate from the transactions view)."""
    project = get_project_for_user(project_id)
    return render_template(
        "projects/charts.html",
        project=project,
        status_labels=STATUS_LABELS,
    )


@bp.route("/projects/<int:project_id>/charts/cumulative-balance.json")
@login_required
def cumulative_balance_json(project_id: int):
    get_project_for_user(project_id)

    rows = get_db().execute(
        """
        WITH daily AS (
            SELECT
                t.date AS day,
                SUM(CASE WHEN c.kind = 'income' THEN t.amount ELSE -t.amount END) AS net
            FROM transactions t
            JOIN categories c ON c.code = t.code
            WHERE t.project_id = ?
            GROUP BY t.date
        )
        SELECT
            day,
            SUM(net) OVER (ORDER BY day ROWS UNBOUNDED PRECEDING) AS cumulative
        FROM daily
        ORDER BY day ASC
        """,
        (project_id,),
    ).fetchall()

    return jsonify(
        {
            "labels": [r["day"] for r in rows],
            "values": [round(r["cumulative"], 2) for r in rows],
        }
    )


@bp.route("/projects/<int:project_id>/charts/expenses-by-category.json")
@login_required
def expenses_by_category_json(project_id: int):
    get_project_for_user(project_id)

    rows = get_db().execute(
        """
        SELECT c.code, c.name, SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON c.code = t.code
        WHERE t.project_id = ? AND c.kind = 'expense'
        GROUP BY c.code, c.name
        HAVING total > 0
        ORDER BY total DESC
        """,
        (project_id,),
    ).fetchall()

    return jsonify(
        {
            "labels": [r["name"] for r in rows],
            "codes": [r["code"] for r in rows],
            "values": [round(r["total"], 2) for r in rows],
        }
    )


@bp.route("/projects/<int:project_id>/charts/monthly-income-expense.json")
@login_required
def monthly_income_expense_json(project_id: int):
    get_project_for_user(project_id)

    rows = get_db().execute(
        """
        SELECT
            strftime('%Y-%m', t.date) AS month,
            COALESCE(SUM(CASE WHEN c.kind = 'income' THEN t.amount END), 0) AS income,
            COALESCE(SUM(CASE WHEN c.kind = 'expense' THEN t.amount END), 0) AS expense
        FROM transactions t
        JOIN categories c ON c.code = t.code
        WHERE t.project_id = ?
        GROUP BY month
        ORDER BY month ASC
        """,
        (project_id,),
    ).fetchall()

    return jsonify(
        {
            "labels": [r["month"] for r in rows],
            "income": [round(r["income"], 2) for r in rows],
            "expense": [round(r["expense"], 2) for r in rows],
        }
    )


def init_app(app) -> None:
    app.register_blueprint(bp)
