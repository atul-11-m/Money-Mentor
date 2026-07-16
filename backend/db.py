import sqlite3

from config import DB_PATH


def get_conn() -> sqlite3.Connection:
    """Return a SQLite connection whose rows behave like dicts.

    sqlite3.Row lets callers use dict(row) and row["col"], so the rest of the
    codebase can treat results uniformly.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the transactions table if it does not already exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            posting_date TEXT,
            description  TEXT,
            amount       REAL,
            type         TEXT,
            balance      REAL,
            category     TEXT,
            UNIQUE(posting_date, description, amount)
        )
        """
    )
    conn.commit()
    conn.close()
