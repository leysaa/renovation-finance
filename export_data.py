"""Export transactions to Excel (scoped by user / project)."""

import io
from datetime import datetime

from flask import Blueprint, Response
from flask_login import current_user, login_required
from openpyxl import Workbook
from openpyxl.styles import Font

from db import get_db
from projects import get_project_for_user

bp = Blueprint("export", __name__)

HEADERS = ("Project", "Date", "Category", "Type", "Amount (EUR)", "Description")


def _fetch_rows(project_id: int | None = None):
    sql = """
        SELECT
            p.name AS project_name,
            t.date,
            c.name AS category_name,
            c.kind AS category_kind,
            t.amount,
            t.description
        FROM transactions t
        JOIN projects p ON p.id = t.project_id
        JOIN categories c ON c.code = t.code
        WHERE p.user_id = ?
    """
    params: list = [current_user.id]
    if project_id is not None:
        sql += " AND p.id = ?"
        params.append(project_id)
    sql += " ORDER BY p.name COLLATE NOCASE ASC, t.date ASC, t.id ASC"
    return get_db().execute(sql, params).fetchall()


def _row_tuple(row) -> tuple:
    return (
        row["project_name"],
        row["date"],
        row["category_name"],
        row["category_kind"],
        round(row["amount"], 2),
        row["description"] or "",
    )


def _xlsx_response(rows, filename: str) -> Response:
    wb = Workbook()
    ws = wb.active
    ws.title = "Transactions"
    ws.append(list(HEADERS))
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in rows:
        ws.append(list(_row_tuple(row)))
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 16
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return Response(
        buf.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d")


@bp.route("/projects/<int:project_id>/export.xlsx")
@login_required
def project_xlsx(project_id: int):
    project = get_project_for_user(project_id)
    rows = _fetch_rows(project_id)
    safe = "".join(c if c.isalnum() else "_" for c in project["name"])[:40]
    return _xlsx_response(rows, f"{safe}_transactions_{_stamp()}.xlsx")


@bp.route("/export/all-transactions.xlsx")
@login_required
def all_xlsx():
    rows = _fetch_rows(None)
    return _xlsx_response(rows, f"all_projects_transactions_{_stamp()}.xlsx")


def init_app(app) -> None:
    app.register_blueprint(bp)
