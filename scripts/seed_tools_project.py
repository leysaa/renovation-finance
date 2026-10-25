"""One-off seed: Tools category, second project, sample transactions."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "instance" / "building.db"


def main() -> None:
    c = sqlite3.connect(DB)
    c.execute("PRAGMA foreign_keys=ON")
    try:
        c.execute(
            "INSERT INTO categories (code, name, kind) VALUES ('T', 'Tools', 'expense')"
        )
        print("Added Tools category")
    except sqlite3.IntegrityError:
        print("Tools category already exists")

    row = c.execute("SELECT user_id FROM projects WHERE id=1").fetchone()
    if not row:
        raise SystemExit("Project 1 not found — create a project first.")
    user_id = row[0]

    existing = c.execute(
        "SELECT id FROM projects WHERE name = 'Office Renovation' AND user_id = ?",
        (user_id,),
    ).fetchone()
    if existing:
        pid = existing[0]
        print("Office Renovation already exists, id", pid)
    else:
        c.execute(
            """
            INSERT INTO projects (
                user_id, name, owner_name, address, city, area_m2, budget,
                start_date, status, notes
            ) VALUES (?, 'Office Renovation', 'Marco B.', 'Via Roma 12', 'Milan',
                      180, 25000, '2026-02-01', 'active', 'Second floor offices')
            """,
            (user_id,),
        )
        pid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        print("New project id:", pid)

    tx = [
        (pid, "I", 12000, "2026-02-10", "Advance payment"),
        (pid, "I", 8000, "2026-04-01", "Second tranche"),
        (pid, "M", 3200, "2026-02-15", "Drywall"),
        (pid, "S", 4500, "2026-03-01", "Crew week 1-2"),
        (pid, "T", 890, "2026-02-20", "Drill set + laser level"),
        (pid, "T", 420, "2026-03-08", "Saw blades"),
        (pid, "T", 650, "2026-03-22", "Scaffolding rental tools"),
        (pid, "O", 200, "2026-03-30", "Parking permits"),
        (1, "T", 310, "2026-04-05", "Angle grinder"),
        (1, "T", 175, "2026-04-08", "Replacement bits"),
    ]
    for t in tx:
        exists = c.execute(
            "SELECT 1 FROM transactions WHERE project_id=? AND code=? AND date=? AND amount=?",
            (t[0], t[1], t[3], t[2]),
        ).fetchone()
        if not exists:
            c.execute(
                "INSERT INTO transactions (project_id, code, amount, date, description) VALUES (?,?,?,?,?)",
                t,
            )
    c.commit()
    print("Done.")


if __name__ == "__main__":
    main()
