import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "instance" / "building.db"

c = sqlite3.connect(DB)
c.execute("PRAGMA foreign_keys=ON")
uid = c.execute("SELECT user_id FROM projects WHERE id=1").fetchone()[0]
name = "Basement Studio"
row = c.execute(
    "SELECT id FROM projects WHERE name = ? AND user_id = ?", (name, uid)
).fetchone()
if row:
    pid = row[0]
else:
    c.execute(
        """
        INSERT INTO projects (
            user_id, name, owner_name, address, city, budget,
            start_date, end_date, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uid,
            name,
            "Sara K.",
            "12 Lindenweg",
            "Hamburg",
            8000,
            "2025-06-01",
            "2025-11-30",
            "completed",
            "Finished over budget",
        ),
    )
    pid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    print("Created project", pid)

tx = [
    (pid, "I", 4000, "2025-07-01", "Owner payment 1"),
    (pid, "I", 2500, "2025-09-15", "Owner payment 2"),
    (pid, "M", 5200, "2025-07-20", "Insulation + flooring"),
    (pid, "S", 3800, "2025-08-01", "Labour"),
    (pid, "T", 650, "2025-08-10", "Power tools"),
    (pid, "O", 890, "2025-10-01", "Unexpected repairs"),
]
for t in tx:
    if not c.execute(
        "SELECT 1 FROM transactions WHERE project_id=? AND code=? AND date=? AND amount=?",
        (t[0], t[1], t[3], t[2]),
    ).fetchone():
        c.execute(
            "INSERT INTO transactions (project_id, code, amount, date, description) VALUES (?,?,?,?,?)",
            t,
        )
c.commit()

inc = c.execute(
    """
    SELECT COALESCE(SUM(t.amount), 0) FROM transactions t
    JOIN categories cat ON cat.code = t.code
    WHERE t.project_id = ? AND cat.kind = 'income'
    """,
    (pid,),
).fetchone()[0]
exp = c.execute(
    """
    SELECT COALESCE(SUM(t.amount), 0) FROM transactions t
    JOIN categories cat ON cat.code = t.code
    WHERE t.project_id = ? AND cat.kind = 'expense'
    """,
    (pid,),
).fetchone()[0]
print("Income", inc, "Expense", exp, "Balance", inc - exp)
