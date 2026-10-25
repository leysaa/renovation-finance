PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    owner_name  TEXT,
    address     TEXT,
    city        TEXT,
    area_m2     REAL,
    budget      REAL,
    start_date  TEXT,
    end_date    TEXT,
    status      TEXT    NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'completed')),
    notes       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE categories (
    code  TEXT PRIMARY KEY,
    name  TEXT NOT NULL,
    kind  TEXT NOT NULL CHECK (kind IN ('income', 'expense'))
);

INSERT INTO categories (code, name, kind) VALUES
    ('I', 'Income from owner', 'income'),
    ('M', 'Materials',         'expense'),
    ('S', 'Salaries / labour', 'expense'),
    ('T', 'Tools',             'expense'),
    ('O', 'Other expenses',    'expense');

CREATE TABLE transactions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    code         TEXT    NOT NULL REFERENCES categories(code),
    amount       REAL    NOT NULL CHECK (amount > 0),
    date         TEXT    NOT NULL,
    description  TEXT,
    created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_tx_project_date ON transactions (project_id, date);
